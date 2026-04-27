#!/usr/bin/env python3
"""
EEG Audit Tool - Flask server
Run: python -m neuroaudit
Then open http://127.0.0.1:5000
"""

import json
import re
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, abort

APP_DIR = Path(__file__).parent
from . import template_checker
from neurodoc.api import (
    anthropic_to_openai_response,
    call_llm_text,
    check_analysis_text,
    load_rules,
    post_llm_json,
    resolve_llm_config,
)
from neurodoc.paths import DATASET_DOCUMENT_DIR

try:
    _DETECT_RULES = load_rules()
except Exception as _detect_err:
    _DETECT_RULES = []
    print(f"[server] WARNING: neurodoc semantic checks not loadable: {_detect_err}")


def _run_semantic_checks(analysis_text: str, dataset_name: str = "") -> list[dict]:
    """Invoke detect.py cross-checks on in-memory analysis.md text. Returns [] on failure."""
    if not _DETECT_RULES:
        return []
    try:
        return check_analysis_text(
            analysis_text,
            dataset_name=dataset_name,
            rules=_DETECT_RULES,
        )
    except Exception as e:
        print(f"[server] detect.check_analysis_text failed: {e}")
        return []


def _check_tasks_fragment(tasks_section: str, dataset_name: str = "", analysis_md: str = "") -> list[str]:
    """Inject the synthesized Tasks section into a minimal analysis.md and run
    Task-scoped cross-checks. Returns human-readable strings.

    If `analysis_md` is supplied its real ## File Scan Result block is reused so
    that target_events_in_event_structure can validate against actual event IDs.
    Without it a stub with an empty Event Structure is used (legacy behaviour).
    """
    ts = (tasks_section or "").strip()
    if not ts.startswith("##"):
        ts = "## Tasks\n\n" + ts

    fsr_block = ""
    if analysis_md:
        m = re.search(r"(## File Scan Result.*?)(?=\n## |\Z)", analysis_md, re.DOTALL)
        if m:
            fsr_block = m.group(1).strip()
    if not fsr_block:
        fsr_block = (
            "## File Scan Result\n\n"
            "### Event Structure\n\n| Event ID | Count | Type | Meta Level | Meaning |\n|---|---|---|---|---|\n\n"
            "### MISC Label Summary\n\n| Channel | Source | Meta | Notes |\n|---|---|---|---|\n\n"
            "### Info\n\n| Field | Value | Completeness | Notes |\n|---|---|---|---|\n"
        )

    shell = (
        "# Analysis\n\n"
        "## Paradigm\n\n(stub)\n\n"
        f"{fsr_block}\n\n"
        f"{ts}\n\n"
        "## Data Quality Notes\n\n- (stub)\n\n"
        "## Kernel Responsibilities\n\n> **Status**: wait_manual_review\n"
        "> **Super Meta Required**: no\n"
    )
    violations = _run_semantic_checks(shell, dataset_name=dataset_name)
    # Only surface rules that point at the Tasks section or derived checks.
    task_relevant = {
        "label_field_required_for_nonevent",
        "label_field_absent_for_event",
        "info_label_field_in_info_section",
        "misc_label_field_in_misc_section",
        "target_def_schema_matches_route",
        "single_target_per_task",
        "misc_classification_forbidden",
        "classification_task_has_multiple_classes",
        "derived_misc_requires_super_meta",
        "segmentation_requires_nonevent_route",
        "segmentation_requires_empty_target_events",
        "target_events_in_event_structure",
        "classical_task_evidence",
        "task_order_classical_first",
        "task_numbering_from_one",
        "no_mi_on_phase_markers",
    }
    filtered = [v for v in violations if v.get("rule_id") in task_relevant]
    return _format_semantic_errors(filtered)


def _format_semantic_errors(violations: list[dict]) -> list[str]:
    """Shape detect.py violations into short strings for the LLM repair prompt."""
    lines = []
    for v in violations:
        rid = v.get("rule_id", "?")
        sev = v.get("severity", "?")
        desc = v.get("desc", "") or ""
        detail = v.get("detail", "") or ""
        if desc and detail:
            lines.append(f"[{sev}] {rid}: {desc} — {detail}")
        elif desc:
            lines.append(f"[{sev}] {rid}: {desc}")
        else:
            lines.append(f"[{sev}] {rid}: {detail}")
    return lines

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    _HAS_REQUESTS = False

CONFIG_FILE = APP_DIR / "config.json"
RULEBOOK_FILE = APP_DIR / "rulebook.md"
DATASET_DIR = DATASET_DOCUMENT_DIR
EXCLUDE_DIRS: set[str] = set()
EXCLUDE_NAME_RE = re.compile(r"\.(py|pdf|md|txt|json|csv)$", re.IGNORECASE)

app = Flask(__name__, static_folder=str(APP_DIR))

# ── Optional deps for reference text extraction ────────────────────────────────
try:
    import fitz as _fitz
    _HAS_FITZ = True
except ImportError:
    _HAS_FITZ = False

try:
    from bs4 import BeautifulSoup as _BS4
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False

