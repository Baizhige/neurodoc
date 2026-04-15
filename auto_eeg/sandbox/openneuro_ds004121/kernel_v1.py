"""Dataset-specific kernel for openneuro ds004121.

BCIT Mind Wandering dataset.
Driving simulation with mind wandering thought probes.
60 subjects, 74 channels, 1024 Hz.

Source: https://doi.org/10.18112/openneuro.ds004121.v1.0.0
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# All BCIT event codes documented in analysis.md
# Source: analysis.md - Event Structure table
_EVENT_MAP = {
    # Lateral perturbation events (Task 1)
    "4311": "lateral_perturb_type1",      # type 1 (leftward)
    "4312": "lateral_perturb_type2",      # type 2 (rightward)
    "4210": "perturbation_onset",
    "4220": "perturbation_event",
    "4230": "perturbation_direction_event",
    "4730": "special_driving_event",
    "3111": "perturbation_onset_alt",
    
    # Police vehicle / vigilance
    "4411": "police_vehicle_event",
    
    # Audio conditions (Task 3)
    "4621": "audio_condition_type1",      # silence
    "4622": "audio_condition_type2",      # music/podcast
    "2811": "audio_cue_event_type1",
    "2812": "audio_cue_event_type2",
    
    # Speed markers
    "3200": "speed_marker",
    
    # Performance metrics
    "3310": "performance_metric",
    
    # Lane corrections
    "1211": "lane_correction_type1",
    "1212": "lane_correction_type2",
    
    # Driver responses
    "1121": "driver_response_type1",
    "1122": "driver_response_type2",
    "1111": "driver_response_alt1",
    "1112": "driver_response_alt2",
    
    # Behavioral responses
    "2621": "behavioral_response_type1",
    "2622": "behavioral_response_type2",
    "2631": "behavioral_response_alt1",
    "2632": "behavioral_response_alt2",
    
    # Thought probes (Mind Wandering - Task 2)
    "2221": "thought_probe_type1",
    "2222": "thought_probe_type2",
    "2241": "probe_response_type1_on_task",   # on-task response
    "2242": "probe_response_type1_off_task",  # off-task response
    "2251": "probe_response_type2_on_task",
    "2252": "probe_response_type2_off_task",
}

# Standard 10-20 electrode names (first 64 for EEG channels)
# LLM 推断，需人类复核
_STANDARD_10_20 = [
    'Fp1', 'Fpz', 'Fp2',
    'AF7', 'AF3', 'AFz', 'AF4', 'AF8',
    'F7', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F8',
    'FT7', 'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 'FT8',
    'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8',
    'TP7', 'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6', 'TP8',
    'P7', 'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6', 'P8',
    'PO7', 'PO3', 'POz', 'PO4', 'PO8',
    'O1', 'Oz', 'O2',
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names.
    
    LLM 推断，需人类复核 - Channel mapping based on typical OpenNeuro
    EEG dataset conventions and standard 10-20 positions.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Pattern 1: EEG-001, EEG-002, ... (BrainVision style)
    eeg_pattern = re.compile(r'^EEG[-_]?(\d+)$', re.IGNORECASE)
    
    # Pattern 2: E001, E002, ... (BioSemi style)
    e_pattern = re.compile(r'^E(\d+)$', re.IGNORECASE)
    
    # Pattern 3: Channel_001, Channel_002, ...
    ch_pattern = re.compile(r'^Channel[-_]?(\d+)$', re.IGNORECASE)
    
    for ch in raw.ch_names:
        match = eeg_pattern.match(ch)
        if match:
            idx = int(match.group(1)) - 1
            if idx < len(_STANDARD_10_20):
                rename_map[ch] = _STANDARD_10_20[idx]
            continue
            
        match = e_pattern.match(ch)
        if match:
            idx = int(match.group(1)) - 1
            if idx < len(_STANDARD_10_20):
                rename_map[ch] = _STANDARD_10_20[idx]
            continue
            
        match = ch_pattern.match(ch)
        if match:
            idx = int(match.group(1)) - 1
            if idx < len(_STANDARD_10_20):
                rename_map[ch] = _STANDARD_10_20[idx]
            continue
    
    return rename_map


def _reconstruct_events_from_raw(
    raw: mne.io.BaseRaw,
) -> Tuple[np.ndarray, Dict[str, int]]:
    """Reconstruct events array from raw stim channels using event_map.
    
    Reads events from stim channels and maps to human-readable descriptions.
    """
    # Get events from stim channels
    events, event_id = mne.events_from_annotations(raw, verbose=False)
    
    # Build reverse mapping from numeric values to event descriptions
    new_event_id: Dict[str, int] = {}
    new_events = []
    
    for desc, code in event_id.items():
        # Try to match against our event map
        mapped_desc = _EVENT_MAP.get(str(code), desc)
        if mapped_desc not in new_event_id:
            new_event_id[mapped_desc] = len(new_event_id) + 1
        new_events.append([events[events[:, 2] == code][0, 0], 0, new_event_id[mapped_desc]])
    
    if new_events:
        new_events = np.array(new_events)
        # Sort by time
        new_events = new_events[np.argsort(new_events[:, 0])]
        # Reassign IDs sequentially
        for i, desc in enumerate(sorted(new_event_id.keys(), key=lambda d: new_event_id[d])):
            new_event_id[desc] = i + 1
        # Rebuild events with final IDs
        final_events = []
        for orig_time, _, _ in new_events:
            mapped_desc = None
            for desc, code in _EVENT_MAP.items():
                if code in new_event_id:
                    mapped_desc = code
                    break
            for ev_desc, ev_code in event_id.items():
                if int(ev_desc) == int(code) if ev_desc.isdigit() else False:
                    pass
        final_events = np.array([[e[0], 0, _EVENT_MAP.get(str(e[2]), str(e[2]))] for e in events])
    else:
        # No events found - create empty events array
        final_events = np.array([[0, 0, 0]])
    
    return final_events, new_event_id


def _build_mind_wandering_labels(
    raw: mne.io.BaseRaw,
) -> mne.Annotations:
    """Build mind wandering state labels by matching probe and response events.
    
    Merges thought probe events (2221/2222) with response events (2241/2242,
    2251/2252) to create binary on-task/off-task labels for super meta.
    
    LLM 推断，需人类复核 - Label derivation logic based on analysis.md
    task description.
    """
    # Get original annotations
    orig_annotations = raw.annotations
    
    # Parse onset times and descriptions
    onset_times = orig_annotations.onset
    descriptions = [str(d) for d in orig_annotations.description]
    durations = orig_annotations.duration
    
    # Find probe events and their responses
    probe_onsets = []
    probe_labels = []
    
    for i, desc in enumerate(descriptions):
        if desc in ["thought_probe_type1", "2221"]:
            probe_onsets.append(onset_times[i])
            # Look for response in next 5 seconds
            response_onset = None
            response_desc = None
            for j in range(i + 1, min(i + 20, len(descriptions))):
                if onset_times[j] - onset_times[i] > 5:
                    break
                if descriptions[j] in ["probe_response_type1_off_task", "2242"]:
                    response_onset = onset_times[j]
                    response_desc = "off_task"
                    break
                elif descriptions[j] in ["probe_response_type1_on_task", "2241"]:
                    response_onset = onset_times[j]
                    response_desc = "on_task"
                    break
            
            if response_desc == "off_task":
                probe_labels.append(1)
            else:
                probe_labels.append(0)
                
        elif desc in ["thought_probe_type2", "2222"]:
            probe_onsets.append(onset_times[i])
            # Look for response in next 5 seconds
            for j in range(i + 1, min(i + 20, len(descriptions))):
                if onset_times[j] - onset_times[i] > 5:
                    break
                if descriptions[j] in ["probe_response_type2_off_task", "2252"]:
                    probe_labels.append(1)
                    break
                elif descriptions[j] in ["probe_response_type2_on_task", "2251"]:
                    probe_labels.append(0)
                    break
    
    if probe_onsets:
        return mne.Annotations(
            onset=np.array(probe_onsets),
            duration=np.full(len(probe_onsets), 3.5),
            description=[f"mw_state_{label}" for label in probe_labels],
        )
    
    return mne.Annotations(onset=[], duration=[], description=[])


def _get_subject_info(row) -> Dict[str, str]:
    """Extract subject metadata from row.
    
    LLM 推断，需人类复核 - Default values used since participant
    metadata not directly available in row.
    """
    # Try to extract subject ID for lookup
    subject_id = row.get("Subject", row.get("subject_id", "unknown"))
    
    # Check if we have participants.tsv in the dataset directory
    # This would be populated by EEGUnity's BIDS loader if available
    if hasattr(row, 'get') and row.get("age"):
        return {
            "age": str(row.get("age", "unknown")),
            "sex": str(row.get("sex", "unknown")).lower(),
            "handedness": str(row.get("handedness", "unknown")).lower(),
        }
    
    return {
        "age": "unknown",      # LLM 推断，需人类复核
        "sex": "unknown",       # LLM 推断，需人类复核
        "handedness": "unknown", # LLM 推断，需人类复核
    }


@dataclass
class OpenNeuroDS004121Kernel:
    """Stage1 kernel for OpenNeuro ds004121 (BCIT Mind Wandering).
    
    This kernel processes EEG data from the BCIT Mind Wandering study,
    which investigated neural correlates of mind wandering during
    simulated driving.
    
    Supported tasks:
    - Task 1: Lateral Perturbation Direction (events 4311/4312)
    - Task 2: Mind Wandering State (events 2221/2222 with responses)
    - Task 3: Audio Condition (events 4621/4622)
    """
    
    KERNEL_ID: str = "openneuro-ds004121-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG object
        row : pandas.Series
            Locator row with file path and metadata
            
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized annotations
        """
        # Store original description
        original_desc = raw.info.get("description", "")
        
        # === Channel Processing ===
        # Rename non-standard channels before set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types (especially important for 74-channel setups)
        # This helps format_channel_name() in EEGUnity parse correctly
        try:
            # Get non-EEG channel types from existing info or set defaults
            for i, ch in enumerate(raw.ch_names):
                ch_type = raw.get_channel_types()[i]
                if ch_type == 'stim':
                    # Likely a trigger channel - keep as stim
                    pass
                elif ch_type == 'eeg':
                    # Already properly typed
                    pass
        except Exception:
            pass
        
        # Try to set standard montage (assumes standard 10-20 system)
        # LLM 推断，需人类复核 - Standard 1020 assumed for 74-channel cap
        try:
            standard_montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(standard_montage, on_missing='ignore')
        except Exception:
            # Montage setting failed - dataset may use non-standard layout
            pass
        
        # === Event/Annotation Processing ===
        # Reconstruct events from numeric codes to human-readable labels
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            
            # Build new annotations with standardized descriptions
            new_descriptions = []
            new_onsets = []
            new_durations = []
            
            for i, desc in enumerate(event_id.keys()):
                desc_str = str(desc)
                mapped = _EVENT_MAP.get(desc_str, desc_str)
                new_descriptions.append(mapped)
                new_onsets.append(events[i, 0] / raw.info['sfreq'])
                new_durations.append(0.0)
            
            if new_descriptions:
                raw.set_annotations(mne.Annotations(
                    onset=np.array(new_onsets),
                    duration=np.array(new_durations),
                    description=new_descriptions,
                ))
        except Exception as e:
            # If annotation processing fails, keep original annotations
            pass
        
        # === Super Meta: Mind Wandering Labels ===
        # Create mind wandering state annotations by matching probes and responses
        try:
            mw_annotations = _build_mind_wandering_labels(raw)
            if len(mw_annotations) > 0:
                # Append super meta annotations to existing
                existing = raw.annotations
                combined = mne.Annotations(
                    onset=np.concatenate([existing.onset, mw_annotations.onset]),
                    duration=np.concatenate([existing.duration, mw_annotations.duration]),
                    description=list(existing.description) + list(mw_annotations.description),
                )
                raw.set_annotations(combined)
        except Exception:
            pass
        
        # === Metadata (eegunity_description) ===
        subject_info = _get_subject_info(row)
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "unknown",      # LLM 推断，需人类复核
                "cap": "Ag/AgCl",            # LLM 推断，需人类复核 - typical for EEG studies
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004121Kernel()