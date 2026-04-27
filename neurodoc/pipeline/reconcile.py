"""Phase 6.5: Reconcile Tasks section against actual scan output.

Purpose: the LLM can hallucinate Label Fields / derived misc channels that the
kernel never actually produces. After the final scan runs, this module cross-
references every Task's referenced field against the real scan whitelist:

  - event IDs → scan_result["event_counts"] keys
  - native misc → scan_result["misc_channel_names"]
  - info fields → participants.tsv columns (from bids_sidecars) + canonical

For any missing field, the logic is:
  1. If the missing field is in kernel_requirements.derived_misc_channels AND this
     patch pass hasn't happened yet → attempt ONE kernel patch + ONE rescan.
  2. Otherwise → DROP the offending task from the Tasks section (and renumber).

This module does NOT rewrite scan output. File Scan Result is still programmatic
(doc_writer builds it from scan_result). Reconcile only prunes the Tasks section.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ref_analyzer import _parse_json
from .task_synthesizer import (
    _split_task_blocks,
    _get_task_field,
    _get_task_title,
    _renumber_tasks,
)


CANONICAL_INFO_FIELDS = {"subject_age", "subject_sex", "device", "age", "sex", "handedness"}


# ──────────────────────────────────────────────────────────────────────────────
# Whitelist construction from scan output
# ──────────────────────────────────────────────────────────────────────────────

def _read_participants_columns(data_dir: Optional[str]) -> set:
    """Return the authoritative set of columns in participants.tsv, or empty set."""
    if not data_dir:
        return set()
    p = Path(data_dir) / "participants.tsv"
    if not p.exists():
        return set()
    try:
        header = p.read_text(encoding="utf-8").splitlines()[0]
    except Exception:
        return set()
    return {c.strip() for c in header.split("\t") if c.strip()}


def build_scan_whitelist(
    scan_result: Dict[str, Any],
    bids_sidecars: Optional[Dict[str, Any]] = None,
    data_dir: Optional[str] = None,
) -> Dict[str, set]:
    """Return {'events': set, 'misc': set, 'info': set} of what the kernel actually exposes.

    The info set is authoritative-first: if `data_dir` is given we read the
    header of `<data_dir>/participants.tsv` directly. We also include anything
    the sidecar cache lists plus the canonical keys as a safety net.
    """
    events = set()
    for k in (scan_result.get("event_counts") or {}).keys():
        events.add(str(k))

    misc = set()
    for c in (scan_result.get("misc_channel_names") or []) or []:
        if isinstance(c, str) and c:
            misc.add(c)

    info = set(CANONICAL_INFO_FIELDS)
    info.update(_read_participants_columns(data_dir))
    if bids_sidecars:
        for f in (bids_sidecars.get("participants_fields") or []):
            name = f.get("name") if isinstance(f, dict) else None
            if name:
                info.add(name)

    return {"events": events, "misc": misc, "info": info}


# ──────────────────────────────────────────────────────────────────────────────
# Per-task extraction of referenced fields
# ──────────────────────────────────────────────────────────────────────────────

_EVENT_ID_IN_TD = re.compile(r"\|\s*`?([A-Za-z0-9_.:+\-]+)`?\s*\|")


def _extract_target_events_from_epoch_params(block: str) -> List[str]:
    """Pull out the target_events = [...] list from the Epoch Parameters bullet."""
    m = re.search(
        r"\*\*Epoch Parameters\*\*:\s*([^\n]+(?:\n\s{2,}[^\n]+)*)",
        block,
    )
    if not m:
        return []
    params_text = m.group(1)
    lst = re.search(r"target_events\s*=\s*\[([^\]]*)\]", params_text)
    if not lst:
        return []
    inside = lst.group(1).strip()
    if not inside:
        return []
    items = re.findall(r"`([^`]+)`", inside)
    if items:
        return items
    return [s.strip().strip("'").strip('"') for s in inside.split(",") if s.strip()]


def _extract_referenced_fields(block: str) -> Dict[str, Any]:
    """Parse one Task block into {route, task_type, label_field, event_ids, meta_level, epoch_method}."""
    route = (_get_task_field(block, "Label Route") or "").strip("`").lower()
    task_type = (_get_task_field(block, "Task Type") or "").strip().lower()
    label_field_raw = _get_task_field(block, "Label Field") or ""
    label_field = label_field_raw.strip().strip("`").split()[0] if label_field_raw else ""
    meta_level = (_get_task_field(block, "Meta Level") or "").strip("`").lower()
    epoch_method_raw = (_get_task_field(block, "Epoch Method") or "").strip("`")
    epoch_method = epoch_method_raw.strip() or ""
    target_events = _extract_target_events_from_epoch_params(block)
    return {
        "route": route,
        "task_type": task_type,
        "label_field": label_field,
        "meta_level": meta_level,
        "epoch_method": epoch_method,
        "target_events": target_events,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Reconcile decision
# ──────────────────────────────────────────────────────────────────────────────

def _is_derived_misc_in_requirements(
    field_name: str,
    kernel_requirements: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    for d in (kernel_requirements.get("derived_misc_channels") or []):
        if d.get("name") == field_name:
            return d
    return None


def _find_missing(
    parsed: Dict[str, Any],
    whitelist: Dict[str, set],
) -> List[str]:
    """Return a list of (human-readable) missing-field descriptions for this task."""
    missing: List[str] = []

    if parsed["epoch_method"] != "epoch_by_segmentation_hdf5":
        for e in parsed["target_events"]:
            if e and e not in whitelist["events"]:
                missing.append(f"event:{e}")

    route = parsed["route"]
    lf = parsed["label_field"]
    if route == "misc" and lf:
        if lf not in whitelist["misc"]:
            missing.append(f"misc:{lf}")
    elif route == "info" and lf:
        if lf not in whitelist["info"]:
            missing.append(f"info:{lf}")
    return missing


def classify_tasks(
    tasks_section: str,
    whitelist: Dict[str, set],
    kernel_requirements: Dict[str, Any],
    log,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], str]:
    """Split tasks into (patchable_tasks, drop_tasks, ok_tasks, prefix).

    'patchable' means the task references a derived misc that exists in kernel_requirements
    but not yet in the scan — a kernel patch could produce it.
    'drop' means the task references something not in scan AND not in requirements (or
    in requirements but un-patchable for other reasons like event ID missing).
    """
    prefix, blocks = _split_task_blocks(tasks_section)
    patchable: List[Dict[str, Any]] = []
    drop: List[Dict[str, Any]] = []
    ok: List[Dict[str, Any]] = []

    for block in blocks:
        title = _get_task_title(block)
        parsed = _extract_referenced_fields(block)
        missing = _find_missing(parsed, whitelist)
        if not missing:
            ok.append({"title": title, "block": block})
            continue
        # Any missing event → drop (we don't patch event IDs — those come from data files)
        if any(m.startswith("event:") for m in missing):
            drop.append({"title": title, "block": block, "missing": missing,
                         "reason": "referenced event id(s) not produced by kernel scan"})
            continue
        # Missing misc/info → check if patchable via kernel_requirements derived_misc_channels
        all_patchable = True
        patch_items: List[Dict[str, Any]] = []
        for m in missing:
            kind, name = m.split(":", 1)
            if kind == "misc":
                req = _is_derived_misc_in_requirements(name, kernel_requirements)
                if not req:
                    all_patchable = False
                    break
                patch_items.append({"kind": "misc", "name": name, "requirement": req})
            elif kind == "info":
                # info fields are read-only from participants.tsv — kernel patch cannot
                # "add" a participants column that doesn't exist
                all_patchable = False
                break
        if all_patchable and patch_items:
            patchable.append({"title": title, "block": block, "missing": missing,
                              "patch_items": patch_items, "parsed": parsed})
        else:
            drop.append({"title": title, "block": block, "missing": missing,
                         "reason": "referenced field not producable by kernel (no derivation path)"})

    if ok:
        log(f"[Reconcile] {len(ok)} task(s) clean against scan.")
    if patchable:
        log(f"[Reconcile] {len(patchable)} task(s) need a kernel patch:")
        for p in patchable:
            log(f"  - {p['title']} → missing {p['missing']}")
    if drop:
        log(f"[Reconcile] {len(drop)} task(s) will be dropped:")
        for d in drop:
            log(f"  - {d['title']} → {d['reason']} (missing {d['missing']})")

    return patchable, drop, ok, prefix  # type: ignore[return-value]


def _drop_blocks_from_section(tasks_section: str, blocks_to_drop: List[str]) -> str:
    """Return tasks_section with the given raw blocks removed, then renumber."""
    if not blocks_to_drop:
        return tasks_section
    prefix, blocks = _split_task_blocks(tasks_section)
    drop_set = set(b for b in blocks_to_drop)
    kept = [b for b in blocks if b not in drop_set]
    new_section = prefix + "".join(kept)
    return _renumber_tasks(new_section)


# ──────────────────────────────────────────────────────────────────────────────
# Kernel patch prompt
# ──────────────────────────────────────────────────────────────────────────────

_KERNEL_PATCH_SYSTEM = """\
You are an EEG kernel engineer. Patch the provided Python kernel so that the listed
derived misc channels are produced in every file's output. Preserve everything else.

