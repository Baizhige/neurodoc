"""OpenNeuro DS005505 (HBN EEG Release 1) stage-1 kernel for EEGUnity.

This kernel keeps the raw event stream intact and adds only two derived labels
needed by the current benchmark draft:

1. `response_time` misc channel for contrast change detection, computed as the
   latency between a target onset and the first subsequent button press in the
   same trial window.
2. `contrast_response_correct` / `contrast_response_incorrect` response-locked
   annotations, derived from whether the button side matches the target side.

The sequence-learning and resting-state tasks rely on native events only.
The p-factor target is exposed as a participant-level description field.
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, Optional

import mne
import numpy as np
import pandas as pd


_HBN_129_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    "F9", "F10",
    "FT9", "FT10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "PO1", "PO2",
    "M1", "M2",
    "VEO", "HEO", "VEOG", "HEOG",
    "CB1", "CB2",
    "A1", "A2",
    "REF", "CzREF",
    "Status", "Trigger",
]

_TARGET_TO_CORRECT_PRESS = {
    "left_target": "left_buttonPress",
    "right_target": "right_buttonPress",
}
_PRESS_LABELS = set(_TARGET_TO_CORRECT_PRESS.values())
_DERIVED_CORRECT_EVENT = "contrast_response_correct"
_DERIVED_INCORRECT_EVENT = "contrast_response_incorrect"
_MAX_CONTRAST_RESPONSE_SEC = 2.5
KERNEL_ID = "openneuro_ds005505"
_DERIVED_EVENT_HINTS = {
    _DERIVED_CORRECT_EVENT: {
        "type": "event",
        "meta_level": "super",
        "meaning": "Response side matched the preceding contrast target",
    },
    _DERIVED_INCORRECT_EVENT: {
        "type": "event",
        "meta_level": "super",
        "meaning": "Response side did not match the preceding contrast target",
    },
}
_DERIVED_MISC_HINTS = {
    "response_time": {
        "source": "derived (kernel)",
        "meta_level": "super",
        "notes": "Latency from target onset to the first subsequent button press in the same contrast trial",
    }
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a conservative rename map for recognizable HBN channel labels."""
    rename_map: Dict[str, str] = {}
    used_targets = set()

    for ch in raw.ch_names:
        cleaned = ch.strip()
        for prefix in ("EEG ", "EEG-", "eeg_", "Ch ", "CH", "Ch"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        target = None
        if cleaned in _HBN_129_CHANNELS and cleaned not in used_targets:
            target = cleaned
        elif cleaned.upper() in {c.upper() for c in _HBN_129_CHANNELS}:
            for std_ch in _HBN_129_CHANNELS:
                if std_ch.upper() == cleaned.upper() and std_ch not in used_targets:
                    target = std_ch
                    break

        if target is not None:
            rename_map[ch] = target
            used_targets.add(target)

    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):
        for cand in (
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ):
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    base = file_path.replace("_eeg.edf", "_events.tsv")
    base = base.replace("_eeg.set", "_events.tsv")
    base = base.replace("_eeg.vhdr", "_events.tsv")
    base = base.replace("_eeg.eeg", "_events.tsv")
    base = base.replace("_eeg.fif", "_events.tsv")

    dir_name = os.path.dirname(file_path)
    parent_dir = os.path.dirname(dir_name)
    candidates = (
        base,
        os.path.join(dir_name, os.path.basename(base)),
        os.path.join(parent_dir, "eeg", os.path.basename(base)),
    )
    for cand in candidates:
        cand = os.path.normpath(cand)
        if os.path.exists(cand):
            return cand

    try:
        for name in os.listdir(dir_name):
            if name.endswith("_events.tsv"):
                return os.path.join(dir_name, name)
    except OSError:
        pass
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _read_participants_tsv(participants_path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(participants_path, sep="\t")
    except Exception:
        return None


def _get_subject_info_from_participants(
    participants_df: pd.DataFrame, subject_id: str
) -> Dict[str, str]:
    if participants_df is None or len(participants_df) == 0:
        return {}

    participant_id_col = "participant_id"
    if participant_id_col not in participants_df.columns:
        for col in participants_df.columns:
            if col.lower() in ("participant_id", "subject_id", "sub_id"):
                participant_id_col = col
                break
    if participant_id_col not in participants_df.columns:
        return {}

    search_id = subject_id if subject_id.startswith("sub-") else f"sub-{subject_id}"
    search_id_short = search_id.replace("sub-", "")
    mask = (
        (participants_df[participant_id_col].astype(str) == search_id)
        | (participants_df[participant_id_col].astype(str) == search_id_short)
    )
    if not mask.any():
        return {}

    row = participants_df[mask].iloc[0]
    info: Dict[str, str] = {}
    for col in participants_df.columns:
        val = row[col]
        info[col] = "" if pd.isna(val) else str(val)
    return info


def _normalize_event_label(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in ("", "nan", "n/a", "na", "none"):
        return ""
    return text


def _prepare_events(events_df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if events_df is None or len(events_df) == 0 or "onset" not in events_df.columns:
        return None

    df = events_df.copy()
    label_col = None
    for cand in ("trial_type", "value", "stim_type"):
        if cand in df.columns:
            label_col = cand
            break
    if label_col is None:
        df["_label"] = ""
    else:
        df["_label"] = df[label_col].map(_normalize_event_label)

    df["_onset_sec"] = pd.to_numeric(df["onset"], errors="coerce")
    if "duration" in df.columns:
        df["_duration_sec"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0.0)
    else:
        df["_duration_sec"] = 0.0

    df = df.dropna(subset=["_onset_sec"]).copy()
    df = df[df["_label"] != ""].sort_values("_onset_sec").reset_index(drop=True)
    return df


def _events_to_annotations(events_df: Optional[pd.DataFrame]) -> Optional[mne.Annotations]:
    if events_df is None or len(events_df) == 0:
        return None
    try:
        return mne.Annotations(
            onset=events_df["_onset_sec"].astype(float).tolist(),
            duration=events_df["_duration_sec"].astype(float).tolist(),
            description=events_df["_label"].astype(str).tolist(),
        )
    except Exception:
        return None


def _build_contrast_derivatives(
    events_df: Optional[pd.DataFrame], sfreq: float, n_times: int
) -> tuple[np.ndarray, Optional[mne.Annotations]]:
    response_time = np.full((1, n_times), np.nan, dtype=float)
    if events_df is None or len(events_df) == 0:
        return response_time, None

    records = events_df[["_label", "_onset_sec"]].to_dict("records")
    derived_onsets = []
    derived_durations = []
    derived_descriptions = []

    for idx, record in enumerate(records):
        target_label = record["_label"]
        if target_label not in _TARGET_TO_CORRECT_PRESS:
            continue

        target_onset = float(record["_onset_sec"])
        next_target_onset = None
        press_record = None

        for future in records[idx + 1:]:
            future_label = future["_label"]
            future_onset = float(future["_onset_sec"])

            if future_label in _TARGET_TO_CORRECT_PRESS:
                next_target_onset = future_onset
                break

            if future_label in _PRESS_LABELS:
                if future_onset - target_onset > _MAX_CONTRAST_RESPONSE_SEC:
                    break
                press_record = future
                break

        if press_record is None:
            continue

        press_onset = float(press_record["_onset_sec"])
        if next_target_onset is not None and press_onset >= next_target_onset:
            continue

        rt = press_onset - target_onset
        if rt <= 0:
            continue

        start_sample = max(0, min(int(round(target_onset * sfreq)), n_times - 1))
        end_sample = max(start_sample + 1, min(int(round(press_onset * sfreq)), n_times))
        response_time[0, start_sample:end_sample] = rt

        derived_onsets.append(press_onset)
        derived_durations.append(0.0)
        if press_record["_label"] == _TARGET_TO_CORRECT_PRESS[target_label]:
            derived_descriptions.append(_DERIVED_CORRECT_EVENT)
        else:
            derived_descriptions.append(_DERIVED_INCORRECT_EVENT)

    if not derived_onsets:
        return response_time, None

    derived_annotations = mne.Annotations(
        onset=derived_onsets,
        duration=derived_durations,
        description=derived_descriptions,
    )
    return response_time, derived_annotations


class OpenNeuroDS005505Kernel:
    """Stage-1 kernel for OpenNeuro DS005505 (HBN EEG Release 1)."""

    DATASET_NAME = "openneuro_ds005505"
    DATASET_PATH = "openneuro/ds005505"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = str(row["File Path"])
        subject_id = _get_subject_id_from_path(file_path) or ""

        participants_path = _find_participants_tsv(file_path)
        participants_df = _read_participants_tsv(participants_path) if participants_path else None
        subject_info = (
            _get_subject_info_from_participants(participants_df, subject_id)
            if participants_df is not None and subject_id
            else {}
        )

        eegunity_description = {
            "age": subject_info.get("age", ""),
            "sex": subject_info.get("sex", ""),
            "amplifier": subject_info.get("amplifier", ""),
            "cap": subject_info.get("cap", ""),
            "handedness": subject_info.get("handedness", ""),
            "attention": subject_info.get("attention", ""),
            "ehq_total": subject_info.get("ehq_total", ""),
            "externalizing": subject_info.get("externalizing", ""),
            "full_pheno": subject_info.get("full_pheno", ""),
            "internalizing": subject_info.get("internalizing", ""),
            "p_factor": subject_info.get("p_factor", ""),
            "seqLearning6target": subject_info.get("seqLearning6target", ""),
        }

        original_description = raw.info.get("description", "")

        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        try:
            montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
            raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
        except Exception:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, match_case=False, match_alias=True, on_missing="ignore")
            except Exception:
                pass

        events_path = _find_events_tsv(file_path)
        events_df = _prepare_events(_read_events_tsv(events_path) if events_path else None)
        if events_df is not None and len(events_df) > 0:
            native_annotations = _events_to_annotations(events_df)
            if native_annotations is not None:
                if raw.annotations is not None and len(raw.annotations) > 0:
                    raw.set_annotations(raw.annotations + native_annotations)
                else:
                    raw.set_annotations(native_annotations)

        response_time_data, contrast_annotations = _build_contrast_derivatives(
            events_df, raw.info["sfreq"], len(raw.times)
        )

        derived_event_hints = {}
        if contrast_annotations is not None:
            if raw.annotations is not None and len(raw.annotations) > 0:
                raw.set_annotations(raw.annotations + contrast_annotations)
            else:
                raw.set_annotations(contrast_annotations)
            derived_event_hints = _DERIVED_EVENT_HINTS

        derived_misc_hints = {}
        if np.isfinite(response_time_data).any() and "response_time" not in raw.ch_names:
            info_rt = mne.create_info(
                ch_names=["response_time"],
                sfreq=raw.info["sfreq"],
                ch_types=["misc"],
            )
            raw_rt = mne.io.RawArray(response_time_data, info_rt, first_samp=raw.first_samp)
            raw = raw.add_channels([raw_rt], force_update_info=True)
            derived_misc_hints = _DERIVED_MISC_HINTS

        raw.info["description"] = json.dumps(
            {
                "original_description": original_description,
                "eegunity_description": eegunity_description,
                "eegunity_scan_hints": {
                    "events": derived_event_hints,
                    "misc_channels": derived_misc_hints,
                },
            },
            ensure_ascii=False,
        )

        return raw


KERNEL = OpenNeuroDS005505Kernel()
