"""OpenNeuro DS005185 (EESM19) stage1 kernel for EEGUnity.

Ear-EEG Sleep Monitoring 2019 dataset.
- 20 subjects, ~25 channels, 500 Hz sampling rate
- BIDS-compliant with participants.tsv, events.tsv sidecars, and JSON descriptors
- Sleep stage labels from PSG scoring sidecars (Scoring1/Scoring2 columns)
- Danish protocol markers + sync triggers in raw events
- Derived misc channels: writtenTime_numeric, pressedTrigger_numeric (from diary events.tsv)

Source: https://openneuro.org/datasets/ds005185
       DOI: 10.1038/s41598-019-53115-3
       DOI: 10.1038/s41597-025-04579-8
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
# Required info fields from participants.tsv
# =============================================================================
_REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness"]

# =============================================================================
# Required native misc channels (already in raw data, ensure type is 'misc')
# =============================================================================
_REQUIRED_NATIVE_MISC: List[str] = []

# =============================================================================
# Derived misc channels to create
# =============================================================================
_DERIVED_MISC_CHANNELS = ["writtenTime_numeric", "pressedTrigger_numeric"]

# =============================================================================
# Sleep stage mapping from scoring files (Scoring1/Scoring2 columns)
# s1=Wake, s2=REM, s3=N1, s4=N2, s5=N3, s6=A, s7=Artefact, s8=Unscored
# =============================================================================
_SCORING_STAGE_MAP = {
    "s1": "Sleep stage W",
    "s2": "Sleep stage REM",
    "s3": "Sleep stage N1",
    "s4": "Sleep stage N2",
    "s5": "Sleep stage N3",
    "s6": "Sleep stage A",
    "s7": "Artefact",
    "s8": "Unscored",
}

# =============================================================================
# Event name standardization mapping for raw events from events.tsv
# =============================================================================
_EVENT_RENAME_MAP = {
    # Admin events
    "trigger": "trigger",
    "Biocalibrations": "Biocalibrations",
    "Biocalibrations start": "Biocalibrations start",
    "Sync": "Sync",
    "Start af maling": "Start af måling",
    # Protocol event markers (raw meta)
    "Lights Out": "Lights Out",
    "Gik i seng": "Gik i seng",
    "Stod op": "Stod op",
    "Vagen": "Vagen",
    "vagen": "Vagen",
}

# =============================================================================
# Numeric event codes for events without string descriptions
# These appear in some BIDS events.tsv files as numeric codes
# =============================================================================
_NUMERIC_EVENT_MAP = {
    "4": "event_4",
    "5": "event_5",
    "6": "event_6",
    "7": "event_7",
    "8": "event_8",
    "9": "event_9",
}


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'sub-([0-9a-zA-Z]+)', file_path)
    if match:
        return match.group(1)
    return None


def _get_session_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS session ID from file path."""
    match = re.search(r'ses-([0-9a-zA-Z]+)', file_path)
    if match:
        return match.group(1)
    return None


def _find_bids_root(file_path: str) -> str:
    """Find BIDS root directory from file path."""
    # Walk up until we find participants.tsv or dataset_description.json
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at root
        if os.path.exists(os.path.join(current_dir, "participants.tsv")) or \
           os.path.exists(os.path.join(current_dir, "dataset_description.json")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    # Fallback: go up 4 levels from typical BIDS path sub-XX/ses-XX/eeg/
    current_dir = os.path.dirname(os.path.abspath(file_path))
    for _ in range(4):
        current_dir = os.path.dirname(current_dir)
        if os.path.exists(os.path.join(current_dir, "participants.tsv")):
            return current_dir
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(file_path)))))


