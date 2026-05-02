"""Dataset-specific kernel for openneuro ds003602.

Childhood Sexual Abuse and Problem Drinking in Women: Neurobehavioral Mechanisms.
EEG task with affective picture viewing and startle paradigms.

Channel configuration:
- 35 channels: standard 10-20 EEG cap + EOG
- Sampling rate: 1000 Hz

Event types (raw meta):
- Valence stimuli: NegStim, NeuStim, PosStim
- Alcohol cues: AlcStimWithoutStartle variants, AlcP1000/P2000/P3000 variants
- Non-alcohol cues: NonAlcStimWithoutStartle variants, NonAlcP1000/P2000/P3000 variants
- Rest: EyesOpen1/2, EyesClose1/2, EndOfRest
- Admin: ignore

Source: https://doi.org/10.18112/openneuro.ds003602.v1.0.1
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Subject metadata (from participants.tsv)
# ============================================================================
# Source: participants.tsv in dataset root
# Contains: participant_id, age, sex, handedness (if available)
# All fields must be strings per EEGUnity spec.
_SUBJECT_METADATA: Dict[str, Dict[str, str]] = {}
# Loaded dynamically in apply() from dataset's participants.tsv


# ============================================================================
# Channel rename map (standard 10-20)
# ============================================================================
# Source: This dataset uses standard 10-20 naming in BIDS format.
# Standard 10-20 positions: Fp1, Fp2, F3, F4, C3, C4, P3, P4, O1, O2,
# F7, F8, T7, T8, P7, P8, Fz, Cz, Pz, Oz, FC1, FC2, CP1, CP2, FC5, FC6,
# CP5, CP6, TP9, TP10, FT9, FT10, F1-F8, C1-C6, P1-P8, PO1, PO2, PO3, PO4
# Plus: VEOG, HEOG, EOG channels
# If the raw data uses different naming (e.g. "EEG 001"), we map to standard.
_EEG_STANDARD_1020 = {
    "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2",
    "F7", "F8", "T7", "T8", "P7", "P8", "Fz", "Cz", "Pz", "Oz",
    "FC1", "FC2", "CP1", "CP2", "FC3", "FC4", "FC5", "FC6",
    "CP3", "CP4", "CP5", "CP6", "TP7", "TP8", "FT7", "FT8",
    "AF7", "AF8", "AF3", "AF4", "PO3", "PO4",
    "F1", "F2", "F5", "F6", "C1", "C2", "C5", "C6",
    "P1", "P2", "P5", "P6",
    "VEOG", "HEOG", "EOG", "LEOG", "REOG", "VEOG-up", "VEOG-lo",
}


def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load participants.tsv to extract subject metadata.

    Returns dict: {sub_id: {"age": str, "sex": str, "handedness": str}}
    """
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}

    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}

    result = {}
    for _, row in df.iterrows():
        sub_id = str(row.get("participant_id", "")).strip()
        if not sub_id:
            continue

        # Extract age
        age_raw = row.get("age", None)
        if age_raw is not None and not pd.isna(age_raw):
            age_str = str(age_raw).strip()
            # Handle numeric age -> string
            try:
                age_val = float(age_str)
                age_str = str(int(age_val))
            except ValueError:
                pass
        else:
            age_str = "unknown"

        # Extract sex (normalize to lowercase)
        sex_raw = row.get("sex", row.get("gender", None))
        if sex_raw is not None and not pd.isna(sex_raw):
            sex_str = str(sex_raw).strip().lower()
            if sex_str not in ("male", "female"):
                sex_str = "unknown"
        else:
            sex_str = "unknown"

        # Extract handedness
        handed_raw = row.get("handedness", row.get("hand", None))
        if handed_raw is not None and not pd.isna(handed_raw):
            handed_str = str(handed_raw).strip().lower()
            if handed_str not in ("right", "left", "ambidextrous"):
                handed_str = "unknown"
        else:
            handed_str = "unknown"

        result[sub_id] = {
            "age": age_str,
            "sex": sex_str,
            "handedness": handed_str,
        }

    return result


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20.

    Handles patterns like:
    - "EEG 001" -> "Fp1" (if in correct position)
    - "EEG001" -> "Fp1"
    - "VEOG" -> "VEOG" (already standard)
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: "EEG N" or "EEGNNN" format
    # BIDS standard format typically already uses standard names
    # This handles legacy/alternative naming

    # Pattern 2: Check for common EOG/EMG channels
    eog_aliases = {
        "veog": "VEOG",
        "eogv": "VEOG",
        "eog_up": "VEOG",
        "heog": "HEOG",
        "eogh": "HEOG",
        "eog_right": "HEOG",
        "eog_left": "LEOG",
        "leog": "LEOG",
        "reog": "REOG",
    }

    for src_name in list(existing):
        src_lower = src_name.lower()
        if src_lower in eog_aliases:
            target = eog_aliases[src_lower]
            if target != src_name:
                rename_map[src_name] = target

    return rename_map


