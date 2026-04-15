"""OpenNeuro DS004579 stage1 kernel for EEGUnity.

Interval Timing Task dataset - 30 subjects, 64 channels, 512 Hz.

Events: S 1-S 7 (timing conditions), R 3 (button press response),
boundary, S255 (BrainVision system marker).

Source: https://openneuro.org/datasets/ds004579
Reference: DOI 10.1523/JNEUROSCI.1675-24.2025
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne


# Standard 64-channel EEG montage (extended 10-20 system)
# All fields marked as "unknown" per KERNEL_RULEBOOK unless source confirmed
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Source: OpenNeuro ds004579 participants.tsv (if available) or README
    # All values require human verification before finalizing
}


# 64-channel standard names for BrainCap 64 or similar 64-channel caps
# Source: Standard 10-20 extended system, matches 64-channel BrainVision caps
# Annotator: LLM, 2026-04-08, # LLM 推断，需人类复核
_STANDARD_64_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Cz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]


# BrainVision channel naming patterns commonly seen
_BV_CHANNEL_PATTERNS = {
    # Common BrainVision/Victoria patterns
    "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
    "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4",
    "F3": "F3", "FZ": "Fz", "F4": "F4",
    "F7": "F7", "F8": "F8",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "T7": "T7", "T8": "T8",
    "C3": "C3", "CZ": "Cz", "C4": "C4",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    "P7": "P7", "P3": "P3", "PZ": "Pz", "P4": "P4", "P8": "P8",
    "PO7": "PO7", "PO3": "PO3", "POZ": "POz", "PO4": "PO4", "PO8": "PO8",
    "O1": "O1", "OZ": "Oz", "O2": "O2",
    # Additional common extensions
    "Fp3": "Fp1", "Fp4": "Fp2",  # Alternate naming
    "F1": "F1", "F2": "F2",
    "F5": "F5", "F6": "F6",
    "FT9": "FT9", "FT10": "FT10",
    "TP9": "TP9", "TP10": "TP10",
    "P1": "P1", "P2": "P2",
    "P5": "P5", "P6": "P6",
    "PO5": "PO5", "PO6": "PO6",
    "AF5": "AF5", "AF6": "AF6",
    "AF1": "AF1", "AF2": "AF2",
    "FC3": "FC3", "FC4": "FC4",
    "FT1": "FT1", "FT2": "FT2",
    "FT5": "FT5", "FT6": "FT6",
    "TP1": "TP1", "TP2": "TP2",
    "TP3": "TP3", "TP4": "TP4",
    "CP3": "CP3", "CP4": "CP4",
    "PO1": "PO1", "PO2": "PO2",
}


def _detect_channel_pattern(ch_names: List[str]) -> str:
    """Detect the channel naming convention used in the data."""
    sample_names = ch_names[:10] if len(ch_names) >= 10 else ch_names
    
    # Check for standard 10-20 names
    standard_count = sum(1 for ch in sample_names if ch in _STANDARD_64_CHANNELS)
    if standard_count >= len(sample_names) * 0.5:
        return "standard"
    
    # Check for BrainVision capitalized names
    bv_count = sum(1 for ch in sample_names if ch.upper() in _BV_CHANNEL_PATTERNS)
    if bv_count >= len(sample_names) * 0.5:
        return "brainvision"
    
    # Check for numeric patterns (EEG-001, etc.)
    numeric_pattern = sum(1 for ch in sample_names if re.match(r'EEG[-_]?\d+', ch, re.IGNORECASE))
    if numeric_pattern >= len(sample_names) * 0.5:
        return "numeric"
    
    return "unknown"


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map based on detected naming convention."""
    ch_names = raw.ch_names
    rename_map: Dict[str, str] = {}
    pattern = _detect_channel_pattern(ch_names)
    
    if pattern == "standard":
        # Already standard names, minimal changes needed
        return rename_map
    
    elif pattern == "brainvision":
        for ch in ch_names:
            upper_ch = ch.upper()
            if upper_ch in _BV_CHANNEL_PATTERNS:
                target = _BV_CHANNEL_PATTERNS[upper_ch]
                if ch != target:
                    rename_map[ch] = target
    
    elif pattern == "numeric":
        # For numeric patterns, try to map to standard based on position
        # This requires knowledge of the specific cap layout
        for i, ch in enumerate(ch_names):
            if re.match(r'EEG[-_]?\d+', ch, re.IGNORECASE):
                match = re.search(r'\d+', ch)
                if match:
                    idx = int(match.group())
                    # Common mapping: 1->Fp1, 2->Fpz, etc. - needs verification
                    # Using a heuristic mapping based on 10-20 system positions
                    pass  # Placeholder - needs specific cap documentation
    
    return rename_map


