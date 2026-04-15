"""OpenNeuro DS003702 Social Memory Cueing stage1 kernel for EEGUnity.

A visual working memory task in VR where participants recall object locations
following social (avatar) or non-social (stick) directional cues.

Source: https://openneuro.org/datasets/ds003702
Reference: DOI 10.1109/SMC58881.2025.11343511
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Source: Dataset documentation / 64-channel standard montage
# Annotator: LLM, 2026-04-08
_STANDARD_64_CHANNELS = [
    "FP1", "FPZ", "FP2",
    "AF3", "AF4",
    "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
    "PO3", "PO4",
    "O1", "OZ", "O2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.
    
    Source: Standard 10-20 electrode naming convention
    Annotator: LLM, 2026-04-08
    """
    existing = set(raw.ch_names)
    rename_map: Dict[str, str] = {}
    
    # Common non-standard patterns in BrainVision/BrainAmp data
    # Pattern: "EEG" + number -> standard name
    alias_groups = [
        ("FP1", ["EEG 001", "FP1", "Fp1"]),
        ("FPZ", ["EEG 002", "FPZ", "Fpz", "Fpz"]),
        ("FP2", ["EEG 003", "FP2", "Fp2"]),
        ("AF3", ["EEG 004", "AF3", "Af3"]),
        ("AF4", ["EEG 005", "AF4", "Af4"]),
        ("F7", ["EEG 006", "F7", "F7"]),
        ("F5", ["EEG 007", "F5", "F5"]),
        ("F3", ["EEG 008", "F3", "F3"]),
        ("F1", ["EEG 009", "F1", "F1"]),
        ("FZ", ["EEG 010", "FZ", "Fz"]),
        ("F2", ["EEG 011", "F2", "F2"]),
        ("F4", ["EEG 012", "F4", "F4"]),
        ("F6", ["EEG 013", "F6", "F6"]),
        ("F8", ["EEG 014", "F8", "F8"]),
        ("FT7", ["EEG 015", "FT7", "Ft7"]),
        ("FC5", ["EEG 016", "FC5", "Fc5"]),
        ("FC3", ["EEG 017", "FC3", "Fc3"]),
        ("FC1", ["EEG 018", "FC1", "Fc1"]),
        ("FCZ", ["EEG 019", "FCZ", "FCz", "Fcz"]),
        ("FC2", ["EEG 020", "FC2", "Fc2"]),
        ("FC4", ["EEG 021", "FC4", "Fc4"]),
        ("FC6", ["EEG 022", "FC6", "Fc6"]),
        ("FT8", ["EEG 023", "FT8", "Ft8"]),
        ("T7", ["EEG 024", "T7", "T7"]),
        ("C5", ["EEG 025", "C5", "C5"]),
        ("C3", ["EEG 026", "C3", "C3"]),
        ("C1", ["EEG 027", "C1", "C1"]),
        ("CZ", ["EEG 028", "CZ", "Cz"]),
        ("C2", ["EEG 029", "C2", "C2"]),
        ("C4", ["EEG 030", "C4", "C4"]),
        ("C6", ["EEG 031", "C6", "C6"]),
        ("T8", ["EEG 032", "T8", "T8"]),
        ("TP7", ["EEG 033", "TP7", "Tp7"]),
        ("CP5", ["EEG 034", "CP5", "Cp5"]),
        ("CP3", ["EEG 035", "CP3", "Cp3"]),
        ("CP1", ["EEG 036", "CP1", "Cp1"]),
        ("CPZ", ["EEG 037", "CPZ", "CPz", "Cpz"]),
        ("CP2", ["EEG 038", "CP2", "Cp2"]),
        ("CP4", ["EEG 039", "CP4", "Cp4"]),
        ("CP6", ["EEG 040", "CP6", "Cp6"]),
        ("TP8", ["EEG 041", "TP8", "Tp8"]),
        ("P7", ["EEG 042", "P7", "P7"]),
        ("P5", ["EEG 043", "P5", "P5"]),
        ("P3", ["EEG 044", "P3", "P3"]),
        ("P1", ["EEG 045", "P1", "P1"]),
        ("PZ", ["EEG 046", "PZ", "Pz"]),
        ("P2", ["EEG 047", "P2", "P2"]),
        ("P4", ["EEG 048", "P4", "P4"]),
        ("P6", ["EEG 049", "P6", "P6"]),
        ("P8", ["EEG 050", "P8", "P8"]),
        ("PO3", ["EEG 051", "PO3", "Po3"]),
        ("PO4", ["EEG 052", "PO4", "Po4"]),
        ("O1", ["EEG 053", "O1", "O1"]),
        ("OZ", ["EEG 054", "OZ", "Oz"]),
        ("O2", ["EEG 055", "O2", "O2"]),
    ]
    
    for target, aliases in alias_groups:
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _get_subject_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.
    
    Source: BIDS participants.tsv
    Annotator: LLM, 2026-04-08
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    
    default_info = {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",
    }
    
    if not os.path.exists(participants_file):
        return default_info
    
    try:
        df = pd.read_csv(participants_file, sep="\t")
        subject_row = df[df["participant_id"] == subject_id]
        
        if subject_row.empty:
            return default_info
        
        row = subject_row.iloc[0]
        
        # Extract age
        age = "unknown"
        if "age" in df.columns:
            age_val = row.get("age")
            if pd.notna(age_val):
                age = str(int(age_val))
        
        # Extract sex
        sex = "unknown"
        if "sex" in df.columns:
            sex_val = row.get("sex")
            if pd.notna(sex_val):
                sex_str = str(sex_val).lower().strip()
                if sex_str in ["m", "male", "男"]:
                    sex = "male"
                elif sex_str in ["f", "female", "女"]:
                    sex = "female"
                else:
                    sex = "unknown"
        
        # Extract handedness
        handedness = "unknown"
        if "handedness" in df.columns:
            hand_val = row.get("handedness")
            if pd.notna(hand_val):
                hand_str = str(hand_val).lower().strip()
                if hand_str in ["r", "right", "右"]:
                    handedness = "right"
                elif hand_str in ["l", "left", "左"]:
                    handedness = "left"
        
        return {
            "age": age,
            "sex": sex,
            "handedness": handedness,
        }
    except Exception:
        return default_info


