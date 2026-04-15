"""PEERS (Penn Electrophysiology of Encoding and Retrieval Study) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004395
Source: https://openneuro.org/datasets/ds004395
Paper: DOI 10.1038/s41467-024-46926-0, DOI 10.31234/osf.io/64j58

This kernel handles the PEERS dataset which contains EEG recordings from 300 subjects
performing memory encoding and retrieval tasks (free recall, recognition memory).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# PEERS dataset uses BrainVision system with 128 EEG channels + 1 external reference
# Source: PEERS dataset documentation / paper supplementary materials
# Annotator: LLM 推断，需人类复核
_AMPLIFIER = "BrainAmp"
_CAP = "Ag/AgCl"

# Standard 10-20 system channel mapping for 128-channel system
# PEERS uses standard 10-20 electrode placement
# Source: Dataset README / paper methodology
# Annotator: LLM 推断，需人类复核
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    "AFp9", "AFp7", "AFp5", "AFp3", "AFpz", "AFp4", "AFp6", "AFp8", "AFp10",
    "Fp9", "Fp10",
    "AFF9", "AFF7", "AFF5", "AFF3", "AFFz", "AFF4", "AFF6", "AFF8", "AFF10",
    "FFT9", "FFT7", "FFT5", "FFT3", "FFT1", "FFTz", "FFT2", "FFT4", "FFT6", "FFT8", "FFT10",
    "FTT9", "FTT7", "FTT5", "FTT3", "FTT1", "FTTz", "FTT2", "FTT4", "FTT6", "FTT8", "FTT10",
    "TTP9", "TTP7", "TTP5", "TTP3", "TTP1", "TTPz", "TTP2", "TTP4", "TTP6", "TTP8", "TTP10",
    "TPP9", "TPP7", "TPP5", "TPP3", "TPP1", "TPPz", "TPP2", "TPP4", "TPP6", "TPP8", "TPP10",
    "PPO9", "PPO7", "PPO5", "PPO3", "PPOz", "PPO4", "PPO6", "PPO8", "PPO10",
    "POO9", "POO7", "POO5", "POO3", "POOz", "POO4", "POO6", "POO8", "POO10",
    "OO9", "OO1", "O1", "OOz", "Oz", "OO2", "OO2", "OO10",
    "CBC9", "CBC7", "CBC5", "CBC3", "CBC1", "CBCz", "CBC2", "CBC4", "CBC6", "CBC8", "CBC10",
    "CBB9", "CBB7", "CBB5", "CBB3", "CBB1", "CBBz", "CBB2", "CBB4", "CBB6", "CBB8", "CBB10",
]

# Event ID mapping for PEERS dataset
# Source: PEERS dataset event documentation
# Annotator: LLM 推断，需人类复核
_EVENT_ID_MAP = {
    "WORD": 1,
    "REC_WORD": 2,
    "REC_WORD_VV": 3,
    "RECOG_TARGET": 4,
    "RECOG_LURE": 5,
    "RECOG_RESP": 6,
    "RECOG_CONF": 7,
    "DISTRACTOR": 8,
    "REST_REWET": 9,
    "SESS_START": 10,
    "SESS_END": 11,
    "REC_START": 12,
    "START": 13,
    "STOP": 14,
    "BREAK_START": 15,
    "BREAK_STOP": 16,
}

# Reverse mapping for annotation creation
_EVENT_LABEL_MAP = {v: k for k, v in _EVENT_ID_MAP.items()}


def _detect_subject_info(row) -> Dict[str, str]:
    """Detect subject age and sex from available sources.

    Parameters
    ----------
    row : pandas.Series
        Locator row containing file path and metadata.

    Returns
    -------
    dict
        Dictionary with 'age', 'sex', 'handedness' keys.
    """
    # Default values - PEERS dataset does not provide subject age/sex in BIDS
    # Source: Dataset info field (subject_age: missing, subject_sex: missing)
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 naming.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object with current channel names.

    Returns
    -------
    dict
        Mapping from original to standardized channel names.
    """
    rename_map = {}
    existing = set(raw.ch_names)

    # Common alternative naming patterns
    alias_patterns = [
        # BrainVision-style
        (r"^EEG\s*(\d+)$", lambda m: f"EEG{int(m.group(1)):03d}"),
        # Extended 10-20 with leading zeros
        (r"^(\w+)\s*$", lambda m: m.group(1)),
    ]

    # Build rename map for non-standard names
    for ch in existing:
        # Skip non-EEG channels
        if ch.upper() in ["EOG", "ECG", "EMG", "REF", "MISC", "STIM"]:
            continue

        # Check if channel needs renaming to standard format
        # Pattern: EEG001 -> keep as is or map to standard
        if re.match(r"^EEG(\d+)$", ch):
            continue  # Keep BrainVision format as-is

        # Check if channel matches standard 10-20 (case-insensitive)
        if ch.upper() in [c.upper() for c in _STANDARD_1020_CHANNELS]:
            # Find exact case match
            for std_ch in _STANDARD_1020_CHANNELS:
                if ch.upper() == std_ch.upper():
                    if ch != std_ch:
                        rename_map[ch] = std_ch
                    break

    return rename_map


