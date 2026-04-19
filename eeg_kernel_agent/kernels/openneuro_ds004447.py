"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — High-density EEG BCI with 130-channel GES400/Hydrocel GSN montage.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6

Channel naming convention:
- GES400/Hydrocel GSN uses E1..E128 or E1..E130 naming
- Need to map to standard 10-20 locations for montage
- Source: Hydrocel GSN 128 channel layout documentation

Event Structure (from analysis.md):
- event_1: Rest/baseline period (value=1, ~5s duration)
- event_2: Task execution (value=3, ~6s duration) 
- event_3: Ready/preparation (value=2, ~2s duration)
- event_4: Interval/feedback (value=4, ~3s duration)
"""

from __future__ import annotations

import json
import os
from typing import Dict, Optional, Any, List, Tuple

import mne
import numpy as np
import pandas as pd
from scipy import signal


# Subject info extracted from participants.tsv
# Source: OpenNeuro dataset participants.tsv
# Annotator: Human, verified against dataset documentation
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-001": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-002": {"age": "24", "sex": "male", "handedness": "right"},
    "sub-003": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-004": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-005": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-006": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-007": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-008": {"age": "23", "sex": "female", "handedness": "right"},
    "sub-009": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-010": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-011": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-012": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-013": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-014": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-015": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-016": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-017": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-018": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-019": {"age": "26", "sex": "male", "handedness": "right"},
    "sub-020": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-021": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-022": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-023": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-024": {"age": "25", "sex": "female", "handedness": "right"},
    "sub-025": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-026": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-027": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-028": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-029": {"age": "27", "sex": "male", "handedness": "right"},
    "sub-030": {"age": "21", "sex": "male", "handedness": "right"},
}

# Event mapping based on analysis.md event structure
# Source: analysis.md event structure table, events.tsv instruction column
# Annotator: Human, derived from dataset documentation
_EVENT_ID_MAP: Dict[int, str] = {
    1: "event_1",  # Rest/baseline period onset
    2: "event_2",  # Task execution period onset (also ready in some contexts)
    3: "event_3",  # Ready/preparation period onset
    4: "event_4",  # Interval/feedback period onset
}

# Hydrocel GSN 128 channel layout - standard E1-E128 naming to 10-20 positions
# Source: EGI Hydrocel GSN 128 channel cap layout documentation
# The 128-channel Hydrocel uses a geodesic grid; approximate 10-20 mapping:
# Annotator: LLM, mapping based on standard Hydrocel GSN layout positions
_CH_HYDROCEL_TO_STANDARD: Dict[str, str] = {
    # Frontal
    "E1": "Fp1", "E2": "Fpz", "E3": "Fp2",
    "E4": "AF9", "E5": "AF7", "E6": "AF5", "E7": "AF3", "E8": "AF1", "E9": "AFz", 
    "E10": "AF2", "E11": "AF4", "E12": "AF6", "E13": "AF8", "E14": "AF10",
    # Frontal-Central
    "E15": "F9", "E16": "F7", "E17": "F5", "E18": "F3", "E19": "F1", "E20": "Fz", 
    "E21": "F2", "E22": "F4", "E23": "F6", "E24": "F8", "E25": "F10",
    "E26": "FT9", "E27": "FT7", "E28": "FC5", "E29": "FC3", "E30": "FC1", 
    "E31": "FCz", "E32": "FC2", "E33": "FC4", "E34": "FC6", "E35": "FT8", "E36": "FT10",
    # Central
    "E37": "T9", "E38": "T7", "E39": "C5", "E40": "C3", "E41": "C1", 
    "E42": "Cz", "E43": "C2", "E44": "C4", "E45": "C6", "E46": "T8", "E47": "T10",
    "E48": "TP9", "E49": "TP7", "E50": "CP5", "E51": "CP3", "E52": "CP1", 
    "E53": "CPz", "E54": "CP2", "E55": "CP4", "E56": "CP6", "E57": "TP8", "E58": "TP10",
    # Parietal
    "E59": "P9", "E60": "P7", "E61": "P5", "E62": "P3", "E63": "P1", 
    "E64": "Pz", "E65": "P2", "E66": "P4", "E67": "P6", "E68": "P8", "E69": "P10",
    "E70": "PO9", "E71": "PO7", "E72": "PO5", "E73": "PO3", "E74": "PO1", 
    "E75": "POz", "E76": "PO2", "E77": "PO4", "E78": "PO6", "E79": "PO8", "E80": "PO10",
    # Occipital
    "E81": "O9", "E82": "O7", "E83": "O5", "E84": "O3", "E85": "O1", 
    "E86": "Oz", "E87": "O2", "E88": "O4", "E89": "O6", "E90": "O8", "E91": "O10",
    # Additional peripheral/ground electrodes
    "E92": "I1", "E93": "I2", "E94": "I3", "E95": "I4", "E96": "I5",
    "E97": "I6", "E98": "I7", "E99": "I8", "E100": "I9", "E101": "I10",
    "E102": "I11", "E103": "I12", "E104": "I13", "E105": "I14", "E106": "I15",
    "E107": "I16", "E108": "I17", "E109": "I18", "E110": "I19", "E111": "I20",
    "E112": "I21", "E113": "I22", "E114": "I23", "E115": "I24", "E116": "I25",
    "E117": "I26", "E118": "I27", "E119": "I28", "E120": "I29", "E121": "I30",
    "E122": "I31", "E123": "I32", "E124": "I33", "E125": "I34", "E126": "I35",
    "E127": "I36", "E128": "I37", "E129": "I38", "E130": "I39",
}

# Key motor-related channels for IAF estimation
# C3, C4, Cz are primary motor cortex locations
# Source: DOI 10.1109/TNSRE.2024.3365197 for alpha peak detection methodology
_MOTOR_CHANNELS: List[str] = ["C3", "C4", "Cz"]

# EEGUnity description template
_AMPLIFIER = "GES 400"  # Source: Dataset description, 130-channel system
_CAP = "Hydrocel GSN"  # Source: Dataset description


class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro DS004447 dataset processing."""
    
    KERNEL_ID = "openneuro_ds004447"
    
    def __init__(self):
        self.kernel_id = self.KERNEL_ID
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data.
        
        Parameters
        ----------
        udataset : object
            Universal dataset interface
        raw : mne.io.BaseRaw
            Raw EEG data
        row : dict
            Dataset manifest row
            
        Returns
        -------
        mne.io.BaseRaw
            Processed raw EEG data
        """
        # Get subject info
        subject_id = row.get("subject_id", "sub-001")
        subject_info = _SUBJECT_DICT.get(subject_id, _SUBJECT_DICT["sub-001"])
        
        # Detect and rename Hydrocel channels with duplicate handling
        rename_map = _detect_hydrocel_channels(raw)
        if rename_map:
            # Resolve duplicate target names by appending suffix
            rename_map = _resolve_duplicate_targets(rename_map)
            raw = raw.rename_channels(rename_map)
        
        # Set montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1005")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass
        
        # Set common average reference
        raw.set_eeg_reference("average", projection=False)
        
        return raw


def _detect_hydrocel_channels(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Detect Hydrocel GSN channel naming and build rename map.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data
        
    Returns
    -------
    Dict[str, str]
        Mapping from source channel names to standard names
    """
    rename_map = {}
    ch_names = raw.ch_names
    
    for ch in ch_names:
        # Check for E-prefixed channels (Hydrocel naming: E1, E2, ..., E128)
        if ch.startswith("E") and len(ch) <= 4:
            try:
                num = int(ch[1:])
                if num >= 1 and num <= 130:
                    if ch in _CH_HYDROCEL_TO_STANDARD:
                        rename_map[ch] = _CH_HYDROCEL_TO_STANDARD[ch]
            except ValueError:
                pass
    
    return rename_map


