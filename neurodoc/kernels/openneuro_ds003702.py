"""OpenNeuro DS003702 Social Memory Cueing stage1 kernel for EEGUnity.

A visual working memory task in VR where participants recall object locations
following social (avatar) or non-social (stick) directional cues.

Source: https://openneuro.org/datasets/ds003702
Reference: DOI 10.1109/SMC58881.2025.11343511
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: Standard 10-20 electrode naming convention for 64-channel BrainVision/BrainAmp
# Annotator: LLM, 2026-04-08
_STANDARD_64_CHANNELS = [
    "FP1", "FPZ", "FP2",
    "AF3", "AF4",
    "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
    "PO3", "PO4",
    "O1", "OZ", "O2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.
    
    Source: Standard 10-20 electrode naming convention
    Annotator: LLM, 2026-04-08
    """
    existing = set(raw.ch_names)
    rename_map: Dict[str, str] = {}
    
    alias_groups = [
        ("FP1", ["EEG 001", "FP1", "Fp1"]),
        ("FPZ", ["EEG 002", "FPZ", "Fpz", "Fpz"]),
        ("FP2", ["EEG 003", "FP2", "Fp2"]),
        ("AF3", ["EEG 004", "AF3", "Af3"]),
        ("AF4", ["EEG 005", "AF4", "Af4"]),
        ("F7", ["EEG 006", "F7"]),
        ("F5", ["EEG 007", "F5"]),
        ("F3", ["EEG 008", "F3"]),
        ("F1", ["EEG 009", "F1"]),
        ("FZ", ["EEG 010", "FZ", "Fz"]),
        ("F2", ["EEG 011", "F2"]),
        ("F4", ["EEG 012", "F4"]),
        ("F6", ["EEG 013", "F6"]),
        ("F8", ["EEG 014", "F8"]),
        ("FT7", ["EEG 015", "FT7", "Ft7"]),
        ("FC5", ["EEG 016", "FC5", "Fc5"]),
        ("FC3", ["EEG 017", "FC3", "Fc3"]),
        ("FC1", ["EEG 018", "FC1", "Fc1"]),
        ("FCZ", ["EEG 019", "FCZ", "FCz", "Fcz"]),
        ("FC2", ["EEG 020", "FC2", "Fc2"]),
        ("FC4", ["EEG 021", "FC4", "Fc4"]),
        ("FC6", ["EEG 022", "FC6", "Fc6"]),
        ("FT8", ["EEG 023", "FT8", "Ft8"]),
        ("T7", ["EEG 024", "T7"]),
        ("C5", ["EEG 025", "C5"]),
        ("C3", ["EEG 026", "C3"]),
        ("C1", ["EEG 027", "C1"]),
        ("CZ", ["EEG 028", "CZ", "Cz"]),
        ("C2", ["EEG 029", "C2"]),
        ("C4", ["EEG 030", "C4"]),
        ("C6", ["EEG 031", "C6"]),
        ("T8", ["EEG 032", "T8"]),
        ("TP7", ["EEG 033", "TP7", "Tp7"]),
        ("CP5", ["EEG 034", "CP5", "Cp5"]),
        ("CP3", ["EEG 035", "CP3", "Cp3"]),
        ("CP1", ["EEG 036", "CP1", "Cp1"]),
        ("CPZ", ["EEG 037", "CPZ", "CPz", "Cpz"]),
        ("CP2", ["EEG 038", "CP2", "Cp2"]),
        ("CP4", ["EEG 039", "CP4", "Cp4"]),
        ("CP6", ["EEG 040", "CP6", "Cp6"]),
        ("TP8", ["EEG 041", "TP8", "Tp8"]),
        ("P7", ["EEG 042", "P7"]),
        ("P5", ["EEG 043", "P5"]),
        ("P3", ["EEG 044", "P3"]),
        ("P1", ["EEG 045", "P1"]),
        ("PZ", ["EEG 046", "PZ", "Pz"]),
        ("P2", ["EEG 047", "P2"]),
        ("P4", ["EEG 048", "P4"]),
        ("P6", ["EEG 049", "P6"]),
        ("P8", ["EEG 050", "P8"]),
        ("PO3", ["EEG 051", "PO3", "Po3"]),
        ("PO4", ["EEG 052", "PO4", "Po4"]),
        ("O1", ["EEG 053", "O1"]),
        ("OZ", ["EEG 054", "OZ", "Oz"]),
        ("O2", ["EEG 055", "O2"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _get_subject_info_from_participants(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read participant info from participants.tsv.
    
    Returns required fields: Age, Gender, Handedness as strings.
    Missing values become 'unknown'.
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    result = {"Age": "unknown", "Gender": "unknown", "Handedness": "unknown"}
    
    if not os.path.exists(participants_path):
        return result
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject_id like 'sub-01' or '01'
        for _, row in df.iterrows():
            pid = str(row.get("participant_id", ""))
            if pid == subject_id or pid == f"sub-{subject_id}" or pid.replace("sub-", "") == subject_id.replace("sub-", ""):
                for field in ["Age", "Gender", "Handedness"]:
                    val = row.get(field, row.get(field.lower(), "unknown"))
                    if pd.isna(val):
                        val = "unknown"
                    result[field] = str(val).strip() if str(val).strip() else "unknown"
                break
    except Exception:
        pass
    
    return result


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    base = file_path.replace(".eeg", "").replace(".vhdr", "").replace(".edf", "").replace(".set", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try BIDS-style: look in same directory
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path).split(".")[0]
    events_path = os.path.join(dirname, basename + "_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Try without suffix variations
    for suffix in ["_events.tsv", "_events.tsv"]:
        candidate = base + suffix
        if os.path.exists(candidate):
            return candidate
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _compute_response_time_misc(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
    """Compute derived misc channels for response times from event timestamps.
    
    For avatar trials: s3025 - s3024 (response_time_location), s3027 - s3026 (response_time_status)
    For stick trials: s3045 - s3044 (response_time_location), s3047 - s3046 (response_time_status)
    
    Returns two arrays: response_time_location, response_time_status
    Each with shape (1, n_samples) - constant per trial based on event timing.
    """
    n_samples = len(raw.times)
    sfreq = raw.info["sfreq"]
    
    # Default: zeros (unknown)
    rt_loc = np.zeros((1, n_samples))
    rt_status = np.zeros((1, n_samples))
    
    # Get annotations from raw
    annots = raw.annotations
    if annots is None or len(annots) == 0:
        return rt_loc, rt_status
    
    # Build event list from annotations
    events_list = []
    for i in range(len(annots)):
        desc = annots.description[i]
        onset = annots.onset[i]
        # Normalize description
        if "/" in desc:
            desc = desc.split("/")[-1]
        events_list.append((onset, desc))
    
    # Sort by time
    events_list.sort(key=lambda x: x[0])
    
    # Group by trial: find s3021/s3041 (trial starts), then look for response pairs
    # Avatar trials (s3021 present): s3024->s3025 (location), s3026->s3027 (status)
    # Stick trials (s3041 present): s3044->s3045 (location), s3046->s3047 (status)
    
    # Simple approach: find all occurrences and compute differences
    # Then broadcast to trial time ranges
    
    # Find trial boundaries based on cue events
    avatar_trials = []  # list of (start_time, end_time)
    stick_trials = []   # list of (start_time, end_time)
    
    cue_times = []
    for onset, desc in events_list:
        if desc in ["s3021", "s3041", "s3001", "s3002", "s3003", "s3004", "s3005", "s3006", "s3007", "s3008"]:
            cue_times.append((onset, desc))
    
    # Define trial windows: from cue to next cue (or end)
    for i, (t, desc) in enumerate(cue_times):
        start = t
        end = cue_times[i+1][0] if i+1 < len(cue_times) else raw.times[-1]
        if desc == "s3021":
            avatar_trials.append((start, end))
        elif desc == "s3041":
            stick_trials.append((start, end))
    
    # Compute response times for avatar trials
    for start, end in avatar_trials:
        # Find s3024, s3025, s3026, s3027 in window
        t3024 = t3025 = t3026 = t3027 = None
        for onset, desc in events_list:
            if start <= onset < end:
                if desc == "s3024":
                    t3024 = onset
                elif desc == "s3025":
                    t3025 = onset
                elif desc == "s3026":
                    t3026 = onset
                elif desc == "s3027":
                    t3027 = onset
        
        if t3024 is not None and t3025 is not None:
            rt_val = t3025 - t3024
            # Broadcast to trial window
            start_idx = int(start * sfreq)
            end_idx = int(end * sfreq)
            start_idx = max(0, min(start_idx, n_samples))
            end_idx = max(0, min(end_idx, n_samples))
            if start_idx < end_idx:
                rt_loc[0, start_idx:end_idx] = rt_val
        
        if t3026 is not None and t3027 is not None:
            rt_val = t3027 - t3026
            start_idx = int(start * sfreq)
            end_idx = int(end * sfreq)
            start_idx = max(0, min(start_idx, n_samples))
            end_idx = max(0, min(end_idx, n_samples))
            if start_idx < end_idx:
                rt_status[0, start_idx:end_idx] = rt_val
    
    # Compute response times for stick trials
    for start, end in stick_trials:
        t3044 = t3045 = t3046 = t3047 = None
        for onset, desc in events_list:
            if start <= onset < end:
                if desc == "s3044":
                    t3044 = onset
                elif desc == "s3045":
                    t3045 = onset
                elif desc == "s3046":
                    t3046 = onset
                elif desc == "s3047":
                    t3047 = onset
        
        if t3044 is not None and t3045 is not None:
            rt_val = t3045 - t3044
            start_idx = int(start * sfreq)
            end_idx = int(end * sfreq)
            start_idx = max(0, min(start_idx, n_samples))
            end_idx = max(0, min(end_idx, n_samples))
            if start_idx < end_idx:
                rt_loc[0, start_idx:end_idx] = rt_val
        
        if t3046 is not None and t3047 is not None:
            rt_val = t3047 - t3046
            start_idx = int(start * sfreq)
            end_idx = int(end * sfreq)
            start_idx = max(0, min(start_idx, n_samples))
            end_idx = max(0, min(end_idx, n_samples))
            if start_idx < end_idx:
                rt_status[0, start_idx:end_idx] = rt_val
    
    return rt_loc, rt_status


def _events_tsv_to_annotations(events_df: pd.DataFrame, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert events.tsv DataFrame to MNE Annotations.
    
    Preserves literal values from 'value' or 'trial_type' columns.
    """
    if events_df is None or len(events_df) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0)) if pd.notna(row.get("duration", 0)) else 0.0
        
        # Prefer 'value' column, fall back to 'trial_type'
        desc = None
        if "value" in row and pd.notna(row["value"]):
            desc = str(row["value"])
        elif "trial_type" in row and pd.notna(row["trial_type"]):
            desc = str(row["trial_type"])
        elif "stim_type" in row and pd.notna(row["stim_type"]):
            desc = str(row["stim_type"])
        else:
            continue
        
        # Skip empty descriptions
        if not desc or desc.lower() in ["n/a", "na", ""]:
            continue
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions, orig_time=raw.info["meas_date"])


@dataclass
class OpenNeuroDS003702Kernel:
    """Stage1 kernel for OpenNeuro DS003702 Social Memory Cueing dataset."""

    KERNEL_ID: str = "openneuro-ds003702-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "dataset_path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from file path
        # BIDS pattern: sub-XX/...
        subject_id = "unknown"
        parts = file_path.replace("\\", "/").split("/")
        for part in parts:
            if part.startswith("sub-"):
                subject_id = part
                break
        
        # --- Channel rename BEFORE set_montage (Rule 7) ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage for standard 10-20 channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in both raw and montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common_chs = sorted(list(montage_chs & raw_chs))
            if len(common_chs) >= 10:  # Only set if we have enough matches
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        # Ensure channel types: EEG channels should be 'eeg', any known misc should be 'misc'
        ch_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            if upper.startswith("EEG") or upper in [c.upper() for c in _STANDARD_64_CHANNELS]:
                ch_types[ch_name] = "eeg"
            elif any(x in upper for x in ["EOG", "ECG", "EMG", "RESP", "MISC"]):
                ch_types[ch_name] = "misc"
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # --- Read participants.tsv for required info fields ---
        participant_info = _get_subject_info_from_participants(dataset_path, subject_id)
        
        # Normalize sex to lowercase
        sex_raw = participant_info.get("Gender", "unknown").lower()
        if sex_raw in ["f", "female"]:
            sex = "female"
        elif sex_raw in ["m", "male"]:
            sex = "male"
        else:
            sex = "unknown"
        
        age = participant_info.get("Age", "unknown")
        handedness = participant_info.get("Handedness", "unknown").lower()
        if handedness not in ["right", "left"]:
            handedness = "unknown"
        
        # --- Device metadata (inferred from dataset documentation) ---
        # Source: Data descriptor paper DOI 10.1016/j.dib.2022.107827
        # 64-channel BrainVision/BrainAmp system at 500 Hz
        # inferred by LLM, needs human review
        amplifier = "BrainAmp"  # inferred by LLM, needs human review
        cap = "Ag/AgCl"  # inferred by LLM, needs human review
        
        # --- Build eegunity_description ---
        eegunity_description = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add required info fields from participants.tsv
        for field in ["Age", "Gender", "Handedness"]:
            val = participant_info.get(field, "unknown")
            eegunity_description[field] = str(val) if val != "unknown" else "unknown"
        
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # --- Handle events from events.tsv if raw lacks annotations ---
        # BrainVision .eeg files should have markers, but check if annotations are empty
        has_native_events = False
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Check if there are actual stimulus events (not just boundaries)
            for desc in raw.annotations.description:
                if desc and not desc.startswith("New Segment") and "Impedance" not in desc:
                    has_native_events = True
                    break
        
        events_tsv_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_tsv_path) if events_tsv_path else None
        
        if not has_native_events and events_df is not None and len(events_df) > 0:
            # Derive annotations from events.tsv
            annots = _events_tsv_to_annotations(events_df, raw)
            if len(annots) > 0:
                raw.set_annotations(annots)
        elif events_df is not None and len(events_df) > 0:
            # Even if raw has events, ensure we have the required event IDs
            # Merge events.tsv annotations with existing
            existing_annots = raw.annotations
            new_annots = _events_tsv_to_annotations(events_df, raw)
            
            # Check if we need to supplement
            existing_descs = set(existing_annots.description) if existing_annots else set()
            required_events = {
                's3001', 's3002', 's3003', 's3004', 's3005', 's3006', 's3007', 's3008',
                's3021', 's3022', 's3023', 's3024', 's3025', 's3026', 's3027', 's3028',
                's3040', 's3041', 's3042', 's3043', 's3044', 's3045', 's3046', 's3047', 's3048',
                's3220', 's3221'
            }
            
            # Normalize existing descriptions
            normalized_existing = set()
            for d in existing_descs:
                if "/" in d:
                    normalized_existing.add(d.split("/")[-1])
                else:
                    normalized_existing.add(d)
            
            missing_required = required_events - normalized_existing
            
            if missing_required and len(new_annots) > 0:
                # Supplement with missing events from events.tsv
                combined_onsets = list(existing_annots.onset) if existing_annots else []
                combined_durations = list(existing_annots.duration) if existing_annots else []
                combined_descriptions = list(existing_annots.description) if existing_annots else []
                
                for i in range(len(new_annots)):
                    desc = new_annots.description[i]
                    norm_desc = desc.split("/")[-1] if "/" in desc else desc
                    if norm_desc in missing_required:
                        combined_onsets.append(new_annots.onset[i])
                        combined_durations.append(new_annots.duration[i])
                        combined_descriptions.append(desc)
                
                if len(combined_onsets) > len(existing_annots) if existing_annots else True:
                    merged = mne.Annotations(
                        onset=combined_onsets,
                        duration=combined_durations,
                        description=combined_descriptions,
                        orig_time=existing_annots.orig_time if existing_annots else raw.info["meas_date"]
                    )
                    raw.set_annotations(merged)
        
        # --- Derived misc channels: response_time_location, response_time_status ---
        rt_loc, rt_status = _compute_response_time_misc(raw, events_df)
        
        # Add as misc channels
        for ch_name, data in [("response_time_location", rt_loc), ("response_time_status", rt_status)]:
            if ch_name not in raw.ch_names:
                info = mne.create_info([ch_name], sfreq=raw.info["sfreq"], ch_types=["misc"])
                raw_misc = mne.io.RawArray(data, info, first_samp=raw.first_samp)
                raw.add_channels([raw_misc], force_update_info=True)
        
        # Ensure misc channel types are set correctly
        misc_channels = {}
        for ch_name in raw.ch_names:
            if ch_name in ["response_time_location", "response_time_status"]:
                misc_channels[ch_name] = "misc"
        
        if misc_channels:
            raw.set_channel_types(misc_channels)
        
        return raw


KERNEL = OpenNeuroDS003702Kernel()