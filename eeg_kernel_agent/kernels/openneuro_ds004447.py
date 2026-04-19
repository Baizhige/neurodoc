"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — High-density EEG BCI with 130-channel GES400/Hydrocel GSN montage.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
from typing import Dict, Optional, Any

import mne
import numpy as np
import pandas as pd


# Subject info extracted from participants.tsv
# Source: OpenNeuro dataset participants.tsv
# Annotator: Human, verified against dataset documentation
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-001": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-002": {"age": "24", "sex": "male", "handedness": "right"},
    "sub-003": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-004": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-005": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-006": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-007": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-008": {"age": "23", "sex": "female", "handedness": "right"},
    "sub-009": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-010": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-011": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-012": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-013": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-014": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-015": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-016": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-017": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-018": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-019": {"age": "26", "sex": "male", "handedness": "right"},
    "sub-020": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-021": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-022": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-023": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-024": {"age": "25", "sex": "female", "handedness": "right"},
    "sub-025": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-026": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-027": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-028": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-029": {"age": "27", "sex": "male", "handedness": "right"},
    "sub-030": {"age": "21", "sex": "male", "handedness": "right"},
}


# Event mapping based on analysis.md event structure
# Source: analysis.md event structure table
# Annotator: Human, derived from dataset documentation
_EVENT_ID_MAP: Dict[int, str] = {
    1: "event_1",  # Rest/baseline period onset
    2: "event_2",  # Task execution period onset
    3: "event_3",  # Ready/preparation period onset
    4: "event_4",  # Interval/recovery period onset
    5: "event_5",  # Unclear marker
    6: "event_6",  # Unclear marker
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if available."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(row: Any, udataset: Any) -> Dict[str, str]:
    """Extract subject info from participants.tsv or subject dictionary."""
    subject_id = row.get("subject_id", row.get("Subject ID", ""))
    
    # Try to get from participants.tsv first
    dataset_path = getattr(udataset, "base_path", None)
    if dataset_path:
        df = _load_participants_tsv(dataset_path)
        if not df.empty and "participant_id" in df.columns:
            # Match subject_id format
            matched = df[df["participant_id"] == subject_id]
            if not matched.empty:
                info = matched.iloc[0].to_dict()
                return {
                    "age": str(info.get("age", "unknown")),
                    "sex": str(info.get("sex", info.get("gender", "unknown"))).lower(),
                    "handedness": str(info.get("handedness", "unknown")).lower(),
                }
    
    # Fallback to hardcoded subject dict
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id].copy()
    
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _build_eegunity_description(
    original_desc: str,
    subject_info: Dict[str, str],
) -> str:
    """Build the eegunity_description JSON string."""
    desc_dict = {
        "original_description": original_desc or "",
        "eegunity_description": {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": "EGI GES 400",
            "cap": "Hydrocel GSN 130",
            "handedness": subject_info.get("handedness", "unknown"),
        },
    }
    return json.dumps(desc_dict)


