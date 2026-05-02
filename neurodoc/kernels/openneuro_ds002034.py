"""OpenNeuro ds002034 stage1 kernel for EEGUnity.

Real-time EEG feedback on alpha power lateralization leads to behavioral
improvements in a covert attention task.

Source: https://openneuro.org/datasets/ds002034
DOI: 10.1007/s10548-019-00725-9

Paradigm: Covert visuospatial attention with real-time alpha-band
neurofeedback. Participants trained to lateralize alpha power (8-13 Hz)
using left/right half-circle cues. 14 subjects, 64 channels at 512 Hz.

This is a BIDS-compliant dataset. The generic BIDS kernel is extended
here to handle:
1. Standard 64-channel renaming to match standard_1020 montage
2. Event remapping from BIDS numeric codes to canonical event IDs
3. Derived misc channels: event_value_misc from events.tsv
4. Required info fields from participants.tsv: age, sex
5. Annotations from events.tsv for formats without native triggers
"""

from __future__ import annotations

import json
import math
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Static metadata
# =============================================================================
# Device info from paper methods: Brain Products system with 64-channel cap
# Source: 10.1007/s10548-019-00725-9 Methods section — inferred by LLM, needs human review
_DEVICE_INFO: Dict[str, str] = {
    "amplifier": "BrainAmp",
    "cap": "Ag/AgCl",
}

# Standard 64-channel 10-20 layout rename map
# Source: Standard extended 10-20 system for 64-channel caps
# Annotator: LLM, 2026-04-08 — inferred by LLM, needs human review
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Frontal
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fpz": "Fpz",
    "AF7": "AF7",
    "AF3": "AF3",
    "AFz": "AFz",
    "AF4": "AF4",
    "AF8": "AF8",
    "F7": "F7",
    "F5": "F5",
    "F3": "F3",
    "F1": "F1",
    "Fz": "Fz",
    "F2": "F2",
    "F4": "F4",
    "F6": "F6",
    "F8": "F8",
    # Frontocentral
    "FT9": "FT9",
    "FT7": "FT7",
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FCz": "FCz",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "FT8": "FT8",
    "FT10": "FT10",
    # Central
    "T7": "T7",
    "C5": "C5",
    "C3": "C3",
    "C1": "C1",
    "Cz": "Cz",
    "C2": "C2",
    "C4": "C4",
    "C6": "C6",
    "T8": "T8",
    # Centoparietal
    "TP7": "TP7",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CPz": "CPz",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    "TP8": "TP8",
    # Parietal
    "P7": "P7",
    "P5": "P5",
    "P3": "P3",
    "P1": "P1",
    "Pz": "Pz",
    "P2": "P2",
    "P4": "P4",
    "P6": "P6",
    "P8": "P8",
    # Occipital
    "PO7": "PO7",
    "PO5": "PO5",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO6": "PO6",
    "PO8": "PO8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    # Mastoids / reference
    "Iz": "Iz",
    "M1": "M1",
    "M2": "M2",
}

