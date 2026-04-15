"""OpenNeuro DS006547 stage1 kernel for EEGUnity.

Visual EEG study with high-density EEG (67 channels, 500 Hz, BrainVision system).
Converted to BIDS format. Contains 31 subjects with 30 visual stimulus conditions
(codes S2-S56, excluding S1 and some others).

Source: https://openneuro.org/datasets/ds006547
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


# =============================================================================
# Channel Rename Map for High-Density BrainVision EEG
# =============================================================================
# The dataset contains 67 EEG channels from a BrainVision system.
# Standard 10-20 extended montage (BioSemi-style naming convention).
# Source: Paper analysis / dataset documentation indicates high-density 64+ channel setup
# Annotator: LLM, 2026-04-08 - LLM 推断，需人类复核

# BioSemi 64-channel layout (common for BrainVision high-density systems)
_BIOSEMI_64_CHANNELS = [
    "Fp1", "AF7", "AF3", "AFz", "AF4", "AF8", "F7", "F5", "F3", "F1",
    "Fz", "F2", "F4", "F6", "F8", "FT7", "FC5", "FC3", "FC1", "FCz",
    "FC2", "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "Cz", "C2",
    "C4", "C6", "T8", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4",
    "CP6", "TP8", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "O1", "Oz", "O2"
]

# Additional 3 channels for 67 total (likely EOG or extra EEG)
_EXTRA_CHANNELS = ["EOG-left", "EOG-right", "EOG-central"]


# BrainVision commonly uses 'EEG' prefix or numbered channels
# Try to match against standard naming patterns
def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for BrainVision high-density EEG."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Pattern 1: EEG-001, EEG-002, etc.
    eeg_prefix_pattern = re.compile(r'^EEG[-_]?(\d+)$', re.IGNORECASE)
    
    # Pattern 2: CH01, CH02, etc.
    ch_pattern = re.compile(r'^CH(\d+)$', re.IGNORECASE)
    
    # Pattern 3: Numeric channel names like 1, 2, 3
    numeric_pattern = re.compile(r'^(\d+)$')
    
    # Standard channel names to look for (lowercase for matching)
    standard_names_lower = {name.lower(): name for name in _BIOSEMI_64_CHANNELS + _EXTRA_CHANNELS}
    
    for ch_name in existing_names:
        # Skip already correct names
        if ch_name in standard_names_lower.values():
            continue
            
        # Try EEG-001 pattern
        match = eeg_prefix_pattern.match(ch_name)
        if match:
            idx = int(match.group(1)) - 1  # 1-indexed
            if 0 <= idx < len(_BIOSEMI_64_CHANNELS):
                rename_map[ch_name] = _BIOSEMI_64_CHANNELS[idx]
                continue
        
        # Try CH01 pattern
        match = ch_pattern.match(ch_name)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(_BIOSEMI_64_CHANNELS):
                rename_map[ch_name] = _BIOSEMI_64_CHANNELS[idx]
                continue
        
        # Try numeric pattern
        match = numeric_pattern.match(ch_name)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(_BIOSEMI_64_CHANNELS):
                rename_map[ch_name] = _BIOSEMI_64_CHANNELS[idx]
                continue
        
        # Try case-insensitive direct match
        ch_lower = ch_name.lower()
        if ch_lower in standard_names_lower:
            rename_map[ch_name] = standard_names_lower[ch_lower]
    
    return rename_map


# =============================================================================
# Event Mapping
# =============================================================================
# BrainVision events: Stimulus/S X (with varying whitespace)
# Map to canonical event labels
# Annotator: LLM, 2026-04-08 - LLM 推断，需人类复核

_STIMULUS_CODE_MAP = {
    "S  1": "Stimulus/S  1",
    "S  2": "Stimulus/S  2",
    "S  3": "Stimulus/S  3",
    "S  4": "Stimulus/S  4",
    "S  5": "Stimulus/S  5",
    "S  6": "Stimulus/S  6",
    "S  7": "Stimulus/S  7",
    "S  8": "Stimulus/S  8",
    "S  9": "Stimulus/S  9",
    "S 10": "Stimulus/S 10",
    "S 11": "Stimulus/S 11",
    "S 12": "Stimulus/S 12",
    "S 13": "Stimulus/S 13",
    "S 14": "Stimulus/S 14",
    "S 15": "Stimulus/S 15",
    "S 16": "Stimulus/S 16",
    "S 17": "Stimulus/S 17",
    "S 18": "Stimulus/S 18",
    "S 19": "Stimulus/S 19",
    "S 20": "Stimulus/S 20",
    "S 21": "Stimulus/S 21",
    "S 22": "Stimulus/S 22",
    "S 41": "Stimulus/S 41",
    "S 42": "Stimulus/S 42",
    "S 43": "Stimulus/S 43",
    "S 44": "Stimulus/S 44",
    "S 45": "Stimulus/S 45",
    "S 46": "Stimulus/S 46",
    "S 47": "Stimulus/S 47",
    "S 48": "Stimulus/S 48",
    "S 49": "Stimulus/S 49",
    "S 50": "Stimulus/S 50",
    "S 51": "Stimulus/S 51",
    "S 52": "Stimulus/S 52",
    "S 53": "Stimulus/S 53",
    "S 54": "Stimulus/S 54",
    "S 55": "Stimulus/S 55",
    "S 56": "Stimulus/S 56",
}


def _normalize_stimulus_code(description: str) -> str:
    """Normalize BrainVision stimulus code to canonical format."""
    if description in _STIMULUS_CODE_MAP:
        return _STIMULUS_CODE_MAP[description]
    
    # Handle formats like "S  1" (double space) vs "S 1" (single space)
    match = re.match(r'^S\s+(\d+)$', description.strip())
    if match:
        code_num = int(match.group(1))
        # Try to find closest match
        for pattern, canonical in _STIMULUS_CODE_MAP.items():
            if f"S {code_num}" in pattern or f"S  {code_num}" in pattern:
                return canonical
    
    return description


# =============================================================================
# Subject Info
# =============================================================================
# Age and sex information not available in dataset metadata
# Annotator: LLM, 2026-04-08 - LLM 推断，需人类复核

_SUBJECT_INFO_FALLBACK = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "BrainVision",  # LLM 推断，需人类复核 - Based on BrainVision system mentioned in dataset
    "cap": "unknown",  # LLM 推断，需人类复核 - High-density cap type not specified
    "handedness": "unknown",
}


def _load_subject_info_from_bids(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load subject info from BIDS participants.tsv if available."""
    participants_tsv = os.path.join(dataset_path, "participants.tsv")
    
    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Match subject_id format (e.g., "sub-01" or "01")
            subj_col = None
            for col in df.columns:
                if "sub" in col.lower() or "participant" in col.lower():
                    subj_col = col
                    break
            
            if subj_col:
                # Normalize subject_id for matching
                normalized_id = subject_id.replace("sub-", "").replace("sub_", "")
                row = df[df[subj_col].astype(str).str.replace("sub-", "").str.replace("sub_", "") == normalized_id]
                
                if len(row) > 0:
                    info = _SUBJECT_INFO_FALLBACK.copy()
                    
                    # Try to get age
                    age_cols = [c for c in df.columns if "age" in c.lower()]
                    if age_cols:
                        age_val = row[age_cols[0]].values[0]
                        if pd.notna(age_val):
                            info["age"] = str(int(age_val)) if isinstance(age_val, (int, float)) else str(age_val)
                    
                    # Try to get sex
                    sex_cols = [c for c in df.columns if "sex" in c.lower() or "gender" in c.lower()]
                    if sex_cols:
                        sex_val = row[sex_cols[0]].values[0]
                        if pd.notna(sex_val):
                            sex_str = str(sex_val).lower().strip()
                            if sex_str in ["m", "male", "f", "female"]:
                                info["sex"] = "male" if sex_str.startswith("m") else "female"
                    
                    return info
        except Exception:
            pass
    
    return _SUBJECT_INFO_FALLBACK.copy()


