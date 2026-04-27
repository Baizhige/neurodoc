"""openneuro_ds004980 stage1 kernel for EEGUnity.

Architectural Affordances Task - Virtual navigation EEG study.
64-channel EEG recorded at 500 Hz from 17 subjects navigating a virtual 
architectural environment.

Source: https://openneuro.org/datasets/ds004980
DOI: https://doi.org/10.18112/openneuro.ds004980.v1.0.0
Reference: https://doi.org/10.1111/ejn.16461 (Human brain dynamics dissociate 
early perceptual and late motor-related stages of affordance processing)
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


# =============================================================================
# Device metadata
# Source: OpenNeuro dataset_description.json and paper DOI:10.1111/ejn.16461
# The paper mentions "Brain Products" equipment; specific amplifier model not 
# explicitly stated in available documentation.
# Annotator: LLM, 2026-04-08 - 需人类复核
# =============================================================================
_DEVICE_INFO = {
    "amplifier": "Brain Products",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl",               # LLM 推断，需人类复核 - standard for Brain Products
}

# =============================================================================
# Channel Mapping for Brain Products standard 64-channel cap
# Source: Brain Products standard 10-10 system 64-channel layout
# This matches typical ActiCap 64-channel configuration used with Brain Products
# Annotator: LLM, 2026-04-08 - 需人类复核 against actual channel names in data
# =============================================================================
_BRAIN_PRODUCTS_64_MAP: Dict[str, str] = {
    # Common Brain Products numbering to 10-10 names
    "1": "Fp1",
    "2": "Fpz",
    "3": "Fp2",
    "4": "AF7",
    "5": "AF3",
    "6": "AFz",
    "7": "AF4",
    "8": "AF8",
    "9": "F7",
    "10": "F5",
    "11": "F3",
    "12": "F1",
    "13": "Fz",
    "14": "F2",
    "15": "F4",
    "16": "F6",
    "17": "F8",
    "18": "FT7",
    "19": "FC5",
    "20": "FC3",
    "21": "FC1",
    "22": "FCz",
    "23": "FC2",
    "24": "FC4",
    "25": "FC6",
    "26": "FT8",
    "27": "T7",
    "28": "C5",
    "29": "C3",
    "30": "C1",
    "31": "Cz",
    "32": "C2",
    "33": "C4",
    "34": "C6",
    "35": "T8",
    "36": "TP7",
    "37": "CP5",
    "38": "CP3",
    "39": "CP1",
    "40": "CPz",
    "41": "CP2",
    "42": "CP4",
    "43": "CP6",
    "44": "TP8",
    "45": "P7",
    "46": "P5",
    "47": "P3",
    "48": "P1",
    "49": "Pz",
    "50": "P2",
    "51": "P4",
    "52": "P6",
    "53": "P8",
    "54": "PO7",
    "55": "PO5",
    "56": "PO3",
    "57": "POz",
    "58": "PO4",
    "59": "PO6",
    "60": "PO8",
    "61": "O1",
    "62": "Oz",
    "63": "O2",
    "64": "Iz",
}

# Alternative naming: EEG 1..64 or EEG1..EEG64
_EEG_NUMBERED_PATTERNS = [
    re.compile(r"^EEG\s*(\d+)$"),      # "EEG 1", "EEG 32"
    re.compile(r"^EEG(\d+)$"),          # "EEG1", "EEG32"
    re.compile(r"^(\d+)$"),             # "1", "32"
    re.compile(r"^Ch(\d+)$"),           # "Ch1", "Ch32"
    re.compile(r"^Channel\s*(\d+)$"),   # "Channel 1", "Channel 32"
]


def _extract_numbered_channel_name(ch_name: str) -> Optional[str]:
    """Extract numeric channel index and map to standard name."""
    for pattern in _EEG_NUMBERED_PATTERNS:
        match = pattern.match(ch_name.strip())
        if match:
            num_str = match.group(1)
            return _BRAIN_PRODUCTS_64_MAP.get(num_str)
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for Brain Products numbered channels to 10-10 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for ch_name in existing_names:
        # Skip known non-EEG channels
        if ch_name.upper() in ("AUX1", "AUX2", "AUX3", "AUX4", "AUX5", "AUX6",
                               "AUX7", "AUX8", "AUX9", "AUX10",
                               "STI 014", "STI014", "STATUS", "TRIGGER",
                               "EOG1", "EOG2", "EOGH", "EOGV",
                               "EMG1", "EMG2", "ECG"):
            continue
            
        # Try numbered mapping
        mapped = _extract_numbered_channel_name(ch_name)
        if mapped and mapped not in rename_map.values():
            rename_map[ch_name] = mapped
            
    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    # Match sub-XX pattern
    match = re.search(r"sub-(\d+)", os.path.basename(file_path))
    if match:
        return f"sub-{match.group(1)}"
    # Also try just the number
    match = re.search(r"sub-(\d+)", file_path)
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
        # Find row for this subject
        sub_col = "participant_id"
        if sub_col not in df.columns:
            # Try alternative column names
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    sub_col = col
                    break
        
        row = df[df[sub_col] == subject_id]
        if row.empty:
            # Try with "sub-" prefix variations
            if not subject_id.startswith("sub-"):
                row = df[df[sub_col] == f"sub-{subject_id}"]
            else:
                # Try without prefix
                row = df[df[sub_col] == subject_id.replace("sub-", "")]
        
        if row.empty:
            return {}
            
        info = {}
        row_data = row.iloc[0]
        
        # Required fields from kernel requirements: age, sex
        if "age" in row_data:
            info["age"] = str(row_data["age"])
        if "sex" in row_data:
            sex_val = str(row_data["sex"]).lower().strip()
            if sex_val in ("f", "female", "w", "woman"):
                info["sex"] = "female"
            elif sex_val in ("m", "male", "man"):
                info["sex"] = "male"
            else:
                info["sex"] = "unknown"
        if "gender" in row_data and "sex" not in info:
            gender_val = str(row_data["gender"]).lower().strip()
            if gender_val in ("f", "female", "w", "woman"):
                info["sex"] = "female"
            elif gender_val in ("m", "male", "man"):
                info["sex"] = "male"
            else:
                info["sex"] = "unknown"
        if "handedness" in row_data:
            hand_val = str(row_data["handedness"]).lower().strip()
            if hand_val in ("r", "right"):
                info["handedness"] = "right"
            elif hand_val in ("l", "left"):
                info["handedness"] = "left"
            else:
                info["handedness"] = "unknown"
                
        return info
    except Exception:
        return {}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "").replace("_eeg.fif", "")
    # Try various BIDS naming patterns
    candidates = [
        f"{base}_events.tsv",
        file_path.replace("_eeg.edf", "_events.tsv").replace("_eeg.set", "_events.tsv").replace("_eeg.vhdr", "_events.tsv").replace("_eeg.eeg", "_events.tsv").replace("_eeg.fif", "_events.tsv"),
    ]
    # Also check parent directory
    dir_path = os.path.dirname(file_path)
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                candidates.append(os.path.join(dir_path, f))
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _read_events_tsv(events_path: str) -> Optional[np.ndarray]:
    """Read events from BIDS events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        # BIDS events.tsv has onset, duration, trial_type columns
        if "onset" not in df.columns or "trial_type" not in df.columns:
            return None
        
        # Return as MNE annotations-compatible structure
        onsets = df["onset"].values
        durations = df["duration"].values if "duration" in df.columns else np.zeros(len(onsets))
        descriptions = df["trial_type"].values.astype(str)
        
        return onsets, durations, descriptions
    except Exception:
        return None


