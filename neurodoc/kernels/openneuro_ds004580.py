"""OpenNeuro DS004580 stage1 kernel for EEGUnity.

Simon-conflict task dataset with 64-channel EEG recorded via BrainVision.
BIDS-compliant with participants.tsv and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds004580
DOI: https://doi.org/10.1101/2022.07.26.22278079
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Extended 10-20 layout with 64 channels as used in this dataset.
# Source: BrainVision actiCAP 64Ch Standard-2 layout; verified against
# dataset channel count (64) and standard BrainVision naming.
# Annotator: LLM, 2026-04-08
_EXTENDED_1020_64 = [
    "Fp1", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
]


def _build_brainvision_channel_rename_map(raw: mne.io.BaseRaw) -> dict:
    """Build a channel rename map from BrainVision vendor names to standard 10-20 names.
    
    BrainVision often exports channels as 'EEG 001', 'EEG 002', etc. or 'EEG 01', 'EEG 02'.
    This maps them to the standard extended 10-20 names in order.
    """
    rename_map: dict = {}
    existing_names = set(raw.ch_names)

    for idx, standard_name in enumerate(_EXTENDED_1020_64, start=1):
        # Try multiple zero-padding patterns used by BrainVision
        for pattern in [f"EEG {idx:03d}", f"EEG {idx:02d}", f"EEG {idx:d}", f"EEG{idx:03d}", f"EEG{idx:02d}", f"EEG{idx:d}"]:
            if pattern in existing_names and pattern != standard_name:
                rename_map[pattern] = standard_name
                break
        # Also check for plain numeric channel names
        for pattern in [f"{idx:03d}", f"{idx:02d}", f"{idx:d}"]:
            if pattern in existing_names and pattern != standard_name:
                rename_map[pattern] = standard_name
                break

    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the sibling events.tsv file for a given EEG file in BIDS layout."""
    # BIDS naming: sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_eeg.<ext>
    # events: sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_events.tsv
    base = os.path.splitext(file_path)[0]
    # Remove any suffix like _eeg to get the base entity string
    if base.endswith("_eeg"):
        base = base[:-4]
    
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: some files use different suffixes
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # Extract sub- and task- entities
    sub_match = None
    task_match = None
    for part in file_name.split("_"):
        if part.startswith("sub-"):
            sub_match = part
        elif part.startswith("task-"):
            task_match = part
        elif part.startswith("ses-"):
            pass  # session info
    
    if sub_match and task_match:
        # Search in same directory
        for f in os.listdir(dir_name):
            if f.endswith("_events.tsv") and sub_match in f and task_match in f:
                return os.path.join(dir_name, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from the file path."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at root
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_info(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {
        "AGE": "unknown",
        "GENDER": "unknown",
        "GROUP": "unknown",
        "MOCA": "unknown",
        "TYPE": "unknown",
        "UPDRS": "unknown",
    }
    
    participants_tsv = _find_participants_tsv(file_path)
    if participants_tsv is None:
        return info
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        # Normalize subject_id format
        if not subject_id.startswith("sub-"):
            search_id = f"sub-{subject_id}"
        else:
            search_id = subject_id
        
        # Try participant_id column
        if "participant_id" in df.columns:
            row = df[df["participant_id"] == search_id]
            if len(row) == 0:
                # Try without sub- prefix
                row = df[df["participant_id"] == subject_id.replace("sub-", "")]
            if len(row) > 0:
                for col in info.keys():
                    if col in row.columns:
                        val = row[col].values[0]
                        if pd.notna(val):
                            info[col] = str(val)
                # Also check for age/sex variants
                if "age" in row.columns and info["AGE"] == "unknown":
                    val = row["age"].values[0]
                    if pd.notna(val):
                        info["AGE"] = str(int(float(val)))
                if "sex" in row.columns and info["GENDER"] == "unknown":
                    val = row["sex"].values[0]
                    if pd.notna(val):
                        info["GENDER"] = str(val).lower()
                if "gender" in row.columns and info["GENDER"] == "unknown":
                    val = row["gender"].values[0]
                    if pd.notna(val):
                        info["GENDER"] = str(val).lower()
    except Exception:
        pass
    
    return info


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    required_cols = ["onset"]
    if not all(col in events_df.columns for col in required_cols):
        return None
    
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Use trial_type if available, otherwise value, otherwise stim_type
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["event"] * len(onsets))
    
    # Handle NaN in descriptions
    descriptions = np.where(pd.isna(descriptions), "unknown", descriptions)
    
    # Filter out boundary events if they're just recording boundaries
    valid_mask = ~np.isnan(onsets)
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    if len(onsets) == 0:
        return None
    
    # Ensure durations are non-negative
    durations = np.maximum(durations, 0)
    
    annotations = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions.tolist(),
    )
    return annotations


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    file_name = os.path.basename(file_path)
    parts = file_name.split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part
    # Try from directory structure
    dirs = os.path.normpath(file_path).split(os.sep)
    for d in dirs:
        if d.startswith("sub-"):
            return d
    return "unknown"


