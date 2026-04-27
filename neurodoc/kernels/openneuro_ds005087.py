"""OpenNeuro DS005087 (Robinson et al., 2025) stage1 kernel for EEGUnity.

RSVP Visual Hemifield Presentation dataset: 80 subjects, 63 channels, 1000 Hz.
Rapid serial visual presentation at 5 Hz to left/right/center hemifield.

Source: https://openneuro.org/datasets/ds005087
DOI: https://doi.org/10.1126/sciadv.adq0889
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["ESL", "Handedness", "Total", "age", "gender"]

# Derived misc channels configuration
# Format: list of (channel_name, source_field, description)
# source_field: "events.tsv:<column>" or "<column>" (participants.tsv)
_DERIVED_MISC_CHANNELS_CONFIG = [
    ("correct_response", "events.tsv:correct", "correct response to a target (1) or not (0)"),
    ("response_time", "events.tsv:rt", "time of response, but this isn't accurate"),
]

_DEFAULT_AMPLIFIER = "unknown"
_DEFAULT_CAP = "unknown"

# Channel mapping for BrainVision standard 64-channel layout
# Source: OpenNeuro ds005087 electrode layout; standard 10-10 system with 63 EEG + 1 ref
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_CHANNEL_RENAME_MAP = {
    # BrainVision default names -> standard 10-10 names
    "1": "Fp1",
    "2": "Fp2",
    "3": "F7",
    "4": "F3",
    "5": "Fz",
    "6": "F4",
    "7": "F8",
    "8": "FC5",
    "9": "FC1",
    "10": "FC2",
    "11": "FC6",
    "12": "T7",
    "13": "C3",
    "14": "Cz",
    "15": "C4",
    "16": "T8",
    "17": "TP9",
    "18": "CP5",
    "19": "CP1",
    "20": "CP2",
    "21": "CP6",
    "22": "TP10",
    "23": "P7",
    "24": "P3",
    "25": "Pz",
    "26": "P4",
    "27": "P8",
    "28": "PO9",
    "29": "O1",
    "30": "Oz",
    "31": "O2",
    "32": "PO10",
    "33": "PO7",
    "34": "PO3",
    "35": "POz",
    "36": "PO4",
    "37": "PO8",
    "38": "P9",
    "39": "P5",
    "40": "P1",
    "41": "P2",
    "42": "P6",
    "43": "P10",
    "44": "TP7",
    "45": "CP3",
    "46": "CPz",
    "47": "CP4",
    "48": "TP8",
    "49": "FT7",
    "50": "FC3",
    "51": "FCz",
    "52": "FC4",
    "53": "FT8",
    "54": "F9",
    "55": "F5",
    "56": "F1",
    "57": "F2",
    "58": "F6",
    "59": "F10",
    "60": "AF7",
    "61": "AF3",
    "62": "AF4",
    "63": "AF8",
    "64": "Fpz",
    # Alternative naming patterns (some files may use EEG- prefix)
    "EEG 1": "Fp1",
    "EEG 2": "Fp2",
    "EEG 3": "F7",
    "EEG 4": "F3",
    "EEG 5": "Fz",
    "EEG 6": "F4",
    "EEG 7": "F8",
    "EEG 8": "FC5",
    "EEG 9": "FC1",
    "EEG 10": "FC2",
    "EEG 11": "FC6",
    "EEG 12": "T7",
    "EEG 13": "C3",
    "EEG 14": "Cz",
    "EEG 15": "C4",
    "EEG 16": "T8",
    "EEG 17": "TP9",
    "EEG 18": "CP5",
    "EEG 19": "CP1",
    "EEG 20": "CP2",
    "EEG 21": "CP6",
    "EEG 22": "TP10",
    "EEG 23": "P7",
    "EEG 24": "P3",
    "EEG 25": "Pz",
    "EEG 26": "P4",
    "EEG 27": "P8",
    "EEG 28": "PO9",
    "EEG 29": "O1",
    "EEG 30": "Oz",
    "EEG 31": "O2",
    "EEG 32": "PO10",
    "EEG 33": "PO7",
    "EEG 34": "PO3",
    "EEG 35": "POz",
    "EEG 36": "PO4",
    "EEG 37": "PO8",
    "EEG 38": "P9",
    "EEG 39": "P5",
    "EEG 40": "P1",
    "EEG 41": "P2",
    "EEG 42": "P6",
    "EEG 43": "P10",
    "EEG 44": "TP7",
    "EEG 45": "CP3",
    "EEG 46": "CPz",
    "EEG 47": "CP4",
    "EEG 48": "TP8",
    "EEG 49": "FT7",
    "EEG 50": "FC3",
    "EEG 51": "FCz",
    "EEG 52": "FC4",
    "EEG 53": "FT8",
    "EEG 54": "F9",
    "EEG 55": "F5",
    "EEG 56": "F1",
    "EEG 57": "F2",
    "EEG 58": "F6",
    "EEG 59": "F10",
    "EEG 60": "AF7",
    "EEG 61": "AF3",
    "EEG 62": "AF4",
    "EEG 63": "AF8",
    "EEG 64": "Fpz",
}


def _get_subject_id_from_path(file_path: str) -> str:
    """Extract BIDS subject ID from file path."""
    import re
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith("sub-"):
            return part
    return "unknown"


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to the data file."""
    current_dir = os.path.dirname(file_path)
    for _ in range(5):
        candidate = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    base = file_path.replace("_eeg.eeg", "").replace("_eeg.vhdr", "").replace("_eeg.edf", "").replace("_eeg.set", "")
    candidate = base + "_events.tsv"
    if os.path.exists(candidate):
        return candidate
    
    dir_name = os.path.dirname(file_path)
    file_base = os.path.basename(file_path)
    import re
    m = re.search(r'(sub-[a-zA-Z0-9]+)(?:_ses-[a-zA-Z0-9]+)?(_task-[a-zA-Z0-9]+)', file_base)
    if m:
        sub, task = m.group(1), m.group(2)
        for f in os.listdir(dir_name):
            if f.startswith(f"{sub}") and f.endswith("_events.tsv"):
                return os.path.join(dir_name, f)
    
    return None


