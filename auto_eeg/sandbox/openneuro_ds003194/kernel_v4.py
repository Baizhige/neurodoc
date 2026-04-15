"""OpenNeuro DS003194 stage1 kernel for EEGUnity.

Neuroepo multisession: Resting-state EEG from Parkinson's disease patients
before/after 6-month Neuroepo drug administration. Clinical neurological
assessment battery with eyes-closed/open, hyperventilation, and photic
stimulation paradigms.

Source: https://openneuro.org/datasets/ds003194
Paper: DOI 10.3389/fnins.2022.841428
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Channel mapping (standard 19-channel 10-20 system)
# Source: Dataset documentation / paper describing 19-channel setup
# Annotator: LLM, 2026-04-08
_STANDARD_19_CHANNEL_NAMES = [
    "Fp1", "Fp2",  # frontal pole
    "F7", "F3", "Fz", "F4", "F8",  # frontal
    "T3", "C3", "Cz", "C4", "T4",  # central
    "T5", "P3", "Pz", "P4", "T6",  # parietal
    "O1", "O2",  # occipital
]

# Mapping from possible raw channel name variants to standard names
# Source: Observed channel name patterns in OpenNeuro EEG datasets
# Annotator: LLM, 2026-04-08
_CHANNEL_ALIAS_MAP = {
    # Common variations
    "EEG Fp1": "Fp1", "EEG Fp2": "Fp2",
    "EEG F7": "F7", "EEG F3": "F3", "EEG Fz": "Fz", "EEG F4": "F4", "EEG F8": "F8",
    "EEG T3": "T3", "EEG C3": "C3", "EEG Cz": "Cz", "EEG C4": "C4", "EEG T4": "T4",
    "EEG T5": "T5", "EEG P3": "P3", "EEG Pz": "Pz", "EEG P4": "P4", "EEG T6": "T6",
    "EEG O1": "O1", "EEG O2": "O2",
    # Alternative hyphen formats
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T3": "T3", "C3": "C3", "Cz": "Cz", "C4": "C4", "T4": "T4",
    "T5": "T5", "P3": "P3", "Pz": "Pz", "P4": "P4", "T6": "T6",
    "O1": "O1", "O2": "O2",
    # Lowercase variants
    "fp1": "Fp1", "fp2": "Fp2",
    "f7": "F7", "f3": "F3", "fz": "Fz", "f4": "F4", "f8": "F8",
    "t3": "T3", "c3": "C3", "cz": "Cz", "c4": "C4", "t4": "T4",
    "t5": "T5", "p3": "P3", "pz": "Pz", "p4": "P4", "t6": "T6",
    "o1": "O1", "o2": "O2",
}

# Spanish event label mappings to canonical English labels
# Source: analysis.md Event Structure table
# Annotator: Human, 2026-04-08
_SPANISH_EVENT_MAP = {
    "ojos cerrados": "eyes_closed",
    "ojos abiertos": "eyes_open",
    "recuperacion": "recovery",
    "hiperventilacion 1": "hyperventilation_1",
    "hiperventilacion 2": "hyperventilation_2",
    "hiperventilacion 3": "hyperventilation_3",
    "hiperventilacion 4": "hyperventilation_4",
    "photic stimulation": "photic_stimulation",
    "fotoestimulacion": "photic_stimulation",
    "discontinuity": "admin_discontinuity",
    "hpvojos abiertos": "hyperventilation_eyes_open",
    "heperventilacion ojos abiertos": "hyperventilation_eyes_open",
}

# Canonical event IDs for raw meta level
_CANONICAL_EVENT_IDS = {
    "eyes_closed": 1,
    "eyes_open": 2,
    "recovery": 3,
    "hyperventilation_1": 4,
    "hyperventilation_2": 5,
    "hyperventilation_3": 6,
    "hyperventilation_4": 7,
    "photic_stimulation": 8,
    "admin_discontinuity": 99,
    "hyperventilation_eyes_open": 10,
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for channels to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for source_name in existing_names:
        # Skip non-EEG channels
        if source_name.lower() in ("stim", "misc", "ekg", "emg", "trigger"):
            continue

        # Try direct alias lookup
        if source_name in _CHANNEL_ALIAS_MAP:
            target = _CHANNEL_ALIAS_MAP[source_name]
            if target != source_name:
                rename_map[source_name] = target
            continue

        # Try case-insensitive match
        source_lower = source_name.lower()
        for alias, target in _CHANNEL_ALIAS_MAP.items():
            if alias.lower() == source_lower and target != source_name:
                rename_map[source_name] = target
                break

    return rename_map


def _load_participants_tsv(dataset_path: str) -> Optional[pd.DataFrame]:
    """Load participants.tsv if it exists."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return None


