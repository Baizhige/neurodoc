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
                continue

        # Already standard name
        base_name = re.sub(r"[-_\s]", "", ch_name)
        if base_name in standard_eeg or ch_name in standard_eeg:
            continue

    return rename_map


def _derive_block_annotations(raw: mne.io.BaseRaw, n_blocks: int = 6) -> mne.Annotations:
    """Derive trance/rest block annotations from known experimental timing.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object with measurement info.
    n_blocks : int
        Number of blocks per session (default 6: 3 trance + 3 rest).

    Returns
    -------
    mne.Annotations
        Annotations with onset, duration, and description for each block.
    """
    sfreq = raw.info["sfreq"]
    n_samp = raw.n_times
    total_dur = n_samp / sfreq

    # Check if total duration matches expected block structure
    expected_dur = n_blocks * _BLOCK_DURATION_S
    if abs(total_dur - expected_dur) > 10.0:  # Allow 10s tolerance
        # Adjust n_blocks based on actual duration
        n_blocks = max(1, int(round(total_dur / _BLOCK_DURATION_S)))

    annotations = []
    for i in range(n_blocks):
        onset_s = i * _BLOCK_DURATION_S
        # Alternate: odd indices = trance, even = rest (1-indexed)
        if (i + 1) % 2 == 1:
            desc = "trance"
        else:
            desc = "rest"
        annotations.append((onset_s, _BLOCK_DURATION_S, desc))

    return mne.Annotations(
        onset=[a[0] for a in annotations],
        duration=[a[1] for a in annotations],
        description=[a[2] for a in annotations],
        ch_names=[None] * len(annotations),
        orig_time=raw.info["meas_date"],
    )


