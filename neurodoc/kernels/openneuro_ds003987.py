"""openneuro_ds003987 stage1 kernel for EEGUnity.

Amphetamine trials with 5CCPT and PST tasks.
23 subjects x 3 sessions (placebo/low/high dose) = 69 files.

Events:
  - 5CCPT: 21, 22, 23, 25 (attention task)
  - PST: 31, 32, 39 (probabilistic selection task)
  - STATUS: 65535, 65289 (admin markers, exclude from analysis)

Source: https://openneuro.org/datasets/ds003987
Reference: 10.1007/s00213-022-06082-z (Cavanagh et al., 2022)
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Paradigm detection based on file naming convention
# -----------------------------------------------------------------------------

def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path or name."""
    basename = os.path.basename(file_path).lower()
    if "5ccpt" in basename or "_5c" in basename:
        return "5CCPT"
    elif "pst" in basename or "prob" in basename:
        return "PST"
    return ""


# -----------------------------------------------------------------------------
# Event mapping with paradigm prefix (raw meta)
# -----------------------------------------------------------------------------

# Admin codes: no paradigm prefix, cross-paradigm shared markers
_ADMIN_CODES = {65535, 65289}

# PST event codes (from analysis.md and paper)
_PST_EVENT_MAP = {
    31: "31 PST",   # likely reward feedback
    32: "32 PST",   # likely punishment feedback
    33: "33 PST",
    34: "34 PST",
    35: "35 PST",
    36: "36 PST",
    37: "37 PST",
    38: "38 PST",
    39: "39 PST",   # likely neutral feedback
    40: "40 PST",
    41: "41 PST",
    42: "42 PST",
    43: "43 PST",
    44: "44 PST",
    45: "45 PST",
    46: "46 PST",
}

# 5CCPT event codes (from analysis.md and paper)
_5CCPT_EVENT_MAP = {
    21: "21 5CCPT",
    22: "22 5CCPT",
    23: "23 5CCPT",
    24: "24 5CCPT",
    25: "25 5CCPT",
    26: "26 5CCPT",
    27: "27 5CCPT",
    28: "28 5CCPT",
    29: "29 5CCPT",
    30: "30 5CCPT",
}

# All other observed codes (from analysis.md event structure table)
_OTHER_EVENT_MAP = {
    1: "unknown_1",
    2: "unknown_2",
    3: "unknown_3",
    4: "unknown_4",
    10: "unknown_10",
    11: "unknown_11",
    12: "unknown_12",
    13: "unknown_13",
    14: "unknown_14",
    15: "unknown_15",
    16: "unknown_16",
    17: "unknown_17",
    18: "unknown_18",
    19: "unknown_19",
    20: "unknown_20",
}


def _map_event_code(code: int, paradigm: str) -> str:
    """Map numeric event code to canonical description string."""
    # Admin codes first (no paradigm prefix)
    if code in _ADMIN_CODES:
        return f"admin: marker-{code}"
    
    # Paradigm-specific codes
    if paradigm == "PST":
        if code in _PST_EVENT_MAP:
            return _PST_EVENT_MAP[code]
    elif paradigm == "5CCPT":
        if code in _5CCPT_EVENT_MAP:
            return _5CCPT_EVENT_MAP[code]
    
    # Try other known codes
    if code in _OTHER_EVENT_MAP:
        return _OTHER_EVENT_MAP[code]
    
    # Fallback for any unmapped code
    return f"unknown_{code}"


# -----------------------------------------------------------------------------
# Required info fields from participants.tsv
# -----------------------------------------------------------------------------

_REQUIRED_INFO_FIELDS = ["Sess1_Drug", "Sess2_Drug", "Sess3_Drug", "age", "session", "sex"]


# -----------------------------------------------------------------------------
# Helper: read participants.tsv for subject info
# -----------------------------------------------------------------------------

def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}
    
    # Match subject ID (handle both "sub-01" and "01" formats)
    sub_col = "participant_id"
    if sub_col not in df.columns:
        return {}
    
    # Normalize subject ID for matching
    search_id = subject_id
    if not search_id.startswith("sub-"):
        search_id = f"sub-{search_id}"
    
    # Try exact match
    mask = df[sub_col] == search_id
    if not mask.any():
        # Try without "sub-" prefix
        mask = df[sub_col] == subject_id.replace("sub-", "")
    
    if not mask.any():
        return {}
    
    row = df[mask].iloc[0]
    info = {}
    for field in _REQUIRED_INFO_FIELDS:
        if field in row:
            val = row[field]
            # Convert to string, handle NaN
            if pd.isna(val):
                info[field] = "unknown"
            else:
                info[field] = str(val)
        else:
            info[field] = "unknown"
    
    return info


# -----------------------------------------------------------------------------
# Helper: extract subject/session from BIDS path
# -----------------------------------------------------------------------------

