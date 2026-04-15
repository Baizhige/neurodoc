"""Dataset-specific kernel for openneuro_ds004444.

The BMI-HDEEG dataset 1

Sensorimotor rhythm BCI: 4-class MI with high-density EEG (130 channels, 1000 Hz).

Source: https://openneuro.org/datasets/ds004444
Source: DOI 10.1038/s41597-023-02260-6 (data descriptor for BMI-HDEEG Dataset 1)

Event Mapping (confirmed by paper):
    1 -> left_hand_MI
    2 -> right_hand_MI
    3 -> feet_MI
    4 -> tongue_MI

Note: Event 3 (feet MI) has 0 events across dataset per scan.
      Kernel handles this gracefully; tasks using event 3 may fail.

Channel Info:
    130-channel high-density scalp EEG (likely BrainVision system)
    Standard naming scheme expected (extended 10-20 or 10-10 system)
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np

# Try to extend base kernel if available, otherwise standalone
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from kernels.openneuro_specific._base import OpenNeuroBaseKernel
    _HAS_BASE = True
except ImportError:
    _HAS_BASE = False

# Event mapping: raw numeric code -> semantic label
_EVENT_MAP: Dict[str, str] = {
    "1": "left_hand_MI",
    "2": "right_hand_MI",
    "3": "feet_MI",
    "4": "tongue_MI",
}

# Reverse mapping for annotations
_ANNOTATION_EVENT_MAP: Dict[str, int] = {
    "left_hand_MI": 1,
    "right_hand_MI": 2,
    "feet_MI": 3,
    "tongue_MI": 4,
}


def _detect_channel_type(ch_name: str) -> Optional[str]:
    """Detect channel type from standard naming conventions."""
    ch_upper = ch_name.upper()
    
    # EEG standard channels
    if any(prefix in ch_upper for prefix in ['FP', 'AF', 'F', 'T', 'C', 'P', 'O']):
        if 'EOG' in ch_upper:
            return 'eog'
        if 'ECG' in ch_upper:
            return 'ecg'
        if 'EMG' in ch_upper:
            return 'emg'
        if ch_upper.startswith('STIM') or ch_upper == 'TRIGGER':
            return 'stim'
        if ch_upper in ['M1', 'M2', 'A1', 'A2', 'TP9', 'TP10', 'REF']:
            return 'misc'
        return 'eeg'
    
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-10 naming."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Common naming patterns to standardize
    alias_patterns = {
        'Fp1': ['Fp1', 'EEG-Fp1'],
        'Fp2': ['Fp2', 'EEG-Fp2'],
        'Fpz': ['Fpz', 'EEG-Fpz'],
        'F7': ['F7', 'EEG-F7'],
        'F3': ['F3', 'EEG-F3'],
        'Fz': ['Fz', 'EEG-Fz'],
        'F4': ['F4', 'EEG-F4'],
        'F8': ['F8', 'EEG-F8'],
        'FC5': ['FC5', 'EEG-FC5'],
        'FC1': ['FC1', 'EEG-FC1'],
        'FCz': ['FCz', 'EEG-FCz'],
        'FC2': ['FC2', 'EEG-FC2'],
        'FC6': ['FC6', 'EEG-FC6'],
        'T7': ['T7', 'EEG-T7', 'TP7'],
        'C3': ['C3', 'EEG-C3'],
        'Cz': ['Cz', 'EEG-Cz'],
        'C4': ['C4', 'EEG-C4'],
        'T8': ['T8', 'EEG-T8', 'TP8'],
        'CP5': ['CP5', 'EEG-CP5'],
        'CP1': ['CP1', 'EEG-CP1'],
        'CPz': ['CPz', 'EEG-CPz'],
        'CP2': ['CP2', 'EEG-CP2'],
        'CP6': ['CP6', 'EEG-CP6'],
        'P7': ['P7', 'EEG-P7'],
        'P3': ['P3', 'EEG-P3'],
        'Pz': ['Pz', 'EEG-Pz'],
        'P4': ['P4', 'EEG-P4'],
        'P8': ['P8', 'EEG-P8'],
        'PO7': ['PO7', 'EEG-PO7'],
        'PO3': ['PO3', 'EEG-PO3'],
        'POz': ['POz', 'EEG-POz'],
        'PO4': ['PO4', 'EEG-PO4'],
        'O1': ['O1', 'EEG-O1'],
        'Oz': ['Oz', 'EEG-Oz'],
        'O2': ['O2', 'EEG-O2'],
        'M1': ['M1', 'A1', 'TP9', 'MastoidL'],
        'M2': ['M2', 'A2', 'TP10', 'MastoidR'],
    }
    
    for target, aliases in alias_patterns.items():
        for alias in aliases:
            if alias in existing_names and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _remap_events_to_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Convert numeric event codes to semantic annotation labels."""
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
    except Exception:
        return raw
    
    # Build mapping from original numeric IDs to semantic labels
    new_annot_map: Dict[str, str] = {}
    
    for desc, orig_id in event_id.items():
        desc_str = str(desc)
        if desc_str in _EVENT_MAP:
            new_annot_map[desc_str] = _EVENT_MAP[desc_str]
        elif desc in _EVENT_MAP:
            new_annot_map[str(desc)] = _EVENT_MAP[desc]
    
    # Create new annotations with semantic labels
    if new_annot_map:
        new_descriptions = []
        for desc in raw.annotations.description:
            desc_str = str(desc)
            new_desc = new_annot_map.get(desc_str, desc_str)
            new_descriptions.append(new_desc)
        
        new_annotations = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=new_descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annotations)
    
    return raw


class OpenNeuroDS004444Kernel:
    """Stage1 kernel for the BMI-HDEEG Dataset 1 (openneuro_ds004444)."""
    
    def apply(self, udataset, raw, row):
        if raw is None:
            return raw
        
        # Rename channels to standard 10-10 naming
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Remap numeric events to semantic labels
        raw = _remap_events_to_annotations(raw)
        
        # Set channel types
        channel_types = {}
        for ch_name in raw.ch_names:
            ch_type = _detect_channel_type(ch_name)
            if ch_type:
                channel_types[ch_name] = ch_type
        
        if channel_types:
            raw.set_channel_types(channel_types, verbose=False)
        
        # Set reference if mastoids present
        if 'M1' in raw.ch_names and 'M2' in raw.ch_names:
            raw = raw.set_eeg_reference(ref_channels=['M1', 'M2'], verbose=False)
        
        return raw


eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "BrainVision",
    "cap": "high-density 130-channel",
    "handedness": "unknown",
}

KERNEL = OpenNeuroDS004444Kernel()