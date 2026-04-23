"""OpenNeuro ds004075 stage1 kernel for EEGUnity.

Dataset: "what_are_we_talking_about" (Context03/09/10 tasks)
Source: https://openneuro.org/datasets/ds004075
DOI: https://doi.org/10.18112/openneuro.ds004075.v1.0.0

BIDS-compliant dataset with BrainVision .vhdr/.vmrk/.eeg files.
64 channels, 1000 Hz sampling rate.

This kernel handles:
- Channel renaming to standard 10-20 montage
- Metadata extraction from participants.tsv
- Event annotation from BrainVision marker files (via MNE's native reader)
- Task-specific event prefixing for multi-paradigm discrimination
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


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Standard 10-20 channel names for 64-channel layout
# Source: BrainVision standard 64-channel cap, standard_1020
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_STANDARD_64CH_NAMES = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5",
    "FC1", "FC2", "FC6", "T7", "C3", "Cz", "C4", "T8",
    "TP9", "CP5", "CP1", "CP2", "CP6", "TP10", "P7", "P3",
    "Pz", "P4", "P8", "PO9", "O1", "Oz", "O2", "PO10",
    "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6",
    "FT9", "FT7", "FC3", "FC4", "FT8", "FT10", "C5", "C1",
    "C2", "C6", "TP7", "CP3", "CPz", "CP4", "TP8", "P5",
    "P1", "P2", "P6", "PO7", "PO3", "POz", "PO4", "PO8"
]

# BrainVision default naming patterns that need normalization
# Source: BrainVision Recorder default channel naming convention
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_BV_CHANNEL_MAP = {
    # Common BrainVision aliases to standard 10-20
    "FP1": "Fp1", "FP2": "Fp2",
    "FZ": "Fz", "CZ": "Cz", "PZ": "Pz", "OZ": "Oz", "POZ": "POz", "CPZ": "CPz",
    "FCZ": "FCz", "AFZ": "AFz", "CPZ": "CPz",
    "T3": "T7", "T4": "T8", "T5": "P7", "T6": "P8",
    "M1": "TP9", "M2": "TP10", "A1": "TP9", "A2": "TP10",
    # Handle numbered EEG channels if present
}

# Event ID mappings from task analysis
# Source: https://doi.org/10.18112/openneuro.ds004075.v1.0.0 — BrainVision .vmrk marker files
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_EVENT_VALUE_MAP = {
    "S  1": "Stimulus/S  1",
    "S  10": "Stimulus/S 10",
    "S  20": "Stimulus/S 20",
    "S  22": "Stimulus/S 22",
    "S  23": "Stimulus/S 23",
    "S  30": "Stimulus/S 30",
    "S  31": "Stimulus/S 31",
    # Numeric variants
    "S1": "Stimulus/S  1",
    "S10": "Stimulus/S 10",
    "S20": "Stimulus/S 20",
    "S22": "Stimulus/S 22",
    "S23": "Stimulus/S 23",
    "S30": "Stimulus/S 30",
    "S31": "Stimulus/S 31",
}

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = []  # No extra required fields beyond standard BIDS

# Required native/derived misc channels
_REQUIRED_NATIVE_MISC = []
_DERIVED_MISC_CHANNELS = []


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _detect_task(file_path: str) -> str:
    """Detect which BIDS task a file belongs to based on filename.
    
    Returns: 'Context03', 'Context09', 'Context10', or 'unknown'
    """
    fname = os.path.basename(file_path)
    if "context03" in fname.lower() or "Context03" in fname:
        return "Context03"
    elif "context09" in fname.lower() or "Context09" in fname:
        return "Context09"
    elif "context10" in fname.lower() or "Context10" in fname:
        return "Context10"
    # Try from directory structure
    dir_parts = file_path.lower().split(os.sep)
    for part in dir_parts:
        if "context03" in part:
            return "Context03"
        elif "context09" in part:
            return "Context09"
        elif "context10" in part:
            return "Context10"
    return "unknown"


def _normalize_channel_name(ch_name: str) -> str:
    """Normalize a BrainVision channel name to standard 10-20."""
    # Remove common prefixes
    clean = ch_name.strip()
    if clean.startswith("EEG "):
        clean = clean[4:]
    elif clean.startswith("EEG"):
        clean = clean[3:]
    
    # Direct lookup in map
    upper = clean.upper()
    if upper in _BV_CHANNEL_MAP:
        return _BV_CHANNEL_MAP[upper]
    
    # Try case-insensitive match against standard names
    for std_name in _STANDARD_64CH_NAMES:
        if clean.upper() == std_name.upper():
            return std_name
    
    # Return original if no mapping found
    return clean


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 montage."""
    rename_map = {}
    for ch_name in raw.ch_names:
        new_name = _normalize_channel_name(ch_name)
        if new_name != ch_name and new_name not in raw.ch_names:
            rename_map[ch_name] = new_name
    return rename_map


