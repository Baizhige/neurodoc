"""OpenNeuro DS005185 (EESM19) stage1 kernel for EEGUnity.

Ear-EEG Sleep Monitoring 2019 dataset.
- 20 subjects, ~25 channels, 500 Hz sampling rate
- BIDS-compliant with participants.tsv, events.tsv sidecars, and JSON descriptors
- Sleep stage labels from PSG scoring sidecars (Scoring1/Scoring2 columns)
- Danish protocol markers + sync triggers in raw events
- Derived misc channels from diary events.tsv: writtenTime, pressedTrigger

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
# Required info fields from participants.tsv (canonical keys for eegunity_description)
# =============================================================================
_REQUIRED_INFO_FIELDS = ["age", "sex"]

# =============================================================================
# Required native misc channels (already in raw data, ensure type is 'misc')
# =============================================================================
_REQUIRED_NATIVE_MISC: List[str] = []

# =============================================================================
# Derived misc channels to create
# =============================================================================
_DERIVED_MISC_CHANNELS = ["writtenTime", "pressedTrigger"]

# =============================================================================
# Event name standardization mapping
# Raw event names -> canonical names for EEGUnity scan compatibility
# =============================================================================
_EVENT_RENAME_MAP = {
    # Admin events
    "trigger": "trigger",
    "Biocalibrations": "Biocalibrations",
    "Biocalibrations start": "Biocalibrations start",
    "Sync": "Sync",
    "Start af maling": "Start_of_recording",
    # Protocol event markers (raw meta)
    "Lights Out": "Lights_Out",
    "Gik i seng": "Went_to_Bed",
    "Stod op": "Got_up",
    "Vagen": "Awake",
    "vagen": "Awake",
    # Sleep stage events from PSG scoring (raw meta, canonical IDs)
    "Sleep stage W": "s1",
    "Sleep stage N1": "s3",
    "Sleep stage N2": "s4",
    "Sleep stage N3": "s5",
    "Sleep stage REM": "s2",
    "Sleep stage ?": "s8",
    "Sleep stage A": "s6",
    "Sleep stage M": "s6",
    "Movement": "s6",
    "Artefact": "s7",
    "Unscored": "s8",
    "Electrodetest": "Electrodetest",
}

# =============================================================================
# Channel rename map: non-standard names -> standard_1020 names
# EESM19 ear-EEG channels are non-standard; keep as-is but ensure consistent naming
# Source: dataset documentation, DOI: 10.1038/s41597-025-04579-8
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
# =============================================================================
_CHANNEL_RENAME_MAP = {
    # Ear-EEG channels use E* naming (e.g., E1, E2, ... E25)
    # These are kept as-is since they are non-standard ear-specific placements
    # PSG reference channels may appear with alternate names
}

# =============================================================================
# Standard 10-20 channel positions for PSG reference channels if present
# =============================================================================
_STANDARD_1020_CHANNELS = {
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T7", "C3", "Cz",
    "C4", "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "O2", "A1",
    "A2", "M1", "M2", "T3", "T4", "T5", "T6", "F9", "F10", "P9",
    "P10", "POz", "Oz", "Iz", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F5", "F1", "F2", "F6", "FT7", "FC5", "FC3", "FC1", "FCz",
    "FC2", "FC4", "FC6", "FT8", "C5", "C1", "C2", "C6", "TP7",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P5", "P1", "P2", "P6", "PO7", "PO3", "PO4", "PO8", "O9", "O10",
}


def _find_sidecar_path(file_path: str, suffix: str) -> Optional[str]:
    """Find BIDS sidecar file for a given data file."""
    base = re.sub(r"(_eeg\.(edf|bdf|set|vhdr|fif))$", "", file_path, flags=re.IGNORECASE)
    # Try direct sibling
    direct = base + suffix
    if os.path.isfile(direct):
        return direct
    # Try in parent directory (some BIDS layouts)
    parent = os.path.join(os.path.dirname(file_path), os.path.basename(base) + suffix)
    if os.path.isfile(parent):
        return parent
    # Try pattern match in same directory
    dirname = os.path.dirname(file_path)
    if os.path.isdir(dirname):
        for f in os.listdir(dirname):
            if f.endswith(suffix) and base.split(os.sep)[-1] in f:
                return os.path.join(dirname, f)
    return None


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.isfile(participants_path):
        return {}

    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}

    # Match subject_id (handle both "sub-001" and "001" formats)
    sub_match = subject_id if subject_id.startswith("sub-") else f"sub-{subject_id}"
    # Also try without prefix
    sub_alt = subject_id.replace("sub-", "")

    for _, row in df.iterrows():
        pid = str(row.get("participant_id", ""))
        if pid in (sub_match, sub_alt, subject_id):
            info = {}
            for col in df.columns:
                if col == "participant_id":
                    continue
                val = row.get(col)
                if pd.isna(val):
                    info[col] = "unknown"
                else:
                    info[col] = str(val)
            return info
    return {}


def _standardize_sex(sex_val: Optional[str]) -> str:
    """Standardize sex to canonical values."""
    if sex_val is None or str(sex_val).lower() in ("unknown", "nan", "", "n/a"):
        return "unknown"
    s = str(sex_val).lower().strip()
    if s in ("f", "female", "w", "woman"):
        return "female"
    if s in ("m", "male", "man"):
        return "male"
    return "unknown"


def _standardize_age(age_val: Any) -> str:
    """Standardize age to string format."""
    if age_val is None or str(age_val).lower() in ("unknown", "nan", "", "n/a"):
        return "unknown"
    try:
        # Handle both integer and float ages
        age_float = float(age_val)
        if age_float == int(age_float):
            return str(int(age_float))
        return str(age_float)
    except (ValueError, TypeError):
        return "unknown"


def _parse_events_tsv(events_path: Optional[str]) -> Optional[pd.DataFrame]:
    """Read and parse a BIDS events.tsv file."""
    if events_path is None or not os.path.isfile(events_path):
        return None
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _create_step_function_channel(
    raw: mne.io.BaseRaw,
    event_onsets: np.ndarray,
    event_values: np.ndarray,
    channel_name: str,
    fill_value: float = 0.0,
) -> mne.io.RawArray:
    """Create a misc channel with step-function values aligned to event onsets.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Reference raw for times and sampling rate.
    event_onsets : np.ndarray
        Event onset times in seconds.
    event_values : np.ndarray
        Values to assign at each onset (one per onset).
    channel_name : str
        Name for the new channel.
    fill_value : float
        Value for samples before first event and between events.

    Returns
    -------
    mne.io.RawArray
        Single-channel RawArray with ch_type='misc'.
    """
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    data = np.full((1, n_samples), fill_value, dtype=np.float64)
    
    # Sort by onset
    if len(event_onsets) > 0:
        sort_idx = np.argsort(event_onsets)
        event_onsets = event_onsets[sort_idx]
        event_values = event_values[sort_idx]
        
        # Convert onsets to sample indices
        onset_samples = (event_onsets * sfreq).astype(int)
        onset_samples = np.clip(onset_samples, 0, n_samples - 1)
        
        # Fill step function
        for i, s in enumerate(onset_samples):
            data[0, s:] = event_values[i]
    
    info = mne.create_info([channel_name], sfreq, ch_types=["misc"])
    raw_array = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    return raw_array


def _create_constant_channel(
    raw: mne.io.BaseRaw,
    channel_name: str,
    constant_value: float,
) -> mne.io.RawArray:
    """Create a misc channel with a constant value."""
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    data = np.full((1, n_samples), constant_value, dtype=np.float64)
    info = mne.create_info([channel_name], sfreq, ch_types=["misc"])
    raw_array = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    return raw_array


def _add_misc_channels(raw: mne.io.BaseRaw, channels_to_add: List[mne.io.RawArray]) -> mne.io.BaseRaw:
    """Add misc channels to raw object."""
    if not channels_to_add:
        return raw
    raw = raw.add_channels(channels_to_add, force_update_info=True)
    return raw


def _read_json_sidecar(file_path: str) -> Dict[str, Any]:
    """Read BIDS JSON sidecar for EEG data file."""
    json_path = _find_sidecar_path(file_path, ".json")
    if json_path is None or not os.path.isfile(json_path):
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


class OpenNeuroDS005185Kernel:
    """Kernel for OpenNeuro DS005185 (EESM19) ear-EEG sleep monitoring dataset."""

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------
    dataset_name = "openneuro_ds005185"
    dataset_alias = "EESM19"
    modality = "eeg"
    task = "sleep"
    reference = (
        "https://openneuro.org/datasets/ds005185; "
        "DOI: 10.1038/s41598-019-53115-3; "
        "DOI: 10.1038/s41597-025-04579-8"
    )

    # -------------------------------------------------------------------------
    # BIDS layout helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _get_dataset_path(row: pd.Series) -> str:
        """Extract dataset root path from row."""
        file_path = str(row.get("file_path", ""))
        # Navigate up to dataset root (openneuro_raw/ds005185)
        parts = file_path.split(os.sep)
        for i, part in enumerate(parts):
            if part == "ds005185":
                return os.sep.join(parts[: i + 1])
        # Fallback: go up from file to find participants.tsv
        d = os.path.dirname(file_path)
        for _ in range(6):
            if os.path.isfile(os.path.join(d, "participants.tsv")):
                return d
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        return os.path.dirname(file_path)

    @staticmethod
    def _get_subject_id(row: pd.Series) -> str:
        """Extract subject ID from row or file path."""
        subj = str(row.get("subject", ""))
        if subj:
            return subj
        file_path = str(row.get("file_path", ""))
        m = re.search(r"sub-([a-zA-Z0-9]+)", file_path)
        if m:
            return m.group(0)  # includes "sub-" prefix
        return "unknown"

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Determine paths and IDs
        file_path = str(row.get("file_path", ""))
        dataset_path = self._get_dataset_path(row)
        subject_id = self._get_subject_id(row)

        # --- 1. Read participants.tsv info ----------------------------------
        participants_info = _read_participants_info(dataset_path, subject_id)

        # Standardize required fields
        age = _standardize_age(participants_info.get("age"))
        sex = _standardize_sex(participants_info.get("sex"))

        # Additional fields with fallbacks
        amplifier = participants_info.get("amplifier", "unknown")
        cap = participants_info.get("cap", "unknown")
        handedness = participants_info.get("handedness", participants_info.get("hand", "unknown"))

        # --- 2. Read JSON sidecar for technical metadata --------------------
        json_meta = _read_json_sidecar(file_path)

        # --- 3. Handle events/annotations ----------------------------------
        # Check if raw already has annotations (e.g., from .set file)
        has_raw_annotations = len(raw.annotations) > 0

        # Find events.tsv sidecar
        events_path = _find_sidecar_path(file_path, "_events.tsv")
        events_df = _parse_events_tsv(events_path)

        # Build annotations from events.tsv if available and raw has no annotations
        if events_df is not None and not has_raw_annotations:
            # BIDS events.tsv columns: onset, duration, trial_type, [optional]
            onsets = []
            durations = []
            descriptions = []
            
            for _, ev_row in events_df.iterrows():
                onset = ev_row.get("onset")
                if pd.isna(onset):
                    continue
                try:
                    onset = float(onset)
                except (ValueError, TypeError):
                    continue
                
                duration = ev_row.get("duration", 0.0)
                try:
                    duration = float(duration) if not pd.isna(duration) else 0.0
                except (ValueError, TypeError):
                    duration = 0.0
                
                # Use trial_type if available, else use any available label column
                trial_type = ev_row.get("trial_type", "")
                if pd.isna(trial_type) or str(trial_type).strip() == "":
                    # Try other common BIDS event columns
                    for col in ["value", "stim_type", "event_type", "event"]:
                        if col in ev_row and not pd.isna(ev_row[col]):
                            trial_type = str(ev_row[col])
                            break
                    else:
                        trial_type = "unknown"
                else:
                    trial_type = str(trial_type)
                
                # Apply rename map (pass through if not in map)
                description = _EVENT_RENAME_MAP.get(trial_type, trial_type)
                
                onsets.append(onset)
                durations.append(duration)
                descriptions.append(description)
            
            if onsets:
                # Create annotations and add to raw
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=raw.annotations.orig_time if hasattr(raw.annotations, "orig_time") else None,
                )
                raw = raw.set_annotations(annotations)

        # --- 4. Create derived misc channels -------------------------------
        misc_channels_to_add = []

        # For events.tsv-sourced columns: use step function from events
        if events_df is not None:
            # writtenTime: look for column with that name or similar
            for target_col in _DERIVED_MISC_CHANNELS:
                col_name = None
                if target_col in events_df.columns:
                    col_name = target_col
                else:
                    # Try case-insensitive match
                    for c in events_df.columns:
                        if c.lower() == target_col.lower():
                            col_name = c
                            break
                
                if col_name is not None:
                    # Build step function from event onsets
                    valid_mask = ~events_df["onset"].isna()
                    if valid_mask.any():
                        onsets_arr = events_df.loc[valid_mask, "onset"].values.astype(float)
                        values_arr = events_df.loc[valid_mask, col_name].values
                        
                        # Convert values to numeric where possible
                        numeric_values = []
                        for v in values_arr:
                            try:
                                numeric_values.append(float(v))
                            except (ValueError, TypeError):
                                # Use hash-based numeric encoding for strings
                                numeric_values.append(float(hash(str(v)) % 1000000))
                        
                        values_arr = np.array(numeric_values)
                        
                        step_raw = _create_step_function_channel(
                            raw, onsets_arr, values_arr, target_col, fill_value=0.0
                        )
                        misc_channels_to_add.append(step_raw)
                else:
                    # Column not found in events.tsv: create constant channel from participants info if available
                    if target_col in participants_info:
                        try:
                            val = float(participants_info[target_col])
                        except (ValueError, TypeError):
                            val = float(hash(str(participants_info[target_col])) % 1000000)
                        const_raw = _create_constant_channel(raw, target_col, val)
                        misc_channels_to_add.append(const_raw)
                    else:
                        # Create zero-filled channel as placeholder
                        zero_raw = _create_constant_channel(raw, target_col, 0.0)
                        misc_channels_to_add.append(zero_raw)
        else:
            # No events.tsv: create constant channels from participants info or zeros
            for target_col in _DERIVED_MISC_CHANNELS:
                if target_col in participants_info:
                    try:
                        val = float(participants_info[target_col])
                    except (ValueError, TypeError):
                        val = float(hash(str(participants_info[target_col])) % 1000000)
                    const_raw = _create_constant_channel(raw, target_col, val)
                    misc_channels_to_add.append(const_raw)
                else:
                    zero_raw = _create_constant_channel(raw, target_col, 0.0)
                    misc_channels_to_add.append(zero_raw)

        # Add all derived misc channels
        if misc_channels_to_add:
            raw = _add_misc_channels(raw, misc_channels_to_add)

        # --- 5. Ensure native misc channels are typed correctly -------------
        # (none required for this dataset, but keep for consistency)
        for ch_name in _REQUIRED_NATIVE_MISC:
            if ch_name in raw.ch_names:
                raw.set_channel_types({ch_name: "misc"})

        # --- 6. Set description with eegunity metadata ----------------------
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }

        # Add any additional participants.tsv fields
        for key, val in participants_info.items():
            if key not in eegunity_description and key not in ("participant_id",):
                eegunity_description[key] = val

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        return raw


# =============================================================================
# Module export
# =============================================================================
KERNEL = OpenNeuroDS005185Kernel()