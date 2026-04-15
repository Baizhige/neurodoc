"""OpenNeuro ds004561 stage1 kernel for EEGUnity.

Dataset: "Illusion of Agency over Electrically-Actuated Movements"
20 subjects, 64 channels, 512 Hz
Events: stimulation (involuntary), pretest/voluntary, posttest/voluntary

Source: https://openneuro.org/datasets/ds004561
DOI: https://doi.org/10.18112/openneuro.ds004561.v1.0.0
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne


# === Subject metadata ===
# Source: extracted from participants.tsv (BIDS)
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "01": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "02": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "03": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "04": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "05": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "06": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "07": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "08": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "09": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "10": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "11": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "12": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "13": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "14": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "15": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "16": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "17": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "18": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "19": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "20": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}

# Device metadata - inferred from paradigm description (electrical stimulation setup)
# Source: paper DOI 10.1523/JNEUROSCI.1116-23.2023, analysis.md
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_DEVICE_METADATA = {
    "amplifier": "unknown",
    "cap": "unknown",
}


# === Channel mapping ===
# OpenNeuro ds004561 uses standard 64-channel setup
# Source: dataset description, electrode cap documentation
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_EEG_64_CHANNEL_STANDARD = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "Fp1", "F7", "FT7", "T7", "TP7", "P7", "PO7", "O1",  # Extended left
    "F3", "FC3", "C3", "CP3", "P3", "PO3",  # Mid-left
    "Fz", "FCz", "Cz", "CPz", "Pz", "POz",  # Midline
    "F4", "FC4", "C4", "CP4", "P4", "PO4",  # Mid-right
    "F8", "FT8", "T8", "TP8", "P8", "PO8", "O2",  # Extended right
    "Fpz", "Oz",  # Additional midline
    "AF7", "AF3", "AFz", "AF4", "AF8",  # Anterior frontal
    "F5", "F1", "F2", "F6",  # Inferior frontal
    "FC5", "FC1", "FC2", "FC6",  # Inferior frontal-central
    "C5", "C1", "C2", "C6",  # Inferior central
    "CP5", "CP1", "CP2", "CP6",  # Inferior central-parietal
    "P5", "P1", "P2", "P6",  # Inferior parietal
    "PO5", "PO1", "PO2", "PO6",  # Inferior parietal-occipital
]

# Standard 64-channel montage names (BrainVision / BrainProducts standard)
_STANDARD_64_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "F5", "F1", "F2", "F6",
    "FC5", "FC1", "FC2", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP1", "CP2", "CP6",
    "P5", "P1", "P2", "P6",
    "PO5", "PO1", "PO2", "PO6",
    "AF7", "AF3", "AFz", "AF4", "AF8",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for 64-channel standard montage."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Common naming patterns in OpenNeuro EEG datasets
    alias_groups = [
        # Standard 10-20 names (may appear as-is or with EEG prefix)
        ("Fp1", ["EEG Fp1", "EEG-Fp1", "Fp1", "fp1"]),
        ("Fpz", ["EEG Fpz", "EEG-Fpz", "Fpz", "fpz"]),
        ("Fp2", ["EEG Fp2", "EEG-Fp2", "Fp2", "fp2"]),
        ("F7", ["EEG F7", "EEG-F7", "F7", "f7"]),
        ("F3", ["EEG F3", "EEG-F3", "F3", "f3"]),
        ("Fz", ["EEG Fz", "EEG-Fz", "Fz", "fz"]),
        ("F4", ["EEG F4", "EEG-F4", "F4", "f4"]),
        ("F8", ["EEG F8", "EEG-F8", "F8", "f8"]),
        ("FT7", ["EEG FT7", "EEG-FT7", "FT7", "ft7"]),
        ("FC3", ["EEG FC3", "EEG-FC3", "FC3", "fc3"]),
        ("FCz", ["EEG FCz", "EEG-FCz", "FCz", "fcz"]),
        ("FC4", ["EEG FC4", "EEG-FC4", "FC4", "fc4"]),
        ("FT8", ["EEG FT8", "EEG-FT8", "FT8", "ft8"]),
        ("T7", ["EEG T7", "EEG-T7", "T7", "t7"]),
        ("C3", ["EEG C3", "EEG-C3", "C3", "c3"]),
        ("Cz", ["EEG Cz", "EEG-Cz", "Cz", "cz"]),
        ("C4", ["EEG C4", "EEG-C4", "C4", "c4"]),
        ("T8", ["EEG T8", "EEG-T8", "T8", "t8"]),
        ("TP7", ["EEG TP7", "EEG-TP7", "TP7", "tp7"]),
        ("CP3", ["EEG CP3", "EEG-CP3", "CP3", "cp3"]),
        ("CPz", ["EEG CPz", "EEG-CPz", "CPz", "cpz"]),
        ("CP4", ["EEG CP4", "EEG-CP4", "CP4", "cp4"]),
        ("TP8", ["EEG TP8", "EEG-TP8", "TP8", "tp8"]),
        ("P7", ["EEG P7", "EEG-P7", "P7", "p7"]),
        ("P3", ["EEG P3", "EEG-P3", "P3", "p3"]),
        ("Pz", ["EEG Pz", "EEG-Pz", "Pz", "pz"]),
        ("P4", ["EEG P4", "EEG-P4", "P4", "p4"]),
        ("P8", ["EEG P8", "EEG-P8", "P8", "p8"]),
        ("PO7", ["EEG PO7", "EEG-PO7", "PO7", "po7"]),
        ("PO3", ["EEG PO3", "EEG-PO3", "PO3", "po3"]),
        ("POz", ["EEG POz", "EEG-POz", "POz", "poz"]),
        ("PO4", ["EEG PO4", "EEG-PO4", "PO4", "po4"]),
        ("PO8", ["EEG PO8", "EEG-PO8", "PO8", "po8"]),
        ("O1", ["EEG O1", "EEG-O1", "O1", "o1"]),
        ("Oz", ["EEG Oz", "EEG-Oz", "Oz", "oz"]),
        ("O2", ["EEG O2", "EEG-O2", "O2", "o2"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _extract_subject_id(row) -> str:
    """Extract subject ID from file path."""
    file_path = row.get("File Path", "")
    # Try to extract sub-XX pattern
    import re
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _get_eegunity_description(raw: mne.io.BaseRaw, row) -> Dict[str, Any]:
    """Build eegunity_description dict with subject metadata."""
    subject_id = _extract_subject_id(row)
    
    subject_info = _SUBJECT_DICT.get(subject_id, {})
    device_info = _DEVICE_METADATA
    
    return {
        "original_description": raw.info.get("description", ""),
        "eegunity_description": {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
            "amplifier": device_info.get("amplifier", "unknown"),
            "cap": device_info.get("cap", "unknown"),
        },
    }


@dataclass
class OpenNeuroDS004561Kernel:
    """Stage1 kernel for OpenNeuro ds004561 dataset."""

    KERNEL_ID: str = "openneuro-ds004561-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (loaded from BIDS)
        row : Locator row with file path

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with annotations and metadata
        """
        # === Step 1: Extract and set subject/device metadata ===
        eegunity_desc = _get_eegunity_description(raw, row)
        raw.info["description"] = json.dumps(eegunity_desc)

        # === Step 2: Rename channels to standard names ===
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[Kernel] Renaming {len(rename_map)} channels: {list(rename_map.values())[:5]}...")
            raw.rename_channels(rename_map)

        # === Step 3: Set standard montage ===
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception as e:
            print(f"[Kernel] Could not set montage: {e}")

        # === Step 4: Process events/annotations ===
        # OpenNeuro BIDS format typically stores events in annotations or events.tsv
        # Ensure events are properly labeled for downstream epoching
        
        # Get existing annotations
        existing_annotations = raw.annotations
        
        # If no annotations exist, try to find events from stim channels
        if len(existing_annotations) == 0:
            # Check for stimulus channels that might contain event codes
            stim_channels = [ch for ch in raw.ch_names if 'stim' in ch.lower() or 'trigger' in ch.lower()]
            if stim_channels:
                print(f"[Kernel] Found stim channels: {stim_channels}")
                # Events will be extracted during epoching via mne.events_from_annotations
            else:
                print("[Kernel] Warning: No annotations found. Check dataset structure.")
        
        # Map existing annotation descriptions to canonical event labels
        # ds004561 events: stimulation, pretest, posttest
        event_label_map = {
            "stimulation": "stimulation",
            "pretest": "pretest",
            "posttest": "posttest",
            # Common BIDS event label variations
            "Stimulus": "stimulation",
            "Response": "pretest",
            "pre_test": "pretest",
            "post_test": "posttest",
        }
        
        if len(existing_annotations) > 0:
            new_descriptions = []
            for desc in existing_annotations.description:
                new_desc = event_label_map.get(desc, desc)
                new_descriptions.append(new_desc)
            
            if new_descriptions != list(existing_annotations.description):
                new_annotations = mne.Annotations(
                    onset=existing_annotations.onset,
                    duration=existing_annotations.duration,
                    description=new_descriptions,
                    orig_time=existing_annotations.orig_time,
                )
                raw.set_annotations(new_annotations)
                print(f"[Kernel] Remapped annotation descriptions")

        # === Step 5: Log summary ===
        print(f"[Kernel] Processed: {raw.filenames}")
        print(f"  - Channels: {len(raw.ch_names)}")
        print(f"  - Duration: {raw.times[-1]:.2f} s")
        print(f"  - Annotations: {len(raw.annotations)}")
        if len(raw.annotations) > 0:
            unique_labels = set(raw.annotations.description)
            print(f"  - Event labels: {unique_labels}")

        return raw


KERNEL = OpenNeuroDS004561Kernel()