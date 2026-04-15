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
                break  # only map one source per target to avoid duplicates

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

    # Convert to numpy array; shape (n_events, 3)
    events = np.array(events_list, dtype=int)
    # events[:,0] is onset in seconds, events[:,1] duration in ms, events[:,2] event_id
    return events, _CANONICAL_EVENT_ID


def _annotate_raw(raw: mne.io.BaseRaw, events: np.ndarray, event_id: Dict[str, int]) -> mne.io.BaseRaw:
    """Add annotations to raw based on events array.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object.
    events : np.ndarray
        Events array, shape (n_events, 3). First column is onset in seconds.
    event_id : dict
        Mapping from label to integer event code.

    Returns
    -------
    raw : mne.io.BaseRaw
        Raw object with added annotations.
    """
    # Invert event_id to get label from event code
    id_to_label = {v: k for k, v in event_id.items()}

    for event in events:
        onset_s = float(event[0])
        duration_s = float(event[1]) / 1000.0  # convert ms to s
        event_code = int(event[2])
        label = id_to_label.get(event_code, f"unknown_{event_code}")
        annot = mne.Annotations(
            onset=[onset_s],
            duration=[duration_s],
            description=[label],
            ch_names=None,
        )
        raw.set_annotations(annot, on_missing="ignore")
    return raw


class EEGUnityKernel:
    def __init__(self):
        self.eegunity_description = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to a single subject raw EEG file.

        Parameters
        ----------
        udataset : object
            Dataset object (unused, can be None).
        raw : mne.io.BaseRaw
            Raw EEG object.
        row : dict
            Row from dataset index containing file path etc.

        Returns
        -------
        raw : mne.io.BaseRaw
            Processed raw object.
        """
        # ------------------------------------------------------------------
        # 1. Rename channels to standard names if needed
        # ------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Check for duplicate target names before renaming
            target_counts: Dict[str, int] = {}
            for src, tgt in rename_map.items():
                target_counts[tgt] = target_counts.get(tgt, 0) + 1
            # Remove any mappings that would cause duplicates
            safe_rename_map = {}
            for src, tgt in rename_map.items():
                if target_counts[tgt] > 1:
                    # Skip this mapping to avoid duplicate target name
                    continue
                safe_rename_map[src] = tgt
            if safe_rename_map:
                mne.rename_channels(raw.info, safe_rename_map)

        # ------------------------------------------------------------------
        # 2. Load events from BIDS events.tsv if available
        # ------------------------------------------------------------------
        # Determine EEG file path from row
        eeg_file = row.get("filepath", None)
        if eeg_file is None:
            # fallback: try to get filename from raw
            eeg_file = raw.filenames[0] if raw.filenames else None

        if eeg_file is not None:
            events, ev_id = _load_events_from_bids(str(eeg_file))
            if events.size > 0:
                # Convert onset in seconds to samples based on raw.info['sfreq']
                sfreq = raw.info["sfreq"]
                events[:, 0] = (events[:, 0] * sfreq).astype(int)
                # Annotate raw
                raw = _annotate_raw(raw, events, ev_id)

        # ------------------------------------------------------------------
        # 3. Set channel types if needed (e.g., auxiliary channels)
        # ------------------------------------------------------------------
        # Ensure common auxiliary channels are set correctly
        for ch in ["M1", "M2", "N", "RF"]:
            if ch in raw.ch_names:
                if ch in ["M1", "M2"]:
                    raw.set_channel_types({ch: "misc"})
                else:
                    raw.set_channel_types({ch: "misc"})

        # ------------------------------------------------------------------
        # 4. Set reference to average (common average reference)
        # ------------------------------------------------------------------
        # Only if there are no active reference channel present
        # If a reference channel is present (e.g., M1/M2), we could drop them
        # or keep them. Here we set to average reference.
        # Note: For some datasets, you may want to keep reference as is.
        # We choose to re-reference to average for consistency.
        # However, avoid re-referencing if raw is already average referenced.
        # We'll apply average reference, but ignore warnings.
        try:
            raw.set_eeg_reference(ref_channels="average")
        except Exception:
            # If fails, ignore (maybe no channels)
            pass

        # ------------------------------------------------------------------
        # 5. Ensure channel locations (montage) if possible
        # ------------------------------------------------------------------
        # Try to set standard 1020 montage if not already present
        if raw.info["dig"] is None or len(raw.info["dig"]) == 0:
            # No digitization points, try to set montage from known channels
            # Use standard 1020 montage if enough channels match
            ch_names = raw.ch_names
            # Check how many standard names are present
            std_names_present = [c for c in ch_names if c in _STANDARD_1020_66]
            if len(std_names_present) >= 20:  # arbitrary threshold
                try:
                    montage = mne.channels.make_standard_montage("standard_1020")
                    raw.set_montage(montage, on_missing="ignore")
                except Exception:
                    # If fails, ignore
                    pass

        # ------------------------------------------------------------------
        # 6. Additional metadata: store subject info in raw.info['subject_info']
        # ------------------------------------------------------------------
        # Determine subject ID from row or filename
        subject_id = row.get("subject_id", None)
        if subject_id is None:
            # Try to infer from filename
            fname = os.path.basename(eeg_file) if eeg_file else ""
            m = re.search(r"sub-(\d+)", fname)
            if m:
                subject_id = f"sub-{int(m.group(1)):02d}"
            else:
                subject_id = "sub-00"
        raw.info["subject_info"] = {
            "his_id": subject_id,
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        # ------------------------------------------------------------------
        # 7. Return processed raw
        # ------------------------------------------------------------------
        return raw


KERNEL = EEGUnityKernel()