@dataclass
class OpenNeuroDS004580Kernel:
    """Stage1 kernel for OpenNeuro DS004580 (Simon-conflict Task)."""

    KERNEL_ID: str = "openneuro-ds004580-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single Simon task recording."""
        original_desc = raw.info.get("description", "")
        file_path = row["File Path"] if "File Path" in row else str(row.get("file_path", ""))
        
        # Extract subject ID
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Read participants.tsv info
        participants_info = _read_participants_info(file_path, subject_id)
        
        # --- Channel renaming BEFORE set_montage() ---
        rename_map = _build_brainvision_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage for standard 10-20
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Check that all channel names are in the montage
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(raw.ch_names)
            missing = raw_ch_names - montage_ch_names
            if missing:
                # Some channels might not be in standard_1020; try to proceed anyway
                # or use on_missing='ignore'
                raw.set_montage(montage, on_missing="ignore", verbose=False)
            else:
                raw.set_montage(montage, verbose=False)
        except Exception:
            pass  # inferred by LLM, needs human review: montage setup failure
        
        # --- Process events from events.tsv if raw lacks annotations ---
        # BrainVision .vhdr/.eeg files may have markers in separate .vmrk file
        # If MNE didn't read them (no annotations or empty), read from events.tsv
        needs_events_from_tsv = False
        current_annotations = raw.annotations
        if current_annotations is None or len(current_annotations) == 0:
            needs_events_from_tsv = True
        else:
            # Check if we only have system events
            descs = set(current_annotations.description)
            if descs == {"boundary"} or len(descs) == 0:
                needs_events_from_tsv = True
        
        # Also check for BrainVision-specific: if raw has no stim channel data
        if not needs_events_from_tsv:
            try:
                events, event_id = mne.events_from_annotations(raw, verbose=False)
                if len(events) == 0:
                    needs_events_from_tsv = True
            except Exception:
                needs_events_from_tsv = True
        
        if needs_events_from_tsv:
            events_tsv_path = _find_events_tsv(file_path)
            if events_tsv_path:
                events_df = _read_events_tsv(events_tsv_path)
                if events_df is not None and len(events_df) > 0:
                    annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                    if annotations is not None:
                        # Combine with existing if any
                        if current_annotations is not None and len(current_annotations) > 0:
                            raw.set_annotations(current_annotations + annotations)
                        else:
                            raw.set_annotations(annotations)
        
        # --- Handle required native misc channels ---
        # No required_native_misc or derived_misc_channels specified for this dataset
        
        # --- Build eegunity_description ---
        # Map GENDER to sex format
        sex = participants_info.get("GENDER", "unknown").lower()
        if sex not in ("male", "female"):
            sex = "unknown"
        
        age = participants_info.get("AGE", "unknown")
        if age != "unknown":
            # Ensure it's a string representation
            try:
                age = str(int(float(age)))
            except ValueError:
                age = "unknown"
        
        # Build description with required info fields
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": "BrainAmp",  # inferred by LLM, needs human review: BrainVision typical amplifier
            "cap": "Ag/AgCl",  # inferred by LLM, needs human review: standard actiCAP
            "handedness": "unknown",  # Not in participants.tsv for this dataset
        }
        
        # Add required info fields from participants.tsv
        required_fields = ["AGE", "GENDER", "GROUP", "MOCA", "TYPE", "UPDRS"]
        for field in required_fields:
            val = participants_info.get(field, "unknown")
            if val == "unknown" or val == "" or val == "nan":
                val = "unknown"
            eegunity_description[field] = str(val)
        
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004580Kernel()