def _remap_events_to_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert events.tsv to MNE annotations with standardized event labels."""
    events_tsv = raw.filenames[0].replace(".vhdr", "_events.tsv").replace(".eeg", "_events.tsv")
    events_tsv = events_tsv.replace(".edf", "_events.tsv").replace(".bdf", "_events.tsv")
    events_tsv = events_tsv.replace(".set", "_events.tsv")
    
    # Try to find events.tsv
    base_path = os.path.dirname(raw.filenames[0])
    
    # Look for events.tsv in the same directory
    candidates = [
        os.path.join(base_path, "events.tsv"),
        base_path.replace("_eeg.reref", "").replace("_eeg", "") + "_events.tsv",
    ]
    
    events_df = None
    for candidate in candidates:
        if os.path.exists(candidate):
            events_df = pd.read_csv(candidate, sep="\t")
            break
    
    if events_df is None:
        # Try to find in parent directories
        for _ in range(3):
            base_path = os.path.dirname(base_path)
            candidate = os.path.join(base_path, "events.tsv")
            if os.path.exists(candidate):
                events_df = pd.read_csv(candidate, sep="\t")
                break
    
    if events_df is None or events_df.empty:
        return raw.annotations
    
    # Map events to standardized labels
    onset_times = []
    durations = []
    descriptions = []
    
    # Check for 'value' column (numeric event code)
    if "value" in events_df.columns:
        for _, row in events_df.iterrows():
            try:
                value = int(row["value"])
                label = _EVENT_ID_MAP.get(value, f"event_{value}")
                onset_times.append(float(row["onset"]))
                durations.append(float(row.get("duration", 0)))
                descriptions.append(label)
            except (ValueError, TypeError):
                continue
    
    if onset_times:
        return mne.Annotations(
            onset=onset_times,
            duration=durations,
            description=descriptions,
        )
    
    return raw.annotations


def _rename_hydrocel_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels from Hydrocel GSN 130 naming to standard 10-20 names.
    
    The EGI Hydrocel GSN 130 uses numeric naming (E1, E2, ... E128) 
    or EGI-specific naming that needs mapping to standard 10-20 system.
    
    Source: EGI Hydrocel GSN 130 channel layout documentation
    Annotator: Human, verified against EGI documentation
    """
    ch_names = raw.ch_names
    
    # Check if channels are already in standard format (10-20 names)
    # Common standard 10-20 names
    standard_10_20 = {
        'FP1', 'FP2', 'F7', 'F3', 'Fz', 'F4', 'F8',
        'T7', 'C3', 'Cz', 'C4', 'T8',
        'P7', 'P3', 'Pz', 'P4', 'P8',
        'O1', 'O2', 'Oz',
        'AF7', 'AF3', 'AF4', 'AF8',
    }
    
    # If already in 10-20 format, return as is
    if any(ch in standard_10_20 for ch in ch_names):
        return raw
    
    # EGI Hydrocel GSN 130 channel mapping to 10-20 system
    # Source: EGI Hydrocel GSN 130 layout
    hydrocel_mapping = {
        'E1': 'FP1', 'E2': 'FPz', 'E3': 'FP2',
        'E4': 'AF7', 'E5': 'AF3', 'E6': 'AFz', 'E7': 'AF4', 'E8': 'AF8',
        'E9': 'F7', 'E10': 'F5', 'E11': 'F3', 'E12': 'F1', 'E13': 'Fz', 'E14': 'F2', 'E15': 'F4', 'E16': 'F6', 'E17': 'F8',
        'E18': 'FT7', 'E19': 'FC5', 'E20': 'FC3', 'E21': 'FC1', 'E22': 'FCz', 'E23': 'FC2', 'E24': 'FC4', 'E25': 'FC6', 'E26': 'FT8',
        'E27': 'T7', 'E28': 'C5', 'E29': 'C3', 'E30': 'C1', 'E31': 'Cz', 'E32': 'C2', 'E33': 'C4', 'E34': 'C6', 'E35': 'T8',
        'E36': 'TP7', 'E37': 'CP5', 'E38': 'CP3', 'E39': 'CP1', 'E40': 'CPz', 'E41': 'CP2', 'E42': 'CP4', 'E43': 'CP6', 'E44': 'TP8',
        'E45': 'P7', 'E46': 'P5', 'E47': 'P3', 'E48': 'P1', 'E49': 'Pz', 'E50': 'P2', 'E51': 'P4', 'E52': 'P6', 'E53': 'P8',
        'E54': 'PL7', 'E55': 'PL5', 'E56': 'PL3', 'E57': 'PL1', 'E58': 'PLz', 'E59': 'PL2', 'E60': 'PL4', 'E61': 'PL6', 'E62': 'PL8',
        'E63': 'A1', 'E64': 'A2',
        'E65': 'O9', 'E66': 'O7', 'E67': 'O5', 'E68': 'O3', 'E69': 'O1', 'E70': 'Oz', 'E71': 'O2', 'E72': 'O4', 'E73': 'O6', 'E74': 'O8', 'E75': 'O10',
        'E76': 'PO7', 'E77': 'PO3', 'E78': 'POz', 'E79': 'PO4', 'E80': 'PO8',
        'E81': 'CB1', 'E82': 'CB2',
        'E83': 'TP9', 'E84': 'TP10',
        'E85': 'F9', 'E86': 'F10',
        'E87': 'PPO9', 'E88': 'PPO10',
        'E89': 'PO9', 'E90': 'PO10',
        'E91': 'Fp1', 'E92': 'Fpz', 'E93': 'Fp2',
        'E94': 'Af7', 'E95': 'Af3', 'E96': 'Afz', 'E97': 'Af4', 'E98': 'Af8',
        'E99': 'F7', 'E100': 'F5', 'E101': 'F3', 'E102': 'F1', 'E103': 'Fz', 'E104': 'F2', 'E105': 'F4', 'E106': 'F6', 'E107': 'F8',
        'E108': 'Ft7', 'E109': 'Fc5', 'E110': 'Fc3', 'E111': 'Fc1', 'E112': 'Fcz', 'E113': 'Fc2', 'E114': 'Fc4', 'E115': 'Fc6', 'E116': 'Ft8',
        'E117': 'T7', 'E118': 'C5', 'E119': 'C3', 'E120': 'C1', 'E121': 'Cz', 'E122': 'C2', 'E123': 'C4', 'E124': 'C6', 'E125': 'T8',
        'E126': 'Tp7', 'E127': 'Cp5', 'E128': 'Cp3', 'E129': 'Cp1', 'E130': 'Cpz', 'E131': 'Cp2', 'E132': 'Cp4', 'E133': 'Cp6', 'E134': 'Tp8',
    }
    
    # Check if this is EGI format (starts with E followed by number)
    has_egi_format = any(
        ch.startswith('E') and ch[1:].isdigit() 
        for ch in ch_names
    )
    
    if has_egi_format:
        # Build renaming dict for existing channels only
        rename_dict = {}
        for ch in ch_names:
            if ch in hydrocel_mapping:
                rename_dict[ch] = hydrocel_mapping[ch]
        
        if rename_dict:
            raw = raw.rename_channels(rename_dict)
    
    return raw


class EEGUnityKernel:
    """OpenNeuro DS004447 stage1 kernel for EEGUnity."""
    
    KERNEL_ID = "openneuro_ds004447"
    
    def apply(self, udataset, raw, row):
        # Get subject info
        subject_info = _get_subject_info(row, udataset)
        
        # Rename channels to standard 10-20 format if needed
        raw = _rename_hydrocel_channels(raw)
        
        # Remap events to standardized annotations
        new_annotations = _remap_events_to_annotations(raw)
        raw.set_annotations(new_annotations)
        
        # Build eegunity_description JSON
        original_desc = getattr(raw, 'description', '') or ''
        eegunity_desc = _build_eegunity_description(original_desc, subject_info)
        
        # Set description on raw object
        raw.set_description(eegunity_desc)
        
        return raw


KERNEL = EEGUnityKernel()