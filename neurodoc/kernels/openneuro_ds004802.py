"""Dataset-specific kernel for openneuro_ds004802.

Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness (Pilot).
Roving oddball EEG paradigm with emotional face stimuli.

Source: https://openneuro.org/datasets/ds004802
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv per kernel_requirements
_REQUIRED_INFO_FIELDS = ["birth_year", "diagnosis", "gender", "loneliness"]

# Standard 10-20 channel names for 73-channel setup
# Source: dataset uses standard extended 10-20 cap with 64 EEG + 9 EOG/other channels
# Annotator: LLM inferred from BIDS structure and channel count, 2026-04-08
# inferred by LLM, needs human review
_STANDARD_EEG_73 = [
    "Fp1", "Fpz", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Iz"
]

# Extended channels beyond standard 64 (EOG, reference, etc.)
# inferred by LLM, needs human review
_EXTENDED_CHANNELS = [
    "VEOG_lower", "VEOG_upper", "HEOG_left", "HEOG_right",
    "M1", "M2", "Cz_REF", "FCz_REF", "STI 014"
]


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find events.tsv file for a given EEG file path."""
    base_dir = os.path.dirname(file_path)
    # BIDS hierarchy: sub-XX/eeg/sub-XX_task-XX_eeg.edf -> events.tsv in same dir
    candidates = [
        os.path.join(base_dir, "events.tsv"),
        # Or with task entity
        os.path.join(base_dir, os.path.basename(file_path).replace("_eeg.edf", "_events.tsv").replace("_eeg.set", "_events.tsv").replace("_eeg.bdf", "_events.tsv")),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv from file path by walking up."""
    current = os.path.dirname(file_path)
    for _ in range(5):  # Search up to 5 levels
        candidate = os.path.join(current, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    basename = os.path.basename(file_path)
    # BIDS pattern: sub-XXXXX_task-...
    if basename.startswith("sub-"):
        parts = basename.split("_")
        if parts:
            sub_id = parts[0]  # sub-XXXXX
            return sub_id
    return None


def _read_participants_info(file_path: str, required_fields: List[str]) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_tsv = _find_participants_tsv(file_path)
    result = {field: "unknown" for field in required_fields}
    
    if participants_tsv is None:
        return result
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        subject_id = _get_subject_id_from_path(file_path)
        
        if subject_id is None or "participant_id" not in df.columns:
            return result
        
        # Match subject (with or without "sub-" prefix)
        match = df[df["participant_id"] == subject_id]
        if match.empty:
            # Try without "sub-" prefix
            clean_id = subject_id.replace("sub-", "")
            match = df[df["participant_id"] == clean_id]
            if match.empty:
                # Try with "sub-" prefix
                match = df[df["participant_id"] == f"sub-{clean_id}"]
        
        if not match.empty:
            row = match.iloc[0]
            for field in required_fields:
                if field in row.index:
                    val = row[field]
                    # Handle NaN/missing
                    if pd.isna(val):
                        result[field] = "unknown"
                    else:
                        result[field] = str(val)
                else:
                    result[field] = "unknown"
    except Exception:
        pass
    
    return result


def _build_eegunity_description(raw: mne.io.BaseRaw, file_path: str) -> str:
    """Build eegunity_description JSON string."""
    original_desc = raw.info.get("description", "") or ""
    
    # Read required fields from participants.tsv
    info_fields = _read_participants_info(file_path, _REQUIRED_INFO_FIELDS)
    
    # Determine sex from gender field
    gender = info_fields.get("gender", "unknown").lower()
    if gender in ["m", "male"]:
        sex = "male"
    elif gender in ["f", "female"]:
        sex = "female"
    else:
        sex = "unknown"
    
    # Age from birth_year if available
    birth_year = info_fields.get("birth_year", "unknown")
    if birth_year != "unknown":
        try:
            # Study conducted ~2023 per dataset metadata
            age = str(2023 - int(float(birth_year)))
        except (ValueError, TypeError):
            age = "unknown"
    else:
        age = "unknown"
    
    eegunity_desc = {
        "age": age,
        "sex": sex,
        "amplifier": "unknown",  # Not documented in dataset
        "cap": "Ag/AgCl",  # Standard for research EEG; inferred by LLM, needs human review
        "handedness": "unknown",  # Not in participants.tsv
    }
    
    # Add required info fields as strings
    for field, value in info_fields.items():
        eegunity_desc[field] = value
    
    description_dict = {
        "original_description": original_desc,
        "eegunity_description": eegunity_desc,
    }
    
    return json.dumps(description_dict)


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names if they use non-standard naming."""
    ch_names = raw.ch_names
    
    # Check if already standard names
    standard_set = set(_STANDARD_EEG_73 + _EXTENDED_CHANNELS)
    if all(ch in standard_set for ch in ch_names if not ch.startswith("EEG")):
        return raw
    
    # Common non-standard patterns in this dataset
    rename_map = {}
    
    # Handle numbered EEG channels (EEG001, EEG002, etc.)
    if any("EEG" in ch and ch[3:].isdigit() for ch in ch_names):
        eeg_count = 0
        for ch in ch_names:
            if "EEG" in ch and ch[3:].isdigit():
                if eeg_count < len(_STANDARD_EEG_73):
                    rename_map[ch] = _STANDARD_EEG_73[eeg_count]
                    eeg_count += 1
    
    # Handle EOG channels
    eog_patterns = {
        "VEOG": ["VEOG", "VEOG_lower", "VEOGl", "VEOG_l", "VEOG-l"],
        "VEOG_upper": ["VEOGu", "VEOG_u", "VEOG-u", "VEOG_upper"],
        "HEOG_left": ["HEOGl", "HEOG_l", "HEOG-l", "HEOG_left", "HEOG"],
        "HEOG_right": ["HEOGr", "HEOG_r", "HEOG-r", "HEOG_right"],
    }
    
    for target, patterns in eog_patterns.items():
        for ch in ch_names:
            if ch in patterns and ch != target:
                rename_map[ch] = target
    
    # Handle reference channels
    ref_patterns = {
        "Cz_REF": ["Cz-REF", "Cz_REF", "CzRef", "REF_Cz"],
        "FCz_REF": ["FCz-REF", "FCz_REF", "FCzRef", "REF_FCz"],
    }
    
    for target, patterns in ref_patterns.items():
        for ch in ch_names:
            if ch in patterns and ch != target:
                rename_map[ch] = target
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set proper channel types for EOG and misc channels."""
    ch_types = {}
    
    for ch in raw.ch_names:
        ch_upper = ch.upper()
        if any(x in ch_upper for x in ["VEOG", "HEOG", "EOG"]):
            ch_types[ch] = "eog"
        elif any(x in ch_upper for x in ["M1", "M2", "A1", "A2", "REF", "STI"]):
            ch_types[ch] = "misc"
    
    if ch_types:
        raw = raw.set_channel_types(ch_types)
    
    return raw


def _add_annotations_from_events_tsv(raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
    """Add annotations from events.tsv if available."""
    events_tsv = _find_events_tsv(file_path)
    
    if events_tsv is None:
        return raw
    
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        
        # Required columns for BIDS events
        if "onset" not in df.columns or "trial_type" not in df.columns:
            return raw
        
        onsets = df["onset"].values
        # Default duration to 0 if not present
        if "duration" in df.columns:
            durations = df["duration"].values
            # Handle NaN durations
            durations = np.where(pd.isna(durations), 0.0, durations)
        else:
            durations = np.zeros(len(onsets))
        
        # Use trial_type as description (literal labels, no remapping per HC-5)
        descriptions = df["trial_type"].astype(str).values
        
        # Create annotations
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        
        raw = raw.set_annotations(annotations)
    except Exception:
        pass
    
    return raw


def _add_misc_channels(raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
    """Add derived misc channels from participants.tsv and events.tsv data."""
    # Ensure data is loaded before adding channels
    if not raw.preload:
        raw.load_data()
    
    # Get participants info for derived misc channels
    participants_tsv = _find_participants_tsv(file_path)
    misc_data = {}
    
    if participants_tsv is not None:
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            subject_id = _get_subject_id_from_path(file_path)
            
            if subject_id is not None and "participant_id" in df.columns:
                match = df[df["participant_id"] == subject_id]
                if match.empty:
                    clean_id = subject_id.replace("sub-", "")
                    match = df[df["participant_id"] == clean_id]
                    if match.empty:
                        match = df[df["participant_id"] == f"sub-{clean_id}"]
                
                if not match.empty:
                    row = match.iloc[0]
                    # Create misc channels for numerical participants columns
                    for col in df.columns:
                        if col == "participant_id":
                            continue
                        val = row.get(col)
                        if pd.notna(val):
                            try:
                                float_val = float(val)
                                misc_data[f"subj_{col}"] = float_val
                            except (ValueError, TypeError):
                                # String columns: encode as constant 0 with name indicating value
                                pass
        except Exception:
            pass
    
    # Also check events.tsv for potential trial-locked derived channels
    events_tsv = _find_events_tsv(file_path)
    events_misc = {}
    
    if events_tsv is not None:
        try:
            df = pd.read_csv(events_tsv, sep="\t")
            # For events, we can create a trial-locked step function
            # But for simplicity with participants.tsv sources, constant broadcast is fine
            # We'll add event count as a misc channel
            events_misc["event_count"] = float(len(df))
        except Exception:
            pass
    
    # Combine all misc channels
    all_misc = {}
    all_misc.update(misc_data)
    all_misc.update(events_misc)
    
    if not all_misc:
        return raw
    
    # Create new raw objects for each misc channel and add them
    for ch_name, value in all_misc.items():
        # Ensure unique channel name
        base_name = ch_name
        counter = 1
        while ch_name in raw.ch_names:
            ch_name = f"{base_name}_{counter}"
            counter += 1
        
        # Create data array: (1, n_times)
        data = np.full((1, len(raw.times)), value, dtype=np.float64)
        
        # Create info for misc channel
        info = mne.create_info(
            ch_names=[ch_name],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"],
        )
        
        # Create RawArray
        new_raw = mne.io.RawArray(data, info, verbose=False)
        
        # Add channel to raw
        raw.add_channels([new_raw], force_update_info=True)
    
    return raw


class OpenneuroDs004802Kernel:
    """Kernel for openneuro_ds004802 dataset."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["file_path"] if "file_path" in row else row.get("path", "")
        
        # Rename channels to standard names
        raw = _rename_channels(raw)
        
        # Set proper channel types
        raw = _set_channel_types(raw)
        
        # Add annotations from events.tsv
        raw = _add_annotations_from_events_tsv(raw, file_path)
        
        # Add derived misc channels (loads data internally if needed)
        raw = _add_misc_channels(raw, file_path)
        
        # Build and set description
        raw.info["description"] = _build_eegunity_description(raw, file_path)
        
        return raw


KERNEL = OpenneuroDs004802Kernel()