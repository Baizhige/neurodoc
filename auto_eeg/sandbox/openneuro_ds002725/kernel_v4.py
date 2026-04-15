"""OpenNeuro DS002725 stage1 kernel for EEGUnity.

Joint EEG-fMRI dataset during affective music listening.
21 subjects, 47 EEG channels, 1000 Hz sampling rate.

Source: https://openneuro.org/datasets/ds002725
DOI: 10.1038/s41597-020-0507-6
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


KERNEL_ID = "openneuro_ds002725_stage1_v1"

eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "BrainAmp MR plus",
    "cap": "Ag/AgCl",
    "handedness": "unknown",
}

# Device metadata from dataset documentation (paper DOI: 10.1038/s41597-020-0507-6)
# Annotator: LLM, 2026-04-08, source: official dataset descriptor paper
_DATASET_DEVICE_INFO = {
    "amplifier": "BrainAmp MR plus",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl",  # LLM 推断，需人类复核 - standard EEG cap material
}

# Standard 10-20 channel mapping for 47-channel EEG-fMRI setup
# Source: Paper describes 47-channel EEG cap, likely standard 10-20 system
# Annotator: LLM, 2026-04-08
_EEG_CHANNEL_RENAME_MAP = {
    # Standard 10-20 electrodes
    "Fp1": "FP1",
    "Fp2": "FP2",
    "Fpz": "FPZ",
    "F7": "F7",
    "F3": "F3",
    "Fz": "FZ",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "CZ",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "PZ",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "OZ",
    "O2": "O2",
    # Additional electrodes (common in 47-channel setups)
    "AF3": "AF3",
    "AF4": "AF4",
    "AF7": "AF7",
    "AF8": "AF8",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC5": "FC5",
    "FC6": "FC6",
    "FT7": "FT7",
    "FT8": "FT8",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP3": "CP3",
    "CP4": "CP4",
    "CP5": "CP5",
    "CP6": "CP6",
    "TP7": "TP7",
    "TP8": "TP8",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO3": "PO3",
    "PO4": "PO4",
    "PO7": "PO7",
    "PO8": "PO8",
    # Possible alternate naming conventions
    "EEG-Fp1": "FP1",
    "EEG-Fp2": "FP2",
    "EEG-F7": "F7",
    "EEG-F3": "F3",
    "EEG-Fz": "FZ",
    "EEG-F4": "F4",
    "EEG-F8": "F8",
    "EEG-T7": "T7",
    "EEG-T8": "T8",
    "EEG-P7": "P7",
    "EEG-P8": "P8",
    "EEG-O1": "O1",
    "EEG-O2": "O2",
    "EEG-Oz": "OZ",
    "EEG-Pz": "PZ",
    "EEG-Cz": "CZ",
    "EEG-C3": "C3",
    "EEG-C4": "C4",
}

# Event ID mapping for raw meta
# Based on analysis.md event structure
_EVENT_RAW_MAP = {
    1282: "mri_sync_start",  # BrainVision MRI sync code (start marker)
    1285: "mri_sync_end",  # BrainVision MRI sync code (end marker)
    265: "synthetic_music_onset",  # Synthetic music condition trial onset
    34053: "hardware_marker",  # BrainVision hardware code
    46: "affective_valence",  # FEELTRACE valence marker - LLM 推断，需人类复核
    9: "affective_arousal",  # FEELTRACE arousal marker - LLM 推断，需人类复核
    767: "trial_boundary",  # Unknown trial boundary marker
}

# Standard 10-20 channel names (subset for 47-channel cap)
_STANDARD_1020_CHANNELS = [
    "FP1", "FP2", "F7", "F3", "FZ", "F4", "F8",
    "T7", "C3", "CZ", "C4", "T8",
    "P7", "P3", "PZ", "P4", "P8",
    "O1", "OZ", "O2",
    "AF3", "AF4", "F1", "F2", "F5", "F6",
    "FC1", "FC2", "FC5", "FC6",
    "C1", "C2", "C5", "C6",
    "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
    "P1", "P2", "P5", "P6",
    "PO3", "PO4", "PO7", "PO8",
]


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv from BIDS dataset root."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        df = pd.read_csv(participants_path, sep="\t")
        return df
    return pd.DataFrame()


def _get_subject_info(
    dataset_root: str,
    subject_id: str,
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv."""
    df = _load_participants_tsv(dataset_root)
    
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    if df.empty:
        return info
    
    # Determine the correct column name for subject identifier
    id_column = None
    for col in ["participant_id", "subject_id", "Subject", "ID"]:
        if col in df.columns:
            id_column = col
            break
    
    if id_column is None:
        return info
    
    # Normalize subject_id for matching
    normalized_id = subject_id.replace("sub-", "")
    
    # Try exact match first
    subject_row = df[df[id_column] == subject_id]
    if subject_row.empty:
        subject_row = df[df[id_column] == normalized_id]
    if subject_row.empty:
        # Try with sub- prefix
        subject_row = df[df[id_column].str.contains(normalized_id, na=False)]
    
    if not subject_row.empty:
        row = subject_row.iloc[0]
        
        # Extract age - must be string
        if "age" in row and pd.notna(row["age"]):
            age_val = str(row["age"])
            info["age"] = age_val
        
        # Extract sex - must be lowercase
        if "sex" in row and pd.notna(row["sex"]):
            sex_val = str(row["sex"]).lower().strip()
            if sex_val in ["m", "male", "f", "female"]:
                info["sex"] = "male" if sex_val in ["m", "male"] else "female"
        
        # Extract handedness
        if "handedness" in row and pd.notna(row["handedness"]):
            handed_val = str(row["handedness"]).lower().strip()
            if handed_val in ["r", "right", "l", "left"]:
                info["handedness"] = "right" if handed_val in ["r", "right"] else "left"
    
    return info


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard names before setting montage."""
    existing_names = raw.ch_names
    
    # Build rename map for existing channels
    rename_map = {}
    for ch_name in existing_names:
        # Check direct mapping
        if ch_name in _EEG_CHANNEL_RENAME_MAP:
            new_name = _EEG_CHANNEL_RENAME_MAP[ch_name]
            if new_name != ch_name:
                rename_map[ch_name] = new_name
        # Check case-insensitive match
        elif ch_name.upper() in [v.upper() for v in _EEG_CHANNEL_RENAME_MAP.values()]:
            for old, new in _EEG_CHANNEL_RENAME_MAP.items():
                if old.lower() == ch_name.lower():
                    if new != ch_name:
                        rename_map[ch_name] = new
                    break
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for recognized channels."""
    try:
        existing_in_montage = [ch for ch in raw.ch_names if ch in mne.channels.get_builtin_montages()]
        if len(existing_in_montage) >= 10:  # At least 10 recognized channels
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Montage setup is best-effort
    
    return raw


