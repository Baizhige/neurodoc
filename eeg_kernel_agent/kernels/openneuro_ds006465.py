"""3M-CPSEED stage1 kernel for EEGUnity.

Dataset: openneuro_ds006465
Paradigm: Chinese Pinyin Production (overt, silent-intended, imagined speech)
Source: https://openneuro.org/datasets/ds006465 | DOI: 10.1038/s41597-025-06346-1

This kernel handles BIDS-formatted EEG data with 32 EEG + 1 EOG channels.
Stimulus events include phoneme codes (1-10) and stimulus_presentation cues.
Amplifier and cap info inferred from publication (LLM 推断，需人类复核).

Annotator: LLM (auto-generated), 2026-06-18
"""

from __future__ import annotations

import json
import os
from typing import Dict

import mne
import pandas as pd


# Source: DOI 10.1038/s41597-025-06346-1 (3M-CPSEED paper)
# Amplifier: Brain Products BrainAmp DC (LLM 推断，需人类复核)
# Cap: Easycap with 32-channel Ag/AgCl electrode layout (LLM 推断，需人类复核)
_DEVICE_METADATA = {
    "amplifier": "BrainAmp DC",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl (Easycap)",  # LLM 推断，需人类复核
}

# Standard 32-channel names per 10-20 system
_STANDARD_32_CHANNELS = [
    "Fp1", "Fz", "F3", "F7", "FT9", "FC5", "FC1", "FCz",
    "C3", "Cz", "C4", "T7", "TP9", "CP5", "CP1", "CPz",
    "Pz", "P3", "P7", "O1", "Oz", "O2", "P4", "P8",
    "TP10", "CP6", "CP2", "T8", "FT10", "FC6", "FC2", "F4",
    "F8",
]

# Event label mapping for phoneme codes (1-10)
# Source: analysis.md (Dataset Documentation)
_PHONEME_EVENT_MAP = {
    1: "pinyin_a",
    2: "pinyin_i",
    3: "pinyin_u",
    4: "pinyin_ue",
    5: "pinyin_m",
    6: "pinyin_f",
    7: "pinyin_j",
    8: "pinyin_l",
    9: "pinyin_k",
    10: "pinyin_ch",
}

# Stimulus presentation events (visual cue for speech production trial)
_STIMULUS_EVENT_IDS = [131061, 131062, 131063, 131070, 131071]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from non-standard to standard names.
    
    The dataset uses numbered channel names (e.g., EEG001, EEG002) which
    need to be mapped to standard 10-20 system names.
    
    Source: channel mapping based on standard 10-20 layout for 32 channels
    Annotator: LLM, 2026-06-18
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Pattern: EEG001 -> Fp1, EEG002 -> Fz, etc.
    eeg_pattern = "EEG{:03d}"
    
    for i, standard_name in enumerate(_STANDARD_32_CHANNELS, start=1):
        eeg_name = eeg_pattern.format(i)
        if eeg_name in existing_names:
            rename_map[eeg_name] = standard_name
    
    # Handle EOG channel if present
    eog_aliases = ["EOG", "EOG1", "EOG001", "EOG-left"]
    for eog_name in eog_aliases:
        if eog_name in existing_names:
            rename_map[eog_name] = "EOG"
            break
    
    return rename_map


