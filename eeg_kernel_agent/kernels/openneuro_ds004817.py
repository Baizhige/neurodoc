"""OpenNeuro DS004817 stage1 kernel for EEGUnity.

Dataset: EEG-attention-rsvp-exp2 (RSVP Experiment 2)
Source: https://openneuro.org/datasets/ds004817
Reference: https://doi.org/10.51628/001c.21174

Paradigm: Rapid Serial Visual Presentation (RSVP) task investigating
neural dynamics of prioritizing task-relevant information.

Events: E 1, E 2, E 3, Event/E 1, Event/E 2, Event/E 3, boundary
- E 1 / Event/E 1: Task-relevant (attended) stimulus
- E 2 / Event/E 2: Task-irrelevant (unattended) stimulus
- E 3 / Event/E 3: Additional stimulus type
- boundary: Artifact boundary marker

BIDS dataset with standard 10-20 channels, 63 channels, 1000 Hz sampling rate.
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


# Standard 63-channel mapping for this dataset (EEG- prefix to standard 10-20)
# Source: BIDS channel info and standard 10-20 layout
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_STANDARD_63_CHANNEL_MAP = {
    "Fp1": "EEG-Fp1",
    "Fpz": "EEG-Fpz",
    "Fp2": "EEG-Fp2",
    "F7": "EEG-F7",
    "F3": "EEG-F3",
    "Fz": "EEG-Fz",
    "F4": "EEG-F4",
    "F8": "EEG-F8",
    "FC5": "EEG-FC5",
    "FC3": "EEG-FC3",
    "FC1": "EEG-FC1",
    "FCz": "EEG-FCz",
    "FC2": "EEG-FC2",
    "FC4": "EEG-FC4",
    "FC6": "EEG-FC6",
    "T7": "EEG-T7",
    "C5": "EEG-C5",
    "C3": "EEG-C3",
    "C1": "EEG-C1",
    "Cz": "EEG-Cz",
    "C2": "EEG-C2",
    "C4": "EEG-C4",
    "C6": "EEG-C6",
    "T8": "EEG-T8",
    "CP5": "EEG-CP5",
    "CP3": "EEG-CP3",
    "CP1": "EEG-CP1",
    "CPz": "EEG-CPz",
    "CP2": "EEG-CP2",
    "CP4": "EEG-CP4",
    "CP6": "EEG-CP6",
    "P7": "EEG-P7",
    "P5": "EEG-P5",
    "P3": "EEG-P3",
    "P1": "EEG-P1",
    "Pz": "EEG-Pz",
    "P2": "EEG-P2",
    "P4": "EEG-P4",
    "P6": "EEG-P6",
    "P8": "EEG-P8",
    "PO7": "EEG-PO7",
    "PO3": "EEG-PO3",
    "POz": "EEG-POz",
    "PO4": "EEG-PO4",
    "PO8": "EEG-PO8",
    "O1": "EEG-O1",
    "Oz": "EEG-Oz",
    "O2": "EEG-O2",
    "AF7": "EEG-AF7",
    "AF3": "EEG-AF3",
    "AFz": "EEG-AFz",
    "AF4": "EEG-AF4",
    "AF8": "EEG-AF8",
    "FT7": "EEG-FT7",
    "FT8": "EEG-FT8",
    "TP7": "EEG-TP7",
    "TP8": "EEG-TP8",
    "PO9": "EEG-PO9",
    "PO10": "EEG-PO10",
    "O9": "EEG-O9",
    "O10": "EEG-O10",
}

_NUMERIC_PATTERN = re.compile(r"EEG-(\d+)")


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for standard 10-20 channel names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Try standard mapping first
    for std_name, bids_name in _STANDARD_63_CHANNEL_MAP.items():
        if bids_name in existing_names and bids_name != std_name:
            rename_map[bids_name] = std_name
    
    # Handle any remaining numeric EEG-XX channels
    for ch_name in existing_names:
        if ch_name in rename_map or ch_name in rename_map.values():
            continue
        match = _NUMERIC_PATTERN.match(ch_name)
        if match:
            # Try to map numeric channels if we have a known ordering
            # This shouldn't happen for this dataset but is defensive
            pass
    
    return rename_map


def _get_subject_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-([a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return ""


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS convention: same directory, same basename with _events.tsv suffix
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: task-rsvp_events.tsv
    dir_path = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    match = re.search(r"sub-[a-zA-Z0-9]+_(ses-[a-zA-Z0-9]+_)?task-([a-zA-Z0-9]+)", base_name)
    if match:
        task = match.group(2)
        sub_match = re.search(r"(sub-[a-zA-Z0-9]+)", base_name)
        if sub_match:
            sub = sub_match.group(1)
            alt_path = os.path.join(dir_path, f"{sub}_task-{task}_events.tsv")
            if os.path.exists(alt_path):
                return alt_path
    
    # Look for any _events.tsv in same directory
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _parse_object_category(objectstim: str) -> float:
    """Parse objectstim filename to extract category: birds→0, fish→1, boats→2, planes→3."""
    if not objectstim or pd.isna(objectstim) or objectstim == "":
        return np.nan
    
    obj_lower = str(objectstim).lower()
    if "birds" in obj_lower or "bird" in obj_lower:
        return 0.0
    elif "fish" in obj_lower:
        return 1.0
    elif "boats" in obj_lower or "boat" in obj_lower:
        return 2.0
    elif "planes" in obj_lower or "plane" in obj_lower:
        return 3.0
    else:
        return np.nan


def _create_derived_misc_channel(raw: mne.io.BaseRaw, name: str, values: np.ndarray) -> mne.io.BaseRaw:
    """Create a derived MISC channel from values array."""
    # Create info for new channel
    info = mne.create_info([name], raw.info["sfreq"], ["misc"])
    # Create RawArray with the values
    raw_misc = mne.io.RawArray(values.reshape(1, -1), info)
    # Add to existing raw
    raw.add_channels([raw_misc], force_update_info=True)
    return raw


def _build_derived_misc_from_events(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    column: str,
    channel_name: str,
    transform_func: Optional[Any] = None,
    default_value: float = 0.0,
) -> mne.io.BaseRaw:
    """Build a derived misc channel by aligning events.tsv rows with raw times.
    
    For each event in events.tsv, find the closest sample in raw and set the
    channel value for that trial period. Uses onset column for timing.
    """
    n_samples = raw.n_times
    sfreq = raw.info["sfreq"]
    data = np.full(n_samples, default_value, dtype=float)
    
    # Get event onsets in samples
    if "onset" not in events_df.columns:
        # Fallback: use sample or try to reconstruct from other columns
        return _create_derived_misc_channel(raw, channel_name, data)
    
    # Sort events by onset
    events_sorted = events_df.sort_values("onset").reset_index(drop=True)
    
    for i, row in events_sorted.iterrows():
        onset_sec = float(row["onset"])
        onset_sample = int(onset_sec * sfreq)
        
        # Determine end of this trial (next event onset or end of data)
        if i + 1 < len(events_sorted):
            next_onset_sec = float(events_sorted.iloc[i + 1]["onset"])
            end_sample = int(next_onset_sec * sfreq)
        else:
            end_sample = n_samples
        
        # Clamp to valid range
        onset_sample = max(0, min(onset_sample, n_samples))
        end_sample = max(onset_sample, min(end_sample, n_samples))
        
        # Get value
        val = row.get(column, default_value)
        if pd.isna(val):
            val = default_value
        else:
            if transform_func is not None:
                val = transform_func(val)
            else:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    val = default_value
        
        # Set value for trial period
        if onset_sample < end_sample:
            data[onset_sample:end_sample] = val
    
    return _create_derived_misc_channel(raw, channel_name, data)


@dataclass
class OpenNeuroDS004817Kernel:
    """Stage1 kernel for OpenNeuro ds004817 (EEG-attention-rsvp-exp2)."""

    KERNEL_ID: str = "openneuro-ds004817-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- 1. Channel rename (before set_montage) ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage if channels match
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Check that all montage channels exist in raw
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            if montage_chs.intersection(raw_chs):
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage optional, fail silently

        # --- 2. Read participants.tsv for subject info ---
        subject_id = _get_subject_from_path(file_path)
        participants_path = _find_participants_tsv(file_path)
        
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"
        extra_info: Dict[str, str] = {}
        
        if participants_path and os.path.exists(participants_path):
            try:
                participants_df = pd.read_csv(participants_path, sep="\t")
                # Find subject row
                sub_col = "participant_id"
                if sub_col in participants_df.columns:
                    # Match subject ID (with or without sub- prefix)
                    sub_match = participants_df[participants_df[sub_col].str.contains(subject_id, na=False, regex=False)]
                    if len(sub_match) == 0:
                        # Try with sub- prefix
                        sub_match = participants_df[participants_df[sub_col] == f"sub-{subject_id}"]
                    if len(sub_match) > 0:
                        sub_row = sub_match.iloc[0]
                        
                        # Age
                        if "age" in sub_row:
                            age = str(sub_row["age"]) if pd.notna(sub_row["age"]) else "unknown"
                        
                        # Sex/gender (lowercase)
                        for sex_col in ["sex", "gender"]:
                            if sex_col in sub_row and pd.notna(sub_row[sex_col]):
                                sex_val = str(sub_row[sex_col]).strip().lower()
                                if sex_val in ["m", "male"]:
                                    sex = "male"
                                elif sex_val in ["f", "female"]:
                                    sex = "female"
                                else:
                                    sex = "unknown"
                                break
                        
                        # Handedness
                        if "handedness" in sub_row and pd.notna(sub_row["handedness"]):
                            hand_val = str(sub_row["handedness"]).strip().lower()
                            if hand_val in ["r", "right"]:
                                handedness = "right"
                            elif hand_val in ["l", "left"]:
                                handedness = "left"
                            else:
                                handedness = "unknown"
                        
                        # Extra required info fields
                        for field in ["age", "gender", "handedness"]:
                            if field in sub_row and pd.notna(sub_row[field]):
                                extra_info[field] = str(sub_row[field])
                            else:
                                extra_info[field] = "unknown"
            except Exception:
                pass  # Keep defaults

        # --- 3. Update description with eegunity_description ---
        original_desc = raw.info.get("description", "") or ""
        
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": "unknown",  # Not specified in BIDS sidecars
            "cap": "unknown",  # Not specified in BIDS sidecars
            "handedness": handedness,
        }
        # Add extra required info fields
        for field in ["age", "gender", "handedness"]:
            if field in extra_info:
                eegunity_desc[field] = extra_info[field]
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)

        # --- 4. Handle events from events.tsv ---
        events_path = _find_events_tsv(file_path)
        events_df: Optional[pd.DataFrame] = None
        
        if events_path and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
            except Exception:
                events_df = None

        # Check if raw already has annotations/events
        has_native_events = False
        try:
            # Check for annotations
            if raw.annotations is not None and len(raw.annotations) > 0:
                has_native_events = True
            # Check for stim channels
            stim_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=True, exclude=[])
            if len(stim_picks) > 0:
                has_native_events = True
        except Exception:
            pass

        # Derive annotations from events.tsv if needed
        if events_df is not None and len(events_df) > 0:
            # Check if we need to add annotations (format may not carry its own triggers)
            need_annotations = False
            
            # EDF, SET without events, plain FIF without baked events need help
            file_lower = file_path.lower()
            if file_lower.endswith(".edf") or file_lower.endswith(".bdf"):
                need_annotations = not has_native_events
            elif file_lower.endswith(".set"):
                # EEGLAB .set may or may not have events
                need_annotations = not has_native_events
            elif file_lower.endswith(".fif"):
                need_annotations = not has_native_events
            elif file_lower.endswith(".eeg"):
                # BrainVision - check if marker file exists
                vhdr_path = file_path.replace(".eeg", ".vhdr")
                vmrk_path = file_path.replace(".eeg", ".vmrk")
                if not (os.path.exists(vmrk_path) or os.path.exists(vhdr_path)):
                    need_annotations = True
            
            # Also add annotations if we have events.tsv columns we need for derived misc
            # (always process events_df for derived misc channels)
            
            if need_annotations and "onset" in events_df.columns:
                # Build annotations from events.tsv
                onsets = []
                durations = []
                descriptions = []
                
                for _, ev_row in events_df.iterrows():
                    onset = float(ev_row["onset"])
                    duration = float(ev_row.get("duration", 0.0))
                    if pd.isna(duration):
                        duration = 0.0
                    
                    # Use trial_type or value for description
                    desc = None
                    for desc_col in ["trial_type", "value", "event_type"]:
                        if desc_col in ev_row and pd.notna(ev_row[desc_col]):
                            desc = str(ev_row[desc_col])
                            break
                    
                    if desc is None:
                        desc = "unknown"
                    
                    # Aggregate duplicate event formats
                    # Map "Event/E 1" -> "E 1", etc.
                    if desc.startswith("Event/"):
                        desc = desc[6:]  # Remove "Event/" prefix
                    
                    onsets.append(onset)
                    durations.append(duration)
                    descriptions.append(desc)
                
                if len(onsets) > 0:
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)

        # --- 5. Create derived misc channels from events.tsv ---
        if events_df is not None and len(events_df) > 0 and "onset" in events_df.columns:
            sfreq = raw.info["sfreq"]
            n_samples = raw.n_times
            
            # Helper to create step-function channels
            def _make_step_channel(values: List[float], channel_name: str) -> None:
                """Create a step-function misc channel from per-trial values."""
                data = np.zeros(n_samples, dtype=float)
                
                # Sort events by onset
                events_sorted = events_df.sort_values("onset").reset_index(drop=True)
                
                for i, (_, ev_row) in enumerate(events_sorted.iterrows()):
                    onset_sec = float(ev_row["onset"])
                    onset_sample = int(onset_sec * sfreq)
                    
                    # End at next event or end of data
                    if i + 1 < len(events_sorted):
                        next_onset = float(events_sorted.iloc[i + 1]["onset"])
                        end_sample = int(next_onset * sfreq)
                    else:
                        end_sample = n_samples
                    
                    onset_sample = max(0, min(onset_sample, n_samples))
                    end_sample = max(onset_sample, min(end_sample, n_samples))
                    
                    val = values[i] if i < len(values) else 0.0
                    if not np.isnan(val):
                        data[onset_sample:end_sample] = val
                
                # Add as misc channel
                info = mne.create_info([channel_name], sfreq, ["misc"])
                raw_misc = mne.io.RawArray(data.reshape(1, -1), info)
                raw.add_channels([raw_misc], force_update_info=True)
            
            # 5.1 object_category_4class
            if "objectstim" in events_df.columns:
                cat_values = []
                for _, ev_row in events_df.iterrows():
                    cat = _parse_object_category(ev_row.get("objectstim", ""))
                    cat_values.append(cat)
                # Only include epochs where objectstim is non-empty
                # Use NaN for non-object trials
                cat_values = [v if not np.isnan(v) else np.nan for v in cat_values]
                # For step function, use NaN as 0 or keep NaN? Use actual values, 0 for no-object
                step_values = [v if not np.isnan(v) else 0.0 for v in cat_values]
                _make_step_channel(step_values, "object_category_4class")
            
            # 5.2 is2back_target
            if "is2back" in events_df.columns:
                is2back_values = []
                for _, ev_row in events_df.iterrows():
                    val = ev_row.get("is2back", 0)
                    try:
                        val = float(val)
                        if val not in [0, 1]:
                            val = 0.0
                    except (ValueError, TypeError):
                        val = 0.0
                    is2back_values.append(val)
                _make_step_channel(is2back_values, "is2back_target")
            
            # 5.3 response_time
            if "rt" in events_df.columns:
                rt_values = []
                for _, ev_row in events_df.iterrows():
                    val = ev_row.get("rt", 0)
                    try:
                        val = float(val)
                        if val == 0:
                            val = np.nan  # No response
                    except (ValueError, TypeError):
                        val = np.nan
                    rt_values.append(val)
                # For step channel, use NaN -> 0 or keep as NaN? Use 0 for NaN to avoid issues
                step_rt = [v if not np.isnan(v) else 0.0 for v in rt_values]
                _make_step_channel(step_rt, "response_time")
            
            # 5.4 attention_condition_reg
            if "condition" in events_df.columns:
                cond_values = []
                for _, ev_row in events_df.iterrows():
                    val = ev_row.get("condition", 0)
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        val = 0.0
                    cond_values.append(val)
                _make_step_channel(cond_values, "attention_condition_reg")
            
            # 5.5 stream_number
            if "streamnumber" in events_df.columns:
                stream_values = []
                for _, ev_row in events_df.iterrows():
                    val = ev_row.get("streamnumber", 0)
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        val = 0.0
                    stream_values.append(val)
                _make_step_channel(stream_values, "stream_number")
            
            # 5.6 stim_number
            if "stimnumber" in events_df.columns:
                stim_values = []
                for _, ev_row in events_df.iterrows():
                    val = ev_row.get("stimnumber", 0)
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        val = 0.0
                    stim_values.append(val)
                _make_step_channel(stim_values, "stim_number")

        # --- 6. Ensure required native misc channels are misc type ---
        # No required native misc channels specified for this dataset
        
        # --- 7. Final verification ---
        # Ensure all derived misc channels exist and have correct type
        required_misc = [
            "object_category_4class",
            "is2back_target", 
            "response_time",
            "attention_condition_reg",
            "stream_number",
            "stim_number",
        ]
        
        for misc_name in required_misc:
            if misc_name in raw.ch_names:
                # Ensure it's misc type
                current_types = raw.get_channel_types(picks=[misc_name])
                if current_types[0] != "misc":
                    raw.set_channel_types({misc_name: "misc"})

        return raw


KERNEL = OpenNeuroDS004817Kernel()