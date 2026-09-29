"""OpenNeuro DS003838 stage1 kernel for EEGUnity.

Digit span working memory task with EEG, pupillometry, ECG and PPG recordings.
BIDS-compliant dataset with EDF files, participants.tsv, and events.tsv sidecars.

Source: https://openneuro.org/datasets/ds003838/versions/1.0.0
Paper: DOI 10.1038/s41597-022-01414-2 (Scientific Data)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: DOI 10.1038/s41597-022-01414-2, Table 1 - EEG acquisition details
# Annotator: Human, 2026-04-08
_AMPLIFIER = "BrainAmp"  # Brain Products amplifier
_CAP = "Ag/AgCl"  # Standard EEG cap

# Standard 10-20 system channel names for 64-channel EEG
# Source: DOI 10.1038/s41597-022-01414-2 - confirms 64-channel EEG montage
# Annotator: Human, 2026-04-08
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
]

# Required info fields from participants.tsv
# Source: Kernel Requirements v2 task synthesizer
# Annotator: Human, 2026-04-08
_REQUIRED_INFO_FIELDS = [
    "EEG_excluded", "NASA_cog_1", "NASA_dissap_1", "NASA_effort_1",
    "NASA_perf_1", "NASA_phys_1", "age", "eye", "hand", "sex"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map to standardize channel names to 10-20 system.

    Handles various naming conventions that may appear in raw data.
    Source: DOI 10.1038/s41597-022-01414-2
    Annotator: Human, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Common alias patterns for 10-20 system channels
    alias_groups = [
        ("Fp1", ["Fp1", "FP1", "fp1"]),
        ("Fp2", ["Fp2", "FP2", "fp2"]),
        ("Fpz", ["Fpz", "FPz", "fpz"]),
        ("F7", ["F7", "F07"]),
        ("F3", ["F3", "F03"]),
        ("Fz", ["Fz", "Fz"]),
        ("F4", ["F4", "F04"]),
        ("F8", ["F8", "F08"]),
        ("T7", ["T7", "T07", "T7"]),
        ("C3", ["C3", "C03"]),
        ("Cz", ["Cz", "Cz"]),
        ("C4", ["C4", "C04"]),
        ("T8", ["T8", "T08", "T8"]),
        ("P7", ["P7", "P07"]),
        ("P3", ["P3", "P03"]),
        ("Pz", ["Pz", "Pz"]),
        ("P4", ["P4", "P04"]),
        ("P8", ["P8", "P08"]),
        ("O1", ["O1", "O01"]),
        ("Oz", ["Oz", "Oz"]),
        ("O2", ["O2", "O02"]),
        ("FC1", ["FC1", "FC01"]),
        ("FC2", ["FC2", "FC02"]),
        ("FC3", ["FC3", "FC03"]),
        ("FC4", ["FC4", "FC04"]),
        ("FC5", ["FC5", "FC05"]),
        ("FC6", ["FC6", "FC06"]),
        ("FCz", ["FCz", "FCz"]),
        ("CP1", ["CP1", "CP01"]),
        ("CP2", ["CP2", "CP02"]),
        ("CP3", ["CP3", "CP03"]),
        ("CP4", ["CP4", "CP04"]),
        ("CP5", ["CP5", "CP05"]),
        ("CP6", ["CP6", "CP06"]),
        ("CPz", ["CPz", "CPz"]),
        ("POz", ["POz", "POz"]),
        ("PO3", ["PO3", "PO03"]),
        ("PO4", ["PO4", "PO04"]),
        ("PO7", ["PO7", "PO07"]),
        ("PO8", ["PO8", "PO08"]),
        ("AFz", ["AFz", "AFz"]),
        ("AF3", ["AF3", "AF03"]),
        ("AF4", ["AF4", "AF04"]),
        ("AF7", ["AF7", "AF07"]),
        ("AF8", ["AF8", "AF08"]),
        ("F1", ["F1", "F01"]),
        ("F2", ["F2", "F02"]),
        ("F5", ["F5", "F05"]),
        ("F6", ["F6", "F06"]),
        ("F9", ["F9", "F09"]),
        ("F10", ["F10", "F010"]),
        ("FT9", ["FT9", "FT09"]),
        ("FT10", ["FT10", "FT010"]),
        ("FT7", ["FT7", "FT07"]),
        ("FT8", ["FT8", "FT08"]),
        ("C1", ["C1", "C01"]),
        ("C2", ["C2", "C02"]),
        ("C5", ["C5", "C05"]),
        ("C6", ["C6", "C06"]),
        ("T9", ["T9", "T09"]),
        ("T10", ["T10", "T010"]),
        ("TP9", ["TP9", "TP09"]),
        ("TP10", ["TP10", "TP010"]),
        ("TP7", ["TP7", "TP07"]),
        ("TP8", ["TP8", "TP08"]),
        ("P1", ["P1", "P01"]),
        ("P2", ["P2", "P02"]),
        ("P5", ["P5", "P05"]),
        ("P6", ["P6", "P06"]),
        ("P9", ["P9", "P09"]),
        ("P10", ["P10", "P010"]),
        ("PO1", ["PO1", "PO01"]),
        ("PO2", ["PO2", "PO02"]),
        ("PO5", ["PO5", "PO05"]),
        ("PO6", ["PO6", "PO06"]),
        ("PO9", ["PO9", "PO09"]),
        ("PO10", ["PO10", "PO010"]),
        ("I1", ["I1", "I01"]),
        ("I2", ["I2", "I02"]),
        ("Iz", ["Iz", "Iz"]),
    ]

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv relative to a data file."""
    # Walk up from file directory looking for participants.tsv
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # stop at root
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info: Dict[str, str] = {}
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for this subject
        subj_rows = df[df["participant_id"] == subject_id]
        if len(subj_rows) == 0:
            # Try without "sub-" prefix
            subj_rows = df[df["participant_id"] == subject_id.replace("sub-", "")]
        if len(subj_rows) > 0:
            row = subj_rows.iloc[0]
            for field in _REQUIRED_INFO_FIELDS:
                if field in row:
                    val = row[field]
                    # Convert to string, handle NaN
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
                else:
                    info[field] = "unknown"
        else:
            for field in _REQUIRED_INFO_FIELDS:
                info[field] = "unknown"
    except Exception:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv for a given EEG file."""
    # BIDS naming: sub-XX_task-YY_eeg.edf -> sub-XX_task-YY_events.tsv
    # Handle various EEG file extensions
    base = file_path
    for ext in [".edf", ".bdf", ".set", ".vhdr", ".eeg"]:
        if base.endswith(ext):
            # Replace the extension with nothing, then handle suffix
            base_no_ext = base[:-len(ext)]
            # Check for _eeg suffix pattern
            if base_no_ext.endswith("_eeg"):
                base = base_no_ext[:-4] + "_events.tsv"
            elif base_no_ext.endswith("_ecg"):
                base = base_no_ext[:-4] + "_events.tsv"
            else:
                base = base_no_ext + "_events.tsv"
            break
    else:
        # No recognized extension, just try appending
        base = base + "_events.tsv"

    if os.path.exists(base):
        return base

    # Try alternative: same directory, replace _eeg with _events
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # Remove extension
    name_no_ext = os.path.splitext(file_name)[0]
    if name_no_ext.endswith("_eeg"):
        alt_name = name_no_ext[:-4] + "_events.tsv"
    else:
        alt_name = name_no_ext + "_events.tsv"
    alt_path = os.path.join(dir_name, alt_name)
    if os.path.exists(alt_path):
        return alt_path

    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events from events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        # Required BIDS columns
        if "onset" not in df.columns or "duration" not in df.columns:
            return None
        return df
    except Exception:
        return None


def _add_events_as_annotations(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Add events from events.tsv as annotations to raw."""
    if events_df is None or len(events_df) == 0:
        return raw

    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float)
    # Use trial_type if available, otherwise use empty string
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].fillna("").astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].fillna("").astype(str).values
    else:
        descriptions = np.array([""] * len(events_df))

    # Create annotations
    annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
    raw.set_annotations(annot)
    return raw


