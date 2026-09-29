"""OpenNeuro DS001787 stage-1 kernel for EEGUnity.

EEG meditation study: continuous BioSemi ActiveTwo recordings with probe
interruptions roughly every two minutes.

Dataset evidence used by this kernel:
- participants.tsv: subject-level age, gender, and expert/novice group labels.
- task-meditation_channels.tsv: canonical 64 EEG names plus auxiliary channels.
- task-meditation_events.json / *_events.tsv: original numeric event values.

Source: https://openneuro.org/datasets/ds001787
"""

from __future__ import annotations

import json
import os
import re
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import mne
import pandas as pd


_REQUIRED_INFO_FIELDS = ("age", "gender", "group")

# task-meditation_channels.tsv is the explicit dataset evidence for both the
# BioSemi A/B-slot to 10-20 rename and the auxiliary-channel roles.
_FALLBACK_CHANNEL_SPECS: List[Tuple[str, str]] = [
    ("Fp1", "EEG"), ("AF7", "EEG"), ("AF3", "EEG"), ("F1", "EEG"),
    ("F3", "EEG"), ("F5", "EEG"), ("F7", "EEG"), ("FT7", "EEG"),
    ("FC5", "EEG"), ("FC3", "EEG"), ("FC1", "EEG"), ("C1", "EEG"),
    ("C3", "EEG"), ("C5", "EEG"), ("T7", "EEG"), ("TP7", "EEG"),
    ("CP5", "EEG"), ("CP3", "EEG"), ("CP1", "EEG"), ("P1", "EEG"),
    ("P3", "EEG"), ("P5", "EEG"), ("P7", "EEG"), ("P9", "EEG"),
    ("PO7", "EEG"), ("PO3", "EEG"), ("O1", "EEG"), ("Iz", "EEG"),
    ("Oz", "EEG"), ("POz", "EEG"), ("Pz", "EEG"), ("CPz", "EEG"),
    ("Fpz", "EEG"), ("Fp2", "EEG"), ("AF8", "EEG"), ("AF4", "EEG"),
    ("AFz", "EEG"), ("Fz", "EEG"), ("F2", "EEG"), ("F4", "EEG"),
    ("F6", "EEG"), ("F8", "EEG"), ("FT8", "EEG"), ("FC6", "EEG"),
    ("FC4", "EEG"), ("FC2", "EEG"), ("FCz", "EEG"), ("Cz", "EEG"),
    ("C2", "EEG"), ("C4", "EEG"), ("C6", "EEG"), ("T8", "EEG"),
    ("TP8", "EEG"), ("CP6", "EEG"), ("CP4", "EEG"), ("CP2", "EEG"),
    ("P2", "EEG"), ("P4", "EEG"), ("P6", "EEG"), ("P8", "EEG"),
    ("P10", "EEG"), ("PO8", "EEG"), ("PO4", "EEG"), ("O2", "EEG"),
    ("EXG1", "MISC"), ("EXG2", "MISC"), ("EXG3", "MISC"),
    ("EXG4", "MISC"), ("EXG5", "MISC"), ("EXG6", "MISC"),
    ("EXG7", "MISC"), ("EXG8", "MISC"), ("GSR1", "GSR"),
    ("GSR2", "GSR"), ("Erg1", "MISC"), ("Erg2", "MISC"),
    ("Resp", "RESP"), ("Plet", "PPG"), ("Temp", "TEMP"),
]

_BIOSEMI_BDF_64_NAMES = [f"A{i}" for i in range(1, 33)] + [f"B{i}" for i in range(1, 33)]
_AUX_AS_MISC = {"MISC", "GSR", "RESP", "PPG", "TEMP"}


def _row_get(row, *keys: str) -> str:
    """Return the first present locator value for the requested key names."""
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


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
    return match.group(1) if match else None


def _find_dataset_root(file_path: str) -> Optional[str]:
    current = os.path.dirname(os.path.abspath(file_path))
    previous = None
    while current and current != previous:
        if (
            os.path.isfile(os.path.join(current, "participants.tsv"))
            or os.path.isfile(os.path.join(current, "dataset_description.json"))
        ):
            return current
        previous = current
        current = os.path.dirname(current)
    return None


def _task_name_from_path(file_path: str) -> Optional[str]:
    match = re.search(r"_task-([^_]+)", os.path.basename(file_path))
    return match.group(1) if match else None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    root = _find_dataset_root(file_path)
    if not root:
        return None
    path = os.path.join(root, "participants.tsv")
    return path if os.path.isfile(path) else None


