"""OpenNeuro ds004850 (ODE Social-Cognitive EEG Dataset) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004850 | Year: 2023 | Channels: 64 | Sampling Rate: 128 Hz
Paradigm: Social-cognitive with hierarchically encoded stimulus conditions.

This is a BIDS dataset with a single aggregated file. The kernel handles:
- Standard 64-channel renaming to standard_1020 montage
- Event annotation from sibling events.tsv (EEGLAB .set without populated events)
- Metadata extraction from participants.tsv

Event Structure (12-class mapping):
    2200  -> y=0  Primary condition code (dominant)
    72011 -> y=1  Category 7, sub-condition 10, variant 1
    52011 -> y=2  Category 5, sub-condition 10, variant 1
    75011 -> y=3  Category 7, sub-condition 50, variant 1
    55011 -> y=4  Category 5, sub-condition 50, variant 1
    73011 -> y=5  Category 7, sub-condition 30, variant 1
    74011 -> y=6  Category 7, sub-condition 40, variant 1
    53011 -> y=7  Category 5, sub-condition 30, variant 1
    54011 -> y=8  Category 5, sub-condition 40, variant 1
    71011 -> y=9  Category 7, sub-condition 10, variant 1
    2201  -> y=10 Primary condition variant
    51011 -> y=11 Category 5, sub-condition 10, variant 1

Required event IDs: ['2200', '2201', '51011', '53011', '54011', '55011', '72011', '72111']

Source: https://openneuro.org/datasets/ds004850 DOI: 10.18112/openneuro.ds004850.v1.0.0
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import mne
import numpy as np
import pandas as pd


# Kernel requirements configuration
kernel_requirements = {
    "required_info_fields": ["age", "sex", "handedness"],  # Fields from participants.tsv
    "required_native_misc": [],
    "derived_misc_channels": [],
}

# inferred by LLM, needs human review
# Source: OpenNeuro dataset description; single aggregated file with no subject-level separation
# No participants.tsv metadata available for age/sex/device
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "aggregate": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
    }
}

# Required event IDs that must be exposed
_REQUIRED_EVENT_IDS: Set[str] = {"2200", "2201", "51011", "53011", "54011", "55011", "72011", "72111"}

# Standard 64-channel layout for standard_1020 montage
# Source: International 10-20 system, 64-channel extended montage
# Annotator: Human standard reference, 2026-04-08
_CHANNELS_64_STANDARD: List[str] = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz",
]

# Alternative naming conventions that might appear in the data
_CHANNEL_ALIASES: Dict[str, List[str]] = {
    "Fp1": ["FP1", "Fp1"],
    "Fpz": ["FPZ", "Fpz", "FPz"],
    "Fp2": ["FP2", "Fp2"],
    "AF7": ["AF7"],
    "AF3": ["AF3"],
    "AFz": ["AFZ", "Afz", "AFz"],
    "AF4": ["AF4"],
    "AF8": ["AF8"],
    "F7": ["F7"],
    "F5": ["F5"],
    "F3": ["F3"],
    "F1": ["F1"],
    "Fz": ["FZ", "Fz"],
    "F2": ["F2"],
    "F4": ["F4"],
    "F6": ["F6"],
    "F8": ["F8"],
    "FT7": ["FT7"],
    "FC5": ["FC5"],
    "FC3": ["FC3"],
    "FC1": ["FC1"],
    "FCz": ["FCZ", "FCz", "Fcz"],
    "FC2": ["FC2"],
    "FC4": ["FC4"],
    "FC6": ["FC6"],
    "FT8": ["FT8"],
    "T7": ["T7"],
    "C5": ["C5"],
    "C3": ["C3"],
    "C1": ["C1"],
    "Cz": ["CZ", "Cz"],
    "C2": ["C2"],
    "C4": ["C4"],
    "C6": ["C6"],
    "T8": ["T8"],
    "TP7": ["TP7"],
    "CP5": ["CP5"],
    "CP3": ["CP3"],
    "CP1": ["CP1"],
    "CPz": ["CPZ", "CPz"],
    "CP2": ["CP2"],
    "CP4": ["CP4"],
    "CP6": ["CP6"],
    "TP8": ["TP8"],
    "P7": ["P7"],
    "P5": ["P5"],
    "P3": ["P3"],
    "P1": ["P1"],
    "Pz": ["PZ", "Pz"],
    "P2": ["P2"],
    "P4": ["P4"],
    "P6": ["P6"],
    "P8": ["P8"],
    "PO7": ["PO7"],
    "PO3": ["PO3"],
    "POz": ["POZ", "POz"],
    "PO4": ["PO4"],
    "PO8": ["PO8"],
    "O1": ["O1"],
    "Oz": ["OZ", "Oz"],
    "O2": ["O2"],
    "Iz": ["IZ", "Iz"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard_1020 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for std_name, aliases in _CHANNEL_ALIASES.items():
        # Skip if standard name already exists
        if std_name in existing_names:
            continue
        # Find first matching alias that exists and isn't already standard
        for alias in aliases:
            if alias in existing_names and alias != std_name and alias not in rename_map:
                rename_map[alias] = std_name
                break
    
    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for the given EEG file."""
    path = Path(file_path)
    
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.set -> sub-XX_task-YY_run-ZZ_events.tsv
    # Try standard BIDS events.tsv naming
    events_tsv = path.parent / path.name.replace("_eeg.", "_events.").replace(".set", ".tsv").replace(".edf", ".tsv").replace(".bdf", ".tsv").replace(".eeg", ".tsv").replace(".fif", ".tsv")
    
    if events_tsv.exists() and events_tsv.is_file():
        return str(events_tsv)
    
    # Also try just replacing extension
    for ext in [".set", ".edf", ".bdf", ".eeg", ".fif"]:
        if path.name.endswith(ext):
            events_tsv = path.parent / (path.name[:-len(ext)] + "_events.tsv")
            if events_tsv.exists() and events_tsv.is_file():
                return str(events_tsv)
    
    # Search for any events.tsv in parent directory
    if path.parent.exists():
        for candidate in path.parent.glob("*events.tsv"):
            if candidate.is_file():
                return str(candidate)
    
    # Search in grandparent (BIDS eeg/ folder structure)
    grandparent = path.parent.parent
    if grandparent.exists():
        for candidate in grandparent.rglob("*events.tsv"):
            if candidate.is_file():
                return str(candidate)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file in the BIDS dataset root."""
    path = Path(file_path)
    
    # Walk up to find participants.tsv
    current = path.parent
    for _ in range(5):  # Limit search depth
        participants_tsv = current / "participants.tsv"
        if participants_tsv.exists() and participants_tsv.is_file():
            return str(participants_tsv)
        current = current.parent
        if current == current.parent:  # Reached filesystem root
            break
    
    return None


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    path = Path(file_path)
    name = path.name
    
    # Try to extract sub-XX from filename
    match = re.search(r'sub-([a-zA-Z0-9]+)', name)
    if match:
        return match.group(1)
    
    # Try from parent directory
    for part in path.parts:
        match = re.search(r'sub-([a-zA-Z0-9]+)', part)
        if match:
            return match.group(1)
    
    return "aggregate"


def _read_events_tsv(events_tsv_path: str, sfreq: float) -> Optional[mne.Annotations]:
    """Read events.tsv file and return MNE Annotations.
    
    The events.tsv has columns: onset, duration, sample, value
    We use 'onset' (in seconds) and 'value' (the event label) directly.
    Duration is in seconds from the tsv file.
    """
    try:
        df = pd.read_csv(events_tsv_path, sep='\t')
        
        # We need onset and value columns. The 'value' column carries the trigger codes.
        if 'onset' not in df.columns:
            return None
        
        # Use 'value' column for event labels; fallback to 'trial_type' if needed
        if 'value' in df.columns:
            labels = df['value'].astype(str).tolist()
        elif 'trial_type' in df.columns:
            labels = df['trial_type'].astype(str).tolist()
        else:
            return None
        
        # Get onsets in seconds
        onsets = df['onset'].astype(float).values
        
        # Get durations in seconds (default to 0 if not present)
        if 'duration' in df.columns:
            durations = df['duration'].astype(float).values
            # Replace NaN durations with 0
            durations = np.nan_to_num(durations, nan=0.0)
        else:
            durations = np.zeros(len(onsets))
        
        # Create MNE Annotations with orig_time matching raw
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=labels,
            orig_time=None,
        )
        
        return annotations
        
    except Exception:
        return None


def _read_participants_tsv(participants_tsv_path: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv file and return DataFrame."""
    try:
        return pd.read_csv(participants_tsv_path, sep='\t')
    except Exception:
        return None


