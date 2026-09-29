"""Build raw-truth File Scan Result blocks from kernel scan outputs."""
from __future__ import annotations

import ast
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


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


def _sample_note(samples: Iterable[str]) -> str:
    cleaned = [str(sample).strip() for sample in samples if str(sample).strip()]
    if not cleaned:
        return ""
    return f"e.g. {', '.join(cleaned[:3])}"


def collect_scan_semantics(
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
                stat = info_stats.setdefault(field, {"count": 0, "samples": [], "seen": 0})
                stat["seen"] += 1
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


def _event_annotation_map(event_annotations: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    ann_map: Dict[str, Dict[str, Any]] = {}
    if not event_annotations:
        return ann_map
    for ann in event_annotations.get("annotations", []):
        key = str(ann.get("event_id", "")).strip()
        if key:
            ann_map[key] = ann
    return ann_map


def _normalize_text_map(value: Optional[Dict[str, str]]) -> Dict[str, str]:
    if not value:
        return {}
    return {
        str(k).strip(): str(v).strip()
        for k, v in value.items()
        if str(k).strip()
    }


def build_file_scan_result_block(
    scan_result: Dict[str, Any],
    *,
    event_annotations: Optional[Dict[str, Any]] = None,
    misc_note_map: Optional[Dict[str, str]] = None,
    info_note_map: Optional[Dict[str, str]] = None,
) -> Tuple[str, Dict[str, Any]]:
    df: pd.DataFrame = scan_result["df"]
    total_n = int(scan_result.get("total_n", len(df)) or len(df))
    event_counts = scan_result.get("event_counts", {})
    misc_channels = sorted(scan_result.get("misc_channel_names", []) or [])

    info_stats, kernel_event_hints, kernel_misc_hints = collect_scan_semantics(df)
    ann_map = _event_annotation_map(event_annotations)
    misc_note_map = _normalize_text_map(misc_note_map)
    info_note_map = _normalize_text_map(info_note_map)

    event_rows: List[str] = []
    for event_id, count in sorted(event_counts.items(), key=lambda item: str(item[0])):
        key = str(event_id)
        hint = kernel_event_hints.get(key, {})
        ann = ann_map.get(key, {})
        event_type = str(hint.get("type") or "").strip() or str(ann.get("event_type") or "").strip() or "event"
        meta_level = str(hint.get("meta_level") or "").strip() or "raw"
        meaning = str(hint.get("meaning") or "").strip() or str(ann.get("meaning") or "").strip()
        event_rows.append(
            f"| `{key}` | {count} | {event_type} | {meta_level} | {meaning} |"
        )

    misc_rows: List[str] = []
    for channel in misc_channels:
        hint = kernel_misc_hints.get(channel, {})
        source = str(hint.get("source") or "").strip() or "native (raw misc in EEG file)"
        meta = str(hint.get("meta_level") or "").strip() or "raw"
        notes = str(hint.get("notes") or "").strip() or misc_note_map.get(channel, "")
        misc_rows.append(f"| `{channel}` | {source} | {meta} | {notes} |")

    info_rows: List[str] = []
    for field in sorted(info_stats):
        stat = info_stats[field]
        completeness = _compute_completeness(int(stat.get("count", 0)), total_n)
        notes = info_note_map.get(field, "") or _sample_note(stat.get("samples", []))
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
        "info_fields": sorted(info_stats),
        "misc_channels": misc_channels,
    }
    return "\n".join(parts), summary
