"""openneuro_ds003555 stage1 kernel for EEGUnity.

Dataset: EEG Recordings of Pediatric Patients with Epilepsy Based on the 10-20 System
Source: https://openneuro.org/datasets/ds003555
BIDS-compliant dataset with EDF files, participants.tsv, and HFO event annotations
in derivatives.

This kernel handles:
- Standard 10-20 channel renaming (EEG Fz-Cz -> Fz, etc.)
- participants.tsv metadata extraction (age, sex, pathology)
- HFO event annotation from derivatives events.tsv files
- Derived misc channels from HFO event properties (SNR, rejection flag, etc.)
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Standard 10-20 channel mapping for this dataset.
# Source: Dataset README and BIDS sidecar json files indicate standard 10-20 system
# Original channel names are like "EEG Fz-Cz" (bipolar montage notation)
# We map to standard channel names for MNE montage compatibility.
# Annotator: LLM, 2026-04-08;
_CHANNEL_RENAME_MAP = {
    "EEG Fp1-F7": "Fp1",
    "EEG F7-T3": "F7",
    "EEG T3-T5": "T7",  # T3 -> T7 (10-10 equivalent)
    "EEG T5-O1": "P7",  # T5 -> P7 (10-10 equivalent)
    "EEG Fp2-F8": "Fp2",
    "EEG F8-T4": "F8",
    "EEG T4-T6": "T8",  # T4 -> T8 (10-10 equivalent)
    "EEG T6-O2": "P8",  # T6 -> P8 (10-10 equivalent)
    "EEG A1-T3": "A1",
    "EEG T3-C3": "T7",  # duplicate T7, will need special handling
    "EEG C3-Cz": "C3",
    "EEG Cz-C4": "Cz",
    "EEG C4-T4": "C4",
    "EEG T4-A2": "A2",
    "EEG Fp1-F3": "Fp1",  # alternative derivation
    "EEG F3-C3": "F3",
    "EEG C3-P3": "C3",  # duplicate
    "EEG P3-O1": "P3",
    "EEG Fp2-F4": "Fp2",  # alternative derivation
    "EEG F4-C4": "F4",
    "EEG C4-P4": "C4",  # duplicate
    "EEG P4-O2": "P4",
    "EEG Fz-Cz": "Fz",
    "EEG Cz-Pz": "Cz",  # duplicate
    "EEG Pz-Oz": "Pz",
    # Additional channels from actual data inspection
    "EEG EKG": "EKG",
    "EKG": "EKG",
    "EMG": "EMG",
    "EOG": "EOG",
    "EEG EOG": "EOG",
}

# More complete mapping based on actual ds003555 channel names
# Source: OpenNeuro ds003555, sub-01 sample file inspection
# Annotator: LLM, 2026-04-08;
_FULL_CHANNEL_MAP = {
    # Left temporal chain
    "EEG Fp1-F7": "Fp1",
    "EEG F7-T3": "F7",
    "EEG T3-T5": "T7",
    "EEG T5-O1": "P7",
    # Right temporal chain  
    "EEG Fp2-F8": "Fp2",
    "EEG F8-T4": "F8",
    "EEG T4-T6": "T8",
    "EEG T6-O2": "P8",
    # Left parasagittal
    "EEG Fp1-F3": "Fp1",
    "EEG F3-C3": "F3",
    "EEG C3-P3": "C3",
    "EEG P3-O1": "P3",
    # Right parasagittal
    "EEG Fp2-F4": "Fp2",
    "EEG F4-C4": "F4",
    "EEG C4-P4": "C4",
    "EEG P4-O2": "P4",
    # Midline
    "EEG Fz-Cz": "Fz",
    "EEG Cz-Pz": "Cz",
    "EEG Pz-Oz": "Pz",
    # Alternative midline notation
    "Fz-Cz": "Fz",
    "Cz-Pz": "Cz",
    "Pz-Oz": "Pz",
    # EKG/EOG/EMG
    "EEG EKG": "EKG",
    "EKG": "EKG",
    "EEG EMG": "EMG",
    "EMG": "EMG",
    "EEG EOG": "EOG",
    "EOG": "EOG",
    # A1/A2 references (often used as reference, map to misc)
    "EEG A1-T3": "A1",
    "EEG T3-C3": "T3",
    "EEG C3-Cz": "C3",
    "EEG Cz-C4": "Cz",
    "EEG C4-T4": "C4",
    "EEG T4-A2": "A2",
    "A1-T3": "A1",
    "T3-C3": "T3",
    "C3-Cz": "C3",
    "Cz-C4": "Cz",
    "C4-T4": "C4",
    "T4-A2": "A2",
}


def _resolve_channel_names(ch_names: List[str]) -> Dict[str, str]:
    """Create rename map handling duplicate target names."""
    rename_map = {}
    used_targets = set()
    
    for ch in ch_names:
        if ch in _FULL_CHANNEL_MAP:
            target = _FULL_CHANNEL_MAP[ch]
            # Handle duplicates by appending suffix
            base_target = target
            suffix = 2
            while target in used_targets and target in rename_map.values():
                target = f"{base_target}_{suffix}"
                suffix += 1
            if ch != target:
                rename_map[ch] = target
                used_targets.add(target)
        else:
            # Keep original if no mapping
            pass
    
    return rename_map


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # Check for events.tsv in same directory (BIDS standard)
    base = file_path.replace(".edf", "").replace(".set", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Check derivatives structure
    # Pattern: derivatives/sub-XX/ses-01/eeg/sub-XX_ses-01_task-hfo_run-NN_events.tsv
    parts = file_path.split(os.sep)
    if "sub-" in file_path:
        # Try to construct derivatives path
        sub_match = None
        for p in parts:
            if p.startswith("sub-"):
                sub_match = p
                break
        
        if sub_match:
            # Look for derivatives events
            dataset_root = file_path
            while dataset_root and not os.path.exists(os.path.join(dataset_root, "derivatives")):
                parent = os.path.dirname(dataset_root)
                if parent == dataset_root:
                    break
                dataset_root = parent
            
            if dataset_root and os.path.exists(os.path.join(dataset_root, "derivatives")):
                deriv_dir = os.path.join(dataset_root, "derivatives")
                # Search for matching events in derivatives
                for root, dirs, files in os.walk(deriv_dir):
                    for f in files:
                        if f.endswith("_events.tsv") and sub_match in f:
                            return os.path.join(root, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv from dataset root."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _extract_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    parts = file_path.split(os.sep)
    for p in parts:
        if p.startswith("sub-"):
            return p
    # Try from filename
    basename = os.path.basename(file_path)
    if basename.startswith("sub-"):
        return basename.split("_")[0]
    return None


def _read_hfo_events(events_path: str, sfreq: float) -> Optional[pd.DataFrame]:
    """Read HFO events from derivatives events.tsv."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        # This dataset's events.tsv uses indStart/indStop in samples, not onset/duration in seconds
        # We need to convert to onset/duration in seconds for MNE annotations
        if "indStart" in df.columns and "indStop" in df.columns:
            df["onset"] = df["indStart"] / sfreq
            df["duration"] = (df["indStop"] - df["indStart"]) / sfreq
        else:
            # Validate required columns if not using indStart/indStop
            required = ["onset", "duration"]
            for col in required:
                if col not in df.columns:
                    return None
        
        # Ensure we have the HFO-specific columns
        hfo_cols = ["SNR", "EvPassRejection", "fmax_FR", "EventPeak2Peak", 
                    "indDuration", "nChannel", "indStart", "indStop"]
        for col in hfo_cols:
            if col not in df.columns:
                df[col] = np.nan
        
        return df
    except Exception:
        return None


