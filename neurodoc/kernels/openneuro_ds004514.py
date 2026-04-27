"""OpenNeuro DS004514 stage1 kernel for EEGUnity.

Semantic decoding dataset: simultaneous EEG and fNIRS recordings for 
imagined animals and tools across four modalities (visual imagery, 
silent naming, auditory imagery, drawing imagery).

This dataset is BIDS-compliant. The generic BIDS kernel is extended here
to handle dataset-specific channel mapping and event processing.

Source: https://openneuro.org/datasets/ds004514
Paper: DOI 10.1038/s41597-025-04967-0

32 channels, 500 Hz, 22 subjects (12 with complete EEG+fNIRS per paper)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness"]

# Channel rename map: raw names -> standard 10-20 names
_CHANNEL_RENAME_ALIASES = [
    ("Fp1", ["Fp1", "EEG-Fp1", "fp1", "EEG.Fp1", "Fp1."]),
    ("Fpz", ["Fpz", "EEG-Fpz", "fpz", "EEG.Fpz", "Fpz."]),
    ("Fp2", ["Fp2", "EEG-Fp2", "fp2", "EEG.Fp2", "Fp2."]),
    ("F7", ["F7", "EEG-F7", "f7", "EEG.F7", "F7."]),
    ("F3", ["F3", "EEG-F3", "f3", "EEG.F3", "F3."]),
    ("Fz", ["Fz", "EEG-Fz", "fz", "EEG.Fz", "Fz."]),
    ("F4", ["F4", "EEG-F4", "f4", "EEG.F4", "F4."]),
    ("F8", ["F8", "EEG-F8", "f8", "EEG.F8", "F8."]),
    ("FC5", ["FC5", "EEG-FC5", "fc5", "EEG.FC5", "FC5."]),
    ("FC1", ["FC1", "EEG-FC1", "fc1", "EEG.FC1", "FC1."]),
    ("FCz", ["FCz", "EEG-FCz", "fcz", "EEG.FCz", "FCz."]),
    ("FC2", ["FC2", "EEG-FC2", "fc2", "EEG.FC2", "FC2."]),
    ("FC6", ["FC6", "EEG-FC6", "fc6", "EEG.FC6", "FC6."]),
    ("T7", ["T7", "EEG-T7", "t7", "EEG.T7", "T7."]),
    ("C3", ["C3", "EEG-C3", "c3", "EEG.C3", "C3."]),
    ("Cz", ["Cz", "EEG-Cz", "cz", "EEG.Cz", "Cz."]),
    ("C4", ["C4", "EEG-C4", "c4", "EEG.C4", "C4."]),
    ("T8", ["T8", "EEG-T8", "t8", "EEG.T8", "T8."]),
    ("CP5", ["CP5", "EEG-CP5", "cp5", "EEG.CP5", "CP5."]),
    ("CP1", ["CP1", "EEG-CP1", "cp1", "EEG.CP1", "CP1."]),
    ("CPz", ["CPz", "EEG-CPz", "cpz", "EEG.CPz", "CPz."]),
    ("CP2", ["CP2", "EEG-CP2", "cp2", "EEG.CP2", "CP2."]),
    ("CP6", ["CP6", "EEG-CP6", "cp6", "EEG.CP6", "CP6."]),
    ("P7", ["P7", "EEG-P7", "p7", "EEG.P7", "P7."]),
    ("P3", ["P3", "EEG-P3", "p3", "EEG.P3", "P3."]),
    ("Pz", ["Pz", "EEG-Pz", "pz", "EEG.Pz", "Pz."]),
    ("P4", ["P4", "EEG-P4", "p4", "EEG.P4", "P4."]),
    ("P8", ["P8", "EEG-P8", "p8", "EEG.P8", "P8."]),
    ("POz", ["POz", "EEG-POz", "poz", "EEG.POz", "POz."]),
    ("O1", ["O1", "EEG-O1", "o1", "EEG.O1", "O1."]),
    ("Oz", ["Oz", "EEG-Oz", "oz", "EEG.Oz", "Oz."]),
    ("O2", ["O2", "EEG-O2", "o2", "EEG.O2", "O2."]),
    ("M1", ["M1", "EEG-M1", "m1", "EEG.M1", "M1."]),
    ("M2", ["M2", "EEG-M2", "m2", "EEG.M2", "M2."]),
]

# Derived misc channels: none required for this dataset
_DERIVED_MISC_CHANNELS: List[Tuple[str, str]] = []

# Native misc channels that should be ensured as 'misc' type
_NATIVE_MISC_CHANNELS: List[str] = []


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for target_name, aliases in _CHANNEL_RENAME_ALIASES:
        for source_name in aliases:
            if source_name in existing and source_name != target_name:
                if target_name in existing:
                    continue
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}
    
    subj_col = "participant_id"
    if subj_col not in df.columns:
        for col in df.columns:
            if "participant" in col.lower() or "subject" in col.lower():
                subj_col = col
                break
    
    row = df[df[subj_col] == subject_id]
    if row.empty:
        row = df[df[subj_col] == subject_id.replace("sub-", "")]
    if row.empty:
        return {}
    
    result: Dict[str, str] = {}
    row_dict = row.iloc[0].to_dict()
    
    for field in _REQUIRED_INFO_FIELDS:
        if field in row_dict:
            val = row_dict[field]
            if pd.isna(val):
                result[field] = "unknown"
            else:
                result[field] = str(val).strip()
        else:
            result[field] = "unknown"
    
    return result


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex value to canonical form."""
    sex_lower = sex_val.lower().strip()
    if sex_lower in ("f", "female", "w", "woman"):
        return "female"
    elif sex_lower in ("m", "male", "man"):
        return "male"
    return "unknown"


