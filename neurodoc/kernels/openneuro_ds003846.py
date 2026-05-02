"""openneuro_ds003846 stage1 kernel for EEGUnity.

Virtual reality haptic interaction study - prediction error detection task.
Participants reached out to touch virtual boxes with visual/vibrotactile/EMS feedback.
Normal (congruent) vs Conflict (incongruent/prediction error) classification.

Source: https://openneuro.org/datasets/ds003846
DOI: 10.3389/fnrgo.2024.1411305
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Device metadata - source: paper DOI 10.3389/fnrgo.2024.1411305
# Exact amplifier and cap type not specified in available documentation
# inferred by LLM, needs human review
_DEVICE_AMPLIFIER: str = "unknown"
_DEVICE_CAP: str = "unknown"  # 64-channel setup, exact type not specified

# Required info fields from participants.tsv per kernel requirements
_REQUIRED_INFO_FIELDS: List[str] = ["age", "block_1", "cap_size"]

# Required event IDs that must appear in scan
_REQUIRED_EVENT_IDS: List[str] = ["box:touched"]


@dataclass
class OpenneuroDs003846Kernel:
    """Stage1 kernel for the openneuro_ds003846 dataset."""

    KERNEL_ID: str = "openneuro-ds003846-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        raw = self._standardize_channels(raw)
        raw = self._set_montage_if_possible(raw)
        raw = self._process_events(raw, file_path)
        subject_id = self._extract_subject_id(file_path)
        original_description = raw.info.get("description", "") or ""
        eegunity_description: Dict[str, str] = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": _DEVICE_AMPLIFIER,
            "cap": _DEVICE_CAP,
            "handedness": "unknown",
        }
        participants_data = self._read_participants_tsv(file_path, udataset)
        if participants_data and subject_id in participants_data:
            subj_data = participants_data[subject_id]
            age_val = subj_data.get("age")
            if age_val is not None and str(age_val).strip():
                eegunity_description["age"] = str(int(float(age_val))) if self._is_number(age_val) else str(age_val).strip()
            sex_val = subj_data.get("sex") or subj_data.get("gender")
            if sex_val is not None and str(sex_val).strip():
                eegunity_description["sex"] = str(sex_val).strip().lower()
            handedness_val = subj_data.get("handedness")
            if handedness_val is not None and str(handedness_val).strip():
                eegunity_description["handedness"] = str(handedness_val).strip().lower()
            for field in _REQUIRED_INFO_FIELDS:
                val = subj_data.get(field)
                if val is not None:
                    eegunity_description[field] = str(val)
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        raw = self._add_derived_misc_channels(raw, participants_data, subject_id)
        return raw

    def _standardize_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename non-standard channel names to standard 10-20 names.

        BIDS datasets may have channels named with BIDS conventions or
        numbered channels. Map to standard 10-20 names for 64-channel setup.

        Source: Standard 10-20 64-channel layout
        # inferred by LLM, needs human review - exact mapping requires dataset documentation verification.
        """
        rename_map: Dict[str, str] = {}

        # Check for common non-standard patterns
        ch_names = raw.ch_names

        # Pattern 1: EEG-0, EEG-1, ... (common in BIDS exports)
        numbered_pattern = re.compile(r'^EEG-(\d+)$')
        # Pattern 2: eeg_0, eeg_1, ...
        underscore_pattern = re.compile(r'^eeg_(\d+)$')

        # Standard 10-20 64-channel layout ordered list
        # Based on extended 10-20 system with 64 electrodes
        standard_64 = [
            "Fp1", "Fpz", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
            "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
            "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
            "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
            "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
            "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
            "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
            "Iz"
        ]

        # Build rename map for numbered channels
        for ch_name in ch_names:
            match = numbered_pattern.match(ch_name)
            if not match:
                match = underscore_pattern.match(ch_name)

            if match:
                idx = int(match.group(1))
                if idx < len(standard_64):
                    rename_map[ch_name] = standard_64[idx]

        # Also handle common BIDS channel naming variations
        bids_renames = {
            "M1": "TP9",
            "M2": "TP10",
            "A1": "TP9",
            "A2": "TP10",
            "HEOG": "HEOG",
            "VEOG": "VEOG",
            "EOGH": "HEOG",
            "EOGV": "VEOG",
        }

        for ch_name in ch_names:
            if ch_name in bids_renames and ch_name not in rename_map:
                # Only rename if target doesn't already exist
                target = bids_renames[ch_name]
                if target not in ch_names or target == ch_name:
                    rename_map[ch_name] = target

        if rename_map:
            raw = raw.rename_channels(rename_map)

        return raw

    def _set_montage_if_possible(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage if channels match standard layout.

        Source: standard_1020 montage from MNE
        # inferred by LLM, needs human review
        """
        try:
            # Check if we have mostly standard 10-20 channel names
            standard_channels = set([
                "Fp1", "Fpz", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
                "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
                "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
                "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
                "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
                "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
                "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
                "Iz", "A1", "A2", "M1", "M2", "HEOG", "VEOG", "ECG"
            ])

            current_channels = set(raw.ch_names)
            eeg_channels = [ch for ch in raw.ch_names if raw.get_channel_types(picks=[ch])[0] == 'eeg']

            # If most EEG channels are standard 10-20, set montage
            standard_eeg = [ch for ch in eeg_channels if ch in standard_channels]
            if len(standard_eeg) >= 32:  # At least half of 64 are standard
                montage = mne.channels.make_standard_montage("standard_1020")
                # Only set montage for channels that exist in both
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # Fail silently if montage can't be set
            pass

        return raw

    def _process_events(self, raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
        """Process annotations and events for this dataset.

        BrainVision .eeg files may not carry markers without their .vmrk file.
        Events MUST come from events.tsv sidecar — use mne.Annotations keyed on
        the onset/duration/type (or value) columns.
        """
        # Try to find events.tsv sidecar
        events_tsv = self._find_events_tsv(file_path)
        
        if events_tsv and os.path.exists(events_tsv):
            # Read events from TSV
            events_df = pd.read_csv(events_tsv, sep='\t')
            
            # Build annotations from events.tsv
            onsets = []
            durations = []
            descriptions = []
            
            for _, event_row in events_df.iterrows():
                onset = float(event_row.get('onset', 0))
                duration = float(event_row.get('duration', 0))
                # Use 'type' column first (contains the actual event type like 'box:touched')
                # Fall back to 'value' or 'trial_type' if 'type' is not available
                event_type = str(event_row.get('type', event_row.get('value', event_row.get('trial_type', 'unknown'))))
                
                onsets.append(onset)
                durations.append(duration)
                descriptions.append(event_type)
            
            # Create annotations and add to raw
            if onsets:
                annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annotations)
        
        return raw

    def _find_events_tsv(self, file_path: str) -> Optional[str]:
        """Find the corresponding events.tsv file for a given data file."""
        # BIDS convention: events.tsv is in the same directory as the eeg file
        # or in the subject's func/eeg directory
        base = os.path.splitext(file_path)[0]
        # Try common BIDS patterns
        candidates = [
            base + '_events.tsv',
            base.replace('_eeg', '_events') + '.tsv',
            os.path.join(os.path.dirname(file_path), 'events.tsv'),
        ]
        
        # Also look for task-specific events
        dir_name = os.path.dirname(file_path)
        if os.path.isdir(dir_name):
            for f in os.listdir(dir_name):
                if f.endswith('_events.tsv'):
                    candidates.append(os.path.join(dir_name, f))
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        
        return None

    def _extract_subject_id(self, file_path: str) -> str:
        """Extract subject ID from file path using BIDS conventions."""
        # Match sub-XX pattern
        match = re.search(r'(sub-[a-zA-Z0-9]+)', file_path)
        if match:
            return match.group(1)
        return "unknown"

    def _read_participants_tsv(self, file_path: str, udataset) -> Optional[Dict[str, Dict[str, Any]]]:
        """Read participants.tsv and return dict keyed by subject_id."""
        # Search for participants.tsv in dataset root
        dataset_root = self._find_dataset_root(file_path, udataset)
        if not dataset_root:
            return None

        participants_path = os.path.join(dataset_root, "participants.tsv")
        if not os.path.exists(participants_path):
            return None

        try:
            df = pd.read_csv(participants_path, sep='\t')
            result = {}
            for _, row in df.iterrows():
                participant_id = str(row.get('participant_id', '')).strip()
                if participant_id:
                    result[participant_id] = row.to_dict()
            return result
        except Exception:
            return None

    def _find_dataset_root(self, file_path: str, udataset) -> Optional[str]:
        """Find the BIDS dataset root directory."""
        # Try to get from udataset
        if hasattr(udataset, 'root_dir') and udataset.root_dir:
            return udataset.root_dir

        # Walk up from file path looking for dataset_description.json
        current_dir = os.path.dirname(file_path)
        while current_dir and current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, "dataset_description.json")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        # Fallback: use file's parent directory
        return os.path.dirname(file_path) if os.path.exists(os.path.dirname(file_path)) else None

    def _is_number(self, value: Any) -> bool:
        """Check if value can be converted to a number."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def _add_derived_misc_channels(self, raw: mne.io.BaseRaw, participants_data: Optional[Dict], subject_id: str) -> mne.io.BaseRaw:
        """Add derived miscellaneous channels from participant metadata."""
        # No additional channels needed for this dataset
        return raw


KERNEL = OpenneuroDs003846Kernel()