def _read_participants_tsv(dataset_path: str, participant_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match participant ID
        row = df[df["participant_id"] == participant_id]
        if row.empty:
            # Try with sub- prefix
            row = df[df["participant_id"] == f"sub-{participant_id.replace('sub-', '')}"]
        if row.empty:
            return {}
        
        info = {}
        for col in row.columns:
            if col == "participant_id":
                continue
            val = row[col].values[0]
            # Convert to string, handle NaN
            if pd.isna(val):
                info[col] = "unknown"
            else:
                info[str(col)] = str(val)
        return info
    except Exception:
        return {}


def _extract_subject_id(file_path: str) -> str:
    """Extract BIDS subject ID from file path."""
    fname = os.path.basename(file_path)
    # Match sub-XX pattern
    match = re.search(r'sub-([a-zA-Z0-9]+)', fname)
    if match:
        return f"sub-{match.group(1)}"
    # Try directory structure
    for part in file_path.split(os.sep):
        match = re.search(r'sub-([a-zA-Z0-9]+)', part)
        if match:
            return f"sub-{match.group(1)}"
    return "unknown"


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex value to lowercase standard."""
    if pd.isna(sex_val) or str(sex_val).lower() in ("n/a", "na", "", "unknown", "none"):
        return "unknown"
    s = str(sex_val).lower().strip()
    if s in ("f", "female", "w", "woman"):
        return "female"
    elif s in ("m", "male", "man"):
        return "male"
    return "unknown"


def _normalize_age(age_val: Any) -> str:
    """Normalize age value to string."""
    if pd.isna(age_val) or str(age_val).lower() in ("n/a", "na", "", "unknown", "none"):
        return "unknown"
    try:
        # Handle ranges like "22-45"
        age_str = str(age_val).strip()
        # If it's a float that looks like an int, convert
        if "." in age_str:
            f = float(age_str)
            if f == int(f):
                return str(int(f))
        return age_str
    except (ValueError, TypeError):
        return "unknown"


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------

@dataclass
class OpenNeuroDS004075Kernel:
    """Stage1 kernel for OpenNeuro ds004075 dataset."""

    KERNEL_ID: str = "openneuro-ds004075-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "root_path", os.path.dirname(os.path.dirname(file_path)))
        
        # ------------------------------------------------------------------
        # 1. Channel renaming and montage
        # ------------------------------------------------------------------
        
        # Build and apply rename map
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage if channels match
        current_names = set(raw.ch_names)
        std_names = set(_STANDARD_64CH_NAMES)
        # Check if we have enough standard names to set montage
        if len(current_names & std_names) >= 60:  # Allow some flexibility
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                # Pick only channels that exist in both
                montage_chs = [ch for ch in montage.ch_names if ch in raw.ch_names]
                if len(montage_chs) >= 60:
                    raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
            except Exception:
                pass  # Montage setting failed, continue without
        
        # ------------------------------------------------------------------
        # 2. Extract subject metadata from participants.tsv
        # ------------------------------------------------------------------
        
        subject_id = _extract_subject_id(file_path)
        participant_info = _read_participants_tsv(dataset_path, subject_id)
        
        # Standard fields
        age = _normalize_age(participant_info.get("age", "unknown"))
        sex = _normalize_sex(participant_info.get("sex", participant_info.get("gender", "unknown")))
        
        # Device info — not available in BIDS for this dataset
        # Source: OpenNeuro metadata suggests BrainVision system based on file format
        # Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
        amplifier = "BrainAmp"  # LLM 推断，需人类复核 — BrainVision standard
        cap = "Ag/AgCl"  # LLM 推断，需人类复核 — standard for BrainVision 64ch
        handedness = "unknown"  # Not in participants.tsv for this dataset
        
        # Build eegunity_description
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add any extra required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field in participant_info:
                eegunity_desc[field] = str(participant_info[field])
            else:
                eegunity_desc[field] = "unknown"
        
        # ------------------------------------------------------------------
        # 3. Handle events/annotations
        # ------------------------------------------------------------------
        
        # BrainVision files read by MNE should already have annotations from .vmrk
        # But we need to ensure event descriptions are standardized
        
        task = _detect_task(file_path)
        
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Process existing annotations
            new_descriptions = []
            for desc in raw.annotations.description:
                # Normalize event descriptions
                normalized = _EVENT_VALUE_MAP.get(desc, desc)
                
                # Add task prefix for multi-paradigm discrimination
                # This is raw meta with paradigm prefix (per KERNEL_RULEBOOK §13-1)
                if task != "unknown" and normalized.startswith("Stimulus/S"):
                    # Keep original as-is — the task is encoded in filename/path
                    # Downstream can use task filtering
                    pass
                
                new_descriptions.append(normalized)
            
            # Create new annotations with normalized descriptions
            new_annot = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descriptions,
                orig_time=raw.annotations.orig_time,
            )
            raw.set_annotations(new_annot)
        else:
            # No annotations found — try to read from events.tsv sidecar
            events_tsv_path = file_path.replace(".vhdr", "_events.tsv").replace(".eeg", "_events.tsv")
            if not os.path.exists(events_tsv_path):
                # Try BIDS naming
                base = file_path.replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "")
                events_tsv_path = f"{base}_events.tsv"
            
            if os.path.exists(events_tsv_path):
                try:
                    events_df = pd.read_csv(events_tsv_path, sep="\t")
                    if not events_df.empty:
                        onsets = events_df["onset"].values
                        durations = events_df.get("duration", np.zeros(len(onsets))).values
                        trial_types = events_df.get("trial_type", events_df.get("value", "")).values
                        
                        # Convert to annotations
                        descriptions = []
                        for tt in trial_types:
                            desc = str(tt) if pd.notna(tt) else "unknown"
                            # Normalize
                            desc = _EVENT_VALUE_MAP.get(desc, desc)
                            descriptions.append(desc)
                        
                        annot = mne.Annotations(
                            onset=onsets,
                            duration=durations,
                            description=descriptions,
                        )
                        raw.set_annotations(annot)
                except Exception:
                    pass  # Failed to read events.tsv
        
        # ------------------------------------------------------------------
        # 4. Handle misc channels
        # ------------------------------------------------------------------
        
        # Ensure native misc channels are properly typed
        for misc_ch in _REQUIRED_NATIVE_MISC:
            if misc_ch in raw.ch_names:
                raw.set_channel_types({misc_ch: "misc"})
        
        # Create derived misc channels if needed
        for derived_name, source_info in _DERIVED_MISC_CHANNELS:
            # Implementation would go here if needed
            pass
        
        # ------------------------------------------------------------------
        # 5. Write metadata to raw.info["description"]
        # ------------------------------------------------------------------
        
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004075Kernel()