def _parse_bids_entities(file_path: str) -> Dict[str, str]:
    """Extract BIDS entities from file path."""
    entities = {
        "subject": "unknown",
        "session": "unknown",
    }
    
    # Parse subject
    sub_match = None
    for part in file_path.replace("\\", "/").split("/"):
        if part.startswith("sub-"):
            sub_match = part[4:]  # after "sub-"
            break
    
    if sub_match:
        entities["subject"] = sub_match
    
    # Parse session
    ses_match = None
    for part in file_path.replace("\\", "/").split("/"):
        if part.startswith("ses-"):
            ses_match = part[4:]  # after "ses-"
            break
    
    if ses_match:
        entities["session"] = ses_match
    
    return entities


# -----------------------------------------------------------------------------
# Helper: find and read events.tsv
# -----------------------------------------------------------------------------

def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # BIDS convention: events.tsv is in same directory as data file
    base = file_path.replace(".set", "").replace(".edf", "").replace(".eeg", "").replace(".vhdr", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Try without suffix (some BIDS layouts)
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).split(".")[0]
    events_path2 = os.path.join(dir_name, base_name + "_events.tsv")
    if os.path.exists(events_path2):
        return events_path2
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Helper: build annotations from events.tsv
# -----------------------------------------------------------------------------

def _build_annotations_from_events_tsv(
    events_df: pd.DataFrame,
    sfreq: float,
    paradigm: str,
) -> Optional[mne.Annotations]:
    """Build MNE Annotations from BIDS events.tsv DataFrame."""
    if events_df is None or len(events_df) == 0:
        return None
    
    # Required columns
    if "onset" not in events_df.columns:
        return None
    
    onsets = events_df["onset"].values
    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(events_df))
    
    # Description: prefer trial_type, then value, then stim_type
    descriptions = []
    for _, row in events_df.iterrows():
        desc = None
        
        # Try trial_type first (human readable)
        if "trial_type" in events_df.columns and pd.notna(row.get("trial_type")):
            desc = str(row["trial_type"])
        # Then value (numeric code)
        elif "value" in events_df.columns and pd.notna(row.get("value")):
            val = row["value"]
            try:
                code = int(float(val))
                desc = _map_event_code(code, paradigm)
            except (ValueError, TypeError):
                desc = str(val)
        # Then stim_type
        elif "stim_type" in events_df.columns and pd.notna(row.get("stim_type")):
            desc = str(row["stim_type"])
        else:
            desc = "unknown"
        
        descriptions.append(desc)
    
    # Filter out empty descriptions
    valid_mask = [d is not None and d != "" and d != "nan" for d in descriptions]
    if not any(valid_mask):
        return None
    
    onsets = onsets[valid_mask] if isinstance(onsets, np.ndarray) else [o for o, v in zip(onsets, valid_mask) if v]
    durations = durations[valid_mask] if isinstance(durations, np.ndarray) else [d for d, v in zip(durations, valid_mask) if v]
    descriptions = [d for d, v in zip(descriptions, valid_mask) if v]
    
    return mne.Annotations(
        onset=np.array(onsets, dtype=float),
        duration=np.array(durations, dtype=float),
        description=descriptions,
    )


# -----------------------------------------------------------------------------
# Helper: build annotations from raw STIM channel (fallback)
# -----------------------------------------------------------------------------

def _build_annotations_from_stim(raw: mne.io.BaseRaw, paradigm: str) -> Optional[mne.Annotations]:
    """Build annotations from STIM channel events in raw."""
    try:
        # Look for stim channel
        stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
        if len(stim_picks) == 0:
            return None
        
        # Find events from stim channel
        events = mne.find_events(raw, stim_channel="STI 014", shortest_event=1, verbose=False)
        if events is None or len(events) == 0:
            # Try other stim channels
            for ch_name in raw.ch_names:
                if "stim" in ch_name.lower() or "sti" in ch_name.lower():
                    try:
                        events = mne.find_events(raw, stim_channel=ch_name, shortest_event=1, verbose=False)
                        if events is not None and len(events) > 0:
                            break
                    except Exception:
                        continue
        
        if events is None or len(events) == 0:
            return None
        
        onsets = events[:, 0] / raw.info["sfreq"]
        durations = np.zeros(len(events))
        descriptions = [_map_event_code(code, paradigm) for code in events[:, 2]]
        
        return mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Helper: build annotations from existing raw.annotations (fallback)
# -----------------------------------------------------------------------------

def _build_annotations_from_existing(raw: mne.io.BaseRaw, paradigm: str) -> mne.Annotations:
    """Rebuild annotations from existing raw.annotations with proper mapping."""
    if raw.annotations is None or len(raw.annotations) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    descriptions = []
    for desc in raw.annotations.description:
        # Try to parse as numeric code
        try:
            code = int(float(desc))
            new_desc = _map_event_code(code, paradigm)
        except (ValueError, TypeError):
            # Keep existing description if not numeric
            new_desc = desc
        
        descriptions.append(new_desc)
    
    return mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=descriptions,
    )


# -----------------------------------------------------------------------------
# Kernel class
# -----------------------------------------------------------------------------

