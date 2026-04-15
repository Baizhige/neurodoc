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
# Source: analysis.md / paper analysis of trigger codes
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
# Order follows standard 64-channel caps (BioSemi, BrainProducts, etc.)
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

# EOG channel names (standard 4-channel EOG)
_EOG_CHANNEL_NAMES = ["EOG_left", "EOG_right", "EOG_central", "EOG_vertical"]

# Reference: https://doi.org/10.1111/psyp.14406
# 64-channel EEG + 4 EOG = 68 channels
# LLM 推断，需人类复核
_AMPLIFIER = "unknown"  # LLM 推断，需人类复核
_CAP = "unknown"  # LLM 推断，需人类复核


def _detect_channel_pattern(ch_names: List[str]) -> Dict[str, str]:
    """Detect and map non-standard channel names to standard 10-20 names.

    OpenNeuro datasets may use various naming conventions:
    - BrainVision: 'EEG 001', 'EEG 002', etc.
    - BioSemi: 'A1', 'A2', etc.
    - Generic: 'CH1', 'CH2', etc.

    This function attempts to map numbered channels to standard positions.
    LLM 推断，需人类复核

    Parameters
    ----------
    ch_names : List[str]
        Original channel names from the raw file.

    Returns
    -------
    Dict[str, str]
        Rename map from original to standard names.
    """
    rename_map: Dict[str, str] = {}

    # Common patterns for numbered EEG channels
    eeg_patterns = [
        (r"^EEG\s*(\d+)$", "EEG  "),  # BrainVision: "EEG 001" -> position by number
        (r"^A(\d+)$", "A"),           # BioSemi: "A1" -> position by number
        (r"^CH(\d+)$", "CH"),         # Generic: "CH1" -> position by number
        (r"^E(\d+)$", "E"),           # EGI: "E1" -> position by number
    ]

    # First, identify which channels are EEG vs EOG vs other
    eeg_candidates = []
    eog_candidates = []
    other_channels = []

    for ch in ch_names:
        ch_upper = ch.upper()
        if any(prefix in ch_upper for prefix in ["EOG", "VEO", "HEO", "ELEC"]):
            eog_candidates.append(ch)
        elif any(pattern.match(ch) for pattern, _ in eeg_patterns if _):
            # Check if it matches EEG patterns
            for pattern_str, _ in eeg_patterns:
                import re
                if re.match(pattern_str, ch):
                    eeg_candidates.append(ch)
                    break
            else:
                other_channels.append(ch)
        else:
            # Check if it's already a standard name or something else
            if ch not in _STANDARD_64_CHANNELS and ch not in _EOG_CHANNEL_NAMES:
                other_channels.append(ch)
            else:
                pass  # Already standard or EOG

    # For standard 64-channel setups, assume first 64 EEG candidates map to standard positions
    # This is a simplification; actual mapping may vary by cap manufacturer
    n_eeg = min(len(eeg_candidates), 64)
    for i, orig_ch in enumerate(sorted(eeg_candidates, key=lambda x: (len(x), x))[:n_eeg]):
        if i < len(_STANDARD_64_CHANNELS):
            if orig_ch != _STANDARD_64_CHANNELS[i]:
                rename_map[orig_ch] = _STANDARD_64_CHANNELS[i]

    # Map EOG channels to standard names
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
    """Create MNE annotations from event codes in the raw data.

    Reads events from raw.annotations or raw.find_events() and maps
    numeric codes to human-readable descriptions.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw MNE object containing event information.

    Returns
    -------
    mne.Annotations
        Annotated events with standardized descriptions.
    """
    sfreq = raw.info["sfreq"]

    # Try to get events from annotations first (BIDS format often stores here)
    if raw.annotations:
        # Map existing annotations to standard event descriptions
        orig_descriptions = raw.annotations.description
        onset_times = raw.annotations.onset
        durations = raw.annotations.duration

        # Convert numeric annotations to event descriptions
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
            onset=onset_times,
            duration=list(durations),
            description=new_descriptions,
        )

    # Fallback: use mne.find_events on STIM channels
    try:
        events = mne.find_events(raw, min_duration=1 / sfreq, verbose=False)
        if len(events) > 0:
            # Create onset times from events
            onsets = events[:, 0] / sfreq
            codes = events[:, 2]

            descriptions = []
            for code in codes:
                if code in _ALL_EVENT_IDS:
                    descriptions.append(_ALL_EVENT_IDS[code])
                else:
                    descriptions.append(f"event_{code}")

            return mne.Annotations(
                onset=onsets.tolist(),
                duration=[0.0] * len(onsets),
                description=descriptions,
            )
    except Exception:
        pass

    # No events found, return empty annotations
    return mne.Annotations(onset=[], duration=[], description=[])


