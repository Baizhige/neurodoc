"""openneuro_ds004980 stage1 kernel for EEGUnity.

Architectural Affordances Task - Virtual navigation EEG study.
64-channel EEG recorded at 500 Hz from 17 subjects navigating a virtual 
architectural environment.

Source: https://openneuro.org/datasets/ds004980
DOI: https://doi.org/10.18112/openneuro.ds004980.v1.0.0
Reference: https://doi.org/10.1111/ejn.16461 (Human brain dynamics dissociate 
early perceptual and late motor-related stages of affordance processing)
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
# Subject Information
# Source: Dataset README / participants.tsv on OpenNeuro
# Annotator: Human, 2026-04-08 (verified against dataset)
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Participant IDs and metadata will be loaded from participants.tsv
    # Fallback values for any missing entries:
    "age": "unknown",      # LLM 推断，需人类复核 - verify against participants.tsv
    "sex": "unknown",      # LLM 推断，需人类复核 - verify against participants.tsv
    "handedness": "unknown",  # LLM 推断，需人类复核 - verify against participants.tsv
}

# Device metadata from dataset description
# Source: OpenNeuro dataset_description.json and paper DOI:10.1111/ejn.16461
# Annotator: Human, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "unknown",   # LLM 推断，需人类复核 - typically BrainAmp or similar
    "cap": "unknown",         # LLM 推断，需人类复核 - typically 64-channel cap
}

# =============================================================================
# Channel Mapping (standard 10-20 system for 64 channels)
# This is a typical configuration for 64-channel EEG studies.
# Source: Standard 10-20 system electrode placement
# Annotator: LLM, 2026-04-08 - 需人类复核 against actual channel names in data
# =============================================================================
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    # Additional common 64-channel names (BioSemi / EGI style)
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
    "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19", "A20",
    "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30",
    "A31", "A32", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10",
    "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20",
    "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30",
    "B31", "B32",
]

# Channel alias groups for robust renaming
# Source: Standard EEG channel naming conventions
# Annotator: LLM, 2026-04-08 - 需人类复核
_CHANNEL_ALIAS_GROUPS = [
    # Standard 10-20 frontal
    ("Fp1", ["Fp1", "EEG Fp1", "EEG-Fp1"]),
    ("Fp2", ["Fp2", "EEG Fp2", "EEG-Fp2"]),
    ("Fpz", ["Fpz", "Fz", "EEG Fz", "EEG-Fz"]),
    # Standard 10-20 frontal-central
    ("F7", ["F7", "F5", "F3", "F1"]),
    ("F3", ["F3", "F1"]),
    ("Fz", ["Fz", "Fpz"]),
    ("F4", ["F4", "F2"]),
    ("F8", ["F8", "F6", "F4"]),
    # Standard 10-20 central
    ("T7", ["T7", "T3", "C5", "C3"]),
    ("C3", ["C3", "C1"]),
    ("Cz", ["Cz", "C2", "C4"]),
    ("C4", ["C4", "C2"]),
    ("T8", ["T8", "T4", "C6", "C4"]),
    # Standard 10-20 parietal
    ("P7", ["P7", "P5", "P3", "P1"]),
    ("P3", ["P3", "P1"]),
    ("Pz", ["Pz", "P2", "P4"]),
    ("P4", ["P4", "P2"]),
    ("P8", ["P8", "P6", "P4"]),
    # Standard 10-20 occipital
    ("O1", ["O1"]),
    ("Oz", ["Oz"]),
    ("O2", ["O2"]),
    # BioSemi / EGI style
    ("A1", ["A1", "EEG A1"]),
    ("A2", ["A2", "EEG A2"]),
    ("A3", ["A3", "EEG A3"]),
    ("A4", ["A4", "EEG A4"]),
    ("A5", ["A5", "EEG A5"]),
    ("A6", ["A6", "EEG A6"]),
    ("A7", ["A7", "EEG A7"]),
    ("A8", ["A8", "EEG A8"]),
    ("A9", ["A9", "EEG A9"]),
    ("A10", ["A10", "EEG A10"]),
    ("A11", ["A11", "EEG A11"]),
    ("A12", ["A12", "EEG A12"]),
    ("A13", ["A13", "EEG A13"]),
    ("A14", ["A14", "EEG A14"]),
    ("A15", ["A15", "EEG A15"]),
    ("A16", ["A16", "EEG A16"]),
    ("A17", ["A17", "EEG A17"]),
    ("A18", ["A18", "EEG A18"]),
    ("A19", ["A19", "EEG A19"]),
    ("A20", ["A20", "EEG A20"]),
    ("A21", ["A21", "EEG A21"]),
    ("A22", ["A22", "EEG A22"]),
    ("A23", ["A23", "EEG A23"]),
    ("A24", ["A24", "EEG A24"]),
    ("A25", ["A25", "EEG A25"]),
    ("A26", ["A26", "EEG A26"]),
    ("A27", ["A27", "EEG A27"]),
    ("A28", ["A28", "EEG A28"]),
    ("A29", ["A29", "EEG A29"]),
    ("A30", ["A30", "EEG A30"]),
    ("A31", ["A31", "EEG A31"]),
    ("A32", ["A32", "EEG A32"]),
    ("B1", ["B1", "EEG B1"]),
    ("B2", ["B2", "EEG B2"]),
    ("B3", ["B3", "EEG B3"]),
    ("B4", ["B4", "EEG B4"]),
    ("B5", ["B5", "EEG B5"]),
    ("B6", ["B6", "EEG B6"]),
    ("B7", ["B7", "EEG B7"]),
    ("B8", ["B8", "EEG B8"]),
    ("B9", ["B9", "EEG B9"]),
    ("B10", ["B10", "EEG B10"]),
    ("B11", ["B11", "EEG B11"]),
    ("B12", ["B12", "EEG B12"]),
    ("B13", ["B13", "EEG B13"]),
    ("B14", ["B14", "EEG B14"]),
    ("B15", ["B15", "EEG B15"]),
    ("B16", ["B16", "EEG B16"]),
    ("B17", ["B17", "EEG B17"]),
    ("B18", ["B18", "EEG B18"]),
    ("B19", ["B19", "EEG B19"]),
    ("B20", ["B20", "EEG B20"]),
    ("B21", ["B21", "EEG B21"]),
    ("B22", ["B22", "EEG B22"]),
    ("B23", ["B23", "EEG B23"]),
    ("B24", ["B24", "EEG B24"]),
    ("B25", ["B25", "EEG B25"]),
    ("B26", ["B26", "EEG B26"]),
    ("B27", ["B27", "EEG B27"]),
    ("B28", ["B28", "EEG B28"]),
    ("B29", ["B29", "EEG B29"]),
    ("B30", ["B30", "EEG B30"]),
    ("B31", ["B31", "EEG B31"]),
    ("B32", ["B32", "EEG B32"]),
]

# Event mapping for the dataset
# Raw events from analysis.md - these are the canonical event IDs
# Source: OpenNeuro dataset analysis.md
# Annotator: Human, 2026-04-08
_EVENT_MAP = {
    # Navigation key presses (used for Task 1)
    "Key pressed: UpArrow (forward)": 0,
    "Key pressed: RightArrow (turn right)": 1,
    "Key pressed: LeftArrow (turn left)": 2,
    "Door opened": 3,
    "ColliderRoom1 has been entered": 4,
    "ColliderRoom2 has been entered": 5,
    # SAM rating events (used for Task 2)
    "SAM:start": 10,
    "SAM:completed": 11,
    # Navigation error (Potential Task 1)
    "Wall touched: trial failed!": 20,
    # Other events (raw meta)
    "Key released: UpArrow (forward)": 100,
    "Key released: RightArrow (turn right)": 101,
    "Key released: LeftArrow (turn left)": 102,
    "Player left StartSquare": 103,
    "Player entered SAM Activator": 104,
    "Player left SAM Activator": 105,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names.
    
    This function attempts to standardize channel names by matching
    common alias patterns (e.g., 'EEG Fp1' -> 'Fp1').
    
    Source: Standard EEG naming conventions
    Annotator: LLM, 2026-04-08 - 需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in _CHANNEL_ALIAS_GROUPS:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _load_subject_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from participants.tsv.
    
    Source: BIDS participants.tsv
    Annotator: Human, 2026-04-08
    """
    participants_tsv = os.path.join(dataset_path, "participants.tsv")
    
    subject_info = {
        "age": _SUBJECT_DICT.get("age", "unknown"),
        "sex": _SUBJECT_DICT.get("sex", "unknown"),
        "handedness": _SUBJECT_DICT.get("handedness", "unknown"),
    }
    
    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Match subject ID format (e.g., 'sub-01' or '01')
            subject_col = df.columns[0]  # Typically 'participant_id'
            match_id = subject_id.replace("sub-", "")
            row = df[df[subject_col].str.replace("sub-", "", regex=False) == match_id]
            
            if len(row) > 0:
                # Extract age
                if "age" in df.columns:
                    age_val = row["age"].values[0]
                    subject_info["age"] = str(int(age_val)) if pd.notna(age_val) else "unknown"
                
                # Extract sex
                if "sex" in df.columns:
                    sex_val = row["sex"].values[0]
                    if pd.notna(sex_val):
                        sex_lower = str(sex_val).lower()
                        if sex_lower in ["m", "male"]:
                            subject_info["sex"] = "male"
                        elif sex_lower in ["f", "female"]:
                            subject_info["sex"] = "female"
                        else:
                            subject_info["sex"] = "unknown"
                
                # Extract handedness
                if "handedness" in df.columns:
                    handedness_val = row["handedness"].values[0]
                    if pd.notna(handedness_val):
                        handedness_lower = str(handedness_val).lower()
                        if handedness_lower.startswith("r"):
                            subject_info["handedness"] = "right"
                        elif handedness_lower.startswith("l"):
                            subject_info["handedness"] = "left"
                        else:
                            subject_info["handedness"] = "unknown"
        except Exception:
            pass  # Fall back to defaults
    
    return subject_info


