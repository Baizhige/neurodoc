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

feasible = true only if at least one reference is 'relevant' or 'partial' AND the dataset
has identifiable event/label structure. If no references exist at all but the dataset is
a well-known public EEG dataset with a clear paradigm described in analysis.md, feasible
may still be true based on the analysis.md alone.

CRITICAL ANTI-HALLUCINATION RULES:
1. If events.tsv samples are provided, the 'value'→'instruction'/'trial_type' mapping is
   GROUND TRUTH. A trigger value that maps to "rest", "ready", "task", "interval" is a
   TRIAL PHASE MARKER — NOT a class label. Do not infer MI class from trigger numbers.
2. If a paper describes a COLLECTION of datasets (e.g. "4 datasets"), do NOT assume all
   paradigm details (e.g. 4-class MI) apply to THIS specific dataset. Read carefully which
   sub-dataset matches this dataset name/ID.
3. If the events.tsv shows only 2 distinct values (e.g. rest/task), this is likely a
   binary paradigm — do not invent additional classes from prior BCI knowledge.
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

Rules:
- "Classical Task": ≥1 reference with classification=relevant AND has a real DOI/URL ref.
- "Potential Task": supported by partial references, or plausible from paradigm alone (no ref required).
- "Normal Task": intermediate support (some evidence but not direct classification=relevant).
- Each task must have: Task Type, Epoch Method, Epoch Parameters, Label Route, Meta Level,
  Target Definition table (Event | y | Meaning), Evidence (DOI), Kernel Notes.
- Target Definition events MUST come from the actual event IDs listed.
- Multiple papers supporting same task → ONE task, all refs in Evidence.
- epoch_method values: epoch_by_event_hdf5 | epoch_by_long_event_hdf5 | epoch_by_segmentation_hdf5
- Label Route values: event | Annotation | misc | stim
- Meta Level values: raw | super

CRITICAL ANTI-HALLUCINATION RULES:
1. If events.tsv samples show a 'value'→'instruction' mapping, that mapping is GROUND TRUTH
   and takes priority over everything else. Example: if value=1→"rest" and value=3→"task",
   these are trial phases — the task is binary (rest vs task), NOT 4-class MI.
2. NEVER assign MI class labels (left hand / right hand / feet / tongue) to trigger values
   based on BCI convention (e.g. BCIC IV 2a uses 769-772). Only use these labels if the
   events.tsv, events.json, or README explicitly states them.
3. If a paper covers multiple datasets in one publication, only use paradigm details that
   explicitly describe THIS specific dataset (match by dataset name, subject count, etc.).
4. Trial phase markers (rest/fixation/cue/task/feedback/interval) are NOT class labels —
   they describe the trial timeline. Do not create a "4-class" task from 4 phase markers.

Output ONLY valid JSON:
{
  "tasks_section": "## Tasks\\n\\n### Classical Task 1: ...\\n\\n...",
  "num_classical_tasks": 0,
  "num_normal_tasks": 0,
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
    """Return the set of event_ids confirmed as trial phase markers."""
    if not event_annotations:
        return set()
    phase_ids = set()
    for ann in event_annotations.get("annotations", []):
        meaning = ann.get("meaning", "").lower()
        if any(kw in meaning for kw in ("trial phase", "phase onset", "rest", "ready", "task onset",
                                        "interval", "fixation", "feedback", "cue onset",
                                        "baseline", "inter-trial")):
            if ann.get("event_type", "") in ("event", "annotation", "stim", ""):
                phase_ids.add(ann["event_id"])
    return phase_ids


def _strip_hallucinated_mi_tasks(tasks_section: str, phase_marker_ids: set, log) -> str:
    """
    Post-synthesis guard: remove or demote tasks whose Target Definition assigns MI class labels
    to event IDs that are locked as trial phase markers.

    Strategy:
    - Parse the tasks_section markdown for ### task blocks
    - For each task block, find the Target Definition table
    - If any event_id in the table is in phase_marker_ids AND the y/Meaning column contains
      MI class keywords (left hand, right hand, feet, tongue, motor imagery), flag the task
    - Replace flagged tasks with a NOTE explaining why they were removed
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
        # Rows look like: | `event_N` | y | Meaning |
        table_rows = re.findall(r"\|\s*`?(event_\w+)`?\s*\|([^|]*)\|([^|]*)\|", block)

        flagged = False
        for eid, y_col, meaning_col in table_rows:
            if eid in phase_marker_ids and mi_class_keywords.search(meaning_col + y_col):
                flagged = True
                log(f"[TaskSynth][Guard] Removing task: {eid} locked as phase marker "
                    f"but assigned MI class label: '{meaning_col.strip()}'")
                break

        if flagged:
            # Extract task heading for the note
            heading_match = re.match(r"(###[^\n]+)", block)
            heading = heading_match.group(1) if heading_match else "### (unknown task)"
            result_blocks.append(
                f"{heading}\n\n"
                f"> **[AUTO-REMOVED]** This task was removed by the post-synthesis guard because "
                f"it assigned motor imagery class labels to event IDs that are confirmed trial phase "
                f"markers (e.g., rest/ready/task/interval) by the isolated P3b event annotator. "
                f"The events.tsv ground truth takes precedence over BCI convention and paper content. "
                f"If the dataset does encode MI class labels, they must appear in a sidecar file "
                f"explicitly mapping event_ids to MI classes.\n\n"
            )
            removed_count += 1
        else:
            result_blocks.append(block)

    if removed_count:
        log(f"[TaskSynth][Guard] Removed {removed_count} task(s) with hallucinated MI class labels.")

    return "".join(result_blocks)


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
        "   TRIAL PHASE MARKER — it is NOT a classification class label.",
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
) -> str:
    """Run epoch alignment + task synthesis. Returns the '## Tasks' markdown string."""

    sidecar_block = _format_bids_sidecars(bids_sidecars or {})
    locked_meanings_block = _format_locked_meanings(event_annotations)

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
        f"{result.get('num_normal_tasks', 0)} normal, "
        f"{result.get('num_potential_tasks', 0)} potential")

    # Post-synthesis guard: strip tasks that hallucinate MI class labels onto phase markers
    phase_marker_ids = _get_phase_marker_event_ids(event_annotations)
    if phase_marker_ids:
        log(f"[TaskSynth][Guard] Phase marker IDs locked by P3b: {sorted(phase_marker_ids)}")
        tasks_section = _strip_hallucinated_mi_tasks(tasks_section, phase_marker_ids, log)

    return tasks_section
