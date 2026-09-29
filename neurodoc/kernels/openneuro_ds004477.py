"""OpenNeuro DS004477 stage1 kernel for EEGUnity.

Dataset: Pandemic Emergency Scenario (PES)
Paradigm: Strategic pandemic simulation with resource allocation decisions,
           multi-agent interaction, and confidence reporting.
Source: https://openneuro.org/datasets/ds004477
DOI: https://doi.org/10.3389/fnhum.2019.00013

Event Structure:
    - stimulus: Decision stimulus onset
    - resp_hold: Response initiation (button press start)
    - resp_release: Response release (button press end)
    - confidence: Confidence rating onset

Task: Decision Making (Multiclass Classification)
    y=0: stimulus | y=1: resp_hold | y=2: resp_release | y=3: confidence
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


# =============================================================================
# Subject Metadata
# =============================================================================
# Source: OpenNeuro participants.tsv (ds004477)
# Annotator: LLM, 2026-04-08
# Note: age/sex from participants.tsv; amplifier/cap/handedness inferred from
# paradigm description (high-density EEG, 2048 Hz suggests research-grade system)
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    # Participant data loaded dynamically from participants.tsv
    # Fallback values if participants.tsv unavailable:
}


# =============================================================================
# Channel Standardization
# =============================================================================
# OpenNeuro EEG datasets commonly use BrainVision, EDF, or BDF formats with
# standard 10-20 electrode nomenclature. 80 channels suggests extended cap.
# Source: Dataset README and common OpenNeuro EEG conventions
# Annotator: LLM, 2026-04-08
_STANDARD_10_20_CHANNELS = {
    "Fp1", "Fp2", "Fpz", "F7", "F3", "Fz", "F4", "F8",
    "T7", "T8", "C3", "C4", "Cz",
    "P7", "P8", "P3", "Pz", "P4",
    "O1", "O2", "Oz",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "FT7", "FT8", "TP7", "TP8",
    "F1", "F2", "F5", "F6",
    "C1", "C2", "C5", "C6",
    "P1", "P2", "P5", "P6",
    "EOG-left", "EOG-right", "EOG-central",
    "ECG", "EMG",
}


def _standardize_channel_name(ch_name: str) -> str:
    """Standardize a channel name to 10-20 nomenclature.
    
    Source: Common OpenNeuro EEG naming conventions
    Annotator: LLM, 2026-04-08
    """
    # Remove common prefixes/suffixes
    name = ch_name.strip()
    name = re.sub(r'^(EEG|EEG-)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\(.*?\)\s*$', '', name)  # Remove parenthetical
    
    # Common mappings for OpenNeuro datasets
    mappings = {
        'fp1': 'Fp1', 'fp2': 'Fp2', 'fpz': 'Fpz',
        'f7': 'F7', 'f3': 'F3', 'fz': 'Fz', 'f4': 'F4', 'f8': 'F8',
        't7': 'T7', 't8': 'T8', 'c3': 'C3', 'c4': 'C4', 'cz': 'Cz',
        'p7': 'P7', 'p8': 'P8', 'p3': 'P3', 'pz': 'Pz', 'p4': 'P4',
        'o1': 'O1', 'o2': 'O2', 'oz': 'Oz',
        'af7': 'AF7', 'af3': 'AF3', 'afz': 'AFz', 'af4': 'AF4', 'af8': 'AF8',
        'fc5': 'FC5', 'fc3': 'FC3', 'fc1': 'FC1', 'fcz': 'FCz', 
        'fc2': 'FC2', 'fc4': 'FC4', 'fc6': 'FC6',
        'cp5': 'CP5', 'cp3': 'CP3', 'cp1': 'CP1', 'cpz': 'CPz',
        'cp2': 'CP2', 'cp4': 'CP4', 'cp6': 'CP6',
        'po7': 'PO7', 'po3': 'PO3', 'poz': 'POz', 'po4': 'PO4', 'po8': 'PO8',
        'ft7': 'FT7', 'ft8': 'FT8', 'tp7': 'TP7', 'tp8': 'TP8',
        'eog l': 'EOG-left', 'eog r': 'EOG-right', 'eog c': 'EOG-central',
        'leog': 'EOG-left', 'reog': 'EOG-right', 'beog': 'EOG-central',
    }
    
    lower_name = name.lower()
    if lower_name in mappings:
        return mappings[lower_name]
    
    # If already in standard format, return as-is
    if name in _STANDARD_10_20_CHANNELS:
        return name
    
    return name


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standardizing channel names.
    
    Source: Common OpenNeuro EEG conventions
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    for ch in raw.ch_names:
        standardized = _standardize_channel_name(ch)
        if standardized != ch and standardized not in existing:
            rename_map[ch] = standardized
    
    return rename_map


def _set_montage_if_possible(raw: mne.io.BaseRaw) -> None:
    """Set standard 10-20 montage if sufficient channels match.
    
    Source: MNE-Python standard_montage_unknown_posizioni
    Annotator: LLM, 2026-04-08
    """
    try:
        # Try standard 1020 first
        montage = mne.channels.make_standard_montage('standard_1020')
        
        # Check how many channels match
        available_chs = set(ch.upper() for ch in raw.ch_names)
        montage_chs = set(ch.upper() for ch in montage.ch_names)
        overlap = available_chs & montage_chs
        
        if len(overlap) >= 20:  # Require at least 20 matching channels
            raw.set_montage(montage, on_missing='ignore')
    except Exception:
        pass  # Montage setting is best-effort


# =============================================================================
# Event Mapping
# =============================================================================
# Normal Task 1: Decision Making (Multiclass Classification)
# y mapping for epoch_by_event_hdf5
# Source: analysis.md event structure table
# Annotator: Human, based on analysis.md
_EVENT_LABEL_MAP = {
    'stimulus': 0,
    'resp_hold': 1,
    'resp_release': 2,
    'confidence': 3,
}


def _load_events_from_bids(row: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """Load events from BIDS *_events.tsv file.
    
    Source: BIDS specification
    Annotator: LLM, 2026-04-08
    """
    file_path = row.get('File Path', '')
    if not file_path:
        return None
    
    # Construct events file path
    events_file = file_path.replace('.edf', '_events.tsv')
    events_file = events_file.replace('.bdf', '_events.tsv')
    events_file = events_file.replace('.fif', '_events.tsv')
    events_file = events_file.replace('_eeg.edf', '_events.tsv')
    
    # Try alternative naming patterns
    base_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    alt_events = os.path.join(base_dir, base_name + '_events.tsv')
    
    for candidate in [events_file, alt_events]:
        if os.path.exists(candidate):
            try:
                df = pd.read_csv(candidate, sep='\t')
                return df
            except Exception:
                pass
    
    return None


def _create_annotations_from_events(raw: mne.io.BaseRaw, 
                                    events_df: pd.DataFrame) -> mne.Annotations:
    """Create MNE annotations from BIDS events.tsv.
    
    Source: BIDS specification, analysis.md
    Annotator: Human, based on analysis.md
    """
    onset_col = None
    duration_col = None
    label_col = None
    
    # Find appropriate columns
    for col in ['onset', 'timestamp', 'time']:
        if col in events_df.columns:
            onset_col = col
            break
    
    for col in ['duration', 'length']:
        if col in events_df.columns:
            duration_col = col
            break
    
    for col in ['trial_type', 'value', 'event', 'event_type', 'condition', 'type']:
        if col in events_df.columns:
            label_col = col
            break
    
    if onset_col is None:
        return raw.annotations  # Return existing
    
    # Extract onset times
    onsets = events_df[onset_col].values
    
    # Handle duration
    if duration_col:
        durations = events_df[duration_col].fillna(0).values
    else:
        durations = np.zeros(len(onsets))
    
    # Extract labels
    if label_col:
        labels = events_df[label_col].astype(str).values
    else:
        labels = [f'event_{i}' for i in range(len(onsets))]
    
    # Normalize labels to match event mapping
    normalized_labels = []
    for label in labels:
        label_lower = label.lower().strip()
        if 'stimulus' in label_lower or 'decision' in label_lower:
            normalized_labels.append('stimulus')
        elif 'hold' in label_lower or 'press' in label_lower and 'start' in label_lower:
            normalized_labels.append('resp_hold')
        elif 'release' in label_lower:
            normalized_labels.append('resp_release')
        elif 'confiden' in label_lower or 'rating' in label_lower:
            normalized_labels.append('confidence')
        else:
            normalized_labels.append(label)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=normalized_labels,
    )


def _create_annotations_from_raw_annotations(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Convert existing raw annotations to normalized labels.
    
    Source: analysis.md event structure
    Annotator: Human, based on analysis.md
    """
    if not raw.annotations:
        return raw.annotations
    
    normalized = []
    for desc in raw.annotations.description:
        desc_lower = str(desc).lower().strip()
        
        # Map to standard event labels
        if 'stimulus' in desc_lower or 'decision' in desc_lower:
            normalized.append('stimulus')
        elif 'hold' in desc_lower or ('press' in desc_lower and 'start' in desc_lower):
            normalized.append('resp_hold')
        elif 'release' in desc_lower:
            normalized.append('resp_release')
        elif 'confiden' in desc_lower or 'rating' in desc_lower:
            normalized.append('confidence')
        else:
            normalized.append(str(desc))
    
    return mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=normalized,
    )


