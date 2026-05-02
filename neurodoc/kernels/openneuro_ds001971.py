"""Dataset-specific kernel for openneuro_ds001971.

Audiocue walking study - mobile brain-body imaging (MoBI) dataset.
Participants walked on a treadmill and adapted gait to auditory tone sequences.

This dataset uses EEGLAB .set files with embedded event codes. The BIDS events.tsv
files exist but do not contain the full event structure (only UncuedWalking with
value column for heel strikes). The kernel extracts the complete event structure
from native EEGLAB annotations and maps them to canonical event IDs.

Event structure (from native EEGLAB .set files):
- 100: PreferredCadence
- 101: PreferredCadence_stream2
- 103: PreferredCadence_stream3
- 109: PreferredCadence_stream4
- 113: AdvanceTempo
- 114: DelayTempo
- 119: UncuedWalking
- 151: UncuedWalking_stream2
- 153: UncuedWalking_stream3
- 159: UncuedWalking_stream4
- 171: Walking_event_171 (gait cycle marker phase A)
- 200: PreferredCadence_stream5
- 201: PreferredCadence_stream6
- 203: PreferredCadence_stream7
- 209: PreferredCadence_stream8
- 251: UncuedWalking_stream5
- 253: UncuedWalking_stream6
- 259: UncuedWalking_stream7
- 271: Walking_event_271 (gait cycle marker phase B)
- 333: AdvanceTempo_stream2
- 444: DelayTempo_stream2
- 999: admin: marker-999 (BioSemi system status marker)

Required info fields from participants.tsv: age, sex

Source: https://openneuro.org/datasets/ds001971
DOI: 10.1038/s41597-019-0223-2
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


KERNEL_ID = "openneuro_ds001971"

# Event label mapping: raw numeric event ID -> semantic description
# Source: Derived from dataset documentation and paper (DOI: 10.1038/s41597-019-0223-2)
# The mapping combines explicit codes from the data descriptor with inferred stream variants.
# Annotator: LLM, 2026-04-08
# inferred by LLM, needs human review
_EVENT_LABEL_MAP: Dict[int, str] = {
    100: "PreferredCadence",
    101: "PreferredCadence_stream2",   # inferred by LLM, needs human review
    103: "PreferredCadence_stream3",   # inferred by LLM, needs human review
    109: "PreferredCadence_stream4",   # inferred by LLM, needs human review
    113: "AdvanceTempo",
    114: "DelayTempo",
    119: "UncuedWalking",
    151: "UncuedWalking_stream2",       # inferred by LLM, needs human review
    153: "UncuedWalking_stream3",      # inferred by LLM, needs human review
    159: "UncuedWalking_stream4",      # inferred by LLM, needs human review
    171: "Walking_event_171",          # inferred by LLM, needs human review - gait cycle marker phase A
    200: "PreferredCadence_stream5",   # inferred by LLM, needs human review
    201: "PreferredCadence_stream6",   # inferred by LLM, needs human review
    203: "PreferredCadence_stream7",   # inferred by LLM, needs human review
    209: "PreferredCadence_stream8",   # inferred by LLM, needs human review
    251: "UncuedWalking_stream5",      # inferred by LLM, needs human review
    253: "UncuedWalking_stream6",      # inferred by LLM, needs human review
    259: "UncuedWalking_stream7",      # inferred by LLM, needs human review
    271: "Walking_event_271",          # inferred by LLM, needs human review - gait cycle marker phase B
    333: "AdvanceTempo_stream2",       # inferred by LLM, needs human review
    444: "DelayTempo_stream2",         # inferred by LLM, needs human review
    999: "admin: marker-999",
}


def _extract_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _read_participants_tsv(dataset_path: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from dataset root if available."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return None


def _get_subject_info(participants_df: Optional[pd.DataFrame], subject_id: str) -> Dict[str, str]:
    """Extract subject info from participants.tsv DataFrame."""
    info = {
        "age": "unknown",
        "sex": "unknown",
    }
    
    if participants_df is None or subject_id is None:
        return info
    
    # Match subject_id (e.g., "sub-01") with participant_id column
    row = participants_df[participants_df["participant_id"] == subject_id]
    if row.empty:
        # Try without "sub-" prefix
        row = participants_df[participants_df["participant_id"] == subject_id.replace("sub-", "")]
    
    if not row.empty:
        # Get age
        if "age" in row.columns:
            age_val = row["age"].values[0]
            if pd.notna(age_val):
                info["age"] = str(int(float(age_val)))
        
        # Get sex - normalize to lowercase
        if "sex" in row.columns:
            sex_val = row["sex"].values[0]
            if pd.notna(sex_val):
                sex_str = str(sex_val).strip().lower()
                if sex_str in ("m", "male"):
                    info["sex"] = "male"
                elif sex_str in ("f", "female"):
                    info["sex"] = "female"
                else:
                    info["sex"] = "unknown"
        elif "gender" in row.columns:
            gender_val = row["gender"].values[0]
            if pd.notna(gender_val):
                gender_str = str(gender_val).strip().lower()
                if gender_str in ("m", "male"):
                    info["sex"] = "male"
                elif gender_str in ("f", "female"):
                    info["sex"] = "female"
                else:
                    info["sex"] = "unknown"
    
    return info


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read sibling events.tsv for the current EEG file."""
    # Determine events.tsv path from EEG file path
    base_path = file_path.replace("_eeg.set", "").replace(".set", "")
    events_path = base_path + "_events.tsv"
    
    if not os.path.exists(events_path):
        # Try alternative: replace extension
        events_path = file_path.rsplit(".", 1)[0] + "_events.tsv"
    
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    
    return None


