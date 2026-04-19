"""Phase 3+4: Feasibility judgement and task synthesis."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from .ref_analyzer import _parse_json


_FEASIBILITY_SYSTEM = """\
You are an EEG dataset feasibility analyst. Given a dataset description and a list of
reference paper extractions, decide whether this dataset supports a concrete ML task.

Output ONLY valid JSON:
{
  "feasible": true|false,
  "reason": "<1-3 sentences explaining the decision>",
  "useful_refs": ["<filename1>", "<filename2>"],
  "task_hint": "<very brief description of what task is possible, or empty if not feasible>"
}

feasible = true if the dataset has identifiable event/label structure that supports ANY
meaningful EEG classification or regression task. This includes but is not limited to:
motor imagery, P300, SSVEP, emotion, sleep staging, cognitive load, phase detection, etc.

A dataset with trial phase markers (rest/ready/task/interval) IS feasible — the markers
themselves define a classifiable structure (e.g. task-state vs rest, or multi-phase
detection). Do NOT reject a dataset merely because its events are phase markers rather
than class labels.

If no references exist at all but the dataset is a well-known public EEG dataset with a
clear paradigm, feasible may still be true based on analysis.md alone.

ANTI-HALLUCINATION RULES:
1. If events.tsv samples show a 'value'→'instruction'/'trial_type' mapping, that mapping
   is GROUND TRUTH. Do not override it with assumptions from BCI conventions or paper claims.
2. If a paper describes a COLLECTION of datasets, do NOT assume all paradigm details
   apply to THIS specific dataset. Match by dataset name/ID carefully.
3. Base your task_hint on what the ACTUAL event structure supports, not on what the
   existing analysis.md claims. The analysis.md may contain errors from a prior run.
"""


_EPOCH_ALIGNMENT_SYSTEM = """\
You are an EEG preprocessing expert. Given a dataset's description and event structure,
determine the correct epoch alignment and recommended parameters.

Output ONLY valid JSON:
{
  "alignment": "onset|offset|mixed|unclear",
  "cue_duration_s": null,
  "recommendations": [
    {
      "paradigm_label": "<short name>",
      "epoch_method": "epoch_by_event_hdf5|epoch_by_long_event_hdf5|epoch_by_segmentation_hdf5",
      "tmin": 0.0,
      "tmax": 4.0,
      "overlap": null,
      "segment_length": null,
      "reasoning": "<2-3 sentences>"
    }
  ],
  "complications": "",
  "kernel_notes": ""
}"""


_TASK_SYNTHESIS_SYSTEM = """\
You are an EEG machine learning task documentation expert.
Write the complete "## Tasks" section of an analysis.md file.

=== Task Template v3 (MUST follow this exact bullet-list format) ===
### Classical Task N: <concise name>
- **Task Type**: classification | regression
- **Epoch Method**: `epoch_by_event_hdf5 | epoch_by_long_event_hdf5 | epoch_by_segmentation_hdf5`
- **Epoch Parameters**: <minimum required keys per method — see Epoch Parameters rules below>
- **Label Route**: `event | misc | info`
- **Label Field**: `<channel_or_column_name>`     # ONLY when Label Route ∈ {misc, info}
- **Meta Level**: raw | super
- **Target Definition**:
  <route-specific table — see schema matrix below>
- **Evidence**:
  - DOI: <doi_or_ref> — <description>
- **Notes**: <free-form task annotation; recommended for super-meta derivation steps and parameter-inference rationale>

=== Epoch Parameters rules (MANDATORY — detect.py rule epoch_parameters_complete, severity=error) ===
Every Task MUST list AT LEAST these keys in Epoch Parameters for its declared Epoch Method:
  * epoch_by_event_hdf5       — tmin, tmax, target_events
  * epoch_by_long_event_hdf5  — tmin, tmax, overlap, target_events
  * epoch_by_segmentation_hdf5 — segment_length, overlap (target_events MUST be [])
Format examples:
  epoch_by_event_hdf5:       `tmin = 0 s, tmax = 3 s, target_events = [\`left\`, \`right\`]`
  epoch_by_long_event_hdf5:  `tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [\`rest\`]`
  epoch_by_segmentation_hdf5: `segment_length = 4 s, overlap = 0.5, target_events = []`