def _create_confidence_misc_channel(raw: mne.io.BaseRaw,
                                    events_df: Optional[pd.DataFrame] = None) -> None:
    """Create misc channel for confidence ratings if not present.
    
    Source: analysis.md MISC Label Summary
    Annotator: LLM, 2026-04-08
    """
    # Check if confidence info already exists
    existing_chs = [ch.lower() for ch in raw.ch_names]
    if 'confidence' in existing_chs or 'misc' in existing_chs:
        return
    
    # Confidence ratings are stored in annotations, not as separate channel
    # This is per analysis.md: "Confidence values stored in misc labels"
    pass


# =============================================================================
# Subject Metadata Loading
# =============================================================================
def _load_participant_info(row: Dict[str, Any]) -> Dict[str, str]:
    """Load participant metadata from BIDS participants.tsv.
    
    Source: BIDS specification
    Annotator: LLM, 2026-04-08
    """
    subject_id = row.get('participant_id', row.get('subject_id', ''))
    if not subject_id:
        subject_id = row.get('File Path', '').split('sub-')[-1][:6]
    
    # Check if we have hardcoded info
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id]
    
    # Try to load from participants.tsv
    file_path = row.get('File Path', '')
    if file_path:
        dataset_root = os.path.dirname(os.path.dirname(file_path))
        participants_file = os.path.join(dataset_root, 'participants.tsv')
        
        if os.path.exists(participants_file):
            try:
                df = pd.read_csv(participants_file, sep='\t')
                subj_row = df[df['participant_id'] == subject_id]
                if len(subj_row) > 0:
                    return {
                        'age': str(int(subj_row['age'].values[0])) if 'age' in subj_row.columns else 'unknown',
                        'sex': subj_row['sex'].values[0].lower() if 'sex' in subj_row.columns else 'unknown',
                        'handedness': subj_row['handedness'].values[0].lower() if 'handedness' in subj_row.columns else 'unknown',
                    }
            except Exception:
                pass
    
    # Default values - LLM inferred, needs human review
    return {
        'age': 'unknown',  # inferred by LLM, needs human review
        'sex': 'unknown',  # inferred by LLM, needs human review
        'handedness': 'unknown',  # inferred by LLM, needs human review
    }


