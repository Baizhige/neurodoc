"""OpenNeuro ds005505 (HBN EEG Release 1) kernel for EEGUnity.

The HBN-EEG release is a multi-task developmental EEG battery. This kernel keeps
native BIDS event names unchanged, exposes participant-level phenotype fields in
``eegunity_description`` (including ``p_factor``), and adds two narrowly scoped
derived labels for the contrast-change detection task:

* ``response_time`` misc channel: target-to-first-valid-button latency in
  seconds, filled only from target onset to the matched response.
* ``contrast_response_correct`` / ``contrast_response_incorrect`` annotations:
  response-locked events derived from target side and response feedback.

The original EEGLAB files already contain annotations, but the BIDS
``events.tsv`` files are the authoritative source here because they include the
behavioral columns imported by the HBN-EEG release. To avoid double-counting
events during scans, this kernel replaces embedded annotations with sidecar
events whenever the matching ``events.tsv`` file is available.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import mne
import numpy as np
import pandas as pd


DATASET_ID = "openneuro_ds005505"

_CONTRAST_TASK = "contrastChangeDetection"
_TARGET_TO_CORRECT_PRESS = {
    "left_target": "left_buttonPress",
    "right_target": "right_buttonPress",
}
_PRESS_LABELS = set(_TARGET_TO_CORRECT_PRESS.values())
_DERIVED_CORRECT_EVENT = "contrast_response_correct"
_DERIVED_INCORRECT_EVENT = "contrast_response_incorrect"
_RESPONSE_TIME_CHANNEL = "response_time"
_MAX_CONTRAST_RESPONSE_SEC = 2.5

_PARTICIPANT_FIELDS = (
    "release_number",
    "sex",
    "age",
    "ehq_total",
    "commercial_use",
    "full_pheno",
    "p_factor",
    "attention",
    "internalizing",
    "externalizing",
    "RestingState",
    "DespicableMe",
    "FunwithFractals",
    "ThePresent",
    "DiaryOfAWimpyKid",
    "contrastChangeDetection_1",
    "contrastChangeDetection_2",
    "contrastChangeDetection_3",
    "surroundSupp_1",
    "surroundSupp_2",
    "seqLearning6target",
    "seqLearning8target",
    "symbolSearch",
)

_CHANNEL_TYPE_MAP = {
    "EEG": "eeg",
    "EOG": "eog",
    "ECG": "ecg",
    "EMG": "emg",
    "MISC": "misc",
    "OTHER": "misc",
    "TRIG": "stim",
    "TRIGGER": "stim",
    "STIM": "stim",
}

_DERIVED_EVENT_HINTS = {
    _DERIVED_CORRECT_EVENT: {
        "type": "event",
        "meta_level": "super",
        "meaning": "Button response was correct for the preceding contrast target",
    },
    _DERIVED_INCORRECT_EVENT: {
        "type": "event",
        "meta_level": "super",
        "meaning": "Button response was incorrect for the preceding contrast target",
    },
}

_DERIVED_MISC_HINTS = {
    _RESPONSE_TIME_CHANNEL: {
        "source": "derived (kernel)",
        "meta_level": "super",
        "notes": (
            "Latency in seconds from left_target/right_target onset to the first "
            "valid left_buttonPress/right_buttonPress in the same contrast trial"
        ),
    }
}


def _row_get(row, *keys: str) -> str:
    if isinstance(row, (str, os.PathLike)):
        return os.fspath(row)

    for key in keys:
        value = None
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
    return match.group(1) if match else ""


def _extract_entity(file_path: str, entity: str) -> str:
    match = re.search(rf"(?:^|_){entity}-([^_./]+)", Path(file_path).name)
    return match.group(1) if match else ""


def _raw_prefix(file_path: str) -> str:
    name = Path(file_path).name
    for suffix in (
        "_eeg.set",
        "_eeg.fdt",
        "_eeg.bdf",
        "_eeg.edf",
        "_eeg.vhdr",
        "_eeg.eeg",
        "_eeg.fif",
    ):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return Path(file_path).stem


def _sidecar_path(file_path: str, suffix: str) -> Optional[Path]:
    path = Path(file_path)
    candidate = path.with_name(_raw_prefix(file_path) + suffix)
    return candidate if candidate.is_file() else None


def _events_tsv_path(file_path: str) -> Optional[Path]:
    return _sidecar_path(file_path, "_events.tsv")


def _channels_tsv_path(file_path: str) -> Optional[Path]:
    return _sidecar_path(file_path, "_channels.tsv")


def _file_eeg_json_path(file_path: str) -> Optional[Path]:
    return _sidecar_path(file_path, "_eeg.json")


def _task_eeg_json_path(root: Optional[Path], task: str) -> Optional[Path]:
    if not root or not task:
        return None
    candidate = root / f"task-{task}_eeg.json"
    return candidate if candidate.is_file() else None


def _read_json(path: Optional[Path]) -> Dict[str, object]:
    if not path:
        return {}
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _read_tsv(path: Optional[Path]) -> Optional[pd.DataFrame]:
    if not path:
        return None
    try:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    except Exception:
        return None


def _missing(value: object) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "n/a", "na", "null"}


def _clean_value(value: object) -> str:
    return "" if _missing(value) else str(value).strip()


def _read_participant_info(root: Optional[Path], subject_id: str) -> Dict[str, str]:
    if not root or not subject_id:
        return {}

    participants_path = root / "participants.tsv"
    participants = _read_tsv(participants_path)
    if participants is None or "participant_id" not in participants.columns:
        return {}

    subject_short = subject_id.replace("sub-", "")
    mask = (participants["participant_id"] == subject_id) | (
        participants["participant_id"] == subject_short
    )
    if not mask.any():
        return {}

    row = participants.loc[mask].iloc[0]
    return {str(key): _clean_value(row.get(key)) for key in participants.columns}


def _merged_eeg_json(root: Optional[Path], task: str, file_path: str) -> Dict[str, object]:
    data: Dict[str, object] = {}
    data.update(_read_json(_task_eeg_json_path(root, task)))
    data.update(_read_json(_file_eeg_json_path(file_path)))
    return data


def _device_label(eeg_json: Dict[str, object]) -> str:
    manufacturer = _clean_value(eeg_json.get("Manufacturer"))
    model = _clean_value(eeg_json.get("ManufacturersModelName"))
    if manufacturer and model:
        return f"{manufacturer} {model}"
    return manufacturer or model


def _build_description(
    file_path: str,
    root: Optional[Path],
    subject_info: Dict[str, str],
    eeg_json: Dict[str, object],
) -> Dict[str, str]:
    task = _extract_entity(file_path, "task")
    run = _extract_entity(file_path, "run")
    subject_id = _extract_subject_id(file_path)

    description: Dict[str, str] = {
        "dataset": DATASET_ID,
        "dataset_root": str(root) if root else "",
        "subject_id": subject_id,
        "task": task,
        "run": run,
        "age": subject_info.get("age", ""),
        "sex": subject_info.get("sex", ""),
        "device": _device_label(eeg_json),
        "manufacturer": _clean_value(eeg_json.get("Manufacturer")),
        "manufacturers_model_name": _clean_value(eeg_json.get("ManufacturersModelName")),
        "eeg_reference": _clean_value(eeg_json.get("EEGReference")),
        "recording_type": _clean_value(eeg_json.get("RecordingType")),
        "sampling_frequency": _clean_value(eeg_json.get("SamplingFrequency")),
        "power_line_frequency": _clean_value(eeg_json.get("PowerLineFrequency")),
    }

    for field in _PARTICIPANT_FIELDS:
        if field in subject_info:
            description[field] = subject_info[field]

    return description


def _set_channel_types_from_sidecar(raw: mne.io.BaseRaw, file_path: str) -> None:
    channels = _read_tsv(_channels_tsv_path(file_path))
    if channels is None or "name" not in channels.columns or "type" not in channels.columns:
        return

    raw_names = set(raw.ch_names)
    mapping: Dict[str, str] = {}
    for _, row in channels.iterrows():
        name = _clean_value(row.get("name"))
        kind = _clean_value(row.get("type")).upper()
        mapped = _CHANNEL_TYPE_MAP.get(kind)
        if name in raw_names and mapped:
            mapping[name] = mapped

    if not mapping:
        return

    try:
        raw.set_channel_types(mapping, on_unit_change="ignore")
    except TypeError:
        raw.set_channel_types(mapping)


def _set_hbn_montage(raw: mne.io.BaseRaw) -> None:
    # The per-file channels.tsv files name E1-E128 plus Cz, and task EEG JSON
    # files identify the EGI 128-channel GSN system, so no channel renaming is
    # needed before applying MNE's matching GSN montage.
    try:
        montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
        raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
    except TypeError:
        try:
            montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            return
    except Exception:
        return


def _normalize_label(value: object) -> str:
    return _clean_value(value)


def _numeric_series(values: Iterable[object], default: float = 0.0) -> pd.Series:
    return pd.to_numeric(pd.Series(list(values)), errors="coerce").fillna(default)


def _prepare_events(events: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if events is None or events.empty or "onset" not in events.columns:
        return None

    df = events.copy()
    label_col = None
    for candidate in ("trial_type", "value", "stim_type"):
        if candidate in df.columns:
            label_col = candidate
            break
    if label_col is None and "event_code" in df.columns:
        label_col = "event_code"
    if label_col is None:
        return None

    df["_label"] = df[label_col].map(_normalize_label)
    df["_onset_sec"] = pd.to_numeric(df["onset"], errors="coerce")
    if "duration" in df.columns:
        df["_duration_sec"] = _numeric_series(df["duration"], default=0.0)
    else:
        df["_duration_sec"] = 0.0

    df = df.dropna(subset=["_onset_sec"]).copy()
    df = df[df["_label"] != ""].sort_values("_onset_sec").reset_index(drop=True)
    return df if not df.empty else None


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
        if onset < 0 or onset > max_time:
            continue
        valid_onsets.append(float(onset))
        valid_durations.append(max(0.0, float(duration)))
        valid_descriptions.append(str(description))
    return valid_onsets, valid_durations, valid_descriptions


def _events_to_annotations(
    raw: mne.io.BaseRaw, events: Optional[pd.DataFrame]
) -> Optional[mne.Annotations]:
    if events is None or events.empty:
        return None

    onsets, durations, descriptions = _valid_annotation_rows(
        raw,
        events["_onset_sec"].astype(float),
        events["_duration_sec"].astype(float),
        events["_label"].astype(str),
    )
    if not onsets:
        return None

    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _feedback_value(record: Dict[str, object]) -> str:
    return _clean_value(record.get("feedback")).lower()


def _is_valid_contrast_press(record: Dict[str, object], has_feedback: bool) -> bool:
    if record["_label"] not in _PRESS_LABELS:
        return False
    if not has_feedback:
        return True

    feedback = _feedback_value(record)
    return feedback in {"", "smiley_face", "sad_face"}


def _press_correctness(target_label: str, press_record: Dict[str, object]) -> str:
    feedback = _feedback_value(press_record)
    if feedback == "smiley_face":
        return _DERIVED_CORRECT_EVENT
    if feedback == "sad_face":
        return _DERIVED_INCORRECT_EVENT
    if press_record["_label"] == _TARGET_TO_CORRECT_PRESS[target_label]:
        return _DERIVED_CORRECT_EVENT
    return _DERIVED_INCORRECT_EVENT


def _build_contrast_derivatives(
    events: Optional[pd.DataFrame], sfreq: float, n_times: int
) -> Tuple[np.ndarray, Optional[mne.Annotations]]:
    response_time = np.full((1, n_times), np.nan, dtype=float)
    if events is None or events.empty:
        return response_time, None

    has_feedback = "feedback" in events.columns
    records = events.to_dict("records")
    derived_onsets: list[float] = []
    derived_durations: list[float] = []
    derived_descriptions: list[str] = []

    for index, record in enumerate(records):
        target_label = record["_label"]
        if target_label not in _TARGET_TO_CORRECT_PRESS:
            continue

        target_onset = float(record["_onset_sec"])
        press_record = None
        for future in records[index + 1 :]:
            future_label = future["_label"]
            future_onset = float(future["_onset_sec"])

            if future_label in _TARGET_TO_CORRECT_PRESS:
                break
            if future_onset - target_onset > _MAX_CONTRAST_RESPONSE_SEC:
                break
            if _is_valid_contrast_press(future, has_feedback):
                press_record = future
                break

        if press_record is None:
            continue

        press_onset = float(press_record["_onset_sec"])
        rt = press_onset - target_onset
        if rt <= 0 or rt > _MAX_CONTRAST_RESPONSE_SEC:
            continue

        start = max(0, min(int(round(target_onset * sfreq)), n_times - 1))
        stop = max(start + 1, min(int(round(press_onset * sfreq)), n_times))
        response_time[0, start:stop] = rt

        derived_onsets.append(press_onset)
        derived_durations.append(0.0)
        derived_descriptions.append(_press_correctness(target_label, press_record))

    if not derived_onsets:
        return response_time, None

    derived_annotations = mne.Annotations(
        onset=derived_onsets,
        duration=derived_durations,
        description=derived_descriptions,
    )
    return response_time, derived_annotations


def _append_annotations(raw: mne.io.BaseRaw, annotations: Optional[mne.Annotations]) -> None:
    if annotations is None or len(annotations) == 0:
        return
    if len(raw.annotations):
        raw.set_annotations(raw.annotations + annotations)
    else:
        raw.set_annotations(annotations)


def _add_response_time_channel(
    raw: mne.io.BaseRaw, response_time: np.ndarray
) -> Tuple[mne.io.BaseRaw, bool]:
    if _RESPONSE_TIME_CHANNEL in raw.ch_names or not np.isfinite(response_time).any():
        return raw, False

    if not raw.preload:
        raw.load_data(verbose="ERROR")

    info = mne.create_info(
        ch_names=[_RESPONSE_TIME_CHANNEL],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    rt_raw = mne.io.RawArray(
        response_time,
        info,
        first_samp=raw.first_samp,
        verbose="ERROR",
    )
    if raw.info.get("meas_date") is not None:
        rt_raw.set_meas_date(raw.info["meas_date"])

    raw.add_channels([rt_raw], force_update_info=True)
    return raw, True


class OpenNeuroDS005505Kernel:
    """Stage-1 kernel for OpenNeuro ds005505 (HBN EEG Release 1)."""

    DATASET_NAME = DATASET_ID
    DATASET_PATH = "openneuro/ds005505"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = _get_file_path(row)
        root = _find_dataset_root(file_path)
        subject_id = _extract_subject_id(file_path)
        task = _extract_entity(file_path, "task")

        participant_info = _read_participant_info(root, subject_id)
        eeg_json = _merged_eeg_json(root, task, file_path)
        original_description = raw.info.get("description") or ""

        _set_channel_types_from_sidecar(raw, file_path)
        _set_hbn_montage(raw)

        events = _prepare_events(_read_tsv(_events_tsv_path(file_path)))
        sidecar_annotations = _events_to_annotations(raw, events)
        if sidecar_annotations is not None:
            raw.set_annotations(sidecar_annotations)

        derived_event_hints: Dict[str, Dict[str, str]] = {}
        derived_misc_hints: Dict[str, Dict[str, str]] = {}
        if task == _CONTRAST_TASK:
            response_time, contrast_annotations = _build_contrast_derivatives(
                events, raw.info["sfreq"], raw.n_times
            )
            if contrast_annotations is not None:
                _append_annotations(raw, contrast_annotations)
                derived_event_hints = _DERIVED_EVENT_HINTS

            raw, added_rt = _add_response_time_channel(raw, response_time)
            if added_rt:
                derived_misc_hints = _DERIVED_MISC_HINTS

        raw.info["description"] = json.dumps(
            {
                "original_description": str(original_description),
                "eegunity_description": _build_description(
                    file_path, root, participant_info, eeg_json
                ),
                "eegunity_scan_hints": {
                    "events": derived_event_hints,
                    "misc_channels": derived_misc_hints,
                },
            },
            ensure_ascii=False,
        )
        return raw


KERNEL = OpenNeuroDS005505Kernel()
