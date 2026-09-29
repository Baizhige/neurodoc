"""OpenNeuro ds004356 stage1 kernel for EEGUnity.

Subcortical responses to music and speech are alike while cortical responses diverge.
EEG auditory brainstem response (ABR) dataset with 34-channel EEG at 10000 Hz.

Source: https://openneuro.org/datasets/ds004356
Paper: DOI 10.1038/s41598-023-50438-0
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = [
    "L_500",
    "R_500",
    "age",
    "formal_musical_training_years",
    "gender",
    "musical_training_years",
    "tonal_language_speaker",
]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = [
    ("trial_number", "events.tsv:trial"),
    ("number_trial", "events.tsv:number_trial"),
]

# Required native misc channels (none specified, but we ensure any non-EEG channels are misc)
_REQUIRED_NATIVE_MISC: List[str] = []

# Channel name standardization for 34-channel layout
# Source: Paper methods section and standard 10-20 system with additional ABR channels
# The dataset uses 34 channels including standard 10-20 plus additional channels for ABR
# Annotator: LLM, 2026-04-08, inference from paper and standard ABR montages
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 channels (common naming variations)
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    # Common alternative names
    "A1": "A1",
    "A2": "A2",
    "M1": "M1",
    "M2": "M2",
    "TP9": "TP9",
    "TP10": "TP10",
    # Possible numbered channels that need mapping
    "EEG 1": "Fp1",
    "EEG 2": "Fp2",
    "EEG 3": "F7",
    "EEG 4": "F3",
    "EEG 5": "Fz",
    "EEG 6": "F4",
    "EEG 7": "F8",
    "EEG 8": "T7",
    "EEG 9": "C3",
    "EEG 10": "Cz",
    "EEG 11": "C4",
    "EEG 12": "T8",
    "EEG 13": "P7",
    "EEG 14": "P3",
    "EEG 15": "Pz",
    "EEG 16": "P4",
    "EEG 17": "P8",
    "EEG 18": "O1",
    "EEG 19": "Oz",
    "EEG 20": "O2",
    # Additional ABR-specific channels (mastoids, neck, etc.)
    "Mastoid L": "M1",
    "Mastoid R": "M2",
    "Neck": "NECK",
    "Chin": "CHIN",
    # Generic numbered fallbacks
    "1": "Fp1",
    "2": "Fp2",
    "3": "F7",
    "4": "F3",
    "5": "Fz",
    "6": "F4",
    "7": "F8",
    "8": "T7",
    "9": "C3",
    "10": "Cz",
    "11": "C4",
    "12": "T8",
    "13": "P7",
    "14": "P3",
    "15": "Pz",
    "16": "P4",
    "17": "P8",
    "18": "O1",
    "19": "Oz",
    "20": "O2",
}


def _extract_subject_id(row) -> str:
    """Extract BIDS subject ID from row or file path."""
    if "Subject" in row and pd.notna(row["Subject"]):
        sub = str(row["Subject"]).replace("sub-", "").zfill(2)
        return f"sub-{sub}"
    file_path = row.get("File Path", "")
    if "sub-" in file_path:
        parts = file_path.split("sub-")
        if len(parts) > 1:
            sub_id = parts[1].split("/")[0].split("_")[0].replace("sub-", "")
            return f"sub-{sub_id.zfill(2)}"
    return "sub-01"


def _find_bids_root(file_path: str) -> Optional[str]:
    """Find BIDS root directory from file path."""
    parts = os.path.normpath(file_path).split(os.sep)
    for i, part in enumerate(parts):
        if part.startswith("sub-"):
            return os.sep.join(parts[:i])
    # Try finding dataset_description.json
    current = os.path.dirname(file_path)
    for _ in range(5):  # Search up to 5 levels
        if os.path.exists(os.path.join(current, "dataset_description.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def _read_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from BIDS root."""
    if bids_root is None:
        return None
    participants_path = os.path.join(bids_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return None
    try:
        return pd.read_csv(participants_path, sep="\t")
    except Exception:
        return None


def _get_subject_info(participants_df: Optional[pd.DataFrame], subject_id: str) -> Dict[str, str]:
    """Extract subject info from participants DataFrame."""
    info: Dict[str, str] = {}
    if participants_df is None:
        return info
    
    # Match subject ID (handle both "sub-01" and "01" formats)
    sub_match = subject_id.replace("sub-", "")
    
    # Try exact match first
    mask = participants_df["participant_id"] == subject_id
    if not mask.any():
        # Try without "sub-" prefix
        mask = participants_df["participant_id"] == sub_match
    if not mask.any():
        # Try with zero-padding variations
        mask = participants_df["participant_id"] == f"sub-{sub_match.zfill(2)}"
    
    if not mask.any():
        return info
    
    row = participants_df[mask].iloc[0]
    
    for field in _REQUIRED_INFO_FIELDS:
        if field in row and pd.notna(row[field]):
            info[field] = str(row[field])
        else:
            info[field] = "unknown"
    
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the matching events.tsv file for a given EEG file."""
    # BrainVision .eeg files have .vhdr header; events.tsv is sibling to header or in same dir
    # First check if this is a BrainVision file where we need to find the header
    if file_path.endswith(".eeg"):
        # Look for corresponding .vhdr file
        vhdr_path = file_path.replace(".eeg", ".vhdr")
        if os.path.exists(vhdr_path):
            # events.tsv should be sibling to the .vhdr or in the same directory
            base_dir = os.path.dirname(file_path)
            base_name = os.path.basename(file_path).replace(".eeg", "")
        else:
            base_dir = os.path.dirname(file_path)
            base_name = os.path.basename(file_path).replace(".eeg", "")
    else:
        base_dir = os.path.dirname(file_path)
        base_name = os.path.basename(file_path).split(".")[0]
    
    # Try direct sibling first
    events_path = os.path.join(base_dir, f"{base_name}_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Try without run suffix if present
    # BIDS naming: sub-XX_task-YYY_run-01_eeg.eeg -> sub-XX_task-YYY_events.tsv (without run)
    # or sub-XX_task-YYY_run-01_events.tsv (with run)
    parts = base_name.split("_")
    for i in range(len(parts) - 1, 0, -1):
        if parts[i].startswith("run-"):
            # Try without this run component
            alt_name = "_".join(parts[:i] + parts[i+1:])
            events_path = os.path.join(base_dir, f"{alt_name}_events.tsv")
            if os.path.exists(events_path):
                return events_path
    
    # Try task-level events.tsv
    task_parts = [p for p in parts if p.startswith("task-")]
    if task_parts:
        task_name = task_parts[0].replace("task-", "")
        # Look for any events.tsv with matching task in directory
        for fname in sorted(os.listdir(base_dir)) if os.path.exists(base_dir) else []:
            if fname.endswith("_events.tsv") and task_name in fname:
                return os.path.join(base_dir, fname)
    
    # Search more broadly in the directory
    for fname in sorted(os.listdir(base_dir)) if os.path.exists(base_dir) else []:
        if fname.endswith("_events.tsv"):
            # Check if subject matches
            sub_id = [p for p in parts if p.startswith("sub-")]
            if sub_id and sub_id[0] in fname:
                return os.path.join(base_dir, fname)
    
    return None


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if file_path is None or not os.path.exists(file_path):
        return None
    try:
        return pd.read_csv(file_path, sep="\t")
    except Exception:
        return None


def _create_misc_channel(raw: mne.io.BaseRaw, name: str, data: np.ndarray) -> mne.io.BaseRaw:
    """Create a misc channel and add it to the raw object."""
    # Ensure data is 2D (1, n_times)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    
    # Create info for new channel
    new_info = mne.create_info(
        ch_names=[name],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    
    # Create RawArray
    new_raw = mne.io.RawArray(data, new_info)
    
    # Add to existing raw
    raw.add_channels([new_raw], force_update_info=True)
    
    return raw


def _standardize_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names and types."""
    # Rename channels based on mapping
    rename_map = {}
    for old_name in raw.ch_names:
        if old_name in _CHANNEL_RENAME_MAP:
            rename_map[old_name] = _CHANNEL_RENAME_MAP[old_name]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    # Set channel types - default to EEG for all, then override specific ones
    ch_types = {ch: "eeg" for ch in raw.ch_names}
    
    # Mark known non-EEG channels as misc
    for ch in raw.ch_names:
        if ch in _REQUIRED_NATIVE_MISC:
            ch_types[ch] = "misc"
        # Also mark any channels with common non-EEG names
        if any(x in ch.upper() for x in ["MASTOID", "NECK", "CHIN", "EOG", "ECG", "EMG"]):
            ch_types[ch] = "misc"
    
    raw.set_channel_types(ch_types)
    
    return raw


def _add_events_as_annotations(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Add events from events.tsv as annotations to the raw object."""
    if events_df is None or events_df.empty:
        return raw
    
    # Check required columns
    if "onset" not in events_df.columns:
        return raw
    
    # Determine which column to use for annotation descriptions
    # Priority: trial_type > value (as string) > EEG_trigger
    if "trial_type" in events_df.columns:
        desc_col = "trial_type"
    elif "value" in events_df.columns:
        desc_col = "value"
    elif "EEG_trigger" in events_df.columns:
        desc_col = "EEG_trigger"
    else:
        # Fallback: use first string column or create generic labels
        for col in events_df.columns:
            if events_df[col].dtype == object:
                desc_col = col
                break
        else:
            desc_col = None
    
    # Build onset, duration, description arrays
    onsets = events_df["onset"].values.astype(float)
    
    if "duration" in events_df.columns:
        durations = events_df["duration"].values.astype(float)
    else:
        durations = np.zeros(len(onsets))
    
    if desc_col is not None:
        descriptions = events_df[desc_col].astype(str).values
    else:
        descriptions = np.array(["event"] * len(onsets))
    
    # Create annotations
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=raw.info.get("meas_date"),
    )
    
    raw.set_annotations(annotations)
    
    return raw


def _add_derived_misc_channels(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Add derived misc channels from events.tsv data."""
    if events_df is None or events_df.empty:
        return raw
    
    sfreq = raw.info["sfreq"]
    n_times = raw.n_times
    
    for misc_name, source in _REQUIRED_DERIVED_MISC:
        # Parse source specification
        if source.startswith("events.tsv:"):
            col_name = source.split(":", 1)[1]
            if col_name not in events_df.columns:
                continue
            
            # Create continuous data array
            data = np.zeros(n_times)
            
            # Get onsets and durations from events
            onsets = events_df["onset"].values.astype(float)
            if "duration" in events_df.columns:
                durations = events_df["duration"].values.astype(float)
            else:
                durations = np.full(len(onsets), 12.0)  # Default 12s epoch duration
            
            # Get trial values
            values = events_df[col_name].values
            
            # For each event, set the channel value from onset to onset+duration
            for onset, duration, value in zip(onsets, durations, values):
                if pd.isna(value):
                    continue
                start_idx = int(round(onset * sfreq))
                end_idx = int(round((onset + duration) * sfreq))
                # Clamp to valid range
                start_idx = max(0, min(start_idx, n_times))
                end_idx = max(0, min(end_idx, n_times))
                if start_idx < end_idx:
                    data[start_idx:end_idx] = float(value)
            
            # Add the channel
            raw = _create_misc_channel(raw, misc_name, data)
    
    return raw


class ds004356Kernel:
    """Kernel for OpenNeuro ds004356 EEG ABR dataset."""

    eegunity_description = {
        "age": "str",
        "sex": "gender",
        "amplifier": "unknown",
        "cap": "unknown",
        "handedness": "unknown",
    }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply kernel processing to raw EEG data."""
        # Extract file path
        file_path = row.get("File Path", "")
        
        # Find BIDS root and read participants info
        bids_root = _find_bids_root(file_path)
        participants_df = _read_participants_tsv(bids_root)
        subject_id = _extract_subject_id(row)
        subject_info = _get_subject_info(participants_df, subject_id)
        
        # Find and read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path)
        
        # Standardize channels
        raw = _standardize_channels(raw)
        
        # Add events as annotations
        raw = _add_events_as_annotations(raw, events_df)
        
        # Add derived misc channels from events.tsv
        raw = _add_derived_misc_channels(raw, events_df)
        
        # Set subject info in raw.info
        if subject_info:
            raw.info["subject_info"] = {
                "his_id": subject_id,
                "age": int(subject_info.get("age", 0)) if subject_info.get("age", "unknown") != "unknown" else None,
                "sex": subject_info.get("gender", "unknown").upper() if subject_info.get("gender", "unknown") != "unknown" else None,
            }
        
        return raw


KERNEL = ds004356Kernel()