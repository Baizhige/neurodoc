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
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_STANDARD_19_CHANNEL_NAMES = [
    "Fp1", "Fp2",  # frontal pole
    "F7", "F3", "Fz", "F4", "F8",  # frontal
    "T3", "C3", "Cz", "C4", "T4",  # central
    "T5", "P3", "Pz", "P4", "T6",  # parietal
    "O1", "O2",  # occipital
]

# Mapping from possible raw channel name variants to standard names
# Source: Observed channel name patterns in OpenNeuro EEG datasets
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
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
    "HPVOJOS ABIERTOS": "hyperventilation_eyes_open",
    "HEPERVENTILACION OJOS ABIERTOS": "hyperventilation_eyes_open",
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
    # Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
    return info


def _remap_annotations(annotations: mne.Annotations) -> mne.Annotations:
    """Remap Spanish event labels to canonical English labels."""
    new_descriptions = []
    for desc in annotations.description:
        desc_clean = str(desc).strip().lower()
        # Check exact match first
        if desc in _SPANISH_EVENT_MAP:
            new_descriptions.append(_SPANISH_EVENT_MAP[desc])
        # Check case-insensitive match
        else:
            matched = False
            for spanish, canonical in _SPANISH_EVENT_MAP.items():
                if spanish.lower() == desc_clean:
                    new_descriptions.append(canonical)
                    matched = True
                    break
            if not matched:
                new_descriptions.append(desc)

    return mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        ch_names=annotations.ch_names,
    )


class OpenNeuroDS003194Kernel:
    """Stage1 kernel for OpenNeuro DS003194 (Neuroepo multisession)."""

    KERNEL_ID: str = "openneuro-ds003194-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (modified in-place)
        row : Locator row with File Path and metadata

        Returns
        -------
        mne.io.BaseRaw
        """
        file_path = row.get("File Path", "")
        dataset_path = os.path.dirname(os.path.dirname(file_path))

        # Get subject info
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))
        participants_df = _load_participants_tsv(dataset_path)
        subject_info = _get_subject_info(participants_df, subject_id)

        # Get device info (hardcoded from dataset documentation)
        # Source: Dataset README / paper describing equipment
        # Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
        amplifier = "unknown"  # Equipment not specified in available docs
        cap = "unknown"  # Electrode cap type not specified

        # Build and apply channel rename map BEFORE set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            mne.rename_channels(raw, rename_map)

        # Set standard 10-20 montage for 19-channel setup
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only keep channels that exist in raw
            available_channels = [ch for ch in montage.ch_names if ch in raw.ch_names]
            if available_channels:
                montage = montage.pick(available_channels)
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setup is optional if channel names don't match

        # Remap Spanish event labels to canonical English labels
        if raw.annotations:
            raw.set_annotations(_remap_annotations(raw.annotations))

        # Preserve original description and write eegunity_description
        original_description = raw.info.get("description", "")

        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": amplifier,
                "cap": cap,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003194Kernel()