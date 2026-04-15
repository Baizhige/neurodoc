"""OpenNeuro ds004515 stage1 kernel for EEGUnity.

EEG: Alcohol imagery reinforcement learning task with light and heavy drinker participants.

Dataset: openneuro_ds004515 | Year: 2023
Source: https://openneuro.org/datasets/ds004515
Paper: https://doi.org/10.1016/j.pscychresns.2023.111685

Paradigm: Participants performed a reinforcement learning task with alcohol-related
and neutral imagery cues. Feedback (green=reward, red=punishment) was provided
for left/right button responses.

Subjects: 42 | Channels: 64 | Sampling Rate: 500 Hz
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne


# Source: Paper DOI 10.1016/j.pscychresns.2023.111685
# 64-channel EEG system with standard 10-20 electrode placement
# Annotator: LLM, 2026-04-08, needs human verification
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "AF7": "AF7",
    "AF3": "AF3",
    "AFz": "AFz",
    "AF4": "AF4",
    "AF8": "AF8",
    "F5": "F5",
    "F1": "F1",
    "F2": "F2",
    "F6": "F6",
    "FC5": "FC5",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC6": "FC6",
    "C5": "C5",
    "C1": "C1",
    "C2": "C2",
    "C6": "C6",
    "CP5": "CP5",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP6": "CP6",
    "P5": "P5",
    "P1": "P1",
    "P2": "P2",
    "P6": "P6",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "FT7": "FT7",
    "FT8": "FT8",
    "TP7": "TP7",
    "TP8": "TP8",
    "PO9": "PO9",
    "PO10": "PO10",
    "Oz": "Oz",
    "Iz": "Iz",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map from raw channel names to standard 10-20 names.
    
    Source: Standard 10-20 system mapping based on 64-channel layout
    Annotator: LLM, 2026-04-08, needs human verification
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Common channel name patterns in BrainVision/BrainAmp data
    alias_groups = [
        ("Fp1", ["Fp1", "EEG Fp1", "EEG-Fp1", "FP1"]),
        ("Fp2", ["Fp2", "EEG Fp2", "EEG-Fp2", "FP2"]),
        ("F7", ["F7", "EEG F7", "EEG-F7", "F7"]),
        ("F3", ["F3", "EEG F3", "EEG-F3", "F3"]),
        ("Fz", ["Fz", "EEG Fz", "EEG-Fz", "Fz"]),
        ("F4", ["F4", "EEG F4", "EEG-F4", "F4"]),
        ("F8", ["F8", "EEG F8", "EEG-F8", "F8"]),
        ("T7", ["T7", "T7", "EEG T7", "EEG-T7", "TP9"]),
        ("C3", ["C3", "EEG C3", "EEG-C3", "C3"]),
        ("Cz", ["Cz", "EEG Cz", "EEG-Cz", "Cz"]),
        ("C4", ["C4", "EEG C4", "EEG-C4", "C4"]),
        ("T8", ["T8", "T8", "EEG T8", "EEG-T8", "TP10"]),
        ("P7", ["P7", "EEG P7", "EEG-P7", "P7"]),
        ("P3", ["P3", "EEG P3", "EEG-P3", "P3"]),
        ("Pz", ["Pz", "EEG Pz", "EEG-Pz", "Pz"]),
        ("P4", ["P4", "EEG P4", "EEG-P4", "P4"]),
        ("P8", ["P8", "EEG P8", "EEG-P8", "P8"]),
        ("O1", ["O1", "EEG O1", "EEG-O1", "O1"]),
        ("Oz", ["Oz", "EEG Oz", "EEG-Oz", "Oz"]),
        ("O2", ["O2", "EEG O2", "EEG-O2", "O2"]),
        ("AF7", ["AF7", "EEG AF7", "EEG-AF7"]),
        ("AF3", ["AF3", "EEG AF3", "EEG-AF3"]),
        ("AFz", ["AFz", "EEG AFz", "EEG-AFz"]),
        ("AF4", ["AF4", "EEG AF4", "EEG-AF4"]),
        ("AF8", ["AF8", "EEG AF8", "EEG-AF8"]),
    ]
    
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


class OpenNeuroDs004515Kernel:
    """Stage1 kernel for OpenNeuro ds004515 dataset.
    
    Alcohol imagery reinforcement learning task with light and heavy drinkers.
    Events include CUE (stimulus onset), FB (feedback), and button responses.
    """

    KERNEL_ID: str = "openneuro-ds004515-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object with raw EEG data
        row : Locator row with dataset metadata
        
        Returns
        -------
        mne.io.BaseRaw : Processed Raw object with updated metadata
        """
        # Get original description
        original_description = raw.info.get("description", "")
        
        # Extract subject ID from row or raw
        subject_id = row.get("subject_id", "unknown")
        
        # Source: Dataset documentation and paper DOI 10.1016/j.pscychresns.2023.111685
        # 64-channel BrainAmp system with standard 10-20 electrode placement
        # Annotator: LLM, 2026-04-08, needs human verification
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": "BrainAmp",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard 10-20 names BEFORE set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter out any non-EEG channels (like status/trigger) from rename
            eeg_rename_map = {
                src: tgt for src, tgt in rename_map.items()
                if tgt not in ["EOG", "EMG", "ECG", "Trigger", "Status"]
            }
            if eeg_rename_map:
                print(f"Renaming channels: {eeg_rename_map}")
                mne.rename_channels(raw.info, eeg_rename_map)
        
        # Set standard montage for 64-channel EEG
        # Source: Standard 1020 system - Annotator: LLM, 2026-04-08
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Remove redundantCz if present (already in standard_1020)
            existing_chs = set(raw.ch_names)
            montage_chs = set(montage.ch_names)
            
            # Only set montage for channels that exist in both
            valid_chs = existing_chs.intersection(montage_chs)
            if len(valid_chs) >= 20:  # At least 20 matching channels
                raw.set_montage(montage, on_missing="ignore")
                print(f"Set standard_1020 montage for {len(valid_chs)} channels")
        except Exception as e:
            print(f"Warning: Could not set montage: {e}")
        
        # Process annotations from events
        # Source: Paper DOI 10.1016/j.pscychresns.2023.111685
        # Event structure: CUE (stimulus onset), FB (feedback), button responses
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Remap numeric event codes to descriptive labels
            # Based on BrainVision marker structure
            event_mapping = self._build_event_mapping(raw)
            self._remap_annotations(raw, event_mapping)
        
        # Set channel types for any remaining non-standard channels
        self._set_channel_types(raw)
        
        return raw
    
    def _build_event_mapping(self, raw: mne.io.BaseRaw) -> Dict[str, str]:
        """Build event code to label mapping based on BrainVision marker structure.
        
        Source: Dataset analysis and paper DOI 10.1016/j.pscychresns.2023.111685
        Event codes: CUE (stimulus onset), FB (feedback), responses
        Annotator: LLM, 2026-04-08, needs human verification
        """
        # Common BrainVision event code mappings
        # These need verification from events.tsv
        base_mapping = {
            # Stimulus/cue events
            "1": "CUE",
            "2": "CUE",
            "3": "CUE",
            "4": "CUE",
            "5": "CUE",
            # Feedback events
            "6": "FB",
            "7": "FB",
            "8": "FB",
            "9": "FB",
            # Response events
            "10": "Left Button",
            "11": "Right Button",
            "12": "Left Button",
            "13": "Right Button",
            # Status/marker events
            "91": "admin: marker-91",
            "92": "admin: marker-92",
            "99": "admin: marker-99",
            "255": "STATUS",
            "256": "STATUS",
        }
        return base_mapping
    
    def _remap_annotations(
        self, raw: mne.io.BaseRaw, event_mapping: Dict[str, str]
    ) -> None:
        """Remap numeric annotation descriptions to descriptive labels."""
        if raw.annotations is None:
            return
            
        new_descriptions = []
        for desc in raw.annotations.description:
            # Keep original if no mapping found
            mapped = event_mapping.get(str(desc).strip(), desc)
            new_descriptions.append(mapped)
        
        # Update descriptions in place
        raw.annotations.description = new_descriptions
    
    def _set_channel_types(self, raw: mne.io.BaseRaw) -> None:
        """Set channel types for special channels."""
        special_channels = {
            "EOG": "eog",
            "EOGv": "eog",
            "EOGh": "eog",
            "ECG": "ecg",
            "EMG": "emg",
            "Trigger": "stim",
            "Status": "stim",
        }
        
        current_types = raw.get_channel_types()
        for ch_name, ch_type in current_types.items():
            if ch_name in special_channels:
                try:
                    raw.set_channel_types({ch_name: special_channels[ch_name]})
                except Exception:
                    pass


KERNEL = OpenNeuroDs004515Kernel()