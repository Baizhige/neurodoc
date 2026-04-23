"""BCIT Traffic Complexity (openneuro_ds004123) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004123
URL: https://openneuro.org/datasets/ds004123
30 subjects, 74 channels, 1024 Hz sampling rate

Paradigm: Simulated driving task with varying traffic complexity (low/medium/high)
and lateral vehicle perturbations.

Source: https://doi.org/10.18112/openneuro.ds004123.v1.0.0
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Dataset-specific constants
# =============================================================================

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["year_of_birth", "amplifier", "cap", "handedness"]

# Required event IDs that must appear in scan output
_REQUIRED_EVENT_IDS = ["1111", "1121", "2221", "2222", "2711", "2712", "3210", "3230", "3240"]

# BCIT event code descriptions based on analysis.md and mega-analysis papers
# Source: DOI 10.1016/j.neuroimage.2019.116054, DOI 10.1016/j.neuroimage.2017.02.057
# Annotator: LLM, 2026-04-08
_EVENT_CODE_MAP: Dict[str, str] = {
    # Traffic complexity (Classical Task 1)
    "3210": "traffic_complexity_low",
    "3230": "traffic_complexity_medium", 
    "3240": "traffic_complexity_high",
    # Perturbation direction (Potential Task 1)
    "1111": "perturbation_left",
    "1121": "perturbation_right",
    # Traffic presence (Potential Task 2)
    "2221": "traffic_present",
    "2222": "traffic_absent",
    # Other required event IDs
    "2711": "admin_marker_2711",
    "2712": "admin_marker_2712",
    # Additional lane correction events (Normal Task 1)
    "1211": "lane_correction_type_1",
    "1212": "lane_correction_type_2",
    # Additional perturbation events (Normal Task 2)
    "3111": "perturbation_onset_3111",
    "4210": "perturbation_onset_4210",
    "4220": "perturbation_event_4220",
    "4230": "perturbation_direction_4230",
}

# Standard 10-20 channel names for 74-channel BCIT montage
# Source: BCIT dataset documentation, standard extended 10-20 system with additional
# peripheral channels for driving research (EOG, EMG, etc.)
# Annotator: LLM 推断，需人类复核
_CHANNEL_NAMES_74: List[str] = [
    # Standard 10-20 EEG channels (64 channels)
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
    "T7", "C3", "Cz", "C4", "T8", "CP5", "CP1", "CP2", "CP6", "P7", "P3",
    "Pz", "P4", "P8", "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6", "FT7", "FT8", "C5",
    "C1", "C2", "C6", "TP7", "TP8", "P5", "P1", "P2", "P6", "PO5", "PO6",
    "CB1", "CB2", "CP3", "CPz", "CP4", "FC3", "FCz", "FC4", "TP9", "TP10",
    # EOG channels (4 channels)
    "HEOG_left", "HEOG_right", "VEOG_lower", "VEOG_upper",
    # EMG/Other peripheral channels (6 channels)
    "EMG_left", "EMG_right", "ECG", "RESP", "GSR", "TEMP",
]

# Channel types mapping
_CHANNEL_TYPES: Dict[str, str] = {
    # EOG
    "HEOG_left": "eog",
    "HEOG_right": "eog", 
    "VEOG_lower": "eog",
    "VEOG_upper": "eog",
    # EMG
    "EMG_left": "emg",
    "EMG_right": "emg",
    # Other physiological
    "ECG": "ecg",
    "RESP": "resp",
    "GSR": "gsr",
    "TEMP": "temperature",
}

# =============================================================================
# Helper functions
# =============================================================================

def _get_subject_id_from_path(file_path: str) -> str:
    """Extract BIDS subject ID from file path."""
    basename = os.path.basename(file_path)
    # Handle patterns like sub-001_task-traffic_eeg.set or sub-001_eeg.set
    if basename.startswith("sub-"):
        parts = basename.split("_")
        return parts[0]
    return "unknown"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for the given EEG file."""
    # BIDS pattern: sub-XXX_task-YYY_eeg.set -> sub-XXX_task-YYY_events.tsv
    # or in eeg/ directory: sub-XXX/eeg/sub-XXX_task-YYY_eeg.set
    base = file_path.replace("_eeg.set", "").replace("_eeg.edf", "").replace("_eeg.bdf", "")
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: same directory, any matching events.tsv
    dirname = os.path.dirname(file_path)
    basename_prefix = os.path.basename(file_path).split("_eeg")[0]
    
    if os.path.isdir(dirname):
        for f in os.listdir(dirname):
            if f.endswith("_events.tsv") and f.startswith(basename_prefix):
                return os.path.join(dirname, f)
    
    # Try parent directory (BIDS eeg/ folder structure)
    parent_dir = os.path.dirname(dirname)
    if parent_dir and os.path.isdir(parent_dir):
        for f in os.listdir(parent_dir):
            if f == "events.tsv" or (f.endswith("_events.tsv") and basename_prefix in f):
                return os.path.join(parent_dir, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    
    # Walk up to find BIDS root
    for _ in range(5):  # Limit search depth
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        
        # Also check parent
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info: Dict[str, str] = {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        
        # Find row for this subject
        subject_col = "participant_id"
        if subject_col not in df.columns:
            # Try alternatives
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    subject_col = col
                    break
        
        subject_row = df[df[subject_col] == subject_id]
        if subject_row.empty:
            # Try without "sub-" prefix
            subject_row = df[df[subject_col] == subject_id.replace("sub-", "")]
        
        if not subject_row.empty:
            row_data = subject_row.iloc[0]
            for field in _REQUIRED_INFO_FIELDS:
                if field in row_data.index:
                    val = row_data[field]
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
                else:
                    info[field] = "unknown"
        else:
            for field in _REQUIRED_INFO_FIELDS:
                info[field] = "unknown"
                
    except Exception:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
    
    return info


def _compute_age_from_year_of_birth(year_of_birth: str, recording_year: int = 2014) -> str:
    """Compute age from year of birth."""
    try:
        yob = int(float(year_of_birth))
        age = recording_year - yob
        if 10 <= age <= 100:
            return str(age)
    except (ValueError, TypeError):
        pass
    return "unknown"


def _rename_channels_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename BCIT channels to standard names."""
    ch_names = raw.ch_names
    
    # Check if already standard names
    if all(c in _CHANNEL_NAMES_74 or c.upper() in [x.upper() for x in _CHANNEL_NAMES_74] 
           for c in ch_names if not c.startswith("STI") and not c.startswith("MISC")):
        return raw
    
    # Build rename map based on position if channels are numbered
    rename_map = {}
    for i, old_name in enumerate(ch_names):
        if old_name.startswith("STI") or old_name.startswith("MISC"):
            continue
        if i < len(_CHANNEL_NAMES_74):
            rename_map[old_name] = _CHANNEL_NAMES_74[i]
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set channel types based on name patterns."""
    ch_types = {}
    for ch_name in raw.ch_names:
        if ch_name in _CHANNEL_TYPES:
            ch_types[ch_name] = _CHANNEL_TYPES[ch_name]
        elif ch_name.upper().startswith("EOG") or "EOG" in ch_name.upper():
            ch_types[ch_name] = "eog"
        elif ch_name.upper().startswith("EMG") or "EMG" in ch_name.upper():
            ch_types[ch_name] = "emg"
        elif ch_name.upper() in ["ECG", "EKG"]:
            ch_types[ch_name] = "ecg"
        elif ch_name.upper().startswith("STI"):
            ch_types[ch_name] = "stim"
    
    if ch_types:
        raw = raw.set_channel_types(ch_types)
    
    return raw


def _read_events_from_tsv(events_path: str, sfreq: float) -> Optional[pd.DataFrame]:
    """Read events from BIDS events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        
        # Ensure we have a description/label column - use 'value' column as the literal event label
        # since that's what carries the distinguishable trigger codes in this dataset
        if "value" in df.columns:
            # Use literal string values from the 'value' column as annotations
            df["description"] = df["value"].astype(str)
        elif "trial_type" in df.columns:
            df["description"] = df["trial_type"].astype(str)
        elif "event_type" in df.columns:
            df["description"] = df["event_type"].astype(str)
        else:
            # Fallback: no usable label column
            return None
            
        # Ensure onset column exists - use 'onset' in seconds directly
        if "onset" not in df.columns:
            if "sample" in df.columns:
                df["onset"] = df["sample"] / sfreq
            else:
                return None
        
        # Ensure duration column exists
        if "duration" not in df.columns:
            df["duration"] = 0.0
        else:
            # Replace n/a with 0
            df["duration"] = df["duration"].replace("n/a", 0.0).replace("N/A", 0.0)
            df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0.0)
        
        return df
    except Exception:
        return None


def _add_events_as_annotations(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add events from DataFrame as MNE Annotations."""
    if events_df is None or events_df.empty:
        return raw
    
    # Required columns
    if "onset" not in events_df.columns or "description" not in events_df.columns:
        return raw
    
    # Filter valid rows
    valid = events_df["onset"].notna() & events_df["description"].notna()
    events_df = events_df[valid].copy()
    
    if events_df.empty:
        return raw
    
    # Create annotations
    onsets = events_df["onset"].astype(float).values
    durations = events_df["duration"].astype(float).values if "duration" in events_df.columns else np.zeros(len(onsets))
    descriptions = events_df["description"].astype(str).values
    
    # Ensure durations are non-negative
    durations = np.maximum(durations, 0.0)
    
    annot = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=raw.info.get("meas_date", None)
    )
    
    raw = raw.set_annotations(annot)
    return raw


# =============================================================================
# Kernel class
# =============================================================================

@dataclass
class BCITTrafficComplexityKernel:
    """Stage-1 kernel for BCIT Traffic Complexity dataset (ds004123)."""
    
    dataset_name: str = "openneuro_ds004123"
    dataset_url: str = "https://openneuro.org/datasets/ds004123"
    dataset_doi: str = "10.18112/openneuro.ds004123.v1.0.0"
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load a single EEG file and return MNE Raw + metadata."""
        # Load EEGLAB .set file
        raw = mne.io.read_raw_eeglab(file_path, preload=False, verbose=False)
        
        # Get sampling frequency for event onset calculation
        sfreq = raw.info["sfreq"]
        
        # Rename channels to standard names if needed
        raw = _rename_channels_to_standard(raw)
        
        # Set channel types
        raw = _set_channel_types(raw)
        
        # Find and load events from sibling events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path is not None:
            events_df = _read_events_from_tsv(events_path, sfreq)
            if events_df is not None:
                raw = _add_events_as_annotations(raw, events_df)
        
        # Get subject info
        subject_id = _get_subject_id_from_path(file_path)
        participants_path = _find_participants_tsv(file_path)
        
        subject_info = {}
        if participants_path is not None:
            subject_info = _read_participants_info(participants_path, subject_id)
        
        # Compute age
        age = "unknown"
        if "year_of_birth" in subject_info:
            age = _compute_age_from_year_of_birth(subject_info["year_of_birth"])
        
        # Build eegunity_description
        description = {
            "dataset_name": self.dataset_name,
            "dataset_url": self.dataset_url,
            "subject_id": subject_id,
            "age": age,
            "sex": "unknown",  # Not available in this dataset
            "handedness": subject_info.get("handedness", "unknown"),
            "amplifier": subject_info.get("amplifier", "unknown"),
            "cap": subject_info.get("cap", "unknown"),
            "task": "DriveWithComplexity",
            "paradigm": "simulated_driving_traffic_complexity",
            "required_event_ids": _REQUIRED_EVENT_IDS,
        }
        
        return {
            "raw": raw,
            "eegunity_description": json.dumps(description),
        }


# Module-level assignment required by EEGUnity
KERNEL = BCITTrafficComplexityKernel()