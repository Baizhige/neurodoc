"""OpenNeuro ds004256 stage1 kernel for EEGUnity.

Dataset: Encoding of Sound Source Elevation in Human Cortex
Source: https://openneuro.org/datasets/ds004256 (DOI: 10.18112/openneuro.ds004256.v1.0.5)

This kernel handles the BIDS-format dataset from OpenNeuro, extracting subject metadata
from participants.tsv, standardizing 64-channel EEG montage, and creating annotations
from events.tsv. The dataset contains two tasks: deviantdetection and oneback.

Sampling rate: 500 Hz | Channels: 64 | Subjects: 53
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 10-20 64-channel system mapping for BrainVision actiCAP 64Ch Standard-2
# Source: Brain Products actiCAP 64Ch Standard-2 montage documentation
# Annotated by: LLM, 2026-04-08 (standard commercial cap layout, widely documented)
_CHANNEL_MAP = {
    "Fp1": ["Fp1", "EEG001", "1"],
    "Fp2": ["Fp2", "EEG002", "2"],
    "F7": ["F7", "EEG003", "3"],
    "F3": ["F3", "EEG004", "4"],
    "Fz": ["Fz", "EEG005", "5"],
    "F4": ["F4", "EEG006", "6"],
    "F8": ["F8", "EEG007", "7"],
    "FC5": ["FC5", "EEG008", "8"],
    "FC1": ["FC1", "EEG009", "9"],
    "FC2": ["FC2", "EEG010", "10"],
    "FC6": ["FC6", "EEG011", "11"],
    "T7": ["T7", "EEG012", "12"],
    "C3": ["C3", "EEG013", "13"],
    "Cz": ["Cz", "EEG014", "14"],
    "C4": ["C4", "EEG015", "15"],
    "T8": ["T8", "EEG016", "16"],
    "CP5": ["CP5", "EEG017", "17"],
    "CP1": ["CP1", "EEG018", "18"],
    "CP2": ["CP2", "EEG019", "19"],
    "CP6": ["CP6", "EEG020", "20"],
    "P7": ["P7", "EEG021", "21"],
    "P3": ["P3", "EEG022", "22"],
    "Pz": ["Pz", "EEG023", "23"],
    "P4": ["P4", "EEG024", "24"],
    "P8": ["P8", "EEG025", "25"],
    "O1": ["O1", "EEG026", "26"],
    "Oz": ["Oz", "EEG027", "27"],
    "O2": ["O2", "EEG028", "28"],
    "Fpz": ["Fpz", "EEG029", "29"],
    "AFz": ["AFz", "EEG030", "30"],
    "F1": ["F1", "EEG031", "31"],
    "F2": ["F2", "EEG032", "32"],
    "AF3": ["AF3", "EEG033", "33"],
    "AF4": ["AF4", "EEG034", "34"],
    "FC3": ["FC3", "EEG035", "35"],
    "FC4": ["FC4", "EEG036", "36"],
    "F5": ["F5", "EEG037", "37"],
    "F6": ["F6", "EEG038", "38"],
    "C5": ["C5", "EEG039", "39"],
    "C6": ["C6", "EEG040", "40"],
    "CP3": ["CP3", "EEG041", "41"],
    "CP4": ["CP4", "EEG042", "42"],
    "P5": ["P5", "EEG043", "43"],
    "P6": ["P6", "EEG044", "44"],
    "PO3": ["PO3", "EEG045", "45"],
    "PO4": ["PO4", "EEG046", "46"],
    "F9": ["F9", "EEG047", "47"],
    "F10": ["F10", "EEG048", "48"],
    "CCP5": ["CCP5", "EEG049", "49"],
    "CCP1": ["CCP1", "EEG050", "50"],
    "CCP2": ["CCP2", "EEG051", "51"],
    "CCP6": ["CCP6", "EEG052", "52"],
    "TP9": ["TP9", "EEG053", "53"],
    "TP10": ["TP10", "EEG054", "54"],
    "CPP5": ["CPP5", "EEG055", "55"],
    "CPP1": ["CPP1", "EEG056", "56"],
    "CPP2": ["CPP2", "EEG057", "57"],
    "CPP6": ["CPP6", "EEG058", "58"],
    "P9": ["P9", "EEG059", "59"],
    "P10": ["P10", "EEG060", "60"],
    "POz": ["POz", "EEG061", "61"],
    "AF7": ["AF7", "EEG062", "62"],
    "AF8": ["AF8", "EEG063", "63"],
    "PO7": ["PO7", "EEG064", "64"],
    "PO8": ["PO8", "EEG065", "65"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for standard_name, aliases in _CHANNEL_MAP.items():
        if standard_name in existing:
            continue
        for alias in aliases:
            if alias in existing and alias != standard_name:
                rename_map[alias] = standard_name
                break
    
    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'sub-(\w+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # BIDS structure: sub-XXX/eeg/sub-XXX_task-YYY[_run-ZZZ]_eeg.<ext>
    # events.tsv: sub-XXX/eeg/sub-XXX_task-YYY[_run-ZZZ]_events.tsv
    base = os.path.splitext(file_path)[0]
    # Remove _eeg suffix if present
    base = re.sub(r'_eeg$', '', base)
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: some files may have different naming
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # Extract task and run info
    task_match = re.search(r'(sub-\w+_task-\w+)(?:_run-\w+)?', file_name)
    if task_match:
        base_name = task_match.group(1)
        # Check for run
        run_match = re.search(r'_run-(\w+)', file_name)
        if run_match:
            candidate = os.path.join(dir_name, f"{base_name}_run-{run_match.group(1)}_events.tsv")
        else:
            candidate = os.path.join(dir_name, f"{base_name}_events.tsv")
        if os.path.exists(candidate):
            return candidate
    
    # Try any events.tsv in same directory matching subject
    sub_match = re.search(r'(sub-\w+)', file_name)
    if sub_match:
        sub_id = sub_match.group(1)
        for f in os.listdir(dir_name):
            if f.startswith(sub_id) and f.endswith("_events.tsv"):
                return os.path.join(dir_name, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        candidate = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        current_dir = os.path.dirname(current_dir)
    return None


@dataclass
class OpenNeuroDS004256Kernel:
    """Stage1 kernel for OpenNeuro ds004256 dataset."""

    KERNEL_ID: str = "openneuro-ds004256-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # --- 1. Channel renaming to standard 10-20 ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # --- 2. Set montage ---
        # Use standard 10-20 montage for 64-channel system
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in raw
            ch_names = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if ch_names:
                montage = montage.copy().pick(ch_names)
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage optional, continue without
        
        # --- 3. Read participants.tsv for subject metadata ---
        subject_id = _get_subject_id_from_path(file_path)
        participants_path = _find_participants_tsv(file_path)
        
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        amplifier = "unknown"
        cap = "unknown"
        
        if participants_path and subject_id:
            try:
                participants_df = pd.read_csv(participants_path, sep="\t")
                # Find subject row
                sub_row = participants_df[participants_df["participant_id"] == subject_id]
                if sub_row.empty:
                    # Try without "sub-" prefix
                    sub_num = subject_id.replace("sub-", "")
                    sub_row = participants_df[
                        (participants_df["participant_id"] == sub_num) |
                        (participants_df["participant_id"] == f"sub-{sub_num}")
                    ]
                
                if not sub_row.empty:
                    sub_row = sub_row.iloc[0]
                    if "age" in sub_row:
                        age = str(sub_row["age"])
                    if "sex" in sub_row:
                        sex = str(sub_row["sex"])
                    if "handedness" in sub_row:
                        handedness = str(sub_row["handedness"])
                    if "amplifier" in sub_row:
                        amplifier = str(sub_row["amplifier"])
                    if "cap" in sub_row:
                        cap = str(sub_row["cap"])
            except Exception:
                pass  # Keep defaults on error
        
        # --- 4. Read events.tsv and create annotations ---
        events_path = _find_events_tsv(file_path)
        
        # Collect trial onset times for derived misc channel
        trial_onset_times = []
        
        if events_path and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                # BIDS events.tsv columns: onset, duration, trial_type, ...
                if "onset" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
                    descriptions = events_df["trial_type"].values if "trial_type" in events_df.columns else np.array(["event"] * len(onsets))
                    
                    # Convert to strings for annotations
                    descriptions = [str(d) for d in descriptions]
                    
                    # Create MNE annotations
                    annot = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions
                    )
                    raw.set_annotations(annot)
                    
                    # Collect trial onset times for derived misc channel
                    trial_onset_times = list(onsets)
            except Exception:
                pass  # No events on error
        
        # --- 5. Create derived misc channel: trial_onset_time ---
        # Create a step function that is 1 at trial onsets and 0 elsewhere
        sfreq = raw.info["sfreq"]
        n_times = len(raw.times)
        trial_onset_data = np.zeros((1, n_times))
        
        for onset in trial_onset_times:
            sample_idx = int(round(onset * sfreq))
            if 0 <= sample_idx < n_times:
                trial_onset_data[0, sample_idx] = 1.0
        
        # Create info for misc channel
        misc_info = mne.create_info(
            ch_names=["trial_onset_time"],
            sfreq=sfreq,
            ch_types=["misc"]
        )
        misc_raw = mne.io.RawArray(trial_onset_data, misc_info)
        
        # Add misc channel to raw
        raw.add_channels([misc_raw], force_update_info=True)
        
        # --- 6. Set description with metadata ---
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        })
        
        return raw


KERNEL = OpenNeuroDS004256Kernel()