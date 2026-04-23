"""OpenNeuro ds004446 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 2 - High-density EEG motor imagery BCI dataset.
3-class motor imagery: left hand, right hand, feet.
130-channel high-density EEG at 1000 Hz.

Source: https://openneuro.org/datasets/ds004446
Paper: https://doi.org/10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Paper DOI 10.1038/s41597-023-02260-6
# High-density EEG setup with 128 EEG channels + 2 EOG channels
# Standard 10-20 electrode naming convention with extended coverage
# Annotator: LLM, 2026-04-08
_AMPLIFIER = "BrainAmp"  # LLM 推断，需人类复核
_CAP_MATERIAL = "Ag/AgCl"  # LLM 推断，需人类复核

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "gender", "handedness"]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = ["trial_index"]

# Required native misc channels (none specified)
_REQUIRED_NATIVE_MISC = []

# Event mapping for motor imagery classes (raw meta)
_EVENT_MAP = {
    "1": "left_hand_MI",
    "2": "right_hand_MI",
    "3": "feet_MI",
    "4": "fixation",
    "5": "rest",
}


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"/sub-([^/]+)/", file_path)
    if match:
        return f"sub-{match.group(1)}"
    # Try alternative pattern
    match = re.search(r"sub-([^/_]+)", file_path)
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
        # Normalize subject_id format
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"
        
        # Find row for this subject
        subj_row = df[df["participant_id"] == subject_id]
        if subj_row.empty:
            # Try without sub- prefix
            subj_row = df[df["participant_id"] == subject_id.replace("sub-", "")]
        if subj_row.empty:
            return {}
        
        result = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in subj_row.columns:
                val = subj_row[field].values[0]
                # Handle NaN/None
                if pd.isna(val):
                    result[field] = "unknown"
                else:
                    result[field] = str(val).strip()
            else:
                result[field] = "unknown"
        return result
    except Exception:
        return {}


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex value to lowercase standard."""
    if not sex_val or sex_val.lower() in ("unknown", "nan", "n/a", ""):
        return "unknown"
    sex_lower = sex_val.lower()
    if sex_lower in ("f", "female", "w", "woman"):
        return "female"
    elif sex_lower in ("m", "male", "man"):
        return "male"
    return "unknown"


