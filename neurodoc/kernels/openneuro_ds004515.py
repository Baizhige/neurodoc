"""OpenNeuro ds004515 stage1 kernel for EEGUnity.

EEG: Alcohol imagery reinforcement learning task with light and heavy drinker participants.

Dataset: openneuro_ds004515 | Year: 2023
Source: https://openneuro.org/datasets/ds004515
Paper: https://doi.org/10.1016/j.pscychresns.2023.111685

Paradigm: Participants (light and heavy drinkers) performed a reinforcement learning task 
involving alcohol-related and neutral imagery cues. On each trial, participants chose 
between left and right buttons in response to cues, with feedback indicating correct/incorrect 
responses.

Subjects: 42 | Channels: 64 | Sampling Rate: 500 Hz
Format: BrainVision (.eeg, .vhdr, .vmrk)

This kernel handles:
- Channel renaming to standard 10-20 names
- Montage setting for 64-channel standard_1020 layout
- Metadata extraction from participants.tsv (age, sex, AUDIT, BDI, EDUCATION, GROUP)
- Event annotation from events.tsv sidecars (BrainVision .eeg without embedded markers)
- Derived misc channels for GROUP and AUDIT from participants.tsv
"""

from __future__ import annotations

import json
import os
import re
import warnings
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: Standard 10-20 system 64-channel electrode layout
# Paper: https://doi.org/10.1016/j.pscychresns.2023.111685
# Annotator: LLM, 2026-04-08, needs human verification
_CHANNEL_ALIAS_GROUPS: List[tuple] = [
    ("Fp1", ["Fp1", "EEG Fp1", "EEG-Fp1", "FP1", "Fp1."]),
    ("Fp2", ["Fp2", "EEG Fp2", "EEG-Fp2", "FP2", "Fp2."]),
    ("AF7", ["AF7", "EEG AF7", "EEG-AF7", "AF7."]),
    ("AF3", ["AF3", "EEG AF3", "EEG-AF3", "AF3."]),
    ("AFz", ["AFz", "EEG AFz", "EEG-AFz", "AFz."]),
    ("AF4", ["AF4", "EEG AF4", "EEG-AF4", "AF4."]),
    ("AF8", ["AF8", "EEG AF8", "EEG-AF8", "AF8."]),
    ("F7", ["F7", "EEG F7", "EEG-F7", "F7."]),
    ("F5", ["F5", "EEG F5", "EEG-F5", "F5."]),
    ("F3", ["F3", "EEG F3", "EEG-F3", "F3."]),
    ("F1", ["F1", "EEG F1", "EEG-F1", "F1."]),
    ("Fz", ["Fz", "EEG Fz", "EEG-Fz", "Fz."]),
    ("F2", ["F2", "EEG F2", "EEG-F2", "F2."]),
    ("F4", ["F4", "EEG F4", "EEG-F4", "F4."]),
    ("F6", ["F6", "EEG F6", "EEG-F6", "F6."]),
    ("F8", ["F8", "EEG F8", "EEG-F8", "F8."]),
    ("FT7", ["FT7", "EEG FT7", "EEG-FT7", "FT7."]),
    ("FT8", ["FT8", "EEG FT8", "EEG-FT8", "FT8."]),
    ("T7", ["T7", "EEG T7", "EEG-T7", "T7.", "TP9"]),
    ("C5", ["C5", "EEG C5", "EEG-C5", "C5."]),
    ("C3", ["C3", "EEG C3", "EEG-C3", "C3."]),
    ("C1", ["C1", "EEG C1", "EEG-C1", "C1."]),
    ("Cz", ["Cz", "EEG Cz", "EEG-Cz", "Cz."]),
    ("C2", ["C2", "EEG C2", "EEG-C2", "C2."]),
    ("C4", ["C4", "EEG C4", "EEG-C4", "C4."]),
    ("C6", ["C6", "EEG C6", "EEG-C6", "C6."]),
    ("T8", ["T8", "EEG T8", "EEG-T8", "T8.", "TP10"]),
    ("TP7", ["TP7", "EEG TP7", "EEG-TP7", "TP7."]),
    ("TP8", ["TP8", "EEG TP8", "EEG-TP8", "TP8."]),
    ("CP5", ["CP5", "EEG CP5", "EEG-CP5", "CP5."]),
    ("CP3", ["CP3", "EEG CP3", "EEG-CP3", "CP3."]),
    ("CP1", ["CP1", "EEG CP1", "EEG-CP1", "CP1."]),
    ("CPz", ["CPz", "EEG CPz", "EEG-CPz", "CPz."]),
    ("CP2", ["CP2", "EEG CP2", "EEG-CP2", "CP2."]),
    ("CP4", ["CP4", "EEG CP4", "EEG-CP4", "CP4."]),
    ("CP6", ["CP6", "EEG CP6", "EEG-CP6", "CP6."]),
    ("P7", ["P7", "EEG P7", "EEG-P7", "P7."]),
    ("P5", ["P5", "EEG P5", "EEG-P5", "P5."]),
    ("P3", ["P3", "EEG P3", "EEG-P3", "P3."]),
    ("P1", ["P1", "EEG P1", "EEG-P1", "P1."]),
    ("Pz", ["Pz", "EEG Pz", "EEG-Pz", "Pz."]),
    ("P2", ["P2", "EEG P2", "EEG-P2", "P2."]),
    ("P4", ["P4", "EEG P4", "EEG-P4", "P4."]),
    ("P6", ["P6", "EEG P6", "EEG-P6", "P6."]),
    ("P8", ["P8", "EEG P8", "EEG-P8", "P8."]),
    ("PO7", ["PO7", "EEG PO7", "EEG-PO7", "PO7."]),
    ("PO3", ["PO3", "EEG PO3", "EEG-PO3", "PO3."]),
    ("POz", ["POz", "EEG POz", "EEG-POz", "POz."]),
    ("PO4", ["PO4", "EEG PO4", "EEG-PO4", "PO4."]),
    ("PO8", ["PO8", "EEG PO8", "EEG-PO8", "PO8."]),
    ("O1", ["O1", "EEG O1", "EEG-O1", "O1."]),
    ("Oz", ["Oz", "EEG Oz", "EEG-Oz", "Oz."]),
    ("O2", ["O2", "EEG O2", "EEG-O2", "O2."]),
    ("PO9", ["PO9", "EEG PO9", "EEG-PO9", "PO9."]),
    ("PO10", ["PO10", "EEG PO10", "EEG-PO10", "PO10."]),
    ("Iz", ["Iz", "EEG Iz", "EEG-Iz", "Iz."]),
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in _CHANNEL_ALIAS_GROUPS:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    # BIDS pattern: sub-<label>/.../sub-<label>_task-..._eeg.<ext>
    match = re.search(r'sub-([a-zA-Z0-9]+)', os.path.basename(file_path))
    if match:
        return f"sub-{match.group(1)}"
    # Try from directory structures
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith('sub-'):
            return part
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to the EEG file."""
    # Walk up from file to find dataset root
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):  # Limit search depth
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
            os.path.join(current_dir, "..", "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv sidecar for a BrainVision file."""
    # BIDS pattern: sub-X_task-Y_eeg.eeg -> sub-X_task-Y_events.tsv
    base = file_path.replace('.eeg', '').replace('.vhdr', '').replace('.vmrk', '')
    candidates = [
        base + '_events.tsv',
        base.replace('_eeg', '_events') + '.tsv',
    ]
    for cand in candidates:
        cand = os.path.normpath(cand)
        if os.path.exists(cand):
            return cand
    
    # Also check in the same directory with pattern matching
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).split('_eeg')[0]
    
    if os.path.isdir(dir_name):
        for f in os.listdir(dir_name):
            if f.endswith('_events.tsv') and f.startswith(base_name):
                return os.path.join(dir_name, f)
    
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "AUDIT": "unknown",
        "BDI": "unknown",
        "EDUCATION": "unknown",
        "GROUP": "unknown",
    }
    
    try:
        df = pd.read_csv(participants_path, sep='\t')
        
        # Find subject row - handle both 'sub-01' and '01' formats
        sub_col = 'participant_id'
        if sub_col not in df.columns:
            # Try alternatives
            for col in df.columns:
                if 'participant' in col.lower() or 'subject' in col.lower():
                    sub_col = col
                    break
        
        # Match subject ID
        subject_rows = df[df[sub_col] == subject_id]
        if len(subject_rows) == 0:
            # Try without 'sub-' prefix
            short_id = subject_id.replace('sub-', '')
            subject_rows = df[df[sub_col] == short_id]
        if len(subject_rows) == 0:
            # Try with 'sub-' prefix added
            if not subject_id.startswith('sub-'):
                long_id = f"sub-{subject_id}"
                subject_rows = df[df[sub_col] == long_id]
        
        if len(subject_rows) > 0:
            row = subject_rows.iloc[0]
            for key in info.keys():
                if key in row:
                    info[key] = str(row[key])
    except Exception:
        pass
    
    return info


