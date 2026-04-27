"""OpenNeuro ds004151 stage1 kernel for EEGUnity.

Effect of obesity on inhibitory control in preadolescents during stop-signal task.
An event-related potentials study.

Dataset: 57 subjects, 128-channel EGI Geodesic HydroCel cap, 500 Hz sampling rate.
Paradigm: Stop-signal task with go trials (event 1) and stop-signal trials (event 2).

Source: https://openneuro.org/datasets/ds004151
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne


# ============================================================================
# Subject Metadata
# ============================================================================
# Source: Paper states preadolescents aged 9-10 years (2022 study)
# Annotator: LLM, 2026-04-08
_SUBJECT_AGE_RANGE: str = "9-10"

# Sex information not directly available in BIDS participants.tsv
# Will attempt to load from participants.tsv at runtime; fallback to "unknown"
# Annotator: LLM, 2026-04-08

# ============================================================================
# Channel Rename Map for EGI 128-channel HydroCel System
# ============================================================================
# Source: EGI Geodesic HydroCel GSN 128 channel naming convention
# Standard naming: E1-E128 (EGI original) -> renamed to standard layout
# Annotator: LLM, 2026-04-08
_EGI_CHANNEL_MAP: Dict[str, str] = {
    f"E{str(i).zfill(3)}": f"EEG-{i}" for i in range(1, 129)
}

# Additional common EGI alias mappings
_EGI_ALIAS_MAP: Dict[str, str] = {
    "E1": "EEG-001",
    "E2": "EEG-002",
    # ... (all E1-E128 mapped to EEG-XXX format for standard recognition)
}

# Build full rename map
_FULL_CHANNEL_MAP: Dict[str, str] = {}
for i in range(1, 129):
    old_name = f"E{i}"
    new_name = f"EEG-{str(i).zfill(3)}"
    _FULL_CHANNEL_MAP[old_name] = new_name


# ============================================================================
# Event Mapping
# ============================================================================
# Source: analysis.md - Event Structure table
# Event ID 1: Go trial stimulus onset (~14,364 events)
# Event ID 2: Stop-signal trial (~6,156 events)
_EVENT_ID_MAP: Dict[str, int] = {
    "go_trial": 1,
    "stop_trial": 2,
}

_REVERSE_EVENT_MAP: Dict[int, str] = {
    1: "go_trial",
    2: "stop_trial",
}


def _load_participants_metadata(dataset_root: str) -> Optional[Dict[str, Dict[str, Any]]]:
    """Load subject metadata from BIDS participants.tsv if available.

    Returns
    -------
    Optional[Dict[str, Dict[str, Any]]]
        Dictionary mapping subject IDs to their metadata (age, sex).
    """
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    if not os.path.exists(participants_tsv):
        return None

    try:
        import pandas as pd

        df = pd.read_csv(participants_tsv, sep="\t")
        subject_dict: Dict[str, Dict[str, Any]] = {}

        for _, row in df.iterrows():
            participant_id = str(row.get("participant_id", ""))
            if not participant_id.startswith("sub-"):
                continue

            subject_id = participant_id.replace("sub-", "")
            subject_dict[subject_id] = {}

            # Extract age
            age = row.get("age")
            if age is not None and not pd.isna(age):
                subject_dict[subject_id]["age"] = str(int(float(age)))
            else:
                subject_dict[subject_id]["age"] = _SUBJECT_AGE_RANGE

            # Extract sex
            sex = row.get("sex", row.get("gender"))
            if sex is not None and not pd.isna(sex):
                sex_lower = str(sex).lower().strip()
                if sex_lower in ["m", "male"]:
                    subject_dict[subject_id]["sex"] = "male"
                elif sex_lower in ["f", "female"]:
                    subject_dict[subject_id]["sex"] = "female"
                else:
                    subject_dict[subject_id]["sex"] = "unknown"
            else:
                subject_dict[subject_id]["sex"] = "unknown"

        return subject_dict
    except Exception:
        return None


def _get_dataset_device_info(dataset_root: str) -> Dict[str, str]:
    """Extract device information from dataset_description.json or README.

    Returns
    -------
    Dict[str, str]
        Dictionary with amplifier, cap, and reference information.
    """
    device_info = {
        "amplifier": "EGI Geodesic EEG System",  # LLM 推断，需人类复核
        "cap": "Geodesic HydroCel 128-channel",  # LLM 推断，需人类复核
        "reference": "vertex (Cz)",  # LLM 推断，需人类复核
    }

    # Try to read dataset_description.json
    desc_file = os.path.join(dataset_root, "dataset_description.json")
    if os.path.exists(desc_file):
        try:
            with open(desc_file, "r", encoding="utf-8") as f:
                desc = json.load(f)
                # Check for EEGReference or other device info
                if "EEGReference" in desc:
                    device_info["reference"] = desc["EEGReference"]
        except Exception:
            pass

    return device_info


def _get_subject_metadata(
    subject_id: str,
    subject_dict: Optional[Dict[str, Dict[str, Any]]],
) -> Dict[str, str]:
    """Get metadata for a specific subject.

    Parameters
    ----------
    subject_id : str
        Subject identifier (e.g., "001", "02")
    subject_dict : Optional[Dict[str, Dict[str, Any]]]
        Pre-loaded subject dictionary from participants.tsv

    Returns
    -------
    Dict[str, str]
        Subject metadata with age, sex, handedness
    """
    if subject_dict and subject_id in subject_dict:
        meta = subject_dict[subject_id]
        return {
            "age": meta.get("age", _SUBJECT_AGE_RANGE),
            "sex": meta.get("sex", "unknown"),
            "handedness": meta.get("handedness", "unknown"),  # LLM 推断，需人类复核
        }

    # Fallback to defaults
    return {
        "age": _SUBJECT_AGE_RANGE,
        "sex": "unknown",
        "handedness": "unknown",
    }


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename EGI channels to standard format if needed.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object

    Returns
    -------
    mne.io.BaseRaw
        Raw object with renamed channels
    """
    ch_names = raw.ch_names
    rename_map: Dict[str, str] = {}

    for ch in ch_names:
        # Check if channel matches EGI pattern (E1, E01, E001, etc.)
        if ch.startswith("E") and len(ch) <= 4:
            # Extract number and create standard EEG-XXX format
            num_str = ch[1:]
            try:
                num = int(num_str)
                if 1 <= num <= 128:
                    new_name = f"EEG-{str(num).zfill(3)}"
                    rename_map[ch] = new_name
            except ValueError:
                pass

    if rename_map:
        raw.rename_channels(rename_map)

    return raw


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap numeric event IDs to descriptive labels.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object with annotations

    Returns
    -------
    mne.io.BaseRaw
        Raw object with remapped annotations
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    new_descriptions = []
    for desc in raw.annotations.description:
        try:
            event_id = int(float(desc))
            new_desc = _REVERSE_EVENT_MAP.get(event_id, desc)
        except (ValueError, TypeError):
            new_desc = desc
        new_descriptions.append(new_desc)

    # Create new annotations with remapped descriptions
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)

    return raw