def _load_raw_file(file_path: str) -> mne.io.BaseRaw:
    """Load raw EEG file with automatic format detection.

    Parameters
    ----------
    file_path : str
        Path to EEG data file.

    Returns
    -------
    mne.io.BaseRaw
        Loaded raw EEG object.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".vhdr", ".eeg", ".vmrk"]:
        # BrainVision format
        raw = mne.io.read_raw_brainvision(file_path, preload=False, verbose=False)
    elif ext in [".edf"]:
        raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
    elif ext in [".bdf"]:
        raw = mne.io.read_raw_bdf(file_path, preload=False, verbose=False)
    elif ext in [".set"]:
        raw = mne.io.read_raw_eeglab(file_path, preload=False, verbose=False)
    elif ext in [".fif"]:
        raw = mne.io.read_raw_fif(file_path, preload=False, verbose=False)
    elif ext in [".gdf"]:
        raw = mne.io.read_raw_gdf(file_path, preload=False, verbose=False)
    else:
        # Try MNE auto-detection
        raw = mne.io.read_raw(file_path, preload=False, verbose=False)

    return raw


class PEERSKernel:
    """Stage1 kernel for the PEERS (Penn Electrophysiology of Encoding and Retrieval Study) dataset."""

    KERNEL_ID: str = "openneuro-ds004395-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single PEERS record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized events and metadata.
        """
        # Preserve original description
        original_description = raw.info.get("description", "")

        # Get subject information
        subject_info = _detect_subject_info(row)

        # Build eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 naming if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Rename BEFORE set_montage() as required
            existing_to_rename = {
                k: v for k, v in rename_map.items() if k in raw.ch_names
            }
            if existing_to_rename:
                mne.rename_channels(raw.info, existing_to_rename)

        # Set standard 10-20 montage for EEG channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in both
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) > 60:  # At least ~half of 128 channels
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If montage fails, continue without it
            pass

        # Process events from annotations or stim channel
        self._process_events(raw)

        return raw

    def _process_events(self, raw: mne.io.BaseRaw) -> None:
        """Process and standardize events in raw object.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object to process events for.
        """
        # Check for existing annotations
        if raw.annotations:
            # Map existing annotations to standardized event IDs
            self._remap_annotations(raw)
        else:
            # Try to extract events from data
            self._extract_stim_events(raw)

    def _remap_annotations(self, raw: mne.io.BaseRaw) -> None:
        """Remap existing annotations to standardized PEERS event labels.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object with annotations.
        """
        if not raw.annotations:
            return

        new_descriptions = []
        for desc in raw.annotations.description:
            # Check if description matches known event
            if desc in _EVENT_ID_MAP:
                new_descriptions.append(desc)
            elif desc in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                          "11", "12", "13", "14", "15", "16"]:
                # Numeric code - map to label
                code = int(desc)
                new_descriptions.append(_EVENT_LABEL_MAP.get(code, f"event_{code}"))
            elif desc.upper() in [k.upper() for k in _EVENT_ID_MAP]:
                # Case-insensitive match
                for key in _EVENT_ID_MAP:
                    if key.upper() == desc.upper():
                        new_descriptions.append(key)
                        break
            else:
                # Keep original description
                new_descriptions.append(desc)

        # Create new annotations with remapped descriptions
        new_annotations = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=new_descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annotations)

    def _extract_stim_events(self, raw: mne.io.BaseRaw) -> None:
        """Extract events from stimulation channels.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object to extract events from.
        """
        # Find stimulus channels
        stim_chs = mne.pick_types(raw.info, stim=True, meg=False, eeg=False)
        misc_chs = mne.pick_types(raw.info, misc=True, meg=False, eeg=False)

        all_event_channels = list(stim_chs) + list(misc_chs)

        if not all_event_channels:
            return

        # Get events from event channels
        events, event_id = mne.events_from_annotations(raw, verbose=False)

        if len(events) == 0:
            return

        # Remap event IDs to standardized labels
        new_event_id = {}
        for desc, code in event_id.items():
            if desc in _EVENT_ID_MAP:
                new_event_id[desc] = _EVENT_ID_MAP[desc]
            elif desc.isdigit() and int(desc) in _EVENT_LABEL_MAP:
                new_event_id[_EVENT_LABEL_MAP[int(desc)]] = code
            else:
                new_event_id[desc] = code

        # Update raw with new events as annotations
        desc_map = {v: k for k, v in new_event_id.items()}
        annotations = mne.annotations_from_events(
            events, raw.info["sfreq"], desc_map=desc_map, orig_time=raw.annotations.orig_time if raw.annotations else None
        )
        raw.set_annotations(annotations)


# Module-level kernel instance
KERNEL = PEERSKernel()