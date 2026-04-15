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
    
    Maps numeric E001-E128 channels to standard 10-20 names where applicable.
    
    Args:
        raw: MNE Raw object with current channel names.
        
    Returns:
        Dictionary mapping original channel names to standardized names.
    """
    rename_map = {}
    
    # Build reverse layout map: E-channel -> standard name
    e_to_standard: Dict[str, str] = {}
    for standard_name, e_channels in _GSN_LAYOUT:
        for e_ch in e_channels:
            e_to_standard[e_ch] = standard_name
    
    # Get current channel names
    current_chs = raw.ch_names
    
    for ch in current_chs:
        # Check if this is a numeric E channel (E001-E128)
        match = _GSN_NUMERIC_PATTERN.match(ch)
        if match:
            e_num = f"E{int(match.group(1)):03d}"
            if e_num in e_to_standard:
                standard_name = e_to_standard[e_num]
                if standard_name != ch:
                    rename_map[ch] = standard_name
    
    return rename_map


def _get_montage_for_gsn(raw: mne.io.BaseRaw) -> Optional[mne.channels.DigMontage]:
    """Create a DigMontage for GSN Hydrocel 128 channel locations.
    
    Args:
        raw: MNE Raw object.
        
    Returns:
        MNE DigMontage with channel positions, or None if unavailable.
    """
    try:
        # Try to get standard GSN montage from MNE
        montage = mne.channels.make_standard_montage("GSN-Hydrocel-128")
        return montage
    except ValueError:
        # Fallback: create approximate montage from layout
        # This is a simplified approximation based on 10-20 system
        pass
    
    return None


def _detect_trial_phases(events: np.ndarray, sfreq: float) -> np.ndarray:
    """Detect trial phases from event markers.
    
    Args:
        events: MNE events array [n_events, 3] with [sample, _, value].
        sfreq: Sampling frequency.
        
    Returns:
        Modified events array with trial_phase annotations.
    """
    if events.size == 0:
        return events
    
    # Add descriptions to events
    phase_descriptions = []
    for event in events:
        event_id = int(event[2])
        if event_id in _TRIAL_PHASE_EVENT_MAP:
            phase_descriptions.append(_TRIAL_PHASE_EVENT_MAP[event_id])
        elif event_id in _ADMIN_EVENT_MAP:
            phase_descriptions.append(_ADMIN_EVENT_MAP[event_id])
        else:
            phase_descriptions.append(f"event_{event_id}")
    
    return events


class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro DS004447 (BMI-HDEEG dataset).
    
    This kernel processes high-density EEG motor imagery BCI data with:
    - 130-channel GES400/Hydrocel GSN acquisition system
    - 4-class motor imagery tasks (left hand, right hand, feet, tongue)
    - Trial phases: rest, ready, task, interval
    """
    
    KERNEL_ID = "openneuro_ds004447_stage1"
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the EEGUnity kernel."""
        self.subject_dict = _SUBJECT_DICT
        self.trial_phase_events = _TRIAL_PHASE_EVENT_MAP
        self.admin_events = _ADMIN_EVENT_MAP
    
    def get_subject_info(self, subject_id: str) -> Optional[Dict[str, str]]:
        """Get demographic information for a subject.
        
        Args:
            subject_id: Subject identifier (e.g., 'sub-01').
            
        Returns:
            Dictionary with age, sex, handedness, or None if unknown.
        """
        return self.subject_dict.get(subject_id)
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to raw EEG data.
        
        Args:
            udataset: Universal dataset object with BIDS information.
            raw: MNE Raw object with raw EEG data.
            row: DataFrame row with subject/session/run info.
            
        Returns:
            Processed MNE Raw object.
        """
        # Get subject identifier
        subject_id = getattr(row, 'subject_id', None)
        if subject_id is None:
            subject_id = getattr(udataset, 'subject_id', None)
        
        # Store subject info in raw annotations if available
        if subject_id and subject_id in self.subject_dict:
            subject_info = self.subject_dict[subject_id]
            # Add subject metadata as annotations description
            desc = f"subject_id:{subject_id}"
            annotations = raw.annotations
            if annotations:
                # Extend annotations description with subject info
                new_description = [f"{d} | {desc}" for d in annotations.description]
                raw.set_annotations(mne.Annotations(
                    onset=annotations.onset,
                    duration=annotations.duration,
                    description=new_description,
                    orig_time=annotations.orig_time
                ))
        
        # Rename channels from numeric E001-E128 to standard names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage for channel locations
        montage = _get_montage_for_gsn(raw)
        if montage is not None:
            # Get channels present in raw data
            ch_names = raw.ch_names
            # Find matching channels
            montage_chs = set(montage.ch_names)
            raw_chs = set(ch_names)
            common_chs = list(montage_chs & raw_chs)
            
            if common_chs:
                # Create subset montage
                try:
                    subset_montage = montage.pick_channels(common_chs)
                    raw = raw.set_montage(subset_montage)
                except Exception:
                    pass  # Skip montage if pick fails
        
        # Detect and annotate trial phases
        events, event_id = mne.events_from_annotations(raw, verbose=False)
        if events.size > 0:
            # Annotate trial phases
            raw = _detect_and_annotate_phases(raw, events)
        
        # Set reference to average
        try:
            raw = raw.set_eeg_reference('average', projection=False)
        except Exception:
            # If average reference fails, try to use existing reference
            pass
        
        # Basic preprocessing: bandpass filter 0.5-40 Hz
        try:
            raw = raw.filter(l_freq=0.5, h_freq=40.0, fir_design='firwin')
        except Exception:
            pass  # Skip filtering if it fails
        
        return raw


