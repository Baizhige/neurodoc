"""Dataset-specific kernel for openneuro_ds003517.

EEG: Continuous Gameplay of an 8-Bit Style Video Game
Source: https://openneuro.org/datasets/ds003517

Paradigm: Participants played a continuous 8-bit style video game while EEG 
was recorded. The experiment included visual oddball task and gambling task 
embedded within the session.

Event Structure:
- Oddball: ODDBALL STANDARD (S 20), ODDBALL RARE (S 29)
- Game events: SHOOT_BUTTON (S 90), COLLECT_STAR (S 91), COLLECT_AMMO (S 92),
  PLAYER_CRASH_WALL (S 94), PLAYER_CRASH_ENEMY (S 97), MISSILE_HIT_ENEMY (S 98)
- Gambling: GAMBLING LOSS (S 50), GAMBLING WIN (S 51)
- Markers: GAME START, GAME OVER, ODDBALL START, ODDBALL DONE, STATUS
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Event code mapping from numeric to semantic labels
# Source: Dataset documentation / analysis.md event structure
_EVENT_CODE_MAP: Dict[int, str] = {
    20: "ODDBALL STANDARD",
    29: "ODDBALL RARE",
    50: "GAMBLING LOSS",
    51: "GAMBLING WIN",
    90: "SHOOT_BUTTON",
    91: "COLLECT_STAR",
    92: "COLLECT_AMMO",
    94: "PLAYER_CRASH_WALL",
    97: "PLAYER_CRASH_ENEMY",
    98: "MISSILE_HIT_ENEMY",
}

# Admin/event markers (no semantic meaning, used for timing/segmentation)
_ADMIN_CODE_MAP: Dict[int, str] = {
    1: "GAME START",
    2: "GAME OVER",
    3: "ODDBALL START",
    4: "ODDBALL DONE",
    91: "admin: marker-91",
    92: "admin: marker-92",
    99: "admin: marker-99",
}

# Combined event map for MNE
_COMBINED_EVENT_MAP: Dict[str, int] = {v: k for k, v in _EVENT_CODE_MAP.items()}
_COMBINED_EVENT_MAP.update({v: k for k, v in _ADMIN_CODE_MAP.items()})

# Subject metadata (if available from participants.tsv or dataset)
# Source: LLM 推断，需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Channel mapping if needed (standard 1020 system, 64 EEG + 1 reference)
# Source: Dataset documentation indicates standard electrode cap
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC5", "FC1", "FC2", "FC6",
    "C5", "C1", "C2", "C6",
    "CP5", "CP1", "CP2", "CP6",
    "P5", "P1", "P2", "P6",
    "PO7", "PO3", "PO4", "PO8",
    "FT7", "FT8",
    "TP7", "TP8",
    "POz",
    "Fpz", "AFz", "Fz", "Cz", "Pz", "Oz",
]


def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from file path (if multi-paradigm dataset)."""
    basename = os.path.basename(file_path)
    return ""  # Single paradigm for this dataset


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 1020."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common BIDS channel naming patterns
    patterns = [
        (r"EEG\s*([A-Z]\d+)", r"\1"),
        (r"eeg\s*([A-Z]\d+)", r"\1"),
        (r"([A-Z][a-z])(\d+)", r"\1\2"),
    ]
    
    for ch in existing:
        for pattern, repl in patterns:
            match = re.match(pattern, ch)
            if match:
                standardized = re.sub(pattern, repl, ch)
                if standardized in _STANDARD_1020_CHANNELS and ch != standardized:
                    rename_map[ch] = standardized
                    break
    
    return rename_map


def _load_participants_tsv(dataset_root: str) -> Dict[str, Dict[str, str]]:
    """Load participant metadata from BIDS participants.tsv if available."""
    participants_file = os.path.join(dataset_root, "participants.tsv")
    subject_data = {}
    
    if os.path.exists(participants_file):
        try:
            import pandas as pd
            df = pd.read_csv(participants_file, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).replace("sub-", "")
                subject_data[subj_id] = {
                    "age": str(row.get("age", "unknown")),
                    "sex": str(row.get("sex", "unknown")).lower(),
                }
        except Exception:
            pass
    
    return subject_data


