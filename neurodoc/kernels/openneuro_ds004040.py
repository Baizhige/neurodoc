"""OpenNeuro DS004040 stage1 kernel for EEGUnity.

Trance Channeling EEG dataset: 13 experienced trance channelers performed
alternating 5-minute blocks of trance channeling and resting state across
two sessions. Events are read from sibling *_events.tsv files.

Source: https://openneuro.org/datasets/ds004040
DOI: https://doi.org/10.18112/openneuro.ds004040.v1.0.0
Paradigm reference: https://doi.org/10.12688/f1000research.17157.2

Kernel Notes:
- 26 files (13 subjects × 2 sessions)
- 64 channels, 512 Hz sampling rate
- BIDS-compliant dataset with participants.tsv and *_events.tsv sidecars
- Events.tsv contains trance/rest block onsets and offsets
- Channel names are standard 10-20 system
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


# Required info fields from participants.tsv (kernel_requirements)
_REQUIRED_INFO_FIELDS: List[str] = ["age", "sex", "handedness"]

# Required native misc channels (none for this dataset)
_REQUIRED_NATIVE_MISC: List[str] = []

# Required derived misc channels (from kernel_requirements)
_REQUIRED_DERIVED_MISC: List[str] = ["trance_label"]

# Block timing parameters (verified from paradigm: 5-minute alternating blocks)
_BLOCK_DURATION_S = 300.0  # 5 minutes per block

# Source: openneuro_ds004040 dataset_description.json and README
# Amplifier: BrainProducts BrainAmp (common in EEG research, inferred from dataset context)
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_AMPLIFIER = "BrainAmp"  # LLM 推断，需人类复核
_CAP = "Ag/AgCl"  # Standard EEG cap material; LLM 推断，需人类复核


def _parse_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: same directory, same basename prefix
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Remove extension
    base_no_ext = basename.split(".")[0]
    # Remove _eeg suffix if present
    if base_no_ext.endswith("_eeg"):
        base_no_ext = base_no_ext[:-4]
    
    alt_events = os.path.join(dirname, base_no_ext + "_events.tsv")
    if os.path.exists(alt_events):
        return alt_events
    
    # Try with _eeg kept
    alt_events2 = os.path.join(dirname, basename.split(".")[0] + "_events.tsv")
    if os.path.exists(alt_events2):
        return alt_events2
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file walking up from the EEG file."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _load_subject_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep="\t")
        
        # Find participant_id column (could be 'participant_id' or 'subject_id')
        id_col = None
        for col in df.columns:
            if col.lower() in ("participant_id", "subject_id"):
                id_col = col
                break
        
        if id_col is None:
            return {}
        
        # Match subject ID (handle 'sub-01' vs '01' formats)
        search_id = f"sub-{subject_id}" if not subject_id.startswith("sub-") else subject_id
        # Also try without prefix
        search_id_no_prefix = subject_id.replace("sub-", "")
        
        row = None
        for idx, pid in enumerate(df[id_col]):
            pid_str = str(pid)
            if pid_str == search_id or pid_str == search_id_no_prefix or pid_str == f"sub-{search_id_no_prefix}":
                row = df.iloc[idx]
                break
        
        if row is None:
            return {}
        
        info = {}
        # Map common column names
        col_map = {
            "age": ["age", "Age", "AGE"],
            "sex": ["sex", "Sex", "SEX", "gender", "Gender", "GENDER"],
            "handedness": ["handedness", "Handedness", "HANDEDNESS", "hand", "Hand", "HAND"],
        }
        
        for target, candidates in col_map.items():
            for col in candidates:
                if col in df.columns:
                    val = str(row[col]) if pd.notna(row[col]) else "unknown"
                    info[target] = val.lower() if target == "sex" and val != "unknown" else val
                    break
        
        return info
    except Exception:
        return {}


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return pd.DataFrame()


def _events_to_annotations(events_df: pd.DataFrame, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df.empty or "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = events_df["onset"].values.astype(float)
    
    # Duration column
    if "duration" in events_df.columns:
        durations = events_df["duration"].values.astype(float)
    else:
        durations = np.zeros(len(onsets))
    
    # Description column: prefer 'trial_type', then 'value', then 'stim_type'
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["unknown"] * len(onsets))
    
    # Filter out empty descriptions
    valid_mask = descriptions != "" if len(descriptions) > 0 else slice(None)
    if not isinstance(valid_mask, slice):
        onsets = onsets[valid_mask]
        durations = durations[valid_mask]
        descriptions = descriptions[valid_mask]
    
    # Ensure onsets are within valid range
    sfreq = raw.info["sfreq"]
    max_time = raw.n_times / sfreq
    valid_time_mask = (onsets >= 0) & (onsets <= max_time)
    onsets = onsets[valid_time_mask]
    durations = durations[valid_time_mask]
    descriptions = descriptions[valid_time_mask]
    
    if len(onsets) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _create_trance_label_misc(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create misc channel named 'trance_label' based on events.tsv trial_type.
    
    Creates a step function: 1.0 during trance blocks, 0.0 during rest blocks.
    """
    # Ensure data is loaded before adding channels
    if not raw.preload:
        raw.load_data()
    
    sfreq = raw.info["sfreq"]
    n_times = raw.n_times
    times = np.arange(n_times) / sfreq
    
    # Initialize with zeros (rest)
    data = np.zeros((1, n_times))
    
    # If we have events, create step function based on trial_type
    if not events_df.empty and "onset" in events_df.columns:
        onsets = events_df["onset"].values.astype(float)
        
        if "duration" in events_df.columns:
            durations = events_df["duration"].values.astype(float)
        else:
            durations = np.full(len(onsets), _BLOCK_DURATION_S)
        
        # Determine which descriptions indicate trance
        if "trial_type" in events_df.columns:
            trial_types = events_df["trial_type"].astype(str).values
        elif "value" in events_df.columns:
            trial_types = events_df["value"].astype(str).values
        else:
            trial_types = np.array(["unknown"] * len(onsets))
        
        for onset, duration, trial_type in zip(onsets, durations, trial_types):
            # Determine if this is a trance block
            is_trance = "trance" in trial_type.lower()
            start_sample = int(onset * sfreq)
            end_sample = int((onset + duration) * sfreq)
            start_sample = max(0, min(start_sample, n_times))
            end_sample = max(0, min(end_sample, n_times))
            if start_sample < end_sample:
                data[0, start_sample:end_sample] = 1.0 if is_trance else 0.0
    
    # Add as misc channel
    info = mne.create_info(ch_names=["trance_label"], sfreq=sfreq, ch_types=["misc"])
    raw_misc = mne.io.RawArray(data, info)
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


