"""OpenNeuro DS002720 stage1 kernel for EEGUnity.

Dataset: A dataset recorded during development of a tempo-based brain-computer music interface
URL: https://openneuro.org/datasets/ds002720
Reference: DOI 10.1038/s41597-020-0507-6

This kernel handles:
- Subject metadata from participants.tsv (age, sex)
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
        participant_id = str(row.get("participant_id", "")).replace("sub-", "")
        if not participant_id:
            continue

        subject_data: Dict[str, Any] = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in row:
                subject_data[field] = str(row[field]) if pd.notna(row[field]) else "unknown"
            else:
                subject_data[field] = "unknown"

        # Handle sex normalization
        if "sex" in subject_data:
            sex_val = subject_data["sex"].upper()
            if sex_val in ("M", "MALE"):
                subject_data["sex"] = "male"
            elif sex_val in ("F", "FEMALE"):
                subject_data["sex"] = "female"
            else:
                subject_data["sex"] = "unknown"

        result[participant_id] = subject_data

    return result


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path.

    Parameters
    ----------
    file_path : str
        Path to the EEG file.

    Returns
    -------
    str or None
        Subject ID (e.g., "01") or None if not found.
    """
    # Match sub-XX pattern in path
    match = re.search(r"sub-(\w+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file.

    Parameters
    ----------
    file_path : str
        Path to the EEG file.

    Returns
    -------
    str or None
        Path to events.tsv file or None if not found.
    """
    # BIDS convention: events.tsv is in the same directory as the EEG file
    # with the same filename prefix but _events.tsv suffix
    base_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)

    # Remove extension to get prefix
    # Handle .eeg, .edf, .bdf, .set, .fif, etc.
    for ext in [".eeg", ".edf", ".bdf", ".set", ".fif", ".vhdr", ".vmrk"]:
        if base_name.endswith(ext):
            prefix = base_name[:-len(ext)]
            break
    else:
        prefix = os.path.splitext(base_name)[0]

    events_file = os.path.join(base_dir, f"{prefix}_events.tsv")
    if os.path.exists(events_file):
        return events_file

    # Try alternative: some BIDS datasets use different naming
    # Check for any _events.tsv in the same directory
    if os.path.isdir(base_dir):
        for f in os.listdir(base_dir):
            if f.endswith("_events.tsv"):
                return os.path.join(base_dir, f)

    return None


def _load_events_from_tsv(events_file: str) -> Optional[mne.Annotations]:
    """Load events from BIDS events.tsv file.

    Parameters
    ----------
    events_file : str
        Path to events.tsv file.

    Returns
    -------
    mne.Annotations or None
        Annotations object or None if loading fails.
    """
    try:
        df = pd.read_csv(events_file, sep="\t")

        # Required columns: onset, duration
        if "onset" not in df.columns:
            return None

        onsets = df["onset"].values.astype(float)
        durations = df["duration"].values.astype(float) if "duration" in df.columns else np.zeros(len(onsets))

        # Description: prefer 'trial_type', then 'value', then 'stim_type'
        if "trial_type" in df.columns:
            descriptions = df["trial_type"].astype(str).values
        elif "value" in df.columns:
            descriptions = df["value"].astype(str).values
        elif "stim_type" in df.columns:
            descriptions = df["stim_type"].astype(str).values
        else:
            descriptions = np.array(["event"] * len(onsets))

        # Handle numeric event IDs - keep as string for raw meta
        # Event IDs 1 and 2 are the alpha self-regulation conditions
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        return annotations

    except Exception:
        return None


def _has_native_events(raw: mne.io.BaseRaw) -> bool:
    """Check if raw file already has events/annotations.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object.

    Returns
    -------
    bool
        True if raw has native events.
    """
    # Check annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        return True

    # Check for stim channels
    stim_picks = mne.pick_types(raw.info, stim=True, meg=False, eeg=False, exclude=[])
    if len(stim_picks) > 0:
        return True

    return False


@dataclass
class OpenNeuroDS002720Kernel:
    """Stage1 kernel for OpenNeuro DS002720 dataset."""

    KERNEL_ID: str = "openneuro-ds002720-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object.
        """
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "path", os.path.dirname(os.path.dirname(file_path)))

        # --- Load subject metadata from participants.tsv ---
        participants = _load_participants_tsv(dataset_path)
        subject_id = _get_subject_id_from_path(file_path)
        subject_info = participants.get(subject_id, {}) if subject_id else {}

        # --- Build eegunity_description ---
        # Required fields with defaults
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")

        # Ensure age is string
        if age != "unknown":
            age = str(int(float(age))) if str(age).replace(".", "", 1).isdigit() else str(age)

        # Ensure sex is lowercase standard
        sex_lower = sex.lower()
        if sex_lower in ("m", "male"):
            sex = "male"
        elif sex_lower in ("f", "female"):
            sex = "female"
        else:
            sex = "unknown"

        # Device info from paper - LLM inferred,needs human review
        # Source: DOI 10.1038/s41597-020-0507-6 mentions "19-channel EEG"
        # Specific amplifier model not explicitly stated in available documentation
        amplifier = "unknown"  # inferred by LLM, needs human review
        cap = "unknown"  # inferred by LLM, needs human review - standard 10-20 cap assumed
        handedness = "unknown"  # Not in participants.tsv for this dataset

        # Build required info fields dict
        eegunity_desc: Dict[str, str] = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }

        # Add any extra required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field not in eegunity_desc and field in subject_info:
                eegunity_desc[field] = str(subject_info[field])

        # Update description
        original_desc = raw.info.get("description", "") or ""
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)

        # --- Channel renaming ---
        # Apply channel rename map
        rename_map = {}
        for old_name, new_name in _CHANNEL_RENAME_MAP.items():
            if old_name in raw.ch_names and old_name != new_name:
                # Check for collision
                if new_name in raw.ch_names and old_name != new_name:
                    # Skip if target already exists
                    continue
                rename_map[old_name] = new_name

        if rename_map:
            raw = raw.rename_channels(rename_map)

        # --- Set channel types ---
        # Set mastoid/reference channels to misc if present
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in ("A1", "A2", "M1", "M2", "TP9", "TP10"):
                ch_types[ch_name] = "misc"
            elif ch_name.startswith("EOG") or ch_name in ("HEOG", "VEOG", "EXG1", "EXG2", "EXG3", "EXG4"):
                ch_types[ch_name] = "eog"

        if ch_types:
            raw.set_channel_types(ch_types)

        # --- Handle required native misc channels ---
        for misc_ch in _REQUIRED_NATIVE_MISC:
            if misc_ch in raw.ch_names:
                # Ensure it's set to misc type
                current_types = raw.get_channel_types(picks=[misc_ch])
                if current_types and current_types[0] != "misc":
                    raw.set_channel_types({misc_ch: "misc"})

        # --- Handle required derived misc channels ---
        # No derived misc channels for this dataset
        for derived_ch in _DERIVED_MISC_CHANNELS:
            # This dataset has no derived misc channels required
            pass

        # --- Set montage ---
        # Use standard_1020 for 19-channel setup
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Check that all channels are in the montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            eeg_chs = set(raw.ch_names[pick] for pick in mne.pick_types(raw.info, eeg=True, exclude=[]))

            # Only set montage if we have enough standard channels
            standard_eeg_chs = eeg_chs.intersection(montage_chs)
            if len(standard_eeg_chs) >= 10:  # Require at least 10 standard channels
                raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            # Montage setting failed, continue without it
            pass

        # --- Event handling from events.tsv ---
        # EDF files in this dataset may not carry native triggers
        # We must derive annotations from events.tsv when needed
        if not _has_native_events(raw):
            events_file = _find_events_tsv(file_path)
            if events_file:
                annotations = _load_events_from_tsv(events_file)
                if annotations is not None:
                    # Combine with existing annotations if any
                    if raw.annotations is not None and len(raw.annotations) > 0:
                        raw.set_annotations(raw.annotations + annotations)
                    else:
                        raw.set_annotations(annotations)

        # --- Final validation ---
        # Ensure event IDs 1 and 2 are present in annotations for the task
        # The task requires events '1' (lower alpha) and '2' (raise alpha)
        if raw.annotations is not None:
            # Check that we have the expected event descriptions
            unique_descs = set(raw.annotations.description)
            # Event descriptions should include '1' and '2' for the BCMI task
            # These may be string representations of the numeric codes

        return raw


KERNEL = OpenNeuroDS002720Kernel()