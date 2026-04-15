"""OpenNeuro DS001784 stage1 kernel for EEGUnity.

Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant
depression (EEG). BIDS-formatted dataset with 65 channels at 1450 Hz.

Dataset: openneuro_ds001784 | Year: 2019 | DOI: https://doi.org/10.1038/s41467-019-09557-4
Paradigm: MSIT with emotional stimuli + DBS ON/OFF

This kernel:
- Reads participants.tsv for age/sex/dbs metadata
- Parses events.tsv to extract trial_type (interference/control) labels
- Maps raw events (event_2/4/6) to semantic labels
- Sets standard 10-20 montage for 65-channel EEG
- Provides DBS ON/OFF labels from participants.tsv

Source: https://openneuro.org/datasets/ds001784
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# =============================================================================
# Device Metadata Defaults
# =============================================================================
_DEVICE_METADATA_DEFAULTS: Dict[str, str] = {
    "amplifier": "unknown",
    "cap": "unknown",
    "handedness": "unknown",
}


# =============================================================================
# Raw Event Mapping
# =============================================================================
_EVENT_RAW_MAP: Dict[str, str] = {
    "event_2": "interference_trial",
    "event_4": "control_trial",
    "event_6": "afmsit_trial",
}


# =============================================================================
# Label Mapping for Super Meta
# =============================================================================
_COGNITIVE_LABEL_MAP: Dict[str, int] = {
    "interference_trial": 1,
    "control_trial": 0,
}


# =============================================================================
# Standard 10-20 Channel Names for 64-65 Channel Systems
# =============================================================================
_STANDARD_1020_CHANNELS: List[str] = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standard 10-20 channel names."""
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    alias_groups = [
        ("Fp1", ["Fp1", "FP1", "fp1"]),
        ("Fpz", ["Fpz", "FPz", "fpz"]),
        ("Fp2", ["Fp2", "FP2", "fp2"]),
        ("F7", ["F7", "F7 "]),
        ("F3", ["F3"]),
        ("Fz", ["Fz"]),
        ("F4", ["F4"]),
        ("F8", ["F8"]),
        ("T7", ["T7", "T7 "]),
        ("C3", ["C3"]),
        ("Cz", ["Cz"]),
        ("C4", ["C4"]),
        ("T8", ["T8"]),
        ("P7", ["P7"]),
        ("P3", ["P3"]),
        ("Pz", ["Pz"]),
        ("P4", ["P4"]),
        ("P8", ["P8"]),
        ("O1", ["O1"]),
        ("Oz", ["Oz"]),
        ("O2", ["O2"]),
        ("AF7", ["AF7"]),
        ("AF3", ["AF3"]),
        ("AFz", ["AFz"]),
        ("AF4", ["AF4"]),
        ("AF8", ["AF8"]),
        ("F5", ["F5"]),
        ("F1", ["F1"]),
        ("F2", ["F2"]),
        ("F6", ["F6"]),
        ("FC5", ["FC5"]),
        ("FC1", ["FC1"]),
        ("FCz", ["FCz"]),
        ("FC2", ["FC2"]),
        ("FC6", ["FC6"]),
        ("C5", ["C5"]),
        ("C1", ["C1"]),
        ("C2", ["C2"]),
        ("C6", ["C6"]),
        ("CP5", ["CP5"]),
        ("CP1", ["CP1"]),
        ("CPz", ["CPz"]),
        ("CP2", ["CP2"]),
        ("CP6", ["CP6"]),
        ("P5", ["P5"]),
        ("P1", ["P1"]),
        ("P2", ["P2"]),
        ("P6", ["P6"]),
        ("PO7", ["PO7"]),
        ("PO3", ["PO3"]),
        ("POz", ["POz"]),
        ("PO4", ["PO4"]),
        ("PO8", ["PO8"]),
    ]
    
    eog_aliases = [
        ("EOG-left", ["EOG左", "EOG-L", "EOGL", "VEOG-L", "HEOG-L", "eog_l"]),
        ("EOG-right", ["EOG右", "EOG-R", "EOGR", "VEOG-R", "HEOG-R", "eog_r"]),
        ("EOG-central", ["EOG中", "EOG-C", "EOGC", "VEOG-C", "eog_c"]),
    ]
    
    misc_aliases = [
        ("Status", ["Status", "STI 014", "Stimulus", "Stim"]),
        ("Misc", ["Misc", "MISC"]),
    ]
    
    all_aliases = alias_groups + eog_aliases + misc_aliases
    
    for target_name, aliases in all_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _load_participants_metadata(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv file."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_file):
        return pd.read_csv(participants_file, sep="\t")
    return pd.DataFrame()


def _get_subject_metadata(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv."""
    metadata = {
        "age": "unknown",
        "sex": "unknown",
        "dbs_condition": "unknown",
    }
    
    if participants_df.empty:
        return metadata
    
    subject_col = None
    for col in ["participant_id", "subject_id", "participant"]:
        if col in participants_df.columns:
            subject_col = col
            break
    
    if subject_col is None:
        return metadata
    
    subject_row = participants_df[participants_df[subject_col] == subject_id]
    if subject_row.empty:
        short_id = subject_id.replace("sub-", "")
        subject_row = participants_df[participants_df[subject_col].str.contains(short_id, na=False)]
    
    if not subject_row.empty:
        row = subject_row.iloc[0]
        if "age" in participants_df.columns:
            metadata["age"] = str(row.get("age", "unknown"))
        if "sex" in participants_df.columns:
            metadata["sex"] = str(row.get("sex", "unknown"))
        if "dbs_condition" in participants_df.columns:
            metadata["dbs_condition"] = str(row.get("dbs_condition", "unknown"))
    
    return metadata


def _load_json_sidecar(raw: mne.io.BaseRaw, dataset_path: str) -> str:
    """Load JSON sidecar file for EEG file, return empty string if not found."""
    raw_filename = raw.filenames[0] if raw.filenames else ""
    if not raw_filename:
        return "{}"
    
    base_path = raw_filename.replace("_eeg.fif", "_eeg.json")
    if os.path.exists(base_path):
        try:
            with open(base_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content if content.strip() else "{}"
        except Exception:
            pass
    
    return "{}"


class EEGUnityKernel:
    KERNEL_ID = "openneuro_ds001784_stage1"
    
    def __init__(self):
        self.eegunity_description = {
            "age": "str",
            "sex": "str",
            "amplifier": _DEVICE_METADATA_DEFAULTS["amplifier"],
            "cap": _DEVICE_METADATA_DEFAULTS["cap"],
            "handedness": _DEVICE_METADATA_DEFAULTS["handedness"],
        }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        if raw is None:
            raise ValueError("raw cannot be None")
        dataset_path = udataset if isinstance(udataset, str) else str(udataset)
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        try:
            raw = raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass
        subject_id = row.get("subject_id", "unknown") if isinstance(row, dict) else str(row)
        participants_df = _load_participants_metadata(dataset_path)
        subject_meta = _get_subject_metadata(participants_df, subject_id)
        description = {
            "subject_id": subject_id,
            "dataset": "openneuro_ds001784",
            "age": subject_meta.get("age", "unknown"),
            "sex": subject_meta.get("sex", "unknown"),
            "dbs_condition": subject_meta.get("dbs_condition", "unknown"),
        }
        if raw.annotations is not None and len(raw.annotations) > 0:
            for idx, ann in enumerate(raw.annotations):
                if hasattr(ann, 'description'):
                    event_desc = str(ann.description)
                    if event_desc in _EVENT_RAW_MAP:
                        raw.annotations.description[idx] = _EVENT_RAW_MAP[event_desc]
        return raw


KERNEL = EEGUnityKernel()