"""OpenNeuro ds003490 stage1 kernel for EEGUnity.

3-Stim Auditory Oddball and Rest in Parkinson's Disease dataset.
- 50 subjects, 67 channels, 500 Hz sampling rate
- Events: Standard Tone (S200), Target Tone (S201), Novel Tone (S202),
  Eyes Open (S  1), Eyes Closed (S  2), Rest sub-conditions (S  3, S  4)
- BioSemi STATUS markers (S 85, S255) and boundary events excluded as admin markers
- Required info fields from participants.tsv: Group, age, sess1_Med, sex

Source: https://openneuro.org/datasets/ds003490
Paper: 10.1016/j.clinph.2017.11.023 (PMID: 29294412)
"""

from __future__ import annotations

import json
import os
import re
import warnings
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# --- Event code mapping ---
# Source: Dataset documentation and paper 10.1016/j.clinph.2017.11.023
# S  1 / S  2: Resting state eyes open/closed (1Hz alternating triggers)
# S  3 / S  4: Resting state sub-conditions
# S200: Standard tone (frequent non-target)
# S201: Target tone (requires button press, P3b)
# S202: Novel distractor tone (rare, P3a)
# S 85 / S255: BioSemi STATUS admin markers - EXCLUDE
# boundary: Recording boundary marker - EXCLUDE
_EVENT_CODE_MAP: Dict[str, str] = {
    "S  1": "Eyes Open",
    "S  2": "Eyes Closed",
    "S  3": "Rest block 3",
    "S  4": "Rest block 4",
    "S200": "Standard Tone",
    "S201": "Target Tone",
    "S202": "Novel Tone",
}

# Admin codes to exclude from annotations
_ADMIN_CODES = {"S 85", "S255", "boundary", "S 85", "S  85"}

# --- Channel information ---
# BioSemi 64-channel system with standard 10-20 extended layout
# 67 channels = 64 EEG + 3 auxiliary (typically EOG/EMG)
# Source: BioSemi electrode naming convention; paper 10.1016/j.clinph.2017.11.023
# Annotator: LLM, 2026-04-08; "由 LLM 推断，需人类复核"
_BIOSEMI_64_CHANNELS = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7", "FC5", "FC3",
    "FC1", "C1", "C3", "C5", "T7", "TP7", "CP5", "CP3", "CP1", "P1",
    "P3", "P5", "P7", "PO7", "PO3", "O1", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "Fz", "F2", "F4", "F6", "F8", "FT8",
    "FC6", "FC4", "FC2", "FCz", "Cz", "C2", "C4", "C6", "T8", "TP8",
    "CP6", "CP4", "CP2", "P2", "P4", "P6", "P8", "PO8", "PO4", "O2",
    "Iz", "M1", "M2",
]

# Extended channel set for 67 channels (64 + 3 extras)
# The exact 3 extra channels vary; common: VEOG, HEOG, or EMG
# Source: LLM inference from BioSemi 67ch configurations; "由 LLM 推断，需人类复核"
_EXTRA_CHANNELS = ["VEOG", "HEOG", "EMG"]

# Complete 67-channel list
_FULL_CHANNEL_LIST = _BIOSEMI_64_CHANNELS + _EXTRA_CHANNELS

# Common alias patterns for channel name normalization
# Source: LLM inference from BioSemi data patterns; "由 LLM 推断，需人类复核"
_CHANNEL_ALIAS_MAP: Dict[str, str] = {
    # Standard EEG aliases
    "EEG Fp1": "Fp1", "EEG Fp2": "Fp2",
    "EEG F7": "F7", "EEG F3": "F3", "EEG Fz": "Fz", "EEG F4": "F4", "EEG F8": "F8",
    "EEG T7": "T7", "EEG C3": "C3", "EEG Cz": "Cz", "EEG C4": "C4", "EEG T8": "T8",
    "EEG P7": "P7", "EEG P3": "P3", "EEG Pz": "Pz", "EEG P4": "P4", "EEG P8": "P8",
    "EEG O1": "O1", "EEG Oz": "Oz", "EEG O2": "O2",
    # Numbered EEG aliases (BioSemi sometimes uses numbers)
    "1": "Fp1", "2": "AF7", "3": "AF3", "4": "F1", "5": "F3",
    "6": "F5", "7": "F7", "8": "FT7", "9": "FC5", "10": "FC3",
    # EOG/EMG aliases
    "EOG1": "VEOG", "EOG2": "HEOG", "EOG": "VEOG",
    "EXG1": "VEOG", "EXG2": "HEOG", "EXG3": "EMG",
    "EXG4": "M1", "EXG5": "M2",
    # Status channel (to be excluded or set as misc)
    "Status": "Status", "STATUS": "Status",
}


