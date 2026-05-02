"""OpenNeuro DS005305 stage1 kernel for EEGUnity.

Resting-state EEG microstates and executive functions dataset.
165 subjects, 64 channels, 512 Hz sampling rate.
Contains RS_EC (eyes-closed) and RS_EO (eyes-open) resting blocks.

Source: https://openneuro.org/datasets/ds005305
Paper: 10.1016/j.cortex.2024.05.019
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Annotator: LLM, 2026-04-08
# Source: Dataset description (standard 64-channel EEG cap)
# inferred by LLM, needs human review
_DEVICE_INFO = {
    "amplifier": "unknown",
    "cap": "Ag/AgCl",
}

# Standard 10-20 64-channel names for validation
_STANDARD_64_CHANNELS = {
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    "A1", "A2",
    "Tp9", "Tp10",
}

# Events to exclude (admin/artifact markers)
_EXCLUDE_EVENTS = {
    "boundary",
    "RIGHT pressed", "RIGHT released",
    "DOWN pressed", "DOWN released",
    "LEFT pressed", "LEFT released",
}


def _load_participants_tsv(dataset_root: str) -> Dict[str, Dict[str, str]]:
    """Load participant metadata from BIDS participants.tsv.

    Parameters
    ----------
    dataset_root : str
        Path to the dataset root directory.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Subject ID -> {age, sex, handedness} mapping.
        All values are strings; missing values are "unknown".
    """
    participants_path = os.path.join(dataset_root, "participants.tsv")
    subject_dict: Dict[str, Dict[str, str]] = {}

    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t")
            for _, row in df.iterrows():
                # Extract subject ID (e.g., "sub-001" -> "001" or "sub-001")
                subject_id = str(row.get("participant_id", ""))
                age_val = str(row.get("age", "unknown"))
                sex_val = str(row.get("sex", row.get("gender", "unknown"))).lower()
                handedness_val = str(row.get("handedness", "unknown")).lower()

                # Normalize sex values
                if sex_val in ["m", "male", "man"]:
                    sex_val = "male"
                elif sex_val in ["f", "female", "woman"]:
                    sex_val = "female"
                else:
                    sex_val = "unknown"

                # Normalize handedness
                if handedness_val not in ["left", "right", "ambidextrous"]:
                    handedness_val = "unknown"

                # Handle age
                if age_val in ["nan", "", "NaN"]:
                    age_val = "unknown"

                subject_dict[subject_id] = {
                    "age": age_val,
                    "sex": sex_val,
                    "handedness": handedness_val,
                }
        except Exception:
            pass

    return subject_dict


def _get_subject_metadata(
    row: Any,
    subject_dict: Dict[str, Dict[str, str]],
    dataset_root: str,
) -> Dict[str, str]:
    """Get subject metadata from various sources.

    Priority: participants.tsv > row metadata > defaults
    """
    defaults = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    # Try to extract subject ID from row
    subject_id = None
    if hasattr(row, "get"):
        subject_id = row.get("Subject", row.get("subject_id", None))
    elif hasattr(row, "__getitem__"):
        try:
            subject_id = row["Subject"] if "Subject" in row else row.get("subject_id", None)
        except (KeyError, TypeError):
            pass

    # Look up in participants.tsv
    if subject_id and subject_dict:
        # Try various subject ID formats
        for fmt in [str(subject_id), f"sub-{subject_id}", subject_id]:
            if fmt in subject_dict:
                return subject_dict[fmt]

    return defaults


def _detect_and_rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Detect non-standard channel names and rename to standard 10-20 names.

    This dataset uses standard 10-20 nomenclature, but may have slight
    variations. This function normalizes common aliases.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data with potentially non-standard channel names.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with renamed channels if needed.
    """
    ch_names = raw.ch_names
    rename_map: Dict[str, str] = {}

    # Common aliases mapping
    alias_map = {
        "EEG-Fp1": "Fp1",
        "EEG-Fpz": "Fpz",
        "EEG-Fp2": "Fp2",
        "EEG-F7": "F7",
        "EEG-F3": "F3",
        "EEG-Fz": "Fz",
        "EEG-F4": "F4",
        "EEG-F8": "F8",
        "EEG-FC5": "FC5",
        "EEG-FC3": "FC3",
        "EEG-FC1": "FC1",
        "EEG-FCz": "FCz",
        "EEG-FC2": "FC2",
        "EEG-FC4": "FC4",
        "EEG-FC6": "FC6",
        "EEG-T7": "T7",
        "EEG-T8": "T8",
        "EEG-C3": "C3",
        "EEG-Cz": "Cz",
        "EEG-C4": "C4",
        "EEG-CP5": "CP5",
        "EEG-CP3": "CP3",
        "EEG-CP1": "CP1",
        "EEG-CPz": "CPz",
        "EEG-CP2": "CP2",
        "EEG-CP4": "CP4",
        "EEG-CP6": "CP6",
        "EEG-P7": "P7",
        "EEG-P3": "P3",
        "EEG-Pz": "Pz",
        "EEG-P4": "P4",
        "EEG-P8": "P8",
        "EEG-PO7": "PO7",
        "EEG-PO3": "PO3",
        "EEG-POz": "POz",
        "EEG-PO4": "PO4",
        "EEG-PO8": "PO8",
        "EEG-O1": "O1",
        "EEG-Oz": "Oz",
        "EEG-O2": "O2",
        "EEG-A1": "A1",
        "EEG-A2": "A2",
        "EEG-MASTOID": "A1",
        "EEG-REF": "Cz",  # Common reference assumption
        "EOG-left": "EOG-L",
        "EOG-right": "EOG-R",
        "EOG-up": "EOG-U",
        "EOG-down": "EOG-D",
        "EMG-chin": "Chin",
        "EMG-limb": "Limb",
        "Status": "STI 014",
    }

    for ch in ch_names:
        if ch in alias_map and ch != alias_map[ch]:
            rename_map[ch] = alias_map[ch]

    if rename_map:
        # Only rename if we have valid targets
        valid_renames = {}
        for old, new in rename_map.items():
            if new in ch_names or new in _STANDARD_64_CHANNELS:
                valid_renames[old] = new
        if valid_renames:
            mne.rename_channels(raw.info, valid_renames)

    return raw


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard 10-20 montage.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with montage set if possible.
    """
    try:
        # Try standard 1020 montage
        montage = mne.channels.make_standard_montage("standard_1020")
        # Get current channel names
        current_chs = set(raw.ch_names)
        montage_chs = set(montage.ch_names)

        # Find intersection
        common_chs = current_chs & montage_chs

        if len(common_chs) >= 20:  # Require at least 20 matching channels
            raw.set_montage(montage, on_missing="ignore")
        else:
            # Try biosemi 64 if standard 1020 doesn't match
            try:
                montage = mne.channels.make_standard_montage("biosemi64")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass
    except Exception:
        pass

    return raw


def _process_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Process and clean annotations.

    - Exclude boundary markers (EEGLAB admin)
    - Exclude key press events
    - Keep only RS_EC and RS_EO events

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data with annotations.

    Returns
    -------
    mne.io.BaseRaw
        Raw object with cleaned annotations.
    """
    if raw.annotations is None or len(raw.annotations) == 0:
        return raw

    # Get annotation descriptions
    descs = np.array([str(d) for d in raw.annotations.description])

    # Create mask for events to keep
    keep_mask = np.ones(len(descs), dtype=bool)

    for i, desc in enumerate(descs):
        desc_lower = desc.lower()
        # Exclude boundary markers
        if "boundary" in desc_lower:
            keep_mask[i] = False
        # Exclude key press/release events
        elif "pressed" in desc_lower or "released" in desc_lower:
            keep_mask[i] = False
        # Only keep RS_EC and RS_EO events
        elif not (desc.startswith("RS_EC") or desc.startswith("RS_EO")):
            # Keep events that might be variants
            if "eyes-closed" in desc_lower or "eyes closed" in desc_lower:
                pass  # Keep
            elif "eyes-open" in desc_lower or "eyes open" in desc_lower:
                pass  # Keep
            else:
                keep_mask[i] = False

    # Apply mask
    if not np.all(keep_mask):
        onset = raw.annotations.onset[keep_mask]
        duration = raw.annotations.duration[keep_mask]
        description = raw.annotations.description[keep_mask]
        if len(onset) > 0:
            raw.set_annotations(
                mne.Annotations(
                    onset=onset,
                    duration=duration,
                    description=description,
                )
            )

    return raw


