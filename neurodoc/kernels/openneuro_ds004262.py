"""OpenNeuro DS004262 (Continuous Feedback Processing) stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Standard 10-20 system channel names expected for this 31-channel dataset
# inferred by LLM, needs human review
# Source: Paper references indicate standard EEG cap with 31 channels
_STANDARD_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FCz", "FC2", "FC6",
    "M1", "T7", "C3", "Cz", "C4", "T8", "M2",
    "CP5", "CP1", "CPz", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
]


def _get_subject_id(row) -> str:
    """Extract subject ID from row."""
    file_path = str(row.get("File Path", ""))
    for prefix in ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05",
                   "sub-06", "sub-07", "sub-08", "sub-09", "sub-10",
                   "sub-11", "sub-12", "sub-13", "sub-14", "sub-15",
                   "sub-16", "sub-17", "sub-18", "sub-19", "sub-20", "sub-21"]:
        if prefix in file_path:
            return prefix
    # Fallback: extract from path pattern sub-XX
    match = re.search(r'(sub-\d+)', file_path)
    if match:
        return match.group(1)
    return "unknown"


def _read_participants_tsv(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and return info fields for subject."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for subject
        sub_row = df[df["participant_id"] == subject_id]
        if sub_row.empty:
            return {}
        result = {}
        for col in ["age", "sex", "handedness"]:
            if col in sub_row.columns:
                val = str(sub_row[col].values[0])
                if pd.isna(val) or val.lower() in ["nan", "n/a", ""]:
                    result[col] = "unknown"
                else:
                    result[col] = val
            else:
                result[col] = "unknown"
        return result
    except Exception:
        return {}


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read sibling events.tsv for given EEG file."""
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.<ext> -> sub-XX_task-YY_run-ZZ_events.tsv
    base = file_path.replace("_eeg.eeg", "").replace("_eeg.vhdr", "").replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.fif", "")
    events_path = base + "_events.tsv"
    if not os.path.exists(events_path):
        # Try without run
        base_no_run = re.sub(r'_run-\d+', '', base)
        events_path_alt = base_no_run + "_events.tsv"
        if os.path.exists(events_path_alt):
            events_path = events_path_alt
        else:
            return None
    try:
        # Handle potential BOM in header
        df = pd.read_csv(events_path, sep="\t", encoding="utf-8-sig")
        # Normalize column names to strip any BOM or whitespace
        df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]
        return df
    except Exception:
        return None


