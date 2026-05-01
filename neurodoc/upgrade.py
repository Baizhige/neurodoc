#!/usr/bin/env python3
"""Incrementally update an existing kernel and analysis.md via [to_agent: ...] tags."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

AGENT_DIR = Path(__file__).resolve().parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

try:
    from .llm_adapter import call_llm_text, resolve_llm_config
    from .paths import DATASET_DOCUMENT_DIR, LOGS_DIR, SANDBOX_DIR
    from .pipeline.context_builder import build_context
    from .pipeline.kernel_builder import (
        _build_test_script,
        _extract_code_block,
        _pick_sample_files,
        _security_check,
        _static_validate,
        install_kernel,
    )
    from . import scan_engine
except ImportError:
    from llm_adapter import call_llm_text, resolve_llm_config
    from paths import DATASET_DOCUMENT_DIR, LOGS_DIR, SANDBOX_DIR
    from pipeline.context_builder import build_context
    from pipeline.kernel_builder import (
        _build_test_script,
        _extract_code_block,
        _pick_sample_files,
        _security_check,
        _static_validate,
        install_kernel,
    )
    import scan_engine


TO_AGENT_RE = re.compile(r"\[to_agent:\s*(.*?)\]", re.IGNORECASE | re.DOTALL)

_PLANNER_SYSTEM = """\
You are NeuroDoc's incremental-upgrade planner.

Existing analysis.md is trusted. Reviewer tags of the form [to_agent: ...] describe
targeted corrections or improvements. Your job is to decide:
1. what kernel changes are required,
2. whether they are feasible from the available local evidence,
3. which analysis.md locations will need final text updates after full_scan.

Rules:
- Do NOT rewrite the whole dataset from scratch.
- Prefer minimal, incremental kernel changes.
- Use current analysis.md as trusted semantic context.
- Ground kernel changes in local evidence when possible.
- If a request only needs prose cleanup, mark kernel_change_required=false.
- For task-note requests, the likely intent is to enrich kernel outputs with more raw
  meta or super meta fields.
- Return JSON ONLY. No markdown fences.

Required JSON object keys:
{
  "kernel_change_required": true/false,
  "feasible": true/false,
  "feasibility_reason": "...",
  "patch_goals": ["..."],
  "doc_goals": ["..."],
  "required_event_ids": ["..."],
  "required_native_misc": ["..."],
  "required_info_fields": ["..."],
  "derived_misc_channels": [
    {
      "name": "...",
      "source_field": "...",
      "derivation": "...",
      "groundable_evidence": "..."
    }
  ]
}
"""

_UPGRADE_KERNEL_SYSTEM = """\
You are an EEG kernel engineer updating an EXISTING EEGUnity kernel.

This is an incremental patch, not a from-scratch rewrite. Preserve working behavior
unless the request explicitly requires change.

Output your response as a Python code block ONLY:
```python
<full revised kernel source>
```

Hard requirements:
1. Keep a valid EEGUnity kernel file with `KERNEL = <ClassName>()` on the last line.
2. Keep `def apply(self, udataset, raw, row) -> mne.io.BaseRaw:` exactly.
3. Inside apply(), write `raw.info["description"] = json.dumps({...})`.
4. `eegunity_description` must remain a flat dict of string values.
5. If required_info_fields is non-empty, include those keys in eegunity_description.
6. If required_native_misc or derived_misc_channels is non-empty, ensure those misc
   channels exist on the returned raw with MNE ch_type `misc`.
7. Do not add file-writing or shell-execution behavior.
8. Minimize unrelated refactors.
"""

_UPGRADE_KERNEL_FIX_SYSTEM = """\
You are fixing an incremental EEGUnity kernel patch.

Return a full corrected kernel as a Python code block ONLY:
```python
<full corrected kernel source>
```

Fix only the failing aspects while preserving the intended upgrade goals.
"""

_DOC_RENDER_SYSTEM = """\
You are updating analysis.md after a NeuroDoc incremental upgrade.

Existing analysis.md is trusted. If full_scan was run, File Scan Result already reflects
the latest raw-truth scan and must remain scan-faithful.