class OpenNeuroDS004151Kernel:
    """Stage1 kernel for OpenNeuro ds004151 dataset."""

    KERNEL_ID: str = "openneuro-ds004151-stage1"

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
            The modified raw object with channel names, montage, and metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", row.get("subject_id", "unknown"))

        # Determine dataset root from file path
        dataset_root = os.path.dirname(os.path.dirname(file_path))

        # Load subject metadata from participants.tsv
        subject_metadata = _load_participants_metadata(dataset_root)

        # Get subject-specific metadata
        subject_meta = _get_subject_metadata(subject_id, subject_metadata)

        # Get device information
        device_info = _get_dataset_device_info(dataset_root)

        # Rename channels to standard format BEFORE set_montage
        raw = _rename_channels(raw)

        # Set EGI HydroCel 128-channel montage
        try:
            montage = mne.channels.make_standard_montage(
                "GSN-HydroCel-128", head_size=0.095
            )
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            # Log warning but continue if montage fails
            print(f"Warning: Could not set montage for {file_path}: {e}")

        # Remap numeric event IDs to descriptive labels
        raw = _remap_annotations(raw)

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        eegunity_description = {
            "age": subject_meta["age"],
            "sex": subject_meta["sex"],
            "amplifier": device_info["amplifier"],
            "cap": device_info["cap"],
            "handedness": subject_meta["handedness"],
        }

        # Update raw.info["description"]
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS004151Kernel()