def _find_channels_tsv(file_path: str) -> Optional[str]:
    path = Path(file_path)
    stem = path.stem
    if stem.endswith("_eeg"):
        sibling = path.with_name(stem[:-4] + "_channels.tsv")
        if sibling.is_file():
            return str(sibling)

    root = _find_dataset_root(file_path)
    task = _task_name_from_path(file_path)
    if root and task:
        candidate = os.path.join(root, f"task-{task}_channels.tsv")
        if os.path.isfile(candidate):
            return candidate

    if root:
        matches = sorted(Path(root).glob("task-*_channels.tsv"))
        if matches:
            return str(matches[0])
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    path = Path(file_path)
    stem = path.stem
    candidates = []
    if stem.endswith("_eeg"):
        candidates.append(path.with_name(stem[:-4] + "_events.tsv"))
    candidates.append(path.with_name(stem + "_events.tsv"))

    root = _find_dataset_root(file_path)
    task = _task_name_from_path(file_path)
    if root and task:
        candidates.append(Path(root) / f"task-{task}_events.tsv")

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    info = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
    try:
        df = pd.read_csv(participants_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return info

    if "participant_id" not in df.columns:
        return info

    candidates = [
        subject_id,
        subject_id.replace("sub-", ""),
        "sub-" + subject_id.replace("sub-", ""),
    ]
    row_df = pd.DataFrame()
    for candidate in candidates:
        row_df = df[df["participant_id"].astype(str) == candidate]
        if not row_df.empty:
            break
    if row_df.empty:
        return info

    row = row_df.iloc[0]
    for field in _REQUIRED_INFO_FIELDS:
        if field in row.index:
            info[field] = _clean_metadata_value(row[field])
    return info


def _clean_metadata_value(value) -> str:
    value_str = str(value).strip()
    if value_str.lower() in {"", "n/a", "na", "nan", "none"}:
        return "unknown"
    return value_str


def _normalize_sex(gender: str) -> str:
    value = gender.strip().lower()
    if value in {"m", "male"}:
        return "male"
    if value in {"f", "female"}:
        return "female"
    return "unknown"


def _read_channel_specs(file_path: str) -> List[Tuple[str, str]]:
    channels_path = _find_channels_tsv(file_path)
    if not channels_path:
        return list(_FALLBACK_CHANNEL_SPECS)
    try:
        df = pd.read_csv(channels_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return list(_FALLBACK_CHANNEL_SPECS)
    if "name" not in df.columns or "type" not in df.columns:
        return list(_FALLBACK_CHANNEL_SPECS)
    return [
        (str(row["name"]).strip(), str(row["type"]).strip().upper())
        for _, row in df.iterrows()
        if str(row.get("name", "")).strip()
    ]


def _rename_biosemi_slots_from_channels_tsv(raw: mne.io.BaseRaw, file_path: str) -> None:
    """Rename BioSemi A/B slots using the dataset channels.tsv evidence file."""
    specs = _read_channel_specs(file_path)
    target_names = [name for name, ch_type in specs if ch_type.upper() == "EEG"]
    if len(target_names) < 64:
        return

    existing = set(raw.ch_names)
    rename_map: Dict[str, str] = {}
    for source_name, target_name in zip(_BIOSEMI_BDF_64_NAMES, target_names[:64]):
        if source_name in existing and source_name != target_name and target_name not in existing:
            rename_map[source_name] = target_name

    if rename_map:
        raw.rename_channels(rename_map)


def _set_channel_types_from_sidecar(raw: mne.io.BaseRaw, file_path: str) -> None:
    specs = _read_channel_specs(file_path)
    ch_types: Dict[str, str] = {}
    raw_names = set(raw.ch_names)
    for name, source_type in specs:
        if name not in raw_names:
            continue
        if source_type == "EEG":
            ch_types[name] = "eeg"
        elif source_type in _AUX_AS_MISC:
            ch_types[name] = "misc"

    if "Status" in raw_names:
        ch_types["Status"] = "stim"

    if ch_types:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r"The unit for channel\(s\).*")
            raw.set_channel_types(ch_types)


def _set_montage(raw: mne.io.BaseRaw) -> None:
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(events_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return None


def _is_missing(value) -> bool:
    return str(value).strip().lower() in {"", "n/a", "na", "nan", "none"}


def _event_value_to_string(value) -> str:
    value_str = str(value).strip()
    try:
        value_float = float(value_str)
    except ValueError:
        return value_str
    if value_float.is_integer():
        return str(int(value_float))
    return value_str


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Build annotations from events.tsv while preserving original event values."""
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
        if "value" in events_df.columns and not _is_missing(row.get("value")):
            description = _event_value_to_string(row.get("value"))
        elif "trial_type" in events_df.columns and not _is_missing(row.get("trial_type")):
            description = str(row.get("trial_type")).strip()

        if not description:
            continue

        onsets.append(onset)
        durations.append(duration)
        descriptions.append(description)

    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS001787Kernel:
    """Stage-1 kernel for OpenNeuro ds001787."""

    KERNEL_ID = "openneuro_ds001787"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)
        subject_id = _get_subject_id_from_path(file_path) or "unknown"

        participants_info: Dict[str, str] = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
        participants_path = _find_participants_tsv(file_path) if file_path else None
        if participants_path and subject_id != "unknown":
            participants_info = _read_participants_info(participants_path, subject_id)

        original_description = raw.info.get("description", "") or ""
        gender = participants_info.get("gender", "unknown")
        eegunity_description = {
            "age": participants_info.get("age", "unknown"),
            "sex": _normalize_sex(gender),
            "amplifier": "BIOSEMI ActiveTwo",
            "cap": "BioSemi 64-channel cap",
            "handedness": "unknown",
            "gender": gender,
            "group": participants_info.get("group", "unknown"),
        }

        if file_path:
            _rename_biosemi_slots_from_channels_tsv(raw, file_path)
            _set_channel_types_from_sidecar(raw, file_path)
            _set_montage(raw)

            events_path = _find_events_tsv(file_path)
            if events_path:
                events_df = _read_events_tsv(events_path)
                annotations = _events_to_annotations(events_df)
                if len(annotations) > 0:
                    raw.set_annotations(annotations)

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = OpenNeuroDS001787Kernel()
