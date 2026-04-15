"""OpenNeuro ds003638 stage1 kernel for EEGUnity.

Dataset: EEG Electrophysiological Biomarkers of Behavioral Dimensions from Cross-Species Paradigms
Source: https://openneuro.org/datasets/ds003638
Reference: DOI 10.1038/s41398-021-01562-w

57 subjects, 73 channels, 512 Hz. Three paradigms: 5CCPT, PRBP, PST.
Channel names use BrainVision convention with numeric suffixes.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Standard 10-20 73-channel layout for BrainCap/Montage72
# Source: Paper 10.1038/s41398-021-01562-w supplementary / standard 10-20 extended
# Annotator: LLM 推断，需人类复核
_STANDARD_1020_EXTENDED = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF6", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    "T1", "T2",
]

# BrainVision channel name mapping (e.g., "EEG 001" -> "Fp1")
# Source: Standard BrainVision 64ch cap naming convention
# Annotator: LLM 推断，需人类复核
_BRAINVISION_CHANNEL_MAP: Dict[str, str] = {}


def _build_brainvision_channel_map(n_channels: int) -> Dict[str, str]:
    """Build BrainVision EEG channel to standard 10-20 name mapping."""
    mapping = {}
    # Standard 73-channel order for BrainCap72
    standard_73 = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF6", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
    ]
    for i, std_name in enumerate(standard_73[:n_channels]):
        brainvision_name = f"EEG {i+1:03d}"
        mapping[brainvision_name] = std_name
    return mapping


# 5CCPT event code mapping: code -> label
# Source: Paper 10.1038/s41398-021-01562-w / events.tsv
# Annotator: LLM 推断，需人类复核
_5CCPT_CODE_MAP = {
    1: "5CCPT: correct rejection 1",
    2: "5CCPT: correct rejection 2",
    3: "5CCPT: correct rejection 3",
    4: "5CCPT: correct rejection 4",
    5: "5CCPT: correct rejection 5",
    6: "5CCPT: stimulus 6",
    7: "5CCPT: stimulus 7",
    8: "5CCPT: stimulus 8",
    9: "5CCPT: stimulus 9",
    10: "5CCPT: stimulus 10",
    11: "5CCPT: stimulus 11",
    12: "5CCPT: stimulus 12",
    13: "5CCPT: stimulus 13",
    14: "5CCPT: stimulus 14",
    15: "5CCPT: stimulus 15",
    16: "5CCPT: stimulus 16",
    17: "5CCPT: stimulus 17",
    18: "5CCPT: stimulus 18",
    19: "5CCPT: stimulus 19",
    20: "5CCPT: stimulus 20",
    21: "5CCPT: stimulus 21",
    22: "5CCPT: stimulus 22",
    23: "5CCPT: stimulus 23",
    24: "5CCPT: stimulus 24",
    25: "5CCPT: stimulus 25",
    26: "5CCPT: stimulus 26",
    27: "5CCPT: stimulus 27",
    28: "5CCPT: stimulus 28",
    29: "5CCPT: stimulus 29",
    30: "5CCPT: stimulus 30",
    31: "5CCPT: stimulus 31",
    32: "5CCPT: stimulus 32",
    33: "5CCPT: stimulus 33",
    34: "5CCPT: stimulus 34",
    35: "5CCPT: stimulus 35",
    36: "5CCPT: stimulus 36",
    37: "5CCPT: stimulus 37",
    38: "5CCPT: stimulus 38",
    39: "5CCPT: stimulus 39",
    40: "5CCPT: correct rejection 40",
    41: "5CCPT: target hit 41",
    42: "5CCPT: target hit 42",
    43: "5CCPT: target hit 43",
    44: "5CCPT: target hit 44",
    45: "5CCPT: target hit 45",
    46: "5CCPT: target hit 46",
    47: "5CCPT: target hit 47",
    48: "5CCPT: target hit 48",
    49: "5CCPT: target hit 49",
    50: "5CCPT: target hit 50",
    51: "5CCPT: target hit 51",
    52: "5CCPT: target hit 52",
    53: "5CCPT: target hit 53",
    54: "5CCPT: target hit 54",
    55: "5CCPT: target hit 55",
    56: "5CCPT: target hit 56",
    57: "5CCPT: target hit 57",
    58: "5CCPT: target hit 58",
    59: "5CCPT: target hit 59",
    60: "5CCPT: target hit 60",
    61: "5CCPT: target hit 61",
    62: "5CCPT: target hit 62",
    63: "5CCPT: target hit 63",
    64: "5CCPT: target hit 64",
    65: "5CCPT: target hit 65",
    66: "5CCPT: target hit 66",
    67: "5CCPT: target hit 67",
    68: "5CCPT: target hit 68",
    69: "5CCPT: target hit 69",
    70: "5CCPT: target hit 70",
    71: "5CCPT: target hit 71",
    72: "5CCPT: target hit 72",
    73: "5CCPT: target hit 73",
    74: "5CCPT: target hit 74",
    75: "5CCPT: target hit 75",
    76: "5CCPT: target hit 76",
    77: "5CCPT: target hit 77",
    78: "5CCPT: target hit 78",
    79: "5CCPT: target hit 79",
    80: "5CCPT: target hit 80",
}

# PRBP event code mapping
# Source: Paper 10.1038/s41398-021-01562-w / events.tsv
# Annotator: LLM 推断，需人类复核
_PRBP_CODE_MAP = {
    116: "PRBP: high probability",
    117: "PRBP: low probability",
}

# PST event code mapping
# Source: Paper 10.1038/s41398-021-01562-w / events.tsv
# Annotator: LLM 推断，需人类复核
_PST_CODE_MAP = {
    31: "PST: cue 31",
    32: "PST: cue 32",
    39: "PST: cue 39",
}

# Admin codes (no paradigm prefix per rulebook)
_ADMIN_CODE_MAP = {
    91: "admin: marker-91",
    92: "admin: marker-92",
    99: "admin: marker-99",
}

# Combined event mapping
_ALL_CODE_MAPS = {**_5CCPT_CODE_MAP, **_PRBP_CODE_MAP, **_PST_CODE_MAP, **_ADMIN_CODE_MAP}


def _detect_paradigm_from_filename(file_path: str) -> str:
    """Detect paradigm from file path prefix."""
    basename = os.path.basename(file_path).lower()
    if "5ccpt" in basename or "5c-cpt" in basename:
        return "5CCPT"
    elif "prbp" in basename or "prp" in basename:
        return "PRBP"
    elif "pst" in basename:
        return "PST"
    return "unknown"


def _map_status_event(status_value: int) -> str:
    """Map STATUS channel value to human-readable label."""
    if status_value in _ALL_CODE_MAPS:
        return _ALL_CODE_MAPS[status_value]
    elif status_value == 1:
        return "5CCPT: start marker"
    elif status_value in (116, 117):
        return _PRBP_CODE_MAP.get(status_value, f"PRBP: code-{status_value}")
    elif status_value in (31, 32, 39):
        return _PST_CODE_MAP.get(status_value, f"PST: code-{status_value}")
    elif status_value == 65280:
        return "admin: experiment start"
    elif status_value == 65281:
        return "admin: block start"
    elif status_value == 65282:
        return "admin: trial start"
    elif status_value == 65389:
        return "admin: block end"
    elif 65281 <= status_value <= 65324:
        return f"5CCPT: event-{status_value}"
    else:
        return f"unknown: {status_value}"


def _create_annotations_from_status_channel(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract events from STATUS channel and create annotations."""
    status_ch_names = [ch for ch in raw.ch_names if "status" in ch.lower()]
    
    if not status_ch_names:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    status_data, times = raw.get_data(return_times=True)
    if status_data.ndim > 1:
        status_data = status_data[0]
    
    sfreq = raw.info["sfreq"]
    
    # Find transitions (rising edges)
    diff = np.diff(status_data.astype(int), prepend=0)
    
    onset_indices = np.where(diff != 0)[0]
    
    annotations_list = []
    onset_list = []
    
    for idx in onset_indices:
        value = int(status_data[idx])
        if value > 0:
            label = _map_status_event(value)
            annotations_list.append(label)
            onset_list.append(times[idx])
    
    durations = [0.0] * len(onset_list)
    
    return mne.Annotations(
        onset=onset_list,
        duration=durations,
        description=annotations_list,
    )


