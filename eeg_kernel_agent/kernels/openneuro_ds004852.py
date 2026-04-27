"""openneuro_ds004852 stage1 kernel for EEGUnity.

InsurgentCivilian (Social-Cognitive EEG Dataset)
BIDS-compliant OpenNeuro dataset with BrainVision format.
64 channels, 128 Hz, single subject.

Tasks supported:
  - 9-class n-back working memory load (events 2090-2098)
  - Binary n-back low vs high load
  - Task Phase Detection

Source: https://doi.org/10.18112/openneuro.ds004852.v1.0.0
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


# LLM 推断，需人类复核
# Based on OpenNeuro ds004852 dataset_description.json and README
# Device info from typical BrainVision setups in military/cognitive research
# Annotator: LLM, 2026-04-08
_AMPLIFIER = "BrainAmp MR plus"  # LLM 推断，需人类复核
_CAP = "Ag/AgCl"  # LLM 推断，需人类复核

# Required info fields from participants.tsv to include in eegunity_description
kernel_requirements = {
    "required_info_fields": ["group", "military_experience", "combat_exposure"],
    "required_native_misc": [],
    "derived_misc_channels": [],
}

# Standard 10-20 channel names for 64-channel BrainVision cap
# Source: BrainVision standard 64-channel cap layout
# Annotator: LLM, 2026-04-08
_STANDARD_64_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5",
    "FC1", "FC2", "FC6", "T7", "C3", "Cz", "C4", "T8",
    "TP9", "CP5", "CP1", "CP2", "CP6", "TP10", "P7", "P3",
    "Pz", "P4", "P8", "PO9", "O1", "Oz", "O2", "PO10",
    "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6",
    "FT9", "FT7", "FC3", "FC4", "FT8", "FT10", "C5", "C1",
    "C2", "C6", "TP7", "CP3", "CPz", "CP4", "TP8", "P5",
    "P1", "P2", "P6", "PO7", "PO3", "POz", "PO4", "PO8",
]

# BrainVision default channel naming patterns that need renaming
# Source: BrainVision standard naming conventions
# Annotator: LLM, 2026-04-08
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Common BrainVision aliases to standard 10-20
    "FP1": "Fp1",
    "FP2": "Fp2",
    "FZ": "Fz",
    "CZ": "Cz",
    "PZ": "Pz",
    "POZ": "POz",
    "OZ": "Oz",
    "FCZ": "FCz",
    "CPZ": "CPz",
    # Numbered EEG channels to standard names (if needed)
}

# Event code to description mapping for raw meta
# Based on analysis.md Event Structure table
# Annotator: LLM, 2026-04-08
_RAW_EVENT_MAP: Dict[str, str] = {
    "1": "response/button press event",
    "1103": "task-related marker",
    "1113": "task-related marker",
    "2090": "0-back condition",
    "2091": "1-back condition",
    "2092": "2-back condition",
    "2093": "3-back condition",
    "2094": "4-back condition",
    "2095": "5-back condition",
    "2096": "6-back condition",
    "2097": "7-back condition",
    "2098": "8-back condition",
    "2200": "stimulus recycling/re-display",
    "2201": "primary condition code (variant)",
    "3": "administration event",
    "307": "rare administration marker",
    "4": "administration event",
    "5": "administration event",
    "51001": "category 5 sub-condition",
    "51011": "category 5 stimulus variant",
    "51110": "category 5 sub-condition",
    "52001": "category 5 sub-condition",
    "52011": "category 5 stimulus",
    "52100": "category 5 sub-condition",
    "52101": "category 5 sub-condition",
    "52110": "category 5 sub-condition",
    "52111": "category 5 sub-condition",
    "53001": "category 5 sub-condition",
    "53011": "category 5 stimulus",
    "53100": "category 5 sub-condition",
    "53110": "category 5 sub-condition",
    "53111": "category 5 sub-condition",
    "54001": "category 5 sub-condition",
    "54011": "category 5 stimulus",
    "54100": "category 5 sub-condition",
    "54101": "category 5 sub-condition",
    "54110": "category 5 sub-condition",
    "54111": "category 5 sub-condition",
    "55000": "category 5 sub-condition",
    "55001": "category 5 sub-condition",
    "55010": "category 5 sub-condition",
    "55011": "category 5 stimulus",
    "55100": "category 5 sub-condition",
    "55101": "category 5 sub-condition",
    "55110": "category 5 sub-condition",
    "55111": "category 5 sub-condition",
    "71001": "category 7 sub-condition",
    "71011": "category 7 stimulus variant",
    "71110": "category 7 sub-condition",
    "72001": "category 7 sub-condition",
    "72011": "category 7 stimulus",
    "72100": "category 7 sub-condition",
    "72101": "category 7 sub-condition",
    "72110": "category 7 sub-condition",
    "72111": "category 7 sub-condition",
    "73001": "category 7 sub-condition",
    "73011": "category 7 stimulus",
    "73100": "category 7 sub-condition",
    "73110": "category 7 sub-condition",
    "73111": "category 7 sub-condition",
    "74001": "category 7 sub-condition",
    "74011": "category 7 stimulus",
    "74100": "category 7 sub-condition",
    "74101": "category 7 sub-condition",
    "74110": "category 7 sub-condition",
    "74111": "category 7 sub-condition",
    "75000": "category 7 sub-condition",
    "75001": "category 7 sub-condition",
    "75010": "category 7 sub-condition",
    "75011": "category 7 stimulus",
    "75100": "category 7 sub-condition",
    "75101": "category 7 sub-condition",
    "75110": "category 7 sub-condition",
    "75111": "category 7 sub-condition",
}


def _get_bids_root(file_path: str) -> Optional[str]:
    """Extract BIDS root directory from file path."""
    if not file_path:
        return None
    
    # Walk up to find dataset root (contains participants.tsv)
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at filesystem root
        if os.path.exists(os.path.join(current_dir, "participants.tsv")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    return None


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    if not file_path:
        return None
    
    # Match sub-XX pattern
    match = os.path.basename(file_path)
    # Look for sub- prefix in path components
    parts = file_path.replace("\\", "/").split("/")
    for part in parts:
        if part.startswith("sub-"):
            return part
    
    return None


def _read_participants_tsv(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "group": "unknown",
        "military_experience": "unknown",
        "combat_exposure": "unknown",
    }
    
    participants_path = os.path.join(bids_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return info
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        
        # Find subject row
        subj_col = "participant_id"
        if subj_col not in df.columns:
            # Try alternative column names
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    subj_col = col
                    break
        
        subject_row = df[df[subj_col] == subject_id]
        if subject_row.empty:
            # Try without sub- prefix
            subject_row = df[df[subj_col] == subject_id.replace("sub-", "")]
        
        if not subject_row.empty:
            row = subject_row.iloc[0]
            
            # Age
            if "age" in df.columns:
                age_val = row["age"]
                if pd.notna(age_val):
                    info["age"] = str(int(float(age_val)))
            
            # Sex
            if "sex" in df.columns:
                sex_val = row["sex"]
                if pd.notna(sex_val):
                    sex_str = str(sex_val).lower().strip()
                    if sex_str in ("m", "male"):
                        info["sex"] = "male"
                    elif sex_str in ("f", "female"):
                        info["sex"] = "female"
            
            # Handedness
            if "handedness" in df.columns:
                hand_val = row["handedness"]
                if pd.notna(hand_val):
                    hand_str = str(hand_val).lower().strip()
                    if hand_str in ("r", "right"):
                        info["handedness"] = "right"
                    elif hand_str in ("l", "left"):
                        info["handedness"] = "left"
                    elif hand_str in ("a", "ambidextrous"):
                        info["handedness"] = "ambidextrous"
            
            # Required fields from kernel_requirements
            for field in kernel_requirements.get("required_info_fields", []):
                if field in df.columns:
                    field_val = row[field]
                    if pd.notna(field_val):
                        info[field] = str(field_val)
                    else:
                        info[field] = "unknown"
                else:
                    info[field] = "unknown"
                    
    except Exception as e:
        warnings.warn(f"Error reading participants.tsv: {e}")
    
    return info


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events from BIDS events.tsv file."""
    if not os.path.exists(events_path):
        return None
    
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception as e:
        warnings.warn(f"Error reading events.tsv: {e}")
        return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv for a given data file."""
    if not file_path:
        return None
    
    # For BrainVision files, events.tsv is in the same directory
    base = os.path.splitext(file_path)[0]
    # Remove .eeg or .vhdr or .vmrk extension
    for ext in [".eeg", ".vhdr", ".vmrk", ".set", ".fdt"]:
        if base.endswith(ext):
            base = base[:-len(ext)]
    
    # Try same directory
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try with task suffix pattern
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(base)
    
    # Look for any events.tsv in the same directory
    for f in os.listdir(dir_name) if os.path.isdir(dir_name) else []:
        if f.endswith("_events.tsv"):
            return os.path.join(dir_name, f)
    
    return None


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 naming."""
    rename_map = {}
    for ch_name in raw.ch_names:
        upper = ch_name.upper()
        if upper in _CHANNEL_RENAME_MAP:
            rename_map[ch_name] = _CHANNEL_RENAME_MAP[upper]
        elif ch_name in _CHANNEL_RENAME_MAP:
            rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