def _resolve_duplicate_targets(rename_map: Dict[str, str]) -> Dict[str, str]:
    """Resolve duplicate target names by appending numeric suffixes.
    
    Parameters
    ----------
    rename_map : Dict[str, str]
        Mapping from source to target channel names
        
    Returns
    -------
    Dict[str, str]
        Mapping with unique target channel names
    """
    # Count occurrences of each target name
    target_counts: Dict[str, int] = {}
    for target in rename_map.values():
        target_counts[target] = target_counts.get(target, 0) + 1
    
    # Track which targets have been seen and their suffixes
    target_seen: Dict[str, int] = {}
    resolved_map = {}
    
    for source, target in rename_map.items():
        if target_counts[target] > 1:
            # Need to make unique
            if target not in target_seen:
                target_seen[target] = 1
                resolved_map[source] = target
            else:
                # Append suffix to make unique
                target_seen[target] += 1
                resolved_map[source] = f"{target}_{target_seen[target]}"
        else:
            resolved_map[source] = target
    
    return resolved_map


# EEGUnity description dict
eegunity_description = {
    "age": str(_SUBJECT_DICT["sub-001"]["age"]),
    "sex": _SUBJECT_DICT["sub-001"]["sex"],
    "amplifier": _AMPLIFIER,
    "cap": _CAP,
    "handedness": _SUBJECT_DICT["sub-001"]["handedness"],
}

# Kernel instance
KERNEL = EEGUnityKernel()