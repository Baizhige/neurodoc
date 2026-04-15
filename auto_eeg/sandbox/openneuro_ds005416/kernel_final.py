"""OpenNeuro DS005416 stage1 kernel for EEGUnity.

Fatigue Characterization of EEG under Mixed Reality Stereo Vision.
64-channel EEG, 1000 Hz, continuous recording during MR viewing.

Source: https://openneuro.org/datasets/ds005416
        https://doi.org/10.18112/openneuro.ds005416.v1.0.1
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: OpenNeuro dataset_description.json (openneuro.org)
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # All subject info unavailable in public BIDS files; set as unknown.
    # Human reviewers should populate from paper supplementary materials.
    f"sub-{i:02d}": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }
    for i in range(1, 24)
}

# Source: Paper 10.1007_s00221_025_07207_4 (main study protocol)
# 64-channel MR-compatible EEG cap; amplifier likely BrainAmp MR plus or equivalent.
# Annotator: LLM, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "unknown",  # LLM 推断，需人类复核
    "cap": "unknown",  # LLM 推断，需人类复核
}

# Standard 64-channel layout for MR-compatible EEG caps.
# Source: standard_1020 montage (extended 64-channel).
# Annotator: LLM, 2026-04-08
_64CH_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]


def _detect_events(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Detect events from annotations or stim channels.

    The dataset uses continuous EEG without trial events.
    Annotations may be sparse or absent; create empty annotations as fallback.
    """
    try:
        annotations = mne.annotations_from_events(
            events=mne.find_events(raw, stim_channel="auto", min_duration=0.001),
            sfreq=raw.info["sfreq"],
            event_desc={0: "trigger"},
        )
        if len(annotations) == 0:
            return mne.Annotations(onset=[], duration=[], description=[])
        return annotations
    except Exception:
        return mne.Annotations(onset=[], duration=[], description=[])


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if present."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _extract_subject_info(
    row: Any, participants_df: pd.DataFrame
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or use defaults."""
    subject_id = row.get("subject_id", "unknown")
    if not participants_df.empty:
        match = participants_df[
            participants_df["participant_id"] == subject_id
        ]
        if not match.empty:
            row_data = match.iloc[0]
            age = str(int(row_data.get("age", "unknown")))
            sex = str(row_data.get("sex", "unknown")).lower()
            if sex not in ("male", "female"):
                sex = "unknown"
            handedness = str(row_data.get("handedness", "unknown")).lower()
            if handedness not in ("right", "left", "ambidextrous"):
                handedness = "unknown"
            return {"age": age, "sex": sex, "handedness": handedness}

    subject_key = f"sub-{subject_id[-2:]}" if isinstance(subject_id, str) else f"sub-{int(subject_id):02d}"
    if subject_key in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_key]
    return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


class OpenNeuroDS005416Kernel:
    """Stage1 kernel for OpenNeuro DS005416 dataset."""

    KERNEL_ID: str = "openneuro-ds005416-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        dataset_path = udataset.path if hasattr(udataset, "path") else ""

        # Get original description.
        original_desc = raw.info.get("description", "")

        # Load participants.tsv for subject info.
        participants_df = _load_participants_tsv(dataset_path)
        subject_info = _extract_subject_info(row, participants_df)

        # Update eegunity_description.
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DEVICE_INFO["amplifier"],
                "cap": _DEVICE_INFO["cap"],
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 1020 if they are non-standard.
        # Source: standard_1020 + extended 64-channel cap.
        # Annotator: LLM, 2026-04-08
        rename_map = {}
        ch_names = raw.ch_names
        eeg_channels = [c for c in ch_names if c.startswith("EEG")]

        for i, ch in enumerate(eeg_channels):
            if i < len(_64CH_CHANNEL_NAMES):
                rename_map[ch] = _64CH_CHANNEL_NAMES[i]

        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage if all channels match standard names.
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            present_channels = [c for c in raw.ch_names if c in montage.ch_names]
            if len(present_channels) >= 20:
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass

        # Detect and set annotations (events).
        annotations = _detect_events(raw)
        raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS005416Kernel()