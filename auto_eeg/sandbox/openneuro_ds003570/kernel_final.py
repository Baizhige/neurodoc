"""Dataset-specific kernel for openneuro ds003570.

EEG auditory oddball task with musical chord progressions.
Extracts chord-level events from events.tsv and maps stimulus conditions
(standard, exemplar_deviant, function_deviant) to annotations for epoching.

Source: https://openneuro.org/datasets/ds003570
Source: DOI 10.1016/j.neuroimage.2021.118458

Paradigm:
- Participants listened to sequences of three-chord musical progressions
- Oddball paradigm with standard (85%), exemplar_deviant (7.5%), function_deviant (7.5%)
- Events: STATUS system marker + stimulus events in events.tsv

Stimulus event naming convention:
- e.g., "five6_S" → standard chord (suffix _S)
- e.g., "four6_deviantE" → exemplar deviant (same functional class, suffix _deviantE)
- e.g., "fourRoot_deviantF" → function deviant (different functional class, suffix _deviantF)
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Condition suffix mapping from stimulus event names
# Source: DOI 10.1016/j.neuroimage.2021.118458, Table 1
# Annotator: LLM, 2026-04-08, requires human verification
_CONDITION_MAP: Dict[str, str] = {
    "_S": "standard",
    "_deviantE": "exemplar_deviant",
    "_deviantF": "function_deviant",
}

# Standard 10-20 system channel names for 64-channel EEG
# Source: standard_1020 montage, BrainVision / BIDS convention
# Annotator: LLM, 2026-04-08, requires human verification
_STANDARD_10_20_CHANNELS: List[str] = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T7", "C3", "Cz",
    "C4", "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "Oz", "O2",
    "F1", "F2", "C1", "C2", "P1", "P2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F5", "F6", "FC5", "FC3", "FC1", "FC2", "FC4", "FC6",
    "FT7", "FT8", "C5", "C6", "TP7", "TP8",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P5", "P6", "PO7", "PO3", "POz", "PO4", "PO8",
    "M1", "M2", "CB1", "CB2",
]


def _find_bids_dir(eeg_file_path: str) -> Optional[str]:
    """Find BIDS root directory from EEG file path.
    
    Walks up the directory tree to find dataset_description.json.
    """
    current = os.path.dirname(eeg_file_path)
    while current and current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "dataset_description.json")):
            return current
        current = os.path.dirname(current)
    return None


def _find_events_tsv(bids_dir: str, subject_id: str) -> Optional[str]:
    """Find events.tsv file for a given subject.
    
    Checks multiple possible locations in BIDS structure.
    """
    candidates = [
        # BIDS root
        os.path.join(bids_dir, f"{subject_id}_events.tsv"),
        os.path.join(bids_dir, "sub-" + subject_id.lstrip("sub-"), "sub-" + subject_id.lstrip("sub-") + "_events.tsv"),
        # Inside sub-* directories
        os.path.join(bids_dir, "sub-" + subject_id.lstrip("sub-"), f"sub-" + subject_id.lstrip("sub-") + "_events.tsv"),
        # Inside eeg subdirectories
        os.path.join(bids_dir, "sub-" + subject_id.lstrip("sub-"), "eeg", f"sub-" + subject_id.lstrip("sub-") + "_events.tsv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _parse_stimulus_condition(event_name: str, paradigm: str) -> Optional[str]:
    """Parse stimulus event name to extract condition label.
    
    Args:
        event_name: Stimulus event name (e.g., "five6_S", "four6_deviantE")
        paradigm: Detected paradigm identifier
        
    Returns:
        Condition label: "standard", "exemplar_deviant", "function_deviant",
        or specific event type ("one", "two", "three"), or None for unknown
    """
    if not isinstance(event_name, str):
        return None
    
    # Check for chord onset markers
    event_lower = event_name.lower()
    if event_lower in ("one", "two", "three", "status"):
        return event_lower
    
    # Check for condition suffixes
    for suffix, condition in _CONDITION_MAP.items():
        if event_name.endswith(suffix):
            return condition
    
    # Check for pattern matching (e.g., "four6", "five6", "fourRoot")
    # These indicate chord positions in the progression
    match = re.match(r'^(one|two|three|four|five|six|seven|sevenRoot|fourRoot|five6|six7)?.*$', 
                     event_name, re.IGNORECASE)
    if match:
        # Check if it's a chord onset marker
        base_event = match.group(1)
        if base_event and base_event.lower() in ("one", "two", "three"):
            return base_event.lower()
    
    return event_name


class OpenNeuroDS003570Kernel:
    """Stage1 kernel for openneuro ds003570 dataset.
    
    Handles BIDS-formatted EEG data with events.tsv containing chord onset markers.
    Maps stimulus event conditions for oddball paradigm analysis.
    
    Key features:
    - Loads stimulus events from events.tsv
    - Maps condition suffixes (_S, _deviantE, _deviantF) to labels
    - Supports epoch alignment on chord onset events (one, two, three)
    - Sets standard 10-20 montage for 64-channel EEG
    - Handles high sampling rate (2048 Hz) data
    """
    
    KERNEL_ID: str = "openneuro-ds003570-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object with raw EEG data.
        row
            Dataset row with file_path and subject information.
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw data with standardized events and channel names.
        """
        # Extract file path and subject ID
        file_path = row.get("File Path", "") or row.get("file_path", "")
        subject_id = row.get("subject_id", "") or row.get("participant_id", "") or "unknown"
        subject_id = subject_id.lstrip("sub-")
        
        # Update raw description with eegunity metadata
        # Age: missing from dataset documentation, set to "unknown"
        # Source: analysis.md Info table
        # Annotator: LLM, 2026-04-08, requires human verification
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Process existing raw annotations (STATUS markers)
        if raw.annotations is not None and len(raw.annotations) > 0:
            status_mask = np.array(["STATUS" in str(d) for d in raw.annotations.description])
            if status_mask.any():
                status_onsets = raw.annotations.onset[status_mask]
                status_descriptions = raw.annotations.description[status_mask]
                
                # Create STATUS annotations as raw meta events
                status_annotations = mne.Annotations(
                    onset=status_onsets,
                    duration=np.zeros(len(status_onsets)),
                    description=["STATUS" if "STATUS" in str(d) else str(d) for d in status_descriptions],
                    orig_time=raw.annotations.orig_time,
                )
            else:
                status_annotations = mne.Annotations(
                    onset=np.array([]),
                    duration=np.array([]),
                    description=np.array([]),
                    orig_time=raw.annotations.orig_time,
                )
        else:
            status_annotations = mne.Annotations(
                onset=np.array([]),
                duration=np.array([]),
                description=np.array([]),
            )
        
        # Load stimulus events from events.tsv
        bids_dir = _find_bids_dir(file_path)
        paradigm = "ODDBALL"  # Default paradigm identifier
        
        stimulus_annotations = mne.Annotations(
            onset=np.array([]),
            duration=np.array([]),
            description=np.array([]),
        )
        
        if bids_dir:
            events_tsv = _find_events_tsv(bids_dir, subject_id)
            if events_tsv and os.path.exists(events_tsv):
                try:
                    events_df = pd.read_csv(events_tsv, sep="\t")
                    
                    if "onset" in events_df.columns and "trial_type" in events_df.columns:
                        # Build condition labels from event names
                        conditions = []
                        for event_name in events_df["trial_type"]:
                            cond = _parse_stimulus_condition(str(event_name), paradigm)
                            conditions.append(cond if cond else "unknown")
                        
                        # Create annotations for stimulus events
                        stimulus_annotations = mne.Annotations(
                            onset=events_df["onset"].values.astype(float),
                            duration=np.zeros(len(events_df)),
                            description=conditions,
                            orig_time=None,  # Relative to recording start
                        )
                        
                except Exception:
                    pass  # Keep empty annotations if loading fails
        
        # Merge STATUS and stimulus annotations
        all_onsets = np.concatenate([
            status_annotations.onset,
            stimulus_annotations.onset,
        ]) if len(stimulus_annotations.onset) > 0 else status_annotations.onset
        
        all_durations = np.concatenate([
            status_annotations.duration,
            stimulus_annotations.duration,
        ]) if len(stimulus_annotations.duration) > 0 else status_annotations.duration
        
        all_descriptions = np.concatenate([
            status_annotations.description,
            stimulus_annotations.description,
        ]) if len(stimulus_annotations.description) > 0 else status_annotations.description
        
        merged_annotations = mne.Annotations(
            onset=all_onsets,
            duration=all_durations,
            description=all_descriptions,
            orig_time=raw.info.get("meas_date"),
        )
        
        if len(merged_annotations) > 0:
            raw.set_annotations(merged_annotations)
        
        # Rename channels to standard names if needed
        # Check if channels need renaming (non-standard names)
        ch_names = raw.ch_names
        eeg_channels = [ch for ch in ch_names if ch not in ("EOG", "ECG", "EMG", "M1", "M2", "CB1", "CB2", "STATUS")]
        
        # Identify if channels use non-standard naming (e.g., "EEG001", "EEG002")
        needs_rename = False
        for ch in eeg_channels[:5]:  # Check first 5 EEG channels
            if re.match(r'^EEG\d+$', ch) or re.match(r'^\d+$', ch):
                needs_rename = True
                break
        
        if needs_rename and len(eeg_channels) == len(_STANDARD_10_20_CHANNELS):
            rename_map = {
                old: new 
                for old, new in zip(eeg_channels, _STANDARD_10_20_CHANNELS)
                if old != new
            }
            if rename_map:
                raw.rename_channels(rename_map)
        elif len(eeg_channels) == len(_STANDARD_10_20_CHANNELS):
            # Direct mapping for 64 channels even with standard-ish names
            rename_map = {
                old: new 
                for old, new in zip(eeg_channels, _STANDARD_10_20_CHANNELS)
                if old != new
            }
            if rename_map:
                raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage for electrode positions
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if channel names don't match
        
        return raw


KERNEL = OpenNeuroDS003570Kernel()