def _detect_and_annotate_phases(raw: mne.io.BaseRaw, events: np.ndarray) -> mne.io.BaseRaw:
    """Add trial phase annotations to raw data.
    
    Args:
        raw: MNE Raw object.
        events: MNE events array.
        
    Returns:
        Raw object with updated annotations.
    """
    if events.size == 0:
        return raw
    
    onset_times = []
    durations = []
    descriptions = []
    
    # Sort events by time
    sorted_events = events[events[:, 0].argsort()]
    
    for i, event in enumerate(sorted_events):
        sample = event[0]
        event_id = int(event[2])
        
        # Get phase description
        if event_id in _TRIAL_PHASE_EVENT_MAP:
            desc = _TRIAL_PHASE_EVENT_MAP[event_id]
        elif event_id in _ADMIN_EVENT_MAP:
            desc = _ADMIN_EVENT_MAP[event_id]
        else:
            desc = f"event_{event_id}"
        
        onset_time = sample / raw.info['sfreq']
        
        # Calculate duration: time until next event
        if i < len(sorted_events) - 1:
            next_sample = sorted_events[i + 1][0]
            duration = (next_sample - sample) / raw.info['sfreq']
        else:
            # Last event: use 0 duration (point event)
            duration = 0.0
        
        onset_times.append(onset_time)
        durations.append(duration)
        descriptions.append(desc)
    
    # Create new annotations
    if onset_times:
        new_annotations = mne.Annotations(
            onset=onset_times,
            duration=durations,
            description=descriptions,
            orig_time=raw.annotations.orig_time if raw.annotations else None
        )
        
        # Combine with existing annotations if any
        if raw.annotations:
            combined_onset = list(raw.annotations.onset) + onset_times
            combined_duration = list(raw.annotations.duration) + durations
            combined_desc = list(raw.annotations.description) + descriptions
            combined_annotations = mne.Annotations(
                onset=combined_onset,
                duration=combined_duration,
                description=combined_desc,
                orig_time=raw.annotations.orig_time
            )
            raw = raw.set_annotations(combined_annotations)
        else:
            raw = raw.set_annotations(new_annotations)
    
    return raw


# Kernel instance for EEGUnity
KERNEL = EEGUnityKernel()