def _get_subject_info(row: pd.Series) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv or row data.

    Parameters
    ----------
    row : pd.Series
        Row from the dataset locator containing file path and metadata.

    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, handedness.
    """
    # Default values (unknown, LLM inference marker)
    subject_info = {
        "age": "unknown",       # LLM 推断，需人类复核
        "sex": "unknown",       # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }

    # Try to get from row if available
    if "age" in row and pd.notna(row["age"]):
        try:
            subject_info["age"] = str(int(float(row["age"])))
        except (ValueError, TypeError):
            subject_info["age"] = str(row["age"])

    if "sex" in row and pd.notna(row["sex"]):
        sex_val = str(row["sex"]).lower().strip()
        if sex_val in ["m", "male", "f", "female"]:
            subject_info["sex"] = "male" if sex_val in ["m", "male"] else "female"

    if "handedness" in row and pd.notna(row["handedness"]):
        handed_val = str(row["handedness"]).lower().strip()
        if handed_val in ["r", "right", "l", "left"]:
            subject_info["handedness"] = "right" if handed_val in ["r", "right"] else "left"

    return subject_info


def _try_set_montage(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 10-20 montage if channels are recognized.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw MNE object.
    """
    try:
        # Try standard 1020 montage first
        montage = mne.channels.make_standard_montage("standard_1020")
        # Pick only channels that exist in the raw data
        ch_names_lower = {ch.lower() for ch in raw.ch_names}
        montage_chs = []

        for ch_name in montage.ch_names:
            if ch_name.lower() in ch_names_lower:
                # Check if it's in raw (case-insensitive match)
                for raw_ch in raw.ch_names:
                    if raw_ch.lower() == ch_name.lower():
                        montage_chs.append(raw_ch)
                        break

        if len(montage_chs) >= 20:  # Only set if we have a reasonable number of channels
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        # If montage setting fails, continue without it
        pass


class OpenNeuroDS004626Kernel:
    """Stage1 kernel for OpenNeuro dataset DS004626.

    Loneliness & Social Threat Hypervigilance Dot Probe Task.
    52 participants performing dot probe task with social threat stimuli.

    Source: https://openneuro.org/datasets/ds004626
    DOI: 10.1111/psyp.14406

    Attributes
    ----------
    KERNEL_ID : str
        Unique kernel identifier.
    """

    KERNEL_ID: str = "openneuro-ds004626-stage1"

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
            Preprocessed raw object with updated metadata and annotations.
        """
        # Get original description
        original_desc = raw.info.get("description", "")

        # Extract subject metadata
        subject_info = _get_subject_info(row)

        # Build eegunity_description
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        rename_map = _detect_channel_pattern(raw.ch_names)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                # If renaming fails, keep original names
                pass

        # Set standard montage for recognized channels
        _try_set_montage(raw)

        # Create annotations from events
        annotations = _create_annotations_from_events(raw)
        raw.set_annotations(annotations)

        # Ensure channel types are set correctly
        for i, ch in enumerate(raw.ch_names):
            ch_upper = ch.upper()
            if "EOG" in ch_upper:
                try:
                    raw.set_channel_types({ch: "eog"})
                except Exception:
                    pass
            elif ch in _STANDARD_64_CHANNELS:
                try:
                    raw.set_channel_types({ch: "eeg"})
                except Exception:
                    pass

        return raw


KERNEL = OpenNeuroDS004626Kernel()