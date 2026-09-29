"""OpenNeuro ds004505 (Real World Table Tennis) stage1 kernel for EEGUnity.

Dataset: Real-world table tennis EEG during cooperative/competitive play.
64-channel mobile EEG at 500 Hz. Hit events detected via IMU acceleration.

Source: https://openneuro.org/datasets/ds004505
Paper: DOI 10.1016/j.dib.2023.110024 (Data in Brief)
      DOI 10.1523/ENEURO.0463-22.2023 (eNeuro)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = [
    "Age", "Gender", "Question1", "Question2", "Question3",
    "Question4", "Question5", "Question6", "Question7", "Question8", "Question9",
]

# Standard 64-channel 10-20 montage names for actiCAP / BrainCap
# Source: Brain Products actiCAP 64-channel standard layout
# Annotator: LLM, 2026-04-08 - needs human verification
_64CH_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8",
    "T7", "T8",
    "TP7", "TP8",
    "M1", "M2",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]

# BrainVision channel naming patterns
_EEG_NUMERIC_PATTERN = re.compile(r"^EEG\s*(\d+)$", re.IGNORECASE)
_EEG_NUMERIC_PATTERN2 = re.compile(r"^Ch(\d+)$", re.IGNORECASE)


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for the given EEG file."""
    base = file_path
    # Remove common EEG extensions to get base
    for ext in [".eeg", ".vhdr", ".vmrk", ".edf", ".bdf", ".set", ".fif"]:
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Try standard BIDS naming
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without task suffix
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # Extract subject from filename
    sub_match = re.search(r"(sub-[a-zA-Z0-9]+)", file_name)
    if sub_match:
        sub = sub_match.group(1)
        # Look for any events.tsv in same directory
        for f in os.listdir(dir_name):
            if f.endswith("_events.tsv") and sub in f:
                return os.path.join(dir_name, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations."""
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0)) if pd.notna(row.get("duration", 0)) else 0
        
        # Use trial_type if available, otherwise value, otherwise stim_type
        desc = None
        for col in ["trial_type", "value", "stim_type"]:
            if col in row and pd.notna(row[col]):
                desc = str(row[col])
                break
        
        if desc is None:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    ch_names = list(raw.ch_names)
    
    # Check if channels are already standard names
    standard_set = set(_64CH_STANDARD_NAMES)
    already_standard = all(ch in standard_set or not ch.startswith(("EEG", "Ch")) for ch in ch_names if ch not in ["Status", "Trig", "ECG", "EMG", "EOG"])
    
    if already_standard:
        return rename_map
    
    # Try numeric EEG patterns (EEG 1, EEG 2, ... or Ch1, Ch2, ...)
    numeric_channels = []
    for ch in ch_names:
        match = _EEG_NUMERIC_PATTERN.match(ch)
        if not match:
            match = _EEG_NUMERIC_PATTERN2.match(ch)
        if match:
            idx = int(match.group(1))
            numeric_channels.append((ch, idx))
    
    # Sort by index and map to standard names
    if numeric_channels and len(numeric_channels) <= len(_64CH_STANDARD_NAMES):
        numeric_channels.sort(key=lambda x: x[1])
        # Check if indices are 0-based or 1-based
        min_idx = min(x[1] for x in numeric_channels)
        
        for ch, idx in numeric_channels:
            standard_idx = idx - min_idx  # Convert to 0-based
            if 0 <= standard_idx < len(_64CH_STANDARD_NAMES):
                if ch != _64CH_STANDARD_NAMES[standard_idx]:
                    rename_map[ch] = _64CH_STANDARD_NAMES[standard_idx]
    
    # Also handle common non-EEG channels
    misc_mappings = {
        "AUX1": "AUX1",
        "AUX2": "AUX2",
        "AUX3": "AUX3",
        "AUX4": "AUX4",
        "ACC1": "ACC1",
        "ACC2": "ACC2",
        "ACC3": "ACC3",
        "Gyro1": "Gyro1",
        "Gyro2": "Gyro2",
        "Gyro3": "Gyro3",
    }
    
    return rename_map


def _get_subject_info_from_participants(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {field.lower(): "unknown" for field in _REQUIRED_INFO_FIELDS}
    info["age"] = "unknown"
    info["sex"] = "unknown"
    info["handedness"] = "unknown"
    info["amplifier"] = "unknown"
    info["cap"] = "unknown"
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        
        # Find subject row
        sub_col = "participant_id"
        if sub_col not in df.columns:
            # Try alternative column names
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    sub_col = col
                    break
        
        subject_row = df[df[sub_col] == subject_id]
        if subject_row.empty:
            # Try without "sub-" prefix
            subject_row = df[df[sub_col] == subject_id.replace("sub-", "")]
        if subject_row.empty:
            # Try with "sub-" prefix
            subject_row = df[df[sub_col] == "sub-" + subject_id.replace("sub-", "")]
        
        if not subject_row.empty:
            row_data = subject_row.iloc[0]
            
            # Map standard fields
            for col in df.columns:
                col_lower = col.lower()
                val = row_data.get(col, "unknown")
                if pd.isna(val):
                    val = "unknown"
                else:
                    val = str(val)
                
                if col_lower in ["age", "participant_age"]:
                    info["age"] = val
                elif col_lower in ["sex", "gender", "participant_sex"]:
                    info["sex"] = val.lower() if val != "unknown" else "unknown"
                elif col_lower in ["handedness", "hand"]:
                    info["handedness"] = val.lower() if val != "unknown" else "unknown"
                elif col_lower in ["amplifier", "eeg_amplifier"]:
                    info["amplifier"] = val
                elif col_lower in ["cap", "eeg_cap"]:
                    info["cap"] = val
                else:
                    # Store all other fields too
                    info[col_lower] = val
            
            # Also store required info fields with original casing
            for field in _REQUIRED_INFO_FIELDS:
                field_lower = field.lower()
                if field_lower not in info:
                    info[field_lower] = "unknown"
                # Check if original case exists in columns
                if field in df.columns:
                    val = row_data.get(field, "unknown")
                    if pd.isna(val):
                        val = "unknown"
                    else:
                        val = str(val)
                    info[field_lower] = val
    
    except Exception:
        pass
    
    return info


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    # Try to get from directory structure
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part
    return "unknown"


class OpenNeuroDS004505Kernel:
    KERNEL_ID = "openneuro_ds004505"
    DATASET_NAME = "ds004505"
    DATASET_DESCRIPTION = "Real-world table tennis EEG during cooperative/competitive play"
    MODALITY = "eeg"
    STAGE = 1

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = str(row.get("file_path", ""))
        subject_id = _extract_subject_id(file_path)
        
        # Get original description
        original_desc = raw.info.get("description", "")
        
        # Find and read participants.tsv
        participants_path = _find_participants_tsv(file_path)
        subject_info = _get_subject_info_from_participants(participants_path, subject_id) if participants_path else {
            "age": "unknown", "sex": "unknown", "handedness": "unknown",
            "amplifier": "unknown", "cap": "unknown"
        }
        
        # Ensure required fields exist
        for field in _REQUIRED_INFO_FIELDS:
            field_lower = field.lower()
            if field_lower not in subject_info:
                subject_info[field_lower] = "unknown"
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": subject_info.get("amplifier", "unknown"),
            "cap": subject_info.get("cap", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Add required info fields
        for field in _REQUIRED_INFO_FIELDS:
            field_lower = field.lower()
            eegunity_description[field_lower] = subject_info.get(field_lower, "unknown")
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage if we have standard channel names
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        # Find and apply events from events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path:
            events_df = _read_events_tsv(events_path)
            if events_df is not None and not events_df.empty:
                # Check if raw already has annotations
                if raw.annotations is None or len(raw.annotations) == 0:
                    # Use events.tsv annotations
                    annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                    raw.set_annotations(annotations)
        
        # Add derived misc channels for required info fields
        sfreq = raw.info["sfreq"]
        n_times = raw.n_times
        for field in _REQUIRED_INFO_FIELDS:
            field_lower = field.lower()
            val = subject_info.get(field_lower, "unknown")
            # Create constant broadcast channel
            data = np.full((1, n_times), float(val) if val.replace('.', '', 1).replace('-', '', 1).isdigit() else 0.0)
            info = mne.create_info([field_lower], sfreq, ch_types="misc")
            misc_raw = mne.io.RawArray(data, info)
            raw.add_channels([misc_raw], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004505Kernel()