def _normalize_age(age_val: str) -> str:
    """Normalize age value to string."""
    if not age_val or age_val.lower() in ("unknown", "n/a", "na", ""):
        return "unknown"
    try:
        if "-" in age_val and age_val.replace("-", "").replace(".", "").isdigit():
            return age_val
        age_float = float(age_val)
        if age_float <= 0 or age_float > 120:
            return "unknown"
        return str(int(age_float))
    except ValueError:
        return "unknown"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    for ext in [".edf", ".set", ".vhdr", ".bdf", ".eeg"]:
        if file_path.endswith(ext):
            base = file_path[:-len(ext)]
            events_path = base + "_events.tsv"
            if os.path.exists(events_path):
                return events_path
            break
    
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    for ext in [".edf", ".set", ".vhdr", ".bdf", ".eeg"]:
        if basename.endswith(ext):
            base_name = basename[:-len(ext)]
            break
    else:
        base_name = os.path.splitext(basename)[0]
    
    events_path = os.path.join(dirname, base_name + "_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    if os.path.isdir(dirname):
        for f in os.listdir(dirname):
            if f.endswith("_events.tsv"):
                return os.path.join(dirname, f)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events from BIDS events.tsv file."""
    if not os.path.exists(events_path):
        return None
    try:
        df = pd.read_csv(events_path, sep="\t")
        if df.empty:
            return None
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert BIDS events DataFrame to MNE Annotations using trial_type as description."""
    # Identify columns
    onset_col = "onset" if "onset" in events_df.columns else None
    if onset_col is None:
        for c in events_df.columns:
            if "onset" in c.lower():
                onset_col = c
                break
    if onset_col is None:
        onset_col = events_df.columns[0]
    
    duration_col = "duration" if "duration" in events_df.columns else None
    if duration_col is None:
        for c in events_df.columns:
            if "duration" in c.lower():
                duration_col = c
                break
    
    # Use trial_type as the description column (literal strings, no remapping)
    trial_type_col = "trial_type" if "trial_type" in events_df.columns else None
    if trial_type_col is None:
        for c in events_df.columns:
            if "trial" in c.lower() or "type" in c.lower():
                trial_type_col = c
                break
    if trial_type_col is None:
        trial_type_col = events_df.columns[1] if len(events_df.columns) > 1 else events_df.columns[0]
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        try:
            onset = float(row[onset_col])
        except (ValueError, TypeError):
            continue
        
        if duration_col and not pd.isna(row.get(duration_col, np.nan)):
            try:
                duration = float(row[duration_col])
            except (ValueError, TypeError):
                duration = 0.0
        else:
            duration = 0.0
        
        description = str(row.get(trial_type_col, "unknown"))
        if pd.isna(description):
            description = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(description)
    
    if not onsets:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Filter out annotations beyond data length
    sfreq = raw.info["sfreq"]
    n_times = raw.n_times
    data_duration = n_times / sfreq
    
    valid_onsets = []
    valid_durations = []
    valid_descriptions = []
    
    for o, d, desc in zip(onsets, durations, descriptions):
        if o < data_duration:
            valid_onsets.append(o)
            valid_durations.append(d)
            valid_descriptions.append(desc)
    
    return mne.Annotations(onset=valid_onsets, duration=valid_durations, description=valid_descriptions)


def _add_derived_misc_channels(raw: mne.io.BaseRaw, derived_channels: List[Tuple[str, str]]) -> mne.io.BaseRaw:
    """Add derived misc channels to raw object."""
    if not derived_channels:
        return raw
    
    sfreq = raw.info["sfreq"]
    n_times = raw.n_times
    data = np.zeros((len(derived_channels), n_times))
    
    ch_names = [name for name, _ in derived_channels]
    ch_types = ["misc"] * len(derived_channels)
    
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp, verbose=False)
    
    raw.add_channels([misc_raw], force_update_info=True)
    return raw


