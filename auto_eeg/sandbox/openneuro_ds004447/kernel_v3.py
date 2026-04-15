"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — 4-class Motor Imagery BCI with 130-channel high-density EEG.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

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
# Channel Rename Map — 130-channel GES400/Hydrocel GSN
# Source: DOI 10.1038/s41597-023-02260-6, Supplement; GSN Hydrocel 128 layout
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# Note: The GES400/Hydrocel GSN uses E1/E2 reference montage with numbered
# channels (001-128) plus two reference electrodes. The kernel attempts to map
# these to standard 10-20 system where applicable based on the cap layout.
# =============================================================================
_GES400_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 landmarks
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T7": "T7", "C3": "C3", "C4": "C4", "T8": "T8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "O2": "O2",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    # Additional channels from Hydrocel GSN
    "AF7": "AF7", "AF3": "AF3", "AF4": "AF4", "AF8": "AF8",
    "F5": "F5", "F1": "F1", "F2": "F2", "F6": "F6",
    "FT7": "FT7", "FC3": "FC3", "FC4": "FC4", "FT8": "FT8",
    "C5": "C5", "C1": "C1", "C2": "C2", "C6": "C6",
    "TP7": "TP7", "CP3": "CP3", "CP4": "CP4", "TP8": "TP8",
    "P5": "P5", "P1": "P1", "P2": "P2", "P6": "P6",
    "PO7": "PO7", "PO3": "PO3", "PO4": "PO4", "PO8": "PO8",
    "POz": "POz", "Oz": "Oz",
    # Reference electrodes
    "M1": "M1", "M2": "M2",
    "TP9": "TP9", "TP10": "TP10",
}

# Numeric channel mapping for GSN format (001-128)
_GSN_NUMERIC_PATTERN = re.compile(r"^E(\d{3})$")

# =============================================================================
# Event Mapping — Trial Phase Detection (Normal Task 2)
# Based on task-smrbmi_events.json: value → instruction mapping
# event_1: rest, event_2: ready, event_3: task, event_4: interval
# Source: DOI 10.1038/s41597-023-02260-6, BIDS sidecar
# Annotator: Human, 2026-04-08
# =============================================================================
_TRIAL_PHASE_EVENT_MAP: Dict[int, str] = {
    1: "trial_phase: rest",
    2: "trial_phase: ready",
    3: "trial_phase: task",
    4: "trial_phase: interval",
}

# Administrative markers (excluded from trial phase analysis)
_ADMIN_EVENT_MAP: Dict[int, str] = {
    5: "feedback_marker",
    6: "special_session_marker",
}

