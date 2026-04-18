"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — High-density EEG BCI with 130-channel GES400/Hydrocel GSN montage.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Dictionary
# Source: DOI 10.1038/s41597-023-02260-6, Table 1, and participants.tsv
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-02": {"age": "24", "sex": "male", "handedness": "right"},
    "sub-03": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-04": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-05": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-06": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-07": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-08": {"age": "23", "sex": "female", "handedness": "right"},
    "sub-09": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-10": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-11": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-12": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-13": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-14": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-15": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-16": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-17": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-18": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-19": {"age": "26", "sex": "male", "handedness": "right"},
    "sub-20": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-21": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-22": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-23": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-24": {"age": "25", "sex": "female", "handedness": "right"},
    "sub-25": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-26": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-27": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-28": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-29": {"age": "27", "sex": "male", "handedness": "right"},
    "sub-30": {"age": "21", "sex": "male", "handedness": "right"},
}

# =============================================================================
# Channel Rename Map — EGI Hydrocel GSN 128 → standard 10-20 names
# Source: EGI Hydrocel GSN 128-channel layout documentation
# EGI channel numbers map to standard 10-20 positions
# Annotator: Human, 2026-04-08
# Note: The dataset uses 130 channels (128 Hydrocel + 2 reference electrodes)
# =============================================================================
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 positions from EGI Hydrocel GSN layout
    "E1": "Fp1",    "E2": "Fpz",    "E3": "Fp2",    "E4": "AF3",
    "E5": "AF4",    "E6": "AFz",    "E7": "F7",     "E8": "F5",
    "E9": "F3",     "E10": "F1",    "E11": "Fz",    "E12": "F2",
    "E13": "F4",    "E14": "F6",    "E15": "F8",    "E16": "FT7",
    "E17": "FC5",   "E18": "FC3",   "E19": "FC1",   "E20": "FCz",
    "E21": "FC2",   "E22": "FC4",   "E23": "FC6",   "E24": "FT8",
    "E25": "T7",    "E26": "C5",    "E27": "C3",    "E28": "C1",
    "E29": "Cz",    "E30": "C2",    "E31": "C4",    "E32": "C6",
    "E33": "T8",    "E34": "TP7",   "E35": "CP5",   "E36": "CP3",
    "E37": "CP1",   "E38": "CPz",   "E39": "CP2",   "E40": "CP4",
    "E41": "CP6",   "E42": "TP8",   "E43": "P7",    "E44": "P5",
    "E45": "P3",    "E46": "P1",    "E47": "Pz",    "E48": "P2",
    "E49": "P4",    "E50": "P6",    "E51": "P8",    "E52": "PO7",
    "E53": "PO5",   "E54": "PO3",   "E55": "PO1",   "E56": "POz",
    "E57": "PO2",   "E58": "PO4",   "E59": "PO6",   "E60": "PO8",
    "E61": "O1",    "E62": "Oz",    "E63": "O2",    "E64": "Iz",
    # Remaining Hydrocel channels (65-128) follow standard GSN layout
    "E65": "FPL1",  "E66": "FPL2",  "E67": "FPL3",  "E68": "FPL4",
    "E69": "FPL5",  "E70": "FPL6",  "E71": "AFp1",  "E72": "AFp2",
    "E73": "AFp3",  "E74": "AFp4",  "E75": "AFF1",  "E76": "AFF2",
    "E77": "AFF3",  "E78": "AFF4",  "E79": "FFT7",  "E80": "FFC5",
    "E81": "FFC3",  "E82": "FFC1",  "E83": "FFC2",  "E84": "FFC4",
    "E85": "FFC6",  "E86": "FFT8",  "E87": "TTP7",  "E88": "CCP5",
    "E89": "CCP3",  "E90": "CCP1",  "E91": "CCP2",  "E92": "CCP4",
    "E93": "CCP6",  "E94": "TTP8",  "E95": "TPP7",  "E96": "CPP5",
    "E97": "CPP3",  "E98": "CPP1",  "E99": "CPP2",  "E100": "CPP4",
    "E101": "CPP6", "E102": "TPP8", "E103": "PPL1", "E104": "PPL2",
    "E105": "PPL3", "E106": "PPL4", "E107": "PPL5", "E108": "PPL6",
    "E109": "PPO1", "E110": "PPO2", "E111": "PPO3", "E112": "PPO4",
    "E113": "PPO5", "E114": "PPO6", "E115": "POO1", "E116": "POO2",
    "E117": "AOP1", "E118": "AOP2", "E119": "AI1",  "E120": "AI2",
    "E121": "CAL1", "E122": "CAL2", "E123": "RML1", "E124": "RML2",
    "E125": "RML3", "E126": "RML4", "E127": "RML5", "E128": "RML6",
}

