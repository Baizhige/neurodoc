"""OpenNeuro DS005185 (EESM19) stage1 kernel for EEGUnity.

Ear-EEG Sleep Monitoring 2019 dataset.
- 20 subjects, 25 channels, 500 Hz sampling rate
- Sleep stage labels extracted from PSG sidecar scoring events.tsv files
- Events: Danish protocol markers (Lights Out, Gik i seng, Stod op, Vagen)
- Admin markers to exclude: trigger (sync), Biocalibrations, Sync, Start af maling
- Derived misc channels: has_arousal (from scoring events.tsv), written_time, pressed_trigger (from diary events.tsv)

Source: https://openneuro.org/datasets/ds005185
       DOI: 10.1038/s41598-019-53115-3
       DOI: 10.1038/s41597-025-04579-8
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
# Required info fields from participants.tsv
# =============================================================================
_REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness"]

# =============================================================================
# Required native misc channels (already in raw data, ensure type is 'misc')
# =============================================================================
_REQUIRED_NATIVE_MISC = []

# =============================================================================
# Derived misc channels to create
# =============================================================================
_DERIVED_MISC_CHANNELS = ["has_arousal", "written_time", "pressed_trigger"]

# =============================================================================
# Event name standardization mapping
# Raw Danish/English event names -> canonical names for EEGUnity
# =============================================================================
_EVENT_RENAME_MAP = {
    # Admin events (excluded from classification)
    "trigger": "trigger",
    "Biocalibrations": "Biocalibrations",
    "Biocalibrations start": "Biocalibrations start",
    "Sync": "Sync",
    "Start af maling": "Start_of_recording",
    # Event markers (kept for potential use)
    "Lights Out": "Lights_Out",
    "Gik i seng": "Went_to_Bed",
    "Stod op": "Got_up",
    "Vagen": "Awake",
    "vagen": "Awake",
    # Sleep stage events (from PSG scoring sidecars, raw meta)
    "Sleep stage W": "s1",
    "Sleep stage N1": "s3",
    "Sleep stage N2": "s4",
    "Sleep stage N3": "s5",
    "Sleep stage REM": "s2",
    "Sleep stage ?": "s8",
    "Sleep stage A": "s6",
    "Sleep stage M": "s6",
    "Movement": "s6",
    "Artefact": "s7",
    "Unscored": "s8",
    # Additional standardizations
    "Electrodetest": "Electrodetest",
}

# =============================================================================
# Sleep stage to canonical event ID mapping
# =============================================================================
_SLEEP_STAGE_MAP = {
    "s1": "s1",  # Wake
    "s2": "s2",  # REM
    "s3": "s3",  # N1
    "s4": "s4",  # N2
    "s5": "s5",  # N3
    "s6": "s6",  # A/Movement
    "s7": "s7",  # Artefact
    "s8": "s8",  # Unscored
}

# =============================================================================
# Channel Mapping for Ear-EEG
# EESM19 uses custom in-ear electrode layout with 25 channels
# Source: DOI 10.1038/s41597-025-04579-8 supplementary electrode positions
# Annotator: Human, 2026-04-08
# =============================================================================
_EAR_EEG_CHANNEL_MAP: Dict[str, str] = {
    # Left ear channels (custom in-ear EEG electrodes)
    "EEG 01": "E1_L",
    "EEG 02": "E2_L",
    "EEG 03": "E3_L",
    "EEG 04": "E4_L",
    "EEG 05": "E5_L",
    "EEG 06": "E6_L",
    "EEG 07": "E7_L",
    "EEG 08": "E8_L",
    # Right ear channels (custom in-ear EEG electrodes)
    "EEG 09": "E1_R",
    "EEG 10": "E2_R",
    "EEG 11": "E3_R",
    "EEG 12": "E4_R",
    "EEG 13": "E5_R",
    "EEG 14": "E6_R",
    "EEG 15": "E7_R",
    "EEG 16": "E8_R",
    # Scalp reference channels
    "EEG 17": "M1",
    "EEG 18": "M2",
    "EEG 19": "Cz",
    # Additional channels
    "EEG 20": "Fpz",
    "EEG 21": "EOG1",
    "EEG 22": "EOG2",
    "EEG 23": "EMG",
    "EEG 24": "ECG",
    "EEG 25": "Trigger",
}

# =============================================================================
# Standard channel types
# =============================================================================
_CHANNEL_TYPES: Dict[str, str] = {
    "E1_L": "eeg",
    "E2_L": "eeg",
    "E3_L": "eeg",
    "E4_L": "eeg",
    "E5_L": "eeg",
    "E6_L": "eeg",
    "E7_L": "eeg",
    "E8_L": "eeg",
    "E1_R": "eeg",
    "E2_R": "eeg",
    "E3_R": "eeg",
    "E4_R": "eeg",
    "E5_R": "eeg",
    "E6_R": "eeg",
    "E7_R": "eeg",
    "E8_R": "eeg",
    "M1": "eeg",
    "M2": "eeg",
    "Cz": "eeg",
    "Fpz": "eeg",
    "EOG1": "eog",
    "EOG2": "eog",
    "EMG": "emg",
    "ECG": "ecg",
    "Trigger": "stim",
}


def _find_sidecar_events_tsv(file_path: str, suffix: str = "events") -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    base = re.sub(r"(_eeg)?\.(edf|bdf|set|fif|vhdr|eeg)$", "", file_path, flags=re.IGNORECASE)
    # Try task-sleep_events.tsv first (scoring events with sleep stages)
    candidates = [
        f"{base}_{suffix}.tsv",
        f"{base}_events.tsv",
        file_path.replace("_eeg.", "_events.").replace(".edf", "_events.tsv"),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    # Search in same directory
    dir_path = os.path.dirname(file_path)
    base_name = os.path.basename(base)
    for f in os.listdir(dir_path) if os.path.isdir(dir_path) else []:
        if f.endswith("_events.tsv") and suffix in f:
            return os.path.join(dir_path, f)
        if f.endswith("_events.tsv") and base_name.split("_")[0] in f:
            return os.path.join(dir_path, f)
    return None


def _find_diary_events_tsv(file_path: str) -> Optional[str]:
    """Find diary events.tsv file for a given EEG file."""
    base = re.sub(r"(_eeg)?\.(edf|bdf|set|fif|vhdr|eeg)$", "", file_path, flags=re.IGNORECASE)
    dir_path = os.path.dirname(file_path)
    # Look for task-sleep_acq-diary_events.tsv
    for f in os.listdir(dir_path) if os.path.isdir(dir_path) else []:
        if "diary" in f.lower() and f.endswith("_events.tsv"):
            return os.path.join(dir_path, f)
    # Try pattern matching
    diary_path = base.replace("task-sleep", "task-sleep_acq-diary") + "_events.tsv"
    if os.path.exists(diary_path):
        return diary_path
    return None


def _find_scoring_events_tsv(file_path: str) -> Optional[str]:
    """Find scoring events.tsv file with sleep stages and arousal info."""
    base = re.sub(r"(_eeg)?\.(edf|bdf|set|fif|vhdr|eeg)$", "", file_path, flags=re.IGNORECASE)
    dir_path = os.path.dirname(file_path)
    # Look for task-sleep_events.tsv (scoring file)
    for f in os.listdir(dir_path) if os.path.isdir(dir_path) else []:
        if f == "task-sleep_events.tsv" or ("sleep" in f.lower() and f.endswith("_events.tsv") and "diary" not in f.lower()):
            return os.path.join(dir_path, f)
    scoring_path = base + "_events.tsv"
    if os.path.exists(scoring_path):
        return scoring_path
    return None


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject ID
        subj_col = "participant_id"
        if subj_col not in df.columns:
            return {}
        
        # Normalize subject ID format
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"
        
        row = df[df[subj_col] == subject_id]
        if row.empty:
            return {}
        
        result = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in row.columns:
                result[field] = str(row[field].values[0])
        return result
    except Exception:
        return {}


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to EEGUnity canonical names."""
    rename_map = {}
    for old_name in raw.ch_names:
        if old_name in _EAR_EEG_CHANNEL_MAP:
            rename_map[old_name] = _EAR_EEG_CHANNEL_MAP[old_name]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    # Set channel types
    for ch_name in raw.ch_names:
        if ch_name in _CHANNEL_TYPES:
            raw.set_channel_types({_CHANNEL_TYPES[ch_name]: _CHANNEL_TYPES[ch_name]})
    
    return raw


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events from a BIDS events.tsv file."""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        return pd.read_csv(file_path, sep="\t")
    except Exception:
        return None


def _create_annotations_from_events_df(events_df: pd.DataFrame, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Create MNE annotations from BIDS events DataFrame."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required columns
    if "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = events_df["onset"].values
    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
    descriptions = events_df["trial_type"].values if "trial_type" in events_df.columns else events_df["value"].values if "value" in events_df.columns else np.array([""] * len(onsets))
    
    # Convert to strings
    descriptions = [str(d) for d in descriptions]
    
    # Filter valid onsets
    valid = ~np.isnan(onsets)
    onsets = onsets[valid]
    durations = durations[valid] if len(durations) == len(valid) else np.zeros(len(onsets))
    descriptions = [d for i, d in enumerate(descriptions) if valid[i]]
    
    # Ensure durations are non-negative
    durations = np.maximum(durations, 0)
    
    # Clip to raw length
    max_time = raw.times[-1] if len(raw.times) > 0 else float('inf')
    valid_time = onsets < max_time
    onsets = onsets[valid_time]
    durations = durations[valid_time]
    descriptions = [d for i, d in enumerate(descriptions) if valid_time[i]]
    
    # Cap durations to not exceed recording
    durations = np.minimum(durations, max_time - onsets)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _get_subject_id_from_row(row: pd.Series) -> str:
    """Extract subject ID from dataset row."""
    # Try common column names
    for col in ["subject", "participant_id", "sub_id", "subject_id"]:
        if col in row.index:
            subj = str(row[col])
            return subj.replace("sub-", "") if subj.startswith("sub-") else subj
    
    # Try to extract from file path
    if "file_path" in row.index:
        fp = str(row["file_path"])
        match = re.search(r'sub-(\w+)', fp)
        if match:
            return match.group(1)
    
    return ""


def _derive_has_arousal(raw: mne.io.BaseRaw, scoring_events_df: Optional[pd.DataFrame]) -> np.ndarray:
    """Create has_arousal misc channel from scoring events."""
    n_times = len(raw.times)
    data = np.zeros((1, n_times))
    
    if scoring_events_df is None or scoring_events_df.empty:
        return data
    
    # Look for arousal-related events
    arousal_keywords = ["arousal", "Arousal", "Sleep stage A", "stage A"]
    for _, event in scoring_events_df.iterrows():
        desc = str(event.get("trial_type", event.get("value", "")))
        if any(kw in desc for kw in arousal_keywords):
            onset = float(event.get("onset", 0))
            duration = float(event.get("duration", 0))
            if duration <= 0:
                duration = 1.0  # Default 1 second for arousal
            
            start_idx = int(onset * raw.info["sfreq"])
            end_idx = int((onset + duration) * raw.info["sfreq"])
            start_idx = max(0, min(start_idx, n_times))
            end_idx = max(0, min(end_idx, n_times))
            if start_idx < end_idx:
                data[0, start_idx:end_idx] = 1.0
    
    return data


def _derive_written_time(raw: mne.io.BaseRaw, diary_events_df: Optional[pd.DataFrame]) -> np.ndarray:
    """Create written_time misc channel from diary events."""
    n_times = len(raw.times)
    data = np.zeros((1, n_times))
    
    if diary_events_df is None or diary_events_df.empty:
        return data
    
    # Look for written_time events - mark time points when diary was written
    for _, event in diary_events_df.iterrows():
        desc = str(event.get("trial_type", event.get("value", "")))
        if "written" in desc.lower() or "time" in desc.lower() or "diary" in desc.lower():
            onset = float(event.get("onset", 0))
            duration = float(event.get("duration", 30))  # Default 30s if not specified
            if duration <= 0:
                duration = 30.0
            
            start_idx = int(onset * raw.info["sfreq"])
            end_idx = int((onset + duration) * raw.info["sfreq"])
            start_idx = max(0, min(start_idx, n_times))
            end_idx = max(0, min(end_idx, n_times))
            if start_idx < end_idx:
                data[0, start_idx:end_idx] = 1.0
    
    return data


def _derive_pressed_trigger(raw: mne.io.BaseRaw, diary_events_df: Optional[pd.DataFrame]) -> np.ndarray:
    """Create pressed_trigger misc channel from diary events."""
    n_times = len(raw.times)
    data = np.zeros((1, n_times))
    
    if diary_events_df is None or diary_events_df.empty:
        return data
    
    # Look for trigger/pressed events in diary
    for _, event in diary_events_df.iterrows():
        desc = str(event.get("trial_type", event.get("value", "")))
        if "trigger" in desc.lower() or "pressed" in desc.lower() or "button" in desc.lower():
            onset = float(event.get("onset", 0))
            duration = float(event.get("duration", 1))  # Brief event
            if duration <= 0:
                duration = 1.0
            
            start_idx = int(onset * raw.info["sfreq"])
            end_idx = int((onset + duration) * raw.info["sfreq"])
            start_idx = max(0, min(start_idx, n_times))
            end_idx = max(0, min(end_idx, n_times))
            if start_idx < end_idx:
                data[0, start_idx:end_idx] = 1.0
    
    return data


class OpenNeuroDS005185Kernel:
    KERNEL_ID = "openneuro_ds005185"
    DATASET_NAME = "ds005185"
    DATASET_DESCRIPTION = "Ear-EEG Sleep Monitoring 2019 (EESM19)"
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path and dataset path
        file_path = str(row.get("file_path", ""))
        dataset_path = str(udataset.get("dataset_path", os.path.dirname(file_path))) if hasattr(udataset, 'get') else os.path.dirname(file_path)
        if hasattr(udataset, 'dataset_path'):
            dataset_path = str(udataset.dataset_path)
        
        # Extract subject ID
        subject_id = _get_subject_id_from_row(row)
        
        # Read participants info
        participants_info = _read_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description
        eegunity_description = {}
        for field in _REQUIRED_INFO_FIELDS:
            eegunity_description[field] = participants_info.get(field, "")
        
        # Set description
        original_desc = str(raw.info.get("description", ""))
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels
        raw = _rename_channels(raw)
        
        # Find and read events files
        scoring_events_df = None
        diary_events_df = None
        
        if file_path:
            scoring_path = _find_scoring_events_tsv(file_path)
            diary_path = _find_diary_events_tsv(file_path)
            scoring_events_df = _read_events_tsv(scoring_path)
            diary_events_df = _read_events_tsv(diary_path)
        
        # Combine annotations from all events files
        all_annotations = []
        
        # Read native events from raw if available
        if raw.annotations:
            all_annotations.append(raw.annotations)
        
        # Add scoring events annotations
        if scoring_events_df is not None:
            scoring_annot = _create_annotations_from_events_df(scoring_events_df, raw)
            if len(scoring_annot) > 0:
                all_annotations.append(scoring_annot)
        
        # Add diary events annotations
        if diary_events_df is not None:
            diary_annot = _create_annotations_from_events_df(diary_events_df, raw)
            if len(diary_annot) > 0:
                all_annotations.append(diary_annot)
        
        # Merge annotations
        if len(all_annotations) > 0:
            merged = all_annotations[0]
            for annot in all_annotations[1:]:
                merged = merged + annot
            raw.set_annotations(merged)
        
        # Create derived misc channels
        derived_data = {}
        derived_data["has_arousal"] = _derive_has_arousal(raw, scoring_events_df)
        derived_data["written_time"] = _derive_written_time(raw, diary_events_df)
        derived_data["pressed_trigger"] = _derive_pressed_trigger(raw, diary_events_df)
        
        # Add derived misc channels to raw
        for ch_name, data in derived_data.items():
            if ch_name not in raw.ch_names:
                info = mne.create_info([ch_name], raw.info["sfreq"], ch_types=["misc"])
                raw_misc = mne.io.RawArray(data, info, first_samp=raw.first_samp)
                raw.add_channels([raw_misc], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS005185Kernel()