class EEGUnityKernel:
    """Kernel for OpenNeuro DS004040 (Trance Channeling EEG dataset).

    This kernel handles the Stage 1 processing for the Trance Channeling
    dataset, which contains EEG recordings from 13 subjects performing
    alternating trance channeling and resting state blocks.

    Parameters
    ----------
    dataset_root : str
        Root directory of the OpenNeuro ds004040 dataset.
    """

    def __init__(self, dataset_root: str = "<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds004040"):
        self.dataset_root = dataset_root
        self.participants_data = _load_participants_tsv(dataset_root)

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Apply standard 10-20 montage to raw data.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object with EEG channels.

        Returns
        -------
        mne.io.BaseRaw
            Raw object with montage applied.
        """
        # Build rename map for non-standard channel names
        rename_map = _build_channel_rename_map(raw)

        if rename_map:
            print(f"[DEBUG] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # Get EEG channels (exclude non-EEG)
        eeg_chs = mne.pick_types(raw.info, eeg=True, meg=False, eog=False, ecg=False, emg=False)

        if len(eeg_chs) == 0:
            print("[WARNING] No EEG channels found after filtering")
            return raw

        # Try to set standard 1020 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[WARNING] Could not set standard montage: {e}")

        return raw

    def _set_reference(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set reference to average.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object with EEG channels.

        Returns
        -------
        mne.io.BaseRaw
            Raw object with average reference.
        """
        try:
            # First, ensure we have EEG channels
            eeg_picks = mne.pick_types(raw.info, eeg=True, meg=False, eog=False, ecg=False, emg=False)
            if len(eeg_picks) == 0:
                print("[WARNING] No EEG channels found for re-referencing")
                return raw

            # Set average reference
            raw.set_eeg_reference(ref_channels="average")
        except Exception as e:
            print(f"[WARNING] Could not set average reference: {e}")

        return raw

    def _set_subject_info(self, raw: mne.io.BaseRaw, subject_info: SubjectInfo) -> mne.io.BaseRaw:
        """Set subject information in raw info.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object.
        subject_info : SubjectInfo
            Subject information container.

        Returns
        -------
        mne.io.BaseRaw
            Raw object with subject info set.
        """
        # Map sex to MNE-compatible format
        sex = subject_info.sex.lower() if subject_info.sex else "unknown"
        if sex not in ("male", "female"):
            sex = "unknown"

        # Map handedness to MNE-compatible format (use 'hand' key)
        hand = subject_info.handedness.lower() if subject_info.handedness else "unknown"
        if hand not in ("right", "left", "ambidextrous"):
            hand = "unknown"

        # Build subject_info dict with ONLY MNE-supported fields
        # MNE SubjectInfo only supports: id, sex, hand, and a few others - NOT 'age'
        subject_info_dict = {
            "id": subject_info.subject_id,
            "sex": sex,
            "hand": hand,
        }

        raw.info["subject_info"] = subject_info_dict
        return raw

    def _load_raw_file(self, file_path: str, row: pd.Series) -> mne.io.BaseRaw:
        """Load raw EEG file.

        Parameters
        ----------
        file_path : str
            Path to EEG file (.set format).
        row : pd.Series
            Row from dataset dataframe.

        Returns
        -------
        mne.io.BaseRaw
            Loaded raw object.
        """
        # Load .set file using MNE
        raw = mne.io.read_raw_eeglab(file_path, preload=True, verbose=False)

        return raw

    def _infer_admin_channels(self, raw: mne.io.BaseRaw) -> List[str]:
        """Infer admin/status channel names from raw data.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object.

        Returns
        -------
        list of str
            List of inferred admin channel names.
        """
        admin_channels = []

        # Common status/admin channel patterns
        patterns = ["STATUS", "Status", "status", "Trigger", "TRIGGER", "MkRange", "MRK", "Event"]

        for ch in raw.ch_names:
            for pattern in patterns:
                if pattern in ch:
                    admin_channels.append(ch)
                    break

        return admin_channels

    def _extract_status_events(self, raw: mne.io.BaseRaw) -> pd.DataFrame:
        """Extract events from STATUS channel.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object with STATUS channel.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: onset, duration, description.
        """
        # Find STATUS channel
        status_ch = None
        for ch in raw.ch_names:
            if "STATUS" in ch.upper():
                status_ch = ch
                break

        if status_ch is None:
            return pd.DataFrame(columns=["onset", "duration", "description"])

        # Get STATUS channel data
        status_data = raw.get_data(picks=[status_ch])[0]

        # Find transitions (events)
        diff = np.diff(status_data)
        onsets = np.where(diff != 0)[0] / raw.info["sfreq"]
        values = status_data[np.where(diff != 0)[0] + 1]

        events = []
        for onset, val in zip(onsets, values):
            events.append({
                "onset": onset,
                "duration": 0.0,
                "description": f"status_{int(val)}",
                "value": int(val),
            })

        return pd.DataFrame(events)

    def apply(self, udataset, raw: mne.io.BaseRaw, row: pd.Series) -> mne.io.BaseRaw:
        """Apply Stage 1 kernel processing to raw EEG data.

        Parameters
        ----------
        udataset : object
            Dataset object (unused, for compatibility).
        raw : mne.io.BaseRaw
            Raw EEG object to process.
        row : pd.Series
            Row from dataset dataframe with file_path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw object.
        """
        # Extract file path
        file_path = row.get("file_path", "")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"EEG file not found: {file_path}")

        # Reload raw to ensure clean state
        raw = self._load_raw_file(file_path, row)

        # Get subject info
        subject_id = _parse_subject_id(file_path)
        session_id = _parse_session_id(file_path)
        task = _detect_paradigm(file_path)

        # Load subject metadata from participants.tsv
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"

        if subject_id and subject_id in self.participants_data:
            meta = self.participants_data[subject_id]
            age = meta.get("age", "unknown")
            sex = meta.get("sex", "unknown")
            handedness = meta.get("handedness", "unknown")

        subject_info = SubjectInfo(
            subject_id=subject_id or "unknown",
            age=age,
            sex=sex,
            handedness=handedness,
        )

        # Set subject info
        raw = self._set_subject_info(raw, subject_info)

        # Set measurement info
        raw.info["experimenter"] = "unknown"
        raw.info["device_info"] = _AMPLIFIER
        raw.info["coil_transformation_time"] = None
        raw.info["utc_offset"] = None

        # Set standard 1020 montage
        raw = self._set_montage(raw)

        # Set average reference
        raw = self._set_reference(raw)

        # Infer and keep admin channels but don't process them
        admin_channels = self._infer_admin_channels(raw)
        if admin_channels:
            print(f"[DEBUG] Found admin channels: {admin_channels}")

        # Derive block annotations from known experimental timing
        annotations = _derive_block_annotations(raw)
        raw.set_annotations(annotations)

        # Handle annotations description normalization
        if raw.annotations:
            descrips = set(raw.annotations.description)
            print(f"[DEBUG] Annotations descriptions: {descrips}")

        return raw


# Kernel instance for EEGUnity
KERNEL = EEGUnityKernel()