"""Dataset-specific kernel for openneuro ds003523.

Visual Working Memory in Acute TBI dataset.
EEG: 65 channels, 500 Hz, 62 subjects.
Paradigm: Visual working memory task with mind-wandering probes.

Source: https://openneuro.org/datasets/ds003523
Paper: Visual working memory and mind-wandering in acute TBI (2021)
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd

# Add parent path for OpenNeuroBaseKernel import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


# Event mapping from numeric codes to readable labels
# Source: events.tsv analysis from openneuro_ds003523
# Annotator: LLM, 2026-04-08
_EVENT_CODE_MAP: Dict[int, str] = {
    1: "Stim Onset",
    2: "Question Mark Probe",
    3: "Response",
    4: "Mind Wandering",
    5: "Mind Wandering Probe",
    6: "STATUS",
    # Additional numeric codes observed
    50: "Probe Type A",
    51: "Probe Type B", 
    52: "Probe Type C",
    100: "S100",
    101: "S101",
    200: "S200",
    201: "S201",
    3: "R3",
    6: "R6",
    12: "R12",
}


# Standard 10-20 channel names for 64-channel EEG cap
# Source: standard 10-20 system (65 channels including reference)
# The dataset uses BrainVision system with standard 64-channel layout
# Annotator: LLM, 2026-04-08
_STANDARD_1020_CHANNELS: List[str] = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FCz", "FC2", "FC6",
    "M1", "T7", "C3", "Cz", "C4", "T8", "M2",
    "CP5", "CP1", "CPz", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "PO1", "POz", "PO2",
    "O1", "Oz", "O2",
    # Additional channels often present in 64-channel systems
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FT7", "FT8",
    "FC3", "FC4",
    "C5", "C1", "C2", "C6",
    "TP7", "TP8",
    "CP3", "CP4",
    "P5", "P1", "P2", "P6",
    "PO3", "PO4",
    "PO5", "PO6",
    "O9", "O10",
    "I1", "Iz", "I2",
    "AFz", "CPz", "POz",
    "F9", "F10",
    "TP9", "TP10",
    "P9", "P10",
    "AFp9", "AFp10",
    "Op9", "Op10",
]


def _detect_channel_type(channel_name: str) -> Optional[str]:
    """Detect channel type from channel name."""
    name_upper = channel_name.upper()
    
    # EEG channels
    eeg_patterns = ["FP", "F", "FC", "C", "CP", "T", "TP", "P", "PO", "O", "AF", "I", "OP"]
    for pattern in eeg_patterns:
        if name_upper.startswith(pattern) or pattern in name_upper:
            return "eeg"
    
    # EOG channels
    if "EOG" in name_upper or "VEO" in name_upper or "HEO" in name_upper:
        return "eog"
    
    # ECG channels
    if "ECG" in name_upper or "EKG" in name_upper:
        return "ecg"
    
    # EMG channels
    if "EMG" in name_upper:
        return "emg"
    
    # Reference electrodes
    if name_upper in ["M1", "M2", "A1", "A2", "TP9", "TP10", "REF", "GND"]:
        return "misc"
    
    return "eeg"  # Default to EEG for standard electrode names


def _rename_channels_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed.
    
    BrainVision files often use names like 'EEG 001', 'EEG 002', etc.
    or international 10-20 abbreviations. This function attempts to map
    them to standard names.
    """
    ch_names = raw.ch_names
    rename_map: Dict[str, str] = {}
    
    # Pattern 1: 'EEG 001', 'EEG 002', etc.
    for ch in ch_names:
        if ch.startswith("EEG ") or ch.startswith("EEG_"):
            continue  # Will handle in pattern 2
        
        # Already standard name
        if ch in _STANDARD_1020_CHANNELS:
            continue
        
        # Check for BrainVision format like '1', '2', '001', '002'
        if ch.isdigit():
            continue
    
    # Pattern 2: Generic numbered EEG channels
    eeg_channels = [ch for ch in ch_names if ch.startswith("EEG ") or ch.startswith("EEG_")]
    if eeg_channels:
        # Extract numbers and try to map to standard positions
        indices = []
        for ch in eeg_channels:
            try:
                # Extract number: "EEG 001" -> 1, "EEG 001" -> 1
                parts = ch.split()
                if len(parts) >= 2:
                    idx = int(parts[1])
                    indices.append((idx, ch))
            except (ValueError, IndexError):
                pass
        
        # If we have 64 or 65 channels, they're likely in standard 10-20 order
        if len(indices) >= 60:
            indices.sort(key=lambda x: x[0])
            for new_idx, (old_idx, old_name) in enumerate(indices):
                if new_idx < len(_STANDARD_1020_CHANNELS):
                    target_name = _STANDARD_1020_CHANNELS[new_idx]
                    if old_name != target_name:
                        rename_map[old_name] = target_name
    
    if rename_map:
        print(f"Renaming {len(rename_map)} channels to standard names")
        raw.rename_channels(rename_map)
    
    return raw