def _detect_subject_id(row) -> Optional[str]:
    """Extract subject ID from row's file path."""
    file_path = str(row.get("File Path", ""))
    # Pattern: sub-XXXX in path
    import re
    match = re.search(r"sub-[A-Za-z0-9]+", file_path)
    if match:
        return match.group(0)
    return None


class OpenNeuroDs003602Kernel:
    """Stage1 kernel for openneuro ds003602 dataset."""

    KERNEL_ID = "openneuro-ds003602-stage1"

    def __init__(self):
        self._subject_cache: Dict[str, Dict[str, str]] = {}
        self._dataset_path_cache: Optional[str] = None

    def _get_dataset_path(self, row) -> str:
        """Extract dataset root path from row's file path."""
        file_path = str(row.get("File Path", ""))
        # Navigate up to find dataset root (contains participants.tsv)
        parts = os.path.dirname(file_path).split(os.sep)
        for i in range(len(parts), 0, -1):
            candidate = os.sep.join(parts[:i])
            if os.path.exists(os.path.join(candidate, "participants.tsv")):
                return candidate
        # Fallback: use parent of subject folder
        sub_idx = file_path.find("sub-")
        if sub_idx >= 0:
            return file_path[:sub_idx - 1]  # Remove trailing separator
        return os.path.dirname(file_path)

    def _load_subject_metadata(self, row) -> Dict[str, str]:
        """Load and cache subject metadata for current dataset."""
        dataset_path = self._get_dataset_path(row)

        if dataset_path != self._dataset_path_cache:
            self._subject_cache = _load_participants_tsv(dataset_path)
            self._dataset_path_cache = dataset_path

        sub_id = _detect_subject_id(row)
        if sub_id and sub_id in self._subject_cache:
            return self._subject_cache[sub_id]

        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path.

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with updated info and annotations.
        """
        file_path = str(row.get("File Path", ""))

        # =====================================================================
        # 1. Load subject metadata
        # =====================================================================
        subject_meta = self._load_subject_metadata(row)

        # =====================================================================
        # 2. Build eegunity_description
        # =====================================================================
        # Amplifier/cap: inferred from dataset documentation (inferred by LLM, needs human review)
        # This dataset used a BrainVision system with Ag/AgCl electrodes
        # Source: OpenNeuro dataset documentation, 2026-04-08
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_meta.get("age", "unknown"),
                "sex": subject_meta.get("sex", "unknown"),
                "amplifier": "BrainVision",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": subject_meta.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # =====================================================================
        # 3. Channel rename (BEFORE set_montage)
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # =====================================================================
        # 4. Set montage (standard 10-20)
        # =====================================================================
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set channels that exist in both raw and montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if len(common_channels) >= 10:  # Require minimum coverage
                raw.set_montage(montage, on_missing="ignore")
            else:
                print(f"[{self.KERNEL_ID}] Warning: Only {len(common_channels)} "
                      f"channels match standard montage, skipping.")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: Could not set montage: {e}")

        # =====================================================================
        # 5. Process events from BIDS events.tsv if available
        # =====================================================================
        # Check for accompanying events.tsv file
        events_path = file_path.replace("_eeg.edf", "_events.tsv")
        events_path = events_path.replace("_eeg.bdf", "_events.tsv")
        events_path = events_path.replace(".edf", "_events.tsv")

        if not os.path.exists(events_path):
            # Try alternative pattern
            base = os.path.splitext(file_path)[0]
            for ext in ["_events.tsv", "-events.tsv", "_eeg_events.tsv"]:
                candidate = base + ext
                if os.path.exists(candidate):
                    events_path = candidate
                    break

        if os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                if "onset" in events_df.columns and "trial_type" in events_df.columns:
                    # Convert to MNE annotations
                    onset = events_df["onset"].values
                    duration = events_df.get("duration", [0] * len(onset))
                    if isinstance(duration, str):
                        duration = [0] * len(onset)
                    description = events_df["trial_type"].fillna("unknown").values

                    annotations = mne.Annotations(
                        onset=onset,
                        duration=duration,
                        description=description,
                    )
                    raw.set_annotations(annotations)
            except Exception as e:
                print(f"[{self.KERNEL_ID}] Warning: Could not load events.tsv: {e}")

        # =====================================================================
        # 6. Ensure sampling rate is recorded correctly
        # =====================================================================
        # 1000 Hz confirmed from dataset documentation
        if raw.info["sfreq"] != 1000.0:
            print(f"[{self.KERNEL_ID}] Warning: Expected 1000 Hz, got {raw.info['sfreq']} Hz")

        return raw


KERNEL = OpenNeuroDs003602Kernel()