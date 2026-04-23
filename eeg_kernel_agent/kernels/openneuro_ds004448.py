"""Dataset-specific kernel for openneuro ds004448 (BMI-HDEEG dataset 4).

High-density EEG motor imagery dataset with 130 channels, 1000 Hz sampling rate.
Participants performed sensorimotor rhythm-based BCI with two-class motor imagery
(left hand vs right hand) and relaxation/rest periods.

BIDS-compliant dataset with EDF files, participants.tsv, and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds004448 | DOI: 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex", "handedness", "amplifier", "cap"]

# Required native misc channels (already in raw data)
_REQUIRED_NATIVE_MISC = []

# Required derived misc channels (kernel must create)
_REQUIRED_DERIVED_MISC = ["trial_index"]

# BrainVision/EDF channel name standardization for 130-channel high-density cap
# Source: BMI-HDEEG paper (10.1038/s41597-023-02260-6) describes 128 EEG + 2 EOG channels
# Standard extended 10-20 layout used with BrainAmp system
# LLM 推断，需人类复核
_CHANNEL_STANDARD_MAP: Dict[str, str] = {
    # Pre-frontal
    "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
    # Anterior frontal
    "AF7": "AF7", "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4", "AF8": "AF8",
    # Frontal
    "F7": "F7", "F5": "F5", "F3": "F3", "F1": "F1", "FZ": "Fz",
    "F2": "F2", "F4": "F4", "F6": "F6", "F8": "F8",
    # Frontal-temporal
    "FT7": "FT7", "FT8": "FT8",
    # Frontal-central
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FCZ": "FCz",
    "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    # Temporal
    "T7": "T7", "T8": "T8",
    # Central
    "C5": "C5", "C3": "C3", "C1": "C1", "CZ": "Cz",
    "C2": "C2", "C4": "C4", "C6": "C6",
    # Temporal-parietal
    "TP7": "TP7", "TP8": "TP8",
    # Central-parietal
    "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CPZ": "CPz",
    "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
    # Parietal
    "P7": "P7", "P5": "P5", "P3": "P3", "P1": "P1", "PZ": "Pz",
    "P2": "P2", "P4": "P4", "P6": "P6", "P8": "P8",
    # Parietal-occipital
    "PO7": "PO7", "PO5": "PO5", "PO3": "PO3", "POZ": "POz",
    "PO4": "PO4", "PO6": "PO6", "PO8": "PO8",
    # Occipital
    "O1": "O1", "OZ": "Oz", "O2": "O2",
    # Extra positions common in 128+ channel systems
    "IZ": "Iz",
    # EOG channels
    "EOG1": "EOG1", "EOG2": "EOG2",
    # Common alternative EOG names
    "VEOG": "VEOG", "HEOG": "HEOG",
}


def _standardize_channel_name(ch_name: str) -> str:
    """Convert raw channel name to standard 10-20 naming."""
    ch_clean = ch_name.strip()
    
    # Remove BrainVision EEG prefix
    if ch_clean.upper().startswith("EEG "):
        ch_clean = ch_clean[4:]
    elif ch_clean.upper().startswith("EEG-"):
        ch_clean = ch_clean[4:]
    elif ch_clean.upper().startswith("EEG"):
        ch_clean = ch_clean[3:]
    
    # Remove leading zeros from numeric channel names
    if ch_clean.isdigit():
        ch_clean = str(int(ch_clean))
    
    # Direct lookup in standard map
    upper_name = ch_clean.upper()
    if upper_name in _CHANNEL_STANDARD_MAP:
        return _CHANNEL_STANDARD_MAP[upper_name]
    
    # Try case-insensitive match
    for key, val in _CHANNEL_STANDARD_MAP.items():
        if key.upper() == upper_name:
            return val
    
    return ch_clean


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for standardizing channel names."""
    rename_map = {}
    for ch_name in raw.ch_names:
        std_name = _standardize_channel_name(ch_name)
        if std_name != ch_name and std_name not in raw.ch_names:
            rename_map[ch_name] = std_name
    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    base = file_path.replace(".edf", "").replace(".bdf", "").replace(".set", "").replace(".eeg", "")
    # Try BIDS naming patterns
    candidates = [
        base + "_events.tsv",
        base.replace("_eeg", "_events.tsv"),
    ]
    # Also check parent directory for session-level events
    dir_path = os.path.dirname(file_path)
    for fname in os.listdir(dir_path) if os.path.isdir(dir_path) else []:
        if fname.endswith("_events.tsv"):
            candidates.append(os.path.join(dir_path, fname))
    
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        ptp = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(ptp):
            return ptp
        current_dir = os.path.dirname(current_dir)
    return None


