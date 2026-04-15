"""OpenNeuro DS004504 stage1 kernel for EEGUnity.

Resting-state EEG dataset of Alzheimer's disease (AD), Frontotemporal dementia (FTD),
and Cognitively Normal (CN) subjects. 88 subjects, 176 files (2 sessions each),
19-channel 10-20 system, 500 Hz.

Source: https://openneuro.org/datasets/ds004504
DOI: 10.1016/j.clinph.2024.12.008
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import pandas as pd


# Standard 19-channel 10-20 system
# Source: Dataset documentation / 10-20 international system
_STANDARD_19_CHANNELS = [
    "Fp1", "Fp2",  # prefrontal
    "F7", "F3", "Fz", "F4", "F8",  # frontal
    "T3", "C3", "Cz", "C4", "T4",  # central
    "T5", "P3", "Pz", "P4", "T6",  # parietal
    "O1", "O2",  # occipital
]

# Diagnosis label mapping (from participants.tsv)
# Source: analysis.md - Task definition
_DIAGNOSIS_MAP = {
    "AD": 0,   # Alzheimer's disease
    "FTD": 1,  # Frontotemporal dementia
    "CN": 2,   # Cognitively normal / Healthy controls
    # Alternative labels sometimes used in participants.tsv
    "HC": 2,   # Healthy control (maps to CN)
}


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if it exists.

    Parameters
    ----------
    dataset_root : str
        Root directory of the dataset.

    Returns
    -------
    pd.DataFrame
        Participants dataframe, or empty DataFrame if not found.
    """
    tsv_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _get_subject_diagnosis(
    subject_id: str,
    participants_df: pd.DataFrame,
) -> Optional[str]:
    """Extract diagnosis label for a subject from participants.tsv.

    Parameters
    ----------
    subject_id : str
        Subject identifier (e.g., "sub-01").
    participants_df : pd.DataFrame
        DataFrame loaded from participants.tsv.

    Returns
    -------
    Optional[str]
        Diagnosis label (AD/FTD/CN) or None if not found.
    """
    if participants_df.empty:
        return None

    # Normalize participant_id column (may be "participant_id" or "Subject")
    if "participant_id" in participants_df.columns:
        match = participants_df[
            participants_df["participant_id"].str.contains(
                subject_id.replace("sub-", ""), case=False, na=False
            )
        ]
        if not match.empty and "diagnosis" in match.columns:
            return match.iloc[0]["diagnosis"]
        # Try alternative column names
        for col in ["Group", "group", "diagnosis", "Diagnosis", "clinical_group"]:
            if col in participants_df.columns:
                val = match.iloc[0][col] if not match.empty else None
                if val is not None and str(val).strip():
                    return str(val).strip()

    return None


def _detect_dataset_root(file_path: str) -> str:
    """Infer dataset root directory from file path.

    Parameters
    ----------
    file_path : str
        Path to an EEG file.

    Returns
    -------
    str
        Inferred dataset root directory.
    """
    # Navigate up to find dataset root (contains participants.tsv)
    parts = os.path.normpath(file_path).split(os.sep)
    for i in range(len(parts), 0, -1):
        candidate = os.sep.join(parts[:i])
        if os.path.exists(os.path.join(candidate, "participants.tsv")):
            return candidate
    # Fallback: assume parent of sub-* directory
    for i, part in enumerate(parts):
        if part.startswith("sub-"):
            return os.sep.join(parts[:i])
    return os.path.dirname(file_path)