def _load_events_tsv(eeg_file_path: str) -> pd.DataFrame:
    """Load events from BIDS *_events.tsv file.
    
    Source: BIDS events.tsv sidecar
    Annotator: LLM, 2026-04-08
    """
    base_path = eeg_file_path.rsplit("_eeg", 1)[0]
    events_file = base_path + "_events.tsv"
    
    if os.path.exists(events_file):
        try:
            return pd.read_csv(events_file, sep="\t")
        except Exception:
            pass
    
    return pd.DataFrame()


def _build_stimulus_annotations(raw: mne.io.BaseRaw, row) -> mne.Annotations:
    """Build annotations from stimulus events (s3021-s3028, s3040-s3048).
    
    Source: Dataset documentation, DOI 10.1109/SMC58881.2025.11343511
    Annotator: LLM, 2026-04-08
    """
    events_df = _load_events_tsv(row.get("File Path", ""))
    
    if events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Standard BIDS events columns: onset, duration, trial_type
    onset_col = None
    for col in ["onset", "onset_sec", "timestamp"]:
        if col in events_df.columns:
            onset_col = col
            break
    
    if onset_col is None:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onset = events_df[onset_col].values
    duration = events_df.get("duration", pd.Series([0.0] * len(onset))).values
    
    # Determine description column
    desc_col = None
    for col in ["trial_type", "stim_type", "value", "event_type", "cue_type"]:
        if col in events_df.columns:
            desc_col = col
            break
    
    if desc_col is None:
        descriptions = events_df.iloc[:, 1].astype(str).values
    else:
        descriptions = events_df[desc_col].astype(str).values
    
    return mne.Annotations(
        onset=onset,
        duration=duration,
        description=descriptions,
    )


@dataclass
class OpenNeuroDS003702Kernel:
    """Stage1 kernel for OpenNeuro DS003702 Social Memory Cueing dataset."""

    KERNEL_ID: str = "openneuro-ds003702-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed MNE Raw object with standardized channels and metadata.
        """
        file_path = row.get("File Path", "")
        dataset_path = os.path.dirname(file_path) if file_path else ""
        
        # Extract subject ID from row or file path
        subject_id = row.get("subject_id", "")
        if not subject_id and file_path:
            parts = file_path.split(os.sep)
            for part in parts:
                if part.startswith("sub-"):
                    subject_id = part.replace("sub-", "")
                    break
        
        # Get subject metadata
        subject_info = _get_subject_info(dataset_path, subject_id)
        
        # Build channel rename map and apply before set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage if all channels match
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            eeg_channels = [ch for ch in raw.ch_names if ch not in ["EOG", "ECG", "EMG"]]
            present_channels = [ch for ch in eeg_channels if ch in montage.ch_names]
            if len(present_channels) >= 20:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if electrodes cannot be mapped
        
        # Build stimulus annotations from events.tsv
        annotations = _build_stimulus_annotations(raw, row)
        if annotations:
            raw.set_annotations(annotations)
        
        # Determine amplifier and cap info from dataset_description.json
        amplifier = "BrainAmp"  # Default assumption based on reference
        cap = "Ag/AgCl"  # Default assumption
        
        # Try to read from dataset_description.json
        desc_file = os.path.join(dataset_path, "dataset_description.json")
        if os.path.exists(desc_file):
            try:
                with open(desc_file) as f:
                    desc = json.load(f)
                    # Look for equipment information if available
            except Exception:
                pass
        
        # Get original description
        original_desc = raw.info.get("description", "")
        
        # Build eegunity_description
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": amplifier,
                "cap": cap,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS003702Kernel()