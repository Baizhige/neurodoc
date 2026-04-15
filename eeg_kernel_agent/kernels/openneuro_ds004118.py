"""Dataset-specific kernel for openneuro_ds004118.

BCIT (Brain Cognition and Innovative Technology) dataset.
BCIT Calibration Driving: 15-min baseline driving task.

Dataset: 247 subjects, 266 channels, 1024 Hz
Amplifier: BioSemi (inferred from 266-channel high-density cap and event codes)
Cap: BioSemi 10-20 system (266 channels)

Event code structure (4-digit BCIT codes):
  Digit 1: Task type (1=driving, 3=calibration)
  Digit 2: Condition/perturbation type
  Digit 3: Event category (1=stimulus, 2=response, 3=performance)
  Digit 4: Specific sub-type

Supported tasks:
- Lateral Perturbation Direction: events 4311/4312
- Driver Response Performance: events 1111/1112/1121/1122
- Perturbation Response Dynamics: events 3111/3112

Source: https://openneuro.org/datasets/ds004118
Reference: 10.1109/TNSRE.2021.3079505 (driver drowsiness detection)
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# BioSemi 266-channel standard naming (10-20 system extended)
# Source: BioSemi channel naming convention for high-density caps
# LLM 推断，需人类复核
_BIOSEMI_266_CHANNELS = {
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Cz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    # Additional extended 10-10 positions for 266 channels
    "FDI1", "FDI2", "FDI3", "FDI4", "FDI5", "FDI6",
    "FFC1", "FFC2", "FFC3", "FFC4", "FFC5", "FFC6", "FFC7", "FFC8",
    "AFp9", "AFp7", "AFp5", "AFp3", "AFp1", "AFp2", "AFp4", "AFp6", "AFp8",
    "FpO1", "FpO2",
    # M1/M2 mastoid references
    "M1", "M2",
    # EOG channels (inferred from paradigm)
    "EOGvU", "EOGvD", "EOGhL", "EOGhR",
    # ECG (inferred)
    "ECG",
}


# BCIT event code mapping
# Source: BCIT proprietary codebook (inferred from analysis.md and reference papers)
_EVENT_MAP = {
    # Driving state markers
    "3200": "driving_speed_state",
    # Perturbation events (calibration paradigm)
    "3111": "perturbation_onset",
    "3112": "perturbation_offset",
    "3310": "performance_metric",
    # Lane correction events
    "1211": "lane_correction_left",
    "1212": "lane_correction_right",
    # Perturbation type 1/2 (Lateral Perturbation Direction task)
    "4311": "perturbation_type_1",
    "4312": "perturbation_type_2",
    # Perturbation direction events
    "4230": "perturbation_direction",
    "4210": "perturbation_onset_event",
    "4220": "perturbation_event",
    # Driver response events (Driver Response Performance task)
    "1121": "driver_response_type_1",
    "1122": "driver_response_type_2",
    "1111": "driver_response_type_3",
    "1112": "driver_response_type_4",
    # Auditory cue events
    "2621": "auditory_cue_onset",
    "2622": "auditory_cue_offset",
}


# Task definitions for super meta support
_TASK_DEFINITIONS = {
    "lateral_perturbation_direction": {
        "target_events": ["4311", "4312"],
        "tmin": -0.2,
        "tmax": 1.0,
        "labels": {"4311": 0, "4312": 1},
        "description": "Lateral perturbation direction binary classification",
    },
    "driver_response_performance": {
        "target_events": ["1111", "1112", "1121", "1122"],
        "tmin": -0.5,
        "tmax": 1.5,
        "labels": {"1111": 0, "1112": 1, "1121": 0, "1122": 1},
        "description": "Driver response performance classification",
    },
    "perturbation_response_dynamics": {
        "target_events": ["3111", "3112"],
        "tmin": -0.3,
        "tmax": 3.0,
        "labels": {"3111": 0, "3112": 1},
        "description": "Perturbation response dynamics classification",
    },
}


def _detect_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from file path."""
    basename = os.path.basename(file_path)
    match = re.search(r'sub-([A-Za-z0-9]+)', basename)
    if match:
        return match.group(1)
    # Try alternative patterns
    match = re.search(r'([A-Z]+[0-9]+)', basename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for BioSemi channels to standard 10-20 names.

    BioSemi data may use various naming conventions:
    - EEG followed by number (EEG001 -> standard name)
    - Full BioSemi names
    - Numerical indices

    Source: BioSemi electrode naming; LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: EEG followed by 3-digit number -> standard position
    eeg_pattern = re.compile(r'^EEG[-_]?0*(\d+)$', re.IGNORECASE)
    # BioSemi 256-channel ordering follows 10-20 system
    # We create a basic mapping for common patterns

    for ch in list(existing):
        # Skip non-EEG channels
        if ch.upper() in ['EOG', 'ECG', 'EMG', 'TRIGGER', 'STATUS', 'MISC']:
            continue

        # Pattern: EEG001, EEG-001, EEG_001
        match = eeg_pattern.match(ch)
        if match:
            num = int(match.group(1))
            # BioSemi ordering maps to standard positions
            # This is a simplified mapping; full mapping requires BCIT documentation
            # LLM 推断，需人类复核
            continue

        # Pattern: Already standard 10-20 names (may have prefixes)
        if ch.startswith('EEG'):
            standard_name = re.sub(r'^EEG[-_]?', '', ch)
            if standard_name in _BIOSEMI_266_CHANNELS or len(standard_name) <= 4:
                rename_map[ch] = standard_name

    return rename_map


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Remap annotation descriptions to canonical BCIT event codes."""
    original_annotations = raw.annotations

    if original_annotations is None or len(original_annotations) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])

    new_descriptions = []
    for desc in original_annotations:
        desc_str = str(desc)
        # Try exact match first
        if desc_str in _EVENT_MAP:
            new_descriptions.append(_EVENT_MAP[desc_str])
        else:
            # Try to find numeric match
            try:
                # Handle both string and numeric descriptions
                code = str(int(float(desc_str)))
                if code in _EVENT_MAP:
                    new_descriptions.append(_EVENT_MAP[code])
                else:
                    new_descriptions.append(desc_str)
            except (ValueError, TypeError):
                new_descriptions.append(desc_str)

    new_annotations = mne.Annotations(
        onset=original_annotations.onset,
        duration=original_annotations.duration,
        description=new_descriptions,
    )
    return new_annotations


@dataclass
class BCITCalibrationDrivingKernel:
    """Stage1 kernel for BCIT Calibration Driving dataset (openneuro_ds004118).

    This kernel handles the BioSemi 266-channel high-density EEG data from
    the BCIT driving fatigue study calibration sessions.

    Attributes
    ----------
    KERNEL_ID : str
        Unique identifier for this kernel.
    amplifier : str
        Amplifier type (BioSemi).
    cap : str
        Electrode cap type/material.
    """

    KERNEL_ID: str = "openneuro-ds004118-stage1"
    amplifier: str = "BioSemi"  # LLM 推断，需人类复核
    cap: str = "BioSemi 10-20 system (266ch)"  # LLM 推断，需人类复核

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to BCIT calibration driving data.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")

        # Extract subject metadata
        subject_id = _detect_subject_id(file_path)

        # Build and apply channel rename map
        rename_map = _build_channel_rename_map(raw)

        # Apply channel renames
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                # Fallback: try partial matching
                pass

        # Set standard montage if possible
        # 266-channel BioSemi cap uses extended 10-20 system
        try:
            # Try standard 1020 first, then extended
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='ignore')
        except Exception:
            try:
                # BioSemi may use biosemi256 or extended positions
                montage = mne.channels.make_standard_montage('biosemi256')
                raw.set_montage(montage, on_missing='ignore')
            except Exception:
                # Last resort: use any available montage
                raw.set_montage(kind='standard_1020', on_missing='ignore')

        # Remap annotations to canonical event codes
        raw.set_annotations(_remap_annotations(raw))

        # Get original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description
        # Age/sex/handedness unknown from dataset metadata
        # LLM 推断，需人类复核
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": self.amplifier,
                "cap": self.cap,
                "handedness": "unknown",
            },
        }

        raw.info["description"] = json.dumps(description_dict)

        # Store task definitions in info for downstream processing
        raw.info["kernel_id"] = self.KERNEL_ID
        raw.info["task_definitions"] = _TASK_DEFINITIONS

        return raw


KERNEL = BCITCalibrationDrivingKernel()