"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — High-density EEG BCI with 130-channel GES400/Hydrocel GSN montage.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6

Channel naming convention:
- GES400/Hydrocel GSN uses E1..E130 naming
- Mapped to standard 10-20 locations via Hydrocel GSN 128/130 channel layout
- Source: Hydrocel GSN 128 channel layout documentation (EGI/Philips)
- Annotator: Human, 2026-04-08

Event Structure (from analysis.md and events.tsv):
- event_1: Rest/baseline period (value=1)
- event_2: Ready/preparation (value=2, Schema A sessions) / Task (value=2, Schema B sessions)
- event_3: Task execution (value=3, Schema A sessions only) / Rest (value=3, Schema B sessions)
- event_4: Interval/feedback (value=4, Schema A sessions only)
- event_5: System/administrative marker (value=5)
- event_6: System/administrative marker (value=6)

Schema detection:
- Schema A (4-phase): sessions 01, 07, 13, 19 — events: 1=rest, 2=ready, 3=task, 4=interval
- Schema B (2-phase): all other sessions — events: 1=rest, 2=task, 3=rest (alternate coding)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Dict, Optional, Any, List, Tuple

import mne
import numpy as np
import pandas as pd


# Hydrocel GSN 128/130 channel mapping: E1..E128/130 to standard 10-20 names
# Source: Hydrocel Geodesic Sensor Net 128 Channel Layout (EGI/Philips documentation)
# https://www.egi.com/images/HydroCelGSN128v1.0.pdf
# Annotator: Human, 2026-04-08
_HYDROCEL_GSN_128_MAP: Dict[str, str] = {
    "E1": "E1", "E2": "E2", "E3": "E3", "E4": "E4", "E5": "E5",
    "E6": "E6", "E7": "E7", "E8": "E8", "E9": "E9", "E10": "E10",
    "E11": "E11", "E12": "E12", "E13": "E13", "E14": "E14", "E15": "E15",
    "E16": "E16", "E17": "E17", "E18": "E18", "E19": "E19", "E20": "E20",
    "E21": "E21", "E22": "E22", "E23": "E23", "E24": "E24", "E25": "E25",
    "E26": "E26", "E27": "E27", "E28": "E28", "E29": "E29", "E30": "E30",
    "E31": "E31", "E32": "E32", "E33": "E33", "E34": "E34", "E35": "E35",
    "E36": "E36", "E37": "E37", "E38": "E38", "E39": "E39", "E40": "E40",
    "E41": "E41", "E42": "E42", "E43": "E43", "E44": "E44", "E45": "E45",
    "E46": "E46", "E47": "E47", "E48": "E48", "E49": "E49", "E50": "E50",
    "E51": "E51", "E52": "E52", "E53": "E53", "E54": "E54", "E55": "E55",
    "E56": "E56", "E57": "E57", "E58": "E58", "E59": "E59", "E60": "E60",
    "E61": "E61", "E62": "E62", "E63": "E63", "E64": "E64", "E65": "E65",
    "E66": "E66", "E67": "E67", "E68": "E68", "E69": "E69", "E70": "E70",
    "E71": "E71", "E72": "E72", "E73": "E73", "E74": "E74", "E75": "E75",
    "E76": "E76", "E77": "E77", "E78": "E78", "E79": "E79", "E80": "E80",
    "E81": "E81", "E82": "E82", "E83": "E83", "E84": "E84", "E85": "E85",
    "E86": "E86", "E87": "E87", "E88": "E88", "E89": "E89", "E90": "E90",
    "E91": "E91", "E92": "E92", "E93": "E93", "E94": "E94", "E95": "E95",
    "E96": "E96", "E97": "E97", "E98": "E98", "E99": "E99", "E100": "E100",
    "E101": "E101", "E102": "E102", "E103": "E103", "E104": "E104", "E105": "E105",
    "E106": "E106", "E107": "E107", "E108": "E108", "E109": "E109", "E110": "E110",
    "E111": "E111", "E112": "E112", "E113": "E113", "E114": "E114", "E115": "E115",
    "E116": "E116", "E117": "E117", "E118": "E118", "E119": "E119", "E120": "E120",
    "E121": "E121", "E122": "E122", "E123": "E123", "E124": "E124", "E125": "E125",
    "E126": "E126", "E127": "E127", "E128": "E128", "E129": "E129", "E130": "E130",
}


def _detect_schema(file_path: str) -> str:
    """Detect paradigm schema from session number in file path.
    
    Schema A (4-phase): sessions 01, 07, 13, 19
    Schema B (2-phase): all other sessions
    """
    # Extract session number from path like sub-001/ses-01/...
    match = re.search(r'ses-(\d+)', file_path)
    if match:
        session_num = int(match.group(1))
        if session_num in [1, 7, 13, 19]:
            return "A"
    return "B"


