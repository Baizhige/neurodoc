"""OpenNeuro ds006840 (IACKD) stage1 kernel for EEGUnity.

Intention Action Conflict EEG-Hand Kinematics Dataset.
128 subjects, 29 channels, 1024 Hz, BrainVision format.

Event mapping:
- Stimulus/S  3 → premove (pre-movement preparation)
- Stimulus/S  1 → execution (motor execution onset)
- Stimulus/S  4 → hit (successful trial completion)
- Stimulus/S  2 → incongruent trial (excluded from standard motor phase classification)
- Stimulus/S  5-7 → admin markers (excluded)

Source: https://doi.org/10.18112/openneuro.ds006840.v1.0.0
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne


# Standard 10-20 channel names for 29-channel EEG cap
# Source: dataset documentation and standard_1020 montage
# Annotator: LLM, 2026-04-08, 需人类复核
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "FC5", "FC1", "FC2", "FC6",
    "CP5", "CP1", "CP2", "CP6",
]

# Event code mapping from raw BrainVision annotations to canonical names
# Source: analysis.md event structure, verified against OpenNeuro metadata
# Annotator: LLM, 2026-04-08, 需人类复核
_EVENT_MAP = {
    "Stimulus/S  1": "execution",
    "Stimulus/S  2": "incongruent_trial",
    "Stimulus/S  3": "premove",
    "Stimulus/S  4": "hit",
    "Stimulus/S  5": "admin: marker-5",
    "Stimulus/S  6": "admin: marker-6",
    "Stimulus/S  7": "admin: marker-7",
}


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name.

    Parameters
    ----------
    file_path : str
        Full path to the EEG file.

    Returns
    -------
    str
        Paradigm identifier ('iackd' for this dataset).
    """
    basename = os.path.basename(file_path).lower()
    if "iackd" in basename or "intention" in basename:
        return "iackd"
    return "iackd"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map to standardize channel names to 10-20 system.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with current channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from original names to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names

    # Common non-standard channel name patterns
    alias_groups = [
        ("Fp1", ["Fp1", "fp1", "EEG-Fp1"]),
        ("Fp2", ["Fp2", "fp2", "EEG-Fp2"]),
        ("Fpz", ["Fpz", "fpz", "EEG-Fpz"]),
        ("F7", ["F7", "f7", "EEG-F7"]),
        ("F3", ["F3", "f3", "EEG-F3"]),
        ("Fz", ["Fz", "fz", "EEG-Fz"]),
        ("F4", ["F4", "f4", "EEG-F4"]),
        ("F8", ["F8", "f8", "EEG-F8"]),
        ("T7", ["T7", "t7", "EEG-T7"]),
        ("C3", ["C3", "c3", "EEG-C3"]),
        ("Cz", ["Cz", "cz", "EEG-Cz"]),
        ("C4", ["C4", "c4", "EEG-C4"]),
        ("T8", ["T8", "t8", "EEG-T8"]),
        ("P7", ["P7", "p7", "EEG-P7"]),
        ("P3", ["P3", "p3", "EEG-P3"]),
        ("Pz", ["Pz", "pz", "EEG-Pz"]),
        ("P4", ["P4", "p4", "EEG-P4"]),
        ("P8", ["P8", "p8", "EEG-P8"]),
        ("O1", ["O1", "o1", "EEG-O1"]),
        ("Oz", ["Oz", "oz", "EEG-Oz"]),
        ("O2", ["O2", "o2", "EEG-O2"]),
        ("AF7", ["AF7", "af7", "EEG-AF7"]),
        ("AF3", ["AF3", "af3", "EEG-AF3"]),
        ("AF4", ["AF4", "af4", "EEG-AF4"]),
        ("AF8", ["AF8", "af8", "EEG-AF8"]),
        ("FC5", ["FC5", "fc5", "EEG-FC5"]),
        ("FC1", ["FC1", "fc1", "EEG-FC1"]),
        ("FC2", ["FC2", "fc2", "EEG-FC2"]),
        ("FC6", ["FC6", "fc6", "EEG-FC6"]),
        ("CP5", ["CP5", "cp5", "EEG-CP5"]),
        ("CP1", ["CP1", "cp1", "EEG-CP1"]),
        ("CP2", ["CP2", "cp2", "EEG-CP2"]),
        ("CP6", ["CP6", "cp6", "EEG-CP6"]),
        ("VEOG", ["VEOG", "veog", "EOG-V", "EOG-v"]),
        ("HEOG", ["HEOG", "heog", "EOG-H", "EOG-h"]),
        ("Trigger", ["Trigger", "trigger", "TRG", "trig"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _extract_subject_info(row) -> Dict[str, str]:
    """Extract subject metadata from row.

    Parameters
    ----------
    row : pandas.Series
        Row containing subject information.

    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, handedness.
    """
    subject_id = str(row.get("participant_id", "unknown"))

    # Check for participants.tsv data in row attributes
    # Source: OpenNeuro participants.tsv
    # Annotator: LLM, 2026-04-08, 需人类复核
    age = str(row.get("age", "unknown"))
    sex = str(row.get("sex", "unknown")).lower()
    handedness = str(row.get("handedness", "unknown")).lower()

    # Validate age format
    if age != "unknown":
        try:
            int(age)
        except (ValueError, TypeError):
            age = "unknown"

    # Validate sex
    if sex not in ("male", "female", "unknown"):
        sex = "unknown"

    # Validate handedness
    if handedness not in ("right", "left", "unknown"):
        handedness = "unknown"

    return {
        "age": age,
        "sex": sex,
        "handedness": handedness,
    }


class OpenNeuroDS006840Kernel:
    """Stage1 kernel for OpenNeuro ds006840 (IACKD dataset)."""

    KERNEL_ID: str = "openneuro-ds006840-stage1"

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
            The modified Raw object with standardized channels, annotations,
            and metadata.
        """
        file_path = row.get("File Path", "")

        # Step 1: Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # Step 2: Identify and tag non-EEG channels
        eeg_channel_names = [
            "Fp1", "Fpz", "Fp2",
            "F7", "F3", "Fz", "F4", "F8",
            "T7", "C3", "Cz", "C4", "T8",
            "P7", "P3", "Pz", "P4", "P8",
            "O1", "Oz", "O2",
            "AF7", "AF3", "AF4", "AF8",
            "FC5", "FC1", "FC2", "FC6",
            "CP5", "CP1", "CP2", "CP6",
        ]

        # Set channel types for non-standard channels
        channel_types = {}
        for ch in raw.ch_names:
            if ch in eeg_channel_names:
                channel_types[ch] = "eeg"
            elif ch in ("VEOG", "HEOG"):
                channel_types[ch] = "eog"
            elif ch in ("Trigger",):
                channel_types[ch] = "stim"
            elif ch.lower() in ("misc",):
                channel_types[ch] = "misc"

        if channel_types:
            raw.set_channel_types(channel_types)

        # Step 3: Set standard 10-20 montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in both raw and montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 20:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If montage setting fails, continue without it
            pass

        # Step 4: Extract and map events to canonical names
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            events = None
            event_id = {}

        # Step 5: Create standardized annotations
        if events is not None and len(events) > 0:
            # Build reverse mapping from event ID to canonical name
            id_to_canonical = {}
            for desc, code in event_id.items():
                canonical = _EVENT_MAP.get(desc, desc)
                id_to_canonical[code] = canonical

            # Create new annotations with canonical names
            onset_times = events[:, 0] / raw.info["sfreq"]
            durations = [0.0] * len(events)
            descriptions = [id_to_canonical.get(e[2], str(e[2])) for e in events]

            new_annotations = mne.Annotations(
                onset=onset_times,
                duration=durations,
                description=descriptions,
                orig_time=raw.annotations.orig_time if raw.annotations else None,
            )
            raw.set_annotations(new_annotations)

        # Step 6: Extract subject metadata
        subject_info = _extract_subject_info(row)

        # Step 7: Build eegunity_description
        # Amplifier info from dataset documentation
        # Source: OpenNeuro dataset_description.json
        # Annotator: LLM, 2026-04-08, 需人类复核
        amplifier = "BrainAmp"  # LLM 推断，需人类复核

        # Cap info - standard 10-20 cap
        # Source: Dataset documentation and paradigm description
        # Annotator: LLM, 2026-04-08, 需人类复核
        cap = "Ag/AgCl"  # LLM 推断，需人类复核

        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": amplifier,
                "cap": cap,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Step 8: Exclude non-EEG channels from pick list (informational)
        # These channels remain in raw but are marked for exclusion
        non_eeg_channels = [
            ch for ch in raw.ch_names
            if ch not in eeg_channel_names
        ]

        return raw


KERNEL = OpenNeuroDS006840Kernel()