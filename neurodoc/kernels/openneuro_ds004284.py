"""OpenNeuro ds004284 (EEG Neuroforecasting) stage1 kernel for EEGUnity.

Dataset: eeg-neuroforecasting
Source: https://openneuro.org/datasets/ds004284
DOI: https://doi.org/10.18112/openneuro.ds004284.v1.0.0
Paper: https://doi.org/10.1038/s41598-023-41613-4

This kernel handles the EEG neuroforecasting dataset with Kickstarter
decision-making paradigm. The dataset contains 129-channel EEG recordings
from 18 subjects viewing Kickstarter project presentations and making
funding decisions.

Key features:
- 129-channel EEG (EGI Hydrocel GSN 128 + reference)
- Sampling rate: 1000 Hz
- Events derived from BIDS events.tsv sidecars (segment events with funded/project_id)
- Derived misc channels for neuroforecasting tasks:
  * funded_continuous: per-trial binary funding decision (0/1)
  * project_funding_rate: aggregate funding rate per project across subjects
  * subject_consistency: subject's choice consistency with population average

Channel Configuration:
- 129 EEG channels using EGI Hydrocel GSN 128 naming convention
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Dataset Metadata
# =============================================================================

# Source: OpenNeuro ds004284 dataset_description.json and paper
# https://doi.org/10.1038/s41598-023-41613-4
# Annotator: LLM, 2026-04-08
_DATASET_INFO = {
    "amplifier": "EGI Net Amps 300",  # inferred by LLM, needs human review
    "cap": "EGI Hydrocel GSN 128",  # inferred by LLM, needs human review
}

# Required info fields from participants.tsv to include in eegunity_description
# These will be read dynamically and attached as string values
_REQUIRED_INFO_FIELDS: List[str] = ["age", "sex", "handedness"]

# Required native misc channels (ensure they exist as 'misc' type)
_REQUIRED_NATIVE_MISC: List[str] = []

# Required derived misc channels (kernel must create these)
_REQUIRED_DERIVED_MISC: List[str] = ["funded_continuous", "project_funding_rate", "subject_consistency"]


# =============================================================================
# Helper Functions
# =============================================================================

def _detect_subject_id(row) -> str:
    """Extract subject ID from file path using BIDS convention."""
    file_path = row.get("File Path", "")
    # BIDS format: sub-104, sub-105, etc.
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return f"sub-{match.group(1)}"
    return "unknown"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XXX_task-YYY_eeg.edf -> sub-XXX_task-YYY_events.tsv
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: same directory, any events.tsv matching subject
    dir_path = os.path.dirname(file_path)
    subject_match = re.search(r"sub-(\d+)", file_path)
    if subject_match:
        subject_id = subject_match.group(0)
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv") and subject_id in f:
                return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    for _ in range(5):  # Walk up at most 5 levels
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    if events_path and os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    return pd.DataFrame()


def _read_participants_tsv(participants_path: str) -> pd.DataFrame:
    """Read participants.tsv file."""
    if participants_path and os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_from_participants(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Get subject info from participants dataframe."""
    if participants_df.empty or "participant_id" not in participants_df.columns:
        return {}
    
    subject_row = participants_df[participants_df["participant_id"] == subject_id]
    if subject_row.empty:
        return {}
    
    result = {}
    for col in participants_df.columns:
        if col != "participant_id":
            val = subject_row.iloc[0][col]
            # Convert to string, handle NaN
            if pd.isna(val):
                result[col] = "unknown"
            else:
                result[col] = str(val)
    return result


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex value to lowercase standard."""
    if not sex_val or sex_val.lower() in ("unknown", "n/a", "na", ""):
        return "unknown"
    sex_lower = sex_val.lower()
    if sex_lower in ("m", "male"):
        return "male"
    elif sex_lower in ("f", "female"):
        return "female"
    return "unknown"


def _create_annotations_from_events(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.Annotations:
    """Create MNE Annotations from BIDS events.tsv dataframe."""
    if events_df.empty or "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Use trial_type if available, otherwise value, otherwise description
    # For this dataset, trial_type contains "image" which is the event type
    # We use trial_type as the annotation description (literal string, no remapping per HC-5)
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    elif "description" in events_df.columns:
        descriptions = events_df["description"].astype(str).values
    else:
        descriptions = np.array(["segment"] * len(onsets))
    
    # Create annotations with literal strings from events.tsv (no remapping per HC-5)
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions.tolist(),
    )
    return annotations


def _create_derived_misc_channel(raw: mne.io.BaseRaw, channel_name: str, values: np.ndarray) -> mne.io.BaseRaw:
    """Create a derived misc channel with given values and add to raw."""
    # Ensure values match raw length
    n_samples = len(raw.times)
    if len(values) != n_samples:
        # Interpolate or pad if needed
        if len(values) < n_samples:
            # Repeat/extend to match length
            repeated = np.tile(values, int(np.ceil(n_samples / len(values))))[:n_samples]
            values = repeated
        else:
            values = values[:n_samples]
    
    # Create info for new channel
    info = mne.create_info(
        ch_names=[channel_name],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    
    # Create RawArray
    data = values.reshape(1, -1)
    raw_misc = mne.io.RawArray(data, info, verbose=False)
    
    # Add to existing raw
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


def _compute_project_funding_rate(events_df: pd.DataFrame) -> Dict[Any, float]:
    """Compute project-level funding rate across all subjects."""
    if events_df.empty or "project_id" not in events_df.columns or "funded" not in events_df.columns:
        return {}
    
    # Group by project_id and compute mean funded rate
    funding_rates = events_df.groupby("project_id")["funded"].mean().to_dict()
    return funding_rates


def _compute_subject_consistency(events_df: pd.DataFrame, subject_funding: Dict[Any, float]) -> float:
    """Compute how consistent subject's choices are with population average."""
    if events_df.empty or "project_id" not in events_df.columns or "funded" not in events_df.columns:
        return 0.5
    
    # For each project, compare subject choice to population rate
    consistencies = []
    for _, row in events_df.iterrows():
        project_id = row["project_id"]
        funded = row["funded"]
        if project_id in subject_funding:
            pop_rate = subject_funding[project_id]
            # Consistency: 1 if choice aligns with majority, 0 otherwise
            if pop_rate >= 0.5 and funded == 1:
                consistencies.append(1.0)
            elif pop_rate < 0.5 and funded == 0:
                consistencies.append(1.0)
            else:
                consistencies.append(0.0)
    
    if not consistencies:
        return 0.5
    return float(np.mean(consistencies))


