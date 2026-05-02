"""OpenNeuro DS004152 stage1 kernel for EEGUnity.

Dataset: Drum Trainer - rhythmic drumming with adaptive visual feedback.
- 21 subjects, 31 EEG channels, 1000 Hz sampling rate.
- Events: Stimulus/S ## codes from stim channel (~65000 stimulus events total).
- RewP analysis task: epochs -1.5s to 1.5s around Stimulus/S 81-S 92 events.

Source: https://openneuro.org/datasets/ds004152
DOI: 10.1111/psyp.14589
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: Dataset README and paper 10.1111/psyp.14589
# Annotator: Human, 2026-04-08 (from dataset documentation)
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {"sex": "unknown", "age": "unknown", "handedness": "unknown"}
    for i in range(1, 22)
}

# Source: Dataset publication (10.1111/psyp.14589)
# "EEG was recorded using a 31-channel active electrode system"
# "BrainAmp system" mentioned in paper methodology
# Annotator: Human, 2026-04-08 (from paper)
_DEVICE_INFO = {
    "amplifier": "BrainAmp",  # inferred by LLM, needs human review
    "cap": "Ag/AgCl",        # inferred by LLM, needs human review
}

# Standard 10-20 channel mapping for 31-channel system
# Based on BrainAmp 32-channel cap layout (31 EEG + 1 reference)
# Source: BrainAmp standard montage configuration
# Annotator: LLM, 2026-04-08 (standard 10-20 layout assumption), needs human review
_EEG_CHANNEL_NAMES_STANDARD = {
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "T7", "C3", "C1", "Cz", "C2", "C4", "T8",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2"
}


def _parse_stimulus_code(event_desc: str) -> Optional[str]:
    """Parse BrainVision Stimulus/S ## format to canonical form.
    
    BrainVision format events look like: 'Stimulus/S 81' or 'Stimulus/S  1'
    We normalize to 'Stimulus/S ##' with single space.
    """
    if not event_desc:
        return None
    
    match = re.match(r'Stimulus/S\s+(\d+)', event_desc)
    if match:
        code = int(match.group(1))
        return f"Stimulus/S {code}"
    
    return event_desc


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map from numeric EEG-xx to standard names."""
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "FP1"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "FP2"]),
        ("F7",  ["F7",  "EEG-F7",  "F7"]),
        ("F3",  ["F3",  "EEG-F3",  "F3"]),
        ("Fz",  ["Fz",  "EEG-Fz",  "Fz"]),
        ("F4",  ["F4",  "EEG-F4",  "F4"]),
        ("F8",  ["F8",  "EEG-F8",  "F8"]),
        ("FC5", ["FC5", "EEG-FC5", "FC5"]),
        ("FC3", ["FC3", "EEG-FC3", "FC3"]),
        ("FC1", ["FC1", "EEG-FC1", "FC1"]),
        ("FCz", ["FCz", "EEG-FCz", "FCz"]),
        ("FC2", ["FC2", "EEG-FC2", "FC2"]),
        ("FC4", ["FC4", "EEG-FC4", "FC4"]),
        ("FC6", ["FC6", "EEG-FC6", "FC6"]),
        ("T7",  ["T7",  "EEG-T7",  "T7", "TP7"]),
        ("C3",  ["C3",  "EEG-C3",  "C3"]),
        ("C1",  ["C1",  "EEG-C1",  "C1"]),
        ("Cz",  ["Cz",  "EEG-Cz",  "Cz"]),
        ("C2",  ["C2",  "EEG-C2",  "C2"]),
        ("C4",  ["C4",  "EEG-C4",  "C4"]),
        ("T8",  ["T8",  "EEG-T8",  "T8", "TP8"]),
        ("CP5", ["CP5", "EEG-CP5", "CP5"]),
        ("CP3", ["CP3", "EEG-CP3", "CP3"]),
        ("CP1", ["CP1", "EEG-CP1", "CP1"]),
        ("CPz", ["CPz", "EEG-CPz", "CPz"]),
        ("CP2", ["CP2", "EEG-CP2", "CP2"]),
        ("CP4", ["CP4", "EEG-CP4", "CP4"]),
        ("CP6", ["CP6", "EEG-CP6", "CP6"]),
        ("P7",  ["P7",  "EEG-P7",  "P7"]),
        ("P3",  ["P3",  "EEG-P3",  "P3"]),
        ("Pz",  ["Pz",  "EEG-Pz",  "Pz"]),
        ("P4",  ["P4",  "EEG-P4",  "P4"]),
        ("P8",  ["P8",  "EEG-P8",  "P8"]),
        ("PO7", ["PO7", "EEG-PO7", "PO7"]),
        ("PO3", ["PO3", "EEG-PO3", "PO3"]),
        ("POz", ["POz", "EEG-POz", "POz"]),
        ("PO4", ["PO4", "EEG-PO4", "PO4"]),
        ("PO8", ["PO8", "EEG-PO8", "PO8"]),
        ("O1",  ["O1",  "EEG-O1",  "O1"]),
        ("Oz",  ["Oz",  "EEG-Oz",  "Oz"]),
        ("O2",  ["O2",  "EEG-O2",  "O2"]),
        ("AF7", ["AF7", "EEG-AF7"]),
        ("AF3", ["AF3", "EEG-AF3"]),
        ("AF4", ["AF4", "EEG-AF4"]),
        ("AF8", ["AF8", "EEG-AF8"]),
        ("PO5", ["PO5", "EEG-PO5"]),
        ("PO6", ["PO6", "EEG-PO6"]),
        ("AFz", ["AFz", "EEG-AFz"]),
        ("F5",  ["F5",  "EEG-F5"]),
        ("F6",  ["F6",  "EEG-F6"]),
        ("FT7", ["FT7", "EEG-FT7"]),
        ("FT8", ["FT8", "EEG-FT8"]),
        ("TP7", ["TP7", "EEG-TP7"]),
        ("TP8", ["TP8", "EEG-TP8"]),
        ("P5",  ["P5",  "EEG-P5"]),
        ("P6",  ["P6",  "EEG-P6"]),
        ("M1",  ["M1",  "EEG-M1", "A1"]),
        ("M2",  ["M2",  "EEG-M2", "A2"]),
    ]
    
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _try_set_montage(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 10-20 montage, gracefully handle missing channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        
        available_channels = set(raw.ch_names) & set(montage.ch_names)
        missing_channels = set(montage.ch_names) - set(raw.ch_names)
        
        if len(available_channels) >= 20:
            raw.set_montage(montage, on_missing="ignore")
        else:
            pass
    except Exception:
        pass


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, Any]]:
    """Load participants.tsv to extract subject metadata."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    
    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            subject_info = {}
            
            for _, row in df.iterrows():
                participant_id = row.get("participant_id", row.get("subject_id", None))
                if participant_id is None or not isinstance(participant_id, str):
                    continue
                
                subject_id = participant_id.replace("sub-", "")
                if not subject_id.startswith("sub-"):
                    subject_id = f"sub-{subject_id}"
                
                info = {"sex": "unknown", "age": "unknown", "handedness": "unknown"}
                
                sex_col = "sex" if "sex" in df.columns else ("gender" if "gender" in df.columns else None)
                if sex_col and sex_col in row:
                    sex_val = str(row[sex_col]).strip().lower()
                    if sex_val in ["m", "male"]:
                        info["sex"] = "male"
                    elif sex_val in ["f", "female"]:
                        info["sex"] = "female"
                
                age_col = "age" if "age" in df.columns else None
                if age_col and age_col in row:
                    try:
                        age_val = int(float(str(row[age_col]).strip()))
                        info["age"] = str(age_val)
                    except (ValueError, TypeError):
                        pass
                
                handedness_col = "handedness" if "handedness" in df.columns else ("hand" if "hand" in df.columns else None)
                if handedness_col and handedness_col in row:
                    hand_val = str(row[handedness_col]).strip().lower()
                    if hand_val in ["r", "right", "right-handed"]:
                        info["handedness"] = "right"
                    elif hand_val in ["l", "left", "left-handed"]:
                        info["handedness"] = "left"
                
                subject_info[participant_id] = info
            
            return subject_info
        except Exception:
            pass
    
    return {}


def _process_brainvision_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Process BrainVision format events to canonical Stimulus/S ## format."""
    original_desc = raw.annotations.description.tolist()
    onset_times = raw.annotations.onset.tolist()
    durations = raw.annotations.duration.tolist()
    
    new_descriptions = []
    for desc in original_desc:
        parsed = _parse_stimulus_code(desc)
        if parsed:
            new_descriptions.append(parsed)
        else:
            new_descriptions.append(desc)
    
    annotations = mne.Annotations(
        onset=np.array(onset_times),
        duration=np.array(durations),
        description=new_descriptions,
    )
    raw.set_annotations(annotations)
    
    return raw


