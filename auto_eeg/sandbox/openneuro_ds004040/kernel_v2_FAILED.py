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
                continue

        # Pattern: Fz, Cz, Pz, etc. (already standard)
        if ch_name in standard_eeg:
            continue  # Already standard

    return rename_map


def _derive_block_events(raw: mne.io.BaseRaw, session_num: int) -> mne.Annotations:
    """Derive trance/rest block events from experimental structure.

    The experiment uses alternating 5-minute blocks: trance-rest-trance-rest-trance-rest.
    Since only STATUS admin markers are present, we derive events from the known
    experimental structure.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data.
    session_num : int
        Session number (1 or 2).

    Returns
    -------
    mne.Annotations
        Annotations for block start events.
    """
    sfreq = raw.info["sfreq"]
    total_duration = raw.times[-1]

    # Calculate block onsets based on alternating 5-min pattern
    onsets = []
    descriptions = []
    durations = []

    for i, label in enumerate(_BLOCK_LABELS):
        onset_s = i * _BLOCK_DURATION_S

        # Only add if block starts within recording duration
        if onset_s < total_duration:
            onsets.append(onset_s)
            descriptions.append(label)
            durations.append(_BLOCK_DURATION_S)

    annotations = mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=descriptions,
    )
    return annotations


class EEGUnityKernel:
    """EEGUnity stage-1 kernel for OpenNeuro DS004040 (Trance Channeling)."""

    def __init__(self):
        """Initialize kernel with dataset metadata."""
        self.dataset_name = "openneuro_ds004040"
        self.stage = 1
        self.paradigm = "trance_channeling"
        self.sfreq = 512.0
        self.n_channels = 64
        self.n_blocks = 6  # 3 trance + 3 rest per session
        self.block_duration_s = _BLOCK_DURATION_S

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage-1 processing to raw EEG data.

        Parameters
        ----------
        udataset : object
            UDataset object (unused, for compatibility).
        raw : mne.io.BaseRaw
            Raw EEG data to process.
        row : dict
            Metadata row containing file_path and other info.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw data with annotations and standardized channels.
        """
        # Extract metadata from row
        file_path = row.get("file_path", "")

        # Determine session number (ses-01 or ses-02)
        session_num = 1
        match = re.search(r"ses-0*(\d+)", file_path)
        if match:
            session_num = int(match.group(1))

        # Add block event annotations
        annotations = _derive_block_events(raw, session_num)
        raw.set_annotations(annotations)

        # Rename channels to standard 10-20 if needed
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Try to set standard montage (suppress warnings for missing channels)
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            existing_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if existing_channels:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Montage is optional for stage-1

        # Set channel types (ensure EEG type for data channels)
        for ch in raw.ch_names:
            if ch.upper() not in ["STIM", "STATUS", "EOG", "ECG", "EMG", "MISC"]:
                try:
                    raw.set_channel_types({ch: "eeg"})
                except Exception:
                    pass

        # Notch filter for line noise (50/60 Hz)
        try:
            raw.notch_filter(freqs=[50, 60], n_jobs=1, verbose="ERROR")
        except Exception:
            pass  # Skip if filtering fails

        return raw

    def get_description(self, subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Get EEGUnity description metadata.

        Parameters
        ----------
        subject_id : str, optional
            Subject identifier for loading subject-specific metadata.

        Returns
        -------
        dict
            EEGUnity description dictionary with age, sex, amplifier, cap, handedness.
        """
        description = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": "unknown",
            "dataset": self.dataset_name,
            "paradigm": self.paradigm,
            "stage": self.stage,
            "sfreq": self.sfreq,
            "n_channels": self.n_channels,
        }

        # Try to load subject-specific info from participants.tsv
        if subject_id and udataset is not None:
            try:
                root = getattr(udataset, "root_path", None)
                if root and os.path.exists(root):
                    subject_dict = _load_participants_tsv(root)
                    if subject_id in subject_dict:
                        meta = subject_dict[subject_id]
                        description["age"] = meta.get("age", "unknown")
                        description["sex"] = meta.get("sex", "unknown")
                        description["handedness"] = meta.get("handedness", "unknown")
            except Exception:
                pass

        return description


# Global kernel instance for EEGUnity
KERNEL = EEGUnityKernel()