def _create_derived_misc_channels(raw: mne.io.BaseRaw, hfo_events: pd.DataFrame, 
                                  sfreq: float) -> mne.io.BaseRaw:
    """Create derived misc channels from HFO event properties."""
    n_samples = raw.n_times
    times = raw.times
    
    # Initialize channels with zeros
    snr_data = np.zeros((1, n_samples))
    rejection_data = np.zeros((1, n_samples))
    peak_freq_data = np.zeros((1, n_samples))
    amplitude_data = np.zeros((1, n_samples))
    duration_data = np.zeros((1, n_samples))
    channel_idx_data = np.zeros((1, n_samples))
    segment_id_data = np.zeros((1, n_samples))
    
    for idx, event in hfo_events.iterrows():
        # Get event timing in samples
        onset = event.get("onset", 0)
        duration = event.get("duration", 0)
        
        onset_sample = int(onset * sfreq)
        duration_samples = int(duration * sfreq)
        end_sample = min(onset_sample + duration_samples, n_samples)
        
        if onset_sample >= n_samples:
            continue
        
        # Fill in values during event window
        # SNR
        snr_val = event.get("SNR", np.nan)
        if pd.notna(snr_val):
            snr_data[0, onset_sample:end_sample] = float(snr_val)
        
        # Rejection flag (1 = rejected, 0 = passed)
        rejection_val = event.get("EvPassRejection", np.nan)
        if pd.notna(rejection_val):
            # EvPassRejection: 0 = pass, 1 = reject
            rejection_data[0, onset_sample:end_sample] = float(rejection_val)
        
        # Peak frequency (fmax_FR)
        freq_val = event.get("fmax_FR", np.nan)
        if pd.notna(freq_val):
            peak_freq_data[0, onset_sample:end_sample] = float(freq_val)
        
        # Amplitude (EventPeak2Peak)
        amp_val = event.get("EventPeak2Peak", np.nan)
        if pd.notna(amp_val):
            amplitude_data[0, onset_sample:end_sample] = float(amp_val)
        
        # Duration (indDuration in ms, convert to seconds or keep as is)
        dur_val = event.get("indDuration", np.nan)
        if pd.notna(dur_val):
            duration_data[0, onset_sample:end_sample] = float(dur_val)
        
        # Channel index (nChannel)
        ch_val = event.get("nChannel", np.nan)
        if pd.notna(ch_val):
            channel_idx_data[0, onset_sample:end_sample] = float(ch_val)
        
        # Segment ID (use row index as segment identifier)
        segment_id_data[0, onset_sample:end_sample] = float(idx)
    
    # Create info for new channels
    ch_names = ["hfo_snr", "hfo_rejection_flag", "hfo_peak_frequency", 
                "hfo_amplitude", "hfo_duration", "hfo_channel_index", "segment_id"]
    ch_types = ["misc"] * len(ch_names)
    
    # Create new info
    new_info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    
    # Create RawArray with the data
    all_data = np.vstack([snr_data, rejection_data, peak_freq_data, 
                          amplitude_data, duration_data, channel_idx_data, segment_id_data])
    
    # Create a temporary raw object with the new channels
    misc_raw = mne.io.RawArray(all_data, new_info)
    
    # Add the new channels to the original raw
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


