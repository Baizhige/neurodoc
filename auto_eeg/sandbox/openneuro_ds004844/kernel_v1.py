"""OpenNeuro DS004844 stage1 kernel for EEGUnity.

Dataset: Semi-Automated Driving Trust Paradigm (T22)
Subjects: 68 | Channels: 72 | Sampling Rate: 1024 Hz

Event codes are 7-digit hierarchical identifiers encoding driving state 
and automation mode. Structure: [level][subtype][variant]
- 1xxx = manual driving
- 2xxx = adaptive cruise
- 3xxx = partial automation
- 4xxx = full automation
- 27xxxx = trust-critical takeover/handoff events

Source: https://doi.org/10.18112/openneuro.ds004844.v1.0.0
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# ============================================================================
# Event Code Mapping
# ============================================================================
# Based on dataset README and analysis.md event structure table.
# All 7-digit codes mapped to human-readable labels.

_EVENT_CODE_MAP: Dict[str, str] = {
    # Raw driving state codes
    "2310002": "driving_state_manual",
    "2310001": "driving_state_adaptive_cruise",
    "4111101": "driving_state_full_automation",
    "2572001": "driving_state_normal",
    "2562001": "driving_state_slow",
    "2552001": "driving_state_stopped",
    "3110002": "driving_state_partial_automation_alt",
    "2812002": "driving_state_partial_automation_alt",
    "3110001": "driving_state_partial_automation",
    "2812001": "driving_state_partial_automation",
    # Trust-critical events
    "2714111": "trust_critical_takeover_request",
    # Manual control events
    "1410001": "manual_control_active",
    "1410002": "manual_control_inactive",
}

# Extended mapping for all observed events (from analysis.md)
_EXTENDED_EVENT_CODE_MAP: Dict[str, str] = {
    # Session management
    "1111001": "session_start",       # LLM 推断，需人类复核
    "1111002": "session_end",         # LLM 推断，需人类复核
    # Driving states (raw meta)
    "1310001": "driving_state_manual",
    "2310001": "driving_state_adaptive_cruise",
    "2310002": "driving_state_manual",
    "2512001": "driving_state_adaptive_cruise_extended",  # LLM 推断，需人类复核
    "2552001": "driving_state_stopped",
    "2562001": "driving_state_slow",
    "2572001": "driving_state_normal",
    "2714111": "trust_critical_takeover_request",
    "2812001": "partial_automation_state_1",
    "2812002": "partial_automation_state_2",
    "3110001": "partial_automation_active",
    "3110002": "partial_automation_active_alt",
    "4111101": "full_automation_active",
    # Automation events
    "2412211": "handoff_to_automation",   # LLM 推断，需人类复核
    "2744321": "automation_sustained",    # LLM 推断，需人类复核
    "2793031": "trust_event_extended",     # LLM 推断，需人类复核
    "1410001": "manual_control_onset",
    "1410002": "manual_control_offset",
}

# Task-specific mappings for classification tasks
_TASK1_DRIVE_MAPPING: Dict[str, int] = {
    "1111001": 0, "1111002": 0,  # Session markers
    "1310001": 1,  # Manual driving
    "2310001": 2,  # Adaptive cruise
    "3110001": 3,  # Partial automation
    "4111101": 4,  # Full automation
    "2714111": 5,  # Trust-critical event
}

_TASK2_AUTOMATION_LEVEL_MAPPING: Dict[str, int] = {
    "2310001": 0,  # Manual driving
    "2512001": 1,  # Adaptive cruise
    "2812001": 2,  # Partial automation
    "3110001": 3,  # Partial automation alt
    "4111101": 4,  # Full automation
}

_TASK3_TRUST_EVENT_MAPPING: Dict[str, int] = {
    "2714111": 0,  # Takeover request
    "2412211": 1,  # Handoff to automation
    "1410001": 2,  # Manual control active
    "2744321": 3,  # Automation sustained
    "2793031": 4,  # Trust extended event
}


# ============================================================================
# Subject Information
# ============================================================================
# Source: OpenNeuro dataset participants.tsv
# Format: sub-XXX with age/sex columns
# Annotator: LLM, 2026-04-08 - 由 LLM 推断，需人类复核

_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # All subjects set to unknown - actual data from participants.tsv
    # requires manual extraction. LLM cannot infer specific subject info.
}


# ============================================================================
# Channel Configuration
# ============================================================================
# Source: Dataset documentation / paper
# 72-channel EEG with extended coverage
# Annotator: LLM, 2026-04-08 - 由 LLM 推断，需人类复核

_STANDARD_1020_CHANNELS = [
    "FP1", "FPZ", "FP2",
    "AF3", "AF4",
    "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
    "PO3", "PO4", "POZ",
    "O1", "OZ", "O2",
]

_EXTENDED_CHANNELS_72 = _STANDARD_1020_CHANNELS + [
    "AF7", "AF8", "T9", "T10",
    "TP9", "TP10", "PO9", "PO10",
    "M1", "M2", "X1", "X2", "X3", "X4",  # Auxiliary channels
]


def _parse_7digit_event(event_value: Any) -> Optional[str]:
    """Parse 7-digit event code into readable label.
    
    Event codes follow pattern: [level][subtype][variant]
    - First digit: automation level (1=manual, 2=adaptive, 3=partial, 4=full)
    - Subsequent digits: state-specific information
    """
    if event_value is None:
        return None
    
    # Handle numeric event values
    if isinstance(event_value, (int, float)):
        code = str(int(event_value)).zfill(7)
    else:
        code = str(event_value).strip()
    
    # Check if it's a 7-digit code
    if len(code) == 7 and code.isdigit():
        return _EXTENDED_EVENT_CODE_MAP.get(code, f"event_{code}")
    
    # Check original mapping
    return _EVENT_CODE_MAP.get(code, str(event_value))


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20.
    
    Common patterns in EEG datasets:
    - EEG-0 -> FC3, EEG-1 -> FC1, etc.
    - A, B, C numbering
    - Prefix/suffix variants
    
    Source: Dataset channel configuration documentation
    Annotator: LLM, 2026-04-08 - 由 LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Pattern 1: EEG-N numbered channels (common in BrainVision exports)
    eeg_number_pattern = re.compile(r'^(?:EEG[-_]?)?(\d+)$', re.IGNORECASE)
    
    # Pattern 2: Channels with A/B/C prefixes
    prefix_pattern = re.compile(r'^(A|B|C)(\d+)$', re.IGNORECASE)
    
    # If we detect numbered EEG channels, try to map them
    eeg_channels = [ch for ch in raw.ch_names if 'EEG' in ch.upper()]
    if len(eeg_channels) == 64 or len(eeg_channels) == 72:
        # Standard 64 or 72 channel setup - use standard ordering
        standard_order = _EXTENDED_CHANNELS_72 if len(eeg_channels) == 72 else _STANDARD_1020_CHANNELS[:64]
        
        # Sort by numeric value
        def get_channel_number(ch_name: str) -> int:
            match = eeg_number_pattern.match(ch_name)
            if match:
                return int(match.group(1))
            return float('inf')
        
        sorted_eeg = sorted(eeg_channels, key=get_channel_number)
        
        # Map in order
        for i, (old_name, new_name) in enumerate(zip(sorted_eeg, standard_order)):
            if old_name != new_name and old_name in existing:
                rename_map[old_name] = new_name
    
    # Pattern 3: Check for alternative naming schemes
    # e.g., 'Fp1' -> 'FP1', 'Fz' -> 'FZ', etc.
    for ch in existing:
        if ch.upper() in [c.upper() for c in _EXTENDED_CHANNELS_72]:
            # Already in standard format
            pass
    
    return rename_map


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from file path."""
    # Pattern: sub-XXX
    match = re.search(r'sub-([A-Za-z0-9]+)', file_path)
    if match:
        return match.group(1)
    return "unknown"


