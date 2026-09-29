"""OpenNeuro DS007172 stage1 kernel for EEGUnity.

EEG-Asymmetries Dataset: Multi-task EEG battery investigating hemispheric
asymmetries across resting state and four cognitive categorization tasks.

Source: https://openneuro.org/datasets/ds007172
Reference: 10.1080/1357650X.2025.2591660
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Annotator: Human, 2026-04-08
# Source: OpenNeuro dataset page (actiCAP mentioned in comments), 32-channel setup
_AMPLIFIER = "BrainAmp"
_CAP = "actiCAP 32-channel Ag/AgCl"

# Standard 32-channel 10-10 system names used by actiCAP for this dataset
# Annotator: LLM, 2026-04-08 - inferred by LLM, needs human review
_EEG_CHANNEL_NAMES = [
    "FP1", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
    "T7", "C3", "Cz", "C4", "T8", "CP5", "CP1", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8", "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "O2",
]


def _normalize_event_key(raw: mne.io.BaseRaw) -> Dict[int, str]:
    """Normalize BrainVision event descriptions to consistent format.

    BrainVision files may contain events with inconsistent spacing like
    'Stimulus/S 111' or 'Stimulus/S111'. This function creates a mapping
    that handles both variants.
    """
    mapping: Dict[int, str] = {}
    original_annotations = raw.annotations

    for i, desc in enumerate(original_annotations.description):
        desc_clean = desc.strip()
        # Normalize: remove spaces in trigger codes, keep paradigm prefix
        normalized = re.sub(r'S(\s*)(\d+)', r'S\2', desc_clean)
        mapping[i] = normalized

    return mapping


def _apply_channel_renaming(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-10 names if needed.

    BrainVision files from this dataset may use generic names like 'EEG001'.
    Renamed to standard names BEFORE set_montage() is called.

    Annotator: LLM, 2026-04-08 - inferred by LLM, needs human review
    Source: Inferring standard 32-channel actiCAP layout from dataset metadata
    """
    current_names = raw.ch_names

    # Check if channels already follow standard naming
    standard_count = sum(1 for name in current_names if name in _EEG_CHANNEL_NAMES)

    if standard_count >= 30:
        # Likely already using standard names
        return raw

    # Build rename map from numeric EEG names to standard names
    rename_map: Dict[str, str] = {}
    eeg_indices: List[int] = []

    for i, ch_name in enumerate(current_names):
        # Match patterns like EEG001, EEG-1, or just numeric suffixes
        match = re.match(r'EEG[-\s]?(\d+)', ch_name, re.IGNORECASE)
        if match:
            eeg_indices.append(i)
            idx = int(match.group(1)) - 1  # 0-based index
            if idx < len(_EEG_CHANNEL_NAMES):
                rename_map[ch_name] = _EEG_CHANNEL_NAMES[idx]

    if rename_map:
        raw.rename_channels(rename_map)

    return raw


def _rebuild_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rebuild annotations with consistent event labels.

    BrainVision events come in formats like 'Stimulus/S 111' or 'Stimulus/S111'.
    Normalize to 'Stimulus/S111' format for consistency.
    """
    original = raw.annotations

    new_descriptions: List[str] = []
    for desc in original.description:
        desc_stripped = desc.strip()
        # Normalize trigger code format: "Stimulus/S 111" -> "Stimulus/S111"
        # Pattern matches both space and no-space variants
        normalized = re.sub(r'^(Stimulus/S)\s+(\d+)$', r'\1\2', desc_stripped)
        new_descriptions.append(normalized)

    new_annotations = mne.Annotations(
        onset=original.onset,
        duration=original.duration,
        description=new_descriptions,
        orig_time=original.orig_time,
    )

    raw.set_annotations(new_annotations)
    return raw


@dataclass
class OpenNeuroDS007172Kernel:
    """Stage1 kernel for the OpenNeuro DS007172 EEG-Asymmetries dataset."""

    KERNEL_ID: str = "openneuro-ds007172-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object from BrainVision files.
        row
            Locator row (pandas.Series-like) with at least File Path, Subject ID.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with standardized metadata.
        """
        file_path = str(row.get("File Path", ""))
        subject_id = str(row.get("Subject ID", "unknown"))

        # Step 1: Channel renaming (BEFORE set_montage)
        raw = _apply_channel_renaming(raw)

        # Step 2: Set montage if possible
        try:
            # Use standard 32-channel 10-10 system
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If standard montage fails, skip gracefully
            pass

        # Step 3: Rebuild annotations with normalized event labels
        raw = _rebuild_annotations(raw)

        # Step 4: Build eegunity_description
        # Subject metadata: try to infer from dataset publications
        # Annotator: LLM, 2026-04-08 - inferred by LLM, needs human review
        subject_info: Dict[str, str] = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        # Check if subject info available from udataset
        if hasattr(udataset, 'subject_dict'):
            subject_dict = getattr(udataset, 'subject_dict', {})
            if subject_id in subject_dict:
                info = subject_dict[subject_id]
                subject_info["age"] = str(info.get("age", "unknown"))
                subject_info["sex"] = info.get("sex", "unknown").lower()
                subject_info["handedness"] = info.get("handedness", "unknown")

        # Get original description
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS007172Kernel()