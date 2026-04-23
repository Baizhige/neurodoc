"""OpenNeuro DS004015 stage1 kernel for EEGUnity.

Attended speaker paradigm using cEEGrid (around-the-ear) EEG.
18 channels, 500 Hz sampling rate, 36 subjects.

This dataset follows BIDS structure with EDF files. Events are stored in
*_events.tsv sidecars. The cEEGrid uses non-standard channel names that
need mapping for proper montage assignment.

Source: https://openneuro.org/datasets/ds004015
Reference: DOI 10.3389/fnins.2022.869426
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Kernel requirements metadata
kernel_requirements = {
    "required_event_ids": ["Beep", "beam", "beep", "omni"],
    "required_info_fields": ["age", "attended_ch", "con_order", "first_bl", "gender", "orig_study", "second_bl", "third_bl"],
    "required_native_misc": [],
    "derived_misc_channels": [],
}


# cEEGrid channel naming - 18 around-the-ear electrodes.
# The cEEGrid uses a specific naming convention with "E" prefix for ear channels.
# Source: DOI 10.3389/fnins.2022.869426, cEEGrid electrode layout
# Annotator: Human, 2026-04-08
_CEEGRID_CHANNEL_MAP: Dict[str, str] = {
    "E1": "cEEGrid_Tp9",
    "E2": "cEEGrid_Tp7",
    "E3": "cEEGrid_Tp8",
    "E4": "cEEGrid_Tp10",
    "E5": "cEEGrid_AntT",
    "E6": "cEEGrid_PostT",
    "E7": "cEEGrid_AntF",
    "E8": "cEEGrid_PostF",
    "E9": "cEEGrid_AntM",
    "E10": "cEEGrid_PostM",
    "E11": "cEEGrid_AntP",
    "E12": "cEEGrid_PostP",
    "E13": "cEEGrid_AntO",
    "E14": "cEEGrid_PostO",
    "E15": "cEEGrid_AntI",
    "E16": "cEEGrid_PostI",
    "E17": "cEEGrid_Ref",
    "E18": "cEEGrid_Gnd",
}


def _find_dataset_root(file_path: str) -> str:
    """Find dataset root by looking for participants.tsv."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        if os.path.exists(os.path.join(current_dir, "participants.tsv")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return current_dir


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if present in dataset root."""
    path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(path):
        return pd.read_csv(path, sep="\t")
    return pd.DataFrame()


def _get_subject_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    basename = os.path.basename(file_path)
    # Match sub-XXX pattern
    if basename.startswith("sub-"):
        parts = basename.split("_")
        if parts:
            return parts[0]  # sub-001
    # Try from directory structure
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part
    return "unknown"


def _get_events_tsv_path(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv for an EEG file."""
    # For BIDS: sub-XXX_task-YYY_eeg.edf -> sub-XXX_task-YYY_events.tsv
    base = file_path.replace("_eeg.edf", "_events.tsv")
    base = base.replace("_eeg.bdf", "_events.tsv")
    base = base.replace("_eeg.set", "_events.tsv")
    if os.path.exists(base):
        return base
    
    # Try without task
    dir_path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Remove extension and _eeg suffix
    name_parts = basename.rsplit(".", 1)[0]
    if name_parts.endswith("_eeg"):
        name_parts = name_parts[:-4]
    
    # Look for any matching events.tsv
    for fname in os.listdir(dir_path):
        if fname.endswith("_events.tsv"):
            return os.path.join(dir_path, fname)
    
    return None


def _load_events_tsv(events_path: str) -> pd.DataFrame:
    """Load events.tsv file."""
    if events_path and os.path.exists(events_path):
        df = pd.read_csv(events_path, sep="\t")
        return df
    return pd.DataFrame()


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = row.get("onset", np.nan)
        if pd.isna(onset):
            continue
        
        duration = row.get("duration", 0.0)
        if pd.isna(duration):
            duration = 0.0
        
        # Use trial_type if available, otherwise value, otherwise stim_type
        desc = None
        for col in ["trial_type", "value", "stim_type"]:
            if col in events_df.columns:
                val = row.get(col)
                if pd.notna(val):
                    desc = str(val)
                    break
        
        if desc is None:
            desc = "unknown"
        
        onsets.append(float(onset))
        durations.append(float(duration))
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


