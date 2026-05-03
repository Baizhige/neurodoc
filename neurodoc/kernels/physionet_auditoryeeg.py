"""PhysioNet Auditory EEG stage1 kernel for EEGUnity.

The dataset stores condition labels in record names of the form
``sXX_exXX[_sXX]``. This kernel restores those filename-level labels as
recording-length MNE annotations and writes subject/device metadata into
``raw.info["description"]``.
"""

import csv
import json
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

import mne
import numpy as np


_SFREQ = 200.0
_CHANNEL_NAMES = ["P4", "Cz", "F8", "T7"]
_RECORD_RE = re.compile(r"(?P<subject>s\d{2})_ex(?P<experiment>\d{2})(?:_s(?P<session>\d{2}))?", re.I)

# Source: dataset_document/physionet_auditoryeeg/analysis.md Event Structure,
#         local README.txt "Testing and data recording" experiment order.
# Annotator: Codex, 2026-05-03 - needs human review
_EXPERIMENT_EVENT_MAP: Dict[str, str] = {
    "01": "resting_eyes_open",
    "02": "resting_eyes_closed",
    "05": "auditory_native_song_in_ear",
    "06": "auditory_nonnative_song_in_ear",
    "07": "auditory_neutral_music_in_ear",
    "08": "auditory_native_song_bone",
    "09": "auditory_nonnative_song_bone",
    "10": "auditory_neutral_music_bone",
}

# Source: PhysioNet Auditory evoked potential EEG-Biometric dataset page and
#         local README.txt; meanings mirror the existing analysis.md table.
# Annotator: Codex, 2026-05-03 - needs human review
_RAW_META: Dict[str, str] = {
    "resting_eyes_open": "Resting state with eyes open (ex01)",
    "resting_eyes_closed": "Resting state with eyes closed (ex02)",
    "auditory_native_song_in_ear": "Native-language song via in-ear headphones (ex05)",
    "auditory_nonnative_song_in_ear": "Non-native language song via in-ear headphones (ex06)",
    "auditory_neutral_music_in_ear": "Neutral instrumental music via in-ear headphones (ex07)",
    "auditory_native_song_bone": "Native song via bone-conduction headphones (ex08)",
    "auditory_nonnative_song_bone": "Non-native song via bone-conduction headphones (ex09)",
    "auditory_neutral_music_bone": "Neutral instrumental music via bone-conduction headphones (ex10)",
}

_EVENT_HINTS: Dict[str, Dict[str, str]] = {
    event_id: {
        "type": "event",
        "meta_level": "raw",
        "meaning": meaning,
    }
    for event_id, meaning in _RAW_META.items()
}

# Source: PhysioNet dataset page / README.txt:
# OpenBCI Ganglion Board, 200 Hz, four gold-cup electrodes at P4, Cz, F8, T7.
# Annotator: Codex, 2026-05-03 - needs human review
_DEVICE_DESCRIPTION = (
    "OpenBCI Ganglion Board, a 4-channel EEG acquisition system sampling at "
    "200 Hz, with gold-cup electrodes at T7, F8, Cz, and P4 using Ten20 "
    "conductive paste and OpenBCI GUI v5.0.3."
)
_AMPLIFIER = "OpenBCI Ganglion Board"
_CAP = "gold-cup electrodes with Ten20 conductive paste"


def _get_file_path(row: Any) -> str:
    for key in ("File Path", "file_path", "path"):
        try:
            value = row[key]
        except Exception:
            continue
        if value:
            return str(value)
    return ""