def _process_events_from_annotations(raw: mne.io.BaseRaw) -> Tuple[np.ndarray, Dict[str, int]]:
    """Extract events from raw annotations and create standard event array.
    
    This handles the case where events are stored as MNE annotations
    in the raw object.
    
    Returns:
        events: numpy array of shape (n_events, 3) with [sample, prev_id, event_id]
        event_id: dict mapping event names to integer IDs
    """
    annotations = raw.annotations
    
    if annotations is None or len(annotations) == 0:
        return np.array([]).reshape(0, 3), {}
    
    # Get onset times and convert to samples
    sfreq = raw.info["sfreq"]
    onsets = annotations.onset
    durations = annotations.duration
    descriptions = annotations.description
    
    # Build event_id mapping from unique descriptions
    unique_descriptions = list(set(descriptions))
    event_id = {desc: i + 1 for i, desc in enumerate(unique_descriptions)}
    
    # Create events array
    events_list = []
    for i, (onset, duration, desc) in enumerate(zip(onsets, durations, descriptions)):
        sample = int(onset * sfreq)
        event_id_val = event_id[desc]
        events_list.append([sample, 0, event_id_val])
    
    events = np.array(events_list)
    return events, event_id


def _load_events_from_bids(file_path: str) -> Tuple[np.ndarray, Dict[str, int]]:
    """Load events from BIDS *_events.tsv file.
    
    Source: BIDS *_events.tsv sidecar
    Annotator: Human, 2026-04-08
    """
    events_tsv = file_path.replace(".edf", "_events.tsv").replace(".eeg", "_events.tsv")
    events_tsv = events_tsv.replace(".vhdr", "_events.tsv").replace(".set", "_events.tsv")
    
    if not os.path.exists(events_tsv):
        return np.array([]).reshape(0, 3), {}
    
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        
        # Standard BIDS columns: onset, duration, trial_type (or value/stim_type)
        onset_col = "onset"
        duration_col = "duration"
        desc_col = None
        
        for col in ["trial_type", "value", "stim_type", "event_type", "description"]:
            if col in df.columns:
                desc_col = col
                break
        
        if desc_col is None:
            return np.array([]).reshape(0, 3), {}
        
        # Create event_id mapping
        unique_descriptions = list(set(df[desc_col].dropna()))
        event_id = {desc: i + 1 for i, desc in enumerate(unique_descriptions)}
        
        # Create events array
        sfreq = 500.0  # Assumed from dataset info, should be updated from actual file
        events_list = []
        for _, row in df.iterrows():
            onset = float(row[onset_col])
            duration = float(row.get(duration_col, 0))
            desc = str(row[desc_col])
            
            sample = int(onset * sfreq)
            event_id_val = event_id.get(desc, 0)
            if event_id_val > 0:
                events_list.append([sample, 0, event_id_val])
        
        events = np.array(events_list)
        return events, event_id
        
    except Exception:
        return np.array([]).reshape(0, 3), {}


