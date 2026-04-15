"""OpenNeuro DS002722 stage1 kernel for EEGUnity.

Affective Brain-Computer Music Interface (BCMI) calibration dataset.
EEG and physiological recordings from 19 participants listening to
40-second synthetic music clips with 9 affective conditions.

Source: https://openneuro.org/datasets/ds002722
DOI: 10.1038/s41597-020-0507-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Subject Information
# ============================================================================
# Source: participants.tsv in the BIDS dataset
# Annotator: Human, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Populated dynamically from participants.tsv in apply()


# ============================================================================
# Channel Rename Map
# ============================================================================
# The dataset uses BrainVision format with channel names like 'EEG 001', 'EEG 002', etc.
# plus physiological channels (ECG, GSR, Resp, etc.)
# Source: Paper 10.1038/s41597-020-0507-6, Table 1 - 32-channel EEG cap layout
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG 001": "FC5",
    "EEG 002": "FC3",
    "EEG 003": "FC1",
    "EEG 004": "Fz",
    "EEG 005": "FC2",
    "EEG 006": "FC4",
    "EEG 007": "FC6",
    "EEG 008": "C5",
    "EEG 009": "C3",
    "EEG 010": "C1",
    "EEG 011": "Cz",
    "EEG 012": "C2",
    "EEG 013": "C4",
    "EEG 014": "C6",
    "EEG 015": "CP5",
    "EEG 016": "CP3",
    "EEG 017": "CP1",
    "EEG 018": "CPz",
    "EEG 019": "CP2",
    "EEG 020": "CP4",
    "EEG 021": "CP6",
    "EEG 022": "FP1",
    "EEG 023": "FP2",
    "EEG 024": "F7",
    "EEG 025": "F3",
    "EEG 026": "F4",
    "EEG 027": "F8",
    "EEG 028": "T7",
    "EEG 029": "T8",
    "EEG 030": "P7",
    "EEG 031": "P3",
    "EEG 032": "Pz",
    "EEG 033": "P4",
    "EEG 034": "P8",
    "EEG 035": "O1",
    "EEG 036": "Oz",
    "EEG 037": "O2",
}

# Physiological channel names (keep as-is or rename to standard types)
_PHYSIOLOGICAL_CHANNELS = {
    "ECG": "ecg",
    "GSR": "gsr",
    "Resp": "resp",
    "Plethysmograph": "pleth",
}


# ============================================================================
# Event Mapping
# ============================================================================
# Events 1-9 are the 9 affective music conditions (40-second clips)
# Events 100-200 are specific music clip identifiers (used for reference, not classification)
_EVENT_MAP: Dict[int, str] = {
    1: "Music Condition 1",
    2: "Music Condition 2",
    3: "Music Condition 3",
    4: "Music Condition 4",
    5: "Music Condition 5",
    6: "Music Condition 6",
    7: "Music Condition 7",
    8: "Music Condition 8",
    9: "Music Condition 9",
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv from the BIDS dataset."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        df = pd.read_csv(participants_path, sep="\t")
        return df
    return pd.DataFrame()


def _get_subject_info(participant_id: str, dataset_path: str) -> Dict[str, str]:
    """Get subject metadata from participants.tsv or return defaults."""
    subject_id = participant_id.replace("sub-", "")

    # Try to load from participants.tsv
    df = _load_participants_tsv(dataset_path)
    if not df.empty and "participant_id" in df.columns:
        match = df[df["participant_id"] == participant_id]
        if not match.empty:
            row = match.iloc[0]
            age = str(int(row.get("age", "unknown"))) if pd.notna(row.get("age")) else "unknown"
            sex = str(row.get("sex", "unknown")).lower()
            if sex not in ["male", "female"]:
                sex = "unknown"
            return {"age": age, "sex": sex}

    return {"age": "unknown", "sex": "unknown"}


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename EEG channels to standard 10-20 names and set physiological types."""
    rename_map = {}
    set_types = {}

    for ch_name in raw.ch_names:
        # EEG channels
        if ch_name in _EEG_CHANNEL_RENAME_MAP:
            rename_map[ch_name] = _EEG_CHANNEL_RENAME_MAP[ch_name]

        # Physiological channels
        if ch_name in _PHYSIOLOGICAL_CHANNELS:
            set_types[ch_name] = _PHYSIOLOGICAL_CHANNELS[ch_name]

    # Apply channel renames
    if rename_map:
        # Only rename channels that exist in this specific file
        actual_rename_map = {k: v for k, v in rename_map.items() if k in raw.ch_names}
        if actual_rename_map:
            raw.rename_channels(actual_rename_map)

    # Set channel types for physiological channels
    if set_types:
        actual_types = {k: v for k, v in set_types.items() if k in raw.ch_names}
        if actual_types:
            try:
                raw.set_channel_types(actual_types)
            except Exception:
                pass  # Some channels may not support type changes

    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage if all EEG channels are recognized."""
    try:
        # Get standard 10-20 montage
        montage = mne.channels.make_standard_montage("standard_1020")

        # Check which channels from the montage are present in the data
        eeg_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]

        if len(eeg_channels) >= 20:  # Only set montage if we have enough channels
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Montage setting is optional

    return raw


def _process_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Process events/annotations from the BrainVision format.

    The dataset stores events as marker channels in BrainVision format.
    Events 1-9 are the primary condition markers.
    Events 100-200 are specific music clip identifiers.
    """
    # BrainVision format typically stores events in annotations
    # If annotations exist, process them
    if raw.annotations is not None and len(raw.annotations) > 0:
        descriptions = []
        for desc in raw.annotations.description:
            # Try to extract numeric code from description
            try:
                code = int(float(desc))
                if 1 <= code <= 9:
                    descriptions.append(_EVENT_MAP[code])
                else:
                    descriptions.append(f"marker-{code}")
            except (ValueError, TypeError):
                descriptions.append(str(desc))

        # Update annotations with readable labels
        new_annotations = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annotations)

    return raw


class OpenNeuroDS002722Kernel:
    """Stage1 kernel for OpenNeuro DS002722 (Affective BCMI Calibration)."""

    KERNEL_ID: str = "openneuro-ds002722-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object loaded from BrainVision files.
        row
            Locator row with File Path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata.
        """
        # Get file path to find dataset root for participants.tsv
        file_path = row.get("File Path", "")
        dataset_path = os.path.dirname(os.path.dirname(file_path))

        # Get subject information
        subject_id = row.get("participant_id", "sub-01")
        subject_info = _get_subject_info(subject_id, dataset_path)

        # Process channel names BEFORE set_montage
        raw = _rename_channels(raw)

        # Set montage for spatial information
        raw = _set_montage_if_possible(raw)

        # Process events
        raw = _process_events(raw)

        # Update description with eegunity_description
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainAmp",  # Source: Paper 10.1038/s41597-020-0507-6  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # Source: Standard EEG cap assumption  # LLM 推断，需人类复核
                "handedness": "unknown",  # Not provided in dataset metadata  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS002722Kernel()