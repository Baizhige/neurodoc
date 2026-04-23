"""OpenNeuro ds003638 stage1 kernel for EEGUnity.

Dataset: EEG Electrophysiological Biomarkers of Behavioral Dimensions from Cross-Species Paradigms
Source: https://openneuro.org/datasets/ds003638
Reference: DOI 10.1038/s41398-021-01562-w

57 subjects, 73 channels, 512 Hz. Three paradigms: 5CCPT, PRBP, PST.
Uses BrainVision .eeg format with .vhdr/.vmrk sidecars.

This kernel handles:
- Channel renaming from BrainVision numeric names to standard 10-20
- Montage setting for standard_1020
- participants.tsv metadata extraction (age, sex, UH2_ID)
- events.tsv annotation loading (BrainVision .eeg may not carry triggers without .vmrk)
- Derived misc channels: response_time_derived, trial_accuracy
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Standard 10-20 73-channel layout for BrainCap72 / extended montage
# Source: Brain Products standard 72-channel cap with FCz, AFz, CPz, POz extensions
# Annotator: LLM 推断，需人类复核
_STANDARD_73_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "Iz",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Map BrainVision-style channel names to standard 10-20 names."""
    rename_map = {}
    existing = set(raw.ch_names)
    
    # Try various BrainVision naming patterns
    for i, std_name in enumerate(_STANDARD_73_CHANNELS):
        # Common BrainVision patterns: "EEG 001", "EEG001", "1", "Ch1", etc.
        candidates = [
            f"EEG {i+1:03d}",
            f"EEG {i+1:02d}",
            f"EEG{i+1:03d}",
            f"EEG{i+1:02d}",
            f"{i+1}",
            f"Ch{i+1}",
            f"CH{i+1}",
            f"Channel {i+1}",
            f"channel {i+1}",
        ]
        for cand in candidates:
            if cand in existing and cand != std_name:
                rename_map[cand] = std_name
                break
    
    # Also handle common non-EEG channels
    misc_mappings = {
        "EOG1": "HEOG",
        "EOG2": "VEOG",
        "EMG1": "EMG",
        "AUX1": "AUX",
        "Status": "STATUS",
    }
    for bv_name, std_name in misc_mappings.items():
        if bv_name in existing and bv_name != std_name:
            rename_map[bv_name] = std_name
    
    return rename_map


def _detect_paradigm(file_name: str) -> Optional[str]:
    """Detect paradigm from filename for event prefixing."""
    fname_lower = file_name.lower()
    if "5ccpt" in fname_lower or "cpt" in fname_lower:
        return "5CCPT"
    elif "prbp" in fname_lower or "probabilistic" in fname_lower:
        return "PRBP"
    elif "pst" in fname_lower or "pavlovian" in fname_lower:
        return "PST"
    return None


# Event code to description mapping based on analysis.md event structure
# Source: analysis.md Event Structure table, paper 10.1038/s41398-021-01562-w
# Annotator: LLM 推断，需人类复核
_EVENT_CODE_MAP = {
    130816: "admin: marker-130816",
    131070: "admin: marker-131070",
    131071: "admin: session-start",
    65281: "5CCPT: Go stimulus 1 onset (circle)",
    65282: "5CCPT: Go stimulus 2 onset (cross)",
    65283: "5CCPT: Go stimulus 3 onset (diamond)",
    65284: "5CCPT: Go stimulus 4 onset (square)",
    65285: "5CCPT: Go stimulus 5 onset (triangle)",
    65286: "5CCPT: NoGo stimulus onset (star)",
    65287: "5CCPT: target/hit",
    65291: "PRBP: feedback probabilistic outcome 1",
    65292: "PRBP: feedback probabilistic outcome 2",
    65293: "PRBP: feedback high/low reward",
    65294: "PRBP: feedback high/low punishment",
    65295: "PRBP: feedback valence",
    65301: "5CCPT: response code 1",
    65302: "5CCPT: response code 2",
    65303: "5CCPT: response code 3",
    65305: "5CCPT: response code 5",
    65310: "5CCPT: response code 10",
    65311: "5CCPT: response code 11 (hit)",
    65312: "5CCPT: response code 12",
    65313: "5CCPT: response code 13",
    65316: "PST: cue code (rare event)",
    65319: "PRBP/PST: event code 65319",
    65320: "PRBP/PST: event code 65320",
    65321: "PST: cue code A",
    65322: "PST: cue code B",
    65323: "PST: cue code C",
    65324: "PST: cue code",
    65325: "PST: cue code",
    65326: "PRBP: trial start/code",
    65327: "PRBP: trial start/code",
    65330: "task event code 65330",
    65336: "5CCPT: block/code",
    65337: "5CCPT: block/code",
    65338: "PST: rare event",
    65339: "5CCPT: block event",
    65340: "5CCPT: block event",
    65341: "rare/error event 65341",
    65342: "rare/error event 65342",
    65343: "PST: cue",
    65344: "PST: cue",
    65345: "PST: cue",
    65346: "PST: cue",
    65347: "PST: cue",
    65349: "PST: cue",
    65360: "5CCPT: block event 65360",
    65361: "5CCPT: block event 65361",
    65362: "5CCPT: block event 65362",
    65363: "5CCPT: block event 65363",
    65364: "5CCPT: block event 65364",
    65366: "5CCPT: block event 65366",
    65396: "admin: marker-65396",
    65397: "admin: marker-65397",
    65398: "admin: marker-65398",
    65401: "admin: marker-65401",
}


