"""Dataset-specific kernel for openneuro_ds004444.

The BMI-HDEEG dataset 1

Sensorimotor rhythm BCI: 4-class MI with high-density EEG (130 channels, 1000 Hz).

Source: https://openneuro.org/datasets/ds004444
Source: DOI 10.1038/s41597-023-02260-6 (data descriptor for BMI-HDEEG Dataset 1)

Event Mapping (confirmed by paper):
    1 -> left_hand_MI
    2 -> right_hand_MI
    3 -> feet_MI
    4 -> tongue_MI

Note: Event 3 (feet MI) has 0 events across dataset per scan.
      Kernel handles this gracefully; tasks using event 3 may fail.

Channel Info:
    130-channel high-density scalp EEG (likely BrainVision system)
    Standard naming scheme expected (extended 10-20 or 10-10 system)
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np

# Try to extend base kernel if available, otherwise standalone
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from kernels.openneuro_specific._base import OpenNeuroBaseKernel
    _HAS_BASE = True
except ImportError:
    _HAS_BASE = False

# Event mapping: raw numeric code -> semantic label
_EVENT_MAP: Dict[str, str] = {
    "1": "left_hand_MI",
    "2": "right_hand_MI",
    "3": "feet_MI",
    "4": "tongue_MI",
}

# Reverse mapping for annotations
_ANNOTATION_EVENT_MAP: Dict[str, int] = {
    "left_hand_MI": 1,
    "right_hand_MI": 2,
    "feet_MI": 3,
    "tongue_MI": 4,
}

# Standard 10-10 system channels for high-density EEG (130 channels)
# Source: DOI 10.1038/s41597-023-02260-6 confirms 128+ channel HD-EEG
# Common high-density 10-10 system electrode names
_10_10_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", 
    "T7", "T8",
    "TP7", "TP8",
    "M1", "M2",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    # Additional 10-5 system for 130+ channels (partial listing)
    "F2", "F4", "F6", "F8", "F10",
    "AF9", "AF10",
    "F9", "F11",
    "FT9", "FT10",
    "T9", "T10",
    "TP9", "TP10",
    "P9", "P11",
    "PO9", "PO10",
    "O9", "O10",
]


def _detect_channel_type(ch_name: str) -> Optional[str]:
    """Detect channel type from standard naming conventions."""
    ch_upper = ch_name.upper()
    
    # EEG standard channels
    if any(prefix in ch_upper for prefix in ['EEG-', 'E', 'FP', 'AF', 'F', 'FT', 'T', 'TP', 'M', 'FC', 'C', 'CP', 'P', 'PO', 'O']):
        if ch_upper.startswith('EOG') or 'EOG' in ch_upper:
            return 'eog'
        if ch_upper.startswith('ECG') or 'ECG' in ch_upper:
            return 'ecg'
        if ch_upper.startswith('EMG') or 'EMG' in ch_upper:
            return 'emg'
        if ch_upper.startswith('STIM') or ch_upper == 'TRIGGER':
            return 'stim'
        if ch_upper in ['M1', 'M2', 'A1', 'A2', 'TP9', 'TP10', 'REF']:
            return 'misc'
        return 'eeg'
    
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-10 naming.
    
    Attempts to normalize channel names to standard 10-10 system.
    Handles common naming variations in BrainVision data.
    
    Source: Standard 10-10 electrode naming convention
    Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Common BrainVision / BVA naming patterns to standardize
    # These are common aliases found in high-density EEG datasets
    alias_patterns = {
        # Standard 10-10 electrodes
        'Fp1': ['Fp1', 'EEG-Fp1', 'Fp 1'],
        'Fp2': ['Fp2', 'EEG-Fp2', 'Fp 2'],
        'Fpz': ['Fpz', 'EEG-Fpz', 'Fpz'],
        'AF7': ['AF7', 'EEG-AF7'],
        'AF3': ['AF3', 'EEG-AF3'],
        'AFz': ['AFz', 'EEG-AFz'],
        'AF4': ['AF4', 'EEG-AF4'],
        'AF8': ['AF8', 'EEG-AF8'],
        'F7': ['F7', 'EEG-F7'],
        'F5': ['F5', 'EEG-F5'],
        'F3': ['F3', 'EEG-F3'],
        'F1': ['F1', 'EEG-F1'],
        'Fz': ['Fz', 'EEG-Fz'],
        'F2': ['F2', 'EEG-F2'],
        'F4': ['F4', 'EEG-F4'],
        'F6': ['F6', 'EEG-F6'],
        'F8': ['F8', 'EEG-F8'],
        'FC5': ['FC5', 'EEG-FC5'],
        'FC3': ['FC3', 'EEG-FC3'],
        'FC1': ['FC1', 'EEG-FC1'],
        'FCz': ['FCz', 'EEG-FCz'],
        'FC2': ['FC2', 'EEG-FC2'],
        'FC4': ['FC4', 'EEG-FC4'],
        'FC6': ['FC6', 'EEG-FC6'],
        'T7': ['T7', 'EEG-T7', 'T7', 'TP7'],
        'C5': ['C5', 'EEG-C5'],
        'C3': ['C3', 'EEG-C3'],
        'C1': ['C1', 'EEG-C1'],
        'Cz': ['Cz', 'EEG-Cz'],
        'C2': ['C2', 'EEG-C2'],
        'C4': ['C4', 'EEG-C4'],
        'C6': ['C6', 'EEG-C6'],
        'T8': ['T8', 'EEG-T8', 'T8', 'TP8'],
        'CP5': ['CP5', 'EEG-CP5'],
        'CP3': ['CP3', 'EEG-CP3'],
        'CP1': ['CP1', 'EEG-CP1'],
        'CPz': ['CPz', 'EEG-CPz'],
        'CP2': ['CP2', 'EEG-CP2'],
        'CP4': ['CP4', 'EEG-CP4'],
        'CP6': ['CP6', 'EEG-CP6'],
        'P7': ['P7', 'EEG-P7'],
        'P5': ['P5', 'EEG-P5'],
        'P3': ['P3', 'EEG-P3'],
        'P1': ['P1', 'EEG-P1'],
        'Pz': ['Pz', 'EEG-Pz'],
        'P2': ['P2', 'EEG-P2'],
        'P4': ['P4', 'EEG-P4'],
        'P6': ['P6', 'EEG-P6'],
        'P8': ['P8', 'EEG-P8'],
        'PO7': ['PO7', 'EEG-PO7'],
        'PO3': ['PO3', 'EEG-PO3'],
        'POz': ['POz', 'EEG-POz'],
        'PO4': ['PO4', 'EEG-PO4'],
        'PO8': ['PO8', 'EEG-PO8'],
        'O1': ['O1', 'EEG-O1'],
        'Oz': ['Oz', 'EEG-Oz'],
        'O2': ['O2', 'EEG-O2'],
        # Mastoid / reference
        'M1': ['M1', 'A1', 'TP9', 'MastoidL'],
        'M2': ['M2', 'A2', 'TP10', 'MastoidR'],
    }
    
    for target, aliases in alias_patterns.items():
        for alias in aliases:
            if alias in existing_names and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _remap_events_to_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Convert numeric event codes to semantic annotation labels.
    
    BMI-HDEEG uses numeric event codes 1-4 that need mapping to semantic labels.
    """
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
    except Exception:
        return raw
    
    # Build mapping from original numeric IDs to semantic labels
    new_annot_map: Dict[str, str] = {}
    
    for desc, orig_id in event_id.items():
        # Try to match numeric codes
        desc_str = str(desc)
        if desc_str in _EVENT_MAP:
            new_annot_map[desc_str] = _EVENT_MAP[desc_str]
        elif desc in _EVENT_MAP:
            new_annot_map[str(desc)] = _EVENT_MAP[desc]
    
    # Create new annotations with semantic labels
    if new_annot_map:
        new_descriptions = []
        for desc in raw.annotations.description:
            desc_str = str(desc)
            new_desc = new_annot_map.get(desc_str, desc_str)
            new_descriptions.append(new_desc)
        
        new_annotations = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=new_descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annotations)
    
    return raw


