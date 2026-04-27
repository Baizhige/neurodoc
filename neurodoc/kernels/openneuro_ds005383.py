"""openneuro_ds005383 stage1 kernel for EEGUnity.

Dataset: TMNRED - A Chinese Language EEG Dataset for Fuzzy Semantic Target
Identification in Natural Reading Environments.

30 channels, 200 Hz, BIDS format. Subject metadata is missing in participants.tsv.
Binary semantic target classification uses event_31 (non-target) and event_32 (target).

Source: https://openneuro.org/datasets/ds005383
Paper: https://doi.org/10.1038/s41597-025-05036-2
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# Standard 10-20 channel names for 30-channel EEG cap (BioSemi compatible)
# Source: BioSemi 64-channel layout documentation, mapped to 30-channel subset
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
_30CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
]


def _build_30ch_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 30-channel BioSemi/standard layouts.

    Handles common naming patterns:
    - BioSemi: 'A1', 'A2', ..., 'A30' or 'EEG 001', 'EEG 002', ...
    - Numeric: '1', '2', ..., '30'
    - Standard: already correct names

    Returns
    -------
    dict
        Mapping from original names to standard 10-20 names.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: BioSemi 'A1', 'A2', etc. or 'A 1', 'A 2'
    import re
    for ch in existing:
        # Match 'A1', 'A2', ... or 'A 1', 'A 2'
        m = re.match(r'^A\s*(\d+)$', ch, re.IGNORECASE)
        if m:
            idx = int(m.group(1)) - 1  # 0-indexed
            if 0 <= idx < len(_30CHANNEL_STANDARD_NAMES):
                rename_map[ch] = _30CHANNEL_STANDARD_NAMES[idx]

    # Pattern 2: 'EEG 001', 'EEG 002', ... or 'EEG001', 'EEG002'
    if not rename_map:
        for ch in existing:
            m = re.match(r'^EEG\s*(\d+)$', ch, re.IGNORECASE)
            if m:
                idx = int(m.group(1)) - 1
                if 0 <= idx < len(_30CHANNEL_STANDARD_NAMES):
                    rename_map[ch] = _30CHANNEL_STANDARD_NAMES[idx]

    # Pattern 3: Pure numeric '1', '2', ...
    if not rename_map:
        for ch in existing:
            if ch.isdigit():
                idx = int(ch) - 1
                if 0 <= idx < len(_30CHANNEL_STANDARD_NAMES):
                    rename_map[ch] = _30CHANNEL_STANDARD_NAMES[idx]

    return rename_map


def _read_bids_events(row: Dict[str, Any]) -> mne.Annotations:
    """Read events from BIDS *_events.tsv file.

    Parameters
    ----------
    row : dict
        Locator row with 'File Path' (EEG file) and derived 'events_tsv' path.

    Returns
    -------
    mne.Annotations
        Annotations extracted from events.tsv with standardized description strings.
    """
    eeg_path = row.get("File Path", "")
    events_tsv = row.get("events_tsv", "")

    # Try to derive events_tsv from EEG path if not directly provided
    if not events_tsv or not os.path.exists(events_tsv):
        # BIDS structure: sub-*/eeg/*_eeg.fif -> sub-*/eeg/*_events.tsv
        base, ext = os.path.splitext(eeg_path)
        candidates = [
            base + "_events.tsv",
            eeg_path.replace("_eeg.fif", "_events.tsv").replace("_raw.fif", "_events.tsv"),
        ]
        for cand in candidates:
            if os.path.exists(cand):
                events_tsv = cand
                break

    if not events_tsv or not os.path.exists(events_tsv):
        # No events.tsv found; return empty annotations
        return mne.Annotations(onset=[], duration=[], description=[])

    import pandas as pd
    df = pd.read_csv(events_tsv, sep="\t")

    # Standard BIDS events columns: onset, duration, trial_type/value
    onset_col = "onset" if "onset" in df.columns else df.columns[0]
    duration_col = "duration" if "duration" in df.columns else None

    # Determine event label column
    label_col = None
    for col in ["trial_type", "value", "event_code", "stim_type", "stim_id"]:
        if col in df.columns:
            label_col = col
            break

    if label_col is None:
        # Use the last column with string data
        for col in reversed(df.columns):
            if df[col].dtype == object:
                label_col = col
                break

    if label_col is None:
        return mne.Annotations(onset=[], duration=[], description=[])

    # Build annotations with standardized event_XX format
    onsets = df[onset_col].values.astype(float)
    durations = df[duration_col].values.astype(float) if duration_col else np.zeros(len(df))
    descriptions = [f"event_{int(v)}" for v in df[label_col].values]

    return mne.Annotations(
        onset=onsets,
        duration=durations.tolist(),
        description=descriptions,
    )


def _extract_subject_metadata(row: Dict[str, Any]) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv.

    Parameters
    ----------
    row : dict
        Locator row with dataset root info.

    Returns
    -------
    dict
        Subject metadata with age, sex, handedness.
        All fields are strings; missing values are "unknown".
    """
    metadata = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    # Try to find participants.tsv
    eeg_path = row.get("File Path", "")
    dataset_root = row.get("dataset_root", os.path.dirname(os.path.dirname(eeg_path)))

    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    if not os.path.exists(participants_tsv):
        # Try parent directories
        parent = os.path.dirname(dataset_root)
        for _ in range(3):
            tsv = os.path.join(parent, "participants.tsv")
            if os.path.exists(tsv):
                participants_tsv = tsv
                break
            parent = os.path.dirname(parent)

    if not os.path.exists(participants_tsv):
        return metadata

    # Extract subject_id from file path
    import re
    match = re.search(r'sub-(\w+)', eeg_path)
    subject_id = match.group(1) if match else None

    if not subject_id:
        return metadata

    import pandas as pd
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        if "participant_id" in df.columns:
            subject_row = df[df["participant_id"] == subject_id]
        elif "subject_id" in df.columns:
            subject_row = df[df["subject_id"] == subject_id]
        else:
            subject_row = df[df[df.columns[0]] == subject_id]

        if len(subject_row) == 0:
            return metadata

        # Age
        age_col = "age" if "age" in df.columns else None
        if age_col:
            val = subject_row[age_col].values[0]
            if pd.notna(val):
                metadata["age"] = str(int(val))

        # Sex
        for col in ["sex", "gender"]:
            if col in df.columns:
                val = subject_row[col].values[0]
                if pd.notna(val):
                    sex = str(val).lower().strip()
                    if sex in ["m", "male", "f", "female"]:
                        metadata["sex"] = "male" if sex in ["m", "male"] else "female"
                    break

        # Handedness
        for col in ["handedness", "hand"]:
            if col in df.columns:
                val = subject_row[col].values[0]
                if pd.notna(val):
                    handed = str(val).lower().strip()
                    if handed in ["r", "right", "l", "left"]:
                        metadata["handedness"] = "right" if handed in ["r", "right"] else "left"
                    break

    except Exception:
        pass

    return metadata


