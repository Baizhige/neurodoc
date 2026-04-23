"""OpenNeuro DS004584 stage1 kernel for EEGUnity.

Resting-state EEG dataset (Parkinson's Disease Study).
149 participants (100 PD + 49 healthy controls), eyes-open ~2 min.
63-channel EEG, 500 Hz sampling rate.

Source: https://openneuro.org/datasets/ds004584
Paper: DOI 10.21203/rs.3.rs-2666578/v1 (LEAPD cognitive impairment)
Paper: DOI 10.1038/s41531-023-00602-0 (LPC coefficients)
Paper: DOI 10.1038/s41398-025-03506-0 (PD vs HC classification)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


_DEFAULT_AMPLIFIER = "unknown"
_DEFAULT_CAP = "unknown"
_DEFAULT_HANDEDNESS = "unknown"

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["AGE", "GENDER", "GROUP", "MOCA", "TYPE", "UPDRS"]

# Channel rename map for standardizing 63-channel layout
# Source: OpenNeuro ds004584 dataset, standard 10-20 system with extended coverage
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_CHANNEL_RENAME_MAP = {
    # EEG channels — standard names already used in this dataset
    # No renaming needed based on sample data inspection
}

# Derived misc channel configuration
_DERIVED_MISC_CHANNELS = [
    {
        "name": "moca_ordinal",
        "source_field": "MOCA",
        "derivation": "Read MOCA from participants.tsv, apply clinical cutoffs (0=normal>=26, 1=mild impairment 20-25, 2=severe impairment <20), broadcast as constant misc channel",
    }
]


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load and parse participants.tsv from the BIDS dataset root."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _extract_subject_info(
    participants_df: pd.DataFrame, subject_id: str
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv."""
    subject_row = None
    for col in ["participant_id", "subject_id", "subject"]:
        if col in participants_df.columns:
            search_id = subject_id
            if not search_id.startswith("sub-"):
                search_id = f"sub-{search_id}"
            matches = participants_df[participants_df[col] == search_id]
            if len(matches) > 0:
                subject_row = matches.iloc[0]
                break

    if subject_row is None:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    age = "unknown"
    for age_col in ["age", "subject_age", "participant_age", "AGE"]:
        if age_col in participants_df.columns:
            val = subject_row.get(age_col)
            if pd.notna(val):
                try:
                    age = str(int(float(val)))
                except (ValueError, TypeError):
                    age = str(val)
            break

    sex = "unknown"
    for sex_col in ["sex", "gender", "GENDER"]:
        if sex_col in participants_df.columns:
            val = subject_row.get(sex_col)
            if pd.notna(val):
                val_lower = str(val).lower().strip()
                if val_lower in ["m", "male", "man"]:
                    sex = "male"
                elif val_lower in ["f", "female", "woman"]:
                    sex = "female"
            break

    handedness = "unknown"
    for hand_col in ["handedness", "hand"]:
        if hand_col in participants_df.columns:
            val = subject_row.get(hand_col)
            if pd.notna(val):
                val_lower = str(val).lower().strip()
                if "right" in val_lower:
                    handedness = "right"
                elif "left" in val_lower:
                    handedness = "left"
            break

    return {
        "age": age,
        "sex": sex,
        "handedness": handedness,
    }


def _extract_required_info_fields(
    participants_df: pd.DataFrame, subject_id: str
) -> Dict[str, str]:
    """Extract required info fields from participants.tsv for eegunity_description."""
    result = {}
    
    if participants_df.empty:
        for field in _REQUIRED_INFO_FIELDS:
            result[field] = "unknown"
        return result

    subject_row = None
    for col in ["participant_id", "subject_id", "subject"]:
        if col in participants_df.columns:
            search_id = subject_id
            if not search_id.startswith("sub-"):
                search_id = f"sub-{search_id}"
            matches = participants_df[participants_df[col] == search_id]
            if len(matches) > 0:
                subject_row = matches.iloc[0]
                break

    if subject_row is None:
        for field in _REQUIRED_INFO_FIELDS:
            result[field] = "unknown"
        return result

    for field in _REQUIRED_INFO_FIELDS:
        if field in participants_df.columns:
            val = subject_row.get(field)
            if pd.notna(val):
                result[field] = str(val)
            else:
                result[field] = "unknown"
        else:
            result[field] = "unknown"

    return result