Additional MNE.Epoch parameters (e.g. baseline, reject, picks) are allowed as extra `key = value` pairs.
If you do not have ground-truth values for the required keys, DROP the task — do not leave them blank or placeholder.

=== Three Task Archetypes (choose one per task) ===

ARCHETYPE A — Event is the label
  Example: left_target → class 0, right_target → class 1
  Route=event, Meta Level=raw (usually), NO Label Field bullet

ARCHETYPE B — Event anchors the epoch, label lives elsewhere
  B1 — Native misc: label = numeric column of events.tsv (e.g. `response_time`, `correct`)
       Route=misc, Meta Level=raw, Label Field = column name, Task Type=regression
  B2 — Derived misc: label = derived from participants.tsv (e.g. `p_factor`, clinical score)
       Route=misc, Meta Level=super, Label Field = new misc channel name, Task Type=regression
  B3 — Native info: label = raw participants.tsv column used directly (e.g. `subject_sex`)
       Route=info, Meta Level=raw, Label Field = column name

ARCHETYPE C — No event; segmentation + subject-level label
  Epoch Method = epoch_by_segmentation_hdf5; target_events = [] (empty)
  Label Route = misc (derived) or info (native). Same Label Field rules as above.

=== Target Definition schema matrix (Route × Task Type) ===

  Label Route    Task Type           Table columns
  ─────────────────────────────────────────────────────────────────
  event          classification      | Event ID | y | Meaning |
  event          regression          | Event ID | Value | Meaning |   (rare)
  misc           regression          | MISC Channel | Value (unit) | Notes |
  misc           classification      FORBIDDEN — use event or info instead
  info           classification      | Info Field | Value | y | Meaning |
  info           regression          | Info Field | Range (unit) | Notes |

=== HARD RULES (violations will be stripped by post-synthesis guards) ===
1. ONE LABEL FIELD PER TASK. Multi-dimension labels (e.g. 4 psychopathology factors)
   MUST be split into N separate tasks — one per Label Field.
2. CLASSIFICATION ≥ 2 DISTINCT y VALUES. A classification task with only one class in
   Target Definition is invalid. Either convert to regression, reframe with a contrastive
   class (e.g. stimulus vs baseline/rest), or DROP the task.
3. misc ROUTE IS REGRESSION-ONLY. If you want discrete labels from a misc value, put
   the derivation into the kernel and use Route=info or Route=event.
4. LABEL FIELD REQUIRED iff Route ∈ {misc, info}; FORBIDDEN when Route=event.
5. DERIVED MISC ⇒ Meta Level=super. Notes SHOULD describe the derivation step
   (how the kernel creates the misc channel from participants.tsv or elsewhere).
   (Recommended, not enforced by detect.py — the Notes field is freeform.)
6. GROUND TRUTH: If the Label Field is not present in events.tsv numeric columns,
   participants.tsv columns, OR the native misc channel list provided below, DROP the task.
   Do not invent fields.
7. segmentation ⇒ target_events = [].

=== Task type classification ===
- "Classical Task": ≥1 reference with classification=relevant AND a real DOI/URL ref.
- "Potential Task": partial references, or plausible from paradigm alone.
- ALL Classical Tasks before all Potential Tasks.
- Numbering starts at 1 within each type.

=== Format rules ===
- Each field: "- **Field**: value" bullet (NOT a wrapping markdown table).
- Target Definition table MUST be indented 2 spaces under "- **Target Definition**:".
- Evidence entries MUST be indented 2 spaces: "  - DOI: ref — description".

=== Anti-hallucination ===
1. events.tsv value→instruction mapping is GROUND TRUTH; do not override with BCI convention.
2. NEVER assign MI class labels (left/right hand, feet, tongue) unless events.tsv/json/README
   explicitly says so.
3. Phase markers (rest/ready/task/interval) are phase markers, not MI classes — but they
   CAN form valid binary tasks (rest vs task state), just label them for what they are.

