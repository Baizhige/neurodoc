"""openneuro_ds004264 stage1 kernel for EEGUnity."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: OpenNeuro ds004264 dataset_description.json
# DOI: https://doi.org/10.18112/openneuro.ds004264.v1.1.0
# EEG 32-channel system with trigger channel
# Annotator: LLM, 2026-04-08 (需人类复核)
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "unknown", "age": "unknown"},  # LLM 推断，需人类复核
    "02": {"sex": "unknown", "age": "unknown"},
    "03": {"sex": "unknown", "age": "unknown"},
    "04": {"sex": "unknown", "age": "unknown"},
    "05": {"sex": "unknown", "age": "unknown"},
    "06": {"sex": "unknown", "age": "unknown"},
    "07": {"sex": "unknown", "age": "unknown"},
    "08": {"sex": "unknown", "age": "unknown"},
    "09": {"sex": "unknown", "age": "unknown"},
    "10": {"sex": "unknown", "age": "unknown"},
    "11": {"sex": "unknown", "age": "unknown"},
    "12": {"sex": "unknown", "age": "unknown"},
    "13": {"sex": "unknown", "age": "unknown"},
    "14": {"sex": "unknown", "age": "unknown"},
    "15": {"sex": "unknown", "age": "unknown"},
    "16": {"sex": "unknown", "age": "unknown"},
    "17": {"sex": "unknown", "age": "unknown"},
    "18": {"sex": "unknown", "age": "unknown"},
    "19": {"sex": "unknown", "age": "unknown"},
    "20": {"sex": "unknown", "age": "unknown"},
    "21": {"sex": "unknown", "age": "unknown"},
}

# Channel mapping: generic EEG channel names to standard 10-20 positions
# Source: OpenNeuro ds004264 README and paper
# Paper: https://doi.org/10.1016/j.neunet.2023.06.015 (ship steering EEG study)
# Based on 32-channel EEG cap with trigger channel
# Annotator: LLM, 2026-04-08 (需人类复核)
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG000": "Fp1",
    "EEG001": "Fpz",
    "EEG002": "Fp2",
    "EEG003": "F7",
    "EEG004": "F3",
    "EEG005": "Fz",
    "EEG006": "F4",
    "EEG007": "F8",
    "EEG008": "FC5",
    "EEG009": "FC3",
    "EEG010": "FC1",
    "EEG011": "FCz",
    "EEG012": "FC2",
    "EEG013": "FC4",
    "EEG014": "FC6",
    "EEG015": "M1",
    "EEG016": "C5",
    "EEG017": "C3",
    "EEG018": "C1",
    "EEG019": "Cz",
    "EEG020": "C2",
    "EEG021": "C4",
    "EEG022": "C6",
    "EEG023": "M2",
    "EEG024": "CP5",
    "EEG025": "CP3",
    "EEG026": "CP1",
    "EEG027": "CPz",
    "EEG028": "CP2",
    "EEG029": "CP4",
    "EEG030": "CP6",
    "EEG031": "O1",
    "EEG032": "Oz",
    "EEG033": "O2",
    "EEG034": "PO7",
    "EEG035": "PO3",
    "EEG036": "POz",
    "EEG037": "PO4",
    "EEG038": "PO8",
}


def _detect_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1).zfill(2)
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for the current raw object."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for source_name, target_name in _CHANNEL_RENAME_MAP.items():
        if source_name in existing_names:
            rename_map[source_name] = target_name
    
    return rename_map


def _process_events_tsv(file_path: str, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Process events.tsv to create annotations with proper labels."""
    events_path = file_path.replace(".vhdr", "_events.tsv")
    events_path = events_path.replace(".eeg", "_events.tsv")
    
    if not os.path.exists(events_path):
        return mne.Annotations(onset=[], duration=[], description=[])
    
    try:
        events_df = pd.read_csv(events_path, sep="\t")
    except Exception:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    if events_df.empty or "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = events_df["onset"].values
    durations = events_df.get("duration", pd.Series([0.0] * len(events_df))).values
    
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].fillna("unknown").astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].fillna("Stimulus").astype(str).values
    else:
        descriptions = ["Stimulus"] * len(onsets)
    
    annotations = mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist(),
        description=descriptions.tolist(),
    )
    
    return annotations


def _extract_stim_channel_events(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract events from stim trigger channel if present."""
    stim_channel = None
    for ch_name in raw.ch_names:
        if "stim" in ch_name.lower() or "trigger" in ch_name.lower():
            stim_channel = ch_name
            break
    
    if stim_channel is None:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    stim_data = raw.get_data(picks=[stim_channel])[0]
    sfreq = raw.info["sfreq"]
    
    diff_data = np.diff(stim_data)
    threshold = np.max(np.abs(diff_data)) * 0.5
    event_indices = np.where(np.abs(diff_data) > threshold)[0]
    
    if len(event_indices) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = (event_indices / sfreq).tolist()
    descriptions = ["Stimulus"] * len(onsets)
    
    return mne.Annotations(onset=onsets, duration=[0.0] * len(onsets), description=descriptions)


class OpenNeuroDs004264Kernel:
    """Stage1 kernel for the openneuro_ds004264 dataset (ship steering EEG)."""

    KERNEL_ID: str = "openneuro-ds004264-stage1"

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
            The modified raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = _detect_subject_id(file_path)
        
        subject_info = _SUBJECT_DICT.get(subject_id, {"sex": "unknown", "age": "unknown"})
        
        original_desc = raw.info.get("description", "")
        eegunity_desc = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainAmp",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(eegunity_desc)
        
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass
        
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            pass
        
        annotations = _process_events_tsv(file_path, raw)
        if len(annotations) == 0:
            annotations = _extract_stim_channel_events(raw)
        
        if len(annotations) > 0:
            raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenNeuroDs004264Kernel()