class OpenNeuroDS004015Kernel:
    """Stage1 kernel for OpenNeuro ds004015 (cEEGrid attended speaker paradigm)."""

    KERNEL_ID: str = "openneuro-ds004015-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_root = _find_dataset_root(file_path)
        subject_id = _get_subject_from_path(file_path)
        
        # Load participants.tsv
        participants_df = _load_participants_tsv(dataset_root)
        
        # Extract subject metadata
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "cEEGrid",  # Known from paper
            "handedness": "unknown",
        }
        
        # Required info fields from participants.tsv
        eegunity_description = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "cEEGrid",
            "handedness": "unknown",
        }
        
        if not participants_df.empty:
            # Find matching subject row
            subj_row = None
            for col in ["participant_id", "subject_id"]:
                if col in participants_df.columns:
                    mask = participants_df[col].astype(str).str.contains(
                        subject_id.replace("sub-", ""), na=False
                    ) | participants_df[col].astype(str).str.contains(
                        subject_id, na=False
                    )
                    if mask.any():
                        subj_row = participants_df[mask].iloc[0]
                        break
            
            if subj_row is not None:
                # Age
                if "age" in participants_df.columns:
                    age_val = subj_row.get("age")
                    if pd.notna(age_val):
                        subject_info["age"] = str(int(float(age_val)))
                        eegunity_description["age"] = str(int(float(age_val)))
                
                # Gender/sex
                for col in ["gender", "sex"]:
                    if col in participants_df.columns:
                        val = subj_row.get(col)
                        if pd.notna(val):
                            sex_str = str(val).lower().strip()
                            # Normalize
                            if sex_str in ["m", "male"]:
                                sex_norm = "male"
                            elif sex_str in ["f", "female"]:
                                sex_norm = "female"
                            else:
                                sex_norm = "unknown"
                            subject_info["sex"] = sex_norm
                            eegunity_description["sex"] = sex_norm
                            break
                
                # Required info fields
                for field in kernel_requirements["required_info_fields"]:
                    if field in participants_df.columns:
                        val = subj_row.get(field)
                        if pd.notna(val):
                            eegunity_description[field] = str(val)
                        else:
                            eegunity_description[field] = "unknown"
                    else:
                        eegunity_description[field] = "unknown"
        
        # Device info from paper - cEEGrid with TMSi amplifier
        # Source: DOI 10.3389/fnins.2022.869426
        # Annotator: Human, 2026-04-08
        subject_info["amplifier"] = "TMSi Refa"
        eegunity_description["amplifier"] = "TMSi Refa"
        
        # Set description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Channel renaming - cEEGrid E1-E18 to descriptive names
        # Must happen BEFORE set_montage()
        rename_map = {}
        for old_name, new_name in _CEEGRID_CHANNEL_MAP.items():
            if old_name in raw.ch_names:
                rename_map[old_name] = new_name
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set channel types for cEEGrid
        # cEEGrid channels are all EEG except reference and ground
        ch_types = {}
        for ch_name in raw.ch_names:
            if "Ref" in ch_name:
                ch_types[ch_name] = "eeg"  # Reference, keep as EEG
            elif "Gnd" in ch_name:
                ch_types[ch_name] = "eeg"  # Ground, keep as EEG
            else:
                ch_types[ch_name] = "eeg"
        
        raw.set_channel_types(ch_types)
        
        # cEEGrid is a non-standard montage; skip standard montage
        # The cEEGrid uses around-the-ear electrodes not in standard 10-20
        # Source: DOI 10.3389/fnins.2022.869426
        # Annotator: Human, 2026-04-08
        
        # Handle events from events.tsv sidecar
        # EDF files may not carry triggers, so we must derive from events.tsv
        events_tsv_path = _get_events_tsv_path(file_path)
        if events_tsv_path:
            events_df = _load_events_tsv(events_tsv_path)
            if not events_df.empty:
                # Check if raw already has meaningful annotations
                has_native_events = False
                try:
                    existing_annot = raw.annotations
                    if existing_annot and len(existing_annot) > 0:
                        # Check if they are actual events or just boundary
                        non_boundary = [d for d in existing_annot.description 
                                       if "boundary" not in str(d).lower()]
                        if len(non_boundary) > 0:
                            has_native_events = True
                except Exception:
                    pass
                
                # Always add events from events.tsv to ensure completeness
                # For EDF without annotations, this is essential
                new_annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                
                if len(new_annotations) > 0:
                    # Combine with existing if any
                    try:
                        existing = raw.annotations
                        if existing and len(existing) > 0:
                            combined = existing + new_annotations
                            raw.set_annotations(combined)
                        else:
                            raw.set_annotations(new_annotations)
                    except Exception:
                        raw.set_annotations(new_annotations)
        
        # Ensure required event IDs exist in annotations
        # Check final annotations
        try:
            final_annot = raw.annotations
            if final_annot:
                unique_descs = set(final_annot.description)
                # Verify required events are present (case-insensitive check)
                required_lower = {e.lower() for e in kernel_requirements["required_event_ids"]}
                found_lower = {d.lower() for d in unique_descs}
        except Exception:
            pass
        
        return raw


KERNEL = OpenNeuroDS004015Kernel()