def _compute_moca_ordinal(moca_value: str) -> int:
    """Compute ordinal MOCA severity from string value.
    
    0 = normal (>= 26)
    1 = mild impairment (20-25)
    2 = severe impairment (< 20)
    -1 = unknown/missing
    """
    try:
        moca_float = float(moca_value)
        if moca_float >= 26:
            return 0
        elif moca_float >= 20:
            return 1
        else:
            return 2
    except (ValueError, TypeError):
        return -1


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # BIDS convention: events.tsv is in the same directory as the data file
    # or in the parent eeg directory
    base_dir = os.path.dirname(file_path)
    
    # Try direct sibling
    fname = os.path.basename(file_path)
    stem = fname.split(".")[0]  # Remove extension
    events_path = os.path.join(base_dir, f"{stem}_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Try without _eeg suffix variations
    for suffix in ["_eeg", "_EEG", ""]:
        test_stem = stem.replace(suffix, "")
        events_path = os.path.join(base_dir, f"{test_stem}_events.tsv")
        if os.path.exists(events_path):
            return events_path
    
    # Try parent eeg directory
    parent_dir = os.path.dirname(base_dir)
    if os.path.basename(base_dir) == "eeg":
        events_path = os.path.join(base_dir, f"{stem}_events.tsv")
        if os.path.exists(events_path):
            return events_path
    
    return None


def _load_events_from_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Load events from BIDS events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        # Standard BIDS columns: onset, duration, trial_type, value, sample
        required_cols = ["onset"]
        if not all(col in df.columns for col in required_cols):
            return None
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events DataFrame to MNE Annotations."""
    onsets = events_df["onset"].values
    
    # Duration: default to 0 if not present or invalid
    if "duration" in events_df.columns:
        durations = events_df["duration"].fillna(0).values
    else:
        durations = np.zeros(len(onsets))
    
    # Description: prefer trial_type, then value, then stim_type
    descriptions = []
    for idx, row in events_df.iterrows():
        desc = None
        for col in ["trial_type", "value", "stim_type"]:
            if col in events_df.columns and pd.notna(row.get(col)):
                desc = str(row[col])
                break
        if desc is None or desc == "nan":
            desc = "unknown"
        descriptions.append(desc)
    
    # Filter out boundary-only
    valid_mask = np.array([d != "boundary" for d in descriptions])
    if not valid_mask.all():
        onsets = onsets[valid_mask]
        durations = durations[valid_mask]
        descriptions = [d for d, m in zip(descriptions, valid_mask) if m]
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS004584Kernel:
    KERNEL_ID = "openneuro_ds004584"
    DATASET_NAME = "OpenNeuro DS004584"
    DATASET_DESCRIPTION = "Resting-state EEG dataset (Parkinson's Disease Study). 149 participants (100 PD + 49 healthy controls), eyes-open ~2 min. 63-channel EEG, 500 Hz sampling rate."

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path and dataset root
        file_path = row.get("file_path", "")
        dataset_root = getattr(udataset, "root", None)
        if dataset_root is None:
            dataset_root = os.path.dirname(os.path.dirname(file_path))
        
        # Extract subject ID from file path or row
        subject_id = row.get("subject", "")
        if not subject_id:
            # Try to extract from BIDS path
            parts = file_path.split(os.sep)
            for part in parts:
                if part.startswith("sub-"):
                    subject_id = part.replace("sub-", "")
                    break
        
        # Load participants.tsv
        participants_df = _load_participants_tsv(dataset_root)
        
        # Extract basic subject info
        subject_info = _extract_subject_info(participants_df, subject_id)
        
        # Extract required info fields
        required_info = _extract_required_info_fields(participants_df, subject_id)
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "amplifier": _DEFAULT_AMPLIFIER,
            "cap": _DEFAULT_CAP,
            "handedness": subject_info["handedness"],
        }
        
        # Add required info fields
        for field, value in required_info.items():
            eegunity_description[field.lower()] = value
        
        # Set description in raw.info
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Handle events: check for events.tsv and apply annotations
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path is not None:
            events_df = _load_events_from_tsv(events_tsv_path)
            if events_df is not None and len(events_df) > 0:
                # Create annotations from events.tsv
                annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                # Set annotations on raw (replace existing)
                raw.set_annotations(annotations)
        
        # Add derived misc channels
        # moca_ordinal from MOCA field
        moca_value = required_info.get("MOCA", "unknown")
        moca_ordinal = _compute_moca_ordinal(moca_value)
        
        # Create misc channel data
        n_times = len(raw.times)
        misc_data = np.full((1, n_times), float(moca_ordinal), dtype=np.float64)
        
        # Create info for misc channel
        misc_info = mne.create_info(
            ch_names=["moca_ordinal"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"],
        )
        misc_raw = mne.io.RawArray(misc_data, misc_info, verbose=False)
        
        # Add misc channel to raw
        raw.add_channels([misc_raw], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004584Kernel()