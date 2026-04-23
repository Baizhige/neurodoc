"""openneuro_ds004000 stage1 kernel for EEGUnity.

Fribourg Ultimatum Game in Schizophrenia Study.
BIDS dataset with BrainVision .vhdr/.vmrk/.eeg files, 43 subjects, 132 channels, 2048 Hz.

This kernel:
- Loads participant metadata from participants.tsv (group field required)
- Ensures EXG1 is typed as misc channel
- Derives annotations from events.tsv when needed (BrainVision .vmrk may not carry all triggers)
- Sets standard 10-20 montage after channel renaming

Source: https://openneuro.org/datasets/ds004000 (v1.0.0)
Evidence: 10.1016/j.schres.2017.05.037, 10.1016/j.schres.2023.01.029
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Event code mapping (raw meta)
# Source: analysis.md Event Structure table
# Annotator: Human, 2026-04-08
# =============================================================================
_EVENT_CODE_MAP = {
    # Segment and timing markers
    "New Segment/": "New Segment/",
    "Time 0/": "Time 0/",
    # Response markers
    "Response/R  1": "Response/R  1",
    "Response/R  3": "Response/R  3",
    # Phase/instruction markers
    "Stimulus/S  1": "Stimulus/S  1",
    "Stimulus/S  2": "Stimulus/S  2",
    "Stimulus/S  3": "Stimulus/S  3",
    "Stimulus/S  4": "Stimulus/S  4",
    # Responder condition offer onsets
    "Stimulus/S 64": "Stimulus/S 64",
    "Stimulus/S 96": "Stimulus/S 96",
    "Stimulus/S128": "Stimulus/S128",
    "Stimulus/S160": "Stimulus/S160",
    # Partner type A offer markers
    "Stimulus/S193": "Stimulus/S193",
    "Stimulus/S194": "Stimulus/S194",
    "Stimulus/S195": "Stimulus/S195",
    "Stimulus/S196": "Stimulus/S196",
    "Stimulus/S197": "Stimulus/S197",
    "Stimulus/S198": "Stimulus/S198",
    "Stimulus/S199": "Stimulus/S199",
    "Stimulus/S200": "Stimulus/S200",
    "Stimulus/S201": "Stimulus/S201",
    # Partner type B offer markers
    "Stimulus/S225": "Stimulus/S225",
    "Stimulus/S226": "Stimulus/S226",
    "Stimulus/S227": "Stimulus/S227",
    "Stimulus/S228": "Stimulus/S228",
    "Stimulus/S229": "Stimulus/S229",
    "Stimulus/S230": "Stimulus/S230",
    "Stimulus/S231": "Stimulus/S231",
    "Stimulus/S232": "Stimulus/S232",
    "Stimulus/S233": "Stimulus/S233",
    # Admin markers
    "UserDefined/Blink": "UserDefined/Blink",
}

# Numeric codes that may appear in BrainVision .vmrk files
# Source: BrainVision marker format analysis
# Annotator: Human, 2026-04-08
_NUMERIC_CODE_MAP = {
    "1": "Response/R  1",
    "3": "Response/R  3",
    "64": "Stimulus/S 64",
    "96": "Stimulus/S 96",
    "128": "Stimulus/S128",
    "160": "Stimulus/S160",
    "193": "Stimulus/S193",
    "194": "Stimulus/S194",
    "195": "Stimulus/S195",
    "196": "Stimulus/S196",
    "197": "Stimulus/S197",
    "198": "Stimulus/S198",
    "199": "Stimulus/S199",
    "200": "Stimulus/S200",
    "201": "Stimulus/S201",
    "225": "Stimulus/S225",
    "226": "Stimulus/S226",
    "227": "Stimulus/S227",
    "228": "Stimulus/S228",
    "229": "Stimulus/S229",
    "230": "Stimulus/S230",
    "231": "Stimulus/S231",
    "232": "Stimulus/S232",
    "233": "Stimulus/S233",
}


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if present."""
    pth = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(pth):
        return pd.read_csv(pth, sep="\t")
    return pd.DataFrame()