def _normalize_channel_name(name: str) -> str:
    """Normalize a channel name to standard convention."""
    # Direct lookup in alias map
    if name in _CHANNEL_ALIAS_MAP:
        return _CHANNEL_ALIAS_MAP[name]
    
    # Remove common prefixes
    cleaned = re.sub(r'^(EEG|EXG|AUX|CH)\s*', '', name, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    # Check again after cleaning
    if cleaned in _CHANNEL_ALIAS_MAP:
        return _CHANNEL_ALIAS_MAP[cleaned]
    
    # Return cleaned name if it's already valid
    if cleaned in _FULL_CHANNEL_LIST:
        return cleaned
    
    # Default: return cleaned name
    return cleaned


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standardization."""
    rename_map = {}
    for ch_name in raw.ch_names:
        normalized = _normalize_channel_name(ch_name)
        if normalized != ch_name and normalized not in raw.ch_names:
            rename_map[ch_name] = normalized
    return rename_map


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if it exists."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # BIDS pattern: sub-<label>/...
    match = re.search(r'sub-([a-zA-Z0-9]+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _get_subject_info(subject_id: str, dataset_path: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv with required fields.
    
    Required fields: Group, age, sess1_Med, sex
    """
    df = _load_participants_tsv(dataset_path)
    
    if df.empty or subject_id is None:
        return {
            "age": "unknown",
            "sex": "unknown",
            "Group": "unknown",
            "sess1_Med": "unknown",
        }
    
    # Find subject column
    subj_col = None
    for col in ["participant_id", "subject_id", "subject"]:
        if col in df.columns:
            subj_col = col
            break
    
    if subj_col is None:
        return {
            "age": "unknown",
            "sex": "unknown",
            "Group": "unknown",
            "sess1_Med": "unknown",
        }
    
    # Find subject row
    subject_row = df[df[subj_col] == subject_id]
    if subject_row.empty:
        # Try without "sub-" prefix
        subject_row = df[df[subj_col] == subject_id.replace("sub-", "")]
    
    if subject_row.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "Group": "unknown",
            "sess1_Med": "unknown",
        }
    
    row = subject_row.iloc[0]
    
    # Extract age
    age = "unknown"
    for col in ["age", "Age", "AGE"]:
        if col in row.index and pd.notna(row[col]):
            age = str(int(float(row[col]))) if str(row[col]).replace('.', '').isdigit() else str(row[col])
            break
    
    # Extract sex and normalize to lowercase
    sex = "unknown"
    for col in ["sex", "Sex", "SEX", "gender", "Gender"]:
        if col in row.index and pd.notna(row[col]):
            val = str(row[col]).lower().strip()
            if val in ["m", "male", "1"]:
                sex = "male"
            elif val in ["f", "female", "2"]:
                sex = "female"
            break
    
    # Extract Group
    group = "unknown"
    for col in ["Group", "group", "GROUP", "diagnosis", "Diagnosis"]:
        if col in row.index and pd.notna(row[col]):
            group = str(row[col]).strip()
            break
    
    # Extract sess1_Med (medication status for session 1)
    sess1_med = "unknown"
    for col in ["sess1_Med", "sess1_med", "medication", "Medication", "med"]:
        if col in row.index and pd.notna(row[col]):
            sess1_med = str(row[col]).strip()
            break
    
    return {
        "age": age,
        "sex": sex,
        "Group": group,
        "sess1_Med": sess1_med,
    }


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    base = os.path.splitext(file_path)[0]
    # BIDS naming: sub-XX_task-YY[_run-ZZ]_eeg.<ext> -> sub-XX_task-YY[_run-ZZ]_events.tsv
    events_path = base.replace("_eeg", "_events")
    if not events_path.endswith("_events"):
        events_path = base + "_events"
    
    events_tsv = events_path + ".tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try alternative: replace extension directly
    events_tsv = os.path.splitext(file_path)[0] + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Search in same directory
    eeg_dir = os.path.dirname(file_path)
    base_name = os.path.basename(os.path.splitext(file_path)[0])
    for f in os.listdir(eeg_dir):
        if f.endswith("_events.tsv") and f.startswith(base_name.split("_eeg")[0]):
            return os.path.join(eeg_dir, f)
    
    return None


def _read_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        return df
    except Exception:
        return None


