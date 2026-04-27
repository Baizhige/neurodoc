"""openneuro_ds004902 stage1 kernel for EEGUnity.

Resting-State EEG Dataset for Sleep Deprivation.
- 71 subjects, 218 files, 61 channels, 500 Hz
- BrainVision format (.vhdr/.eeg/.vmrk)
- Sessions: normal sleep (NS) and 24-hour sleep deprivation (SD)
- Recording types: eyes-open and eyes-closed
- 5-minute continuous blocks

Source: https://openneuro.org/datasets/ds004902
DOI: 10.1038/s41597-024-03268-2
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


# Source: dataset README / published paper (DOI 10.1038/s41597-024-03268-2)
# Standard 10-20 61-channel system with EOG.  LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "Fpz": "Fpz",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FCz": "FCz",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "T7": "T7",
    "C5": "C5",
    "C3": "C3",
    "C1": "C1",
    "Cz": "Cz",
    "C2": "C2",
    "C4": "C4",
    "C6": "C6",
    "T8": "T8",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CPz": "CPz",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    "P7": "P7",
    "P5": "P5",
    "P3": "P3",
    "P1": "P1",
    "Pz": "Pz",
    "P2": "P2",
    "P4": "P4",
    "P6": "P6",
    "P8": "P8",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "AF9": "AF9",
    "AF7": "AF7",
    "AF5": "AF5",
    "AF3": "AF3",
    "AFz": "AFz",
    "AF4": "AF4",
    "AF6": "AF6",
    "AF8": "AF8",
    "AF10": "AF10",
    "EOG-left": "EOG-left",
    "EOG-right": "EOG-right",
    "EOG-central": "EOG-central",
}

# Standard 10-20 EEG channels for montage.
# Source: dataset publication (DOI 10.1038/s41597-024-03268-2).  LLM 推断，需人类复核
_STANDARD_EEG_CHANNELS: List[str] = [
    "Fp1", "Fp2", "Fpz",
    "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
]

# Admin system markers to exclude from annotations.
_ADMIN_MARKERS = {"S 44", "S 45", "S 55", "S 66", "S119"}

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = [
    "ATQ_NS", "ATQ_SD", "Age", "Buss_Perry", "EQ", "Gender",
    "KSS_NS", "KSS_SD", "PANAS_N_NS", "PANAS_N_SD", "PANAS_P_NS", "PANAS_P_SD",
    "PSQI_GlobalScore", "PVT_item1_NS", "PVT_item1_SD", "PVT_item2_NS", "PVT_item2_SD",
    "SAI_NS", "SAI_SD", "SSS_NS", "SSS_SD", "SessionOrder",
]

# Derived misc channels specification: (name, source_column, ns_column)
# source_column and ns_column are in participants.tsv
_DERIVED_MISC_SPEC = [
    ("PVT_RT_change", "PVT_item2_SD", "PVT_item2_NS"),
    ("PANAS_P_change", "PANAS_P_SD", "PANAS_P_NS"),
    ("PANAS_N_change", "PANAS_N_SD", "PANAS_N_NS"),
    ("KSS_change", "KSS_SD", "KSS_NS"),
]


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-([a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _get_session_from_path(file_path: str) -> Optional[str]:
    """Extract session (normal or sleepdeprived) from file path."""
    if "ses-sleepdeprived" in file_path or "ses-sleepdep" in file_path:
        return "sleep_deprived"
    elif "ses-normal" in file_path:
        return "normal"
    return None


def _get_eyes_condition_from_path(file_path: str) -> Optional[str]:
    """Extract eyes condition from file path."""
    fname = os.path.basename(file_path).lower()
    if "eyesopen" in fname or "eyes_open" in fname:
        return "eyes_open"
    elif "eyesclosed" in fname or "eyes_closed" in fname:
        return "eyes_closed"
    return None


def _read_participants_tsv(dataset_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from dataset root."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return None


def _get_participant_info(df: Optional[pd.DataFrame], subject_id: str) -> Dict[str, str]:
    """Get participant info from participants.tsv DataFrame."""
    info: Dict[str, str] = {}
    if df is None:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
        return info

    # BIDS subject IDs may have 'sub-' prefix in the file but not in the tsv
    sub_id_clean = subject_id.replace("sub-", "")
    
    # Try matching with or without 'sub-' prefix
    row = df[df["participant_id"] == f"sub-{sub_id_clean}"]
    if row.empty:
        row = df[df["participant_id"] == sub_id_clean]
    
    if row.empty:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
        return info

    row = row.iloc[0]
    for field in _REQUIRED_INFO_FIELDS:
        if field in row.index:
            val = row[field]
            if pd.isna(val):
                info[field] = "unknown"
            else:
                info[field] = str(val)
        else:
            info[field] = "unknown"

    return info


def _compute_derived_misc_values(info: Dict[str, str]) -> Dict[str, Optional[float]]:
    """Compute derived misc channel values from participant info."""
    derived: Dict[str, Optional[float]] = {}

    # PVT_RT_change = PVT_item2_SD - PVT_item2_NS
    try:
        pvt_ns = info.get("PVT_item2_NS", "unknown")
        pvt_sd = info.get("PVT_item2_SD", "unknown")
        if pvt_ns != "unknown" and pvt_sd != "unknown":
            derived["PVT_RT_change"] = float(pvt_sd) - float(pvt_ns)
        else:
            derived["PVT_RT_change"] = None
    except (ValueError, TypeError):
        derived["PVT_RT_change"] = None

    # PANAS_P_change = PANAS_P_SD - PANAS_P_NS
    try:
        panas_p_ns = info.get("PANAS_P_NS", "unknown")
        panas_p_sd = info.get("PANAS_P_SD", "unknown")
        if panas_p_ns != "unknown" and panas_p_sd != "unknown":
            derived["PANAS_P_change"] = float(panas_p_sd) - float(panas_p_ns)
        else:
            derived["PANAS_P_change"] = None
    except (ValueError, TypeError):
        derived["PANAS_P_change"] = None

    # PANAS_N_change = PANAS_N_SD - PANAS_N_NS
    try:
        panas_n_ns = info.get("PANAS_N_NS", "unknown")
        panas_n_sd = info.get("PANAS_N_SD", "unknown")
        if panas_n_ns != "unknown" and panas_n_sd != "unknown":
            derived["PANAS_N_change"] = float(panas_n_sd) - float(panas_n_ns)
        else:
            derived["PANAS_N_change"] = None
    except (ValueError, TypeError):
        derived["PANAS_N_change"] = None

    # KSS_change = KSS_SD - KSS_NS
    try:
        kss_ns = info.get("KSS_NS", "unknown")
        kss_sd = info.get("KSS_SD", "unknown")
        if kss_ns != "unknown" and kss_sd != "unknown":
            derived["KSS_change"] = float(kss_sd) - float(kss_ns)
        else:
            derived["KSS_change"] = None
    except (ValueError, TypeError):
        derived["KSS_change"] = None

    return derived


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar for a given EEG file."""
    base = file_path.replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    
    # Try alternative naming
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    fname_base = fname.replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "")
    events_path = os.path.join(dir_path, fname_base + "_events.tsv")
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    
    return None