def _set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for 64-channel cap."""
    try:
        # Try to set standard_1020 montage
        montage = mne.channels.make_standard_montage("standard_1020")
        raw = raw.set_montage(montage, match_case=False, on_missing="warn")
    except Exception as e:
        warnings.warn(f"Could not set montage: {e}")
    
    return raw


def _add_events_from_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add events from BIDS events.tsv to raw as annotations."""
    if events_df is None or events_df.empty:
        return raw
    
    # Required columns for events
    onset_col = None
    duration_col = None
    trial_type_col = None
    
    for col in events_df.columns:
        col_lower = col.lower()
        if col_lower in ("onset", "onsets"):
            onset_col = col
        elif col_lower in ("duration", "durations"):
            duration_col = col
        elif col_lower in ("trial_type", "trialtype", "event_type", "eventtype", "stim_type", "value"):
            trial_type_col = col
    
    if onset_col is None:
        warnings.warn("No onset column found in events.tsv")
        return raw
    
    # Default duration if not specified
    if duration_col is None:
        durations = np.zeros(len(events_df))
    else:
        durations = events_df[duration_col].fillna(0).values
    
    # Default description if trial_type not found
    if trial_type_col is None:
        # Try to find any meaningful column for description
        for col in events_df.columns:
            if col not in (onset_col, duration_col):
                trial_type_col = col
                break
    
    if trial_type_col is None:
        descriptions = ["event"] * len(events_df)
    else:
        descriptions = events_df[trial_type_col].astype(str).tolist()
    
    onsets = events_df[onset_col].values
    
    # Create annotations
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )
    
    # Set annotations on raw
    raw = raw.set_annotations(annotations)
    
    return raw


