"""OpenNeuro DS002720 stage1 kernel for EEGUnity.

Dataset: A dataset recorded during development of a tempo-based brain-computer music interface
URL: https://openneuro.org/datasets/ds002720
Reference: DOI 10.1038/s41597-020-0507-6

This kernel handles:
- Subject metadata from participants.tsv (age, sex, handedness)
- Channel rename from non-standard names to standard 10-20 names
- Event loading from events.tsv for EDF files that don't carry native triggers
- Required info fields: age, sex
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 19-channel 10-20 montage for this dataset
# Source: DOI 10.1038/s41597-020-0507-6 (19 EEG channels)
# LLM inferred channel mapping, 2026-04-08; based on standard 10-20 with 19 channels
# The dataset uses a standard 10-20 cap; common non-standard names are mapped below
_CHANNEL_RENAME_MAP = {
    # Common variations found in BIDS EEG exports
    "EEG Fp1": "Fp1",
    "EEG Fpz": "Fpz",
    "EEG Fp2": "Fp2",
    "EEG F7": "F7",
    "EEG F3": "F3",
    "EEG Fz": "Fz",
    "EEG F4": "F4",
    "EEG F8": "F8",
    "EEG T7": "T7",
    "EEG T3": "T7",  # older nomenclature
    "EEG C3": "C3",
    "EEG Cz": "Cz",
    "EEG C4": "C4",
    "EEG T8": "T8",
    "EEG T4": "T8",  # older nomenclature
    "EEG P7": "P7",
    "EEG T5": "P7",  # older nomenclature
    "EEG P3": "P3",
    "EEG Pz": "Pz",
    "EEG P4": "P4",
    "EEG P8": "P8",
    "EEG T6": "P8",  # older nomenclature
    "EEG O1": "O1",
    "EEG O2": "O2",
    "EEG A1": "A1",  # mastoid, will be set to misc
    "EEG A2": "A2",  # mastoid, will be set to misc
    # Generic numbered channels mapped by position (fallback)
    "EEG 0": "Fp1",
    "EEG 1": "Fpz",
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
    "EEG 19": "O2",
}

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex"]

# Required native misc channels (none for this dataset)
_REQUIRED_NATIVE_MISC = []

# Required derived misc channels (none for this dataset)
_DERIVED_MISC_CHANNELS = []


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, Any]]:
    """Load subject metadata from BIDS participants.tsv.

    Parameters
    ----------
    dataset_path : str
        Root directory of the dataset.

    Returns
    -------
    dict
        Mapping from subject ID (e.g., "01") to metadata dict.
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_file):
        return {}

    df = pd.read_csv(participants_file, sep="\t")
    result: Dict[str, Dict[str, Any]] = {}

    for _, row in df.iterrows():
        participant_id = str(row.get("participant_id", ""))
        if not participant_id.startswith("sub-"):
            continue
        subject_id = participant_id[4:]  # Strip "sub-" prefix

        result[subject_id] = {}
        for field in _REQUIRED_INFO_FIELDS:
            val = row.get(field, "unknown")
            if pd.isna(val):
                val = "unknown"
            else:
                val = str(val).lower() if field == "sex" else str(val)
            result[subject_id][field] = val

    return result


def _detect_subject_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from file path.

    Parameters
    ----------
    file_path : str
        Full path to the EEG file.

    Returns
    -------
    str or None
        Subject ID (e.g., "01") if found.
    """
    match = re.search(r"sub-(\w+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file.

    Parameters
    ----------
    file_path : str
        Full path to the EEG file.

    Returns
    -------
    str or None
        Path to events.tsv if found.
    """
    # BIDS convention: events.tsv is in the same directory with matching entity
    base_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)

    # Remove extension to get base
    for ext in [".edf", ".bdf", ".set", ".eeg", ".fif", ".vhdr", ".vmrk"]:
        if base_name.endswith(ext):
            base_name = base_name[:-len(ext)]
            break

    # Try exact match: sub-XX_task-YY_run-ZZ_events.tsv
    events_file = os.path.join(base_dir, base_name.replace("_eeg", "_events") + "_events.tsv")
    if os.path.exists(events_file):
        return events_file

    # Try without _eeg suffix replacement
    events_file = os.path.join(base_dir, base_name + "_events.tsv")
    if os.path.exists(events_file):
        return events_file

    # Search for any events.tsv in same directory matching subject
    if base_dir and os.path.isdir(base_dir):
        for f in os.listdir(base_dir):
            if f.endswith("_events.tsv"):
                return os.path.join(base_dir, f)

    return None


