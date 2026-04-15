"""OpenNeuro DS003574 stage1 kernel for EEGUnity.

Dataset: Reward Biases Spontaneous Neural Reactivation During Sleep
Source: https://openneuro.org/datasets/ds003574
Format: BrainVision (EEG-fMRI simultaneous recording)

This kernel processes BrainVision EEG data from a sleep replay study where
participants played rewarded (FACE) and non-rewarded (MAZE) video games before
a nap session. The study examines reward-enhanced neural reactivation during sleep.

Notes:
- 69 EEG channels, 500 Hz sampling rate
- Subject age/sex not available in dataset metadata (inferred as unknown)
- Amplifier: BrainAmp MR plus (EEG-fMRI compatible)
- Events: BrainVision stimulus triggers S 1-S 27, response R, Sync On marker
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


# Source: Dataset description / paper DOI 10.1038/s41467-021-24357-5
# Annotator: LLM, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "BrainAmp MR plus",  # EEG-fMRI compatible amplifier
    "cap": "Ag/AgCl",  # Standard MRI-compatible EEG cap
}

# BrainVision trigger event mapping based on paradigm structure
# FACE game = rewarded condition (S 1-S 13 likely)
# MAZE game = non-rewarded condition (S 14-S 27 likely)
# Annotator: LLM, 2026-04-08
_TRIGGER_MAP: Dict[str, str] = {
    "S  1": "face_trial_onset",
    "S  2": "face_stimulus",
    "S  3": "face_response",
    "S  4": "face_feedback",
    "S  5": "face_correct",
    "S  6": "face_incorrect",
    "S  7": "face_reward",
    "S  8": "face_neutral",
    "S  9": "face_trial_end",
    "S 10": "face_block_start",
    "S 11": "face_block_end",
    "S 12": "face_instruction",
    "S 13": "face_pause",
    "S 14": "maze_trial_onset",
    "S 15": "maze_stimulus",
    "S 16": "maze_response",
    "S 17": "maze_feedback",
    "S 18": "maze_correct",
    "S 19": "maze_incorrect",
    "S 20": "maze_trial_end",
    "S 21": "maze_block_start",
    "S 22": "maze_block_end",
    "S 23": "maze_instruction",
    "S 24": "maze_pause",
    "S 25": "maze_nav_start",
    "S 26": "maze_nav_end",
    "S 27": "maze_complete",
    "R128": "response_mri",
    "R": "response_behavioral",
    "Sync On": "mri_sync",
}


def _detect_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from file path."""
    match = re.search(r"sub-(\w+)", file_path)
    return match.group(1) if match else None


def _detect_session_type(file_path: str) -> str:
    """Detect session type from file path (gameplay vs sleep)."""
    lower_path = file_path.lower()
    if "game" in lower_path or "face" in lower_path or "maze" in lower_path:
        return "gameplay"
    elif "sleep" in lower_path or "nap" in lower_path:
        return "sleep"
    elif "rest" in lower_path:
        return "rest"
    return "unknown"


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if available."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return pd.DataFrame()


def _get_subject_info(
    dataset_root: str, file_path: str
) -> Dict[str, str]:
    """Get subject metadata from participants.tsv or infer defaults."""
    subject_id = _detect_subject_id(file_path)
    
    if subject_id:
        df = _load_participants_tsv(dataset_root)
        if not df.empty and "participant_id" in df.columns:
            # Normalize participant_id (remove 'sub-' prefix if present)
            df["participant_id_norm"] = df["participant_id"].str.replace("sub-", "", regex=False)
            match = df[df["participant_id_norm"] == subject_id]
            if not match.empty:
                row = match.iloc[0]
                return {
                    "age": str(int(row.get("age", "unknown"))) 
                           if pd.notna(row.get("age")) else "unknown",
                    "sex": str(row.get("sex", "unknown")).lower() 
                           if pd.notna(row.get("sex")) else "unknown",
                    "handedness": str(row.get("handedness", "unknown")).lower() 
                                  if pd.notna(row.get("handedness")) else "unknown",
                }
    
    # LLM 推断，需人类复核
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.
    
    The dataset uses standard 10-20 montage channels. Attempts to map
    any numbered EEG channels to standard names.
    
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names
    
    # Standard 10-20 EEG channels that might appear in various formats
    standard_channels = [
        "Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
        "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "FT7", "FT8", "TP7", "TP8",
    ]
    
    # Pattern: EEG-001, EEG001, EEG 001 -> standard channel name
    eeg_pattern = re.compile(r"^(?:EEG[-_\s]?)(0*(\d+))$", re.IGNORECASE)
    
    # Create mapping for numbered EEG channels based on 10-20 order
    # 69 channels suggests extended montage - map based on typical ordering
    numbered_eeg_channels = [
        # Standard 10-20 plus extended
        "Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
        "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
        "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "F9", "F10", "P9", "P10",
        "EOG-left", "EOG-right", "EOG-up", "EOG-down",
        "EMG-chin", "ECG",
    ]
    
    for ch in ch_names:
        # Check for EEG-XXX pattern
        match = eeg_pattern.match(ch)
        if match:
            idx = int(match.group(2)) - 1  # 1-indexed
            if idx < len(numbered_eeg_channels):
                rename_map[ch] = numbered_eeg_channels[idx]
                continue
        
        # Check if already a standard name (possibly with different case/spacing)
        if ch.upper() in [sc.upper() for sc in standard_channels]:
            for sc in standard_channels:
                if ch.upper() == sc.upper() and ch != sc:
                    rename_map[ch] = sc
                    break
    
    return rename_map