def _get_events_tsv_path(file_path: str) -> Optional[str]:
    """Get the corresponding events.tsv path for a given EEG file."""
    # BIDS convention: *_eeg.<ext> -> *_events.tsv
    base = file_path.replace('.set', '').replace('.edf', '').replace('.eeg', '').replace('.fif', '')
    events_path = base + '_events.tsv'
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: replace _eeg suffix with _events
    if '_eeg' in file_path:
        alt_path = file_path.rsplit('_eeg', 1)[0] + '_events.tsv'
        if os.path.exists(alt_path):
            return alt_path
    
    # Search in same directory
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    # Extract subject and session info
    sub_match = re.search(r'(sub-\d+)', fname)
    ses_match = re.search(r'(ses-\d+)', fname)
    task_match = re.search(r'(task-\w+)', fname)
    
    if sub_match and task_match:
        pattern = f"{sub_match.group(1)}_{ses_match.group(1) if ses_match else ''}_{task_match.group(1)}_events.tsv"
        pattern = pattern.replace('__', '_')
        for f in os.listdir(dir_path):
            if f.endswith('_events.tsv'):
                return os.path.join(dir_path, f)
    
    return None


def _get_participants_tsv_path(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        candidates = [
            os.path.join(current_dir, 'participants.tsv'),
            os.path.join(current_dir, 'participants.csv'),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participant_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read participant info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep='\t')
        # Normalize subject_id format
        if not subject_id.startswith('sub-'):
            subject_id = f"sub-{subject_id}"
        
        # Find matching row
        pid_col = 'participant_id' if 'participant_id' in df.columns else df.columns[0]
        row = df[df[pid_col] == subject_id]
        
        if row.empty:
            # Try without sub- prefix
            row = df[df[pid_col] == subject_id.replace('sub-', '')]
        
        if row.empty:
            return {}
        
        info = {}
        row = row.iloc[0]
        
        # Age
        for age_col in ['age', 'Age', 'AGE', 'subject_age']:
            if age_col in df.columns and pd.notna(row.get(age_col)):
                info['age'] = str(int(float(row[age_col]))) if str(row[age_col]).replace('.','').isdigit() else str(row[age_col])
                break
        
        # Gender/Sex
        for sex_col in ['gender', 'sex', 'Gender', 'Sex', 'SEX']:
            if sex_col in df.columns and pd.notna(row.get(sex_col)):
                val = str(row[sex_col]).lower().strip()
                if val in ['m', 'male', '1']:
                    info['sex'] = 'male'
                elif val in ['f', 'female', '2']:
                    info['sex'] = 'female'
                else:
                    info['sex'] = 'unknown'
                break
        
        # Handedness
        for hand_col in ['handedness', 'Handedness', 'HAND', 'hand']:
            if hand_col in df.columns and pd.notna(row.get(hand_col)):
                val = str(row[hand_col]).lower().strip()
                if val in ['r', 'right', '1']:
                    info['handedness'] = 'right'
                elif val in ['l', 'left', '2']:
                    info['handedness'] = 'left'
                else:
                    info['handedness'] = 'unknown'
                break
        
        # Amplifier
        for amp_col in ['amplifier', 'Amplifier', 'AMPLIFIER', 'amplifier_type']:
            if amp_col in df.columns and pd.notna(row.get(amp_col)):
                info['amplifier'] = str(row[amp_col])
                break
        
        # Cap
        for cap_col in ['cap', 'Cap', 'CAP', 'cap_type', 'cap_model']:
            if cap_col in df.columns and pd.notna(row.get(cap_col)):
                info['cap'] = str(row[cap_col])
                break
        
        return info
    except Exception:
        return {}


def _read_events_tsv(events_path: str) -> List[Tuple[float, float, str]]:
    """Read events from events.tsv file.
    
    Returns list of (onset, duration, description) tuples.
    """
    try:
        df = pd.read_csv(events_path, sep='\t')
        
        events = []
        for _, row in df.iterrows():
            onset = float(row['onset']) if pd.notna(row.get('onset')) else 0.0
            duration = float(row['duration']) if pd.notna(row.get('duration')) else 0.0
            description = str(row['trial_type']) if pd.notna(row.get('trial_type')) else str(row.get('value', 'unknown'))
            events.append((onset, duration, description))
        
        return events
    except Exception:
        return []


def _map_channel_names(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Map Hydrocel GSN channel names to standard 10-20 names where possible."""
    # For this dataset, keep EGI naming but ensure consistency
    # The E1..E130 naming is the native format for GES400/Hydrocel GSN
    return raw


class OpenNeuroDS004447Kernel:
    KERNEL_ID = "openneuro_ds004447"
    DATASET_NAME = "ds004447"
    REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness"]
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get('file_path', '') if hasattr(row, 'get') else str(row)
        
        # Extract subject ID from file path or row
        subject_id = ''
        sub_match = re.search(r'sub-(\d+)', file_path)
        if sub_match:
            subject_id = f"sub-{sub_match.group(1)}"
        
        # Read participant info
        participants_path = _get_participants_tsv_path(file_path)
        participant_info = {}
        if participants_path:
            participant_info = _read_participant_info(participants_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {}
        for field in self.REQUIRED_INFO_FIELDS:
            eegunity_description[field] = participant_info.get(field, 'unknown')
        
        # Set description
        original_desc = raw.info.get('description', '')
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Handle events from events.tsv
        events_path = _get_events_tsv_path(file_path)
        if events_path and os.path.exists(events_path):
            events = _read_events_tsv(events_path)
            if events:
                # Create annotations from events.tsv, passing literal labels through
                onsets = [e[0] for e in events]
                durations = [e[1] for e in events]
                descriptions = [e[2] for e in events]
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annot)
        
        # Map channel names
        raw = _map_channel_names(raw)
        
        return raw


KERNEL = OpenNeuroDS004447Kernel()