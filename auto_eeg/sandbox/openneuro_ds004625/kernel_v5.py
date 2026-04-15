"""OpenNeuro ds004625 stage1 kernel for EEGUnity.

Dataset: Mind in Motion: Young Adults Walking Over Uneven Terrain
Source: https://openneuro.org/datasets/ds004625
284-channel high-density EEG, 500 Hz, 32 subjects.
Paradigm: Locomotor control during uneven terrain walking.

This kernel extends the generic BIDS kernel with dataset-specific
channel renaming and hardcoded amplifier metadata derived from
the accompanying reference papers.

Annotator: LLM (gpt-4o), 2025-01-15
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ---------------------------------------------------------------------------
# Constants derived from dataset documentation / reference papers
# ---------------------------------------------------------------------------
_SUBJECT_AGE: str = "unknown"
_SUBJECT_SEX: str = "unknown"
_AMPLIFIER: str = "BioSemi ActiveTwo"
_CAP: str = "BioSemi 256-channel Ag/AgCl"
_HANDEDNESS: str = "unknown"

# ---------------------------------------------------------------------------
# High-density channel naming (unique target names)
# ---------------------------------------------------------------------------
_BIOSEMI_10_20_MAP: Dict[str, str] = {
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T7": "T7", "C3": "C3", "Cz": "Cz", "C4": "C4", "T8": "T8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "Oz": "Oz", "O2": "O2",
    "AF7": "AF7", "AF3": "AF3", "AFz": "AFz", "AF4": "AF4", "AF8": "AF8",
    "F1": "F1", "F2": "F2",
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1",
    "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    "C1": "C1", "C2": "C2",
    "CP5": "CP5", "CP3": "CP3", "CP1": "CP1",
    "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
    "P1": "P1", "P2": "P2",
    "PO7": "PO7", "PO3": "PO3", "POz": "POz", "PO4": "PO4", "PO8": "PO8",
    "TP9": "TP9", "TP10": "TP10",
    "FT9": "FT9", "FT10": "FT10",
    "PO9": "PO9", "PO10": "PO10",
}


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from raw channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    used_targets: set = set()

    for src, dst in _BIOSEMI_10_20_MAP.items():
        if src in existing and dst not in used_targets:
            rename_map[src] = dst
            used_targets.add(dst)

    if "EMG-L" in existing:
        rename_map["EMG-L"] = "EMG-L"
    if "EMG-R" in existing:
        rename_map["EMG-R"] = "EMG-R"

    for prefix in ("EOG", "ECG", "REF", "GND"):
        for ch in raw.ch_names:
            if ch.startswith(prefix) and ch not in rename_map:
                rename_map[ch] = ch

    return rename_map


def _set_montage_safe(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard_1020 montage on raw, skipping unavailable channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        available = set(raw.ch_names)
        montage_names = set(montage.ch_names)
        common = available & montage_names

        if len(common) >= 20:
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass
    return raw


def _extract_bids_sidecar_fields(row) -> Dict[str, Any]:
    """Extract subject metadata from BIDS participants.tsv sidecar."""
    result = {
        "age": _SUBJECT_AGE,
        "sex": _SUBJECT_SEX,
        "handedness": _HANDEDNESS,
    }
    for key in ("age", "sex", "handedness"):
        if key in row and row[key] not in (None, ""):
            val = str(row[key]).strip()
            if key == "sex":
                val = val.lower()
                if val not in ("male", "female"):
                    val = "unknown"
            result[key] = val
    return result


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------

class OpenNeuroDS004625Kernel:
    """Stage1 kernel for OpenNeuro ds004625 (Mind in Motion dataset)."""

    KERNEL_ID: str = "openneuro-ds004625-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record."""
        subject_info = _extract_bids_sidecar_fields(row)

        raw = _set_montage_safe(raw)

        rename_map = _build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        description_dict = {
            "original_description": raw.info.get("description", ""),
        }

        subject_id = row.get("subject_id", "unknown") if hasattr(row, "get") else row.get("subject_id", "unknown")
        description_dict["kernel_id"] = self.KERNEL_ID
        description_dict["dataset_id"] = "openneuro_ds004625"
        description_dict["subject_id"] = subject_id

        raw.info["description"] = json.dumps(description_dict)

        age_str = str(subject_info.get("age", _SUBJECT_AGE))
        sex_str = str(subject_info.get("sex", _SUBJECT_SEX))
        handedness_str = str(subject_info.get("handedness", _HANDEDNESS))

        eegunity_description = {
            "age": age_str,
            "sex": sex_str,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": handedness_str,
        }

        setattr(udataset, 'eegunity_description', eegunity_description)

        return raw


KERNEL = OpenNeuroDS004625Kernel()