def _load_participants_data(udataset) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from participants.tsv.
    
    Returns dict mapping subject_id -> {age, sex, handedness}
    Age and sex may be missing in original BIDS; mark as unknown.
    
    Annotator: LLM, 2026-06-18
    """
    subject_data = {}
    
    # Try to find participants.tsv
    dataset_root = getattr(udataset, "root_path", "")
    participants_file = os.path.join(dataset_root, "participants.tsv")
    
    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).replace("sub-", "")
                age = str(row.get("age", "unknown"))
                sex = str(row.get("sex", "unknown")).lower()
                handedness = str(row.get("handedness", "unknown")).lower()
                
                if age in ["", "nan", "NaN"]:
                    age = "unknown"
                if sex in ["", "nan", "NaN"]:
                    sex = "unknown"
                if handedness in ["", "nan", "NaN"]:
                    handedness = "unknown"
                
                subject_data[subj_id] = {
                    "age": age,
                    "sex": sex if sex in ["male", "female"] else "unknown",
                    "handedness": handedness if handedness in ["right", "left"] else "unknown",
                }
        except Exception:
            pass
    
    return subject_data


def _extract_subject_id(row) -> str:
    """Extract subject ID from row file path or metadata."""
    file_path = str(row.get("File Path", ""))
    # Extract subject ID from path like .../sub-01/eeg/...
    import re
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _create_annotations_from_events(raw: mne.io.BaseRaw, events_tsv_path: str = None) -> mne.Annotations:
    """Create MNE annotations from events.tsv file.
    
    Maps numeric event codes to descriptive labels:
    - 1-10: phoneme/pinyin syllable codes
    - stimulus_presentation cues (stimulus_presentation)
    
    Annotator: LLM, 2026-06-18
    """
    onset_list = []
    duration_list = []
    description_list = []
    
    # Add stimulus_presentation events at known positions
    # Trials are ~25 seconds: stimulus at 0s, overt 3-9s, silent 10-16s, imagined 17-23s
    # Count events from analysis.md: stimulus_presentation = 42
    if events_tsv_path and os.path.exists(events_tsv_path):
        try:
            events_df = pd.read_csv(events_tsv_path, sep="\t")
            
            # Find event_value column (may be named value, event_code, etc.)
            value_col = None
            for col in ["event_value", "value", "code", "event_code", "trigger"]:
                if col in events_df.columns:
                    value_col = col
                    break
            
            if value_col:
                onset_col = "onset" if "onset" in events_df.columns else events_df.columns[0]
                
                for _, row in events_df.iterrows():
                    onset = float(row[onset_col])
                    value = row[value_col]
                    
                    # Map numeric codes to descriptive labels
                    if isinstance(value, (int, float)) and 1 <= value <= 10:
                        desc = _PHONEME_EVENT_MAP.get(int(value), f"phoneme_{value}")
                    elif "stimulus" in str(value).lower():
                        desc = "stimulus_presentation"
                    elif str(value).startswith("response"):
                        desc = "response"
                    else:
                        desc = str(value)
                    
                    onset_list.append(onset)
                    duration_list.append(0.0)
                    description_list.append(desc)
        except Exception:
            pass
    
    if not onset_list:
        # Fallback: no events found, return empty annotations
        return mne.Annotations(onset=[], duration=[], description=[])
    
    return mne.Annotations(onset=onset_list, duration=duration_list, description=description_list)


class OpenNeuroDS006465Kernel:
    """Stage1 kernel for 3M-CPSEED dataset (openneuro_ds006465).
    
    Handles Chinese Pinyin speech production EEG data with three modes:
    - Overt speech (spoken aloud)
    - Silent-intended (mouthed without sound)
    - Imagined (mental speech)
    
    Channel naming follows standard 10-20 system after renaming from EEG### format.
    """
    
    KERNEL_ID: str = "openneuro-ds006465-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object with EEG data
        row : Locator row with File Path information
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels and metadata
        """
        # Extract subject ID and load metadata
        subject_id = _extract_subject_id(row)
        subject_metadata = _load_participants_data(udataset)
        subj_info = subject_metadata.get(subject_id, {})
        
        # Get original description
        original_desc = raw.info.get("description", "")
        
        # Build eegunity_description
        age = subj_info.get("age", "unknown")
        sex = subj_info.get("sex", "unknown")
        handedness = subj_info.get("handedness", "unknown")
        
        # Update description field
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _DEVICE_METADATA["amplifier"],
                "cap": _DEVICE_METADATA["cap"],
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[Kernel] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)
        
        # Set montage (standard 1020 system)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[Kernel] Could not set montage: {e}")
        
        # Create annotations from events
        file_path = str(row.get("File Path", ""))
        events_dir = os.path.dirname(file_path)
        
        # Look for events.tsv in the same directory
        events_tsv = os.path.join(events_dir, "events.tsv")
        if not os.path.exists(events_tsv):
            # Try parent directory
            events_tsv = os.path.join(os.path.dirname(events_dir), "events.tsv")
        
        annotations = _create_annotations_from_events(raw, events_tsv if os.path.exists(events_tsv) else None)
        raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenNeuroDS006465Kernel()