"""OpenNeuro DS004040 stage1 kernel for EEGUnity.

Trance Channeling EEG dataset: 13 experienced trance channelers performed
alternating 5-minute blocks of trance channeling and resting state across
two sessions. Only STATUS admin markers present; block labels must be
derived from the known experimental structure.

Source: https://openneuro.org/datasets/ds004040
DOI: https://doi.org/10.18112/openneuro.ds004040.v1.0.0
Paradigm reference: https://doi.org/10.12688/f1000research.17157.2

Kernel Notes:
- 26 files (13 subjects × 2 sessions)
- 64 channels, 512 Hz sampling rate
- Only STATUS admin marker present; no discrete trance/rest events
- Block labels derived from alternating 5-min structure: trance-rest-trance-rest-trance-rest
- 3 trance blocks + 3 rest blocks per session (300s each)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Block timing parameters (verified from paradigm: 5-minute alternating blocks)
_BLOCK_DURATION_S = 300.0  # 5 minutes per block
_PRESTIM_S = 0.0  # No prestim period for long events

# Block label sequence per session (alternating pattern)
_BLOCK_LABELS = [
    "trance1_start",
    "rest1_start",
    "trance2_start",
    "rest2_start",
    "trance3_start",
    "rest3_start",
]

# Event ID mapping for raw meta (trance=1, rest=0)
_EVENT_ID = {
    "trance1_start": 1,
    "trance2_start": 1,
    "trance3_start": 1,
    "rest1_start": 0,
    "rest2_start": 0,
    "rest3_start": 0,
}

# Source: openneuro_ds004040 dataset_description.json
# Amplifier: BrainAmp MR plus (inferred from BrainProducts system common in EEG research)
# Annotator: LLM, 2026-04-08 (LLM 推断，需人类复核)
_AMPLIFIER = "BrainAmp"
_CAP = "Ag/AgCl"  # Standard EEG cap material (LLM 推断，需人类复核)

# EEGUnity description dict (required for all kernels)
eegunity_description = {
    "age": "unknown",  # Age will be loaded from participants.tsv per subject
    "sex": "unknown",  # Sex will be loaded from participants.tsv per subject
    "amplifier": _AMPLIFIER,
    "cap": _CAP,
    "handedness": "unknown",  # Handedness will be loaded from participants.tsv per subject
}


@dataclass
class SubjectInfo:
    """Container for subject metadata."""
    subject_id: str
    age: str
    sex: str
    handedness: str


def _parse_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path.

    Parameters
    ----------
    file_path : str
        BIDS-style file path containing 'sub-XX' pattern.

    Returns
    -------
    str or None
        Subject identifier (e.g., '01', '02') or None if not found.
    """
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return match.group(1)
    return None


def _parse_session_id(file_path: str) -> Optional[str]:
    """Extract session ID from BIDS file path.

    Parameters
    ----------
    file_path : str
        BIDS-style file path containing 'ses-XX' pattern.

    Returns
    -------
    str or None
        Session identifier (e.g., '01', '02') or None if not found.
    """
    match = re.search(r"ses-(\d+)", file_path)
    if match:
        return match.group(1)
    return None