# =============================================================================
# Kernel Class
# =============================================================================

class OpenNeuroDS004284Kernel:
    KERNEL_ID = "openneuro_ds004284"
    DATASET_NAME = "eeg-neuroforecasting"
    VERSION = "1.0.0"

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract subject ID
        subject_id = _detect_subject_id(row)
        file_path = row.get("File Path", "")
        
        # Find and read participants.tsv
        participants_path = _find_participants_tsv(file_path)
        participants_df = _read_participants_tsv(participants_path)
        subject_info = _get_subject_from_participants(participants_df, subject_id)
        
        # Find and read events.tsv
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path)
        
        # Build eegunity_description with required fields from participants.tsv
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": _normalize_sex(subject_info.get("sex", "unknown")),
            "amplifier": _DATASET_INFO["amplifier"],
            "cap": _DATASET_INFO["cap"],
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Add any additional required info fields that exist
        for field in _REQUIRED_INFO_FIELDS:
            if field in subject_info and field not in eegunity_description:
                eegunity_description[field] = subject_info[field]
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Apply annotations from events.tsv if available
        if not events_df.empty:
            annotations = _create_annotations_from_events(raw, events_df)
            # Set annotations, replacing any existing ones
            raw.set_annotations(annotations)
        
        # Create derived misc channels
        n_samples = len(raw.times)
        sfreq = raw.info["sfreq"]
        
        # funded_continuous: per-trial binary funding decision broadcast to all samples in trial
        if "funded" in events_df.columns and "onset" in events_df.columns:
            funded_values = np.zeros(n_samples)
            for _, evt in events_df.iterrows():
                onset = float(evt["onset"])
                duration = float(evt["duration"]) if "duration" in evt and pd.notna(evt["duration"]) else 0.0
                funded_val = float(evt["funded"]) if pd.notna(evt["funded"]) else 0.0
                
                # Convert to sample indices
                start_sample = int(onset * sfreq)
                end_sample = int((onset + duration) * sfreq) if duration > 0 else start_sample + 1
                start_sample = max(0, min(start_sample, n_samples))
                end_sample = max(0, min(end_sample, n_samples))
                
                if start_sample < end_sample:
                    funded_values[start_sample:end_sample] = funded_val
            
            # Only add if we have valid funded data
            if len(events_df) > 0 and "funded" in events_df.columns:
                raw = _create_derived_misc_channel(raw, "funded_continuous", funded_values)
        
        # project_funding_rate: group events.tsv by project_id, compute mean funded rate per project
        if "funded" in events_df.columns and "project_id" in events_df.columns:
            project_funding_rates = _compute_project_funding_rate(events_df)
            
            if project_funding_rates:
                project_rate_values = np.zeros(n_samples)
                for _, evt in events_df.iterrows():
                    onset = float(evt["onset"])
                    duration = float(evt["duration"]) if "duration" in evt and pd.notna(evt["duration"]) else 0.0
                    project_id = evt["project_id"]
                    
                    if project_id in project_funding_rates:
                        rate_val = project_funding_rates[project_id]
                        
                        # Convert to sample indices
                        start_sample = int(onset * sfreq)
                        end_sample = int((onset + duration) * sfreq) if duration > 0 else start_sample + 1
                        start_sample = max(0, min(start_sample, n_samples))
                        end_sample = max(0, min(end_sample, n_samples))
                        
                        if start_sample < end_sample:
                            project_rate_values[start_sample:end_sample] = rate_val
                
                raw = _create_derived_misc_channel(raw, "project_funding_rate", project_rate_values)
        
        # subject_consistency: compute agreement between subject's choices and population average
        if "funded" in events_df.columns and "project_id" in events_df.columns:
            # Compute population-level funding rates (need all subjects' data)
            # We use the events_df we have; for a single file this is just that subject's events
            # To get population rates, we need to aggregate across all events files
            # Since we only have this file's events, we compute project rates from available data
            # In practice, with full dataset all subjects' events would be pooled
            
            # Try to find all events.tsv files in the dataset for population aggregation
            all_events_dfs = []
            if file_path:
                dataset_root = os.path.dirname(file_path)
                # Walk up to find dataset root (where participants.tsv is)
                for _ in range(5):
                    if os.path.exists(os.path.join(dataset_root, "participants.tsv")):
                        break
                    parent = os.path.dirname(dataset_root)
                    if parent == dataset_root:
                        break
                    dataset_root = parent
                
                # Search for all events.tsv files
                for root, dirs, files in os.walk(dataset_root):
                    for f in files:
                        if f.endswith("_events.tsv"):
                            full_path = os.path.join(root, f)
                            try:
                                df = pd.read_csv(full_path, sep="\t")
                                if "funded" in df.columns and "project_id" in df.columns:
                                    all_events_dfs.append(df)
                            except Exception:
                                pass
            
            # Compute population funding rates from all available events
            if all_events_dfs:
                all_events = pd.concat(all_events_dfs, ignore_index=True)
                pop_funding_rates = _compute_project_funding_rate(all_events)
            else:
                # Fallback: use current file's events only (degenerate but valid)
                pop_funding_rates = _compute_project_funding_rate(events_df)
            
            # Compute subject consistency
            consistency_score = _compute_subject_consistency(events_df, pop_funding_rates)
            
            # Broadcast as constant channel
            consistency_values = np.full(n_samples, consistency_score)
            raw = _create_derived_misc_channel(raw, "subject_consistency", consistency_values)
        
        return raw


KERNEL = OpenNeuroDS004284Kernel()