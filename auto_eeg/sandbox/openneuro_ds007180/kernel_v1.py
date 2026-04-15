"""OpenNeuro DS007180 (Exo-EEG) stage1 kernel for EEGUnity.

Dataset: Exoskeleton-assisted upper and lower limb movement EEG.
Source: https://openneuro.org/datasets/ds007180
Paper: DOI 10.1371/journal.pone.0182578 (upper limb MI/executed movement)
Channels: 63 EEG + 1+ trigger channels
Sampling Rate: 500 Hz

Note on metadata:
- age/sex/handedness not in original data; set to "unknown" (LLM 推断，需人类复核)
- amplifier inferred from dataset documentation as BrainAmp (LLM 推断，需人类复核)
- cap inferred as Ag/AgCl gel-based (LLM 推断，需人类复核)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# LLM 推断，需人类复核
# Source: paper DOI 10.1371/journal.pone.0182578 - 64-channel BrainAmp system
# 63 EEG + 1 trigger; standard electrode cap
_AMPLIFIER = "BrainAmp"  # LLM 推断，需人类复核
_CAP = "Ag/AgCl"  # LLM 推断，需人类复核


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for 64-channel BrainAmp/BrainVision standard cap.

    Based on standard_1020 with 63 EEG channels.
    Source: BrainVision 64-channel layout documentation (standard alpha montage)
    Annotator: LLM, 2026-04-08, 需人类复核
    """
    # Standard 64-channel BrainVision/BrainAmp layout (10-20 system)
    # 63 EEG positions + 1 reference/ground (typically VREF or GND)
    standard_64_channels = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        "T9", "T7", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO3", "POz", "PO4", "PO8", "PO10",
        "O1", "Oz", "O2",
        "Iz", "AFz", "Fz", "Cz", "Pz", "Oz"
    ]

    # 63-channel variant (missing some positions)
    # Common 63-channel config: standard 64 minus one
    eeg_63_standard = [
        "Fp1", "Fpz", "Fp2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
        "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
        "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
        "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "Iz"
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Pattern 1: EEG-0, EEG-1, ... EEG-62
    eeg_num_pattern = re.compile(r"^EEG-?(\d+)$", re.IGNORECASE)
    for ch in existing_names:
        match = eeg_num_pattern.match(ch)
        if match:
            idx = int(match.group(1))
            if idx < len(eeg_63_standard):
                target = eeg_63_standard[idx]
                if target != ch:
                    rename_map[ch] = target

    # Pattern 2: Already named but with slight variations
    alias_groups = [
        ("Fp1", ["Fp1", "fp1", "FP1"]),
        ("Fp2", ["Fp2", "fp2", "FP2"]),
        ("Fpz", ["Fpz", "fpz", "FPz"]),
        ("F7", ["F7", "f7", "F7"]),
        ("F3", ["F3", "f3", "F3"]),
        ("Fz", ["Fz", "fz", "FZ"]),
        ("F4", ["F4", "f4", "F4"]),
        ("F8", ["F8", "f8", "F8"]),
        ("T7", ["T7", "t7", "T7"]),
        ("C3", ["C3", "c3", "C3"]),
        ("Cz", ["Cz", "cz", "CZ"]),
        ("C4", ["C4", "c4", "C4"]),
        ("T8", ["T8", "t8", "T8"]),
        ("P7", ["P7", "p7", "P7"]),
        ("P3", ["P3", "p3", "P3"]),
        ("Pz", ["Pz", "pz", "PZ"]),
        ("P4", ["P4", "p4", "P4"]),
        ("P8", ["P8", "p8", "P8"]),
        ("O1", ["O1", "o1", "O1"]),
        ("O2", ["O2", "o2", "O2"]),
        ("Oz", ["Oz", "oz", "OZ"]),
        ("FC1", ["FC1", "fc1", "FC1"]),
        ("FC2", ["FC2", "fc2", "FC2"]),
        ("FCz", ["FCz", "fcz", "FCz"]),
        ("CP1", ["CP1", "cp1", "CP1"]),
        ("CP2", ["CP2", "cp2", "CP2"]),
        ("CPz", ["CPz", "cpz", "CPz"]),
        ("PO3", ["PO3", "po3", "PO3"]),
        ("PO4", ["PO4", "po4", "PO4"]),
        ("POz", ["POz", "poz", "POz"]),
    ]

    for target_name, aliases in alias_groups:
        for alias in aliases:
            if alias in existing_names and alias != target_name:
                rename_map[alias] = target_name
                break

    return rename_map


def _map_stim_to_annotation(stim_channel: np.ndarray, sfreq: float) -> mne.Annotations:
    """Convert BrainVision STIM channel data to MNE annotations.

    BrainVision uses S-prefixed event codes (e.g., S21, S22, S13).
    These are stored as float values in the STIM channel.

    Returns
    -------
    mne.Annotations
        Annotations with onset times and event descriptions.
    """
    # Find non-zero samples (events)
    # Events are stored as marker codes at specific sample indices
    events_idx = np.where(stim_channel != 0)[0]

    if len(events_idx) == 0:
        return mne.Annotations(
            onset=[], duration=[], description=[], orig_time=None
        )

    # Get unique event codes
    event_codes = stim_channel[events_idx]

    # Create onset times (in seconds)
    onsets = events_idx / sfreq
    durations = [0.0] * len(events_idx)

    # Map event codes to descriptions
    descriptions = []
    for code in event_codes:
        code_int = int(code)
        # BrainVision stores S-prefixed codes as SXX (e.g., 21 = S21)
        if 1 <= code_int <= 999:
            descriptions.append(f"S{code_int}")
        else:
            descriptions.append(str(code_int))

    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=None
    )