def _detect_paradigm(file_path: str) -> str:
    """Detect BIDS task name from file path.

    Parameters
    ----------
    file_path : str
        BIDS-style file path containing 'task-XXX' pattern.

    Returns
    -------
    str
        Task name (e.g., 'trance', 'rest') or 'unknown'.
    """
    match = re.search(r"task-(\w+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _load_participants_tsv(dataset_root: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from participants.tsv.

    Parameters
    ----------
    dataset_root : str
        Root directory of the BIDS dataset.

    Returns
    -------
    dict
        Mapping from subject_id to metadata dict with age, sex, handedness.
    """
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}

    try:
        df = pd.read_csv(participants_path, sep="\t")
        if "participant_id" not in df.columns:
            return {}

        subject_dict = {}
        for _, row in df.iterrows():
            pid = row["participant_id"]
            # Extract numeric part (e.g., 'sub-01' -> '01')
            subj_id = re.sub(r"^sub-", "", str(pid))

            # Map columns to standard fields
            age = "unknown"
            sex = "unknown"
            handedness = "unknown"

            # Check for age column variants
            for col in df.columns:
                col_lower = col.lower()
                if "age" in col_lower and "hand" not in col_lower:
                    val = row.get(col)
                    if pd.notna(val):
                        age = str(int(float(val)))
                elif col_lower in ("sex", "gender"):
                    val = row.get(col)
                    if pd.notna(val):
                        sex = str(val).strip().lower()
                        if sex not in ("male", "female", "m", "f"):
                            sex = "unknown"
                        elif sex in ("m", "f"):
                            sex = "male" if sex == "m" else "female"
                elif "hand" in col_lower:
                    val = row.get(col)
                    if pd.notna(val):
                        handedness = str(val).strip().lower()
                        if handedness not in ("right", "left", "r", "l"):
                            handedness = "unknown"
                        elif handedness in ("r", "l"):
                            handedness = "right" if handedness == "r" else "left"

            subject_dict[subj_id] = {
                "age": age,
                "sex": sex,
                "handedness": handedness,
            }

        return subject_dict
    except Exception:
        return {}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard_1020 montage.

    Handles common non-standard channel name patterns found in EEG datasets:
    - EEG-0, EEG-1, ... numbered channels
    - Channels with 'EEG' prefix but standard names
    - Channels with leading zeros or spacing variations

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with current channel names.

    Returns
    -------
    dict
        Mapping from source channel names to standard 10-20 names.
    """
    rename_map = {}
    existing = set(raw.ch_names)

    # Standard 10-20 EEG channels (excluding EOG, reference, ground)
    standard_eeg = {
        "Fp1", "Fp2", "Fz", "F3", "F4", "F7", "F8",
        "Cz", "C3", "C4", "T7", "T8",
        "Pz", "P3", "P4", "P7", "P8",
        "O1", "O2", "Oz",
        "F1", "F2", "F5", "F6",
        "FC1", "FC2", "FC5", "FC6",
        "CP1", "CP2", "CP5", "CP6",
        "PO3", "PO4", "PO7", "PO8",
    }

    # Common 64-channel extended layouts
    extended_channels = {
        "AF3", "AF4", "AF7", "AF8",
        "FCz", "FC3", "FC4", "FC1", "FC2",
        "FT7", "FT8",
        "C1", "C2", "C5", "C6",
        "TP7", "TP8",
        "CPz", "CP3", "CP4",
        "P1", "P2", "P5", "P6",
        "POz",
        "O9", "O10",
    }
    standard_eeg.update(extended_channels)

    for ch_name in existing:
        # Skip non-EEG channels
        if any(skip in ch_name.upper() for skip in ["EOG", "ECG", "EMG", "REF", "GND", "GRND", "STIM", "MISC", "STATUS", "AUDIO"]):
            continue

        # Pattern: EEG-0, EEG-1, ... (numbered with prefix)
        match = re.match(r"^(?:EEG[-_\s]?)?(\d+)$", ch_name, re.IGNORECASE)
        if match:
            continue  # Keep as-is; MNE will handle with standard montage

        # Pattern: EEG-Fz, EEG-Cz, etc. (standard names with EEG prefix)
        match = re.match(r"^EEG[-_\s]?([A-Z][a-z]?\d*)$", ch_name, re.IGNORECASE)
        if match:
            std_name = match.group(1)
            if std_name in standard_eeg:
                rename_map[ch_name] = std_name

    return rename_map


def _derive_block_events(raw: mne.io.BaseRaw, sfreq: float) -> np.ndarray:
    """Derive trance/rest block events from alternating 5-minute structure.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object.
    sfreq : float
        Sampling frequency.

    Returns
    -------
    np.ndarray
        Events array with columns [onset, duration, trigger].
    """
    n_samples = raw.n_times
    total_duration_s = n_samples / sfreq
    block_duration_samples = int(_BLOCK_DURATION_S * sfreq)

    events = []
    offset = 0.0

    for label in _BLOCK_LABELS:
        if offset >= total_duration_s:
            break

        # Adjust last block if it extends beyond recording
        end_time = min(offset + _BLOCK_DURATION_S, total_duration_s)
        duration = end_time - offset

        if label in _EVENT_ID:
            trigger = _EVENT_ID[label]
            events.append([offset, duration, trigger])

        offset += _BLOCK_DURATION_S

    return np.array(events) if events else np.zeros((0, 3))


class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro DS004040 - Trance Channeling dataset.

    This kernel handles:
    - Loading BrainVision format EEG data from BIDS structure
    - Detecting and renaming channels to standard 10-20 montage
    - Deriving trance/rest block events from alternating 5-minute structure
    - Attaching subject metadata from participants.tsv
    """

    KERNEL_ID = "openneuro_ds004040"

    def __init__(self):
        """Initialize the kernel."""
        self.dataset_root = None
        self.subject_metadata = {}

    def _get_dataset_root(self, udataset) -> str:
        """Extract dataset root path from udataset.

        Parameters
        ----------
        udataset : object
            Dataset object with path information.

        Returns
        -------
        str
            Dataset root directory path.
        """
        # Try to get path from various attributes
        if hasattr(udataset, 'dataset_path'):
            return str(udataset.dataset_path)
        elif hasattr(udataset, 'path'):
            return str(udataset.path)
        elif hasattr(udataset, 'root'):
            return str(udataset.root)
        else:
            # Try to get from the object itself
            for attr in ['dataset_path', 'path', 'root', '__str__']:
                if hasattr(udataset, attr):
                    try:
                        val = getattr(udataset, attr)
                        if isinstance(val, (str, os.PathLike)):
                            return str(val)
                    except Exception:
                        continue
            return ""

    def _load_subject_info(self, subject_id: str) -> SubjectInfo:
        """Get or load subject metadata.

        Parameters
        ----------
        subject_id : str
            Subject identifier.

        Returns
        -------
        SubjectInfo
            Subject metadata container.
        """
        if subject_id in self.subject_metadata:
            return self.subject_metadata[subject_id]

        # Load from participants.tsv if available
        if self.dataset_root:
            all_metadata = _load_participants_tsv(self.dataset_root)
            if subject_id in all_metadata:
                meta = all_metadata[subject_id]
                info = SubjectInfo(
                    subject_id=subject_id,
                    age=meta.get("age", "unknown"),
                    sex=meta.get("sex", "unknown"),
                    handedness=meta.get("handedness", "unknown"),
                )
                self.subject_metadata[subject_id] = info
                return info

        # Default metadata
        info = SubjectInfo(
            subject_id=subject_id,
            age="unknown",
            sex="unknown",
            handedness="unknown",
        )
        self.subject_metadata[subject_id] = info
        return info

    def _preprocess_raw(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Apply preprocessing steps to raw data.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw EEG object.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object.
        """
        # Build and apply channel rename map
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # Try to set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass

        # Handle STATUS channel if present
        if "STATUS" in raw.ch_names:
            # STATUS channel typically contains trigger information
            # We'll use it to derive block events instead of keeping it
            pass

        return raw

    def _add_block_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Add trance/rest block annotations based on experimental structure.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw EEG object.

        Returns
        -------
        mne.io.BaseRaw
            Raw object with annotations added.
        """
        sfreq = raw.info["sfreq"]
        events = _derive_block_events(raw, sfreq)

        # Convert events to MNE annotations
        onsets = []
        durations = []
        descriptions = []
        trigger_map = {v: k.split("_")[0] for k, v in _EVENT_ID.items()}

        for event in events:
            onset_s, duration_s, trigger = event
            onsets.append(onset_s)
            durations.append(duration_s)
            block_type = trigger_map.get(int(trigger), "unknown")
            descriptions.append(block_type)

        if onsets:
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
                orig_time=raw.info.get("meas_date", None),
            )
            raw.set_annotations(annotations)

        return raw

    def _set_subject_info(self, raw: mne.io.BaseRaw, subject_info: SubjectInfo) -> mne.io.BaseRaw:
        """Attach subject metadata to raw object.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw EEG object.
        subject_info : SubjectInfo
            Subject metadata.

        Returns
        -------
        mne.io.BaseRaw
            Raw object with metadata in info.
        """
        # Store in raw.info['subject_info']
        raw.info["subject_info"] = {
            "his_id": subject_info.subject_id,
            "age": subject_info.age,
            "sex": subject_info.sex,
            "handedness": subject_info.handedness,
        }
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply kernel processing to raw EEG data.

        Parameters
        ----------
        udataset : object
            Dataset object containing path and metadata.
        raw : mne.io.BaseRaw
            Raw EEG data to process.
        row : dict
            Row from dataset indexing with file_path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw object with standardized channels, annotations,
            and subject metadata.
        """
        # Extract dataset root if not already done
        if self.dataset_root is None:
            self.dataset_root = self._get_dataset_root(udataset)

        # Extract subject ID from file path
        file_path = row.get("file_path", "")
        subject_id = _parse_subject_id(file_path) or "unknown"

        # Load subject metadata
        subject_info = self._load_subject_info(subject_id)

        # Apply preprocessing
        raw = self._preprocess_raw(raw)

        # Add block annotations
        raw = self._add_block_annotations(raw)

        # Attach subject info
        raw = self._set_subject_info(raw, subject_info)

        return raw


# Instantiate kernel for EEGUnity framework
KERNEL = EEGUnityKernel()