class OpenNeuroDS004444Kernel:
    """Stage1 kernel for the BMI-HDEEG Dataset 1 (openneuro_ds004444).
    
    This kernel handles:
    - High-density 130-channel EEG data
    - 4-class motor imagery events (1-4)
    - Standard 10-10 channel naming normalization
    - Missing subject metadata (sets to 'unknown')
    
    Parameters
    ----------
    udataset : object
        EEGUnity dataset context.
    raw : mne.io.BaseRaw
        MNE Raw object for the recording.
    row : pandas.Series
        Locator row with file information.
    
    Returns
    -------
    mne.io.BaseRaw
        Processed Raw object with updated metadata and events.
    """
    
    KERNEL_ID: str = "openneuro-ds004444-stage1"
    
    # Device metadata (hardcoded from paper references)
    # Source: DOI 10.1038/s41597-023-02260-6
    # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
    _DEVICE_INFO: Dict[str, str] = {
        "amplifier": "unknown",  # Paper mentions "high-density EEG" but no specific model
        "cap": "unknown",  # 130-channel system, exact cap type not specified in descriptor
        "handedness": "unknown",  # Not available in dataset metadata
    }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record."""
        
        # Store original description
        original_description = raw.info.get("description", "")
        if not original_description:
            original_description = ""
        
        # Build eegunity_description with metadata
        # Note: age and sex are missing in dataset (confirmed by scan)
        # Source: Dataset Info table in analysis.md
        eegunity_description = {
            "age": "unknown",  # LLM 推断，需人类复核
            "sex": "unknown",  # LLM 推断，需人类复核
            "amplifier": self._DEVICE_INFO["amplifier"],
            "cap": self._DEVICE_INFO["cap"],
            "handedness": self._DEVICE_INFO["handedness"],
        }
        
        # Write description to raw.info
        description_dict = {
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard 10-10 naming BEFORE set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming {len(rename_map)} channels to standard 10-10 names")
            raw.rename_channels(rename_map, verbose=False)
        
        # Set channel types for non-EEG channels
        for ch_name in raw.ch_names:
            ch_idx = raw.ch_names.index(ch_name)
            ch_type = _detect_channel_type(ch_name)
            if ch_type and ch_type != 'eeg':
                try:
                    raw.set_channel_types({ch_name: ch_type}, verbose=False)
                except Exception:
                    pass
        
        # Try to set standard 10-10 montage if channels are recognizable
        # This may fail if channel count > standard 1020; use 10-05 as fallback
        montage_set = False
        for montage_name in ['standard_1020', 'standard_1005']:
            try:
                montage = mne.channels.make_standard_montage(montage_name)
                # Check how many channels match
                common_chs = set(raw.ch_names) & set(montage.ch_names)
                if len(common_chs) > 60:  # At least 60 channels should match
                    raw.set_montage(montage, verbose=False)
                    print(f"[{self.KERNEL_ID}] Set montage: {montage_name} ({len(common_chs)} channels)")
                    montage_set = True
                    break
            except Exception:
                continue
        
        if not montage_set:
            print(f"[{self.KERNEL_ID}] Warning: Could not set standard montage")
        
        # Remap numeric event codes (1-4) to semantic labels
        raw = _remap_events_to_annotations(raw)
        
        return raw


class OpenNeuroDS004444KernelCompat:
    """Compatibility wrapper for OpenNeuroBaseKernel interface.
    
    Used when base kernel is available for consistency with other 
    OpenNeuro dataset kernels.
    """
    
    KERNEL_ID: str = "openneuro-ds004444-stage1"
    
    def __init__(self):
        self._kernel = OpenNeuroDS004444Kernel()
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Delegate to underlying kernel implementation."""
        return self._kernel.apply(udataset, raw, row)