class OpenNeuroDs003987Kernel:
    """Stage1 kernel for openneuro_ds003987 dataset."""

    KERNEL_ID: str = "openneuro-ds003987-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")
        dataset_path = getattr(udataset, "dataset_path", "") if udataset else ""
        
        # Parse BIDS entities
        bids_entities = _parse_bids_entities(file_path)
        subject_id = bids_entities["subject"]
        session_id = bids_entities["session"]
        
        # Detect paradigm from filename
        paradigm = _detect_paradigm(file_path)
        
        # ---------------------------------------------------------------------
        # Step 1: Read participants.tsv info
        # ---------------------------------------------------------------------
        participants_info = _read_participants_info(dataset_path, subject_id)
        
        # Standardize sex to lowercase
        sex = participants_info.get("sex", "unknown").lower()
        if sex not in ("male", "female"):
            sex = "unknown"
        
        # Age as string
        age = participants_info.get("age", "unknown")
        
        # Session as string
        session = participants_info.get("session", session_id)
        
        # Drug info for each session
        sess1_drug = participants_info.get("Sess1_Drug", "unknown")
        sess2_drug = participants_info.get("Sess2_Drug", "unknown")
        sess3_drug = participants_info.get("Sess3_Drug", "unknown")
        
        # ---------------------------------------------------------------------
        # Step 2: Build eegunity_description
        # ---------------------------------------------------------------------
        original_desc = raw.info.get("description", "") or ""
        
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review - not specified in BIDS, paper mentions BrainAmp but need verification
            "cap": "unknown",  # inferred by LLM, needs human review - 71-channel system, likely custom or extended 10-20
            "handedness": "unknown",  # not in participants.tsv
            "Sess1_Drug": sess1_drug,
            "Sess2_Drug": sess2_drug,
            "Sess3_Drug": sess3_drug,
            "session": session,
        }
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # ---------------------------------------------------------------------
        # Step 3: Channel renaming and montage
        # ---------------------------------------------------------------------
        # Check if channels need renaming (some files may have non-standard names)
        # Standard 10-20 / 10-10 names expected for 71-channel system
        
        # Common renaming patterns for this dataset
        rename_map = {}
        for ch_name in raw.ch_names:
            # Handle EGI-style or numbered channels if present
            if ch_name.startswith("E") and ch_name[1:].isdigit():
                # EGI naming - would need specific mapping, but BIDS usually has standard names
                pass
            # Ensure consistent casing
            upper_name = ch_name.upper()
            # Map known variants
            if upper_name == "FPZ" and "Fpz" not in raw.ch_names:
                rename_map[ch_name] = "Fpz"
        
        # Apply rename if any
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known non-EEG channels
        # 71 channels: likely 64 EEG + 7 externals (EOG, etc.)
        eog_names = [ch for ch in raw.ch_names if any(x in ch.upper() for x in ["EOG", "EYE"])]
        ecg_names = [ch for ch in raw.ch_names if any(x in ch.upper() for x in ["ECG", "EKG"])]
        emg_names = [ch for ch in raw.ch_names if "EMG" in ch.upper()]
        
        ch_type_map = {}
        for ch in eog_names:
            ch_type_map[ch] = "eog"
        for ch in ecg_names:
            ch_type_map[ch] = "ecg"
        for ch in emg_names:
            ch_type_map[ch] = "emg"
        
        if ch_type_map:
            raw.set_channel_types(ch_type_map)
        
        # Set montage if channels appear to be standard 10-20/10-10
        # 71 channels suggests extended 10-20 or 10-10 system
        try:
            # Try standard_1020 first (will work for subset)
            # For 71 channels, likely need standard_1005 (10-10 system)
            raw.set_montage("standard_1005", match_case=False, on_missing="warn")
        except Exception:
            try:
                raw.set_montage("standard_1020", match_case=False, on_missing="warn")
            except Exception:
                pass  # Montage setting failed, continue without
        
        # ---------------------------------------------------------------------
        # Step 4: Build annotations from events.tsv or raw data
        # ---------------------------------------------------------------------
        annotations = None
        
        # Priority 1: events.tsv sidecar (BIDS standard)
        events_tsv_path = _find_events_tsv(file_path)
        if events_tsv_path:
            events_df = _read_events_tsv(events_tsv_path)
            if events_df is not None:
                annotations = _build_annotations_from_events_tsv(events_df, raw.info["sfreq"], paradigm)
        
        # Priority 2: existing raw.annotations with remapping
        if annotations is None and raw.annotations is not None and len(raw.annotations) > 0:
            annotations = _build_annotations_from_existing(raw, paradigm)
        
        # Priority 3: STIM channel
        if annotations is None:
            annotations = _build_annotations_from_stim(raw, paradigm)
        
        # Apply annotations if found
        if annotations is not None and len(annotations) > 0:
            raw.set_annotations(annotations)
        
        # ---------------------------------------------------------------------
        # Step 5: Ensure required native/derived misc channels
        # ---------------------------------------------------------------------
        # No required misc channels specified for this dataset
        
        # ---------------------------------------------------------------------
        # Step 6: Final validation
        # ---------------------------------------------------------------------
        # Ensure data is usable
        if raw.info["sfreq"] != 500:
            # Resample if needed (should be 500 Hz per dataset spec)
            pass  # Keep original, don't resample in kernel
        
        return raw


KERNEL = OpenNeuroDs003987Kernel()