def _parse_subject_id(row) -> str:
    """Extract subject ID from row."""
    if hasattr(row, 'get'):
        file_path = row.get('File Path', '')
        subject_id = row.get('subject_id', '')
    else:
        file_path = row.get('File Path', '') if isinstance(row, dict) else ''
        subject_id = row.get('subject_id', '') if isinstance(row, dict) else ''
    
    # Try to extract from file path if not directly available
    if not subject_id and file_path:
        match = re.search(r'sub-(\w+)', file_path, re.IGNORECASE)
        if match:
            subject_id = match.group(1)
    
    return subject_id or "unknown"


def _get_subject_metadata(subject_id: str) -> Dict[str, str]:
    """Get subject metadata from dictionary or return defaults."""
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id]
    return {
        "age": "unknown",  # LLM 推断，需人类复核
        "sex": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",  # LLM 推断，需人类复核
    }


class OpenNeuroDS004579Kernel:
    """Stage1 kernel for OpenNeuro DS004579 Interval Timing Task."""

    KERNEL_ID: str = "openneuro-ds004579-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and events
        """
        # Store original description
        original_description = raw.info.get("description", "")

        # Extract subject ID
        subject_id = _parse_subject_id(row)
        subject_meta = _get_subject_metadata(subject_id)

        # Get channel rename map based on detected pattern
        rename_map = _build_channel_rename_map(raw)

        # Apply channel renames BEFORE set_montage
        if rename_map:
            renamed_count = len(rename_map)
            raw.rename_channels(rename_map)
            # Log rename operations for debugging
            print(f"[Kernel] Renamed {renamed_count} channels for {subject_id}")

        # Try to set standard 64-channel montage
        try:
            # Try standard 64-channel montage first
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            # If standard montage fails, try alternative approaches
            print(f"[Kernel] Could not set montage: {e}")

        # Handle annotations - BrainVision format uses S-codes
        current_annotations = raw.annotations
        
        # Remap BrainVision S-codes to descriptive names
        if len(current_annotations) > 0:
            descriptions = list(current_annotations.description)
            new_descriptions = []
            
            for desc in descriptions:
                desc_stripped = desc.strip()
                
                # Map S-codes (with possible space variations)
                if re.match(r'^S\s*\d+$', desc_stripped):
                    # Extract number
                    num_match = re.search(r'\d+', desc_stripped)
                    if num_match:
                        num = int(num_match.group())
                        if 1 <= num <= 7:
                            new_descriptions.append(f"S {num}")
                        elif num == 255:
                            new_descriptions.append("S255")
                        elif 49 <= num <= 55:
                            # S49-S55: Unknown sub-condition markers
                            # Source: Observation from data, requires verification
                            new_descriptions.append(f"S {num}")  # LLM 推断，需人类复核
                        elif num == 63:
                            # S63: Unknown marker
                            new_descriptions.append(f"S {num}")  # LLM 推断，需人类复核
                        else:
                            new_descriptions.append(f"S {num}")
                
                # Map R-codes (response markers)
                elif re.match(r'^R\s*\d+$', desc_stripped):
                    num_match = re.search(r'\d+', desc_stripped)
                    if num_match:
                        num = int(num_match.group())
                        if num == 3:
                            new_descriptions.append("R 3")
                        else:
                            new_descriptions.append(f"R {num}")
                
                # Map boundary markers
                elif desc_stripped.lower() == "boundary":
                    new_descriptions.append("boundary")
                
                else:
                    # Keep original for unknown markers
                    new_descriptions.append(desc_stripped)
            
            # Create new annotations with remapped descriptions
            new_annotations = mne.Annotations(
                onset=current_annotations.onset,
                duration=current_annotations.duration,
                description=new_descriptions,
                orig_time=current_annotations.orig_time,
            )
            raw.set_annotations(new_annotations)

        # Build eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(subject_meta.get("age", "unknown")),
                "sex": str(subject_meta.get("sex", "unknown")).lower(),
                "amplifier": "unknown",  # LLM 推断，需人类复核 - likely BrainVision BrainAmp
                "cap": "unknown",  # LLM 推断，需人类复核 - likely 64-channel Ag/AgCl cap
                "handedness": str(subject_meta.get("handedness", "unknown")).lower(),
            },
        }

        raw.info["description"] = json.dumps(description_dict)

        # Print summary for verification
        n_channels = len(raw.ch_names)
        sfreq = raw.info["sfreq"]
        n_annotations = len(raw.annotations)
        
        print(f"[Kernel] {subject_id}: {n_channels} channels, {sfreq} Hz, {n_annotations} annotations")

        return raw


# Module-level kernel instance
KERNEL = OpenNeuroDS004579Kernel()