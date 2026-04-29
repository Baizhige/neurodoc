#!/usr/bin/env python3
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
import ast
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

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


def _parse_json_like(value: Any) -> Dict[str, Any]:
    text = str(value or "").strip()
    if not text or text.lower() in ("nan", "none", "null"):
        return {}
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def _normalize_hint_dict(value: Any) -> Dict[str, Dict[str, str]]:
    parsed = _parse_json_like(value) if isinstance(value, str) else value
    if not isinstance(parsed, dict):
        return {}
    out: Dict[str, Dict[str, str]] = {}
    for key, meta in parsed.items():
        if not isinstance(meta, dict):
            continue
        out[str(key)] = {
            str(k): str(v).strip()
            for k, v in meta.items()
            if str(v).strip()
        }
    return out


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return text.lower() not in ("", "nan", "none", "null", "n/a", "na", "unknown")


def _compute_completeness(ok: int, total: int) -> str:
    if total <= 0:
        return "missing"
    pct = ok / total
    if pct >= 0.99:
        return "complete"
    if pct > 0:
        return f"partial ({ok}/{total})"
    return "missing"


def _parse_existing_event_rows(analysis_text: str) -> Dict[str, Dict[str, str]]:
    fsr = _extract_section(analysis_text, "File Scan Result")
    if not fsr:
        return {}
    es_m = re.search(r"(### Event Structure\s*\n)(.*?)(?=\n###|\n## |\Z)", fsr, re.DOTALL)
    if not es_m:
        return {}
    return scan_engine._parse_event_table(es_m.group(2))  # type: ignore[attr-defined]


def _parse_existing_misc_rows(analysis_text: str) -> Dict[str, Dict[str, str]]:
    fsr = _extract_section(analysis_text, "File Scan Result")
    if not fsr:
        return {}
    misc_m = re.search(
        r"### MISC Label Summary\s*\n\|.*?\n\|[-| ]+\n(.*?)(?=\n###|\n## |\Z)",
        fsr,
        re.DOTALL,
    )
    if not misc_m:
        return {}
    rows: Dict[str, Dict[str, str]] = {}
    for line in misc_m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 4:
            continue
        channel = parts[0].strip("`").strip()
        if not channel or channel.lower() in ("channel", "---"):
            continue
        rows[channel] = {
            "source": parts[1],
            "meta": parts[2],
            "notes": parts[3],
        }
    return rows


def _parse_existing_info_order(analysis_text: str) -> List[str]:
    fsr = _extract_section(analysis_text, "File Scan Result")
    if not fsr:
        return []
    info_m = re.search(
        r"### Info\s*\n\|.*?\n\|[-| ]+\n(.*?)(?=\n###|\n## |\Z)",
        fsr,
        re.DOTALL,
    )
    if not info_m:
        return []
    fields: List[str] = []
    for line in info_m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 3:
            continue
        field = parts[0].strip("`").strip()
        if field and field.lower() not in ("field", "---"):
            fields.append(field)
    return fields


