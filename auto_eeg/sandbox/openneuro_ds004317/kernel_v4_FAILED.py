"""openneuro_ds004317 stage1 kernel for EEGUnity.

Mood Manipulation and PST, Experiment 2.
Reinforcement learning task (Probabilistic Selection Task) with sad/happy mood induction.

Source: https://openneuro.org/datasets/ds004317
Paper: DOI 10.1111/psyp.14276

Dataset Overview:
- 50 subjects, 66 channels, 500 Hz
- BIDS format (EEG .vhdr/.eeg/.vmk files)
- Missing subject metadata (age/sex) → fill with "unknown"

Event Mapping (from BIDS events.tsv, verified via kernel code):
- S1-S9   → STIM    (stimulus onset)
- S10     → FB      (feedback onset)
- S12-S16 → RESP    (button-press response)
- S101    → Correct (correct feedback / positive outcome)
- S102    → Incorrect (incorrect feedback / negative outcome)
- S91     → admin: marker-91  (system status marker, no paradigm prefix)
- S92     → admin: marker-92
- S99     → admin: marker-99
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


# ----------------------------------------------------------------------
# Event / Annotation Mapping
# ----------------------------------------------------------------------
# BIDS events.tsv 'value' column contains numeric codes (S101, S102, etc.)
# Annotator: Human, based on events.tsv inspection and paper DOI 10.1111/psyp.14276
# Date: 2026-04-08
_NUMERIC_TO_LABEL: Dict[str, str] = {
    "S1":   "STIM",
    "S2":   "STIM",
    "S3":   "STIM",
    "S4":   "STIM",
    "S5":   "STIM",
    "S6":   "STIM",
    "S7":   "STIM",
    "S8":   "STIM",
    "S9":   "STIM",
    "S10":  "FB",
    "S12":  "RESP",
    "S13":  "RESP",
    "S14":  "RESP",
    "S15":  "RESP",
    "S16":  "RESP",
    "S101": "Correct",
    "S102": "Incorrect",
    "S91":  "admin: marker-91",
    "S92":  "admin: marker-92",
    "S99":  "admin: marker-99",
}

# Task epoch events (raw meta level)
_TASK_EVENTS = {"Correct", "Incorrect", "STIM", "RESP", "FB"}

# Canonical event ID for annotation parsing
_EVENT_ID = {v: i for i, v in enumerate(_NUMERIC_TO_LABEL.values())}
_CANONICAL_EVENT_ID: Dict[str, int] = {
    "STIM":       1,
    "FB":         2,
    "RESP":       3,
    "Correct":    4,
    "Incorrect":  5,
    "admin: marker-91": 91,
    "admin: marker-92": 92,
    "admin: marker-99": 99,
}


# ----------------------------------------------------------------------
# Device / Subject Metadata
# ----------------------------------------------------------------------
# Source: Dataset README / paper DOI 10.1111/psyp.14276
# Amplifier and cap info inferred from Brain Products system common in EEG labs.
# Annotator: LLM, needs human verification
_DEVICE_AMPLIFIER = "unknown"       # LLM 推断，需人类复核
_DEVICE_CAP       = "unknown"       # LLM 推断，需人类复核

# subject_age / subject_sex are MISSING in participants.tsv (confirmed via analysis.md)
# All subjects default to "unknown"
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Populate unknown for all 50 subjects
for i in range(1, 51):
    subj_id = f"sub-{i:02d}"
    _SUBJECT_DICT[subj_id] = {
        "age":       "unknown",
        "sex":       "unknown",
        "handedness": "unknown",
        "amplifier": _DEVICE_AMPLIFIER,
        "cap":       _DEVICE_CAP,
    }
# Source: analysis.md confirms subject_age and subject_sex are missing
# Annotator: Human, 2026-04-08


# ----------------------------------------------------------------------
# Channel Name Mapping
# ----------------------------------------------------------------------
# 66-channel system; standard_1020 names expected.
# BIDS sidecar may already use standard names; apply conservative rename.
# Source: standard_1020 montage, Brain Products cap layout
# Annotator: Human, 2026-04-08
_STANDARD_1020_66 = {
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
    "F9",  "F7",  "F5",  "F3",  "F1",  "Fz",  "F2",  "F4",  "F6",  "F8",  "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9",  "T7",  "T5",  "T3",  "T1",  "Cz",  "T2",  "T4",  "T6",  "T8",  "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9",  "P7",  "P5",  "P3",  "P1",  "Pz",  "P2",  "P4",  "P6",  "P8",  "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1",  "Oz",  "O2",
    "I1",  "Iz",  "I2",
    # common auxiliary
    "M1",  "M2",
    "N",   "RF",
}

# Common Brain Products alias → standard name
# These are the most likely aliases present in BrainVision .vhdr files
_BP_ALIAS_MAP: Dict[str, List[str]] = {
    "Fp1": ["Fp1", "fp1"],
    "Fpz": ["Fpz", "fpz"],
    "Fp2": ["Fp2", "fp2"],
    "F7":  ["F7",  "F 7"],
    "F3":  ["F3",  "F 3"],
    "Fz":  ["Fz",  "Fz "],
    "F4":  ["F4",  "F 4"],
    "F8":  ["F8",  "F 8"],
    "T7":  ["T7",  "T 7"],
    "C3":  ["C3",  "C 3"],
    "Cz":  ["Cz",  "Cz "],
    "C4":  ["C4",  "C 4"],
    "T8":  ["T8",  "T 8"],
    "P7":  ["P7",  "P 7"],
    "P3":  ["P3",  "P 3"],
    "Pz":  ["Pz",  "Pz "],
    "P4":  ["P4",  "P 4"],
    "P8":  ["P8",  "P 8"],
    "O1":  ["O1",  "O 1"],
    "Oz":  ["Oz",  "Oz "],
    "O2":  ["O2",  "O 2"],
    "M1":  ["M1",  "A1"],
    "M2":  ["M2",  "A2"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a conservative rename map from raw channel names to standard names.

    Only renames channels that are clearly misnamed but match a known alias.
    Does not rename already-correct standard names.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    used_targets: set[str] = set()

    for target, aliases in _BP_ALIAS_MAP.items():
        if target in used_targets:
            continue
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                used_targets.add(target)
                break

    return rename_map


def _load_events_from_bids(eeg_file: str) -> Tuple[np.ndarray, Dict[str, int]]:
    """Load events.tsv companion file and convert to MNE events array.

    Parameters
    ----------
    eeg_file : str
        Path to the EEG file (.vhdr, .eeg, .bdf, etc.)

    Returns
    -------
    events : np.ndarray
        Shape (n_events, 3): [sample, 0, event_id]
    event_id : dict
        Mapping from label -> integer event code
    """
    base = os.path.splitext(eeg_file)[0]
    # Try common BIDS events.tsv naming
    for events_file in [
        base + "_events.tsv",
        os.path.join(os.path.dirname(eeg_file), os.path.basename(base) + "_events.tsv"),
    ]:
        if os.path.exists(events_file):
            break
    else:
        # Fallback: no events file found
        return np.empty((0, 3), dtype=int), _CANONICAL_EVENT_ID

    df = pd.read_csv(events_file, sep="\t")

    # Standard BIDS events columns: onset, duration, trial_type / value
    # value column contains the numeric code (S101, S102, etc.)
    onset_col = "onset" if "onset" in df.columns else df.columns[0]
    value_col = "value" if "value" in df.columns else None
    dur_col = "duration" if "duration" in df.columns else None

    events_list = []
    labels_list = []

    for _, row in df.iterrows():
        onset_s = float(row[onset_col])
        if dur_col and dur_col in row.index:
            duration = float(row[dur_col]) if pd.notna(row[dur_col]) else 0.0
        else:
            duration = 0.0

        if value_col and value_col in row.index:
            raw_val = str(row[value_col])
        else:
            raw_val = str(row.get("trial_type", "unknown"))

        # Map numeric value to label
        label = _NUMERIC_TO_LABEL.get(raw_val, raw_val)
        event_id = _CANONICAL_EVENT_ID.get(label, 0)
        if event_id == 0:
            event_id = 999  # unknown

        events_list.append([onset_s, int(duration * 1000), event_id])
        labels_list.append(label)

    if not events_list:
        return np.empty((0, 3), dtype=int), _CANONICAL_EVENT_ID

    events = np.array(events_list, dtype=int)
    return events, _CANONICAL_EVENT_ID


# ----------------------------------------------------------------------
# Kernel Definition
# ----------------------------------------------------------------------
@dataclass
class KernelResult:
    raw: mne.io.BaseRaw
    description: Dict[str, Any]
    annotations: List[Dict[str, Any]]


class Kernel:
    """EEGUnity kernel for openneuro_ds004317 dataset."""

    def __init__(self):
        self.name = "openneuro_ds004317"
        self.version = "3.0.0"

    def _get_eeg_description(self, subject_id: str) -> Dict[str, Any]:
        """Return standardized EEG description dict for subject."""
        meta = _SUBJECT_DICT.get(subject_id, {})
        return {
            "age": str(meta.get("age", "unknown")),
            "sex": str(meta.get("sex", "unknown")),
            "amplifier": str(meta.get("amplifier", "unknown")),
            "cap": str(meta.get("cap", "unknown")),
            "handedness": str(meta.get("handedness", "unknown")),
        }

    def _extract_subject_id(self, row: Dict[str, Any]) -> str:
        """Extract subject ID from row dict."""
        # Try common column names
        for col in ["subject", "participant_id", "subj_id", "subject_id"]:
            if col in row and row[col]:
                val = str(row[col])
                if not val.startswith("sub-"):
                    val = f"sub-{val}"
                return val
        # Try to infer from file path
        if "file_path" in row:
            match = re.search(r"sub-\d+", str(row["file_path"]))
            if match:
                return match.group(0)
        return "sub-01"

    def _extract_task_info(self, row: Dict[str, Any]) -> Dict[str, str]:
        """Extract task-specific info from row."""
        info = {"task": "PST", "run": "1"}
        if "task" in row:
            info["task"] = str(row["task"])
        if "run" in row:
            info["run"] = str(row["run"])
        return info

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Determine subject info
        subject_id = self._extract_subject_id(row)
        eeg_description = self._get_eeg_description(subject_id)

        # Apply channel rename (conservative, avoid duplicates)
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Ensure channel types are set correctly (EEG)
        eeg_channels = [ch for ch in raw.ch_names if ch not in ["M1", "M2", "N", "RF"]]
        if eeg_channels:
            raw.set_channel_types({ch: "eeg" for ch in eeg_channels if ch in raw.ch_names})

        # Set reference (average by default)
        if "M1" in raw.ch_names and "M2" in raw.ch_names:
            raw = raw.set_eeg_reference(ref_channels=["M1", "M2"])
        elif "M1" in raw.ch_names:
            raw = raw.set_eeg_reference(ref_channels=["M1"])
        elif "M2" in raw.ch_names:
            raw = raw.set_eeg_reference(ref_channels=["M2"])
        else:
            raw = raw.set_eeg_reference(ref_channels="average")

        # Load events from BIDS events.tsv if available
        file_path = row.get("file_path", "")
        if file_path and os.path.exists(file_path):
            events, event_id = _load_events_from_bids(file_path)
            if len(events) > 0:
                # Add events as annotations
                annotations = mne.Annotations(
                    onset=events[:, 0] / raw.info["sfreq"],
                    duration=np.zeros(len(events)),
                    description=[list(event_id.keys())[list(event_id.values()).index(e)] for e in events[:, 2]],
                    orig_time=None,
                )
                raw = raw.set_annotations(annotations)

        return raw


# ----------------------------------------------------------------------
# Kernel Export
# ----------------------------------------------------------------------
KERNEL = Kernel()