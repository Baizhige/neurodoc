"""OpenNeuro DS004504 stage1 kernel for EEGUnity.

Resting-state EEG dataset of Alzheimer's disease (AD), Frontotemporal dementia (FTD),
and Cognitively Normal (CN) subjects. 88 subjects, 176 files (2 sessions each),
19-channel 10-20 system, 500 Hz.

BIDS-compliant dataset with .set files (EEGLAB format). No discrete event markers
in raw files; labels derived from participants.tsv Group column.

Source: https://openneuro.org/datasets/ds004504
DOI: 10.3390/data8060095 (dataset descriptor)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 19-channel 10-20 system used in this dataset
# Source: Dataset descriptor paper (10.3390/data8060095) — 19 channels, 10-20 system
# Annotator: LLM, 2026-04-08
_STANDARD_19_CHANNELS = [
    "Fp1", "Fp2",  # prefrontal
    "F7", "F3", "Fz", "F4", "F8",  # frontal
    "T3", "C3", "Cz", "C4", "T4",  # central (T3/T4 = T7/T8 in newer nomenclature)
    "T5", "P3", "Pz", "P4", "T6",  # parietal (T5/T6 = P7/P8 in newer nomenclature)
    "O1", "O2",  # occipital
]

# Channel rename map for common non-standard naming variants
# Source: 10-20 international system standard names
# Annotator: LLM, 2026-04-08
_CHANNEL_RENAME_MAP = {
    # Temporal channels: older 10-20 vs newer 10-10 nomenclature
    "T7": "T3",
    "T8": "T4",
    "P7": "T5",
    "P8": "T6",
    # EEG-prefixed variants
    "EEG-Fp1": "Fp1",
    "EEG-Fp2": "Fp2",
    "EEG-F7": "F7",
    "EEG-F3": "F3",
    "EEG-Fz": "Fz",
    "EEG-F4": "F4",
    "EEG-F8": "F8",
    "EEG-T7": "T3",
    "EEG-C3": "C3",
    "EEG-Cz": "Cz",
    "EEG-C4": "C4",
    "EEG-T8": "T4",
    "EEG-P7": "T5",
    "EEG-P3": "P3",
    "EEG-Pz": "Pz",
    "EEG-P4": "P4",
    "EEG-P8": "T6",
    "EEG-O1": "O1",
    "EEG-O2": "O2",
    # Numbered variants (if any)
    "EEG 0": "Fp1",
    "EEG 1": "Fp2",
    "EEG 2": "F7",
    "EEG 3": "F3",
    "EEG 4": "Fz",
    "EEG 5": "F4",
    "EEG 6": "F8",
    "EEG 7": "T3",
    "EEG 8": "C3",
    "EEG 9": "Cz",
    "EEG 10": "C4",
    "EEG 11": "T4",
    "EEG 12": "T5",
    "EEG 13": "P3",
    "EEG 14": "Pz",
    "EEG 15": "P4",
    "EEG 16": "T6",
    "EEG 17": "O1",
    "EEG 18": "O2",
}

# Required info fields from participants.tsv
# Source: Kernel Requirements v2 task synthesizer
_REQUIRED_INFO_FIELDS = ["Age", "Gender", "Group", "MMSE"]

# Required derived misc channels (none for this dataset)
_REQUIRED_DERIVED_MISC_CHANNELS: List[str] = []

# Required native misc channels (none for this dataset)
_REQUIRED_NATIVE_MISC_CHANNELS: List[str] = []


def _detect_dataset_root(file_path: str) -> str:
    """Infer dataset root directory from file path.
    
    BIDS datasets have sub-*/ directories under root.
    """
    parts = os.path.normpath(file_path).split(os.sep)
    for i, part in enumerate(parts):
        if re.match(r'^sub-[0-9a-zA-Z]+$', part):
            return os.sep.join(parts[:i])
    # Fallback: go up until we find participants.tsv
    current = os.path.dirname(file_path)
    for _ in range(5):  # reasonable depth limit
        if os.path.exists(os.path.join(current, "participants.tsv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv from dataset root."""
    tsv_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # Match sub-XX pattern in path
    match = re.search(r'sub-([0-9a-zA-Z]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.set -> sub-XX_task-YY_run-ZZ_events.tsv
    base = file_path.replace("_eeg.set", "").replace("_eeg.edf", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run level
    base_no_run = re.sub(r'_run-[0-9a-zA-Z]+', '', base)
    if base_no_run != base:
        events_path = base_no_run + "_events.tsv"
        if os.path.exists(events_path):
            return events_path
    
    # Search in same directory
    eeg_dir = os.path.dirname(file_path)
    for f in os.listdir(eeg_dir):
        if f.endswith("_events.tsv"):
            return os.path.join(eeg_dir, f)
    
    return None


def _normalize_sex(value: Any) -> str:
    """Normalize sex/gender value to lowercase standard."""
    if pd.isna(value) or value is None:
        return "unknown"
    val = str(value).strip().lower()
    if val in ("f", "female", "w", "woman"):
        return "female"
    elif val in ("m", "male", "man"):
        return "male"
    return "unknown"


def _normalize_age(value: Any) -> str:
    """Normalize age value to string."""
    if pd.isna(value) or value is None:
        return "unknown"
    try:
        # Handle both numeric and string ages
        age_float = float(value)
        if age_float <= 0 or age_float > 150:
            return "unknown"
        return str(int(age_float))
    except (ValueError, TypeError):
        val = str(value).strip()
        if val and val.lower() not in ("n/a", "na", "unknown", ""):
            return val
        return "unknown"


class OpenNeuroDS004504Kernel:
    """Stage1 kernel for OpenNeuro ds004504 dataset."""

    KERNEL_ID: str = "openneuro-ds004504-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_root = _detect_dataset_root(file_path)
        subject_id = _get_subject_id_from_path(file_path)
        
        # Load participants.tsv
        participants_df = _load_participants_tsv(dataset_root)
        
        # Get subject info from participants.tsv
        subject_info: Dict[str, str] = {}
        if not participants_df.empty and subject_id and "participant_id" in participants_df.columns:
            # Normalize participant_id for matching (handle sub- prefix variations)
            pid_col = participants_df["participant_id"].astype(str)
            # Try exact match
            mask = pid_col == subject_id
            if not mask.any():
                # Try without sub- prefix
                mask = pid_col == subject_id.replace("sub-", "")
            if not mask.any():
                # Try with sub- prefix added
                mask = pid_col == f"sub-{subject_id.replace('sub-', '')}"
            
            if mask.any():
                subj_row = participants_df[mask].iloc[0]
                for field in _REQUIRED_INFO_FIELDS:
                    if field in subj_row.index:
                        val = subj_row[field]
                        if pd.isna(val):
                            subject_info[field] = "unknown"
                        else:
                            subject_info[field] = str(val).strip()
                    else:
                        subject_info[field] = "unknown"
        
        # Fill missing required fields with "unknown"
        for field in _REQUIRED_INFO_FIELDS:
            if field not in subject_info:
                subject_info[field] = "unknown"
        
        # Extract canonical fields
        age = _normalize_age(subject_info.get("Age", "unknown"))
        sex = _normalize_sex(subject_info.get("Gender", "unknown"))
        group = subject_info.get("Group", "unknown")
        mmse = subject_info.get("MMSE", "unknown")
        
        # Device metadata — from dataset descriptor paper
        # Source: 10.3390/data8060095 — BrainAmp amplifier, Ag/AgCl cap
        # Annotator: LLM, 2026-04-08
        amplifier = "BrainAmp"  # inferred by LLM, needs human review
        cap = "Ag/AgCl"  # inferred by LLM, needs human review
        handedness = "unknown"  # Not provided in participants.tsv
        
        # Channel renaming to standard 10-20 names
        rename_map = {}
        for old_name in raw.ch_names:
            if old_name in _CHANNEL_RENAME_MAP:
                rename_map[old_name] = _CHANNEL_RENAME_MAP[old_name]
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Ensure all channels are EEG type (not misc or other)
        # Set channel types for any non-EEG channels that should be EEG
        ch_types = raw.get_channel_types()
        type_map = {}
        for ch_name, ch_type in zip(raw.ch_names, ch_types):
            if ch_name in _STANDARD_19_CHANNELS and ch_type != "eeg":
                type_map[ch_name] = "eeg"
        
        if type_map:
            raw.set_channel_types(type_map)
        
        # Set montage for standard 10-20 system
        # All 19 channels should be present after renaming
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in both raw and montage
            raw.pick([ch for ch in raw.ch_names if ch in montage.ch_names])
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            # If montage fails, continue without it
            pass
        
        # Handle events from events.tsv if raw has no annotations/events
        # EEGLAB .set files may have events, but we check for events.tsv as backup
        events_tsv_path = _find_events_tsv(file_path)
        
        # Check if raw already has meaningful annotations
        has_annotations = False
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Check if annotations are meaningful (not just empty or single entry)
            descs = [d for d in raw.annotations.description if d and str(d).strip()]
            if len(descs) > 0:
                has_annotations = True
        
        # If no meaningful annotations and events.tsv exists, create annotations from it
        if not has_annotations and events_tsv_path and os.path.exists(events_tsv_path):
            try:
                events_df = pd.read_csv(events_tsv_path, sep="\t")
                if len(events_df) > 0 and "onset" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(events_df))
                    
                    # Use trial_type if available, else value, else stim_type
                    if "trial_type" in events_df.columns:
                        descriptions = events_df["trial_type"].astype(str).values
                    elif "value" in events_df.columns:
                        descriptions = events_df["value"].astype(str).values
                    elif "stim_type" in events_df.columns:
                        descriptions = events_df["stim_type"].astype(str).values
                    else:
                        descriptions = np.array(["event"] * len(events_df))
                    
                    # Filter out empty/NaN descriptions
                    valid_mask = [d and str(d).strip().lower() not in ("nan", "n/a", "") for d in descriptions]
                    if any(valid_mask):
                        onsets = onsets[valid_mask]
                        durations = durations[valid_mask] if len(durations) == len(valid_mask) else np.zeros(sum(valid_mask))
                        descriptions = descriptions[valid_mask]
                        
                        # Convert onsets to seconds if they appear to be in samples
                        if np.max(onsets) > raw.n_times:
                            onsets = onsets / raw.info["sfreq"]
                        
                        annotations = mne.Annotations(
                            onset=onsets,
                            duration=durations,
                            description=descriptions,
                        )
                        raw.set_annotations(annotations)
            except Exception:
                # If events.tsv parsing fails, continue without annotations
                pass
        
        # Handle derived misc channels if required
        for misc_name in _REQUIRED_DERIVED_MISC_CHANNELS:
            if misc_name not in raw.ch_names:
                # Create constant broadcast channel with group label value
                # Use numeric encoding: AD=0, FTD=1, CN=2, unknown=-1
                group_val = -1.0
                if group == "A" or group == "AD":
                    group_val = 0.0
                elif group == "F" or group == "FTD":
                    group_val = 1.0
                elif group == "C" or group == "CN" or group == "HC":
                    group_val = 2.0
                
                misc_data = np.full((1, raw.n_times), group_val)
                misc_info = mne.create_info([misc_name], raw.info["sfreq"], ["misc"])
                misc_raw = mne.io.RawArray(misc_data, misc_info)
                raw.add_channels([misc_raw], force_update_info=True)
        
        # Ensure native misc channels are typed correctly
        for misc_name in _REQUIRED_NATIVE_MISC_CHANNELS:
            if misc_name in raw.ch_names:
                current_type = raw.get_channel_types(picks=[misc_name])[0]
                if current_type != "misc":
                    raw.set_channel_types({misc_name: "misc"})
        
        # Build eegunity_description
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
            # Required info fields from participants.tsv
            "Group": group,
            "MMSE": mmse,
        }
        
        # Add any extra required info fields
        for field in _REQUIRED_INFO_FIELDS:
            if field not in eegunity_description and field in subject_info:
                eegunity_description[field] = subject_info[field]
        
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004504Kernel()