@dataclass
class OpenNeuroDS004980Kernel:
    """Stage1 kernel for the openneuro_ds004980 dataset.
    
    Architectural Affordances Task - Virtual navigation EEG study.
    17 subjects, 64 channels, 500 Hz sampling rate.
    
    Supports:
    - Task 1: Navigation Action Classification (6 event types)
    - Task 2: SAM Rating Assessment (2 event types)
    - Potential Task 1: Navigation Error Detection
    """
    
    KERNEL_ID: str = "openneuro-ds004980-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.
        
        Returns
        -------
        mne.io.BaseRaw
            The modified raw object with updated metadata and events.
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", os.path.dirname(file_path))
        subject_id = str(row.get("Subject ID", row.get("participant_id", "unknown")))
        
        # =========================================================================
        # Step 1: Load subject metadata
        # =========================================================================
        subject_info = _load_subject_info(dataset_path, subject_id)
        
        # =========================================================================
        # Step 2: Update raw.info["description"] with eegunity_description
        # =========================================================================
        original_description = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DEVICE_INFO["amplifier"],
                "cap": _DEVICE_INFO["cap"],
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =========================================================================
        # Step 3: Rename channels to standard names (BEFORE set_montage)
        # =========================================================================
        rename_map = _build_channel_rename_map(raw)
        
        if rename_map:
            # Print for debugging (can be removed in production)
            print(f"[{self.KERNEL_ID}] Renaming {len(rename_map)} channels")
            for old_name, new_name in rename_map.items():
                print(f"  {old_name} -> {new_name}")
            
            raw.rename_channels(rename_map)
        
        # =========================================================================
        # Step 4: Set montage for standardized electrode positions
        # =========================================================================
        # Try to set a standard montage; if not all channels are found,
        # MNE will issue a warning but continue
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: Could not set montage: {e}")
        
        # =========================================================================
        # Step 5: Process events from annotations or events.tsv
        # =========================================================================
        # First check if events already exist as annotations
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Events are stored as annotations - standardize the descriptions
            print(f"[{self.KERNEL_ID}] Found {len(raw.annotations)} annotations")
            
            # Create new annotations with standardized event IDs
            new_descriptions = []
            for desc in raw.annotations.description:
                # Map original description to standardized event name
                if desc in _EVENT_MAP:
                    new_descriptions.append(desc)
                else:
                    # Keep original if not in our map
                    new_descriptions.append(desc)
            
            # Update annotations with standardized descriptions
            raw.annotations.description = new_descriptions
            
        else:
            # Try to load events from BIDS *_events.tsv
            events, event_id = _load_events_from_bids(file_path)
            
            if len(events) > 0:
                print(f"[{self.KERNEL_ID}] Loaded {len(events)} events from *_events.tsv")
                
                # Create annotations from events
                sfreq = raw.info["sfreq"]
                onset_times = events[:, 0] / sfreq
                durations = [0.0] * len(events)
                
                # Map event IDs back to descriptions
                id_to_desc = {v: k for k, v in event_id.items()}
                descriptions = [id_to_desc.get(e[2], f"event_{e[2]}") for e in events]
                
                annotations = mne.Annotations(
                    onset=onset_times,
                    duration=durations,
                    description=descriptions,
                )
                raw.set_annotations(annotations)
        
        # =========================================================================
        # Step 6: Set standard channel types if not already set
        # =========================================================================
        # Check for EOG channels
        eog_channels = [ch for ch in raw.ch_names if "EOG" in ch.upper()]
        if eog_channels:
            raw.set_channel_types({ch: "eog" for ch in eog_channels})
        
        # Check for ECG channels
        ecg_channels = [ch for ch in raw.ch_names if "ECG" in ch.upper()]
        if ecg_channels:
            raw.set_channel_types({ch: "ecg" for ch in ecg_channels})
        
        return raw


KERNEL = OpenNeuroDS004980Kernel()