Output ONLY valid JSON:
{
  "tasks_section": "## Tasks\\n\\n### Classical Task 1: ...\\n\\n...",
  "num_classical_tasks": 0,
  "num_potential_tasks": 0,
  "reasoning": "<2-3 sentences summarizing key decisions>"
}"""


def _format_bids_sidecars(bids_sidecars: Dict) -> str:
    """Format BIDS sidecar data as a readable block for LLM prompts."""
    if not bids_sidecars:
        return ""
    parts = ["=== BIDS Sidecar Data (Evidence Level ① — highest priority) ==="]

    if "participants_summary" in bids_sidecars:
        parts.append(f"\n[participants.tsv summary]\n{bids_sidecars['participants_summary']}")
    if "participants_tsv_sample" in bids_sidecars:
        parts.append(f"\n[participants.tsv sample (first rows)]\n{bids_sidecars['participants_tsv_sample']}")
    if "dataset_description" in bids_sidecars:
        parts.append(f"\n[dataset_description.json]\n{bids_sidecars['dataset_description'][:1000]}")
    if "events_jsons" in bids_sidecars:
        for fname, content in bids_sidecars["events_jsons"].items():
            parts.append(f"\n[{fname} — column definitions]\n{content[:2000]}")
    if "events_tsv_samples" in bids_sidecars:
        parts.append(
            "\n[events.tsv samples — AUTHORITATIVE: these are the ACTUAL trigger values and their meanings.\n"
            "Use the 'value' and 'instruction'/'trial_type'/'description' columns to determine what each\n"
            "trigger code means. Do NOT infer meanings from BCI convention or prior knowledge.]"
        )
        for fname, content in bids_sidecars["events_tsv_samples"].items():
            parts.append(f"\n  [{fname}]\n{content}")
    if "eeg_json" in bids_sidecars:
        parts.append(f"\n[eeg.json (device info)]\n{bids_sidecars['eeg_json'][:800]}")
    if "readme" in bids_sidecars:
        parts.append(f"\n[README]\n{bids_sidecars['readme'][:1500]}")

    return "\n".join(parts)


def _collect_grounded_label_fields(
    bids_sidecars: Optional[Dict],
    misc_channel_names: Optional[List[str]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Aggregate the per-route catalog of grounded Label Field candidates.

    Returns dict with keys: participants, events_numeric, misc_native.
    """
    bs = bids_sidecars or {}
    participants = list(bs.get("participants_fields", []) or [])
    events_numeric: List[Dict[str, Any]] = []
    for fname, cols in (bs.get("events_numeric_columns") or {}).items():
        for c in cols:
            events_numeric.append({"name": c, "found_in": fname})
    misc_native = []
    for name in misc_channel_names or []:
        if name and isinstance(name, str):
            misc_native.append({"name": name})
    return {
        "participants": participants,
        "events_numeric": events_numeric,
        "misc_native": misc_native,
    }


def _format_grounded_label_fields(grounded: Dict[str, List[Dict[str, Any]]]) -> str:
    """Format the grounded Label Field catalog for the synthesis prompt."""
    parts = [
        "=== GROUNDED LABEL FIELD CATALOG — ONLY SOURCES ALLOWED ===",
        "Every Task's Label Field MUST be drawn from one of the three lists below.",
        "If the label you want does not appear here, you MUST DROP the task.",
        "",
    ]

    parts.append("[participants.tsv columns — info route (native), or misc route (derived)]")
    if grounded["participants"]:
        for f in grounded["participants"]:
            sv = ", ".join(str(x) for x in (f.get("sample_values") or [])[:3])
            parts.append(
                f"  - {f['name']}  (dtype={f.get('dtype','?')}, "
                f"completeness={f.get('completeness','?')}, sample=[{sv}])"
            )
    else:
        parts.append("  (none discovered — info route and derived misc unavailable)")
    parts.append("")

    parts.append("[events.tsv numeric columns — misc route native (regression only)]")
    if grounded["events_numeric"]:
        for f in grounded["events_numeric"]:
            parts.append(f"  - {f['name']}  (found_in={f.get('found_in','?')})")
    else:
        parts.append("  (none discovered — native misc from events.tsv unavailable)")
    parts.append("")

    parts.append("[Native misc channels — misc route native (regression only)]")
    if grounded["misc_native"]:
        for f in grounded["misc_native"]:
            parts.append(f"  - {f['name']}")
    else:
        parts.append("  (none discovered in raw files)")

    return "\n".join(parts)


