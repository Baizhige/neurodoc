"""OpenNeuro ds003800 stage1 kernel for EEGUnity.

Auditory Gamma Entrainment dataset - 40 Hz amplitude-modulated auditory stimulation
in elderly participants with dementia.

This kernel handles BIDS-compliant EDF files with standard 10-20 channels.
Events are read from sidecar *_events.tsv files when the EDF lacks embedded annotations.

Source: https://openneuro.org/datasets/ds003800
Reference: https://doi.org/10.1016/j.dib.2022.107839
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["Age", "Gender", "MMSE"]

# Required derived misc channels
_REQUIRED_DERIVED_MISC = ["duration"]

# Standard 10-20 system channel mapping for 19 channels
# Source: Standard 10-20 electrode placement system, 19-channel configuration
# Annotator: LLM, 2026-04-08
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T3", "C3", "Cz", "C4", "T4",
    "T5", "P3", "Pz", "P4", "T6",
    "O1", "O2"
]


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    import re
    match = re.search(r'sub-(\w+)', file_path)
    if match:
        return f"sub-{match.group(1)}"
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv sidecar file."""
    # BIDS convention: same directory, same base name with _events.tsv suffix
    base = file_path.replace(".edf", "").replace(".set", "").replace(".eeg", "").replace(".fif", "")
    events_tsv = base + "_events.tsv"
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try in the same directory with pattern matching
    dir_path = os.path.dirname(file_path)
    if not dir_path:
        dir_path = "."
    
    base_name = os.path.basename(file_path).split(".")[0]
    # Remove any run/task suffixes to find matching events
    for fname in os.listdir(dir_path):
        if fname.endswith("_events.tsv") and base_name.split("_run-")[0].split("_task-")[0] in fname:
            return os.path.join(dir_path, fname)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find the participants.tsv file in the dataset root."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    # Walk up to find participants.tsv
    for _ in range(10):  # Limit search depth
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None


def _read_participants_info(file_path: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {}
    participants_tsv = _find_participants_tsv(file_path)
    if participants_tsv is None:
        return info
    
    subject_id = _get_subject_id_from_path(file_path)
    if subject_id is None:
        return info
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        # Match participant_id
        participant_col = "participant_id" if "participant_id" in df.columns else "Participant ID"
        if participant_col not in df.columns:
            # Try case-insensitive
            for col in df.columns:
                if col.lower() == "participant_id":
                    participant_col = col
                    break
        
        if participant_col in df.columns:
            row = df[df[participant_col] == subject_id]
            if len(row) == 0:
                # Try without "sub-" prefix
                row = df[df[participant_col] == subject_id.replace("sub-", "")]
            if len(row) > 0:
                for field in _REQUIRED_INFO_FIELDS:
                    # Case-insensitive column matching
                    for col in df.columns:
                        if col.lower() == field.lower():
                            val = row[col].values[0]
                            # Handle missing/NaN values
                            if pd.isna(val):
                                info[field] = "unknown"
                            else:
                                info[field] = str(val)
                            break
    except Exception:
        pass
    
    return info


def _read_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Read events from BIDS events.tsv file."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        return df
    except Exception:
        return None


def _events_tsv_to_annotations(events_df: pd.DataFrame) -> Optional[mne.Annotations]:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    # Required columns: onset, (duration), and either trial_type or value
    if "onset" not in events_df.columns:
        return None
    
    onsets = events_df["onset"].values.astype(float)
    
    # Duration
    if "duration" in events_df.columns:
        durations = events_df["duration"].values.astype(float)
    else:
        durations = np.zeros(len(onsets))
    
    # Description: prefer trial_type, then value, then stim_type
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        # Map numeric values to labels if possible
        descs = []
        for v in events_df["value"]:
            if pd.isna(v):
                descs.append("unknown")
            else:
                # Check for known mappings from events.json
                try:
                    val_float = float(v)
                    if val_float == 1:
                        descs.append("Rest")
                    elif val_float == 2:
                        descs.append("Stimulus")
                    else:
                        descs.append(str(v))
                except (ValueError, TypeError):
                    descs.append(str(v))
        descriptions = np.array(descs)
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    else:
        descriptions = np.array(["event"] * len(onsets))
    
    # Filter out empty/NaN descriptions
    valid_mask = [d is not None and str(d).strip() != "" and str(d).lower() != "nan" for d in descriptions]
    if not any(valid_mask):
        return None
    
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _has_embedded_events(raw: mne.io.BaseRaw) -> bool:
    """Check if raw file has embedded events/annotations."""
    # Check for existing annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        # Check if they look like actual events, not just measurement annotations
        for desc in raw.annotations.description:
            if desc in ["Rest", "Stimulus", "1", "2", "Resting", "Stimulation"]:
                return True
            try:
                val = int(float(desc))
                if val in [1, 2]:
                    return True
            except (ValueError, TypeError):
                pass
    
    # Check for stim channels
    stim_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=True, exclude=[])
    if len(stim_picks) > 0:
        return True
    
    return False


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Direct matches (case-insensitive)
    for std_ch in _STANDARD_1020_CHANNELS:
        for ch in raw.ch_names:
            if ch.upper() == std_ch.upper() and ch != std_ch:
                rename_map[ch] = std_ch
                break
    
    # EEG-prefixed numbered channels
    eeg_numbered = [(ch, i) for i, ch in enumerate(raw.ch_names) 
                    if ch.upper().startswith("EEG") and not any(c.isalpha() for c in ch[3:].strip())]
    for ch, idx in eeg_numbered:
        if idx < len(_STANDARD_1020_CHANNELS) and ch not in rename_map:
            new_name = _STANDARD_1020_CHANNELS[idx]
            if new_name not in existing or new_name == ch:
                rename_map[ch] = new_name
    
    # Handle common variants
    variant_map = {
        "T3": "T7", "T4": "T8", "T5": "P7", "T6": "P8",
        "T7": "T7", "T8": "T8", "P7": "P7", "P8": "P8",
    }
    for ch in raw.ch_names:
        if ch in variant_map and ch not in rename_map:
            # Only rename if the target isn't already present
            target = variant_map[ch]
            if target not in existing:
                rename_map[ch] = target
    
    return rename_map


