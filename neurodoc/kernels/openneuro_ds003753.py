"""OpenNeuro DS003753 stage1 kernel for EEGUnity.

Probabilistic Learning with Affective Feedback: Exp #2
66-channel EEG, 500 Hz sampling rate, 25 subjects.
BIDS format with BrainVision .vhdr/.eeg/.vmrk files.

Source: https://openneuro.org/datasets/ds003753
Paper: https://doi.org/10.3758/s13415-021-00950-5
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Paper DOI 10.3758/s13415-021-00950-5, Methods section
# "EEG was recorded using a 64-channel BrainVision system"
# inferred by LLM, needs human review
_AMPLIFIER = "BrainVision Recorder"

# Source: Paper DOI 10.3758/s13415-021-00950-5, Methods section
# Standard Ag/AgCl electrodes used
# inferred by LLM, needs human review
_CAP = "Ag/AgCl"

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex"]

# Required event IDs that must appear in scan
_REQUIRED_EVENT_IDS = ["S  1", "S  2", "S  3", "S  4", "S 10", "S 20"]

# Raw event ID to description mapping (from analysis.md Event Structure table)
_RAW_EVENT_MAP = {
    "S  1": "CUE: choice required",
    "S  2": "FB: affective feedback subtype 1",
    "S  3": "FB: affective feedback subtype 2",
    "S  4": "FB: affective feedback subtype 3",
    "S 10": "FB: feedback/choice subtype 10",
    "S 20": "FB: feedback/choice subtype 20",
    "S101": "CUE: positive valence subtype",
    "S102": "CUE: negative valence subtype",
    "S103": "CUE: subtype 103",
    "S104": "CUE: subtype 104",
    "S110": "RESP: left button press",
    "S111": "RESP: right button press",
    "S120": "RESP: subtype 120",
    "boundary": "boundary: data segment marker",
}


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from participants.tsv."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    participants_dict: Dict[str, Dict[str, str]] = {}

    if os.path.exists(participants_file):
        df = pd.read_csv(participants_file, sep="\t")
        for _, prow in df.iterrows():
            subj_id = str(prow.get("participant_id", ""))
            if not subj_id:
                continue
            # Normalize subj_id to match file naming (sub-01 -> sub-01)
            participants_dict[subj_id] = {
                "age": str(prow.get("age", "unknown")),
                "sex": str(prow.get("sex", "unknown")).lower(),
                "handedness": str(prow.get("handedness", "unknown")).lower(),
            }

    return participants_dict


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    base_dir = os.path.dirname(file_path)
    
    # For BIDS: file is like sub-XX/eeg/sub-XX_task-YYY_eeg.vhdr
    # events.tsv should be: sub-XX/eeg/sub-XX_task-YYY_events.tsv
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    events_path = os.path.join(base_dir, f"{base_name}_events.tsv")
    
    if os.path.exists(events_path):
        return events_path
    
    # Fallback: try glob patterns
    sub_match = re.match(r"(sub-\d+)", os.path.basename(file_path))
    if sub_match:
        sub_id = sub_match.group(1)
        # Try task-specific events
        task_match = re.search(r"task-([^_]+)", os.path.basename(file_path))
        if task_match:
            task_name = task_match.group(1)
            alt_path = os.path.join(base_dir, f"{sub_id}_task-{task_name}_events.tsv")
            if os.path.exists(alt_path):
                return alt_path
    
    # Try any events.tsv in same directory
    for f in os.listdir(base_dir) if os.path.isdir(base_dir) else []:
        if f.endswith("_events.tsv"):
            return os.path.join(base_dir, f)
    
    return None


def _find_channels_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding channels.tsv file for a given EEG file."""
    base_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    channels_path = os.path.join(base_dir, f"{base_name}_channels.tsv")
    
    if os.path.exists(channels_path):
        return channels_path
    
    # Fallback patterns
    for f in os.listdir(base_dir) if os.path.isdir(base_dir) else []:
        if f.endswith("_channels.tsv"):
            return os.path.join(base_dir, f)
    
    return None


