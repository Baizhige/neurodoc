"""OpenNeuro DS004626 stage1 kernel for EEGUnity.

Dataset: Loneliness & Social Threat Hypervigilance (Dot Probe Task)
Source: https://openneuro.org/datasets/ds004626 | DOI: 10.1111/psyp.14406

Paradigm: Dot probe task investigating hypervigilance to social threats in lonely individuals.
- 52 participants, 68 channels, 1000 Hz sampling rate
- Events: stimulus triggers (146, 186, 206, 236, 142, 210), response (208), trial boundary (998)
- Admin markers to exclude: 255, 999

Channel info: Standard 64-channel EEG cap (10-20 system) + 4 EOG channels.
Amplifier/cap info not available in metadata; set to "unknown" per KERNEL_RULEBOOK.
Age/sex also unavailable; set to "unknown" with LLM inference marker.

Annotator: LLM, 2026-04-10
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Event code definitions
_STIMULUS_EVENTS = {
    146: "stim_condition_A",
    186: "stim_condition_B",
    206: "stim_condition_C",
    236: "stim_condition_D",
    142: "stim_condition_E",
    210: "stim_condition_F",
}

_RESPONSE_EVENTS = {
    208: "response_button_press",
}

_TRIAL_BOUNDARY_EVENTS = {
    998: "trial_boundary_ITI",
}

_ADMIN_EVENTS = {
    255: "admin_sync",
    999: "admin_trial_end",
}

_ALL_EVENT_IDS = {
    **_STIMULUS_EVENTS,
    **_RESPONSE_EVENTS,
    **_TRIAL_BOUNDARY_EVENTS,
    **_ADMIN_EVENTS,
}

# Standard 64-channel EEG names (10-20 system)
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF6", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
]

_EOG_CHANNEL_NAMES = ["EOG_left", "EOG_right", "EOG_central", "EOG_vertical"]

_AMPLIFIER = "unknown"
_CAP = "unknown"


def _detect_channel_pattern(ch_names: List[str]) -> Dict[str, str]:
    """Detect and map non-standard channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    eeg_candidates = []
    eog_candidates = []

    for ch in ch_names:
        ch_upper = ch.upper()
        if any(prefix in ch_upper for prefix in ["EOG", "VEO", "HEO", "ELEC"]):
            eog_candidates.append(ch)
        elif ch not in _STANDARD_64_CHANNELS and ch not in _EOG_CHANNEL_NAMES:
            eeg_candidates.append(ch)

    n_eeg = min(len(eeg_candidates), 64)
    for i, orig_ch in enumerate(sorted(eeg_candidates, key=lambda x: (len(x), x))[:n_eeg]):
        if i < len(_STANDARD_64_CHANNELS):
            if orig_ch != _STANDARD_64_CHANNELS[i]:
                rename_map[orig_ch] = _STANDARD_64_CHANNELS[i]

    eog_standard_map = {
        "VEO": "EOG_vertical",
        "HEO": "EOG_horizontal",
        "EOG_L": "EOG_left",
        "EOG_R": "EOG_right",
    }
    for orig_ch in eog_candidates:
        for pattern, standard in eog_standard_map.items():
            if pattern.upper() in orig_ch.upper():
                if orig_ch != standard:
                    rename_map[orig_ch] = standard
                break

    return rename_map


def _create_annotations_from_events(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Create MNE annotations from event codes in the raw data."""
    sfreq = raw.info["sfreq"]

    if raw.annotations:
        orig_descriptions = raw.annotations.description
        onset_times = raw.annotations.onset
        durations = raw.annotations.duration

        new_descriptions = []
        for desc in orig_descriptions:
            try:
                code = int(float(desc))
                if code in _ALL_EVENT_IDS:
                    new_descriptions.append(_ALL_EVENT_IDS[code])
                else:
                    new_descriptions.append(str(desc))
            except (ValueError, TypeError):
                new_descriptions.append(str(desc))

        return mne.Annotations(
            onset=list(onset_times),
            duration=list(durations),
            description=new_descriptions,
        )

    return mne.Annotations(onset=[], duration=[], description=[])


def _get_subject_info(row: pd.Series) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv or row data."""
    return {
        "age": str(row.get("age", "unknown")),
        "sex": str(row.get("sex", "unknown")),
        "handedness": str(row.get("handedness", "unknown")),
    }


class EEGUnityKernel:
    KERNEL_ID = "openneuro_ds004626_stage1"

    def __init__(self):
        self.kernel_version = "1.0.0"
        self.dataset_name = "openneuro_ds004626"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data."""
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))
        sfreq = raw.info.get("sfreq", 1000)

        # Detect and apply channel renaming
        rename_map = _detect_channel_pattern(raw.ch_names)
        if rename_map:
            raw.rename_channels(rename_map)

        # Create annotations from events
        annotations = _create_annotations_from_events(raw)
        if len(annotations) > 0:
            raw.set_annotations(annotations)

        # Extract subject info and add to raw.info
        subject_info = _get_subject_info(row)
        raw.info["subject_info"] = {
            "his_id": subject_id,
            "age": subject_info.get("age"),
            "sex": subject_info.get("sex"),
        }

        return raw

    def get_eegunity_description(self) -> Dict[str, str]:
        """Return EEGUnity metadata description."""
        return {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": "unknown",
        }


KERNEL = EEGUnityKernel()