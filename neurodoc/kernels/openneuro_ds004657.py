"""OpenNeuro ds004657 stage1 kernel for EEGUnity.

Driving with Autonomous Aids dataset - semi-automated driving task with lane 
maintenance and collision avoidance. Contains 74-channel EEG recordings at 
1024 Hz with 7-digit trigger codes encoding driving conditions.

Source: https://openneuro.org/datasets/ds004657
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


# Source: Dataset documentation and paper references
# inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# No participant metadata available in dataset; all fields set to unknown

# 74-channel standard 10-20 system mapping
# Source: standard_1020 montage with extended 10-10 positions
# inferred by LLM, needs human review
_STANDARD_1024_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    # Extended channels for 74 total
    "PO9", "PO10",
    "Fpz", "AFp1", "AFp2",
    "Affp1", "Affp2",
    "FTT", "TTP",
    "CCP", "CCI",
    "CPP", "CPI",
    "O9", "O10",
    "I1", "I2",
]

# Source: Dataset analysis.md - Event Structure table
_EVENT_CODE_MAP = {
    "2310001": "Driving 231 V1",
    "2310002": "Driving 231 V2",
    "4111101": "Driving 411 V1",
    "1410001": "Driving 141 V1",
    "1410002": "Driving 141 V2",
    "1320001": "Driving 132 V1",
    "1320002": "Driving 132 V2",
    "1420001": "Driving 142 V1",
    "1420002": "Driving 142 V2",
    "2541001": "Driving 254 V1",
    "2561001": "Driving 256 V1",
    "2781021": "Driving 278 V021",
    "2781022": "Driving 278 V022",
    "2320001": "Driving 232 V1",
    "2320002": "Driving 232 V2",
}

# Simple road codes (low mental workload, y=0)
_SIMPLE_ROAD_CODES = {"2310001", "2310002", "4111101"}

# Complex road codes (high mental workload, y=1)
_COMPLEX_ROAD_CODES = {
    "1320001", "1320002",
    "1410001", "1410002",
    "1420001", "1420002",
    "2541001", "2561001",
    "2781021", "2781022",
}

# Multiclass label mapping for 15 driving conditions
_MULTICLASS_LABEL_MAP = {
    "2310001": 0,
    "2310002": 1,
    "4111101": 2,
    "1410001": 3,
    "1410002": 4,
    "1320001": 5,
    "1320002": 6,
    "1420001": 7,
    "1420002": 8,
    "2541001": 9,
    "2561001": 10,
    "2781021": 11,
    "2781022": 12,
    "2320001": 13,
    "2320002": 14,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names to standard 10-20 names.
    
    Source: Dataset documentation, standard electrode naming conventions
    inferred by LLM, needs human review
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Common patterns in EEG datasets
    alias_groups = [
        ("Fp1", ["EEG001", "Fp1", "fp1", "EEG Fp1"]),
        ("Fp2", ["EEG002", "Fp2", "fp2", "EEG Fp2"]),
        ("Fpz", ["EEG003", "Fpz", "fpz", "EEG Fpz"]),
        ("AF7", ["EEG004", "AF7"]),
        ("AF3", ["EEG005", "AF3"]),
        ("AFz", ["EEG006", "AFz"]),
        ("AF4", ["EEG007", "AF4"]),
        ("AF8", ["EEG008", "AF8"]),
        ("F7", ["EEG009", "F7"]),
        ("F5", ["EEG010", "F5"]),
        ("F3", ["EEG011", "F3"]),
        ("F1", ["EEG012", "F1"]),
        ("Fz", ["EEG013", "Fz"]),
        ("F2", ["EEG014", "F2"]),
        ("F4", ["EEG015", "F4"]),
        ("F6", ["EEG016", "F6"]),
        ("F8", ["EEG017", "F8"]),
        ("FT7", ["EEG018", "FT7"]),
        ("FC5", ["EEG019", "FC5"]),
        ("FC3", ["EEG020", "FC3"]),
        ("FC1", ["EEG021", "FC1"]),
        ("FCz", ["EEG022", "FCz"]),
        ("FC2", ["EEG023", "FC2"]),
        ("FC4", ["EEG024", "FC4"]),
        ("FC6", ["EEG025", "FC6"]),
        ("FT8", ["EEG026", "FT8"]),
        ("T7", ["EEG027", "T7", "T7_2"]),
        ("C5", ["EEG028", "C5"]),
        ("C3", ["EEG029", "C3"]),
        ("C1", ["EEG030", "C1"]),
        ("Cz", ["EEG031", "Cz"]),
        ("C2", ["EEG032", "C2"]),
        ("C4", ["EEG033", "C4"]),
        ("C6", ["EEG034", "C6"]),
        ("T8", ["EEG035", "T8"]),
        ("TP7", ["EEG036", "TP7"]),
        ("CP5", ["EEG037", "CP5"]),
        ("CP3", ["EEG038", "CP3"]),
        ("CP1", ["EEG039", "CP1"]),
        ("CPz", ["EEG040", "CPz"]),
        ("CP2", ["EEG041", "CP2"]),
        ("CP4", ["EEG042", "CP4"]),
        ("CP6", ["EEG043", "CP6"]),
        ("TP8", ["EEG044", "TP8"]),
        ("P7", ["EEG045", "P7"]),
        ("P5", ["EEG046", "P5"]),
        ("P3", ["EEG047", "P3"]),
        ("P1", ["EEG048", "P1"]),
        ("Pz", ["EEG049", "Pz"]),
        ("P2", ["EEG050", "P2"]),
        ("P4", ["EEG051", "P4"]),
        ("P6", ["EEG052", "P6"]),
        ("P8", ["EEG053", "P8"]),
        ("PO7", ["EEG054", "PO7"]),
        ("PO3", ["EEG055", "PO3"]),
        ("POz", ["EEG056", "POz"]),
        ("PO4", ["EEG057", "PO4"]),
        ("PO8", ["EEG058", "PO8"]),
        ("O1", ["EEG059", "O1"]),
        ("Oz", ["EEG060", "Oz"]),
        ("O2", ["EEG061", "O2"]),
        ("PO9", ["EEG062", "PO9"]),
        ("PO10", ["EEG063", "PO10"]),
        ("FTT", ["EEG064", "FTT"]),
        ("CCP", ["EEG065", "CCP"]),
        ("CPP", ["EEG066", "CPP"]),
        ("O9", ["EEG067", "O9"]),
        ("O10", ["EEG068", "O10"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    # Handle numbered EEG channels
    for i in range(1, 75):
        eeg_pattern = f"EEG{i:03d}"
        if eeg_pattern in existing_names:
            idx = i - 1
            if idx < len(_STANDARD_1024_CHANNELS):
                standard_name = _STANDARD_1024_CHANNELS[idx]
                if eeg_pattern != standard_name:
                    rename_map[eeg_pattern] = standard_name
    
    return rename_map


def _parse_event_code(value: Any) -> Optional[str]:
    """Parse event code from various formats."""
    if value is None:
        return None
    
    # Convert to string and extract numeric part
    value_str = str(value).strip()
    
    # Try to find 7-digit code
    match = re.search(r'(\d{7})', value_str)
    if match:
        return match.group(1)
    
    # Try simple integer/float
    try:
        int_val = int(float(value_str))
        if 1000000 <= int_val <= 9999999:
            return str(int_val)
    except (ValueError, TypeError):
        pass
    
    return value_str


@dataclass
class OpenNeuroDS004657Kernel:
    """Stage1 kernel for OpenNeuro ds004657 (Driving with Autonomous Aids)."""

    KERNEL_ID: str = "openneuro-ds004657-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")

        # Update description with metadata
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names before setting montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if rename fails

        # Set standard montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip if montage fails

        # Extract events from annotations or STIM channel
        events, event_id = mne.events_from_annotations(raw)
        
        # Build new annotations from event codes
        new_onsets = []
        new_durations = []
        new_descriptions = []
        
        for event in events:
            # Get original description
            orig_desc = None
            for desc, eid in event_id.items():
                if eid == event[2]:
                    orig_desc = desc
                    break
            
            if orig_desc is not None:
                # Parse event code
                event_code = _parse_event_code(orig_desc)
                
                if event_code in _EVENT_CODE_MAP:
                    new_descriptions.append(_EVENT_CODE_MAP[event_code])
                elif orig_desc in _EVENT_CODE_MAP:
                    new_descriptions.append(_EVENT_CODE_MAP[orig_desc])
                else:
                    # Try to parse as numeric code
                    parsed = _parse_event_code(orig_desc)
                    if parsed:
                        new_descriptions.append(f"Driving {parsed}")
                    else:
                        new_descriptions.append(str(orig_desc))
                
                # Convert sample to seconds
                new_onsets.append(event[0] / raw.info["sfreq"])
                new_durations.append(0.0)
        
        if new_onsets:
            annotations = mne.Annotations(
                onset=new_onsets,
                duration=new_durations,
                description=new_descriptions,
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004657Kernel()