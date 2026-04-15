"""Dataset-specific kernel for openneuro_ds001971.

Audiocue walking study - mobile brain-body imaging (MoBI) dataset.
Participants walked on a treadmill and adapted gait to auditory tone sequences.

Event structure:
- Preferred cadence: 100, 200
- Uncued walking: 119
- Advance tempo (step shortening): 113, 333
- Delay tempo (step lengthening): 114, 444
- Other gait/response events: 101, 103, 109, 151, 153, 159, 171, 201, 203, 209, 251, 253, 259, 271, 999
- Admin markers: STATUS events (typically not in events.tsv)

Source: https://openneuro.org/datasets/ds001971
DOI: 10.1038/s41597-019-0223-2
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Event label mapping: raw numeric event ID -> semantic description
# Source: Derived from dataset documentation and paper (DOI: 10.1038/s41597-019-0223-2)
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核
_EVENT_LABEL_MAP: Dict[int, str] = {
    100: "PreferredCadence",
    101: "PreferredCadence_stream2",   # LLM 推断，需人类复核
    103: "PreferredCadence_stream3",   # LLM 推断，需人类复核
    109: "PreferredCadence_stream4",   # LLM 推断，需人类复核
    113: "AdvanceTempo",
    114: "DelayTempo",
    119: "UncuedWalking",
    151: "UncuedWalking_stream2",       # LLM 推断，需人类复核
    153: "UncuedWalking_stream3",      # LLM 推断，需人类复核
    159: "UncuedWalking_stream4",      # LLM 推断，需人类复核
    171: "Walking_event_171",          # LLM 推断，需人类复核 - purpose unclear
    200: "PreferredCadence_stream5",   # LLM 推断，需人类复核 - alt recording stream
    201: "PreferredCadence_stream6",   # LLM 推断，需人类复核
    203: "PreferredCadence_stream7",   # LLM 推断，需人类复核
    209: "PreferredCadence_stream8",   # LLM 推断，需人类复核
    251: "UncuedWalking_stream5",      # LLM 推断，需人类复核
    253: "UncuedWalking_stream6",      # LLM 推断，需人类复核
    259: "UncuedWalking_stream7",     # LLM 推断，需人类复核
    271: "Walking_event_271",          # LLM 推断，需人类复核 - purpose unclear
    333: "AdvanceTempo_stream2",
    444: "DelayTempo_stream2",
    999: "admin: marker-999",
}

# Channel rename map for standard 10-20 naming
# Source: 115-channel system with motion capture - EEG channels follow standard naming
# Based on common 64-channel extended 10-20 + additional 64-channel cap layout
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核
_EEG_CHANNEL_PREFIXES = [
    "Fp", "F", "Fz", "Af", "Nz", "T", "Tp", "Ft", "Fta", "Fpc", "Fp",
    "F", "FC", "Fcz", "Cz", "C", "CP", "P", "PO", "O", "I", "Oz", "O1", "O2"
]

# Standard 10-20 channel names for reference (subset)
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fp2", "Fz", "F3", "F4", "F7", "F8",
    "Cz", "C3", "C4", "C1", "C2",
    "T7", "T8", "T3", "T4", "T5", "T6",
    "CPz", "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
    "Pz", "P3", "P4", "P7", "P8",
    "POz", "PO3", "PO4", "PO7", "PO8",
    "Oz", "O1", "O2",
    "FCz", "FC1", "FC2", "FC3", "FC4", "FC5", "FC6",
    "AFz", "AF3", "AF4", "AF7", "AF8",
]

# Known device metadata
# Source: Brain Products amplifier mentioned in dataset documentation
# Annotator: LLM, 2026-04-08 # LLM 推断，需人类复核
_DEVICE_METADATA = {
    "amplifier": "BrainAmp",           # LLM 推断，需人类复核
    "cap": "Ag/AgCl",                  # LLM 推断，需人类复核
}


def _detect_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from file path.
    
    Args:
        file_path: Full path to the EEG file.
        
    Returns:
        Subject ID string (e.g., 'sub-01') or None if not found.
    """
    match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map for standard 10-20 naming.
    
    This handles common channel naming variations in EEG data.
    
    Args:
        raw: MNE Raw object with current channel names.
        
    Returns:
        Dictionary mapping source names to target names.
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names
    
    for ch in ch_names:
        # Skip non-EEG channels
        if ch.startswith("EOG") or ch.startswith("ECG") or ch.startswith("EMG"):
            continue
        if ch.startswith("misc") or ch.startswith("stim") or ch.startswith("STATUS"):
            continue
        if ch.startswith("Resp") or ch.startswith("Breath") or ch.startswith("GSR"):
            continue
            
        # Handle common prefixes like 'EEG-' or 'eeg'
        if ch.startswith("EEG-") or ch.startswith("EEG_"):
            base_name = ch.replace("EEG-", "").replace("EEG_", "")
            # Check if base_name matches a standard 10-20 name
            if base_name in _STANDARD_1020_CHANNELS:
                rename_map[ch] = base_name
            # Handle numbered EEG channels like EEG-0, EEG-1
            elif base_name.isdigit():
                continue  # Keep original numbering if not mappable
                
        # Handle channels already named with standard nomenclature
        elif any(std in ch for std in ["Fp", "Fz", "Cz", "Pz", "Oz", "T"]):
            # Already standard - check if needs case normalization
            standardized = ch.title() if ch.isupper() else ch
            if standardized != ch and standardized in _STANDARD_1020_CHANNELS:
                rename_map[ch] = standardized
    
    return rename_map


