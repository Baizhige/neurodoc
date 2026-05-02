"""Run a full EEGUnity scan for one dataset and rewrite analysis.md.

This script is a kernel-validation utility. It does not use LLMs, BIDS sidecars,
or task-derived backfilling. It only trusts artifacts that come back from the
kernelized EEGUnity scan, i.e. event counts, misc channels, and description
payloads stored on the resulting MNE Raw objects.

Usage:
    python -m neurodoc.full_scan --dataset openneuro_ds005505
    python neurodoc/full_scan.py --dataset openneuro_ds005505
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

AGENT_DIR = Path(__file__).resolve().parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

try:
    from .paths import DATASET_DOCUMENT_DIR, LOGS_DIR, MACHINE_CONFIG_DIR
    from .pipeline.doc_writer import (
        _build_kr_block,
        _detect_super_meta,
        _enforce_kr_block,
        _enforce_manual_review_blank,
    )
    from .pipeline.file_scan_result_builder import build_file_scan_result_block
    from .pipeline.scan_bridge import run_scan
    from . import scan_engine
except ImportError:
    from paths import DATASET_DOCUMENT_DIR, LOGS_DIR, MACHINE_CONFIG_DIR
    from pipeline.doc_writer import (
        _build_kr_block,
        _detect_super_meta,
        _enforce_kr_block,
        _enforce_manual_review_blank,
    )
    from pipeline.file_scan_result_builder import build_file_scan_result_block
    from pipeline.scan_bridge import run_scan
    import scan_engine


_SECTION_RE_TEMPLATE = r"^##\s+{name}\s*$"


def _find_config(explicit: str | None) -> Dict[str, Any]:
    if explicit:
        return json.loads(Path(explicit).read_text(encoding="utf-8"))
    candidates = sorted(MACHINE_CONFIG_DIR.glob("*.json"))
    if not candidates:
        raise FileNotFoundError(
            "No machine_config JSON found in Script/neurodoc_runtime/machine_config/."
        )
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


def _extract_section(text: str, section_name: str) -> str:
    start_m = re.search(
        _SECTION_RE_TEMPLATE.format(name=re.escape(section_name)),
        text,
        re.MULTILINE,
    )
    if not start_m:
        return ""
    rest = text[start_m.start():]
    end_m = re.search(r"^##\s+\S", rest[3:], re.MULTILINE)
    return rest[: end_m.start() + 3] if end_m else rest


def _replace_section(text: str, section_name: str, new_block: str) -> str:
    start_m = re.search(
        _SECTION_RE_TEMPLATE.format(name=re.escape(section_name)),
        text,
        re.MULTILINE,
    )
    if not start_m:
        return text.rstrip() + "\n\n" + new_block.rstrip() + "\n"
    rest = text[start_m.start():]
    end_m = re.search(r"^##\s+\S", rest[3:], re.MULTILINE)
    end = start_m.start() + (end_m.start() + 3 if end_m else len(rest))
    return text[: start_m.start()] + new_block.rstrip() + "\n\n" + text[end:].lstrip("\n")


def _rewrite_kernel_responsibilities(analysis_text: str) -> str:
    tasks_section = _extract_section(analysis_text, "Tasks")
    super_meta_required = _detect_super_meta(tasks_section)
    current_status = scan_engine.read_analysis_status(analysis_text) or "wait_manual_review"
    kr_block = _build_kr_block(super_meta_required, current_status)
    return _enforce_kr_block(analysis_text, kr_block)


def _write_log(log_path: Path, lines: List[str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a full scan with the current kernel and refresh analysis.md."
    )
    parser.add_argument("--dataset", "-d", required=True, help="Dataset ID, e.g. openneuro_ds005505")
    parser.add_argument("--config", default=None, help="Optional machine_config JSON path")
    parser.add_argument("--workers", type=int, default=None, help="Override EEGUnity worker count")
    args = parser.parse_args()

    dataset_name = args.dataset.strip()
    if not dataset_name:
        raise SystemExit("ERROR: --dataset cannot be empty.")

    cfg = _find_config(args.config)
    dataset_roots = cfg.get("dataset_roots", [])
    eegunity_path = cfg.get("eegunity_path", "")
    num_workers = args.workers if args.workers is not None else int(cfg.get("num_workers", 1) or 1)

    kernel_path = scan_engine.detect_kernel_path(dataset_name)
    if not kernel_path:
        raise SystemExit(f"ERROR: No kernel found for {dataset_name}.")

    dataset_path = scan_engine.find_dataset_path(dataset_name, dataset_roots)
    if not dataset_path:
        searched = ", ".join(dataset_roots) or "(none configured)"
        raise SystemExit(f"ERROR: Dataset {dataset_name} not found in configured roots: {searched}")

    analysis_path = DATASET_DOCUMENT_DIR / dataset_name / "analysis.md"
    if not analysis_path.exists():
        raise SystemExit(f"ERROR: analysis.md not found: {analysis_path}")

    existing_analysis = analysis_path.read_text(encoding="utf-8", errors="replace")
    log_lines: List[str] = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"{dataset_name}.full_scan.{timestamp}.log"

    def log(msg: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {msg}"
        print(line)
        log_lines.append(line)

    log(f"[full_scan] Dataset: {dataset_name}")
    log(f"[full_scan] Kernel: {kernel_path}")
    log(f"[full_scan] Raw data dir: {dataset_path}")

    scan_result = run_scan(
        dataset_name=dataset_name,
        kernel_path=kernel_path,
        dataset_roots=dataset_roots,
        eegunity_path=eegunity_path,
        num_workers=num_workers,
        log=log,
    )

    file_scan_block, summary = build_file_scan_result_block(scan_result)
    log(f"[full_scan] Kernel-derived event hints: {summary['event_hints']}")
    log(f"[full_scan] Kernel-derived misc hints: {summary['misc_hints']}")
    log(f"[full_scan] Detected misc channels: {summary['misc_channels']}")
    log(f"[full_scan] Description info fields: {summary['info_fields']}")

    updated = _replace_section(existing_analysis, "File Scan Result", file_scan_block)
    updated = _rewrite_kernel_responsibilities(updated)
    updated = _enforce_manual_review_blank(updated)
    analysis_path.write_text(updated, encoding="utf-8")
    log(f"[full_scan] analysis.md updated: {analysis_path}")

    _write_log(log_path, log_lines)
    log(f"[full_scan] Log written: {log_path}")


if __name__ == "__main__":
    main()
