"""OpenNeuro ds003710 (APPLESEED) stage1 kernel for EEGUnity.

Longitudinal infant EEG dataset (4, 8, 12 months) with social/non-social 
stimuli. Events use BrainVision-style Stimulus/S codes that need remapping.

Source: https://openneuro.org/datasets/ds003710
Paper: 10.1016/j.dcn.2022.101163
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import mne
import numpy as np


# Event code mapping: Stimulus/S  N -> canonical label
# Source: Dataset documentation and event frequency analysis
# - S  1 (3424 occurrences) and S  2 (3316) = social stimuli (face, speech)
# - S  3 (1992) and S  4 (2024) = non-social stimuli (object, water)
# Annotator: LLM, 2026-01-15 (needs human verification of face/speech split)
_STIMULUS_CODE_MAP: Dict[str, str] = {
    "Stimulus/S  1": "face",    # Social: face stimulus
    "Stimulus/S  2": "speech",   # Social: speech stimulus
    "Stimulus/S  3": "object",   # Non-social: object stimulus
    "Stimulus/S  4": "water",    # Non-social: water stimulus
}

# Codes to exclude from epoching (admin/artifact markers)
_EXCLUDE_CODES: set = {
    "New Segment",
    "Comment",
    "Stimulus/boundary",
    "Stimulus/S  5",
    "Stimulus/S  6",
    "Stimulus/S  85",
    "Stimulus/S 255",
    "Time 0/",
    "experimenter-pause",
    "attention-getter",
}


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap BrainVision Stimulus/S codes to canonical event labels.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with original annotations.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with remapped annotation descriptions.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    original_descriptions = raw.annotations.description.copy()
    new_descriptions: List[str] = []

    for desc in original_descriptions:
        # Try direct mapping first
        if desc in _STIMULUS_CODE_MAP:
            new_descriptions.append(_STIMULUS_CODE_MAP[desc])
        elif desc in _EXCLUDE_CODES:
            # Mark excluded events with admin prefix for filtering later
            new_descriptions.append(f"admin: {desc}")
        else:
            # Keep unknown events as-is but prefixed
            new_descriptions.append(f"unknown: {desc}")

    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    return raw


def _rename_channels_standard1020(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if needed.

    APPLESEED dataset uses standard 32-channel infant EEG cap.
    Channels are typically named as 'EEG 001', 'EEG 002', etc.
    
    Source: APPLESEED pipeline documentation (10.1016/j.dcn.2022.101163)
    Assumes standard infant 32-channel layout (10-20 system).
    Annotator: LLM, 2026-01-15 (needs human verification)
    """
    # Standard 32-channel names for infant EEG (10-20 system)
    standard_32_channels = [
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "Tp7", "Cp3", "Cpz", "Cp4", "Tp8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "F1", "F2", "C1", "C2", "P1", "P2",
        "A1", "A2"  # Auxiliary/mastoid channels
    ]

    rename_map: Dict[str, str] = {}
    current_names = raw.ch_names

    for i, ch_name in enumerate(current_names):
        # Handle 'EEG 001' format
        if re.match(r"EEG\s*0*(\d+)", ch_name, re.IGNORECASE):
            idx = int(re.match(r"EEG\s*0*(\d+)", ch_name, re.IGNORECASE).group(1)) - 1
            if idx < len(standard_32_channels):
                rename_map[ch_name] = standard_32_channels[idx]
        # Handle 'E1', 'E2' format (BioSemi style)
        elif re.match(r"^E\d+$", ch_name):
            # BioSemi 32-channel layout - map sequentially
            if ch_name.startswith("E"):
                try:
                    idx = int(ch_name[1:]) - 1
                    if idx < len(standard_32_channels):
                        rename_map[ch_name] = standard_32_channels[idx]
                except ValueError:
                    pass

    if rename_map:
        # Only rename EEG-type channels, preserve EOG/EMG/misc
        eeg_chans = [ch for ch in raw.ch_names if ch.startswith("EEG") or 
                     re.match(r"^E\d+$", ch) or ch.startswith("eeg")]
        subset_rename = {k: v for k, v in rename_map.items() if k in eeg_chans}
        if subset_rename:
            raw.rename_channels(subset_rename)
            # Try to set standard 1020 montage
            try:
                raw.set_montage("standard_1020", on_missing="warn")
            except Exception:
                pass  # Montage setting is best-effort

    return raw


@dataclass
class APPLESEEDKernel:
    """Stage1 kernel for OpenNeuro ds003710 (APPLESEED infant EEG dataset).

    This kernel handles:
    - Remapping BrainVision-style Stimulus/S codes to canonical event labels
    - Setting eegunity_description metadata
    - Standard 10-20 channel naming for montage
    - High sampling rate (5000 Hz) noting for downstream processing
    """

    KERNEL_ID: str = "openneuro-ds003710-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single APPLESEED recording.

        Parameters
        ----------
        udataset : 
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            MNE Raw object loaded from BIDS format.
        row : 
            Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated annotations and metadata.
        """
        # Store original description
        original_desc = raw.info.get("description", "")

        # Subject info - all unknown for this dataset (not in BIDS)
        # Dataset contains infants at 4, 8, 12 months - specific ages not per-subject
        # Source: Dataset README - no participants.tsv with age data
        # Annotator: LLM, 2026-01-15 (needs human verification)
        subject_info = {
            "age": "unknown",      # Infant data, specific ages not recorded per subject
            "sex": "unknown",      # Sex not recorded in dataset
            "amplifier": "unknown", # Amplifier model not specified in metadata
            "cap": "unknown",       # Cap type not specified in metadata
            "handedness": "unknown" # Not applicable for infant population
        }

        # Build description JSON
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": subject_info
        }
        raw.info["description"] = json.dumps(description_dict)

        # Remap event annotations from Stimulus/S codes to canonical labels
        raw = _remap_annotations(raw)

        # Rename channels to standard 10-20 names (before set_montage)
        raw = _rename_channels_standard1020(raw)

        # Note high sampling rate for downstream processing
        if raw.info["sfreq"] > 1000:
            raw.info["sfreq_original"] = raw.info["sfreq"]

        return raw


KERNEL = APPLESEEDKernel()