class OpenNeuroDS004514Kernel:
    """Stage1 kernel for OpenNeuro ds004514 dataset."""

    def __init__(self):
        self.name = "openneuro_ds004514"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("file_path", "")
        dataset_path = udataset.get("dataset_path", "") if hasattr(udataset, "get") else str(udataset)
        
        # Get subject ID and read participants info
        subject_id = _get_subject_id_from_path(file_path)
        participants_info = {}
        if subject_id and dataset_path:
            participants_info = _read_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {}
        for field in _REQUIRED_INFO_FIELDS:
            val = participants_info.get(field, "unknown")
            if field == "sex":
                val = _normalize_sex(val)
            elif field == "age":
                val = _normalize_age(val)
            eegunity_description[field] = val
        
        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map, allow_duplicates=False)
        
        # Set channel types for known non-EEG channels
        # A1-A32 are EEG channels, EXG1-EXG8 are external (misc)
        ch_type_map = {}
        for ch_name in raw.ch_names:
            if ch_name.startswith("EXG"):
                ch_type_map[ch_name] = "misc"
            elif ch_name.startswith("A") and ch_name[1:].isdigit():
                # A1-A32 are EEG channels, keep as eeg
                pass
            elif ch_name in ["Status", "Trigger", "STI", "STI 014"]:
                ch_type_map[ch_name] = "stim"
        
        if ch_type_map:
            raw.set_channel_types(ch_type_map)
        
        # Handle events: read from events.tsv if no annotations in raw
        if len(raw.annotations) == 0:
            events_path = _find_events_tsv(file_path)
            if events_path:
                events_df = _read_events_tsv(events_path)
                if events_df is not None and not events_df.empty:
                    annotations = _events_to_annotations(events_df, raw)
                    if len(annotations) > 0:
                        raw.set_annotations(annotations)
        
        # Add derived misc channels if any
        if _DERIVED_MISC_CHANNELS:
            raw = _add_derived_misc_channels(raw, _DERIVED_MISC_CHANNELS)
        
        return raw


KERNEL = OpenNeuroDS004514Kernel()