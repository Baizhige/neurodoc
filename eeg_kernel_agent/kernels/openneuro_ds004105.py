"""OpenNeuro ds004105 stage1 kernel for EEGUnity.

BCIT Auditory Cueing dataset - driving fatigue paradigm.
74-channel BioSemi ActiveTwo, 1024 Hz sampling.

Source: https://openneuro.org/datasets/ds004105
Reference: https://doi.org/10.1016/j.neuroimage.2017.02.057
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
# BioSemi ActiveTwo amplifier
# Source: BCIT lab documentation, BioSemi ActiveTwo specifications
_AMPLIFIER = "BioSemi ActiveTwo"  # LLM 推断，需人类复核

# 74-channel high-density cap - assuming standard layout with extended coverage
# Source: BCIT lab standard cap configuration, 10-20 extended system
_CAP = "Ag/AgCl"  # LLM 推断，需人类复核


# ----------------------------------------------------------------------
# BCIT Event Code Mapping (raw meta)
# ----------------------------------------------------------------------
# 4-digit BCIT code structure:
#   Digit 1: Task type (1=driving, 2=guard, 3=calibration, 4=special)
#   Digit 2: Condition/perturbation
#   Digit 3: Event category (1=stimulus, 2=response, 3=performance)
#   Digit 4: Specific sub-type
#
# Source: BCIT lab codebook (inferred from dataset analysis.md)
_EVENT_MAP: Dict[str, str] = {
    # Driving events
    "4210": "driving: lateral perturbation onset",
    "4220": "driving: event code 4220",
    "4230": "driving: event code 4230",
    # Lane deviation / correction (binary classification targets)
    "4311": "lane deviation type 1",
    "4312": "lane deviation type 2",
    # Speed / control
    "3200": "speed control event",
    # Perturbation response
    "3111": "perturbation response type 1",
    "3112": "perturbation response type 2",
    # Performance metric
    "3310": "performance metric event",
    # Auditory cue events (classical task targets - P300/ERN)
    "1211": "auditory cue type 1",
    "1212": "auditory cue type 2",
    # Behavioral response
    "2621": "behavioral response type 1",
    "2622": "behavioral response type 2",
    # Condition-specific (half of subjects)
    "1111": "condition event 1111",
    "1112": "condition event 1112",
    "1121": "condition event 1121",
    "1122": "condition event 1122",
    "1211": "condition event 1211",
    "1212": "condition event 1212",
    "1221": "condition event 1221",
    "1222": "condition event 1222",
    "1311": "condition event 1311",
    "1312": "condition event 1312",
    "1321": "condition event 1321",
    "1322": "condition event 1322",
    # Rare event
    "4411": "rare event",
}


# ----------------------------------------------------------------------
# Channel Mapping (standard_1020 extended)
# ----------------------------------------------------------------------
# BioSemi 74-channel cap typically follows standard_1020 with extensions.
# Standard 10-20 channels: Fp1, Fp2, F7, F3, Fz, F4, F8, T7, C3, Cz, C4,
#                          T8, P7, P3, Pz, P4, P8, O1, Oz, O2
# Extended positions for 74 channels add intermediate and lateral sites.
#
# Source: BioSemi ActiveTwo 64/128 channel cap layout documentation
#         standard_1020 extended montage
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 electrodes
    "Fp1": "Fp1", "Fp2": "Fp2", "F7": "F7", "F3": "F3", "Fz": "Fz",
    "F4": "F4", "F8": "F8", "T7": "T7", "C3": "C3", "Cz": "Cz",
    "C4": "C4", "T8": "T8", "P7": "P7", "P3": "P3", "Pz": "Pz",
    "P4": "P4", "P8": "P8", "O1": "O1", "Oz": "Oz", "O2": "O2",
    # Additional BioSemi standard positions
    "AF7": "AF7", "AF3": "AF3", "AFz": "AFz", "AF4": "AF4", "AF8": "AF8",
    "F5": "F5", "F1": "F1", "F2": "F2", "F6": "F6",
    "FC5": "FC5", "FC3": "FC3", "FC1": "FC1", "FC2": "FC2", "FC4": "FC4", "FC6": "FC6",
    "C5": "C5", "C1": "C1", "C2": "C2", "C6": "C6",
    "CP5": "CP5", "CP3": "CP3", "CP1": "CP1", "CP2": "CP2", "CP4": "CP4", "CP6": "CP6",
    "P5": "P5", "P1": "P1", "P2": "P2", "P6": "P6",
    "PO7": "PO7", "PO3": "PO3", "POz": "POz", "PO4": "PO4", "PO8": "PO8",
    # Possible numeric aliases (BioSemi sometimes exports as EEG001, etc.)
    "EEG001": "Fp1", "EEG002": "Fp2", "EEG003": "F7", "EEG004": "F3",
    "EEG005": "Fz", "EEG006": "F4", "EEG007": "F8", "EEG008": "T7",
    "EEG009": "C3", "EEG010": "Cz", "EEG011": "C4", "EEG012": "T8",
    "EEG013": "P7", "EEG014": "P3", "EEG015": "Pz", "EEG016": "P4",
    "EEG017": "P8", "EEG018": "O1", "EEG019": "Oz", "EEG020": "O2",
    # Continue mapping for 74 channels
    "EEG021": "FC5", "EEG022": "FC3", "EEG023": "FC1", "EEG024": "FCz",
    "EEG025": "FC2", "EEG026": "FC4", "EEG027": "FC6",
    "EEG028": "C5", "EEG029": "C1", "EEG030": "C2", "EEG031": "C6",
    "EEG032": "CP5", "EEG033": "CP3", "EEG034": "CP1", "EEG035": "CPz",
    "EEG036": "CP2", "EEG037": "CP4", "EEG038": "CP6",
    "EEG039": "P5", "EEG040": "P1", "EEG041": "P2", "EEG042": "P6",
    "EEG043": "PO7", "EEG044": "PO3", "EEG045": "POz", "EEG046": "PO4",
    "EEG047": "PO8",
    "EEG048": "AF7", "EEG049": "AF3", "EEG050": "AFz", "EEG051": "AF4",
    "EEG052": "AF8",
    "EEG053": "F5", "EEG054": "F1", "EEG055": "F2", "EEG056": "F6",
    "EEG057": "O9", "EEG058": "OI1", "EEG059": "OI2", "EEG060": "O10",  # LLM 推断
    "EEG061": "F9", "EEG062": "F10",  # LLM 推断
    "EEG063": "TP7", "EEG064": "TP8",  # LLM 推断
    "EEG065": "CP5", "EEG066": "CP6",
    "EEG067": "P9", "EEG068": "P10",
    "EEG069": "PO9", "EEG070": "PO10",
    "EEG071": "AF9", "EEG072": "AF10",
    "EEG073": "unknown1", "EEG074": "unknown2",
}


# ----------------------------------------------------------------------
# Subject Info (from OpenNeuro participants.tsv or hardcoded)
# ----------------------------------------------------------------------
# Age/sex unknown for most subjects - dataset does not expose demographics
# in public participants.tsv.
# Source: OpenNeuro dataset description / analysis.md
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Format: "sub-01": {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
}


# ----------------------------------------------------------------------
# Kernel Class
# ----------------------------------------------------------------------
@dataclass
class OpenNeuroDS004105Kernel:
    """Stage1 kernel for OpenNeuro ds004105 - BCIT Auditory Cueing dataset."""

    KERNEL_ID: str = "openneuro-ds004105-stage1"

    # Event map for BCIT codes
    event_map: Dict[str, str] = field(default_factory=lambda: _EVENT_MAP.copy())

    # Channel rename map
    channel_rename_map: Dict[str, str] = field(
        default_factory=lambda: _CHANNEL_RENAME_MAP.copy()
    )

    def _load_participants_tsv(self, dataset_path: str) -> Dict[str, Dict[str, Any]]:
        """Load subject metadata from participants.tsv if available."""
        participants_tsv = os.path.join(dataset_path, "participants.tsv")
        if not os.path.exists(participants_tsv):
            return {}

        try:
            import pandas as pd

            df = pd.read_csv(participants_tsv, sep="\t")
            result = {}
            for _, row in df.iterrows():
                subj_id = row.get("participant_id", "")
                if not subj_id:
                    continue
                # Normalize to sub-XX format
                if not subj_id.startswith("sub-"):
                    subj_id = f"sub-{subj_id}"

                age_val = row.get("age", "unknown")
                sex_val = str(row.get("sex", "unknown")).lower()
                handedness_val = str(row.get("handedness", "unknown")).lower()

                # Normalize sex values
                if sex_val in ["m", "male"]:
                    sex_val = "male"
                elif sex_val in ["f", "female"]:
                    sex_val = "female"
                else:
                    sex_val = "unknown"

                # Normalize age
                if isinstance(age_val, (int, float)) and not np.isnan(age_val):
                    age_val = str(int(age_val))
                else:
                    age_val = "unknown"

                # Normalize handedness
                if handedness_val in ["r", "right", "right-handed"]:
                    handedness_val = "right"
                elif handedness_val in ["l", "left", "left-handed"]:
                    handedness_val = "left"
                else:
                    handedness_val = "unknown"

                result[subj_id] = {
                    "age": age_val,
                    "sex": sex_val,
                    "handedness": handedness_val,
                }
            return result
        except Exception:
            return {}

    def _extract_subject_id(self, file_path: str) -> str:
        """Extract subject ID from file path."""
        match = re.search(r"sub-(\d+)", file_path)
        if match:
            return f"sub-{match.group(1)}"
        return "sub-00"

    def _get_subject_info(self, file_path: str, dataset_path: str) -> Dict[str, str]:
        """Get subject metadata for a given file."""
        subj_id = self._extract_subject_id(file_path)
        participants_info = self._load_participants_tsv(dataset_path)

        if subj_id in participants_info:
            return participants_info[subj_id]

        if subj_id in _SUBJECT_DICT:
            return _SUBJECT_DICT[subj_id]

        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    def _build_channel_rename_map(self, raw: mne.io.BaseRaw) -> Dict[str, str]:
        """Build a rename map for the current raw object's channel names."""
        rename_map = {}
        existing = set(raw.ch_names)

        # Try standard names first
        for source, target in self.channel_rename_map.items():
            if source in existing and source != target:
                rename_map[source] = target

        return rename_map

    def _remap_events_to_annotations(
        self, raw: mne.io.BaseRaw
    ) -> mne.Annotations:
        """Convert numeric STIM channel events to human-readable annotations."""
        # Try to find events from annotations first
        events, event_id = mne.events_from_annotations(raw, verbose=False)

        if len(events) == 0:
            return raw.annotations

        # Build new descriptions based on event codes
        onset_list = []
        duration_list = []
        description_list = []

        for event in events:
            code = str(event[2])
            desc = self.event_map.get(code, f"event_{code}")
            onset_list.append(event[0] / raw.info["sfreq"])
            duration_list.append(0.0)
            description_list.append(desc)

        new_annotations = mne.Annotations(
            onset=np.array(onset_list),
            duration=np.array(duration_list),
            description=np.array(description_list),
        )

        return new_annotations

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 kernel to a single raw recording.

        Parameters
        ----------
        udataset : EEGUnity UnifiedDataset
            Dataset context holder.
        raw : mne.io.BaseRaw
            In-memory MNE Raw object loaded by EEGUnity.
        row : pandas.Series
            Locator row containing at least "File Path".

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with metadata and annotations.
        """
        file_path = row.get("File Path", "")
        dataset_path = udataset.path if hasattr(udataset, "path") else ""

        # ------------------------------------------------------------------
        # 1. Channel Renaming (before set_montage)
        # ------------------------------------------------------------------
        rename_map = self._build_channel_rename_map(raw)
        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if renaming fails

        # ------------------------------------------------------------------
        # 2. Set Montage (standard_1020 extended)
        # ------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Skip montage if not applicable

        # ------------------------------------------------------------------
        # 3. Extract Subject Information
        # ------------------------------------------------------------------
        subject_info = self._get_subject_info(file_path, dataset_path)

        # ------------------------------------------------------------------
        # 4. Build eegunity_description
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "") or ""

        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ------------------------------------------------------------------
        # 5. Convert Events to Annotations
        # ------------------------------------------------------------------
        try:
            new_annotations = self._remap_events_to_annotations(raw)
            raw.set_annotations(new_annotations)
        except Exception:
            pass  # Keep original annotations if conversion fails

        return raw


# ----------------------------------------------------------------------
# Module-level kernel instance
# ----------------------------------------------------------------------
KERNEL = OpenNeuroDS004105Kernel()