@dataclass
class OpenNeuroDS004040Kernel:
    """Kernel for OpenNeuro ds004040 Trance Channeling EEG dataset."""
    
    KERNEL_ID: str = "openneuro_ds004040"
    DATASET_NAME: str = "ds004040"
    REQUIRED_INFO_FIELDS: List[str] = None
    REQUIRED_NATIVE_MISC: List[str] = None
    REQUIRED_DERIVED_MISC: List[str] = None
    
    def __post_init__(self):
        self.REQUIRED_INFO_FIELDS = _REQUIRED_INFO_FIELDS.copy()
        self.REQUIRED_NATIVE_MISC = _REQUIRED_NATIVE_MISC.copy()
        self.REQUIRED_DERIVED_MISC = _REQUIRED_DERIVED_MISC.copy()
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        
        # Find participants.tsv and load subject info
        participants_path = _find_participants_tsv(file_path)
        subject_id = _parse_subject_id(file_path)
        
        subject_info = {}
        if participants_path and subject_id:
            subject_info = _load_subject_info(participants_path, subject_id)
        
        # Find and read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = pd.DataFrame()
        if events_path:
            events_df = _read_events_tsv(events_path)
        
        # Add events as annotations
        if not events_df.empty:
            annotations = _events_to_annotations(events_df, raw)
            if len(annotations) > 0:
                # Set annotations, replacing any existing ones
                raw.set_annotations(annotations)
        
        # Create derived misc channel: trance_label
        if "trance_label" in _REQUIRED_DERIVED_MISC:
            raw = _create_trance_label_misc(raw, events_df)
        
        # Build eegunity_description
        eegunity_description = {
            "age": str(subject_info.get("age", "unknown")),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": str(subject_info.get("handedness", "unknown")),
        }
        
        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS004040Kernel()