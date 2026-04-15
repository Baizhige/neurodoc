"""OpenNeuro ds005505 (HBN EEG Release 1) stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 1 - Large-scale multi-task developmental
battery collected from children and adolescents. Contains resting-state, movie watching,
contrast detection, and sequence learning paradigms.

Source: https://openneuro.org/datasets/ds005505
Reference: https://doi.org/10.1016/j.neuroimage.2020.117001
          https://doi.org/10.1101/2024.10.03.615261
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
# CHANNEL RENAME MAP - HBN EEG Release 1 uses BioSemi 128-channel system
# ============================================================================
_BIOSEMI_128_CHANNELS = [
    "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", "T7", "T8", "TP7", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
    "Fp2", "F6", "F4", "F2", "AF4", "AF8", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P6", "P4", "P2", "P8", "PO8", "PO4", "O2",
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
    "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32",
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
    "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32",
    "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21",
    "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16",
    "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32",
]

_NUMERIC_CHANNEL_MAP: Dict[str, str] = {}
for i, ch_name in enumerate(_BIOSEMI_128_CHANNELS, start=1):
    _NUMERIC_CHANNEL_MAP[str(i)] = ch_name

_ADDITIONAL_ALIASES = {
    "EOG-left": "EOG_L",
    "EOG-right": "EOG_R",
    "EOG-up": "EOG_U",
    "EOG-down": "EOG_D",
    "EOG_L": "EOG_L",
    "EOG_R": "EOG_R",
    "EOG_U": "EOG_U",
    "EOG_D": "EOG_D",
    "Status": "Status",
    "Resp": "Resp",
    "EMG": "EMG",
}


_EVENT_LABEL_MAP: Dict[int, str] = {
    1: "contrast:contrastTrial_start",
    2: "contrast:left_target",
    3: "contrast:right_target",
    4: "contrast:left_buttonPress",
    5: "contrast:right_buttonPress",
    6: "contrast:video_start",
    7: "contrast:video_stop",
    8: "contrast:contrastChangeB1_start",
    9: "contrast:contrastChangeB2_start",
    10: "contrast:contrastChangeB3_start",
    11: "resting:instructed_toOpenEyes",
    12: "resting:instructed_toCloseEyes",
    13: "resting:resting_start",
    20: "video_start",
    21: "video_stop",
    30: "seqLearning_start",
    31: "seqLearning_response",
    90: "admin: end_marker",
    91: "boundary",
    92: "break cnt",
    93: "admin: break_marker",
    100: "contrastTrial_start",
    101: "contrastChangeB2_start",
    102: "contrastChangeB3_start",
    110: "dot_no2_ON",
    111: "dot_no2_OFF",
    112: "dot_no3_ON",
    113: "dot_no7_OFF",
    120: "fixpoint_ON",
    121: "newPage",
    130: "resting:dot_no1_ON",
    131: "resting:dot_no1_OFF",
    132: "resting:dot_no2_ON",
    133: "resting:dot_no2_OFF",
    134: "resting:dot_no3_ON",
    135: "resting:dot_no3_OFF",
    136: "resting:dot_no4_ON",
    137: "resting:dot_no4_OFF",
    138: "resting:dot_no5_ON",
    139: "resting:dot_no5_OFF",
}


def _detect_paradigm(file_path: str) -> Optional[str]:
    file_name = os.path.basename(file_path).lower()
    if "contrast" in file_name:
        return "contrast"
    elif "resting" in file_name:
        return "resting"
    elif "movie" in file_name or "video" in file_name:
        return "movie"
    elif "seqlearning" in file_name or "seq_learning" in file_name:
        return "seqLearning"
    elif "surround" in file_name or "suppression" in file_name:
        return "surroundingSuppression"
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    for old_name in existing_names:
        if old_name in _NUMERIC_CHANNEL_MAP:
            new_name = _NUMERIC_CHANNEL_MAP[old_name]
            if old_name != new_name:
                rename_map[old_name] = new_name
    for old_name in existing_names:
        if old_name in _ADDITIONAL_ALIASES:
            new_name = _ADDITIONAL_ALIASES[old_name]
            if old_name != new_name:
                rename_map[old_name] = new_name
    return rename_map


def _remap_events_from_annotations(
    annotations: mne.Annotations,
    paradigm: Optional[str],
) -> mne.Annotations:
    new_descriptions: List[str] = []
    for desc in annotations.description:
        desc_lower = str(desc).lower().strip()
        if desc_lower.isdigit():
            code = int(desc_lower)
            if code in _EVENT_LABEL_MAP:
                new_descriptions.append(_EVENT_LABEL_MAP[code])
                continue
        if "stimulus" in desc_lower:
            new_descriptions.append(desc)
        else:
            new_descriptions.append(desc)
    if len(annotations) > 0:
        return annotations.copy().rename({i: d for i, d in enumerate(new_descriptions)}, in_place=True)
    return annotations


def _get_safe_field(row: Dict[str, Any], field: str, default: str = "unknown") -> str:
    """Safely extract a field from row dictionary, handling various cases."""
    value = row.get(field, None)
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip() if value.strip() else default
    return str(value)


class Kernel:
    def __init__(self):
        self.amplifier = "BioSemi 128-channel"
        self.cap = "BioSemi 128-channel cap"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        age = _get_safe_field(row, "age", "unknown")
        sex = _get_safe_field(row, "sex", "unknown")
        handedness = _get_safe_field(row, "handedness", "unknown")
        
        udataset['eegunity_description'] = {
            'age': age,
            'sex': sex,
            'amplifier': self.amplifier,
            'cap': self.cap,
            'handedness': handedness,
        }
        paradigm = _detect_paradigm(row.get("file_path", ""))
        if paradigm and len(raw.annotations) > 0:
            annot = raw.annotations.copy()
            annot.description[0] = f"paradigm:{paradigm}"
            raw.set_annotations(annot)
        elif paradigm:
            onset = raw.times[0] if len(raw.times) > 0 else 0.0
            desc = f"paradigm:{paradigm}"
            raw.set_annotations(mne.Annotations(onset=[onset], duration=[0.0], description=[desc]))
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        if len(raw.annotations) > 0:
            _remap_events_from_annotations(raw.annotations, paradigm)
        return raw


KERNEL = Kernel()