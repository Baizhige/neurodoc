"""BCIT Baseline Driving dataset kernel for EEGUnity.

Dataset: openneuro_ds004120
Source: https://openneuro.org/datasets/ds004120
Reference: 10.3389/fnins.2014.00155 (BCIT driving paradigm)

Channel setup: 256-channel BioSemi system + auxiliary channels
Sampling rate: 1024 Hz
Paradigm: 60-minute simulated driving with lateral perturbations

Event code structure (4-digit):
  Digit 1: Task category (1=driving response, 2=guard/perturbation, 3=calibration/block, 4=perturbation type, 5=rare condition)
  Digit 2: Condition/sub-condition
  Digit 3: Event category (1=onset/stimulus, 2=response, 3=performance/metric)
  Digit 4: Specific sub-type
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject metadata (from participants.tsv if available, otherwise inferred)
# Source: openneuro_ds004120/participants.tsv
# Annotator: LLM, 2026-01-15 (requires human verification)
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Age/sex will be loaded from participants.tsv at runtime if available


# =============================================================================
# Channel mapping for 256-channel BioSemi system
# Source: BioSemi 256-channel layout documentation
# Channel naming follows BioSemi convention: A1-A32, B1-B32, C1-C32, D1-D32,
# E1-E32, F1-F32, G1-G32, H1-H32 plus auxiliary channels
# Annotator: LLM, 2026-01-15 (requires human verification)
# =============================================================================
_BIOSEMI_256_CHANNEL_RENAME_MAP: Dict[str, str] = {}

# Build BioSemi 256-channel standard names (A1-H8 layout, 32 channels each)
biosemi_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
biosemi_cols = list(range(1, 33))

for row in biosemi_rows:
    for col in biosemi_cols:
        # BioSemi uses format like A01, A02, ... H32
        biosemi_name = f"{row}{col:02d}"
        # Standard 10-5 system equivalent (approximate mapping for BioSemi 256)
        # BioSemi A-H rows correspond to standard positions
        # This is a simplified mapping; full mapping requires cap documentation
        _BIOSEMI_256_CHANNEL_RENAME_MAP[biosemi_name] = biosemi_name


# Common auxiliary channel names to standardize
_AUX_CHANNEL_ALIASES: Dict[str, str] = {
    "EOGleft": "EOG_left",
    "EOGright": "EOG_right",
    "EOGcentral": "EOG_central",
    "EOG-up": "EOG_up",
    "EOG-down": "EOG_down",
    "ECG": "ECG",
    "EMG": "EMG",
    "Resp": "Respiratory",
    "Trigger": "Trigger",
    "Status": "Status",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for BioSemi 256-channel system.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object containing original channel names.
    
    Returns
    -------
    Dict[str, str]
        Mapping from original names to standardized names.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Handle BioSemi 256-channel format (A01-H32)
    for orig_name in existing_names:
        # Check if it matches BioSemi format A01, A1, etc.
        if len(orig_name) >= 2:
            first_char = orig_name[0]
            if first_char in biosemi_rows:
                # Extract row and number
                if len(orig_name) == 3 and orig_name[1].isdigit():
                    row = orig_name[0]
                    num = int(orig_name[1:3])
                    if 1 <= num <= 32:
                        # Standardize to A01 format
                        new_name = f"{row}{num:02d}"
                        if orig_name != new_name:
                            rename_map[orig_name] = new_name
                elif len(orig_name) == 2 and orig_name[1].isdigit():
                    row = orig_name[0]
                    num = int(orig_name[1])
                    if 1 <= num <= 8:
                        new_name = f"{row}{num:02d}"
                        if orig_name != new_name:
                            rename_map[orig_name] = new_name
    
    # Handle auxiliary channel aliases
    for standard_name, aliases in _AUX_CHANNEL_ALIASES.items():
        for alias in aliases if isinstance(aliases, list) else [aliases]:
            if alias in existing_names and alias != standard_name:
                rename_map[alias] = standard_name
    
    return rename_map


def _detect_biosemi_montage(ch_names: List[str]) -> Optional[mne.channels.ChannelsMontage]:
    """Attempt to create montage for BioSemi 256-channel system.
    
    Parameters
    ----------
    ch_names : List[str]
        List of channel names.
    
    Returns
    -------
    Optional[mne.channels.ChannelsMontage]
        Montage if recognized, None otherwise.
    """
    # Check if all channels follow BioSemi format
    biosemi_format_count = 0
    for name in ch_names:
        if len(name) >= 2 and name[0] in biosemi_rows:
            try:
                num = int(name[1:]) if len(name) == 2 else int(name[1:3])
                if 1 <= num <= 32:
                    biosemi_format_count += 1
            except ValueError:
                pass
    
    # If majority of channels are BioSemi format, use standard 1020 as fallback
    if biosemi_format_count > len(ch_names) * 0.5:
        try:
            # Try to use standard 1020 for common channels
            # Note: Full BioSemi 256 montage requires specific digitizer positions
            # Using standard 1020 as approximate for the 10-20 positions
            montage = mne.channels.make_standard_montage("standard_1020")
            return montage
        except Exception:
            pass
    
    return None


# =============================================================================
# Event mapping based on analysis.md Event Structure table
# =============================================================================
_EVENT_MAP: Dict[str, str] = {
    # Lateral perturbation types
    "4311": "lateral_perturbation_type1",
    "4312": "lateral_perturbation_type2",
    
    # Perturbation events
    "4210": "perturbation_onset",
    "4220": "perturbation_event",
    "4230": "perturbation_direction_event",
    
    # Speed/driving state
    "3200": "speed_driving_state",
    
    # Perturbation onset/response
    "3111": "perturbation_onset_v2",
    "3112": "perturbation_response",
    
    # Performance metric
    "3310": "performance_metric",
    
    # Lane correction events (Classical Task 2)
    "1211": "lane_correction_type1",
    "1212": "lane_correction_type2",
    
    # Driver response events
    "1121": "driver_response_left",
    "1122": "driver_response_right",
    "1111": "driver_action_type1",
    "1112": "driver_action_type2",
    
    # Auditory cue events (subset of 28 files)
    "2621": "auditory_cue_type1",
    "2622": "auditory_cue_type2",
    "2611": "auditory_cue_type3",
    "2612": "auditory_cue_type4",
    
    # Rare condition events
    "5241": "rare_condition_type1",
    "5242": "rare_condition_type2",
}

# Rare/very rare events (2-5 files)
_RARE_EVENT_MAP: Dict[str, str] = {
    "4421": "very_rare_event_1",
    "4422": "very_rare_event_2",
    "5231": "very_rare_event_3",
    "5232": "very_rare_event_4",
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if available.
    
    Parameters
    ----------
    dataset_path : str
        Path to dataset root directory.
    
    Returns
    -------
    pd.DataFrame
        Participants data or empty DataFrame.
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t")
            return df
        except Exception:
            pass
    return pd.DataFrame()


def _get_subject_info(participant_id: str, dataset_path: str) -> Dict[str, str]:
    """Get subject information from participants.tsv.
    
    Parameters
    ----------
    participant_id : str
        Subject identifier (e.g., "sub-001").
    dataset_path : str
        Path to dataset root.
    
    Returns
    -------
    Dict[str, str]
        Subject info dict with age, sex, handedness.
    """
    global _SUBJECT_DICT
    
    # Check cache first
    if participant_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[participant_id]
    
    # Load from participants.tsv
    df = _load_participants_tsv(dataset_path)
    if not df.empty and "participant_id" in df.columns:
        # Normalize participant_id (remove 'sub-' prefix if present)
        normalized_id = participant_id.replace("sub-", "")
        mask = df["participant_id"].str.replace("sub-", "", regex=False) == normalized_id
        if mask.any():
            row = df[mask].iloc[0]
            info = {
                "age": str(int(row.get("age", "unknown"))) if pd.notna(row.get("age")) else "unknown",
                "sex": str(row.get("sex", "unknown")).lower() if pd.notna(row.get("sex")) else "unknown",
                "handedness": str(row.get("handedness", "unknown")).lower() if pd.notna(row.get("handedness")) else "unknown",
            }
            _SUBJECT_DICT[participant_id] = info
            return info
    
    # Default unknown values (LLM inference flag)
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


def _create_annotations_from_events_tsv(
    raw: mne.io.BaseRaw,
    events_tsv_path: str,
) -> mne.Annotations:
    """Create MNE annotations from BIDS events.tsv file.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object for timing reference.
    events_tsv_path : str
        Path to events.tsv file.
    
    Returns
    -------
    mne.Annotations
        Annotations object.
    """
    try:
        events_df = pd.read_csv(events_tsv_path, sep="\t")
    except Exception:
        return raw.annotations
    
    sfreq = raw.info["sfreq"]
    annotations_list = []
    
    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0))
        
        # Try to get event description from various columns
        description = "unknown"
        
        # Check value/code columns
        for col in ["trial_type", "value", "event_code", "stim_type", "response"]:
            if col in row and pd.notna(row.get(col)):
                raw_value = str(row.get(col))
                # Check if it's a numeric code we should map
                if raw_value.isdigit():
                    mapped = _EVENT_MAP.get(raw_value)
                    if mapped:
                        description = mapped
                        break
                    mapped = _RARE_EVENT_MAP.get(raw_value)
                    if mapped:
                        description = mapped
                        break
                else:
                    description = raw_value
                    break
        
        annotations_list.append((onset, duration, description))
    
    if annotations_list:
        onsets = [a[0] for a in annotations_list]
        durations = [a[1] for a in annotations_list]
        descriptions = [a[2] for a in annotations_list]
        return mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
    
    return raw.annotations


def _apply_bids_events(raw: mne.io.BaseRaw, row: Dict[str, Any]) -> mne.io.BaseRaw:
    """Apply BIDS events from events.tsv file.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object.
    row : Dict[str, Any]
        Locator row with file path information.
    
    Returns
    -------
    mne.io.BaseRaw
        Raw with annotations set.
    """
    file_path = row.get("File Path", "")
    if not file_path:
        return raw
    
    # Derive events.tsv path from EEG file path
    dir_path = os.path.dirname(file_path)
    events_tsv = os.path.join(dir_path, os.path.basename(file_path).split(".")[0] + "_events.tsv")
    
    if os.path.exists(events_tsv):
        annotations = _create_annotations_from_events_tsv(raw, events_tsv)
        raw.set_annotations(annotations)
    else:
        # Fallback: try to use raw.annotations if already present
        pass
    
    return raw


class BCITDrivingKernel:
    """Stage1 kernel for BCIT Baseline Driving dataset (openneuro_ds004120).
    
    This kernel handles:
    - 256-channel BioSemi EEG recordings at 1024 Hz
    - BIDS format with events.tsv
    - Channel standardization for BioSemi 256-channel system
    - Event mapping from 4-digit numeric codes to human-readable labels
    - Subject metadata from participants.tsv
    - Amplifier info: BioSemi 256-channel system
    """
    
    KERNEL_ID: str = "openneuro-ds004120-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single BCIT driving recording.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels and events.
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", os.path.dirname(os.path.dirname(file_path)))
        participant_id = row.get("participant_id", row.get("Subject", "unknown"))
        
        # -------------------------------------------------------------------------
        # Step 1: Channel renaming (before set_montage)
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming channels: {list(rename_map.items())[:5]}...")
            raw.rename_channels(rename_map)
        
        # -------------------------------------------------------------------------
        # Step 2: Set montage (after renaming)
        # -------------------------------------------------------------------------
        ch_names = raw.ch_names
        montage = _detect_biosemi_montage(ch_names)
        
        if montage is not None:
            # Get actual channel names that exist in both raw and montage
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(ch_names)
            common_ch_names = list(montage_ch_names & raw_ch_names)
            
            if common_ch_names:
                try:
                    raw.set_montage(montage, on_missing="ignore")
                    print(f"[{self.KERNEL_ID}] Montage set for {len(common_ch_names)} channels")
                except Exception as e:
                    print(f"[{self.KERNEL_ID}] Warning: Could not set montage: {e}")
        else:
            print(f"[{self.KERNEL_ID}] Warning: No recognized montage for BioSemi 256-channel system")
        
        # -------------------------------------------------------------------------
        # Step 3: Load and apply BIDS events
        # -------------------------------------------------------------------------
        raw = _apply_bids_events(raw, row)
        
        # -------------------------------------------------------------------------
        # Step 4: Update info["description"] with eegunity_description
        # -------------------------------------------------------------------------
        subject_info = _get_subject_info(participant_id, dataset_path)
        
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BioSemi 256-channel",  # LLM 推断，需人类复核
                "cap": "BioSemi 256-channel cap",  # LLM 推断，需人类复核
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # -------------------------------------------------------------------------
        # Step 5: Set channel types if identifiable
        # -------------------------------------------------------------------------
        # Identify EEG vs auxiliary channels based on BioSemi naming
        eeg_channels = []
        aux_channels = []
        
        for ch_name in raw.ch_names:
            # BioSemi EEG channels: A01-H32
            if len(ch_name) >= 2 and ch_name[0] in biosemi_rows:
                try:
                    num = int(ch_name[1:])
                    if 1 <= num <= 32:
                        eeg_channels.append(ch_name)
                        continue
                except ValueError:
                    pass
            
            # Auxiliary channels (EOG, ECG, etc.)
            if any(prefix in ch_name.upper() for prefix in ["EOG", "ECG", "EMG", "RESP", "TRIG", "STATUS", "AUX"]):
                aux_channels.append(ch_name)
            else:
                # Default unknown channels to EEG if not clearly auxiliary
                if ch_name not in aux_channels:
                    eeg_channels.append(ch_name)
        
        # Set auxiliary channel types
        if aux_channels:
            type_dict = {ch: "eog" if "EOG" in ch.upper() else 
                        "ecg" if "ECG" in ch.upper() else
                        "emg" if "EMG" in ch.upper() else
                        "misc" for ch in aux_channels}
            try:
                raw.set_channel_types(type_dict)
            except Exception as e:
                print(f"[{self.KERNEL_ID}] Warning: Could not set channel types: {e}")
        
        return raw


KERNEL = BCITDrivingKernel()