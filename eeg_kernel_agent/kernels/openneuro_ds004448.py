"""Dataset-specific kernel for openneuro ds004448 (BMI-HDEEG dataset 4).

High-density EEG motor imagery dataset with 130 channels, 1000 Hz sampling rate.
Participants performed sensorimotor rhythm-based BCI with two-class motor imagery
(left hand vs right hand) and relaxation/rest periods.

BIDS-compliant dataset with EDF files, participants.tsv, and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds004448 | DOI: 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex", "handedness", "amplifier", "cap", "gender"]

# Required native misc channels (already in raw data)
_REQUIRED_NATIVE_MISC = []

# Required derived misc channels (kernel must create)
_REQUIRED_DERIVED_MISC = ["trial_index"]

# BrainVision/EDF channel name standardization for 130-channel high-density cap
# Source: BMI-HDEEG paper (10.1038/s41597-023-02260-6) describes 128 EEG + 2 EOG channels
# Standard extended 10-20 layout used with BrainAmp system
# LLM 推断，需人类复核
_CHANNEL_STANDARD_MAP: Dict[str, str] = {
    # Pre-frontal
    "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
    # Anterior frontal
    "AF7": "AF7", "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4", "AF8": "AF8",
    # Frontal
    "F7": "F7", "F5": "F5", "F3": "F3", "F1": "F1", "FZ": "Fz",
    "F2": "F2", "F4": "F4", "F6": "F6", "F8": "F8",
    # Frontal-temporal
    "FT7": "FT7", "FT8": "FT8",
    # Frontal-central
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FCZ": "FCz",
    "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    # Temporal
    "T7": "T7", "T8": "T8",
    # Central
    "C5": "C5", "C3": "C3", "C1": "C1", "CZ": "Cz",
    "C2": "C2", "C4": "C4", "C6": "C6",
    # Temporal-parietal
    "TP7": "TP7", "TP8": "TP8",
    # Central-parietal
    "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CPZ": "CPz",
    "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
    # Parietal
    "P7": "P7", "P5": "P5", "P3": "P3", "P1": "P1", "PZ": "Pz",
    "P2": "P2", "P4": "P4", "P6": "P6", "P8": "P8",
    # Parietal-occipital
    "PO7": "PO7", "PO5": "PO5", "PO3": "PO3", "POZ": "POz",
    "PO4": "PO4", "PO6": "PO6", "PO8": "PO8",
    # Occipital
    "O1": "O1", "OZ": "Oz", "O2": "O2",
    # Extra positions common in 128+ channel systems
    "IZ": "Iz",
    # EOG channels
    "EOG1": "EOG1", "EOG2": "EOG2",
    # Common alternative EOG names
    "VEOG": "VEOG", "HEOG": "HEOG",
}


def _standardize_channel_name(ch_name: str) -> str:
    """Convert raw channel name to standard 10-20 naming."""
    ch_clean = ch_name.strip()
    
    # Remove BrainVision EEG prefix
    if ch_clean.upper().startswith("EEG "):
        ch_clean = ch_clean[4:]
    elif ch_clean.upper().startswith("EEG-"):
        ch_clean = ch_clean[4:]
    elif ch_clean.upper().startswith("EEG"):
        ch_clean = ch_clean[3:]
    
    # Direct lookup in map
    upper_clean = ch_clean.upper()
    if upper_clean in _CHANNEL_STANDARD_MAP:
        return _CHANNEL_STANDARD_MAP[upper_clean]
    
    # Already standard case
    return ch_clean


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # BIDS naming: sub-XXX_ses-YY_task-ZZ[_run-WW]_eeg.edf -> sub-XXX_ses-YY_task-ZZ[_run-WW]_events.tsv
    base = file_path.replace("_eeg.edf", "").replace("_eeg.bdf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run entity
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # Pattern match for BIDS files
    parts = file_name.replace("_eeg.edf", "").split("_")
    for i in range(len(parts), 0, -1):
        candidate_base = "_".join(parts[:i])
        candidate = os.path.join(dir_name, candidate_base + "_events.tsv")
        if os.path.exists(candidate):
            return candidate
    
    # Search directory for matching events.tsv
    if os.path.isdir(dir_name):
        for f in os.listdir(dir_name):
            if f.endswith("_events.tsv"):
                return os.path.join(dir_name, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file directory."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at root
        candidate = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        current_dir = os.path.dirname(current_dir)
    return None


def _extract_subject_id(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    file_name = os.path.basename(file_path)
    # Match sub-XXX pattern
    match = re.search(r'(sub-[a-zA-Z0-9]+)', file_name)
    if match:
        return match.group(1)
    return None


@dataclass
class OpenNeuroDS004448Kernel:
    """Stage1 kernel for OpenNeuro ds004448 (BMI-HDEEG dataset 4)."""

    KERNEL_ID: str = "openneuro-ds004448-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Preload raw data to allow adding channels
        if not raw.preload:
            raw.load_data()

        # --- 1. Channel renaming to standard 10-20 ---
        rename_map = {}
        for ch_name in raw.ch_names:
            std_name = _standardize_channel_name(ch_name)
            if std_name != ch_name:
                rename_map[ch_name] = std_name
        
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # --- 2. Set channel types ---
        # Mark EOG channels
        eog_names = [ch for ch in raw.ch_names if ch.upper() in ["EOG1", "EOG2", "VEOG", "HEOG", "EOG"]]
        ch_types = {}
        for ch in eog_names:
            ch_types[ch] = "eog"
        
        # Mark any non-EEG, non-EOG as misc if needed
        for ch in raw.ch_names:
            if ch not in ch_types:
                # Default to EEG; format_channel_name in EEGUnity will handle standard types
                pass
        
        if ch_types:
            raw.set_channel_types(ch_types)

        # --- 3. Set montage ---
        # 128-channel extended 10-20 layout
        # LLM 推断，需人类复核
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            try:
                raw.set_montage("standard_1005", match_case=False, on_missing="warn")
            except Exception:
                pass  # Non-standard cap or missing positions

        # --- 4. Read participants.tsv for subject info ---
        subject_id = _extract_subject_id(file_path)
        participants_path = _find_participants_tsv(file_path)
        
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        amplifier = "unknown"
        cap = "unknown"
        gender = "unknown"

        if participants_path and subject_id:
            try:
                participants_df = pd.read_csv(participants_path, sep="\t")
                # Find matching row
                sub_row = participants_df[participants_df["participant_id"] == subject_id]
                if sub_row.empty:
                    # Try without "sub-" prefix
                    sub_id_num = subject_id.replace("sub-", "")
                    sub_row = participants_df[participants_df["participant_id"] == sub_id_num]
                if sub_row.empty:
                    # Try with "sub-" prefix
                    sub_row = participants_df[participants_df["participant_id"] == "sub-" + sub_id_num]
                
                if not sub_row.empty:
                    row_data = sub_row.iloc[0]
                    
                    # Map participants.tsv columns to required fields
                    if "age" in row_data:
                        age = str(row_data["age"])
                    if "sex" in row_data:
                        sex = str(row_data["sex"])
                    if "handedness" in row_data:
                        handedness = str(row_data["handedness"])
                    if "amplifier" in row_data:
                        amplifier = str(row_data["amplifier"])
                    if "cap" in row_data:
                        cap = str(row_data["cap"])
                    if "gender" in row_data:
                        gender = str(row_data["gender"])
            except Exception:
                pass  # Keep defaults if file can't be read

        # --- 5. Read events.tsv and create annotations ---
        events_path = _find_events_tsv(file_path)
        event_onsets = []
        event_durations = []
        event_descriptions = []
        
        if events_path and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                # BIDS events.tsv columns: onset, duration, trial_type, etc.
                for _, ev_row in events_df.iterrows():
                    onset = float(ev_row["onset"])
                    duration = float(ev_row.get("duration", 0))
                    trial_type = str(ev_row.get("trial_type", "unknown"))
                    event_onsets.append(onset)
                    event_durations.append(duration)
                    event_descriptions.append(trial_type)
            except Exception:
                pass  # Keep empty if file can't be read
        
        # Create annotations from events
        if event_onsets:
            # Remove any existing annotations first to avoid duplicates
            raw.set_annotations(None)
            annotations = mne.Annotations(
                onset=event_onsets,
                duration=event_durations,
                description=event_descriptions,
                orig_time=raw.info["meas_date"]
            )
            raw.set_annotations(annotations)

        # --- 6. Create derived misc channels ---
        # trial_index: constant broadcast of 0 for participants.tsv sources
        # (no trial-level info in participants.tsv, so use constant)
        trial_index_data = np.zeros((1, len(raw.times)))
        
        # Create info for new misc channel
        ch_info = mne.create_info(
            ch_names=["trial_index"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"]
        )
        trial_index_raw = mne.io.RawArray(trial_index_data, ch_info, verbose=False)
        raw.add_channels([trial_index_raw], force_update_info=True)

        # --- 7. Set description with eegunity metadata ---
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "handedness": handedness,
                "amplifier": amplifier,
                "cap": cap,
                "gender": gender,
            },
        })

        return raw


KERNEL = OpenNeuroDS004448Kernel()