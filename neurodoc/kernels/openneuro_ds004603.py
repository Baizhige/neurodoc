"""OpenNeuro DS004603 stage1 kernel for EEGUnity.

Visual Attribute-Specific Contextual Trajectory Paradigm.
37 subjects, 65 channels, 1024 Hz sampling rate.

Source: https://openneuro.org/datasets/ds004603
Paper DOI: 10.1016/j.cortex.2023.08.004
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import mne


# Event code mapping from raw Stimulus/S codes to canonical event labels.
# Source: Dataset event codes observed in raw data + analysis.md event table.
# Annotator: LLM, 2026-04-08
_EVENT_CODE_MAP: Dict[int, str] = {
    1: "step_1",
    2: "step_2",
    3: "step_3",
    4: "step_4",
    10: "col_vio",
    20: "siz_vio",
    30: "ori_vio",
    40: "control",
    50: "catch",
    255: "initalising_triggers",
}

# Canonical event IDs used by EEGUnity tasks.
# These are consistent with analysis.md Event Structure table.
_EVENT_ID: Dict[str, int] = {
    "step_1": 1,
    "step_2": 2,
    "step_3": 3,
    "step_4": 4,
    "col_vio": 10,
    "siz_vio": 20,
    "ori_vio": 30,
    "control": 40,
    "catch": 50,
    "initalising_triggers": 255,
}


def _apply_channel_standardization(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename non-standard channel names to standard 10-20 names.
    
    The dataset uses BrainVision format with channels like 'EEG 001', 'EEG 002', etc.
    This function maps them to standard 10-20 electrode nomenclature.
    
    Source: Standard 10-20 cap layout for 64-channel system (extended).
    Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
    """
    ch_names = raw.ch_names
    
    # Standard 64-channel layout (extended 10-20 system)
    # Order follows BrainVision typical convention
    standard_layout_64 = [
        "Fp1", "Fpz", "Fp2",
        "F7", "F3", "Fz", "F4", "F8",
        "FC5", "FC1", "FCz", "FC2", "FC6",
        "M1", "T7", "C3", "Cz", "C4", "T8", "M2",
        "CP5", "CP1", "CPz", "CP2", "CP6",
        "P7", "P3", "Pz", "P4", "P8",
        "POz",
        "O1", "Oz", "O2",
        "F5", "F1", "F2", "F6",
        "FC3", "FCz", "FC4",
        "C5", "C1", "C2", "C6",
        "CP3", "CPz", "CP4",
        "P5", "P1", "P2", "P6",
        "PO3", "PO4",
        "F9", "F10",
        "FT9", "FT10",
        "TP9", "TP10",
        "P9", "P10",
        "AF7", "AFz", "AF8",
        "PO9", "PO10",
    ]
    
    # Detect EEG channel pattern (e.g., 'EEG 001', 'EEG001', 'E 001')
    eeg_channels = []
    other_channels = []
    
    for ch in ch_names:
        # Check for EEG channel patterns
        if ch.startswith("EEG") or ch.startswith("E ") or ch.startswith("EEG "):
            eeg_channels.append(ch)
        elif ch in ["M1", "M2", "TP9", "TP10", "A1", "A2"]:
            # Already standard reference/mastoid
            other_channels.append(ch)
        elif ch.startswith("EOG") or ch.startswith("ECG") or ch.startswith("EMG"):
            other_channels.append(ch)
        elif ch in standard_layout_64:
            other_channels.append(ch)
        else:
            other_channels.append(ch)
    
    # Build rename map only if we have numbered EEG channels
    rename_map: Dict[str, str] = {}
    
    if len(eeg_channels) >= 60:
        # Sort by numeric suffix to ensure correct mapping
        def extract_number(name: str) -> int:
            import re
            match = re.search(r"\d+", name)
            return int(match.group()) if match else 0
        
        eeg_channels_sorted = sorted(eeg_channels, key=extract_number)
        
        # Map to standard layout (take first N channels)
        for i, old_name in enumerate(eeg_channels_sorted):
            if i < len(standard_layout_64):
                new_name = standard_layout_64[i]
                if old_name != new_name:
                    rename_map[old_name] = new_name
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _build_annotations_from_stim_channel(
    raw: mne.io.BaseRaw,
) -> mne.io.BaseRaw:
    """Extract events from STIM channel and convert to MNE annotations.
    
    BrainVision format typically uses a Stimulus channel for event markers.
    The events are encoded as integer values that map to semantic meanings.
    """
    # Find stimulus channel
    stim_channel = None
    for ch in raw.ch_names:
        if "stim" in ch.lower() or ch.startswith("STI"):
            stim_channel = ch
            break
    
    if stim_channel is None:
        # No explicit stim channel found - events may already be in annotations
        return raw
    
    # Get events from stim channel using MNE's find_events or get_data approach
    stim_data = raw.get_data(picks=[stim_channel])[0]
    
    # Find samples where stimulus value changes
    diff = np.diff(stim_data)
    event_indices = np.where(diff != 0)[0] + 1  # +1 because diff shifts indices
    
    # Get unique values at event points
    event_values = stim_data[event_indices]
    
    # Convert sample indices to onset times (in seconds)
    sfreq = raw.info["sfreq"]
    onsets = event_indices / sfreq
    
    # Map event codes to labels
    descriptions = []
    for val in event_values:
        val_int = int(val)
        if val_int in _EVENT_CODE_MAP:
            descriptions.append(_EVENT_CODE_MAP[val_int])
        else:
            descriptions.append(f"unknown_{val_int}")
    
    # Create annotations with 0 duration (point events)
    annotations = mne.Annotations(
        onset=onsets.tolist(),
        duration=[0.0] * len(onsets),
        description=descriptions,
    )
    
    raw.set_annotations(annotations)
    
    return raw


class OpenNeuroDS004603Kernel:
    """Stage1 kernel for OpenNeuro DS004603 (Visual Trajectory Paradigm)."""

    KERNEL_ID: str = "openneuro-ds004603-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized events and metadata.
        """
        # Store original description
        original_description = raw.info.get("description", "")

        # Standardize channel names before setting montage
        raw = _apply_channel_standardization(raw)

        # Try to set standard 10-20 montage (64-channel extended system)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # For 64+ channels, use extended 10-20
            if len(raw.ch_names) > 32:
                # Keep only channels that exist in the data
                common_channels = [ch for ch in montage.ch_names if ch in raw.ch_names]
                if len(common_channels) > 20:  # Only apply if we have good coverage
                    raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # Montage setting is optional; continue if it fails
            pass

        # Extract events from stim channel and create annotations
        raw = _build_annotations_from_stim_channel(raw)

        # Write eegunity_description
        # All fields default to "unknown" since dataset lacks subject metadata.
        # Source: analysis.md - Info table shows age/sex/device as "missing".
        # Annotator: LLM, 2026-04-08  # inferred by LLM, needs human review
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": "unknown",       # inferred by LLM, needs human review
                "sex": "unknown",       # inferred by LLM, needs human review
                "amplifier": "unknown", # inferred by LLM, needs human review
                "cap": "unknown",       # inferred by LLM, needs human review
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


# Module-level kernel instance for EEGUnity loading
KERNEL = OpenNeuroDS004603Kernel()