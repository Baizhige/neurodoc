"""OpenNeuro ds004356 stage1 kernel for EEGUnity.

Subcortical responses to music and speech are alike while cortical responses diverge.
EEG auditory brainstem response (ABR) dataset with 34-channel EEG at 10000 Hz.

Source: https://openneuro.org/datasets/ds004356
Paper: DOI 10.1038/s41598-023-50438-0
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Subject metadata - Source: OpenNeuro dataset participants.tsv
# Annotator: LLM, 2026-04-08, inference from dataset documentation
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }
    for i in range(1, 23)
}

# Device metadata - Source: Paper DOI 10.1038/s41598-023-50438-0
# 64-channel active Ag/AgCl electrode system (EasyCap) with Brainamp MR plus amplifier
# Annotator: LLM, 2026-04-08, inference from paper methods section
_DEVICE_METADATA = {
    "amplifier": "BrainAmp MR plus",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl",  # LLM 推断，需人类复核
}

# Event mapping from raw stimulus markers to semantic labels
# Source: Dataset README and paper describing stimulus categories
# The dataset uses stimulus markers (1, 2, 4, 8) mapped to different audio categories
_EVENT_MAP: Dict[int, str] = {
    1: "click",       # Continuous click train stimulus
    2: "acoustic",    # Acoustic guitar stimulus
    4: "classical",   # Classical music stimulus
    8: "jazz",        # Jazz music stimulus
}

# Extended event map for additional music/speech categories (if present in annotations)
_EXTENDED_EVENT_MAP: Dict[str, str] = {
    "pop": "pop",         # Pop music stimulus
    "metal": "metal",     # Metal music stimulus
    "hiphop": "hiphop",   # Hip-hop music stimulus
    "chn_aud": "chn_aud", # Chinese speech stimulus
    "eng_aud": "eng_aud", # English speech stimulus
    "news": "news",       # News speech stimulus
    "talk": "talk",       # Talk speech stimulus
    "interview": "interview",  # Interview speech stimulus
    "lecture": "lecture",     # Lecture speech stimulus
}

# Music vs Speech classification labels (Classical Task 1)
_MUSIC_SPEECH_LABELS: Dict[str, int] = {
    # Music categories -> label 0
    "acoustic": 0,
    "classical": 0,
    "jazz": 0,
    "pop": 0,
    "metal": 0,
    "hiphop": 0,
    # Speech categories -> label 1
    "chn_aud": 1,
    "eng_aud": 1,
    "news": 1,
    "talk": 1,
    "interview": 1,
    "lecture": 1,
}


def _extract_subject_id(row) -> str:
    """Extract subject ID from row."""
    if "Subject" in row:
        return f"sub-{str(row['Subject']).zfill(2)}"
    file_path = row.get("File Path", "")
    if "sub-" in file_path:
        parts = file_path.split("sub-")
        if len(parts) > 1:
            sub_id = parts[1].split("/")[0].split("_")[0]
            return f"sub-{sub_id}"
    return "sub-01"


def _parse_events_from_annotations(
    raw: mne.io.BaseRaw, 
    stim_channel: Optional[str] = None
) -> mne.Annotations:
    """Parse events from raw annotations or stim channel.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object
    stim_channel : str, optional
        Stimulus channel name if present
        
    Returns
    -------
    mne.Annotations
        Processed annotations with semantic event labels
    """
    # Try to use existing annotations first
    if raw.annotations is not None and len(raw.annotations) > 0:
        onset_list = []
        duration_list = []
        description_list = []
        
        for i, desc in enumerate(raw.annotations.description):
            desc_str = str(desc)
            
            # Check if it's already a semantic label
            if desc_str in _EVENT_MAP.values() or desc_str in _EXTENDED_EVENT_MAP.values():
                onset_list.append(raw.annotations.onset[i])
                duration_list.append(raw.annotations.duration[i])
                description_list.append(desc_str)
            # Check if it's a numeric code that needs mapping
            elif desc_str.isdigit():
                code = int(desc_str)
                if code in _EVENT_MAP:
                    onset_list.append(raw.annotations.onset[i])
                    duration_list.append(raw.annotations.duration[i])
                    description_list.append(_EVENT_MAP[code])
            else:
                # Keep original for unknown events
                onset_list.append(raw.annotations.onset[i])
                duration_list.append(raw.annotations.duration[i])
                description_list.append(desc_str)
        
        if onset_list:
            return mne.Annotations(
                onset=np.array(onset_list),
                duration=np.array(duration_list),
                description=description_list,
            )
    
    # Try to read from stim channel if present
    if stim_channel and stim_channel in raw.ch_names:
        stim_idx = raw.ch_names.index(stim_channel)
        stim_data, _ = raw[stim_idx, :]
        
        # Find event onsets (rising edges where value changes)
        diffs = np.diff(stim_data.astype(int))
        event_indices = np.where(np.abs(diffs) > 0)[0]
        event_codes = stim_data[event_indices + 1].astype(int)
        event_onsets = (event_indices + 1) / raw.info["sfreq"]
        
        # Map event codes to semantic labels
        descriptions = []
        for code in event_codes:
            if code in _EVENT_MAP:
                descriptions.append(_EVENT_MAP[code])
            else:
                descriptions.append(f"stim_{code}")
        
        return mne.Annotations(
            onset=event_onsets,
            duration=np.zeros(len(event_onsets)),
            description=descriptions,
        )
    
    # Return empty annotations if no events found
    return mne.Annotations(onset=[], duration=[], description=[])


def _apply_bandpass_filter(
    raw: mne.io.BaseRaw, 
    low_freq: float = 70.0, 
    high_freq: float = 2000.0
) -> mne.io.BaseRaw:
    """Apply bandpass filter for ABR analysis (70-2000 Hz).
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object
    low_freq : float
        High-pass frequency for subcortical ABR (default: 70 Hz)
    high_freq : float
        Low-pass frequency for subcortical ABR (default: 2000 Hz)
        
    Returns
    -------
    mne.io.BaseRaw
        Filtered raw object
    """
    # Only filter EEG-type channels, not stim/misc channels
    eeg_channels = [
        ch for ch in raw.ch_names 
        if raw.get_channel_types([ch])[0] == "eeg"
    ]
    
    if eeg_channels:
        raw_filt = raw.copy()
        raw_filt.filter(
            l_freq=low_freq,
            h_freq=high_freq,
            picks=eeg_channels,
            method="fir",
            fir_window="hamming",
            phase="zero",
        )
        return raw_filt
    
    return raw


class OpenNeuroDS004356Kernel:
    """Stage1 kernel for OpenNeuro ds004356 dataset.
    
    Handles EEG auditory brainstem response (ABR) data from the study
    "Subcortical responses to music and speech are alike while cortical 
    responses diverge".
    
    Features:
    - 34-channel EEG at 10000 Hz sampling rate
    - Bandpass filtering (70-2000 Hz) for subcortical ABR analysis
    - Event mapping from stimulus markers to semantic labels
    - Subject metadata extraction
    
    Tasks supported:
    - Classical Task 1: Music vs Speech Binary Classification
    - Classical Task 2: Click Train ABR Control Task
    """

    KERNEL_ID: str = "openneuro-ds004356-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
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
            The modified Raw object with updated annotations and metadata.
        """
        # Extract subject ID
        subject_id = _extract_subject_id(row)
        
        # Get subject metadata
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")
        
        # Get device metadata
        amplifier = _DEVICE_METADATA.get("amplifier", "unknown")
        cap = _DEVICE_METADATA.get("cap", "unknown")
        
        # Get original description
        original_description = raw.info.get("description", "")
        
        # Update raw.info["description"] with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Identify stimulus channel (usually named 'Stim' or similar)
        stim_channel = None
        for ch in raw.ch_names:
            ch_type = raw.get_channel_types([ch])[0]
            if ch_type in ["stim", "misc"]:
                ch_upper = ch.upper()
                if "STIM" in ch_upper or "MARKER" in ch_upper:
                    stim_channel = ch
                    break
        
        # If no stim channel found, check for any misc/stim type channel
        if not stim_channel:
            for ch in raw.ch_names:
                if raw.get_channel_types([ch])[0] in ["stim", "misc"]:
                    stim_channel = ch
                    break
        
        # Parse and set annotations
        annotations = _parse_events_from_annotations(raw, stim_channel)
        raw.set_annotations(annotations)
        
        # Apply bandpass filter for ABR analysis (70-2000 Hz)
        # This is appropriate for subcortical brainstem response analysis
        raw = _apply_bandpass_filter(raw, low_freq=70.0, high_freq=2000.0)
        
        # Note: Channel renaming should happen here if needed
        # For this dataset, channels appear to use standard naming
        # If specific channel mapping is required, add _CHANNEL_RENAME_MAP
        
        return raw


KERNEL = OpenNeuroDS004356Kernel()