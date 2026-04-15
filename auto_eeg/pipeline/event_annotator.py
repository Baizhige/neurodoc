"""Phase 3: Event Structure Annotation — ISOLATED from paper content.

P3a: Multi-turn evidence collection agent (reads data_dir files only).
P3b: Single LLM call to annotate event Meanings from collected evidence.

ISOLATION GUARANTEE: No paper content, no analysis.md paradigm section,
no category SKILL, no BCI-related context is passed to any LLM call here.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ref_analyzer import _parse_json

# ---------------------------------------------------------------------------
# System prompts (P3a and P3b)
# ---------------------------------------------------------------------------

_P3A_0_SYSTEM = """\
You are a dataset structure analyst. Your job is to identify all grouping \
dimensions in this EEG dataset and plan evidence collection to cover them all. \
You read files ONLY from the raw data directory via the tool calls you issue.

ISOLATION RULES (mandatory):
- You have no access to research papers, analysis notes, or paradigm descriptions.
- Do NOT apply BCI conventions or prior knowledge about what event codes typically mean.
- A marker "event_3" could mean anything — determine its meaning from the files.
- The ONLY valid evidence sources are files inside the data directory.

GROUPING GOAL:
Ensure you collect at least one events.tsv (or equivalent) sample per unique
(task, session) combination. If the dataset has one task and one session, a
single sample may be sufficient.

OUTPUT FORMAT — strict JSON only:
{
  "turn_summary": "<what structure you found>",
  "groups_identified": ["ses-01/task-mi", "ses-02/task-nf", ...],
  "groups_covered": ["ses-01/task-mi"],
  "groups_missing": ["ses-02/task-nf"],
  "coverage_sufficient": false,
  "next_reads": [
    {"tool": "read_tsv", "path": "sub-001/ses-01/eeg/sub-001_ses-01_task-nf_events.tsv", "params": {"nrows": 20}},
    {"tool": "read_json", "path": "task-nf_events.json", "params": {}}
  ]
}

RULES:
- coverage_sufficient MUST be false on turn 0 (even if initial samples exist,
  you have not yet had a chance to verify consistency across groups).
- Prioritise root-level task-*_events.json and task-*_events.tsv first.
- For non-BIDS formats (no events.tsv), request read_eeg_header to check
  annotations embedded in the EEG file itself.
- Only request next_reads for groups that are not yet covered.
"""

_P3A_N_SYSTEM = """\
You are a dataset structure analyst continuing evidence collection.
You now receive the results of your previous read requests.

Same isolation rules apply:
- No BCI conventions, no prior paradigm knowledge.
- Determine event meanings solely from the files you read.

Assess the new read results, update your coverage map, and decide whether to
continue or declare coverage sufficient.

STOPPING RULES:
- coverage_sufficient=true is only valid after turn >= 3 (minimum 3 turns).
- Stop if: all groups are covered AND read results are consistent across groups.
- Stop if: diminishing returns — last 2 turns produced no new information.
- Continue if: any identified group has no events.tsv/annotation sample yet.

When stopping (coverage_sufficient=true), include an "assessment" field:
{
  "turn_summary": "...",
  "groups_identified": [...],
  "groups_covered": [...],
  "groups_missing": [],
  "coverage_sufficient": true,
  "assessment": "<summary of what each event ID maps to, citing specific files>"
}

When continuing:
{
  "turn_summary": "...",
  "groups_identified": [...],
  "groups_covered": [...],
  "groups_missing": [...],
  "coverage_sufficient": false,
  "next_reads": [...]
}
"""

_P3B_SYSTEM = """\
You are an event annotation specialist. Your ONLY job is to assign Meaning,
Event Type, and Meta Level to each raw event ID based on the evidence collected
from the dataset's own files.

CRITICAL ISOLATION RULES:
1. You have NOT seen any research papers. Do NOT apply BCI conventions.
2. Do NOT use class labels (left hand, right hand, feet, tongue) unless they
   are EXPLICITLY stated verbatim in the sidecar files you have seen.