def _read_participants_tsv(dataset_path: str, participant_id: str) -> Dict[str, str]:
    """Read participants.tsv and return metadata for given participant."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}
    
    # Match participant_id (could be "sub-01", "01", etc.)
    for _, row in df.iterrows():
        pid = str(row.get("participant_id", ""))
        if pid == participant_id or pid == f"sub-{participant_id}" or pid.replace("sub-", "") == participant_id:
            result = {}
            for col in ["UH2_ID", "age", "sex"]:
                if col in row:
                    val = row[col]
                    if pd.isna(val):
                        result[col] = "unknown"
                    else:
                        result[col] = str(val).strip()
            return result
    
    return {}


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file if it exists."""
    if not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for given EEG file."""
    base = file_path.replace(".eeg", "").replace(".vhdr", "").replace(".vmrk", "").replace(".set", "").replace(".edf", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try BIDS naming: sub-XX_task-YY_events.tsv
    dirname = os.path.dirname(file_path)
    for fname in os.listdir(dirname) if os.path.isdir(dirname) else []:
        if fname.endswith("_events.tsv"):
            return os.path.join(dirname, fname)
    
    return None


def _derive_response_time(events_df: pd.DataFrame, sfreq: float) -> Tuple[np.ndarray, np.ndarray]:
    """Derive response time channel from events.tsv.
    
    For each stimulus event (65281-65287), find following response event (65301/65303/65305/65310)
    and compute RT in seconds. NoGo correct rejections get NaN.
    """
    if events_df is None or len(events_df) == 0:
        return np.array([]), np.array([])
    
    # Ensure required columns exist
    if "onset" not in events_df.columns or "value" not in events_df.columns:
        return np.array([]), np.array([])
    
    # Filter to numeric values
    events_df = events_df.copy()
    events_df["value_num"] = pd.to_numeric(events_df["value"], errors="coerce")
    events_df = events_df.dropna(subset=["value_num", "onset"])
    events_df["value_num"] = events_df["value_num"].astype(int)
    events_df = events_df.sort_values("onset").reset_index(drop=True)
    
    stimulus_codes = {65281, 65282, 65283, 65284, 65285, 65286, 65287}
    response_codes = {65301, 65303, 65305, 65310}
    
    onsets = []
    values = []
    
    for i, row in events_df.iterrows():
        code = int(row["value_num"])
        if code in stimulus_codes:
            stim_onset = float(row["onset"])
            # Look for next response within 2 seconds
            found_rt = np.nan
            for j in range(i + 1, len(events_df)):
                next_code = int(events_df.iloc[j]["value_num"])
                next_onset = float(events_df.iloc[j]["onset"])
                if next_onset - stim_onset > 2.0:
                    break
                if next_code in response_codes:
                    found_rt = next_onset - stim_onset
                    break
                # Stop if we hit another stimulus
                if next_code in stimulus_codes:
                    break
            
            onsets.append(stim_onset)
            values.append(found_rt)
    
    return np.array(onsets), np.array(values)


def _derive_trial_accuracy(events_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Derive trial accuracy channel from events.tsv.
    
    For each stimulus onset (65281-65287), examine next non-mask event.
    Correct: response code 65301/65303/65305/65291-65295/65310 -> 1.0
    Incorrect: 65326-65340/65360/65361-65366 -> 0.0
    Otherwise: NaN (missing)
    """
    if events_df is None or len(events_df) == 0:
        return np.array([]), np.array([])
    
    if "onset" not in events_df.columns or "value" not in events_df.columns:
        return np.array([]), np.array([])
    
    events_df = events_df.copy()
    events_df["value_num"] = pd.to_numeric(events_df["value"], errors="coerce")
    events_df = events_df.dropna(subset=["value_num", "onset"])
    events_df["value_num"] = events_df["value_num"].astype(int)
    events_df = events_df.sort_values("onset").reset_index(drop=True)
    
    stimulus_codes = {65281, 65282, 65283, 65284, 65285, 65286, 65287}
    correct_codes = {65301, 65303, 65305, 65291, 65292, 65293, 65294, 65295, 65310}
    incorrect_codes = set(range(65326, 65341)) | {65360, 65361, 65362, 65363, 65364, 65366}
    
    onsets = []
    values = []
    
    for i, row in events_df.iterrows():
        code = int(row["value_num"])
        if code in stimulus_codes:
            stim_onset = float(row["onset"])
            found_acc = np.nan
            for j in range(i + 1, len(events_df)):
                next_code = int(events_df.iloc[j]["value_num"])
                next_onset = float(events_df.iloc[j]["onset"])
                # Stop at next stimulus
                if next_code in stimulus_codes:
                    break
                if next_code in correct_codes:
                    found_acc = 1.0
                    break
                elif next_code in incorrect_codes:
                    found_acc = 0.0
                    break
            
            onsets.append(stim_onset)
            values.append(found_acc)
    
    return np.array(onsets), np.array(values)


