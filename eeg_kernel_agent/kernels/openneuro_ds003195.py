"""OpenNeuro ds003195 stage1 kernel for EEGUnity.

Parkinson's disease placebo control group resting-state EEG dataset.
19 channels, 200 Hz sampling rate, recorded at Hospital Universitario
de San Vicente Fundación (Antioquia, Colombia).

Source: https://openneuro.org/datasets/ds003195
Paper: DOI 10.3389/fnins.2022.841428

Channel naming note: This dataset uses standard 10-20 electrode names
in Spanish publications; channel names are assumed to follow standard
naming conventions with 19 EEG channels. Channels are renamed to
standard names before setting montage.

Events: The dataset uses Spanish event labels (ojos cerrados/abiertos,
hiperventilacion, recuperacion, photic stimulation variants). Event
label normalization is handled in the apply() method.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ---------------------------------------------------------------------------
# Subject metadata
# Source: Paper DOI 10.3389/fnins.2022.841428
# - PD patients, age range 45-75 years (estimated from inclusion criteria)
# - Exact ages per subject not published in accessible documents
# - Sex distribution not published in accessible documents
# Annotator: LLM, 2026-04-08
# NOTE: All values are "unknown" because the source paper and OpenNeuro
# dataset README do not provide individual subject metadata in an easily
# parseable format. Human review needed to extract from clinical records.
# ---------------------------------------------------------------------------
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Format: sub-XX -> {"age": str, "sex": str, "handedness": str}
    # All fields set to "unknown" pending human verification.
}

# ---------------------------------------------------------------------------
# Channel rename map
# Assumption: The dataset uses 19-channel EEG with standard 10-20 locations.
# Common 19-channel configurations include:
#   FP1, FP2, F7, F3, Fz, F4, F8, T7, C3, Cz, C4, T8, P7, P3, Pz, P4, P8, O1, O2
#   (extended 10-20 with additional temporal channels)
# Source: LLM inference based on 19-channel standard EEG montages
# Annotator: LLM, 2026-04-08 — needs human verification against actual data
# ---------------------------------------------------------------------------
_STANDARD_19_CHANNEL_MAP: Dict[str, str] = {
    "FP1": "Fp1",
    "FP2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
}


def _get_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    match = re.search(r"sub-(\w+)", file_path)
    return match.group(1) if match else "unknown"


def _get_subject_metadata(subject_id: str) -> Tuple[str, str, str]:
    """Get subject metadata from subject dict or return unknown values.

    Returns:
        Tuple of (age, sex, handedness)
    """
    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return (
            info.get("age", "unknown"),
            info.get("sex", "unknown"),
            info.get("handedness", "unknown"),
        )
    return ("unknown", "unknown", "unknown")


def _normalize_event_label(label: str) -> str:
    """Normalize Spanish event labels to canonical forms.

    Merges variant spellings:
    - fotoestimulacion -> photic stimulation
    - hipervantilacion 4 -> hiperventilacion 4

    Parameters
    ----------
    label : str
        Original event label from annotations.

    Returns
    -------
    str
        Normalized event label.
    """
    label_lower = label.lower().strip()

    # Merge Spanish photic stimulation with English
    if label_lower == "fotoestimulacion":
        return "photic stimulation"

    # Fix typo in hyperventilation period 4
    if label_lower == "hipervantilacion 4":
        return "hiperventilacion 4"

    return label


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for channels that need standardization.

    Handles common variations in channel naming:
    - Case variations (fp1 vs Fp1)
    - Prefix/suffix variations

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object.

    Returns
    -------
    Dict[str, str]
        Mapping from old channel names to new standardized names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Check for case variations
    for std_name, canonical in _STANDARD_19_CHANNEL_MAP.items():
        if std_name in existing_names and std_name != canonical:
            rename_map[std_name] = canonical
        # Check lowercase versions
        for ch in existing_names:
            if ch.lower() == std_name.lower() and ch != canonical:
                rename_map[ch] = canonical
                break

    return rename_map


def _set_standard_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard 10-20 montage.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object.

    Returns
    -------
    mne.io.BaseRaw
        Raw with montage set if possible.
    """
    try:
        # Try standard_1020 first, fall back to standard_1005
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="warn")
    except Exception:
        # If standard_1020 fails, try standard_1005
        try:
            montage = mne.channels.make_standard_montage("standard_1005")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # Montage setting failed, continue without it
            pass

    return raw


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap annotation descriptions to normalized labels.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object with annotations.

    Returns
    -------
    mne.io.BaseRaw
        Raw with remapped annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    # Normalize all annotation descriptions
    new_descriptions = []
    for desc in raw.annotations.description:
        new_descriptions.append(_normalize_event_label(desc))

    # Create new annotations with normalized labels
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )

    raw.set_annotations(new_annotations)
    return raw


@dataclass
class OpenNeuroDS003195Kernel:
    """Stage1 kernel for the OpenNeuro ds003195 dataset (Placebo Neuroepo)."""

    KERNEL_ID: str = "openneuro-ds003195-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : object
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : pandas.Series
            Locator row with at least 'File Path'.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")

        # -----------------------------------------------------------------
        # Step 1: Get subject information
        # -----------------------------------------------------------------
        subject_id = _get_subject_id(file_path)
        age, sex, handedness = _get_subject_metadata(subject_id)

        # -----------------------------------------------------------------
        # Step 2: Rename channels to standard names (before set_montage)
        # -----------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Only rename channels that exist and need renaming
            valid_renames = {
                old: new for old, new in rename_map.items()
                if old in raw.ch_names
            }
            if valid_renames:
                raw.rename_channels(valid_renames)

        # -----------------------------------------------------------------
        # Step 3: Set standard montage (after channel renaming)
        # -----------------------------------------------------------------
        raw = _set_standard_montage(raw)

        # -----------------------------------------------------------------
        # Step 4: Remap annotations to normalized labels
        # -----------------------------------------------------------------
        raw = _remap_annotations(raw)

        # -----------------------------------------------------------------
        # Step 5: Build and write eegunity_description
        # -----------------------------------------------------------------
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "unknown",  # Not specified in accessible docs
                "cap": "unknown",  # Not specified in accessible docs
                "handedness": handedness,
            },
        }

        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003195Kernel()