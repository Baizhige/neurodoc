"""OpenNeuro ds004816 stage1 kernel for EEGUnity.

EEG Attention RSVP Experiment investigating neural dynamics of prioritizing
task-relevant information using stimuli composed of small letters on large objects.

Source: https://openneuro.org/datasets/ds004816
Reference: DOI 10.51628/001c.21174
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne


# Raw meta event mapping: original annotations -> canonical labels
# LLM 推断，需人类复核 - based on analysis.md event structure
_RAW_EVENT_MAP: Dict[str, str] = {
    "Event/E 1": "E 1",
    "Event/E 2": "E 2",
    "Event/E 3": "E 3",
}

# All valid raw-level event codes
_RAW_EVENT_IDS: Dict[str, int] = {
    "E 1": 1,
    "E 2": 2,
    "1": 3,
    "0": 4,
    "E 3": 5,
}

# Amplifier information - LLM 推断，需人类复核
# Based on standard EEG lab practices for RSVP experiments at 1000 Hz
_AMPLIFIER: str = "unknown"  # LLM 推断，需人类复核

# Electrode cap type - LLM 推断，需人类复核
_CAP: str = "unknown"  # LLM 推断，需人类复核


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 10-20 standard naming.

    This dataset has 63 EEG channels following standard 10-20 system.
    LLM 推断，需人类复核 - based on typical RSVP experiment setups.
    """
    rename_map: Dict[str, str] = {}

    # Standard 10-20 channel names (63 channels typical for high-density caps)
    standard_channels = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
        "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
        "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO8", "PO10",
        "O1", "Oz", "O2",
        "I1", "Iz", "I2",
    ]

    existing_names = set(raw.ch_names)
    for ch_name in existing_names:
        # Check if channel already follows standard naming
        if ch_name in standard_channels:
            continue
        # Handle common non-standard formats
        if ch_name.startswith("EEG ") or ch_name.startswith("EEG-"):
            base_name = ch_name.replace("EEG ", "").replace("EEG-", "")
            if base_name in standard_channels:
                rename_map[ch_name] = base_name
        # Handle numbered channels (e.g., "01", "02")
        elif re.match(r"^\d+$", ch_name):
            continue  # Skip purely numeric names for now

    return rename_map


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name.

    This dataset contains RSVP attention conditions.
    LLM 推断，需人类复核.
    """
    basename = os.path.basename(file_path).lower()
    return "RSVP"  # LLM 推断，需人类复核


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap annotation descriptions to canonical raw meta labels.

    Handles both 'Event/E x' and 'E x' formats.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    new_descriptions = []
    for desc in raw.annotations.description:
        # Apply mapping if exists, otherwise keep original
        new_desc = _RAW_EVENT_MAP.get(desc, desc)
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


@dataclass
class OpenNeuroDS004816Kernel:
    """Stage1 kernel for OpenNeuro ds004816 RSVP Attention dataset."""

    KERNEL_ID: str = "openneuro-ds004816-stage1"

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
            The modified Raw object with standardized metadata.
        """
        file_path = row.get("File Path", "")

        # === Channel renaming (BEFORE set_montage) ===
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # === Set montage ===
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Skip montage if not applicable

        # === Detect paradigm ===
        paradigm = _detect_paradigm(file_path)

        # === Extract subject info from row ===
        subject_id = str(row.get("subject_id", "unknown"))
        age = str(row.get("age", "unknown"))
        sex = str(row.get("sex", "unknown")).lower()
        handedness = str(row.get("handedness", "unknown")).lower()

        # Normalize sex values
        if sex in ("m", "male", "M", "Male"):
            sex = "male"
        elif sex in ("f", "female", "F", "Female"):
            sex = "female"
        else:
            sex = "unknown"

        # === Build description JSON ===
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, str):
            try:
                original_desc = json.loads(original_desc).get("original_description", original_desc)
            except (json.JSONDecodeError, TypeError):
                pass

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # === Remap annotations to canonical raw meta labels ===
        raw = _remap_annotations(raw)

        return raw


KERNEL = OpenNeuroDS004816Kernel()