@dataclass
class OpenNeuroDS006547Kernel:
    """Stage1 kernel for the OpenNeuro DS006547 visual EEG dataset."""

    KERNEL_ID: str = "openneuro-ds006547-stage1"

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
            The modified Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", "unknown")
        dataset_path = row.get("Dataset Path", "")
        
        # -------------------------------------------------------------------------
        # Step 1: Channel renaming
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        
        if rename_map:
            # Get channels that need renaming and will become EEG
            eeg_channels_to_rename = {k: v for k, v in rename_map.items() 
                                       if v in _BIOSEMI_64_CHANNELS}
            other_rename = {k: v for k, v in rename_map.items() 
                           if v not in _BIOSEMI_64_CHANNELS}
            
            # Apply EEG channel renames
            if eeg_channels_to_rename:
                raw.rename_channels(eeg_channels_to_rename)
            
            # Apply other channel renames
            if other_rename:
                raw.rename_channels(other_rename)
            
            # Set channel types for EOG channels
            eog_channels = [v for v in other_rename.values() 
                           if v.startswith("EOG")]
            if eog_channels:
                for ch in eeg_channels_to_rename.values():
                    if ch in _EXTRA_CHANNELS:
                        eog_channels.append(ch)
                try:
                    raw.set_channel_types({ch: "eog" for ch in eog_channels if ch in raw.ch_names})
                except Exception:
                    pass
        
        # -------------------------------------------------------------------------
        # Step 2: Set montage
        # -------------------------------------------------------------------------
        # Use standard 1020 montage for 67-channel setup
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Get EEG channels in raw (intersection with montage)
            available_eeg = [ch for ch in raw.ch_names 
                            if ch in montage.ch_names and 
                            ch not in ["EOG-left", "EOG-right", "EOG-central"]]
            
            if len(available_eeg) >= 20:  # Only set montage if we have enough channels
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is optional if channels don't match
        
        # -------------------------------------------------------------------------
        # Step 3: Update description with eegunity_description
        # -------------------------------------------------------------------------
        subject_info = _load_subject_info_from_bids(dataset_path, subject_id)
        
        original_desc = raw.info.get("description", "")
        if not original_desc or original_desc == "None":
            original_desc = ""
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": subject_info["amplifier"],
                "cap": subject_info["cap"],
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # -------------------------------------------------------------------------
        # Step 4: Normalize events/annotations
        # -------------------------------------------------------------------------
        # Get current annotations
        try:
            annotations = raw.annotations
            if len(annotations) > 0:
                # Normalize stimulus descriptions
                new_descriptions = []
                for desc in annotations.description:
                    new_desc = _normalize_stimulus_code(desc)
                    new_descriptions.append(new_desc)
                
                # Create new annotations with normalized descriptions
                new_annotations = mne.Annotations(
                    onset=annotations.onset,
                    duration=annotations.duration,
                    description=new_descriptions,
                    orig_time=annotations.orig_time,
                )
                raw.set_annotations(new_annotations)
        except Exception:
            pass
        
        # -------------------------------------------------------------------------
        # Step 5: Check for stimulus channel (STIM/MRK) and convert to annotations
        # -------------------------------------------------------------------------
        stim_channels = [ch for ch in raw.ch_names 
                        if "stim" in ch.lower() or "mrk" in ch.lower() or 
                        "trigger" in ch.lower()]
        
        if stim_channels:
            # Extract events from stimulus channel
            for stim_ch in stim_channels:
                try:
                    stim_data, times = raw[stim_ch, :]
                    stim_data = stim_data.flatten()
                    
                    # Find rising edges (event onsets)
                    threshold = np.mean(stim_data) + 2 * np.std(stim_data)
                    rising_edges = np.where(np.diff(stim_data > threshold) > 0)[0]
                    
                    if len(rising_edges) > 0:
                        # Get event values
                        event_values = stim_data[rising_edges + 1]
                        event_times = times[rising_edges + 1]
                        
                        # Create event descriptions
                        event_descriptions = [f"Stimulus/S {int(v)}" for v in event_values]
                        
                        # Add as annotations if we don't have any yet
                        current_annotations = raw.annotations
                        if len(current_annotations) == 0 or \
                           all(d.startswith("BAD_") for d in current_annotations.description):
                            new_annotations = mne.Annotations(
                                onset=event_times,
                                duration=[0] * len(event_times),
                                description=event_descriptions,
                            )
                            raw.set_annotations(new_annotations)
                except Exception:
                    pass
        
        return raw


KERNEL = OpenNeuroDS006547Kernel()