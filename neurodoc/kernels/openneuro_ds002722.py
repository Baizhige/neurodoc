"""OpenNeuro DS002722 stage1 kernel for EEGUnity.

Affective Brain-Computer Music Interface (BCMI) calibration dataset.
EEG and physiological recordings from 19 participants listening to
40-second synthetic music clips with 9 affective conditions.

Source: https://openneuro.org/datasets/ds002722
DOI: 10.1038/s41597-020-0507-6
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


# ============================================================================
# Channel Rename Map
# ============================================================================
# The dataset uses BrainVision format with channel names like 'EEG 001', 'EEG 002', etc.
# plus physiological channels (ECG, GSR, Resp, etc.)
# Source: Paper 10.1038/s41597-020-0507-6, Table 1 - 32-channel EEG cap layout
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG 001": "FC5",
    "EEG 002": "FC3",
    "EEG 003": "FC1",
    "EEG 004": "Fz",
    "EEG 005": "FC2",
    "EEG 006": "FC4",
    "EEG 007": "FC6",
    "EEG 008": "C5",
    "EEG 009": "C3",
    "EEG 010": "C1",
    "EEG 011": "Cz",
    "EEG 012": "C2",
    "EEG 013": "C4",
    "EEG 014": "C6",
    "EEG 015": "CP5",
    "EEG 016": "CP3",
    "EEG 017": "CP1",
    "EEG 018": "CPz",
    "EEG 019": "CP2",
    "EEG 020": "CP4",
    "EEG 021": "CP6",
    "EEG 022": "FP1",
    "EEG 023": "FP2",
    "EEG 024": "F7",
    "EEG 025": "F3",
    "EEG 026": "F4",
    "EEG 027": "F8",
    "EEG 028": "T7",
    "EEG 029": "T8",
    "EEG 030": "P7",
    "EEG 031": "P3",
    "EEG 032": "Pz",
    "EEG 033": "P4",
    "EEG 034": "P8",
    "EEG 035": "O1",
    "EEG 036": "Oz",
    "EEG 037": "O2",
}

# Physiological channel names (keep as-is or rename to standard types)
# Source: Paper 10.1038/s41597-020-0507-6, physiological recordings section
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_PHYSIOLOGICAL_CHANNEL_MAP: Dict[str, str] = {
    "ECG": "ECG",
    "GSR": "GSR",
    "Resp": "Resp",
    "Plethysmograph": "Pleth",
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv from the BIDS dataset root."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_required_info_fields(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Extract required info fields from participants.tsv for eegunity_description.
    
    Required fields: age, sex, handedness, amplifier, cap
    """
    info = {}
    
    if participants_df.empty or "participant_id" not in participants_df.columns:
        for field in ["age", "sex", "handedness", "amplifier", "cap"]:
            info[field] = "unknown"
        return info
    
    subject_row = participants_df[participants_df["participant_id"] == subject_id]
    if subject_row.empty:
        for field in ["age", "sex", "handedness", "amplifier", "cap"]:
            info[field] = "unknown"
        return info
    
    row = subject_row.iloc[0]
    
    # Age
    if "age" in row and pd.notna(row["age"]):
        info["age"] = str(int(float(row["age"])))
    else:
        info["age"] = "unknown"
    
    # Sex (lowercase)
    if "sex" in row and pd.notna(row["sex"]):
        sex_val = str(row["sex"]).strip().lower()
        if sex_val in ("m", "male"):
            info["sex"] = "male"
        elif sex_val in ("f", "female"):
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    else:
        info["sex"] = "unknown"
    
    # Handedness
    if "handedness" in row and pd.notna(row["handedness"]):
        info["handedness"] = str(row["handedness"]).strip().lower()
    else:
        info["handedness"] = "unknown"
    
    # Amplifier - from participants.tsv if available, else unknown
    if "amplifier" in row and pd.notna(row["amplifier"]):
        info["amplifier"] = str(row["amplifier"]).strip()
    else:
        info["amplifier"] = "unknown"
    
    # Cap - from participants.tsv if available, else unknown
    if "cap" in row and pd.notna(row["cap"]):
        info["cap"] = str(row["cap"]).strip()
    else:
        info["cap"] = "unknown"
    
    # Ensure all required fields are present
    for field in ["age", "sex", "handedness", "amplifier", "cap"]:
        if field not in info:
            info[field] = "unknown"
    
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS convention: eeg/<file>.edf -> eeg/<file>_events.tsv
    base_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    
    # Remove extension
    base_name_no_ext = os.path.splitext(base_name)[0]
    
    # Try standard BIDS events.tsv naming
    events_path = os.path.join(base_dir, f"{base_name_no_ext}_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: some datasets use different naming
    for ext in [".vhdr", ".vmrk", ".eeg", ".set", ".edf"]:
        if base_name.endswith(ext):
            alt_name = base_name[:-len(ext)]
            alt_events_path = os.path.join(base_dir, f"{alt_name}_events.tsv")
            if os.path.exists(alt_events_path):
                return alt_events_path
    
    return None


def _load_events_from_tsv(events_path: str) -> pd.DataFrame:
    """Load events from a BIDS events.tsv file."""
    if not os.path.exists(events_path):
        return pd.DataFrame()
    
    df = pd.read_csv(events_path, sep="\t")
    return df


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events DataFrame to MNE Annotations.
    
    Note: onset is in seconds, which is what MNE Annotations expects.
    Do NOT divide by sfreq - MNE Annotations.onset is in seconds.
    """
    if events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Standard BIDS events columns: onset, duration, trial_type, value, sample, etc.
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        
        # Duration: default to 0 if not present or empty
        duration = row.get("duration", 0)
        if pd.isna(duration) or duration == "":
            duration = 0.0
        else:
            duration = float(duration)
        
        # Description: prefer trial_type, then value, then stim_type
        # Use literal string values from the TSV - NO remapping (HC-5)
        desc = None
        for col in ["trial_type", "value", "stim_type"]:
            if col in row and pd.notna(row[col]):
                desc = str(row[col])
                break
        
        if desc is None or desc == "" or desc == "nan":
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _has_native_events(raw: mne.io.BaseRaw) -> bool:
    """Check if the raw file already has meaningful events/annotations."""
    # Check for existing annotations with non-empty descriptions
    if raw.annotations is not None and len(raw.annotations) > 0:
        # Check if descriptions are meaningful (not just empty or "BAD" etc.)
        for desc in raw.annotations.description:
            if desc and not desc.startswith("BAD"):
                return True
    
    # Check for stim channels
    stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
    if len(stim_picks) > 0:
        return True
    
    return False


@dataclass
class OpenNeuroDS002722Kernel:
    """Stage1 kernel for OpenNeuro DS002722 (BCMI calibration dataset)."""

    KERNEL_ID: str = "openneuro-ds002722-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record."""
        # Determine dataset path
        dataset_path = getattr(udataset, "path", None)
        if dataset_path is None:
            dataset_path = os.environ.get("EEG_DATASET_PATH", "")
        
        # Get subject ID from file path or row
        file_path = row.get("file_path", "") if isinstance(row, dict) else str(row)
        subject_match = re.search(r"sub-(\w+)", file_path)
        if subject_match:
            subject_id = f"sub-{subject_match.group(1)}"
        else:
            subject_id = "unknown"
        
        # Load participants.tsv and get required info fields
        participants_df = _load_participants_tsv(dataset_path)
        required_info = _get_required_info_fields(participants_df, subject_id)
        
        # Rename EEG channels
        rename_map = {}
        for ch in raw.ch_names:
            if ch in _EEG_CHANNEL_RENAME_MAP:
                rename_map[ch] = _EEG_CHANNEL_RENAME_MAP[ch]
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set channel types for physiological channels
        channel_types = {}
        for ch in raw.ch_names:
            if ch in _PHYSIOLOGICAL_CHANNEL_MAP:
                ch_type = _PHYSIOLOGICAL_CHANNEL_MAP[ch]
                if ch_type == "ECG":
                    channel_types[ch] = "ecg"
                elif ch_type == "GSR":
                    channel_types[ch] = "gsr"
                elif ch_type == "Resp":
                    channel_types[ch] = "resp"
                else:
                    channel_types[ch] = "misc"
        
        if channel_types:
            raw.set_channel_types(channel_types)
        
        # Always load events from events.tsv if available, regardless of native events
        # The EDF files in this dataset have no native triggers; events.tsv is the source
        events_path = _find_events_tsv(file_path)
        if events_path is not None:
            events_df = _load_events_from_tsv(events_path)
            if not events_df.empty:
                annotations = _events_to_annotations(events_df)
                raw.set_annotations(annotations)
        
        # Set eegunity_description
        eegunity_description = {
            "dataset": "ds002722",
            "dataset_name": "BCMI Calibration Dataset",
            "task": "affective_music_listening",
            "subject_id": subject_id,
            "age": required_info.get("age", "unknown"),
            "sex": required_info.get("sex", "unknown"),
            "handedness": required_info.get("handedness", "unknown"),
            "amplifier": required_info.get("amplifier", "unknown"),
            "cap": required_info.get("cap", "unknown"),
            "channel_count": len(raw.ch_names),
            "sfreq": raw.info["sfreq"],
            "recording_duration_sec": raw.n_times / raw.info["sfreq"],
        }
        
        raw.info["eegunity_description"] = json.dumps(eegunity_description)
        
        return raw


KERNEL = OpenNeuroDS002722Kernel()