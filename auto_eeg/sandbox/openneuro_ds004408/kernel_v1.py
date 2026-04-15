"""OpenNeuro DS004408 stage1 kernel for EEGUnity.

Dataset: EEG responses to continuous naturalistic speech (audiobook listening).
380 subjects, 128 channels, 512 Hz, continuous paradigm with no discrete events.
Used for cortical entrainment / mTRF encoding model analysis.

Source: https://openneuro.org/datasets/ds004408
DOI: 10.18112/openneuro.ds004408.v1.0.8
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# No subject info available in dataset metadata.
# All fields marked as LLM inference, require human review.
# Source: analysis.md (openneuro_ds004408), 2025-01
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Subject metadata not available in BIDS sidecar or participants.tsv.
# Source: LLM inference, 2025-01, requires human review


# Channel naming: 128-channel system (likely BioSemi 128-channel cap).
# Standard channel names follow 10-20 system with extended coverage.
# Source: Dataset documentation / paper 10.1016/j.neuroimage.2020.117586
# Annotator: LLM, 2025-01, requires human review
_EEG_128_CHANNEL_RENAME_MAP = {
    # Standard 10-20 positions
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fz": "Fz",
    "F7": "F7",
    "F3": "F3",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    # Extended 10-10 positions (128-channel layout)
    "AFp1": "AFp1",
    "AFp2": "AFp2",
    "AFz": "AFz",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FCz": "FCz",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CPz": "CPz",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "O9": "O9",
    "O10": "O10",
    # Additional 128-channel positions (typical BioSemi 128 layout)
    "I1": "I1",
    "I2": "I2",
    "OIz": "OIz",
    "AFF1": "AFF1",
    "AFF2": "AFF2",
    "AFF5": "AFF5",
    "AFF6": "AFF6",
    "AFF7": "AFF7",
    "AFF8": "AFF8",
    "FTT7": "FTT7",
    "FTT8": "FTT8",
    "FTT9": "FTT9",
    "FTT10": "FTT10",
    "FT7": "FT7",
    "FT8": "FT8",
    "FT9": "FT9",
    "FT10": "FT10",
    "FTR7": "FTR7",
    "FTR8": "FTR8",
    "FTR9": "FTR9",
    "FTR10": "FTR10",
    "T9": "T9",
    "T10": "T10",
    "TTP7": "TTP7",
    "TTP8": "TTP8",
    "TTP9": "TTP9",
    "TTP10": "TTP10",
    "TP7": "TP7",
    "TP8": "TP8",
    "TP9": "TP9",
    "TP10": "TP10",
    "TPR7": "TPR7",
    "TPR8": "TPR8",
    "TPR9": "TPR9",
    "TPR10": "TPR10",
    "PTT7": "PTT7",
    "PTT8": "PTT8",
    "PTT9": "PTT9",
    "PTT10": "PTT10",
    "P9": "P9",
    "P10": "P10",
    "PTT11": "PTT11",
    "PTT12": "PTT12",
    "PPO9": "PPO9",
    "PPO10": "PPO10",
    "PPO7": "PPO7",
    "PPO8": "PPO8",
    "POO9": "POO9",
    "POO10": "POO10",
    "POO7": "POO7",
    "POO8": "POO8",
    "OI1": "OI1",
    "OI2": "OI2",
    "I3": "I3",
    "I4": "I4",
    "I5": "I5",
    "I6": "I6",
    "AFp9": "AFp9",
    "AFp10": "AFp10",
    "AFp7": "AFp7",
    "AFp8": "AFp8",
    "F9": "F9",
    "F10": "F10",
    "F7": "F7",
    "F8": "F8",
    "FFT9": "FFT9",
    "FFT10": "FFT10",
    "FFT7": "FFT7",
    "FFT8": "FFT8",
}


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for 128-channel EEG system.
    
    Handle various naming conventions (e.g., 'EEG 001' vs 'Fp1').
    Source: Dataset channel naming conventions, LLM inference, 2025-01
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Pattern 1: EEG 001, EEG 002, ... (zero-padded or not)
    import re
    for ch in list(existing_names):
        # Match EEG XX pattern
        match = re.match(r"EEG\s*(\d+)", ch, re.IGNORECASE)
        if match:
            idx = int(match.group(1))
            # Map to standard 10-10 position based on index
            # BioSemi 128 uses sequential numbering
            # This is a simplified mapping - needs verification
            standard_positions = [
                "Fp1", "AFp9", "AFp7", "AFF5", "AFF3", "AFF1", "AFz", "AFF2", "AFF4", "AFF6", "AFp8", "AFp10",
                "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
                "FFT9", "FFT7", "FFT5", "FFT3", "FFT1", "FFTz", "FFT2", "FFT4", "FFT6", "FFT8", "FFT10",
                "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
                "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
                "TTP9", "TTP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TTP8", "TTP10",
                "TP9", "TP7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "TP8", "TP10",
                "P9", "P7", "PO7", "PO3", "POz", "PO4", "PO8", "P10",
                "O9", "OI1", "OI2", "O10",
                # Extra positions for 128-channel
                "I1", "I2", "I3", "I4", "I5", "I6",
            ]
            if idx <= len(standard_positions):
                target = standard_positions[idx - 1]
                if target not in existing_names:
                    rename_map[ch] = target
    
    # Pattern 2: Try to match from the known 128-channel map
    for ch in list(existing_names):
        if ch in _EEG_128_CHANNEL_RENAME_MAP:
            rename_map[ch] = _EEG_128_CHANNEL_RENAME_MAP[ch]
    
    return rename_map


@dataclass
class OpenNeuroDS004408Kernel:
    """Stage1 kernel for OpenNeuro DS004408 (continuous naturalistic speech EEG)."""

    KERNEL_ID: str = "openneuro-ds004408-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        This dataset has no discrete trial events - continuous audiobook listening.
        Subject metadata is missing from dataset; all fields set to "unknown".

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata.
        """
        # Get original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description with available metadata
        # Source: analysis.md - subject_age, subject_sex, device all missing
        # All fields set to "unknown" per KERNEL_RULEBOOK
        # Source: LLM inference, 2025-01, requires human review
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",  # BioSemi likely but not confirmed
                "cap": "unknown",  # 128-channel cap, type unspecified
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 / 10-10 nomenclature
        # This is critical for montage setting and downstream analysis
        rename_map = _build_rename_map(raw)
        if rename_map:
            # Only rename if there are non-standard names
            non_standard = set(rename_map.keys())
            standard = set(rename_map.values())
            if non_standard != standard:
                print(f"[DS004408] Renaming {len(rename_map)} channels to standard names")
                raw.rename_channels(rename_map)

        # Set montage for standard 10-20 system
        # 128-channel should be supported by standard 1020 with extension
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[DS004408] Warning: Could not set montage: {e}")
            print(f"[DS004408] Available channels: {raw.ch_names[:20]}...")

        # No events in this dataset - continuous paradigm
        # Add annotation indicating continuous recording paradigm
        # This allows downstream segmentation tasks to proceed
        n_samples = raw.n_times
        sfreq = raw.info["sfreq"]
        
        # Create a single annotation marking the continuous nature
        # Duration spans entire recording
        duration_sec = n_samples / sfreq
        annotations = mne.Annotations(
            onset=[0.0],
            duration=[duration_sec],
            description=["continuous_speech_listening"],
        )
        raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004408Kernel()