"""Stage1 kernel for openneuro_ds003518.

Simon Conflict Task with Reinforcement and Cabergoline Challenge.
64-channel EEG, 500 Hz, BIDS format (.set files with EEGLAB format).

Source: https://openneuro.org/datasets/ds003518
References:
  - Cavanagh et al. (2014) Nat Commun 5:5394. DOI: 10.1038/ncomms6394
  - Dataset uses BrainVision format with .eeg, .vhdr, .vmrk files

This kernel handles:
- Channel renaming to standard 10-20 montage
- Metadata extraction from participants.tsv
- Event annotation from events.tsv (EEGLAB .set files may not carry events)
- Derived misc channels: feedback_value, response_time from events.tsv
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Dataset-specific constants
# =============================================================================

DATASET_ID = "openneuro_ds003518"
KERNEL_ID = "openneuro_ds003518"

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex", "handedness", "amplifier", "cap"]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = ["feedback_value", "response_time"]

# Standard 64-channel extended 10-20 layout used in this dataset
# Source: BrainVision standard 64-channel cap, common in conflict/RL EEG studies
# Annotator: LLM inferred from dataset documentation and standard practices, 2026-04-08
# inferred by LLM, needs human review
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "FCz",  # sometimes included separately
]

# BrainVision/EEGLAB common aliases to standard 10-20 names
# Source: Standard BrainVision 64-channel naming conventions
# Annotator: LLM, 2026-04-08
# inferred by LLM, needs human review
_CHANNEL_ALIASES: Dict[str, List[str]] = {
    "Fp1": ["Fp1", "EEG Fp1", "EEG-Fp1", "FP1"],
    "Fpz": ["Fpz", "EEG Fpz", "EEG-Fpz", "FPz"],
    "Fp2": ["Fp2", "EEG Fp2", "EEG-Fp2", "FP2"],
    "AF7": ["AF7", "EEG AF7", "EEG-AF7"],
    "AF3": ["AF3", "EEG AF3", "EEG-AF3"],
    "AFz": ["AFz", "EEG AFz", "EEG-AFz"],
    "AF4": ["AF4", "EEG AF4", "EEG-AF4"],
    "AF8": ["AF8", "EEG AF8", "EEG-AF8"],
    "F7": ["F7", "EEG F7", "EEG-F7"],
    "F5": ["F5", "EEG F5", "EEG-F5"],
    "F3": ["F3", "EEG F3", "EEG-F3"],
    "F1": ["F1", "EEG F1", "EEG-F1"],
    "Fz": ["Fz", "EEG Fz", "EEG-Fz", "FZ"],
    "F2": ["F2", "EEG F2", "EEG-F2"],
    "F4": ["F4", "EEG F4", "EEG-F4"],
    "F6": ["F6", "EEG F6", "EEG-F6"],
    "F8": ["F8", "EEG F8", "EEG-F8"],
    "FT7": ["FT7", "EEG FT7", "EEG-FT7"],
    "FT5": ["FT5", "EEG FT5", "EEG-FT5"],
    "FT3": ["FT3", "EEG FT3", "EEG-FT3"],
    "FT1": ["FT1", "EEG FT1", "EEG-FT1"],
    "FTz": ["FTz", "EEG FTz", "EEG-FTz"],
    "FT2": ["FT2", "EEG FT2", "EEG-FT2"],
    "FT4": ["FT4", "EEG FT4", "EEG-FT4"],
    "FT6": ["FT6", "EEG FT6", "EEG-FT6"],
    "FT8": ["FT8", "EEG FT8", "EEG-FT8"],
    "T7": ["T7", "EEG T7", "EEG-T7", "T3"],  # T3 is older 10-20 name
    "C5": ["C5", "EEG C5", "EEG-C5"],
    "C3": ["C3", "EEG C3", "EEG-C3"],
    "C1": ["C1", "EEG C1", "EEG-C1"],
    "Cz": ["Cz", "EEG Cz", "EEG-Cz", "CZ"],
    "C2": ["C2", "EEG C2", "EEG-C2"],
    "C4": ["C4", "EEG C4", "EEG-C4"],
    "C6": ["C6", "EEG C6", "EEG-C6"],
    "T8": ["T8", "EEG T8", "EEG-T8", "T4"],  # T4 is older 10-20 name
    "TP7": ["TP7", "EEG TP7", "EEG-TP7", "T5"],  # T5 is older 10-20 name
    "TP5": ["TP5", "EEG TP5", "EEG-TP5"],
    "TP3": ["TP3", "EEG TP3", "EEG-TP3"],
    "TP1": ["TP1", "EEG TP1", "EEG-TP1"],
    "TPz": ["TPz", "EEG TPz", "EEG-TPz"],
    "TP2": ["TP2", "EEG TP2", "EEG-TP2"],
    "TP4": ["TP4", "EEG TP4", "EEG-TP4"],
    "TP6": ["TP6", "EEG TP6", "EEG-TP6"],
    "TP8": ["TP8", "EEG TP8", "EEG-TP8", "T6"],  # T6 is older 10-20 name
    "P7": ["P7", "EEG P7", "EEG-P7"],
    "P5": ["P5", "EEG P5", "EEG-P5"],
    "P3": ["P3", "EEG P3", "EEG-P3"],
    "P1": ["P1", "EEG P1", "EEG-P1"],
    "Pz": ["Pz", "EEG Pz", "EEG-Pz", "PZ"],
    "P2": ["P2", "EEG P2", "EEG-P2"],
    "P4": ["P4", "EEG P4", "EEG-P4"],
    "P6": ["P6", "EEG P6", "EEG-P6"],
    "P8": ["P8", "EEG P8", "EEG-P8"],
    "PO7": ["PO7", "EEG PO7", "EEG-PO7"],
    "PO3": ["PO3", "EEG PO3", "EEG-PO3"],
    "POz": ["POz", "EEG POz", "EEG-POz"],
    "PO4": ["PO4", "EEG PO4", "EEG-PO4"],
    "PO8": ["PO8", "EEG PO8", "EEG-PO8"],
    "O1": ["O1", "EEG O1", "EEG-O1"],
    "Oz": ["Oz", "EEG Oz", "EEG-Oz"],
    "O2": ["O2", "EEG O2", "EEG-O2"],
    "FCz": ["FCz", "EEG FCz", "EEG-FCz"],
}

# Event codes from the task requirements
# Source: analysis.md and task synthesizer
_STIMULUS_CODES = {
    "S111", "S112", "S113", "S114",
    "S121", "S122", "S123", "S124",
    "S211", "S212", "S213", "S214",
    "S221", "S222", "S223", "S224",
}
_RESPONSE_CODES = {"S101", "S102", "S105"}
_FEEDBACK_CODES = {"S  8", "S  9"}

# Congruency mapping: second digit indicates congruency
# Source: Cavanagh et al. 2014, primary publication
# 1 = congruent, 2 = incongruent
_CONGRUENCY_MAP = {
    "S111": 0, "S112": 0, "S113": 0, "S114": 0,
    "S211": 0, "S212": 0, "S213": 0, "S214": 0,
    "S121": 1, "S122": 1, "S123": 1, "S124": 1,
    "S221": 1, "S222": 1, "S223": 1, "S224": 1,
}

# Color mapping: first digit indicates color
# 1 = yellow, 2 = blue
_COLOR_MAP = {
    "S111": 0, "S112": 0, "S113": 0, "S114": 0,
    "S121": 1, "S122": 1, "S123": 1, "S124": 1,
    "S211": 2, "S212": 2, "S213": 2, "S214": 2,
    "S221": 3, "S222": 3, "S223": 3, "S224": 3,
}


# =============================================================================
# Helper functions
# =============================================================================

def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for standard_name, aliases in _CHANNEL_ALIASES.items():
        if standard_name in existing:
            continue  # Already correct
        for alias in aliases:
            if alias in existing and alias not in rename_map:
                rename_map[alias] = standard_name
                break
    
    return rename_map


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.isfile(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv for a given EEG file."""
    # BIDS convention: same directory, same basename with _events.tsv suffix
    # Use str.replace() on the string, not Path.replace()
    file_path_str = str(file_path)
    base = file_path_str.replace(".eeg", "").replace(".vhdr", "").replace(".vmrk", "").replace(".set", "").replace(".fdt", "")
    # Handle common BIDS patterns
    dirname = os.path.dirname(file_path_str)
    basename = os.path.basename(base)
    
    # Try direct sibling
    direct = os.path.join(dirname, basename + "_events.tsv")
    if os.path.isfile(direct):
        return direct
    
    # Try without run/task suffix variations
    # Pattern: sub-XX_task-YYY_run-ZZ_eeg -> sub-
    # Try subject-level directory
    sub_dir = dirname
    while sub_dir and not os.path.basename(sub_dir).startswith("sub-"):
        sub_dir = os.path.dirname(sub_dir)
    if sub_dir:
        sub_basename = os.path.basename(sub_dir)
        # Look for any events.tsv in the subject's directories
        for root, dirs, files in os.walk(sub_dir):
            for f in files:
                if f.endswith("_events.tsv"):
                    return os.path.join(root, f)
    
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read participant info from participants.tsv for a given subject."""
    df = pd.read_csv(participants_path, sep="\t")
    # Subject ID might be 'sub-01' or just '01'
    if "participant_id" in df.columns:
        # Try exact match first
        mask = df["participant_id"] == subject_id
        if not mask.any():
            # Try with/without sub- prefix
            alt_id = subject_id.replace("sub-", "") if subject_id.startswith("sub-") else "sub-" + subject_id
            mask = df["participant_id"] == alt_id
        if mask.any():
            row = df[mask].iloc[0]
            return {k: str(v) for k, v in row.to_dict().items()}
    return {}


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events from events.tsv."""
    return pd.read_csv(events_path, sep="\t")


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    # BIDS pattern: sub-XX/... or sub-XX_...
    basename = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    
    # Try from basename
    if basename.startswith("sub-"):
        parts = basename.split("_")
        return parts[0]
    
    # Try from directory path
    path_parts = file_path.replace("\\", "/").split("/")
    for part in path_parts:
        if part.startswith("sub-"):
            return part
    
    return ""