def _create_duration_misc_channel(raw: mne.io.BaseRaw, events_tsv_path: str) -> mne.io.BaseRaw:
    """Create derived 'duration' misc channel from events.tsv duration column."""
    events_df = _read_events_tsv(events_tsv_path)
    if events_df is None or "duration" not in events_df.columns or "onset" not in events_df.columns:
        # Create empty duration channel with zeros if no events data
        data = np.zeros((1, len(raw.times)))
        info = mne.create_info(["duration"], raw.info["sfreq"], ch_types=["misc"])
        duration_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
        raw.add_channels([duration_raw], force_update_info=True)
        return raw
    
    # Build duration signal: at each sample, use the duration of the active event
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    duration_signal = np.zeros(n_samples)
    
    for _, row in events_df.iterrows():
        onset = float(row["onset"])
        duration = float(row["duration"]) if pd.notna(row["duration"]) else 0.0
        
        # Determine end: either onset+duration or next event onset
        start_sample = int(onset * sfreq)
        end_sample = int((onset + duration) * sfreq) if duration > 0 else n_samples
        
        # Clamp to valid range
        start_sample = max(0, min(start_sample, n_samples))
        end_sample = max(0, min(end_sample, n_samples))
        
        if start_sample < end_sample:
            duration_signal[start_sample:end_sample] = duration
    
    # Create RawArray and add
    data = duration_signal.reshape(1, -1)
    info = mne.create_info(["duration"], sfreq, ch_types=["misc"])
    duration_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    
    # Ensure time alignment
    duration_raw.set_annotations(raw.annotations)
    
    raw.add_channels([duration_raw], force_update_info=True)
    
    return raw