def _add_misc_channels(raw: mne.io.BaseRaw, info: Dict[str, str]) -> mne.io.BaseRaw:
    """Add required misc channels from participants.tsv info."""
    # Create misc channels for each required info field
    sfreq = raw.info["sfreq"]
    n_times = raw.n_times

    misc_data = []
    misc_names = []
    misc_types = []

    for field in _REQUIRED_INFO_FIELDS:
        val = info.get(field, "unknown")
        # Try to convert to numeric, otherwise use 0
        try:
            numeric_val = float(val)
        except (ValueError, TypeError):
            numeric_val = 0.0

        # Create constant channel
        data = np.full((1, n_times), numeric_val)
        misc_data.append(data)
        misc_names.append(field)
        misc_types.append("misc")

    if len(misc_data) == 0:
        return raw

    # Create new info for misc channels
    misc_info = mne.create_info(ch_names=misc_names, sfreq=sfreq, ch_types=misc_types)
    misc_raw = mne.io.RawArray(np.concatenate(misc_data, axis=0), misc_info)

    # Add to raw
    raw.add_channels([misc_raw], force_update_info=True)
    return raw


class OpenNeuroDS003838Kernel:
    """Stage-1 kernel for OpenNeuro ds003838."""

    KERNEL_ID = "openneuro_ds003838"

    def __init__(self):
        self.dataset_id = "ds003838"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row
        file_path = row.get("File Path", "")
        if not file_path and hasattr(row, "get"):
            # Try alternative column names
            for col in ["file_path", "filepath", "path"]:
                if col in row:
                    file_path = row[col]
                    break

        # Get subject ID
        subject_id = _get_subject_id_from_path(file_path)
        if not subject_id:
            subject_id = "unknown"

        # Read participants info
        participants_path = _find_participants_tsv(file_path)
        if participants_path:
            info = _read_participants_info(participants_path, subject_id)
        else:
            info = {field: "unknown" for field in _REQUIRED_INFO_FIELDS}

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        eegunity_description = {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": info.get("hand", "unknown"),
        }

        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        # Rename channels to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for known non-EEG channels
        # ECG, PPG, pupillometry channels if present
        ecg_patterns = ["ECG", "EKG", "ecg", "ekg"]
        eog_patterns = ["EOG", "eog", "HEOG", "VEOG", "heog", "veog"]
        emg_patterns = ["EMG", "emg"]
        misc_patterns = ["PPG", "ppg", "pupil", "Pupil", "GSR", "gsr", "RESP", "resp"]

        for ch_name in raw.ch_names:
            if any(pat in ch_name for pat in ecg_patterns):
                raw.set_channel_types({ch_name: "ecg"})
            elif any(pat in ch_name for pat in eog_patterns):
                raw.set_channel_types({ch_name: "eog"})
            elif any(pat in ch_name for pat in emg_patterns):
                raw.set_channel_types({ch_name: "emg"})
            elif any(pat in ch_name for pat in misc_patterns):
                raw.set_channel_types({ch_name: "misc"})

        # Add events from events.tsv
        events_path = _find_events_tsv(file_path)
        if events_path:
            events_df = _read_events_tsv(events_path)
            if events_df is not None:
                raw = _add_events_as_annotations(raw, events_df)

        # Add misc channels for participants info
        raw = _add_misc_channels(raw, info)

        return raw


KERNEL = OpenNeuroDS003838Kernel()