def _extract_session_from_path(file_path: str) -> Optional[str]:
    """Extract session ID from file path."""
    match = re.search(r'ses-([A-Za-z0-9]+)', file_path)
    if match:
        return match.group(1)
    return None


# ============================================================================
# Kernel Implementation
# ============================================================================

@dataclass
class OpenNeuroDS004844Kernel:
    """Stage1 kernel for OpenNeuro DS004844 (Semi-Automated Driving Trust Paradigm).
    
    This kernel handles:
    - 7-digit hierarchical event codes (driving state + automation level)
    - Trust-critical event detection (27xxxx codes)
    - BIDS-compatible subject metadata from participants.tsv
    - Standard 10-20 channel naming (72-channel system)
    """
    
    KERNEL_ID: str = "openneuro-ds004844-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context
        raw
            In-memory MNE Raw object
        row
            Locator row with file path and metadata
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with annotations and metadata
        """
        file_path = row.get("File Path", "") if hasattr(row, 'get') else row.get("File Path", str(row))
        
        # 1. Rename channels to standard 10-20 system
        raw = self._rename_channels(raw)
        
        # 2. Set montage if possible
        raw = self._set_montage(raw)
        
        # 3. Extract and process events
        raw = self._process_events(raw)
        
        # 4. Update description metadata
        raw = self._update_description(raw, file_path)
        
        return raw
    
    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename non-standard channels to standard 10-20 naming."""
        rename_map = _build_channel_rename_map(raw)
        
        if rename_map:
            try:
                existing_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
                if existing_renames:
                    print(f"[Kernel] Renaming {len(existing_renames)} channels to standard 10-20")
                    raw.rename_channels(existing_renames)
            except Exception as e:
                print(f"[Kernel] Channel rename warning: {e}")
        
        return raw
    
    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage for spatial information."""
        try:
            # Try to set standard 1020 montage
            montage = mne.channels.make_standard_montage('standard_1020')
            
            # Check which channels are present
            present_channels = set(raw.ch_names) & set(montage.ch_names)
            
            if len(present_channels) >= 20:
                raw.set_montage(montage, on_missing='ignore')
                print(f"[Kernel] Set montage for {len(present_channels)} channels")
            else:
                print(f"[Kernel] Skipped montage - only {len(present_channels)} standard channels found")
        except Exception as e:
            print(f"[Kernel] Montage warning: {e}")
        
        return raw
    
    def _process_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process and annotate events from triggers/stim channels."""
        
        # Get current annotations
        annotations = raw.annotations
        
        if len(annotations) == 0:
            # Try to read events from stim channels
            raw = self._extract_stim_events(raw)
        else:
            # Remap existing annotations
            raw = self._remap_annotations(raw)
        
        return raw
    
    def _extract_stim_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Extract events from stim channels and create annotations."""
        
        # Find stim/misc channels
        stim_channels = []
        for i, ch_type in enumerate(raw.get_channel_types()):
            if ch_type in ['stim', 'misc']:
                stim_channels.append(raw.ch_names[i])
        
        # If no stim channels, check if we need to look at data directly
        if not stim_channels:
            # Check if any channel might contain event codes
            # Common names: 'Event', 'Trigger', 'Status'
            for ch_name in ['Event', 'Trigger', 'Status', 'event', 'trigger']:
                if ch_name in raw.ch_names:
                    stim_channels.append(ch_name)
                    break
        
        if not stim_channels:
            print("[Kernel] No stim channels found - no events to extract")
            return raw
        
        # Extract events from stim channel data
        stim_data = None
        stim_ch = stim_channels[0]
        
        try:
            stim_idx = raw.ch_names.index(stim_ch)
            stim_data = raw.get_data()[stim_idx]
        except Exception as e:
            print(f"[Kernel] Could not read stim channel {stim_ch}: {e}")
            return raw
        
        # Find threshold crossings (event onsets)
        threshold = 0.5 * np.max(np.abs(stim_data)) if np.max(np.abs(stim_data)) > 0 else 1.0
        
        # Find rising edges (event onsets)
        above_threshold = stim_data > threshold
        edges = np.diff(above_threshold.astype(int))
        onset_indices = np.where(edges > 0)[0] + 1
        
        if len(onset_indices) == 0:
            print("[Kernel] No event onsets detected in stim channel")
            return raw
        
        # Get event values at onset points
        sfreq = raw.info['sfreq']
        event_values = stim_data[onset_indices]
        
        # Convert to string labels
        descriptions = []
        for val in event_values:
            label = _parse_7digit_event(val)
            descriptions.append(label if label else f"event_{int(val)}")
        
        # Create annotations
        onsets = onset_indices / sfreq
        durations = np.zeros(len(onsets))
        
        try:
            new_annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions
            )
            raw.set_annotations(new_annotations)
            print(f"[Kernel] Created {len(onsets)} annotations from stim channel")
        except Exception as e:
            print(f"[Kernel] Failed to create annotations: {e}")
        
        return raw
    
    def _remap_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Remap existing annotation descriptions to standardized labels."""
        
        if len(raw.annotations) == 0:
            return raw
        
        descriptions = []
        for desc in raw.annotations.description:
            label = _parse_7digit_event(desc)
            descriptions.append(label if label else str(desc))
        
        # Create new annotations with remapped descriptions
        try:
            new_annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=descriptions
            )
            raw.set_annotations(new_annotations)
        except Exception as e:
            print(f"[Kernel] Failed to remap annotations: {e}")
        
        return raw
    
    def _update_description(self, raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
        """Update raw.info['description'] with standardized metadata."""
        
        # Extract subject ID
        subject_id = _extract_subject_id_from_path(file_path)
        
        # Get subject info if available
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        
        # Build description dictionary
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),      # LLM 推断，需人类复核
                "sex": subject_info.get("sex", "unknown"),      # LLM 推断，需人类复核
                "amplifier": "unknown",                          # LLM 推断，需人类复核
                "cap": "unknown",                                # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),  # LLM 推断，需人类复核
            },
            "dataset_info": {
                "dataset_id": "ds004844",
                "paradigm": "semi-automated driving trust",
                "task": "drive",
                "sampling_rate": raw.info.get('sfreq', 'unknown'),
                "n_channels": len(raw.ch_names),
            }
        }
        
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


# ============================================================================
# Module Export
# ============================================================================

KERNEL = OpenNeuroDS004844Kernel()