3. A marker mapping to "rest"/"ready"/"task"/"interval" describes a TRIAL PHASE.
   Its Meaning is "Trial phase onset: [phase name]" — NOT a class label.
4. Event Type MUST be exactly "event" or "admin":
   - "event": experimental stimulus, response, or trial phase marker
   - "admin": system marker, session boundary, calibration, trigger sync
5. Meta Level:
   - "raw": label is directly readable from event ID (default)
   - "super": label requires joining with external source (rare)
6. confidence:
   - "confirmed": events.tsv/events.json directly states the mapping
   - "inferred": derived from context (e.g. event order, README description)
   - "unclear": insufficient evidence

OUTPUT FORMAT — strict JSON only:
{
  "annotations": [
    {
      "event_id": "event_1",
      "event_type": "event",
      "meta_level": "raw",
      "meaning": "Rest/baseline period onset",
      "confidence": "confirmed",
      "session_task_scope": "all"
    }
  ],
  "notes": "<brief summary citing which files confirmed the mappings>"
}
"""

# ---------------------------------------------------------------------------
# Directory tree helper (local, avoids importing context_builder)
# ---------------------------------------------------------------------------

def _ls_tree(path: Path, max_depth: int = 4, _depth: int = 0) -> List[str]:
    lines: List[str] = []
    try:
        entries = sorted(path.iterdir())
    except (PermissionError, OSError):
        return []
    for e in entries:
        indent = "  " * _depth
        if e.is_dir():
            lines.append(f"{indent}{e.name}/")
            if _depth < max_depth - 1:
                lines.extend(_ls_tree(e, max_depth, _depth + 1))
        else:
            lines.append(f"{indent}{e.name}")
    return lines


def _build_dir_summary(data_dir: str) -> str:
    p = Path(data_dir)
    lines = _ls_tree(p, max_depth=4)
    tree = "\n".join(lines[:300])

    # Programmatic grouping summary
    all_names: List[str] = []
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            all_names.append(f)

    sessions = sorted({
        part for n in all_names
        for part in n.split("_")
        if part.startswith("ses-")
    })
    tasks = sorted({
        part for n in all_names
        for part in n.split("_")
        if part.startswith("task-")
    })
    runs = sorted({
        part for n in all_names
        for part in n.split("_")
        if part.startswith("run-")
    })

    summary_lines = [
        f"Sessions: {sessions or ['(none)']}"[:200],
        f"Tasks: {tasks or ['(none)']}"[:200],
        f"Runs: {runs or ['(none)']}"[:200],
    ]
    return f"=== Directory tree (max depth 4) ===\n{tree}\n\n=== Programmatic grouping ===\n" + "\n".join(summary_lines)


# ---------------------------------------------------------------------------
# Tool executor — enforces data_dir boundary
# ---------------------------------------------------------------------------

def _execute_tool(tool_name: str, path: str, params: Dict, data_dir: str) -> str:
    """Execute one tool call. Returns result string or error message."""
    data_path = Path(data_dir).resolve()

    # Path validation: must stay within data_dir
    try:
        target = (data_path / path).resolve()
    except Exception as e:
        return f"[path error: {e}]"

    try:
        target.relative_to(data_path)
    except ValueError:
        return f"[security: path '{path}' is outside data_dir — rejected]"

    if not target.exists():
        return f"[file not found: {path}]"

    try:
        if tool_name == "read_tsv":
            import pandas as pd
            nrows = params.get("nrows", 20)
            usecols = params.get("usecols")
            df = pd.read_csv(target, sep="\t", nrows=nrows, usecols=usecols)
            return df.to_string(index=False)[:4000]

        elif tool_name == "read_json":
            with open(target, encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)[:3000]

        elif tool_name == "read_eeg_header":
            try:
                import mne
                mne.set_log_level("ERROR")
            except ImportError:
                return "[mne not available]"
            ext = target.suffix.lower()
            loaders = {
                ".set": mne.io.read_raw_eeglab,
                ".bdf": mne.io.read_raw_bdf,
                ".edf": mne.io.read_raw_edf,
                ".fif": mne.io.read_raw_fif,
                ".vhdr": mne.io.read_raw_brainvision,
                ".cnt": mne.io.read_raw_cnt,
                ".gdf": mne.io.read_raw_gdf,
            }
            loader = loaders.get(ext)
            if loader is None:
                return f"[unsupported EEG format: {ext}]"
            raw = loader(target, preload=False, verbose=False)
            ch_names = raw.ch_names[:16]
            result_lines = [
                f"File: {target.name}",
                f"  Channels ({raw.info['nchan']}): {ch_names}",
                f"  Sfreq: {raw.info['sfreq']} Hz",
                f"  Duration: {raw.times[-1]:.1f}s",
            ]
            if hasattr(raw, "annotations") and len(raw.annotations) > 0:
                unique = list(dict.fromkeys(raw.annotations.description))[:20]
                result_lines.append(f"  Annotation descriptions (sample): {unique}")
            raw.close()
            return "\n".join(result_lines)

        elif tool_name == "read_mat":
            try:
                from scipy.io import loadmat
            except ImportError:
                return "[scipy not available]"
            variable_names = params.get("variable_names")
            mat = loadmat(str(target), variable_names=variable_names)
            lines = []
            for k, v in mat.items():
                if k.startswith("__"):
                    continue
                try:
                    shape = getattr(v, "shape", "scalar")
                    dtype = getattr(v, "dtype", type(v).__name__)
                    lines.append(f"  {k}: shape={shape}, dtype={dtype}")
                    if hasattr(v, "flat") and v.size <= 20:
                        lines.append(f"    values={v.tolist()}")
                except Exception:
                    lines.append(f"  {k}: (unprintable)")
            return "\n".join(lines)[:3000]

        elif tool_name == "read_text":
            max_chars = params.get("max_chars", 3000)
            with open(target, encoding="utf-8", errors="replace") as f:
                return f.read(max_chars)

        else:
            return f"[unknown tool: {tool_name}]"

    except Exception as e:
        return f"[tool error: {type(e).__name__}: {e}]"


# ---------------------------------------------------------------------------
# Phase 3a: Evidence collection agent loop
# ---------------------------------------------------------------------------

def _format_initial_samples(initial_samples: Dict) -> str:
    """Format P0 BIDS sidecar samples for Turn 0 input."""
    parts: List[str] = []
    if initial_samples.get("events_tsv_samples"):
        parts.append("=== events.tsv samples already available (from Phase 0) ===")
        for fname, content in initial_samples["events_tsv_samples"].items():
            parts.append(f"\n[{fname}]\n{content}")
    if initial_samples.get("events_jsons"):
        parts.append("\n=== events.json definitions already available ===")
        for fname, content in initial_samples["events_jsons"].items():
            parts.append(f"\n[{fname}]\n{content[:1500]}")
    if initial_samples.get("readme"):
        parts.append(f"\n=== README (excerpt) ===\n{initial_samples['readme'][:1000]}")
    return "\n".join(parts) if parts else "(no initial samples available)"


def _run_agent_loop(
    event_ids: str,
    data_dir: str,
    initial_samples: Dict,
    call_llm: Callable,
    budget,
    log: Callable,
    cache_dir: Optional[str],
) -> List[Dict]:
    """P3a: multi-turn evidence collection. Returns list of turn records."""
    dir_summary = _build_dir_summary(data_dir)
    initial_str = _format_initial_samples(initial_samples)

    # Turn 0 user message
    turn0_user = (
        f"=== Raw event IDs and counts (from pre-scan) ===\n{event_ids}\n\n"
        f"{dir_summary}\n\n"
        f"{initial_str}\n\n"
        "Now: identify all grouping dimensions (sessions × tasks) and plan "
        "which files to read to cover all groups. Remember: coverage_sufficient "
        "must be false on turn 0."
    )

    conversation: List[Dict] = [
        {"role": "system", "content": _P3A_0_SYSTEM},
        {"role": "user", "content": turn0_user},
    ]

    turns_data: List[Dict] = []
    max_turns = 20

    for turn_idx in range(max_turns):
        log(f"[EventAnnotator] P3a turn {turn_idx}...")
        budget.charge("event_annotation")
        raw = call_llm(conversation)
        parsed = _parse_json(raw) or {}

        # Collect read results for this turn
        read_results: Dict[str, str] = {}
        next_reads = parsed.get("next_reads", [])
        for req in next_reads:
            tool = req.get("tool", "")
            path = req.get("path", "")
            params = req.get("params", {})
            if not path:
                continue
            result = _execute_tool(tool, path, params, data_dir)
            read_results[f"{tool}:{path}"] = result
            log(f"[EventAnnotator]   {tool}({path}) → {len(result)} chars")

        turn_record = {
            "turn": turn_idx,
            "llm_output": parsed,
            "llm_raw": raw[:2000],
            "read_results": read_results,
        }
        turns_data.append(turn_record)

        # Persist to evidence cache
        if cache_dir:
            cache_path = Path(cache_dir)
            cache_path.mkdir(parents=True, exist_ok=True)
            (cache_path / f"phase3_turn{turn_idx}.json").write_text(
                json.dumps(turn_record, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        # Check termination
        coverage_sufficient = parsed.get("coverage_sufficient", False)
        if coverage_sufficient and turn_idx >= 2:
            log(f"[EventAnnotator] P3a coverage sufficient after {turn_idx + 1} turns.")
            break

        if turn_idx == max_turns - 1:
            log("[EventAnnotator] P3a: max turns reached, forcing exit.")
            break

        if not next_reads and not coverage_sufficient:
            log("[EventAnnotator] P3a: no more reads requested, stopping early.")
            break

        # Build next turn user message with read results
        result_lines = [f"=== Results of turn {turn_idx} reads ==="]
        for key, val in read_results.items():
            result_lines.append(f"\n[{key}]\n{val[:2000]}")
        next_user = "\n".join(result_lines) + (
            "\n\nUpdate your coverage map. Declare coverage_sufficient=true only "
            f"if all groups are covered AND you are past turn 2 (current turn: {turn_idx + 1})."
        )

        # Switch to P3a-N system prompt after turn 0
        if turn_idx == 0:
            conversation[0] = {"role": "system", "content": _P3A_N_SYSTEM}

        conversation.append({"role": "assistant", "content": raw})
        conversation.append({"role": "user", "content": next_user})

    return turns_data


# ---------------------------------------------------------------------------
# Phase 3b: Event annotation (isolated, 1 LLM call)
# ---------------------------------------------------------------------------

def _run_annotation(
    turns_data: List[Dict],
    event_ids: str,
    call_llm: Callable,
    budget,
    log: Callable,
) -> Dict:
    """P3b: single isolated LLM call to annotate event Meanings."""
    # Assemble all evidence from agent loop turns
    evidence_parts: List[str] = [
        f"=== Raw event IDs and counts ===\n{event_ids}",
        "\n=== Evidence collected from data directory ===",
    ]
    for t in turns_data:
        assessment = t["llm_output"].get("assessment", "")
        turn_summary = t["llm_output"].get("turn_summary", "")
        read_results = t.get("read_results", {})
        if turn_summary:
            evidence_parts.append(f"\n[Turn {t['turn']} summary]: {turn_summary}")
        if assessment:
            evidence_parts.append(f"[Coverage assessment]: {assessment}")
        for key, val in read_results.items():
            evidence_parts.append(f"\n[File read: {key}]\n{val[:2000]}")

    user_msg = (
        "\n".join(evidence_parts)
        + "\n\nUsing ONLY the evidence above, annotate each event ID. "
        "Do not apply BCI conventions or prior knowledge."
    )

    log("[EventAnnotator] P3b: running isolated event annotation...")
    budget.charge("event_annotation")
    raw = call_llm([
        {"role": "system", "content": _P3B_SYSTEM},
        {"role": "user", "content": user_msg},
    ])
    result = _parse_json(raw) or {"annotations": [], "notes": "(parse failed)"}

    if not result.get("annotations"):
        log("[EventAnnotator] WARNING: P3b produced no annotations.")
    else:
        log(f"[EventAnnotator] P3b: {len(result['annotations'])} events annotated.")
        for ann in result["annotations"]:
            log(f"  {ann['event_id']}: {ann['meaning']} [{ann['confidence']}]")

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def annotate_events(
    dataset_name: str,
    event_ids_preview: str,
    data_dir: str,
    initial_samples: Dict,
    call_llm: Callable,
    budget,
    log: Callable,
    evidence_cache_dir: Optional[str] = None,
) -> Dict:
    """Run P3a + P3b. Returns {"annotations": [...], "notes": "..."}."""
    if not data_dir or not Path(data_dir).is_dir():
        log("[EventAnnotator] No valid data_dir — returning empty annotations.")
        return {"annotations": [], "notes": "No data_dir available."}

    cache_dir = None
    if evidence_cache_dir:
        cache_dir = str(Path(evidence_cache_dir) / dataset_name)

    log(f"[EventAnnotator] Starting P3a agent loop for {dataset_name}...")
    turns_data = _run_agent_loop(
        event_ids_preview,
        data_dir,
        initial_samples,
        call_llm,
        budget,
        log,
        cache_dir,
    )

    annotation = _run_annotation(turns_data, event_ids_preview, call_llm, budget, log)

    # Persist final annotation to evidence cache
    if cache_dir:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        (cache_path / "phase3_annotation.json").write_text(
            json.dumps(annotation, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log(f"[EventAnnotator] Annotation cached to {cache_path / 'phase3_annotation.json'}")

    return annotation


# ---------------------------------------------------------------------------
# Standalone test helper (no full pipeline required)
# ---------------------------------------------------------------------------

def annotate_events_standalone(
    dataset_name: str,
    data_dir: str,
    llm_config: Dict,
    event_ids_override: Optional[str] = None,
) -> Dict:
    """
    Run P3a+P3b without the full pipeline. Useful for testing.

    llm_config: {"url": "...", "key": "...", "model": "..."}

    Example:
        from auto_eeg.pipeline.event_annotator import annotate_events_standalone
        result = annotate_events_standalone(
            "openneuro_ds004447",
            "<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds004447",
            {"url": "http://...", "key": "...", "model": "..."},
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    """
    import sys
    from pathlib import Path as _Path

    # Minimal Budget stub
    class _Budget:
        def __init__(self):
            self.used = 0
        def charge(self, _phase):
            self.used += 1

    # Minimal call_llm
    def _call_llm(messages):
        import requests
        url = llm_config["url"].rstrip("/") + "/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config.get('key', '')}",
        }
        body = {
            "model": llm_config.get("model", ""),
            "messages": messages,
        }
        r = requests.post(url, headers=headers, json=body, timeout=240)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    log_lines: List[str] = []
    def _log(msg):
        print(msg)
        log_lines.append(msg)

    # Read initial samples from data_dir (replicate what P0 does)
    from .context_builder import _read_bids_sidecars
    initial_samples = _read_bids_sidecars(_Path(data_dir), _log)

    # Build a simple event_ids_preview if not provided
    if event_ids_override:
        event_ids = event_ids_override
    else:
        # Try to read from events.tsv to get unique values
        tsv_samples = initial_samples.get("events_tsv_samples", {})
        if tsv_samples:
            sample_text = next(iter(tsv_samples.values()))
            event_ids = f"(from events.tsv samples):\n{sample_text[:500]}"
        else:
            event_ids = "(unknown — pre-scan not available; reading from directory)"

    budget = _Budget()
    result = annotate_events(
        dataset_name,
        event_ids,
        data_dir,
        initial_samples,
        _call_llm,
        budget,
        _log,
        evidence_cache_dir=str(_Path(__file__).parent.parent / "evidence_cache"),
    )
    _log(f"\n[Standalone] Total LLM calls: {budget.used}")
    return result