def _extract_subject_id(row) -> str:
    """Extract subject ID from row."""
    if hasattr(row, "get"):
        file_path = row.get("File Path", str(row.get("file_path", "")))
        subject_id = row.get("Subject", row.get("subject_id", ""))
    else:
        file_path = str(row.get("File Path", row.get("file_path", "")))
        subject_id = str(row.get("Subject", row.get("subject_id", "")))
    
    # Try to extract from file path
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1)
    
    match = re.search(r"sub-([A-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    
    return subject_id if subject_id else "unknown"


def _get_subject_metadata(subject_id: str, dataset_root: str) -> Dict[str, str]:
    """Get subject metadata from various sources."""
    # Try participants.tsv first
    participants = _load_participants_tsv(dataset_root)
    if subject_id in participants:
        return participants[subject_id]
    
    # LLM 推断，需人类复核
    return {
        "age": "unknown",
        "sex": "unknown",
    }


class OpenNeuroDS003517Kernel:
    """Stage1 kernel for openneuro_ds003517 dataset.
    
    EEG recording during continuous 8-bit video game gameplay with embedded
    oddball and gambling tasks.
    """

    KERNEL_ID: str = "openneuro-ds003517-stage1"
    HANDLES_UNAVAILABLE: bool = False

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to raw EEG data.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object
        row : pandas.Series
            Locator row with file path and metadata
            
        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with updated metadata and annotations
        """
        # Get dataset root for accessing sidecar files
        dataset_root = getattr(udataset, "root", "")
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(row.get("File Path", ""))
        
        # Extract subject ID
        subject_id = _extract_subject_id(row)
        
        # Get subject metadata
        subject_meta = _get_subject_metadata(subject_id, dataset_root)
        
        # Store original description
        original_description = raw.info.get("description", "")
        
        # Update description with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_meta.get("age", "unknown"),
                "sex": subject_meta.get("sex", "unknown").lower() if subject_meta.get("sex") else "unknown",
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            }
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels to standard names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Channel rename BEFORE set_montage()
            mne.rename_channels(raw.info, rename_map)
        
        # Try to set standard montage if channels are standard 1020
        try:
            # Check if we have enough standard channels
            standard_chs = [ch for ch in raw.ch_names if ch in _STANDARD_1020_CHANNELS]
            if len(standard_chs) >= 20:  # Enough channels to assume standard 1020
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage setting is best-effort
        
        # Process events/annotations from STIM channels or existing annotations
        self._process_events(raw)
        
        return raw

    def _process_events(self, raw: mne.io.BaseRaw) -> None:
        """Process and remap events in the raw data.
        
        Handles:
        1. Numeric event codes from STIM channels
        2. Existing annotations with numeric descriptions
        3. Mapping to semantic event labels
        """
        # Get existing annotations
        annotations = raw.annotations
        
        if len(annotations) > 0:
            # Process existing annotations
            new_descriptions = []
            for desc in annotations.description:
                desc_str = str(desc)
                
                # Check if description is a numeric code
                try:
                    code = int(float(desc_str))
                    if code in _EVENT_CODE_MAP:
                        new_descriptions.append(_EVENT_CODE_MAP[code])
                    elif code in _ADMIN_CODE_MAP:
                        new_descriptions.append(_ADMIN_CODE_MAP[code])
                    else:
                        new_descriptions.append(desc_str)
                except (ValueError, TypeError):
                    # Description is already a string
                    new_descriptions.append(desc_str)
            
            # Update annotations with remapped descriptions
            new_annotations = mne.Annotations(
                onset=annotations.onset,
                duration=annotations.duration,
                description=new_descriptions,
                orig_time=annotations.orig_time,
            )
            raw.set_annotations(new_annotations)
        
        # Also check for events array if available
        # Some BIDS datasets store events in the stim channel
        stim_channels = [ch for ch in raw.ch_names 
                         if raw.get_channel_types(picks=[ch])[0] in ['stim', 'stim', 'trig']]
        
        if stim_channels:
            # Read events from stim channel
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            
            # Remap event codes
            remapped_events = events.copy()
            for old_desc, old_id in event_id.items():
                try:
                    code = int(float(old_desc))
                    if code in _EVENT_CODE_MAP:
                        # Find and update matching events
                        mask = remapped_events[:, 2] == old_id
                        remapped_events[mask, 2] = _COMBINED_EVENT_MAP[_EVENT_CODE_MAP[code]]
                    elif code in _ADMIN_CODE_MAP:
                        mask = remapped_events[:, 2] == old_id
                        remapped_events[mask, 2] = _COMBINED_EVENT_MAP[_ADMIN_CODE_MAP[code]]
                except (ValueError, TypeError):
                    pass
            
            # Create new annotations from remapped events
            new_annotations = mne.Annotations(
                onset=remapped_events[:, 0] / raw.info['sfreq'],
                duration=np.zeros(len(remapped_events)),
                description=[str(e[2]) for e in remapped_events],
            )
            raw.set_annotations(new_annotations)


# Module-level kernel instance
KERNEL = OpenNeuroDS003517Kernel()