def _build_channel_rename_map_130ch(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 130-channel high-density EEG.

    Standard 10-20 extended system with 128 EEG + 2 EOG channels.
    Mapping from potential BIDS-standard names to standard 10-20 names.

    Source: Paper DOI 10.1038/s41597-023-02260-6
    Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
    """
    existing_names = list(raw.ch_names)
    rename_map: Dict[str, str] = {}

    # For BIDS datasets, channels often already have standard names or
    # are named with EEG prefix. We handle common cases here.
    
    # Pattern 1: Direct standard 10-20 names (already correct)
    standard_channels = {
        "Fp1", "Fpz", "Fp2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
        "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8",
        "T7", "T5", "T3", "T1", "T2", "T4", "T6", "T8",
        "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "Iz",
        # Extended high-density channels
        "F9", "F10", "P9", "P10", "T9", "T10",
        "PO9", "PO10", "O9", "O10",
        "AF9", "AF10", "FP9", "FP10",
        # EOG channels
        "EOG1", "EOG2", "HEOG", "VEOG", "EOG_left", "EOG_right",
        "EOG1", "EOG2", "E1", "E2",
    }
    
    # Pattern 2: Common non-standard naming patterns to fix
    alias_patterns = [
        # EEG-001 style -> standard name by position
        (r"^EEG[-_]?0*(\d+)$", None),  # Will be handled by position mapping
        # EOG variants
        (r"^(?:EEG[-_])?(EOG[12]|HEOG|VEOG|E[12])$", lambda m: m.group(1).replace("E1", "EOG1").replace("E2", "EOG2")),
        # Status/Trigger channels that should be misc
        (r"^Status$", None),  # Keep as is, will be set to misc
        (r"^TRIG(ger)?$", None),
    ]
    
    # For numbered channels, try to map by position if we have 130 channels
    # This is a fallback for datasets with numbered channels
    if len(existing_names) == 130:
        # Typical 130ch layout: 128 EEG + 2 EOG
        # We try to use standard extended 10-20 positions
        extended_128 = [
            "Fp1", "Fpz", "Fp2",
            "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
            "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
            "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
            "T9", "T7", "T5", "T3", "T1", "T2", "T4", "T6", "T8", "T10",
            "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
            "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
            "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
            "O1", "Oz", "O2", "I1", "Iz", "I2",
            # Additional channels for 128 setup
            "FFC1", "FFC2", "FFC3", "FFC4", "FFC5", "FFC6",
            "FCC1", "FCC2", "FCC3", "FCC4", "FCC5", "FCC6",
            "CCP1", "CCP2", "CCP3", "CCP4", "CCP5", "CCP6",
            "CPP1", "CPP2", "CPP3", "CPP4", "CPP5", "CPP6",
            "PPO1", "PPO2", "PPO3", "PPO4", "PPO5", "PPO6",
            "OO1", "OO2",
            # EOG at the end
            "EOG1", "EOG2",
        ]
        
        # Only use position mapping if we have a reasonable match
        if len(extended_128) >= len(existing_names):
            for i, old_name in enumerate(existing_names):
                if old_name.startswith("EEG") or old_name.isdigit() or re.match(r"^0*\d+$", old_name):
                    if i < len(extended_128):
                        new_name = extended_128[i]
                        if old_name != new_name:
                            rename_map[old_name] = new_name
    
    # Apply explicit alias patterns
    for old_name in existing_names:
        if old_name in rename_map:
            continue
        for pattern, replacer in alias_patterns:
            match = re.match(pattern, old_name, re.IGNORECASE)
            if match:
                if replacer is not None:
                    new_name = replacer(match)
                    if new_name and new_name != old_name:
                        rename_map[old_name] = new_name
                break
    
    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS convention: same directory, same base name with _events.tsv suffix
    base = file_path.replace(".edf", "").replace(".set", "").replace(".eeg", "").replace(".fif", "").replace(".vhdr", "").replace(".bdf", "")
    events_tsv = base + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try alternative: events.tsv in the same directory
    dir_path = os.path.dirname(file_path)
    alt_events = os.path.join(dir_path, "events.tsv")
    if os.path.exists(alt_events):
        return alt_events
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert events DataFrame to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required BIDS columns
    if "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = events_df["onset"].values.astype(float)
    
    if "duration" in events_df.columns:
        durations = events_df["duration"].values.astype(float)
    else:
        durations = np.zeros_like(onsets)
    
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "event_type" in events_df.columns:
        descriptions = events_df["event_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    else:
        descriptions = np.array(["unknown"] * len(onsets))
    
    # Filter to valid time range
    max_time = raw.times[-1] if len(raw.times) > 0 else float('inf')
    valid_mask = onsets < max_time
    
    return mne.Annotations(
        onset=onsets[valid_mask],
        duration=durations[valid_mask],
        description=descriptions[valid_mask],
    )


def _add_trial_index_misc(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Add trial_index as a misc channel derived from events."""
    n_times = len(raw.times)
    trial_index_data = np.zeros((1, n_times))
    
    if events_df is not None and not events_df.empty and "onset" in events_df.columns:
        onsets = events_df["onset"].values.astype(float)
        # Create step function: increment trial index at each event onset
        for i, onset in enumerate(onsets):
            if onset >= 0 and onset < raw.times[-1]:
                sample_idx = int(onset * raw.info["sfreq"])
                if sample_idx < n_times:
                    trial_index_data[0, sample_idx:] = float(i + 1)
    
    # Add as misc channel
    info_misc = mne.create_info(
        ch_names=["trial_index"],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    raw_misc = mne.io.RawArray(trial_index_data, info_misc)
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


class OpenNeuroDS004446Kernel:
    """Stage-1 kernel for OpenNeuro ds004446 (BMI-HDEEG dataset 2)."""
    
    KERNEL_ID = "openneuro_ds004446"
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["file_path"]
        dataset_path = udataset.root if hasattr(udataset, "root") else os.path.dirname(file_path)
        
        # Get subject info from participants.tsv
        subject_id = _get_subject_id_from_path(file_path)
        participants_info = _read_participants_info(dataset_path, subject_id) if subject_id else {}
        
        # Build and apply channel rename map
        rename_map = _build_channel_rename_map_130ch(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types: EEG for most, EOG for EOG channels, misc for others
        eog_names = {"EOG1", "EOG2", "HEOG", "VEOG", "EOG_left", "EOG_right", "E1", "E2"}
        ch_types = {}
        for ch_name in raw.ch_names:
            base_name = ch_name.upper()
            if any(eog in base_name for eog in ["EOG", "HEOG", "VEOG", "E1", "E2"]):
                ch_types[ch_name] = "eog"
            elif ch_name.upper() in {"STATUS", "TRIG", "TRIGGER", "STI", "STIM"}:
                ch_types[ch_name] = "misc"
            else:
                ch_types[ch_name] = "eeg"
        
        # Only set types for channels that exist
        existing_ch_types = {k: v for k, v in ch_types.items() if k in raw.ch_names}
        if existing_ch_types:
            raw.set_channel_types(existing_ch_types)
        
        # Read events and add annotations
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path) if events_path else None
        
        if events_df is not None and not events_df.empty:
            annotations = _events_to_annotations(events_df, raw)
            if len(annotations) > 0:
                raw.set_annotations(annotations)
        
        # Add derived misc channels
        raw = _add_trial_index_misc(raw, events_df)
        
        # Build description
        age = participants_info.get("age", "unknown")
        sex_raw = participants_info.get("gender", "unknown")
        sex = _normalize_sex(sex_raw)
        handedness = participants_info.get("handedness", "unknown")
        
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": {
                "age": str(age),
                "sex": sex,
                "amplifier": _AMPLIFIER,
                "cap": _CAP_MATERIAL,
                "handedness": str(handedness),
            },
        })
        
        return raw


KERNEL = OpenNeuroDS004446Kernel()