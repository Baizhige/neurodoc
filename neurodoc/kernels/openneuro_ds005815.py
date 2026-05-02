"""OpenNeuro ds005815 (YOTO) stage1 kernel for EEGUnity.

Dataset: YOTO (You Only Think Once): An EEG Dataset for Tracking Spontaneous
         Cognitive Transitions and Multimodal Stimuli Responses in Resting-State
         and Task Phases
Source: https://openneuro.org/datasets/ds005815
        DOI: 10.18112/openneuro.ds005815.v2.0.1
        Paper: 10.1038/s41597-025-05881-1

This dataset is BIDS-compliant with BrainVision (.eeg/.vhdr/.vmrk) files.
The kernel handles:
- Channel renaming to standard 10-20 names (dataset uses numbered EEG channels)
- Montage setting for standard_1020
- Event extraction from events.tsv sidecars (BrainVision .vmrk may not have all events)
- eegunity_description with required fields
- No required_info_fields, required_native_misc, or derived_misc_channels needed

Channel mapping: The dataset uses EEG-0..EEG-29 numbering. Based on standard
10-20 30-channel layouts and BIDS channel info, we map to standard names.
Annotator: LLM, 2026-04-08 — inferred by LLM, needs human review
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 10-20 30-channel mapping for numbered EEG channels
# Source: Standard 10-20 system for 30 channels, common in resting-state/task EEG
# Dataset uses EEG-0 to EEG-29
# Annotator: LLM, 2026-04-08
_EEG_CHANNEL_MAP: Dict[str, str] = {
    "EEG-0": "Fp1",
    "EEG-1": "Fp2",
    "EEG-2": "F7",
    "EEG-3": "F3",
    "EEG-4": "Fz",
    "EEG-5": "F4",
    "EEG-6": "F8",
    "EEG-7": "FC5",
    "EEG-8": "FC1",
    "EEG-9": "FC2",
    "EEG-10": "FC6",
    "EEG-11": "T7",
    "EEG-12": "C3",
    "EEG-13": "Cz",
    "EEG-14": "C4",
    "EEG-15": "T8",
    "EEG-16": "CP5",
    "EEG-17": "CP1",
    "EEG-18": "CP2",
    "EEG-19": "CP6",
    "EEG-20": "P7",
    "EEG-21": "P3",
    "EEG-22": "Pz",
    "EEG-23": "P4",
    "EEG-24": "P8",
    "EEG-25": "O1",
    "EEG-26": "Oz",
    "EEG-27": "O2",
    "EEG-28": "POz",
    "EEG-29": "AFz",
}

# Alternative naming patterns that might appear (without EEG- prefix)
_ALT_CHANNEL_MAP: Dict[str, str] = {
    "0": "Fp1", "1": "Fp2", "2": "F7", "3": "F3", "4": "Fz",
    "5": "F4", "6": "F8", "7": "FC5", "8": "FC1", "9": "FC2",
    "10": "FC6", "11": "T7", "12": "C3", "13": "Cz", "14": "C4",
    "15": "T8", "16": "CP5", "17": "CP1", "18": "CP2", "19": "CP6",
    "20": "P7", "21": "P3", "22": "Pz", "23": "P4", "24": "P8",
    "25": "O1", "26": "Oz", "27": "O2", "28": "POz", "29": "AFz",
}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-<label>[_ses-<label>]_task-<label>[_run-<label>]_eeg.<ext>
    # events: sub-<label>[_ses-<label>]_task-<label>[_run-<label>]_events.tsv
    base_dir = os.path.dirname(file_path)
    if not base_dir:
        return None
    basename = os.path.basename(file_path)
    
    # Remove extension(s)
    # Handle .eeg, .vhdr, .vmrk -> all map to same base
    if basename.endswith(".eeg"):
        base = basename[:-4]
    elif basename.endswith(".vhdr"):
        base = basename[:-5]
    elif basename.endswith(".vmrk"):
        base = basename[:-5]
    else:
        # Try generic: remove last extension
        base = os.path.splitext(basename)[0]
    
    # The base should end with _eeg, replace with _events
    if base.endswith("_eeg"):
        events_base = base[:-4] + "_events"
    else:
        events_base = base + "_events"
    
    events_path = os.path.join(base_dir, events_base + ".tsv")
    
    if os.path.exists(events_path):
        return events_path
    
    # Try without _eeg suffix replacement (sometimes base is already correct)
    alt_events_path = os.path.join(base_dir, base + ".tsv")
    if os.path.exists(alt_events_path) and "events" in alt_events_path:
        return alt_events_path
    
    # Search in directory for matching events file
    try:
        for f in os.listdir(base_dir):
            if f.endswith("_events.tsv"):
                # Check if subject and task match
                if base.split("_task-")[0] in f:
                    return os.path.join(base_dir, f)
    except (OSError, FileNotFoundError):
        pass
    
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv and return DataFrame."""
    df = pd.read_csv(events_path, sep="\t")
    return df


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations.
    
    Uses onset (in seconds) and duration (in seconds) directly.
    Description uses trial_type column as the literal string label.
    """
    # Required BIDS columns: onset, duration
    onsets = events_df["onset"].values.astype(float)
    
    # Duration: use provided or default to 0
    if "duration" in events_df.columns:
        durations = events_df["duration"].values.astype(float)
        # Replace NaN with 0.0; keep actual zeros (valid in BIDS for instantaneous events)
        durations = np.where(np.isnan(durations), 0.0, durations)
    else:
        durations = np.zeros(len(onsets))
    
    # Description: use trial_type column with literal strings (HC-5: no remapping)
    # Per evidence, trial_type contains distinguishable labels: StartInstruction, Eyeclosed, etc.
    descriptions = []
    for idx, row in events_df.iterrows():
        if "trial_type" in events_df.columns and pd.notna(row.get("trial_type")):
            trial_type = str(row["trial_type"]).strip()
            if trial_type:
                descriptions.append(trial_type)
            else:
                # Fallback to value if trial_type is empty
                if "value" in events_df.columns and pd.notna(row.get("value")):
                    descriptions.append(str(row["value"]).strip())
                else:
                    descriptions.append("unknown")
        elif "value" in events_df.columns and pd.notna(row.get("value")):
            # Fallback to value if no trial_type column
            descriptions.append(str(row["value"]).strip())
        else:
            descriptions.append("unknown")
    
    # Create annotations - onset is already in seconds, no sfreq scaling needed
    annotations = mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist(),
        description=descriptions,
    )
    
    return annotations


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find the participants.tsv file for this dataset."""
    base_dir = os.path.dirname(file_path)
    # Walk up to find participants.tsv
    current_dir = base_dir
    for _ in range(5):  # BIDS datasets are usually shallow
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _read_participants_tsv(participants_path: str) -> pd.DataFrame:
    """Read participants.tsv and return DataFrame."""
    df = pd.read_csv(participants_path, sep="\t")
    return df