def _collect_scan_semantics(
    df: pd.DataFrame,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    info_stats: Dict[str, Dict[str, Any]] = {}
    event_hints: Dict[str, Dict[str, str]] = {}
    misc_hints: Dict[str, Dict[str, str]] = {}

    for desc_str in df.get("description", []):
        desc = _parse_json_like(desc_str)
        eegu = desc.get("eegunity_description", {})
        if isinstance(eegu, str):
            eegu = _parse_json_like(eegu)
        if isinstance(eegu, dict):
            for key, raw_value in eegu.items():
                field = str(key).strip()
                if not field:
                    continue
                stat = info_stats.setdefault(field, {"count": 0, "samples": []})
                if _is_present(raw_value):
                    stat["count"] += 1
                    sample = str(raw_value).strip()
                    if sample not in stat["samples"] and len(stat["samples"]) < 3:
                        stat["samples"].append(sample)

        hints = desc.get("eegunity_scan_hints", {})
        if isinstance(hints, str):
            hints = _parse_json_like(hints)
        if not isinstance(hints, dict):
            continue

        for event_id, meta in _normalize_hint_dict(hints.get("events", {})).items():
            event_hints.setdefault(event_id, meta)
        for channel, meta in _normalize_hint_dict(hints.get("misc_channels", {})).items():
            misc_hints.setdefault(channel, meta)

    return info_stats, event_hints, misc_hints


def _build_file_scan_result_block(
    analysis_text: str,
    scan_result: Dict[str, Any],
) -> Tuple[str, Dict[str, Any]]:
    df: pd.DataFrame = scan_result["df"]
    total_n = int(scan_result.get("total_n", len(df)) or len(df))
    event_counts = scan_result.get("event_counts", {})
    misc_channels = sorted(scan_result.get("misc_channel_names", []) or [])

    existing_event_rows = _parse_existing_event_rows(analysis_text)
    existing_misc_rows = _parse_existing_misc_rows(analysis_text)
    existing_info_order = _parse_existing_info_order(analysis_text)
    info_stats, kernel_event_hints, kernel_misc_hints = _collect_scan_semantics(df)

    event_rows: List[str] = []
    for event_id, count in sorted(event_counts.items(), key=lambda item: str(item[0])):
        key = str(event_id)
        existing = existing_event_rows.get(key, {})
        hint = kernel_event_hints.get(key, {})
        event_type = existing.get("type", "").strip() or hint.get("type", "event")
        meta_level = existing.get("meta_level", "").strip() or hint.get("meta_level", "raw")
        meaning = existing.get("meaning", "").strip() or hint.get("meaning", "")
        event_rows.append(
            f"| `{key}` | {count} | {event_type} | {meta_level} | {meaning} |"
        )

    misc_rows: List[str] = []
    for channel in misc_channels:
        existing = existing_misc_rows.get(channel, {})
        hint = kernel_misc_hints.get(channel, {})
        source = hint.get("source") or existing.get("source") or "native (raw misc in EEG file)"
        meta = hint.get("meta_level") or existing.get("meta") or "raw"
        notes = hint.get("notes") or existing.get("notes") or "Verify channel role and unit"
        misc_rows.append(f"| `{channel}` | {source} | {meta} | {notes} |")

    age_count = int(info_stats.get("age", {}).get("count", 0))
    sex_count = int(info_stats.get("sex", {}).get("count", 0))
    device_count = 0
    for key in ("device", "amplifier", "cap"):
        device_count = max(device_count, int(info_stats.get(key, {}).get("count", 0)))

    info_rows = [
        f"| `subject_age` | {_compute_completeness(age_count, total_n)} | N/A |",
        f"| `subject_sex` | {_compute_completeness(sex_count, total_n)} | N/A |",
        f"| `device` | {_compute_completeness(device_count, total_n)} | N/A |",
    ]

    canonical_aliases = {"age", "sex", "gender", "device"}
    ordered_extra_fields: List[str] = []
    for field in existing_info_order:
        if field in ("subject_age", "subject_sex", "device"):
            continue
        if (
            field in info_stats
            and int(info_stats[field].get("count", 0)) > 0
            and field not in ordered_extra_fields
        ):
            ordered_extra_fields.append(field)
    for field in sorted(info_stats):
        if (
            field in canonical_aliases
            or field in ordered_extra_fields
            or int(info_stats[field].get("count", 0)) <= 0
        ):
            continue
        ordered_extra_fields.append(field)

    for field in ordered_extra_fields:
        stat = info_stats[field]
        completeness = _compute_completeness(int(stat.get("count", 0)), total_n)
        samples = stat.get("samples", [])
        notes = f"e.g. {', '.join(samples)}" if samples else "N/A"
        info_rows.append(f"| `{field}` | {completeness} | {notes} |")

    parts = [
        "## File Scan Result\n",
        f"> **Kernel SHA256**: `{scan_result.get('kernel_sha256', 'N/A')}`",
        f"> **EEGUnity Version**: `{scan_result.get('eegunity_version', 'N/A')}`",
        "> **Scan Type**: Full\n",
        "### Event Structure\n",
        "| Event ID | Count (total) | Type | Meta Level | Meaning |",
        "|---|---|---|---|---|",
        *event_rows,
    ]

    if misc_rows:
        parts += [
            "",
            "### MISC Label Summary\n",
            "| Channel | Source | Meta | Notes |",
            "|---|---|---|---|",
            *misc_rows,
        ]

    parts += [
        "",
        "### Info\n",
        "| Field | Completeness | Notes |",
        "|---|---|---|",
        *info_rows,
    ]

    summary = {
        "event_hints": sorted(kernel_event_hints),
        "misc_hints": sorted(kernel_misc_hints),
        "info_fields": sorted(
            field for field, stat in info_stats.items() if int(stat.get("count", 0)) > 0
        ),
        "misc_channels": misc_channels,
    }
    return "\n".join(parts), summary


def _rewrite_kernel_responsibilities(analysis_text: str) -> str:
    tasks_section = _extract_section(analysis_text, "Tasks")
    super_meta_required = _detect_super_meta(tasks_section)
    current_status = scan_engine.read_analysis_status(analysis_text)
    if current_status == "wait_kernel_update" or not current_status:
        status = "wait_manual_review"
    else:
        status = current_status
    kr_block = _build_kr_block(super_meta_required, status)
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

    file_scan_block, summary = _build_file_scan_result_block(existing_analysis, scan_result)
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