def _get_subject_info(
    participants_df: Optional[pd.DataFrame],
    subject_id: str,
) -> Dict[str, str]:
    """Extract subject info from participants.tsv or return unknown."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    if participants_df is not None:
        # Match subject ID (handle various formats: sub-01, 01, etc.)
        subject_col = None
        for col in participants_df.columns:
            if "subject" in col.lower() or "participant" in col.lower():
                subject_col = col
                break

        if subject_col:
            # Try exact match first
            match = participants_df[participants_df[subject_col] == subject_id]
            if match.empty:
                # Try without 'sub-' prefix
                clean_id = re.sub(r"^sub-", "", subject_id)
                match = participants_df[
                    participants_df[subject_col].str.contains(clean_id, na=False)
                ]

            if not match.empty:
                row = match.iloc[0]
                # Age
                age_col = None
                for col in ["age", "Age", "AGE"]:
                    if col in participants_df.columns:
                        age_col = col
                        break
                if age_col:
                    age_val = row.get(age_col)
                    if pd.notna(age_val):
                        info["age"] = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)

                # Sex
                sex_col = None
                for col in ["sex", "Sex", "gender", "Gender"]:
                    if col in participants_df.columns:
                        sex_col = col
                        break
                if sex_col:
                    sex_val = row.get(sex_col)
                    if pd.notna(sex_val):
                        sex_str = str(sex_val).lower().strip()
                        if sex_str in ("m", "male", "hombre"):
                            info["sex"] = "male"
                        elif sex_str in ("f", "female", "mujer"):
                            info["sex"] = "female"
                        else:
                            info["sex"] = "unknown"

                # Handedness
                handedness_col = None
                for col in ["handedness", "Handedness", "hand", "Hand"]:
                    if col in participants_df.columns:
                        handedness_col = col
                        break
                if handedness_col:
                    handed_val = row.get(handedness_col)
                    if pd.notna(handed_val):
                        handed_str = str(handed_val).lower().strip()
                        if handed_str in ("r", "right", "diestro"):
                            info["handedness"] = "right"
                        elif handed_str in ("l", "left", "zurdo"):
                            info["handedness"] = "left"

    # Source: participants.tsv extracted values
    # Annotator: LLM, 2026-04-08
    return info


def _remap_annotations(annotations: mne.Annotations) -> mne.Annotations:
    """Remap Spanish event labels to canonical English labels."""
    new_descriptions = []
    for desc in annotations.description:
        desc_clean = str(desc).strip().lower()
        # Check exact match first
        if desc in _SPANISH_EVENT_MAP:
            new_descriptions.append(_SPANISH_EVENT_MAP[desc])
        elif desc_clean in _SPANISH_EVENT_MAP:
            new_descriptions.append(_SPANISH_EVENT_MAP[desc_clean])
        else:
            # Keep original description if no mapping found
            new_descriptions.append(str(desc))

    return mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )


def _load_json_sidecar(sidecar_path: str) -> Dict[str, Any]:
    """Load JSON sidecar file if it exists."""
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


class EEGUnity_Kernel:
    """EEGUnity stage1 kernel for OpenNeuro DS003194.

    Processes Neuroepo multisession resting-state EEG data from Parkinson's
    disease patients before/after 6-month Neuroepo drug administration.

    Args:
        udataset: Universal dataset object (passed by EEGUnity framework)
        raw: MNE Raw object containing the EEG data
        row: DataFrame row with metadata (bids_dir, subject_id, etc.)
    """

    def __init__(self):
        """Initialize the kernel."""
        self._eegunity_description: Dict[str, Any] = {}

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 processing to raw EEG data.

        Args:
            udataset: Universal dataset object
            raw: MNE Raw object
            row: DataFrame row with metadata

        Returns:
            Processed MNE Raw object
        """
        dataset_path = row.get("bids_dir", "")
        subject_id = row.get("subject_id", "unknown")
        session = row.get("session", "unknown")

        # -------------------------------------------------------------------------
        # Step 1: Load participants.tsv for subject metadata
        # -------------------------------------------------------------------------
        participants_df = _load_participants_tsv(dataset_path)
        subject_info = _get_subject_info(participants_df, subject_id)

        # Store eegunity_description (age must be string)
        self._eegunity_description = {
            "age": str(subject_info.get("age", "unknown")),
            "sex": str(subject_info.get("sex", "unknown")),
            "handedness": str(subject_info.get("handedness", "unknown")),
            "amplifier": "N/A",  # Unknown from metadata
            "cap": "N/A",  # Unknown from metadata
        }

        # -------------------------------------------------------------------------
        # Step 2: Standardize channel names
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[DS003194] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # Set channel types for non-standard channels
        channel_types = {}
        for ch in raw.ch_names:
            if ch.lower() in ("ecg", "eeg ecg"):
                channel_types[ch] = "ecg"
            elif ch.lower() in ("emg", "eeg emg"):
                channel_types[ch] = "emg"
            elif ch.lower() in ("trigger", "stim", "status"):
                channel_types[ch] = "stim"

        if channel_types:
            print(f"[DS003194] Setting channel types: {channel_types}")
            raw.set_channel_types(channel_types)

        # -------------------------------------------------------------------------
        # Step 3: Set standard 10-20 montage
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
            print(f"[DS003194] Set standard 10-20 montage")
        except Exception as e:
            print(f"[DS003194] Warning: Could not set montage: {e}")

        # -------------------------------------------------------------------------
        # Step 4: Remap annotations from Spanish to canonical English labels
        # -------------------------------------------------------------------------
        if raw.annotations is not None and len(raw.annotations) > 0:
            print(f"[DS003194] Original annotations: {list(raw.annotations.description[:10])}")
            raw.annotations = _remap_annotations(raw.annotations)
            print(f"[DS003194] Remapped annotations: {list(raw.annotations.description[:10])}")

        # -------------------------------------------------------------------------
        # Step 5: Ensure proper project name
        # -------------------------------------------------------------------------
        if raw.info.get("project_name") is None:
            raw.info["project_name"] = "Neuroepo_PD_EEG"

        return raw

    def get_eegunity_description(self) -> Dict[str, Any]:
        """Return the EEGUnity description dictionary.

        Returns:
            Dictionary containing subject metadata (age, sex, handedness, amplifier, cap)
        """
        return self._eegunity_description


KERNEL = EEGUnity_Kernel()