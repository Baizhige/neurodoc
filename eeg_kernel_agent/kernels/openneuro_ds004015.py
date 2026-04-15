"""OpenNeuro DS004015 stage1 kernel for EEGUnity.

Attended speaker paradigm using cEEGrid (around-the-ear) EEG.
18 channels, 500 Hz sampling rate, 36 subjects.

Source: https://openneuro.org/datasets/ds004015
Reference: DOI 10.3389/fnins.2022.869426
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Subject metadata from participants.tsv.
# Source: openneuro_ds004015/participants.tsv
# age column is present, sex column is absent.
# Annotator: Human, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# Load participants.tsv for age information
# Annotator: LLM, 2026-04-08
_participants_tsv_path = None  # Will be set during apply() if available


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if present in dataset root."""
    global _participants_tsv_path
    path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(path):
        _participants_tsv_path = path
        return pd.read_csv(path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(row, dataset_root: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or infer defaults."""
    subject_id = row.get("participant_id", row.get("subject_id", "unknown"))

    # Load participants data
    df = _load_participants_tsv(dataset_root)
    subject_info = {"age": "unknown", "sex": "unknown"}

    if not df.empty:
        # Find matching subject
        subj_row = df[df.get("participant_id", pd.Series()).str.contains(
            subject_id, na=False)]
        if subj_row.empty:
            subj_row = df[df.get("subject_id", pd.Series()).str.contains(
                subject_id, na=False)]

        if not subj_row.empty:
            row_data = subj_row.iloc[0]
            # Get age
            if "age" in df.columns:
                age_val = row_data.get("age", "unknown")
                if pd.notna(age_val):
                    subject_info["age"] = str(int(float(age_val)))
            # Sex column reportedly missing, but check anyway
            for col in ["sex", "gender"]:
                if col in df.columns:
                    sex_val = row_data.get(col, "unknown")
                    if pd.notna(sex_val):
                        subject_info["sex"] = str(sex_val).lower().strip()
                    break

    return subject_info


# cEEGrid channel naming - 18 around-the-ear electrodes.
# The cEEGrid uses a specific naming convention with "E" prefix for ear channels.
# Source: DOI 10.3389/fnins.2022.869426, cEEGrid electrode layout
# Annotator: Human, 2026-04-08
_CEEGRID_CHANNEL_MAP: Dict[str, str] = {
    "E1": "cEEGrid_Tp9",    # Left temporal, above ear
    "E2": "cEEGrid_Tp7",    # Left temporal-anterior
    "E3": "cEEGrid_Tp8",    # Right temporal, above ear
    "E4": "cEEGrid_Tp10",   # Right temporal-anterior
    "E5": "cEEGrid_AntT",   # Anterior temporal
    "E6": "cEEGrid_Ft7",    # Left fronto-temporal
    "E7": "cEEGrid_Ft8",    # Right fronto-temporal
    "E8": "cEEGrid_Tt",     # Top temporal
    "E9": "cEEGrid_Cb",     # Central button/vertex
    "E10": "cEEGrid_Pt",    # Posterior temporal
    "E11": "cEEGrid_Pt7",   # Left posterior temporal
    "E12": "cEEGrid_Pt8",   # Right posterior temporal
    "E13": "cEEGrid_Ot",    # Occipital-temporal
    "E14": "cEEGrid_At",    # Anterior temporal (alternative)
    "E15": "cEEGrid_Om",    # Mastoid region
    "E16": "cEEGrid_Op",    # Opcipital region
    "E17": "cEEGrid_C",     # Central
    "E18": "cEEGrid_F",     # Frontal
}


# Standard cEEGrid 10-10 compatible positions for montage
# These approximate positions for cEEGrid electrodes
# Source: cEEGrid manufacturer documentation, 10-20 system extensions
# Annotator: LLM 推断，需人类复核
_CEEGRID_MONTAGE_LOCATIONS = {
    "cEEGrid_Tp9": [(-0.08, -0.06, 0.04)],
    "cEEGrid_Tp7": [(-0.09, -0.03, 0.04)],
    "cEEGrid_Tp8": [(0.08, -0.06, 0.04)],
    "cEEGrid_Tp10": [(0.09, -0.03, 0.04)],
    "cEEGrid_AntT": [(-0.10, 0.00, 0.03)],
    "cEEGrid_Ft7": [(-0.08, 0.04, 0.04)],
    "cEEGrid_Ft8": [(0.08, 0.04, 0.04)],
    "cEEGrid_Tt": [(-0.05, -0.07, 0.05)],
    "cEEGrid_Cb": [(0.00, 0.00, 0.08)],
    "cEEGrid_Pt": [(0.00, -0.08, 0.04)],
    "cEEGrid_Pt7": [(-0.03, -0.09, 0.03)],
    "cEEGrid_Pt8": [(0.03, -0.09, 0.03)],
    "cEEGrid_Ot": [(-0.02, -0.10, 0.02)],
    "cEEGrid_At": [(0.02, -0.10, 0.02)],
    "cEEGrid_Om": [(-0.04, -0.02, 0.02)],
    "cEEGrid_Op": [(0.04, -0.02, 0.02)],
    "cEEGrid_C": [(0.00, 0.02, 0.05)],
    "cEEGrid_F": [(0.00, 0.06, 0.04)],
}


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename cEEGrid channels to standardized names."""
    rename_map = {}
    for ch_name in raw.ch_names:
        # Check for E1-E18 pattern
        if ch_name in _CEEGRID_CHANNEL_MAP:
            rename_map[ch_name] = _CEEGRID_CHANNEL_MAP[ch_name]
        # Handle common variations
        elif ch_name.startswith("EEG E") or ch_name.startswith("E"):
            # Try to match numeric suffix
            if ch_name.startswith("EEG "):
                suffix = ch_name.replace("EEG ", "")
            else:
                suffix = ch_name
            if suffix in _CEEGRID_CHANNEL_MAP:
                rename_map[ch_name] = _CEEGRID_CHANNEL_MAP[suffix]

    if rename_map:
        raw.rename_channels(rename_map)

    return raw


def _create_cEEGrid_montage() -> mne.channels.DigMontage:
    """Create a custom montage for cEEGrid electrodes."""
    dig_points = []
    ch_pos = {}

    for ch_name, coords_list in _CEEGRID_MONTAGE_LOCATIONS.items():
        coords = coords_list[0]
        ch_pos[ch_name] = np.array(coords)

    # Create montage with custom positions
    montage = mne.channels.make_dig_montage(
        ch_pos=ch_pos,
        coord_frame="head"
    )
    return montage


class OpenNeuroDS004015Kernel:
    """Stage1 kernel for OpenNeuro DS004015 (cEEGrid attended speaker paradigm)."""

    KERNEL_ID: str = "openneuro-ds004015-stage1"

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
            The modified Raw object with updated metadata and annotations.
        """
        # Get dataset root path
        dataset_root = getattr(udataset, "root_path", "")
        if not dataset_root and "File Path" in row:
            dataset_root = os.path.dirname(row["File Path"])

        # Get subject metadata
        subject_info = _get_subject_info(row, dataset_root)

        # Build description dict
        # Amplifier/cap info from paper DOI 10.3389/fnins.2022.869426
        # Annotator: LLM 推断，需人类复核
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "unknown",  # Not specified in available metadata
                "cap": "cEEGrid (Ag/AgCl)",  # cEEGrid uses Ag/AgCl electrodes
                "handedness": "unknown",  # Not available in metadata
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels BEFORE set_montage
        raw = _rename_channels(raw)

        # Set cEEGrid montage
        try:
            cEEGrid_montage = _create_cEEGrid_montage()
            raw.set_montage(cEEGrid_montage, on_missing="warn")
        except Exception:
            # If montage fails, continue without it
            pass

        # Standardize annotations from raw events
        # Map the event structure to standard annotation format
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)

            # Event mapping for standardization
            # Raw events: Beep, Calib_End, Calib_Start, StartTrigger, beam, beep, boundary, omni
            new_event_id = {
                "Beep": 1,
                "Calib_End": 2,
                "Calib_Start": 3,
                "StartTrigger": 4,
                "beam": 5,
                "beep": 6,
                "boundary": 7,
                "omni": 8,
            }

            # Create new annotations with standardized descriptions
            descriptions = []
            for event in events:
                event_code = event[2]
                # Find matching description
                desc = "unknown"
                for name, code in event_id.items():
                    if code == event_code:
                        desc = name
                        break
                # Standardize to our event names
                for std_name, std_code in new_event_id.items():
                    if std_name.lower() == str(desc).lower() or std_code == event_code:
                        descriptions.append(std_name)
                        break
                else:
                    descriptions.append(str(desc))

            annotations = mne.Annotations(
                onset=events[:, 0] / raw.info["sfreq"],
                duration=[0.0] * len(events),
                description=descriptions,
            )
            raw.set_annotations(annotations)

        except Exception:
            # Keep original annotations if processing fails
            pass

        # Ensure channel types are set correctly for cEEGrid
        eeg_channels = [ch for ch in raw.ch_names if ch.startswith("cEEGrid_")]
        if eeg_channels:
            try:
                raw.set_channel_types({ch: "eeg" for ch in eeg_channels})
            except Exception:
                pass

        return raw


KERNEL = OpenNeuroDS004015Kernel()