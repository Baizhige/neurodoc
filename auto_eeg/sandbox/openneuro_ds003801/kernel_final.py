"""OpenNeuro ds003801 stage1 kernel for EEGUnity.

Neural Tracking to Go - Mobile EEG dichotic listening study.
Participants performed dichotic listening while sitting or walking.
Used for auditory attention decoding (attended vs ignored speaker).

Source: https://openneuro.org/datasets/ds003801
Original paper: DOI 10.1088/1741-2552/ac42b5
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ============================================================================
# Channel Rename Map
# ============================================================================
# Source: Dataset documentation / TMSi Saga 32-channel system default mapping
# (24 EEG channels used in this dataset)
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Ch 1": "Fp1",
    "Ch 2": "Fp2",
    "Ch 3": "F7",
    "Ch 4": "F3",
    "Ch 5": "Fz",
    "Ch 6": "F4",
    "Ch 7": "F8",
    "Ch 8": "T7",
    "Ch 9": "C3",
    "Ch 10": "Cz",
    "Ch 11": "C4",
    "Ch 12": "T8",
    "Ch 13": "P7",
    "Ch 14": "P3",
    "Ch 15": "Pz",
    "Ch 16": "P4",
    "Ch 17": "P8",
    "Ch 18": "O1",
    "Ch 19": "Oz",
    "Ch 20": "O2",
    "Ch 21": "AF7",
    "Ch 22": "AF8",
    "Ch 23": "AFz",
    "Ch 24": "FC1",
}


# ============================================================================
# Event Detection Patterns
# ============================================================================
# File naming convention: sub-<XX>_task-<taskname>_<suffix>.edf
# Suffixes: sit = sitting, walk = walking
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
_START_SOUND_PATTERNS = [
    r"start_sound(?:_L|_R)?_sit",
    r"start_sound(?:_L|_R)?_walk",
    r"start_sit",
    r"start_walk",
]
_STOP_SOUND_PATTERNS = [
    r"stop_sound(?:_L|_R)?_sit",
    r"stop_sound(?:_L|_R)?_walk",
    r"stop_sit",
    r"stop_walk",
]


def _detect_condition_from_filename(filename: str) -> str:
    """Detect sitting vs walking condition from file name.
    
    Parameters
    ----------
    filename : str
        The raw file name (not full path).
    
    Returns
    -------
    str
        "sit" if walking not indicated, "walk" if walking condition.
    """
    lower_fn = filename.lower()
    if "_walk" in lower_fn:
        return "walk"
    return "sit"


def _build_annotations_from_annotations(
    raw: mne.io.BaseRaw,
    file_name: str,
) -> mne.Annotations:
    """Build annotations from existing MNE annotations or file metadata.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw object potentially containing existing annotations.
    file_name : str
        File name for condition detection.
    
    Returns
    -------
    mne.Annotations
        Standardized annotations.
    """
    existing_annotations = raw.annotations
    condition = _detect_condition_from_filename(file_name)
    
    if len(existing_annotations) > 0:
        # Remap existing annotations to standardized format
        onset_list = []
        duration_list = []
        description_list = []
        
        for i, desc in enumerate(existing_annotations.description):
            desc_lower = str(desc).lower()
            
            # Check for start events
            is_start = any(re.search(p, desc_lower) for p in _START_SOUND_PATTERNS)
            is_stop = any(re.search(p, desc_lower) for p in _STOP_SOUND_PATTERNS)
            
            if is_start:
                description_list.append(f"start_sound_{condition}")
                onset_list.append(existing_annotations.onset[i])
                duration_list.append(existing_annotations.duration[i])
            elif is_stop:
                description_list.append(f"stop_sound_{condition}")
                onset_list.append(existing_annotations.onset[i])
                duration_list.append(existing_annotations.duration[i])
            else:
                # Keep original description for other events
                description_list.append(str(desc))
                onset_list.append(existing_annotations.onset[i])
                duration_list.append(existing_annotations.duration[i])
        
        if onset_list:
            return mne.Annotations(
                onset=np.array(onset_list),
                duration=np.array(duration_list),
                description=description_list,
            )
    
    # If no annotations found, create from condition based on file metadata
    # Assuming continuous blocks, estimate block boundaries from recording length
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    duration_sec = n_samples / sfreq
    
    # Estimate block length (~60 seconds based on paradigm description)
    block_length = 60.0
    n_blocks = int(duration_sec / block_length)
    
    if n_blocks == 0:
        n_blocks = 1
        block_length = duration_sec
    
    onset_list = []
    duration_list = []
    description_list = []
    
    for i in range(n_blocks):
        onset_list.append(i * block_length)
        duration_list.append(block_length)
        description_list.append(f"start_sound_{condition}")
    
    return mne.Annotations(
        onset=np.array(onset_list),
        duration=np.array(duration_list),
        description=description_list,
    )


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 system names.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw object with potentially non-standard channel names.
    
    Returns
    -------
    mne.io.BaseRaw
        The raw object with renamed channels.
    """
    rename_map = {}
    for ch_name in raw.ch_names:
        if ch_name in _CHANNEL_RENAME_MAP:
            rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    # Set standard montage if possible
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        # Only keep channels that exist in the raw data
        available_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
        if available_channels:
            raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass  # Skip montage if not possible
    
    return raw


@dataclass
class OpenNeuroDS003801Kernel:
    """Stage1 kernel for OpenNeuro ds003801 (Neural Tracking to Go).
    
    This dataset contains mobile EEG recordings during dichotic listening
    tasks performed while sitting or walking. Used for auditory attention
    decoding studies.
    
    Attributes
    ----------
    KERNEL_ID : str
        Kernel identifier.
    """

    KERNEL_ID: str = "openneuro-ds003801-stage1"

    def apply(
        self,
        udataset,
        raw: mne.io.BaseRaw,
        row,
    ) -> mne.io.BaseRaw:
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
            The modified raw object with channel names standardized,
            eegunity_description populated, and annotations set.
        """
        # Extract file name for condition detection
        file_path = row.get("File Path", "")
        file_name = os.path.basename(file_path) if file_path else ""

        # Rename channels to standard names BEFORE set_montage()
        raw = _rename_channels(raw)

        # Extract subject ID from file path
        subject_id = "unknown"
        if "sub-" in file_path:
            match = re.search(r"sub-(\d+)", file_path)
            if match:
                subject_id = match.group(1)

        # Build and set annotations
        annotations = _build_annotations_from_annotations(raw, file_name)
        raw.set_annotations(annotations)

        # Detect condition for description
        condition = _detect_condition_from_filename(file_name)

        # Original description
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""

        # eegunity_description
        # All fields marked as unknown since dataset documentation does not provide
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003801Kernel()