@dataclass
class OpenNeuroDS003800Kernel:
    """Stage1 kernel for OpenNeuro ds003800 (Auditory Gamma Entrainment)."""

    KERNEL_ID: str = "openneuro-ds003800-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- 1. Channel renaming to standard 10-20 ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage after renaming
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Pick only channels that exist in both raw and montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common_chs = list(raw_chs & montage_chs)
            if len(common_chs) >= 10:  # Require reasonable coverage
                raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage not critical
        
        # --- 2. Read participants.tsv info ---
        participants_info = _read_participants_info(file_path)
        
        # Build eegunity_description
        # Age: from participants.tsv or unknown
        age = participants_info.get("Age", "unknown")
        if age == "unknown":
            age = "unknown"  # LLM 推断，需人类复核
        
        # Sex: from participants.tsv Gender column, lowercase
        sex = participants_info.get("Gender", "unknown").lower()
        if sex not in ["male", "female"]:
            sex = "unknown"
        
        # Device info: not available in dataset metadata
        # Source: Dataset descriptor (DOI: 10.1016/j.dib.2022.107839) - no device specified
        # LLM 推断，需人类复核
        amplifier = "unknown"  # LLM 推断，需人类复核
        cap = "unknown"  # LLM 推断，需人类复核
        handedness = "unknown"  # LLM 推断，需人类复核
        
        # Build description dict
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_desc = {
            "age": str(age),
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        # Add required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field in participants_info:
                eegunity_desc[field] = str(participants_info[field])
            else:
                eegunity_desc[field] = "unknown"
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })
        
        # --- 3. Events handling: derive from events.tsv if raw lacks embedded events ---
        events_tsv_path = _find_events_tsv(file_path)
        
        if not _has_embedded_events(raw) and events_tsv_path is not None:
            # EDF without annotations - must derive from events.tsv
            events_df = _read_events_tsv(events_tsv_path)
            annotations = _events_tsv_to_annotations(events_df)
            if annotations is not None:
                raw.set_annotations(annotations)
        
        # Also ensure annotations match expected event IDs even if embedded
        # Remap numeric codes to standard names if needed
        if raw.annotations is not None and len(raw.annotations) > 0:
            new_descriptions = []
            needs_update = False
            for desc in raw.annotations.description:
                remapped = desc
                try:
                    val = int(float(desc))
                    if val == 1:
                        remapped = "Rest"
                        needs_update = True
                    elif val == 2:
                        remapped = "Stimulus"
                        needs_update = True
                except (ValueError, TypeError):
                    # Keep as-is if already string
                    if desc in ["Rest", "Stimulus"]:
                        pass
                    elif desc.lower() in ["rest", "resting"]:
                        remapped = "Rest"
                        needs_update = True
                    elif desc.lower() in ["stimulus", "stimulation", "stim"]:
                        remapped = "Stimulus"
                        needs_update = True
                new_descriptions.append(remapped)
            
            if needs_update:
                new_annot = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(new_annot)
        
        # --- 4. Derived misc channels ---
        # Create 'duration' misc channel from events.tsv
        if events_tsv_path is not None:
            raw = _create_duration_misc_channel(raw, events_tsv_path)
        else:
            # Create empty duration channel if no events.tsv found
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(["duration"], raw.info["sfreq"], ch_types=["misc"])
            duration_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([duration_raw], force_update_info=True)
        
        # Ensure all required misc channels exist and have correct type
        for ch_name in _REQUIRED_DERIVED_MISC:
            if ch_name in raw.ch_names:
                current_type = raw.get_channel_types(picks=[ch_name])[0]
                if current_type != "misc":
                    raw.set_channel_types({ch_name: "misc"})
        
        # --- 5. Final validation ---
        # Ensure Rest and Stimulus events are present in annotations
        if raw.annotations is not None:
            event_ids_found = set(raw.annotations.description)
            # Check that we have the required events
            required_events = {"Rest", "Stimulus"}
            missing = required_events - event_ids_found
            # If missing, try to reconstruct from events.tsv one more time
            if missing and events_tsv_path is not None:
                events_df = _read_events_tsv(events_tsv_path)
                if events_df is not None and len(events_df) > 0:
                    # Force rebuild annotations
                    annotations = _events_tsv_to_annotations(events_df)
                    if annotations is not None:
                        raw.set_annotations(annotations)
        
        return raw


KERNEL = OpenNeuroDS003800Kernel()