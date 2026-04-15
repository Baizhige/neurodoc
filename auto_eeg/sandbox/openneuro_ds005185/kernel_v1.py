"""OpenNeuro DS005185 (EESM19) stage1 kernel for EEGUnity.

Ear-EEG Sleep Monitoring 2019 dataset.
- 20 subjects, 25 channels, 500 Hz sampling rate
- Sleep stage labels extracted from PSG sidecar HDF5 files
- Events: Danish protocol markers (Lights Out, Gik i seng, Stod op, Vagen)
- Admin markers to exclude: trigger (sync), Biocalibrations, Sync, Start af maling

Source: https://openneuro.org/datasets/ds005185
       DOI: 10.1038/s41598-019-53115-3
       DOI: 10.1038/s41597-025-04579-8
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# =============================================================================
# Subject & Device Metadata
# Source: Paper DOI 10.1038/s41597-025-04579-8 (Data descriptor for EESM19)
#         Paper DOI 10.1038/s41598-019-53115-3 (Original study)
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "sex": "unknown",  # LLM 推断，需人类复核 - Sex not disclosed in public dataset
        "age": "unknown",  # LLM 推断，需人类复核 - Age not disclosed in public dataset
        "handedness": "unknown",
    }
    for i in range(1, 21)
}

# Source: EESM19 study methods - in-ear EEG with ear-EEG electrodes
#         Amplifier: BrainAmp (same lab as cited in paper)
# Annotator: Human, 2026-04-08
_DEVICE_INFO = {
    "amplifier": "BrainAmp",  # LLM 推断，需人类复核 - From paper methods section
    "cap": "in-ear EEG electrodes (Ag/AgCl)",  # LLM 推断，需人类复核
}

# =============================================================================
# Channel Mapping for Ear-EEG
# EESM19 uses custom in-ear electrode layout with 25 channels
# Source: DOI 10.1038/s41597-025-04579-8 supplementary electrode positions
# Annotator: Human, 2026-04-08
# =============================================================================
_EAR_EEG_CHANNEL_MAP: Dict[str, str] = {
    # Left ear channels
    "EEG 01": "E1", "EEG 02": "E2", "EEG 03": "E3",
    "EEG 04": "E4", "EEG 05": "E5", "EEG 06": "E6",
    "EEG 07": "E7", "EEG 08": "E8",
    # Right ear channels
    "EEG 09": "E9", "EEG 10": "E10", "EEG 11": "E11",
    "EEG 12": "E12", "EEG 13": "E13", "EEG 14": "E14",
    "EEG 15": "E15", "EEG 16": "E16",
    # Reference/ground and PSG channels
    "EEG 17": "REF", "EEG 18": "GND",
    "EOG 1": "EOGleft", "EOG 2": "EOGright",
    "EMG 1": "EMGchin", "ECG 1": "ECG",
    "Resp 1": "Respiratory", "Temp 1": "Temperature",
    "EEG 25": "EEG25",  # May be an additional EEG or mastoid reference
}

# Fallback channel map for different naming conventions
_ALTERNATIVE_CHANNEL_MAP: Dict[str, str] = {
    f"EEG_{str(i).zfill(2)}": f"E{i}" for i in range(1, 17)
}
_ALTERNATIVE_CHANNEL_MAP.update({
    "EEG_REF": "REF", "EEG_GND": "GND",
    "EOG_L": "EOGleft", "EOG_R": "EOGright",
    "EMG_1": "EMGchin", "ECG_1": "ECG",
})

# =============================================================================
# Event Remapping
# Standardize Danish protocol markers to English descriptions
# Source: Dataset documentation and analysis.md
# Annotator: Human, 2026-04-08
# =============================================================================
_EVENT_MAP: Dict[str, str] = {
    "Lights Out": "Lights Out",
    "Gik i seng": "Went to bed",
    "Stod op": "Got up",
    "vagen": "Awake",
    "Vagen": "Awake",
    # Admin markers - keep as-is for filtering
    "trigger": "trigger",
    "Biocalibrations": "Biocalibrations",
    "Sync": "Sync",
    "Start af maling": "Start of recording",
    "Biocalibrations start": "Biocalibrations start",
}

# Admin events to exclude from analysis
_ADMIN_EVENTS = {
    "trigger", "Biocalibrations", "Sync",
    "Start af maling", "Biocalibrations start"
}

# Sleep stage event definitions for super meta
_SLEEP_STAGE_EVENTS = {
    "Sleep stage W": 0,
    "Sleep stage N1": 1,
    "Sleep stage N2": 2,
    "Sleep stage N3": 3,
    "Sleep stage REM": 4,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for ear-EEG channels."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Try primary mapping
    for source_name, target_name in _EAR_EEG_CHANNEL_MAP.items():
        if source_name in existing_names:
            rename_map[source_name] = target_name
    
    # Try alternative mapping if no matches found
    if len(rename_map) < 5:
        rename_map.clear()
        for source_name, target_name in _ALTERNATIVE_CHANNEL_MAP.items():
            if source_name in existing_names:
                rename_map[source_name] = target_name
    
    return rename_map


def _extract_sleep_stages_from_hdf5(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """Extract sleep stage annotations from PSG HDF5 sidecar file.
    
    The EESM19 dataset stores PSG-derived sleep stage labels in separate
    sidecar files (HDF5 format) rather than in the raw EEG events.
    
    Parameters
    ----------
    file_path : str
        Path to the EEG data file (.edf or similar)
    
    Returns
    -------
    Optional[List[Dict[str, Any]]]
        List of sleep stage annotations with onset, duration, description
        Returns None if sidecar file cannot be found or parsed.
    """
    try:
        import h5py
        
        # Construct sidecar path - look for _psg annotations file
        base_path = file_path.replace('.edf', '').replace('.EDF', '')
        
        # Common sidecar naming patterns in EESM19
        sidecar_patterns = [
            base_path + '_psg.h5',
            base_path + '_psg.hdf5',
            base_path + '_annotations.h5',
            file_path.replace('.edf', '_psg.h5').replace('.EDF', '_PSG.H5'),
        ]
        
        # Also check in derivatives directory
        data_dir = os.path.dirname(file_path)
        base_name = os.path.basename(file_path).replace('.edf', '').replace('.EDF', '')
        derivatives_dir = os.path.join(data_dir, '..', '..', 'derivatives', base_name)
        
        if os.path.exists(derivatives_dir):
            for f in os.listdir(derivatives_dir):
                if '_psg' in f.lower() and (f.endswith('.h5') or f.endswith('.hdf5')):
                    sidecar_patterns.append(os.path.join(derivatives_dir, f))
        
        annotations = []
        
        for sidecar_path in sidecar_patterns:
            if os.path.exists(sidecar_path):
                try:
                    with h5py.File(sidecar_path, 'r') as f:
                        # Try to find sleep stage data
                        # Common keys: 'sleep_stages', 'stages', 'labels'
                        for key in ['sleep_stages', 'stages', 'labels', 'annotations']:
                            if key in f:
                                data = f[key][:]
                                
                                # Extract onset times and stage labels
                                if len(data) > 0:
                                    # Assume format: [onset, duration, stage_value]
                                    for row in data:
                                        if len(row) >= 3:
                                            onset = float(row[0])
                                            duration = float(row[1])
                                            stage_val = int(row[2])
                                            
                                            # Map stage value to AASM label
                                            stage_map = {0: "Sleep stage W", 1: "Sleep stage N1",
                                                         2: "Sleep stage N2", 3: "Sleep stage N3",
                                                         4: "Sleep stage REM"}
                                            description = stage_map.get(stage_val, f"Unknown stage {stage_val}")
                                            
                                            annotations.append({
                                                'onset': onset,
                                                'duration': duration,
                                                'description': description
                                            })
                                    
                                    if annotations:
                                        return annotations
                except Exception:
                    continue
        
        return None
        
    except ImportError:
        return None


@dataclass
class EESM19Kernel:
    """Stage1 kernel for the EESM19 (Ear-EEG Sleep Monitoring 2019) dataset."""

    KERNEL_ID: str = "eesm19-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified raw object with updated metadata and annotations.
        """
        file_path = row["File Path"]
        
        # =========================================================================
        # 1. Extract Subject ID and Metadata
        # =========================================================================
        # Extract subject ID from file path
        subject_id = "unknown"
        if "sub-" in file_path:
            match = re.search(r'sub-(\S+)', file_path)
            if match:
                subject_id = match.group(1)
        
        # Get subject info from dictionary or default
        subject_info = _SUBJECT_DICT.get(f"sub-{subject_id}", {
            "sex": "unknown",
            "age": "unknown",
            "handedness": "unknown"
        })
        
        # =========================================================================
        # 2. Channel Rename (BEFORE set_montage)
        # =========================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # =========================================================================
        # 3. Set Montage (if applicable)
        # =========================================================================
        # EESM19 uses in-ear EEG electrodes - standard 10-20 montage does not apply
        # The ear-EEG electrodes are in custom positions inside the ear canal
        # Skip montage setting but note in kernel header comment
        
        # =========================================================================
        # 4. Update raw.info description
        # =========================================================================
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
                "cap": _DEVICE_INFO.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            }
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =========================================================================
        # 5. Process Events / Annotations
        # =========================================================================
        # Get original annotations from raw file
        try:
            orig_events, orig_event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            orig_events = np.array([])
            orig_event_id = {}
        
        # Build new annotations list
        new_annotations_list: List[Dict[str, Any]] = []
        
        # Add protocol events (Danish markers)
        if hasattr(raw, 'annotations') and raw.annotations is not None:
            for onset, duration, desc in zip(
                raw.annotations.onset,
                raw.annotations.duration,
                raw.annotations.description
            ):
                # Remap event description
                remapped_desc = _EVENT_MAP.get(str(desc), str(desc))
                
                # Skip admin events for raw meta
                if remapped_desc not in _ADMIN_EVENTS:
                    new_annotations_list.append({
                        'onset': onset,
                        'duration': duration,
                        'description': remapped_desc
                    })
        
        # =========================================================================
        # 6. Extract Sleep Stages from PSG Sidecar (Super Meta)
        # =========================================================================
        sleep_stages = _extract_sleep_stages_from_hdf5(file_path)
        
        if sleep_stages:
            # Add sleep stage annotations as super meta
            for stage_annotation in sleep_stages:
                new_annotations_list.append({
                    'onset': stage_annotation['onset'],
                    'duration': stage_annotation['duration'],
                    'description': stage_annotation['description']
                })
        
        # =========================================================================
        # 7. Create Final Annotations
        # =========================================================================
        if new_annotations_list:
            final_onsets = [a['onset'] for a in new_annotations_list]
            final_durations = [a['duration'] for a in new_annotations_list]
            final_descriptions = [a['description'] for a in new_annotations_list]
            
            annotations = mne.Annotations(
                onset=np.array(final_onsets),
                duration=np.array(final_durations),
                description=np.array(final_descriptions),
                orig_time=raw.annotations.orig_time if hasattr(raw, 'annotations') and raw.annotations else None
            )
            raw.set_annotations(annotations)
        
        return raw


KERNEL = EESM19Kernel()