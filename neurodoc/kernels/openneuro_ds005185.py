"""OpenNeuro ds005185 (EESM19) kernel for EEGUnity.

EESM19 is an ear-EEG sleep monitoring dataset with EEGLAB ``.set/.fdt`` EEG
files. The public BIDS dataset contains multiple recording types:

- sleep/acq-PSG: ear-EEG plus partial PSG, with two manual sleep scorings.
- sleep/acq-earEEG: self-applied ear-EEG sleep recordings, with diary events.
- ASSR/acq-PSG and electrodeTestLab/acq-PSG: laboratory quality checks.

This kernel keeps the raw EEG files lazy-loadable. It does not create derived
misc channels, because adding channels requires preloading large overnight
recordings. Instead, grounded sidecar labels are represented as annotations:
manual sleep scoring rows become ``scoring1_<code>-<stage>`` and
``scoring2_<code>-<stage>`` events, while sleep diary rows keep their original
``trial_type`` text.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import mne
import pandas as pd


_DATASET_ID = "openneuro_ds005185"
_DEVICE = "TMSi Mobita"
_STAGE_MAP = {
    "1": "W",
    "2": "REM",
    "3": "N1",
    "4": "N2",
    "5": "N3",
    "6": "A",
    "7": "Artefact",
    "8": "Unscored",
}


def _row_get(row, *keys: str) -> str:
    if isinstance(row, (str, os.PathLike)):
        return os.fspath(row)

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


def _extract_entity(file_path: str, entity: str) -> str:
    match = re.search(rf"_{entity}-([^_]+)", Path(file_path).name)
    if match:
        return match.group(1)

    if entity == "sub":
        match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
        return match.group(1).replace("sub-", "") if match else "unknown"
    if entity == "ses":
        match = re.search(r"(ses-[A-Za-z0-9]+)", file_path)
        return match.group(1).replace("ses-", "") if match else "unknown"
    return "unknown"


def _subject_id(file_path: str) -> str:
    match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
    return match.group(1) if match else "unknown"


def _session_id(file_path: str) -> str:
    match = re.search(r"(ses-[A-Za-z0-9]+)", file_path)
    return match.group(1) if match else "unknown"


def _read_json(path: Optional[Path]) -> Dict[str, object]:
    if not path:
        return {}
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _task_json_path(root: Optional[Path], task: str) -> Optional[Path]:
    if not root or task == "unknown":
        return None
    candidate = root / f"task-{task}_eeg.json"
    return candidate if candidate.is_file() else None


def _channel_sidecar_path(root: Optional[Path], acq: str) -> Optional[Path]:
    if not root or acq == "unknown":
        return None
    candidate = root / f"acq-{acq}_channels.tsv"
    return candidate if candidate.is_file() else None


def _participants_tsv_path(root: Optional[Path]) -> Optional[Path]:
    if not root:
        return None
    candidate = root / "participants.tsv"
    return candidate if candidate.is_file() else None


def _read_participant_info(root: Optional[Path], subject_id: str) -> Dict[str, str]:
    participants_path = _participants_tsv_path(root)
    if not participants_path:
        return {}

    try:
        participants = pd.read_csv(participants_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return {}

    if "participant_id" not in participants.columns:
        return {}

    row = participants.loc[participants["participant_id"] == subject_id]
    if row.empty:
        return {}
    values = row.iloc[0].to_dict()

    info: Dict[str, str] = {}
    for field in ("age", "sex"):
        value = str(values.get(field, "")).strip()
        if value:
            info[field] = value
    return info


def _set_channel_types(raw: mne.io.BaseRaw, root: Optional[Path], acq: str) -> None:
    channels_path = _channel_sidecar_path(root, acq)
    if not channels_path:
        return

    try:
        channels = pd.read_csv(channels_path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return

    if "name" not in channels.columns or "type" not in channels.columns:
        return

    raw_names = set(raw.ch_names)
    mapping: Dict[str, str] = {}
    for _, channel in channels.iterrows():
        name = str(channel.get("name", "")).strip()
        kind = str(channel.get("type", "")).strip().upper()
        if name not in raw_names:
            continue
        if kind == "EEG":
            mapping[name] = "eeg"
        elif kind == "EOG":
            mapping[name] = "eog"
        elif kind == "EMG":
            mapping[name] = "emg"
        elif kind == "ECG":
            mapping[name] = "ecg"
        elif kind in {"MISC", "OTHER"}:
            mapping[name] = "misc"

    if mapping:
        raw.set_channel_types(mapping)


def _base_prefix(file_path: str) -> str:
    name = Path(file_path).name
    for suffix in ("_eeg.set", "_eeg.fdt", "_eeg.edf"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return Path(file_path).stem


def _sleep_event_path(file_path: str, acq: str) -> Optional[Path]:
    """Return a sleep sidecar events path for acq=scoring1/scoring2/diary."""
    path = Path(file_path)
    prefix = _base_prefix(file_path)
    prefix = re.sub(r"_task-[^_]+", "_task-sleep", prefix)
    prefix = re.sub(r"_acq-[^_]+", f"_acq-{acq}", prefix)
    candidate = path.with_name(prefix + "_events.tsv")
    return candidate if candidate.is_file() else None


def _stage_label(value: object) -> Tuple[str, str]:
    raw = str(value).strip()
    if raw.lower().startswith("s") and raw[1:].isdigit():
        code = raw[1:]
    else:
        try:
            code = str(int(float(raw)))
        except Exception:
            code = raw
    return code, _STAGE_MAP.get(code, f"stage_{code}")


def _valid_annotation_rows(
    raw: mne.io.BaseRaw,
    onsets: Iterable[float],
    durations: Iterable[float],
    descriptions: Iterable[str],
) -> Tuple[list[float], list[float], list[str]]:
    max_time = raw.n_times / raw.info["sfreq"]
    valid_onsets: list[float] = []
    valid_durations: list[float] = []
    valid_descriptions: list[str] = []

    for onset, duration, description in zip(onsets, durations, descriptions):
        if onset < 0 or onset >= max_time:
            continue
        valid_onsets.append(float(onset))
        valid_durations.append(float(duration))
        valid_descriptions.append(str(description))
    return valid_onsets, valid_durations, valid_descriptions


def _append_annotations(
    raw: mne.io.BaseRaw,
    onsets: Iterable[float],
    durations: Iterable[float],
    descriptions: Iterable[str],
) -> None:
    onsets, durations, descriptions = _valid_annotation_rows(
        raw, onsets, durations, descriptions
    )
    if not onsets:
        return

    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )
    if len(raw.annotations):
        raw.set_annotations(raw.annotations + annotations)
    else:
        raw.set_annotations(annotations)


def _add_scoring_annotations(raw: mne.io.BaseRaw, file_path: str, scorer: int) -> bool:
    path = _sleep_event_path(file_path, f"scoring{scorer}")
    if not path:
        return False

    try:
        scoring = pd.read_csv(path, sep="\t")
    except Exception:
        return False

    stage_col = f"Scoring{scorer}"
    if not {"onset", "duration", stage_col}.issubset(scoring.columns):
        return False

    onsets = pd.to_numeric(scoring["onset"], errors="coerce").fillna(-1.0)
    durations = pd.to_numeric(scoring["duration"], errors="coerce").fillna(30.0)
    descriptions = []
    for value in scoring[stage_col]:
        code, label = _stage_label(value)
        descriptions.append(f"scoring{scorer}_{code}-{label}")

    _append_annotations(raw, onsets, durations, descriptions)
    return True


def _add_diary_annotations(raw: mne.io.BaseRaw, file_path: str) -> bool:
    path = _sleep_event_path(file_path, "diary")
    if not path:
        return False

    try:
        diary = pd.read_csv(path, sep="\t")
    except Exception:
        return False

    if "onset" not in diary.columns or "trial_type" not in diary.columns:
        return False

    onsets = pd.to_numeric(diary["onset"], errors="coerce").fillna(-1.0)
    if "duration" in diary.columns:
        durations = pd.to_numeric(diary["duration"], errors="coerce").fillna(0.0)
    else:
        durations = [0.0] * len(diary)
    descriptions = [str(value).strip() for value in diary["trial_type"]]
    _append_annotations(raw, onsets, durations, descriptions)
    return True


def _cap_description(acq: str) -> str:
    if acq == "PSG":
        return "custom ear-EEG earpieces with partial PSG electrodes"
    if acq == "earEEG":
        return "custom self-applied ear-EEG earpieces with single EOG electrode"
    return "custom ear-EEG earpieces"


def _build_description(
    raw: mne.io.BaseRaw,
    file_path: str,
    root: Optional[Path],
    scoring1_available: bool,
    scoring2_available: bool,
    diary_available: bool,
) -> str:
    subject_id = _subject_id(file_path)
    session_id = _session_id(file_path)
    task = _extract_entity(file_path, "task")
    acq = _extract_entity(file_path, "acq")
    participant = _read_participant_info(root, subject_id)
    task_json = _read_json(_task_json_path(root, task))

    channel_counts = {
        "eeg": raw.get_channel_types().count("eeg"),
        "eog": raw.get_channel_types().count("eog"),
        "emg": raw.get_channel_types().count("emg"),
        "misc": raw.get_channel_types().count("misc"),
    }

    eegunity_description: Dict[str, object] = {
        "dataset": _DATASET_ID,
        "subject_id": subject_id,
        "session": session_id,
        "age": participant.get("age", "unknown"),
        "sex": participant.get("sex", "unknown"),
        "device": _DEVICE,
        "amplifier": _DEVICE,
        "cap": _cap_description(acq),
        "task": task,
        "acq": acq,
        "sampling_rate_hz": raw.info.get("sfreq", "unknown"),
        "recording_type": "EEG",
        "eeg_channel_count": str(channel_counts["eeg"]),
        "eog_channel_count": str(channel_counts["eog"]),
        "emg_channel_count": str(channel_counts["emg"]),
        "misc_channel_count": str(channel_counts["misc"]),
        "eeg_reference": str(task_json.get("EEGReference", "average")).strip() or "average",
        "power_line_frequency_hz": str(task_json.get("PowerLineFrequency", 50)),
        "sleep_scoring1_available": str(bool(scoring1_available)),
        "sleep_scoring2_available": str(bool(scoring2_available)),
        "sleep_diary_available": str(bool(diary_available)),
        "sleep_stage_event_format": "scoring<scorer>_<code>-<stage>",
        "source_file": Path(file_path).name,
    }
    if "TaskDescription" in task_json:
        eegunity_description["task_description"] = str(task_json["TaskDescription"]).strip()

    return json.dumps(
        {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": eegunity_description,
        },
        separators=(",", ":"),
    )


class OpenNeuroDS005185Kernel:
    """Stage-1 kernel for OpenNeuro ds005185."""

    KERNEL_ID = _DATASET_ID

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)
        if not file_path:
            return raw

        root = _find_dataset_root(file_path)
        task = _extract_entity(file_path, "task")
        acq = _extract_entity(file_path, "acq")

        _set_channel_types(raw, root, acq)

        scoring1_available = False
        scoring2_available = False
        diary_available = False
        if task == "sleep":
            diary_available = _add_diary_annotations(raw, file_path)
            if acq == "PSG":
                scoring1_available = _add_scoring_annotations(raw, file_path, scorer=1)
                scoring2_available = _add_scoring_annotations(raw, file_path, scorer=2)

        raw.info["description"] = _build_description(
            raw=raw,
            file_path=file_path,
            root=root,
            scoring1_available=scoring1_available,
            scoring2_available=scoring2_available,
            diary_available=diary_available,
        )
        return raw


KERNEL = OpenNeuroDS005185Kernel()