def _read_participants_tsv(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(bids_root, "participants.tsv")
    result = {}
    
    if not os.path.exists(participants_path):
        return result
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for this subject
        subj_col = "participant_id"
        if subj_col not in df.columns:
            return result
        
        # Handle subject ID format (with or without "sub-" prefix)
        search_ids = [f"sub-{subject_id}", subject_id]
        for search_id in search_ids:
            mask = df[subj_col] == search_id
            if mask.any():
                row = df[mask].iloc[0]
                for field in _REQUIRED_INFO_FIELDS:
                    if field in row:
                        val = row[field]
                        if pd.isna(val):
                            result[field] = "unknown"
                        else:
                            result[field] = str(val).strip()
                    else:
                        result[field] = "unknown"
                # Include any extra fields present in participants.tsv
                for col in df.columns:
                    if col not in [subj_col] + _REQUIRED_INFO_FIELDS:
                        val = row.get(col, "unknown")
                        if pd.isna(val):
                            result[col] = "unknown"
                        else:
                            result[col] = str(val).strip()
                break
    except Exception:
        pass
    
    # Ensure required fields exist
    for field in _REQUIRED_INFO_FIELDS:
        if field not in result:
            result[field] = "unknown"
    
    return result


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex value to canonical form."""
    sex_lower = sex_val.lower().strip()
    if sex_lower in ("f", "female"):
        return "female"
    elif sex_lower in ("m", "male"):
        return "male"
    else:
        return "unknown"


def _normalize_age(age_val: str) -> str:
    """Normalize age value to string."""
    try:
        # Try to parse as number and return as string
        float_age = float(age_val)
        return str(int(float_age))
    except (ValueError, TypeError):
        return "unknown"


def _parse_written_time(time_str: str) -> float:
    """Parse Danish time string like '23.05' to decimal hours."""
    try:
        time_str = str(time_str).strip().replace(",", ".")
        if ":" in time_str:
            parts = time_str.split(":")
            hours = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0
            return hours + minutes / 60.0
        elif "." in time_str:
            parts = time_str.split(".")
            hours = float(parts[0])
            # Check if it's already decimal hours or hours.minutes
            if len(parts[1]) <= 2:
                # Could be hours.minutes format
                minutes = float(parts[1])
                if minutes < 60:
                    return hours + minutes / 60.0
                else:
                    # It's decimal hours
                    return float(time_str)
            else:
                return float(time_str)
        else:
            return float(time_str)
    except (ValueError, TypeError):
        return np.nan


def _find_events_tsv(file_path: str, subject_id: str, session_id: Optional[str] = None) -> Optional[str]:
    """Find events.tsv file for the given recording."""
    bids_root = _find_bids_root(file_path)
    eeg_dir = os.path.dirname(os.path.abspath(file_path))
    
    # Search order: same directory, then subject/session hierarchy
    search_paths = []
    
    # Same directory as the .set file
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    search_paths.append(os.path.join(eeg_dir, f"{base_name}_events.tsv"))
    search_paths.append(os.path.join(eeg_dir, "events.tsv"))
    
    # Subject-specific events in eeg directory
    if session_id:
        search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", f"sub-{subject_id}_ses-{session_id}_events.tsv"))
        search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", "events.tsv"))
    search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", "eeg", f"sub-{subject_id}_events.tsv"))
    search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", "eeg", "events.tsv"))
    
    # Diary events (for writtenTime_numeric, pressedTrigger_numeric)
    if session_id:
        search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", f"sub-{subject_id}_ses-{session_id}_diary_events.tsv"))
        search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", "diary_events.tsv"))
    search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", "eeg", f"sub-{subject_id}_diary_events.tsv"))
    search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", "eeg", "diary_events.tsv"))
    
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    return None


def _find_diary_events_tsv(file_path: str, subject_id: str, session_id: Optional[str] = None) -> Optional[str]:
    """Find diary events.tsv file for derived misc channels."""
    bids_root = _find_bids_root(file_path)
    eeg_dir = os.path.dirname(os.path.abspath(file_path))
    
    search_paths = []
    
    # Diary events in same directory
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    search_paths.append(os.path.join(eeg_dir, f"{base_name}_diary_events.tsv"))
    search_paths.append(os.path.join(eeg_dir, "diary_events.tsv"))
    
    # Subject/session hierarchy
    if session_id:
        search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", f"sub-{subject_id}_ses-{session_id}_diary_events.tsv"))
        search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", "diary_events.tsv"))
    search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", "eeg", f"sub-{subject_id}_diary_events.tsv"))
    search_paths.append(os.path.join(bids_root, f"sub-{subject_id}", "eeg", "diary_events.tsv"))
    
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return pd.DataFrame()


def _read_scoring_file(bids_root: str, subject_id: str, session_id: Optional[str] = None) -> pd.DataFrame:
    """Read sleep scoring file for subject."""
    search_paths = []
    
    if session_id:
        search_paths.extend([
            os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", f"sub-{subject_id}_ses-{session_id}_scoring.tsv"),
            os.path.join(bids_root, f"sub-{subject_id}", f"ses-{session_id}", "eeg", "scoring.tsv"),
        ])
    
    search_paths.extend([
        os.path.join(bids_root, f"sub-{subject_id}", "eeg", f"sub-{subject_id}_scoring.tsv"),
        os.path.join(bids_root, f"sub-{subject_id}", "eeg", "scoring.tsv"),
        os.path.join(bids_root, "scoring", f"sub-{subject_id}_scoring.tsv"),
    ])
    
    for path in search_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, sep="\t")
                return df
            except Exception:
                continue
    
    return pd.DataFrame()


def _load_diary_data(diary_path: str) -> Dict[str, Any]:
    """Load diary events and extract writtenTime_numeric and pressedTrigger_numeric values."""
    result = {
        "writtenTime_numeric": np.nan,
        "pressedTrigger_numeric": np.nan,
    }
    
    try:
        df = pd.read_csv(diary_path, sep="\t")
        
        # Look for writtenTime column
        for col in df.columns:
            col_lower = col.lower().replace(" ", "_")
            if "writtentime" in col_lower or "written_time" in col_lower:
                # Get the first non-null value
                for val in df[col]:
                    if pd.notna(val):
                        parsed = _parse_written_time(str(val))
                        if not np.isnan(parsed):
                            result["writtenTime_numeric"] = parsed
                            break
            
            if "pressedtrigger" in col_lower or "pressed_trigger" in col_lower or "trigger" in col_lower:
                for val in df[col]:
                    if pd.notna(val):
                        try:
                            result["pressedTrigger_numeric"] = float(str(val).strip())
                            break
                        except (ValueError, TypeError):
                            continue
        
        # Also check standard BIDS event columns
        if "trial_type" in df.columns:
            for _, row in df.iterrows():
                trial_type = str(row.get("trial_type", "")).lower()
                if "writtentime" in trial_type or "written_time" in trial_type:
                    for resp_col in ["response_time", "value", "writtenTime", "written_time"]:
                        if resp_col in row and pd.notna(row[resp_col]):
                            parsed = _parse_written_time(str(row[resp_col]))
                            if not np.isnan(parsed):
                                result["writtenTime_numeric"] = parsed
                                break
                elif "pressedtrigger" in trial_type or "pressed_trigger" in trial_type:
                    for resp_col in ["response_time", "value", "pressedTrigger", "pressed_trigger"]:
                        if resp_col in row and pd.notna(row[resp_col]):
                            try:
                                result["pressedTrigger_numeric"] = float(str(row[resp_col]).strip())
                                break
                            except (ValueError, TypeError):
                                continue
    except Exception:
        pass
    
    return result


def _add_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add annotations from events.tsv DataFrame to raw object."""
    if events_df.empty:
        return raw
    
    onsets = []
    durations = []
    descriptions = []
    
    # Required columns for BIDS events.tsv
    if "onset" not in events_df.columns:
        return raw
    
    for _, row in events_df.iterrows():
        onset = row.get("onset")
        if pd.isna(onset):
            continue
        
        try:
            onset = float(onset)
        except (ValueError, TypeError):
            continue
        
        # Duration (default to 0 if not present)
        duration = row.get("duration", 0)
        try:
            duration = float(duration) if pd.notna(duration) else 0.0
        except (ValueError, TypeError):
            duration = 0.0
        
        # Description from trial_type or value column
        description = None
        if "trial_type" in row and pd.notna(row["trial_type"]):
            description = str(row["trial_type"]).strip()
        elif "value" in row and pd.notna(row["value"]):
            description = str(row["value"]).strip()
        
        # Map numeric events and standardize names
        if description:
            # Check numeric map first
            if description in _NUMERIC_EVENT_MAP:
                description = _NUMERIC_EVENT_MAP[description]
            # Check rename map
            elif description in _EVENT_RENAME_MAP:
                description = _EVENT_RENAME_MAP[description]
            # Keep original if no mapping
            
            onsets.append(onset)
            durations.append(duration)
            descriptions.append(description)
    
    if onsets:
        # Create annotations, filtering out any that exceed recording length
        sfreq = raw.info["sfreq"]
        n_times = raw.n_times
        valid_mask = [(o < n_times / sfreq) for o in onsets]
        
        onsets = [o for o, m in zip(onsets, valid_mask) if m]
        durations = [d for d, m in zip(durations, valid_mask) if m]
        descriptions = [d for d, m in zip(descriptions, valid_mask) if m]
        
        if onsets:
            new_annot = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
            
            # Combine with existing annotations
            if raw.annotations:
                raw.set_annotations(raw.annotations + new_annot)
            else:
                raw.set_annotations(new_annot)
    
    return raw


def _add_sleep_stage_annotations(raw: mne.io.BaseRaw, scoring_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add sleep stage annotations from scoring DataFrame."""
    if scoring_df.empty:
        return raw
    
    onsets = []
    durations = []
    descriptions = []
    
    # Determine column names for scoring
    onset_col = None
    for col in ["onset", "time", "start"]:
        if col in scoring_df.columns:
            onset_col = col
            break
    
    duration_col = None
    for col in ["duration", "dur", "length"]:
        if col in scoring_df.columns:
            duration_col = col
            break
    
    stage_col = None
    for col in ["Scoring1", "Scoring2", "stage", "label", "trial_type", "value"]:
        if col in scoring_df.columns:
            stage_col = col
            break
    
    if onset_col is None or stage_col is None:
        return raw
    
    for _, row in scoring_df.iterrows():
        onset = row.get(onset_col)
        if pd.isna(onset):
            continue
        
        try:
            onset = float(onset)
        except (ValueError, TypeError):
            continue
        
        duration = row.get(duration_col, 30.0)  # Default 30s epoch
        try:
            duration = float(duration) if pd.notna(duration) else 30.0
        except (ValueError, TypeError):
            duration = 30.0
        
        stage = str(row.get(stage_col, "")).strip().lower()
        
        # Map stage
        stage_mapped = _SCORING_STAGE_MAP.get(stage, f"Sleep stage {stage.upper()}" if stage else "Unknown")
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(stage_mapped)
    
    if onsets:
        sfreq = raw.info["sfreq"]
        n_times = raw.n_times
        valid_mask = [(o < n_times / sfreq) for o in onsets]
        
        onsets = [o for o, m in zip(onsets, valid_mask) if m]
        durations = [d for d, m in zip(durations, valid_mask) if m]
        descriptions = [d for d, m in zip(descriptions, valid_mask) if m]
        
        if onsets:
            new_annot = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
            
            if raw.annotations:
                raw.set_annotations(raw.annotations + new_annot)
            else:
                raw.set_annotations(new_annot)
    
    return raw


def _create_misc_channel(raw: mne.io.BaseRaw, name: str, value: float) -> mne.io.BaseRaw:
    """Create a misc-type channel with constant broadcast value."""
    data = np.full((1, len(raw.times)), value, dtype=np.float64)
    
    # Create info for new channel
    new_info = mne.create_info(
        ch_names=[name],
        sfreq=raw.info["sfreq"],
        ch_types=["misc"],
    )
    
    # Create RawArray
    new_raw = mne.io.RawArray(data, new_info, verbose=False)
    
    # Add to existing raw
    raw.add_channels([new_raw], force_update_info=True)
    
    return raw


def _ensure_native_misc_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Ensure required native channels are marked as 'misc' type."""
    if not _REQUIRED_NATIVE_MISC:
        return raw
    
    # Get current channel types
    current_types = raw.get_channel_types()
    
    # Map channel names to their desired types
    channel_type_map = {}
    for ch_name in _REQUIRED_NATIVE_MISC:
        if ch_name in raw.ch_names:
            channel_type_map[ch_name] = "misc"
    
    if channel_type_map:
        raw.set_channel_types(channel_type_map)
    
    return raw


class OpenNeuroDS005185Kernel:
    KERNEL_ID = "openneuro_ds005185"
    DATASET_NAME = "OpenNeuro DS005185 (EESM19)"
    DATASET_DESCRIPTION = "Ear-EEG Sleep Monitoring 2019 dataset with sleep stage scoring"

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract file path and subject info
        file_path = str(row.get("file_path", row.get("path", "")))
        subject_id = _get_subject_id_from_path(file_path)
        
        if subject_id is None:
            # Fallback: try to get from row
            subject_id = str(row.get("subject", "unknown")).replace("sub-", "")
        
        session_id = _get_session_id_from_path(file_path)
        
        # Find BIDS root
        bids_root = _find_bids_root(file_path)
        
        # Read participants.tsv for subject info
        participant_info = _read_participants_tsv(bids_root, subject_id)
        
        # Normalize fields
        age = _normalize_age(participant_info.get("age", "unknown"))
        sex = _normalize_sex(participant_info.get("sex", "unknown"))
        amplifier = participant_info.get("amplifier", "unknown")
        cap = participant_info.get("cap", "unknown")
        handedness = participant_info.get("handedness", "unknown")
        
        # Build eegunity_description
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add any extra participant fields
        for key, val in participant_info.items():
            if key not in eegunity_description:
                eegunity_description[key] = val
        
        # Store original description
        original_description = raw.info.get("description", "")
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Ensure native misc channels
        raw = _ensure_native_misc_channels(raw)
        
        # Find and process events.tsv
        events_path = _find_events_tsv(file_path, subject_id, session_id)
        if events_path:
            events_df = _read_events_tsv(events_path)
            raw = _add_annotations_from_events_tsv(raw, events_df)
        
        # Find and process scoring file for sleep stages
        scoring_df = _read_scoring_file(bids_root, subject_id, session_id)
        if not scoring_df.empty:
            raw = _add_sleep_stage_annotations(raw, scoring_df)
        
        # Create derived misc channels from diary events
        diary_data = {
            "writtenTime_numeric": np.nan,
            "pressedTrigger_numeric": np.nan,
        }
        
        diary_path = _find_diary_events_tsv(file_path, subject_id, session_id)
        if diary_path:
            diary_data = _load_diary_data(diary_path)
        
        # Add derived misc channels
        for ch_name in _DERIVED_MISC_CHANNELS:
            value = diary_data.get(ch_name, np.nan)
            if np.isnan(value):
                value = 0.0  # Default for missing diary data
            raw = _create_misc_channel(raw, ch_name, value)
        
        return raw


KERNEL = OpenNeuroDS005185Kernel()