def _read_participants_info(participants_tsv: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    result: Dict[str, str] = {}
    
    if not os.path.exists(participants_tsv):
        return {k: "unknown" for k in _REQUIRED_INFO_FIELDS}
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
    except Exception:
        return {k: "unknown" for k in _REQUIRED_INFO_FIELDS}
    
    sub_col = "participant_id"
    if sub_col not in df.columns:
        for col in df.columns:
            if "participant" in col.lower() or "subject" in col.lower():
                sub_col = col
                break
    
    row = df[df[sub_col] == subject_id]
    if row.empty:
        clean_id = subject_id.replace("sub-", "")
        row = df[df[sub_col] == clean_id]
    if row.empty:
        row = df[df[sub_col] == subject_id.replace("sub-", "sub-")]
    
    if row.empty:
        return {k: "unknown" for k in _REQUIRED_INFO_FIELDS}
    
    row = row.iloc[0]
    
    age_val = row.get("age", "unknown")
    if pd.isna(age_val):
        age = "unknown"
    else:
        age = str(int(age_val)) if isinstance(age_val, (int, float)) else str(age_val).strip()
        if not age or age.lower() == "nan":
            age = "unknown"
    
    sex_val = row.get("gender", row.get("sex", "unknown"))
    if pd.isna(sex_val):
        sex = "unknown"
    else:
        sex = str(sex_val).lower().strip()
        if sex in ("f", "female"):
            sex = "female"
        elif sex in ("m", "male"):
            sex = "male"
        else:
            sex = "unknown"
    
    esl = str(row.get("ESL", "unknown"))
    if pd.isna(esl) or not esl.strip() or esl.lower() == "nan":
        esl = "unknown"
    
    handedness = str(row.get("Handedness", "unknown"))
    if pd.isna(handedness) or not handedness.strip() or handedness.lower() == "nan":
        handedness = "unknown"
    
    total = str(row.get("Total", "unknown"))
    if pd.isna(total) or not total.strip() or total.lower() == "nan":
        total = "unknown"
    
    result = {
        "age": age,
        "sex": sex,
        "ESL": esl,
        "Handedness": handedness,
        "Total": total,
    }
    
    for field in _REQUIRED_INFO_FIELDS:
        if field not in result:
            result[field] = "unknown"
    
    return result


def _read_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not os.path.exists(events_tsv):
        return None
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        return df
    except Exception:
        return None


def _build_misc_channels_from_events(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Build derived misc channels from events.tsv data."""
    if events_df is None or events_df.empty:
        return raw
    
    sfreq = raw.info["sfreq"]
    n_times = len(raw.times)
    
    onset_col = "onset"
    if onset_col not in events_df.columns:
        for col in events_df.columns:
            if "onset" in col.lower():
                onset_col = col
                break
    
    if onset_col not in events_df.columns:
        return raw
    
    # For each configured derived channel, check if source column exists
    misc_data = {}
    for ch_name, source_field, _desc in _DERIVED_MISC_CHANNELS_CONFIG:
        if not source_field.startswith("events.tsv:"):
            continue
        col = source_field.split(":", 1)[1]
        if col not in events_df.columns:
            continue
        
        channel_data = np.full(n_times, np.nan)
        
        for _, ev_row in events_df.iterrows():
            onset_sec = ev_row[onset_col]
            if pd.isna(onset_sec):
                continue
            onset_sample = int(round(onset_sec * sfreq))
            if 0 <= onset_sample < n_times:
                val = ev_row[col]
                if not pd.isna(val):
                    # Determine end of stimulus duration if available
                    duration = 0.0
                    if "duration" in events_df.columns:
                        dur_val = ev_row.get("duration", 0.0)
                        if not pd.isna(dur_val):
                            duration = float(dur_val)
                    
                    # For correct_response: handle istarget logic
                    if ch_name == "correct_response":
                        istarget = ev_row.get("istarget", 1)
                        if pd.isna(istarget):
                            istarget = 1
                        if int(istarget) == 0:
                            # Non-target trials: set to NaN (will be forward-filled from previous or left as NaN)
                            # Actually per spec: for non-target trials, set to NaN or exclude
                            # We leave as NaN for this segment, but need to handle carefully
                            # Set NaN for the stim duration, then continue
                            end_sample = min(n_times, int(round((onset_sec + max(duration, 0.2)) * sfreq)))
                            channel_data[onset_sample:end_sample] = np.nan
                            continue
                    
                    # For response_time: handle response=0 trials
                    if ch_name == "response_time":
                        response = ev_row.get("response", 1)
                        if pd.isna(response):
                            response = 1
                        if int(response) == 0:
                            # No response: set to NaN for stim duration
                            end_sample = min(n_times, int(round((onset_sec + max(duration, 0.2)) * sfreq)))
                            channel_data[onset_sample:end_sample] = np.nan
                            continue
                    
                    # Set value from onset to end of stimulus
                    end_sample = min(n_times, int(round((onset_sec + max(duration, 0.2)) * sfreq)))
                    channel_data[onset_sample:end_sample] = float(val)
        
        # Forward-fill NaNs (step function holds last value), but keep leading NaNs as 0
        mask = np.isnan(channel_data)
        if mask.all():
            channel_data[:] = 0.0
        else:
            first_valid = np.where(~mask)[0]
            if len(first_valid) > 0:
                channel_data[:first_valid[0]] = 0.0
                for i in range(first_valid[0] + 1, len(channel_data)):
                    if mask[i]:
                        channel_data[i] = channel_data[i - 1]
        
        misc_data[ch_name] = channel_data.reshape(1, -1)
    
    if not misc_data:
        return raw
    
    # Add channels using MNE idioms: RawArray + raw.add_channels
    for ch_name, data in misc_data.items():
        info = mne.create_info([ch_name], sfreq=sfreq, ch_types=["misc"])
        misc_raw = mne.io.RawArray(data, info, verbose=False)
        raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


def _read_events_as_annotations(raw: mne.io.BaseRaw, events_tsv: str) -> mne.io.BaseRaw:
    """Read events from events.tsv and add as MNE annotations."""
    events_df = _read_events_tsv(events_tsv)
    if events_df is None or events_df.empty:
        return raw
    
    onset_col = "onset"
    if onset_col not in events_df.columns:
        for col in events_df.columns:
            if "onset" in col.lower():
                onset_col = col
                break
    
    duration_col = "duration"
    if duration_col not in events_df.columns:
        for col in events_df.columns:
            if "duration" in col.lower():
                duration_col = col
                break
    
    description_col = "trial_type"
    if description_col not in events_df.columns:
        for col in events_df.columns:
            if "type" in col.lower() or "condition" in col.lower():
                description_col = col
                break
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = row.get(onset_col, np.nan)
        if pd.isna(onset):
            continue
        onsets.append(float(onset))
        
        duration = row.get(duration_col, 0.0)
        if pd.isna(duration):
            duration = 0.0
        durations.append(float(duration))
        
        desc = str(row.get(description_col, "unknown"))
        if pd.isna(desc):
            desc = "unknown"
        descriptions.append(desc)
    
    if onsets:
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        raw.set_annotations(annot)
    
    return raw


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels according to the mapping."""
    rename_map = {}
    for old_name in raw.ch_names:
        if old_name in _CHANNEL_RENAME_MAP:
            rename_map[old_name] = _CHANNEL_RENAME_MAP[old_name]
        # Also check with spaces replaced
        elif old_name.replace(" ", "") in _CHANNEL_RENAME_MAP:
            rename_map[old_name] = _CHANNEL_RENAME_MAP[old_name.replace(" ", "")]
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-10 montage for renamed channels."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, match_case=False, on_missing="warn")
    except Exception:
        pass
    return raw


class DS005087Kernel:
    """Stage1 kernel for OpenNeuro DS005087."""
    
    def __init__(self):
        self.name = "ds005087"
        self.version = "1.0.0"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to a raw EEG file."""
        file_path = row.get("file_path", "")
        if not file_path:
            return raw
        
        # Get subject ID
        subject_id = _get_subject_id_from_path(file_path)
        
        # Read participants info
        participants_tsv = _find_participants_tsv(file_path)
        subject_info = _read_participants_info(participants_tsv, subject_id) if participants_tsv else {k: "unknown" for k in _REQUIRED_INFO_FIELDS}
        
        # Set subject info in raw
        raw.info["subject_info"] = {
            "his_id": subject_id,
            "age": float(subject_info["age"]) if subject_info["age"] != "unknown" else None,
            "sex": 1 if subject_info["sex"] == "male" else (2 if subject_info["sex"] == "female" else 0),
        }
        
        # Rename channels
        raw = _rename_channels(raw)
        
        # Set montage
        raw = _set_montage(raw)
        
        # Find and process events
        events_tsv = _find_events_tsv(file_path)
        if events_tsv:
            # Add events as annotations first
            raw = _read_events_as_annotations(raw, events_tsv)
            
            # Build derived misc channels from events
            events_df = _read_events_tsv(events_tsv)
            if events_df is not None:
                raw = _build_misc_channels_from_events(raw, events_df)
        
        # Build eegunity_description
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": _DEFAULT_AMPLIFIER,
            "cap": _DEFAULT_CAP,
            "handedness": subject_info.get("Handedness", "unknown"),
        }
        
        # Store in raw info
        if raw.info.get("description") is None:
            raw.info["description"] = ""
        raw.info["eegunity_description"] = eegunity_description
        
        return raw


KERNEL = DS005087Kernel()