def _standardize_channel_names(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names for 64+2 channel layout.
    
    BrainVision files may have numbered or non-standard names.
    Map to standard 10-20 extended names based on position.
    """
    ch_names = raw.ch_names
    
    # Check if already standard names
    standard_prefixes = ("Fp", "AF", "F", "FC", "C", "CP", "P", "PO", "O", "T")
    if all(any(n.startswith(p) for p in standard_prefixes) for n in ch_names if not n.upper().startswith("E")):
        # Already looks standard
        return raw
    
    # Common BrainVision 64-channel naming patterns
    # If channels are numbered like 1, 2, 3... or Ch1, Ch2...
    rename_map = {}
    
    # Try to match based on known 64+2 layout from paper
    # Paper mentions 64 channels + 2 EOG = 66 channels total
    # Standard BrainVision 64-channel cap with FCz reference
    
    # Check for simple numbered channels
    numbered_pattern = re.compile(r"^(?:Ch|Channel|EEG)?\s*(\d+)$", re.IGNORECASE)
    
    # Extended 10-20 system 64-channel layout (approximate)
    # This is a common BrainVision 64-channel montage
    _BRAINVISION_64_MAP = [
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5",
        "FC1", "FC2", "FC6", "T7", "C3", "Cz", "C4", "T8",
        "CP5", "CP1", "CP2", "CP6", "P7", "P3", "Pz", "P4",
        "P8", "PO9", "O1", "Oz", "O2", "PO10", "AF7", "AF3",
        "AF4", "AF8", "F5", "F1", "F2", "F6", "FT9", "FT7",
        "FC3", "FC4", "FT8", "FT10", "C5", "C1", "C2", "C6",
        "TP7", "CP3", "CPz", "CP4", "TP8", "P5", "P1", "P2",
        "P6", "PO7", "PO3", "POz", "PO4", "PO8", "TP9", "TP10",
    ]
    
    for i, ch_name in enumerate(ch_names):
        match = numbered_pattern.match(ch_name)
        if match:
            idx = int(match.group(1)) - 1  # 1-based to 0-based
            if 0 <= idx < len(_BRAINVISION_64_MAP):
                rename_map[ch_name] = _BRAINVISION_64_MAP[idx]
        # Also handle EEG-1, EEG-2, etc.
        eeg_match = re.match(r"^EEG-?(\d+)$", ch_name, re.IGNORECASE)
        if eeg_match and ch_name not in rename_map:
            idx = int(eeg_match.group(1)) - 1
            if 0 <= idx < len(_BRAINVISION_64_MAP):
                rename_map[ch_name] = _BRAINVISION_64_MAP[idx]
    
    # Handle EOG channels
    for ch_name in ch_names:
        upper = ch_name.upper()
        if any(x in upper for x in ["EOG", "VEOG", "HEOG", "EYE"]):
            if "H" in upper or "HEOG" in upper or "HOR" in upper:
                rename_map[ch_name] = "HEOG"
            elif "V" in upper or "VEOG" in upper or "VER" in upper:
                rename_map[ch_name] = "VEOG"
            else:
                # Default EOG naming
                rename_map[ch_name] = "EOG"
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set proper channel types based on name patterns."""
    ch_types = {}
    
    for ch_name in raw.ch_names:
        upper = ch_name.upper()
        if ch_name in ("HEOG", "VEOG", "EOG", "EYE"):
            ch_types[ch_name] = "eog"
        elif any(ch_name.startswith(p) for p in ["Fp", "AF", "F", "FC", "C", "CP", "P", "PO", "O", "T", "Iz"]):
            ch_types[ch_name] = "eeg"
        elif "ECG" in upper or "EKG" in upper:
            ch_types[ch_name] = "ecg"
        elif "EMG" in upper:
            ch_types[ch_name] = "emg"
        elif "STIM" in upper or "TRIG" in upper or "MARK" in upper:
            ch_types[ch_name] = "stim"
        else:
            # Default to EEG for unknown channels
            ch_types[ch_name] = "eeg"
    
    raw.set_channel_types(ch_types)
    return raw


def _load_events_from_tsv(events_path: str, raw: mne.io.BaseRaw) -> Optional[mne.Annotations]:
    """Load events from BIDS events.tsv file."""
    if not os.path.exists(events_path):
        return None
    
    try:
        df = pd.read_csv(events_path, sep="\t")
        
        # Required columns for events
        if "onset" not in df.columns:
            return None
        
        onsets = df["onset"].values
        durations = df["duration"].values if "duration" in df.columns else np.zeros(len(onsets))
        
        # Get descriptions from trial_type or value column
        if "trial_type" in df.columns:
            descriptions = df["trial_type"].astype(str).values
        elif "value" in df.columns:
            descriptions = df["value"].astype(str).values
        elif "event_type" in df.columns:
            descriptions = df["event_type"].astype(str).values
        else:
            # Use onset as description fallback
            descriptions = np.array([f"event_{i}" for i in range(len(onsets))])
        
        # Filter to valid time range
        max_time = raw.times[-1] if len(raw.times) > 0 else float('inf')
        valid_mask = onsets < max_time
        
        if not np.any(valid_mask):
            return None
        
        onsets = onsets[valid_mask]
        durations = durations[valid_mask]
        descriptions = descriptions[valid_mask]
        
        # Ensure non-negative durations
        durations = np.maximum(durations, 0)
        
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        
        return annotations
        
    except Exception:
        return None


def _read_brainvision_events(raw: mne.io.BaseRaw) -> Optional[mne.Annotations]:
    """Try to read events from BrainVision marker file."""
    try:
        # BrainVision files store events in .vmrk file
        # mne should have already read these into annotations
        if raw.annotations is not None and len(raw.annotations) > 0:
            return raw.annotations
    except Exception:
        pass
    return None


class OpenNeuroDS003753Kernel:
    """Kernel for OpenNeuro ds003753 dataset."""

    KERNEL_ID = "openneuro_ds003753"

    def __init__(self):
        self._participants_cache: Optional[Dict[str, Dict[str, str]]] = None

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        dataset_path = str(getattr(udataset, "dataset_path", "") or getattr(udataset, "path", "") or "")
        file_path = str(row.get("File Path", row.get("file_path", "")))

        # Load participants.tsv if not cached
        if self._participants_cache is None and dataset_path:
            self._participants_cache = _load_participants_tsv(dataset_path)

        # Extract subject ID from file path
        sub_match = re.search(r"(sub-\d+)", file_path)
        sub_id = sub_match.group(1) if sub_match else ""

        # Get participant info
        participant_info = self._participants_cache.get(sub_id, {}) if self._participants_cache else {}

        # Standardize channel names
        raw = _standardize_channel_names(raw)

        # Set channel types
        raw = _set_channel_types(raw)

        # Set montage (standard 10-20)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass

        # Handle events: prefer events.tsv, fallback to BrainVision markers
        events_tsv_path = _find_events_tsv(file_path)
        annotations = None

        if events_tsv_path:
            annotations = _load_events_from_tsv(events_tsv_path, raw)

        if annotations is None:
            annotations = _read_brainvision_events(raw)

        if annotations is not None and len(annotations) > 0:
            raw.set_annotations(annotations)

        # Build eegunity_description with required fields
        original_description = raw.info.get("description", "")

        eegunity_description = {
            "age": participant_info.get("age", "unknown"),
            "sex": participant_info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": participant_info.get("handedness", "unknown"),
        }

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = OpenNeuroDS003753Kernel()