def _events_tsv_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv DataFrame to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, event_row in events_df.iterrows():
        onset = float(event_row["onset"])
        
        # Duration: default to 0 if not present or invalid
        if "duration" in event_row and pd.notna(event_row["duration"]):
            duration = float(event_row["duration"])
        else:
            duration = 0.0
        
        # Description: prefer trial_type, fall back to value
        if "trial_type" in event_row and pd.notna(event_row["trial_type"]):
            desc = str(event_row["trial_type"]).strip()
        elif "value" in event_row and pd.notna(event_row["value"]):
            desc = str(event_row["value"]).strip()
        else:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _extract_native_eeglab_events(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract and map native EEGLAB event codes to canonical labels."""
    # Get events from raw annotations (EEGLAB .set files store events here)
    events, event_id = mne.events_from_annotations(raw, verbose=False)
    
    if len(events) == 0:
        return raw.annotations if raw.annotations else mne.Annotations(onset=[], duration=[], description=[])
    
    # Build new annotations with mapped descriptions
    sfreq = raw.info["sfreq"]
    onsets = []
    durations = []
    descriptions = []
    
    # Get original annotations to preserve timing
    orig_annotations = raw.annotations
    
    for i, annot in enumerate(orig_annotations):
        onset = annot["onset"]
        duration = annot["duration"]
        desc = annot["description"]
        
        # Try to map numeric description to canonical label
        # EEGLAB stores events as strings like "100", "101", etc.
        try:
            event_code = int(float(desc))
            mapped_desc = _EVENT_LABEL_MAP.get(event_code, str(event_code))
        except (ValueError, TypeError):
            # Keep original description if not a numeric code
            mapped_desc = desc
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(mapped_desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


class OpenneuroDs001971Kernel:
    KERNEL_ID = "openneuro_ds001971"
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path and dataset path
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        dataset_path = udataset.dataset_path if hasattr(udataset, "dataset_path") else os.path.dirname(file_path)
        
        # Extract subject ID
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Read participants.tsv
        participants_df = _read_participants_tsv(dataset_path)
        
        # Get subject info
        subject_info = _get_subject_info(participants_df, subject_id)
        
        # Read events.tsv (for heel strike data)
        events_df = _read_events_tsv(file_path)
        
        # Extract native EEGLAB events with canonical labels
        native_annotations = _extract_native_eeglab_events(raw)
        
        # Combine native annotations with events.tsv annotations if available
        if events_df is not None and not events_df.empty:
            events_tsv_annotations = _events_tsv_to_annotations(events_df, raw.info["sfreq"])
            
            # Combine annotations: native first, then events.tsv
            all_onsets = list(native_annotations.onset) + list(events_tsv_annotations.onset)
            all_durations = list(native_annotations.duration) + list(events_tsv_annotations.duration)
            all_descriptions = list(native_annotations.description) + list(events_tsv_annotations.description)
            
            combined_annotations = mne.Annotations(
                onset=all_onsets,
                duration=all_durations,
                description=all_descriptions,
            )
            raw.set_annotations(combined_annotations)
        else:
            raw.set_annotations(native_annotations)
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": "BioSemi ActiveTwo",
            "cap": "64-channel BioSemi cap",
            "handedness": "unknown",
        }
        
        # Get original description
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenneuroDs001971Kernel()