"""OpenNeuro DS006040 (gradCPT) stage1 kernel for EEGUnity.

Sustained Attention Task dataset using simultaneous EEG-fMRI.
64-channel EEG, 5000 Hz sampling rate.
Events: S155 (mountain standard), S245 (city target), S254 (button press).

Source: https://openneuro.org/datasets/ds006040
Reference: https://doi.org/10.1038/s41597-026-06616-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ============================================================================
# Channel Mapping for 64-channel EEG cap (standard 10-20 layout)
# ============================================================================
_64CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz",
    "EOG-left", "EOG-right", "EOG-up", "EOG-down",
    "ECG", "EMG-mentalis", "EMG-orbicularis",
]


def _build_64ch_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 64-channel standard montage."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    alias_groups = [
        ("Fp1", ["Fp1", "Fp 1", "EEG Fp1", "Fp_1"]),
        ("Fp2", ["Fp2", "Fp 2", "EEG Fp2", "Fp_2"]),
        ("Fpz", ["Fpz", "EEG Fpz"]),
        ("AF7", ["AF7", "AF 7", "EEG AF7"]),
        ("AF3", ["AF3", "AF 3", "EEG AF3"]),
        ("AFz", ["AFz", "EEG AFz"]),
        ("AF4", ["AF4", "AF 4", "EEG AF4"]),
        ("AF8", ["AF8", "AF 8", "EEG AF8"]),
        ("F7", ["F7", "F 7", "EEG F7"]),
        ("F5", ["F5", "F 5", "EEG F5"]),
        ("F3", ["F3", "F 3", "EEG F3"]),
        ("F1", ["F1", "F 1", "EEG F1"]),
        ("Fz", ["Fz", "EEG Fz"]),
        ("F2", ["F2", "F 2", "EEG F2"]),
        ("F4", ["F4", "F 4", "EEG F4"]),
        ("F6", ["F6", "F 6", "EEG F6"]),
        ("F8", ["F8", "F 8", "EEG F8"]),
        ("FT7", ["FT7", "FT 7", "EEG FT7"]),
        ("FC5", ["FC5", "FC 5", "EEG FC5"]),
        ("FC3", ["FC3", "FC 3", "EEG FC3"]),
        ("FC1", ["FC1", "FC 1", "EEG FC1"]),
        ("FCz", ["FCz", "EEG FCz"]),
        ("FC2", ["FC2", "FC 2", "EEG FC2"]),
        ("FC4", ["FC4", "FC 4", "EEG FC4"]),
        ("FC6", ["FC6", "FC 6", "EEG FC6"]),
        ("FT8", ["FT8", "FT 8", "EEG FT8"]),
        ("T7", ["T7", "T 7", "EEG T7", "T3"]),
        ("C5", ["C5", "C 5", "EEG C5"]),
        ("C3", ["C3", "C 3", "EEG C3"]),
        ("C1", ["C1", "C 1", "EEG C1"]),
        ("Cz", ["Cz", "EEG Cz"]),
        ("C2", ["C2", "C 2", "EEG C2"]),
        ("C4", ["C4", "C 4", "EEG C4"]),
        ("C6", ["C6", "C 6", "EEG C6"]),
        ("T8", ["T8", "T 8", "EEG T8", "T4"]),
        ("TP7", ["TP7", "TP 7", "EEG TP7"]),
        ("CP5", ["CP5", "CP 5", "EEG CP5"]),
        ("CP3", ["CP3", "CP 3", "EEG CP3"]),
        ("CP1", ["CP1", "CP 1", "EEG CP1"]),
        ("CPz", ["CPz", "EEG CPz"]),
        ("CP2", ["CP2", "CP 2", "EEG CP2"]),
        ("CP4", ["CP4", "CP 4", "EEG CP4"]),
        ("CP6", ["CP6", "CP 6", "EEG CP6"]),
        ("TP8", ["TP8", "TP 8", "EEG TP8"]),
        ("P7", ["P7", "P 7", "EEG P7"]),
        ("P5", ["P5", "P 5", "EEG P5"]),
        ("P3", ["P3", "P 3", "EEG P3"]),
        ("P1", ["P1", "P 1", "EEG P1"]),
        ("Pz", ["Pz", "EEG Pz"]),
        ("P2", ["P2", "P 2", "EEG P2"]),
        ("P4", ["P4", "P 4", "EEG P4"]),
        ("P6", ["P6", "P 6", "EEG P6"]),
        ("P8", ["P8", "P 8", "EEG P8"]),
        ("PO7", ["PO7", "PO 7", "EEG PO7"]),
        ("PO3", ["PO3", "PO 3", "EEG PO3"]),
        ("POz", ["POz", "EEG POz"]),
        ("PO4", ["PO4", "PO 4", "EEG PO4"]),
        ("PO8", ["PO8", "PO 8", "EEG PO8"]),
        ("O1", ["O1", "O 1", "EEG O1"]),
        ("Oz", ["Oz", "EEG Oz"]),
        ("O2", ["O2", "O 2", "EEG O2"]),
        ("Iz", ["Iz", "EEG Iz"]),
        ("EOG-left", ["EOG-left", "EOG L", "EOGL", "Veog-left"]),
        ("EOG-right", ["EOG-right", "EOG R", "EOGR", "Veog-right"]),
        ("EOG-up", ["EOG-up", "EOG U", "EOGU"]),
        ("ECG", ["ECG", "ecg", "Cardiac"]),
        ("EMG-mentalis", ["EMG-mentalis", "EMG1", "EMG-mental"]),
        ("EMG-orbicularis", ["EMG-orbicularis", "EMG2", "EMG-orb"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


# ============================================================================
# Event Mapping
# ============================================================================
_EVENT_DESCRIPTION_MAP = {
    "155": "S155",
    "245": "S245",
    "254": "S254",
    "sync": "Sync On",
    "qrs": "qrs",
    "tr": "TR",
    "t1": "T 1",
    "[]": "[]",
}


def _parse_event_description(desc: str) -> str:
    """Parse event description to canonical form."""
    if not desc or desc == "":
        return "[]"

    desc_clean = str(desc).strip()
    desc_lower = desc_clean.lower()

    if desc_clean in ("155", "S155"):
        return "S155"
    if desc_clean in ("245", "S245"):
        return "S245"
    if desc_clean in ("254", "S254"):
        return "S254"

    if "sync" in desc_lower:
        return "Sync On"
    if desc_lower in ("qrs", "q r s", "cardiac"):
        return "qrs"
    if desc_lower in ("tr", "trigger", "repetition"):
        return "TR"
    if desc_lower in ("t1", "t 1", "marker t1"):
        return "T 1"

    if desc_clean in ("[]", "empty", "null", ""):
        return "[]"

    return desc_clean


# ============================================================================
# Kernel Class
# ============================================================================
class OpenNeuroDS006040Kernel:
    """EEGUnity kernel for OpenNeuro DS006040 (gradCPT EEG-fMRI dataset)."""

    eegunity_description = {
        "age": "unknown",
        "sex": "unknown",
        "amplifier": "BrainAmp MR",
        "cap": "Brain Products 64-channel",
        "handedness": "unknown",
    }

    # Target sampling rate after preprocessing (downsample from 5000 Hz)
    TARGET_SFREQ = 500.0

    # Channel types for non-EEG channels
    NON_EEG_CHANNEL_TYPES = {
        "ECG": "ecg",
        "EOG-left": "eog",
        "EOG-right": "eog",
        "EOG-up": "eog",
        "EOG-down": "eog",
        "EMG-mentalis": "emg",
        "EMG-orbicularis": "emg",
    }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply preprocessing pipeline to a raw EEG recording."""
        # ----------------------------------------------------------------
        # 1. Load data into memory
        # ----------------------------------------------------------------
        if not raw.preload:
            raw.load_data(verbose=False)

        # ----------------------------------------------------------------
        # 2. Rename channels to standard names
        # ----------------------------------------------------------------
        rename_map = _build_64ch_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map, verbose=False)

        # ----------------------------------------------------------------
        # 3. Set channel types for non-EEG channels
        # ----------------------------------------------------------------
        ch_type_map = {}
        for ch_name, ch_type in self.NON_EEG_CHANNEL_TYPES.items():
            if ch_name in raw.ch_names:
                ch_type_map[ch_name] = ch_type
        if ch_type_map:
            raw.set_channel_types(ch_type_map, verbose=False)

        # ----------------------------------------------------------------
        # 4. Set standard montage
        # ----------------------------------------------------------------
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="warn", verbose=False)

        # ----------------------------------------------------------------
        # 5. Resample to target frequency
        #    NOTE: Raw objects do not have a .decimate() method.
        #    Use .resample() instead.
        # ----------------------------------------------------------------
        current_sfreq = raw.info["sfreq"]
        if current_sfreq > self.TARGET_SFREQ:
            raw.resample(self.TARGET_SFREQ, verbose=False)

        # ----------------------------------------------------------------
        # 6. Apply bandpass filter (0.1 – 100 Hz)
        # ----------------------------------------------------------------
        raw.filter(
            l_freq=0.1,
            h_freq=100.0,
            method="fir",
            fir_window="hamming",
            verbose=False,
        )

        # ----------------------------------------------------------------
        # 7. Apply notch filter for MRI gradient artifacts (50 Hz and harmonics)
        # ----------------------------------------------------------------
        notch_freqs = np.arange(50, min(101, self.TARGET_SFREQ / 2), 50)
        if len(notch_freqs) > 0:
            raw.notch_filter(notch_freqs, verbose=False)

        # ----------------------------------------------------------------
        # 8. Set EEG reference to average
        # ----------------------------------------------------------------
        raw.set_eeg_reference("average", projection=False, verbose=False)

        # ----------------------------------------------------------------
        # 9. Remap annotations to canonical event descriptions
        # ----------------------------------------------------------------
        if raw.annotations is not None and len(raw.annotations) > 0:
            new_descriptions = []
            for ann in raw.annotations:
                new_desc = _parse_event_description(ann["description"])
                new_descriptions.append(new_desc)
            raw.annotations.description[:] = new_descriptions

        return raw


# ============================================================================
# Module-level kernel instance (required by EEGUnity)
# ============================================================================
KERNEL = OpenNeuroDS006040Kernel()