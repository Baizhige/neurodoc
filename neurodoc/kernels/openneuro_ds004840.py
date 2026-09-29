"""OpenNeuro ds004840 stage1 kernel for EEGUnity.

EEG/ECG/EMG recordings during Music-Assisted Relaxation (MAR) therapy
in ICU burn patients. BIDS-compliant dataset with participants.tsv
and events.tsv sidecars. Phases (PRE/MTI/POST) are derived from
events.tsv annotations.

Source: https://openneuro.org/datasets/ds004840
Paper: 10.1038/s41598-024-73211-3
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Channel rename map: raw names -> standard 10-20 names
# Source: OpenNeuro ds004840 dataset, EEG channel labels follow standard 10-20 convention
# with numeric prefixes; mapped based on BIDS eeg.json and channel inspection
# Annotator: LLM, 2026-04-08
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG-1": "Fp1",
    "EEG-2": "Fpz",
    "EEG-3": "Fp2",
    "EEG-4": "F7",
    "EEG-5": "F3",
    "EEG-6": "Fz",
    "EEG-7": "F4",
    "EEG-8": "F8",
    "EEG-9": "T7",
    "EEG-10": "P7",
    "EEG-11": "C3",
    "EEG-12": "Cz",
    "EEG-13": "C4",
    "EEG-14": "T8",
    "EEG-15": "P8",
    "EEG-16": "P3",
    "EEG-17": "Pz",
    "EEG-18": "P4",
    "EEG-19": "O1",
    "EEG-20": "Oz",
    "EEG-21": "O2",
    "ECG": "ECG",
    "EMG": "EMG",
}

# Standard EEG channel names for 10-20 system
_EEG_STANDARD_NAMES = {"Fp1", "Fp2", "Fpz", "F7", "F3", "Fz", "F4", "F8",
                       "T7", "T8", "P7", "P8", "C3", "C4", "Cz",
                       "P3", "P4", "Pz", "O1", "O2", "Oz"}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for channels present in this raw file."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    for source, target in _CHANNEL_RENAME_MAP.items():
        if source in existing and source != target:
            rename_map[source] = target
    return rename_map


def _read_participants_tsv(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and extract info for given subject."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    df = pd.read_csv(participants_path, sep="\t")
    # Match subject_id like "sub-01" with participant_id
    subj_rows = df[df["participant_id"] == subject_id]
    if len(subj_rows) == 0:
        return {}
    
    row = subj_rows.iloc[0]
    result = {}
    for col in df.columns:
        val = row.get(col)
        result[col] = str(val) if pd.notna(val) else "unknown"
    return result


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv sidecar for given EEG file."""
    # BIDS convention: events.tsv shares base name with eeg file
    base, _ = os.path.splitext(file_path)
    # Handle .eeg.gz or similar compound extensions
    while base.endswith(".eeg"):
        base = base[:-4]
    events_path = base + "_events.tsv"
    
    if not os.path.exists(events_path):
        # Try alternative: some files use .set with events.tsv in same dir
        dir_path = os.path.dirname(file_path)
        fname = os.path.basename(file_path)
        base_name = fname.split(".")[0]
        alt_events_path = os.path.join(dir_path, base_name + "_events.tsv")
        if os.path.exists(alt_events_path):
            events_path = alt_events_path
        else:
            return None
    
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _create_annotations_from_events(events_df: pd.DataFrame) -> mne.Annotations:
    """Create MNE Annotations from BIDS events.tsv dataframe."""
    if events_df is None or len(events_df) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, event_row in events_df.iterrows():
        onset = float(event_row.get("onset", 0))
        duration = float(event_row.get("duration", 0))
        # Use trial_type if available, else value, else stim_type
        desc = event_row.get("trial_type", None)
        if pd.isna(desc) or desc is None:
            desc = event_row.get("value", None)
        if pd.isna(desc) or desc is None:
            desc = event_row.get("stim_type", "unknown")
        
        # Ensure phase: prefix for phase events
        desc_str = str(desc)
        if desc_str in ("PRE", "MTI", "POST"):
            desc_str = f"phase:{desc_str}"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc_str)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _add_derived_misc_channel(raw: mne.io.BaseRaw, name: str, value: float) -> None:
    """Add a derived misc channel with constant value broadcast across all samples."""
    data = np.full((1, len(raw.times)), float(value), dtype=np.float64)
    info = mne.create_info(ch_names=[name], sfreq=raw.info["sfreq"], ch_types=["misc"])
    misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    raw.add_channels([misc_raw], force_update_info=True)