class OpenNeuroDs005383Kernel:
    """Stage1 kernel for openneuro_ds005383 (TMNRED dataset).

    Binary semantic target identification:
    - event_31: Non-target sentence (y=0)
    - event_32: Target sentence (y=1)

    Multiclass: event_15 through event_64 (all condition codes).
    """

    KERNEL_ID: str = "openneuro-ds005383-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object (loaded from .fif/.edf BIDS format).
        row
            Locator row with File Path and derived paths.

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw with standardized channels, events, and metadata.
        """
        # Step 1: Rename channels to standard 10-20 if needed
        rename_map = _build_30ch_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
            # Set standard montage (30-channel cap)
            try:
                raw.set_montage("standard_1020", on_missing="warn")
            except Exception:
                pass

        # Step 2: Read events from BIDS events.tsv
        events_tsv = row.get("events_tsv", "")
        if events_tsv and os.path.exists(events_tsv):
            annotations = _read_bids_events(row)
            raw.set_annotations(annotations)

        # Step 3: Extract subject metadata
        subject_meta = _extract_subject_metadata(row)

        # Step 4: Build eegunity_description
        original_desc = raw.info.get("description", "") or ""

        description_dict = {
            "original_description": original_desc if isinstance(original_desc, str) else str(original_desc),
            "eegunity_description": {
                "age": subject_meta.get("age", "unknown"),
                "sex": subject_meta.get("sex", "unknown"),
                "amplifier": "unknown",  # BIDS sidecar not parsed; LLM 推断，需人类复核
                "cap": "unknown",  # BIDS sidecar not parsed; LLM 推断，需人类复核
                "handedness": subject_meta.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDs005383Kernel()