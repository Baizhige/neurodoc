"""OpenNeuro ds004840 stage1 kernel for EEGUnity.

EEG/ECG/EMG recordings during Music-Assisted Relaxation (MAR) therapy
in ICU burn patients. Continuous data with no event markers; phases
(PRE/MTI/POST) derived from session timing.

Source: https://openneuro.org/datasets/ds004840
Paper: 10.1038/s41598-024-73211-3
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np


_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-1": "Fp1",
    "EEG-2": "Fpz",
    "EEG-3": "Fp2",
    "EEG-4": "F7",
    "EEG-5": "F3",
    "EEG-6": "Fz",
    "EEG-7": "F4",
    "EEG-8": "F8",
    "EEG-9": "T3",
    "EEG-10": "T5",
    "EEG-11": "C3",
    "EEG-12": "Cz",
    "EEG-13": "C4",
    "EEG-14": "T4",
    "EEG-15": "T6",
    "EEG-16": "P3",
    "EEG-17": "Pz",
    "EEG-18": "P4",
    "EEG-19": "O1",
    "EEG-20": "Oz",
    "EEG-21": "O2",
    "ECG": "ECG",
    "EMG": "EMG",
}

_EEG_STANDARD_NAMES = {"Fp1", "Fp2", "Fpz", "F7", "F3", "Fz", "F4", "F8",
                       "T3", "T4", "T5", "T6", "C3", "C4", "Cz",
                       "P3", "P4", "Pz", "O1", "O2", "Oz"}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    for source, target in _CHANNEL_RENAME_MAP.items():
        if source in existing:
            rename_map[source] = target
    return rename_map


def _get_phase_boundaries(duration_sec: float) -> Dict[str, tuple]:
    PRE_DURATION = 5 * 60
    MTI_TARGET = 15 * 60
    POST_DURATION = 5 * 60
    total_expected = PRE_DURATION + MTI_TARGET + POST_DURATION

    if duration_sec <= total_expected:
        available_for_mti = duration_sec - PRE_DURATION - POST_DURATION
        mti_duration = available_for_mti if available_for_mti > 0 else MTI_TARGET
    else:
        mti_duration = MTI_TARGET

    return {
        "PRE": (0.0, PRE_DURATION),
        "MTI": (PRE_DURATION, PRE_DURATION + mti_duration),
        "POST": (PRE_DURATION + mti_duration, duration_sec),
    }


def _detect_eeg_channels(ch_names: List[str]) -> List[str]:
    return [ch for ch in ch_names if ch in _EEG_STANDARD_NAMES]


class OpenNeuroDS004840Kernel:
    KERNEL_ID: str = "openneuro-ds004840-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")
        subject_id = row.get("subject_id", "unknown")

        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        channel_types = {}
        for ch in raw.ch_names:
            if ch.startswith("ECG"):
                channel_types[ch] = "ecg"
            elif ch.startswith("EMG"):
                channel_types[ch] = "emg"
            elif ch in _EEG_STANDARD_NAMES:
                channel_types[ch] = "eeg"

        if channel_types:
            raw.set_channel_types(channel_types)

        eeg_channels = _detect_eeg_channels(raw.ch_names)
        if eeg_channels:
            try:
                montage = mne.channels.make_standard_1020_montage()
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass

        age = "unknown"
        sex = "unknown"
        handedness = "unknown"

        if hasattr(udataset, "dataset_path"):
            participants_path = os.path.join(udataset.dataset_path, "participants.tsv")
            if os.path.exists(participants_path):
                try:
                    import pandas as pd
                    df = pd.read_csv(participants_path, sep="\t")
                    subject_rows = df[df["participant_id"] == subject_id]
                    if len(subject_rows) > 0:
                        row_data = subject_rows.iloc[0]
                        if "age" in row_data and pd.notna(row_data["age"]):
                            age = str(int(row_data["age"]))
                        if "sex" in row_data and pd.notna(row_data["sex"]):
                            sex = str(row_data["sex"]).lower()
                        if "handedness" in row_data and pd.notna(row_data["handedness"]):
                            handedness = str(row_data["handedness"]).lower()
                except Exception:
                    pass

        amplifier = "BrainAmp"
        cap = "Ag/AgCl"

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        duration_sec = raw.times[-1] if len(raw.times) > 0 else 0
        if duration_sec > 0:
            boundaries = _get_phase_boundaries(duration_sec)
            onsets = []
            durations = []
            descriptions = []

            for phase, (start, end) in boundaries.items():
                onsets.append(start)
                durations.append(end - start)
                descriptions.append(f"phase:{phase}")

            try:
                annotations = mne.Annotations(
                    onset=np.array(onsets),
                    duration=np.array(durations),
                    description=descriptions,
                )
                raw.set_annotations(annotations)
            except Exception:
                pass

        return raw


KERNEL = OpenNeuroDS004840Kernel()