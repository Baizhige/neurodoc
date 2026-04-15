"""OpenNeuro ds004315 stage1 kernel for EEGUnity.

Mood Manipulation and PST (Probabilistic Selection Task), Experiment 1.
50 subjects, 66 channels, 500 Hz sampling rate.
BIDS-format dataset with MISC trigger channel for events.

Source: https://openneuro.org/datasets/ds004315
Reference: DOI 10.1111/psyp.14276
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Information
# =============================================================================
# Source: OpenNeuro ds004315 participants.tsv
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Note: participants.tsv exists in BIDS dataset; age/sex will be loaded dynamically
    # from participants.tsv if available. Fallback values below for safety.
}
# LLM 推断，需人类复核

# =============================================================================
# Device Metadata
# =============================================================================
# Source: OpenNeuro ds004315 dataset_description.json and common practices
# Annotator: LLM, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "BrainAmp",  # LLM 推断，需人类复核 - typical for BrainVision format on OpenNeuro
    "cap": "Ag/AgCl",  # LLM 推断，需人类复核
}
# LLM 推断，需人类复核

# =============================================================================
# Channel Mapping
# =============================================================================
# Source: Standard 10-20 system; 66-channel cap typical for this dataset
# Annotator: LLM, 2026-04-08
_EEG_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    # Additional 10-20 positions for 66-channel cap
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC5", "FC1", "FC2", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP1", "CP2", "CP6",
    "P5", "P1", "P2", "P6",
    "PO5", "PO1", "PO2", "PO6",
    "O9", "O10",
]
# LLM 推断，需人类复核


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.

    This dataset uses BrainVision format with potentially numbered channels
    like 'EEG 001', 'EEG 002', etc. that need mapping to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common patterns for BrainVision/Edinburgh channels
    eeg_patterns = [
        # Pattern: EEG 001 -> Fp1, EEG 002 -> F3, etc.
    ]

    # Try to match numbered EEG channels to standard positions
    for i, ch_name in enumerate(raw.ch_names):
        if ch_name.startswith("EEG ") or ch_name.startswith("EEG-"):
            try:
                # Extract number from "EEG 001" or "EEG-001"
                num = int(ch_name.replace("EEG ", "").replace("EEG-", ""))
                # Map to standard 10-20 position based on typical 66-channel layout
                if num - 1 < len(_EEG_1020_CHANNELS):
                    target = _EEG_1020_CHANNELS[num - 1]
                    if target in existing_names:
                        rename_map[ch_name] = f"{target}_dup{num}"
                    else:
                        rename_map[ch_name] = target
            except ValueError:
                pass

    return rename_map


def _detect_events_from_misc(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Detect events from MISC trigger channel.

    The dataset uses a MISC 'stim' channel for trigger signals.
    Events: STIM, RESP, FB, Correct, Incorrect, TESTING, STATUS
    """
    # Find MISC/stim channel by name first
    stim_ch = None
    for ch in raw.ch_names:
        if "stim" in ch.lower() or ch.lower() in ["stim", "trigger", "status"]:
            stim_ch = ch
            break

    if stim_ch is None:
        # Try to find by channel type using get_channel_types
        ch_types = raw.get_channel_types()
        for i, ch_type in enumerate(ch_types):
            if ch_type == "stim":
                stim_ch = raw.ch_names[i]
                break

    if stim_ch is None:
        return mne.Annotations(onset=[], duration=[], description=[])

    # Get data from stim channel
    stim_data, times = raw[stim_ch, :]
    stim_data = stim_data.flatten()

    # Find transitions (rising/falling edges)
    diff = np.diff(stim_data)
    onsets = np.where(np.abs(diff) > 0)[0] / raw.info["sfreq"]

    # Map trigger values to event names
    # Typical trigger values: 1=STIM, 2=RESP, 3=FB, 4=Correct, 5=Incorrect, etc.
    event_map = {
        1: "STIM",
        2: "RESP",
        3: "FB",
        4: "Correct",
        5: "Incorrect",
        6: "TESTING",
        7: "STATUS",  # admin marker
    }

    descriptions = []
    for idx in np.where(np.abs(diff) > 0)[0]:
        val = int(stim_data[idx])
        desc = event_map.get(val, f"trigger-{val}")
        descriptions.append(desc)

    return mne.Annotations(
        onset=onsets.tolist(),
        duration=[0.0] * len(onsets),
        description=descriptions,
    )


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject information from BIDS participants.tsv."""
    participants_file = os.path.join(dataset_path, "participants.tsv")

    if not os.path.exists(participants_file):
        return {}

    try:
        df = pd.read_csv(participants_file, sep="\t")
        subject_info = {}

        for _, row in df.iterrows():
            # Extract subject ID (e.g., "sub-01" -> "sub-01")
            subject_id = row.get("participant_id", "")
            if not subject_id or not isinstance(subject_id, str):
                continue

            # Map age
            age = str(row.get("age", "unknown"))
            if pd.isna(row.get("age")) or age == "nan":
                age = "unknown"

            # Map sex (ensure lowercase)
            sex = str(row.get("sex", "unknown")).lower()
            if pd.isna(row.get("sex")) or sex == "nan":
                sex = "unknown"
            if sex not in ["male", "female"]:
                sex = "unknown"

            # Handedness if available
            handedness = str(row.get("handedness", "unknown")).lower()
            if pd.isna(row.get("handedness")) or handedness == "nan":
                handedness = "unknown"

            subject_info[subject_id] = {
                "age": age,
                "sex": sex,
                "handedness": handedness,
            }

        return subject_info
    except Exception:
        return {}


class OpenNeuroDS004315Kernel:
    """Stage1 kernel for OpenNeuro ds004315 dataset."""

    KERNEL_ID: str = "openneuro-ds004315-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path`` and
            ``Subject ID``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        # Extract paths
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", "unknown")

        # Determine dataset path for participants.tsv
        dataset_path = ""
        if file_path:
            # Navigate from file path to dataset root
            parts = file_path.split(os.sep)
            for i in range(len(parts), 0, -1):
                test_path = os.sep.join(parts[:i])
                desc_file = os.path.join(test_path, "dataset_description.json")
                if os.path.exists(desc_file):
                    dataset_path = test_path
                    break

        # =========================================================================
        # 1. Rename channels to standard 10-20 names
        # =========================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # =========================================================================
        # 2. Set channel types (EEG, EOG, ECG, etc.)
        # =========================================================================
        # Mark EOG/ECG channels if found
        eog_channels = [ch for ch in raw.ch_names if ch.startswith("EOG")]
        if eog_channels:
            raw.set_channel_types({ch: "eog" for ch in eog_channels})

        # =========================================================================
        # 3. Detect and add events from MISC trigger channel
        # =========================================================================
        misc_annotations = _detect_events_from_misc(raw)
        if misc_annotations.onset:
            existing_annotations = raw.annotations if raw.annotations else mne.Annotations([], [], [])
            combined_annotations = mne.Annotations(
                onset=list(existing_annotations.onset) + list(misc_annotations.onset),
                duration=list(existing_annotations.duration) + list(misc_annotations.duration),
                description=list(existing_annotations.description) + list(misc_annotations.description),
            )
            raw.set_annotations(combined_annotations)

        # =========================================================================
        # 4. Load subject metadata from participants.tsv
        # =========================================================================
        subject_info = _load_participants_tsv(dataset_path)

        # Get subject info from participants.tsv or use fallback
        info = subject_info.get(subject_id, {})
        age = info.get("age", "unknown")
        sex = info.get("sex", "unknown")
        handedness = info.get("handedness", "unknown")

        # =========================================================================
        # 5. Store EEGUnity metadata in raw.info['temp']
        # =========================================================================
        eegunity_description: Dict[str, Any] = {
            "age": str(age),
            "sex": str(sex),
            "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
            "cap": _DEVICE_INFO.get("cap", "unknown"),
            "handedness": str(handedness),
        }
        raw.info["temp"] = eegunity_description

        return raw


KERNEL = OpenNeuroDS004315Kernel()