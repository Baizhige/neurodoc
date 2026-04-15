"""OpenNeuro DS004475 stage1 kernel for EEGUnity.

Mobile EEG split-belt walking study.
- 30 subjects
- 260 channels (includes motion capture)
- 512 Hz sampling rate
- Paradigm: split-belt treadmill walking with EEG and gait events

Source: https://openneuro.org/datasets/ds004475
"""

from __future__ import annotations

import re
from typing import Any, Dict

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Information
# Source: Dataset documentation / paper 10.1113/jp284505
# Note: Paper describes 30 participants but specific demographics not confirmed.
# Annotator: LLM, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    for i in range(1, 31)
}

# Standard 10-10 channels that may appear with various prefixes
_STANDARD_10_10_CHANNELS = {
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P5", "P1", "P2", "P6",
    "PO7", "PO3", "POz", "PO4", "PO8",
}

_STANDARD_10_10_CHANNELS_LOWER = {ch.lower() for ch in _STANDARD_10_10_CHANNELS}

# Motion capture / auxiliary channel patterns (to be excluded or renamed)
_MOTION_CHANNEL_PATTERNS = [
    r"^X[0-9]", r"^Y[0-9]", r"^Z[0-9]",
    r"^OP_", r"^TX", r"^TY", r"^TZ",
    r"_X$", r"_Y$", r"_Z$",
    r"^EMA_", r"^Mocap_",
    r"^Resp_", r"^GSR_",
    r"^TRG", r"^TRIGGER",
]

_COMPILED_MOTION_RE = re.compile(
    "|".join(_MOTION_CHANNEL_PATTERNS),
    re.IGNORECASE
)


def _is_motion_channel(ch_name: str) -> bool:
    """Check if channel is likely a motion capture or auxiliary channel."""
    return bool(_COMPILED_MOTION_RE.search(ch_name))


def _get_subject_info(row) -> Dict[str, str]:
    """Extract subject information from row or use defaults."""
    subject_id = row.get("subject_id", row.get("participant_id", ""))
    
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id]
    
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


eegunity_description: Dict[str, Any] = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "BrainAmp",
    "cap": "Standard 10-10",
    "handedness": "unknown",
}


class OpenNeuroDS004475Kernel:
    """Stage1 kernel for OpenNeuro DS004475 (Mobile EEG split-belt walking study)."""

    KERNEL_ID: str = "openneuro-ds004475-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
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
            The modified Raw object with updated metadata.
        """
        # Step 1: Get subject information
        subject_info = _get_subject_info(row)
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        # Step 2: Identify and mark motion capture channels as misc
        ch_names = raw.ch_names
        motion_channels = [ch for ch in ch_names if _is_motion_channel(ch)]
        
        if motion_channels:
            try:
                raw.set_channel_types({ch: "misc" for ch in motion_channels})
            except Exception:
                pass

        # Step 3: Rename BrainVision EEG channels to standard naming
        rename_map = {}
        for ch_name in ch_names:
            if ch_name.startswith("EEG"):
                match = re.match(r"^EEG\s*[-_]?\s*([A-Za-z0-9]+)$", ch_name, re.IGNORECASE)
                if match:
                    potential = match.group(1)
                    if potential.lower() in _STANDARD_10_10_CHANNELS_LOWER:
                        rename_map[ch_name] = potential
        
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass

        # Step 4: Set EEG reference (average projection) - avoid in-place computation timeout
        try:
            eeg_chs = [ch for ch in raw.ch_names 
                      if ch.lower() in _STANDARD_10_10_CHANNELS_LOWER or ch.startswith("EEG")]
            if eeg_chs:
                raw.set_eeg_reference("average", projection=True)
        except Exception:
            pass

        # Step 5: Set subject info
        raw._subject_info = {
            "id": row.get("subject_id", row.get("participant_id", "unknown")),
            "age": age,
            "sex": sex,
            "handedness": handedness,
        }

        return raw


KERNEL = OpenNeuroDS004475Kernel()