"""OpenNeuro DS005403 Delayed Auditory Feedback EEG/EGG stage1 kernel for EEGUnity.

Dataset: Delayed Auditory Feedback EEG/EGG
Source: https://openneuro.org/datasets/ds005403
Paradigm: Speech production with DAF (Delayed Auditory Feedback)
Channels: EEG + EGG (electroglottography)
Sampling Rate: 1000 Hz
Subjects: 66

Event Structure:
- baseline: Baseline (no delay) speech block
- adaption: Adaptation DAF condition block
- random1: Random delay condition 1 block
- random2: Random delay condition 2 block

Source: DOI 10.1523/jneurosci.2294.24.2025
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Event mapping: raw numeric codes to canonical event names
# Source: OpenNeuro dataset event documentation
_EVENT_NUMERIC_MAP: Dict[int, str] = {
    1: "baseline",
    2: "adaption",
    3: "random1",
    4: "random2",
}

# Canonical event ID for consistent labeling
CANONICAL_EVENT_ID: Dict[str, int] = {
    "baseline": 1,
    "adaption": 2,
    "random1": 3,
    "random2": 4,
}


@dataclass
class OpenNeuroDS005403Kernel:
    """Stage1 kernel for OpenNeuro DS005403 (Delayed Auditory Feedback EEG/EGG)."""

    KERNEL_ID: str = "openneuro-ds005403-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path`` and ``Subject ID``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed MNE Raw object.
        """
        file_path = row["File Path"]
        subject_id = row.get("Subject ID", "")

        # Load participant info from participants.tsv
        dataset_root = self._get_dataset_root(file_path)
        subject_info = self._load_participant_info(dataset_root, subject_id)

        # Update description with metadata
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp" if subject_info.get("amplifier") == "unknown" else subject_info.get("amplifier", "unknown"),
                "cap": "Ag/AgCl" if subject_info.get("cap") == "unknown" else subject_info.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names
        raw = self._rename_channels(raw)

        # Set montage if standard 1020
        raw = self._set_montage(raw)

        # Map events to canonical names
        raw = self._map_events(raw)

        return raw

    def _get_dataset_root(self, file_path: str) -> str:
        """Get dataset root by traversing up directories."""
        current = os.path.dirname(file_path)
        while current and current != os.path.dirname(current):
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return os.path.dirname(file_path)

    def _load_participant_info(self, dataset_root: str, subject_id: str) -> Dict[str, str]:
        """Load participant info from participants.tsv if available.
        
        Returns a dict with keys: age, sex, amplifier, cap, handedness.
        All values are strings, unknown values are "unknown".
        
        Source: participants.tsv file (if exists), else defaults.
        Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
        """
        default_info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }

        participants_file = os.path.join(dataset_root, "participants.tsv")
        if not os.path.exists(participants_file):
            return default_info

        try:
            df = pd.read_csv(participants_file, sep="\t")
            # Normalize subject_id for matching (remove 'sub-' prefix if present)
            normalized_id = subject_id.replace("sub-", "") if subject_id else ""
            # Try matching both with and without prefix
            subject_row = df[
                (df["participant_id"] == subject_id) |
                (df["participant_id"] == normalized_id) |
                (df["participant_id"].str.replace("sub-", "", regex=False) == normalized_id)
            ]
            
            if subject_row.empty:
                return default_info

            info = default_info.copy()
            row = subject_row.iloc[0]

            # Age
            if "age" in df.columns:
                age_val = row.get("age")
                if pd.notna(age_val):
                    info["age"] = str(int(age_val)) if isinstance(age_val, (int, float)) else str(age_val)

            # Sex
            if "sex" in df.columns or "gender" in df.columns:
                sex_col = "sex" if "sex" in df.columns else "gender"
                sex_val = row.get(sex_col)
                if pd.notna(sex_val):
                    sex_str = str(sex_val).strip().lower()
                    if sex_str in ["m", "male", "f", "female"]:
                        info["sex"] = "male" if sex_str in ["m", "male"] else "female"

            # Handedness
            if "handedness" in df.columns or "hand" in df.columns:
                hand_col = "handedness" if "handedness" in df.columns else "hand"
                hand_val = row.get(hand_col)
                if pd.notna(hand_val):
                    hand_str = str(hand_val).strip().lower()
                    if hand_str in ["r", "right", "right-handed"]:
                        info["handedness"] = "right"
                    elif hand_str in ["l", "left", "left-handed"]:
                        info["handedness"] = "left"

            return info

        except Exception:
            return default_info

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard names.
        
        EEG channels follow standard_1020 naming. EGG channels are preserved.
        
        Source: OpenNeuro dataset channel metadata
        Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
        """
        rename_map: Dict[str, str] = {}
        existing_names = set(raw.ch_names)

        # Identify EEG and EGG channels
        eeg_indices = []
        egg_indices = []
        misc_indices = []
        
        for i, ch_name in enumerate(raw.ch_names):
            ch_name_lower = ch_name.lower()
            
            # EGG channels (electroglottography)
            if "egg" in ch_name_lower or ch_name_lower == "egg":
                egg_indices.append(i)
            # Misc channels that might be audio or other
            elif raw.get_channel_types()[i] in ["misc", "stim"]:
                misc_indices.append(i)
            # EEG channels
            elif raw.get_channel_types()[i] == "eeg":
                eeg_indices.append(i)

        # Build rename map for EEG channels
        # Standard 1020 channels are expected:Fp1, Fp2, F3, F4, C3, C4, P3, P4, 
        # O1, O2, F7, F8, T7, T8, P7, P8, Fz, Cz, Pz, Oz, FC1, FC2, FC5, FC6,
        # CP1, CP2, CP5, CP6, FT7, FT8, TP7, TP8, AF7, AF8, etc.
        standard_eeg_patterns = {
            "fp1": "Fp1", "fp2": "Fp2", "f3": "F3", "f4": "F4",
            "c3": "C3", "c4": "C4", "p3": "P3", "p4": "P4",
            "o1": "O1", "o2": "O2", "f7": "F7", "f8": "F8",
            "t7": "T7", "t8": "T8", "p7": "P7", "p8": "P8",
            "fz": "Fz", "cz": "Cz", "pz": "Pz", "oz": "Oz",
            "fc1": "FC1", "fc2": "FC2", "fc5": "FC5", "fc6": "FC6",
            "cp1": "CP1", "cp2": "CP2", "cp5": "CP5", "cp6": "CP6",
            "ft7": "FT7", "ft8": "FT8", "tp7": "TP7", "tp8": "TP8",
            "af7": "AF7", "af8": "AF8", "af3": "AF3", "af4": "AF4",
            "f1": "F1", "f2": "F2", "f5": "F5", "f6": "F6",
            "c1": "C1", "c2": "C2", "c5": "C5", "c6": "C6",
            "p1": "P1", "p2": "P2", "p5": "P5", "p6": "P6",
            "afz": "AFz", "cpz": "CPz", "fcz": "FCz",
        }

        for ch_name in raw.ch_names:
            ch_name_lower = ch_name.lower()
            if ch_name_lower in standard_eeg_patterns:
                standard_name = standard_eeg_patterns[ch_name_lower]
                if ch_name != standard_name:
                    rename_map[ch_name] = standard_name
            elif ch_name.startswith("eeg-") or ch_name.startswith("EEG-"):
                # Handle numbered EEG channels
                pass  # Keep as-is if already in standard format

        if rename_map:
            raw.rename_channels(rename_map)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 1020 montage if all EEG channels are recognized.
        
        Source: OpenNeuro dataset standard_1020 cap assumption
        Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
        """
        try:
            # Check if we have standard channel names
            eeg_chs = [ch for ch in raw.ch_names if raw.get_channel_types()[raw.ch_names.index(ch)] == "eeg"]
            if len(eeg_chs) >= 16:  # Minimum for reasonable montage
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Skip montage if channels don't match standard_1020

        return raw

    def _map_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Map raw events to canonical event names.
        
        Events are stored as annotations or in stim channels.
        Maps numeric event codes to semantic labels.
        
        Source: OpenNeuro DS005403 event documentation
        Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
        """
        try:
            # Try to get events from annotations first
            annotations = raw.annotations
            if annotations is not None and len(annotations) > 0:
                new_descriptions = []
                for desc in annotations.description:
                    # Check if description is numeric
                    try:
                        event_code = int(desc)
                        if event_code in _EVENT_NUMERIC_MAP:
                            new_descriptions.append(_EVENT_NUMERIC_MAP[event_code])
                        else:
                            new_descriptions.append(str(desc))
                    except (ValueError, TypeError):
                        # Already a string, check if it's in our map
                        if desc in _EVENT_NUMERIC_MAP.values() or desc in _EVENT_NUMERIC_MAP:
                            new_descriptions.append(str(desc))
                        else:
                            new_descriptions.append(str(desc))
                
                new_annotations = mne.Annotations(
                    onset=annotations.onset,
                    duration=annotations.duration,
                    description=new_descriptions,
                )
                raw.set_annotations(new_annotations)
            else:
                # Try to read events from stim channel or events array
                events, event_id = mne.events_from_annotations(raw, verbose=False)
                if len(events) > 0:
                    # Remap events
                    remapped_events = events.copy()
                    for orig_desc, orig_id in event_id.items():
                        try:
                            code = int(orig_desc)
                            if code in _EVENT_NUMERIC_MAP:
                                new_desc = _EVENT_NUMERIC_MAP[code]
                                if new_desc in CANONICAL_EVENT_ID:
                                    remapped_events[remapped_events[:, 2] == orig_id, 2] = CANONICAL_EVENT_ID[new_desc]
                        except (ValueError, TypeError):
                            pass
                    
                    # Create new annotations from remapped events
                    new_annotations = mne.Annotations(
                        onset=remapped_events[:, 0] / raw.info["sfreq"],
                        duration=[0.0] * len(remapped_events),
                        description=[list(CANONICAL_EVENT_ID.keys())[list(CANONICAL_EVENT_ID.values()).index(e[2])] for e in remapped_events],
                    )
                    raw.set_annotations(new_annotations)

        except Exception:
            pass  # If event mapping fails, keep original annotations

        return raw


KERNEL = OpenNeuroDS005403Kernel()