# Choose implementation based on base kernel availability
if _HAS_BASE:
    # Extend base kernel for consistency
    class OpenNeuroDS004444Kernel(OpenNeuroBaseKernel):
        """Stage1 kernel for BMI-HDEEG Dataset 1 extending base kernel."""
        
        KERNEL_ID = "openneuro-ds004444-stage1"
        
        def __init__(self):
            super().__init__(
                KERNEL_ID=self.KERNEL_ID,
                event_map=_EVENT_MAP,
            )
        
        def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
            """Apply stage1 preprocessing with extended functionality."""
            
            # Call parent apply first
            raw = super().apply(udataset, raw, row)
            
            # Store original description before parent overwrites
            # Re-parse and update eegunity_description
            original_description = ""
            try:
                desc_dict = json.loads(raw.info.get("description", "{}"))
                original_description = desc_dict.get("original_description", "")
            except (json.JSONDecodeError, TypeError):
                original_description = raw.info.get("description", "")
            
            # Build updated eegunity_description
            eegunity_description = {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": self._DEVICE_INFO.get("amplifier", "unknown"),
                "cap": self._DEVICE_INFO.get("cap", "unknown"),
                "handedness": self._DEVICE_INFO.get("handedness", "unknown"),
            }
            
            description_dict = {
                "original_description": original_description,
                "eegunity_description": eegunity_description,
            }
            raw.info["description"] = json.dumps(description_dict)
            
            # Rename channels to standard 10-10 naming BEFORE set_montage
            rename_map = _build_channel_rename_map(raw)
            if rename_map:
                raw.rename_channels(rename_map, verbose=False)
            
            # Set channel types for non-EEG channels
            for ch_name in raw.ch_names:
                ch_type = _detect_channel_type(ch_name)
                if ch_type and ch_type != 'eeg':
                    try:
                        raw.set_channel_types({ch_name: ch_type}, verbose=False)
                    except Exception:
                        pass
            
            # Try to set standard 10-10 montage
            for montage_name in ['standard_1020', 'standard_1005']:
                try:
                    montage = mne.channels.make_standard_montage(montage_name)
                    common_chs = set(raw.ch_names) & set(montage.ch_names)
                    if len(common_chs) > 60:
                        raw.set_montage(montage, verbose=False)
                        break
                except Exception:
                    continue
            
            # Additional event remapping for semantic labels
            raw = _remap_events_to_annotations(raw)
            
            return raw
        
        # Device metadata
        # Source: DOI 10.1038/s41597-023-02260-6
        # Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
        _DEVICE_INFO = {
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }


# Module-level KERNEL object for EEGUnity
KERNEL = OpenNeuroDS004444Kernel()