def _create_events_from_events_tsv(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.Annotations:
    """Create MNE Annotations from events.tsv DataFrame."""
    onset = []
    duration = []
    description = []
    
    for _, row in events_df.iterrows():
        if "onset" in row:
            onset.append(float(row["onset"]))
        else:
            continue
            
        if "duration" in row:
            dur = row["duration"]
            if pd.isna(dur):
                duration.append(0.0)
            else:
                duration.append(float(dur))
        else:
            duration.append(0.0)
            
        if "trial_type" in row:
            description.append(str(row["trial_type"]))
        elif "value" in row:
            description.append(str(row["value"]))
        else:
            description.append("unknown")
    
    return mne.Annotations(onset=onset, duration=duration, description=description)


def _add_derived_misc_channels(raw: mne.io.BaseRaw, derived_values: Dict[str, Optional[float]]) -> mne.io.BaseRaw:
    """Add derived misc channels to raw. Skip channels with None or non-finite values."""
    for ch_name in _DERIVED_MISC_CHANNELS:
        value = derived_values.get(ch_name, None)
        if value is None or not np.isfinite(value):
            continue
        
        data = np.full((1, len(raw.times)), value)
        info = mne.create_info([ch_name], raw.info["sfreq"], ch_types=["misc"])
        raw_add = mne.io.RawArray(data, info)
        raw = raw.add_channels([raw_add], force_update_info=True)
    
    return raw


@dataclass
class OpenneuroDs004902Kernel:
    KERNEL_ID: str = "openneuro_ds004902"
    DATASET_NAME: str = "openneuro_ds004902"
    DATASET_PATH: str = "openneuro/ds004902"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_root = udataset.dataset_path
        
        # Get subject info
        subject_id = _get_subject_id_from_path(file_path)
        session = _get_session_from_path(file_path)
        eyes_condition = _get_eyes_condition_from_path(file_path)
        
        # Read participants.tsv
        participants_df = _read_participants_tsv(dataset_root)
        participant_info = _get_participant_info(participants_df, subject_id or "")
        
        # Compute derived misc values
        derived_values = _compute_derived_misc_values(participant_info)
        
        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_description = {
            "age": participant_info.get("Age", "unknown"),
            "sex": participant_info.get("Gender", "unknown"),
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
            "session": session or "unknown",
            "eyes_condition": eyes_condition or "unknown",
            "subject_id": subject_id or "unknown",
        }
        
        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Handle events/annotations
        events_df = _read_events_tsv(file_path)
        if events_df is not None and not events_df.empty:
            annotations = _create_events_from_events_tsv(raw, events_df)
            raw.set_annotations(annotations)
        
        # Add derived misc channels
        raw = _add_derived_misc_channels(raw, derived_values)
        
        # Rename channels if needed
        raw.rename_channels(lambda x: _CHANNEL_RENAME_MAP.get(x, x))
        
        # Set channel types
        eog_channels = ["EOG-left", "EOG-right", "EOG-central"]
        for ch in eog_channels:
            if ch in raw.ch_names:
                raw.set_channel_types({ch: "eog"})
        
        # Set EEG channel types for standard channels
        eeg_chs = [ch for ch in raw.ch_names if ch in _STANDARD_EEG_CHANNELS]
        if eeg_chs:
            raw.set_channel_types({ch: "eeg" for ch in eeg_chs})
        
        # Set montage for EEG channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        return raw


KERNEL = OpenneuroDs004902Kernel()