# ── SKILL directory ────────────────────────────────────────────────────────────
SKILLS_DIR = APP_DIR / "skills"
CATEGORY_SKILL_MAP = {
    "Action/Output":      "action_output.md",
    "Sensory/Response":   "sensory_response.md",
    "Biological State":   "biological_state.md",
    "High-level Mental":  "high_level_mental.md",
    "Complex Applied":    "complex_applied.md",
    "Others":             "complex_applied.md",
}

def _load_skill(category: str) -> str:
    fname = CATEGORY_SKILL_MAP.get(category, "")
    if not fname:
        return ""
    p = SKILLS_DIR / fname
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""

def _category_from_md(analysis_md: str) -> str:
    m = re.search(r"\*\*Category\*\*:\s*([^|*\n]+)", analysis_md)
    return m.group(1).strip() if m else ""

# ── Phase-0 system prompt (DOI/URL/ref extraction per paper) ──────────────────
_P0_SYSTEM = """\
You are a research paper metadata extractor. Given the first two pages of a paper,
extract the primary reference identifier (DOI, URL, or arXiv ID) and the paper title.

Rules:
- Prefer DOI (format: 10.XXXX/...) over URL over arXiv ID
- arXiv ID format: arXiv:XXXX.XXXXX or https://arxiv.org/abs/XXXX.XXXXX
- If multiple DOIs appear, use the one for THIS paper (usually in header/footer, not in references)
- title: full paper title as it appears on the first page
- If nothing found, return empty strings

Output ONLY valid JSON, no markdown fences:
{"ref": "<doi or url or arxiv>", "ref_type": "doi|url|arxiv|none", "title": "<paper title>"}"""

# ── Phase-1 system prompt (relevance + task extraction per paper) ──────────────
_P1_SYSTEM = """\
You are an expert EEG neuroscience analyst. For a given EEG dataset and one reference paper,
perform TWO tasks in a single pass.

TASK A — Relevance classification (one of):
  relevant   : paper (a) explicitly uses/describes THIS specific dataset AND (b) defines a concrete ML task.
  partial    : paper uses this dataset but task definition is vague/incomplete (e.g. no class count,
               no epoch params, dataset only mentioned in passing). Can support Potential Tasks.
  irrelevant : related topic but does NOT use this dataset.
  uncertain  : insufficient text to judge.
  junk       : clearly wrong domain.

TASK B — Task extraction (fill for relevant/partial; leave empty only for irrelevant/junk):
  supports_task      : true if classification=relevant AND a concrete ML task with labels is defined.
  task_type          : "classification" | "regression" | "none"
                       (v3: Task Type is the learning target type, NOT the epoch method.
                        segmentation is an Epoch Method, not a Task Type.)
  n_classes          : integer number of classes, or 0 if unclear
  paradigm           : brief paradigm description (e.g. "4-class MI left/right fist, both fists, feet")
  epoch_method_hint  : "event-based" | "long-event" | "segmentation" | "unclear"
  epoch_params       : exact values stated in paper, e.g. "tmin=0s tmax=3s" or "unclear". Include
                       whether marker is cue onset or offset if stated.
  target_events      : list of class/event names using the paper's own terms (not raw IDs)
  label_mapping      : e.g. "left hand->0, right hand->1"
  meta_level         : "raw" | "super" | "unclear"
  super_meta_note    : how labels are derived if super; "" otherwise
  evidence_desc      : 2-4 sentences covering: (1) what task was performed on this dataset,
                       (2) number of classes and which classes, (3) epoch window if stated,
                       (4) any deviation from standard protocol or ambiguity. Be specific.
  ref                : the paper's DOI (10.xxxx/...), URL, or arXiv ID. Use value from Phase-0 if provided.

Output ONLY valid JSON, no surrounding text or markdown fences:
{
  "classification": "relevant|partial|irrelevant|uncertain|junk",
  "cot_reasoning": "<3-6 sentence chain-of-thought>",
  "supports_task": true|false,
  "task_type": "classification|regression|none",
  "n_classes": 0,
  "paradigm": "",
  "epoch_method_hint": "event-based|long-event|segmentation|unclear",
  "epoch_params": "",
  "target_events": [],
  "label_mapping": "",
  "meta_level": "raw|super|unclear",
  "super_meta_note": "",
  "evidence_desc": "",
  "ref": ""
}"""

# ── Phase-2-1 system prompt (epoch alignment analysis, dataset-level) ──────────
_P21_SYSTEM = """\
You are an EEG preprocessing expert. Analyse a dataset's paradigm and event structure
to determine the correct epoch alignment and recommended parameters.

You receive: the dataset's analysis.md, Category SKILL guide, and Phase-1 extractions.

Your job:
1. Determine whether event markers represent cue ONSET or cue OFFSET.
2. Determine cue duration (seconds) if inferable.
3. Recommend tmin and tmax (or segment_length/overlap for segmentation paradigms).
4. Identify if multiple paradigm types exist in the same dataset (each needs separate recommendation).
5. Flag any run-dependent or subject-dependent complications.

Output ONLY valid JSON, no markdown fences:
{
  "alignment": "onset|offset|mixed|unclear",
  "cue_duration_s": <float or null>,
  "recommendations": [
    {
      "paradigm_label": "<short name, e.g. 'Motor Imagery'>",
      "epoch_method": "epoch_by_event_hdf5|epoch_by_long_event_hdf5|epoch_by_segmentation_hdf5",
      "tmin": <float>,
      "tmax": <float or null>,
      "overlap": <float or null>,
      "segment_length": <float or null>,
      "reasoning": "<2-3 sentences explaining the choice>"
    }
  ],
  "complications": "<any run-dependent, protocol-dependent, or subject-dependent issues>",
  "kernel_notes": "<implementation notes for the kernel team>"
}"""