def _detect_file_type(file_path: str) -> str:
    """Detect file type from extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".vhdr":
        return "brainvision"
    elif ext == ".set":
        return "eeglab"
    elif ext == ".edf":
        return "edf"
    elif ext == ".gdf":
        return "gdf"
    else:
        return "unknown"


class OpenNeuroDS007180Kernel:
    """Stage1 kernel for OpenNeuro DS007180 Exo-EEG dataset.

    This kernel handles BrainVision format files from the Exo-EEG experiment
    with exoskeleton-assisted movement tasks.
    """

    KERNEL_ID: str = "openneuro-ds007180-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object loaded from file.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        # Get original description
        original_description = raw.info.get("description", "") or ""

        # Build eegunity_description
        # LLM 推断，需人类复核 - actual values should come from paper/dataset docs
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))
        age = "unknown"  # LLM 推断，需人类复核
        sex = "unknown"  # LLM 推断，需人类复核
        handedness = "unknown"  # LLM 推断，需人类复核

        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": _AMPLIFIER,  # LLM 推断，需人类复核
                "cap": _CAP,  # LLM 推断，需人类复核
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            existing_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if existing_renames:
                print(f"[DS007180] Renaming {len(existing_renames)} channels: {list(existing_renames.keys())[:5]}...")
                mne.rename_channels(raw, existing_renames)

        # Set montage if we have standard channel names
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only keep channels that exist in raw and in montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 20:  # Only set if we have enough channels
                raw.set_montage(montage, on_missing="ignore")
        except Exception as e:
            print(f"[DS007180] Could not set montage: {e}")

        # Handle STIM channel for BrainVision files
        stim_channels = [ch for ch in raw.ch_names if "stim" in ch.lower() or "trigger" in ch.lower()]
        if stim_channels:
            stim_ch = stim_channels[0]
            stim_data = raw.get_data(picks=[stim_ch]).flatten()
            annotations = _map_stim_to_annotation(stim_data, raw.info["sfreq"])
            raw.set_annotations(annotations)
            print(f"[DS007180] Created {len(annotations)} annotations from {stim_ch}")
        else:
            # Check if there are annotations already
            if len(raw.annotations) == 0:
                print("[DS007180] No STIM channel found and no existing annotations")

        return raw


KERNEL = OpenNeuroDS007180Kernel()