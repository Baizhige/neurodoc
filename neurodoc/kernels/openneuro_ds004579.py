"""OpenNeuro DS004579 stage1 kernel for EEGUnity.

Interval Timing Task dataset - 30 subjects, 64 channels, 512 Hz.
BrainVision format with S 1-S 7 timing condition events and R 3 button press responses.

This kernel handles:
- Channel renaming to standard 10-20 names (BrainVision uppercase variants)
- Metadata extraction from participants.tsv (AGE, GENDER, GROUP, MOCA, TYPE, UPDRS)
- Event annotation from *_events.tsv sidecars (BrainVision .eeg without marker file)
- Derived misc channels for GROUP and TYPE from participants.tsv

Source: https://openneuro.org/datasets/ds004579
Reference: DOI 10.1523/JNEUROSCI.1675-24.2025
"""

from __future__ import annotations

import json
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# BrainVision channel name variants -> standard 10-20 lowercase
# Source: BrainVision standard 64-channel cap layout
# Annotator: LLM, 2026-04-08
_BV_TO_STANDARD_64 = {
    "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
    "AF7": "AF7", "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4", "AF8": "AF8",
    "F7": "F7", "F5": "F5", "F3": "F3", "F1": "F1", "FZ": "Fz", "F2": "F2", "F4": "F4", "F6": "F6", "F8": "F8",
    "FT7": "FT7", "FT8": "FT8",
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FCZ": "FCz", "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    "T7": "T7", "T8": "T8",
    "C5": "C5", "C3": "C3", "C1": "C1", "CZ": "Cz", "C2": "C2", "C4": "C4", "C6": "C6",
    "TP7": "TP7", "TP8": "TP8",
    "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CPZ": "CPz", "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
    "P7": "P7", "P5": "P5", "P3": "P3", "P1": "P1", "PZ": "Pz", "P2": "P2", "P4": "P4", "P6": "P6", "P8": "P8",
    "PO7": "PO7", "PO3": "PO3", "POZ": "POz", "PO4": "PO4", "PO8": "PO8",
    "O1": "O1", "OZ": "Oz", "O2": "O2",
    "VEOG": "VEOG", "HEOG": "HEOG", "EMG": "EMG",
    "A1": "A1", "A2": "A2",
}

# Standard 64-channel extended 10-20 set for validation
_STANDARD_64_CHANNELS = {
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "T7", "T8",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "TP7", "TP8",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
}


