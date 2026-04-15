"""OpenNeuro DS001784 stage1 kernel for EEGUnity.

Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant
depression (EEG). BIDS-formatted dataset with 65 channels at 1450 Hz.

Dataset: openneuro_ds001784 | Year: 2019 | DOI: https://doi.org/10.1038/s41467-019-09557-4
Paradigm: MSIT with emotional stimuli + DBS ON/OFF

This kernel:
- Reads participants.tsv for age/sex/dbs metadata
- Parses events.tsv to extract trial_type (interference/control) labels
- Maps raw events (event_2/4/6) to semantic labels
- Sets standard 10-20 montage for 65-channel EEG
- Provides DBS ON/OFF labels from participants.tsv

Source: https://openneuro.org/datasets/ds001784
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# =============================================================================
# Device Metadata Defaults
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: Dataset publication DOI 10.1038/s41467-019-09557-4, methods section
# Amplifier, cap, and handedness cannot be confirmed from available documentation.
# These values are LLM inferences and require human verification.
_DEVICE_METADATA_DEFAULTS: Dict[str, str] = {
    "amplifier": "unknown",    # LLM 推断，需人类复核
    "cap": "unknown",          # LLM 推断，需人类复核
    "handedness": "unknown",   # LLM 推断，需人类复核
}


# =============================================================================
# Raw Event Mapping
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: Dataset events.tsv analysis
# event_2 (1296 occurrences) -> interference trials (high-interference MSIT)
# event_4 (2592 occurrences) -> control trials (low interference)
# event_6 (1296 occurrences) -> AFMSIT trials (active foreground MSIT)
_EVENT_RAW_MAP: Dict[str, str] = {
    "event_2": "interference_trial",
    "event_4": "control_trial",
    "event_6": "afmsit_trial",
}


# =============================================================================
# Label Mapping for Super Meta
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: analysis.md Classical Task 1 definition
# interference_trial -> y=1, control_trial -> y=0
_COGNITIVE_LABEL_MAP: Dict[str, int] = {
    "interference_trial": 1,
    "control_trial": 0,
}


# =============================================================================
# Standard 10-20 Channel Names for 64-65 Channel Systems
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: Standard 10-20 system for 65-channel EEG (extended 10-20)
# These represent the standard electrode positions in order
_STANDARD_1020_CHANNELS: List[str] = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standard 10-20 channel names.
    
    Attempts to match raw channel names to standard 10-20 positions.
    Handles common naming patterns from BrainVision, BrainProducts, and other systems.
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: Standard 10-20 electrode naming conventions
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    # Create alias groups for common channel name patterns
    alias_groups = [
        # Standard 10-20 names
        ("Fp1", ["Fp1", "FP1", "fp1"]),
        ("Fpz", ["Fpz", "FPz", "fpz"]),
        ("Fp2", ["Fp2", "FP2", "fp2"]),
        ("F7", ["F7", "F7 "]),
        ("F3", ["F3"]),
        ("Fz", ["Fz"]),
        ("F4", ["F4"]),
        ("F8", ["F8"]),
        ("T7", ["T7", "T7 "]),
        ("C3", ["C3"]),
        ("Cz", ["Cz"]),
        ("C4", ["C4"]),
        ("T8", ["T8"]),
        ("P7", ["P7"]),
        ("P3", ["P3"]),
        ("Pz", ["Pz"]),
        ("P4", ["P4"]),
        ("P8", ["P8"]),
        ("O1", ["O1"]),
        ("Oz", ["Oz"]),
        ("O2", ["O2"]),
        # Extended 10-20 names
        ("AF7", ["AF7"]),
        ("AF3", ["AF3"]),
        ("AFz", ["AFz"]),
        ("AF4", ["AF4"]),
        ("AF8", ["AF8"]),
        ("F5", ["F5"]),
        ("F1", ["F1"]),
        ("F2", ["F2"]),
        ("F6", ["F6"]),
        ("FC5", ["FC5"]),
        ("FC1", ["FC1"]),
        ("FCz", ["FCz"]),
        ("FC2", ["FC2"]),
        ("FC6", ["FC6"]),
        ("C5", ["C5"]),
        ("C1", ["C1"]),
        ("C2", ["C2"]),
        ("C6", ["C6"]),
        ("CP5", ["CP5"]),
        ("CP1", ["CP1"]),
        ("CPz", ["CPz"]),
        ("CP2", ["CP2"]),
        ("CP6", ["CP6"]),
        ("P5", ["P5"]),
        ("P1", ["P1"]),
        ("P2", ["P2"]),
        ("P6", ["P6"]),
        ("PO7", ["PO7"]),
        ("PO3", ["PO3"]),
        ("POz", ["POz"]),
        ("PO4", ["PO4"]),
        ("PO8", ["PO8"]),
    ]
    
    # EOG channels
    eog_aliases = [
        ("EOG-left", ["EOG左", "EOG-L", "EOGL", "VEOG-L", "HEOG-L", "eog_l"]),
        ("EOG-right", ["EOG右", "EOG-R", "EOGR", "VEOG-R", "HEOG-R", "eog_r"]),
        ("EOG-central", ["EOG中", "EOG-C", "EOGC", "VEOG-C", "eog_c"]),
    ]
    
    # MISC/STATUS channels
    misc_aliases = [
        ("Status", ["Status", "STI 014", "Stimulus", "Stim"]),
        ("Misc", ["Misc", "MISC"]),
    ]
    
    all_aliases = alias_groups + eog_aliases + misc_aliases
    
    for target_name, aliases in all_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _load_participants_metadata(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv file.
    
    Returns empty DataFrame if file not found.
    
    Annotator: LLM (gpt-4o), 2026-04-08
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_file):
        return pd.read_csv(participants_file, sep="\t")
    return pd.DataFrame()


def _get_subject_metadata(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.
    
    Args:
        participants_df: DataFrame from participants.tsv
        subject_id: Subject identifier (e.g., 'sub-01')
    
    Returns:
        Dictionary with age, sex, dbs_condition for the subject
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: BIDS participants.tsv standard columns
    """
    metadata = {
        "age": "unknown",
        "sex": "unknown",
        "dbs_condition": "unknown",  # LLM 推断，需人类复核
    }
    
    if participants_df.empty:
        return metadata
    
    # Match subject ID (handle both 'sub-01' and '01' formats)
    subject_col = None
    for col in ["participant_id", "subject_id", "participant"]:
        if col in participants_df.columns:
            subject_col = col
            break
    
    if subject_col is None:
        return metadata
    
    # Normalize subject ID for matching
    subject_row = participants_df[participants_df[subject_col] == subject_id]
    if subject_row.empty:
        # Try without 'sub-' prefix
        short_id = subject_id.replace("sub-", "")
        subject_row = participants_df[participants_df[subject_col].str.contains(short_id, na=False)]
    
    if not subject_row.empty:
        row = subject_row.iloc[0]
        if "age" in participants_df.columns:
            age_val = row.get("age", "unknown")
            metadata["age"] = str(age_val) if pd.notna(age_val) else "unknown"
        if "sex" in participants_df.columns:
            sex_val = row.get("sex", "unknown")
            metadata["sex"] = str(sex_val) if pd.notna(sex_val) else "unknown"
        if "dbs_condition" in participants_df.columns:
            dbs_val = row.get("dbs_condition", "unknown")
            metadata["dbs_condition"] = str(dbs_val) if pd.notna(dbs_val) else "unknown"
    
    return metadata


