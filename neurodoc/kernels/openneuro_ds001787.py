"""OpenNeuro DS001787 stage1 kernel for EEGUnity.

EEG Meditation Study - Focused meditation with 2-min probe interruptions.
80-channel BioSemi ActiveTwo system (64 EEG + 16 misc including GSR, Plet, Resp, Temp).
24 subjects (12 expert, 12 novice meditators).

Source: https://openneuro.org/datasets/ds001787
Paradigm: Focused meditation with probe-based sustained attention assessment
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Required info fields from participants.tsv (kernel_requirements)
# ============================================================================
_REQUIRED_INFO_FIELDS = ["age", "gender", "group"]

# ============================================================================
# Required native misc channels (already in raw data, ensure type is 'misc')
# ============================================================================
# From analysis.md: B1-B32, EXG1-EXG5 are native misc channels
_REQUIRED_NATIVE_MISC = [
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10",
    "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20",
    "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30",
    "B31", "B32",
    "EXG1", "EXG2", "EXG3", "EXG4", "EXG5",
]

# ============================================================================
# Required derived misc channels (kernel MUST create these)
# ============================================================================
# No derived misc channels required for this dataset
_REQUIRED_DERIVED_MISC: List[str] = []

# ============================================================================
# BioSemi ActiveTwo 64-channel standard naming
# ============================================================================
# Source: BioSemi 64-channel cap layout (standard_1020 extension)
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_BIOSEMI_64_CH_NAMES = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2",
]


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # Match sub-XX pattern
    match = re.search(r'sub-(\w+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to the data file."""
    # Walk up from file to find dataset root
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # Limit search depth
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding *_events.tsv for a data file."""
    # BIDS convention: same directory, same base name with _events.tsv suffix
    base = file_path.replace(".bdf", "").replace(".edf", "").replace(".set", "").replace(".eeg", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Also check in the same directory
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    # Remove extension
    base_no_ext = re.sub(r'\.(bdf|edf|set|eeg|fif|vhdr)$', '', base_name, flags=re.IGNORECASE)
    events_path = os.path.join(dir_name, base_no_ext + "_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    df = pd.read_csv(participants_path, sep='\t')
    
    # Find row for this subject
    # participant_id may be 'sub-01' or just '01'
    if 'participant_id' not in df.columns:
        return {}
    
    # Try exact match first
    row = df[df['participant_id'] == subject_id]
    if row.empty:
        # Try without 'sub-' prefix
        short_id = subject_id.replace('sub-', '')
        row = df[df['participant_id'] == short_id]
        if row.empty:
            # Try with 'sub-' prefix
            row = df[df['participant_id'] == f"sub-{short_id}"]
    
    if row.empty:
        return {}
    
    info = {}
    row_data = row.iloc[0]
    
    for field in _REQUIRED_INFO_FIELDS:
        if field in row_data.index:
            val = row_data[field]
            # Handle NaN
            if pd.isna(val):
                info[field] = "unknown"
            else:
                info[field] = str(val).strip()
        else:
            info[field] = "unknown"
    
    return info


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events from BIDS events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep='\t')
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame) -> Optional[mne.Annotations]:
    """Convert BIDS events DataFrame to MNE Annotations."""
    if events_df is None or events_df.empty:
        return None
    
    # Required columns: onset, (optional: duration, trial_type, value)
    if 'onset' not in events_df.columns:
        return None
    
    onsets = events_df['onset'].values.astype(float)
    durations = events_df['duration'].values.astype(float) if 'duration' in events_df.columns else np.zeros(len(onsets))
    
    # Description: prefer trial_type, then value, then fallback
    descriptions = []
    for _, row in events_df.iterrows():
        if 'trial_type' in row and pd.notna(row['trial_type']) and str(row['trial_type']).strip():
            desc = str(row['trial_type']).strip()
        elif 'value' in row and pd.notna(row['value']):
            desc = str(row['value']).strip()
        else:
            desc = "unknown"
        descriptions.append(desc)
    
    # Filter out any invalid rows
    valid_mask = np.isfinite(onsets)
    onsets = onsets[valid_mask]
    durations = durations[valid_mask] if len(durations) == len(valid_mask) else np.zeros(np.sum(valid_mask))
    descriptions = [d for i, d in enumerate(descriptions) if valid_mask[i]]
    
    if len(onsets) == 0:
        return None
    
    # Ensure durations match
    if len(durations) != len(onsets):
        durations = np.zeros(len(onsets))
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS001787Kernel:
    """Stage1 kernel for OpenNeuro ds001787 (EEG Meditation Study)."""

    KERNEL_ID: str = "openneuro-ds001787-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # =====================================================================
        # 1. Extract subject ID and read participants.tsv
        # =====================================================================
        subject_id = _get_subject_id_from_path(file_path)
        participants_path = _find_participants_tsv(file_path) if subject_id else None
        
        participant_info: Dict[str, str] = {}
        if participants_path and subject_id:
            participant_info = _read_participants_info(participants_path, subject_id)
        
        # =====================================================================
        # 2. Build eegunity_description
        # =====================================================================
        # Map participants.tsv fields to required eegunity_description fields
        age = participant_info.get("age", "unknown")
        # Map gender -> sex
        sex = participant_info.get("gender", "unknown")
        # group field for handedness (expert/novice -> use as handedness or unknown)
        group = participant_info.get("group", "unknown")
        
        # For this dataset, handedness is not in participants.tsv, use unknown
        handedness = "unknown"
        
        eegunity_description = {
            "age": str(age),
            "sex": str(sex),
            "amplifier": "BioSemi ActiveTwo",
            "cap": "BioSemi 64-channel cap",
            "handedness": str(handedness),
        }
        
        # =====================================================================
        # 3. Set raw.info["description"] as JSON string
        # =====================================================================
        original_description = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # =====================================================================
        # 4. Ensure native misc channels are typed correctly
        # =====================================================================
        # Set channel types for B1-B32 and EXG1-EXG5 to 'misc'
        new_types = {}
        for ch_name in raw.ch_names:
            if ch_name in _REQUIRED_NATIVE_MISC:
                new_types[ch_name] = "misc"
        
        if new_types:
            raw.set_channel_types(new_types)
        
        # =====================================================================
        # 5. Handle events/annotations from events.tsv
        # =====================================================================
        # BDF files from BioSemi may not carry annotations natively.
        # We MUST load events from the sibling *_events.tsv and attach them
        # via raw.set_annotations() so that mne.events_from_annotations(raw)
        # yields at least as many events as non-empty rows in events.tsv.
        events_path = _find_events_tsv(file_path)
        if events_path:
            events_df = _read_events_tsv(events_path)
            annotations = _events_to_annotations(events_df)
            if annotations is not None:
                # CRITICAL: use set_annotations, not assignment to raw.info
                raw.set_annotations(annotations)
        
        # =====================================================================
        # 6. Return processed raw
        # =====================================================================
        return raw


# Module-level assignment required by EEGUnity
KERNEL = OpenNeuroDS001787Kernel()