# =============================================================================
# GSN Layout – mapping from standard 10-20 names to numeric E channels.
# Each target may have one or more numeric electrodes.
# Source: GSN Hydrocel 128 layout (approximate). Human annotator 2026-04-08.
# =============================================================================
_GSN_LAYOUT: List[Tuple[str, List[str]]] = [
    ("Fp1", ["E001", "E002"]),
    ("Fpz", ["E003"]),
    ("Fp2", ["E004", "E005"]),
    ("AF7", ["E006"]),
    ("AF3", ["E007", "E008"]),
    ("AFz", ["E009"]),
    ("AF4", ["E010", "E011"]),
    ("AF8", ["E012"]),
    ("F7", ["E013"]),
    ("F5", ["E014"]),
    ("F3", ["E015", "E016"]),
    ("F1", ["E017"]),
    ("Fz", ["E018", "E019"]),
    ("F2", ["E020"]),
    ("F4", ["E021", "E022"]),
    ("F6", ["E023"]),
    ("F8", ["E024"]),
    ("FT7", ["E025"]),
    ("FC5", ["E026", "E027"]),
    ("FC3", ["E028", "E029"]),
    ("FC1", ["E030", "E031"]),
    ("FCz", ["E032", "E033"]),
    ("FC2", ["E034", "E035"]),
    ("FC4", ["E036", "E037"]),
    ("FC6", ["E038", "E039"]),
    ("FT8", ["E040"]),
    ("T7", ["E041", "E042"]),
    ("C5", ["E043"]),
    ("C3", ["E044", "E045", "E046"]),
    ("C1", ["E047", "E048"]),
    ("Cz", ["E049", "E050", "E051"]),
    ("C2", ["E052", "E053"]),
    ("C4", ["E054", "E055", "E056"]),
    ("C6", ["E057"]),
    ("T8", ["E058", "E059"]),
    ("TP7", ["E060"]),
    ("CP5", ["E061", "E062"]),
    ("CP3", ["E063", "E064"]),
    ("CP1", ["E065", "E066"]),
    ("CPz", ["E067", "E068"]),
    ("CP2", ["E069", "E070"]),
    ("CP4", ["E071", "E072"]),
    ("CP6", ["E073", "E074"]),
    ("TP8", ["E075"]),
    ("P7", ["E076", "E077"]),
    ("P5", ["E078", "E079"]),
    ("P3", ["E080", "E081", "E082"]),
    ("P1", ["E083", "E084"]),
    ("Pz", ["E085", "E086"]),
    ("P2", ["E087", "E088"]),
    ("P4", ["E089", "E090", "E091"]),
    ("P6", ["E092", "E093"]),
    ("P8", ["E094", "E095"]),
    ("PO7", ["E096"]),
    ("PO3", ["E097", "E098"]),
    ("POz", ["E099", "E100"]),
    ("PO4", ["E101", "E102"]),
    ("PO8", ["E103"]),
    ("O1", ["E104", "E105"]),
    ("Oz", ["E106", "E107"]),
    ("O2", ["E108", "E109"]),
    # Remaining electrodes not covered by 10-20 system
    ("E110", ["E110"]),
    ("E111", ["E111"]),
    ("E112", ["E112"]),
    ("E113", ["E113"]),
    ("E114", ["E114"]),
    ("E115", ["E115"]),
    ("E116", ["E116"]),
    ("E117", ["E117"]),
    ("E118", ["E118"]),
    ("E119", ["E119"]),
    ("E120", ["E120"]),
    ("E121", ["E121"]),
    ("E122", ["E122"]),
    ("E123", ["E123"]),
    ("E124", ["E124"]),
    ("E125", ["E125"]),
    ("E126", ["E126"]),
    ("E127", ["E127"]),
    ("E128", ["E128"]),
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for GES400/Hydrocel GSN channels.

    Args:
        raw: Raw EEG data.

    Returns:
        Dictionary mapping original channel names to standard names.
    """
    ch_names = raw.ch_names
    rename_map = {}

    # Build reverse layout map: E### → standard name
    layout_map = {}
    for std_name, e_channels in _GSN_LAYOUT:
        for e_ch in e_channels:
            layout_map[e_ch] = std_name

    for ch in ch_names:
        # Try numeric E### format
        if _GSN_NUMERIC_PATTERN.match(ch):
            std_name = layout_map.get(ch)
            if std_name:
                rename_map[ch] = std_name
        # Keep already standard names (no change needed)
        elif ch in _GES400_CHANNEL_MAP:
            pass  # Already in standard format

    return rename_map


def _map_trial_phases(events: np.ndarray) -> np.ndarray:
    """Map raw event values to trial_phase annotations.

    Args:
        events: numpy array of shape (n_events, 3) with [sample, value, _].

    Returns:
        Modified events array with descriptive annotations.
    """
    if events.size == 0:
        return events

    mapped_events = events.copy()
    for i in range(events.shape[0]):
        val = int(events[i, 1])
        if val in _TRIAL_PHASE_EVENT_MAP:
            mapped_events[i, 1] = 0  # Reserved for MNE
        elif val in _ADMIN_EVENT_MAP:
            mapped_events[i, 1] = 0
    return mapped_events


class Kernel:
    """EEGUnity stage1 kernel for OpenNeuro DS004447.

    Processes high-density EEG motor imagery data from BMI-HDEEG dataset.
    Handles GSN Hydrocel channel naming, common average re-referencing,
    and trial phase annotation.
    """

    eegunity_description = {
        "age": "22-27",
        "sex": "mixed",
        "amplifier": "GES400 (Brain Products)",
        "cap": "Hydrocel GSN 128-channel",
        "handedness": "right",
    }

    def apply(self, udataset, raw, row):
        """Apply stage1 processing to raw EEG data.

        Args:
            udataset: Unified dataset object with data_path and metadata.
            raw: mne.io.BaseRaw object to process.
            row: DataFrame row with subject/run information.

        Returns:
            Processed mne.io.BaseRaw object.
        """
        # Get subject info
        subject = row.get("subject", "unknown")
        session = row.get("session", "smrbmi")

        # --- Step 1: Rename GSN channels ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map))
            print(f"[{subject}] Renamed {len(rename_map)} GSN channels to 10-20 names")

        # --- Step 2: Set montage ---
        try:
            montage = mne.channels.make_standard_montage("GSN-Hydrocel-128")
            raw = raw.set_montage(montage, on_missing="warn")
            print(f"[{subject}] Set GSN-Hydrocel montage")
        except Exception as e:
            print(f"[{subject}] Warning: Could not set montage: {e}")

        # --- Step 3: Re-reference to average ---
        # Use all EEG channels for common average reference
        eeg_chs = mne.pick_types(raw.info, eeg=True)
        if len(eeg_chs) > 0:
            raw = mne.set_eeg_reference(raw, ref_type="average")[0]
            print(f"[{subject}] Re-referenced to average")

        # --- Step 4: Handle meas_date ---
        date = raw.info.get("meas_date")
        if date is None:
            # Try to infer from file metadata or set to None
            raw.info["meas_date"] = None

        # --- Step 5: Annotate trial phases ---
        events, event_id = mne.events_from_annotations(raw)
        if events.size > 0:
            # Map events to trial phases
            mapped_events = _map_trial_phases(events)
            # Create new annotations for trial phases
            annot_events = []
            for i in range(mapped_events.shape[0]):
                val = int(events[i, 1])
                if val in _TRIAL_PHASE_EVENT_MAP:
                    desc = _TRIAL_PHASE_EVENT_MAP[val]
                    sample = int(mapped_events[i, 0])
                    annot_events.append([sample, 0, desc])

            if annot_events:
                annot_arr = np.array(annot_events)
                descriptions = annot_arr[:, 2].astype(str)
                onsets = annot_arr[:, 0] / raw.info["sfreq"]
                durations = np.zeros(len(onsets))
                new_annot = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=raw.info["meas_date"],
                )
                if raw.annotations is not None:
                    raw = raw.concatenate_new_annotations([new_annot])
                else:
                    raw.set_annotations(new_annot)
                print(f"[{subject}] Added {len(descriptions)} trial phase annotations")

        return raw


KERNEL = Kernel()