def _add_stim_channel(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Add a stimulus channel from annotations if needed."""
    # Check if annotations exist
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    # Try to create stim channel from annotations
    try:
        # Get events from annotations
        events, event_id = mne.events_from_annotations(raw)
        
        if len(events) > 0:
            # Add stim channel
            stim_data = np.zeros((1, len(raw.times)))
            
            # Create info for stim channel
            stim_info = mne.create_info(
                ["STI 014"],
                raw.info["sfreq"],
                ["stim"],
            )
            stim_raw = mne.io.RawArray(stim_data, stim_info, first_samp=raw.first_samp)
            
            # Add to raw
            raw = raw.add_channels([stim_raw], force_update_info=True)
            
            # Add events to stim channel
            for event in events:
                sample = event[0] - raw.first_samp
                if 0 <= sample < len(raw.times):
                    raw._data[raw.ch_names.index("STI 014"), sample] = event[2]
    except Exception as e:
        warnings.warn(f"Could not add stim channel: {e}")
    
    return raw


class OpenNeuroDS004852Kernel:
    KERNEL_ID = "openneuro_ds004852"
    DATASET_NAME = "openneuro_ds004852"
    BIDS_COMPATIBLE = True
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        
        # Get BIDS root and subject info
        bids_root = _get_bids_root(file_path)
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants info
        participant_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "group": "unknown",
            "military_experience": "unknown",
            "combat_exposure": "unknown",
        }
        if bids_root and subject_id:
            participant_info = _read_participants_tsv(bids_root, subject_id)
        
        # Rename channels to standard 10-20
        raw = _rename_channels(raw)
        
        # Set montage
        raw = _set_montage(raw)
        
        # Find and read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = None
        if events_path:
            events_df = _read_events_tsv(events_path)
        
        # Add events from events.tsv as annotations
        if events_df is not None:
            raw = _add_events_from_tsv(raw, events_df)
        
        # Set eeg reference
        try:
            raw = raw.set_eeg_reference("average", projection=True)
        except Exception as e:
            warnings.warn(f"Could not set average reference: {e}")
        
        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_description = {
            "age": str(participant_info.get("age", "unknown")),
            "sex": participant_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": participant_info.get("handedness", "unknown"),
            "group": participant_info.get("group", "unknown"),
            "military_experience": participant_info.get("military_experience", "unknown"),
            "combat_exposure": participant_info.get("combat_exposure", "unknown"),
        }
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS004852Kernel()