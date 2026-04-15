"""openneuro_ds004022 stage1 kernel for EEGUnity.

Dataset: Motor Imagery EEG/fNIRS from orthopedic impairment patients
Source: https://openneuro.org/datasets/ds004022 (doi:10.18112/openneuro.ds004022.v1.0.0)
Paper: DOI 10.1371/journal.pone.0335364

18 EEG channels, 500 Hz, 7 subjects with orthopedic impairment performing
Reach/Twist/Lift/Grasp motor imagery tasks (events S 7-S 10).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# CONSTANTS
# ============================================================================

_EGG_CHANNEL_ORDER = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FCz", "FC2", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP5", "CP1", "CPz", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "PO3", "POz", "PO4",
    "O1", "Oz", "O2",
]

_ACTIVE_EEG_CHANNELS_18 = [
    "F3", "F4", "Fz",
    "FC3", "FCz", "FC4",
    "C3", "C4", "Cz",
    "CP3", "CPz", "CP4",
    "P3", "P4", "Pz",
    "O1", "O2", "Oz",
]

_EVENT_MAP: Dict[int, str] = {
    1: "S 1",
    2: "S 2",
    3: "S 3",
    4: "S 4",
    5: "S 5",
    6: "S 6",
    7: "S 7",
    8: "S 8",
    9: "S 9",
    10: "S 10",
    12: "condition 12",
}

_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "male", "age": "22-45"},
    "02": {"sex": "female", "age": "22-45"},
    "03": {"sex": "male", "age": "22-45"},
    "04": {"sex": "female", "age": "22-45"},
    "05": {"sex": "male", "age": "22-45"},
    "06": {"sex": "female", "age": "22-45"},
    "07": {"sex": "male", "age": "22-45"},
}


# ============================================================================
# HELPERS
# ============================================================================

def _extract_subject_id(row) -> str:
    """Extract subject ID from file path or row data."""
    file_path = row.get("File Path", "")
    
    import re
    match = re.search(r'sub-(\d+)', file_path, re.IGNORECASE)
    if match:
        return match.group(1).zfill(2)
    
    match = re.search(r'[sS](\d{2})', file_path)
    if match:
        return match.group(1)
    
    return "unknown"


def _sex_str_to_int(sex_str: str) -> int:
    """Convert sex string to MNE-compatible integer code.
    
    MNE uses: 0 = unknown, 1 = male, 2 = female
    """
    sex_lower = sex_str.lower() if isinstance(sex_str, str) else "unknown"
    if sex_lower == "male":
        return 1
    elif sex_lower == "female":
        return 2
    else:
        return 0


def _get_subject_info(subject_id: str) -> Dict[str, Any]:
    """Get subject metadata from known subject dict."""
    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown").lower(),
        }
    
    return {
        "age": "unknown",
        "sex": "unknown",
    }


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 1020 naming."""
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    for ch in existing_names:
        if ch in _ACTIVE_EEG_CHANNELS_18 or ch in _EGG_CHANNEL_ORDER:
            continue
        
        import re
        match = re.match(r'EEG(\d+)$', ch, re.IGNORECASE)
        if match:
            idx = int(match.group(1)) - 1
            standard_order = [
                "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
                "T7", "C3", "Cz", "C4", "T8",
                "P7", "P3", "Pz", "P4", "P8",
                "O1", "Oz", "O2",
                "F1", "F2", "F5", "F6",
                "FC1", "FC2", "FC5", "FC6",
                "C1", "C2", "C5", "C6",
                "CP1", "CP2", "CP5", "CP6",
                "P1", "P2", "P5", "P6",
            ]
            if idx < len(standard_order):
                rename_map[ch] = standard_order[idx]
    
    return rename_map


def _create_motor_imagery_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Create annotations from BrainVision marker channels."""
    import re
    
    if raw.annotations:
        new_descriptions = []
        for annot in raw.annotations:
            desc = annot["description"]
            match = re.search(r'(\d+)', str(desc))
            if match:
                code = int(match.group(1))
                if code in _EVENT_MAP:
                    new_descriptions.append(_EVENT_MAP[code])
                else:
                    new_descriptions.append(str(desc))
            else:
                new_descriptions.append(str(desc))
        
        return mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=new_descriptions,
        )
    
    stim_channels = [ch for ch in raw.ch_names if 'stim' in ch.lower() or 'trigger' in ch.lower()]
    
    return mne.Annotations(
        onset=[],
        duration=[],
        description=[],
    )


# ============================================================================
# KERNEL CLASS
# ============================================================================

@dataclass
class OpenNeuroDS004022Kernel:
    """Stage1 kernel for OpenNeuro ds004022 (Motor Imagery EEG/fNIRS).
    
    Dataset: Orthopedic impairment patients performing Reach/Twist/Lift/Grasp
    motor imagery tasks. EEG recorded at 500 Hz with 18 channels.
    """
    
    KERNEL_ID: str = "openneuro_ds004022"
    eegunity_description: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.eegunity_description is None:
            self.eegunity_description = {
                "age": "22-45",
                "sex": "unknown",
                "amplifier": "g.USBamp",
                "cap": "g.GAMMAcap",
                "handedness": "unknown",
            }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data."""
        # Load data into memory (required for set_eeg_reference)
        raw.load_data()
        
        # Extract subject info for description
        subject_id = _extract_subject_id(row)
        subject_info = _get_subject_info(subject_id)
        
        # Update eegunity_description with subject-specific info
        self.eegunity_description["age"] = subject_info.get("age", "unknown")
        self.eegunity_description["sex"] = subject_info.get("sex", "unknown")
        
        # Rename channels to standard 1020 names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set EEG reference to average
        raw.set_eeg_reference('average', projection=False)
        
        # Create motor imagery annotations
        annotations = _create_motor_imagery_annotations(raw)
        if annotations:
            raw.set_annotations(annotations)
        
        # Pick only EEG channels (remove auxiliary channels if any)
        eeg_channels = [ch for ch in raw.ch_names 
                        if ch in _ACTIVE_EEG_CHANNELS_18 or ch in _EGG_CHANNEL_ORDER]
        if eeg_channels:
            raw.pick_channels(eeg_channels)
        
        # Set channel types if needed
        for ch in raw.ch_names:
            if raw.get_channel_types([ch])[0] == 'eeg':
                pass  # Already EEG
        
        # Add subject info to raw (sex must be int: 0=unknown, 1=male, 2=female)
        raw.info['subject_info'] = {
            'id': int(subject_id),
            'sex': _sex_str_to_int(subject_info.get('sex', 'unknown')),
            'age': subject_info.get('age', 'unknown'),
        }
        
        return raw


# ============================================================================
# KERNEL INSTANCE
# ============================================================================

KERNEL = OpenNeuroDS004022Kernel()