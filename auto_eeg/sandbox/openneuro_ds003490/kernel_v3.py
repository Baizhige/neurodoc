"""OpenNeuro ds003490 stage1 kernel for EEGUnity.

3-Stim Auditory Oddball and Rest in Parkinson's Disease dataset.
- 50 subjects, 67 channels, 500 Hz sampling rate
- Events: Standard Tone, Target Tone, Novel Tone, Eyes Closed, Eyes Open
- BioSemi STATUS markers (S 85, S255) excluded as admin markers

Source: https://openneuro.org/datasets/ds003490
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

import mne
import pandas as pd


# Mapping from BioSemi Stim Trak codes to canonical event descriptions
# S 85 = STATUS onset marker (BioSemi admin) → EXCLUDE
# S255 = STATUS offset marker (BioSemi admin) → EXCLUDE
# Source: Dataset documentation / BioSemi manual
_EVENT_CODE_MAP: Dict[str, str] = {
    "S  1": "Standard Tone",
    "S  2": "Standard Tone",
    "S  3": "Novel Tone",
    "S  4": "Novel Tone",
    "S200": "Target Tone",
    "S202": "Target Tone",
}

# BioSemi 64-channel system standard electrode naming (extended 10-20)
# 67 channels includes 3 auxiliary (EOG, etc.)
# Source: BioSemi electrode naming convention
_BIOSEMI_64_CHANNELS = [
    "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1",
    "Fz", "F2", "F4", "F6", "F8", "FT7", "FC5", "FC3", "FC1", "FCz",
    "FC2", "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2",
    "C4", "C6", "T8", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4",
    "CP6", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2", "CB1", "CB2",
    "VEOG", "HEOG", "M1", "M2",
]

# Common alias patterns for channel name normalization
# Source: LLM inference from BioSemi data patterns; needs human verification
_CHANNEL_ALIAS_MAP: Dict[str, str] = {
    "EEG Fp1": "Fp1", "EEG Fp2": "Fp2",
    "EEG F7": "F7", "EEG F3": "F3", "EEG Fz": "Fz", "EEG F4": "F4", "EEG F8": "F8",
    "EEG T7": "T7", "EEG C3": "C3", "EEG Cz": "Cz", "EEG C4": "C4", "EEG T8": "T8",
    "EEG P7": "P7", "EEG P3": "P3", "EEG Pz": "Pz", "EEG P4": "P4", "EEG P8": "P8",
    "EEG O1": "O1", "EEG Oz": "Oz", "EEG O2": "O2",
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if it exists."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(subject_id: str, dataset_path: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.

    Returns dict with age, sex keys. Unknown values marked as "unknown".
    """
    df = _load_participants_tsv(dataset_path)

    # Try common column names for subject ID
    subj_col = None
    for col in ["participant_id", "subject_id", "subject"]:
        if col in df.columns:
            subj_col = col
            break

    if subj_col is None or df.empty:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}

    # Normalize subject ID format (sub-01 -> 01 or keep as-is)
    normalized_id = subject_id.replace("sub-", "").replace("sub_", "")
    row = df[df[subj_col].str.replace("sub-", "").str.replace("sub_", "") == normalized_id]

    if row.empty:
        return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}

    result = {"age": "unknown", "sex": "unknown", "handedness": "unknown"}

    # Extract age - handle various column names and formats
    age_col = None
    for col in ["age", "subject_age", "participant_age"]:
        if col in df.columns:
            age_col = col
            break

    if age_col is not None:
        age_val = row[age_col].values[0]
        if pd.notna(age_val) and str(age_val).strip():
            result["age"] = str(age_val).strip()

    # Extract sex - handle various column names and value formats
    sex_col = None
    for col in ["sex", "gender", "subject_sex"]:
        if col in df.columns:
            sex_col = col
            break

    if sex_col is not None:
        sex_val = str(row[sex_col].values[0]).strip().lower()
        if sex_val in ["m", "male", "f", "female"]:
            result["sex"] = "male" if sex_val.startswith("m") else "female"
        elif sex_val and sex_val != "n/a":
            result["sex"] = sex_val

    # Extract handedness
    hand_col = None
    for col in ["handedness", "hand", "dominant_hand"]:
        if col in df.columns:
            hand_col = col
            break

    if hand_col is not None:
        hand_val = str(row[hand_col].values[0]).strip().lower()
        if hand_val in ["r", "right", "l", "left", "a", "ambidextrous"]:
            if hand_val.startswith("r"):
                result["handedness"] = "right"
            elif hand_val.startswith("l"):
                result["handedness"] = "left"
            else:
                result["handedness"] = "ambidextrous"
        elif hand_val and hand_val != "n/a":
            result["handedness"] = hand_val

    return result


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    for source, target in _CHANNEL_ALIAS_MAP.items():
        if source in existing:
            rename_map[source] = target

    return rename_map


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap BioSemi Stim Trak event codes to canonical descriptions.

    Excludes BioSemi STATUS admin markers (S 85, S255).
    """
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
    except Exception:
        return raw  # No annotations to remap

    # Build new annotations based on event code map
    new_onsets = []
    new_durations = []
    new_descriptions = []

    for idx, event in enumerate(events):
        # Access description via attribute array, not indexing annotation object
        orig_desc = raw.annotations.description[idx]

        # Check if this is a STATUS admin marker to exclude
        if orig_desc.strip() in ["S 85", "S255", "STATUS"]:
            continue

        # Map to canonical description
        mapped_desc = _EVENT_CODE_MAP.get(orig_desc.strip(), orig_desc.strip())

        sample_idx = event[0]
        new_onsets.append(raw.annotations.onset[idx])
        new_durations.append(0.0)
        new_descriptions.append(mapped_desc)

    if new_onsets:
        new_annotations = mne.Annotations(
            onset=new_onsets,
            duration=new_durations,
            description=new_descriptions,
        )
        raw.set_annotations(new_annotations)

    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard montage for known BioSemi channel configurations.

    Uses standard_1020 which covers all standard 10-20 electrodes.
    May fail silently if channels don't match standard montage.
    """
    try:
        # Check if most channels are standard 10-20
        standard_channels = set(mne.channels.make_standard_montage("standard_1020").ch_names)
        existing_eeg = set(ch for ch in raw.ch_names if ch not in ["EOG", "VEOG", "HEOG", "M1", "M2", "A1", "A2"])

        if existing_eeg & standard_channels:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Montage setting is best-effort

    return raw


class OpenNeuroDs003490Kernel:
    """Stage1 kernel for OpenNeuro ds003490 (3-Stim Auditory Oddball in PD)."""

    KERNEL_ID: str = "openneuro-ds003490-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single BDF/EDF recording."""
        file_path = row.get("File Path", "")
        subject_id = str(row.get("Subject ID", ""))

        # Get dataset root path for participants.tsv lookup
        dataset_path = getattr(udataset, "path", os.path.dirname(file_path))

        # Load subject metadata from participants.tsv
        subject_info = _get_subject_info(subject_id, dataset_path)

        # Get device info - BioSemi system
        # Source: Dataset recorded with BioSemi ActiveTwo system
        amplifier = "BioSemi ActiveTwo"
        cap = "Ag/AgCl"

        # Build eegunity_description dict
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": amplifier,
            "cap": cap,
            "handedness": subject_info.get("handedness", "unknown"),
        }

        # Rename non-standard channel names to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Remap event annotations to canonical descriptions
        raw = _remap_annotations(raw)

        # Attempt to set standard montage
        raw = _set_montage_if_possible(raw)

        # Convert to float64 for numerical stability
        raw.set_dtype(np.float64)

        return raw


KERNEL = OpenNeuroDs003490Kernel()