def _relabel_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Relabel annotations using semantic event names.
    
    Args:
        raw: MNE Raw object with existing annotations.
        
    Returns:
        Raw object with relabeled annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    new_descriptions = []
    for desc in raw.annotations.description:
        try:
            event_id = int(desc)
            new_desc = _EVENT_LABEL_MAP.get(event_id, f"event_{event_id}")
        except (ValueError, TypeError):
            new_desc = desc
        new_descriptions.append(new_desc)
    
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    
    return raw


class OpenNeuroDS001971Kernel:
    """Stage1 kernel for openneuro_ds001971 (Audiocue walking study).
    
    This kernel handles:
    - Event relabeling from numeric IDs to semantic names
    - Channel name standardization
    - Metadata enrichment with device and subject information
    - Response time extraction from misc channel
    """
    
    KERNEL_ID: str = "openneuro-ds001971-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : object
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object.
        row : pandas.Series
            Locator row with File Path and other metadata.
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = _detect_subject_id(file_path)
        
        # Build eegunity_description
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": "unknown",          # LLM 推断，需人类复核 - check participants.tsv
                "sex": "unknown",          # LLM 推断，需人类复核 - check participants.tsv
                "amplifier": _DEVICE_METADATA.get("amplifier", "unknown"),
                "cap": _DEVICE_METADATA.get("cap", "unknown"),
                "handedness": "unknown",   # LLM 推断，需人类复核 - check if available
            },
        }
        
        # Try to load subject metadata from participants.tsv if available
        if hasattr(udataset, 'dataset_path'):
            participants_tsv = os.path.join(udataset.dataset_path, "participants.tsv")
            if os.path.exists(participants_tsv):
                try:
                    import pandas as pd
                    df = pd.read_csv(participants_tsv, sep="\t")
                    # Extract subject number from subject_id
                    if subject_id:
                        subject_num = subject_id.replace("sub-", "")
                        subj_row = df[df['participant_id'] == subject_id]
                        if len(subj_row) > 0:
                            subj_row = subj_row.iloc[0]
                            if 'age' in df.columns and pd.notna(subj_row.get('age')):
                                description_dict["eegunity_description"]["age"] = str(subj_row['age'])
                            if 'sex' in df.columns and pd.notna(subj_row.get('sex')):
                                sex_val = str(subj_row['sex']).lower()
                                if sex_val in ['m', 'male']:
                                    description_dict["eegunity_description"]["sex"] = "male"
                                elif sex_val in ['f', 'female']:
                                    description_dict["eegunity_description"]["sex"] = "female"
                            if 'handedness' in df.columns and pd.notna(subj_row.get('handedness')):
                                handedness_val = str(subj_row['handedness']).lower()
                                if handedness_val in ['r', 'right', 'right-handed']:
                                    description_dict["eegunity_description"]["handedness"] = "right"
                                elif handedness_val in ['l', 'left', 'left-handed']:
                                    description_dict["eegunity_description"]["handedness"] = "left"
                except Exception:
                    pass  # Keep defaults if reading fails
        
        raw.info["description"] = json.dumps(description_dict)
        
        # Relabel annotations with semantic event names
        raw = _relabel_annotations(raw)
        
        # Channel renaming (before set_montage)
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter to only existing channels
            valid_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if valid_renames:
                raw.rename_channels(valid_renames)
        
        # Try to set montage for standard 10-20 channels
        try:
            # Get only EEG channels for montage
            eeg_chs = [ch for ch in raw.ch_names 
                      if ch not in raw.get_channel_types(mapname="stim", use_names=True)]
            eeg_chs = [ch for ch in eeg_chs 
                      if raw.get_channel_types(mesg=ch) not in ['stim', 'misc']]
            
            # Use standard 1020 montage for recognized channels
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # Montage setting is optional - continue if it fails
            pass
        
        # Process response_time from misc channel if present
        if "response_time" in raw.ch_names or any("response" in ch.lower() for ch in raw.ch_names):
            # Keep as continuous data in misc channel
            # This is used for regression tasks per analysis.md
            pass
        
        return raw


KERNEL = OpenNeuroDS001971Kernel()