def _convert_events_to_annotations(
    raw: mne.io.BaseRaw,
) -> mne.io.BaseRaw:
    """Convert raw event channels to annotations using event mapping."""
    try:
        # Try to get events from annotations first
        events, event_id = mne.events_from_annotations(raw)
        
        # Build new event description mapping
        new_annotations = []
        for event in events:
            onset = event[0] / raw.info["sfreq"]
            original_desc = raw.annotations.description[list(events[:, 0]).index(event[0])]
            
            # Map numeric event IDs to readable descriptions
            desc = _EVENT_RAW_MAP.get(int(original_desc), original_desc)
            new_annotations.append({
                "onset": onset,
                "duration": 0.0,
                "description": desc,
            })
        
        # Also check for STI 101 or other stimulus channels
        stim_channels = [ch for ch in raw.ch_names if "stim" in ch.lower() or "trigger" in ch.lower()]
        
        # Add new annotations
        if new_annotations:
            annot = mne.Annotations(
                onset=[a["onset"] for a in new_annotations],
                duration=[a["duration"] for a in new_annotations],
                description=[a["description"] for a in new_annotations],
            )
            raw.set_annotations(annot)
        
    except Exception:
        pass  # Event conversion is best-effort
    
    return raw


class EEGUnityKernel:
    """OpenNeuro DS002725 stage1 kernel for EEGUnity."""
    
    KERNEL_ID = KERNEL_ID
    
    def apply(self, udataset, raw, row):
        """Apply stage1 processing to raw EEG data."""
        # Rename channels to standard names
        raw = _rename_channels(raw)
        
        # Set standard 10-20 montage
        raw = _set_montage_if_possible(raw)
        
        # Convert events to annotations
        raw = _convert_events_to_annotations(raw)
        
        return raw


KERNEL = EEGUnityKernel()