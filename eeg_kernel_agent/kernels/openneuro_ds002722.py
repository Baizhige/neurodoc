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


def _get_subject_info(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Extract subject info from participants DataFrame."""
    if participants_df.empty or "participant_id" not in participants_df.columns:
        return {}
    
    subject_row = participants_df[participants_df["participant_id"] == subject_id]
    if subject_row.empty:
        return {}
    
    info = {}
    row = subject_row.iloc[0]
    
    # Age
    if "age" in row and pd.notna(row["age"]):
        info["age"] = str(int(float(row["age"])))
    else:
        info["age"] = "unknown"
    
    # Sex
    if "sex" in row and pd.notna(row["sex"]):
        sex_val = str(row["sex"]).strip().lower()
        if sex_val in ("f", "female"):
            info["sex"] = "female"
        elif sex_val in ("m", "male"):
            info["sex"] = "male"
        else:
            info["sex"] = "unknown"
    else:
        info["sex"] = "unknown"
    
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.<ext> -> sub-XX_task-YY_run-ZZ_events.tsv
    base = file_path
    
    # Remove common EEG extensions
    for ext in [".eeg", ".vhdr", ".vmrk", ".edf", ".bdf", ".set", ".fdt"]:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Try exact match first
    events_path = base.replace("_eeg", "_events") + ".tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try with _events.tsv suffix
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Search in same directory for matching events file
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(base)
    
    # Extract subject/task/run info
    pattern = r"(sub-[a-zA-Z0-9]+)(?:_(task-[a-zA-Z0-9]+))?(?:_(run-[a-zA-Z0-9]+))?"
    match = re.match(pattern, os.path.basename(file_name))
    
    if match:
        sub, task, run = match.groups()
        search_pattern = f"{sub}_"
        if task:
            search_pattern += f"{task}_"
        if run:
            search_pattern += f"{run}_"
        search_pattern += "events.tsv"
        
        for f in os.listdir(dir_path):
            if f.endswith("events.tsv") and sub in f:
                if (task is None or task in f) and (run is None or run in f):
                    return os.path.join(dir_path, f)
    
    return None


def _load_events_from_tsv(events_path: str) -> pd.DataFrame:
    """Load events from a BIDS events.tsv file."""
    df = pd.read_csv(events_path, sep="\t")
    # Ensure required columns exist
    if "onset" not in df.columns:
        raise ValueError(f"events.tsv missing 'onset' column: {events_path}")
    return df


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events DataFrame to MNE Annotations."""
    onsets = events_df["onset"].values.astype(float)
    
    # Duration: use column if present, default to 0
    if "duration" in events_df.columns:
        durations = events_df["duration"].values.astype(float)
        # Replace NaN or missing with 0
        durations = np.where(np.isnan(durations), 0, durations)
    else:
        durations = np.zeros(len(onsets))
    
    # Description: prefer 'trial_type', then 'value', then 'stim_type'
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["unknown"] * len(onsets))
    
    # Filter out empty/NaN descriptions
    valid_mask = pd.notna(descriptions) & (descriptions != "nan") & (descriptions != "")
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS002722Kernel:
    """Stage1 kernel for OpenNeuro DS002722 (BCMI calibration dataset)."""

    KERNEL_ID: str = "openneuro-ds002722-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "root_path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from file path
        # BIDS format: sub-01, sub-02, etc.
        subject_match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
        subject_id = subject_match.group(1) if subject_match else "unknown"
        
        # =====================================================================
        # 1. Load participants.tsv and extract subject info
        # =====================================================================
        participants_df = _load_participants_tsv(dataset_path)
        subject_info = _get_subject_info(participants_df, subject_id)
        
        # =====================================================================
        # 2. Build eegunity_description
        # =====================================================================
        # Device info from paper: Brain Products BrainAmp MR plus, actiCAP
        # Source: Paper 10.1038/s41597-020-0507-6, Methods section
        # Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": "BrainAmp MR plus",  # LLM 推断，需人类复核
            "cap": "actiCAP (Ag/AgCl)",  # LLM 推断，需人类复核
            "handedness": "unknown",  # not reported in participants.tsv
        }
        
        # Add required info fields from participants.tsv
        # Required: ['age', 'sex'] - these are already in eegunity_description above
        
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # =====================================================================
        # 3. Channel renaming (BEFORE set_montage)
        # =====================================================================
        rename_map = {}
        for old_name, new_name in _EEG_CHANNEL_RENAME_MAP.items():
            if old_name in raw.ch_names and old_name != new_name:
                rename_map[old_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for physiological channels
        channel_types = {}
        for ch_name in raw.ch_names:
            # Check if it's a physiological channel
            base_name = ch_name.replace(" ", "")
            if base_name in _PHYSIOLOGICAL_CHANNEL_MAP:
                # Map to appropriate MNE channel type
                phys_name = _PHYSIOLOGICAL_CHANNEL_MAP[base_name]
                if phys_name == "ECG":
                    channel_types[ch_name] = "ecg"
                else:
                    channel_types[ch_name] = "misc"
        
        if channel_types:
            raw.set_channel_types(channel_types)
        
        # Set montage for EEG channels
        # Use standard_1020 since we have standard named channels
        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
        if len(eeg_picks) > 0:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, match_case=False, on_missing="ignore")
            except Exception:
                pass  # Montage setting failed, continue without it
        
        # =====================================================================
        # 4. Handle events from events.tsv
        # =====================================================================
        # EDF files in this dataset do not carry annotations/triggers internally.
        # We must derive annotations from sibling events.tsv.
        events_path = _find_events_tsv(file_path)
        
        if events_path and os.path.exists(events_path):
            try:
                events_df = _load_events_from_tsv(events_path)
                annotations = _events_to_annotations(events_df)
                
                # Combine with existing annotations if any
                existing_annotations = raw.annotations
                if existing_annotations is not None and len(existing_annotations) > 0:
                    raw.set_annotations(existing_annotations + annotations)
                else:
                    raw.set_annotations(annotations)
            except Exception:
                pass  # Events loading failed, continue without them
        
        # =====================================================================
        # 5. Final info adjustments
        # =====================================================================
        raw.info["subject_info"] = {
            "his_id": subject_id,
            "age": int(subject_info.get("age", 0)) if subject_info.get("age", "unknown") != "unknown" else None,
            "sex": 1 if subject_info.get("sex") == "male" else (2 if subject_info.get("sex") == "female" else 0),
        }
        
        return raw


KERNEL = OpenNeuroDS002722Kernel()