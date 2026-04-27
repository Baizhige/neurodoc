"""Phase 4 v2: two-step task synthesis (aggregate → per-task fill) with detect gate.

Design principle: task ↔ kernel deep coupling. This module produces both:
  (a) the v3 `## Tasks` markdown section,
  (b) a structured `kernel_requirements` dict telling kernel_builder what
      event IDs, misc channels, info fields, and derived super-meta fields
      the tasks assume exist.

Hallucination guards:
  - Event IDs come only from pre_scan.event_ids + locked meanings.
  - Native Label Fields (info/misc-native) come only from the grounded catalog.
  - Derived super-meta misc channels require an LLM-declared `groundable` flag
    with cited evidence (a participants.tsv column name).
  - After synthesis, detect.py runs as a gate; up to 2 repair calls.
  - Hard whitelist enforcement is done later in pipeline.reconcile against
    the actual scan output (not here — here we only check schema).
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from .budget import BudgetExhausted
from .ref_analyzer import _parse_json
from .task_synthesizer import (
    _collect_grounded_label_fields,
    _format_bids_sidecars,
    _format_grounded_label_fields,
    _format_locked_meanings,
    _renumber_tasks,
    _strip_single_class_classifications,
    _strip_ungrounded_label_fields,
    _get_phase_marker_event_ids,
    _strip_hallucinated_mi_tasks,
)


# ──────────────────────────────────────────────────────────────────────────────
# Step A — aggregate candidate tasks across refs (dedupe paradigms)
# ──────────────────────────────────────────────────────────────────────────────

_AGGREGATE_SYSTEM = """\
You are an EEG ML task curator. Your job is to produce a RICH, grounded set of candidate
tasks that this dataset can support. Err on the side of including candidates — it is
better to let downstream repair/filter drop a marginal candidate than to silently censor
a legitimate paradigm here.

You receive:
  - Per-reference task extractions (output of Phase 1 per-ref analysis).
  - Grounded catalog of available Label Field sources for THIS dataset
    (participants.tsv columns, events.tsv numeric columns, native misc channels).
  - Locked event meanings (ground truth from dataset sidecar files).
  - BIDS sidecars (events.json column definitions).

Emit candidates covering all of:
  1. Every Route=event paradigm suggested by any relevant/partial ref.
  2. Every classical paradigm visible in the event IDs but not in refs (e.g. resting state
     eyes-open/closed, contrast-change target direction — Potential Tasks).
  3. Subject-level Info regression/classification for any participants.tsv column with ≥1
     non-trivial value (age, p_factor, attention, internalizing, externalizing, etc.) —
     these are archetype B3 (Route=info) or archetype C (Route=info + segmentation) when
     no discriminating event exists.
  4. Native misc regression (archetype B1) — ONLY for CONTINUOUS misc channels that
     already exist on the raw object (EMG traces, EOG traces, GSR — channels visible in
     `misc_channel_names` from the grounded catalog). Per-trial scalars from events.tsv
     do NOT satisfy B1; see (5).
  5. Derived misc (archetype B2, Meta Level = super) — THE default archetype for every
     numeric events.tsv column (confidence, response_time, rt, correct_answer, accuracy,
     etc.) AND for participants.tsv columns requiring a non-trivial transform (accuracy
     from correct_answer+total, log-RT from response_time, binned-age from age, etc.).
     The kernel will materialise these as misc channels — exact mechanism (constant
     broadcast, trial-locked step function, RawArray, etc.) is the kernel's choice.
     Prefer B3 only when the participants.tsv column is usable as-is (age itself,
     p_factor, handedness).

For each candidate, decide:
  name              short descriptive task name (e.g. "4-class motor imagery")
  archetype         "A" | "B1" | "B2" | "B3" | "C"
                    A  — event is the label (Route=event, no Label Field)
                    B1 — native misc: label = numeric column of events.tsv, regression only
                    B2 — derived misc: label derived from participants.tsv OR events.tsv
                         numeric column by a kernel transform, regression only, Meta=super
                    B3 — native info: label = participants.tsv column, Route=info
                    C  — segmentation with subject-level label; Route=misc(derived) or info
  label_route       event | misc | info
  task_type         classification | regression
  epoch_method      epoch_by_event_hdf5 | epoch_by_long_event_hdf5 | epoch_by_segmentation_hdf5
  paradigm          2-5 word paradigm label (e.g. "motor imagery", "P300 oddball")
  is_classical      true if ≥1 reference of classification=relevant cites it; else false
  evidence_refs     list of DOI/URL/arxiv strings; may be empty for Potential
  evidence_summary  2-4 sentences; state concrete facts (n_classes, tmin/tmax, label names)
  epoch_hint        {                                                     <-- use for downstream fill
    "tmin": <float or null>,
    "tmax": <float or null>,
    "overlap": <float or null>,
    "segment_length": <float or null>,
    "inferred": true|false,        // true if not explicit in ref
    "rationale": "<1-2 sentences>"
  }
  kernel_needs      structured dict (see below)

