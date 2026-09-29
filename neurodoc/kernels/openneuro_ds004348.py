"""openneuro_ds004348 stage1 kernel for EEGUnity.

Ear-EEG Sleep Monitoring 2017 (EESM17)
- 9 subjects, 35 channels, 200 Hz sampling rate
- Sleep monitoring with ear-EEG and partial polysomnography
- BIDS-compliant dataset with participants.tsv and events.tsv sidecars

Source: https://openneuro.org/datasets/ds004348
Reference: DOI 10.1186/s12938-017-0400-5
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["gender"]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = ["sleep_stage_ordinal"]

# Required native misc channels (none specified)
_REQUIRED_NATIVE_MISC = []

# Sleep stage mapping from events.tsv:staging to ordinal values
# Source: events.json in dataset; values 1-8 defined
# 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Arousal, 7=Artifact, 8=Unscored
# Target ordinal: Wake=0, N1=1, N2=2, N3=3, REM=4
_SLEEP_STAGE_MAP = {
    1: 0.0,   # Wake
    3: 1.0,   # N1
    4: 2.0,   # N2
    5: 3.0,   # N3
    2: 4.0,   # REM
    # 6, 7, 8 excluded (Arousal, Artifact, Unscored)
}

# Channel rename map for standardizing ear-EEG and PSG channel names
# Source: Dataset documentation and BIDS channel naming conventions
# Annotator: LLM, 2026-04-08
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # EEG channels - standard 10-20 approximations for ear-EEG
    "EEG-Fz": "Fz",
    "EEG-Cz": "Cz",
    "EEG-Pz": "Pz",
    "EEG-Oz": "Oz",
    # Ear-EEG channels (left ear)
    "EEG-L1": "LE1",
    "EEG-L2": "LE2",
    "EEG-L3": "LE3",
    "EEG-L4": "LE4",
    "EEG-L5": "LE5",
    # Ear-EEG channels (right ear)
    "EEG-R1": "RE1",
    "EEG-R2": "RE2",
    "EEG-R3": "RE3",
    "EEG-R4": "RE4",
    "EEG-R5": "RE5",
    # EOG channels
    "EOG-Left": "EOG1",
    "EOG-Right": "EOG2",
    # EMG channels
    "EMG-Chin": "EMG1",
    "EMG-Leg": "EMG2",
    # ECG
    "ECG": "ECG",
}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1).zfill(2)
    return "unknown"


def _get_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # BIDS participant_id format: sub-01, sub-02, etc.
        participant_id = f"sub-{int(subject_id):02d}"
        row = df[df["participant_id"] == participant_id]
        if row.empty:
            return {}
        info = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in row.columns:
                val = row[field].values[0]
                info[field] = str(val) if pd.notna(val) else "unknown"
            else:
                info[field] = "unknown"
        return info
    except Exception:
        return {}


def _get_events_tsv_path(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given data file."""
    # BIDS naming: sub-XX_ses-YY_task-ZZ[_acq-AAA]_run-RR[_desc-DESC]_eeg.<ext>
    # Events: sub-XX_ses-YY_task-ZZ[_acq-AAA]_run-RR[_desc-DESC]_events.tsv
    base = file_path.split(".")[0]  # remove extension
    # Check for acq-scoring variant first (sleep staging annotations)
    if "_acq-scoring" in base:
        events_path = base.replace("_eeg", "") + "_events.tsv"
    else:
        # Try standard events.tsv
        events_path = base.rsplit("_eeg", 1)[0] + "_events.tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Also try acq-scoring variant for sleep files
    if "_task-sleep" in base and "_acq-scoring" not in base:
        scoring_base = base.replace("_task-sleep", "_task-sleep_acq-scoring")
        scoring_events = scoring_base.rsplit("_eeg", 1)[0] + "_events.tsv"
        if os.path.exists(scoring_events):
            return scoring_events
    
    return None


