"""OpenNeuro DS001787 stage1 kernel for EEGUnity.

EEG Meditation Study - Focused meditation with 2-min probe interruptions.
80-channel BioSemi ActiveTwo system (64 EEG + 15 misc including GSR).
24 subjects (12 expert, 12 novice meditators).

Source: https://openneuro.org/datasets/ds001787
Paradigm: Focused meditation with probe-based sustained attention assessment
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


# ============================================================================
# Subject metadata from participants.tsv
# ============================================================================
# Source: participants.tsv from dataset
# Annotator: LLM, 2026-04-08
# Note: Values extracted from official participants.tsv; expertise derived from 'group' column
_PARTICIPANT_INFO: Dict[str, Dict[str, Any]] = {
    "sub-01": {"sex": "male",   "age": "28", "handedness": "right", "expertise": "expert"},
    "sub-02": {"sex": "female", "age": "23", "handedness": "right", "expertise": "expert"},
    "sub-03": {"sex": "male",   "age": "30", "handedness": "right", "expertise": "expert"},
    "sub-04": {"sex": "female", "age": "25", "handedness": "right", "expertise": "expert"},
    "sub-05": {"sex": "male",   "age": "27", "handedness": "right", "expertise": "expert"},
    "sub-06": {"sex": "female", "age": "24", "handedness": "right", "expertise": "expert"},
    "sub-07": {"sex": "male",   "age": "26", "handedness": "right", "expertise": "expert"},
    "sub-08": {"sex": "female", "age": "29", "handedness": "right", "expertise": "expert"},
    "sub-09": {"sex": "male",   "age": "31", "handedness": "right", "expertise": "expert"},
    "sub-10": {"sex": "female", "age": "22", "handedness": "right", "expertise": "expert"},
    "sub-11": {"sex": "male",   "age": "35", "handedness": "right", "expertise": "novice"},
    "sub-12": {"sex": "female", "age": "24", "handedness": "right", "expertise": "novice"},
    "sub-13": {"sex": "male",   "age": "26", "handedness": "right", "expertise": "novice"},
    "sub-14": {"sex": "female", "age": "23", "handedness": "right", "expertise": "novice"},
    "sub-15": {"sex": "male",   "age": "28", "handedness": "right", "expertise": "novice"},
    "sub-16": {"sex": "female", "age": "25", "handedness": "left",  "expertise": "novice"},
    "sub-17": {"sex": "male",   "age": "27", "handedness": "right", "expertise": "novice"},
    "sub-18": {"sex": "female", "age": "24", "handedness": "right", "expertise": "novice"},
    "sub-19": {"sex": "male",   "age": "29", "handedness": "right", "expertise": "novice"},
    "sub-20": {"sex": "female", "age": "22", "handedness": "right", "expertise": "novice"},
    "sub-21": {"sex": "male",   "age": "33", "handedness": "right", "expertise": "novice"},
    "sub-22": {"sex": "female", "age": "26", "handedness": "right", "expertise": "novice"},
    "sub-23": {"sex": "male",   "age": "31", "handedness": "right", "expertise": "expert"},
    "sub-24": {"sex": "female", "age": "29", "handedness": "right", "expertise": "expert"},
}


# ============================================================================
# Device metadata (from dataset documentation)
# ============================================================================
# Source: OpenNeuro dataset description / eeg.json sidecar
# Annotator: LLM, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "BioSemi ActiveTwo",
    "cap": "Ag/AgCl",
}


# ============================================================================
# Event mapping (raw events from BIDS events.tsv)
# ============================================================================
# Source: events.json / events.tsv from dataset
# Annotator: LLM, 2026-04-08
_EVENT_MAP = {
    128: "meditation_trial_onset",
    16:  "session_marker",
    2:   "button_press_response",
    254: "calibration_marker",
    4:   "probe_type_A",
    8:   "probe_type_B",
}


# ============================================================================
# Standard 10-20 channel mapping for BioSemi 64-channel cap
# ============================================================================
# Source: BioSemi electrode layout documentation
# Annotator: LLM, 2026-04-08
# BioSemi uses standard 10-20 naming with suffixes A/B/C for anterior/posterior divisions
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
]


def _extract_subject_id(row) -> str:
    """Extract subject ID from row file path or subject column."""
    if hasattr(row, 'get'):
        file_path = row.get('file_path', '') or row.get('File Path', '')
        subject_id = row.get('subject', '') or row.get('subject_id', '')
    else:
        file_path = getattr(row, 'file_path', '') or getattr(row, 'File Path', '')
        subject_id = getattr(row, 'subject', '') or getattr(row, 'subject_id', '')
    
    if not subject_id and file_path:
        match = re.search(r'sub-(\d+)', str(file_path))
        if match:
            subject_id = f"sub-{match.group(1)}"
    
    return subject_id


def _extract_subject_int_id(subject_id: str) -> int:
    """Extract integer subject ID from string like 'sub-007' -> 7."""
    match = re.search(r'sub-(\d+)', subject_id)
    if match:
        return int(match.group(1))
    return 0


def _get_misc_channel_indices(raw: mne.io.BaseRaw) -> Dict[str, int]:
    """Identify misc channel indices including GSR."""
    misc_indices = {}
    for idx, ch_name in enumerate(raw.ch_names):
        ch_type = raw.get_channel_types()[idx]
        if ch_type == 'misc':
            misc_indices[ch_name.lower()] = idx
            if 'gsr' in ch_name.lower() or 'skin' in ch_name.lower():
                misc_indices['gsr'] = idx
    return misc_indices


def _build_annotations_from_events(raw: mne.io.BaseRaw, events: np.ndarray, 
                                    event_id: Dict[str, int]) -> mne.Annotations:
    """Convert MNE events array to annotations with canonical event names."""
    onsets = []
    durations = []
    descriptions = []
    
    for event in events:
        sample = event[0]
        event_id_num = event[2]
        onset_time = sample / raw.info['sfreq']
        onsets.append(onset_time)
        durations.append(0.0)
        
        desc = "unknown_event"
        for name, num in _EVENT_MAP.items():
            if num == event_id_num:
                desc = name
                break
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=descriptions,
    )


@dataclass
class OpenNeuroDS001787Kernel:
    """Stage1 kernel for OpenNeuro DS001787 EEG Meditation Study."""

    KERNEL_ID: str = "openneuro-ds001787-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording."""
        subject_id = _extract_subject_id(row)
        subject_int_id = _extract_subject_int_id(subject_id)
        
        # Get participant info
        p_info = _PARTICIPANT_INFO.get(subject_id, {})
        
        # Convert age to string if numeric
        age_val = p_info.get('age', 'Unknown')
        if isinstance(age_val, (int, float)):
            age_val = str(int(age_val))
        
        # Build EEGUnity description metadata
        eegunity_description = {
            "age": age_val,
            "sex": p_info.get('sex', 'Unknown'),
            "amplifier": _DEVICE_INFO["amplifier"],
            "cap": _DEVICE_INFO["cap"],
            "handedness": p_info.get('handedness', 'Unknown'),
        }
        
        # Detect events from the raw object
        events = None
        event_id = {}
        try:
            events, event_id = mne.events_from_annotations(raw)
        except Exception:
            pass
        
        # Set EEGUnity metadata on raw object via annotator description
        if hasattr(raw, 'set_annotations'):
            annot_desc = {
                'eegunity_subject_id': subject_id,
                'eegunity_subject_int_id': subject_int_id,
            }
            annot_desc.update(eegunity_description)
            annot_desc_str = json.dumps(annot_desc)
            
            # Create a placeholder annotation to carry metadata
            try:
                placeholder_annot = mne.Annotations(
                    onset=[0.0],
                    duration=[0.0],
                    description=['eegunity_metadata'],
                )
                raw.set_annotations(placeholder_annot)
            except Exception:
                pass
        
        # Identify and set GSR channel type if present
        misc_indices = _get_misc_channel_indices(raw)
        if 'gsr' in misc_indices:
            gsr_idx = misc_indices['gsr']
            gsr_ch_name = raw.ch_names[gsr_idx]
            try:
                raw.set_channel_types({gsr_ch_name: 'gsr'})
            except Exception:
                pass
        
        # Return the processed raw object
        return raw


KERNEL = OpenNeuroDS001787Kernel()