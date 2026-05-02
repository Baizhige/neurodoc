"""openneuro_ds004388 stage1 kernel for EEGUnity.

Somatosensory evoked potentials (SEPs) in response to mixed median and tibial
nerve stimulation, with simultaneous EEG and epidural spinal cord recordings.

Dataset: openneuro_ds004388 | Year: 2023
Source: https://openneuro.org/datasets/ds004388

115 channels, 10 kHz sampling rate.
Events from stim channel (stimulus markers).
Stimulus types: Median nerve and Tibial nerve stimulation.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# inferred by LLM, needs human review
# Amplifier info based on paper references for spinal cord SEP studies
_AMPLIFIER = "unknown"

# inferred by LLM, needs human review
# Cap info - epidural spinal cord ESG electrodes mentioned, EEG likely standard
_CAP = "unknown"

# inferred by LLM, needs human review
# No handedness info in dataset description
_HANDEDNESS = "unknown"


def _detect_stimulus_type(file_path: str) -> str:
    """Detect stimulus type from file naming convention.
    
    OpenNeuro ds004388 uses mixed median/tibial nerve stimulation.
    File naming typically indicates stimulation site.
    
    Returns:
        "median" if median nerve stimulation
        "tibial" if tibial nerve stimulation
        "unknown" if cannot determine
    """
    file_name = os.path.basename(file_path).lower()
    
    # Common patterns for median/tibial in SEP literature
    if "median" in file_name or "mn" in file_name:
        return "median"
    elif "tibial" in file_name or "tn" in file_name:
        return "tibial"
    elif "mixed" in file_name:
        return "mixed"
    
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names.
    
    This dataset has 115 channels including:
    - EEG scalp electrodes
    - ESG epidural spinal cord electrodes
    - EMG/ENG peripheral nerve channels
    - MISC trigger/stim channels
    
    Source: Standard 10-20 system for EEG, paper descriptions for ESG/EMG channels.
    inferred by LLM, needs human review - channel naming conventions.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Standard EEG 10-20 system channels
    eeg_aliases = [
        ("Fp1", ["EEG-Fp1", "Fp1"]),
        ("Fp2", ["EEG-Fp2", "Fp2"]),
        ("F7", ["EEG-F7", "F7"]),
        ("F3", ["EEG-F3", "F3"]),
        ("Fz", ["EEG-Fz", "Fz"]),
        ("F4", ["EEG-F4", "F4"]),
        ("F8", ["EEG-F8", "F8"]),
        ("T7", ["EEG-T7", "T7", "T3"]),
        ("C3", ["EEG-C3", "C3"]),
        ("Cz", ["EEG-Cz", "Cz"]),
        ("C4", ["EEG-C4", "C4"]),
        ("T8", ["EEG-T8", "T8", "T4"]),
        ("P7", ["EEG-P7", "P7", "T5"]),
        ("P3", ["EEG-P3", "P3"]),
        ("Pz", ["EEG-Pz", "Pz"]),
        ("P4", ["EEG-P4", "P4"]),
        ("P8", ["EEG-P8", "P8", "T6"]),
        ("O1", ["EEG-O1", "O1"]),
        ("O2", ["EEG-O2", "O2"]),
        ("Oz", ["EEG-Oz", "Oz"]),
        ("FC1", ["EEG-FC1", "FC1"]),
        ("FC2", ["EEG-FC2", "FC2"]),
        ("FC5", ["EEG-FC5", "FC5"]),
        ("FC6", ["EEG-FC6", "FC6"]),
        ("CP1", ["EEG-CP1", "CP1"]),
        ("CP2", ["EEG-CP2", "CP2"]),
        ("CP5", ["EEG-CP5", "CP5"]),
        ("CP6", ["EEG-CP6", "CP6"]),
        ("PO3", ["EEG-PO3", "PO3"]),
        ("PO4", ["EEG-PO4", "PO4"]),
        ("PO7", ["EEG-PO7", "PO7"]),
        ("PO8", ["EEG-PO8", "PO8"]),
        ("AF7", ["EEG-AF7", "AF7"]),
        ("AF8", ["EEG-AF8", "AF8"]),
        ("AFz", ["EEG-AFz", "AFz"]),
        ("F1", ["EEG-F1", "F1"]),
        ("F2", ["EEG-F2", "F2"]),
        ("F5", ["EEG-F5", "F5"]),
        ("F6", ["EEG-F6", "F6"]),
        ("C1", ["EEG-C1", "C1"]),
        ("C2", ["EEG-C2", "C2"]),
        ("C5", ["EEG-C5", "C5"]),
        ("C6", ["EEG-C6", "C6"]),
        ("P1", ["EEG-P1", "P1"]),
        ("P2", ["EEG-P2", "P2"]),
        ("P5", ["EEG-P5", "P5"]),
        ("P6", ["EEG-P6", "P6"]),
    ]
    
    for target_name, aliases in eeg_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    # ESG (Epidural Spinal Cord) channels - typical naming
    esg_aliases = [
        ("ESG-C7", ["ESG-C7", "ESG-C7"]),
        ("ESG-C8", ["ESG-C8", "ESG-C8"]),
        ("ESG-Th1", ["ESG-Th1", "ESG-Th1"]),
        ("ESG-Th2", ["ESG-Th2", "ESG-Th2"]),
        ("ESG-Th3", ["ESG-Th3", "ESG-Th3"]),
        ("ESG-Th4", ["ESG-Th4", "ESG-Th4"]),
        ("ESG-Th5", ["ESG-Th5", "ESG-Th5"]),
        ("ESG-Th6", ["ESG-Th6", "ESG-Th6"]),
        ("ESG-Th7", ["ESG-Th7", "ESG-Th7"]),
        ("ESG-Th8", ["ESG-Th8", "ESG-Th8"]),
        ("ESG-Th9", ["ESG-Th9", "ESG-Th9"]),
        ("ESG-Th10", ["ESG-Th10", "ESG-Th10"]),
        ("ESG-Th11", ["ESG-Th11", "ESG-Th11"]),
        ("ESG-Th12", ["ESG-Th12", "ESG-Th12"]),
        ("ESG-L1", ["ESG-L1", "ESG-L1"]),
        ("ESG-L2", ["ESG-L2", "ESG-L2"]),
        ("ESG-L3", ["ESG-L3", "ESG-L3"]),
    ]
    
    for target_name, aliases in esg_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    # EMG/ENG peripheral nerve channels
    emg_aliases = [
        ("EMG-median", ["EMG-median", "EMG-MN", "median-EMG"]),
        ("EMG-tibial", ["EMG-tibial", "EMG-TN", "tibial-EMG"]),
        ("EMG-ulnar", ["EMG-ulnar", "EMG-UN"]),
        ("ENG-peroneal", ["ENG-peroneal", "ENG-peroneal"]),
        ("ENG-sural", ["ENG-sural", "ENG-sural"]),
    ]
    
    for target_name, aliases in emg_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    # Trigger/Stim channel normalization
    stim_candidates = ["stim", "Stim", "STIM", "trigger", "Trigger", "TRIGGER", 
                       "stimulus", "Stimulus", "marker", "Marker"]
    for stim_name in stim_candidates:
        if stim_name in existing_names:
            rename_map[stim_name] = "stim"
            break
    
    return rename_map


def _setup_annotations_from_stim(raw: mne.io.BaseRaw, file_path: str) -> mne.Annotations:
    """Set up annotations from stim channel.
    
    The stim channel contains stimulus markers. This function detects onset
    events from the stim channel and creates appropriate annotations.
    
    Returns:
        mne.Annotations with stimulus events labeled by type.
    """
    # Detect stimulus type from file name
    stim_type = _detect_stimulus_type(file_path)
    
    # Map to event description
    if stim_type == "median":
        event_desc = "Median - Stimulation"
    elif stim_type == "tibial":
        event_desc = "Tibial - Stimulation"
    elif stim_type == "mixed":
        # For mixed stimulation, keep as generic
        event_desc = "stimulus"
    else:
        event_desc = "stimulus"
    
    sfreq = raw.info["sfreq"]
    
    # Find stim channel
    stim_ch = None
    for ch_name in raw.ch_names:
        if ch_name.lower() in ["stim", "trigger", "stimulus", "marker"]:
            stim_ch = ch_name
            break
    
    if stim_ch is None:
        # Try to find from annotations if already parsed
        try:
            existing_annots = raw.annotations
            if len(existing_annots) > 0:
                return existing_annots
        except Exception:
            pass
        # Return empty annotations if no stim channel found
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Get stim channel data
    stim_idx = raw.ch_names.index(stim_ch)
    stim_data, _ = raw[stim_idx, :]
    stim_data = stim_data.flatten()
    
    # Find threshold crossings (stimulus onsets)
    # Assuming stim channel has binary signal with stimulus markers
    threshold = np.mean(stim_data) + 2 * np.std(stim_data)
    above_threshold = stim_data > threshold
    
    # Find transitions (onsets)
    diff_signal = np.diff(above_threshold.astype(int))
    onset_indices = np.where(diff_signal == 1)[0] + 1
    
    if len(onset_indices) == 0:
        # Alternative: look for any non-zero values
        non_zero_indices = np.where(stim_data != 0)[0]
        if len(non_zero_indices) > 0:
            # Cluster nearby indices
            gaps = np.diff(non_zero_indices)
            split_points = np.where(gaps > sfreq * 0.01)[0] + 1
            onset_indices = [non_zero_indices[0]]
            for sp in split_points:
                onset_indices.append(non_zero_indices[sp])
            onset_indices = np.array(onset_indices)
    
    if len(onset_indices) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Convert to time
    onsets = onset_indices / sfreq
    durations = np.zeros(len(onsets))
    
    # Create annotations with appropriate labels
    descriptions = [event_desc] * len(onsets)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


class openneuro_ds004388_Kernel:
    """Stage1 kernel for openneuro_ds004388 dataset.
    
    SEP (Somatosensory Evoked Potentials) dataset with mixed median and tibial
    nerve stimulation, including EEG scalp and epidural spinal cord (ESG) channels.
    """

    KERNEL_ID: str = "openneuro-ds004388-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed MNE Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        
        # Preserve original description
        original_desc = raw.info.get("description", "")
        
        # Build eegunity_description
        # inferred by LLM, needs human review - age and sex unknown from dataset
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": "unknown",  # inferred by LLM, needs human review
                "sex": "unknown",  # inferred by LLM, needs human review
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": _HANDEDNESS,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels before set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception as e:
                # Some channels may not exist, log and continue
                print(f"Channel rename warning: {e}")
        
        # Try to set montage for EEG channels
        # Note: ESG and EMG channels are not standard 10-20 positions
        eeg_channels = []
        for ch in raw.ch_names:
            if ch.startswith("EEG") and not any(x in ch for x in ["ESG", "EMG", "ENG"]):
                eeg_channels.append(ch)
        
        if eeg_channels:
            try:
                # Try standard_1020 montage for EEG channels
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # If montage fails, continue without it
                pass
        
        # Set up annotations from stim channel
        annotations = _setup_annotations_from_stim(raw, file_path)
        if len(annotations) > 0:
            raw.set_annotations(annotations)
        
        # Downsample if needed (10 kHz is very high for standard EEG)
        # Comment out unless specifically needed - let users decide
        # if raw.info["sfreq"] > 5000:
        #     raw.resample(sfreq=5000)
        
        return raw


KERNEL = openneuro_ds004388_Kernel()