"""OpenNeuro DS004262 (Continuous Feedback Processing) stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# LLM 推断，需人类复核
# Source: Dataset description / paper 10.1111/psyp.14399
# All metadata fields are missing from participants.tsv and dataset documentation.
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-02": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-03": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-04": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-05": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-06": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-07": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-08": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-09": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-10": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-11": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-12": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-13": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-14": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-15": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-16": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-17": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-18": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-19": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-20": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-21": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}

# Standard 10-20 system channel names expected for this 31-channel dataset
# LLM 推断，需人类复核
# Source: Paper references indicate standard EEG cap with 31 channels
_STANDARD_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FCz", "FC2", "FC6",
    "M1", "T7", "C3", "Cz", "C4", "T8", "M2",
    "CP5", "CP1", "CPz", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
]

# Event mapping for raw meta
_EVENT_MAP: Dict[str, str] = {
    "Stimulus": "Stimulus",
    "New Segment": "New Segment",
    "Comment": "Comment",
}


def _get_subject_id(row) -> str:
    """Extract subject ID from row."""
    file_path = str(row.get("File Path", ""))
    for prefix in ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05",
                   "sub-06", "sub-07", "sub-08", "sub-09", "sub-10",
                   "sub-11", "sub-12", "sub-13", "sub-14", "sub-15",
                   "sub-16", "sub-17", "sub-18", "sub-19", "sub-20",
                   "sub-21"]:
        if prefix in file_path:
            return prefix
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names.
    
    LLM 推断，需人类复核
    Source: Standard 10-20 system naming convention
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Handle common non-standard naming patterns
    for i, ch in enumerate(existing_names):
        # Pattern: EEG-1, EEG-2, etc.
        if ch.startswith("EEG-") and ch[4:].isdigit():
            idx = int(ch[4:])
            if idx < len(_STANDARD_CHANNEL_NAMES):
                rename_map[ch] = _STANDARD_CHANNEL_NAMES[idx]
        # Pattern: E1, E2, etc.
        elif ch.startswith("E") and ch[1:].isdigit():
            idx = int(ch[1:])
            if idx < len(_STANDARD_CHANNEL_NAMES):
                rename_map[ch] = _STANDARD_CHANNEL_NAMES[idx]
        # Pattern: CH1, CH2, etc.
        elif ch.startswith("CH") and ch[2:].isdigit():
            idx = int(ch[2:]) - 1
            if idx < len(_STANDARD_CHANNEL_NAMES):
                rename_map[ch] = _STANDARD_CHANNEL_NAMES[idx]
    
    return rename_map


def _remap_stimulus_events(annotations: mne.Annotations) -> mne.Annotations:
    """Remap stimulus events with subtype information.
    
    LLM 推断，需人类复核
    Source: analysis.md - Stimulus subtypes S1-S56 for classification task
    """
    new_descriptions = []
    for desc in annotations.description:
        if desc.startswith("Stimulus/S"):
            new_descriptions.append(desc.strip())
        elif desc == "Stimulus" or desc.startswith("Stimulus/S  "):
            new_descriptions.append(desc.strip())
        else:
            new_descriptions.append(desc)
    
    return mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )


@dataclass
class OpenNeuroDS004262Kernel:
    """Stage1 kernel for the OpenNeuro DS004262 dataset.
    
    Dataset: Continuous Feedback Processing
    Source: https://openneuro.org/datasets/ds004262
    Year: 2022
    Subjects: 21
    Channels: 31 (EEG) + reference channels
    Sampling Rate: 1000 Hz
    
    Paradigm: Participants predicted the final height of an animated rising bar
    based on cues with varying predictability to study continuous feedback
    processing and prediction error.
    
    References:
    - 10.1101/2022.10.06.511117 (Preprint)
    - 10.1111/psyp.14399 (Psychophysiology 2023)
    """
    
    KERNEL_ID: str = "openneuro-ds004262-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
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
        # Extract subject ID for metadata lookup
        subject_id = _get_subject_id(row)
        subject_info = _SUBJECT_DICT.get(subject_id, {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown",
        })
        
        # Get original description
        original_description = raw.info.get("description", "")
        
        # Build eegunity_description with required fields
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": "unknown",  # LLM 推断，需人类复核 - not specified in dataset
                "cap": "unknown",  # LLM 推断，需人类复核 - not specified in dataset
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename non-standard channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard montage if all channels are recognized
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            available_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if len(available_channels) >= 20:  # Most channels recognized
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is optional
        
        # Process existing annotations
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Remap stimulus events with subtype information
            raw.set_annotations(_remap_stimulus_events(raw.annotations))
        
        return raw


KERNEL = OpenNeuroDS004262Kernel()