def _remap_channel_names(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap non-standard channel names to standard 10-20 names.

    This dataset uses standard 10-20 nomenclature but may have slight
    variations (e.g., 'T3' vs 'T7', 'T4' vs 'T8'). The function attempts
    to normalize channel names based on the standard 19-channel montage.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with remapped channel names.
    """
    rename_map: Dict[str, str] = {}

    # Alternative 10-20 names that may appear
    alias_groups = [
        ("T3", ["T3", "T7", "TA1"]),
        ("T4", ["T4", "T8", "TA2"]),
        ("T5", ["T5", "P7", "TP7"]),
        ("T6", ["T6", "P8", "TP8"]),
        ("Fp1", ["Fp1", "AF7"]),
        ("Fp2", ["Fp2", "AF8"]),
        ("F7", ["F7", "AF7"]) if "F7" not in raw.ch_names else ("F7", ["F7"]),
        ("F8", ["F8", "AF8"]) if "F8" in raw.ch_names else None,
        ("O1", ["O1", "OI1"]),
        ("O2", ["O2", "OI2"]),
        ("Fz", ["Fz"]),
        ("Cz", ["Cz"]),
        ("Pz", ["Pz"]),
    ]

    existing_names = set(raw.ch_names)
    for item in alias_groups:
        if item is None:
            continue
        target_name, aliases = item
        for alias in aliases:
            if alias in existing_names and alias != target_name:
                rename_map[alias] = target_name
                break

    if rename_map:
        raw.rename_channels(rename_map)

    return raw


class OpenNeuroDS004504Kernel:
    """Stage1 kernel for OpenNeuro DS004504 dataset."""

    KERNEL_ID: str = "openneuro-ds004504-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject ID", row.get("participant_id", "unknown"))

        # Detect dataset root for participants.tsv
        dataset_root = _detect_dataset_root(file_path)
        participants_df = _load_participants_tsv(dataset_root)

        # Extract diagnosis label
        diagnosis = _get_subject_diagnosis(subject_id, participants_df)
        # Normalize to AD/FTD/CN
        if diagnosis is not None:
            diagnosis_normalized = _DIAGNOSIS_MAP.get(diagnosis.upper(), None)
        else:
            diagnosis_normalized = None

        # Extract subject metadata
        age_value = "unknown"
        sex_value = "unknown"

        if not participants_df.empty and "participant_id" in participants_df.columns:
            match = participants_df[
                participants_df["participant_id"].str.contains(
                    subject_id.replace("sub-", ""), case=False, na=False
                )
            ]
            if not match.empty:
                # Extract age
                for col in ["age", "Age", "AGE"]:
                    if col in match.columns:
                        age_raw = match.iloc[0][col]
                        if age_raw is not None and str(age_raw).strip():
                            age_value = str(age_raw).strip()
                        break

                # Extract sex
                for col in ["sex", "Sex", "gender", "Gender"]:
                    if col in match.columns:
                        sex_raw = match.iloc[0][col]
                        if sex_raw is not None and str(sex_raw).strip():
                            sex_lower = str(sex_raw).strip().lower()
                            if sex_lower in ["m", "male", "man"]:
                                sex_value = "male"
                            elif sex_lower in ["f", "female", "woman"]:
                                sex_value = "female"
                            else:
                                sex_value = "unknown"
                        break

        # If age is still unknown, mark as LLM inference
        if age_value == "unknown":
            age_value = "unknown"  # LLM 推断，需人类复核

        # Device information - inferred from dataset description
        # Source: Dataset documentation and typical clinical EEG setup
        amplifier_value = "unknown"  # LLM 推断，需人类复核
        cap_value = "unknown"  # LLM 推断，需人类复核
        handedness_value = "unknown"

        # Remap channel names before setting montage
        raw = _remap_channel_names(raw)

        # Set standard 10-20 montage if channels match
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Check if all channels in raw are in the montage
            raw_channels = set(raw.ch_names)
            montage_channels = set(montage.ch_names)
            if raw_channels.issubset(montage_channels) or len(raw_channels) >= 19:
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setting is best-effort

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age_value,
                "sex": sex_value,
                "amplifier": amplifier_value,
                "cap": cap_value,
                "handedness": handedness_value,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Add diagnosis annotation for super meta (classification task)
        # This dataset has no_events (resting-state), so we create a synthetic
        # annotation from the diagnosis label for downstream epoch labeling
        if diagnosis_normalized is not None:
            # Create an annotation at time 0 with the diagnosis label
            # This enables epoch_by_segmentation_hdf5 to label epochs by subject diagnosis
            onset = raw.times[0] if len(raw.times) > 0 else 0.0
            annotations = mne.Annotations(
                onset=[onset],
                duration=[0.0],
                description=[f"diagnosis:{diagnosis}"],
            )
            raw.set_annotations(annotations)
        else:
            # No diagnosis found - create no_events annotation
            annotations = mne.Annotations(
                onset=[0.0],
                duration=[0.0],
                description=["no_events"],
            )
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenNeuroDS004504Kernel()