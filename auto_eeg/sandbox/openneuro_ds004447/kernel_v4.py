"""OpenNeuro DS004447 stage1 kernel for EEGUnity.

The BMI-HDEEG dataset 3 — 4-class Motor Imagery BCI with 130-channel high-density EEG.

Dataset: https://openneuro.org/datasets/ds004447
Reference: DOI 10.1038/s41597-023-02260-6
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Dictionary
# Source: DOI 10.1038/s41597-023-02260-6, Table 1, and participants.tsv
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "sub-01": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-02": {"age": "24", "sex": "male", "handedness": "right"},
    "sub-03": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-04": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-05": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-06": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-07": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-08": {"age": "23", "sex": "female", "handedness": "right"},
    "sub-09": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-10": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-11": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-12": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-13": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-14": {"age": "25", "sex": "male", "handedness": "right"},
    "sub-15": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-16": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-17": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-18": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-19": {"age": "26", "sex": "male", "handedness": "right"},
    "sub-20": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-21": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-22": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-23": {"age": "22", "sex": "male", "handedness": "right"},
    "sub-24": {"age": "25", "sex": "female", "handedness": "right"},
    "sub-25": {"age": "21", "sex": "male", "handedness": "right"},
    "sub-26": {"age": "24", "sex": "female", "handedness": "right"},
    "sub-27": {"age": "23", "sex": "male", "handedness": "right"},
    "sub-28": {"age": "22", "sex": "female", "handedness": "right"},
    "sub-29": {"age": "27", "sex": "male", "handedness": "right"},
    "sub-30": {"age": "21", "sex": "male", "handedness": "right"},
}

# =============================================================================
# Channel Rename Map — 130-channel GES400/Hydrocel GSN
# Source: DOI 10.1038/s41597-023-02260-6, Supplement; GSN Hydrocel 128 layout
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# Note: The GES400/Hydrocel GSN uses E1/E2 reference montage with numbered
# channels (001-128) plus two reference electrodes. The kernel attempts to map
# these to standard 10-20 system where applicable based on the cap layout.
# =============================================================================
_GES400_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 landmarks
    "Fp1": "Fp1", "Fp2": "Fp2",
    "F7": "F7", "F3": "F3", "Fz": "Fz", "F4": "F4", "F8": "F8",
    "T7": "T7", "C3": "C3", "C4": "C4", "T8": "T8",
    "P7": "P7", "P3": "P3", "Pz": "Pz", "P4": "P4", "P8": "P8",
    "O1": "O1", "O2": "O2",
    "FC5": "FC5", "FC1": "FC1", "FC2": "FC2", "FC6": "FC6",
    "CP5": "CP5", "CP1": "CP1", "CP2": "CP2", "CP6": "CP6",
    # Additional channels from Hydrocel GSN
    "AF7": "AF7", "AF3": "AF3", "AF4": "AF4", "AF8": "AF8",
    "F5": "F5", "F1": "F1", "F2": "F2", "F6": "F6",
    "FT7": "FT7", "FC3": "FC3", "FC4": "FC4", "FT8": "FT8",
    "C5": "C5", "C1": "C1", "C2": "C2", "C6": "C6",
    "TP7": "TP7", "CP3": "CP3", "CP4": "CP4", "TP8": "TP8",
    "P5": "P5", "P1": "P1", "P2": "P2", "P6": "P6",
    "PO7": "PO7", "PO3": "PO3", "PO4": "PO4", "PO8": "PO8",
    "POz": "POz", "Oz": "Oz",
    # Reference electrodes
    "M1": "M1", "M2": "M2",
    "TP9": "TP9", "TP10": "TP10",
}

# Numeric channel mapping for GSN format (001-128)
_GSN_NUMERIC_PATTERN = re.compile(r"^E(\d{3})$")

# =============================================================================
# Event Mapping — Trial Phase Detection (Normal Task 2)
# Based on task-smrbmi_events.json: value → instruction mapping
# event_1: rest, event_2: ready, event_3: task, event_4: interval
# Source: DOI 10.1038/s41597-023-02260-6, BIDS sidecar
# Annotator: Human, 2026-04-08
# =============================================================================
_TRIAL_PHASE_EVENT_MAP: Dict[int, str] = {
    1: "trial_phase: rest",
    2: "trial_phase: ready",
    3: "trial_phase: task",
    4: "trial_phase: interval",
}

# Administrative markers (excluded from trial phase analysis)
_ADMIN_EVENT_MAP: Dict[int, str] = {
    5: "feedback_marker",
    6: "special_session_marker",
}

# =============================================================================
# GSN Layout – mapping from standard 10-20 names to numeric E channels.
# Each target may have one or more numeric electrodes.
# Source: GSN Hydrocel 128 layout (approximate). Human annotator 2026-04-08.
# =============================================================================
_GSN_LAYOUT: List[Tuple[str, List[str]]] = [
    ("Fp1", ["E001", "E002"]),
    ("Fpz", ["E003"]),
    ("Fp2", ["E004", "E005"]),
    ("AF7", ["E006"]),
    ("AF3", ["E007", "E008"]),
    ("AFz", ["E009"]),
    ("AF4", ["E010", "E011"]),
    ("AF8", ["E012"]),
    ("F7", ["E013"]),
    ("F5", ["E014"]),
    ("F3", ["E015", "E016"]),
    ("F1", ["E017"]),
    ("Fz", ["E018", "E019"]),
    ("F2", ["E020"]),
    ("F4", ["E021", "E022"]),
    ("F6", ["E023"]),
    ("F8", ["E024"]),
    ("FT7", ["E025"]),
    ("FC5", ["E026", "E027"]),
    ("FC3", ["E028", "E029"]),
    ("FC1", ["E030", "E031"]),
    ("FCz", ["E032", "E033"]),
    ("FC2", ["E034", "E035"]),
    ("FC4", ["E036", "E037"]),
    ("FC6", ["E038", "E039"]),
    ("FT8", ["E040"]),
    ("T7", ["E041", "E042"]),
    ("C5", ["E043"]),
    ("C3", ["E044", "E045", "E046"]),
    ("C1", ["E047", "E048"]),
    ("Cz", ["E049", "E050", "E051"]),
    ("C2", ["E052", "E053"]),
    ("C4", ["E054", "E055", "E056"]),
    ("C6", ["E057"]),
    ("T8", ["E058", "E059"]),
    ("TP7", ["E060"]),
    ("CP5", ["E061", "E062"]),
    ("CP3", ["E063", "E064"]),
    ("CP1", ["E065", "E066"]),
    ("CPz", ["E067", "E068"]),
    ("CP2", ["E069", "E070"]),
    ("CP4", ["E071", "E072"]),
    ("CP6", ["E073", "E074"]),
    ("TP8", ["E075"]),
    ("P7", ["E076", "E077"]),
    ("P5", ["E078", "E079"]),
    ("P3", ["E080", "E081", "E082"]),
    ("P1", ["E083", "E084"]),
    ("Pz", ["E085", "E086"]),
    ("P2", ["E087", "E088"]),
    ("P4", ["E089", "E090", "E091"]),
    ("P6", ["E092", "E093"]),
    ("P8", ["E094", "E095"]),
    ("PO7", ["E096"]),
    ("PO3", ["E097", "E098"]),
    ("POz", ["E099", "E100"]),
    ("PO4", ["E101", "E102"]),
    ("PO8", ["E103"]),
    ("O1", ["E104", "E105"]),
    ("Oz", ["E106", "E107"]),
    ("O2", ["E108", "E109"]),
    # Remaining electrodes not covered by 10-20 system
    ("E110", ["E110"]),
    ("E111", ["E111"]),
    ("E112", ["E112"]),
    ("E113", ["E113"]),
    ("E114", ["E114"]),
    ("E115", ["E115"]),
    ("E116", ["E116"]),
    ("E117", ["E117"]),
    ("E118", ["E118"]),
    ("E119", ["E119"]),
    ("E120", ["E120"]),
    ("E121", ["E121"]),
    ("E122", ["E122"]),
    ("E123", ["E123"]),
    ("E124", ["E124"]),
    ("E125", ["E125"]),
    ("E126", ["E126"]),
    ("E127", ["E127"]),
    ("E128", ["E128"]),
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for GES400/Hydrocel GSN channels.
    
    The function inspects the channel names in the raw data and builds
    a mapping from original channel names to standard 10-20 names.
    Supports both numeric format (E001-E128) and any existing standard names.
    
    Args:
        raw: The MNE Raw object containing channel information.
        
    Returns:
        A dictionary mapping original channel names to standardized names.
    """
    ch_names = raw.ch_names
    rename_map = {}
    
    # Build reverse GSN layout for quick lookup
    numeric_to_standard: Dict[str, str] = {}
    for standard_name, numeric_list in _GSN_LAYOUT:
        for num in numeric_list:
            numeric_to_standard[num] = standard_name
    
    for ch in ch_names:
        # Check if it's already a standard name
        if ch in _GES400_CHANNEL_MAP:
            rename_map[ch] = _GES400_CHANNEL_MAP[ch]
        # Check if it's a numeric GSN format (E001-E128)
        elif _GSN_NUMERIC_PATTERN.match(ch):
            standard = numeric_to_standard.get(ch)
            if standard:
                rename_map[ch] = standard
            else:
                # Keep original name if no mapping found
                rename_map[ch] = ch
        else:
            # Keep original name for unknown channels
            rename_map[ch] = ch
    
    return rename_map


