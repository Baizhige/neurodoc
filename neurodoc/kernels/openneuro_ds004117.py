"""OpenNeuro DS004117 (Sternberg Working Memory) stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds004117
Paradigm: Modified Sternberg working memory task with memory load manipulation (3, 5, 7 letters)
Channels: 71 (SCCN extended 10-20 system), 250 Hz
Reference: 10.1016/j.neuroimage.2005.04.014

Source: OpenNeuro DS004117, SCCN 71-channel Sternberg WM dataset
Paper: "Frontal midline theta dynamics..." (NeuroImage, 2005)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne
import numpy as np
import pandas as pd


# Subject metadata - age/sex not in participants.tsv, defaulting to unknown
# Source: dataset documentation (age/sex not provided)
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    # Age and sex unknown for all 23 subjects
}

# Amplifier information from SCCN lab standard equipment
# Source: SCCN lab equipment documentation; 10.1016/j.neuroimage.2005.04.014
# Annotator: LLM, 2026-04-08
_AMPLIFIER = "BrainAmp"  # inferred by LLM, needs human review
_CAP = "Ag/AgCl"  # inferred by LLM, needs human review


# SCCN 71-channel system channel mapping
# Raw files may use abbreviated names like Fz, Cz, Pz, etc.
# Source: SCCN 71-channel electrode layout (standard_1020 extended)
# Annotator: LLM, 2026-04-08
_SCCN_71_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FC7", "FC3", "FCz", "FC4", "FC8",
    "T7", "C3", "Cz", "C4", "T8",
    "CP7", "CP3", "CPz", "CP4", "CP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    # Additional 71-channel extended electrodes
    "AF7", "AF3", "AF4", "AF8",
    "FT7", "FT8",
    "TP7", "TP8",
    "PO7", "PO8",  # some systems distinguish these from P7/P8
    # Below: likely 71-channel specific extended positions
    "F1", "F2",
    "FC1", "FC2",
    "C1", "C2",
    "CP1", "CP2",
    "P1", "P2",
    "PO1", "PO2",
    # Possibly EOG channels
    "EOG-left", "EOG-right", "EOG-up", "EOG-down",
    # Reference/misc
    "A1", "A2", "TP10", "CBA",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for SCCN 71-channel system.

    BrainVision files may have abbreviated channel names.
    This function maps common variants to standard names.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Common BrainVision / SCCN name variations
    alias_groups = [
        # Standard 10-20 primary
        ("Fp1", ["Fp1", "EEG Fp1", "Fp 1"]),
        ("Fpz", ["Fpz", "Fpz", "EEG Fpz"]),
        ("Fp2", ["Fp2", "EEG Fp2", "Fp 2"]),
        ("F7", ["F7", "F7", "EEG F7"]),
        ("F3", ["F3", "F3", "EEG F3"]),
        ("Fz", ["Fz", "Fz", "EEG Fz"]),
        ("F4", ["F4", "F4", "EEG F4"]),
        ("F8", ["F8", "F8", "EEG F8"]),
        ("T7", ["T7", "T7", "EEG T7"]),
        ("C3", ["C3", "C3", "EEG C3"]),
        ("Cz", ["Cz", "Cz", "EEG Cz"]),
        ("C4", ["C4", "C4", "EEG C4"]),
        ("T8", ["T8", "T8", "EEG T8"]),
        ("P7", ["P7", "P7", "EEG P7"]),
        ("P3", ["P3", "P3", "EEG P3"]),
        ("Pz", ["Pz", "Pz", "EEG Pz"]),
        ("P4", ["P4", "P4", "EEG P4"]),
        ("P8", ["P8", "P8", "EEG P8"]),
        ("O1", ["O1", "O1", "EEG O1"]),
        ("Oz", ["Oz", "Oz", "EEG Oz"]),
        ("O2", ["O2", "O2", "EEG O2"]),
        # EOG channels
        ("EOG-left", ["EOG L", "EOGL", "EOG-left", "Veog L"]),
        ("EOG-right", ["EOG R", "EOGR", "EOG-right", "Veog R"]),
        ("EOG-up", ["EOG V", "VEOG", "EOG-up"]),
        ("EOG-down", ["HEOG", "EOG H", "EOG-down"]),
        # Mastoid reference
        ("A1", ["A1", "M1", "LeftMastoid"]),
        ("A2", ["A2", "M2", "RightMastoid"]),
    ]

    for target_name, aliases in alias_groups:
        for alias in aliases:
            if alias in existing and alias != target_name:
                rename_map[alias] = target_name
                break

    return rename_map


def _load_subject_metadata(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from participants.tsv if available."""
    participants_file = os.path.join(dataset_path, "participants.tsv")

    if os.path.exists(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            if "participant_id" in df.columns:
                # Normalize participant_id (remove 'sub-' prefix if present)
                df["participant_id"] = df["participant_id"].str.replace("sub-", "", regex=False)
                row = df[df["participant_id"] == subject_id]
                if not row.empty:
                    metadata: Dict[str, str] = {}

                    # Extract age
                    if "age" in df.columns:
                        age_val = row["age"].values[0]
                        if pd.notna(age_val):
                            metadata["age"] = str(age_val)

                    # Extract sex
                    if "sex" in df.columns or "gender" in df.columns:
                        sex_col = "sex" if "sex" in df.columns else "gender"
                        sex_val = row[sex_col].values[0]
                        if pd.notna(sex_val):
                            sex_str = str(sex_val).lower().strip()
                            if sex_str in ["m", "male", "f", "female"]:
                                metadata["sex"] = "male" if sex_str.startswith("m") else "female"

                    return metadata
        except Exception:
            pass

    return {}


def _extract_events_from_raw(raw: mne.io.BaseRaw) -> None:
    """Extract and remap events from raw annotations.

    BrainVision files store events in annotations.
    Remap to canonical event names: WM, nonWM, gA-gZ, A-Z, admin marker.
    """
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
    except Exception:
        return

    # Define event remapping based on dataset documentation
    # Event IDs are stored as string descriptions in BrainVision format
    # Original event mapping:
    # - "WM" -> WM trial onset
    # - "nonWM" -> non-WM distractor trial
    # - "gA"-"gZ" -> target letter onset (memorize)
    # - "A"-"Z" -> distractor letter onset (ignore)
    # - "255" -> admin/system marker

    # Build reverse mapping
    reverse_map: Dict[str, str] = {}
    for desc, code in event_id.items():
        desc_str = str(desc).strip()
        # WM trial marker
        if desc_str == "WM":
            reverse_map[desc] = "WM"
        elif desc_str == "nonWM":
            reverse_map[desc] = "nonWM"
        # Admin marker
        elif desc_str in ["255", "254", 255, 254]:
            reverse_map[desc] = "admin: marker-255"
        # Target letters (g-prefixed)
        elif len(desc_str) == 2 and desc_str.startswith("g") and desc_str[1].isalpha():
            reverse_map[desc] = desc_str.upper()
        # Distractor letters (plain)
        elif len(desc_str) == 1 and desc_str.isalpha():
            reverse_map[desc] = desc_str.upper()
        else:
            reverse_map[desc] = desc_str

    # Create new annotations with remapped descriptions
    onset = events[:, 0] / raw.info["sfreq"]
    duration = np.zeros(len(events))
    descriptions = [reverse_map.get(str(e), str(e)) for e in events[:, 2]]

    if descriptions:
        new_annotations = mne.Annotations(
            onset=onset,
            duration=duration,
            description=descriptions,
        )
        raw.set_annotations(new_annotations)


class OpenNeuroDS004117Kernel:
    """Stage1 kernel for OpenNeuro DS004117 (Sternberg Working Memory).

    This kernel:
    - Loads subject metadata from participants.tsv (age/sex)
    - Renames channels to standard names (SCCN 71-channel system)
    - Sets montage for standard_1020
    - Extracts and remaps events to canonical names
    - Writes eegunity_description to raw.info["description"]
    """

    KERNEL_ID: str = "openneuro-ds004117-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG object loaded by EEGUnity
        row : pandas.Series
            Locator row with File Path and subject info

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with metadata and events
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", os.path.dirname(file_path))
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))

        # Extract subject metadata
        subject_meta = _SUBJECT_DICT.get(subject_id, {})
        if not subject_meta:
            # Try loading from participants.tsv
            loaded_meta = _load_subject_metadata(dataset_path, subject_id)
            subject_meta.update(loaded_meta)

        # Get age and sex
        age = subject_meta.get("age", "unknown")  # inferred by LLM, needs human review
        sex = subject_meta.get("sex", "unknown")  # inferred by LLM, needs human review

        # Original description
        original_description = raw.info.get("description", "")

        # Update description with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex).lower() if sex != "unknown" else "unknown",
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names BEFORE set_montage()
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[Kernel] Renaming {len(rename_map)} channels: {rename_map}")
            raw.rename_channels(rename_map)

        # Set montage (standard 1020 for SCCN 71-channel system)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Add extra channels if present that are not in standard_1020
            raw.set_montage(montage, on_missing="ignore")
        except Exception as e:
            print(f"[Kernel] Warning: Could not set montage: {e}")

        # Extract and remap events
        _extract_events_from_raw(raw)

        return raw


KERNEL = OpenNeuroDS004117Kernel()