class OpenNeuroDS005305Kernel:
    """Stage1 kernel for OpenNeuro DS005305 dataset."""

    KERNEL_ID: str = "openneuro-ds005305-stage1"

    def __init__(self):
        """Initialize kernel with dataset-level caches."""
        self._subject_dict: Dict[str, Dict[str, str]] = {}
        self._dataset_root: Optional[str] = None

    def apply(
        self,
        udataset,
        raw: mne.io.BaseRaw,
        row,
    ) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least file path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations.
        """
        # Get dataset root path
        file_path = getattr(row, "File Path", None)
        if file_path is None and hasattr(row, "get"):
            file_path = row.get("File Path", None)

        if file_path and self._dataset_root is None:
            # Infer dataset root from file path
            self._dataset_root = os.path.dirname(file_path)
            while self._dataset_root and not os.path.exists(
                os.path.join(self._dataset_root, "participants.tsv")
            ):
                parent = os.path.dirname(self._dataset_root)
                if parent == self._dataset_root:
                    break
                self._dataset_root = parent

        # Load participant metadata
        if self._dataset_root and not self._subject_dict:
            self._subject_dict = _load_participants_tsv(self._dataset_root)

        # Get subject metadata
        subject_meta = _get_subject_metadata(row, self._subject_dict, self._dataset_root or "")

        # Rename channels to standard names (before set_montage)
        raw = _detect_and_rename_channels(raw)

        # Set standard 10-20 montage
        raw = _set_montage_if_possible(raw)

        # Process annotations (exclude boundary and key press events)
        raw = _process_annotations(raw)

        # Build description JSON
        original_desc = raw.info.get("description", "")
        if isinstance(original_desc, dict):
            original_desc = json.dumps(original_desc)

        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_meta.get("age", "unknown"),
                "sex": subject_meta.get("sex", "unknown"),
                "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
                "cap": _DEVICE_INFO.get("cap", "unknown"),
                "handedness": subject_meta.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Set channel types if needed
        current_chs = set(raw.ch_names)
        eog_chs = {"EOG-L", "EOG-R", "EOG-U", "EOG-D", "EOG-left", "EOG-right"}
        emg_chs = {"Chin", "Limb", "EMG-chin", "EMG-limb"}
        stim_chs = {"STI 014", "Status", "Trigger"}

        type_updates = {}
        for ch in current_chs:
            if ch in eog_chs:
                type_updates[ch] = "eog"
            elif ch in emg_chs:
                type_updates[ch] = "emg"
            elif ch in stim_chs:
                type_updates[ch] = "stim"

        if type_updates:
            try:
                raw.set_channel_types(type_updates)
            except Exception:
                pass

        return raw


KERNEL = OpenNeuroDS005305Kernel()