Return JSON ONLY with this shape:
{
  "paradigm": {"text": "..."} or null,
  "event_meanings": {"<event_id>": "..."},
  "event_structure_note": {"text": "..."} or null,
  "info_notes": {"<field>": "..."},
  "misc_notes": {"<channel>": "..."},
  "task_notes": {"<task title>": "..."}
}

Rules:
- Never include `[to_agent: ...]` in outputs.
- For Info Notes, MISC Notes, and Event Meaning, if evidence is insufficient, use an
  empty string.
- Preserve the meaning of trusted existing content when possible.
- Do not invent scan facts; only refine prose around already trusted facts.
"""


@dataclass
class TaggedRequest:
    kind: str
    key: str
    instructions: List[str] = field(default_factory=list)
    clean_text: str = ""
    raw_text: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "key": self.key,
            "instructions": list(self.instructions),
            "clean_text": self.clean_text,
            "raw_text": self.raw_text,
        }


def _find_config(explicit: Optional[str]) -> Tuple[Dict[str, Any], Optional[Path]]:
    if explicit:
        path = Path(explicit)
        return json.loads(path.read_text(encoding="utf-8")), path
    path = scan_engine.get_config_path()
    return scan_engine.load_machine_config(), path if path.exists() else None


def _strip_tags(text: str) -> Tuple[str, List[str]]:
    instructions = [m.group(1).strip() for m in TO_AGENT_RE.finditer(text)]
    cleaned = TO_AGENT_RE.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
    return cleaned, [x for x in instructions if x]


def _find_section_span(text: str, level: int, name: str) -> Optional[Tuple[int, int]]:
    heading_re = re.compile(rf"^{'#' * level}\s+{re.escape(name)}\s*$", re.MULTILINE)
    start_m = heading_re.search(text)
    if not start_m:
        return None
    after = text[start_m.end():]
    end_re = re.compile(rf"^{'#' * level}\s+\S", re.MULTILINE)
    end_m = end_re.search(after)
    end = start_m.end() + (end_m.start() if end_m else len(after))
    return start_m.start(), end


def _extract_section(text: str, level: int, name: str) -> str:
    span = _find_section_span(text, level, name)
    if not span:
        return ""
    return text[span[0]:span[1]]


def _replace_section(text: str, level: int, name: str, new_block: str) -> str:
    span = _find_section_span(text, level, name)
    if not span:
        suffix = "\n\n" if text.rstrip() else ""
        return text.rstrip() + suffix + new_block.rstrip() + "\n"
    return text[:span[0]] + new_block.rstrip() + "\n" + text[span[1]:].lstrip("\n")


def _iter_level3_blocks(section_text: str) -> Iterable[Tuple[str, int, int, str]]:
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", section_text, re.MULTILINE))
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section_text)
        yield match.group(1).strip(), start, end, section_text[start:end]


def _split_md_row(line: str) -> List[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _format_md_row(cells: Iterable[str]) -> str:
    return "| " + " | ".join(str(c).strip() for c in cells) + " |"


def _parse_review_requests(analysis_text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "paradigm": None,
        "event_meanings": {},
        "event_structure_note": None,
        "info_notes": {},
        "misc_notes": {},
        "task_notes": {},
    }

    paradigm_block = _extract_section(analysis_text, 2, "Paradigm")
    if paradigm_block:
        body = re.sub(r"^##\s+Paradigm\s*$", "", paradigm_block, count=1, flags=re.MULTILINE).strip()
        clean_text, instructions = _strip_tags(body)
        if instructions:
            result["paradigm"] = TaggedRequest(
                kind="paradigm",
                key="paradigm",
                instructions=instructions,
                clean_text=clean_text,
                raw_text=body,
            )

    fsr_block = _extract_section(analysis_text, 2, "File Scan Result")
    event_block = _extract_section(fsr_block, 3, "Event Structure") if fsr_block else ""
    if event_block:
        lines = event_block.splitlines()
        table_rows_end = 0
        for idx, line in enumerate(lines):
            cells = _split_md_row(line)
            if cells and len(cells) >= 5 and not re.fullmatch(r"-+", cells[0].replace(" ", "")):
                if cells[0] != "Event ID":
                    event_id = cells[0].strip().strip("`")
                    clean_text, instructions = _strip_tags(cells[4])
                    if instructions:
                        result["event_meanings"][event_id] = TaggedRequest(
                            kind="event_meaning",
                            key=event_id,
                            instructions=instructions,
                            clean_text=clean_text,
                            raw_text=cells[4],
                        )
            if line.strip().startswith("|"):
                table_rows_end = idx + 1
        quote_lines = [ln[1:].strip() for ln in lines[table_rows_end:] if ln.strip().startswith(">")]
        if quote_lines:
            note_text = "\n".join(quote_lines).strip()
            clean_text, instructions = _strip_tags(note_text)
            if instructions:
                result["event_structure_note"] = TaggedRequest(
                    kind="event_structure_note",
                    key="event_structure_note",
                    instructions=instructions,
                    clean_text=clean_text,
                    raw_text=note_text,
                )

    misc_block = _extract_section(fsr_block, 3, "MISC Label Summary") if fsr_block else ""
    if misc_block:
        for line in misc_block.splitlines():
            cells = _split_md_row(line)
            if not cells or len(cells) < 4 or cells[0] == "Channel" or re.fullmatch(r"-+", cells[0].replace(" ", "")):
                continue
            channel = cells[0].strip().strip("`")
            clean_text, instructions = _strip_tags(cells[3])
            if instructions:
                result["misc_notes"][channel] = TaggedRequest(
                    kind="misc_note",
                    key=channel,
                    instructions=instructions,
                    clean_text=clean_text,
                    raw_text=cells[3],
                )

    info_block = _extract_section(fsr_block, 3, "Info") if fsr_block else ""
    if info_block:
        for line in info_block.splitlines():
            cells = _split_md_row(line)
            if not cells or len(cells) < 3 or cells[0] == "Field" or re.fullmatch(r"-+", cells[0].replace(" ", "")):
                continue
            field_name = cells[0].strip().strip("`")
            clean_text, instructions = _strip_tags(cells[2])
            if instructions:
                result["info_notes"][field_name] = TaggedRequest(
                    kind="info_note",
                    key=field_name,
                    instructions=instructions,
                    clean_text=clean_text,
                    raw_text=cells[2],
                )

    tasks_block = _extract_section(analysis_text, 2, "Tasks")
    if tasks_block:
        for title, _, _, block in _iter_level3_blocks(tasks_block):
            note_m = re.search(r"^- \*\*Notes\*\*:\s*(.*)$", block, re.MULTILINE)
            if not note_m:
                continue
            clean_text, instructions = _strip_tags(note_m.group(1))
            if instructions:
                result["task_notes"][title] = TaggedRequest(
                    kind="task_note",
                    key=title,
                    instructions=instructions,
                    clean_text=clean_text,
                    raw_text=note_m.group(1),
                )
    return result


def _request_count(requests: Mapping[str, Any]) -> int:
    total = 0
    if requests.get("paradigm"):
        total += 1
    if requests.get("event_structure_note"):
        total += 1
    total += len(requests.get("event_meanings") or {})
    total += len(requests.get("info_notes") or {})
    total += len(requests.get("misc_notes") or {})
    total += len(requests.get("task_notes") or {})
    return total


def _requests_payload(requests: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "paradigm": requests["paradigm"].as_dict() if requests.get("paradigm") else None,
        "event_meanings": {k: v.as_dict() for k, v in (requests.get("event_meanings") or {}).items()},
        "event_structure_note": (
            requests["event_structure_note"].as_dict() if requests.get("event_structure_note") else None
        ),
        "info_notes": {k: v.as_dict() for k, v in (requests.get("info_notes") or {}).items()},
        "misc_notes": {k: v.as_dict() for k, v in (requests.get("misc_notes") or {}).items()},
        "task_notes": {k: v.as_dict() for k, v in (requests.get("task_notes") or {}).items()},
    }


def _format_sidecar_evidence(sidecars: Mapping[str, Any]) -> str:
    if not sidecars:
        return "(no raw-data sidecar evidence loaded)"
    parts: List[str] = []
    for key in (
        "participants_summary",
        "participants_tsv_sample",
        "dataset_description",
        "eeg_json",
        "readme",
    ):
        value = sidecars.get(key)
        if value:
            parts.append(f"=== {key} ===\n{value}")
    for key in ("events_jsons", "events_tsv_samples"):
        value = sidecars.get(key)
        if isinstance(value, Mapping) and value:
            lines = [f"=== {key} ==="]
            for name, content in value.items():
                lines.append(f"[{name}]\n{content}")
            parts.append("\n".join(lines))
    return "\n\n".join(parts)[:18000]


def _extract_json_object(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    text = re.sub(r"```json\s*([\s\S]*?)```", r"\1", text, flags=re.IGNORECASE).strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"Could not parse JSON object from LLM response: {raw[:400]!r}")


def _unique_str_list(values: Iterable[Any]) -> List[str]:
    out: List[str] = []
    for value in values:
        item = str(value or "").strip()
        if item and item not in out:
            out.append(item)
    return out


def _normalize_kernel_requirements(plan: Mapping[str, Any]) -> Dict[str, Any]:
    derived = plan.get("derived_misc_channels") or []
    clean_derived: List[Dict[str, str]] = []
    for item in derived:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        clean_derived.append({
            "name": name,
            "source_field": str(item.get("source_field") or "").strip(),
            "derivation": str(item.get("derivation") or "").strip(),
            "groundable_evidence": str(item.get("groundable_evidence") or "").strip(),
        })
    return {
        "required_event_ids": _unique_str_list(plan.get("required_event_ids") or []),
        "required_native_misc": _unique_str_list(plan.get("required_native_misc") or []),
        "required_info_fields": _unique_str_list(plan.get("required_info_fields") or []),
        "derived_misc_channels": clean_derived,
    }


def _plan_upgrade(
    dataset_name: str,
    analysis_text: str,
    requests: Mapping[str, Any],
    context: Mapping[str, Any],
    llm_config: Mapping[str, Any],
    log,
) -> Dict[str, Any]:
    payload = _requests_payload(requests)
    user_prompt = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Review requests ===\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        f"=== Trusted analysis.md ===\n{analysis_text[:28000]}\n\n"
        f"=== Existing kernel ===\n```python\n{context.get('existing_kernel', '')[:16000]}\n```\n\n"
        f"=== Raw-data evidence ===\n{_format_sidecar_evidence(context.get('bids_sidecars') or {})}\n\n"
        f"=== EEG header summary ===\n{context.get('eeg_header_summary', '')[:3000]}"
    )
    raw = call_llm_text(
        llm_config,
        [{"role": "system", "content": _PLANNER_SYSTEM}, {"role": "user", "content": user_prompt}],
        timeout=300,
    )
    plan = _extract_json_object(raw)
    plan["kernel_change_required"] = bool(plan.get("kernel_change_required"))
    plan["feasible"] = bool(plan.get("feasible", True))
    plan["patch_goals"] = _unique_str_list(plan.get("patch_goals") or [])
    plan["doc_goals"] = _unique_str_list(plan.get("doc_goals") or [])
    plan["feasibility_reason"] = str(plan.get("feasibility_reason") or "").strip()
    plan["kernel_requirements"] = _normalize_kernel_requirements(plan)
    log(
        "[upgrade] Planner: "
        f"kernel_change_required={plan['kernel_change_required']} "
        f"feasible={plan['feasible']} "
        f"requirements={json.dumps(plan['kernel_requirements'], ensure_ascii=False)}"
    )
    return plan


def _render_doc_updates(
    dataset_name: str,
    requests: Mapping[str, Any],
    original_analysis: str,
    current_analysis: str,
    plan: Mapping[str, Any],
    llm_config: Mapping[str, Any],
) -> Dict[str, Any]:
    payload = _requests_payload(requests)
    plan_view = {
        "patch_goals": plan.get("patch_goals") or [],
        "doc_goals": plan.get("doc_goals") or [],
        "kernel_requirements": plan.get("kernel_requirements") or {},
        "feasibility_reason": plan.get("feasibility_reason") or "",
    }
    user_prompt = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Review requests ===\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        f"=== Planner summary ===\n{json.dumps(plan_view, ensure_ascii=False, indent=2)}\n\n"
        f"=== Original trusted analysis.md ===\n{original_analysis[:26000]}\n\n"
        f"=== Current analysis.md after full_scan (or current working version) ===\n{current_analysis[:26000]}"
    )
    raw = call_llm_text(
        llm_config,
        [{"role": "system", "content": _DOC_RENDER_SYSTEM}, {"role": "user", "content": user_prompt}],
        timeout=300,
    )
    data = _extract_json_object(raw)
    return {
        "paradigm": data.get("paradigm") if isinstance(data.get("paradigm"), Mapping) else None,
        "event_meanings": dict(data.get("event_meanings") or {}),
        "event_structure_note": (
            data.get("event_structure_note") if isinstance(data.get("event_structure_note"), Mapping) else None
        ),
        "info_notes": dict(data.get("info_notes") or {}),
        "misc_notes": dict(data.get("misc_notes") or {}),
        "task_notes": dict(data.get("task_notes") or {}),
    }


def _merge_doc_update_defaults(requests: Mapping[str, Any], updates: Mapping[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "paradigm": updates.get("paradigm"),
        "event_meanings": dict(updates.get("event_meanings") or {}),
        "event_structure_note": updates.get("event_structure_note"),
        "info_notes": dict(updates.get("info_notes") or {}),
        "misc_notes": dict(updates.get("misc_notes") or {}),
        "task_notes": dict(updates.get("task_notes") or {}),
    }
    if requests.get("paradigm") and merged["paradigm"] is None:
        merged["paradigm"] = {"text": requests["paradigm"].clean_text}
    if requests.get("event_structure_note") and merged["event_structure_note"] is None:
        merged["event_structure_note"] = {"text": requests["event_structure_note"].clean_text}
    for key, req in (requests.get("event_meanings") or {}).items():
        merged["event_meanings"].setdefault(key, req.clean_text)
    for key, req in (requests.get("info_notes") or {}).items():
        merged["info_notes"].setdefault(key, req.clean_text)
    for key, req in (requests.get("misc_notes") or {}).items():
        merged["misc_notes"].setdefault(key, req.clean_text)
    for key, req in (requests.get("task_notes") or {}).items():
        merged["task_notes"].setdefault(key, req.clean_text)
    return merged


def _run_kernel_test(
    kernel_code: str,
    dataset_name: str,
    dataset_path: str,
    python_env: str,
    eegunity_path: str,
    sandbox_dir: Path,
    kernel_requirements: Mapping[str, Any],
    log,
) -> Tuple[bool, str]:
    static_errors = _static_validate(kernel_code, dict(kernel_requirements))
    if static_errors:
        return False, "\n".join(static_errors)

    sec_errors = _security_check(kernel_code)
    if sec_errors:
        return False, "\n".join(sec_errors)

    sample_files = _pick_sample_files(Path(dataset_path))
    kernel_path = sandbox_dir / f"{dataset_name}.upgrade.test.py"
    kernel_path.write_text(kernel_code, encoding="utf-8")

    if not sample_files:
        return True, "No sample EEG files found; static validation passed."

    test_script = _build_test_script(kernel_path, sample_files, eegunity_path, python_env)
    test_path = sandbox_dir / f"{dataset_name}.upgrade.test_runner.py"
    test_path.write_text(test_script, encoding="utf-8")

    result = subprocess.run(
        [python_env, str(test_path)],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(sandbox_dir),
    )
    combined = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()
    if combined:
        for line in combined.splitlines()[-20:]:
            log(f"  {line}")
    return result.returncode == 0, combined


def _patch_kernel_incrementally(
    dataset_name: str,
    analysis_text: str,
    requests: Mapping[str, Any],
    plan: Mapping[str, Any],
    context: Mapping[str, Any],
    llm_config: Mapping[str, Any],
    dataset_path: str,
    python_env: str,
    eegunity_path: str,
    sandbox_dir: Path,
    log,
) -> Tuple[str, bool]:
    current_kernel = str(context.get("existing_kernel") or "")
    if not current_kernel.strip():
        raise RuntimeError(f"No existing kernel found for {dataset_name}; upgrade requires an existing kernel.")

    payload = _requests_payload(requests)
    kernel_requirements = dict(plan.get("kernel_requirements") or {})
    goals_json = json.dumps({
        "patch_goals": plan.get("patch_goals") or [],
        "kernel_requirements": kernel_requirements,
    }, ensure_ascii=False, indent=2)
    sidecar_text = _format_sidecar_evidence(context.get("bids_sidecars") or {})
    last_error = ""
    candidate_code = current_kernel

    for attempt in range(1, 5):
        log(f"[upgrade] Kernel patch attempt {attempt}/4")
        if attempt == 1:
            user_prompt = (
                f"Dataset: {dataset_name}\n\n"
                f"=== Requested upgrade locations ===\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
                f"=== Upgrade goals ===\n{goals_json}\n\n"
                f"=== Trusted analysis.md ===\n{analysis_text[:22000]}\n\n"
                f"=== Raw-data evidence ===\n{sidecar_text}\n\n"
                f"=== Existing kernel to patch ===\n```python\n{current_kernel[:20000]}\n```"
            )
            raw = call_llm_text(
                llm_config,
                [{"role": "system", "content": _UPGRADE_KERNEL_SYSTEM}, {"role": "user", "content": user_prompt}],
                timeout=360,
            )
        else:
            user_prompt = (
                f"Dataset: {dataset_name}\n\n"
                f"=== Current candidate kernel ===\n```python\n{candidate_code[:22000]}\n```\n\n"
                f"=== Upgrade goals ===\n{goals_json}\n\n"
                f"=== Failure details ===\n{last_error[:8000]}"
            )
            raw = call_llm_text(
                llm_config,
                [{"role": "system", "content": _UPGRADE_KERNEL_FIX_SYSTEM}, {"role": "user", "content": user_prompt}],
                timeout=360,
            )

        code = _extract_code_block(raw)
        if not code:
            last_error = "LLM returned no Python code block."
            continue

        candidate_code = code
        ok, detail = _run_kernel_test(
            candidate_code,
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            python_env=python_env,
            eegunity_path=eegunity_path,
            sandbox_dir=sandbox_dir,
            kernel_requirements=kernel_requirements,
            log=log,
        )
        if ok:
            return candidate_code, True
        last_error = detail or "Kernel test failed."

    return candidate_code, False


def _run_full_scan(dataset_name: str, python_env: str, config_path: Optional[Path], log) -> None:
    cmd = [python_env, str(AGENT_DIR / "full_scan.py"), "--dataset", dataset_name]
    if config_path:
        cmd.extend(["--config", str(config_path)])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=360,
        cwd=str(AGENT_DIR.parent),
    )
    combined = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()
    if combined:
        for line in combined.splitlines()[-30:]:
            log(f"  {line}")
    if result.returncode != 0:
        raise RuntimeError(f"full_scan failed for {dataset_name}")


def _patch_table_notes(subsection: str, key_header: str, notes_header: str, updates: Mapping[str, str]) -> str:
    if not subsection or not updates:
        return subsection
    lines = subsection.splitlines()
    header_idx = None
    notes_idx = None
    key_idx = None
    for idx, line in enumerate(lines):
        cells = _split_md_row(line)
        if not cells:
            continue
        if key_header in cells and notes_header in cells:
            header_idx = idx
            key_idx = cells.index(key_header)
            notes_idx = cells.index(notes_header)
            break
    if header_idx is None or key_idx is None or notes_idx is None:
        return subsection

    for idx in range(header_idx + 2, len(lines)):
        cells = _split_md_row(lines[idx])
        if not cells:
            break
        if len(cells) <= max(key_idx, notes_idx):
            continue
        key = cells[key_idx].strip().strip("`")
        if key in updates:
            cells[notes_idx] = str(updates[key] or "").strip()
            lines[idx] = _format_md_row(cells)
    return "\n".join(lines)


def _patch_event_structure(subsection: str, meaning_updates: Mapping[str, str], note_text: Optional[str]) -> str:
    if not subsection:
        return subsection
    lines = subsection.splitlines()
    heading_end = 0
    table_end = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("|"):
            table_end = idx + 1
        if idx == 0 and line.strip().startswith("### "):
            heading_end = 1
    for idx in range(heading_end, len(lines)):
        cells = _split_md_row(lines[idx])
        if not cells or len(cells) < 5:
            continue
        if cells[0] == "Event ID" or re.fullmatch(r"-+", cells[0].replace(" ", "")):
            continue
        event_id = cells[0].strip().strip("`")
        if event_id in meaning_updates:
            cells[4] = str(meaning_updates[event_id] or "").strip()
            lines[idx] = _format_md_row(cells)

    rebuilt = lines[:table_end]
    post_table = lines[table_end:]
    if note_text is None:
        if post_table:
            rebuilt.extend(post_table)
        return "\n".join(rebuilt).rstrip() + "\n"

    while post_table and not post_table[0].strip():
        post_table = post_table[1:]
    while post_table and post_table[0].strip().startswith(">"):
        post_table = post_table[1:]
    new_note = (note_text or "").strip()
    if new_note:
        rebuilt.append("")
        for line in new_note.splitlines():
            rebuilt.append(f"> {line.strip()}")
    if post_table:
        rebuilt.append("")
        rebuilt.extend(post_table)
    return "\n".join(rebuilt).rstrip() + "\n"


def _patch_paradigm(text: str, new_text: Optional[str]) -> str:
    if new_text is None:
        return text
    body = str(new_text or "").strip()
    new_block = "## Paradigm\n\n" + body + "\n"
    return _replace_section(text, 2, "Paradigm", new_block)


def _patch_task_notes(text: str, updates: Mapping[str, str]) -> str:
    if not updates:
        return text
    tasks_section = _extract_section(text, 2, "Tasks")
    if not tasks_section:
        return text
    rebuilt = tasks_section
    for title, _, _, block in list(_iter_level3_blocks(tasks_section))[::-1]:
        if title not in updates:
            continue
        new_note = str(updates[title] or "").strip()
        if re.search(r"^- \*\*Notes\*\*:", block, re.MULTILINE):
            patched = re.sub(
                r"^- \*\*Notes\*\*:\s*.*$",
                f"- **Notes**: {new_note}",
                block,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            patched = block.rstrip() + f"\n- **Notes**: {new_note}\n"
        rebuilt = rebuilt.replace(block, patched, 1)
    return _replace_section(text, 2, "Tasks", rebuilt)


def _apply_doc_updates(text: str, updates: Mapping[str, Any]) -> str:
    out = _patch_paradigm(text, (updates.get("paradigm") or {}).get("text") if updates.get("paradigm") else None)

    fsr = _extract_section(out, 2, "File Scan Result")
    if fsr:
        event_block = _extract_section(fsr, 3, "Event Structure")
        note_payload = updates.get("event_structure_note") or {}
        if event_block and ((updates.get("event_meanings") or {}) or updates.get("event_structure_note") is not None):
            patched_event = _patch_event_structure(
                event_block,
                updates.get("event_meanings") or {},
                note_payload.get("text") if updates.get("event_structure_note") is not None else None,
            )
            fsr = fsr.replace(event_block, patched_event, 1)
        misc_block = _extract_section(fsr, 3, "MISC Label Summary")
        if misc_block:
            patched_misc = _patch_table_notes(
                misc_block,
                key_header="Channel",
                notes_header="Notes",
                updates=updates.get("misc_notes") or {},
            )
            fsr = fsr.replace(misc_block, patched_misc, 1)
        info_block = _extract_section(fsr, 3, "Info")
        if info_block:
            patched_info = _patch_table_notes(
                info_block,
                key_header="Field",
                notes_header="Notes",
                updates=updates.get("info_notes") or {},
            )
            fsr = fsr.replace(info_block, patched_info, 1)
        out = _replace_section(out, 2, "File Scan Result", fsr)

    out = _patch_task_notes(out, updates.get("task_notes") or {})
    return out


def _ensure_llm_ready(cfg: Mapping[str, Any]) -> Dict[str, Any]:
    llm_cfg = resolve_llm_config(cfg)
    if not llm_cfg.get("active_url"):
        raise RuntimeError("LLM URL not configured. upgrade.py requires an active LLM config.")
    if not llm_cfg.get("key"):
        raise RuntimeError("LLM API key not configured. upgrade.py requires an active LLM config.")
    if not llm_cfg.get("model"):
        raise RuntimeError("LLM model not configured. upgrade.py requires an active LLM config.")
    return llm_cfg


def _write_log(log_path: Path, lines: List[str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Incrementally upgrade a dataset kernel and analysis.md.")
    parser.add_argument("--dataset", "-d", required=True, help="Dataset ID, e.g. openneuro_ds002722")
    parser.add_argument("--config", default=None, help="Optional machine_config JSON path")
    parser.add_argument("--plan-only", action="store_true", help="Parse requests and emit planner result only")
    args = parser.parse_args()

    dataset_name = args.dataset.strip()
    if not dataset_name:
        raise SystemExit("ERROR: --dataset cannot be empty.")

    cfg, cfg_path = _find_config(args.config)
    llm_cfg = _ensure_llm_ready(cfg)
    dataset_roots = list(cfg.get("dataset_roots") or [])
    python_env = str(cfg.get("python_env") or sys.executable)
    eegunity_path = str(cfg.get("eegunity_path") or "")
    dataset_path = scan_engine.find_dataset_path(dataset_name, dataset_roots)
    kernel_rel = scan_engine.detect_kernel_path(dataset_name)
    analysis_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"

    if not dataset_path:
        searched = ", ".join(dataset_roots) or "(none configured)"
        raise SystemExit(f"ERROR: Dataset {dataset_name} not found in configured roots: {searched}")
    if not kernel_rel:
        raise SystemExit(f"ERROR: No existing kernel found for {dataset_name}.")
    if not analysis_path.exists():
        raise SystemExit(f"ERROR: analysis.md not found: {analysis_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"{dataset_name}.upgrade.{timestamp}.log"
    log_lines: List[str] = []

    def log(msg: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {msg}"
        print(line)
        log_lines.append(line)

    original_analysis = analysis_path.read_text(encoding="utf-8", errors="replace")
    requests = _parse_review_requests(original_analysis)
    total_requests = _request_count(requests)
    log(f"[upgrade] Dataset: {dataset_name}")
    log(f"[upgrade] Kernel: {kernel_rel}")
    log(f"[upgrade] analysis.md: {analysis_path}")
    log(f"[upgrade] Found [to_agent] requests: {total_requests}")
    if total_requests == 0:
        _write_log(log_path, log_lines)
        raise SystemExit("No [to_agent: ...] requests found in supported locations.")

    context = build_context(dataset_name, log, data_dir=dataset_path)
    plan = _plan_upgrade(dataset_name, original_analysis, requests, context, llm_cfg, log)
    if args.plan_only:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        _write_log(log_path, log_lines)
        return

    if plan["kernel_change_required"] and not plan["feasible"]:
        _write_log(log_path, log_lines)
        raise SystemExit(f"Planner marked request infeasible: {plan['feasibility_reason'] or '(no reason given)'}")

    kernel_changed = False
    if plan["kernel_change_required"]:
        sandbox_dir = SANDBOX_DIR / f"{dataset_name}_upgrade_{timestamp}"
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        log(f"[upgrade] Patching kernel in {sandbox_dir}")
        patched_code, ok = _patch_kernel_incrementally(
            dataset_name=dataset_name,
            analysis_text=original_analysis,
            requests=requests,
            plan=plan,
            context=context,
            llm_config=llm_cfg,
            dataset_path=dataset_path,
            python_env=python_env,
            eegunity_path=eegunity_path,
            sandbox_dir=sandbox_dir,
            log=log,
        )
        if not ok:
            _write_log(log_path, log_lines)
            raise SystemExit("Kernel patch failed after all retries.")
        install_kernel(patched_code, dataset_name, log)
        kernel_changed = True

    if kernel_changed:
        log("[upgrade] Running full_scan to refresh File Scan Result")
        _run_full_scan(dataset_name, python_env=python_env, config_path=cfg_path, log=log)

    current_analysis = analysis_path.read_text(encoding="utf-8", errors="replace")
    updates = _render_doc_updates(dataset_name, requests, original_analysis, current_analysis, plan, llm_cfg)
    updates = _merge_doc_update_defaults(requests, updates)
    updated_analysis = _apply_doc_updates(current_analysis, updates)
    analysis_path.write_text(updated_analysis, encoding="utf-8")
    log(f"[upgrade] analysis.md updated: {analysis_path}")
    _write_log(log_path, log_lines)
    log(f"[upgrade] Log written: {log_path}")


if __name__ == "__main__":
    main()
