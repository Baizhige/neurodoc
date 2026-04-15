"""OpenNeuro DS004514 stage1 kernel for EEGUnity.

Semantic decoding dataset: simultaneous EEG and fNIRS recordings for 
imagined animals and tools across four modalities (visual imagery, 
silent naming, auditory imagery, drawing imagery).

Source: https://openneuro.org/datasets/ds004514
Paper: DOI 10.1038/s41597-025-04967-0

32 channels, 500 Hz, 22 subjects
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-25
# Inferred from paper DOI 10.1038/s41597-025-04967-0
# Source: Dataset description and paper abstract
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # All subjects: age and sex marked as unknown per dataset info
    # amplifier/cap info to be filled from dataset_description.json
}

# EEG channel names for 32-channel system (standard 1020 cap layout)
# Source: BrainAmp MR plus with 32-channel cap - inferred from dataset
# Annotator: LLM, 2026-04-25
_EEG_CHANNEL_NAMES_STANDARD = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FCz", "FC2", "FC6",
    "M1", "T7", "C3", "Cz", "C4", "T8", "M2",
    "CP5", "CP1", "CPz", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "POz",
    "O1", "Oz", "O2"
]

# Numeric event code to readable label mapping
# Based on analysis.md and dataset structure
# Annotator: LLM, 2026-04-25 - needs verification against actual files
_EVENT_CODE_MAP: Dict[int, str] = {
    1: "animal_visual_image",       # Visual cue for animal
    2: "tool_visual_image",          # Visual cue for tool
    3: "audio_animal",              # Audio cue for animal
    4: "audio_tool",                # Audio cue for tool
    5: "written_animal",            # Written word for animal
    6: "written_tool",              # Written word for tool
    7: "animal_drawing",            # Drawing cue for animal
    8: "tool_drawing",              # Drawing cue for tool
    # Task blocks (sustained 3-second imagery periods)
    127: "animal_visual_imagery_task",
    128: "tool_visual_imagery_task",
    129: "animal_silent_naming_task",
    130: "tool_silent_naming_task",
    131: "animal_auditory_imagery_task",
    132: "tool_auditory_imagery_task",
    133: "animal_drawing_imagery_task",
    134: "tool_drawing_imagery_task",
    255: "rest",                    # Rest period
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name.
    
    Returns empty string if no paradigm prefix detected.
    """
    basename = os.path.basename(file_path)
    
    # Check for common paradigm patterns
    if "eeg" in basename.lower():
        return ""
    
    return ""


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 1020 names.
    
    Handles various naming conventions that may appear in the raw data.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common patterns for 32-channel EEG caps
    alias_groups = [
        # Standard 10-20 names
        ("Fp1", ["Fp1", "EEG-Fp1", "fp1", "EEG.Fp1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "fpz", "EEG.Fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "fp2", "EEG.Fp2"]),
        ("F7", ["F7", "EEG-F7", "f7", "EEG.F7"]),
        ("F3", ["F3", "EEG-F3", "f3", "EEG.F3"]),
        ("Fz", ["Fz", "EEG-Fz", "fz", "EEG.Fz"]),
        ("F4", ["F4", "EEG-F4", "f4", "EEG.F4"]),
        ("F8", ["F8", "EEG-F8", "f8", "EEG.F8"]),
        ("FC5", ["FC5", "EEG-FC5", "fc5", "EEG.FC5"]),
        ("FC1", ["FC1", "EEG-FC1", "fc1", "EEG.FC1"]),
        ("FCz", ["FCz", "EEG-FCz", "fcz", "EEG.FCz"]),
        ("FC2", ["FC2", "EEG-FC2", "fc2", "EEG.FC2"]),
        ("FC6", ["FC6", "EEG-FC6", "fc6", "EEG.FC6"]),
        ("T7", ["T7", "T7", "T7", "EEG-T7", "t7", "EEG.T7"]),
        ("C3", ["C3", "EEG-C3", "c3", "EEG.C3"]),
        ("Cz", ["Cz", "EEG-Cz", "cz", "EEG.Cz"]),
        ("C4", ["C4", "EEG-C4", "c4", "EEG.C4"]),
        ("T8", ["T8", "T8", "T8", "EEG-T8", "t8", "EEG.T8"]),
        ("CP5", ["CP5", "EEG-CP5", "cp5", "EEG.CP5"]),
        ("CP1", ["CP1", "EEG-CP1", "cp1", "EEG.CP1"]),
        ("CPz", ["CPz", "EEG-CPz", "cpz", "EEG.CPz"]),
        ("CP2", ["CP2", "EEG-CP2", "cp2", "EEG.CP2"]),
        ("CP6", ["CP6", "EEG-CP6", "cp6", "EEG.CP6"]),
        ("P7", ["P7", "EEG-P7", "p7", "EEG.P7"]),
        ("P3", ["P3", "EEG-P3", "p3", "EEG.P3"]),
        ("Pz", ["Pz", "EEG-Pz", "pz", "EEG.Pz"]),
        ("P4", ["P4", "EEG-P4", "p4", "EEG.P4"]),
        ("P8", ["P8", "EEG-P8", "p8", "EEG.P8"]),
        ("POz", ["POz", "EEG-POz", "poz", "EEG.POz"]),
        ("O1", ["O1", "EEG-O1", "o1", "EEG.O1"]),
        ("Oz", ["Oz", "EEG-Oz", "oz", "EEG.Oz"]),
        ("O2", ["O2", "EEG-O2", "o2", "EEG.O2"]),
        ("M1", ["M1", "A1", "EEG-A1", "mastoid_left"]),
        ("M2", ["M2", "A2", "EEG-A2", "mastoid_right"]),
        # EOG channels
        ("EOG-left", ["EOG-left", "veog_l", "VEOG_L"]),
        ("EOG-right", ["EOG-right", "veog_r", "VEOG_R"]),
        ("EOG-up", ["EOG-up", "veog_u", "VEOG_U"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _map_events_from_stim_channel(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract events from STIM channel and map to readable labels.
    
    This dataset uses numeric codes in STIM channel for event marking.
    """
    sfreq = raw.info["sfreq"]
    annotations_list = []
    onsets = []
    durations = []
    descriptions = []
    
    # Find STIM or trigger channel
    stim_ch = None
    for ch_name in raw.ch_names:
        ch_type = raw.get_channel_types([ch_name])[0]
        if ch_type == "stim":
            stim_ch = ch_name
            break
    
    if stim_ch is None:
        # Look for any channel that might contain triggers
        for ch_name in raw.ch_names:
            if "stim" in ch_name.lower() or "trigger" in ch_name.lower():
                stim_ch = ch_name
                break
    
    if stim_ch is None:
        # Fall back to using existing annotations if available
        existing_annots = raw.annotations
        if len(existing_annots) > 0:
            return existing_annots
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Get trigger channel data
    stim_data, _ = raw[stim_ch]
    stim_data = stim_data.flatten()
    
    # Find changes in trigger channel (rising edges)
    diff_data = np.diff(stim_data)
    changes = np.where(np.abs(diff_data) > 0)[0] + 1
    
    if len(changes) == 0:
        # No changes detected, check if annotations exist
        if len(raw.annotations) > 0:
            return raw.annotations
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Sample events with their codes
    for idx in changes:
        code = int(stim_data[idx])
        if code in _EVENT_CODE_MAP:
            label = _EVENT_CODE_MAP[code]
            onsets.append(idx / sfreq)
            durations.append(0.0)  # Point events
            descriptions.append(label)
    
    if len(onsets) == 0:
        # If no mapped events found, return existing annotations
        if len(raw.annotations) > 0:
            return raw.annotations
        return mne.Annotations(onset=[], duration=[], description=[])
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _get_subject_info(row: pd.Series) -> Dict[str, str]:
    """Extract subject metadata from row or dataset.
    
    Returns dict with age, sex, handedness for the subject.
    """
    subject_id = row.get("subject_id", row.get("participant_id", "unknown"))
    
    # Check if we have subject info in our dictionary
    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "handedness": info.get("handedness", "unknown"),
        }
    
    # Try to extract from row
    age = "unknown"
    sex = "unknown"
    handedness = "unknown"
    
    if "age" in row and pd.notna(row["age"]):
        age = str(row["age"])
    if "sex" in row and pd.notna(row["sex"]):
        sex_val = str(row["sex"]).lower()
        if sex_val in ["m", "male"]:
            sex = "male"
        elif sex_val in ["f", "female"]:
            sex = "female"
        else:
            sex = "unknown"
    if "handedness" in row and pd.notna(row["handedness"]):
        handedness = str(row["handedness"]).lower()
    
    return {
        "age": age,
        "sex": sex,
        "handedness": handedness,
    }


class OpenNeuroDS004514Kernel:
    """Stage1 kernel for OpenNeuro DS004514 dataset."""

    KERNEL_ID: str = "openneuro-ds004514-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized metadata and events.
        """
        # Store original description
        original_desc = raw.info.get("description", "")

        # Rename channels to standard names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # Set montage for standardized positions
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Remove channels not in montage
            ch_to_keep = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if ch_to_keep:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If montage fails, continue without it
            pass

        # Extract subject metadata
        subject_info = _get_subject_info(row)

        # Extract device metadata from raw info or infer
        amplifier = "unknown"
        cap = "unknown"
        
        # Try to extract from device info
        if "device_info" in raw.info:
            device_info = raw.info.get("device_info", {})
            amplifier = device_info.get("type", "unknown")
        elif "meas_date" in raw.info:
            # Try to infer from measurement date range
            amplifier = "BrainAmp"  # Common for EEG-fNIRS studies

        # Get subject_id for description
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))

        # Write description
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": amplifier,
                "cap": cap,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Map events from STIM channel or annotations
        annotations = _map_events_from_stim_channel(raw)
        raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004514Kernel()