def _read_events_tsv(events_path: str) -> List[Dict[str, Any]]:
    """Read events from events.tsv."""
    events = []
    try:
        df = pd.read_csv(events_path, sep='\t')
        
        required_cols = ['onset', 'trial_type']
        if not all(c in df.columns for c in required_cols):
            # Try alternatives
            onset_col = 'onset' if 'onset' in df.columns else 'sample' if 'sample' in df.columns else None
            type_col = 'trial_type' if 'trial_type' in df.columns else 'event_type' if 'event_type' in df.columns else 'value' if 'value' in df.columns else None
            
            if onset_col is None or type_col is None:
                return events
        
        for _, row in df.iterrows():
            event = {
                'onset': float(row.get('onset', 0)),
                'duration': float(row.get('duration', 0)) if 'duration' in row else 0.0,
                'trial_type': str(row.get('trial_type', 'unknown')),
            }
            # Add optional columns
            for col in ['response_time', 'stim_file', 'value', 'sample']:
                if col in row:
                    event[col] = row[col]
            events.append(event)
    except Exception:
        pass
    
    return events


class OpenNeuro_ds004515_Kernel:
    KERNEL_ID = "openneuro_ds004515"
    DATASET_NAME = "openneuro_ds004515"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        
        # Extract subject ID
        subject_id = _get_subject_id_from_path(file_path)
        
        # Find and read participants.tsv
        participants_path = _find_participants_tsv(file_path)
        participants_info = {}
        if participants_path and subject_id:
            participants_info = _read_participants_info(participants_path, subject_id)
        
        # Channel renaming to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage for 64-channel standard_1020 layout
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw = raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass
        
        # Read events from events.tsv sidecar
        events_path = _find_events_tsv(file_path)
        if events_path:
            events = _read_events_tsv(events_path)
            if events:
                # Create annotations from events
                onsets = [e['onset'] for e in events]
                durations = [e.get('duration', 0.0) for e in events]
                descriptions = [e['trial_type'] for e in events]
                
                # Remove any existing annotations to avoid conflicts
                raw.set_annotations(None)
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw = raw.set_annotations(annot)
        
        # Build eegunity_description with required fields
        original_desc = raw.info.get("description", "")
        
        eegunity_description = {
            "age": participants_info.get("age", "unknown"),
            "sex": participants_info.get("sex", "unknown"),
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }
        
        # Add additional metadata
        for key in ["AUDIT", "BDI", "EDUCATION", "GROUP"]:
            if key in participants_info:
                eegunity_description[key.lower()] = participants_info[key]
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Add derived misc channels from participants.tsv
        misc_channels_to_add = []
        for key in ["GROUP", "AUDIT"]:
            if key in participants_info and participants_info[key] != "unknown":
                misc_channels_to_add.append((key, participants_info[key]))
        
        if misc_channels_to_add:
            # Create misc channel data
            n_times = len(raw.times)
            misc_data = []
            misc_names = []
            misc_types = []
            
            for name, value in misc_channels_to_add:
                try:
                    # Try to convert to numeric, otherwise use 0/1 encoding
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    # String encoding: map unique values to integers
                    numeric_value = 1.0  # Default for non-numeric
                
                misc_data.append(np.full((1, n_times), numeric_value))
                misc_names.append(name)
                misc_types.append('misc')
            
            if misc_data:
                # Create new info for misc channels
                misc_info = mne.create_info(ch_names=misc_names, sfreq=raw.info['sfreq'], ch_types=misc_types)
                misc_raw = mne.io.RawArray(np.concatenate(misc_data, axis=0), misc_info)
                
                # Add to raw
                raw = raw.add_channels([misc_raw], force_update_info=True)
        
        return raw


KERNEL = OpenNeuro_ds004515_Kernel()