def _create_step_function_channel(raw: mne.io.BaseRaw, event_onsets: np.ndarray, 
                                   event_values: np.ndarray, channel_name: str) -> mne.io.RawArray:
    """Create a misc channel with step function values at event onsets."""
    n_samples = len(raw.times)
    data = np.full((1, n_samples), np.nan, dtype=np.float64)
    
    # Fill with step function: value holds until next event, then changes
    # For samples before first event, use 0
    sample_onsets = (event_onsets * raw.info["sfreq"]).astype(int)
    sample_onsets = np.clip(sample_onsets, 0, n_samples - 1)
    
    current_val = 0.0 if len(event_values) > 0 else np.nan
    for i in range(n_samples):
        # Find if there's an event at this sample
        evt_idx = np.searchsorted(sample_onsets, i, side="right") - 1
        if evt_idx >= 0 and evt_idx < len(event_values):
            current_val = event_values[evt_idx]
        elif evt_idx < 0:
            current_val = 0.0  # Before first event
        data[0, i] = current_val
    
    # Replace any remaining NaN with 0
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
    
    info = mne.create_info([channel_name], raw.info["sfreq"], ["misc"])
    return mne.io.RawArray(data, info)


class OpenNeuroDS003638Kernel:
    """Stage1 kernel for OpenNeuro ds003638 dataset."""

    KERNEL_ID: str = "openneuro-ds003638-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "root_path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from path
        fname = os.path.basename(file_path)
        # Try to extract sub-XX from filename or path
        sub_match = None
        for part in file_path.replace("\\", "/").split("/"):
            if part.startswith("sub-"):
                sub_match = part.replace("sub-", "")
                break
        
        if sub_match is None:
            # Try from filename
            import re
            m = re.search(r'sub[_-]?(\d+)', fname, re.I)
            if m:
                sub_match = m.group(1).zfill(2)
            else:
                sub_match = "unknown"
        
        participant_id = f"sub-{sub_match}" if not sub_match.startswith("sub-") else sub_match
        
        # --- Read participants.tsv for metadata ---
        p_info = _read_participants_tsv(dataset_path, sub_match)
        
        age = p_info.get("age", "unknown")
        sex = p_info.get("sex", "unknown").lower()
        if sex not in ("male", "female"):
            sex = "unknown"
        uh2_id = p_info.get("UH2_ID", "unknown")
        
        # --- Channel renaming ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # --- Set channel types ---
        # Mark any non-EEG channels appropriately
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in ["HEOG", "VEOG", "EOG1", "EOG2", "EOGh", "EOGv"]:
                ch_types[ch_name] = "eog"
            elif ch_name in ["EMG", "EMG1", "EMG2"]:
                ch_types[ch_name] = "emg"
            elif ch_name in ["STATUS", "Status", "Trigger", "TRIGGER"]:
                ch_types[ch_name] = "stim"
            elif ch_name in ["AUX", "AUX1", "AUX2"]:
                ch_types[ch_name] = "misc"
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # --- Set montage ---
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            pass  # Montage setting failed, continue without
        
        # --- Read events.tsv and create annotations if needed ---
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path) if events_path else None
        
        # Check if raw already has annotations/events
        has_events = False
        try:
            # Try to get events from annotations
            annots = raw.annotations
            if len(annots) > 0:
                has_events = True
        except Exception:
            pass
        
        # If no events in raw and we have events.tsv, create annotations
        if not has_events and events_df is not None and len(events_df) > 0:
            # Build annotations from events.tsv
            onsets = []
            durations = []
            descriptions = []
            
            for _, evt_row in events_df.iterrows():
                if "onset" not in evt_row or pd.isna(evt_row["onset"]):
                    continue
                
                onset = float(evt_row["onset"])
                duration = float(evt_row.get("duration", 0))
                if pd.isna(duration):
                    duration = 0.0
                
                # Get description from value or trial_type
                desc = None
                if "value" in evt_row and not pd.isna(evt_row["value"]):
                    try:
                        val = int(float(evt_row["value"]))
                        desc = _EVENT_CODE_MAP.get(val, f"event_{val}")
                    except (ValueError, TypeError):
                        pass
                
                if desc is None and "trial_type" in evt_row and not pd.isna(evt_row["trial_type"]):
                    desc = str(evt_row["trial_type"])
                
                if desc is None:
                    desc = "unknown"
                
                onsets.append(onset)
                durations.append(duration)
                descriptions.append(desc)
            
            if onsets:
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=descriptions,
                    orig_time=raw.annotations.orig_time if hasattr(raw, "annotations") and raw.annotations else None
                )
                raw.set_annotations(annotations)
        
        # --- Derived misc channels ---
        # response_time_derived
        rt_onsets, rt_values = _derive_response_time(events_df, raw.info["sfreq"]) if events_df is not None else (np.array([]), np.array([]))
        if len(rt_onsets) > 0:
            rt_raw = _create_step_function_channel(raw, rt_onsets, rt_values, "response_time_derived")
            raw.add_channels([rt_raw], force_update_info=True)
        
        # trial_accuracy
        acc_onsets, acc_values = _derive_trial_accuracy(events_df) if events_df is not None else (np.array([]), np.array([]))
        if len(acc_onsets) > 0:
            acc_raw = _create_step_function_channel(raw, acc_onsets, acc_values, "trial_accuracy")
            raw.add_channels([acc_raw], force_update_info=True)
        
        # Ensure misc channel types for derived channels
        for ch_name in ["response_time_derived", "trial_accuracy"]:
            if ch_name in raw.ch_names:
                raw.set_channel_types({ch_name: "misc"})
        
        # --- Update description with metadata ---
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_desc = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": "BrainAmp DC",  # Source: BrainVision format, standard Brain Products amplifier
            # LLM 推断，需人类复核
            "cap": "BrainCap 64ch with 8 externals",  # Source: 73 channels suggests 64+8+1 reference setup
            # LLM 推断，需人类复核
            "handedness": "unknown",  # Not in participants.tsv, not reported in paper abstract
            "UH2_ID": str(uh2_id),
        }
        
        # Add any extra fields from participants.tsv
        for key, val in p_info.items():
            if key not in ("age", "sex", "UH2_ID") and key not in eegunity_desc:
                eegunity_desc[key] = str(val) if not pd.isna(val) else "unknown"
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS003638Kernel()