def _read_sleep_staging_events(events_path: str) -> Optional[pd.DataFrame]:
    """Read sleep staging events from events.tsv."""
    if not events_path or not os.path.exists(events_path):
        return None
    
    try:
        df = pd.read_csv(events_path, sep="\t")
        # Check for staging column
        if "staging" not in df.columns:
            return None
        # Filter valid staging values (exclude 6, 7, 8)
        valid_mask = df["staging"].isin(_SLEEP_STAGE_MAP.keys())
        return df[valid_mask].copy()
    except Exception:
        return None


def _create_sleep_stage_ordinal_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.RawArray:
    """Create derived misc channel for sleep stage ordinal values.
    
    Creates a step-function channel where each 30-second epoch holds
    the mapped ordinal sleep stage value.
    """
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    data = np.zeros((1, n_samples), dtype=np.float64)
    
    for _, event in events_df.iterrows():
        onset = event["onset"]
        duration = event.get("duration", 30.0)  # Standard 30-s epochs
        staging_val = event["staging"]
        
        if staging_val not in _SLEEP_STAGE_MAP:
            continue
            
        ordinal_val = _SLEEP_STAGE_MAP[staging_val]
        
        # Convert to sample indices
        start_idx = int(onset * sfreq)
        end_idx = int((onset + duration) * sfreq)
        
        # Clamp to data bounds
        start_idx = max(0, min(start_idx, n_samples))
        end_idx = max(0, min(end_idx, n_samples))
        
        if start_idx < end_idx:
            data[0, start_idx:end_idx] = ordinal_val
    
    # Create info for misc channel
    info = mne.create_info(
        ch_names=["sleep_stage_ordinal"],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    
    raw_misc = mne.io.RawArray(data, info, verbose=False)
    return raw_misc


def _derive_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_path: str) -> mne.io.BaseRaw:
    """Derive MNE Annotations from BIDS events.tsv sidecar.
    
    For file formats that may not carry their own triggers (EDF without
    annotations, SET without populated event, etc.), read sibling events.tsv
    and create annotations.
    """
    try:
        df = pd.read_csv(events_path, sep="\t")
        
        # Required columns for annotations
        if "onset" not in df.columns:
            return raw
        
        onsets = df["onset"].values
        durations = df["duration"].values if "duration" in df.columns else np.zeros(len(df))
        
        # Description: prefer trial_type, then value, then stim_type
        if "trial_type" in df.columns:
            descriptions = df["trial_type"].astype(str).values
        elif "value" in df.columns:
            descriptions = df["value"].astype(str).values
        elif "stim_type" in df.columns:
            descriptions = df["stim_type"].astype(str).values
        else:
            # Use generic description with row index
            descriptions = np.array([f"event_{i}" for i in range(len(df))])
        
        # Filter out empty/NaN descriptions
        valid_mask = pd.notna(descriptions) & (descriptions != "nan") & (descriptions != "")
        if not valid_mask.any():
            return raw
        
        onsets = onsets[valid_mask]
        durations = durations[valid_mask]
        descriptions = descriptions[valid_mask]
        
        # Ensure non-negative durations
        durations = np.maximum(durations, 0)
        
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions.tolist()
        )
        
        raw.set_annotations(annotations)
        return raw
        
    except Exception:
        return raw