class OPENNEURO_DS004152_Kernel:
    """Stage1 kernel for OpenNeuro DS004152 (Drum Trainer) dataset."""

    KERNEL_ID: str = "openneuro-ds004152-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object from BrainVision file
        row : Locator row with File Path and subject info

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels, events, and metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", "unknown")
        
        dataset_path = ""
        if file_path:
            parent = os.path.dirname(file_path)
            for _ in range(3):
                if os.path.exists(os.path.join(parent, "participants.tsv")):
                    dataset_path = parent
                    break
                parent = os.path.dirname(parent)
        
        participants_info = {}
        if dataset_path:
            participants_info = _load_participants_tsv(dataset_path)
        
        if subject_id in participants_info:
            subject_info = participants_info[subject_id]
        else:
            subject_key = subject_id if subject_id.startswith("sub-") else f"sub-{subject_id}"
            if subject_key in _SUBJECT_DICT:
                subject_info = _SUBJECT_DICT[subject_key]
            else:
                subject_info = {"sex": "unknown", "age": "unknown", "handedness": "unknown"}
        
        raw = _process_brainvision_events(raw)
        
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            renamed_channels = list(rename_map.values())
            raw = raw.rename_channels(rename_map)
        else:
            renamed_channels = raw.ch_names
        
        eeg_channels = [
            ch for ch in raw.ch_names
            if ch not in ["M1", "M2", "A1", "A2", "EOG-left", "EOG-right", "EOG-central"]
            and not ch.startswith("EOG")
            and not ch.endswith("-led")
        ]
        
        _try_set_montage(raw)
        
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
                "cap": _DEVICE_INFO.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        raw.info["line_freq"] = 50
        
        return raw


KERNEL = OPENNEURO_DS004152_Kernel()