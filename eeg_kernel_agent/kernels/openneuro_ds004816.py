"""OpenNeuro ds004816 stage1 kernel for EEGUnity.

EEG Attention RSVP Experiment investigating neural dynamics of prioritizing
task-relevant information using stimuli composed of small letters on large objects.

Source: https://openneuro.org/datasets/ds004816
Reference: DOI 10.51628/001c.21174
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


# Required info fields from participants.tsv
# Source: kernel requirements
_REQUIRED_INFO_FIELDS: List[str] = ["age", "gender", "native_speaker"]

# Required derived misc channels with their source fields
# Source: kernel requirements
_REQUIRED_DERIVED_MISC: List[Dict[str, str]] = [
    {"name": "response_time", "source_field": "events.tsv:rt"},
    {"name": "trial_correct", "source_field": "events.tsv:correct"},
    {"name": "object_stim_id", "source_field": "events.tsv:objectstimnumber"},
]

# Native misc channels that must exist as 'misc' type
# Source: kernel requirements
_REQUIRED_NATIVE_MISC: List[str] = []


def _get_participant_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read participant info from participants.tsv.

    Returns a dict with required info fields. Missing fields use "unknown".
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {field: "unknown" for field in _REQUIRED_INFO_FIELDS}

    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {field: "unknown" for field in _REQUIRED_INFO_FIELDS}

    # Match subject_id (e.g., "sub-01" or "01")
    sub_match = subject_id.replace("sub-", "") if subject_id.startswith("sub-") else subject_id
    sub_id_col = "participant_id"

    # Try exact match first
    row = df[df[sub_id_col] == subject_id]
    if row.empty:
        # Try without "sub-" prefix
        row = df[df[sub_id_col] == f"sub-{sub_match}"]
    if row.empty:
        # Try with just the number
        row = df[df[sub_id_col] == sub_match]

    if row.empty:
        return {field: "unknown" for field in _REQUIRED_INFO_FIELDS}

    info = {}
    for field in _REQUIRED_INFO_FIELDS:
        if field in row.columns:
            val = row[field].values[0]
            # Handle missing/NaN values
            if pd.isna(val):
                info[field] = "unknown"
            else:
                info[field] = str(val).strip()
        else:
            info[field] = "unknown"

    return info


def _get_events_tsv_path(file_path: str) -> Optional[str]:
    """Get the corresponding events.tsv path for a given EEG file."""
    # BIDS naming: sub-XX_task-YY_run-ZZ_eeg.<ext> -> sub-XX_task-YY_run-ZZ_events.tsv
    # Or: sub-XX_task-YY_eeg.<ext> -> sub-XX_task-YY_events.tsv
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)

    # Remove extension
    base_no_ext = re.sub(r'_eeg\.[^.]+$', '', basename)
    if base_no_ext == basename:
        # Try alternative pattern
        base_no_ext = re.sub(r'\.[^.]+$', '', basename)

    events_path = os.path.join(dirname, f"{base_no_ext}_events.tsv")
    if os.path.exists(events_path):
        return events_path

    # Try without run suffix
    base_no_run = re.sub(r'_run-\d+', '', base_no_ext)
    events_path = os.path.join(dirname, f"{base_no_run}_events.tsv")
    if os.path.exists(events_path):
        return events_path

    # Search in directory for matching events.tsv
    if os.path.exists(dirname):
        for fname in os.listdir(dirname):
            if fname.endswith("_events.tsv"):
                # Check if subject and task match
                if base_no_ext.split('_')[0] in fname and 'task-' in fname:
                    return os.path.join(dirname, fname)

    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not events_path or not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 naming.

    This dataset uses standard 10-20 channel names with possible prefixes.
    Source: analysis.md indicates 63 channels at 1000 Hz, typical for standard caps.
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing_names = list(raw.ch_names)

    # Common non-standard prefixes to strip
    prefixes = ["EEG ", "EEG-", "A", "B"]

    for ch_name in existing_names:
        # Skip if already standard
        # Check against standard 10-20 names (case-insensitive)
        if _is_standard_1020(ch_name):
            continue

        # Try stripping prefixes
        cleaned = ch_name
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break

        # Handle specific known mappings
        if cleaned.startswith("0") and cleaned.isdigit():
            # Numeric channels - map based on position if known
            continue

        # Check if cleaned name is standard
        if _is_standard_1020(cleaned) and cleaned != ch_name:
            rename_map[ch_name] = cleaned

    return rename_map


def _is_standard_1020(name: str) -> bool:
    """Check if a channel name follows standard 10-20 convention."""
    standard_names = {
        "Fp1", "Fpz", "Fp2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
        "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
        "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
        "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "Iz",
        # Extended 10-10
        "AF9", "AF5", "AF10",
        "F9", "F3a", "F4a", "F10",
        "FT9", "FT10",
        "T9", "T10",
        "TP9", "TP10",
        "P9", "P10",
        "PO9", "PO5", "PO6", "PO10",
        "I1", "I2",
    }
    return name in standard_names


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    basename = os.path.basename(file_path)
    match = re.search(r'(sub-[0-9]+)', basename)
    if match:
        return match.group(1)
    # Try without "sub-" prefix
    match = re.search(r'([0-9]{2,})', basename)
    if match:
        return match.group(1)
    return "unknown"


def _normalize_sex(sex_str: str) -> str:
    """Normalize sex string to required format."""
    sex_lower = sex_str.lower().strip()
    if sex_lower in ("m", "male", "1"):
        return "male"
    elif sex_lower in ("f", "female", "2"):
        return "female"
    else:
        return "unknown"


def _create_events_derived_misc_channel(raw: mne.io.BaseRaw, events_df: pd.DataFrame, 
                                        column: str, channel_name: str) -> Optional[mne.io.RawArray]:
    """Create a derived misc channel from events.tsv data with trial-locked step function.
    
    For each event in events_df, creates a step function that updates the channel value
    at each annotation onset and holds that value until the next event onset or end of data.
    """
    if events_df is None or events_df.empty:
        return None
    
    if column not in events_df.columns:
        return None
    
    sfreq = raw.info["sfreq"]
    n_times = raw.n_times
    times = raw.times
    
    # Initialize with NaN
    data = np.full((1, n_times), np.nan, dtype=np.float64)
    
    # Get event onsets and values
    onsets = events_df["onset"].values.astype(float)
    values = events_df[column].values
    
    # Handle NaN values in the column
    valid_mask = ~pd.isna(values)
    onsets = onsets[valid_mask]
    values = values[valid_mask]
    
    if len(onsets) == 0:
        return None
    
    # Sort by onset
    sort_idx = np.argsort(onsets)
    onsets = onsets[sort_idx]
    values = values[sort_idx]
    
    # Apply special derivation rules based on channel name
    if channel_name == "response_time":
        # Compute response time relative to stimulus onset (rt - time_stimon)
        # Need time_stimon column, or use onset as proxy
        if "time_stimon" in events_df.columns:
            time_stimon = events_df["time_stimon"].values.astype(float)[valid_mask][sort_idx]
            values = values - time_stimon
        # else keep rt as-is (already relative to something)
    elif channel_name == "object_stim_id":
        # Use object stimulus number when > 0, else NaN
        values = np.where(values > 0, values, np.nan)
        # Re-filter NaNs after this operation
        valid_after = ~np.isnan(values)
        onsets = onsets[valid_after]
        values = values[valid_after]
        if len(onsets) == 0:
            return None
    
    # Build step function: for each time point, find the most recent event onset
    # and use its value
    sample_onsets = np.round(onsets * sfreq).astype(int)
    sample_onsets = np.clip(sample_onsets, 0, n_times - 1)
    
    # Create step function using sample indices
    current_val = np.nan
    prev_sample = 0
    for i, samp in enumerate(sample_onsets):
        current_val = values[i]
        if not np.isnan(current_val):
            data[0, prev_sample:samp] = current_val if i == 0 else data[0, prev_sample]
            prev_sample = samp
    
    # Fill from last event to end
    if not np.isnan(current_val) and prev_sample < n_times:
        data[0, prev_sample:] = current_val
    
    # Forward-fill any remaining NaNs at the start
    # Find first valid value
    first_valid = np.where(~np.isnan(data[0]))[0]
    if len(first_valid) > 0:
        data[0, :first_valid[0]] = data[0, first_valid[0]]
    
    # Ensure finite values (replace any remaining NaN with 0, though there shouldn't be any)
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Create info for misc channel
    info = mne.create_info(
        ch_names=[channel_name],
        sfreq=sfreq,
        ch_types=["misc"],
    )
    
    raw_misc = mne.io.RawArray(data, info, first_samp=raw.first_samp, verbose=False)
    return raw_misc


@dataclass
class OpenNeuroDS004816Kernel:
    """Stage1 kernel for OpenNeuro ds004816 dataset."""

    KERNEL_ID: str = "openneuro-ds004816-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Determine dataset path
        dataset_path = getattr(udataset, "dataset_path", None)
        if not dataset_path:
            # Infer from file path
            parts = file_path.split(os.sep)
            for i, part in enumerate(parts):
                if part.startswith("ds004816") or "openneuro" in part.lower():
                    dataset_path = os.sep.join(parts[:i+1])
                    break
        if not dataset_path:
            dataset_path = os.path.dirname(os.path.dirname(file_path))

        # Extract subject ID
        subject_id = _extract_subject_id(file_path)

        # Get participant info from participants.tsv
        participant_info = _get_participant_info(dataset_path, subject_id)

        # Build eegunity_description
        # age: always string
        age_str = participant_info.get("age", "unknown")
        if age_str != "unknown":
            # Ensure it's a clean string
            try:
                float(age_str)
                age_str = str(int(float(age_str)))
            except ValueError:
                age_str = "unknown"

        # sex: lowercase male/female/unknown
        sex_raw = participant_info.get("gender", "unknown")
        sex_str = _normalize_sex(sex_raw)

        # amplifier and cap: unknown for this dataset (no device info in BIDS)
        # LLM 推断，需人类复核
        amplifier_str = "unknown"  # LLM 推断，需人类复核 - no device info in BIDS sidecars
        cap_str = "unknown"  # LLM 推断，需人类复核 - standard cap assumed but not specified

        # handedness: not in participants.tsv, check if available
        handedness_str = "unknown"  # LLM 推断，需人类复核 - not in required fields

        # Build extra info from participants.tsv
        extra_info = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in participant_info and field not in ("age", "gender"):
                extra_info[field] = participant_info[field]

        # Handle native_speaker specifically
        native_speaker = participant_info.get("native_speaker", "unknown")
        extra_info["native_speaker"] = native_speaker

        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age_str,
                "sex": sex_str,
                "amplifier": amplifier_str,
                "cap": cap_str,
                "handedness": handedness_str,
                "native_speaker": native_speaker,
                "extra_info": extra_info,
            },
        }

        # Set description as JSON string
        raw.info["description"] = json.dumps(description_dict, ensure_ascii=False)

        # Load events from events.tsv and set as annotations
        # The BrainVision .eeg file has no native triggers; events must come from events.tsv
        events_path = _get_events_tsv_path(file_path)
        events_df = _read_events_tsv(events_path)

        if events_df is not None and not events_df.empty:
            # Use 'condition' column as the event label since it carries distinguishable values
            # (0, 1, etc. representing different experimental conditions)
            # If 'condition' is not available or all identical, fall back to other columns
            if "condition" in events_df.columns and events_df["condition"].nunique() > 1:
                labels = events_df["condition"].astype(str)
            elif "trial_type" in events_df.columns:
                labels = events_df["trial_type"].astype(str)
            else:
                # Default: use eventnumber or row index as label
                labels = events_df.get("eventnumber", events_df.index).astype(str)

            onsets = events_df["onset"].values.astype(float)
            durations = events_df["duration"].values.astype(float)

            # Handle any NaN values
            valid_mask = ~(np.isnan(onsets) | np.isnan(durations))
            onsets = onsets[valid_mask]
            durations = durations[valid_mask]
            labels = labels[valid_mask]

            # Create annotations
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=labels.values,
                orig_time=raw.info.get("meas_date"),
            )

            # Set annotations on raw
            raw.set_annotations(annotations)

        # Create derived misc channels from events.tsv
        misc_channels_to_add = []
        for derived_spec in _REQUIRED_DERIVED_MISC:
            name = derived_spec["name"]
            source_field = derived_spec["source_field"]
            
            # Parse source_field: expect "events.tsv:<column>"
            if not source_field.startswith("events.tsv:"):
                continue
            
            column = source_field.split(":", 1)[1]
            
            # Create the derived misc channel
            misc_raw = _create_events_derived_misc_channel(raw, events_df, column, name)
            if misc_raw is not None:
                misc_channels_to_add.append(misc_raw)
        
        # Add all derived misc channels to raw
        if misc_channels_to_add:
            raw = raw.add_channels(misc_channels_to_add, force_update_info=True)
            # Ensure channel types are set to misc
            for misc_raw in misc_channels_to_add:
                for ch_name in misc_raw.ch_names:
                    if ch_name in raw.ch_names:
                        raw.set_channel_types({ch_name: "misc"})

        return raw


KERNEL = OpenNeuroDS004816Kernel()