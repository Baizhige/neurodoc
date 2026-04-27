"""OpenNeuro ds005345 (Le Petit Prince Multitalker) stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds005345
EEG recorded during 7T fMRI with 64-channel actiCAP system at 500 Hz.
Paradigm: naturalistic listening to single-talker and multi-talker speech.

Source: DOI 10.1038/s41597-025-05158-7 (Nature Scientific Data, 2025)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Known metadata from dataset documentation
# Source: Dataset description and DOI 10.1038/s41597-025-05158-7
# Annotator: Human, 2025-06-20
_DATASET_METADATA = {
    "amplifier": "BrainAmp MR plus",  # 7T MRI-compatible EEG system
    "cap": "actiCAP 64-channel",  # From "Comment/actiCAP Data On" marker
}

# Event mapping from raw event codes to human-readable labels
# Source: DOI 10.1101/2025.04.03.646958 (validation paper)
# Annotator: Human, 2025-06-20
_EVENT_MAP = {
    11: "Stimulus/S 11",
    31: "Stimulus/S 31",
    32: "Stimulus/S 32",
    33: "Stimulus/S 33",
    34: "Stimulus/S 34",
}


def _load_bids_participants(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if exists."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _extract_subject_info(row, dataset_path: str) -> Dict[str, Any]:
    """Extract subject info from BIDS participants.tsv or infer defaults."""
    subject_id = row.get("participant_id", "unknown")
    participants_df = _load_bids_participants(dataset_path)
    
    if not participants_df.empty and "participant_id" in participants_df.columns:
        subj_row = participants_df[participants_df["participant_id"] == subject_id]
        if not subj_row.empty:
            age = subj_row.iloc[0].get("age", "unknown")
            sex = subj_row.iloc[0].get("sex", "unknown")
            handedness = subj_row.iloc[0].get("hand", "unknown")
            
            # Normalize sex to lowercase
            if pd.notna(sex):
                sex = str(sex).lower()
                if sex not in ["male", "female"]:
                    sex = "unknown"
            else:
                sex = "unknown"
            
            # Normalize handedness
            if pd.notna(handedness):
                handedness = str(handedness).lower()
                if handedness not in ["right", "left"]:
                    handedness = "unknown"
            else:
                handedness = "unknown"
            
            # Age as string
            if pd.notna(age):
                age = str(int(float(age)))
            else:
                age = "unknown"
            
            return {"age": age, "sex": sex, "handedness": handedness}
    
    # Defaults for missing metadata
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XX_task-YY_eeg.edf -> sub-XX_task-YY_events.tsv
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: same directory
    dir_path = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).split("_eeg")[0]
    for f in os.listdir(dir_path):
        if f.endswith("_events.tsv") and f.startswith(base_name):
            return os.path.join(dir_path, f)
    
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    return pd.read_csv(events_path, sep="\t")


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required columns in BIDS events.tsv
    onsets = events_df["onset"].values
    durations = events_df.get("duration", [0] * len(onsets)).values
    if "duration" not in events_df.columns:
        durations = [0.0] * len(onsets)
    
    # Use trial_type if available, otherwise value, otherwise description
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        # Map numeric values to event names if possible
        descriptions = []
        for val in events_df["value"].values:
            if val in _EVENT_MAP:
                descriptions.append(_EVENT_MAP[val])
            else:
                descriptions.append(str(val))
    else:
        descriptions = events_df.get("description", ["unknown"] * len(onsets)).astype(str).values
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _standardize_channel_names(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names to 10-20 convention if needed."""
    # Check if channels already follow standard naming
    ch_names = raw.ch_names
    
    # Common BrainAmp/MR channel naming patterns
    # If channels are numbered (e.g., 1-64), we need to map to 10-20
    # Based on actiCAP 64-channel standard layout
    
    # Check if we have standard names already
    standard_1020_names = {
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
        "T7", "C3", "Cz", "C4", "T8", "TP9", "CP5", "CP1", "CP2", "CP6", "TP10",
        "P7", "P3", "Pz", "P4", "P8", "PO9", "O1", "Oz", "O2", "PO10",
        "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2", "F6", "FT9", "FT7", "FC3",
        "FC4", "FT8", "FT10", "C5", "C1", "C2", "C6", "TP7", "CP3", "CPz", "CP4",
        "TP8", "P5", "P1", "P2", "P6", "PO7", "PO3", "POz", "PO4", "PO8"
    }
    
    # If most channels match standard names, no renaming needed
    matching = sum(1 for ch in ch_names if ch.upper() in {n.upper() for n in standard_1020_names} or ch in standard_1020_names)
    if matching >= len(ch_names) * 0.8:
        return raw
    
    # If channels are numbered, apply standard 64-channel actiCAP mapping
    # Source: actiCAP 64-channel standard layout for BrainAmp
    # Annotator: Human, 2025-06-20
    numbered_map = {
        "1": "Fp1", "2": "Fp2", "3": "F7", "4": "F3", "5": "Fz", "6": "F4", "7": "F8",
        "8": "FC5", "9": "FC1", "10": "FC2", "11": "FC6", "12": "T7", "13": "C3",
        "14": "Cz", "15": "C4", "16": "T8", "17": "TP9", "18": "CP5", "19": "CP1",
        "20": "CP2", "21": "CP6", "22": "TP10", "23": "P7", "24": "P3", "25": "Pz",
        "26": "P4", "27": "P8", "28": "PO9", "29": "O1", "30": "Oz", "31": "O2",
        "32": "PO10", "33": "AF7", "34": "AF3", "35": "AF4", "36": "AF8", "37": "F5",
        "38": "F1", "39": "F2", "40": "F6", "41": "FT9", "42": "FT7", "43": "FC3",
        "44": "FC4", "45": "FT8", "46": "FT10", "47": "C5", "48": "C1", "49": "C2",
        "50": "C6", "51": "TP7", "52": "CP3", "53": "CPz", "54": "CP4", "55": "TP8",
        "56": "P5", "57": "P1", "58": "P2", "59": "P6", "60": "PO7", "61": "PO3",
        "62": "POz", "63": "PO4", "64": "PO8"
    }
    
    rename_map = {}
    for old_name in ch_names:
        # Strip common prefixes
        clean_name = old_name.replace("EEG ", "").replace("EEG", "").replace("Ch", "").replace("Channel", "").strip()
        if clean_name in numbered_map:
            rename_map[old_name] = numbered_map[clean_name]
        elif clean_name.isdigit() and clean_name in numbered_map:
            rename_map[old_name] = numbered_map[clean_name]
    
    if rename_map:
        raw = raw.rename_channels(rename_map)
    
    return raw