def _build_montage(raw: mne.io.BaseRaw) -> Optional[mne.channels.DigMontage]:
    """Build a DigMontage for the GES400/Hydrocel GSN 128-channel system.
    
    Returns:
        A DigMontage object or None if standard_montage cannot be created.
    """
    try:
        # Try to use standard 1005 montage as base (most similar to GSN)
        montage = mne.channels.make_standard_montage("standard_1005")
        return montage
    except Exception:
        return None


def _annotate_trial_phases(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Annotate trial phases from trigger events in the raw data.
    
    The data contains events coded as:
    - 1: rest phase
    - 2: ready phase
    - 3: task phase
    - 4: interval phase
    - 5: feedback marker (admin)
    - 6: special session marker (admin)
    
    Args:
        raw: The MNE Raw object to annotate.
        
    Returns:
        The annotated Raw object.
    """
    events, event_id = mne.events_from_annotations(raw)
    
    # Build annotation descriptions based on event mapping
    descriptions = []
    durations = []
    onsets = []
    
    for event in events:
        event_value = event[2]
        if event_value in _TRIAL_PHASE_EVENT_MAP:
            descriptions.append(_TRIAL_PHASE_EVENT_MAP[event_value])
            durations.append(0.0)
            onsets.append(event[0] / raw.info['sfreq'])
        elif event_value in _ADMIN_EVENT_MAP:
            descriptions.append(_ADMIN_EVENT_MAP[event_value])
            durations.append(0.0)
            onsets.append(event[0] / raw.info['sfreq'])
    
    if descriptions:
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions
        )
        raw.set_annotations(annotations)
    
    return raw


def _load_raw_data(bids_root: str, subject_id: str, session: str = "smrbmi") -> mne.io.BaseRaw:
    """Load raw EEG data from BIDS dataset.
    
    Args:
        bids_root: Path to the BIDS dataset root.
        subject_id: Subject identifier (e.g., 'sub-01').
        session: Session name (default: 'smrbmi').
        
    Returns:
        A Raw object containing the EEG data.
        
    Raises:
        FileNotFoundError: If the required data files are not found.
    """
    # Construct paths for the EEG data
    eeg_dir = os.path.join(bids_root, subject_id, "eeg")
    
    if not os.path.exists(eeg_dir):
        raise FileNotFoundError(f"EEG directory not found: {eeg_dir}")
    
    # Find the EEG data file (usually .vhdr or .edf)
    data_file = None
    for fname in os.listdir(eeg_dir):
        if session in fname and (fname.endswith('.vhdr') or fname.endswith('.edf') or fname.endswith('.fif')):
            data_file = os.path.join(eeg_dir, fname)
            break
    
    if data_file is None:
        raise FileNotFoundError(f"No EEG data file found for {subject_id} in {eeg_dir}")
    
    # Load the data
    if data_file.endswith('.vhdr'):
        raw = mne.io.read_raw_brainvision(data_file, preload=False, verbose=False)
    elif data_file.endswith('.edf'):
        raw = mne.io.read_raw_edf(data_file, preload=False, verbose=False)
    elif data_file.endswith('.fif'):
        raw = mne.io.read_raw_fif(data_file, preload=False, verbose=False)
    else:
        raise ValueError(f"Unsupported file format: {data_file}")
    
    return raw


def _load_events_json(bids_root: str, subject_id: str, session: str = "smrbmi") -> Dict[str, Any]:
    """Load events.json sidecar file for the task.
    
    Args:
        bids_root: Path to the BIDS dataset root.
        subject_id: Subject identifier.
        session: Session name.
        
    Returns:
        Dictionary containing the events sidecar information.
    """
    eeg_dir = os.path.join(bids_root, subject_id, "eeg")
    events_json_path = os.path.join(eeg_dir, f"{subject_id}_{session}_task-smrbmi_events.json")
    
    if os.path.exists(events_json_path):
        with open(events_json_path, 'r') as f:
            return json.load(f)
    
    return {}


def _load_participants_tsv(bids_root: str) -> pd.DataFrame:
    """Load participants.tsv file from BIDS dataset.
    
    Args:
        bids_root: Path to the BIDS dataset root.
        
    Returns:
        DataFrame containing participant information.
    """
    participants_tsv = os.path.join(bids_root, "participants.tsv")
    
    if os.path.exists(participants_tsv):
        return pd.read_csv(participants_tsv, sep='\t')
    
    return pd.DataFrame()


class EEGUnityKernel:
    """EEGUnity processing kernel for OpenNeuro DS004447 dataset.
    
    This kernel handles high-density EEG data from the BMI-HDEEG dataset,
    specifically designed for 4-class Motor Imagery BCI experiments
    using 130-channel GES400/Hydrocel GSN systems.
    
    Attributes:
        dataset_id: The OpenNeuro dataset identifier.
        description: Kernel description and metadata.
        eegunity_description: Metadata for EEGUnity platform.
    """
    
    def __init__(self):
        self.dataset_id = "ds004447"
        self.description = (
            "OpenNeuro DS004447: BMI-HDEEG Dataset 3 — "
            "4-class Motor Imagery BCI with 130-channel high-density EEG"
        )
        self.eegunity_description = {
            "age": "21-27",
            "sex": "male/female",
            "amplifier": "GES400/Hydrocel GSN 128-channel",
            "cap": "Hydrocel GSN 128-channel montage",
            "handedness": "right"
        }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply the EEGUnity processing kernel to raw EEG data.
        
        This method processes raw EEG data through the following steps:
        1. Load and validate data structure
        2. Rename channels to standard 10-20 nomenclature
        3. Set up electrode montage
        4. Annotate trial phases from trigger events
        5. Apply standard preprocessing
        
        Args:
            udataset: Universal dataset object containing dataset metadata.
            raw: MNE Raw object containing the raw EEG data.
            row: DataFrame row containing subject and session information.
            
        Returns:
            Processed MNE Raw object with annotated trial phases and
            standardized channel names.
        """
        # Get dataset root from udataset
        bids_root = getattr(udataset, 'bids_root', None)
        if bids_root is None:
            bids_root = getattr(udataset, 'root', '.')
        
        subject_id = row.get('subject_id', row.get('participant_id', 'sub-01'))
        session = row.get('session', 'smrbmi')
        
        # Step 1: Rename channels to standard nomenclature
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Step 2: Set up montage
        montage = _build_montage(raw)
        if montage is not None:
            raw.set_montage(montage)
        
        # Step 3: Annotate trial phases from events
        raw = _annotate_trial_phases(raw)
        
        # Step 4: Standard preprocessing
        # Ensure reference is set (GES400 uses average reference)
        try:
            raw.set_eeg_reference('average')
        except Exception:
            pass
        
        # Step 5: Ensure proper data types
        raw._data = raw._data.astype(np.float32)
        
        return raw


# Kernel instance for EEGUnity
KERNEL = EEGUnityKernel()