"""Phase 6: Run EEGUnity scan via scan_engine and return structured results."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from ..paths import NEURODOC_DIR
except ImportError:
    from paths import NEURODOC_DIR


def _ensure_scan_engine():
    if str(NEURODOC_DIR) not in sys.path:
        sys.path.insert(0, str(NEURODOC_DIR))
    import scan_engine
    return scan_engine


def run_scan(
    dataset_name: str,
    kernel_path: str,
    dataset_roots: List[str],
    eegunity_path: str,
    num_workers: int,
    log,
) -> Dict[str, Any]:
    """
    Run a full scan via scan_engine.run_full_scan().
    Returns scan_result dict ready for merge_scan_results().
    """
    engine = _ensure_scan_engine()

    log(f"[ScanBridge] Starting scan for {dataset_name}...")
    log(f"[ScanBridge] Kernel: {kernel_path or '(default parser)'}")

    stdout_lines: List[str] = []

    def _cb(step: str, pct: int):
        log(f"[ScanBridge] {pct}% — {step}")

    kernel_sha = engine.get_kernel_sha256(kernel_path or "")
    eegu_ver = engine.get_eegunity_version(eegunity_path)

    df, misc_channel_names = engine.run_full_scan(
        dataset_name=dataset_name,
        dataset_roots=dataset_roots,
        kernel_path=kernel_path or None,
        eegunity_path=eegunity_path,
        progress_cb=_cb,
        stdout_lines=stdout_lines,
        sampled_indices=None,
        num_workers=num_workers,
        persist_base_cache=True,
        persist_metadata_cache=True,
        kernel_sha256=kernel_sha,
        eegunity_version=eegu_ver,
    )

    for line in stdout_lines:
        log(f"  {line}")

    event_counts = engine.extract_event_stats(df)
    subject_info = engine.extract_subject_info(df)
    total_n = len(df)

    log(f"[ScanBridge] Scan done: {total_n} files, {len(event_counts)} event types")

    return {
        "kernel_path": kernel_path or "",
        "kernel_sha256": kernel_sha,
        "eegunity_version": eegu_ver,
        "scan_type": "full",
        "sampled": False,
        "sampled_n": total_n,
        "total_n": total_n,
        "cache_source": "live_full_scan",
        "event_counts": event_counts,
        "subject_info": subject_info,
        "misc_channel_names": misc_channel_names,
        "df": df,
    }


def get_event_ids_preview(scan_result: Dict[str, Any]) -> str:
    """Return a human-readable list of event IDs for use in LLM prompts."""
    counts = scan_result.get("event_counts", {})
    if not counts:
        return "(no events detected)"
    lines = [f"  - `{eid}`: {cnt}" for eid, cnt in sorted(counts.items())]
    return "\n".join(lines)