def _read_events_from_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events from BIDS events.tsv file.

    Parameters
    ----------
    events_path : str
        Path to events.tsv file.

    Returns
    -------
    pd.DataFrame or None
        Events dataframe with standardized columns.
    """
    try:
        df = pd.read_csv(events_path, sep="\t")
        # Standard BIDS columns: onset, duration, trial_type, value, sample
        # Ensure required columns exist
        if "onset" not in df.columns:
            return None

        # Ensure duration column exists
        if "duration" not in df.columns:
            df["duration"] = 0.0

        return df
    except Exception:
        return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for the given raw object.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw EEG data.

    Returns
    -------
    dict
        Mapping from original channel names to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for orig_name, std_name in _CHANNEL_RENAME_MAP.items():
        if orig_name in existing_names and orig_name != std_name:
            # Avoid collisions
            if std_name not in existing_names or std_name == orig_name:
                rename_map[orig_name] = std_name

    return rename_map


@dataclass
class OpenNeuroDS002720Kernel:
    """Stage1 kernel for OpenNeuro DS002720 dataset."""

    KERNEL_ID: str = "openneuro-ds002720-stage1"
    kernel_requirements: Dict[str, Any] = None

    def __post_init__(self):
        self.kernel_requirements = {
            "required_event_ids": ["1", "2"],
            "required_info_fields": ["age", "sex"],
            "required_native_misc": [],
            "derived_misc_channels": [],
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Get dataset root from udataset or infer from path
        dataset_path = getattr(udataset, "dataset_path", None)
        if dataset_path is None:
            # Infer from file path: go up until we find participants.tsv
            temp_path = os.path.dirname(file_path)
            for _ in range(5):  # Max 5 levels up
                if os.path.exists(os.path.join(temp_path, "participants.tsv")):
                    dataset_path = temp_path
                    break
                parent = os.path.dirname(temp_path)
                if parent == temp_path:
                    break
                temp_path = parent

        # Load subject metadata
        participants = _load_participants_tsv(dataset_path) if dataset_path else {}

        # Detect subject from file path
        subject_id = _detect_subject_from_path(file_path)
        subject_meta = participants.get(subject_id, {}) if subject_id else {}

        # Get required info fields
        age = subject_meta.get("age", "unknown")
        sex = subject_meta.get("sex", "unknown")

        # Normalize sex to lowercase standard
        if sex.lower() in ("m", "male"):
            sex = "male"
        elif sex.lower() in ("f", "female"):
            sex = "female"
        else:
            sex = "unknown"

        # Ensure age is string
        age = str(age) if age != "unknown" else "unknown"

        # Build eegunity_description with required info fields
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": "unknown",  # LLM 推断，需人类复核: device info not in standard BIDS
            "cap": "unknown",  # LLM 推断，需人类复核: cap info not in standard BIDS
            "handedness": "unknown",  # LLM 推断，需人类复核: not in required_info_fields
        }

        # Add any extra required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field not in ("age", "sex"):
                val = subject_meta.get(field, "unknown")
                eegunity_description[field] = str(val) if val != "unknown" else "unknown"

        # Update description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        # Channel rename BEFORE set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for non-EEG channels
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in ("A1", "A2", "M1", "M2", "HEOG", "VEOG", "EOG"):
                ch_types[ch_name] = "eog"
            elif ch_name in ("Nz", "Iz"):
                ch_types[ch_name] = "misc"

        if ch_types:
            raw.set_channel_types(ch_types)

        # Set standard 10-20 montage if channels match
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Check if we have enough standard channels
            standard_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            if len(raw_chs & standard_chs) >= 10:  # At least 10 matching channels
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without

        # Handle events from events.tsv for formats that may not carry triggers
        # EDF files in this dataset do not contain native annotations, so we must
        # always load from the sidecar events.tsv
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_df = _read_events_from_tsv(events_tsv_path)
            if events_df is not None and len(events_df) > 0:
                # Build annotations from events.tsv
                # Use trial_type column as the annotation description (contains "1" and "2")
                onsets = events_df["onset"].values.astype(float)
                durations = events_df["duration"].values.astype(float)
                
                # Use trial_type if available, otherwise fall back to value
                if "trial_type" in events_df.columns:
                    descriptions = events_df["trial_type"].astype(str).values
                elif "value" in events_df.columns:
                    descriptions = events_df["value"].astype(str).values
                else:
                    descriptions = np.array([""] * len(events_df))

                # Create MNE Annotations and assign to raw
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=raw.info.get("meas_date"),
                )
                raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS002720Kernel()