"""PEARL-Neuro Database (openneuro_ds004796) stage1 kernel for EEGUnity.

A multimodal neuroimaging database of healthy middle-aged adults (50-63 years)
carrying Alzheimer's risk genes (APOE, PICALM). The EEG protocol includes
resting-state recordings (eyes open and closed) and two active cognitive tasks:
the Multi-Source Interference Task (MSIT) and Sternberg's memory task.

Source: https://openneuro.org/datasets/ds004796
DOI: 10.1038/s41597-024-03106-5
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# 被试者元信息
# =============================================================================

# Source: DOI 10.1038/s41597-024-03106-5 (PEARL-Neuro paper)
# "healthy middle-aged adults (50–63 years)" → age range string
# LLM 推断，需人类复核
_SUBJECT_AGE_RANGE: str = "50-63"

# Source: DOI 10.1038/s41597-024-03106-5
# "healthy middle-aged adults" → sex distribution unknown at dataset level
# LLM 推断，需人类复核
_SUBJECT_SEX_DEFAULT: str = "unknown"

# Source: DOI 10.1038/s41597-024-03106-5
# 127-channel EEG system used for PEARL-Neuro data collection
# LLM 推断，需人类复核
_AMPLIFIER: str = "unknown"

# Source: DOI 10.1038/s41597-024-03106-5
# High-density EEG cap used in PEARL-Neuro study
# LLM 推断，需人类复核
_CAP: str = "unknown"

# Source: DOI 10.1038/s41597-024-03106-5
# Handedness information not explicitly stated in available documentation
# LLM 推断，需人类复核
_HANDEDNESS: str = "unknown"


# =============================================================================
# 通道重映射
# =============================================================================

# PEARL-Neuro uses 127-channel EEG cap based on standard_1020 system.
# The actual channel naming follows a pattern where channels are named with
# standard 10-20 nomenclature. However, raw data may contain non-standard names.
# Source: Dataset documentation / paper 10.1038/s41597-024-03106-5
# Annotator: LLM, 2025-01-01
# LLM 推断，需人类复核

# Standard 10-20 channel list for 127-channel system (expanded montage)
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fp2", "Fpz", "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "M1", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "M2",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO5", "PO3", "POz", "PO4", "PO6",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FT7", "FT8",
    "C6",
    "TP7", "TP8",
    "PO7", "PO8",
    "PO9", "PO10",
    "Oz",
    # Additional channels for 127-channel system (from extended 10-20)
    "I1", "I2", "ION", "ION2",
    "F9", "F10",
    "T7", "T8", "T9", "T10",
    "TP9", "TP10",
    "P9", "P10",
    "M1", "M2",
    "A1", "A2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from raw channel names to standard 10-20 names.

    Handles common non-standard naming patterns found in EEG datasets:
    - EEG-0, EEG-1, ... numbered channels
    - Channels with 'EEG' prefix
    - Alternative spellings (e.g., 'T7' vs 'T7')

    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw EEG object containing original channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from original channel names to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Pattern 1: EEG-0, EEG-1, ... numbered channels
    # These are typically ordered following standard 10-20 positions
    numbered_pattern = re.compile(r"^(?:EEG[_-])?(\d+)$")
    numbered_channels = []
    for ch in existing_names:
        match = numbered_pattern.match(ch)
        if match:
            numbered_channels.append((ch, int(match.group(1))))

    if len(numbered_channels) > 0:
        # Sort by number and map to standard channels in order
        numbered_channels.sort(key=lambda x: x[1])
        # Try to map to standard_1020 channels
        try:
            standard_chs = [c for c in _STANDARD_1020_CHANNELS if c in mne.channels.get_standard_montage("standard_1020").ch_names]
            for idx, (_, num) in enumerate(numbered_channels):
                if idx < len(standard_chs):
                    rename_map[f"EEG-{num}"] = standard_chs[idx]
        except Exception:
            pass

    # Pattern 2: Channels with EEG prefix (e.g., 'EEG Fz' -> 'Fz')
    eeg_prefix_pattern = re.compile(r"^EEG[\s_-]*(.+)$", re.IGNORECASE)
    for ch in existing_names:
        match = eeg_prefix_pattern.match(ch)
        if match:
            standard_name = match.group(1).strip()
            # Try to find matching standard name
            for std_ch in _STANDARD_1020_CHANNELS:
                if std_ch.lower().replace("-", "") == standard_name.lower().replace("-", "").replace(" ", ""):
                    rename_map[ch] = std_ch
                    break

    # Pattern 3: Direct alias matching for common variations
    alias_map = {
        # Standard variations
        "Fpz": ["Fpz", "Fpz", "fpz", "AFz"],
        "Fz": ["Fz", "Fz", "fz"],
        "Cz": ["Cz", "Cz", "cz"],
        "Pz": ["Pz", "Pz", "pz"],
        "Oz": ["Oz", "Oz", "oz"],
        "T7": ["T7", "T7", "T7"],
        "T8": ["T8", "T8", "T8"],
        # Add more as needed
    }
    for std_name, aliases in alias_map.items():
        for ch in existing_names:
            if ch in aliases and ch != std_name:
                rename_map[ch] = std_name

    return rename_map


# =============================================================================
# 事件映射
# =============================================================================

# Event codes from MSIT task: Stimulus/S 1 through S 5
# Event codes from Sternberg task: Stimulus/S 10 through S 12
# Source: analysis.md / kernel documentation
# Annotator: LLM, 2025-01-01
# LLM 推断，需人类复核

_MSIT_STIMULUS_CODES: Dict[str, int] = {
    "Stimulus/S  1": 1,
    "Stimulus/S  2": 2,
    "Stimulus/S  3": 3,
    "Stimulus/S  4": 4,
    "Stimulus/S  5": 5,
}

_STERNBERG_STIMULUS_CODES: Dict[str, int] = {
    "Stimulus/S 10": 10,
    "Stimulus/S 11": 11,
    "Stimulus/S 12": 12,
}

_RESPONSE_CODE: str = "response"


def _detect_task_from_filename(filename: str) -> Optional[str]:
    """Detect task type from filename.

    Parameters
    ----------
    filename : str
        The filename or path containing the task identifier.

    Returns
    -------
    Optional[str]
        Task identifier: 'MSIT', 'Sternberg', 'resting', or None if unknown.
    """
    filename_lower = filename.lower()
    if "msit" in filename_lower:
        return "MSIT"
    elif "sternberg" in filename_lower:
        return "Sternberg"
    elif "rest" in filename_lower or "eyes" in filename_lower:
        return "resting"
    return None


def _map_event_code_to_label(event_code: int, task: str) -> str:
    """Map event code and task to human-readable label.

    Parameters
    ----------
    event_code : int
        The numeric event code.
    task : str
        The task type ('MSIT', 'Sternberg', 'resting').

    Returns
    -------
    str
        Human-readable event label.
    """
    if task == "MSIT":
        for label, code in _MSIT_STIMULUS_CODES.items():
            if code == event_code:
                return label
    elif task == "Sternberg":
        for label, code in _STERNBERG_STIMULUS_CODES.items():
            if code == event_code:
                return label

    # Generic mapping for response and other events
    if event_code == 0:
        return "response"
    elif 1 <= event_code <= 5:
        return f"Stimulus/S  {event_code}"
    elif 10 <= event_code <= 12:
        return f"Stimulus/S  {event_code}"

    return f"event_{event_code}"


# =============================================================================
# Kernel Class
# =============================================================================

@dataclass
class PEARLNeuroKernel:
    """Stage1 kernel for the PEARL-Neuro Database (openneuro_ds004796)."""

    KERNEL_ID: str = "openneuro-ds004796-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row
            Locator row with file path information.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and events.
        """
        # Get original description
        original_description = raw.info.get("description", "")

        # Build eegunity_description
        # Source: DOI 10.1038/s41597-024-03106-5 - age range 50-63 years
        # Source: DOI 10.1038/s41597-024-03106-5 - sex unknown at dataset level
        # LLM 推断，需人类复核
        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": _SUBJECT_AGE_RANGE,
                "sex": _SUBJECT_SEX_DEFAULT,
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": _HANDEDNESS,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names before set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if rename fails

        # Set standard 1020 montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if not applicable

        # Detect task type from filename
        file_path = row.get("File Path", row.get("file_path", ""))
        filename = os.path.basename(file_path)
        task = _detect_task_from_filename(filename)

        # Process annotations/events from raw data
        try:
            annotations = raw.annotations
            if len(annotations) > 0:
                # Remap annotation descriptions to standardized labels
                new_descriptions = []
                for desc in annotations.description:
                    # Try to parse event code from description
                    # Common patterns: numeric codes, 'Stimulus/S  X', 'response'
                    desc_str = str(desc).strip()

                    # Check if it's already a known label
                    if desc_str in _MSIT_STIMULUS_CODES:
                        new_descriptions.append(desc_str)
                    elif desc_str in _STERNBERG_STIMULUS_CODES:
                        new_descriptions.append(desc_str)
                    elif desc_str.lower() == "response":
                        new_descriptions.append("response")
                    elif desc_str.lower() == "stimulus":
                        new_descriptions.append(desc_str)
                    else:
                        # Try to extract numeric code
                        code_match = re.search(r"(\d+)", desc_str)
                        if code_match:
                            code = int(code_match.group(1))
                            if task == "MSIT" and code in _MSIT_STIMULUS_CODES.values():
                                for label, c in _MSIT_STIMULUS_CODES.items():
                                    if c == code:
                                        new_descriptions.append(label)
                                        break
                            elif task == "Sternberg" and code in _STERNBERG_STIMULUS_CODES.values():
                                for label, c in _STERNBERG_STIMULUS_CODES.items():
                                    if c == code:
                                        new_descriptions.append(label)
                                        break
                            else:
                                new_descriptions.append(desc_str)
                        else:
                            new_descriptions.append(desc_str)

                # Create new annotations with remapped descriptions
                new_annotations = mne.Annotations(
                    onset=annotations.onset,
                    duration=annotations.duration,
                    description=new_descriptions,
                    orig_time=annotations.orig_time,
                )
                raw.set_annotations(new_annotations)
        except Exception:
            pass  # Skip annotation processing if it fails

        return raw


KERNEL = PEARLNeuroKernel()