class OpenNeuroDS003638Kernel:
    """Stage1 kernel for OpenNeuro ds003638 dataset."""

    KERNEL_ID: str = "openneuro-ds003638-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : pandas.Series
            Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with standardized channels and annotations.
        """
        file_path = row.get("File Path", "")

        # 1. Build channel rename map based on actual channel count
        n_eeg_channels = len([ch for ch in raw.ch_names if ch.startswith("EEG")])
        if n_eeg_channels > 0:
            channel_map = _build_brainvision_channel_map(n_eeg_channels)
            
            # Apply channel renames
            rename_dict = {}
            for old_name in raw.ch_names:
                if old_name in channel_map:
                    rename_dict[old_name] = channel_map[old_name]
            
            if rename_dict:
                raw.rename_channels(rename_dict)

        # 2. Set standard 10-20 montage AFTER renaming
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for EEG channels that exist in standard montage
            eeg_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if eeg_channels:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if standard montage fails

        # 3. Create annotations from STATUS channel
        annotations = _create_annotations_from_status_channel(raw)
        raw.set_annotations(annotations)

        # 4. Set eegunity_description in raw.info["description"]
        original_desc = raw.info.get("description", "") or ""

        # Extract subject info from row if available
        subject_id = row.get("Subject", row.get("subject_id", "unknown"))
        age = row.get("age", "unknown")
        sex = row.get("sex", "unknown")
        handedness = row.get("handedness", "unknown")

        # Ensure proper types
        if not isinstance(age, str):
            age = str(age) if age else "unknown"
        if sex:
            sex = str(sex).lower()
            if sex not in ("male", "female", "unknown"):
                sex = "unknown"
        else:
            sex = "unknown"
        if handedness:
            handedness = str(handedness).lower()
            if handedness not in ("right", "left", "unknown"):
                handedness = "unknown"
        else:
            handedness = "unknown"

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "BrainAmp",  # Source: Paper methodology
                "cap": "BrainCap 72ch (Ag/AgCl)",  # Source: LLM 推断，需人类复核
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003638Kernel()