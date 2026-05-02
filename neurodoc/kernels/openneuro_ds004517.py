"""openneuro_ds004517 stage1 kernel for EEGUnity.

Semantic decoding of imagined animals and tools during auditory imagery task.
32-channel EEG, 500 Hz, 20 subjects.

Events:
- animal_auditory_imagery_task / tool_auditory_imagery_task (long events)
- audio_animal / audio_tool (short cue events)
- rest

Source: https://openneuro.org/datasets/ds004517
       DOI: https://doi.org/10.18112/openneuro.ds004517.v1.0.2
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-08
# Source: Dataset description and paper DOI: 10.1038/s41597-025-04967-0
# amplifier information not explicitly stated in public documentation
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",  # inferred by LLM, needs human review
        "sex": "unknown",  # inferred by LLM, needs human review
        "handedness": "unknown",  # inferred by LLM, needs human review
    }
    for i in range(1, 21)
}

# Annotator: Human, 2026-04-08
# Source: Standard 32-channel EEG cap (typically 10-20 system)
# Common channel naming in auditory EEG studies
_EEG_CHANNEL_NAMES_STANDARD = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "T5", "T6",
    "M1", "M2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.

    Annotator: Human, 2026-04-08
    Source: OpenNeuro ds004517 channel naming convention review
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    # Common EEG channel aliases for 32-channel caps
    alias_groups = [
        # Standard 10-20 positions
        ("Fp1", ["EEG Fp1", "Fp1", "EEG-Fp1"]),
        ("Fp2", ["EEG Fp2", "Fp2", "EEG-Fp2"]),
        ("Fpz", ["EEG Fpz", "Fpz", "EEG-Fpz"]),
        ("F7", ["EEG F7", "F7", "EEG-F7"]),
        ("F3", ["EEG F3", "F3", "EEG-F3"]),
        ("Fz", ["EEG Fz", "Fz", "EEG-Fz"]),
        ("F4", ["EEG F4", "F4", "EEG-F4"]),
        ("F8", ["EEG F8", "F8", "EEG-F8"]),
        ("T7", ["EEG T7", "T7", "EEG-T7", "T7 left"]),
        ("C3", ["EEG C3", "C3", "EEG-C3"]),
        ("Cz", ["EEG Cz", "Cz", "EEG-Cz"]),
        ("C4", ["EEG C4", "C4", "EEG-C4"]),
        ("T8", ["EEG T8", "T8", "EEG-T8", "T8 right"]),
        ("P7", ["EEG P7", "P7", "EEG-P7"]),
        ("P3", ["EEG P3", "P3", "EEG-P3"]),
        ("Pz", ["EEG Pz", "Pz", "EEG-Pz"]),
        ("P4", ["EEG P4", "P4", "EEG-P4"]),
        ("P8", ["EEG P8", "P8", "EEG-P8"]),
        ("O1", ["EEG O1", "O1", "EEG-O1"]),
        ("Oz", ["EEG Oz", "Oz", "EEG-Oz"]),
        ("O2", ["EEG O2", "O2", "EEG-O2"]),
        ("T5", ["EEG T5", "T5", "EEG-T5"]),
        ("T6", ["EEG T6", "T6", "EEG-T6"]),
        # Mastoide references
        ("M1", ["EEG M1", "M1", "EEG-M1", "Mastoid left", "left mastoid"]),
        ("M2", ["EEG M2", "M2", "EEG-M2", "Mastoid right", "right mastoid"]),
    ]

    for target_name, aliases in alias_groups:
        for alias in aliases:
            if alias in ch_names and alias != target_name:
                rename_map[alias] = target_name
                break

    return rename_map


def _get_subject_info_from_participants(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv.

    Annotator: Human, 2026-04-08
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}

    try:
        df = pd.read_csv(participants_path, sep="\t")
        subject_row = df[df["participant_id"] == subject_id]
        if subject_row.empty:
            return {}
        info = {}
        if "age" in subject_row.columns:
            val = subject_row["age"].values[0]
            info["age"] = str(int(float(val))) if pd.notna(val) else "unknown"
        if "sex" in subject_row.columns:
            val = subject_row["sex"].values[0]
            if pd.notna(val):
                sex = str(val).strip().lower()
                if sex in ("f", "female"):
                    info["sex"] = "female"
                elif sex in ("m", "male"):
                    info["sex"] = "male"
                else:
                    info["sex"] = "unknown"
            else:
                info["sex"] = "unknown"
        if "handedness" in subject_row.columns:
            val = subject_row["handedness"].values[0]
            info["handedness"] = str(val).strip().lower() if pd.notna(val) else "unknown"
        return info
    except Exception:
        return {}


def _load_events_from_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Load events from sibling events.tsv file.

    Annotator: Human, 2026-04-08
    """
    base = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_path = base + "_events.tsv"
    if not os.path.exists(events_path):
        # Try BIDS-style path resolution
        dir_path = os.path.dirname(file_path)
        fname = os.path.basename(file_path)
        fname_stem = fname.split("_eeg")[0]
        events_path = os.path.join(dir_path, fname_stem + "_events.tsv")
    
    if os.path.exists(events_path):
        try:
            return pd.read_csv(events_path, sep="\t")
        except Exception:
            pass
    return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations.

    Annotator: Human, 2026-04-08
    """
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Build description from trial_type or value
    descriptions = []
    for idx, row in events_df.iterrows():
        if "trial_type" in events_df.columns and pd.notna(row.get("trial_type")):
            desc = str(row["trial_type"])
        elif "value" in events_df.columns and pd.notna(row.get("value")):
            desc = str(row["value"])
        else:
            desc = "unknown"
        descriptions.append(desc)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


@dataclass
class OpenNeuroDS004517Kernel:
    """Stage1 kernel for OpenNeuro ds004517 dataset."""

    KERNEL_ID: str = "openneuro-ds004517-stage1"
    required_info_fields: List[str] = field(default_factory=lambda: ["age", "sex"])
    required_native_misc: List[str] = field(default_factory=list)
    derived_misc_channels: List[str] = field(default_factory=list)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "root_dir", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from file path
        fname = os.path.basename(file_path)
        subject_id = None
        for part in fname.split("_"):
            if part.startswith("sub-"):
                subject_id = part
                break
        
        if subject_id is None:
            # Try from directory structure
            parts = file_path.split(os.sep)
            for part in parts:
                if part.startswith("sub-"):
                    subject_id = part
                    break
        
        # Get subject info from participants.tsv with required fields
        subject_info = _get_subject_info_from_participants(dataset_path, subject_id) if subject_id else {}
        
        # Merge with fallback dict
        fallback = _SUBJECT_DICT.get(subject_id, {}) if subject_id else {}
        
        age = subject_info.get("age", fallback.get("age", "unknown"))
        sex = subject_info.get("sex", fallback.get("sex", "unknown"))
        handedness = subject_info.get("handedness", fallback.get("handedness", "unknown"))
        
        # Build eegunity_description with required fields
        eegunity_description = {
            "age": str(age),
            "sex": str(sex),
            "amplifier": "unknown",
            "cap": "32-channel standard 10-20",
            "handedness": str(handedness),
        }
        
        # Add any additional required info fields from participants.tsv
        for field_name in self.required_info_fields:
            if field_name not in eegunity_description and field_name in subject_info:
                eegunity_description[field_name] = str(subject_info[field_name])
        
        # Set description as JSON string (MNE stores description as string)
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })
        
        # Rename channels to standard names if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set channel types for known non-EEG channels
        for ch_name in raw.ch_names:
            if ch_name in ("M1", "M2"):
                raw.set_channel_types({ch_name: "misc"})
        
        # Load events from events.tsv and set annotations
        events_df = _load_events_from_tsv(file_path)
        if events_df is not None and not events_df.empty:
            # Remove existing annotations if any
            if raw.annotations is not None:
                raw.set_annotations(None)
            annotations = _events_to_annotations(events_df, raw.info["sfreq"])
            raw.set_annotations(annotations)
        
        # Add derived misc channels
        for misc_name in self.derived_misc_channels:
            if misc_name not in raw.ch_names:
                misc_data = np.zeros((1, len(raw.times)))
                info_misc = mne.create_info([misc_name], raw.info["sfreq"], ["misc"])
                raw_misc = mne.io.RawArray(misc_data, info_misc)
                raw = raw.add_channels([raw_misc], force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004517Kernel()