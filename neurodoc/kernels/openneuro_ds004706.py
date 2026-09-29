"""openneuro_ds004706 stage1 kernel for EEGUnity.

Spatial Memory and Non-Invasive Closed-Loop Stimulus Timing dataset.
High-density EEG (137 channels, 2048 Hz) recorded during virtual town
navigation with free/cued recall phases and closed-loop theta stimulation.

Source: https://openneuro.org/datasets/ds004706
Paper: 10.1037/xlm0001341
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ============================================================================
# Subject metadata
# ============================================================================
# Source: Dataset description states subject_age and subject_sex are missing.
# inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # All subjects have unknown age/sex per dataset documentation
}

# ============================================================================
# Device metadata (hardcoded based on paradigm characteristics)
# ============================================================================
# Source: High-density 137-channel EEG with 2048 Hz sampling suggests
# BrainProducts system (e.g., BrainAmp DC). Paper mentions "EEG data were
# recorded using a 128-channel ..." - specific system needs verification.
# inferred by LLM, needs human review
_DEVICE_AMPLIFIER = "unknown"  # Needs confirmation from paper/methodology
_DEVICE_CAP = "unknown"  # Ag/AgCl or similar, needs confirmation
_HANDEDNESS = "unknown"  # Not provided in dataset


# ============================================================================
# Channel rename map
# ============================================================================
# Source: 137-channel system likely follows standard_1020 or extended layout.
# Channel naming convention unknown from available documentation.
# inferred by LLM, needs human review
def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.

    Assumes numbered EEG channels (EEG-001, EEG-002, etc.) may need
    mapping to standard 10-20 names if present.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common standard 10-20 electrodes for high-density systems
    standard_1020 = {
        "Fp1", "Fp2", "Fz", "F3", "F4", "F7", "F8",
        "Cz", "C3", "C4", "T7", "T8",
        "Pz", "P3", "P4", "P7", "P8",
        "O1", "O2", "Oz",
        "AFz", "AF3", "AF4", "AF7", "AF8",
        "F1", "F2", "F5", "F6",
        "FCz", "FC3", "FC4", "FC5", "FC6",
        "C1", "C2", "C5", "C6",
        "CPz", "CP3", "CP4", "CP5", "CP6",
        "P1", "P2", "P5", "P6",
        "POz", "PO3", "PO4", "PO7", "PO8",
    }

    # Pattern: EEG-001, EEG-002, etc.
    eeg_pattern = re.compile(r"^EEG-0*(\d+)$", re.IGNORECASE)

    for ch_name in existing_names:
        # Handle EEG-XXX format
        match = eeg_pattern.match(ch_name)
        if match:
            # Keep as-is for now, montage will handle spatial positioning
            # unless specific mapping is verified
            pass

    return rename_map


# ============================================================================
# Event mapping
# ============================================================================
# Source: analysis.md event structure table
_EVENT_ID_MAP: Dict[str, int] = {
    "FFR_REC_WORD": 1,       # Free-form recall word event
    "CUED_REC_STOP": 2,      # Cued recall stop marker
    "CUED_REC_CUE": 3,       # Cued recall cue onset
    "WORD": 4,               # Word stimulus onset (encoding)
    "REC_WORD": 5,           # Recalled word event
    "CUED_REC_WORD": 6,      # Cued recall word event
    "CLASSIFIER_WAIT": 7,    # Closed-loop classifier waiting
    "POINTER_ON": 8,         # Spatial navigation pointer onset
    "CLASSIFIER": 9,         # Closed-loop classifier event
    "EFR_MARK": 10,          # EFR (encoding-phase) marker
    "CUED_REC_WORD_VV": 11,  # Cued recall word (video verified)
    "TRIAL_END": 12,         # Trial end marker
    "TRIAL_START": 13,        # Trial start marker
    "REC_STOP": 14,          # Recording stop marker
    "REC_START": 15,         # Recording start marker
}


def _remap_events_from_annotations(
    raw: mne.io.BaseRaw,
) -> mne.io.BaseRaw:
    """Remap annotation descriptions to canonical event names.

    OpenNeuro BIDS datasets may use numeric event codes or
    abbreviated labels. This function standardizes them.
    """
    annotations = raw.annotations

    if annotations is None or len(annotations) == 0:
        return raw

    # Create new descriptions based on known patterns
    new_descriptions = []
    for desc in annotations.description:
        desc_str = str(desc)

        # Check if already a canonical name
        if desc_str in _EVENT_ID_MAP:
            new_descriptions.append(desc_str)
        # Check numeric codes
        elif desc_str.isdigit():
            code = int(desc_str)
            # Reverse lookup
            for name, code_val in _EVENT_ID_MAP.items():
                if code_val == code:
                    new_descriptions.append(name)
                    break
            else:
                new_descriptions.append(f"admin: marker-{code}")
        else:
            # Keep original if not recognized
            new_descriptions.append(desc_str)

    # Update annotations
    new_annotations = mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )
    raw.set_annotations(new_annotations)

    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard montage based on channel count."""
    existing = set(raw.ch_names)

    # Try standard_1020 montage first (128 channels typically fits)
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        # Check how many channels match
        montage_names = set(montage.ch_names)
        overlap = existing & montage_names

        if len(overlap) >= 64:  # At least half the channels match
            # Pick only channels that exist in the data
            kept_channels = list(overlap & set(raw.ch_names))
            raw.set_montage(montage, on_missing="ignore")
        else:
            # Try biosemi128 or other high-density montages
            for montage_name in ["biosemi128", "biosemi160", "standard_1005"]:
                try:
                    montage = mne.channels.make_standard_montage(montage_name)
                    raw.set_montage(montage, on_missing="ignore")
                    break
                except Exception:
                    continue
    except Exception:
        # Montage setting failed, continue without it
        pass

    return raw


def _get_subject_info(row) -> Dict[str, str]:
    """Extract subject metadata from row or use defaults."""
    subject_id = row.get("participant_id", row.get("subject_id", "unknown"))

    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "handedness": info.get("handedness", "unknown"),
        }

    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": _HANDEDNESS,
    }


class OpenNeuroDs004706Kernel:
    """Stage1 kernel for openneuro_ds004706 dataset.

    Handles high-density EEG data from spatial memory and closed-loop
    stimulation paradigm. Applies channel standardization, event
    remapping, and metadata enrichment.
    """

    KERNEL_ID: str = "openneuro-ds004706-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels,
            events, and metadata.
        """
        # -----------------------------------------------------------------
        # 1. Channel renaming (before montage)
        # -----------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # -----------------------------------------------------------------
        # 2. Set montage for spatial information
        # -----------------------------------------------------------------
        raw = _set_montage_if_possible(raw)

        # -----------------------------------------------------------------
        # 3. Remap events to canonical names
        # -----------------------------------------------------------------
        raw = _remap_events_from_annotations(raw)

        # -----------------------------------------------------------------
        # 4. Set eegunity_description metadata
        # -----------------------------------------------------------------
        subject_info = _get_subject_info(row)

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DEVICE_AMPLIFIER,
                "cap": _DEVICE_CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDs004706Kernel()