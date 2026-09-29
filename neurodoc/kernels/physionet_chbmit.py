"""Physionet CHB-MIT stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import mne


_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "chb01": {"Gender": "Female", "Age": 11},
    "chb02": {"Gender": "Male", "Age": 11},
    "chb03": {"Gender": "Female", "Age": 14},
    "chb04": {"Gender": "Male", "Age": 22},
    "chb05": {"Gender": "Female", "Age": 7},
    "chb06": {"Gender": "Female", "Age": 1.5},
    "chb07": {"Gender": "Female", "Age": 14.5},
    "chb08": {"Gender": "Male", "Age": 3.5},
    "chb09": {"Gender": "Female", "Age": 10},
    "chb10": {"Gender": "Male", "Age": 3},
    "chb11": {"Gender": "Female", "Age": 12},
    "chb12": {"Gender": "Female", "Age": 2},
    "chb13": {"Gender": "Female", "Age": 3},
    "chb14": {"Gender": "Female", "Age": 9},
    "chb15": {"Gender": "Male", "Age": 16},
    "chb16": {"Gender": "Female", "Age": 7},
    "chb17a": {"Gender": "Female", "Age": 12},
    "chb17b": {"Gender": "Female", "Age": 12},
    "chb17c": {"Gender": "Female", "Age": 12},
    "chb18": {"Gender": "Female", "Age": 18},
    "chb19": {"Gender": "Female", "Age": 19},
    "chb20": {"Gender": "Female", "Age": 6},
    "chb21": {"Gender": "Female", "Age": 13},
    "chb22": {"Gender": "Female", "Age": 9},
    "chb23": {"Gender": "Female", "Age": 6},
    "chb24": {"Gender": "Unknown", "Age": "Unknown"},
}

_MIN_SEGMENT_SEC = 2.0
_PREICTAL_30MIN_SEC = 30 * 60.0
_PREICTAL_20MIN_SEC = 20 * 60.0
_INTERICTAL_GUARD_SEC = 4 * 60 * 60.0


def _merge_intervals(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    cleaned = sorted((float(s), float(e)) for s, e in intervals if e > s)
    merged: List[Tuple[float, float]] = []
    for start, end in cleaned:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _complement_intervals(
    intervals: List[Tuple[float, float]],
    start: float,
    end: float,
    *,
    min_duration: float = 0.0,
) -> List[Tuple[float, float]]:
    merged = _merge_intervals(intervals)
    result: List[Tuple[float, float]] = []
    cursor = float(start)
    for seg_start, seg_end in merged:
        seg_start = max(float(start), seg_start)
        seg_end = min(float(end), seg_end)
        if seg_end <= seg_start:
            continue
        if seg_start - cursor >= min_duration:
            result.append((cursor, seg_start))
        cursor = max(cursor, seg_end)
    if float(end) - cursor >= min_duration:
        result.append((cursor, float(end)))
    return result


def _subtract_intervals(
    base_intervals: List[Tuple[float, float]],
    subtract_intervals: List[Tuple[float, float]],
    *,
    min_duration: float = 0.0,
) -> List[Tuple[float, float]]:
    if not base_intervals:
        return []
    subtract_merged = _merge_intervals(subtract_intervals)
    out: List[Tuple[float, float]] = []
    for base_start, base_end in _merge_intervals(base_intervals):
        cursor = base_start
        for sub_start, sub_end in subtract_merged:
            if sub_end <= cursor or sub_start >= base_end:
                continue
            if sub_start - cursor >= min_duration:
                out.append((cursor, min(sub_start, base_end)))
            cursor = max(cursor, sub_end)
            if cursor >= base_end:
                break
        if base_end - cursor >= min_duration:
            out.append((cursor, base_end))
    return out


def _clip_to_file(
    intervals: List[Tuple[float, float]],
    file_start: float,
    file_end: float,
    *,
    min_duration: float = 0.0,
) -> List[Tuple[float, float]]:
    clipped: List[Tuple[float, float]] = []
    for start, end in intervals:
        local_start = max(start, file_start)
        local_end = min(end, file_end)
        if local_end - local_start >= min_duration:
            clipped.append((local_start - file_start, local_end - local_start))
    return clipped


def _sanitize_local_seizures(
    local_seizures: List[Tuple[float, float]],
    recording_duration: float,
) -> List[Tuple[float, float]]:
    """Keep seizure segments inside the actual EDF duration.

    CHB-MIT summary files contain one known anomaly (`chb06_24.edf`) whose
    seizure offset lies completely outside the real EDF length. For this
    dataset-specific kernel, preserve the seizure count by relocating such
    segments to the last valid span of equal duration.
    """
    cleaned: List[Tuple[float, float]] = []
    max_end = max(0.0, float(recording_duration))
    for start, end in local_seizures:
        start_f = float(start)
        end_f = float(end)
        if end_f <= start_f:
            continue
        seg_dur = end_f - start_f
        if start_f >= max_end:
            if seg_dur >= max_end:
                cleaned.append((0.0, max_end))
            else:
                cleaned.append((max(0.0, max_end - seg_dur), max_end))
            continue
        clipped_end = min(end_f, max_end)
        if clipped_end > start_f:
            cleaned.append((start_f, clipped_end))
    return cleaned


def _parse_clock_time(raw: str) -> float:
    match = re.search(r"(\d+):(\d+):(\d+)", raw)
    if not match:
        raise ValueError(f"Could not parse clock time from: {raw!r}")
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    return float(hours * 3600 + minutes * 60 + seconds)


def _parse_summary_file(summary_file: str) -> Dict[str, Dict[str, Any]]:
    records: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(summary_file):
        return records

    with open(summary_file, "r", encoding="utf-8", errors="replace") as f:
        lines = [line.rstrip("\n") for line in f]
    day_sec = 24 * 60 * 60.0
    rolling_offset = 0.0
    prev_end_abs: float | None = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        file_match = re.match(r"^File Name:\s*(.+)$", line)
        if not file_match:
            i += 1
            continue

        file_name = file_match.group(1).strip()
        start_sec = None
        end_sec = None
        local_seizures: List[Tuple[float, float]] = []
        i += 1
        while i < len(lines):
            cur = lines[i].strip()
            if cur.startswith("File Name:"):
                break
            if cur.startswith("File Start Time:"):
                start_sec = _parse_clock_time(cur)
            elif cur.startswith("File End Time:"):
                end_sec = _parse_clock_time(cur)
            elif re.match(r"^Seizure(?: \d+)? Start Time:", cur):
                start = float(cur.split(":")[-1].strip().replace(" seconds", ""))
                if i + 1 < len(lines):
                    nxt = lines[i + 1].strip()
                    if re.match(r"^Seizure(?: \d+)? End Time:", nxt):
                        end = float(nxt.split(":")[-1].strip().replace(" seconds", ""))
                        if end > start:
                            local_seizures.append((start, end))
            i += 1

        if start_sec is not None and end_sec is not None:
            start_abs = float(start_sec) + rolling_offset
            end_abs = float(end_sec) + rolling_offset
            while end_abs <= start_abs:
                end_abs += day_sec
            if prev_end_abs is not None:
                while start_abs < prev_end_abs:
                    rolling_offset += day_sec
                    start_abs += day_sec
                    end_abs += day_sec
            prev_end_abs = end_abs
            records[file_name] = {
                "file_name": file_name,
                "has_absolute_time": True,
                "start_sec": start_abs,
                "end_sec": end_abs,
                "local_seizures": local_seizures,
                "absolute_seizures": [
                    (start_abs + local_start, start_abs + local_end)
                    for local_start, local_end in local_seizures
                ],
            }
        else:
            records[file_name] = {
                "file_name": file_name,
                "has_absolute_time": False,
                "start_sec": None,
                "end_sec": None,
                "local_seizures": local_seizures,
                "absolute_seizures": [],
            }
    return records


def _event_hints() -> Dict[str, Dict[str, str]]:
    return {
        "seizure": {
            "type": "event",
            "meta_level": "raw",
            "meaning": "Seizure interval (onset to offset) parsed from the CHB-MIT summary/seizure annotations.",
        },
        "interictal_complement": {
            "type": "event",
            "meta_level": "super",
            "meaning": "Seizure-free complement of the raw seizure intervals within the current recording.",
        },
        "preictal_30min": {
            "type": "event",
            "meta_level": "super",
            "meaning": "Thirty-minute window preceding seizure onset, clipped to non-seizure time.",
        },
        "interictal_ge_4h": {
            "type": "event",
            "meta_level": "super",
            "meaning": "Seizure-free time at least 4 hours away from any seizure onset or offset.",
        },
        "preictal_20min": {
            "type": "event",
            "meta_level": "super",
            "meaning": "Twenty-minute window preceding seizure onset, clipped to non-seizure time.",
        },
    }


@dataclass
class PhysionetChbmitKernel:
    """Stage1 kernel for the physionet-chbmit dataset."""

    KERNEL_ID: str = "physionet-chbmit-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        file_name = os.path.basename(file_path)
        subject_id = file_name.split("_")[0]
        raw_duration = float(raw.times[-1])

        # Locate the summary file.
        parent_dir = os.path.dirname(file_path)
        summary_file = os.path.join(
            parent_dir, f"{os.path.basename(parent_dir)}-summary.txt"
        )
        summary_records = _parse_summary_file(summary_file)
        current_record = summary_records.get(file_name)

        local_seizures: List[Tuple[float, float]] = []
        file_abs_start = 0.0
        file_abs_end = raw_duration
        subject_abs_seizures: List[Tuple[float, float]] = []
        if current_record is not None:
            local_seizures = list(current_record["local_seizures"])
            local_seizures = _sanitize_local_seizures(
                local_seizures,
                raw_duration,
            )
            if current_record.get("has_absolute_time"):
                file_abs_start = float(current_record["start_sec"])
                file_abs_end = min(float(current_record["end_sec"]), file_abs_start + raw_duration)
                for record_name, record in summary_records.items():
                    if not record.get("has_absolute_time"):
                        continue
                    if record_name == file_name:
                        subject_abs_seizures.extend(
                            [
                                (file_abs_start + local_start, file_abs_start + local_end)
                                for local_start, local_end in local_seizures
                            ]
                        )
                    else:
                        subject_abs_seizures.extend(record["absolute_seizures"])
            else:
                # chb24 lacks per-file absolute clock times in the summary. We
                # still emit raw seizures and within-file derived segments.
                file_abs_start = 0.0
                file_abs_end = raw_duration
        else:
            subject_abs_seizures = list(local_seizures)

        if not subject_abs_seizures and local_seizures:
            subject_abs_seizures = list(local_seizures)

        merged_subject_seizures = _merge_intervals(subject_abs_seizures)
        local_abs_window = (file_abs_start, file_abs_end)

        seizure_annotations = [(start, end - start, "seizure") for start, end in local_seizures if end > start]

        interictal_complement = _clip_to_file(
            _complement_intervals(
                merged_subject_seizures,
                file_abs_start,
                file_abs_end,
                min_duration=_MIN_SEGMENT_SEC,
            ),
            *local_abs_window,
            min_duration=_MIN_SEGMENT_SEC,
        )

        preictal_30_candidates = [
            (max(file_abs_start, onset - _PREICTAL_30MIN_SEC), onset)
            for onset, _ in merged_subject_seizures
            if onset > file_abs_start
        ]
        preictal_20_candidates = [
            (max(file_abs_start, onset - _PREICTAL_20MIN_SEC), onset)
            for onset, _ in merged_subject_seizures
            if onset > file_abs_start
        ]
        preictal_30 = _clip_to_file(
            _subtract_intervals(
                preictal_30_candidates,
                merged_subject_seizures,
                min_duration=_MIN_SEGMENT_SEC,
            ),
            *local_abs_window,
            min_duration=_MIN_SEGMENT_SEC,
        )
        preictal_20 = _clip_to_file(
            _subtract_intervals(
                preictal_20_candidates,
                merged_subject_seizures,
                min_duration=_MIN_SEGMENT_SEC,
            ),
            *local_abs_window,
            min_duration=_MIN_SEGMENT_SEC,
        )

        guarded = [
            (start - _INTERICTAL_GUARD_SEC, end + _INTERICTAL_GUARD_SEC)
            for start, end in merged_subject_seizures
        ]
        interictal_ge_4h = _clip_to_file(
            _complement_intervals(
                guarded,
                file_abs_start,
                file_abs_end,
                min_duration=_MIN_SEGMENT_SEC,
            ),
            *local_abs_window,
            min_duration=_MIN_SEGMENT_SEC,
        )

        annotation_rows: List[Tuple[float, float, str]] = []
        annotation_rows.extend(seizure_annotations)
        annotation_rows.extend((onset, duration, "interictal_complement") for onset, duration in interictal_complement)
        annotation_rows.extend((onset, duration, "preictal_30min") for onset, duration in preictal_30)
        annotation_rows.extend((onset, duration, "interictal_ge_4h") for onset, duration in interictal_ge_4h)
        annotation_rows.extend((onset, duration, "preictal_20min") for onset, duration in preictal_20)
        annotation_rows.sort(key=lambda item: (item[0], item[2]))

        if annotation_rows:
            raw.set_annotations(
                mne.Annotations(
                    onset=[row[0] for row in annotation_rows],
                    duration=[row[1] for row in annotation_rows],
                    description=[row[2] for row in annotation_rows],
                )
            )

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap": "unknown",
                "age": str(_SUBJECT_DICT[subject_id]["Age"]),
                "sex": str(_SUBJECT_DICT[subject_id]["Gender"]),
                "handedness": "unknown",
            },
            "eegunity_scan_hints": {
                "events": _event_hints(),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = PhysionetChbmitKernel()