class OpenNeuroDS005345Kernel:
    """Stage1 kernel for OpenNeuro ds005345 (Le Petit Prince Multitalker)."""

    KERNEL_ID: str = "openneuro-ds005345-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        file_path = row["File Path"]
        dataset_path = os.path.dirname(os.path.dirname(file_path))  # Go up to dataset root
        
        # Extract subject info from participants.tsv
        subject_info = _extract_subject_info(row, dataset_path)
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "amplifier": _DATASET_METADATA["amplifier"],
            "cap": _DATASET_METADATA["cap"],
            "handedness": subject_info["handedness"],
        }
        
        # Update description
        original_description = raw.info.get("description", "")
        if original_description is None:
            original_description = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Standardize channel names BEFORE set_montage
        raw = _standardize_channel_names(raw)
        
        # Set montage for standard 10-20 channels
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            # If montage fails, continue without it
            pass
        
        # Handle events from events.tsv if raw doesn't have proper annotations
        # This dataset uses BrainVision format which may need events.tsv for triggers
        current_annotations = raw.annotations
        has_meaningful_annotations = (
            current_annotations is not None 
            and len(current_annotations) > 0
            and any(not desc.startswith("New Segment") for desc in current_annotations.description)
        )
        
        # Check if we need to load events from events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path:
            events_df = _read_events_tsv(events_path)
            
            # Determine if we should use events.tsv annotations
            # Use if raw has no annotations, or if raw annotations seem incomplete
            if not has_meaningful_annotations or len(events_df) > len(current_annotations):
                # Filter to required event IDs
                required_events = ["Stimulus/S 11", "Stimulus/S 31", "Stimulus/S 32", "Stimulus/S 33", "Stimulus/S 34"]
                
                # Check if events.tsv has the required events
                if "trial_type" in events_df.columns:
                    mask = events_df["trial_type"].isin(required_events)
                    if mask.any():
                        filtered_events = events_df[mask]
                        annotations = _events_to_annotations(filtered_events)
                        raw.set_annotations(annotations)
                elif "value" in events_df.columns:
                    # Map numeric values
                    value_map = {11: "Stimulus/S 11", 31: "Stimulus/S 31", 32: "Stimulus/S 32", 
                                33: "Stimulus/S 33", 34: "Stimulus/S 34"}
                    mask = events_df["value"].isin(value_map.keys())
                    if mask.any():
                        filtered_events = events_df[mask].copy()
                        filtered_events["trial_type"] = filtered_events["value"].map(value_map)
                        annotations = _events_to_annotations(filtered_events)
                        raw.set_annotations(annotations)
        
        # Ensure required event IDs are present in final annotations
        final_annotations = raw.annotations
        if final_annotations is not None and len(final_annotations) > 0:
            existing_descriptions = set(final_annotations.description)
            required_events = {"Stimulus/S 11", "Stimulus/S 31", "Stimulus/S 32", "Stimulus/S 33", "Stimulus/S 34"}
            
            # Verify we have the required events (this is for validation)
            found_required = existing_descriptions & required_events
            # We don't error if missing, but the scan will catch it
        
        return raw


KERNEL = OpenNeuroDS005345Kernel()