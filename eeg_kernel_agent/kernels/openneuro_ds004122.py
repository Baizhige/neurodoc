"""Dataset-specific kernel for openneuro ds004122 (BCIT Speed Control).

BCIT (Brain Cognition and Innovative Technology) dataset.
BCIT Speed Control: fatigue study with manual/auto speed control.

74-channel BioSemi ActiveTwo at 1024 Hz.
Standard 10-20 layout with BioSemi naming convention.

Event code structure (from task-Drive_events.json):
  1111: Start of left perturbation
  1112: End of left perturbation
  1121: Start of right perturbation
  1122: End of right perturbation
  1211: Steer left
  1212: Steer right
  2621: Auto speed control on
  2622: Auto speed control off
  3111: Perturbation onset
  3112: Perturbation response
  3200: Speed control state marker
  3310: Performance metric event
  4210: Vehicle moves into lane
  4220: Vehicle moves into right lane
  4230: Vehicle moves into left lane
  4311: Driver starts correcting lane position
  4312: Driver has completed the lane position correction
  4411: Rare event
  4421: Rare event

Source: https://openneuro.org/datasets/ds004122
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# BioSemi ActiveTwo 74-channel standard naming
# Source: BioSemi 64+10-20 layout documentation; standard cap configuration
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_BIOSEMI_74_CHANNELS = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2",
    "EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8",
    "GSR1", "GSR2", "Erg1", "Erg2"
]

# Standard 10-20 mapping for common BioSemi channel names
# Source: standard_1020 montage in MNE
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_CHANNEL_RENAME_MAP = {
    # EXG channels are typically EOG/EMG references
    "EXG1": "EOG1",
    "EXG2": "EOG2",
    "EXG3": "EOG3",
    "EXG4": "EOG4",
    "EXG5": "EMG1",
    "EXG6": "EMG2",
    "EXG7": "EMG3",
    "EXG8": "EMG4",
    # GSR and Erg stay as misc
    "GSR1": "GSR1",
    "GSR2": "GSR2",
    "Erg1": "Erg1",
    "Erg2": "Erg2",
}


def _get_events_tsv_path(file_path: str) -> Optional[str]:
    """Get the path to the corresponding events.tsv file."""
    # BIDS naming: sub-XX_ses-YY_task-Task_run-ZZ_eeg.ext
    # events file: sub-XX_ses-YY_task-Task_run-ZZ_events.tsv
    base = file_path.split("_eeg.")[0]
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    # Try without run
    parts = base.split("_")
    for i, part in enumerate(parts):
        if part.startswith("run-"):
            base_no_run = "_".join(parts[:i] + parts[i+1:])
            events_path_alt = base_no_run + "_events.tsv"
            if os.path.exists(events_path_alt):
                return events_path_alt
    return None


def _get_participants_tsv_path(file_path: str) -> Optional[str]:
    """Get the path to participants.tsv from file path."""
    # Navigate up to dataset root
    dir_path = os.path.dirname(file_path)
    for _ in range(10):  # reasonable depth limit
        candidate = os.path.join(dir_path, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(dir_path)
        if parent == dir_path:
            break
        dir_path = parent
    return None


def _parse_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    basename = os.path.basename(file_path)
    if basename.startswith("sub-"):
        parts = basename.split("_")
        for part in parts:
            if part.startswith("sub-"):
                return part
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for this subject
        sub_col = "participant_id"
        if sub_col not in df.columns:
            # Try alternatives
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    sub_col = col
                    break
        
        # Match subject ID
        subject_rows = df[df[sub_col] == subject_id]
        if len(subject_rows) == 0:
            # Try without "sub-" prefix
            subject_rows = df[df[sub_col] == subject_id.replace("sub-", "")]
        if len(subject_rows) == 0:
            return {}
        
        row = subject_rows.iloc[0]
        info = {}
        for col in df.columns:
            if col != sub_col and pd.notna(row[col]):
                info[col] = str(row[col])
        return info
    except Exception:
        return {}


def _compute_median_age_group(all_years: List[int], subject_year: int) -> int:
    """Compute age group by median split."""
    ages = [2022 - y for y in all_years if y is not None and not pd.isna(y)]
    if len(ages) == 0:
        return -1
    median_age = np.median(ages)
    subject_age = 2022 - subject_year
    return 0 if subject_age < median_age else 1


@dataclass
class OpenNeuroDS004122Kernel:
    """Stage1 kernel for openneuro ds004122 (BCIT Speed Control)."""

    KERNEL_ID: str = "openneuro-ds004122-stage1"
    
    # Cache for participants data to avoid repeated reads
    _participants_cache: Dict[str, pd.DataFrame] = field(default_factory=dict)
    _age_group_cache: Dict[str, int] = field(default_factory=dict)

    def _get_participants_df(self, participants_path: str) -> pd.DataFrame:
        """Get cached participants dataframe."""
        if participants_path not in self._participants_cache:
            self._participants_cache[participants_path] = pd.read_csv(
                participants_path, sep="\t"
            )
        return self._participants_cache[participants_path]

    def _compute_all_age_groups(self, participants_path: str) -> Dict[str, int]:
        """Precompute age groups for all subjects."""
        if participants_path in self._age_group_cache:
            return {"_global": self._age_group_cache[participants_path]}
        
        df = self._get_participants_df(participants_path)
        
        # Find year_of_birth column
        yob_col = None
        for col in df.columns:
            if "year" in col.lower() and "birth" in col.lower():
                yob_col = col
                break
        if yob_col is None:
            for col in df.columns:
                if "age" in col.lower() or "birth" in col.lower():
                    yob_col = col
                    break
        
        if yob_col is None or yob_col not in df.columns:
            return {}
        
        # Parse years
        years = []
        for val in df[yob_col]:
            try:
                if pd.notna(val):
                    years.append(int(float(val)))
            except (ValueError, TypeError):
                pass
        
        # Compute age groups for each subject
        age_groups = {}
        for _, row in df.iterrows():
            sub_id = row.get("participant_id", "")
            if pd.isna(sub_id):
                continue
            try:
                y = int(float(row[yob_col]))
                age_groups[str(sub_id)] = _compute_median_age_group(years, y)
            except (ValueError, TypeError):
                age_groups[str(sub_id)] = -1
        
        # Cache global median for subjects not found
        if len(years) > 0:
            median_age = np.median([2022 - y for y in years])
            self._age_group_cache[participants_path] = 0  # default
        else:
            self._age_group_cache[participants_path] = -1
        
        return age_groups

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        subject_id = _parse_subject_id(file_path)
        
        # Get participants info
        participants_path = _get_participants_tsv_path(file_path)
        participants_info = {}
        if participants_path and subject_id:
            participants_info = _read_participants_info(participants_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participants_info.get("age", participants_info.get("year_of_birth", "")),
            "sex": participants_info.get("sex", participants_info.get("gender", "")),
            "amplifier": participants_info.get("amplifier", "BioSemi ActiveTwo"),
            "cap": participants_info.get("cap", "BioSemi 64+10-20"),
            "handedness": participants_info.get("handedness", participants_info.get("hand", "")),
        }
        
        # Set description as JSON string
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Read events.tsv and add annotations if available
        # The events.tsv has columns: onset, duration, sample, value
        # We must use the "value" column for event descriptions, not "trial_type"
        # The "value" column contains the numeric event codes like 1111, 1211, etc.
        events_path = _get_events_tsv_path(file_path)
        if events_path and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                if "onset" in events_df.columns and "value" in events_df.columns:
                    onsets = events_df["onset"].values.astype(float)
                    # Handle duration: n/a or missing -> 0
                    if "duration" in events_df.columns:
                        durations = events_df["duration"].values
                        # Replace n/a, NaN, or non-numeric with 0
                        durations_clean = []
                        for d in durations:
                            try:
                                if pd.isna(d) or str(d).lower() in ('n/a', 'na', 'nan', ''):
                                    durations_clean.append(0.0)
                                else:
                                    durations_clean.append(float(d))
                            except (ValueError, TypeError):
                                durations_clean.append(0.0)
                        durations = np.array(durations_clean)
                    else:
                        durations = np.zeros(len(onsets))
                    # Use "value" column for descriptions (literal strings, no remapping per HC-5)
                    descriptions = events_df["value"].astype(str).values
                    # Remove existing annotations to avoid duplicates
                    raw.set_annotations(mne.Annotations(onset=onsets, duration=durations, description=descriptions))
            except Exception:
                pass
        
        # Create derived misc channels from participants.tsv info (constant broadcast)
        misc_channels = {
            "perturbation_to_correction_latency": float(participants_info.get("perturbation_to_correction_latency", 0)) if "perturbation_to_correction_latency" in participants_info else 0.0,
            "correction_duration": float(participants_info.get("correction_duration", 0)) if "correction_duration" in participants_info else 0.0,
            "time_into_session": float(participants_info.get("time_into_session", 0)) if "time_into_session" in participants_info else 0.0,
            "proactive_reactive_index": float(participants_info.get("proactive_reactive_index", 0)) if "proactive_reactive_index" in participants_info else 0.0,
        }
        
        # If not in participants, try to get from events.tsv columns (trial-locked step function)
        if events_path and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                for ch_name in ["perturbation_to_correction_latency", "correction_duration", "time_into_session", "proactive_reactive_index"]:
                    if ch_name in events_df.columns:
                        # Create step function aligned to event onsets
                        data = np.zeros((1, len(raw.times)))
                        if "onset" in events_df.columns:
                            sfreq = raw.info["sfreq"]
                            for _, ev_row in events_df.iterrows():
                                onset_sample = int(ev_row["onset"] * sfreq)
                                if onset_sample < len(raw.times):
                                    val = float(ev_row[ch_name]) if pd.notna(ev_row[ch_name]) else 0.0
                                    data[0, onset_sample:] = val
                        # Add as misc channel
                        info = mne.create_info([ch_name], sfreq=raw.info["sfreq"], ch_types=["misc"])
                        raw = raw.add_channels([mne.io.RawArray(data, info, first_samp=raw.first_samp)], force_update_info=True)
            except Exception:
                pass
        
        # Add constant misc channels from participants info
        for ch_name, val in misc_channels.items():
            if val != 0.0:
                data = np.full((1, len(raw.times)), val)
                info = mne.create_info([ch_name], sfreq=raw.info["sfreq"], ch_types=["misc"])
                raw = raw.add_channels([mne.io.RawArray(data, info, first_samp=raw.first_samp)], force_update_info=True)
        
        # Set channel types for known non-EEG channels
        channel_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            if upper.startswith("EXG") or upper in ["EOG1", "EOG2", "EOG3", "EOG4", "EMG1", "EMG2", "EMG3", "EMG4"]:
                if any(x in upper for x in ["EOG", "EXG1", "EXG2", "EXG3", "EXG4"]):
                    channel_types[ch_name] = "eog"
                else:
                    channel_types[ch_name] = "emg"
            elif upper.startswith("GSR") or upper.startswith("ERG"):
                channel_types[ch_name] = "misc"
        
        if channel_types:
            raw.set_channel_types(channel_types)
        
        # Rename channels to standard names if possible
        rename_map = {}
        for ch_name in raw.ch_names:
            if ch_name in _CHANNEL_RENAME_MAP:
                rename_map[ch_name] = _CHANNEL_RENAME_MAP[ch_name]
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard montage for EEG channels
        eeg_ch_names = [ch for ch in raw.ch_names if ch not in 
                       ["EOG1", "EOG2", "EOG3", "EOG4", "EMG1", "EMG2", "EMG3", "EMG4",
                        "GSR1", "GSR2", "Erg1", "Erg2"] + 
                       [f"EXG{i}" for i in range(1, 9)] +
                       ["perturbation_to_correction_latency", "correction_duration", 
                        "time_into_session", "proactive_reactive_index"]]
        
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Check if channels match montage
            montage_chs = set(montage.ch_names)
            raw_eeg_chs = set(eeg_ch_names)
            if raw_eeg_chs.issubset(montage_chs) or len(raw_eeg_chs & montage_chs) > 0:
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        return raw


KERNEL = OpenNeuroDS004122Kernel()