"""Phase 7: Generate complete analysis.md and write the final document."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

try:
    from ..paths import DATASET_DOCUMENT_DIR
except ImportError:
    from paths import DATASET_DOCUMENT_DIR

try:
    from .file_scan_result_builder import build_file_scan_result_block, collect_scan_semantics
except ImportError:
    from file_scan_result_builder import build_file_scan_result_block, collect_scan_semantics


_ANALYSIS_SYSTEM = """\
You are an EEG dataset documentation expert. Write a complete analysis.md file for the given dataset.

The file must have exactly this structure (5 top-level ## sections, in this exact order):

```
# <Dataset Full Name>

**Dataset**: `<dataset_name>` | **Year**: <year> | **URL**: <url>
**Category**: <category> | **Subjects**: <n> | **Files (Completed)**: <n> | **Channels**: <n> | **Sampling Rate**: <hz> Hz | **Manual Review**:

## Paradigm

<2-4 sentences describing the experimental paradigm, subjects, tasks, equipment>

## File Scan Result

<INSERT the File Scan Result block provided below AS-IS. Do NOT modify.>

## Tasks

<INSERT the tasks_section provided below AS-IS. Do NOT modify.>

## Data Quality Notes

<Bullet points using "- " prefix. Note data quality issues, conflicts, or limitations.
If no issues are known, write exactly: "- No known data quality issues.">

## Kernel Responsibilities

<INSERT the Kernel Responsibilities block provided below AS-IS. Do NOT modify.>
```

RULES:
1. The ## File Scan Result, ## Tasks, and ## Kernel Responsibilities blocks are provided
   pre-built. Copy each exactly - do NOT alter any content in these sections.
2. You write ONLY: the # heading + meta area, ## Paradigm, ## Data Quality Notes.
3. ## Data Quality Notes must use "- " bullet format for every line of content.
4. Do NOT add any extra ## sections beyond these 5.
5. Do NOT invent event IDs, counts, or meanings not present in the provided data.
6. <category> MUST be exactly one of these 6 values (copy verbatim, no other strings allowed):
   "Action/Output"    — motor imagery, BCI task, movement, key-press, finger/hand execution, reaction
   "High-level Mental" — emotion recognition, cognitive load, mental workload, attention, meditation, memory
   "Sensory/Response" — SSVEP, auditory ERP, visual ERP, N400, MMN, steady-state or evoked potentials
   "Complex Applied"  — multi-paradigm or applied BCI combining more than one of the above
   "Biological State" — sleep staging, seizure/epilepsy detection, clinical disorder monitoring
   "Others"           — does not clearly fit any category above

Output ONLY valid JSON:
{
  "analysis_md": "<complete markdown content as a single string, \\n for newlines>",
  "reasoning": "<1-2 sentences>"
}"""


_SCAN_NOTE_SYSTEM = """\
You are an EEG metadata note annotator.

Your job is to fill ONLY:
- MISC Label Summary -> Notes
- Info -> Notes

STRICT RULES:
1. Use only the raw scan summaries and local dataset evidence snippets provided.
2. Do NOT use prior analysis documents, domain conventions, or invented assumptions.
3. If the evidence is insufficient for a field, return an empty string for that field.
4. Do NOT change field names. Do NOT add extra fields.

Output ONLY valid JSON:
{
  "misc_notes": {"channel_name": "short note or empty string"},
  "info_notes": {"field_name": "short note or empty string"}
}"""


def _truncate_text(text: str, limit: int = 1800) -> str:
    text = str(text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def _collect_evidence_snippets(bids_sidecars: Optional[Dict[str, Any]]) -> str:
    if not bids_sidecars:
        return "(none)"

    snippets = []
    direct_keys = ("dataset_description", "eeg_json", "readme", "participants_tsv_sample")
    for key in direct_keys:
        value = bids_sidecars.get(key)
        if value:
            snippets.append(f"=== {key} ===\n{_truncate_text(value)}")

    for key in ("events_jsons", "events_tsv_samples"):
        value = bids_sidecars.get(key) or {}
        if not isinstance(value, dict):
            continue
        for name, content in list(value.items())[:3]:
            snippets.append(f"=== {name} ===\n{_truncate_text(content, 1200)}")

    return "\n\n".join(snippets) if snippets else "(none)"


def _annotate_scan_notes(
    scan_result: Dict[str, Any],
    bids_sidecars: Optional[Dict[str, Any]],
    call_llm,
    budget,
    log,
) -> tuple[Dict[str, str], Dict[str, str]]:
    from .ref_analyzer import _parse_json

    info_stats, _, kernel_misc_hints = collect_scan_semantics(scan_result["df"])
    misc_targets = [
        {
            "channel": channel,
            "source": kernel_misc_hints.get(channel, {}).get("source", "native (raw misc in EEG file)"),
            "meta_level": kernel_misc_hints.get(channel, {}).get("meta_level", "raw"),
        }
        for channel in sorted(scan_result.get("misc_channel_names", []) or [])
        if not str(kernel_misc_hints.get(channel, {}).get("notes", "")).strip()
    ]
    info_targets = [
        {
            "field": field,
            "samples": list(info_stats[field].get("samples", [])),
            "count": int(info_stats[field].get("count", 0)),
            "seen": int(info_stats[field].get("seen", 0)),
        }
        for field in sorted(info_stats)
    ]

    if not misc_targets and not info_targets:
        return {}, {}

    user_msg = (
        "Use the following raw-truth summaries to annotate Notes only.\n\n"
        f"=== MISC targets ===\n{json.dumps(misc_targets, ensure_ascii=False, indent=2)}\n\n"
        f"=== Info targets ===\n{json.dumps(info_targets, ensure_ascii=False, indent=2)}\n\n"
        f"=== Local dataset evidence ===\n{_collect_evidence_snippets(bids_sidecars)}"
    )

    budget.charge("scan_notes")
    raw = call_llm(
        [
            {"role": "system", "content": _SCAN_NOTE_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        timeout=180,
    )
    result = _parse_json(raw) or {}
    misc_allowed = {item["channel"] for item in misc_targets}
    info_allowed = {item["field"] for item in info_targets}

    misc_notes = {
        str(k).strip(): str(v).strip()
        for k, v in (result.get("misc_notes") or {}).items()
        if str(k).strip() in misc_allowed and str(v).strip()
    }
    info_notes = {
        str(k).strip(): str(v).strip()
        for k, v in (result.get("info_notes") or {}).items()
        if str(k).strip() in info_allowed and str(v).strip()
    }
    log(
        "[DocWriter] Scan notes annotated: "
        f"misc={sorted(misc_notes) or []}, info={sorted(info_notes) or []}"
    )
    return misc_notes, info_notes


def _build_kr_block(super_meta_required: str, status: str) -> str:
    """Build the ## Kernel Responsibilities blockquote section programmatically."""
    return (
        "## Kernel Responsibilities\n\n"
        f"> **Super Meta Required**: {super_meta_required}\n"
        f"> **Status**: {status}"
    )


_VALID_CATEGORIES = (
    "Action/Output", "High-level Mental", "Sensory/Response",
    "Complex Applied", "Biological State", "Others",
)


def _enforce_manual_review_blank(analysis_md: str) -> str:
    """Force the Manual Review field to be blank."""
    return re.sub(
        r"\*\*Manual Review\*\*:[^\n]*",
        "**Manual Review**:",
        analysis_md,
    )


def _enforce_category_fallback(analysis_md: str) -> tuple[str, bool]:
    """If Category is blank or not one of the 6 valid values, set it to 'Others'.

    Returns (new_md, was_changed). This is a last-resort guard — the LLM prompt
    already lists valid values, but scan failures or LLM refusals can leave the
    field blank, which triggers the category_valid_value detect error.
    """
    m = re.search(r"\*\*Category\*\*:\s*([^|*\n]*)", analysis_md)
    if not m:
        return analysis_md, False
    current = m.group(1).strip()
    if current in _VALID_CATEGORIES:
        return analysis_md, False
    new_md = re.sub(
        r"(\*\*Category\*\*:)\s*[^|*\n]*",
        r"\1 Others ",  # trailing space preserves ' | ' separator
        analysis_md,
        count=1,
    )
    return new_md, True


def _enforce_kr_block(analysis_md: str, kr_block: str) -> str:
    """Replace the ## Kernel Responsibilities section with the pre-built block."""
    m = re.search(r"^## Kernel Responsibilities\s*$", analysis_md, re.MULTILINE)
    if not m:
        return analysis_md.rstrip() + "\n\n" + kr_block + "\n"
    start = m.start()
    next_section = re.search(r"^## ", analysis_md[m.end():], re.MULTILINE)
    if next_section:
        end = m.end() + next_section.start()
    else:
        end = len(analysis_md)
    return analysis_md[:start] + kr_block + "\n" + analysis_md[end:]


def _detect_super_meta(tasks_section: str) -> str:
    """Return 'Yes' if any task has Meta Level = super, else 'No'."""
    if re.search(r"\*\*Meta Level\*\*:\s*super\b", tasks_section, re.IGNORECASE):
        return "Yes"
    if re.search(r"\|\s*Meta Level\s*\|\s*super\s*\|", tasks_section, re.IGNORECASE):
        return "Yes"
    return "No"


def generate_analysis_md(
    dataset_name: str,
    context: Dict[str, Any],
    scan_result: Dict[str, Any],
    tasks_section: str,
    kernel_path: str,
    call_llm,
    budget,
    log,
    bids_sidecars: Optional[Dict] = None,
    event_annotations: Optional[Dict] = None,
    status: str = "wait_manual_review",
) -> str:
    """Generate the full analysis.md using LLM."""
    from .ref_analyzer import _parse_json

    log("[DocWriter] Generating complete analysis.md...")

    misc_notes, info_notes = _annotate_scan_notes(
        scan_result,
        bids_sidecars,
        call_llm,
        budget,
        log,
    )
    file_scan_block, _ = build_file_scan_result_block(
        scan_result,
        event_annotations=event_annotations,
        misc_note_map=misc_notes,
        info_note_map=info_notes,
    )

    super_meta = _detect_super_meta(tasks_section)
    kr_block = _build_kr_block(super_meta, status)
    log(f"[DocWriter] KR block: Super Meta Required={super_meta}, Status={status}")

    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Existing analysis.md draft (reference for metadata only) ===\n"
        f"{context['analysis_md'][:4000]}\n\n"
        f"=== File Scan Result block (COPY AS-IS into ## File Scan Result) ===\n"
        f"{file_scan_block}\n\n"
        f"=== Tasks section (COPY AS-IS into ## Tasks) ===\n{tasks_section}\n\n"
        f"=== Kernel Responsibilities block (COPY AS-IS into ## Kernel Responsibilities) ===\n"
        f"{kr_block}\n\n"
        "Now write the complete analysis.md.\n"
        "Use the existing draft only as a reference for metadata (year, URL, category, subjects, etc).\n"
        "The File Scan Result, Tasks, and Kernel Responsibilities blocks above are authoritative - copy them unchanged."
    )

    budget.charge("doc_write")
    raw = call_llm([
        {"role": "system", "content": _ANALYSIS_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {}
    analysis_md = result.get("analysis_md", "")

    if not analysis_md:
        log("[DocWriter] WARNING: LLM returned empty analysis_md, using template fallback.")
        analysis_md = _fallback_analysis_md(
            dataset_name, context["analysis_md"], scan_result,
            tasks_section, file_scan_block, kr_block,
        )

    analysis_md = _enforce_kr_block(analysis_md, kr_block)
    before_mr = analysis_md
    analysis_md = _enforce_manual_review_blank(analysis_md)
    if analysis_md != before_mr:
        log("[DocWriter] Manual Review field was non-blank; forced to blank.")

    analysis_md, cat_fixed = _enforce_category_fallback(analysis_md)
    if cat_fixed:
        log("[DocWriter] Category was blank/invalid; defaulted to 'Others'.")

    log(f"[DocWriter] analysis.md: {len(analysis_md)} chars")
    return analysis_md


def merge_and_write(
    dataset_name: str,
    analysis_md_new: str,
    scan_result: Dict[str, Any],
    log,
    bids_sidecars: Optional[Dict] = None,
) -> str:
    """Write the final authoritative analysis.md content to disk."""
    out_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"
    out_path.write_text(analysis_md_new, encoding="utf-8")
    log(f"[DocWriter] Written: {out_path} ({len(analysis_md_new)} chars)")
    return analysis_md_new


def write_failed_analysis(
    dataset_name: str,
    existing_md: str,
    reason: str,
    log,
) -> None:
    """Write a FAILED-status analysis.md preserving existing content."""
    if existing_md.strip():
        content = existing_md
    else:
        kr_block = _build_kr_block("No", "wait_manual_review")
        content = (
            f"# {dataset_name}\n\n"
            f"**Dataset**: `{dataset_name}` | **Year**:  | **URL**: \n"
            f"**Category**: Others | **Subjects**:  | **Files (Completed)**:  | **Channels**:  | **Sampling Rate**:  | **Manual Review**:\n\n"
            f"## Paradigm\n\n(Pending)\n\n"
            f"## File Scan Result\n\n"
            f"> **Kernel SHA256**: `N/A`\n"
            f"> **EEGUnity Version**: `N/A`\n"
            f"> **Scan Type**: N/A\n\n"
            f"### Event Structure\n\n"
            f"| Event ID | Count (total) | Type | Meta Level | Meaning |\n"
            f"|---|---|---|---|---|\n\n"
            f"### Info\n\n"
            f"| Field | Completeness | Notes |\n"
            f"|---|---|---|\n\n"
            f"## Tasks\n\n(No tasks synthesized)\n\n"
            f"## Data Quality Notes\n\n- Pipeline failed - no quality assessment available.\n\n"
            f"{kr_block}\n"
        )

    content = content.rstrip() + f"\n\n---\n\n> **Pipeline FAILED**: {reason}\n"

    out_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"
    out_path.write_text(content, encoding="utf-8")
    log(f"[DocWriter] FAILED analysis.md written: {out_path}")


def _fallback_analysis_md(
    dataset_name,
    existing_md,
    scan_result,
    tasks_section,
    file_scan_block,
    kr_block,
) -> str:
    """Simple string-based fallback when LLM fails to produce doc."""
    header_match = re.match(r"(#[^\n]+\n(?:[^\n]*\n){0,4})", existing_md)
    header = header_match.group(1) if header_match else (
        f"# {dataset_name}\n\n"
        f"**Dataset**: `{dataset_name}` | **Year**:  | **URL**: \n"
        f"**Category**:  | **Subjects**:  | **Files (Completed)**:  | **Channels**:  | **Sampling Rate**:  | **Manual Review**:\n"
    )

    return (
        f"{header}\n"
        "## Paradigm\n\n(See existing draft)\n\n"
        f"{file_scan_block}\n\n"
        f"{tasks_section}\n\n"
        "## Data Quality Notes\n\n- No quality assessment available (LLM fallback).\n\n"
        f"{kr_block}\n"
    )
