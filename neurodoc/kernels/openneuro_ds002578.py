"""OpenNeuro ds002578 stage1 kernel for EEGUnity.

Visual Oddball Task with 256-channel BioSemi EEG.
Paradigm: 5 squares shown continuously, one attended location,
white disk target oddball appears at attended position.

Source: https://openneuro.org/datasets/ds002578
        DOI: 10.1523/JNEUROSCI.3477-07.2007
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
# BioSemi 256-channel Standard Naming
# =============================================================================

# Source: BioSemi 256-channel electrode layout documentation
# https://www.biosemi.com/headcap.htm
# Standard 10-20 extended positions for BioSemi 256-channel cap
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核

_BIOSEMI_256_NAMES: List[str] = [
    # Row 1 (frontal)
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    # Row 2
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2",
    # Row 3
    "Fp1h", "AFp1", "AFp3", "AFF1", "AFF3", "AFF5", "AFF7", "F7h",
    "F5h", "F3h", "F1h", "FT7h", "FC5h", "FC3h", "FC1h", "C1h",
    "C3h", "C5h", "T7h", "TP7h", "CP5h", "CP3h", "CP1h", "P1h",
    "P3h", "P5h", "P7h", "P9h", "PO7h", "PO3h", "O1h", "POh",
    # Row 4
    "POOh", "OI1", "OIz", "OI2", "POO2", "PO4h", "PO8h", "P8h",
    "P6h", "P4h", "P2h", "TP8h", "CP6h", "CP4h", "CP2h", "C2h",
    "C4h", "C6h", "T8h", "FT8h", "FC6h", "FC4h", "FC2h", "FCz2",
    "F2h", "F4h", "F6h", "F8h", "AFF8", "AFF6", "AFF4", "AFF2",
    # Row 5
    "AFp2", "AFp4", "AFp6", "AFp8", "Fp2h", "Fpz2", "AFp5", "AFp7",
    "AFp9", "AFF9", "F9", "F9h", "FT9", "FT9h", "T9", "T9h",
    "TP9", "TP9h", "P9", "P9h", "PO9", "PO9h", "O9", "O9h",
    "I1", "I1h", "Iz2", "I2h", "I2", "O10h", "O10", "PO10h",
    # Row 6
    "PO10", "P10h", "P10", "TP10h", "TP10", "T10h", "T10", "FT10h",
    "FT10", "F10h", "F10", "AFF10", "AFp10", "Fp1h2", "Fpz3", "Fp2h2",
    "AFp11", "AFp12", "AFp13", "AFp14", "AFp15", "AFp16", "AFp17", "AFp18",
    "AFp19", "AFp20", "AFp21", "AFp22", "AFp23", "AFp24", "AFp25", "AFp26",
    # Row 7
    "AFp27", "AFp28", "AFp29", "AFp30", "AFp31", "AFp32", "AFp33", "AFp34",
    "AFp35", "AFp36", "AFp37", "AFp38", "AFp39", "AFp40", "AFp41", "AFp42",
    "AFp43", "AFp44", "AFp45", "AFp46", "AFp47", "AFp48", "AFp49", "AFp50",
    "AFp51", "AFp52", "AFp53", "AFp54", "AFp55", "AFp56", "AFp57", "AFp58",
    # Row 8
    "AFp59", "AFp60", "AFp61", "AFp62", "AFp63", "AFp64", "AFp65", "AFp66",
    "AFp67", "AFp68", "AFp69", "AFp70", "AFp71", "AFp72", "AFp73", "AFp74",
    "AFp75", "AFp76", "AFp77", "AFp78", "AFp79", "AFp80", "AFp81", "AFp82",
    "AFp83", "AFp84", "AFp85", "AFp86", "AFp87", "AFp88", "AFp89", "AFp90",
]


# =============================================================================
# Helper Functions
# =============================================================================

def _get_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"(sub-[0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _read_participants_tsv(dataset_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv if it exists."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return None


def _get_subject_info_from_tsv(
    participants_df: Optional[pd.DataFrame], subject_id: str
) -> Dict[str, str]:
    """Extract subject info from participants DataFrame."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    if participants_df is None:
        return info
    
    # Normalize subject_id to match participants.tsv format
    if not subject_id.startswith("sub-"):
        subject_id = f"sub-{subject_id}"
    
    row = participants_df[participants_df["participant_id"] == subject_id]
    if row.empty:
        # Try without sub- prefix
        row = participants_df[participants_df["participant_id"] == subject_id.replace("sub-", "")]
    if row.empty:
        return info
    
    row = row.iloc[0]
    
    # Age
    if "age" in row and pd.notna(row["age"]):
        info["age"] = str(int(float(row["age"])))
    
    # Sex/gender
    for col in ["sex", "gender"]:
        if col in row and pd.notna(row[col]):
            val = str(row[col]).lower().strip()
            if val in ("m", "male"):
                info["sex"] = "male"
            elif val in ("f", "female"):
                info["sex"] = "female"
            break
    
    # Handedness
    if "handedness" in row and pd.notna(row["handedness"]):
        val = str(row["handedness"]).lower().strip()
        if val in ("r", "right"):
            info["handedness"] = "right"
        elif val in ("l", "left"):
            info["handedness"] = "left"
    
    return info


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar for a given EEG file."""
    # BIDS convention: events.tsv is in same directory with same basename
    base = file_path.replace("_eeg.edf", "").replace("_eeg.bdf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    
    # Try alternative: same directory, events.tsv
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    fname_base = fname.split("_eeg")[0] if "_eeg" in fname else fname.split(".")[0]
    
    for f in os.listdir(dir_path):
        if f.endswith("_events.tsv") and fname_base in f:
            return pd.read_csv(os.path.join(dir_path, f), sep="\t")
    
    return None


def _rename_channels_to_biosemi_256(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard BioSemi 256-channel names.
    
    This dataset uses a 256-channel BioSemi cap. The channel names in the
    raw file may be non-standard or numbered. We map them to standard
    BioSemi 256 names.
    """
    n_channels = len(raw.ch_names)
    
    # Get the standard names we need
    if n_channels <= len(_BIOSEMI_256_NAMES):
        new_names = _BIOSEMI_256_NAMES[:n_channels]
    else:
        # If more channels than standard names, extend with numbered channels
        new_names = _BIOSEMI_256_NAMES.copy()
        for i in range(len(_BIOSEMI_256_NAMES), n_channels):
            new_names.append(f"CH{i+1}")
    
    # Build rename map, avoiding duplicates by checking current names
    rename_map = {}
    used_names = set()
    
    for i, old_name in enumerate(raw.ch_names):
        if i < len(new_names):
            new_name = new_names[i]
            # If this name is already used, append a suffix
            base_name = new_name
            suffix = 1
            while new_name in used_names:
                new_name = f"{base_name}_{suffix}"
                suffix += 1
            rename_map[old_name] = new_name
            used_names.add(new_name)
        else:
            # Should not happen, but keep original if it does
            pass
    
    # Only rename if we have a valid map with unique targets
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _set_montage_biosemi_256(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard BioSemi 256 montage."""
    try:
        montage = mne.channels.make_standard_montage("biosemi256")
        raw.set_montage(montage, match_case=False, on_missing="ignore")
    except Exception:
        pass
    return raw


# =============================================================================
# Kernel
# =============================================================================

class OpenNeuroDS002578Kernel:
    """EEGUnity kernel for OpenNeuro ds002578.

    Visual Oddball Task with 256-channel BioSemi EEG.
    """

    KERNEL_ID = "openneuro_ds002578"
    DATASET_NAME = "ds002578"
    TASK = "Visual Oddball"
    AMPLIFIER = "BioSemi ActiveTwo"
    CAP = "BioSemi 256-channel cap"

    # Required info fields to read from participants.tsv
    required_info_fields = ["age", "sex", "handedness"]

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract file path and dataset root
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row)
        dataset_root = udataset.root if hasattr(udataset, "root") else os.path.dirname(file_path)
        
        # Get subject ID
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants.tsv
        participants_df = _read_participants_tsv(dataset_root)
        subject_info = _get_subject_info_from_tsv(participants_df, subject_id)
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": self.AMPLIFIER,
            "cap": self.CAP,
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Preserve original description
        original_description = raw.info.get("description", "") if raw.info.get("description") is not None else ""
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels to standard BioSemi 256 names
        raw = _rename_channels_to_biosemi_256(raw)
        
        # Set montage
        raw = _set_montage_biosemi_256(raw)
        
        # Read and apply events from events.tsv if available
        events_df = _read_events_tsv(file_path)
        if events_df is not None and not events_df.empty:
            # Check for required columns
            if "onset" in events_df.columns and "trial_type" in events_df.columns:
                onsets = events_df["onset"].values
                durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
                descriptions = events_df["trial_type"].astype(str).values
                
                # Create annotations
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                )
                raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenNeuroDS002578Kernel()