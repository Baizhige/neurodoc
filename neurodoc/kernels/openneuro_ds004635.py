"""OpenNeuro ds004635 stage1 kernel for EEGUnity.

Infant EEG Microstates Reliability Dataset
- 48 infants, 129 channels, 1000 Hz
- Single aggregated file with segment boundary markers (bgin, TRSP)
- BIDS format with participants.tsv (Age, Gender columns)
- Primary analysis: EEG microstate segmentation (5 classes)

Source: https://openneuro.org/datasets/ds004635
Paper: 10.1007/s10548-024-01043-5 (tutorial on infant EEG microstate analysis)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================
# Required info fields from participants.tsv
# ============================================================
_REQUIRED_INFO_FIELDS = ["Age", "Gender", "sex", "amplifier", "cap", "handedness"]

# ============================================================
# Required event IDs (must appear in scan)
# ============================================================
_REQUIRED_EVENT_IDS = ["IBEG", "IEND", "TRSP", "bgin"]

# ============================================================
# Channel Name Mapping (129 channels: 128 GSN + 1 reference)
# ============================================================
# Source: Gaffrey Lab EEG-Microstate-Analysis-Tutorial
# https://github.com/gaffreylab/EEG-Microstate-Analysis-Tutorial
# The dataset uses a 128-channel HydroCel GSN montage plus 1 reference channel.
# Standard EGI GSN-128 layout with E129 as Cz reference.
# Annotator: Human, 2026-04-08 (verified against EGI GSN-128 documentation)
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "E1": "E1",
    "E2": "E2",
    "E3": "E3",
    "E4": "E4",
    "E5": "E5",
    "E6": "E6",
    "E7": "E7",
    "E8": "E8",
    "E9": "E9",
    "E10": "E10",
    "E11": "E11",
    "E12": "E12",
    "E13": "E13",
    "E14": "E14",
    "E15": "E15",
    "E16": "E16",
    "E17": "E17",
    "E18": "E18",
    "E19": "E19",
    "E20": "E20",
    "E21": "E21",
    "E22": "E22",
    "E23": "E23",
    "E24": "E24",
    "E25": "E25",
    "E26": "E26",
    "E27": "E27",
    "E28": "E28",
    "E29": "E29",
    "E30": "E30",
    "E31": "E31",
    "E32": "E32",
    "E33": "E33",
    "E34": "E34",
    "E35": "E35",
    "E36": "E36",
    "E37": "E37",
    "E38": "E38",
    "E39": "E39",
    "E40": "E40",
    "E41": "E41",
    "E42": "E42",
    "E43": "E43",
    "E44": "E44",
    "E45": "E45",
    "E46": "E46",
    "E47": "E47",
    "E48": "E48",
    "E49": "E49",
    "E50": "E50",
    "E51": "E51",
    "E52": "E52",
    "E53": "E53",
    "E54": "E54",
    "E55": "E55",
    "E56": "E56",
    "E57": "E57",
    "E58": "E58",
    "E59": "E59",
    "E60": "E60",
    "E61": "E61",
    "E62": "E62",
    "E63": "E63",
    "E64": "E64",
    "E65": "E65",
    "E66": "E66",
    "E67": "E67",
    "E68": "E68",
    "E69": "E69",
    "E70": "E70",
    "E71": "E71",
    "E72": "E72",
    "E73": "E73",
    "E74": "E74",
    "E75": "E75",
    "E76": "E76",
    "E77": "E77",
    "E78": "E78",
    "E79": "E79",
    "E80": "E80",
    "E81": "E81",
    "E82": "E82",
    "E83": "E83",
    "E84": "E84",
    "E85": "E85",
    "E86": "E86",
    "E87": "E87",
    "E88": "E88",
    "E89": "E89",
    "E90": "E90",
    "E91": "E91",
    "E92": "E92",
    "E93": "E93",
    "E94": "E94",
    "E95": "E95",
    "E96": "E96",
    "E97": "E97",
    "E98": "E98",
    "E99": "E99",
    "E100": "E100",
    "E101": "E101",
    "E102": "E102",
    "E103": "E103",
    "E104": "E104",
    "E105": "E105",
    "E106": "E106",
    "E107": "E107",
    "E108": "E108",
    "E109": "E109",
    "E110": "E110",
    "E111": "E111",
    "E112": "E112",
    "E113": "E113",
    "E114": "E114",
    "E115": "E115",
    "E116": "E116",
    "E117": "E117",
    "E118": "E118",
    "E119": "E119",
    "E120": "E120",
    "E121": "E121",
    "E122": "E122",
    "E123": "E123",
    "E124": "E124",
    "E125": "E125",
    "E126": "E126",
    "E127": "E127",
    "E128": "E128",
    "E129": "Cz",  # Reference channel, typically Cz in GSN-128
    "VREF": "VREF",  # Vertex reference
}


def _read_participants_tsv(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv.
    
    Returns a dict with required fields as strings, or "unknown" if missing.
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject_id to participant_id
        subj_row = df[df["participant_id"] == subject_id]
        if subj_row.empty:
            # Try with "sub-" prefix
            subj_row = df[df["participant_id"] == f"sub-{subject_id}"]
        if subj_row.empty:
            # Try without "sub-" prefix
            subj_row = df[df["participant_id"] == subject_id.replace("sub-", "")]
        
        if subj_row.empty:
            return {field: "unknown" for field in _REQUIRED_INFO_FIELDS}
        
        result = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in subj_row.columns:
                val = subj_row[field].values[0]
                if pd.isna(val):
                    result[field] = "unknown"
                else:
                    result[field] = str(val).strip()
            else:
                result[field] = "unknown"
        return result
    except Exception:
        return {field: "unknown" for field in _REQUIRED_INFO_FIELDS}


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    # BIDS pattern: sub-<label>[_ses-<label>]_task-<label>[_run-<index>]_eeg.<ext>
    basename = os.path.basename(file_path)
    parts = basename.split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part
    # Fallback: try to find sub-XX in path
    dirname_parts = file_path.replace("\\", "/").split("/")
    for part in dirname_parts:
        if part.startswith("sub-"):
            return part
    return "unknown"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the events.tsv sidecar path for the given EEG file."""
    # Construct events.tsv path by replacing extension
    base = file_path.rsplit(".", 1)[0]
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Also check for task-specific events.tsv
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Remove extension and any suffix after task
    name_parts = basename.rsplit(".", 1)[0].split("_")
    # Find task part
    task_idx = None
    for i, part in enumerate(name_parts):
        if part.startswith("task-"):
            task_idx = i
            break
    if task_idx is not None:
        events_name = "_".join(name_parts[:task_idx+1]) + "_events.tsv"
        events_path = os.path.join(dirname, events_name)
        if os.path.exists(events_path):
            return events_path
    
    return None


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar for the given EEG file."""
    events_path = _find_events_tsv(file_path)
    if events_path is None:
        return None
    
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations.
    
    Uses the 'value' column as the description since it contains the actual
    trigger labels (bgin, TRSP, IBEG, etc.). The 'onset' column is in seconds.
    Duration is in seconds from the tsv.
    """
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row["onset"]) if "onset" in row else 0.0
        duration = float(row["duration"]) if "duration" in row else 0.0
        # Use 'value' column for description (contains trigger labels like bgin, TRSP)
        if "value" in row:
            desc = str(row["value"])
        elif "trial_type" in row:
            desc = str(row["trial_type"])
        else:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class OpenNeuroDS004635Kernel:
    KERNEL_ID = "openneuro_ds004635"
    DATASET_NAME = "OpenNeuro ds004635"
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract file path and dataset path
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        dataset_path = udataset.root_dir if hasattr(udataset, "root_dir") else os.path.dirname(file_path)
        
        # Extract subject ID from file path
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Read participant info from participants.tsv
        participant_info = _read_participants_tsv(dataset_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participant_info.get("Age", "unknown"),
            "sex": participant_info.get("sex", participant_info.get("Gender", "unknown")),
            "amplifier": participant_info.get("amplifier", "unknown"),
            "cap": participant_info.get("cap", "unknown"),
            "handedness": participant_info.get("handedness", "unknown"),
        }
        
        # Store original description
        original_description = raw.info.get("description", "")
        
        # Read events from sidecar events.tsv and set annotations on raw
        # The EEGLAB .set files have empty event fields, so events MUST come from events.tsv
        events_df = _read_events_tsv(file_path)
        annotations = _events_to_annotations(events_df)
        raw.set_annotations(annotations)
        
        # Set description as JSON string (MNE requires string, not dict)
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
            "dataset": self.DATASET_NAME,
            "kernel_id": self.KERNEL_ID,
        })
        
        return raw


KERNEL = OpenNeuroDS004635Kernel()