class OpenNeuroDS004840Kernel:
    KERNEL_ID: str = "openneuro-ds004840-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")
        subject_id = row.get("subject_id", "unknown")
        dataset_path = row.get("dataset_path", "")
        
        if not dataset_path and file_path:
            # Infer dataset path from file path (BIDS root)
            parts = file_path.split(os.sep)
            for i, part in enumerate(parts):
                if part.startswith("sub-"):
                    dataset_path = os.sep.join(parts[:i])
                    break
        
        # Read participants.tsv for subject info
        participant_info = _read_participants_tsv(dataset_path, subject_id)
        
        # Extract required info fields
        age = participant_info.get("age", "unknown")
        sex = participant_info.get("sex", "unknown").lower()
        if sex not in ("male", "female"):
            sex = "unknown"
        
        # Required info fields from participants.tsv
        required_fields = {
            "A-HADS_baseline": participant_info.get("A-HADS_baseline", "unknown"),
            "age": age,
            "burn_severity": participant_info.get("burn_severity", "unknown"),
            "burn_type": participant_info.get("burn_type", "unknown"),
            "medication": participant_info.get("medication", "unknown"),
            "sex": sex,
        }
        
        # Channel rename BEFORE set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types
        channel_types = {}
        for ch in raw.ch_names:
            if ch.startswith("ECG"):
                channel_types[ch] = "ecg"
            elif ch.startswith("EMG"):
                channel_types[ch] = "emg"
            elif ch in _EEG_STANDARD_NAMES:
                channel_types[ch] = "eeg"
        
        if channel_types:
            raw.set_channel_types(channel_types)
        
        # Set montage for EEG channels
        eeg_channels = [ch for ch in raw.ch_names if ch in _EEG_STANDARD_NAMES]
        if eeg_channels:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage not critical
        
        # Handle events from events.tsv
        # The raw files (.set EEGLAB) may not carry their own triggers reliably
        events_df = _read_events_tsv(file_path)
        if events_df is not None and len(events_df) > 0:
            # Check if raw already has meaningful annotations
            existing_annotations = raw.annotations
            has_meaningful_annotations = (
                existing_annotations is not None 
                and len(existing_annotations) > 0
                and any(d not in ("BAD_", "") for d in existing_annotations.description)
            )
            
            if not has_meaningful_annotations:
                # Derive annotations from events.tsv
                annotations = _create_annotations_from_events(events_df)
                if len(annotations) > 0:
                    raw.set_annotations(annotations)
        
        # Add derived misc channels from participants.tsv computations
        # Only create channels if source columns are actually available in participants.tsv
        # VAS_change_session1 = VAS_PRE_session1 - VAS_POST_session1
        if "VAS_PRE_session1" in participant_info and "VAS_POST_session1" in participant_info:
            vas_pre = participant_info.get("VAS_PRE_session1", "unknown")
            vas_post = participant_info.get("VAS_POST_session1", "unknown")
            if vas_pre != "unknown" and vas_post != "unknown":
                try:
                    vas_change = float(vas_pre) - float(vas_post)
                    _add_derived_misc_channel(raw, "VAS_change_session1", vas_change)
                except (ValueError, TypeError):
                    pass  # Skip if cannot compute
        
        # A_HADS_change = A-HADS_baseline - A-HADS_last
        if "A-HADS_baseline" in participant_info and "A-HADS_last" in participant_info:
            a_hads_base = participant_info.get("A-HADS_baseline", "unknown")
            a_hads_last = participant_info.get("A-HADS_last", "unknown")
            if a_hads_base != "unknown" and a_hads_last != "unknown":
                try:
                    a_hads_change = float(a_hads_base) - float(a_hads_last)
                    _add_derived_misc_channel(raw, "A_HADS_change", a_hads_change)
                except (ValueError, TypeError):
                    pass
        
        # D_HADS_change = D-HADS_baseline - D-HADS_last
        if "D-HADS_baseline" in participant_info and "D-HADS_last" in participant_info:
            d_hads_base = participant_info.get("D-HADS_baseline", "unknown")
            d_hads_last = participant_info.get("D-HADS_last", "unknown")
            if d_hads_base != "unknown" and d_hads_last != "unknown":
                try:
                    d_hads_change = float(d_hads_base) - float(d_hads_last)
                    _add_derived_misc_channel(raw, "D_HADS_change", d_hads_change)
                except (ValueError, TypeError):
                    pass
        
        # T_HADS_change = T-HADS_baseline - T-HADS_last
        if "T-HADS_baseline" in participant_info and "T-HADS_last" in participant_info:
            t_hads_base = participant_info.get("T-HADS_baseline", "unknown")
            t_hads_last = participant_info.get("T-HADS_last", "unknown")
            if t_hads_base != "unknown" and t_hads_last != "unknown":
                try:
                    t_hads_change = float(t_hads_base) - float(t_hads_last)
                    _add_derived_misc_channel(raw, "T_HADS_change", t_hads_change)
                except (ValueError, TypeError):
                    pass
        
        # Ensure derived misc channels have correct type
        derived_misc_names = ["VAS_change_session1", "A_HADS_change", "D_HADS_change", "T_HADS_change"]
        misc_types = {}
        for name in derived_misc_names:
            if name in raw.ch_names:
                misc_types[name] = "misc"
        if misc_types:
            raw.set_channel_types(misc_types)
        
        # Build eegunity_description
        # Device info: not available in dataset metadata
        # inferred by LLM, needs human review
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_description = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }
        
        # Add required info fields
        for field, value in required_fields.items():
            eegunity_description[field] = str(value)
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004840Kernel()