# ── Phase-2-2 system prompt (task synthesis + self-check, v3 taxonomy) ────────
_P22_SYSTEM = """\
You are an EEG machine learning task documentation expert. Write the complete "## Tasks" section
of an EEG dataset's analysis.md following the v3 epoch/label taxonomy, then self-check.

You receive: the full analysis.md, raw event IDs, Phase-1 extractions, Phase-2-1 epoch alignment,
and a Category SKILL guide.

=== EEGUnity Epoch Methods (ONLY these three) ===
1. epoch_by_event_hdf5        short discrete events: params tmin, tmax, target_events
2. epoch_by_long_event_hdf5   long sustained annotations: params tmin, tmax, overlap, target_events
3. epoch_by_segmentation_hdf5 sliding window, no annotations: params segment_length, overlap;
                              target_events MUST be []

=== Task Template (v3) ===
### Classical Task N: <concise name>
- **Task Type**: classification | regression
- **Epoch Method**: `<method>`
- **Epoch Parameters**: <minimum required keys for the method — see Epoch Parameters rules below>
- **Label Route**: `event` | `misc` | `info`
- **Label Field**: `<channel_or_column_name>`     # ONLY when Route ∈ {misc, info}
- **Meta Level**: raw | super
- **Target Definition**:
  <route-specific table — see schema matrix below>
- **Evidence**:
  - <ref> — <evidence_desc>
- **Notes**: free-form task annotation (recommended: super-meta derivation steps, parameter inference rationale).

=== Epoch Parameters rules (MANDATORY — detect.py rule epoch_parameters_complete, severity=error) ===
Every Task MUST list AT LEAST these keys in Epoch Parameters for its declared Epoch Method:
  * epoch_by_event_hdf5       — tmin, tmax, target_events
  * epoch_by_long_event_hdf5  — tmin, tmax, overlap, target_events
  * epoch_by_segmentation_hdf5 — segment_length, overlap (target_events MUST be [])
Extra MNE.Epoch parameters (baseline, reject, picks, ...) are allowed as additional `key = value` pairs.
If you cannot ground the required keys, DROP the task — do not leave them blank.

=== Three Task Archetypes ===
A — Event is the label  (Route=event, no Label Field)
B1 — Native misc: label = numeric column of events.tsv (Route=misc, Meta=raw, regression only)
B2 — Derived misc: label derived by kernel from participants.tsv (Route=misc, Meta=super, regression only)
B3 — Native info: label = participants.tsv column used directly (Route=info)
C  — No event; epoch_by_segmentation_hdf5 with subject-level label (Route=misc derived or info)

=== Target Definition schema matrix (Route × Task Type) ===
  event  classification  | Event ID | y | Meaning |
                         y = integer class index (e.g. 0, 1, 2) OR comma-separated
                         integers for multi-label events (e.g. "0,1" when one event
                         belongs to multiple classes simultaneously).
                         The union of all y tokens across all rows must be {0,1,…,N-1}.
  event  regression      | Event ID | Value | Meaning |
  misc   regression      | MISC Channel | Value (unit) | Notes |
  misc   classification  FORBIDDEN — use event or info instead
  info   classification  | Info Field | Value | y | Meaning |
  info   regression      | Info Field | Range (unit) | Notes |

=== HARD RULES ===
H1 ONE LABEL FIELD PER TASK. Multi-dimension labels split into N tasks.
H2 CLASSIFICATION ≥ 2 DISTINCT y VALUES.
H3 misc ROUTE IS REGRESSION-ONLY.
H4 LABEL FIELD REQUIRED iff Route ∈ {misc, info}; FORBIDDEN when Route=event.
H5 DERIVED MISC ⇒ Meta Level = super. Notes SHOULD describe the derivation
   (recommended, not enforced — Notes is freeform).
H6 GROUND TRUTH only — do not invent fields. If the Label Field is not present in
   events.tsv, participants.tsv, or the native misc list, DROP the task.
H7 segmentation ⇒ target_events = [].
H8 segmentation ⇒ Label Route MUST be misc or info. Label Route = event is FORBIDDEN
   for epoch_by_segmentation_hdf5 because segmentation has no event anchors.

=== Other Rules ===
R1 Event grounding: target_events MUST come from Available Raw Event IDs.
R2 Task classification:
   "Classical Task": ≥1 paper with classification=relevant AND has ref. ref required.
   "Potential Task": plausible analysis; partial/indirect evidence allowed.
   Multiple papers → ONE task with all refs.
R3 Refs: only from Phase-1 extractions. Never fabricate.
R4 Mark unconfirmed params with * (e.g. tmin = -0.5 s *).
R5 Use Phase-2-1 alignment recommendations as primary source.
R6 Evidence desc must cover: task type, n-classes, epoch window, any deviation.

=== SELF-CHECK (perform AFTER writing tasks, fix before output) ===
A: HARD FAIL — every entry in target_events MUST appear verbatim in the Available Raw
   Event IDs list above. Drop any entry not in that list. If dropping leaves
   target_events = [] for an event/long-event task, drop the entire task or downgrade
   it to Potential Task with a note. No invented, approximate, or synonymous IDs.
   (Skip this check only for epoch_by_segmentation_hdf5, which always uses target_events = [].)
B: Every Classical Task has at least one ref in Evidence.
C: Epoch params match Phase-2-1 (or deviation noted).
D: No duplicate tasks (same epoch+label combination).
E: H1–H8 all satisfied — Label Field present iff non-event; classification has ≥2 y;
   misc is regression-only; segmentation has target_events=[] AND Label Route ≠ event
   (segmentation NEVER uses Label Route=event — use misc or info instead);
   derived misc is super meta.
F: Epoch Parameters contain all MINIMUM required keys for the declared Epoch Method
   (see rules table above). Missing a required key (e.g. `overlap` for long-event) is a
   hard error and will be rejected by detect.py. If you lack a value, DROP the task.
G: Every classification Task's Target Definition must have ≥2 rows with DISTINCT y values
   (e.g. 0 and 1 for binary). If only one class is present or the table is empty, either
   add the missing class row or drop the task entirely.

=== Output Format ===
Return ONLY valid JSON (no markdown fences):
{
  "tasks_section": "## Tasks\\n\\n### Classical Task 1: ...\\n\\n### Potential Task 1: ...",
  "num_classical_tasks": <integer>,
  "num_potential_tasks": <integer>,
  "self_check_notes": "<brief summary of checks performed and any fixes made>",
  "summary": "<one sentence overall summary>"
}
CRITICAL: tasks_section is a single JSON string — use \\n for newlines."""