def _extract_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    import re
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return "sub-" + match.group(1)
    return None


@dataclass
class OpenNeuroDS004448Kernel:
    """Stage1 kernel for OpenNeuro ds004448 (BMI-HDEEG dataset 4)."""

    KERNEL_ID: str = "openneuro-ds004448-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Preload raw data before any operations that require it
        if not raw.preload:
            raw.load_data()

        # --- 1. Channel renaming (before set_montage) ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage for standard 10-20 channels if possible
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
        except Exception:
            pass  # Non-standard channels will be ignored

        # --- 2. Read participants.tsv for subject metadata ---
        subject_id = _extract_subject_id_from_path(file_path)
        participants_path = _find_participants_tsv(file_path)
        
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        amplifier = "unknown"
        cap = "unknown"
        extra_info: Dict[str, str] = {}

        if participants_path and subject_id:
            try:
                df = pd.read_csv(participants_path, sep="\t")
                sub_row = df[df["participant_id"] == subject_id]
                if not sub_row.empty:
                    # Get the first row as a Series
                    ev_row = sub_row.iloc[0]
                    
                    # age
                    if "age" in ev_row.index:
                        val = ev_row["age"]
                        if pd.notna(val):
                            age = str(int(float(val)))
                    
                    # sex (check both sex and gender columns)
                    for col in ["sex", "gender"]:
                        if col in ev_row.index:
                            val = ev_row[col]
                            if pd.notna(val):
                                sex = str(val).lower().strip()
                                break
                    
                    # handedness
                    if "handedness" in ev_row.index:
                        val = ev_row["handedness"]
                        if pd.notna(val):
                            handedness = str(val).lower().strip()
                    
                    # amplifier
                    if "amplifier" in ev_row.index:
                        val = ev_row["amplifier"]
                        if pd.notna(val):
                            amplifier = str(val).lower().strip()
                    
                    # cap
                    if "cap" in ev_row.index:
                        val = ev_row["cap"]
                        if pd.notna(val):
                            cap = str(val).lower().strip()
                    
                    # Collect any other columns as extra info
                    for col in df.columns:
                        if col not in ["participant_id", "age", "sex", "gender", "handedness", "amplifier", "cap"]:
                            if col in ev_row.index:
                                val = ev_row[col]
                                if pd.notna(val):
                                    extra_info[col] = str(val)
            except Exception:
                pass  # Keep defaults if participants.tsv can't be read

        # --- 3. Read events.tsv and add as annotations ---
        events_path = _find_events_tsv(file_path)
        if events_path:
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                # BIDS events.tsv columns: onset, duration, trial_type, [optional]
                if "onset" in events_df.columns and "duration" in events_df.columns:
                    # The onset column in this dataset is in samples, not seconds!
                    # Need to convert to seconds for MNE Annotations
                    sfreq = raw.info["sfreq"]
                    onsets = events_df["onset"].values.astype(float) / sfreq
                    durations = events_df["duration"].values.astype(float) / sfreq
                    
                    # Use 'value' column as the description to preserve event IDs
                    # The 'value' column contains the trigger values (e.g., '1')
                    # HC-5: do NOT remap or rename event IDs - pass literal tsv labels through
                    if "value" in events_df.columns:
                        descriptions = events_df["value"].astype(str).values
                    elif "trial_type" in events_df.columns:
                        descriptions = events_df["trial_type"].astype(str).values
                    else:
                        descriptions = np.array([""] * len(events_df))
                    
                    # Create annotations, filtering out any invalid rows
                    valid_mask = ~(np.isnan(onsets) | np.isnan(durations))
                    if valid_mask.any():
                        # Remove existing annotations to avoid duplicates
                        raw.set_annotations(None)
                        annot = mne.Annotations(
                            onset=onsets[valid_mask],
                            duration=durations[valid_mask],
                            description=descriptions[valid_mask],
                        )
                        raw.set_annotations(annot)
            except Exception:
                pass  # Keep existing annotations if events.tsv can't be parsed

        # --- 4. Create derived misc channels ---
        # trial_index: create a step function based on trial onsets from events
        sfreq = raw.info["sfreq"]
        n_times = raw.n_times
        trial_index_data = np.zeros((1, n_times))

        if events_path:
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                if "onset" in events_df.columns:
                    # Sort by onset to assign trial indices
                    # Onsets are in samples, convert to seconds for time-based indexing
                    onsets = events_df["onset"].values.astype(float) / sfreq
                    valid_mask = ~np.isnan(onsets)
                    onsets = onsets[valid_mask]
                    sorted_indices = np.argsort(onsets)
                    
                    for trial_idx, event_idx in enumerate(sorted_indices, start=1):
                        onset = onsets[event_idx]
                        # Determine end of trial: next onset or end of recording
                        sorted_onsets = onsets[sorted_indices]
                        pos = np.searchsorted(sorted_onsets, onset)
                        if pos + 1 < len(sorted_onsets):
                            next_onset = sorted_onsets[pos + 1]
                        else:
                            next_onset = raw.times[-1] + 1.0  # beyond end
                        
                        start_sample = max(0, int(onset * sfreq))
                        end_sample = min(n_times, int(next_onset * sfreq))
                        if start_sample < end_sample:
                            trial_index_data[0, start_sample:end_sample] = trial_idx
            except Exception:
                pass  # trial_index stays zeros if events can't be parsed

        # Add trial_index as a misc channel
        if "trial_index" not in raw.ch_names:
            info_trial = mne.create_info(
                ch_names=["trial_index"],
                sfreq=sfreq,
                ch_types=["misc"]
            )
            raw_trial = mne.io.RawArray(trial_index_data, info_trial)
            raw.add_channels([raw_trial], force_update_info=True)

        # --- 5. Build eegunity_description ---
        description = {
            "dataset_name": "openneuro-ds004448",
            "dataset_alias": "BMI-HDEEG-motor-imagery",
            "task": "smrbmi",
            "sampling_rate_hz": int(raw.info["sfreq"]),
            "n_channels": len(raw.ch_names),
            "n_eeg_channels": len(mne.pick_types(raw.info, eeg=True, exclude=[])),
            "n_eog_channels": len(mne.pick_types(raw.info, eog=True, exclude=[])),
            "n_misc_channels": len(mne.pick_types(raw.info, misc=True, exclude=[])),
            "channel_names": raw.ch_names,
            "subject_id": subject_id or "unknown",
            "age": age,
            "sex": sex,
            "handedness": handedness,
            "amplifier": amplifier,
            "cap": cap,
            "duration_sec": raw.times[-1] if len(raw.times) > 0 else 0,
            "n_trials": int(trial_index_data.max()) if trial_index_data.max() > 0 else 0,
            "event_codes_present": list(set(raw.annotations.description)) if raw.annotations else [],
            "has_annotations": raw.annotations is not None and len(raw.annotations) > 0,
            "notes": "Sensorimotor rhythm-based BCI with motor imagery. Events loaded from events.tsv with sample-based onsets converted to seconds.",
        }
        
        # Add extra participant info
        description.update(extra_info)
        
        # Store description in raw.info
        raw.info["description"] = json.dumps(description)

        return raw


KERNEL = OpenNeuroDS004448Kernel()