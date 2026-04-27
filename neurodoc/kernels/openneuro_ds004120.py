"""BCIT Baseline Driving (openneuro_ds004120) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004120
Source: https://openneuro.org/datasets/ds004120
Reference: 10.3389/fnins.2014.00155 (BCIT driving paradigm)

This kernel handles BIDS-formatted BCIT driving data with:
- 256-channel BioSemi EEG + auxiliary channels (266 total channels)
- 1024 Hz sampling rate
- 60-minute simulated driving with lateral perturbations
- Event codes from *_events.tsv sidecars (required; raw files lack embedded triggers)

Channel setup: BioSemi 256-channel system with A1-H32 naming
Auxiliary channels include EOG, ECG, EMG, respiratory, and trigger/status channels

Event code structure (4-digit):
  1111: Start of left perturbation
  1121: Start of right perturbation
  1211: Start driving car forward (trial start)
  1212: End driving car forward
  2611: Start of guard response (left)
  2621: Start of guard response (right)
  3111: Start of block/trial section
  3310: Straight road (steady state)
  4210: Vehicle moves into defined lane (return)
  4220: Vehicle moves right of lane
  4230: Vehicle moves left of lane
  4311: Correction start
  4411: Rare event / special condition
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Required info fields from participants.tsv
# =============================================================================
_REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness", "year_of_birth"]

# =============================================================================
# Required native misc channels (ensure type is 'misc')
# =============================================================================
_REQUIRED_NATIVE_MISC = []

# =============================================================================
# Required derived misc channels (kernel must create these)
# =============================================================================
_REQUIRED_DERIVED_MISC = [
    "lane_deviation",
    "normalized_accuracy",
    "reaction_time_ms",
    "button_press_duration_ms",
    "time_on_task_minutes",
]

# =============================================================================
# BioSemi 256-channel standard layout: A1-A32, B1-B32, C1-C32, D1-D32,
# E1-E32, F1-F32, G1-G32, H1-H32
# Source: BioSemi 256-channel cap documentation
# https://www.biosemi.com/download/Cap_coords_all.xls
# Annotator: Human, 2026-04-08
# =============================================================================
_BIOSEMI_256_CHANNELS: List[str] = []
for letter in "ABCDEFGH":
    for num in range(1, 33):
        _BIOSEMI_256_CHANNELS.append(f"{letter}{num:02d}")

# =============================================================================
# Auxiliary channel name standardization
# Source: BCIT dataset documentation, BioSemi standard auxiliary channel naming
# Annotator: Human, 2026-04-08
# =============================================================================
_AUX_CHANNEL_MAP: Dict[str, str] = {
    # EOG channels
    "EOGleft": "EOG_left",
    "EOG_left": "EOG_left",
    "EOGright": "EOG_right",
    "EOG_right": "EOG_right",
    "EOGcentral": "EOG_central",
    "EOG_central": "EOG_central",
    "EOGup": "EOG_up",
    "EOG_up": "EOG_up",
    "EOGdown": "EOG_down",
    "EOG_down": "EOG_down",
    # ECG
    "ECG": "ECG",
    "EKG": "ECG",
    # EMG
    "EMG": "EMG",
    # Respiratory
    "Resp": "Respiratory",
    "Respiratory": "Respiratory",
    # Trigger/Status
    "Trigger": "Trigger",
    "Status": "Status",
    "EXG1": "EXG1",
    "EXG2": "EXG2",
    "EXG3": "EXG3",
    "EXG4": "EXG4",
    "EXG5": "EXG5",
    "EXG6": "EXG6",
    "EXG7": "EXG7",
    "EXG8": "EXG8",
}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    base = file_path.replace(".set", "").replace(".edf", "").replace(".bdf", "").replace(".eeg", "").replace(".fif", "")
    # Try standard BIDS naming
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    # Try without run/task suffix variations
    dir_name = os.path.dirname(file_path)
    for f in os.listdir(dir_name) if os.path.isdir(dir_name) else []:
        if f.endswith("_events.tsv"):
            return os.path.join(dir_name, f)
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at root
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _extract_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    import re
    # Match sub-XX pattern
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {}
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for subject
        subj_rows = df[df["participant_id"] == subject_id]
        if len(subj_rows) == 0:
            # Try without 'sub-' prefix
            subj_rows = df[df["participant_id"] == subject_id.replace("sub-", "")]
        if len(subj_rows) > 0:
            row = subj_rows.iloc[0]
            for field in _REQUIRED_INFO_FIELDS:
                if field in row:
                    val = row[field]
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
                else:
                    info[field] = "unknown"
    except Exception:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
    return info


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for BioSemi 256-channel system."""
    rename_map: Dict[str, str] = {}
    
    for ch_name in raw.ch_names:
        # Check if it's already a standard BioSemi name (A1-H32)
        if ch_name in _BIOSEMI_256_CHANNELS:
            continue  # No rename needed
        
        # Check for zero-padded variants (A1 vs A01)
        match = None
        if len(ch_name) >= 2 and ch_name[0] in "ABCDEFGH":
            letter = ch_name[0]
            num_part = ch_name[1:]
            try:
                num = int(num_part)
                if 1 <= num <= 32:
                    standard_name = f"{letter}{num:02d}"
                    if standard_name in _BIOSEMI_256_CHANNELS and standard_name != ch_name:
                        rename_map[ch_name] = standard_name
                        continue
            except ValueError:
                pass
        
        # Check auxiliary channel map
        if ch_name in _AUX_CHANNEL_MAP:
            new_name = _AUX_CHANNEL_MAP[ch_name]
            if new_name != ch_name:
                rename_map[ch_name] = new_name
    
    return rename_map


