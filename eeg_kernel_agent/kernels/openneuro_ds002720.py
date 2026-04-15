"""OpenNeuro DS002720 stage1 kernel for EEGUnity.

Dataset: A dataset recorded during development of a tempo-based brain-computer music interface
URL: https://openneuro.org/datasets/ds002720
Reference: DOI 10.1038/s41597-020-0507-6

This kernel handles:
- Subject metadata from participants.tsv (age, sex, handedness)
- Hardware metadata from dataset_description.json (amplifier, cap)
- Channel rename from non-standard names to standard 10-20 names
- Event remapping for alpha-state BCMI conditions
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne


# Standard 19-channel 10-20 montage for this dataset
# Source: DOI 10.1038/s41597-020-0507-6 (19 EEG channels)
_STANDARD_19_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "O2",
]

# Event mapping: numeric code -> human-readable label
# Source: DOI 10.1038/s41597-020-0507-6 and analysis.md
_EVENT_MAP = {
    1: "lower_alpha",
    2: "raise_alpha",
}


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

    import pandas as pd

    df = pd.read_csv(participants_file, sep="\t")
    result: Dict[str, Dict[str, Any]] = {}

    for _, row in df.iterrows():
        participant_id = str(row.get("participant_id", ""))
        if not participant_id.startswith("sub-"):
            continue
        subject_id = participant_id[4:]  # Strip "sub-" prefix

        result[subject_id] = {
            "age": str(row.get("age", "unknown")),
            "sex": str(row.get("sex", "unknown")).lower(),
            "handedness": str(row.get("handedness", "unknown")).lower(),
        }

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
    import re

    match = re.search(r"sub-(\w+)", file_path)
    if match:
        return match.group(1)
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from current channel names to standard 10-20 names.

    This handles common non-standard naming patterns in EEG datasets.
    Source: General 10-20 standard mapping, annotated for this dataset

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object with current channel names.

    Returns
    -------
    dict
        Mapping from old names to new standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Standard 10-20 channel name variants
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "FP1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "FPZ"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "FP2"]),
        ("F7", ["F7", "EEG-F7", "F7"]),
        ("F3", ["F3", "EEG-F3", "F3"]),
        ("Fz", ["Fz", "EEG-Fz", "FZ"]),
        ("F4", ["F4", "EEG-F4", "F4"]),
        ("F8", ["F8", "EEG-F8", "F8"]),
        ("T7", ["T7", "T3", "EEG-T7", "EEG-T3"]),
        ("C3", ["C3", "EEG-C3", "C3"]),
        ("Cz", ["Cz", "EEG-Cz", "CZ"]),
        ("C4", ["C4", "EEG-C4", "C4"]),
        ("T8", ["T8", "T4", "EEG-T8", "EEG-T4"]),
        ("P7", ["P7", "P3", "EEG-P7", "EEG-P3"]),
        ("P3", ["P3", "EEG-P3"]),
        ("Pz", ["Pz", "EEG-Pz", "PZ"]),
        ("P4", ["P4", "EEG-P4"]),
        ("P8", ["P8", "P4", "EEG-P8", "EEG-P4"]),
        ("O1", ["O1", "EEG-O1"]),
        ("O2", ["O2", "EEG-O2"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _remap_events_from_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap numeric event codes to human-readable labels.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        MNE Raw object with annotations.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with updated annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    old_descriptions = raw.annotations.description
    new_descriptions = []

    for desc in old_descriptions:
        desc_str = str(desc)
        if desc_str in _EVENT_MAP:
            new_descriptions.append(_EVENT_MAP[desc_str])
        else:
            # Keep unknown descriptions as-is
            new_descriptions.append(desc_str)

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)

    return raw


class OpenNeuroDS002720Kernel:
    """Stage1 kernel for OpenNeuro DS002720 (tempo-based BCMI dataset)."""

    KERNEL_ID: str = "openneuro-ds002720-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

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
            Preprocessed MNE Raw object.
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", "")

        # Store original description
        original_description = raw.info.get("description", "")

        # Load subject metadata from participants.tsv
        subject_dict = _load_participants_tsv(dataset_path)

        # Detect subject from file path
        subject_id = _detect_subject_from_path(file_path)

        # Get subject-specific metadata
        if subject_id and subject_id in subject_dict:
            subject_info = subject_dict[subject_id]
            age = subject_info.get("age", "unknown")
            sex = subject_info.get("sex", "unknown").lower()
            handedness = subject_info.get("handedness", "unknown").lower()
        else:
            # LLM 推断，需人类复核
            age = "unknown"
            sex = "unknown"
            handedness = "unknown"

        # Hardware metadata from dataset_description.json or known values
        # Source: DOI 10.1038/s41597-020-0507-6 - BrainAmp amplifier, Ag/AgCl cap
        amplifier = "BrainAmp"  # LLM 推断，需人类复核
        cap = "Ag/AgCl"  # LLM 推断，需人类复核

        # Try to load from dataset_description.json
        desc_file = os.path.join(dataset_path, "dataset_description.json")
        if os.path.exists(desc_file):
            try:
                with open(desc_file, "r", encoding="utf-8") as f:
                    desc_data = json.load(f)
                    # Check for equipment info in description
                    equipment = desc_data.get("EEGReference", "")
                    if equipment:
                        amplifier = equipment
            except Exception:
                pass

        # Build channel rename map and apply before set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Skip montage if not available

        # Remap events from numeric codes to descriptive labels
        raw = _remap_events_from_annotations(raw)

        # Update description with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex),
                "amplifier": str(amplifier),
                "cap": str(cap),
                "handedness": str(handedness),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS002720Kernel()