kernel_needs schema — what the kernel MUST produce for this task to be trainable:
{
  "must_have_events": ["<event_id>", ...],          // for Route=event, or as epoch anchor
  "must_have_native_misc": ["<channel_name>", ...], // Route=misc Meta=raw (B1)
  "must_have_info_fields": ["<column>", ...],       // Route=info (B3 or C-info)
  "must_derive_misc": [                             // Route=misc Meta=super (B2, C-derived)
    {
      "name": "<new_misc_channel_name>",
      "source_field": "<participants.tsv column OR events.tsv:column>",
      "derivation": "<step-by-step: how kernel creates this misc channel>",
      "groundable_evidence": "<cite the exact row in the grounded catalog>"
    }
  ]
}

HARD RULES (non-negotiable):
  H1 ONE Label Field per task. Multi-dim labels → N candidates.
  H2 Classification needs ≥2 distinct classes at the *label-value* level. For event route,
     that means ≥2 distinct Event IDs. For info/misc route, ≥2 distinct values of the column.
  H2b Classification y values MUST be 0-based sequential ints: {0, 1, ..., N-1}. Many-to-one
     mapping is encouraged when the paradigm justifies it (e.g. merge sleep N3+N4 → y=2
     keeping `N3` as the label name; merge different distractor positions into y=0). Decide
     merges by task-context relevance, not convenience. FORBIDDEN: gapped y ({0, 1, 3}),
     1-based y ({1, 2}), string labels ("class_A"), non-int y ("target"/"distractor").
  H3 misc route is REGRESSION ONLY. Never propose misc+classification.
  H4 Label Field required iff Route ∈ {misc, info}; forbidden for Route=event.
  H6 segmentation ⇒ target_events = [] (don't populate must_have_events).
  G1 Every must_have_event MUST be in the Available event IDs list (or locked meanings).
  G2 Every must_have_native_misc MUST correspond to a CONTINUOUS misc channel on the raw
     object (already in the pre-scan `misc_channel_names` list or typed non-EEG in
     channels.tsv). Per-trial events.tsv columns do NOT satisfy G2 — route them through
     must_derive_misc (archetype B2) instead.
  G3 Every must_have_info_field MUST be in the grounded catalog's participants.tsv list.
  G4 Every must_derive_misc.source_field MUST be in the grounded catalog. When sourced
     from events.tsv, write the source_field as `events.tsv:<column>` so the kernel
     builder knows to read from the sidecar. When sourced from participants.tsv, use the
     literal column name.

SOFT GUIDELINES (favor inclusion over exclusion):
  - DISTINCT EVENT SETS ⇒ DISTINCT CANDIDATES. seqLearning6target and seqLearning8target
    use different event IDs → TWO candidates, not one.
  - A naturalistic-viewing or resting paradigm with NO discriminable trigger structure is
    still a valid archetype-C candidate (segmentation + subject-level label like age,
    p_factor). Emit it as Potential with epoch_method=epoch_by_segmentation_hdf5 and
    segment_length/overlap from the Category SKILL defaults if refs are silent.
  - If a paradigm's only issue is "unclear tmin/tmax", still emit the candidate and set
    epoch_hint.inferred=true with the SKILL-guide default; the downstream fill will mark
    unconfirmed params with *.
  - Only skip a candidate (move to "dropped") when you cannot find ANY grounded Label
    Field or Event ID source for it. Aim for ≥5 candidates per dataset when the catalog
    has multiple participants.tsv columns and multiple event types.

Deduplication:
  - Merge two refs proposing the SAME paradigm (same event IDs, same classes) into one.
  - Keep overlapping-but-distinct tasks separate (different event sets, different label
    granularity, 2-class vs 4-class).
  - Classical candidates come first in the output list.

Output ONLY valid JSON (no markdown fences, no preamble):
{
  "candidates": [ { ... }, ... ],
  "dropped": [ { "paradigm": "...", "reason": "<concrete why nothing could be grounded>" } ],
  "reasoning": "<3-5 sentence summary of your decisions>"
}
"""


def _format_ref_extractions_for_aggregate(ref_extractions: List[Dict]) -> str:
    """Compress per-ref extractions into the aggregator prompt payload."""
    keep_fields = (
        "filename", "ref", "classification", "supports_task", "task_type",
        "n_classes", "paradigm", "epoch_method_hint", "epoch_params",
        "target_events", "label_mapping", "meta_level", "super_meta_note",
        "evidence_desc",
    )
    relevant = [
        e for e in ref_extractions
        if e.get("classification") in ("relevant", "partial")
    ]
    if not relevant:
        return "[No references classified as relevant or partial. Synthesize from dataset sidecars only.]"
    compact = [
        {k: v for k, v in e.items() if k in keep_fields and v not in (None, "", [])}
        for e in relevant
    ]
    return json.dumps(compact, indent=2, ensure_ascii=False)


def aggregate_candidates(
    dataset_name: str,
    analysis_md: str,
    ref_extractions: List[Dict],
    event_ids_preview: str,
    grounded_block: str,
    locked_meanings_block: str,
    category_skill: str,
    call_llm,
    budget,
    log,
    format_type: str = "unknown",
    eeg_header_summary: str = "",
    sidecar_block: str = "",
) -> Dict[str, Any]:
    """Run the dedupe/candidate step. Returns dict with 'candidates' list."""
    log("[TaskSynthV2] Aggregating candidates across references...")

    ref_block = _format_ref_extractions_for_aggregate(ref_extractions)
    user_msg = (
        f"Dataset: {dataset_name} (format: {format_type})\n\n"
        f"=== analysis.md excerpt ===\n{analysis_md[:3000]}\n\n"
        + (f"{sidecar_block}\n\n" if sidecar_block else "")
        + (f"=== EEG File Header Sample ===\n{eeg_header_summary}\n\n" if eeg_header_summary else "")
        + f"=== Available event IDs (from pre-scan — authoritative) ===\n{event_ids_preview}\n\n"
        + (f"{locked_meanings_block}\n\n" if locked_meanings_block else "")
        + f"{grounded_block}\n\n"
        + f"=== Category SKILL ===\n{category_skill[:2000]}\n\n"
        f"=== Per-reference task extractions (relevant + partial only) ===\n{ref_block}"
    )
    budget.charge("task_synthesis")
    raw = call_llm([
        {"role": "system", "content": _AGGREGATE_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {}
    candidates = result.get("candidates") or []
    dropped = result.get("dropped") or []
    log(f"[TaskSynthV2] Candidates: {len(candidates)} | Dropped: {len(dropped)}")
    for d in dropped[:5]:
        log(f"  dropped '{d.get('paradigm','?')}': {d.get('reason','?')}")
    for i, c in enumerate(candidates, 1):
        archetype = c.get("archetype", "?")
        route = c.get("label_route", "?")
        name = c.get("name", "?")
        log(f"  candidate {i}: {name} [archetype={archetype}, route={route}]")
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Step B — fill one candidate into v3 markdown (per-task call)
# ──────────────────────────────────────────────────────────────────────────────

_FILL_SYSTEM = """\
You are an EEG ML task writer. Fill exactly ONE candidate task into the v3 markdown bullet
format. The candidate's archetype, route, task_type, and kernel_needs are already decided —
use them. Your job is to produce the full v3 task block with grounded parameters and a
correctly-shaped Target Definition table.

=== v3 Task markdown (exact bullet format, in this order) ===
### Classical Task N: <name>   OR   ### Potential Task N: <name>
- **Task Type**: classification | regression
- **Epoch Method**: `<method>`
- **Epoch Parameters**: <see Epoch Parameters rules below>
- **Label Route**: `event` | `misc` | `info`
- **Label Field**: `<channel_or_column>`        # REQUIRED iff route ∈ {misc, info}; FORBIDDEN if route=event
- **Meta Level**: raw | super
- **Target Definition**:
  <route-specific table — see schema matrix below>
- **Evidence**:
  - <ref> — <short description>
  ... (at least 1 entry for Classical; may be empty for Potential)
- **Notes**: <free-form; for archetype B2/C-derived, describe the kernel derivation step>

=== Epoch Parameters rules (MANDATORY — detect.py rule epoch_parameters_complete, error) ===
Minimum required keys by method:
  * epoch_by_event_hdf5        — tmin, tmax, target_events
  * epoch_by_long_event_hdf5   — tmin, tmax, overlap, target_events
  * epoch_by_segmentation_hdf5 — segment_length, overlap (target_events MUST be [])
Format examples:
  `tmin = 0 s, tmax = 3 s, target_events = [\`left_hand\`, \`right_hand\`]`
  `segment_length = 4 s, overlap = 0.5, target_events = []`

PARAMETER INFERENCE (do NOT drop for unclear params):
  - The candidate includes an `epoch_hint` with tentative values. Use them.
  - If epoch_hint.inferred=true, mark the value with a trailing `*` (e.g. `tmin = 0 s *`).
  - If a specific value is null in epoch_hint, fall back to Category SKILL defaults and
    still mark with `*`.
  - ONLY set drop=true when BOTH: (a) no ref/skill provides ANY hint AND (b) the required
    field (e.g. target_events) is empty. Do not drop for soft reasons.

=== Target Definition schema matrix ===
  event  classification  | Event ID | y | Meaning |           (≥2 distinct y)
  event  regression      | Event ID | Value | Meaning |
  misc   regression      | MISC Channel | Value (unit) | Notes |   (single row)
  info   classification  | Info Field | Value | y | Meaning |      (≥2 distinct y)
  info   regression      | Info Field | Range (unit) | Notes |     (single row)
  misc   classification  FORBIDDEN

=== Meta Level by archetype (MANDATORY) ===
  A  (Route=event)                    → Meta Level = raw
  B1 (Route=misc, native channel)     → Meta Level = raw
  B2 (Route=misc, kernel-derived)     → Meta Level = super
  B3 (Route=info, native column)      → Meta Level = raw
  C  (segmentation + info-native)     → Meta Level = raw
  C  (segmentation + derived misc)    → Meta Level = super
RULE: Meta Level = super iff the task uses a derived misc channel that the kernel must
compute. All native/pre-existing sources (event IDs, events.tsv columns, participants.tsv
columns) → Meta Level = raw.

=== Hard invariants (the task block will be rejected by detect.py if violated) ===
  - Label Field present iff route ∈ {misc, info}.
  - misc route is regression only.
  - classification ⇒ ≥2 distinct y values in Target Definition.
  - classification y MUST be 0-based sequential ints: {0, 1, ..., N-1}. Many-to-one
    mapping is allowed AND encouraged when the paradigm justifies (merge sleep N3+N4
    → y=2 keeping `N3` as the label name; merge distractors at different positions
    → y=0). FORBIDDEN: {0, 1, 3} (gap), {1, 2} (not 0-based), "class_A"/"target" (string).
    Do NOT write y=target/y=distractor/y=more_symmetric — pick a 0..N-1 integer.
  - segmentation ⇒ target_events = [].
  - Every Event ID used MUST appear in the candidate's kernel_needs.must_have_events
    (for event route) OR be empty (for segmentation) OR be the event anchor (for B1/B2).

=== Authorized Label Field sources ===
For misc/info routes the Label Field value MUST equal one of:
  (a) a name in kernel_needs.must_have_native_misc (B1 native misc channel),
  (b) a name in kernel_needs.must_have_info_fields (B3 native info column), OR
  (c) a name in kernel_needs.must_derive_misc[*].name (B2/C-derived; kernel-created).

IMPORTANT: A (c) name is authorized even though it DOES NOT APPEAR in the grounded catalog —
the catalog enumerates native sources only. For derived misc (archetype B2/C-derived),
the candidate's must_derive_misc[].name is the new channel the kernel will create; do NOT
drop the task for "Label Field not in catalog" in this case. The source_field (not the
derived name) is what must be grounded, and the aggregator already verified that.

=== Output ===
Output ONLY valid JSON (no markdown fences):
{
  "drop": false,
  "drop_reason": "",
  "task_number": 1,
  "is_classical": true,
  "task_markdown": "### Classical Task 1: ...\\n- **Task Type**: ...\\n...",
  "kernel_requirements": {
    "event_ids_used": ["..."],
    "native_misc_used": ["..."],
    "info_fields_used": ["..."],
    "derived_misc_used": [
      {"name": "...", "source_field": "...", "derivation": "...", "groundable_evidence": "..."}
    ]
  }
}

If you cannot write a grounded block (e.g. cannot infer tmin/tmax), set drop=true and
give a concrete drop_reason. Do not emit a task with placeholder values.
"""


def _format_candidate_for_fill(candidate: Dict[str, Any]) -> str:
    return json.dumps(candidate, indent=2, ensure_ascii=False)


def fill_task_schema(
    dataset_name: str,
    candidate: Dict[str, Any],
    task_index: int,
    event_ids_preview: str,
    grounded_block: str,
    locked_meanings_block: str,
    sidecar_block: str,
    call_llm,
    budget,
    log,
    eeg_header_summary: str = "",
) -> Dict[str, Any]:
    """Fill one candidate into a v3 task markdown block."""
    name = candidate.get("name", f"task_{task_index}")
    log(f"[TaskSynthV2] Filling task #{task_index}: {name}")

    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"Candidate to fill (archetype/route already decided — respect them):\n"
        f"{_format_candidate_for_fill(candidate)}\n\n"
        f"task_number to use in the heading: {task_index}\n"
        f"is_classical: {candidate.get('is_classical', False)}\n\n"
        f"=== Available event IDs ===\n{event_ids_preview}\n\n"
        + (f"{locked_meanings_block}\n\n" if locked_meanings_block else "")
        + f"{grounded_block}\n\n"
        + (f"{sidecar_block}\n\n" if sidecar_block else "")
        + (f"=== EEG File Header Sample ===\n{eeg_header_summary}\n" if eeg_header_summary else "")
    )
    budget.charge("task_synthesis")
    raw = call_llm([
        {"role": "system", "content": _FILL_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {}
    if result.get("drop"):
        log(f"[TaskSynthV2] Dropped #{task_index}: {result.get('drop_reason','?')}")
        return {"dropped": True, "reason": result.get("drop_reason", ""), "candidate": candidate}
    md = result.get("task_markdown", "").strip()
    if not md or not md.startswith("### "):
        log(f"[TaskSynthV2] WARNING: task #{task_index} produced invalid markdown, skipping.")
        return {"dropped": True, "reason": "invalid_markdown", "candidate": candidate}
    return {
        "dropped": False,
        "is_classical": bool(result.get("is_classical", candidate.get("is_classical", False))),
        "task_markdown": md,
        "kernel_requirements": result.get("kernel_requirements") or {},
        "candidate": candidate,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Step C — detect.py gate on draft Tasks section
# ──────────────────────────────────────────────────────────────────────────────

_CANONICAL_INFO_FIELDS = ("subject_age", "subject_sex", "device")


def _build_shell_analysis_md(
    tasks_section: str,
    info_fields_hint: Optional[List[str]] = None,
    misc_label_fields_hint: Optional[List[str]] = None,
) -> str:
    """Minimal shell so detect.py template checks don't false-positive.

    info_fields_hint     list of participants.tsv columns + canonical fields the kernel
                         will surface; populates the ### Info stub so that tasks using
                         info-route label fields don't get flagged by the
                         info_label_field_in_info_section rule.
    misc_label_fields_hint  list of misc channel names (native or derived) that tasks
                         reference; populates ### MISC Label Summary so misc-route
                         tasks don't get flagged.
    """
    info_rows = []
    for f in _CANONICAL_INFO_FIELDS:
        info_rows.append(f"| `{f}` | complete | N/A |")
    for f in info_fields_hint or []:
        if f and f not in _CANONICAL_INFO_FIELDS:
            info_rows.append(f"| `{f}` | complete | N/A |")

    misc_block = ""
    if misc_label_fields_hint:
        misc_rows = "\n".join(
            f"| `{f}` | (regression) | N/A |" for f in misc_label_fields_hint if f
        )
        misc_block = (
            "\n### MISC Label Summary\n\n"
            "| MISC Channel | Value (unit) | Notes |\n|---|---|---|\n"
            f"{misc_rows}\n"
        )

    super_meta_required = "Yes" if re.search(r"\*\*Meta Level\*\*:\s*super", tasks_section) else "No"

    return (
        "# placeholder\n\n"
        "**Manual Review**:\n\n"
        "## Paradigm\n\n(placeholder)\n\n"
        "## File Scan Result\n\n"
        "### Event Structure\n\n| Event ID | Count (total) | Type | Meta Level | Meaning |\n|---|---|---|---|---|\n\n"
        "### Info\n\n| Field | Completeness | Notes |\n|---|---|---|\n"
        + "\n".join(info_rows) + "\n"
        + misc_block
        + f"\n{tasks_section.rstrip()}\n\n"
        "## Data Quality Notes\n\n- placeholder\n\n"
        f"## Kernel Responsibilities\n\n> **Super Meta Required**: {super_meta_required}\n> **Status**: wait_kernel_update\n"
    )


def run_detect_gate(
    tasks_section: str,
    dataset_name: str,
    log,
    info_fields_hint: Optional[List[str]] = None,
    misc_label_fields_hint: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Run detect.check_analysis_text on a shell doc; return Task-scoped errors only."""
    try:
        import sys
        from pathlib import Path as _P
        agent_dir = _P(__file__).parent.parent
        if str(agent_dir) not in sys.path:
            sys.path.insert(0, str(agent_dir))
        import detect as _detect
    except Exception as exc:
        log(f"[TaskSynthV2] detect.py unavailable ({exc}); skipping gate.")
        return []

    shell = _build_shell_analysis_md(
        tasks_section,
        info_fields_hint=info_fields_hint,
        misc_label_fields_hint=misc_label_fields_hint,
    )
    violations = _detect.check_analysis_text(
        analysis_text=shell,
        dataset_name=dataset_name,
        kernel_text="",
        severity_filter="error",
    )
    task_scoped = [
        v for v in violations
        if any(tok in (v.get("rule_id") or "") for tok in (
            "label_field", "task", "target_def", "epoch_parameters", "misc_",
            "classification_task", "segmentation_requires",
        ))
    ]
    if task_scoped:
        log(f"[TaskSynthV2][Gate] detect.py reports {len(task_scoped)} Task-scoped error(s).")
        for v in task_scoped[:6]:
            log(f"  - {v.get('rule_id','?')}: {(v.get('detail') or '')[:200]}")
    else:
        log("[TaskSynthV2][Gate] detect.py: clean.")
    return task_scoped


# ──────────────────────────────────────────────────────────────────────────────
# Step D — repair loop
# ──────────────────────────────────────────────────────────────────────────────

_REPAIR_SYSTEM = """\
You are repairing the ## Tasks section of an EEG dataset's analysis.md.
You will be given the current Tasks section and a list of detect.py rule violations.

*** FIX IN PLACE. DO NOT DROP UNLESS ABSOLUTELY NECESSARY. ***
Dropping a task is an irreversible loss of user-visible value. Prefer surgical edits.

=== Fix-in-place playbook ===

(a) misc_classification_forbidden
    → REWRITE as either `misc + regression` (if the field is naturally continuous/ordinal)
      or `info + classification` (if the label is a participants.tsv column), or
      `event + classification` (if the label maps 1:1 onto distinct event IDs).
    → Do NOT drop.

(b) info_label_field_in_info_section / misc_label_field_in_misc_section
    → These rules check that every Label Field in a non-event-route task is also listed in
      the dataset's ### Info / ### MISC Label Summary. The Info section in this stub is
      pre-populated with the known participants.tsv columns; if the violation still fires,
      the Label Field you wrote may be a minor spelling variant — rewrite it to match the
      canonical column name in the stub (see the Info/MISC tables).
    → Do NOT drop for this rule.

(c) epoch_parameters_complete (missing tmin/tmax/overlap/segment_length/target_events)
    → Infer from Category SKILL defaults; mark the inferred value with a trailing `*`.
      E.g. `tmin = 0 s *, tmax = 4 s *, overlap = 0.5 *`.
    → Only drop if target_events is empty for an event/long-event method AND no candidate
      event IDs exist — that is truly unrecoverable.

(d) classification_task_has_multiple_classes (<2 distinct y)
    → If the task has only one class, try to pair with a rest/baseline/phase-marker event
      to form 2-class rest-vs-task. Only drop if no second class is available anywhere.

(d2) classification_y_zero_indexed_sequential (non-int y, gapped y, 1-based y)
    → Renumber in place, preserving row order. Distinct source labels get 0, 1, 2, ...
      Example: y={target, distractor} → rewrite rows as y=0 (target) and y=1 (distractor).
      Example: y={0, 2} → renumber to y={0, 1}.
      Example: y={1, 2, 3} → renumber to y={0, 1, 2}.
    → Many-to-one merges are allowed AND encouraged when the paradigm justifies it
      (e.g. merge sleep N3+N4 → y=2 keeping both rows with N3 as the label name;
      merge distractors at different positions → y=0 for all distractor rows). Prefer
      a merge over dropping rows.
    → Do NOT drop for this rule.

(e) label_field_required_for_nonevent
    → Add the **Label Field** bullet with the channel/column name the Target Definition
      already references.

(f) label_field_absent_for_event
    → Remove the stray **Label Field** bullet. Target Definition stays unchanged.

(g) segmentation_requires_empty_target_events
    → Clear target_events to [] for segmentation-method tasks.

=== Schema reference ===
Epoch Parameters minimum required keys by method:
  * epoch_by_event_hdf5        — tmin, tmax, target_events
  * epoch_by_long_event_hdf5   — tmin, tmax, overlap, target_events
  * epoch_by_segmentation_hdf5 — segment_length, overlap (target_events = [])

Target Definition schema matrix:
  event  classification  | Event ID | y | Meaning |
  event  regression      | Event ID | Value | Meaning |
  misc   regression      | MISC Channel | Value (unit) | Notes |
  info   classification  | Info Field | Value | y | Meaning |
  info   regression      | Info Field | Range (unit) | Notes |
  misc   classification  FORBIDDEN — rewrite (see (a)).

Label Field required iff Route ∈ {misc, info}.
classification ⇒ ≥2 distinct y.
segmentation ⇒ target_events = [].

Renumber tasks after any drop: Classical 1,2,...  Potential 1,2,...
All Classical Tasks come before any Potential Task.

Output ONLY valid JSON (no markdown fences):
{
  "tasks_section": "## Tasks\\n\\n### Classical Task 1: ...\\n...",
  "dropped_tasks": ["<task name>"],
  "dropped_reasons": ["<why this task could not be fixed in place>"],
  "changes_summary": "<1-3 sentences — emphasize what you rewrote>"
}
"""


def _format_violations(violations: List[Dict[str, Any]]) -> str:
    lines = []
    for i, v in enumerate(violations, 1):
        lines.append(f"{i}. rule={v.get('rule_id','?')} | {v.get('detail','')}")
    return "\n".join(lines)


def repair_tasks(
    tasks_section: str,
    violations: List[Dict[str, Any]],
    dataset_name: str,
    call_llm,
    budget,
    log,
    info_fields_hint: Optional[List[str]] = None,
    misc_label_fields_hint: Optional[List[str]] = None,
    category_skill: str = "",
) -> str:
    """One repair pass. Returns the fixed tasks_section."""
    info_block = ""
    if info_fields_hint:
        info_block = (
            "\n=== Available ### Info columns (these ARE populated in the final doc) ===\n"
            + ", ".join(f"`{f}`" for f in _CANONICAL_INFO_FIELDS)
            + ", " + ", ".join(f"`{f}`" for f in info_fields_hint if f not in _CANONICAL_INFO_FIELDS)
            + "\n"
        )
    misc_block_str = ""
    if misc_label_fields_hint:
        misc_block_str = (
            "\n=== Available ### MISC Label Summary channels ===\n"
            + ", ".join(f"`{m}`" for m in misc_label_fields_hint if m)
            + "\n"
        )
    skill_block = (
        f"\n=== Category SKILL (for inferred tmin/tmax/overlap defaults) ===\n{category_skill[:1500]}\n"
        if category_skill else ""
    )
    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Current ## Tasks section ===\n{tasks_section}\n\n"
        f"=== detect.py violations to fix ===\n{_format_violations(violations)}"
        f"{info_block}{misc_block_str}{skill_block}"
    )
    budget.charge("task_synthesis")
    raw = call_llm([
        {"role": "system", "content": _REPAIR_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {}
    fixed = (result.get("tasks_section") or "").strip()
    dropped = result.get("dropped_tasks") or []
    reasons = result.get("dropped_reasons") or []
    summary = result.get("changes_summary", "")
    if fixed:
        log(f"[TaskSynthV2][Repair] {summary}")
        if dropped:
            log(f"[TaskSynthV2][Repair] Dropped tasks: {dropped}")
            for t, r in zip(dropped, reasons):
                log(f"  - {t}: {r}")
        return fixed
    log("[TaskSynthV2][Repair] LLM returned empty; keeping previous section.")
    return tasks_section


# ──────────────────────────────────────────────────────────────────────────────
# Step E — assemble final tasks_section + aggregated kernel_requirements
# ──────────────────────────────────────────────────────────────────────────────

def _assemble_tasks_section(filled_tasks: List[Dict[str, Any]]) -> str:
    """Order classical first, renumber within type, return full '## Tasks' markdown."""
    classical = [t for t in filled_tasks if t.get("is_classical")]
    potential = [t for t in filled_tasks if not t.get("is_classical")]

    def _normalize_heading(md: str, kind: str, n: int) -> str:
        # Replace whatever heading the LLM wrote with "### <kind> Task N: <title>"
        lines = md.split("\n", 1)
        first_line = lines[0]
        body = lines[1] if len(lines) > 1 else ""
        m = re.match(
            r"###\s+(?:Classical Task|Potential Task|Task)\s*\d*\s*:?\s*(.*)",
            first_line,
        )
        title = m.group(1).strip() if m else first_line.lstrip("# ").strip()
        new_first = f"### {kind} Task {n}: {title}"
        return new_first + ("\n" + body if body else "")

    parts = ["## Tasks\n"]
    for i, t in enumerate(classical, 1):
        parts.append(_normalize_heading(t["task_markdown"], "Classical", i).rstrip() + "\n")
    for i, t in enumerate(potential, 1):
        parts.append(_normalize_heading(t["task_markdown"], "Potential", i).rstrip() + "\n")
    return "\n".join(parts).rstrip() + "\n"


def _aggregate_kernel_requirements(filled_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge kernel_requirements from all tasks into one dict."""
    events: set = set()
    native_misc: set = set()
    info_fields: set = set()
    derived_misc: Dict[str, Dict[str, Any]] = {}  # key by name

    for t in filled_tasks:
        kr = t.get("kernel_requirements") or {}
        for e in kr.get("event_ids_used") or []:
            if isinstance(e, str) and e:
                events.add(e)
        for m in kr.get("native_misc_used") or []:
            if isinstance(m, str) and m:
                native_misc.add(m)
        for f in kr.get("info_fields_used") or []:
            if isinstance(f, str) and f:
                info_fields.add(f)
        for d in kr.get("derived_misc_used") or []:
            if not isinstance(d, dict):
                continue
            name = d.get("name")
            if not name:
                continue
            if name not in derived_misc:
                derived_misc[name] = {
                    "name": name,
                    "source_field": d.get("source_field", ""),
                    "derivation": d.get("derivation", ""),
                    "groundable_evidence": d.get("groundable_evidence", ""),
                    "used_by": [],
                }
            candidate_name = (t.get("candidate") or {}).get("name", "")
            if candidate_name:
                derived_misc[name]["used_by"].append(candidate_name)

    return {
        "required_event_ids": sorted(events),
        "required_native_misc": sorted(native_misc),
        "required_info_fields": sorted(info_fields),
        "derived_misc_channels": list(derived_misc.values()),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def synthesize_tasks_v2(
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
    max_repair_rounds: int = 2,
) -> Tuple[str, Dict[str, Any]]:
    """Run the two-step v2 synthesis pipeline.

    Returns:
      (tasks_section, kernel_requirements)
    """
    sidecar_block = _format_bids_sidecars(bids_sidecars or {})
    locked_meanings_block = _format_locked_meanings(event_annotations)
    grounded = _collect_grounded_label_fields(bids_sidecars, misc_channel_names)
    grounded_block = _format_grounded_label_fields(grounded)

    # Step A — aggregate candidates
    agg = aggregate_candidates(
        dataset_name, analysis_md, ref_extractions, event_ids_preview,
        grounded_block, locked_meanings_block, category_skill,
        call_llm, budget, log,
        format_type=format_type, eeg_header_summary=eeg_header_summary,
        sidecar_block=sidecar_block,
    )
    candidates: List[Dict[str, Any]] = agg.get("candidates") or []
    if not candidates:
        log("[TaskSynthV2] No candidates produced. Returning empty Tasks section.")
        empty_section = "## Tasks\n\n(No tasks could be grounded from available references and sidecars.)\n"
        return empty_section, {
            "required_event_ids": [], "required_native_misc": [],
            "required_info_fields": [], "derived_misc_channels": [],
        }

    # Step B — fill each candidate (sequential to preserve budget ordering; parallel
    # can be added later, but per-LLM-key rate limits make it marginal)
    filled: List[Dict[str, Any]] = []
    # Separate numbering for classical vs potential; assign later in assemble
    for idx, cand in enumerate(candidates, 1):
        try:
            result = fill_task_schema(
                dataset_name, cand, idx, event_ids_preview,
                grounded_block, locked_meanings_block, sidecar_block,
                call_llm, budget, log,
                eeg_header_summary=eeg_header_summary,
            )
        except BudgetExhausted:
            log("[TaskSynthV2] Budget exhausted mid-fill; assembling what we have.")
            break
        except Exception as exc:
            log(f"[TaskSynthV2] fill #{idx} raised {exc!r}; skipping this candidate.")
            continue
        if not result.get("dropped"):
            filled.append(result)

    if not filled:
        log("[TaskSynthV2] All candidates dropped during fill. Returning empty.")
        empty_section = "## Tasks\n\n(All candidate tasks dropped during v3 schema fill — see logs.)\n"
        return empty_section, {
            "required_event_ids": [], "required_native_misc": [],
            "required_info_fields": [], "derived_misc_channels": [],
        }

    # Assemble
    tasks_section = _assemble_tasks_section(filled)

    # Build hints for the shell doc — so Info / MISC stubs don't false-positive.
    info_fields_hint = [f.get("name", "") for f in (grounded.get("participants") or []) if f.get("name")]
    misc_native_names = [f.get("name", "") for f in (grounded.get("misc_native") or []) if f.get("name")]
    events_numeric_names = [f.get("name", "") for f in (grounded.get("events_numeric") or []) if f.get("name")]
    # Also include any derived misc names that candidates proposed (they will be created by kernel)
    candidate_derived_names: List[str] = []
    for c in candidates:
        kn = c.get("kernel_needs") or {}
        for d in kn.get("must_derive_misc") or []:
            if isinstance(d, dict) and d.get("name"):
                candidate_derived_names.append(d["name"])
    misc_label_fields_hint = list(dict.fromkeys(
        misc_native_names + events_numeric_names + candidate_derived_names
    ))

    # Step C+D — detect.py gate + repair loop
    for repair_round in range(max_repair_rounds + 1):
        violations = run_detect_gate(
            tasks_section, dataset_name, log,
            info_fields_hint=info_fields_hint,
            misc_label_fields_hint=misc_label_fields_hint,
        )
        if not violations:
            break
        if repair_round == max_repair_rounds:
            log(f"[TaskSynthV2][Gate] Still {len(violations)} error(s) after {repair_round} repair round(s). Proceeding.")
            break
        try:
            tasks_section = repair_tasks(
                tasks_section, violations, dataset_name, call_llm, budget, log,
                info_fields_hint=info_fields_hint,
                misc_label_fields_hint=misc_label_fields_hint,
                category_skill=category_skill,
            )
        except BudgetExhausted:
            log("[TaskSynthV2][Repair] Budget exhausted. Proceeding with current draft.")
            break

    # Legacy guards (low-cost, help catch residual hallucinations missed by LLM repair)
    phase_marker_ids = _get_phase_marker_event_ids(event_annotations)
    if phase_marker_ids:
        log(f"[TaskSynthV2][Guard] Phase marker IDs locked: {sorted(phase_marker_ids)}")
        tasks_section = _strip_hallucinated_mi_tasks(tasks_section, phase_marker_ids, log)
    tasks_section = _strip_single_class_classifications(tasks_section, log)
    tasks_section = _strip_ungrounded_label_fields(tasks_section, grounded, log)

    # Rebuild kernel_requirements from the (possibly post-repair / post-drop) filled list.
    # Note: if repair dropped tasks, the kernel_requirements here is a superset — reconcile
    # will prune actual usage against the final tasks_section.
    kernel_requirements = _aggregate_kernel_requirements(filled)
    # Add dropped list for visibility
    kernel_requirements["_dropped_candidates"] = agg.get("dropped") or []

    log(
        f"[TaskSynthV2] Done. "
        f"events={len(kernel_requirements['required_event_ids'])} | "
        f"native_misc={len(kernel_requirements['required_native_misc'])} | "
        f"info={len(kernel_requirements['required_info_fields'])} | "
        f"derived_misc={len(kernel_requirements['derived_misc_channels'])}"
    )
    return tasks_section, kernel_requirements
