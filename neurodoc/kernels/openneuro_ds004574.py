"""OpenNeuro ds004574 stage1 kernel for EEGUnity.

Cross-modal Oddball Task dataset with 30 subjects, 64 channels at 512 Hz.
Contains S 1 (standard), S 2 (deviant), S 3 (rare/target) stimuli for MMN/P300 analysis.

Source: https://openneuro.org/datasets/ds004574
DOI: 10.1101/2022.07.26.22278079
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne


# Standard 64-channel montage mapping (based on standard_1005)
# Channels are typically named as EEG001-EEG064 in BrainVision format
# LLM 推断，需人类复核 - 需要确认实际通道命名格式
_EEG_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "EEG001": "Fp1",
    "EEG002": "Fpz",
    "EEG003": "Fp2",
    "EEG004": "AF7",
    "EEG005": "AF3",
    "EEG006": "AFz",
    "EEG007": "AF4",
    "EEG008": "AF8",
    "EEG009": "F7",
    "EEG010": "F5",
    "EEG011": "F3",
    "EEG012": "F1",
    "EEG013": "Fz",
    "EEG014": "F2",
    "EEG015": "F4",
    "EEG016": "F6",
    "EEG017": "F8",
    "EEG018": "FT7",
    "EEG019": "FC5",
    "EEG020": "FC3",
    "EEG021": "FC1",
    "EEG022": "FCz",
    "EEG023": "FC2",
    "EEG024": "FC4",
    "EEG025": "FC6",
    "EEG026": "FT8",
    "EEG027": "T7",
    "EEG028": "C5",
    "EEG029": "C3",
    "EEG030": "C1",
    "EEG031": "Cz",
    "EEG032": "C2",
    "EEG033": "C4",
    "EEG034": "C6",
    "EEG035": "T8",
    "EEG036": "TP7",
    "EEG037": "CP5",
    "EEG038": "CP3",
    "EEG039": "CP1",
    "EEG040": "CPz",
    "EEG041": "CP2",
    "EEG042": "CP4",
    "EEG043": "CP6",
    "EEG044": "TP8",
    "EEG045": "P7",
    "EEG046": "P5",
    "EEG047": "P3",
    "EEG048": "P1",
    "EEG049": "Pz",
    "EEG050": "P2",
    "EEG051": "P4",
    "EEG052": "P6",
    "EEG053": "P8",
    "EEG054": "PO7",
    "EEG055": "PO5",
    "EEG056": "PO3",
    "EEG057": "POz",
    "EEG058": "PO4",
    "EEG059": "PO6",
    "EEG060": "PO8",
    "EEG061": "O1",
    "EEG062": "Oz",
    "EEG063": "O2",
    "EEG064": "Iz",
}

# BrainVision event code mapping
# S  1 = Standard stimulus, S  2 = Deviant stimulus, S  3 = Rare/target
# S255 = BrainVision overflow/system marker (admin, exclude from epoching)
# boundary = Recording boundary marker (admin, exclude from epoching)
_EVENT_CODE_MAP: Dict[str, str] = {
    "S  1": "S 1",   # Standard stimulus (note: BrainVision may have double space)
    "S  2": "S 2",   # Deviant stimulus
    "S  3": "S 3",   # Rare/target stimulus
    "S255": "S255",  # BrainVision system marker
    "boundary": "boundary",  # Recording boundary marker
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for the given raw object.
    
    Handles various possible channel naming conventions from BrainVision files.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Check for EEG### pattern (standard BrainVision)
    for ch_name in existing_names:
        # Match EEG001, EEG01, EEG1 patterns
        match = re.match(r"EEG(\d+)", ch_name, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 64:
                # Map to standard name based on position
                standard_names = list(_EEG_CHANNEL_RENAME_MAP.values())
                if num <= len(standard_names):
                    std_name = standard_names[num - 1]
                    if std_name not in existing_names:
                        rename_map[ch_name] = std_name
    
    # Also check for numbered channels like 1, 2, 3...
    for ch_name in existing_names:
        if re.match(r"^\d+$", ch_name):
            num = int(ch_name)
            if 1 <= num <= 64:
                standard_names = list(_EEG_CHANNEL_RENAME_MAP.values())
                if num <= len(standard_names):
                    std_name = standard_names[num - 1]
                    if std_name not in existing_names:
                        rename_map[ch_name] = std_name
    
    return rename_map


def _remap_annotations_to_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Convert annotation descriptions to canonical event labels.
    
    BrainVision files may have annotations like 'S  1' (double space)
    that need normalization to 'S 1' (single space).
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw
    
    descriptions = []
    for desc in raw.annotations.description:
        # Normalize double spaces to single space
        normalized = re.sub(r"\s+", " ", desc.strip())
        # Map to canonical event code
        canonical = _EVENT_CODE_MAP.get(normalized, normalized)
        descriptions.append(canonical)
    
    # Create new annotations with remapped descriptions
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)
    
    return raw


@dataclass
class OpenNeuroDS004574Kernel:
    """Stage1 kernel for OpenNeuro ds004574 (Cross-modal Oddball Task).
    
    This kernel handles BrainVision format EEG data from a cross-modal
    oddball paradigm designed to elicit MMN and P300 components.
    
    Attributes
    ----------
    KERNEL_ID : str
        Unique identifier for this kernel.
    """
    
    KERNEL_ID: str = "openneuro-ds004574-stage1"
    
    # Subject metadata - LLM 推断，需人类复核
    # Source: Dataset README / paper not explicitly stating demographics
    # All values set to "unknown" per KERNEL_RULEBOOK requirements
    _SUBJECT_METADATA: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "unknown": {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }
    })

    def _get_subject_info(self, row) -> Dict[str, str]:
        """Extract subject metadata from row or defaults.
        
        Parameters
        ----------
        row : dict-like
            Row containing subject information (e.g., 'subject_id').
            
        Returns
        -------
        Dict[str, str]
            Subject metadata with age, sex, handedness.
        """
        subject_id = row.get("subject_id", "unknown")
        
        # Check if we have known metadata for this subject
        if subject_id in self._SUBJECT_METADATA:
            return self._SUBJECT_METADATA[subject_id].copy()
        
        # Return default unknown values
        # LLM 推断，需人类复核 - 如果有participants.tsv可用，应从此处读取
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    def _set_channel_names(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names and set montage.
        
        Channels are renamed BEFORE set_montage() as per requirements.
        
        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw EEG object with potentially non-standard channel names.
            
        Returns
        -------
        mne.io.BaseRaw
            Raw object with renamed channels and standard montage.
        """
        # Build and apply channel rename map
        rename_map = _build_channel_rename_map(raw)
        
        if rename_map:
            # Check which channels can actually be renamed
            valid_renames = {
                src: tgt for src, tgt in rename_map.items()
                if src in raw.ch_names
            }
            if valid_renames:
                print(f"[Kernel] Renaming {len(valid_renames)} channels to standard names")
                raw.rename_channels(valid_renames)
        
        # Set standard 10-20 montage for EEG channels
        try:
            montage = mne.channels.make_standard_montage("standard_1005")
            
            # Get only the channels that exist in both raw and montage
            existing_channels = set(raw.ch_names)
            montage_channels = set(montage.ch_names)
            common_channels = existing_channels & montage_channels
            
            if common_channels:
                # Pick a subset of channels that exist in raw
                raw.set_montage(montage, on_missing="warn")
                print(f"[Kernel] Set montage for {len(common_channels)} channels")
        except Exception as e:
            print(f"[Kernel] Warning: Could not set montage: {e}")
        
        return raw

    def _set_device_info(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set device information in raw.info.
        
        LLM 推断，需人类复核 - 需要确认实际使用的放大器型号
        Source: OpenNeuro dataset_description.json 或采集论文
        
        Returns
        -------
        mne.io.BaseRaw
            Raw object with updated device info.
        """
        # Common EEG amplifiers used in cross-modal studies
        # LLM 推断，需人类复核
        raw.info["device_info"] = {
            "type": "unknown",  # LLM 推断，需人类复核
            "manufacturer": "unknown",
        }
        
        return raw

    def _write_description(self, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Write eegunity_description to raw.info['description'].
        
        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw EEG object.
        row : dict-like
            Row containing file path and subject information.
            
        Returns
        -------
        mne.io.BaseRaw
            Raw object with updated description.
        """
        # Get subject metadata
        subject_info = self._get_subject_info(row)
        
        # Build description dict
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": subject_info["handedness"],
            },
        }
        
        raw.info["description"] = json.dumps(description_dict)
        
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 kernel to a single EEG recording.
        
        This method:
        1. Renames channels to standard 10-20 names
        2. Sets standard montage
        3. Remaps event annotations to canonical labels
        4. Writes eegunity_description metadata
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            Raw EEG object loaded from file.
        row : dict-like
            Locator row with file path and metadata.
            
        Returns
        -------
        mne.io.BaseRaw
            Processed raw EEG object.
        """
        # Step 1: Set device info
        raw = self._set_device_info(raw)
        
        # Step 2: Rename channels to standard names (BEFORE set_montage)
        raw = self._set_channel_names(raw)
        
        # Step 3: Remap annotations to canonical event labels
        raw = _remap_annotations_to_events(raw)
        
        # Step 4: Write eegunity_description
        raw = self._write_description(raw, row)
        
        return raw


KERNEL = OpenNeuroDS004574Kernel()