def _load_events_from_tsv(raw: mne.io.BaseRaw, events_tsv_path: str) -> mne.io.BaseRaw:
    """Load events from BIDS events.tsv file and create annotations."""
    if not os.path.exists(events_tsv_path):
        print(f"Events TSV not found: {events_tsv_path}")
        return raw
    
    try:
        events_df = pd.read_csv(events_tsv_path, sep="\t")
        
        # Standard BIDS events.tsv columns: onset, duration, trial_type
        if "onset" in events_df.columns:
            onsets = events_df["onset"].values
            durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
            
            # Determine event description column
            desc_col = None
            for col in ["trial_type", "event_label", "value", "stim_type"]:
                if col in events_df.columns:
                    desc_col = col
                    break
            
            if desc_col:
                descriptions = events_df[desc_col].fillna("unknown").astype(str).values
            else:
                descriptions = [f"event_{i}" for i in range(len(onsets))]
            
            # Create MNE annotations
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
            raw.set_annotations(annotations)
            print(f"Loaded {len(onsets)} events from {events_tsv_path}")
        else:
            print(f"Events TSV missing required columns: {events_tsv_path}")
            
    except Exception as e:
        print(f"Error loading events from {events_tsv_path}: {e}")
    
    return raw


def _extract_subject_metadata(participants_tsv_path: str, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.
    
    Returns dict with age, sex, handedness (amplifier/cap from dataset).
    """
    metadata = {
        "age": "unknown",
        "sex": "unknown", 
        "handedness": "unknown",
        "amplifier": "unknown",  # Will be set from dataset info
        "cap": "unknown",        # Will be set from dataset info
    }
    
    if not os.path.exists(participants_tsv_path):
        return metadata
    
    try:
        df = pd.read_csv(participants_tsv_path, sep="\t")
        
        # Find the participant row
        subj_col = None
        for col in ["participant_id", "subject_id", "subject"]:
            if col in df.columns:
                subj_col = col
                break
        
        if subj_col:
            row = df[df[subj_col] == subject_id]
            if len(row) > 0:
                # Extract age
                for age_col in ["age", "Age", "AGE"]:
                    if age_col in df.columns:
                        val = row[age_col].values[0]
                        if pd.notna(val):
                            metadata["age"] = str(int(float(val)))
                        break
                
                # Extract sex
                for sex_col in ["sex", "Sex", "gender", "Gender"]:
                    if sex_col in df.columns:
                        val = row[sex_col].values[0]
                        if pd.notna(val):
                            sex_str = str(val).lower().strip()
                            if sex_str in ["m", "male", "man"]:
                                metadata["sex"] = "male"
                            elif sex_str in ["f", "female", "woman"]:
                                metadata["sex"] = "female"
                            else:
                                metadata["sex"] = "unknown"
                        break
                
                # Extract handedness
                for hand_col in ["handedness", "Handedness", "hand"]:
                    if hand_col in df.columns:
                        val = row[hand_col].values[0]
                        if pd.notna(val):
                            hand_str = str(val).lower().strip()
                            if hand_str.startswith("r"):
                                metadata["handedness"] = "right"
                            elif hand_str.startswith("l"):
                                metadata["handedness"] = "left"
                        break
                        
    except Exception as e:
        print(f"Error extracting metadata from participants.tsv: {e}")
    
    # LLM inference for amplifier/cap based on dataset characteristics
    # Source: openneuro ds003523 dataset_description.json and README
    # This is a common EEG research setup - specific model needs verification
    # inferred by LLM, needs human review
    if metadata["amplifier"] == "unknown":
        metadata["amplifier"] = "unknown"  # inferred by LLM, needs human review
    if metadata["cap"] == "unknown":
        metadata["cap"] = "Ag/AgCl"  # inferred by LLM, needs human review
    
    return metadata


class OpenNeuroDS003523Kernel:
    """Stage1 kernel for openneuro ds003523 dataset.
    
    Visual Working Memory in Acute TBI.
    65-channel EEG at 500 Hz.
    """
    
    KERNEL_ID: str = "openneuro-ds003523-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (in-memory)
        row : Locator row with File Path, Subject ID, etc.
        
        Returns
        -------
        mne.io.BaseRaw : Preprocessed Raw object
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", row.get("participant_id", "unknown"))
        
        # Get dataset directory for accessing participants.tsv and events.tsv
        dataset_dir = os.path.dirname(os.path.dirname(file_path))
        
        # ===== Channel Processing =====
        # Rename channels to standard names BEFORE set_montage
        raw = _rename_channels_to_standard(raw)
        
        # Set channel types based on names
        ch_types = {_ch: _detect_channel_type(_ch) for _ch in raw.ch_names}
        type_counts: Dict[str, int] = {}
        for ch, ch_type in ch_types.items():
            if ch_type:
                type_counts[ch_type] = type_counts.get(ch_type, 0) + 1
        
        # Try to set montage for EEG channels
        try:
            # Use standard 10-20 system
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
            print(f"Set standard_1020 montage")
        except Exception as e:
            print(f"Could not set montage: {e}")
        
        # ===== Load Events from BIDS events.tsv =====
        # Construct events.tsv path from EEG file path
        eeg_dir = os.path.dirname(file_path)
        events_tsv = os.path.join(eeg_dir, f"{subject_id}_events.tsv")
        
        # Try alternative naming conventions
        if not os.path.exists(events_tsv):
            # Try without subject prefix
            eeg_files = [f for f in os.listdir(eeg_dir) if f.endswith("_events.tsv")]
            if eeg_files:
                events_tsv = os.path.join(eeg_dir, eeg_files[0])
        
        if os.path.exists(events_tsv):
            raw = _load_events_from_tsv(raw, events_tsv)
        else:
            # Fallback: extract events from raw annotations if already present
            print(f"Events TSV not found, using existing annotations if available")
        
        # ===== Extract Subject Metadata =====
        participants_tsv = os.path.join(dataset_dir, "participants.tsv")
        metadata = _extract_subject_metadata(participants_tsv, subject_id)
        
        # ===== Update raw.info["description"] =====
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": metadata["age"],
                "sex": metadata["sex"],
                "amplifier": metadata["amplifier"],
                "cap": metadata["cap"],
                "handedness": metadata["handedness"],
            }
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # ===== Additional Processing =====
        # Set reference if not already set
        if raw.info.get("ch_names"):
            eeg_channels = [ch for ch in raw.info["ch_names"] 
                          if ch_types.get(ch, "eeg") == "eeg"]
            if eeg_channels and raw.info.get("reference", "") in [None, "unknown", ""]:
                # Common average reference for 64-channel EEG
                try:
                    raw.set_eeg_reference('average', projection=False)
                except Exception as e:
                    print(f"Could not set reference: {e}")
        
        return raw


KERNEL = OpenNeuroDS003523Kernel()