def judge_feasibility(
    dataset_name: str,
    analysis_md: str,
    ref_extractions: List[Dict],
    call_llm,
    budget,
    log,
    bids_sidecars: Optional[Dict] = None,
) -> Tuple[bool, str]:
    """Returns (feasible, reason)."""
    log("[TaskSynth] Judging feasibility...")

    extractions_summary = json.dumps([
        {k: v for k, v in e.items() if k in (
            "filename", "classification", "supports_task", "paradigm",
            "task_type", "n_classes", "evidence_desc", "ref"
        )}
        for e in ref_extractions
    ], indent=2)

    sidecar_block = _format_bids_sidecars(bids_sidecars or {})

    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"=== analysis.md excerpt ===\n{analysis_md[:3000]}\n\n"
        + (f"{sidecar_block}\n\n" if sidecar_block else "")
        + f"=== Reference extractions ===\n{extractions_summary}"
    )

    budget.charge("feasibility")
    raw = call_llm([
        {"role": "system", "content": _FEASIBILITY_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {}
    feasible = bool(result.get("feasible", False))
    reason = result.get("reason", "No reason provided.")
    log(f"[TaskSynth] Feasible: {feasible} — {reason}")
    return feasible, reason


def _get_phase_marker_event_ids(event_annotations: Optional[Dict]) -> set:
    """Return the set of event_ids confirmed as trial phase markers.

    Only includes events whose Meaning indicates a trial phase transition
    (rest/ready/task/interval). Does NOT include stimulus markers (cue/feedback)
    or system markers, since those can legitimately form classification targets.
    """
    if not event_annotations:
        return set()
    phase_ids = set()
    for ann in event_annotations.get("annotations", []):
        meaning = ann.get("meaning", "").lower()
        if any(kw in meaning for kw in ("trial phase", "phase onset", "rest", "ready",
                                        "task onset", "interval", "fixation",
                                        "baseline", "inter-trial")):
            if ann.get("event_type", "") in ("event", "annotation", "stim", ""):
                phase_ids.add(ann["event_id"])
    return phase_ids


def _strip_hallucinated_mi_tasks(tasks_section: str, phase_marker_ids: set, log) -> str:
    """
    Post-synthesis guard: fully remove tasks whose Target Definition assigns MI class labels
    to event IDs that are locked as trial phase markers, then renumber remaining tasks.
    """
    if not phase_marker_ids:
        return tasks_section

    mi_class_keywords = re.compile(
        r"\b(left hand|right hand|feet|tongue|motor imagery|mi class|hand mi|feet mi|tongue mi)\b",
        re.IGNORECASE,
    )

    # Split into task blocks at ### boundaries
    blocks = re.split(r"(?=###\s)", tasks_section)
    result_blocks = []
    removed_count = 0

    for block in blocks:
        if not block.strip().startswith("###"):
            result_blocks.append(block)
            continue

        # Find all event_id references in the Target Definition table rows
        table_rows = re.findall(r"\|\s*`?(event_\w+)`?\s*\|([^|]*)\|([^|]*)\|", block)

        flagged = False
        for eid, y_col, meaning_col in table_rows:
            if eid in phase_marker_ids and mi_class_keywords.search(meaning_col + y_col):
                flagged = True
                log(f"[TaskSynth][Guard] Removing task: {eid} locked as phase marker "
                    f"but assigned MI class label: '{meaning_col.strip()}'")
                break

        if flagged:
            removed_count += 1
        else:
            result_blocks.append(block)

    if removed_count:
        log(f"[TaskSynth][Guard] Removed {removed_count} task(s) with hallucinated MI class labels.")

    result = "".join(result_blocks)

    # Renumber tasks within each type (Classical: 1,2,...; Potential: 1,2,...)
    if removed_count:
        result = _renumber_tasks(result)

    return result


def _renumber_tasks(tasks_section: str) -> str:
    """Renumber task headings so each type starts from 1 consecutively."""
    counters = {"Classical": 0, "Potential": 0}

    def _repl(m):
        kind = m.group(1)
        counters[kind] += 1
        return f"### {kind} Task {counters[kind]}:{m.group(3)}"

    return re.sub(
        r"###\s+(Classical|Potential)\s+Task\s+(\d+):(.*)",
        _repl, tasks_section,
    )


def _split_task_blocks(tasks_section: str) -> Tuple[str, List[str]]:
    """Split tasks_section into (prefix_before_first_task, [task_blocks])."""
    parts = re.split(r"(?=###\s)", tasks_section)
    prefix = ""
    blocks: List[str] = []
    for p in parts:
        if p.lstrip().startswith("###"):
            blocks.append(p)
        else:
            prefix += p
    return prefix, blocks


def _get_task_field(block: str, field_name: str) -> Optional[str]:
    """Return the RHS of `- **Field**: value` bullet, or None."""
    m = re.search(
        rf"-\s*\*\*{re.escape(field_name)}\*\*\s*:\s*(.+)",
        block,
    )
    if not m:
        return None
    return m.group(1).strip()


def _get_task_title(block: str) -> str:
    m = re.search(r"###\s+(.+)", block)
    return m.group(1).strip() if m else "(unnamed)"


def _extract_target_def_rows(block: str) -> List[List[str]]:
    """Extract table rows from the Target Definition subtable. Returns list of cell lists.

    Skips header and separator rows. Each row is the list of trimmed cell strings.
    """
    rows: List[List[str]] = []
    lines = block.splitlines()
    in_td = False
    seen_header = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- **Target Definition**"):
            in_td = True
            seen_header = False
            continue
        if in_td:
            if stripped.startswith("- **") and not stripped.startswith("|"):
                in_td = False
                continue
            if stripped.startswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                # Skip the separator row (cells like ---, :---:)
                if all(re.fullmatch(r":?-+:?", c or "") for c in cells if c):
                    continue
                if not seen_header:
                    seen_header = True
                    continue
                rows.append(cells)
            elif stripped == "":
                continue
            else:
                # Non-table content inside TD — treat as end
                if seen_header:
                    in_td = False
    return rows


def _strip_single_class_classifications(tasks_section: str, log) -> str:
    """Drop classification tasks whose Target Definition contains <2 distinct y values."""
    prefix, blocks = _split_task_blocks(tasks_section)
    if not blocks:
        return tasks_section
    kept: List[str] = []
    removed = 0
    for block in blocks:
        task_type = (_get_task_field(block, "Task Type") or "").lower()
        if "classification" not in task_type:
            kept.append(block)
            continue
        route = (_get_task_field(block, "Label Route") or "").strip("`").lower()
        rows = _extract_target_def_rows(block)
        if not rows:
            kept.append(block)
            continue
        # y column position depends on route
        # event classification:  | Event ID | y | Meaning |         y at col idx 1
        # info  classification:  | Info Field | Value | y | Meaning |  y at col idx 2
        y_idx = 2 if route == "info" else 1
        y_values = set()
        for r in rows:
            if y_idx < len(r):
                v = r[y_idx]
                if v:
                    y_values.add(v)
        if len(y_values) < 2:
            removed += 1
            log(
                f"[TaskSynth][Guard] Dropping '{_get_task_title(block)}' — "
                f"classification with <2 distinct y values (found: {sorted(y_values) or 'empty'})."
            )
            continue
        kept.append(block)

    if removed:
        result = prefix + "".join(kept)
        return _renumber_tasks(result)
    return tasks_section


def _strip_ungrounded_label_fields(
    tasks_section: str,
    grounded: Dict[str, List[Dict[str, Any]]],
    log,
) -> str:
    """Drop Tasks whose Label Field is not present in any grounded source.

    Only applied to Route ∈ {misc, info}. Route=event has no Label Field and is skipped.
    """
    grounded_names = set()
    for f in grounded.get("participants", []):
        grounded_names.add(f["name"])
    for f in grounded.get("events_numeric", []):
        grounded_names.add(f["name"])
    for f in grounded.get("misc_native", []):
        grounded_names.add(f["name"])

    prefix, blocks = _split_task_blocks(tasks_section)
    if not blocks:
        return tasks_section
    kept: List[str] = []
    removed = 0
    for block in blocks:
        route = (_get_task_field(block, "Label Route") or "").strip("`").lower()
        if route not in ("misc", "info"):
            kept.append(block)
            continue
        label_field_raw = _get_task_field(block, "Label Field")
        if not label_field_raw:
            # Missing Label Field for non-event route → detect.py will flag it;
            # keep the block so the rule can report the violation.
            kept.append(block)
            continue
        # Strip backticks / trailing descriptions
        lf = label_field_raw.strip().strip("`")
        lf = lf.split()[0] if lf else ""
        # For derived misc, the Label Field names a NEW channel, not an existing one —
        # but Notes (freeform) may describe the derivation. Accept the task if any
        # grounded name appears in Notes (preferred) or Kernel Notes (legacy docs).
        meta_level = (_get_task_field(block, "Meta Level") or "").strip("`").lower()
        notes_text = (
            _get_task_field(block, "Notes")
            or _get_task_field(block, "Kernel Notes")
            or ""
        )

        grounded_here = lf in grounded_names
        if (not grounded_here) and route == "misc" and meta_level == "super":
            # Allow derived misc if the derivation step names a grounded source
            for name in grounded_names:
                if re.search(rf"\b{re.escape(name)}\b", notes_text):
                    grounded_here = True
                    break

        if not grounded_here:
            removed += 1
            log(
                f"[TaskSynth][Guard] Dropping '{_get_task_title(block)}' — "
                f"Label Field '{lf}' not present in grounded sources and no derivation "
                f"mentions a grounded column."
            )
            continue
        kept.append(block)

    if removed:
        result = prefix + "".join(kept)
        return _renumber_tasks(result)
    return tasks_section


def _format_locked_meanings(event_annotations: Optional[Dict]) -> str:
    """Format P3b annotations as a locked Meanings block for LLM prompts."""
    if not event_annotations:
        return ""
    annotations = event_annotations.get("annotations", [])
    if not annotations:
        return ""
    lines = [
        "=== EVENT MEANINGS — LOCKED GROUND TRUTH (DO NOT REINTERPRET) ===",
        "These meanings were determined by reading the dataset's own sidecar files",
        "(events.tsv, events.json, README). They take priority over all other sources.",
        "",
    ]
    for ann in annotations:
        scope = ann.get("session_task_scope", "all")
        conf = ann.get("confidence", "?")
        lines.append(
            f"  {ann['event_id']}: {ann['meaning']}"
            f"  [type={ann['event_type']}, confidence={conf}, scope={scope}]"
        )
    lines += [
        "",
        "BINDING RULES:",
        "1. A Meaning that says 'Trial phase onset: rest/ready/task/interval' is a",
        "   TRIAL PHASE MARKER — it is NOT an MI class label. However, phase markers",
        "   CAN form valid classification tasks when labeled correctly (e.g. rest vs",
        "   task state detection). Just don't mislabel them as MI classes.",
        "2. Do NOT assign motor imagery class labels (left hand, right hand, feet,",
        "   tongue) to any event unless the Meaning above explicitly states that.",
        "3. These Meanings are final — do not rationalize overriding them.",
    ]
    notes = event_annotations.get("notes", "")
    if notes:
        lines += ["", f"Evidence summary: {notes}"]
    return "\n".join(lines)


def synthesize_tasks(
    dataset_name: str,
    analysis_md: str,
    ref_extractions: List[Dict],
    event_ids_preview: str,
    category_skill: str,
    call_llm,
    budget,
    log,
    bids_sidecars: Optional[Dict] = None,
    format_type: str = "unknown",
    eeg_header_summary: str = "",
    event_annotations: Optional[Dict] = None,
    misc_channel_names: Optional[List[str]] = None,
) -> str:
    """Run epoch alignment + task synthesis. Returns the '## Tasks' markdown string."""

    sidecar_block = _format_bids_sidecars(bids_sidecars or {})
    locked_meanings_block = _format_locked_meanings(event_annotations)
    grounded = _collect_grounded_label_fields(bids_sidecars, misc_channel_names)
    grounded_block = _format_grounded_label_fields(grounded)

    # Step A: epoch alignment
    log("[TaskSynth] Running epoch alignment analysis...")
    alignment_user = (
        f"Dataset: {dataset_name} (format: {format_type})\n\n"
        f"=== analysis.md ===\n{analysis_md[:4000]}\n\n"
        + (f"{sidecar_block}\n\n" if sidecar_block else "")
        + (f"=== EEG File Header Sample ===\n{eeg_header_summary}\n\n" if eeg_header_summary else "")
        + f"=== Category SKILL ===\n{category_skill[:2000]}\n\n"
        f"=== Available event IDs (from pre-scan) ===\n{event_ids_preview}"
        + (f"\n\n{locked_meanings_block}" if locked_meanings_block else "")
    )
    budget.charge("task_synthesis")
    alignment_raw = call_llm([
        {"role": "system", "content": _EPOCH_ALIGNMENT_SYSTEM},
        {"role": "user", "content": alignment_user},
    ])
    alignment = _parse_json(alignment_raw) or {}
    log(f"[TaskSynth] Alignment: {alignment.get('alignment')} | {len(alignment.get('recommendations', []))} paradigm(s)")

    # Step B: task synthesis
    log("[TaskSynth] Synthesizing tasks...")
    extractions_full = json.dumps([
        {k: v for k, v in e.items() if k not in ("cot_reasoning",)}
        for e in ref_extractions
        if e.get("classification") in ("relevant", "partial")
    ], indent=2)

    synthesis_user = (
        f"Dataset: {dataset_name} (format: {format_type})\n\n"
        f"=== analysis.md ===\n{analysis_md[:4000]}\n\n"
        + (f"{sidecar_block}\n\n" if sidecar_block else "")
        + (f"=== EEG File Header Sample ===\n{eeg_header_summary}\n\n" if eeg_header_summary else "")
        + f"=== Available event IDs (from pre-scan — USE THESE EXACT NAMES) ===\n{event_ids_preview}\n\n"
        f"IMPORTANT: Target Definition events MUST use the exact event IDs listed above.\n"
        f"If BIDS events.json defines meanings for these IDs, use that as the authoritative semantic definition.\n\n"
        + (f"{locked_meanings_block}\n\n" if locked_meanings_block else "")
        + f"{grounded_block}\n\n"
        + f"=== Epoch alignment recommendations ===\n{json.dumps(alignment, indent=2)}\n\n"
        f"=== Category SKILL ===\n{category_skill[:2000]}\n\n"
        f"=== Reference extractions (relevant/partial only) ===\n{extractions_full}"
    )

    budget.charge("task_synthesis")
    synthesis_raw = call_llm([
        {"role": "system", "content": _TASK_SYNTHESIS_SYSTEM},
        {"role": "user", "content": synthesis_user},
    ])
    result = _parse_json(synthesis_raw) or {}
    tasks_section = result.get("tasks_section", "## Tasks\n\n(No tasks could be synthesized.)")
    log(f"[TaskSynth] Tasks: {result.get('num_classical_tasks', 0)} classical, "
        f"{result.get('num_potential_tasks', 0)} potential")

    # Post-synthesis guard: strip tasks that hallucinate MI class labels onto phase markers
    phase_marker_ids = _get_phase_marker_event_ids(event_annotations)
    if phase_marker_ids:
        log(f"[TaskSynth][Guard] Phase marker IDs locked by P3b: {sorted(phase_marker_ids)}")
        tasks_section = _strip_hallucinated_mi_tasks(tasks_section, phase_marker_ids, log)

    # v3 guards: drop single-class classifications and Label Fields with no grounded source
    tasks_section = _strip_single_class_classifications(tasks_section, log)
    tasks_section = _strip_ungrounded_label_fields(tasks_section, grounded, log)

    return tasks_section