def _create_misc_channel(raw: mne.io.BaseRaw, name: str, data: np.ndarray) -> mne.io.BaseRaw:
    """Create a misc channel and add it to the raw object."""
    # Ensure data is correct shape
    if data.ndim == 1:
        data = data.reshape(1, -1)
    
    # Create info for misc channel
    misc_info = mne.create_info([name], raw.info["sfreq"], ["misc"])
    misc_raw = mne.io.RawArray(data, misc_info, first_samp=raw.first_samp)
    
    # Add to raw
    raw.add_channels([misc_raw], force_update_info=True)
    return raw


class OpenneuroDs003518Kernel:
    """Kernel for openneuro_ds003518 dataset."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row
        file_path = str(row.get("File Path", ""))
        if not file_path:
            file_path = str(row.get("file_path", ""))
        
        # Extract subject ID
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Read participants.tsv for metadata
        participants_path = _find_participants_tsv(file_path)
        participant_info = {}
        if participants_path:
            participant_info = _read_participants_info(participants_path, subject_id)
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": participant_info.get("age", ""),
            "sex": participant_info.get("sex", ""),
            "amplifier": participant_info.get("amplifier", ""),
            "cap": participant_info.get("cap", ""),
            "handedness": participant_info.get("handedness", ""),
        }
        
        # Set description
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Channel renaming to standard 10-20
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # ============================================
        # CRITICAL FIX: Load events from events.tsv
        # ============================================
        # EEGLAB .set files in this dataset have empty event fields
        # Events MUST come from the sibling events.tsv files
        events_path = _find_events_tsv(file_path)
        
        if events_path and os.path.isfile(events_path):
            events_df = _read_events_tsv(events_path)
            
            # Build annotations from events.tsv using the 'value' column as trigger codes
            # The 'value' column contains the actual trigger codes (S224, S102, S  9, etc.)
            # per events.json: "value": {"Description": "Trigger Code"}
            onsets = []
            durations = []
            descriptions = []
            
            for _, event_row in events_df.iterrows():
                onset = event_row.get("onset")
                value = event_row.get("value")
                
                # Skip rows with missing onset or value
                if pd.isna(onset) or pd.isna(value):
                    continue
                
                # Skip boundary events (not actual triggers)
                value_str = str(value).strip()
                if value_str.lower() == "boundary":
                    continue
                
                # Use the literal value string as the annotation description
                # This preserves all event IDs exactly as they appear in the TSV
                onsets.append(float(onset))
                durations.append(0.0)  # Instant events
                descriptions.append(value_str)
            
            # Create and set annotations on the raw object
            if onsets:
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=raw.info.get("meas_date")
                )
                raw.set_annotations(annotations)
            
            # ============================================
            # Create derived misc channels from events.tsv
            # ============================================
            # feedback_value: numeric feedback from FB events
            # response_time: response time from response events
            
            # Build continuous misc channels aligned to raw time
            n_samples = raw.n_times
            sfreq = raw.info["sfreq"]
            times = raw.times  # seconds from raw.first_samp / sfreq
            
            feedback_values = np.full(n_samples, np.nan)
            response_times = np.full(n_samples, np.nan)
            
            for _, event_row in events_df.iterrows():
                onset = event_row.get("onset")
                if pd.isna(onset):
                    continue
                
                onset_sec = float(onset)
                # Find closest sample index
                sample_idx = int(round((onset_sec - raw.first_time) * sfreq))
                if sample_idx < 0 or sample_idx >= n_samples:
                    continue
                
                value = str(event_row.get("value", "")).strip()
                trial_type = str(event_row.get("trial_type", "")).strip()
                
                # Extract feedback value from FB events
                if "FB:" in trial_type:
                    fb_str = trial_type.replace("FB:", "").strip()
                    try:
                        feedback_values[sample_idx] = float(fb_str)
                    except ValueError:
                        pass
                
                # Extract response time from response events
                rt = event_row.get("response_time")
                if pd.notna(rt):
                    try:
                        response_times[sample_idx] = float(rt)
                    except (ValueError, TypeError):
                        pass
            
            # Add misc channels (only if we have valid data)
            if not np.all(np.isnan(feedback_values)):
                raw = _create_misc_channel(raw, "feedback_value", feedback_values)
            
            if not np.all(np.isnan(response_times)):
                raw = _create_misc_channel(raw, "response_time", response_times)
        
        return raw


KERNEL = OpenneuroDs003518Kernel()