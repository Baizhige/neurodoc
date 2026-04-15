"""Stage1 kernel for openneuro_ds003518.

Simon Conflict Task with Reinforcement and Cabergoline Challenge.
64-channel EEG, 500 Hz, BIDS format.

Source: https://openneuro.org/datasets/ds003518
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

import mne
import numpy as np

# Add parent directory to path for base kernel imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from kernels.openneuro_specific._base import OpenNeuroBaseKernel
    _HAS_BASE_KERNEL = True
except ImportError:
    _HAS_BASE_KERNEL = False

# Dataset-specific constants
_DATASET_ID = "openneuro_ds003518"
_SFREQ = 500.0

# Standard 64-channel EEG names (10-20 system extended)
# Source: standard_1020 montage - 64-channel extended cap
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2"
]

# Common alias patterns for BrainVision / EGI style recordings
_ALIAS_GROUPS = [
    ("Fp1", ["Fp1", "EEG Fp1", "EEG-Fp1"]),
    ("Fpz", ["Fpz", "EEG Fpz", "EEG-Fpz"]),
    ("Fp2", ["Fp2", "EEG Fp2", "EEG-Fp2"]),
    ("F7", ["F7", "EEG F7", "EEG-F7"]),
    ("F3", ["F3", "EEG F3", "EEG-F3"]),
    ("Fz", ["Fz", "EEG Fz", "EEG-Fz"]),
    ("F4", ["F4", "EEG F4", "EEG-F4"]),
    ("F8", ["F8", "EEG F8", "EEG-F8"]),
    ("T7", ["T7", "T7 (T8)", "EEG T7", "EEG-T7", "T7"]),
    ("C3", ["C3", "EEG C3", "EEG-C3"]),
    ("Cz", ["Cz", "EEG Cz", "EEG-Cz"]),
    ("C4", ["C4", "EEG C4", "EEG-C4"]),
    ("T8", ["T8", "EEG T8", "EEG-T8", "T8 (T7)"]),
    ("P7", ["P7", "P7 (P8)", "EEG P7", "EEG-P7", "P7"]),
    ("P3", ["P3", "EEG P3", "EEG-P3"]),
    ("Pz", ["Pz", "EEG Pz", "EEG-Pz"]),
    ("P4", ["P4", "EEG P4", "EEG-P4"]),
    ("P8", ["P8", "P8 (P7)", "EEG P8", "EEG-P8", "P8"]),
    ("O1", ["O1", "EEG O1", "EEG-O1"]),
    ("Oz", ["Oz", "EEG Oz", "EEG-Oz"]),
    ("O2", ["O2", "EEG O2", "EEG-O2"]),
]

# Event mapping from raw numeric codes to human-readable labels
# Source: analysis.md event structure table
_EVENT_ID_MAP = {
    "Trn Stim": "Trn Stim",
    "Test Stim": "Test Stim",
    "correct": "correct",
    "incorrect": "incorrect",
    "Trn Resp": "Trn Resp",
    "Test Resp": "Test Resp",
    "FB": "FB",
    "Trn No Response": "Trn No Response",
    "Test No Response": "Test No Response",
    "STATUS": "STATUS",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map based on existing channel names.

    Handles common alias patterns found in EEG recordings.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in _ALIAS_GROUPS:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    # Handle numbered EEG channels (e.g., EEG-0 -> standard name)
    # Common pattern: EEG-0, EEG-1, ... or simply numeric strings
    numeric_pattern_channels = []
    for ch in raw.ch_names:
        if ch.startswith("EEG-") and ch[4:].isdigit():
            numeric_pattern_channels.append(ch)
        elif ch.startswith("EEG 0") and ch[4:].replace(" ", "").isdigit():
            numeric_pattern_channels.append(ch)

    # Map based on position if we have 64 channels with numeric names
    if len(numeric_pattern_channels) >= 60:
        numeric_pattern_channels.sort()
        for i, old_name in enumerate(numeric_pattern_channels):
            if i < len(_STANDARD_64_CHANNELS):
                new_name = _STANDARD_64_CHANNELS[i]
                if old_name != new_name:
                    rename_map[old_name] = new_name

    return rename_map


def _set_standard_montage(raw: mne.io.BaseRaw) -> bool:
    """Attempt to set standard 10-20 montage.

    Returns True if successful, False if skipped.
    """
    try:
        # Try standard_1020 first (covers most EEG caps)
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="warn")
        return True
    except Exception:
        # Fallback: try to set only the channels that match
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Keep only channels that exist in both raw and montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 20:
                raw.set_montage(montage, on_missing="ignore")
                return True
        except Exception:
            pass
    return False


class OpenNeuroDS003518Kernel:
    """Stage1 kernel for openneuro_ds003518 (Simon Conflict Task)."""

    KERNEL_ID: str = "openneuro-ds003518-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (in-memory)
        row : Locator row with file metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels and events
        """
        # Store original description
        original_description = raw.info.get("description", "")

        # Step 1: Rename channels to standard names (BEFORE set_montage)
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw, rename_map)

        # Step 2: Set standard montage
        _set_standard_montage(raw)

        # Step 3: Ensure all EEG channels have correct type
        eeg_channels = [ch for ch in raw.ch_names if ch not in raw.info["bads"]]
        eeg_types = ["eeg"] * len(eeg_channels)
        try:
            raw.set_channel_types({ch: "eeg" for ch in eeg_channels if ch not in raw.info.get("custom_ref_applied", []) and ch not in raw.info.get(" projectors", [])})
        except Exception:
            pass  # Keep original types if set_channel_types fails

        # Step 4: Handle events from annotations or stim channel
        # The dataset uses BIDS format with events.tsv, which MNE reads as annotations
        if raw.annotations is None or len(raw.annotations) == 0:
            # Try to read events from stim channel if present
            stim_channels = [ch for ch in raw.ch_names if "stim" in ch.lower() or "trigger" in ch.lower()]
            if stim_channels:
                stim_data, stim_times = raw[stim_channels[0], :]
                # Extract events from threshold crossing
                threshold = np.mean(stim_data) + 2 * np.std(stim_data)
                event_mask = stim_data.flatten() > threshold
                event_indices = np.where(np.diff(event_mask.astype(int)) > 0)[0]
                if len(event_indices) > 0:
                    event_onsets = stim_times[event_indices]
                    event_descriptions = ["STATUS"] * len(event_onsets)  # Default label
                    new_annotations = mne.Annotations(
                        onset=event_onsets,
                        duration=[0.0] * len(event_onsets),
                        description=event_descriptions,
                    )
                    raw.set_annotations(new_annotations)

        # Step 5: Standardize annotation descriptions
        if raw.annotations is not None and len(raw.annotations) > 0:
            standardized_descriptions = []
            for desc in raw.annotations.description:
                # Map to canonical event labels
                standardized = _EVENT_ID_MAP.get(desc, desc)
                standardized_descriptions.append(standardized)
            raw.annotations.description = standardized_descriptions

        # Step 6: Build eegunity_description
        # All values from external sources must be marked
        # Per analysis.md: subject_age and subject_sex are missing (unknown)
        # Source: analysis.md Info table - "Completeness: missing"
        eegunity_description = {
            "age": "unknown",  # LLM 推断，需人类复核 - no age info in dataset metadata
            "sex": "unknown",  # LLM 推断，需人类复核 - no sex info in dataset metadata
            "amplifier": "unknown",  # LLM 推断，需人类复核 - no device info in metadata
            "cap": "unknown",  # LLM 推断，需人类复核 - cap type not specified
            "handedness": "unknown",  # LLM 推断，需人类复核 - no handedness info
        }

        description_dict = {
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


# Module-level kernel instance
KERNEL = OpenNeuroDS003518Kernel()