# BIDS event value to canonical event ID mapping
# Source: analysis.md Event Structure table
# Annotator: LLM, 2026-04-08 — inferred by LLM, needs human review
_EVENT_VALUE_TO_ID: Dict[int, str] = {
    1: "event_1",    # Cue: left
    2: "event_2",    # Cue: right
    4: "event_4",    # Run start
    5: "event_5",    # Run end
    6: "event_6",    # Trial start
    8: "event_8",    # Trial start
    9: "event_9",    # Trial start (fixation onset)
    11: "event_11",  # Target: left
    12: "event_12",  # Target: right
    13: "event_13",  # Target: center
    15: "event_15",  # Button press: correct
}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    # BIDS naming: sub-XX[_ses-YY]_task-ZZ[_run-WW]_eeg.<ext>
    # events: sub-XX[_ses-YY]_task-ZZ[_run-WW]_events.tsv
    base = re.sub(r'_eeg\.[^.]+$', '', file_path)
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run level
    base_no_run = re.sub(r'_run-\d+', '', base)
    if base_no_run != base:
        events_path = base_no_run + "_events.tsv"
        if os.path.exists(events_path):
            return events_path
    
    # Search in same directory
    eeg_dir = os.path.dirname(file_path)
    base_name = os.path.basename(base)
    for fname in os.listdir(eeg_dir):
        if fname.endswith("_events.tsv") and base_name in fname:
            return os.path.join(eeg_dir, fname)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _get_subject_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Normalize subject_id format
        if not subject_id.startswith("sub-"):
            subject_id = "sub-" + subject_id
        
        row = df[df["participant_id"] == subject_id]
        if row.empty:
            # Try without sub- prefix
            row = df[df["participant_id"] == subject_id.replace("sub-", "")]
        
        if row.empty:
            return {}
        
        result = {}
        for col in ["age", "sex", "handedness"]:
            if col in row.columns:
                val = row[col].values[0]
                if pd.isna(val):
                    result[col] = "unknown"
                else:
                    result[col] = str(val).strip()
            else:
                result[col] = "unknown"
        
        # Normalize sex to lowercase
        if "sex" in result:
            result["sex"] = result["sex"].lower()
            if result["sex"] not in ["male", "female"]:
                result["sex"] = "unknown"
        
        return result
    
    except Exception:
        return {}


def _create_event_value_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.RawArray:
    """Create a misc channel from events.tsv event_value column as step function."""
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    
    # Initialize with zeros
    data = np.zeros((1, n_samples))
    
    # Sort by onset
    events_df = events_df.sort_values("onset").reset_index(drop=True)
    
    for _, ev in events_df.iterrows():
        onset_sample = int(round(ev["onset"] * sfreq))
        # Use duration if available, otherwise extend to next event or end
        if "duration" in ev and pd.notna(ev["duration"]) and ev["duration"] > 0:
            duration_samples = int(round(ev["duration"] * sfreq))
        else:
            # Default: 1 second or until next event
            duration_samples = int(sfreq)
        
        end_sample = min(onset_sample + duration_samples, n_samples)
        
        if onset_sample < n_samples and "value" in ev and pd.notna(ev["value"]):
            try:
                val = float(ev["value"])
                data[0, onset_sample:end_sample] = val
            except (ValueError, TypeError):
                pass
    
    # Create info for misc channel
    info = mne.create_info(
        ch_names=["event_value_misc"],
        sfreq=sfreq,
        ch_types=["misc"],
        verbose=False
    )
    
    misc_raw = mne.io.RawArray(data, info, verbose=False)
    return misc_raw


def _annotations_from_events_tsv(events_df: pd.DataFrame) -> mne.Annotations:
    """Create MNE Annotations from BIDS events.tsv dataframe."""
    onsets = []
    durations = []
    descriptions = []
    
    for _, ev in events_df.iterrows():
        onset = float(ev["onset"])
        duration = float(ev.get("duration", 0)) if pd.notna(ev.get("duration", 0)) else 0
        
        # Build description from value or trial_type
        desc = None
        if "value" in ev and pd.notna(ev["value"]):
            try:
                val = int(ev["value"])
                desc = _EVENT_VALUE_TO_ID.get(val, f"event_{val}")
            except (ValueError, TypeError):
                pass
        
        if desc is None and "trial_type" in ev and pd.notna(ev["trial_type"]):
            desc = str(ev["trial_type"])
        
        if desc is None:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions
    )


def _needs_events_from_tsv(file_path: str, raw: mne.io.BaseRaw) -> bool:
    """Check if raw file format likely needs events from sidecar."""
    ext = os.path.splitext(file_path)[1].lower()
    
    # EEGLAB .set without events
    if ext == ".set":
        return len(raw.annotations) == 0
    
    # EDF without annotations
    if ext in [".edf", ".bdf"]:
        return len(raw.annotations) == 0
    
    # BrainVision without proper marker file
    if ext == ".eeg":
        return len(raw.annotations) == 0
    
    # Plain .fif without events
    if ext == ".fif":
        return len(raw.annotations) == 0
    
    return False