def _parse_record(file_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    stem = os.path.splitext(os.path.basename(file_path))[0]
    match = _RECORD_RE.search(stem)
    if not match:
        return None, None, None
    return (
        match.group("subject").lower(),
        match.group("experiment"),
        match.group("session"),
    )


def _find_dataset_root(file_path: str) -> Optional[str]:
    current = os.path.abspath(os.path.dirname(file_path))
    for _ in range(8):
        if os.path.exists(os.path.join(current, "Subjects.csv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


@lru_cache(maxsize=8)
def _load_subjects(subjects_csv: str) -> Dict[str, Dict[str, str]]:
    subjects: Dict[str, Dict[str, str]] = {}
    if not subjects_csv or not os.path.exists(subjects_csv):
        return subjects

    with open(subjects_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {str(k).strip(): str(v).strip() for k, v in row.items() if k is not None}
            subject_id = cleaned.get("Subject ID", "").upper()
            if subject_id:
                subjects[subject_id] = cleaned
    return subjects


def _normalize_sex(value: str) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("m"):
        return "male"
    if text.startswith("f"):
        return "female"
    return "unknown"


def _subject_description_fields(file_path: str) -> Dict[str, str]:
    subject, _, _ = _parse_record(file_path)
    if not subject:
        return {"age": "unknown", "sex": "unknown"}

    dataset_root = _find_dataset_root(file_path)
    if not dataset_root:
        return {"age": "unknown", "sex": "unknown"}

    subjects = _load_subjects(os.path.join(dataset_root, "Subjects.csv"))
    subject_row = subjects.get(subject.upper(), {})
    age = subject_row.get("Age", "").strip()
    return {
        "age": age if age else "unknown",
        "sex": _normalize_sex(subject_row.get("Gender", "")),
    }


def _record_duration(raw: mne.io.BaseRaw) -> float:
    sfreq = float(raw.info.get("sfreq") or 0.0)
    if sfreq > 0 and getattr(raw, "n_times", 0):
        return float(raw.n_times) / sfreq
    if len(raw.times):
        return float(raw.times[-1])
    return 0.0


def _read_text_record(file_path: str) -> Optional[mne.io.BaseRaw]:
    suffix = os.path.splitext(file_path)[1].lower()
    if suffix not in {".csv", ".txt"}:
        return None

    _, experiment, _ = _parse_record(file_path)
    if experiment is None:
        return None

    try:
        data = np.genfromtxt(
            file_path,
            delimiter=",",
            skip_header=1,
            usecols=(1, 2, 3, 4),
            dtype=float,
            autostrip=True,
        )
    except Exception:
        return None

    if data.size == 0:
        return None
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.shape[1] != len(_CHANNEL_NAMES):
        return None

    info = mne.create_info(_CHANNEL_NAMES, sfreq=_SFREQ, ch_types=["eeg"] * len(_CHANNEL_NAMES))
    return mne.io.RawArray(data.T * 1e-6, info, verbose=False)


def _standardize_channels(raw: mne.io.BaseRaw) -> None:
    existing = set(raw.ch_names)
    if not all(ch in existing for ch in _CHANNEL_NAMES):
        eeg_picks = mne.pick_types(raw.info, eeg=True, misc=False, stim=False, eog=False, ecg=False, emg=False)
        if len(eeg_picks) >= len(_CHANNEL_NAMES):
            rename = {}
            for pick, standard_name in zip(eeg_picks[: len(_CHANNEL_NAMES)], _CHANNEL_NAMES):
                current = raw.ch_names[pick]
                if current != standard_name and standard_name not in existing:
                    rename[current] = standard_name
            if rename:
                raw.rename_channels(rename)

    channel_types = {ch: "eeg" for ch in _CHANNEL_NAMES if ch in raw.ch_names}
    if channel_types:
        raw.set_channel_types(channel_types)

    try:
        raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
    except Exception:
        pass


def _set_description(raw: mne.io.BaseRaw, file_path: str) -> None:
    subject_fields = _subject_description_fields(file_path)
    eegunity_description = {
        "age": subject_fields["age"],
        "sex": subject_fields["sex"],
        "amplifier": _AMPLIFIER,
        "cap": _CAP,
        "handedness": "unknown",
        "device": _DEVICE_DESCRIPTION,
    }

    raw.info["description"] = json.dumps(
        {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": eegunity_description,
            "eegunity_scan_hints": {
                "events": _EVENT_HINTS,
            },
        },
        ensure_ascii=True,
    )


@dataclass
class PhysionetAuditoryEegKernel:
    """Stage1 kernel for the PhysioNet auditory-eeg dataset."""

    KERNEL_ID: str = "physionet-auditoryeeg-stage1"
    HANDLES_UNAVAILABLE: bool = True
    required_info_fields: list[str] = field(default_factory=lambda: ["age", "sex", "device"])
    raw_meta: Dict[str, str] = field(default_factory=lambda: dict(_RAW_META))
    super_meta: Dict[str, str] = field(default_factory=dict)

    def load(self, *args) -> Optional[mne.io.BaseRaw]:
        row = args[-1]
        file_path = _get_file_path(row)
        if not file_path:
            return None
        return _read_text_record(file_path)

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)
        _, experiment, _ = _parse_record(file_path)

        _standardize_channels(raw)
        _set_description(raw, file_path)

        if not experiment:
            return raw

        event_id = _EXPERIMENT_EVENT_MAP.get(experiment, f"ex{experiment}")
        duration = _record_duration(raw)
        raw.set_annotations(
            mne.Annotations(
                onset=[0.0],
                duration=[duration],
                description=[event_id],
                orig_time=raw.annotations.orig_time,
            )
        )
        return raw


KERNEL = PhysionetAuditoryEegKernel()