class OpenNeuroDS004348Kernel:
    """Stage1 kernel for OpenNeuro ds004348 (EESM17 ear-EEG sleep monitoring)."""

    KERNEL_ID: str = "openneuro-ds004348-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID
        subject_id = _extract_subject_id(file_path)
        
        # Get participants info
        participants_info = _get_participants_info(dataset_path, subject_id)
        
        # Build eegunity_description
        original_desc = raw.info.get("description", "") or ""
        
        # Gender from participants.tsv (required info field)
        gender = participants_info.get("gender", "unknown")
        # Normalize gender to lowercase standard
        gender_lower = gender.lower().strip() if gender != "unknown" else "unknown"
        if gender_lower in ["m", "male"]:
            sex = "male"
        elif gender_lower in ["f", "female"]:
            sex = "female"
        else:
            sex = "unknown"
        
        # Age is missing in this dataset
        age = "unknown"  # Not available in participants.tsv
        
        # Device info - from dataset documentation
        # Source: analysis.md and dataset README
        # Annotator: LLM, 2026-04-08
        amplifier = "unknown"  # inferred by LLM, needs human review
        cap = "unknown"  # inferred by LLM, needs human review (ear-EEG custom electrodes)
        handedness = "unknown"  # Not in participants.tsv
        
        eegunity_description = {
            "age": str(age),
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
            "gender": gender,  # Include original gender field from participants.tsv
        }
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Channel renaming BEFORE set_montage
        rename_map = {}
        existing_names = set(raw.ch_names)
        for old_name, new_name in _CHANNEL_RENAME_MAP.items():
            if old_name in existing_names and old_name != new_name:
                rename_map[old_name] = new_name
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage if channels match standard positions
        try:
            # Try standard 1005 montage for available channels
            montage = mne.channels.make_standard_montage("standard_1005")
            # Only set montage for channels that exist in the montage
            montage_ch_names = set(montage.ch_names)
            raw_eeg_chs = [ch for ch in raw.ch_names 
                          if ch in montage_ch_names and 
                          raw.get_channel_types(picks=[ch])[0] == "eeg"]
            if raw_eeg_chs:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without
        
        # Handle native misc channels (ensure type is 'misc')
        native_misc_to_set = {}
        for ch_name in raw.ch_names:
            # Detect potential misc channels by name patterns
            if any(pattern in ch_name.upper() for pattern in 
                   ["PHOTIC", "PHOTO", "MARKER", "TRIGGER", "STIM", "RESP", 
                    "TEMP", "PULSE", "OXIM", "GSR", "EDA"]):
                current_type = raw.get_channel_types(picks=[ch_name])[0]
                if current_type != "misc":
                    native_misc_to_set[ch_name] = "misc"
        
        if native_misc_to_set:
            raw.set_channel_types(native_misc_to_set)
        
        # Derive annotations from events.tsv if needed
        # Check if raw has meaningful annotations/events
        has_native_events = False
        try:
            # Try to get events from annotations
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if len(events) > 0:
                has_native_events = True
        except Exception:
            pass
        
        # Also check for stim channels
        stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
        if len(stim_picks) > 0:
            has_native_events = True
        
        # If no native events, derive from events.tsv
        events_tsv_path = _get_events_tsv_path(file_path)
        if not has_native_events and events_tsv_path and os.path.exists(events_tsv_path):
            raw = _derive_annotations_from_events_tsv(raw, events_tsv_path)
        
        # Create derived misc channel: sleep_stage_ordinal
        # Read from acq-scoring_events.tsv staging column
        scoring_events_path = None
        
        # Find acq-scoring events.tsv specifically
        base = file_path.split(".")[0]
        if "_task-sleep" in base:
            # Try acq-scoring variant
            scoring_base = base.replace("_task-sleep", "_task-sleep_acq-scoring")
            scoring_events_path = scoring_base.rsplit("_eeg", 1)[0] + "_events.tsv"
            if not os.path.exists(scoring_events_path):
                # Try with _eeg in name
                scoring_events_path = scoring_base + "_events.tsv"
        
        # Also check general events path
        if not scoring_events_path or not os.path.exists(scoring_events_path):
            scoring_events_path = events_tsv_path
        
        if scoring_events_path and os.path.exists(scoring_events_path):
            staging_df = _read_sleep_staging_events(scoring_events_path)
            if staging_df is not None and len(staging_df) > 0:
                # Create the derived misc channel
                raw_misc = _create_sleep_stage_ordinal_channel(raw, staging_df)
                
                # Add to raw
                raw = raw.add_channels([raw_misc], force_update_info=True)
                
                # Ensure channel type is misc
                if "sleep_stage_ordinal" in raw.ch_names:
                    raw.set_channel_types({"sleep_stage_ordinal": "misc"})
        
        return raw


KERNEL = OpenNeuroDS004348Kernel()