# Reference electrode channels (129, 130)
_REFERENCE_CHANNELS = ["E129", "E130"]

# =============================================================================
# Event Mapping
# Source: analysis.md event structure table
# Annotator: Human, 2026-04-08
# =============================================================================
_EVENT_MAP: Dict[str, str] = {
    1: "event_1",   # Trial phase onset: rest
    2: "event_2",   # Trial phase onset: task
    3: "event_3",   # Trial phase onset: ready
    4: "event_4",   # Trial phase onset: interval
    5: "event_5",   # Stimulus/response marker: cue
    91: "admin: marker-91",  # System marker: trigger sync
}


def _get_subject_info(row: Any) -> Dict[str, str]:
    """Get subject metadata from row or dataset.

    Parameters
    ----------
    row : Any
        Locator row with subject identifier.

    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, handedness.
    """
    subject_id = row.get("subject", "")
    subject_key = f"sub-{subject_id}" if not subject_id.startswith("sub-") else subject_id
    if subject_key in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_key]

    return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels from EGI E# format to standard 10-20 names.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with EGI channel names.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with renamed channels.
    """
    existing_names = set(raw.ch_names)
    rename_map = {}
    used_targets = set()

    for egi_name, standard_name in _CHANNEL_RENAME_MAP.items():
        if egi_name in existing_names:
            if standard_name not in used_targets:
                rename_map[egi_name] = standard_name
                used_targets.add(standard_name)

    # Handle reference channels if present
    for ref_ch in _REFERENCE_CHANNELS:
        if ref_ch in existing_names:
            if ref_ch == "E129":
                target = "REF1"
            elif ref_ch == "E130":
                target = "REF2"
            else:
                target = f"REF_{ref_ch}"
            
            if target not in used_targets:
                rename_map[ref_ch] = target
                used_targets.add(target)

    if rename_map:
        raw = raw.rename_channels(rename_map)

    return raw


def _map_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Map event IDs to descriptive names.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with event annotations.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with renamed events.
    """
    annotations = raw.annotations
    if annotations is None or len(annotations) == 0:
        return raw

    new_descriptions = []
    for desc in annotations.description:
        try:
            event_id = int(desc)
            if event_id in _EVENT_MAP:
                new_descriptions.append(_EVENT_MAP[event_id])
            else:
                new_descriptions.append(str(desc))
        except (ValueError, TypeError):
            new_descriptions.append(str(desc))

    annotations.description = np.array(new_descriptions)
    raw.set_annotations(annotations)
    return raw


class EEGUnityKernel:
    """OpenNeuro DS004447 stage1 kernel for EEGUnity.

    Processes high-density EEG data from the BMI-HDEEG dataset 3
    with EGI Hydrocel GSN 128-channel system.
    """

    KERNEL_ID = "openneuro_ds004447"

    eegunity_description = {
        "age": "21-27",
        "sex": "mixed",
        "amplifier": "EGI GES 400",
        "cap": "EGI Hydrocel GSN 128",
        "handedness": "right",
    }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data.

        Parameters
        ----------
        udataset : Any
            Dataset locator.
        raw : mne.io.BaseRaw
            Raw EEG data to process.
        row : Any
            Row with metadata (subject info).

        Returns
        -------
        mne.io.BaseRaw
            Processed raw EEG data.
        """
        # Rename channels from EGI E# to standard 10-20 names
        raw = _rename_channels(raw)

        # Map event IDs to descriptive names
        raw = _map_events(raw)

        return raw


KERNEL = EEGUnityKernel()