def _get_subject_info(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Get subject info from participants DataFrame."""
    # BIDS subject IDs are like "sub-01", strip "sub-" prefix for matching if needed
    match_id = subject_id
    # Try exact match first
    mask = participants_df["participant_id"] == match_id
    if not mask.any() and match_id.startswith("sub-"):
        # Try without prefix
        alt_id = match_id[4:]
        mask = participants_df["participant_id"] == alt_id
    if not mask.any():
        # Try adding prefix
        alt_id = "sub-" + match_id
        mask = participants_df["participant_id"] == alt_id
    
    if mask.any():
        row = participants_df[mask].iloc[0]
        info = {}
        for col in participants_df.columns:
            if col != "participant_id" and pd.notna(row.get(col)):
                info[col] = str(row[col])
        return info
    return {}


def _get_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    basename = os.path.basename(file_path)
    parts = basename.split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part
    # Try from directory path
    for dir_part in file_path.split(os.sep):
        if dir_part.startswith("sub-"):
            return dir_part
    return "unknown"


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename numbered channels to standard 10-20 names."""
    ch_names = raw.ch_names
    rename_map = {}
    
    for ch in ch_names:
        if ch in _EEG_CHANNEL_MAP:
            rename_map[ch] = _EEG_CHANNEL_MAP[ch]
        elif ch in _ALT_CHANNEL_MAP:
            rename_map[ch] = _ALT_CHANNEL_MAP[ch]
        # Also handle cases where channel might have spaces or different casing
        elif ch.strip() in _EEG_CHANNEL_MAP:
            rename_map[ch] = _EEG_CHANNEL_MAP[ch.strip()]
        elif ch.strip() in _ALT_CHANNEL_MAP:
            rename_map[ch] = _ALT_CHANNEL_MAP[ch.strip()]
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


def _set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage for the raw data."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw = raw.set_montage(montage, match_case=False, on_missing="warn")
    except Exception:
        pass
    return raw


class OpenNeuroDS005815Kernel:
    """Kernel for OpenNeuro ds005815 (YOTO) dataset."""

    def __init__(self):
        self.dataset_name = "openneuro_ds005815"
        self.required_info_fields = ["age", "sex", "amplifier", "cap", "handedness"]

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row
        file_path = row.get("file_path", "") if isinstance(row, dict) else getattr(row, "file_path", "")
        
        # Rename channels to standard 10-20 names
        raw = _rename_channels(raw)
        
        # Set montage
        raw = _set_montage(raw)
        
        # Extract subject info from participants.tsv
        subject_id = _get_subject_id_from_path(file_path)
        participants_path = _find_participants_tsv(file_path)
        subject_info = {}
        if participants_path:
            participants_df = _read_participants_tsv(participants_path)
            subject_info = _get_subject_info(participants_df, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {}
        for field in self.required_info_fields:
            eegunity_description[field] = subject_info.get(field, "")
        
        # Set description
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Find and apply events from events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path and os.path.exists(events_path):
            events_df = _read_events_tsv(events_path)
            if len(events_df) > 0:
                annotations = _events_to_annotations(events_df)
                # Set annotations, replacing any existing ones
                raw = raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenNeuroDS005815Kernel()