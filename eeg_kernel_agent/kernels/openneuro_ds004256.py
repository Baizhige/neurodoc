"""OpenNeuro ds004256 stage1 kernel for EEGUnity.

Dataset: Encoding of Sound Source Elevation in Human Cortex
Source: https://openneuro.org/datasets/ds004256 (DOI: 10.18112/openneuro.ds004256.v1.0.5)

This kernel handles the BIDS-format dataset from OpenNeuro, extracting subject metadata
from participants.tsv and standardizing event codes for three paradigms:
- Sound Elevation Decoding (Stimulus/S 1-7)
- DeviantDetection (Stimulus/S 7)
- Oneback (Stimulus/S 1-6)

Sampling rate: 500 Hz | Channels: 64 | Subjects: 53
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: OpenNeuro ds004256 participants.tsv
# Annotated by: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Standard 10-20 64-channel system mapping
# Source: BrainVision montage documentation for 64-channel standard EEG
# Annotated by: Human, 2026-04-08
_64CH_STANDARD_MONTAGE = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
    "T7", "C3", "Cz", "C4", "T8", "CP5", "CP1", "CP2", "CP6", "P7", "P3",
    "Pz", "P4", "P8", "O1", "Oz", "O2", "Fpz", "AFz", "F1", "F2", "AF3",
    "AF4", "FC3", "FC4", "F5", "F6", "C5", "C6", "CP3", "CP4", "P5", "P6",
    "PO3", "PO4", "F9", "F10", "CCP5", "CCP1", "CCP2", "CCP6", "TP9", "TP10",
    "CPP5", "CPP1", "CPP2", "CPP6", "P9", "P10", "POz", "AF7", "AF8", "PO7",
    "PO8"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.
    
    Attempts multiple matching strategies for flexibility.
    Source: Standard 10-20 electrode naming conventions
    """
    rename_map: Dict[str, str] = {}
    
    # Common alias patterns for standard 10-20 system
    alias_groups = [
        # Standard names - map numbered EEG channels to standard names
        ("Fp1", ["EEG001", "EEG001", "1"]),
        ("Fp2", ["EEG002", "EEG002", "2"]),
        ("F7", ["EEG003", "EEG003", "3"]),
        ("F3", ["EEG004", "EEG004", "4"]),
        ("Fz", ["EEG005", "EEG005", "5"]),
        ("F4", ["EEG006", "EEG006", "6"]),
        ("F8", ["EEG007", "EEG007", "7"]),
        ("FC5", ["EEG008", "EEG008", "8"]),
        ("FC1", ["EEG009", "EEG009", "9"]),
        ("FC2", ["EEG010", "EEG010", "10"]),
        ("FC6", ["EEG011", "EEG011", "11"]),
        ("T7", ["EEG012", "EEG012", "12"]),
        ("C3", ["EEG013", "EEG013", "13"]),
        ("Cz", ["EEG014", "EEG014", "14"]),
        ("C4", ["EEG015", "EEG015", "15"]),
        ("T8", ["EEG016", "EEG016", "16"]),
        ("CP5", ["EEG017", "EEG017", "17"]),
        ("CP1", ["EEG018", "EEG018", "18"]),
        ("CP2", ["EEG019", "EEG019", "19"]),
        ("CP6", ["EEG020", "EEG020", "20"]),
        ("P7", ["EEG021", "EEG021", "21"]),
        ("P3", ["EEG022", "EEG022", "22"]),
        ("Pz", ["EEG023", "EEG023", "23"]),
        ("P4", ["EEG024", "EEG024", "24"]),
        ("P8", ["EEG025", "EEG025", "25"]),
        ("O1", ["EEG026", "EEG026", "26"]),
        ("Oz", ["EEG027", "EEG027", "27"]),
        ("O2", ["EEG028", "EEG028", "28"]),
    ]
    
    existing_names = set(raw.ch_names)
    
    # Strategy 1: Match EEG### pattern to standard names
    for ch in raw.ch_names:
        if ch.startswith("EEG"):
            try:
                idx = int(ch.replace("EEG", ""))
                if 1 <= idx <= 64:
                    # Map to standard_1020 compatible names
                    standard_names = [
                        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
                        "FC5", "FC1", "FC2", "FC6", "T7", "C3", "Cz", "C4", "T8",
                        "CP5", "CP1", "CP2", "CP6", "P7", "P3", "Pz", "P4", "P8",
                        "O1", "Oz", "O2"
                    ]
                    if idx <= len(standard_names):
                        rename_map[ch] = standard_names[idx - 1]
            except ValueError:
                continue
    
    return rename_map