@dataclass
class OpenNeuroDS002034Kernel:
    """Stage1 kernel for OpenNeuro ds002034 dataset."""

    KERNEL_ID: str = "openneuro-ds002034-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # Extract subject ID from file path
        subject_match = re.search(r'sub-(\d+)', file_path)
        subject_id = f"sub-{subject_match.group(1)}" if subject_match else "unknown"
        
        # =================================================================
        # 1. Read participants.tsv for required info fields
        # =================================================================
        participants_path = _find_participants_tsv(file_path)
        subject_info = {}
        if participants_path:
            subject_info = _get_subject_info(participants_path, subject_id)
        
        # Ensure all required fields exist
        age = str(subject_info.get("age", "unknown"))
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")
        
        # Validate age is string
        if age == "unknown" or age == "nan":
            age = "unknown"
        
        # Validate sex
        sex = sex.lower() if sex else "unknown"
        if sex not in ["male", "female"]:
            sex = "unknown"
        
        # =================================================================
        # 2. Update description with eegunity_description
        # =================================================================
        original_desc = raw.info.get("description", "") or ""
        
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
            "cap": _DEVICE_INFO.get("cap", "unknown"),
            "handedness": handedness,
        }
        
        # Add required info fields from participants.tsv as specified
        # These are already included above (age, sex)
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =================================================================
        # 3. Channel renaming to standard 10-20
        # =================================================================
        # Build rename map for channels that need renaming
        rename_map = {}
        for ch_name in raw.ch_names:
            # Check if channel matches any key in rename map directly
            if ch_name in _CHANNEL_RENAME_MAP and ch_name != _CHANNEL_RENAME_MAP[ch_name]:
                rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
            # Check for common BIDS patterns: EEG-001, EEG 001, etc.
            elif re.match(r'^EEG[-\s]?\d+$', ch_name):
                # Try to extract number and map to standard name
                num_match = re.search(r'(\d+)', ch_name)
                if num_match:
                    # For numbered channels, we'd need the actual cap layout
                    # This dataset should already have named channels
                    pass
        
        # Apply rename if any found
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set standard montage for 64-channel cap
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in both raw and montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common_chs = list(raw_chs & montage_chs)
            if len(common_chs) >= 32:  # Reasonable threshold for valid montage
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without
        
        # =================================================================
        # 4. Handle events from events.tsv if needed
        # =================================================================
        events_path = _find_events_tsv(file_path)
        
        if events_path and os.path.exists(events_path):
            events_df = pd.read_csv(events_path, sep="\t")
            
            # Check if raw needs annotations from events.tsv
            if _needs_events_from_tsv(file_path, raw):
                # Create annotations from events.tsv
                annotations = _annotations_from_events_tsv(events_df)
                raw.set_annotations(annotations)
            elif len(raw.annotations) == 0:
                # Even if format might have events, we have none - use tsv
                annotations = _annotations_from_events_tsv(events_df)
                raw.set_annotations(annotations)
            
            # =================================================================
            # 5. Create derived misc channel: event_value_misc
            # =================================================================
            if "value" in events_df.columns or "event_value" in events_df.columns:
                # Standardize column name
                if "event_value" in events_df.columns and "value" not in events_df.columns:
                    events_df = events_df.rename(columns={"event_value": "value"})
                
                try:
                    misc_raw = _create_event_value_misc_channel(raw, events_df)
                    raw = raw.add_channels([misc_raw], force_update_info=True)
                    
                    # Ensure channel type is misc
                    if "event_value_misc" in raw.ch_names:
                        raw.set_channel_types({"event_value_misc": "misc"})
                except Exception:
                    pass  # Failed to add misc channel
        
        # =================================================================
        # 6. Ensure any required native misc channels are properly typed
        # =================================================================
        # Check for common misc channels in this dataset
        misc_channels = []
        for ch in raw.ch_names:
            if any(x in ch.upper() for x in ["STIM", "TRIGGER", "STATUS", "MISC"]):
                misc_channels.append(ch)
        
        if misc_channels:
            type_map = {ch: "misc" for ch in misc_channels}
            try:
                raw.set_channel_types(type_map)
            except Exception:
                pass
        
        return raw


KERNEL = OpenNeuroDS002034Kernel()