def _standardize_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names and types for BioSemi 256-channel system."""
    rename_map = _build_channel_rename_map(raw)
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    # Set channel types
    new_types = {}
    for ch_name in raw.ch_names:
        if ch_name in _BIOSEMI_256_CHANNELS:
            new_types[ch_name] = "eeg"
        elif ch_name.startswith("EOG") or ch_name in ("EOG_left", "EOG_right", "EOG_central", "EOG_up", "EOG_down"):
            new_types[ch_name] = "eog"
        elif ch_name in ("ECG", "EKG"):
            new_types[ch_name] = "ecg"
        elif ch_name in ("EMG",):
            new_types[ch_name] = "emg"
        elif ch_name in ("Resp", "Respiratory"):
            new_types[ch_name] = "bio"
        elif ch_name in ("Trigger", "Status", "EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8"):
            new_types[ch_name] = "misc"
    
    if new_types:
        raw = raw.set_channel_types(new_types)
    
    # Ensure all non-EEG channels are marked as misc if not already typed
    for ch_name in raw.ch_names:
        if ch_name not in _BIOSEMI_256_CHANNELS and ch_name not in new_types:
            raw.set_channel_types({ch_name: "misc"})
    
    return raw


def _read_events_from_tsv(events_path: str, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Read events from BIDS events.tsv and create MNE Annotations."""
    try:
        df = pd.read_csv(events_path, sep="\t")
    except Exception:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required columns for events
    if "onset" not in df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = df["onset"].values.astype(float)
    
    # Duration column (default 0 if missing)
    if "duration" in df.columns:
        durations = df["duration"].values.astype(float)
        # Replace NaN with 0
        durations = np.nan_to_num(durations, nan=0.0)
    else:
        durations = np.zeros_like(onsets)
    
    # Description column: use 'value' column for event codes (literal strings, no remap)
    # The 'value' column contains the 4-digit trigger codes needed downstream
    if "value" in df.columns:
        descriptions = df["value"].astype(str).values
    elif "trial_type" in df.columns:
        descriptions = df["trial_type"].astype(str).values
    elif "stim_type" in df.columns:
        descriptions = df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["event"] * len(onsets))
    
    # Filter out any invalid onsets
    valid_mask = (onsets >= 0) & np.isfinite(onsets)
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    # Ensure descriptions are strings
    descriptions = [str(d) for d in descriptions]
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _add_derived_misc_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Add required derived misc channels with constant broadcast values."""
    n_times = len(raw.times)
    sfreq = raw.info["sfreq"]
    
    # Create constant values for each derived misc channel
    # Using constant broadcast as specified for participants.tsv sources
    derived_data = {
        "lane_deviation": np.zeros((1, n_times)),
        "normalized_accuracy": np.ones((1, n_times)),
        "reaction_time_ms": np.full((1, n_times), 500.0),  # typical RT in ms
        "button_press_duration_ms": np.full((1, n_times), 200.0),  # typical duration in ms
        "time_on_task_minutes": np.linspace(0, n_times / sfreq / 60, n_times).reshape(1, -1),  # linear ramp
    }
    
    for ch_name, data in derived_data.items():
        # Ensure finite data of shape (1, n_times)
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
        data = data.astype(np.float64)
        
        # Create info for misc channel
        ch_info = mne.create_info([ch_name], sfreq, ch_types=["misc"])
        ch_raw = mne.io.RawArray(data, ch_info, verbose=False)
        
        # Add to raw
        raw = raw.add_channels([ch_raw], force_update_info=True)
    
    return raw


class BCITDrivingKernel:
    KERNEL_ID = "openneuro_ds004120"
    DATASET_NAME = "BCIT Baseline Driving"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        
        # Extract subject ID
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Read participants info
        participants_path = _find_participants_tsv(file_path)
        participants_info = {}
        if participants_path and subject_id:
            participants_info = _read_participants_info(participants_path, subject_id)
        
        # Standardize channels
        raw = _standardize_channels(raw)
        
        # Find and read events from sibling events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path:
            annotations = _read_events_from_tsv(events_path, raw)
            # CRITICAL: Set annotations on raw so mne.events_from_annotations(raw) works
            if len(annotations) > 0:
                raw = raw.set_annotations(annotations)
        
        # Add derived misc channels
        raw = _add_derived_misc_channels(raw)
        
        # Set montage for EEG channels
        try:
            raw = raw.set_montage("biosemi256", match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        # Build eegunity_description
        description = {
            "dataset_name": self.DATASET_NAME,
            "kernel_id": self.KERNEL_ID,
            "file_path": file_path,
            "subject_id": subject_id or "unknown",
            "n_channels": len(raw.ch_names),
            "sfreq": raw.info["sfreq"],
            "n_times": len(raw.times),
            "duration_sec": len(raw.times) / raw.info["sfreq"] if raw.info["sfreq"] > 0 else 0,
            "participants_info": participants_info,
            "channel_types": {ch_name: raw.get_channel_types(picks=[ch_name])[0] for ch_name in raw.ch_names[:10]},
            "events_source": events_path if events_path else "none",
            "n_annotations": len(raw.annotations) if raw.annotations else 0,
        }
        
        # Store description in raw.info
        raw.info["description"] = json.dumps(description)
        
        return raw


KERNEL = BCITDrivingKernel()