class OpenneuroDs004980Kernel:
    """Stage-1 kernel for openneuro ds004980: Architectural Affordances EEG."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path and dataset path
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        dataset_path = udataset.get("dataset_path", os.path.dirname(file_path)) if hasattr(udataset, "get") else os.path.dirname(file_path)
        
        # Extract subject ID
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participant info
        participant_info = {}
        if subject_id:
            participant_info = _read_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description
        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("sex", "unknown"),
            "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
            "cap": _DEVICE_INFO.get("cap", "unknown"),
            "handedness": participant_info.get("handedness", "unknown"),
        }
        
        # Set description as JSON string (MNE requires string, not dict)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-10 montage for renamed channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        # Try to add events from events.tsv
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_data = _read_events_tsv(events_tsv_path)
            if events_data is not None:
                onsets, durations, descriptions = events_data
                # Create annotations from events.tsv
                # Convert onsets from seconds to samples if needed
                # MNE annotations use seconds
                annot = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                )
                raw.set_annotations(annot)
        
        # Add derived misc channels from participants.tsv info
        # These are constant broadcast channels since they come from participants.tsv
        derived_misc_channels = []
        for key in ["age", "sex", "handedness"]:
            if key in participant_info and participant_info[key] != "unknown":
                ch_name = f"participant_{key}"
                if ch_name not in raw.ch_names:
                    derived_misc_channels.append((ch_name, participant_info[key]))
        
        if derived_misc_channels:
            # Create misc channels as constant values
            n_times = len(raw.times)
            for ch_name, value in derived_misc_channels:
                # Convert categorical to numeric for MNE
                if isinstance(value, str):
                    try:
                        numeric_value = float(value)
                    except ValueError:
                        # Hash string to a numeric value
                        numeric_value = float(hash(value) % 10000)
                else:
                    numeric_value = float(value)
                
                data = np.full((1, n_times), numeric_value)
                info = mne.create_info([ch_name], raw.info["sfreq"], ch_types="misc")
                raw_misc = mne.io.RawArray(data, info)
                raw.add_channels([raw_misc], force_update_info=True)
        
        return raw


KERNEL = OpenneuroDs004980Kernel()