# ── Reference pipeline helpers ─────────────────────────────────────────────────
_P1_REF_MAX   = 100_000
_P0_PAGE_MAX  = 6_000    # first ~2 pages for Phase-0
_P1_ANALYSIS_MAX = 5_000
_REF_EXTENSIONS = {'.pdf', '.html', '.htm', '.txt', '.md'}


def _clean_ref_text(text):
    text = re.sub(
        r"You may also like\n.*?This content was downloaded from IP address[^\n]*\n?",
        "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d{3,4}\s*$", "", text)
    blocks = re.split(r"\n{2,}", text)
    merged = []
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) >= 4 and lines and sum(len(l) for l in lines) / len(lines) < 45:
            merged.append(" ".join(lines))
        else:
            merged.append(block)
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(merged)).strip()


def _extract_ref_text(file_path):
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        if not _HAS_FITZ:
            return f"[PDF unavailable: install pymupdf — filename: {file_path.name}]", "pdf"
        try:
            doc = _fitz.open(str(file_path))
            parts = [p.get_text("text") for p in doc if p.get_text("text").strip()]
            doc.close()
            return _clean_ref_text("\n".join(parts)), "pdf"
        except Exception as e:
            return f"[PDF error: {e}]", "pdf"
    if suffix in (".html", ".htm"):
        if _HAS_BS4:
            try:
                soup = _BS4(file_path.read_bytes(), "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return _clean_ref_text(soup.get_text(separator="\n")), "html"
            except Exception as e:
                return f"[HTML error: {e}]", "html"
    try:
        return file_path.read_text(encoding="utf-8", errors="replace"), "text"
    except Exception as e:
        return f"[read error: {e}]", "unknown"


def _ref_from_filename(filename):
    """Extract DOI hint from structured filenames like paper_10_1109_tnsre_..."""
    stem = Path(filename).stem
    if stem.startswith("paper_"):
        doi_raw = stem[6:]
        if doi_raw.startswith("10_"):
            parts = doi_raw.split("_")
            if len(parts) >= 3:
                return f"10.{parts[1]}/{'.'.join(parts[2:])}", "doi"
    m = re.search(r"(10\.\d{4,})_([^\s]+)", stem)
    if m:
        return f"{m.group(1)}/{m.group(2)}", "doi"
    return "", ""

# Keep old name as alias for backward compat
def _doi_from_filename(filename):
    ref, _ = _ref_from_filename(filename)
    return ref


def _ref_from_text_regex(text):
    """Fast regex extraction of DOI/URL/arXiv from text. Returns (ref, ref_type)."""
    # DOI pattern
    m = re.search(r'\b(10\.\d{4,}/[^\s,;"\'\]>\)]+)', text)
    if m:
        return m.group(1).rstrip('.'), "doi"
    # arXiv
    m = re.search(r'arXiv[:\s]+(\d{4}\.\d{4,})', text, re.IGNORECASE)
    if m:
        return f"https://arxiv.org/abs/{m.group(1)}", "arxiv"
    # URL
    m = re.search(r'(https?://[^\s,;"\'\]>]+)', text)
    if m:
        return m.group(1).rstrip('.'), "url"
    return "", "none"


def _event_ids_from_md(analysis_md):
    m = re.search(r"## File Scan Result(.*?)(?=\n## |\Z)", analysis_md, re.DOTALL)
    if not m:
        return []
    ids = re.findall(r"\|\s*`([^`\n]+)`", m.group(1))
    seen, result = set(), []
    for eid in ids:
        if eid not in seen:
            seen.add(eid)
            result.append(eid)
    return result


def _build_p21_user_msg(dataset, analysis_md, skill_text, extractions):
    """User message for Phase-2-1 epoch alignment analysis."""
    ext_block = ""
    for i, ext in enumerate(extractions, 1):
        extr = ext.get("extraction", ext)
        ref  = ext.get("ref") or ext.get("doi", "")
        ext_block += (
            f"\n--- Extraction {i}: {ext.get('reference_file', '')} "
            f"[{ext.get('classification','?')}] ---\n"
            + (f"ref: {ref}\n" if ref else "")
            + f"paradigm:          {extr.get('paradigm', '')}\n"
            + f"epoch_method_hint: {extr.get('epoch_method_hint', 'unclear')}\n"
            + f"epoch_params:      {extr.get('epoch_params', 'unclear')}\n"
        )
    skill_block = f"\n=== Category SKILL Guide ===\n{skill_text}\n" if skill_text else ""
    return (
        f"Dataset: {dataset}\n"
        f"{skill_block}"
        f"\n=== analysis.md (Paradigm + Event Structure) ===\n{analysis_md}\n"
        f"\n=== Phase-1 Extractions ({len(extractions)}) ===\n{ext_block}"
        f"\nAnalyse epoch alignment and provide recommendations."
    )


def _build_p22_user_msg(dataset, analysis_md, extractions, p21_result, skill_text):
    """User message for Phase-2-2 task synthesis + self-check."""
    event_ids = _event_ids_from_md(analysis_md)
    if event_ids:
        eid_block = (
            f"\n=== Available Raw Event IDs in '{dataset}' ===\n"
            + "  " + ",  ".join(f"`{e}`" for e in event_ids) + "\n"
            + "(EXACT strings. Raw meta target_events MUST use IDs from this list.)\n"
        )
    else:
        eid_block = "\n(No Event Structure found — use best judgment.)\n"

    ext_block = ""
    for i, ext in enumerate(extractions, 1):
        ref   = ext.get("ref") or ext.get("doi", "")
        extr  = ext.get("extraction", ext)
        cls   = ext.get("classification", "?")
        ext_block += (
            f"\n--- Extraction {i}: {ext.get('reference_file','')} [{cls}] ---\n"
            + (f"ref: {ref}\n" if ref else "ref: (not identified)\n")
            + f"supports_task:     {extr.get('supports_task', False)}\n"
            + f"task_type:         {extr.get('task_type','none')}\n"
            + f"n_classes:         {extr.get('n_classes', 0)}\n"
            + f"paradigm:          {extr.get('paradigm','')}\n"
            + f"epoch_method_hint: {extr.get('epoch_method_hint','unclear')}\n"
            + f"epoch_params:      {extr.get('epoch_params','unclear')}\n"
            + f"target_events:     {extr.get('target_events',[])}\n"
            + f"label_mapping:     {extr.get('label_mapping','')}\n"
            + f"meta_level:        {extr.get('meta_level','unclear')}\n"
            + f"super_meta_note:   {extr.get('super_meta_note','')}\n"
            + f"evidence_desc:     {extr.get('evidence_desc', extr.get('evidence_sentence',''))}\n"
        )

    p21_block = ""
    if p21_result:
        p21_block = (
            f"\n=== Phase-2-1 Epoch Alignment Analysis ===\n"
            f"alignment:      {p21_result.get('alignment','unclear')}\n"
            f"cue_duration_s: {p21_result.get('cue_duration_s','unknown')}\n"
            f"complications:  {p21_result.get('complications','')}\n"
            f"kernel_notes:   {p21_result.get('kernel_notes','')}\n"
        )
        for rec in p21_result.get("recommendations", []):
            p21_block += (
                f"  recommendation [{rec.get('paradigm_label','')}]: "
                f"{rec.get('epoch_method','')} "
                f"tmin={rec.get('tmin','?')} tmax={rec.get('tmax','?')} "
                f"overlap={rec.get('overlap','?')} segment_length={rec.get('segment_length','?')}\n"
                f"    reasoning: {rec.get('reasoning','')}\n"
            )

    skill_block = f"\n=== Category SKILL Guide ===\n{skill_text}\n" if skill_text else ""

    return (
        f"Dataset: {dataset}\n"
        f"{eid_block}"
        f"{p21_block}"
        f"{skill_block}"
        f"\n=== Current analysis.md ===\n{analysis_md}\n"
        f"\n=== Phase-1 Extractions ({len(extractions)} papers) ===\n{ext_block}"
        f"\nSynthesize tasks for '{dataset}'. Apply all RULES and perform SELF-CHECK."
    )


def _call_llm(messages, timeout=180):
    """Internal LLM call using the stored /api/config credentials."""
    cfg = {}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return call_llm_text(cfg, messages, timeout=timeout)


def _parse_llm_json(raw):
    """Strip <think> blocks, fences, then extract the outermost JSON object."""
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```\s*$", "", raw).strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None, raw
    try:
        return json.loads(m.group()), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}\nRaw (first 400 chars): {raw[:400]}"


def _read_meta(content):
    category = ""
    status = ""
    m = re.search(r"\*\*Category\*\*:\s*([^|*\n]+)", content)
    if m:
        category = m.group(1).strip()
    m = re.search(r"\*\*Status\*\*:\s*(\S+)", content)
    if m:
        status = m.group(1).strip()
    return category, status


def _template_payload(content):
    result = template_checker.check_analysis_template(content)
    return {
        "template_ok": result["ok"],
        "template_errors": result["errors"],
        "template_check": result,
    }


def _list_datasets():
    result = []
    for entry in sorted(DATASET_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIRS or entry.name.startswith("."):
            continue
        if EXCLUDE_NAME_RE.search(entry.name):
            continue
        analysis = entry / "analysis.md"
        if not analysis.exists():
            continue
        try:
            content = analysis.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        category, status = _read_meta(content)
        template_info = _template_payload(content)
        result.append({
            "name": entry.name,
            "category": category or "Unknown",
            "status": status or "unknown",
            "template_ok": template_info["template_ok"],
            "template_errors": template_info["template_errors"],
        })
    return result


@app.route("/")
def index():
    return send_from_directory(APP_DIR, "index.html")


@app.route("/api/datasets")
def api_datasets():
    return jsonify(_list_datasets())


@app.route("/api/dataset/<name>", methods=["GET"])
def api_get_dataset(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    path = DATASET_DIR / name / "analysis.md"
    if not path.exists():
        abort(404)
    content = path.read_text(encoding="utf-8", errors="replace")
    payload = {"name": name, "content": content}
    payload.update(_template_payload(content))
    return jsonify(payload)


@app.route("/api/dataset/<name>", methods=["PUT"])
def api_put_dataset(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    path = DATASET_DIR / name / "analysis.md"
    if not path.exists():
        abort(404)
    data = request.get_json(silent=True)
    if not data or "content" not in data:
        abort(400)
    check = template_checker.check_analysis_template(data["content"])
    if not check["ok"]:
        return jsonify({
            "ok": False,
            "error": "Template validation failed",
            "template_check": check,
        }), 400
    path.write_text(data["content"], encoding="utf-8")
    return jsonify({"ok": True, "template_check": check})


@app.route("/api/template/check", methods=["POST"])
def api_template_check():
    data = request.get_json(silent=True) or {}
    content = data.get("content", "")
    dataset_name = data.get("dataset", "")
    result = template_checker.check_analysis_template(content)
    semantic = _run_semantic_checks(content, dataset_name=dataset_name)
    result["semantic_errors"] = _format_semantic_errors(semantic)
    result["semantic_errors_raw"] = semantic
    if semantic and result.get("ok"):
        result["ok"] = False
    return jsonify(result)


@app.route("/api/rulebook")
def api_rulebook():
    if not RULEBOOK_FILE.exists():
        return jsonify({"content": "# Rulebook not found"})
    content = RULEBOOK_FILE.read_text(encoding="utf-8", errors="replace")
    return jsonify({"content": content})


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        else:
            cfg = {"BASE_URL": "", "ANTHROPIC_BASE_URL": "", "key": "", "model": "", "proxy": ""}
        try:
            normalized = resolve_llm_config(cfg)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        result = dict(cfg)
        result["BASE_URL"] = normalized["BASE_URL"]
        result["ANTHROPIC_BASE_URL"] = normalized["ANTHROPIC_BASE_URL"]
        result.setdefault("key", "")
        result.setdefault("model", "")
        result.setdefault("proxy", "")
        return jsonify(result)
    data = request.get_json(silent=True) or {}
    try:
        normalized = resolve_llm_config(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    to_save = {
        "BASE_URL": normalized["BASE_URL"],
        "ANTHROPIC_BASE_URL": normalized["ANTHROPIC_BASE_URL"],
        "key": normalized["key"],
        "model": normalized["model"],
        "proxy": normalized["proxy"],
    }
    CONFIG_FILE.write_text(json.dumps(to_save, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify({"ok": True})


@app.route("/api/llm", methods=["POST"])
def api_llm():
    cfg = {}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    try:
        resolved_cfg = resolve_llm_config(cfg)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not resolved_cfg.get("active_url"):
        return jsonify({"error": "LLM URL not configured. Open Settings to configure."}), 400

    body = request.get_json(silent=True) or {}
    messages = body.get("messages") or []
    # remove stream flag — some providers reject it
    body.pop("stream", None)

    try:
        data = post_llm_json(resolved_cfg, messages, timeout=90, extra_body=body)
        if resolved_cfg["provider"] == "anthropic":
            return jsonify(anthropic_to_openai_response(data))
        return jsonify(data)
    except Exception as e:
        response = getattr(e, "response", None)
        status = getattr(response, "status_code", None)
        if status is not None:
            return jsonify({"error": f"HTTP {status}: {getattr(response, 'text', '')}"}), 502
        return jsonify({"error": str(e)}), 500


@app.route("/api/template/fix_with_llm/<name>", methods=["POST"])
def api_template_fix_with_llm(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)

    analysis_path = DATASET_DIR / name / "analysis.md"
    if not analysis_path.exists():
        abort(404)

    content = analysis_path.read_text(encoding="utf-8", errors="replace")
    check = template_checker.check_analysis_template(content)
    semantic_violations = _run_semantic_checks(content, dataset_name=name)
    semantic_errors = _format_semantic_errors(semantic_violations)

    if check["ok"] and not semantic_errors:
        return jsonify({
            "fixed_content": content,
            "template_check": check,
            "semantic_errors": [],
            "message": "Document already matches the required template and v3 semantic rules.",
        })

    combined_errors = list(check["errors"]) + semantic_errors
    prompts = template_checker.build_template_repair_messages(
        dataset_name=name,
        content=content,
        errors=combined_errors,
    )
    try:
        raw = _call_llm([
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]},
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    try:
        raw = str(raw or "").strip()
        parsed, err = _parse_llm_json(raw)
        if parsed and isinstance(parsed, dict):
            fixed_content = parsed.get("fixed_content", "")
        elif raw.startswith("#"):
            fixed_content = raw
        else:
            raise ValueError(err or f"LLM returned invalid JSON: {raw[:300]}")

        if not fixed_content.strip():
            raise ValueError("LLM returned empty content.")

        fixed_check = template_checker.check_analysis_template(fixed_content)
        fixed_semantic = _run_semantic_checks(fixed_content, dataset_name=name)
        return jsonify({
            "fixed_content": fixed_content,
            "template_check": fixed_check,
            "semantic_errors": _format_semantic_errors(fixed_semantic),
            "semantic_errors_raw": fixed_semantic,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/refs/<name>")
def api_refs_list(name):
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    refs_dir = DATASET_DIR / name / "references"
    if not refs_dir.is_dir():
        return jsonify({"files": [], "error": "No references/ directory found for this dataset."})
    files = sorted(
        f.name for f in refs_dir.iterdir()
        if f.is_file() and f.suffix.lower() in _REF_EXTENSIONS
    )
    return jsonify({"files": files})


@app.route("/api/refs/phase0/<name>", methods=["POST"])
def api_refs_phase0(name):
    """Phase-0: extract DOI/URL/ref from a single reference file (regex + LLM fallback)."""
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    data = request.get_json(silent=True) or {}
    ref_file = data.get("file", "")
    if not ref_file or ".." in ref_file:
        abort(400)
    ref_path = DATASET_DIR / name / "references" / ref_file
    if not ref_path.exists():
        return jsonify({"error": f"File not found: {ref_file}"}), 404

    # 1. Filename-based hint
    filename_ref, filename_ref_type = _ref_from_filename(ref_file)
    if filename_ref_type == "doi":
        return jsonify({"ref": filename_ref, "ref_type": "doi",
                        "title": "", "reference_file": ref_file, "source": "filename"})

    # 2. Extract text and try regex on first portion
    ref_text, _ = _extract_ref_text(ref_path)
    first_chunk = ref_text[:_P0_PAGE_MAX]
    regex_ref, regex_type = _ref_from_text_regex(first_chunk)
    if regex_ref and regex_type == "doi":
        return jsonify({"ref": regex_ref, "ref_type": "doi",
                        "title": "", "reference_file": ref_file, "source": "regex"})

    # 3. LLM fallback for title + any ref type
    try:
        raw = _call_llm([
            {"role": "system", "content": _P0_SYSTEM},
            {"role": "user",   "content": f"File: {ref_file}\n\n{first_chunk}"},
        ], timeout=60)
        parsed, _ = _parse_llm_json(raw)
        if parsed and parsed.get("ref"):
            parsed["reference_file"] = ref_file
            parsed["source"] = "llm"
            return jsonify(parsed)
    except Exception:
        pass

    # 4. Use regex result even if not DOI, or empty
    return jsonify({"ref": regex_ref, "ref_type": regex_type or "none",
                    "title": "", "reference_file": ref_file, "source": "regex_fallback"})


@app.route("/api/refs/phase1/<name>", methods=["POST"])
def api_refs_phase1(name):
    """Phase-1: relevance classification + task extraction for one reference file."""
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    data = request.get_json(silent=True) or {}
    ref_file = data.get("file", "")
    p0_result = data.get("p0", {})   # Phase-0 result passed in from frontend
    if not ref_file or ".." in ref_file:
        abort(400)
    ref_path = DATASET_DIR / name / "references" / ref_file
    if not ref_path.exists():
        return jsonify({"error": f"File not found: {ref_file}"}), 404

    ref_text, _ = _extract_ref_text(ref_path)
    ref_text = ref_text[:_P1_REF_MAX]

    analysis_brief = ""
    analysis_path = DATASET_DIR / name / "analysis.md"
    if analysis_path.exists():
        analysis_brief = analysis_path.read_text(encoding="utf-8", errors="replace")[:_P1_ANALYSIS_MAX]

    # Ref hint: Phase-0 result takes priority over filename
    ref_hint = p0_result.get("ref") or _doi_from_filename(ref_file)
    ref_hint_line = f"Reference identifier (DOI/URL/arXiv): {ref_hint}\n" if ref_hint else ""

    user_msg = (
        f"Dataset: {name}\n\n"
        f"=== Dataset context (from analysis.md) ===\n{analysis_brief}\n\n"
        f"=== Reference file: {ref_file} ===\n"
        f"{ref_hint_line}"
        f"{ref_text}\n\n"
        f"Classify and extract task information for dataset '{name}' from the above reference."
    )

    try:
        raw = _call_llm([
            {"role": "system", "content": _P1_SYSTEM},
            {"role": "user",   "content": user_msg},
        ])
        parsed, err = _parse_llm_json(raw)
        if parsed is None:
            return jsonify({"error": f"Phase-1 parse failed: {err}",
                            "reference_file": ref_file,
                            "classification": "uncertain",
                            "supports_task": False}), 200

        parsed["reference_file"] = ref_file
        # Resolve ref: LLM output > Phase-0 > filename
        parsed["ref"] = parsed.get("ref") or ref_hint
        parsed["doi"] = parsed["ref"]  # backward compat alias
        parsed["extraction"] = {k: parsed.get(k) for k in (
            "supports_task", "task_type", "n_classes", "paradigm",
            "epoch_method_hint", "epoch_params", "target_events",
            "label_mapping", "meta_level", "super_meta_note",
            "evidence_desc", "ref",
        )}
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e), "reference_file": ref_file,
                        "classification": "uncertain", "supports_task": False}), 500


@app.route("/api/tasks/phase2/<name>", methods=["POST"])
def api_tasks_phase2(name):
    """Phase-2: epoch alignment (2-1) then task synthesis + self-check (2-2)."""
    if name in EXCLUDE_DIRS or ".." in name:
        abort(400)
    data = request.get_json(silent=True) or {}
    # Accept both supporting (old) and extractions (new)
    extractions = data.get("extractions", data.get("supporting", []))

    analysis_md = ""
    analysis_path = DATASET_DIR / name / "analysis.md"
    if analysis_path.exists():
        analysis_md = analysis_path.read_text(encoding="utf-8", errors="replace")

    category  = _category_from_md(analysis_md)
    skill_text = _load_skill(category)

    # ── Phase-2-1: epoch alignment ────────────────────────────────────────────
    p21_result = None
    try:
        p21_msg = _build_p21_user_msg(name, analysis_md, skill_text, extractions)
        p21_raw = _call_llm([
            {"role": "system", "content": _P21_SYSTEM},
            {"role": "user",   "content": p21_msg},
        ], timeout=120)
        p21_result, _ = _parse_llm_json(p21_raw)
    except Exception:
        pass  # Non-fatal: Phase-2-2 will proceed without alignment hint

    # ── Phase-2-2: synthesis + self-check ────────────────────────────────────
    p22_msg = _build_p22_user_msg(name, analysis_md, extractions, p21_result, skill_text)
    try:
        p22_raw = _call_llm([
            {"role": "system", "content": _P22_SYSTEM},
            {"role": "user",   "content": p22_msg},
        ], timeout=300)
        parsed, err = _parse_llm_json(p22_raw)
        if parsed is None:
            # Fallback: extract tasks_section from raw markdown
            stripped = re.sub(r"<think>[\s\S]*?</think>", "", p22_raw,
                              flags=re.IGNORECASE).strip()
            m = re.search(r"(##\s*Tasks[\s\S]+)", stripped)
            if m:
                ts = m.group(1).strip()
                return jsonify({"tasks_section": ts,
                                "num_classical_tasks": -1, "num_potential_tasks": -1,
                                "p21": p21_result, "summary": "",
                                "semantic_errors": _check_tasks_fragment(ts, name)})
            m2 = re.search(r"(###\s+(?:Classical|Potential)\s+Task[\s\S]+)", stripped)
            if m2:
                ts = "## Tasks\n\n" + m2.group(1).strip()
                return jsonify({"tasks_section": ts,
                                "num_classical_tasks": -1, "num_potential_tasks": -1,
                                "p21": p21_result, "summary": "",
                                "semantic_errors": _check_tasks_fragment(ts, name)})
            return jsonify({"error": f"Phase-2-2 parse failed: {err}",
                            "p21": p21_result}), 502

        parsed["p21"] = p21_result
        if isinstance(parsed, dict) and parsed.get("tasks_section"):
            parsed["semantic_errors"] = _check_tasks_fragment(
                parsed["tasks_section"], name, analysis_md=analysis_md
            )
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e), "p21": p21_result}), 500


if __name__ == "__main__":
    print("EEG Audit Tool running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
