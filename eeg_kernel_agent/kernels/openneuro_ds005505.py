"""OpenNeuro ds005505 (HBN EEG Release 1) stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 1 - Large-scale multi-task developmental
battery collected from children and adolescents (ages 5.2-21.7). Contains resting-state,
movie watching, contrast detection, surrounding suppression, sequence learning, and
symbol search paradigms. Uses BioSemi 128-channel system at 500 Hz.

Source: https://openneuro.org/datasets/ds005505
Reference: https://doi.org/10.1016/j.neuroimage.2020.117001
          https://doi.org/10.1101/2024.10.03.615261
          https://www.nature.com/articles/sdata201740
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
# BIO SEMI 128-CHANNEL SYSTEM - Standard electrode positions
# Source: BioSemi ActiveTwo 128-channel layout documentation
# Annotator: Human, 2026-04-08
# ============================================================================
_BIOSEMI_128_STANDARD_NAMES = [
    "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", "T7", "T8", "TP7", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Fp2", "F6", "F4", "F2", "AF4", "AF8",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
]

_BIOSEMI_AUX_CHANNELS = [
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
    "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
    "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24",
    "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8",
    "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
    "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24",
    "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32",
    "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8",
    "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16",
    "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24",
    "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8",
    "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16",
    "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24",
    "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32",
    "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8",
    "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16",
    "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24",
    "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32",
]


def _build_biosemi_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for BioSemi 128-channel system."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for i, std_name in enumerate(_BIOSEMI_128_STANDARD_NAMES):
        possible_names = [
            f"EEG {i+1:03d}",
            f"EEG {i+1}",
            f"EEG{i+1:03d}",
            f"EEG{i+1}",
            f"EEG-{i+1:03d}",
            f"EEG-{i+1}",
        ]
        for src in possible_names:
            if src in existing_names and src != std_name:
                rename_map[src] = std_name
                break

    alias_groups = [
        ("Fp1", ["Fp1", "FP1"]),
        ("Fp2", ["Fp2", "FP2"]),
        ("AF7", ["AF7"]),
        ("AF3", ["AF3"]),
        ("AFz", ["AFz"]),
        ("AF4", ["AF4"]),
        ("AF8", ["AF8"]),
        ("F7", ["F7"]),
        ("F5", ["F5"]),
        ("F3", ["F3"]),
        ("F1", ["F1"]),
        ("Fz", ["Fz"]),
        ("F2", ["F2"]),
        ("F4", ["F4"]),
        ("F6", ["F6"]),
        ("F8", ["F8"]),
        ("FT7", ["FT7"]),
        ("FT8", ["FT8"]),
        ("T7", ["T7"]),
        ("T8", ["T8"]),
        ("TP7", ["TP7"]),
        ("TP8", ["TP8"]),
        ("P7", ["P7"]),
        ("P5", ["P5"]),
        ("P3", ["P3"]),
        ("P1", ["P1"]),
        ("Pz", ["Pz"]),
        ("P2", ["P2"]),
        ("P4", ["P4"]),
        ("P6", ["P6"]),
        ("P8", ["P8"]),
        ("PO7", ["PO7"]),
        ("PO3", ["PO3"]),
        ("POz", ["POz"]),
        ("PO4", ["PO4"]),
        ("PO8", ["PO8"]),
        ("O1", ["O1"]),
        ("Oz", ["Oz"]),
        ("O2", ["O2"]),
        ("FC5", ["FC5"]),
        ("FC3", ["FC3"]),
        ("FC1", ["FC1"]),
        ("FCz", ["FCz"]),
        ("FC2", ["FC2"]),
        ("FC4", ["FC4"]),
        ("FC6", ["FC6"]),
        ("C5", ["C5"]),
        ("C3", ["C3"]),
        ("C1", ["C1"]),
        ("Cz", ["Cz"]),
        ("C2", ["C2"]),
        ("C4", ["C4"]),
        ("C6", ["C6"]),
        ("CP5", ["CP5"]),
        ("CP3", ["CP3"]),
        ("CP1", ["CP1"]),
        ("CPz", ["CPz"]),
        ("CP2", ["CP2"]),
        ("CP4", ["CP4"]),
        ("CP6", ["CP6"]),
    ]

    for target_name, aliases in alias_groups:
        for src in aliases:
            if src in existing_names and src != target_name:
                rename_map[src] = target_name
                break

    return rename_map


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name."""
    file_name = os.path.basename(file_path).lower()

    if "resting" in file_name:
        return "resting"
    elif "contrast" in file_name:
        return "contrast"
    elif "movie" in file_name or "video" in file_name:
        return "video"
    elif "symbol" in file_name:
        return "symbol"
    elif "sequence" in file_name:
        return "sequence"
    elif "surround" in file_name:
        return "surround"
    else:
        return "unknown"


def _extract_subject_info(udataset, row) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv."""
    subject_id = row.get("participant_id", "") if isinstance(row, dict) else getattr(row, "participant_id", "")
    dataset_path = getattr(udataset, "path", "")
    participants_tsv = os.path.join(dataset_path, "participants.tsv")

    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "cap": "BioSemi 128-channel",
        "amplifier": "BioSemi ActiveTwo",
    }

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
            if subject_col in df.columns:
                match_id = subject_id if subject_id.startswith("sub-") else f"sub-{subject_id}"
                row_data = df[df[subject_col] == match_id]
                if len(row_data) > 0:
                    if "age" in row_data.columns:
                        age_val = row_data["age"].values[0]
                        if pd.notna(age_val):
                            subject_info["age"] = str(int(float(age_val)))
                    if "sex" in row_data.columns:
                        sex_val = row_data["sex"].values[0]
                        if pd.notna(sex_val):
                            sex_lower = str(sex_val).lower().strip()
                            if sex_lower in ["m", "male"]:
                                subject_info["sex"] = "male"
                            elif sex_lower in ["f", "female"]:
                                subject_info["sex"] = "female"
                    if "handedness" in row_data.columns:
                        hand_val = row_data["handedness"].values[0]
                        if pd.notna(hand_val):
                            hand_lower = str(hand_val).lower().strip()
                            if hand_lower in ["r", "right", "right-handed"]:
                                subject_info["handedness"] = "right"
                            elif hand_lower in ["l", "left", "left-handed"]:
                                subject_info["handedness"] = "left"
                            elif hand_lower in ["a", "ambidextrous"]:
                                subject_info["handedness"] = "ambidextrous"
        except Exception:
            pass

    return subject_info


class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro ds005505 (HBN EEG Release 1)."""
    
    KERNEL_ID = "openneuro_ds005505"
    
    eegunity_description = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
        "cap": "BioSemi 128-channel",
        "amplifier": "BioSemi ActiveTwo",
    }
    
    def apply(self, udataset, raw, row):
        subject_info = _extract_subject_info(udataset, row)
        self.eegunity_description.update(subject_info)
        
        file_path = getattr(row, "file_path", "") if hasattr(row, "file_path") else str(row)
        paradigm = _detect_paradigm(file_path)
        
        rename_map = _build_biosemi_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        return raw


KERNEL = EEGUnityKernel()