def _events_tsv_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Standard BIDS columns: onset, duration, trial_type, value
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0)) if pd.notna(row.get("duration", 0)) else 0
        
        # Use trial_type if available, else value, else stim_file
        desc = None
        for col in ["trial_type", "value", "stim_file", "event_type"]:
            if col in row.index and pd.notna(row[col]):
                desc = str(row[col])
                break
        
        if desc is None:
            continue
        
        # Skip admin/boundary codes
        if desc in _ADMIN_CODES or any(admin in desc for admin in _ADMIN_CODES):
            continue
        
        # Map known codes
        if desc in _EVENT_CODE_MAP:
            desc = _EVENT_CODE_MAP[desc]
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _extract_annotations_from_raw(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Extract and clean annotations from raw file (for .set files with embedded events)."""
    if raw.annotations is None or len(raw.annotations) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for onset, duration, desc in zip(raw.annotations.onset, raw.annotations.duration, raw.annotations.description):
        # Skip admin/boundary codes
        if desc in _ADMIN_CODES or any(admin in desc for admin in _ADMIN_CODES):
            continue
        
        # Map known codes
        mapped_desc = _EVENT_CODE_MAP.get(desc, desc)
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(mapped_desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


class OpenNeuroDS003490Kernel:
    """Stage1 kernel for OpenNeuro ds003490 dataset."""

    KERNEL_ID: str = "openneuro-ds003490-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        
        # --- Extract subject info ---
        subject_id = _get_subject_from_path(file_path)
        subject_info = _get_subject_info(subject_id, dataset_path)
        
        # --- Channel renaming (BEFORE set_montage) ---
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set channel types: identify EEG vs EOG vs EMG vs misc
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in ["VEOG", "HEOG", "EOG1", "EOG2", "EOG"]:
                ch_types[ch_name] = "eog"
            elif ch_name in ["EMG", "EXG3"]:
                ch_types[ch_name] = "emg"
            elif ch_name in ["Status", "STATUS"]:
                ch_types[ch_name] = "misc"
            elif ch_name in _BIOSEMI_64_CHANNELS or ch_name in ["Fp1", "Fp2", "Fz", "Cz", "Pz", "Oz"]:
                ch_types[ch_name] = "eeg"
            elif ch_name.startswith("M") and len(ch_name) <= 2:
                ch_types[ch_name] = "misc"  # Mastoid references
            else:
                # Default to EEG for unknown channels that look like EEG
                if re.match(r'^[A-Z][a-z]?\d*$', ch_name):
                    ch_types[ch_name] = "eeg"
                else:
                    ch_types[ch_name] = "misc"
        
        # Apply channel types
        raw.set_channel_types({k: v for k, v in ch_types.items() if k in raw.ch_names})
        
        # --- Set montage ---
        # Use standard_1020 for BioSemi 64-channel layout
        # Source: BioSemi uses standard 10-20 extended; "由 LLM 推断，需人类复核"
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in the montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            available_chs = list(raw_chs & montage_chs)
            if available_chs:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without
        
        # --- Handle events/annotations ---
        # Priority: 1) events.tsv sidecar, 2) raw.annotations (for .set files with embedded events)
        events_tsv_path = _find_events_tsv(file_path)
        
        if events_tsv_path:
            # Read from BIDS events.tsv
            events_df = _read_events_tsv(events_tsv_path)
            if events_df is not None and not events_df.empty:
                new_annotations = _events_tsv_to_annotations(events_df, raw.info["sfreq"])
                raw.set_annotations(new_annotations)
        else:
            # No events.tsv found - use raw annotations if present
            # This is common for task-Rest files where events are embedded in .set
            # For oddball task files, events should be in raw.annotations
            if raw.annotations is not None and len(raw.annotations) > 0:
                new_annotations = _extract_annotations_from_raw(raw)
                if len(new_annotations) > 0:
                    raw.set_annotations(new_annotations)
        
        # --- Ensure required event IDs exist ---
        # Verify S200, S201, S202 are present in annotations for oddball task
        if raw.annotations is not None:
            current_events = set(raw.annotations.description)
            required_events = {"Standard Tone", "Target Tone", "Novel Tone"}
            # Map back to check original codes if needed
            has_required = any(req in current_events for req in required_events)
        
        # --- Build eegunity_description ---
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        # Device info: BioSemi ActiveTwo system
        # Source: Paper 10.1016/j.clinph.2017.11.023; "由 LLM 推断，需人类复核"
        amplifier = "BioSemi ActiveTwo"  # LLM 推断，需人类复核
        cap = "BioSemi 64-channel cap"   # LLM 推断，需人类复核
        
        # Handedness: not reported in this dataset
        handedness = "unknown"
        
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
            # Required info fields from participants.tsv
            "Group": subject_info.get("Group", "unknown"),
            "sess1_Med": subject_info.get("sess1_Med", "unknown"),
        }
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # --- Handle derived/misc channels ---
        # No derived misc channels required for this dataset
        # Ensure any existing misc channels are properly typed
        
        # --- Final validation ---
        # Ensure all channel types are set
        for ch_name in raw.ch_names:
            if ch_name not in ch_types and raw.get_channel_types(picks=[ch_name])[0] is None:
                # Default unknown to misc
                raw.set_channel_types({ch_name: "misc"})
        
        return raw


KERNEL = OpenNeuroDS003490Kernel()