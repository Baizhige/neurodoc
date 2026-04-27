"""Dataset-specific kernel for openneuro ds004121.

BCIT Mind Wandering dataset.
Driving simulation with mind wandering thought probes.
60 subjects, 74 channels, 1024 Hz.

Source: https://doi.org/10.18112/openneuro.ds004121.v1.0.0
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
_REQUIRED_INFO_FIELDS = ["legacy_labID", "year_of_birth", "age", "sex", "amplifier", "cap", "handedness"]


def _find_bids_root(file_path: str) -> Optional[str]:
    """Find BIDS root directory from a file path."""
    parts = os.path.normpath(file_path).split(os.sep)
    for i in range(len(parts)):
        # Look for participants.tsv
        candidate = os.sep.join(parts[:i+1])
        if os.path.isfile(os.path.join(candidate, "participants.tsv")):
            return candidate
    return None


def _get_subject_from_file(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # Match sub-XX pattern
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _read_participants_tsv(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and extract subject info."""
    info = {}
    try:
        participants_path = os.path.join(bids_root, "participants.tsv")
        if not os.path.exists(participants_path):
            return info
        
        df = pd.read_csv(participants_path, sep="\t")
        
        # Find row for this subject
        subj_rows = df[df["participant_id"] == subject_id]
        if subj_rows.empty:
            # Try without "sub-" prefix
            subj_rows = df[df["participant_id"] == subject_id.replace("sub-", "")]
        
        if not subj_rows.empty:
            row_data = subj_rows.iloc[0]
            for field in _REQUIRED_INFO_FIELDS:
                if field in row_data.index:
                    val = row_data[field]
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
                else:
                    info[field] = "unknown"
    except Exception:
        pass
    
    # Ensure all required fields exist
    for field in _REQUIRED_INFO_FIELDS:
        if field not in info:
            info[field] = "unknown"
    
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv for an EEG file."""
    # BIDS naming: sub-XX_ses-YY_task-ZZ_run-W_eeg.<ext> -> sub-XX_ses-YY_task-ZZ_run-W_events.tsv
    base = file_path
    for ext in [".edf", ".bdf", ".set", ".eeg", ".vhdr", ".vmrk", ".fif"]:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run number
    base_no_run = re.sub(r'_run-\d+', '', base)
    events_path = base_no_run + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Search in same directory
    dir_path = os.path.dirname(file_path)
    if os.path.exists(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                return os.path.join(dir_path, f)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t", dtype=str, na_values=["n/a", "N/A", "na", "NA"])
        return df
    except Exception:
        return None


def _create_annotations_from_events_tsv(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Create MNE Annotations from BIDS events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return None
    
    required_cols = ["onset"]
    if not all(c in events_df.columns for c in required_cols):
        return None
    
    # Parse onsets as float (seconds in BIDS)
    onsets = pd.to_numeric(events_df["onset"], errors="coerce").values
    # Drop rows with invalid onsets
    valid_mask = ~np.isnan(onsets)
    if not np.any(valid_mask):
        return None
    
    onsets = onsets[valid_mask]
    
    # Use 'value' column as description (literal strings, no remapping per HC-5)
    # The 'value' column contains the actual trigger codes (e.g., 3111, 1211, etc.)
    if "value" in events_df.columns:
        descriptions = events_df.loc[valid_mask, "value"].astype(str).values
    elif "trial_type" in events_df.columns:
        descriptions = events_df.loc[valid_mask, "trial_type"].astype(str).values
    else:
        # Fallback: use empty string descriptions
        descriptions = np.array([""] * len(onsets))
    
    # Duration: use duration column if present, else 0.0
    if "duration" in events_df.columns:
        durations = pd.to_numeric(events_df.loc[valid_mask, "duration"], errors="coerce").fillna(0.0).values
    else:
        durations = np.zeros(len(onsets))
    
    # Ensure non-negative durations
    durations = np.maximum(durations, 0.0)
    
    annot = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )
    return annot


@dataclass
class _EEGUnityDescription:
    """Description object for EEGUnity."""
    sfreq: float
    n_channels: int
    n_times: int
    duration_sec: float
    channel_types: Dict[str, str]
    events: Optional[np.ndarray]
    event_id: Optional[Dict[str, int]]
    subject_info: Dict[str, Any]
    dataset_name: str
    task_name: Optional[str]
    montage_kind: Optional[str]


class _KERNEL:
    """Dataset-specific kernel for openneuro ds004121."""

    KERNEL_ID = "openneuro_ds004121"
    DATASET_NAME = "ds004121"
    TASK_NAME = "DriveWithTaskAudio"

    def __init__(self):
        pass

    def _get_task_name(self, file_path: str) -> Optional[str]:
        """Extract task name from BIDS file path."""
        match = re.search(r'task-([a-zA-Z0-9]+)', file_path)
        if match:
            return match.group(1)
        return None

    def _load_raw(self, file_path: str) -> mne.io.BaseRaw:
        """Load EEG file and return raw object."""
        if file_path.endswith(".edf"):
            raw = mne.io.read_raw_edf(file_path, preload=False)
        elif file_path.endswith(".bdf"):
            raw = mne.io.read_raw_bdf(file_path, preload=False)
        elif file_path.endswith(".set"):
            raw = mne.io.read_raw_eeglab(file_path, preload=False)
        elif file_path.endswith(".vhdr") or file_path.endswith(".eeg"):
            raw = mne.io.read_raw_brainvision(file_path, preload=False)
        elif file_path.endswith(".fif"):
            raw = mne.io.read_raw_fif(file_path, preload=False)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["file_path"] if "file_path" in row else str(row.get("path", ""))
        bids_root = _find_bids_root(file_path)
        subject_id = _get_subject_from_file(file_path)
        subject_info = {}
        if bids_root and subject_id:
            subject_info = _read_participants_tsv(bids_root, subject_id)
        eegunity_description = {
            "legacy_labID": subject_info.get("legacy_labID", "unknown"),
            "year_of_birth": subject_info.get("year_of_birth", "unknown"),
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": subject_info.get("amplifier", "unknown"),
            "cap": subject_info.get("cap", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
        }
        original_description = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Always load events from events.tsv for this dataset.
        # The EEGLAB .set files have empty event fields, so file-native triggers are not present.
        # We must use the sibling events.tsv files which contain the actual event information.
        events_path = _find_events_tsv(file_path)
        if events_path:
            events_df = _read_events_tsv(events_path)
            if events_df is not None and not events_df.empty:
                annot = _create_annotations_from_events_tsv(events_df, raw.info["sfreq"])
                if annot is not None:
                    # Set annotations on the raw object, replacing any existing annotations
                    raw.set_annotations(annot)
        
        return raw


KERNEL = _KERNEL()