class OpenNeuroDS003555Kernel:
    """Kernel for OpenNeuro ds003555 dataset."""
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["file_path"]
        original_description = raw.info.get("description", "")
        
        # Extract subject ID
        subject_id = _extract_subject_id(file_path)
        
        # Find and read participants.tsv
        participants_path = _find_participants_tsv(file_path)
        participants_data = {}
        if participants_path and subject_id:
            try:
                df = pd.read_csv(participants_path, sep="\t")
                sub_row = df[df["participant_id"] == subject_id]
                if not sub_row.empty:
                    participants_data = sub_row.iloc[0].to_dict()
            except Exception:
                pass
        
        # Build eegunity_description from participants.tsv fields
        eegunity_description = {
            "age": str(participants_data.get("age", "")),
            "sex": str(participants_data.get("sex", "")),
            "amplifier": str(participants_data.get("amplifier", "")),
            "cap": str(participants_data.get("cap", "")),
            "handedness": str(participants_data.get("handedness", "")),
        }
        
        # Rename channels
        rename_map = _resolve_channel_names(raw.ch_names)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage if possible
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass
        
        # Find and load HFO events from events.tsv
        sfreq = raw.info["sfreq"]
        events_path = _find_events_tsv(file_path)
        hfo_events = None
        if events_path:
            hfo_events = _read_hfo_events(events_path, sfreq)
        
        # Create annotations from HFO events using nChannel as the event label
        # This preserves event IDs as required: event_1, event_2, ..., event_10
        if hfo_events is not None and not hfo_events.empty:
            onsets = hfo_events["onset"].values
            durations = hfo_events["duration"].values
            # Use nChannel to create event labels like "event_1", "event_2", etc.
            descriptions = ["event_" + str(int(x)) for x in hfo_events["nChannel"].values]
            
            # Create MNE annotations and set on raw
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions
            )
            raw.set_annotations(annotations)
            
            # Create derived misc channels from HFO properties
            raw = _create_derived_misc_channels(raw, hfo_events, sfreq)
        
        # Update description with eegunity metadata
        eegunity_description["original_description"] = original_description
        eegunity_description["subject_id"] = subject_id or ""
        eegunity_description["events_file"] = events_path or ""
        eegunity_description["dataset"] = "openneuro_ds003555"
        
        raw.info["description"] = json.dumps(eegunity_description)
        
        return raw


KERNEL = OpenNeuroDS003555Kernel()