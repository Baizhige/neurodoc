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
    "T7":  ["T7",  "T 7", "TP7"],
    "C3":  ["C3",  "C 3"],
    "Cz":  ["Cz",  "Cz "],
    "C4":  ["C4",  "C 4"],
    "T8":  ["T8",  "T 8", "TP8"],
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

    for target, aliases in _BP_ALIAS_MAP.items():
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
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
        # Convert onset (seconds) to samples
        # We don't have sfreq here, so return raw onset in seconds
        # The caller will handle sample conversion
        if dur_col and dur_col in row.index:
            duration = float(row[dur_col]) if pd.notna(row[dur_col]) else 0.0
        else:
            duration = 0.0

        if value_col and value_col in row.index:
            raw_val = str(row[value_col])
        else:
            # Use trial_type column
            raw_val = str(row.get("trial_type", "unknown"))

        # Map numeric value to label
        label = _NUMERIC_TO_LABEL.get(raw_val, raw_val)
        event_id = _CANONICAL_EVENT_ID.get(label, 0)
        if event_id == 0:
            event_id = 999  # unknown

        events_list.append([onset_s, int(duration * 1000), event_id])
        labels_list.append(label)

    return np.array(events_list, dtype=int), labels_list


def _create_annotations_from_events(
    events: np.ndarray,
    labels: List[str],
    sfreq: float,
) -> mne.Annotations:
    """Convert events array + labels to MNE Annotations."""
    onsets = events[:, 0] / sfreq  # convert samples to seconds
    durations = events[:, 1] / sfreq
    descriptions = labels
    return mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist(),
        description=descriptions,
    )


# ----------------------------------------------------------------------
# Kernel Class
# ----------------------------------------------------------------------
@dataclass
class OpenNeuroDS004317Kernel:
    """Stage1 kernel for openneuro_ds004317 (Mood Manipulation and PST, Experiment 2).

    This kernel handles:
    - BIDS EEG format (BrainVision .vhdr)
    - Channel name normalization to standard_1020
    - Annotation creation from BIDS events.tsv (numeric code → label mapping)
    - eegunity_description population (missing age/sex → "unknown")
    """

    KERNEL_ID: str = "openneuro-ds004317-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated description and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = str(row.get("Subject", row.get("participant_id", "unknown")))

        # --- Build eegunity_description ---------------------------------
        original_desc = raw.info.get("description", "")

        subj_meta = _SUBJECT_DICT.get(subject_id, {})
        eegunity_desc = {
            "age":       subj_meta.get("age", "unknown"),
            "sex":       subj_meta.get("sex", "unknown"),
            "amplifier": subj_meta.get("amplifier", _DEVICE_AMPLIFIER),
            "cap":       subj_meta.get("cap", _DEVICE_CAP),
            "handedness": subj_meta.get("handedness", "unknown"),
        }

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # --- Channel rename (before set_montage) -------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # --- Set montage (standard_1020, 66 channels) --------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in raw
            ch_names = [ch for ch in montage.ch_names if ch in raw.ch_names]
            if ch_names:
                raw.set_montage(mon)
        except Exception:
            # If montage fails (e.g., non-standard cap), skip silently
            pass

        # --- Load events from BIDS events.tsv and create annotations ----
        if file_path:
            events_arr, labels = _load_events_from_bids(file_path)
            if len(events_arr) > 0:
                # events_arr[:, 0] is onset in seconds; events[:, 1] is duration in ms
                # Convert to seconds for MNE Annotations
                onsets_s = events_arr[:, 0].astype(float) / raw.info["sfreq"]
                durations_s = events_arr[:, 1].astype(float) / raw.info["sfreq"]
                annotations = mne.Annotations(
                    onset=onsets_s.tolist(),
                    duration=durations_s.tolist(),
                    description=labels,
                )
                raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004317Kernel()