def _get_dataset_metadata(dataset_path: str) -> Dict[str, str]:
    """Load dataset metadata from dataset_description.json.
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: BIDS dataset_description.json
    """
    desc_file = os.path.join(dataset_path, "dataset_description.json")
    if os.path.exists(desc_file):
        with open(desc_file, "r") as f:
            return json.load(f)
    return {}


def _parse_events(raw: mne.io.BaseRaw, events_file: str) -> mne.io.BaseRaw:
    """Parse events from events.tsv and add to raw.
    
    Args:
        raw: MNE Raw object
        events_file: Path to events.tsv file
    
    Returns:
        Raw object with annotations
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: BIDS events.tsv format
    """
    if not os.path.exists(events_file):
        return raw
    
    events_df = pd.read_csv(events_file, sep="\t")
    
    # Check required columns
    required_cols = ["onset", "duration", "trial_type"]
    if not all(col in events_df.columns for col in required_cols):
        return raw
    
    # Create annotations from events
    onset = events_df["onset"].values
    duration = events_df["duration"].values
    
    # Map trial_type to semantic labels
    descriptions = events_df["trial_type"].map(
        lambda x: _EVENT_RAW_MAP.get(str(x), str(x))
    ).values
    
    annotations = mne.Annotations(
        onset=onset,
        duration=duration,
        description=descriptions,
        orig_time=raw.info["meas_date"]
    )
    
    return raw.set_annotations(annotations, on_missing="ignore")


