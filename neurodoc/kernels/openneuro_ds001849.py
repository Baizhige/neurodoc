"""OpenNeuro DS001849 stage1 kernel for EEGUnity.

Resting-state EEG data recorded with Transcranial Magnetic Stimulation (TMS).
30-channel EEG at 5000 Hz sampling rate. BrainVision format.
R128 is a BrainVision system/recording artifact marker present in all files.
Labels (active vs sham) are derived from the BIDS `acq-*` entity in filenames.

Source: https://openneuro.org/datasets/ds001849
Reference: 10.1371/journal.pone.0216185
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Kernel requirements
kernel_requirements = {
    "required_event_ids": ["R128"],
    "required_info_fields": ["age", "sex", "handedness"],
    "required_native_misc": [],
    "derived_misc_channels": ["inter_pulse_condition"],
}

# Standard 10-20 30-channel layout - LLM 推断，需人类复核
# Source: Based on standard 10-20 system with 30 channels typically used in TMS-EEG studies
# Annotator: LLM, 2026-04-08
_30_CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 naming."""
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1", "Fp 1", "fp1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "Fpz", "fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "Fp 2", "fp2"]),
        ("F7",  ["F7",  "EEG-F7",  "F7",  "f7"]),
        ("F3",  ["F3",  "EEG-F3",  "F3",  "f3"]),
        ("Fz",  ["Fz",  "EEG-Fz",  "Fz",  "fz"]),
        ("F4",  ["F4",  "EEG-F4",  "F4",  "f4"]),
        ("F8",  ["F8",  "EEG-F8",  "F8",  "f8"]),
        ("FT7", ["FT7", "EEG-FT7", "FT7", "ft7"]),
        ("FC3", ["FC3", "EEG-FC3", "FC3", "fc3"]),
        ("FCz", ["FCz", "EEG-FCz", "FCz", "fcz"]),
        ("FC4", ["FC4", "EEG-FC4", "FC4", "fc4"]),
        ("FT8", ["FT8", "EEG-FT8", "FT8", "ft8"]),
        ("T7",  ["T7",  "EEG-T7",  "T7",  "t7"]),
        ("C3",  ["C3",  "EEG-C3",  "C3",  "c3"]),
        ("Cz",  ["Cz",  "EEG-Cz",  "Cz",  "cz"]),
        ("C4",  ["C4",  "EEG-C4",  "C4",  "c4"]),
        ("T8",  ["T8",  "EEG-T8",  "T8",  "t8"]),
        ("TP7", ["TP7", "EEG-TP7", "TP7", "tp7"]),
        ("CP3", ["CP3", "EEG-CP3", "CP3", "cp3"]),
        ("CPz", ["CPz", "EEG-CPz", "CPz", "cpz"]),
        ("CP4", ["CP4", "EEG-CP4", "CP4", "cp4"]),
        ("TP8", ["TP8", "EEG-TP8", "TP8", "tp8"]),
        ("P7",  ["P7",  "EEG-P7",  "P7",  "p7"]),
        ("P3",  ["P3",  "EEG-P3",  "P3",  "p3"]),
        ("Pz",  ["Pz",  "EEG-Pz",  "Pz",  "pz"]),
        ("P4",  ["P4",  "EEG-P4",  "P4",  "p4"]),
        ("P8",  ["P8",  "EEG-P8",  "P8",  "p8"]),
        ("O1",  ["O1",  "EEG-O1",  "O1",  "o1"]),
        ("Oz",  ["Oz",  "EEG-Oz",  "Oz",  "oz"]),
        ("O2",  ["O2",  "EEG-O2",  "O2",  "o2"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _extract_acq_label(file_path: str) -> str:
    """Extract acquisition condition from BIDS filename acq- entity."""
    # Extract acq-<label> from filename like sub-01_acq-dlpfcactive_eeg.vhdr
    match = re.search(r'_acq-([^_]+)_', os.path.basename(file_path))
    if match:
        return match.group(1).lower()
    return "unknown"


def _is_valid_condition(acq_label: str) -> bool:
    """Check if acquisition label is one of the 6 known conditions."""
    valid_conditions = {"dlpfcactive", "dlpfcsham", "m1active", "m1sham", "ppcactive", "ppcsham"}
    return acq_label in valid_conditions


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read sibling events.tsv file if it exists."""
    # For BrainVision, the .vhdr file is the header; data is .eeg, markers are .vmrk
    # But BIDS also provides *_events.tsv
    base = file_path.replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "").replace(".set", "").replace(".fdt", "")
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    
    # Also check in BIDS eeg/ directory structure
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).replace(".vhdr", "").replace(".eeg", "").replace(".vmrk", "").replace(".set", "").replace(".fdt", "")
    events_path2 = os.path.join(dir_name, base_name + "_events.tsv")
    if os.path.exists(events_path2):
        return pd.read_csv(events_path2, sep="\t")
    
    return None


def _read_participants_tsv(dataset_path: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from the BIDS dataset root."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return None


def _get_subject_info(subject_id: str, participants_df: Optional[pd.DataFrame]) -> Dict[str, str]:
    """Get subject info from participants.tsv DataFrame."""
    info = {}
    if participants_df is not None and "participant_id" in participants_df.columns:
        row = participants_df[participants_df["participant_id"] == subject_id]
        if not row.empty:
            for field in ["age", "sex", "handedness"]:
                if field in row.columns:
                    info[field] = str(row[field].values[0])
    return info


def _create_inter_pulse_condition_channel(raw: mne.io.BaseRaw, acq_label: str) -> mne.io.BaseRaw:
    """Create derived misc channel 'inter_pulse_condition' based on file-level condition.
    
    For each 2s segment between R128 events, assign the condition label.
    Exclude segments within 500ms of any R128 event.
    """
    if not _is_valid_condition(acq_label):
        acq_label = "unknown"
    
    # Create numeric encoding for the 6 conditions
    condition_map = {
        "dlpfcactive": 0.0,
        "dlpfcsham": 1.0,
        "m1active": 2.0,
        "m1sham": 3.0,
        "ppcactive": 4.0,
        "ppcsham": 5.0,
        "unknown": -1.0,
    }
    condition_value = condition_map.get(acq_label, -1.0)
    
    # Get R128 event times from annotations
    r128_onsets = []
    for annot in raw.annotations:
        if annot["description"] == "R128":
            r128_onsets.append(annot["onset"])
    
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    times = raw.times
    
    # Initialize channel with zeros
    channel_data = np.zeros((1, n_samples))
    
    if len(r128_onsets) >= 2:
        # Define valid inter-pulse intervals (excluding 500ms around R128)
        exclude_margin = 0.5  # 500ms
        
        for i in range(len(r128_onsets) - 1):
            start_time = r128_onsets[i] + exclude_margin
            end_time = r128_onsets[i + 1] - exclude_margin
            
            if end_time - start_time >= 2.0:  # At least 2 seconds available
                # Fill 2-second segments within this valid interval
                segment_start = start_time
                while segment_start + 2.0 <= end_time:
                    seg_start_sample = int(segment_start * sfreq)
                    seg_end_sample = int((segment_start + 2.0) * sfreq)
                    seg_end_sample = min(seg_end_sample, n_samples)
                    if seg_start_sample < n_samples:
                        channel_data[0, seg_start_sample:seg_end_sample] = condition_value
                    segment_start += 2.0
    
    # Create RawArray for the new channel
    info = mne.create_info(
        ch_names=["inter_pulse_condition"],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    raw_misc = mne.io.RawArray(channel_data, info, verbose=False)
    
    # Ensure raw is loaded before adding channels
    if not raw.preload:
        raw.load_data()
    
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


class OpenNeuroDS001849Kernel:
    """Kernel for OpenNeuro dataset ds001849 (TMS-EEG resting-state)."""

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract file path from row
        file_path = row.get("file_path", "") if hasattr(row, "get") else str(row)
        
        # Get dataset path (parent of subject directories)
        dataset_path = os.path.dirname(os.path.dirname(file_path))
        
        # Extract subject ID from filename
        subject_match = re.search(r'(sub-[0-9]+)', os.path.basename(file_path))
        subject_id = subject_match.group(1) if subject_match else "unknown"
        
        # Read participants.tsv for subject info
        participants_df = _read_participants_tsv(dataset_path)
        subject_info = _get_subject_info(subject_id, participants_df)
        
        # Extract acquisition label from filename
        acq_label = _extract_acq_label(file_path)
        
        # Build and apply channel rename map
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage to standard 10-20
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        # Create derived misc channel
        raw = _create_inter_pulse_condition_channel(raw, acq_label)
        
        # Build description with original and eegunity parts
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_description = {
            "age": subject_info.get("age", ""),
            "sex": subject_info.get("sex", ""),
            "amplifier": "",
            "cap": "",
            "handedness": subject_info.get("handedness", ""),
        }
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        return raw


KERNEL = OpenNeuroDS001849Kernel()