"""Dataset-specific kernel for openneuro_ds003039 (Free Walking Study).

This kernel handles the free-walking EEG dataset with mobile EEG recordings.
Events (button presses, heel strikes, toe-offs, steps) are sourced from BIDS
*_events.tsv sidecar files. The dataset uses a 64+3 channel mobile EEG system
with BioSemi ActiveTwo amplifier and standard 1020 cap layout.

Source: https://openneuro.org/datasets/ds003039
DOI: https://doi.org/10.18112/openneuro.ds003039.v1.0.2
Paper: 10.1111/ejn.14965 (Jacobsen et al., 2020)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Device Metadata (from paper 10.1111/ejn.14965)
# Annotator: LLM, 2026-04-08 — 需人类复核
# ============================================================================
_AMPLIFIER = "BioSemi ActiveTwo"
_CAP = "BioSemi 64-channel cap with standard 10-20 positions"  # LLM 推断，需人类复核
_HANDEDNESS = "unknown"  # not reported in available metadata

# ============================================================================
# Channel Configuration
# ============================================================================
# Source: Dataset uses standard 10-20 extended 64-channel layout + 3 accelerometer
# channels (x_dir, y_dir, z_dir) for gait event detection.
# The 64 EEG channels follow standard naming; accelerometer channels are misc.
# Annotator: LLM, 2026-04-08 — 需人类复核

# Standard 64-channel EEG names (standard_1020 extended)
_STANDARD_EEG_CHANNELS = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "PO7",
    "PO3", "O1", "Oz", "POz", "Pz", "CPz", "Fpz", "AFz",
    "Fz", "FCz", "Cz", "F2", "F4", "F6", "F8", "FT8",
    "FC6", "FC4", "FC2", "C2", "C4", "C6", "T8", "TP8",
    "CP6", "CP4", "CP2", "P2", "P4", "P6", "P8", "PO8",
    "PO4", "O2", "Iz", "AF8", "AF4", "F10", "Fp2", "EOG"
]

# Accelerometer channels (native misc)
_NATIVE_MISC_CHANNELS = ["x_dir", "y_dir", "z_dir"]

# Common channel aliases that may appear in raw data
_CHANNEL_ALIAS_MAP: Dict[str, List[str]] = {
    "Fp1": ["EEG Fp1", "Fp1", "EEG-Fp1", "Fp1-0"],
    "AF7": ["EEG AF7", "AF7", "EEG-AF7"],
    "AF3": ["EEG AF3", "AF3", "EEG-AF3"],
    "F1": ["EEG F1", "F1", "EEG-F1"],
    "F3": ["EEG F3", "F3", "EEG-F3"],
    "F5": ["EEG F5", "F5", "EEG-F5"],
    "F7": ["EEG F7", "F7", "EEG-F7"],
    "FT7": ["EEG FT7", "FT7", "EEG-FT7"],
    "FC5": ["EEG FC5", "FC5", "EEG-FC5"],
    "FC3": ["EEG FC3", "FC3", "EEG-FC3"],
    "FC1": ["EEG FC1", "FC1", "EEG-FC1"],
    "C1": ["EEG C1", "C1", "EEG-C1"],
    "C3": ["EEG C3", "C3", "EEG-C3"],
    "C5": ["EEG C5", "C5", "EEG-C5"],
    "T7": ["EEG T7", "T7", "EEG-T7"],
    "TP7": ["EEG TP7", "TP7", "EEG-TP7"],
    "CP5": ["EEG CP5", "CP5", "EEG-CP5"],
    "CP3": ["EEG CP3", "CP3", "EEG-CP3"],
    "CP1": ["EEG CP1", "CP1", "EEG-CP1"],
    "P1": ["EEG P1", "P1", "EEG-P1"],
    "P3": ["EEG P3", "P3", "EEG-P3"],
    "P5": ["EEG P5", "P5", "EEG-P5"],
    "P7": ["EEG P7", "P7", "EEG-P7"],
    "PO7": ["EEG PO7", "PO7", "EEG-PO7"],
    "PO3": ["EEG PO3", "PO3", "EEG-PO3"],
    "O1": ["EEG O1", "O1", "EEG-O1"],
    "Oz": ["EEG Oz", "Oz", "EEG-Oz"],
    "POz": ["EEG POz", "POz", "EEG-POz"],
    "Pz": ["EEG Pz", "Pz", "EEG-Pz"],
    "CPz": ["EEG CPz", "CPz", "EEG-CPz"],
    "Fpz": ["EEG Fpz", "Fpz", "EEG-Fpz"],
    "AFz": ["EEG AFz", "AFz", "EEG-AFz"],
    "Fz": ["EEG Fz", "Fz", "EEG-Fz"],
    "FCz": ["EEG FCz", "FCz", "EEG-FCz"],
    "Cz": ["EEG Cz", "Cz", "EEG-Cz"],
    "F2": ["EEG F2", "F2", "EEG-F2"],
    "F4": ["EEG F4", "F4", "EEG-F4"],
    "F6": ["EEG F6", "F6", "EEG-F6"],
    "F8": ["EEG F8", "F8", "EEG-F8"],
    "FT8": ["EEG FT8", "FT8", "EEG-FT8"],
    "FC6": ["EEG FC6", "FC6", "EEG-FC6"],
    "FC4": ["EEG FC4", "FC4", "EEG-FC4"],
    "FC2": ["EEG FC2", "FC2", "EEG-FC2"],
    "C2": ["EEG C2", "C2", "EEG-C2"],
    "C4": ["EEG C4", "C4", "EEG-C4"],
    "C6": ["EEG C6", "C6", "EEG-C6"],
    "T8": ["EEG T8", "T8", "EEG-T8"],
    "TP8": ["EEG TP8", "TP8", "EEG-TP8"],
    "CP6": ["EEG CP6", "CP6", "EEG-CP6"],
    "CP4": ["EEG CP4", "CP4", "EEG-CP4"],
    "CP2": ["EEG CP2", "CP2", "EEG-CP2"],
    "P2": ["EEG P2", "P2", "EEG-P2"],
    "P4": ["EEG P4", "P4", "EEG-P4"],
    "P6": ["EEG P6", "P6", "EEG-P6"],
    "P8": ["EEG P8", "P8", "EEG-P8"],
    "PO8": ["EEG PO8", "PO8", "EEG-PO8"],
    "PO4": ["EEG PO4", "PO4", "EEG-PO4"],
    "O2": ["EEG O2", "O2", "EEG-O2"],
    "Iz": ["EEG Iz", "Iz", "EEG-Iz"],
    "AF8": ["EEG AF8", "AF8", "EEG-AF8"],
    "AF4": ["EEG AF4", "AF4", "EEG-AF4"],
    "F10": ["EEG F10", "F10", "EEG-F10"],
    "Fp2": ["EEG Fp2", "Fp2", "EEG-Fp2"],
    "EOG": ["EEG EOG", "EOG", "EEG-EOG", "VEOG", "HEOG", "EOG1", "EOG2"],
    "x_dir": ["x_dir", "x-dir", "X_dir", "X-dir", "accel_x", "AccX"],
    "y_dir": ["y_dir", "y-dir", "Y_dir", "Y-dir", "accel_y", "AccY"],
    "z_dir": ["z_dir", "z-dir", "Z_dir", "Z-dir", "accel_z", "AccZ"],
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map from raw channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for target, aliases in _CHANNEL_ALIAS_MAP.items():
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    base = file_path.replace(".set", "").replace(".edf", "").replace(".eeg", "").replace(".fif", "")
    candidates = [
        base + "_events.tsv",
        base + ".tsv",
    ]
    # Also check BIDS-style path
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Try to match sub-XX_task-YY_run-ZZ pattern
    match = re.match(r"(sub-\w+)(?:_ses-\w+)?_(task-\w+)(?:_run-\w+)?(?:_eeg)?\.(?:set|edf|eeg|fif)", basename)
    if match:
        sub, task = match.group(1), match.group(2)
        bids_candidates = [
            os.path.join(dirname, f"{sub}_{task}_events.tsv"),
            os.path.join(dirname, f"{sub}_{task}_run-01_events.tsv"),
            os.path.join(dirname, f"{sub}_{task}_run-1_events.tsv"),
        ]
        candidates.extend(bids_candidates)
    
    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    
    # Walk up to find events.tsv in parent directories
    for root, dirs, files in os.walk(os.path.dirname(file_path)):
        for f in files:
            if f.endswith("_events.tsv"):
                # Check if it matches our subject
                fp = os.path.join(root, f)
                # Simple heuristic: same subject ID in path
                sub_match = re.search(r"(sub-\w+)", file_path)
                if sub_match and sub_match.group(1) in fp:
                    return fp
    
    return None


def _read_participants_info(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.isfile(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find subject row
        sub_col = "participant_id"
        if sub_col not in df.columns:
            # Try alternatives
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    sub_col = col
                    break
        
        # Normalize subject ID format
        if not subject_id.startswith("sub-"):
            search_id = f"sub-{subject_id}"
        else:
            search_id = subject_id
        
        row = df[df[sub_col] == search_id]
        if row.empty:
            # Try without sub- prefix
            row = df[df[sub_col] == subject_id.replace("sub-", "")]
        
        if row.empty:
            return {}
        
        info = {}
        for col in df.columns:
            if col != sub_col:
                val = row.iloc[0][col]
                info[col] = str(val) if pd.notna(val) else "unknown"
        
        return info
    except Exception:
        return {}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path."""
    # Try BIDS pattern
    match = re.search(r"(sub-\w+)", file_path)
    if match:
        return match.group(1)
    # Try numeric pattern
    match = re.search(r"/(\d+)/", file_path)
    if match:
        return match.group(1)
    # Fallback to parent directory name
    return os.path.basename(os.path.dirname(file_path))


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex to canonical values."""
    if pd.isna(sex_val):
        return "unknown"
    sex_lower = str(sex_val).lower().strip()
    if sex_lower in ("m", "male", "1"):
        return "male"
    elif sex_lower in ("f", "female", "2"):
        return "female"
    return "unknown"


def _normalize_age(age_val: Any) -> str:
    """Normalize age to string."""
    if pd.isna(age_val):
        return "unknown"
    try:
        age_float = float(age_val)
        if age_float <= 0 or np.isnan(age_float):
            return "unknown"
        return str(int(age_float))
    except (ValueError, TypeError):
        age_str = str(age_val).strip()
        if age_str.lower() in ("n/a", "na", "unknown", ""):
            return "unknown"
        # Check for range like "22-45"
        if re.match(r"^\d+\s*-\s*\d+$", age_str):
            return age_str.replace(" ", "")
        # Try to extract number
        num_match = re.search(r"(\d+(?:\.\d+)?)", age_str)
        if num_match:
            return str(int(float(num_match.group(1))))
        return "unknown"


@dataclass
class OpenNeuroDS003039Kernel:
    """Stage1 kernel for openneuro_ds003039 Free Walking Study."""

    KERNEL_ID: str = "openneuro-ds003039-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        
        # =====================================================================
        # 1. Channel renaming to standard 10-20
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # =====================================================================
        # 2. Set channel types
        # =====================================================================
        ch_types: Dict[str, str] = {}
        for ch_name in raw.ch_names:
            if ch_name in _NATIVE_MISC_CHANNELS:
                ch_types[ch_name] = "misc"
            elif ch_name == "EOG":
                ch_types[ch_name] = "eog"
            elif ch_name in _STANDARD_EEG_CHANNELS:
                ch_types[ch_name] = "eeg"
            else:
                # Default to EEG for unknown channels that look like EEG
                if re.match(r"^[A-Z][a-z]?\d+$|^[A-Z][a-z]?z$", ch_name):
                    ch_types[ch_name] = "eeg"
                else:
                    ch_types[ch_name] = "misc"
        
        # Ensure native misc channels are typed correctly
        for misc_ch in _NATIVE_MISC_CHANNELS:
            if misc_ch in raw.ch_names:
                ch_types[misc_ch] = "misc"
        
        raw.set_channel_types(ch_types)
        
        # =====================================================================
        # 3. Set montage (standard_1020)
        # =====================================================================
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in the montage
            montage_chs = set(montage.ch_names)
            raw_eeg_chs = [ch for ch in raw.ch_names if raw.get_channel_types(picks=[ch])[0] == "eeg"]
            available = [ch for ch in raw_eeg_chs if ch in montage_chs]
            if available:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without
        
        # =====================================================================
        # 4. Read participants.tsv info
        # =====================================================================
        subject_id = _extract_subject_id(file_path)
        part_info = _read_participants_info(dataset_path, subject_id)
        
        # Required info fields from participants.tsv: age, gender
        age = "unknown"
        sex = "unknown"
        
        if "age" in part_info:
            age = _normalize_age(part_info["age"])
        if "gender" in part_info:
            sex = _normalize_sex(part_info["gender"])
        elif "sex" in part_info:
            sex = _normalize_sex(part_info["sex"])
        
        # Build eegunity_description with required fields + extra participants columns
        eegunity_desc: Dict[str, str] = {
            "age": age,
            "sex": sex,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": _HANDEDNESS,
        }
        
        # Add any extra participants.tsv columns as strings
        for key, val in part_info.items():
            if key not in ("age", "gender", "sex", "participant_id"):
                eegunity_desc[key] = str(val) if val is not None else "unknown"
        
        # =====================================================================
        # 5. Update raw.info["description"]
        # =====================================================================
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })
        
        # =====================================================================
        # 6. Handle events from events.tsv sidecar
        # =====================================================================
        events_tsv_path = _find_events_tsv(file_path)
        
        # Check if raw already has annotations/events
        has_native_events = False
        try:
            if raw.annotations is not None and len(raw.annotations) > 0:
                has_native_events = True
            # Also check for stim channels
            stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
            if len(stim_picks) > 0:
                has_native_events = True
        except Exception:
            pass
        
        # For EEGLAB .set files, events might be embedded; for EDF without annotations,
        # we need events.tsv. BrainVision .eeg without .vmrk also needs events.tsv.
        needs_events_tsv = False
        if file_path.endswith(".edf"):
            # EDF without annotations needs events.tsv
            if raw.annotations is None or len(raw.annotations) == 0:
                needs_events_tsv = True
        elif file_path.endswith(".eeg"):
            # BrainVision without proper marker file
            needs_events_tsv = True
        elif file_path.endswith(".fif"):
            # Plain .fif without events
            if not has_native_events:
                needs_events_tsv = True
        elif file_path.endswith(".set"):
            # EEGLAB .set may or may not have events
            # Check if events are actually populated
            if not has_native_events:
                needs_events_tsv = True
        
        # Always derive from events.tsv if available, to ensure complete event coverage
        if events_tsv_path and os.path.isfile(events_tsv_path):
            try:
                events_df = pd.read_csv(events_tsv_path, sep="\t")
                
                # Required columns: onset, (duration), trial_type or value
                if "onset" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
                    
                    # Determine description column
                    if "trial_type" in events_df.columns:
                        descriptions = events_df["trial_type"].astype(str).values
                    elif "value" in events_df.columns:
                        descriptions = events_df["value"].astype(str).values
                    elif "stim_type" in events_df.columns:
                        descriptions = events_df["stim_type"].astype(str).values
                    else:
                        descriptions = np.array(["event"] * len(onsets))
                    
                    # Filter out NaN/empty rows
                    valid_mask = pd.notna(onsets) & (descriptions != "nan") & (descriptions != "")
                    onsets = onsets[valid_mask]
                    durations = durations[valid_mask]
                    descriptions = descriptions[valid_mask]
                    
                    # Convert onsets to seconds if in samples
                    if np.max(onsets) > raw.n_times:
                        # Likely in samples, convert to seconds
                        onsets = onsets / raw.info["sfreq"]
                    
                    # Ensure non-negative durations
                    durations = np.maximum(durations, 0)
                    
                    # Create annotations
                    new_annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    
                    # Combine with existing or replace
                    if raw.annotations is not None and len(raw.annotations) > 0:
                        # Combine
                        all_onsets = np.concatenate([raw.annotations.onset, new_annotations.onset])
                        all_durations = np.concatenate([raw.annotations.duration, new_annotations.duration])
                        all_descriptions = np.concatenate([raw.annotations.description, new_annotations.description])
                        # Sort by onset
                        sort_idx = np.argsort(all_onsets)
                        raw.set_annotations(mne.Annotations(
                            onset=all_onsets[sort_idx],
                            duration=all_durations[sort_idx],
                            description=all_descriptions[sort_idx],
                        ))
                    else:
                        raw.set_annotations(new_annotations)
            except Exception:
                pass  # Failed to read events.tsv, continue with what we have
        
        # =====================================================================
        # 7. Ensure native misc channels exist and are properly typed
        # =====================================================================
        for misc_ch in _NATIVE_MISC_CHANNELS:
            if misc_ch not in raw.ch_names:
                # Create derived misc channel with zeros if missing
                data = np.zeros((1, raw.n_times))
                info = mne.create_info([misc_ch], raw.info["sfreq"], ["misc"])
                misc_raw = mne.io.RawArray(data, info)
                raw.add_channels([misc_raw], force_update_info=True)
            else:
                # Ensure it's typed as misc
                current_type = raw.get_channel_types(picks=[misc_ch])[0]
                if current_type != "misc":
                    raw.set_channel_types({misc_ch: "misc"})
        
        return raw


KERNEL = OpenNeuroDS003039Kernel()