def _get_subject_info(dataset_root: str, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.
    
    Returns dict with age, sex, handedness, group for the given subject.
    Missing values are set to "unknown".
    
    Annotator: Human, 2026-04-08
    Source: participants.tsv columns
    """
    df = _load_participants_tsv(dataset_root)
    if df.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "group": "unknown",
        }
    
    # Match subject_id (case-insensitive, handle sub- prefix)
    clean_id = subject_id.lower().replace("sub-", "")
    match_rows = df[
        df["participant_id"].str.lower().str.replace("sub-", "", regex=False) == clean_id
    ]
    
    if match_rows.empty:
        # Try exact match with sub- prefix
        match_rows = df[
            df["participant_id"].str.lower() == subject_id.lower()
        ]
    
    if match_rows.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
            "group": "unknown",
        }
    
    row = match_rows.iloc[0]
    
    age_val = "unknown"
    if "age" in df.columns:
        raw_age = row.get("age")
        if pd.notna(raw_age):
            try:
                age_val = str(int(float(raw_age)))
            except (ValueError, TypeError):
                age_val = str(raw_age).strip()
                if age_val == "":
                    age_val = "unknown"
    
    sex_val = "unknown"
    if "sex" in df.columns:
        raw_sex = row.get("sex")
        if pd.notna(raw_sex):
            sex_str = str(raw_sex).strip().lower()
            if sex_str in ("m", "male"):
                sex_val = "male"
            elif sex_str in ("f", "female"):
                sex_val = "female"
            else:
                sex_val = "unknown"
    
    handed_val = "unknown"
    if "handedness" in df.columns:
        raw_handed = row.get("handedness")
        if pd.notna(raw_handed):
            handed_str = str(raw_handed).strip().lower()
            if handed_str in ("r", "right"):
                handed_val = "right"
            elif handed_str in ("l", "left"):
                handed_val = "left"
            else:
                handed_val = "unknown"
    
    group_val = "unknown"
    if "group" in df.columns:
        raw_group = row.get("group")
        if pd.notna(raw_group):
            group_val = str(raw_group).strip()
            if group_val == "":
                group_val = "unknown"
    
    return {
        "age": age_val,
        "sex": sex_val,
        "handedness": handed_val,
        "group": group_val,
    }


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # BrainVision files: .vhdr, .eeg, .vmrk
    base = file_path
    for ext in [".vhdr", ".eeg", ".vmrk", ".edf", ".set", ".fif"]:
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Try BIDS-style naming: sub-X_task-Y_run-Z_events.tsv
    # or just alongside the file
    candidates = [
        base + "_events.tsv",
        base.replace("_eeg", "") + "_events.tsv",
    ]
    
    # Also try to find in the same directory with pattern matching
    dir_path = os.path.dirname(file_path)
    if dir_path:
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                # Check if it matches our subject/task
                file_sub = _extract_subject_id(file_path)
                event_sub = _extract_subject_id(f)
                if file_sub and event_sub and file_sub.lower() == event_sub.lower():
                    candidates.append(os.path.join(dir_path, f))
    
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    
    return None


def _extract_subject_id(file_name: str) -> Optional[str]:
    """Extract subject ID from BIDS filename."""
    match = re.search(r'sub-([a-zA-Z0-9]+)', os.path.basename(file_name))
    if match:
        return match.group(1)
    return None


def _extract_task_name(file_name: str) -> Optional[str]:
    """Extract task name from BIDS filename."""
    match = re.search(r'task-([a-zA-Z0-9]+)', os.path.basename(file_name))
    if match:
        return match.group(1)
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not os.path.exists(events_path):
        return None
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations.
    
    HC-5: Pass literal tsv labels through to raw.annotations (no remapping).
    """
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required BIDS columns: onset, duration, trial_type (or value/description)
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = row.get("onset")
        if pd.isna(onset):
            continue
        
        duration = row.get("duration", 0.0)
        if pd.isna(duration):
            duration = 0.0
        
        # Use trial_type if available, else value, else description
        desc = None
        for col in ["trial_type", "value", "description"]:
            if col in events_df.columns:
                val = row.get(col)
                if pd.notna(val):
                    desc = str(val).strip()
                    break
        
        if desc is None:
            desc = "unknown"
        
        onsets.append(float(onset))
        durations.append(float(duration))
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _get_dataset_root(file_path: str) -> str:
    """Find dataset root from file path (contains participants.tsv)."""
    current = os.path.dirname(file_path)
    for _ in range(10):  # Limit search depth
        if os.path.exists(os.path.join(current, "participants.tsv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Fallback: return parent of file's directory
    return os.path.dirname(os.path.dirname(file_path))


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 naming where applicable.
    
    This dataset uses standard 10-20 with some non-standard names.
    """
    # Mapping for known non-standard names in this dataset
    rename_map = {}
    
    # Common BrainVision EXG channels -> standard names
    exg_mapping = {
        "EXG1": "EXG1",
        "EXG2": "EXG2",
        "EXG3": "EXG3",
        "EXG4": "EXG4",
        "EXG5": "EXG5",
        "EXG6": "EXG6",
        "EXG7": "EXG7",
        "EXG8": "EXG8",
    }
    
    for old_name in raw.ch_names:
        if old_name in exg_mapping:
            rename_map[old_name] = exg_mapping[old_name]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set channel types for non-EEG channels."""
    channel_types = {}
    
    for ch_name in raw.ch_names:
        upper = ch_name.upper()
        if upper.startswith("EXG"):
            channel_types[ch_name] = "misc"
        elif upper.startswith("EOG"):
            channel_types[ch_name] = "eog"
        elif upper.startswith("ECG") or upper == "EKG":
            channel_types[ch_name] = "ecg"
        elif "EMG" in upper:
            channel_types[ch_name] = "emg"
    
    if channel_types:
        raw.set_channel_types(channel_types)
    
    return raw


def _set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for EEG channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass
    return raw


@dataclass
class OpenneuroDs004000Kernel:
    """Kernel for openneuro_ds004000 dataset."""
    
    KERNEL_ID: str = "openneuro_ds004000"
    DATASET_NAME: str = "openneuro_ds004000"
    REQUIRED_INFO_FIELDS: List[str] = None
    DERIVED_MISC_CHANNELS: List[str] = None
    
    def __post_init__(self):
        if self.REQUIRED_INFO_FIELDS is None:
            self.REQUIRED_INFO_FIELDS = ["age", "sex", "handedness", "group"]
        if self.DERIVED_MISC_CHANNELS is None:
            self.DERIVED_MISC_CHANNELS = []
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply kernel transformations to raw EEG data."""
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        dataset_root = _get_dataset_root(file_path)
        subject_id = _extract_subject_id(file_path) or "unknown"
        
        # Get participant info
        subject_info = _get_subject_info(dataset_root, subject_id)
        
        # Rename channels to standard names
        raw = _rename_channels(raw)
        
        # Set channel types (EXG1 -> misc, etc.)
        raw = _set_channel_types(raw)
        
        # Set montage
        raw = _set_montage(raw)
        
        # Handle events/annotations
        events_tsv = _find_events_tsv(file_path)
        if events_tsv:
            events_df = _read_events_tsv(events_tsv)
            if events_df is not None and not events_df.empty:
                # Check if raw already has meaningful annotations
                existing_annotations = raw.annotations
                has_meaningful_annotations = (
                    len(existing_annotations) > 0 and
                    not all(d.startswith("New Segment") or d == "BAD boundary" or d == "EDGE boundary" 
                           for d in existing_annotations.description)
                )
                
                if not has_meaningful_annotations:
                    # Use events.tsv annotations (HC-5: pass literal labels)
                    new_annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                    if len(new_annotations) > 0:
                        raw.set_annotations(new_annotations)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenneuroDs004000Kernel()