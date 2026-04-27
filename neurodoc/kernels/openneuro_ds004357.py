"""openneuro_ds004357 stage1 kernel for EEGUnity.

Visual feature decoding from RSVP stimuli - 16 subjects, 127 channels, 1000 Hz.
BIDS dataset with BrainVision .vhdr/.eeg/.vmrk files, EEGLAB .set files, and EDF files.

Source: https://openneuro.org/datasets/ds004357
Paper: https://doi.org/10.1038/s41598-025-27703-5
"""

from __future__ import annotations

import json
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Paper DOI 10.1038/s41598-025-27703-5 (Methods section)
# "EEG was recorded from 128 channels using a BrainAmp MR plus amplifier"
# "Ag/AgCl electrode cap" - LLM 推断，需人类复核
_AMPLIFIER = "BrainAmp MR plus"
_CAP = "Ag/AgCl"  # LLM 推断，需人类复核

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["Age", "Gender", "Handedness"]

# Required derived misc channels with their source fields
# Format: "events.tsv:<column>" for per-trial values from events.tsv
_DERIVED_MISC_CHANNELS = {
    "response_time_label": "events.tsv:rt",
    "correct_label": "events.tsv:correct",
    "soaduration_label": "events.tsv:soaduration",
    "phase_label": "events.tsv:feature_phase",
    "presentation_number_label": "events.tsv:presentationnumber",
}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    base = file_path.replace(".set", "").replace(".edf", "").replace(".eeg", "").replace(".vhdr", "")
    # Try BIDS naming conventions
    candidates = [
        base + "_events.tsv",
        base.replace("_eeg", "_events") + ".tsv",
        base.replace("_EEG", "_events") + ".tsv",
    ]
    # Also try parent directory patterns
    dir_path = os.path.dirname(file_path)
    base_name = os.path.basename(base)
    candidates.extend([
        os.path.join(dir_path, base_name + "_events.tsv"),
        os.path.join(dir_path, "events.tsv"),
    ])
    
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    
    # Fallback: search for any events.tsv in same directory or parent
    for search_dir in [dir_path, os.path.dirname(dir_path)]:
        if os.path.isdir(search_dir):
            for f in os.listdir(search_dir):
                if f.endswith("_events.tsv") or f == "events.tsv":
                    return os.path.join(search_dir, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find the participants.tsv file for the dataset."""
    current_dir = os.path.dirname(file_path)
    # Walk up to find participants.tsv
    for _ in range(5):  # Search up to 5 levels up
        candidate = os.path.join(current_dir, "participants.tsv")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _get_subject_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # BIDS pattern: sub-XX
    match = re.search(r'sub-(\d+)', file_path)
    if match:
        return match.group(1).zfill(2)  # Zero-pad to 2 digits
    # Try other patterns
    match = re.search(r'/(\d{2})/', file_path)
    if match:
        return match.group(1)
    match = re.search(r'sub(\d+)', os.path.basename(file_path))
    if match:
        return match.group(1).zfill(2)
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {}
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Normalize subject ID format
        df["participant_id"] = df["participant_id"].astype(str).str.replace("sub-", "").str.zfill(2)
        subject_id_norm = subject_id.zfill(2)
        
        row = df[df["participant_id"] == subject_id_norm]
        if row.empty:
            # Try without zero-padding
            row = df[df["participant_id"] == subject_id.lstrip("0") or subject_id]
        
        if not row.empty:
            for field in _REQUIRED_INFO_FIELDS:
                if field in row.columns:
                    val = row[field].values[0]
                    # Handle missing/NaN
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val).strip()
                else:
                    info[field] = "unknown"
        else:
            for field in _REQUIRED_INFO_FIELDS:
                info[field] = "unknown"
    except Exception:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
    
    return info


def _normalize_sex(sex: str) -> str:
    """Normalize sex to lowercase standard."""
    sex = sex.lower().strip()
    if sex in ("m", "male", "1"):
        return "male"
    elif sex in ("f", "female", "2"):
        return "female"
    else:
        return "unknown"


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return pd.DataFrame()


def _create_derived_misc_channel_from_events(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    channel_name: str,
    column_name: str,
) -> mne.io.BaseRaw:
    """Create a derived MISC channel from events.tsv column values.
    
    Creates a trial-locked step function aligned to stimulus onsets.
    If source data is not available, skip channel creation.
    """
    # Skip if events_df is empty or column not available
    if events_df.empty or column_name not in events_df.columns:
        return raw
    
    # Get onset times and values
    if "onset" not in events_df.columns:
        return raw
    
    # Filter to rows with valid values for this column
    valid_mask = events_df[column_name].notna()
    
    if not valid_mask.any():
        return raw
    
    onset_times = events_df.loc[valid_mask, "onset"].values.astype(float)
    values = events_df.loc[valid_mask, column_name].values
    
    # Convert to float where possible
    float_values = []
    for v in values:
        try:
            float_values.append(float(v))
        except (ValueError, TypeError):
            float_values.append(0.0)
    values = np.array(float_values)
    
    # Create step function: value at onset, carry forward
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    data = np.zeros(n_samples)
    
    # Sort by onset time
    sort_idx = np.argsort(onset_times)
    onset_times = onset_times[sort_idx]
    values = values[sort_idx]
    
    for onset_time, value in zip(onset_times, values):
        sample_idx = int(round(onset_time * sfreq))
        if 0 <= sample_idx < n_samples:
            data[sample_idx:] = value  # Carry-forward step function
    
    # Add as new channel
    info = mne.create_info([channel_name], raw.info["sfreq"], ["misc"])
    misc_raw = mne.io.RawArray(data.reshape(1, -1), info, first_samp=raw.first_samp)
    raw.add_channels([misc_raw], force_update_info=True)
    return raw


class OpenneuroDs004357Kernel:
    KERNEL_ID = "openneuro_ds004357"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        original_description = raw.info.get("description", "")
        
        # Get subject info from participants.tsv
        subject_id = _get_subject_from_path(file_path)
        participants_path = _find_participants_tsv(file_path)
        participant_info = {}
        if participants_path and subject_id:
            participant_info = _read_participants_info(participants_path, subject_id)
        
        # Build eegunity_description
        age = participant_info.get("Age", "unknown")
        sex = _normalize_sex(participant_info.get("Gender", "unknown"))
        handedness = participant_info.get("Handedness", "unknown")
        
        eegunity_description = {
            "age": str(age),
            "sex": sex,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": handedness,
        }
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Read events.tsv and add annotations
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path) if events_path else pd.DataFrame()
        
        if not events_df.empty and "onset" in events_df.columns:
            # Add events as annotations from events.tsv
            # Use stimname column for event labels if available, otherwise trial_type or eventnumber
            if "stimname" in events_df.columns:
                descriptions = events_df["stimname"].astype(str).values
            elif "trial_type" in events_df.columns:
                descriptions = events_df["trial_type"].astype(str).values
            elif "value" in events_df.columns:
                descriptions = events_df["value"].astype(str).values
            elif "eventnumber" in events_df.columns:
                descriptions = events_df["eventnumber"].astype(str).values
            else:
                # Fallback: use row index as description
                descriptions = np.arange(len(events_df)).astype(str)
            
            onsets = events_df["onset"].values.astype(float)
            durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
            
            # Create annotations and assign to raw
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
                orig_time=None,
            )
            raw.set_annotations(annotations)
        
        # Add derived MISC channels from specified source fields
        for channel_name, source_field in _DERIVED_MISC_CHANNELS.items():
            # Parse source field format
            if source_field.startswith("events.tsv:"):
                column_name = source_field.split(":", 1)[1]
                raw = _create_derived_misc_channel_from_events(
                    raw, events_df, channel_name, column_name
                )
            elif source_field.startswith("participants.tsv:"):
                # participants.tsv source: broadcast constant value
                column_name = source_field.split(":", 1)[1]
                # Skip if participants data not available
                if participants_path and subject_id and column_name in participant_info:
                    try:
                        value = float(participant_info[column_name])
                    except (ValueError, TypeError):
                        continue  # Skip if cannot convert to numeric
                    
                    # Create constant broadcast channel
                    sfreq = raw.info["sfreq"]
                    n_samples = len(raw.times)
                    data = np.full(n_samples, value)
                    
                    info = mne.create_info([channel_name], sfreq, ["misc"])
                    misc_raw = mne.io.RawArray(data.reshape(1, -1), info, first_samp=raw.first_samp)
                    raw.add_channels([misc_raw], force_update_info=True)
                # else: skip if source not available
            else:
                # Bare column name: try participants.tsv first, then events.tsv
                # Try participants.tsv
                if participants_path and subject_id and source_field in participant_info:
                    try:
                        value = float(participant_info[source_field])
                    except (ValueError, TypeError):
                        pass  # Will try events.tsv below
                    else:
                        # Create constant broadcast channel
                        sfreq = raw.info["sfreq"]
                        n_samples = len(raw.times)
                        data = np.full(n_samples, value)
                        
                        info = mne.create_info([channel_name], sfreq, ["misc"])
                        misc_raw = mne.io.RawArray(data.reshape(1, -1), info, first_samp=raw.first_samp)
                        raw.add_channels([misc_raw], force_update_info=True)
                        continue  # Successfully created from participants.tsv
                
                # Try events.tsv
                raw = _create_derived_misc_channel_from_events(
                    raw, events_df, channel_name, source_field
                )
        
        return raw


KERNEL = OpenneuroDs004357Kernel()