Output ONLY a Python code block, no explanation, no JSON:
```python
<full corrected kernel source code>
```

Constraints on the patch:
- def apply(self, udataset, raw, row) -> mne.io.BaseRaw:   (exact signature, one line)
- KERNEL = <ClassName>()  at end of file
- eegunity_description dict with: age (str), sex, amplifier, cap, handedness
- The derived misc channels you add MUST be created from the SPECIFIED source_field.
  source_field formats:
    * "<column>"              → read from participants.tsv (subject-level scalar).
    * "events.tsv:<column>"   → read from the sibling events.tsv (per-trial scalar).
  If the source is not actually available at apply() time, do NOT fabricate values;
  skip that channel (reconcile will drop the task rather than accept hallucinated data).
- No os.remove / shutil.rmtree / subprocess / eval / exec / write-mode open.

Mechanism for materialising the derived channel is YOUR call — constant broadcast is
fine for participants.tsv sources (one value per file); events.tsv sources typically
warrant a trial-locked step function (channel value updates at each annotation onset).
Use MNE idioms: mne.io.RawArray + raw.add_channels([...]), or set_channel_types after
concatenation. Only invariants: exact `name` in raw.ch_names, ch_type 'misc', data
shape (1, len(raw.times)), finite values.
"""


def _extract_code_block(raw: str) -> str:
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    m = re.search(r"```python\s*\n([\s\S]*?)\n```", raw, re.IGNORECASE)
    if not m:
        m = re.search(r"```\s*\n([\s\S]*?)\n```", raw)
    if m:
        return m.group(1).strip()
    if "def apply" in raw and "KERNEL" in raw:
        return raw.strip()
    return ""


def patch_kernel_for_derived_misc(
    current_kernel_code: str,
    patch_items: List[Dict[str, Any]],
    dataset_name: str,
    call_llm,
    budget,
    log,
) -> Optional[str]:
    """Call LLM to add derived misc channels to the kernel. Returns new code or None."""
    log(f"[Reconcile] Requesting kernel patch for {len(patch_items)} derived misc channel(s)...")

    # De-duplicate requirements by name
    seen: Dict[str, Dict[str, Any]] = {}
    for item in patch_items:
        req = item.get("requirement") or {}
        name = req.get("name")
        if name and name not in seen:
            seen[name] = req
    unique_reqs = list(seen.values())

    reqs_block = json.dumps(unique_reqs, indent=2, ensure_ascii=False)
    user_msg = (
        f"Dataset: {dataset_name}\n\n"
        f"=== Current kernel ===\n```python\n{current_kernel_code[:12000]}\n```\n\n"
        f"=== Derived misc channels the kernel must now produce ===\n{reqs_block}\n\n"
        f"For each entry, read the source_field from participants.tsv for the current subject,\n"
        f"then append a misc-type channel named `<name>` with that value broadcast to the full duration.\n"
        f"If the source column is not actually available, skip that entry rather than inventing data."
    )
    try:
        budget.charge("kernel_loop")
        raw = call_llm([
            {"role": "system", "content": _KERNEL_PATCH_SYSTEM},
            {"role": "user", "content": user_msg},
        ])
    except Exception as exc:
        log(f"[Reconcile] Kernel patch LLM call failed: {exc}")
        return None
    code = _extract_code_block(raw)
    if not code:
        log("[Reconcile] Kernel patch returned no Python code block.")
        return None
    return code


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def reconcile(
    tasks_section: str,
    scan_result: Dict[str, Any],
    kernel_requirements: Dict[str, Any],
    kernel_code: str,
    dataset_name: str,
    bids_sidecars: Optional[Dict[str, Any]],
    call_llm,
    budget,
    log,
    rescan_func: Optional[Callable[[str], Dict[str, Any]]] = None,
    install_func: Optional[Callable[[str], str]] = None,
    data_dir: Optional[str] = None,
) -> Tuple[str, Dict[str, Any], str, bool]:
    """Reconcile tasks against scan. Drops hallucinated tasks, optionally patches kernel once.

    Parameters:
      tasks_section        — current '## Tasks' markdown.
      scan_result          — latest scan_result dict (has event_counts, misc_channel_names).
      kernel_requirements  — dict from task_synthesizer_v2 (derived_misc_channels etc.).
      kernel_code          — current kernel Python source (for patching).
      rescan_func          — callable(new_kernel_path) -> new scan_result; required for patch path.
      install_func         — callable(new_kernel_code) -> installed_kernel_path; required for patch path.
      data_dir             — raw BIDS dataset directory; used to read participants.tsv header
                             directly so the info whitelist is authoritative.

    Returns:
      (final_tasks_section, final_scan_result, final_kernel_code, did_patch)
    """
    whitelist = build_scan_whitelist(scan_result, bids_sidecars, data_dir)
    log(
        f"[Reconcile] Scan whitelist: "
        f"events={len(whitelist['events'])}, misc={len(whitelist['misc'])}, info={len(whitelist['info'])}"
    )

    result = classify_tasks(tasks_section, whitelist, kernel_requirements, log)
    # classify_tasks returns (patchable, drop, ok, prefix)
    patchable: List[Dict[str, Any]]
    drop: List[Dict[str, Any]]
    ok: List[Dict[str, Any]]
    patchable, drop, ok, _prefix = result  # type: ignore[misc]

    did_patch = False
    new_scan_result = scan_result
    new_kernel_code = kernel_code

    # Patch path (at most once)
    if patchable and rescan_func and install_func:
        all_patch_items = [pi for p in patchable for pi in p["patch_items"]]
        patched_code = patch_kernel_for_derived_misc(
            kernel_code, all_patch_items, dataset_name, call_llm, budget, log
        )
        if patched_code:
            try:
                installed_path = install_func(patched_code)
                log(f"[Reconcile] Patched kernel installed at: {installed_path}")
                new_scan_result = rescan_func(installed_path)
                new_kernel_code = patched_code
                did_patch = True
                # Re-classify with fresh whitelist
                whitelist = build_scan_whitelist(new_scan_result, bids_sidecars, data_dir)
                log(
                    f"[Reconcile] Post-patch whitelist: "
                    f"events={len(whitelist['events'])}, misc={len(whitelist['misc'])}, info={len(whitelist['info'])}"
                )
                result2 = classify_tasks(tasks_section, whitelist, kernel_requirements, log)
                patchable, drop, ok, _prefix = result2  # type: ignore[misc]
            except Exception as exc:
                log(f"[Reconcile] Patch+rescan failed: {exc}. Falling back to drop.")

    # Anything still 'patchable' after one attempt (or if no rescan func) → drop
    blocks_to_drop = [p["block"] for p in patchable] + [d["block"] for d in drop]
    if blocks_to_drop:
        tasks_section = _drop_blocks_from_section(tasks_section, blocks_to_drop)
        log(f"[Reconcile] Dropped {len(blocks_to_drop)} task(s) after reconciliation.")

    return tasks_section, new_scan_result, new_kernel_code, did_patch