def _find_bids_root(file_path: str) -> Optional[str]:
    """Walk upward to find BIDS root (directory containing participants.tsv)."""
    current = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # reasonable depth limit
        if os.path.isfile(os.path.join(current, "participants.tsv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    # Match patterns like sub-01, sub-1, etc.
    match = re.search(r"(sub-[a-zA-Z0-9]+)", os.path.basename(file_path))
    if match:
        return match.group(1)
    # Also try from directory structures
    parts = os.path.normpath(file_path).split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part
    return None


def _read_participants_tsv(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and extract fields for given subject."""
    result = {
        "AGE": "unknown",
        "GENDER": "unknown",
        "GROUP": "unknown",
        "MOCA": "unknown",
        "TYPE": "unknown",
        "UPDRS": "unknown",
    }
    
    participants_path = os.path.join(bids_root, "participants.tsv")
    if not os.path.isfile(participants_path):
        return result
    
    try:
        df = pd.read_csv(participants_path, sep="\t", dtype=str)
    except Exception:
        return result
    
    # Find subject row - handle both 'sub-01' and '01' formats
    sub_col = "participant_id"
    if sub_col not in df.columns:
        # Try alternatives
        for alt in ["subject_id", "Subject", "subject"]:
            if alt in df.columns:
                sub_col = alt
                break
    
    if sub_col not in df.columns:
        return result
    
    # Normalize subject_id for matching
    search_ids = [subject_id]
    if subject_id.startswith("sub-"):
        search_ids.append(subject_id[4:])  # without "sub-" prefix
    else:
        search_ids.append(f"sub-{subject_id}")
    
    subject_row = None
    for sid in search_ids:
        mask = df[sub_col].astype(str).str.strip() == sid
        if mask.any():
            subject_row = df[mask].iloc[0]
            break
    
    if subject_row is None:
        return result
    
    for field in result.keys():
        if field in subject_row.index:
            val = str(subject_row[field]).strip()
            if pd.notna(val) and val.lower() not in ("nan", "na", "n/a", "", "none"):
                result[field] = val
    
    return result


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding *_events.tsv file for a given EEG file."""
    # BrainVision: .eeg file has sibling .vhdr and _events.tsv
    base = file_path
    # Remove common extensions
    for ext in [".eeg", ".vhdr", ".vmrk", ".set", ".edf", ".bdf", ".fif"]:
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Try _events.tsv suffix
    events_path = base + "_events.tsv"
    if os.path.isfile(events_path):
        return events_path
    
    # Try in same directory with task matching
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(base)
    
    # Look for any *_events.tsv in same directory
    if os.path.isdir(dir_name):
        for fname in os.listdir(dir_name):
            if fname.endswith("_events.tsv"):
                # Check if it matches our file's task/entity
                if base_name.split("_")[0] in fname:  # sub-XX match
                    return os.path.join(dir_name, fname)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t", dtype=str)
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or events_df.empty:
        return None
    
    # Required columns
    if "onset" not in events_df.columns:
        return None
    
    # Parse onsets
    try:
        onsets = events_df["onset"].astype(float).values
    except (ValueError, TypeError):
        return None
    
    # Durations
    if "duration" in events_df.columns:
        try:
            durations = events_df["duration"].astype(float).values
        except (ValueError, TypeError):
            durations = np.zeros(len(onsets))
    else:
        durations = np.zeros(len(onsets))
    
    # Descriptions: prefer value column for this dataset (contains 'S  1', 'S  2', etc.)
    # trial_type is NOT present in this dataset's events.tsv; value is the correct column
    if "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    elif "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["event"] * len(onsets))
    
    # Filter out empty/NaN descriptions
    valid_mask = pd.notna(descriptions) & (descriptions != "nan") & (descriptions != "n/a") & (descriptions != "")
    if not valid_mask.any():
        return None
    
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    # Remove boundary events if present
    boundary_mask = ~(descriptions == "boundary")
    if boundary_mask.any() and not boundary_mask.all():
        onsets = onsets[boundary_mask]
        durations = durations[boundary_mask]
        descriptions = descriptions[boundary_mask]
    
    if len(onsets) == 0:
        return None
    
    # MNE Annotations use seconds for onset - already in seconds from BIDS
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _rename_channels_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename BrainVision uppercase channels to standard 10-20 lowercase."""
    rename_map = {}
    for ch_name in raw.ch_names:
        upper = ch_name.upper()
        if upper in _BV_TO_STANDARD_64:
            target = _BV_TO_STANDARD_64[upper]
            if ch_name != target:
                rename_map[ch_name] = target
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _add_misc_channel(raw: mne.io.BaseRaw, name: str, value: float) -> mne.io.BaseRaw:
    """Add a constant-valued misc channel to the raw object."""
    # Create data array with constant value
    data = np.full((1, len(raw.times)), value, dtype=raw._data.dtype)
    
    # Create info for new channel
    info = mne.create_info([name], raw.info["sfreq"], ch_types="misc")
    
    # Create RawArray and append
    misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    
    # Add to existing raw
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


class OpenNeuroDS004579Kernel:
    KERNEL_ID = "openneuro_ds004579"
    DATASET_NAME = "OpenNeuro DS004579 - Interval Timing Task"
    FORMAT = "BrainVision"
    SFREQ = 512.0
    N_CHANNELS = 64
    
    # Required info fields from participants.tsv -> eegunity_description mapping
    REQUIRED_INFO_FIELDS = {
        "AGE": "age",
        "GENDER": "sex",
    }
    
    # Derived misc channels from participants.tsv (constant broadcast)
    DERIVED_MISC_CHANNELS = ["GROUP", "TYPE"]
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Step 1: Rename channels to standard 10-20
        raw = _rename_channels_to_standard(raw)
        
        # Step 2: Find BIDS root and extract subject metadata
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        bids_root = _find_bids_root(file_path)
        subject_id = _get_subject_id_from_path(file_path)
        
        # Default metadata
        participant_info = {
            "AGE": "unknown",
            "GENDER": "unknown",
            "GROUP": "unknown",
            "MOCA": "unknown",
            "TYPE": "unknown",
            "UPDRS": "unknown",
        }
        
        if bids_root and subject_id:
            participant_info = _read_participants_tsv(bids_root, subject_id)
        
        # Step 3: Build eegunity_description from required fields
        eegunity_description = {
            "age": str(participant_info.get("AGE", "unknown")),
            "sex": str(participant_info.get("GENDER", "unknown")),
            "amplifier": "BrainVision",
            "cap": "BrainVision 64-channel standard cap",
            "handedness": "unknown",
        }
        
        # Step 4: Set description as JSON string (MNE stores description as string)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Step 5: Load events from BIDS events.tsv sidecar and set annotations
        # The .set files have empty event fields; events MUST come from events.tsv
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_df = _read_events_tsv(events_tsv_path)
            annotations = _events_to_annotations(events_df, raw.info["sfreq"])
            if annotations is not None:
                raw.set_annotations(annotations)
        
        # Step 6: Add derived misc channels from participants.tsv
        for field in self.DERIVED_MISC_CHANNELS:
            value_str = participant_info.get(field, "unknown")
            # Try to convert to numeric, fallback to hash for string values
            try:
                value = float(value_str)
            except (ValueError, TypeError):
                # Use simple hash for string categories
                value = float(hash(value_str) % 10000)
            
            raw = _add_misc_channel(raw, field, value)
        
        return raw


KERNEL = OpenNeuroDS004579Kernel()