def _build_response_time_misc(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> Optional[mne.io.RawArray]:
    """Build response_time misc channel from events.tsv data.
    
    For each response event (S31-S36), find matching bar onset event (S21-S26)
    with same condition number, compute RT = onset(S3x) - onset(S2x).
    """
    if events_df is None or events_df.empty:
        return None
    
    # Ensure required columns exist
    if "value" not in events_df.columns or "onset" not in events_df.columns:
        return None
    
    # Convert onset to numeric
    events_df = events_df.copy()
    events_df["onset"] = pd.to_numeric(events_df["onset"], errors="coerce")
    
    # Filter to bar onset (S21-S26) and response (S31-S36) events
    bar_events = events_df[events_df["value"].astype(str).str.match(r'^S 2[1-6]$', na=False)].copy()
    resp_events = events_df[events_df["value"].astype(str).str.match(r'^S 3[1-6]$', na=False)].copy()
    
    if bar_events.empty or resp_events.empty:
        return None
    
    # Extract condition number (last digit)
    bar_events["condition"] = bar_events["value"].astype(str).str[-1]
    resp_events["condition"] = resp_events["value"].astype(str).str[-1]
    
    # Sort by onset
    bar_events = bar_events.sort_values("onset").reset_index(drop=True)
    resp_events = resp_events.sort_values("onset").reset_index(drop=True)
    
    # Match bar to response by condition and temporal proximity
    # Within each trial sequence: fixation -> cue -> bar -> response -> animation
    rt_values = []  # list of (onset_time, rt_seconds)
    
    for _, bar_row in bar_events.iterrows():
        cond = bar_row["condition"]
        bar_onset = bar_row["onset"]
        # Find next response with same condition after bar onset
        matching_resp = resp_events[
            (resp_events["condition"] == cond) & 
            (resp_events["onset"] > bar_onset)
        ]
        if not matching_resp.empty:
            # Take the earliest matching response
            resp_onset = matching_resp.iloc[0]["onset"]
            rt = resp_onset - bar_onset
            rt_values.append((resp_onset, rt))
            # Remove used response to prevent double-matching
            resp_events = resp_events.drop(matching_resp.index[0])
            resp_events = resp_events.reset_index(drop=True)
    
    if not rt_values:
        return None
    
    # Create continuous channel with RT values at response onsets, 0 elsewhere
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    rt_data = np.zeros((1, n_samples))
    
    for onset_time, rt in rt_values:
        sample_idx = int(round(onset_time * sfreq))
        if 0 <= sample_idx < n_samples:
            rt_data[0, sample_idx] = rt
    
    # Create info for misc channel
    info = mne.create_info(
        ch_names=["response_time"],
        sfreq=sfreq,
        ch_types=["misc"],
    )
    
    return mne.io.RawArray(rt_data, info)


def _events_tsv_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert events.tsv DataFrame to mne.Annotations.
    
    Uses 'value' column as the annotation description (contains the actual trigger
    codes like 'S  3', 'S 13', etc.), and 'onset'/'duration' for timing.
    """
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Ensure required columns exist
    required_cols = ["onset", "duration"]
    for col in required_cols:
        if col not in events_df.columns:
            return mne.Annotations(onset=[], duration=[], description=[])
    
    # Determine which column to use for descriptions: 'value' has the trigger codes
    # 'trial_type' has generic labels like 'Stimulus', 'New Segment', 'Comment'
    if "value" in events_df.columns:
        desc_col = "value"
    elif "trial_type" in events_df.columns:
        desc_col = "trial_type"
    else:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Convert to numeric, drop rows with invalid onsets
    events_df = events_df.copy()
    events_df["onset"] = pd.to_numeric(events_df["onset"], errors="coerce")
    events_df["duration"] = pd.to_numeric(events_df["duration"], errors="coerce").fillna(0.0)
    
    # Drop rows with NaN onsets (can't place them in time)
    valid_mask = events_df["onset"].notna()
    events_df = events_df[valid_mask].reset_index(drop=True)
    
    if events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Get descriptions, replacing NaN with empty string
    descriptions = events_df[desc_col].astype(str).replace("nan", "").replace("n/a", "").tolist()
    
    # Use onset in seconds directly (BIDS events.tsv onset is in seconds)
    onsets = events_df["onset"].values
    durations = events_df["duration"].values
    
    # Ensure non-negative durations
    durations = np.maximum(durations, 0.0)
    
    return mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist(),
        description=descriptions,
    )


class OpenNeuroDS004262Kernel:
    KERNEL_ID = "openneuro_ds004262"
    DATASET_NAME = "OpenNeuro DS004262 - Continuous Feedback Processing"
    EXPECTED_CHANNELS = _STANDARD_CHANNEL_NAMES

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get dataset path and subject info
        dataset_path = str(udataset.base_path) if hasattr(udataset, "base_path") else str(udataset)
        subject_id = _get_subject_id(row)
        
        # Read participants.tsv for required fields
        participant_info = _read_participants_tsv(dataset_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("sex", "unknown"),
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": participant_info.get("handedness", "unknown"),
        }
        
        # Get original description
        original_description = raw.info.get("description", "")
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Read events.tsv and add annotations from it
        file_path = str(row.get("File Path", ""))
        events_df = _read_events_tsv(file_path)
        
        # Add annotations from events.tsv to raw
        if events_df is not None and not events_df.empty:
            annotations = _events_tsv_to_annotations(events_df)
            # CRITICAL FIX: Must use set_annotations to attach annotations to raw
            # Assigning to raw.annotations directly or not calling set_annotations
            # means annotations won't be properly registered
            raw.set_annotations(annotations)
        
        # Build and add response_time misc channel if possible
        rt_raw = _build_response_time_misc(raw, events_df)
        if rt_raw is not None:
            raw = raw.add_channels([rt_raw], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004262Kernel()