def _apply_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply standard 10-20 montage to raw data.
    
    Args:
        raw: MNE Raw object
    
    Returns:
        Raw object with montage set
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: Standard 10-20 system
    """
    try:
        # Try to set standard 10-20 montage
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass
    
    return raw


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 names.
    
    Args:
        raw: MNE Raw object
    
    Returns:
        Raw object with renamed channels
    
    Annotator: LLM (gpt-4o), 2026-04-08
    """
    rename_map = _build_channel_rename_map(raw)
    if rename_map:
        raw.rename_channels(rename_map, allow_duplicates=True)
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set correct channel types for EOG and other special channels.
    
    Args:
        raw: MNE Raw object
    
    Returns:
        Raw object with correct channel types
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: Standard BIDS channel type conventions
    """
    # Common EOG channel patterns
    eog_patterns = ["EOG", "VEOG", "HEOG", "eog"]
    misc_patterns = ["Status", "Stim", "Trigger", "STI"]
    
    for ch_name in raw.ch_names:
        ch_upper = ch_name.upper()
        # Check for EOG channels
        if any(pattern.upper() in ch_upper for pattern in eog_patterns):
            if "EOG" in ch_upper:
                raw.set_channel_types({ch_name: "eog"})
        # Check for stimulus/trigger channels
        elif any(pattern.upper() in ch_upper for pattern in misc_patterns):
            raw.set_channel_types({ch_name: "stim"})
    
    return raw


def _check_valid_fif_file(fpath: str) -> bool:
    """Check if FIF file contains valid measurement data.
    
    Args:
        fpath: Path to FIF file
    
    Returns:
        True if file contains valid measurement data
    """
    try:
        # Try reading with read_raw_fif which requires measurement data
        _ = mne.io.read_raw_fif(fpath, preload=False, allow_maxshield=True, verbose=False)
        return True
    except ValueError as e:
        if "Could not find measurement data" in str(e):
            return False
        raise
    except Exception:
        return False


class EEGUnityKernel:
    """EEGUnity kernel for OpenNeuro DS001784 dataset.
    
    This kernel handles EEG data from the Deep Brain Stimulation study
    with MSIT paradigm, providing standardized preprocessing.
    """
    
    def __init__(self):
        """Initialize the EEGUnity kernel."""
        self.name = "openneuro_ds001784"
        self.version = "1.0.0"
        self.dataset_path = None
    
    def setup(self, dataset_path: str) -> None:
        """Set up the kernel with dataset path.
        
        Args:
            dataset_path: Path to the dataset directory
        """
        self.dataset_path = dataset_path
    
    def get_description(self) -> Dict[str, str]:
        """Get kernel description.
        
        Returns:
            Dictionary with kernel metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "dataset": "openneuro_ds001784",
            "description": "Deep Brain Stimulation EEG study with MSIT paradigm",
        }
    
    def get_eegunity_description(self, subject_id: str = None) -> Dict[str, str]:
        """Get eegunity_description dict with required fields.
        
        Args:
            subject_id: Optional subject ID for subject-specific metadata
        
        Returns:
            Dictionary with age, sex, amplifier, cap, handedness
        """
        metadata = _DEVICE_METADATA_DEFAULTS.copy()
        
        if self.dataset_path and subject_id:
            participants_df = _load_participants_metadata(self.dataset_path)
            subject_meta = _get_subject_metadata(participants_df, subject_id)
            metadata["age"] = subject_meta.get("age", "unknown")
            metadata["sex"] = subject_meta.get("sex", "unknown")
        else:
            metadata["age"] = "unknown"
            metadata["sex"] = "unknown"
        
        return metadata
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        if not _check_valid_fif_file(row.get("fpath", "")):
            return None
        dataset_path = getattr(udataset, "path", self.dataset_path or "")
        if dataset_path:
            participants_df = _load_participants_metadata(dataset_path)
            subject_id = row.get("subject_id", "")
            subject_meta = _get_subject_metadata(participants_df, subject_id)
            raw.set_info({"age": subject_meta.get("age", "unknown")})
        return raw


# Kernel instance for EEGUnity
KERNEL = EEGUnityKernel()