"""OpenNeuro DS002722 stage-1 kernel for EEGUnity.

BCMI-MIdAS calibration recordings contain EDF EEG plus physiological and
continuous user-report channels while participants listened to affective music
clips. The EDF files do not carry usable annotations, so trial annotations are
loaded from the sibling BIDS ``*_events.tsv`` files.

Dataset evidence used by this kernel:
- participants.tsv: subject-level age and sex.
- per-file *_channels.tsv: 32 EEG channels plus GSR, ECG, VA1, VA2, VAtarg.
- per-file *_events.tsv/json: raw trial_type event IDs 1-9 and 101-209.
- per-file *_eeg.json: 1000 Hz sampling rate and channel-count metadata.
"""

from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import mne
import pandas as pd


_INFO_FIELDS = ("age", "sex")
_MISSING_VALUES = {"", "n/a", "na", "nan", "none"}


def _row_get(row, *keys: str) -> str:
    for key in keys:
        try:
            value = row.get(key)
        except AttributeError:
            try:
                value = row[key]
            except Exception:
                value = None
        if value not in (None, ""):
            return str(value)
    return ""


def _get_file_path(row) -> str:
    return _row_get(row, "File Path", "file_path", "filepath", "path")


def _find_dataset_root(file_path: str) -> Optional[Path]:
    current = Path(file_path).resolve().parent
    while True:
        if (current / "dataset_description.json").is_file():
            return current
        if current.parent == current:
            return None
        current = current.parent


def _extract_subject_id(file_path: str) -> str:
    match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
    return match.group(1) if match else "unknown"


def _find_sibling_sidecar(file_path: str, suffix: str) -> Optional[Path]:
    path = Path(file_path)
    stem = path.stem
    candidates: List[Path] = []
    if stem.endswith("_eeg"):
        candidates.append(path.with_name(stem[:-4] + suffix))
    candidates.append(path.with_name(stem + suffix))

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _find_participants_tsv(file_path: str) -> Optional[Path]:
    root = _find_dataset_root(file_path)
    if not root:
        return None
    path = root / "participants.tsv"
    return path if path.is_file() else None


def _clean_value(value) -> str:
    value_str = str(value).strip()
    if value_str.lower() in _MISSING_VALUES:
        return "unknown"
    return value_str


def _normalize_sex(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"f", "female"}:
        return "female"
    if normalized in {"m", "male"}:
        return "male"
    return "unknown"


def _read_participants_info(file_path: str, subject_id: str) -> Dict[str, str]:
    info = {field: "unknown" for field in _INFO_FIELDS}
    participants_path = _find_participants_tsv(file_path)
    if not participants_path:
        return info

    try:
        df = pd.read_csv(participants_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return info

    if "participant_id" not in df.columns:
        return info

    subject_rows = df[df["participant_id"].astype(str) == subject_id]
    if subject_rows.empty:
        return info

    row = subject_rows.iloc[0]
    for field in _INFO_FIELDS:
        if field in row.index:
            info[field] = _clean_value(row[field])
    info["sex"] = _normalize_sex(info.get("sex", "unknown"))
    return info


def _read_json(path: Optional[Path]) -> Dict[str, object]:
    if not path:
        return {}
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _set_channel_types_from_sidecar(raw: mne.io.BaseRaw, file_path: str) -> None:
    channels_path = _find_sibling_sidecar(file_path, "_channels.tsv")
    if not channels_path:
        return

    try:
        channels_df = pd.read_csv(channels_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return

    if "name" not in channels_df.columns or "type" not in channels_df.columns:
        return

    raw_names = set(raw.ch_names)
    channel_types: Dict[str, str] = {}
    for _, channel in channels_df.iterrows():
        name = str(channel.get("name", "")).strip()
        source_type = str(channel.get("type", "")).strip().upper()
        if name not in raw_names:
            continue
        if source_type == "EEG":
            channel_types[name] = "eeg"
        elif source_type == "ECG":
            channel_types[name] = "ecg"
        elif source_type in {"GSR", "USERREPORT", "METADATA", "MISC"}:
            channel_types[name] = "misc"

    if channel_types:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r"The unit for channel\(s\).*")
            raw.set_channel_types(channel_types)


def _set_montage(raw: mne.io.BaseRaw) -> None:
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    events_path = _find_sibling_sidecar(file_path, "_events.tsv")
    if not events_path:
        return None
    try:
        return pd.read_csv(events_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return None


def _is_missing(value) -> bool:
    return str(value).strip().lower() in _MISSING_VALUES


def _event_id_to_string(value) -> str:
    value_str = str(value).strip()
    try:
        value_float = float(value_str)
    except ValueError:
        return value_str
    if value_float.is_integer():
        return str(int(value_float))
    return value_str


def _events_to_annotations(events_df: Optional[pd.DataFrame]) -> mne.Annotations:
    if events_df is None or events_df.empty or "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])

    onsets: List[float] = []
    durations: List[float] = []
    descriptions: List[str] = []

    for _, row in events_df.iterrows():
        onset_value = row.get("onset")
        if _is_missing(onset_value):
            continue
        try:
            onset = float(str(onset_value).strip())
        except ValueError:
            continue

        duration_value = row.get("duration", 0)
        try:
            duration = 0.0 if _is_missing(duration_value) else float(str(duration_value).strip())
        except ValueError:
            duration = 0.0

        description = ""
        for column in ("trial_type", "value", "stim_type"):
            if column in events_df.columns and not _is_missing(row.get(column)):
                description = _event_id_to_string(row.get(column))
                break
        if not description:
            continue

        onsets.append(onset)
        durations.append(duration)
        descriptions.append(description)

    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS002722Kernel:
    """Stage-1 kernel for OpenNeuro ds002722."""

    KERNEL_ID = "openneuro_ds002722"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)
        subject_id = _extract_subject_id(file_path) if file_path else "unknown"
        subject_info = _read_participants_info(file_path, subject_id) if file_path else {
            "age": "unknown",
            "sex": "unknown",
        }

        if file_path:
            # Channel names and non-EEG roles are directly listed in each
            # *_channels.tsv file; no speculative channel rename is performed.
            _set_channel_types_from_sidecar(raw, file_path)
            _set_montage(raw)

            annotations = _events_to_annotations(_read_events_tsv(file_path))
            if len(annotations) > 0:
                raw.set_annotations(annotations)

        eeg_json = _read_json(_find_sibling_sidecar(file_path, "_eeg.json")) if file_path else {}
        original_description = raw.info.get("description", "") or ""
        eegunity_description = {
            "dataset": "openneuro_ds002722",
            "subject_id": subject_id,
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "handedness": "unknown",
            "device": "unknown",
            "amplifier": "unknown",
            "cap": f"{eeg_json.get('EEGChannelCount', 32)}-channel EEG cap",
            "eeg_reference": str(eeg_json.get("EEGReference", "unknown")),
            "task": str(eeg_json.get("TaskName", "Run")),
        }

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = OpenNeuroDS002722Kernel()