def _read_bids_participants(bids_dir: str) -> Dict[str, Dict[str, Any]]:
    """Read participants.tsv from BIDS dataset.
    
    Returns dict mapping subject ID to metadata dict.
    Source: OpenNeuro ds004256 dataset_description.json
    """
    participants_file = os.path.join(bids_dir, "participants.tsv")
    subject_info = {}
    
    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).strip()
                if subj_id:
                    info = {}
                    # Extract age
                    age_val = row.get("age", None)
                    if pd.notna(age_val):
                        try:
                            age_str = str(int(float(age_val)))
                            info["age"] = age_str
                        except (ValueError, TypeError):
                            info["age"] = str(age_val)
                    else:
                        info["age"] = "unknown"
                    
                    # Extract sex
                    sex_val = row.get("sex", row.get("gender", None))
                    if pd.notna(sex_val):
                        sex_lower = str(sex_val).lower().strip()
                        if sex_lower in ["m", "male", "man"]:
                            info["sex"] = "male"
                        elif sex_lower in ["f", "female", "woman"]:
                            info["sex"] = "female"
                        else:
                            info["sex"] = "unknown"
                    else:
                        info["sex"] = "unknown"
                    
                    subject_info[subj_id] = info
        except Exception as e:
            print(f"Warning: Could not read participants.tsv: {e}")
    
    return subject_info


def _extract_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path.
    
    Pattern: sub-<subject_id>
    """
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


@dataclass
class OpenNeuroDS004256Kernel:
    """Stage1 kernel for OpenNeuro ds004256 dataset.
    
    Handles BIDS-format EEG data with three paradigms:
    - Sound Elevation Decoding (7 classes: Stimulus/S 1-7)
    - DeviantDetection (Stimulus/S 7 only)
    - Oneback (6 classes: Stimulus/S 1-6)
    """

    KERNEL_ID: str = "openneuro-ds004256-stage1"

    # Event mapping for raw meta: original -> canonical
    # Source: Dataset documentation and analysis.md
    EVENT_MAP: Dict[str, str] = field(default_factory=lambda: {
        "Stimulus/S  1": "Stimulus/S 1",
        "Stimulus/S  2": "Stimulus/S 2",
        "Stimulus/S  3": "Stimulus/S 3",
        "Stimulus/S  4": "Stimulus/S 4",
        "Stimulus/S  5": "Stimulus/S 5",
        "Stimulus/S  6": "Stimulus/S 6",
        "Stimulus/S  7": "Stimulus/S 7",
    })

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object loaded from BIDS EEG file
        row : Locator row with File Path and metadata
        
        Returns
        -------
        mne.io.BaseRaw : Processed Raw object with standardized metadata
        """
        file_path = row.get("File Path", "")
        
        # Extract subject ID and read BIDS participants info
        subject_id = _extract_subject_id_from_path(file_path)
        bids_dir = os.path.dirname(os.path.dirname(file_path))  # Go up to dataset root
        
        subject_info = _read_bids_participants(bids_dir)
        subj_meta = subject_info.get(subject_id, {}) if subject_id else {}
        
        # Build eegunity_description
        # Source: Dataset documentation and inference
        # Amplifier/cap: Brain Products BrainAmp (standard for this dataset format)
        # LLM 推断，需人类复核
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subj_meta.get("age", "unknown"),
                "sex": subj_meta.get("sex", "unknown"),
                "amplifier": "BrainAmp",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": "unknown",  # Not in participants.tsv
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels if non-standard
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception as e:
                print(f"Warning: Channel rename failed: {e}")
        
        # Set standard montage if most channels are standard names
        try:
            # Get standard 10-20 positions
            montage = mne.channels.make_standard_standard_montage("standard_1020")
            # Check if we have enough matching channels
            ch_match = sum(1 for ch in raw.ch_names if ch in montage.ch_names)
            if ch_match >= 20:  # If we have 20+ standard channels, apply montage
                raw.set_montage(montage, on_missing="ignore")
        except Exception as e:
            print(f"Warning: Montage setup failed: {e}")
        
        # Remap annotations/events from BIDS to standardized form
        if raw.annotations:
            new_descriptions = []
            for ann in raw.annotations:
                orig_desc = str(ann.description).strip()
                # Handle both single and double space variants
                normalized = orig_desc.replace("  ", " ")
                new_desc = self.EVENT_MAP.get(normalized, orig_desc)
                new_descriptions.append(new_desc)
            
            if new_descriptions:
                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(new_annotations)
        
        # If no annotations but we have events from stim channel,
        # extract and create annotations
        if not raw.annotations or len(raw.annotations) == 0:
            events, event_id = mne.events_from_annotations(raw)
            if len(events) > 0:
                # Filter for stimulus events
                stim_events = []
                stim_desc_map = {}
                stim_counter = 0
                for desc, eid in event_id.items():
                    if "Stimulus" in str(desc) or "S  " in str(desc) or "S " in str(desc):
                        normalized = str(desc).replace("  ", " ")
                        canonical = self.EVENT_MAP.get(normalized, normalized)
                        stim_desc_map[eid] = canonical
                
                if stim_desc_map:
                    new_events = []
                    for ev in events:
                        eid = ev[2]
                        if eid in stim_desc_map:
                            new_events.append({
                                "onset": ev[0] / raw.info["sfreq"],
                                "duration": 0.0,
                                "description": stim_desc_map[eid],
                            })
                    
                    if new_events:
                        onsets = [e["onset"] for e in new_events]
                        durations = [e["duration"] for e in new_events]
                        descs = [e["description"] for e in new_events]
                        new_annotations = mne.Annotations(
                            onset=onsets,
                            duration=durations,
                            description=descs,
                        )
                        raw.set_annotations(new_annotations)
        
        return raw


KERNEL = OpenNeuroDS004256Kernel()