def _get_subject_info(participants_df: Optional[pd.DataFrame], subject_id: str) -> Dict[str, str]:
    """Get subject info from participants DataFrame."""
    if participants_df is None or 'participant_id' not in participants_df.columns:
        return _SUBJECT_DICT.get("aggregate", {}).copy()
    
    # Try exact match first
    row = participants_df[participants_df['participant_id'] == f"sub-{subject_id}"]
    if row.empty:
        row = participants_df[participants_df['participant_id'] == subject_id]
    if row.empty:
        # Try partial match
        for idx, prow in participants_df.iterrows():
            pid = str(prow.get('participant_id', ''))
            if subject_id in pid or pid in subject_id:
                row = participants_df.iloc[[idx]]
                break
    
    if row.empty:
        return _SUBJECT_DICT.get("aggregate", {}).copy()
    
    info = {}
    row_data = row.iloc[0]
    for field in ["age", "sex", "handedness", "amplifier", "cap"]:
        val = row_data.get(field, "unknown")
        info[field] = str(val) if pd.notna(val) else "unknown"
    
    # Ensure all fields exist
    for field in ["age", "sex", "handedness", "amplifier", "cap"]:
        if field not in info:
            info[field] = "unknown"
    
    return info


class OpenneuroDs004850Kernel:
    """EEGUnity kernel for OpenNeuro ds004850 dataset."""
    
    KERNEL_ID = "openneuro_ds004850"
    DATASET_NAME = "OpenNeuro ds004850 (ODE Social-Cognitive EEG Dataset)"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract file path from row
        file_path = str(row.get("File Path", row.get("file_path", "")))
        
        # Find and read participants.tsv for metadata
        participants_tsv = _find_participants_tsv(file_path)
        participants_df = _read_participants_tsv(participants_tsv) if participants_tsv else None
        
        # Extract subject ID and get info
        subject_id = _extract_subject_id_from_path(file_path)
        subject_info = _get_subject_info(participants_df, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
            "amplifier": subject_info.get("amplifier", "unknown"),
            "cap": subject_info.get("cap", "unknown"),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels to standard_1020 montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage if not already set
        try:
            montage = raw.get_montage()
            if montage is None:
                raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
        except Exception:
            try:
                raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
            except Exception:
                pass
        
        # Load events from sibling events.tsv
        # The EEGLAB .set file has empty event field, so we MUST populate from events.tsv
        events_tsv = _find_events_tsv(file_path)
        if events_tsv:
            sfreq = raw.info.get("sfreq", 128.0)
            annotations = _read_events_tsv(events_tsv, sfreq)
            if annotations is not None:
                # Set annotations on raw - this is critical for events to be accessible
                raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenneuroDs004850Kernel()