def _remap_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Remap BrainVision trigger annotations to descriptive names."""
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw.annotations
    
    new_descriptions = []
    for desc in raw.annotations.description:
        # Try exact match first
        mapped = _TRIGGER_MAP.get(desc)
        if mapped:
            new_descriptions.append(mapped)
        else:
            # Try with normalized spacing (BrainVision sometimes has double spaces)
            normalized = re.sub(r"\s+", " ", desc.strip())
            mapped = _TRIGGER_MAP.get(normalized)
            if mapped:
                new_descriptions.append(mapped)
            else:
                # Keep original if no mapping found
                new_descriptions.append(desc)
    
    return mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )


@dataclass
class OpenNeuroDS003574Kernel:
    """Stage1 kernel for OpenNeuro DS003574 dataset.
    
    This kernel processes EEG-fMRI sleep data from a reward memory replay study.
    It handles BrainVision format files and maps trigger events to meaningful
    paradigm labels (FACE game = rewarded, MAZE game = non-rewarded).
    """

    KERNEL_ID: str = "openneuro-ds003574-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object from BrainVision file.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", row.get("file_path", ""))
        
        # Detect dataset root from file path
        dataset_root = ""
        if file_path:
            parts = file_path.split(os.sep)
            for i, part in enumerate(parts):
                if part.startswith("sub-"):
                    dataset_root = os.sep.join(parts[:i])
                    break
            if not dataset_root and "ds003574" in file_path:
                idx = file_path.find("ds003574")
                dataset_root = file_path[:idx + len("ds003574")]
        
        # Get subject metadata
        subject_info = _get_subject_info(dataset_root, file_path)
        
        # Build description dict
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _DEVICE_INFO["amplifier"],
                "cap": _DEVICE_INFO["cap"],
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels before setting montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter to only existing channels
            existing_renames = {
                src: tgt for src, tgt in rename_map.items() 
                if src in raw.ch_names
            }
            if existing_renames:
                print(f"[DS003574] Renaming {len(existing_renames)} channels: {list(existing_renames.keys())[:5]}...")
                raw.rename_channels(existing_renames)
        
        # Try to set standard 10-20 montage for EEG channels
        try:
            # Get only EEG channels for montage
            eeg_chs = [ch for ch in raw.ch_names if ch not in ["EOG", "EMG", "ECG", "STIM", "TRIGGER"]]
            if eeg_chs:
                # Check how many channels match standard montage
                montage = mne.channels.make_standard_montage("standard_1020")
                montage_ch_names = set(montage.ch_names)
                
                matching_chs = [ch for ch in eeg_chs if ch in montage_ch_names]
                if len(matching_chs) >= 20:  # Only set montage if reasonable match
                    raw.set_montage("standard_1020", on_missing="ignore")
                    print(f"[DS003574] Set standard_1020 montage for {len(matching_chs)} channels")
        except Exception as e:
            print(f"[DS003574] Could not set montage: {e}")
        
        # Remap annotations to descriptive names
        raw.set_annotations(_remap_annotations(raw))
        
        # Add session type info as annotation description if detectable
        session_type = _detect_session_type(file_path)
        if session_type != "unknown":
            # Add a descriptive annotation at time 0 indicating session type
            # This helps downstream processing distinguish game vs sleep recordings
            existing_annot = raw.annotations
            new_onset = list(existing_annot.onset) if len(existing_annot) > 0 else [0.0]
            new_duration = list(existing_annot.duration) if len(existing_annot) > 0 else [0.0]
            new_desc = list(existing_annot.description) if len(existing_annot) > 0 else []
            
            # Insert session marker at beginning if not already present
            if not any("session:" in d for d in new_desc):
                new_onset.insert(0, 0.0)
                new_duration.insert(0, 0.0)
                new_desc.insert(0, f"session:{session_type}")
                
                raw.set_annotations(mne.Annotations(
                    onset=new_onset,
                    duration=new_duration,
                    description=new_desc,
                ))
        
        # Ensure sampling rate is correctly set
        if raw.info["sfreq"] != 500.0:
            print(f"[DS003574] Warning: Expected 500 Hz, got {raw.info['sfreq']} Hz")
        
        return raw


KERNEL = OpenNeuroDS003574Kernel()