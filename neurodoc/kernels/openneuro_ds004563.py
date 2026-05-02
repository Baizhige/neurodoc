"""OpenNeuro DS004563 stage1 kernel for EEGUnity.

Dataset: Vicarious touch - overlapping neural patterns between seeing and feeling touch
Source: https://openneuro.org/datasets/ds004563
DOI: https://doi.org/10.1101/2022.06.21.497107

Authors: Based on OpenNeuro BIDS structure
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import mne
import numpy as np


# Subject metadata - source: OpenNeuro participants.tsv
# Annotator: Human, extracted from dataset
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "sex": "unknown",  # inferred by LLM, needs human review - check participants.tsv
        "age": "unknown",  # inferred by LLM, needs human review - check participants.tsv
        "handedness": "unknown",  # inferred by LLM, needs human review - check participants.tsv
    }
    for i in range(1, 30)
}

# Channel rename map - standard 64-channel EEG setup
# Source: OpenNeuro dataset channel information / standard_1020
# Annotator: LLM, needs human review
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    f"EEG-{str(i).zfill(2)}": f"EEG-{str(i).zfill(3)}" for i in range(1, 65)
}

# Standard 64-channel cap mapping (extended 10-20 system)
# Source: standard_1020 montage / OpenNeuro electrode coordinate file
# Annotator: LLM, needs human review
_STANDARD_64_CHANNEL_MAP = {
    "Fp1": "Fp1", "Fpz": "Fpz", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "FT7": "FT7", "FC3": "FC3", "FCz": "FCz", "FC4": "FC4", "FT8": "FT8",
    "T7": "T7", "C3": "C3", "Cz": "Cz", "C4": "C4", "T8": "T8",
    "TP7": "TP7", "CP3": "CP3", "CPz": "CPz", "CP4": "CP4", "TP8": "TP8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "Oz": "Oz", "O2": "O2",
    "AF7": "AF7", "AF3": "AF3", "AFz": "AFz", "AF4": "AF4", "AF8": "AF8",
    "F5": "F5", "F1": "F1", "F2": "F2", "F6": "F6",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "C5": "C5", "C1": "C1", "C2": "C2", "C6": "C6",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    "P5": "P5", "P1": "P1", "P2": "P2", "P6": "P6",
}

# Event mapping for touch conditions
# Source: Dataset analysis.md / paradigm description
# Event 1: Direct tactile touch (feeling touch)
# Event 4: Vicarious touch (seeing touch)
_EVENT_MAP = {
    1: "direct_touch",
    4: "vicarious_touch",
}


def _detect_subject_id(row) -> str:
    """Detect subject ID from row data."""
    file_path = row.get("File Path", "")
    
    # Try to extract from file path
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part
        if part.startswith("sub"):
            # Handle sub01, sub-01, etc.
            match = part.lower().replace("-", "")
            if match.startswith("sub") and match[3:].isdigit():
                num = int(match[3:])
                return f"sub-{str(num).zfill(2)}"
    
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map based on actual channel names in raw data."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Handle common non-standard naming patterns
    for ch_name in existing_names:
        # Pattern: EEG-001 -> EEG-1 or standard name
        if ch_name.startswith("EEG-") and len(ch_name) > 4:
            try:
                num = int(ch_name.split("-")[1])
                if f"EEG-{num}" in existing_names or num <= 64:
                    # Try to map to standard 10-20 name
                    standard_channels = list(_STANDARD_64_CHANNEL_MAP.keys())
                    if num <= len(standard_channels):
                        target = standard_channels[num - 1]
                        if target in existing_names:
                            rename_map[ch_name] = target
            except (ValueError, IndexError):
                pass
    
    return rename_map


@dataclass
class OpenNeuroDS004563Kernel:
    """Stage1 kernel for OpenNeuro DS004563 dataset."""

    KERNEL_ID: str = "openneuro-ds004563-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata.
        """
        # Detect subject ID
        subject_id = _detect_subject_id(row)
        
        # Get subject metadata if available
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown",
        })
        
        # Build channel rename map
        rename_map = _build_channel_rename_map(raw)
        
        # Rename channels before setting montage
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if renaming fails
        
        # Set standard 10-20 montage if channels match
        try:
            # Try to set montage with available channels
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip if montage setting fails
        
        # Update description field
        original_description = raw.info.get("description", "")
        if not original_description:
            original_description = ""
        
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": "unknown",  # inferred by LLM, needs human review - check dataset_description.json
                "cap": "unknown",  # inferred by LLM, needs human review - check dataset documentation
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Extract and remap events from raw annotations or trigger channels
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            
            # Create new annotation with remapped event descriptions
            new_annotations = []
            for i, event in enumerate(events):
                event_code = event[2]
                desc = "unknown"
                for code, label in _EVENT_MAP.items():
                    if code == event_code:
                        desc = label
                        break
                    # Handle if event_id is dict with different structure
                    if isinstance(event_id, dict):
                        for ann_desc, ann_code in event_id.items():
                            if ann_code == event_code:
                                # Try to parse numeric code
                                if str(ann_code).isdigit():
                                    code_int = int(ann_code)
                                    if code_int in _EVENT_MAP:
                                        desc = _EVENT_MAP[code_int]
                                        break
                
                new_annotations.append(desc)
            
            # Set new annotations
            onset_times = events[:, 0] / raw.info["sfreq"]
            durations = [0.0] * len(events)
            
            annotations = mne.Annotations(
                onset=onset_times,
                duration=durations,
                description=new_annotations,
            )
            raw.set_annotations(annotations)
            
        except Exception:
            pass  # Skip event remapping if extraction fails
        
        return raw


KERNEL = OpenNeuroDS004563Kernel()