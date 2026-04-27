"""Dataset-specific kernel for openneuro_ds006171.

EEG during near-threshold visual detection tasks (no-cue, 50%-cue, 100%-cue).
BioSemi BDF format with 144 channels, 1024 Hz sampling rate.

Source: https://openneuro.org/datasets/ds006171
DOI: https://doi.org/10.18112/openneuro.ds006171.v1.0.0
Paper: https://doi.org/10.1111/psyp.14525

Event Structure (verified from analysis.md):
  1    = trial_start
  2    = response (detection report)
  11   = No-cue condition, stimulus A (epoch align reference)
  12   = No-cue condition, stimulus B (epoch align reference)
  21   = 50%-validity cue condition, stimulus A (epoch align reference)
  22   = 50%-validity cue condition, stimulus B (epoch align reference)
  101  = No-cue - hit
  103  = No-cue - false alarm
  104  = No-cue - correct rejection
  111  = 50%-validity cue - hit
  121  = 50%-validity cue - miss
  122  = 50%-validity cue - miss (duplicate code)
  124  = 100%-validity cue - false alarm
  125  = 100%-validity cue - correct rejection
  128  = BioSemi boundary marker (admin; exclude)

Behavioral columns in events.tsv: gabor_contrast, subjective_r, objective_r, response_time
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

_HARDWARE_METADATA = {
    "amplifier": "BioSemi ActiveTwo",
    "cap": "Ag/AgCl",
}

# =============================================================================
# Channel Name Mapping
# =============================================================================
_EEG_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    "AF11", "AF12", "F11", "F12", "FT11", "FT12", "T11", "T12",
    "TP11", "TP12", "P11", "P12", "PO11", "PO12",
    "EOG1", "EOG2", "EOG3", "EOG4",
    "ECG1", "ECG2",
    "EMG1", "EMG2",
    "Resp1", "Resp2",
    "Trigger", "Status",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for BioSemi BDF channels to standard names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for i, ch_name in enumerate(existing_names, start=1):
        if ch_name.startswith("A") and ch_name[1:].isdigit():
            idx = int(ch_name[1:]) - 1
            if idx < len(_EEG_CHANNEL_NAMES):
                rename_map[ch_name] = _EEG_CHANNEL_NAMES[idx]

    return rename_map


# =============================================================================
# Event ID Mapping
# =============================================================================
_EVENT_MAP: Dict[str, int] = {
    "trial_start": 1,
    "response": 2,
    "nocue_stim_A": 11,
    "nocue_stim_B": 12,
    "nocue_hit": 101,
    "nocue_FA": 103,
    "nocue_CR": 104,
    "50pct_stim_A": 21,
    "50pct_stim_B": 22,
    "50pct_hit": 111,
    "50pct_miss_1": 121,
    "50pct_miss_2": 122,
    "100pct_FA": 124,
    "100pct_CR": 125,
    "boundary": 128,
}

_EVENT_ID_TO_NAME: Dict[int, str] = {v: k for k, v in _EVENT_MAP.items()}


# =============================================================================
# Kernel Class
# =============================================================================
class OpenNeuroDS006171Kernel:
    """Stage1 kernel for OpenNeuro ds006171 dataset."""

    KERNEL_ID: str = "openneuro-ds006171-stage1"

    def _load_subject_info(self, udataset, subject_id: str) -> Dict[str, Any]:
        """Load subject metadata from participants.tsv."""
        subject_info: Dict[str, Any] = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }
        
        try:
            participants_path = os.path.join(udataset.dataset_path, "participants.tsv")
            if os.path.exists(participants_path):
                participants_df = pd.read_csv(participants_path, sep="\t")
                subject_row = participants_df[participants_df["participant_id"] == subject_id]
                if not subject_row.empty:
                    row = subject_row.iloc[0]
                    subject_info["age"] = str(row.get("age", "unknown"))
                    subject_info["sex"] = str(row.get("sex", "unknown"))
                    subject_info["handedness"] = str(row.get("handedness", "unknown"))
        except Exception:
            pass
        
        return subject_info

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record."""
        file_path = row["File Path"]
        subject_id = row.get("subject_id", "unknown")
        original_desc = raw.info.get("description", "")

        # Load subject metadata
        subject_info = self._load_subject_info(udataset, subject_id)

        # Update raw.info["description"]
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": _HARDWARE_METADATA.get("amplifier", "unknown"),
                "cap": _HARDWARE_METADATA.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            valid_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if valid_renames:
                raw.rename_channels(valid_renames)

        # Set montage
        try:
            montage = mne.channels.make_standard_montage("standard_1005")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS006171Kernel()