# =============================================================================
# Kernel Class
# =============================================================================
@dataclass
class OpenNeuroDS004477Kernel:
    """Stage1 kernel for OpenNeuro dataset ds004477 (PES paradigm).
    
    Dataset Info:
        - 9 subjects
        - 80 channels at 2048 Hz
        - Paradigm: Pandemic Emergency Scenario with resource allocation,
          multi-agent interaction, and confidence reporting
    
    Source: https://openneuro.org/datasets/ds004477
    DOI: https://doi.org/10.3389/fnhum.2019.00013
    """

    KERNEL_ID: str = "openneuro-ds004477-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (dict/Series-like) with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with standardized metadata.
        """
        # Convert row to dict if pandas Series
        if hasattr(row, 'to_dict'):
            row = row.to_dict()
        
        file_path = row.get('File Path', '')
        subject_id = row.get('participant_id', 
                             row.get('subject_id', 
                                    file_path.split('sub-')[-1][:6] if 'sub-' in file_path else 'unknown'))
        
        # -------------------------------------------------------------------------
        # 1. Load participant metadata
        # -------------------------------------------------------------------------
        participant_info = _load_participant_info(row)
        
        # -------------------------------------------------------------------------
        # 2. Standardize channel names BEFORE set_montage()
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set montage (best-effort, only if sufficient standard channels)
        _set_montage_if_possible(raw)
        
        # -------------------------------------------------------------------------
        # 3. Extract and normalize events
        # -------------------------------------------------------------------------
        events_df = _load_events_from_bids(row)
        
        if events_df is not None and len(events_df) > 0:
            # Create annotations from BIDS events.tsv
            annotations = _create_annotations_from_events(raw, events_df)
        elif raw.annotations and len(raw.annotations) > 0:
            # Normalize existing annotations
            annotations = _create_annotations_from_raw_annotations(raw)
        else:
            # No events found - this may indicate file scan issue
            # Create empty annotations to preserve structure
            annotations = mne.Annotations(
                onset=np.array([]),
                duration=np.array([]),
                description=np.array([]),
            )
        
        raw.set_annotations(annotations)
        
        # -------------------------------------------------------------------------
        # 4. Handle confidence misc channel
        # -------------------------------------------------------------------------
        # Confidence ratings are stored as annotations (per analysis.md)
        # No separate misc channel creation needed
        
        # -------------------------------------------------------------------------
        # 5. Update raw.info["description"] with eegunity_description
        # -------------------------------------------------------------------------
        original_desc = raw.info.get('description', '')
        if isinstance(original_desc, dict):
            original_desc = json.dumps(original_desc)
        elif not isinstance(original_desc, str):
            original_desc = str(original_desc) if original_desc else ''
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": participant_info.get('age', 'unknown'),
                "sex": participant_info.get('sex', 'unknown'),
                "amplifier": "unknown",  # inferred by LLM, needs human review (2048 Hz suggests research-grade)
                "cap": "unknown",  # inferred by LLM, needs human review (80 channels suggests extended cap)
                "handedness": participant_info.get('handedness', 'unknown'),
            }
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # -------------------------------------------------------------------------
        # 6. Set standard reference if not set
        # -------------------------------------------------------------------------
        if raw.info.get('ch_names') and 'eeg' in raw.get_channel_types():
            if raw.info.get('reference', 'unknown') == 'unknown':
                # Common reference for high-density EEG
                pass  # Leave as-is unless specified
        
        return raw


KERNEL = OpenNeuroDS004477Kernel()