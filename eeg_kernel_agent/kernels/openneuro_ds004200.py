"""OpenNeuro DS004200 (Temporal Scaling) stage1 kernel for EEGUnity.

Dataset: Temporal Scaling experiment investigating human interval production and judgment.
Source: https://openneuro.org/datasets/ds004200 DOI: https://doi.org/10.18112/openneuro.ds004200.v1.0.1

This kernel handles:
- Standard BIDS structure with participants.tsv
- Event code mapping for temporal scaling paradigm
- Channel renaming for 37-channel EEG cap
- Metadata standardization for EEGUnity

Reference paper: DOI: https://doi.org/10.1073/pnas.2214638119
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Subject Metadata
# ============================================================================
# Source: OpenNeuro participants.tsv
# Annotator: LLM, 2026-04-08 - inferred from dataset; human review required
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-001": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-002": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-003": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-004": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-005": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-006": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-007": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-008": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-009": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-010": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-011": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-012": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-013": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-014": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-015": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-016": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-017": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-018": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-019": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
    "sub-020": {"sex": "unknown", "age": "unknown", "handedness": "unknown"},
}

# ============================================================================
# Event Code Mapping (Raw Meta)
# ============================================================================
# Tens digit: task type (1=production, 2-6=other conditions)
# Units digit: phase (1/2/3) or feedback (7)
# Event 2 is block/session boundary marker (admin code, excluded)
_EVENT_MAP: Dict[int, str] = {
    11: "Cond1_Phase1",
    12: "Cond1_Phase2",
    13: "Cond1_Phase3",
    17: "Cond1_Feedback",
    21: "Cond2_Phase1",
    22: "Cond2_Phase2",
    23: "Cond2_Phase3",
    27: "Cond2_Feedback",
    31: "Cond3_Phase1",
    32: "Cond3_Phase2",
    33: "Cond3_Phase3",
    37: "Cond3_Feedback",
    41: "Cond4_Phase1",
    42: "Cond4_Phase2",
    43: "Cond4_Phase3",
    47: "Cond4_Feedback",
    51: "Cond5_Phase1",
    52: "Cond5_Phase2",
    53: "Cond5_Phase3",
    57: "Cond5_Feedback",
    61: "Cond6_Phase1",
    62: "Cond6_Phase2",
    63: "Cond6_Phase3",
    67: "Cond6_Feedback",
}

# Admin codes to exclude
_ADMIN_CODES = {2}

# ============================================================================
# Channel Configuration
# ============================================================================
# Standard 37-channel layout for BrainVision / EasyCAP systems
# Source: Dataset documentation / standard_1020 extended montage
# Annotator: LLM, 2026-04-08 - inferred from 37-channel count; human review required
_EEG_CHANNEL_STANDARD_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC3", "FCz", "FC4", "FT8",
    "T7", "C3", "Cz", "C4", "T8",
    "TP7", "CP3", "CPz", "CP4", "TP8",
    "P7", "P3", "Pz", "P4", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2",
    "VEO", "HEO",  # Vertical/horizontal EOG
    "Cz_Reference",  # Often used as reference channel
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names.
    
    Attempts to map common alias patterns to standard 10-20 names.
    """
    alias_groups = [
        # Fp group
        ("Fp1", ["Fp1", "EEG-Fp1", "Fp 1"]),
        ("Fpz", ["Fpz", "EEG-Fpz", "Fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2", "Fp 2"]),
        # F group
        ("F7", ["F7", "EEG-F7", "F 7"]),
        ("F3", ["F3", "EEG-F3", "F 3"]),
        ("Fz", ["Fz", "EEG-Fz", "Fz"]),
        ("F4", ["F4", "EEG-F4", "F 4"]),
        ("F8", ["F8", "EEG-F8", "F 8"]),
        # FC group
        ("FC3", ["FC3", "EEG-FC3", "FC 3"]),
        ("FCz", ["FCz", "EEG-FCz", "FCz"]),
        ("FC4", ["FC4", "EEG-FC4", "FC 4"]),
        # C group
        ("C3", ["C3", "EEG-C3", "C 3"]),
        ("Cz", ["Cz", "EEG-Cz", "Cz"]),
        ("C4", ["C4", "EEG-C4", "C 4"]),
        # CP group
        ("CP3", ["CP3", "EEG-CP3", "CP 3"]),
        ("CPz", ["CPz", "EEG-CPz", "CPz"]),
        ("CP4", ["CP4", "EEG-CP4", "CP 4"]),
        # P group
        ("P7", ["P7", "EEG-P7", "P 7"]),
        ("P3", ["P3", "EEG-P3", "P 3"]),
        ("Pz", ["Pz", "EEG-Pz", "Pz"]),
        ("P4", ["P4", "EEG-P4", "P 4"]),
        ("P8", ["P8", "EEG-P8", "P 8"]),
        # PO group
        ("PO7", ["PO7", "EEG-PO7", "PO 7"]),
        ("PO3", ["PO3", "EEG-PO3", "PO 3"]),
        ("POz", ["POz", "EEG-POz", "POz"]),
        ("PO4", ["PO4", "EEG-PO4", "PO 4"]),
        ("PO8", ["PO8", "EEG-PO8", "PO 8"]),
        # O group
        ("O1", ["O1", "EEG-O1", "O 1"]),
        ("Oz", ["Oz", "EEG-Oz", "Oz"]),
        ("O2", ["O2", "EEG-O2", "O 2"]),
        # EOG channels
        ("VEO", ["VEO", "EOG-V", "EOG-VEO", "veog"]),
        ("HEO", ["HEO", "EOG-H", "EOG-HEO", "heog"]),
        # Reference /Misc
        ("REF", ["REF", "Reference", "Cz_ref", "CMS"]),
        ("MISC", ["MISC", "Misc", "Status", "Trigger"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _read_events_from_bids(raw: mne.io.BaseRaw, events_file: Optional[str] = None) -> mne.Annotations:
    """Extract events from BIDS events.tsv or from STIM channel.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG data
    events_file : str, optional
        Path to events.tsv file
        
    Returns
    -------
    mne.Annotations
        MNE annotations with standardized event labels
    """
    annotations = None
    
    # Try to load from events.tsv if provided
    if events_file and os.path.exists(events_file):
        try:
            events_df = pd.read_csv(events_file, sep="\t")
            if all(col in events_df.columns for col in ['onset', 'duration', 'value']):
                onset = events_df['onset'].values
                duration = events_df['duration'].values if 'duration' in events_df.columns else np.zeros(len(onset))
                
                # Map value column - could be 'value', 'trial_type', or 'stim_type'
                value_col = 'value' if 'value' in events_df.columns else 'trial_type'
                if value_col in events_df.columns:
                    descriptions = events_df[value_col].astype(str).values
                else:
                    descriptions = events_df['trial_type'].astype(str).values
                
                # Convert numeric codes to standardized labels
                mapped_descriptions = []
                for desc in descriptions:
                    try:
                        code = int(float(desc))
                        if code in _ADMIN_CODES:
                            mapped_descriptions.append(f"admin: marker-{code}")
                        elif code in _EVENT_MAP:
                            mapped_descriptions.append(_EVENT_MAP[code])
                        else:
                            mapped_descriptions.append(f"unknown_{desc}")
                    except (ValueError, TypeError):
                        mapped_descriptions.append(str(desc))
                
                annotations = mne.Annotations(
                    onset=onset,
                    duration=duration,
                    description=mapped_descriptions,
                )
        except Exception as e:
            print(f"Warning: Could not read events.tsv: {e}")
    
    # Fallback: extract from raw annotations or STIM channel
    if annotations is None:
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if len(events) > 0:
                new_descriptions = []
                for event in events:
                    code = event[2]
                    if code in _ADMIN_CODES:
                        new_descriptions.append(f"admin: marker-{code}")
                    elif code in _EVENT_MAP:
                        new_descriptions.append(_EVENT_MAP[code])
                    else:
                        # Keep original annotation if not in our map
                        orig_desc = [k for k, v in event_id.items() if v == code]
                        if orig_desc:
                            new_descriptions.append(orig_desc[0])
                        else:
                            new_descriptions.append(f"event_{code}")
                
                annotations = mne.Annotations(
                    onset=events[:, 0] / raw.info['sfreq'],
                    duration=np.zeros(len(events)),
                    description=new_descriptions,
                )
        except Exception as e:
            print(f"Warning: Could not extract events from raw: {e}")
            annotations = mne.Annotations(
                onset=np.array([]),
                duration=np.array([]),
                description=np.array([]),
            )
    
    return annotations


def _try_set_montage(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard montage for EEG channels.
    
    Uses standard_1020 as fallback, handles common non-standard naming.
    """
    eeg_channels = [ch for ch in raw.ch_names if ch.startswith(('EEG-', 'E')) 
                    or ch in _EEG_CHANNEL_STANDARD_NAMES]
    
    if len(eeg_channels) >= 20:  # Likely a full EEG cap
        try:
            # Try standard 1020 first
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='ignore', verbose=False)
        except Exception:
            pass


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv if available.
    
    Returns empty DataFrame if not found.
    """
    participants_file = os.path.join(dataset_path, 'participants.tsv')
    if os.path.exists(participants_file):
        try:
            return pd.read_csv(participants_file, sep='\t')
        except Exception:
            pass
    return pd.DataFrame()


def _get_subject_info(subject_id: str, dataset_path: str) -> Dict[str, str]:
    """Get subject metadata from participants.tsv or fallback dict.
    
    Parameters
    ----------
    subject_id : str
        Subject identifier (e.g., 'sub-001')
    dataset_path : str
        Path to dataset root
        
    Returns
    -------
    dict
        Dict with age, sex, handedness keys
    """
    # Check cached subject dict first
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id].copy()
    
    # Try to load from participants.tsv
    df = _load_participants_tsv(dataset_path)
    if not df.empty:
        # Normalize subject_id
        search_id = subject_id.replace('sub-', '')
        if 'participant_id' in df.columns:
            row = df[df['participant_id'] == subject_id]
            if row.empty:
                row = df[df['participant_id'] == search_id]
            
            if not row.empty:
                result = {
                    'age': 'unknown',
                    'sex': 'unknown', 
                    'handedness': 'unknown'
                }
                
                # Map age
                if 'age' in df.columns:
                    age_val = row['age'].values[0]
                    if pd.notna(age_val):
                        result['age'] = str(int(float(age_val)))
                
                # Map sex
                if 'sex' in df.columns:
                    sex_val = str(row['sex'].values[0]).lower()
                    if sex_val in ['m', 'male']:
                        result['sex'] = 'male'
                    elif sex_val in ['f', 'female']:
                        result['sex'] = 'female'
                
                # Map handedness
                if 'handedness' in df.columns:
                    hand_val = str(row['handedness'].values[0]).lower()
                    if 'right' in hand_val:
                        result['handedness'] = 'right'
                    elif 'left' in hand_val:
                        result['handedness'] = 'left'
                
                return result
    
    return {
        'age': 'unknown',
        'sex': 'unknown',
        'handedness': 'unknown'
    }


@dataclass
class OpenNeuroDS004200Kernel:
    """Stage1 kernel for OpenNeuro DS004200 (Temporal Scaling).
    
    This kernel handles:
    - BIDS format EEG data from temporal scaling experiment
    - Event code mapping for 24 experimental conditions (6 conditions × 4 phases)
    - 37-channel EEG with standard 10-20 nomenclature
    - Metadata standardization for EEGUnity
    """

    KERNEL_ID: str = "openneuro-ds004200-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object loaded from BIDS.
        row
            Locator row (pandas.Series-like) with File Path and subject info.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata and annotations.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("subject_id", "unknown")
        
        # Determine dataset root path for loading sidecar files
        dataset_root = os.path.dirname(os.path.dirname(file_path))
        
        # ==================================================================
        # Step 1: Channel Renaming (BEFORE set_montage)
        # ==================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # ==================================================================
        # Step 2: Set Montage
        # ==================================================================
        _try_set_montage(raw)
        
        # ==================================================================
        # Step 3: Extract and Remap Events
        # ==================================================================
        # Look for events.tsv in the same directory as the EEG file
        eeg_dir = os.path.dirname(file_path)
        events_file = None
        
        # Common BIDS event file patterns
        for pattern in ['*_events.tsv', 'events.tsv']:
            import glob
            matches = glob.glob(os.path.join(eeg_dir, pattern))
            if matches:
                events_file = matches[0]
                break
        
        annotations = _read_events_from_bids(raw, events_file)
        if annotations is not None and len(annotations) > 0:
            raw.set_annotations(annotations)
        
        # ==================================================================
        # Step 4: Get Subject Metadata
        # ==================================================================
        subject_info = _get_subject_info(subject_id, dataset_root)
        
        # ==================================================================
        # Step 5: Update Description
        # ==================================================================
        original_desc = raw.info.get("description", "")
        if not original_desc:
            original_desc = ""
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004200Kernel()