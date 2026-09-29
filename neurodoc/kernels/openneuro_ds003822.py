"""OpenNeuro ds003822 stage1 kernel for EEGUnity.

Probabilistic Learning with Affective Feedback - Experiment #1
A reinforcement learning task investigating Reward Positivity (RewP) EEG component.

Source: https://openneuro.org/datasets/ds003822
Paper: https://doi.org/10.3758/s13415-021-00950-5
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


# Annotator: LLM, 2026-04-08
# Source: Based on standard 64-channel EEG cap plus additional channels
# 66 channels suggest a 64-channel EEG cap with 2 EOG channels
# Assuming standard 10-20 system with extended 10-10 positions
# inferred by LLM, needs human review
_DEFAULT_66_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF3", "AFz", "AF4",
    "F7", "F3", "Fz", "F4", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO3", "POz", "PO4",
    "O1", "Oz", "O2",
    "VEO", "HEO",  # Vertical and Horizontal EOG
    "TP10", "FT10", "FTT10", "TTP10", "TPP10", "P10", "PO8", "PO10", "O10"
]

# Event code to descriptive label mapping for S1xx codes
# Source: Dataset documentation and paper methodology
# Annotator: LLM, 2026-04-08
_S1XX_EVENT_MAP = {
    "S101": "FB type: liked win",
    "S102": "FB type: liked win",
    "S103": "FB type: liked win",
    "S104": "FB type: liked win",
    "S105": "FB type: disliked loss",
    "S106": "FB type: disliked loss",
    "S107": "FB type: disliked loss",
    "S108": "FB type: disliked loss",
    "S110": "FB type: point positive",
    "S111": "FB type: point positive",
    "S120": "FB type: point negative",
}

# Super meta labels for Task 1: Reward Valence Classification
# Annotator: LLM, 2026-04-08
_REWARD_VALENCE_MAP = {
    "FB type: liked win": 1,      # Rewarding/positive
    "FB type: point positive": 1,  # Rewarding/positive
    "FB type: disliked loss": 0,   # Punishing/negative
    "FB type: point negative": 0,  # Punishing/negative
}

# Super meta labels for Task 2: Feedback Modality Classification
# Annotator: LLM, 2026-04-08
_FEEDBACK_MODALITY_MAP = {
    "FB type: liked win": 1,       # Picture feedback
    "FB type: disliked loss": 1,    # Picture feedback
    "FB type: point positive": 0,   # Point feedback
    "FB type: point negative": 0,   # Point feedback
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.
    
    Source: Standard 10-20 system electrode positions
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Common non-standard naming patterns in EEG datasets
    alias_groups = [
        ("Fp1", ["Fp1", "EEG001", "EEG 001", "eeg001"]),
        ("Fp2", ["Fp2", "EEG002", "EEG 002", "eeg002"]),
        ("F7", ["F7", "EEG003", "EEG 003", "eeg003"]),
        ("F3", ["F3", "EEG004", "EEG 004", "eeg004"]),
        ("Fz", ["Fz", "EEG005", "EEG 005", "eeg005"]),
        ("F4", ["F4", "EEG006", "EEG 006", "eeg006"]),
        ("F8", ["F8", "EEG007", "EEG 007", "eeg007"]),
        ("T7", ["T7", "EEG008", "EEG 008", "eeg008"]),
        ("C3", ["C3", "EEG009", "EEG 009", "eeg009"]),
        ("C1", ["C1", "EEG010", "EEG 010", "eeg010"]),
        ("Cz", ["Cz", "EEG011", "EEG 011", "eeg011"]),
        ("C2", ["C2", "EEG012", "EEG 012", "eeg012"]),
        ("C4", ["C4", "EEG013", "EEG 013", "eeg013"]),
        ("T8", ["T8", "EEG014", "EEG 014", "eeg014"]),
        ("P7", ["P7", "EEG015", "EEG 015", "eeg015"]),
        ("P3", ["P3", "EEG016", "EEG 016", "eeg016"]),
        ("Pz", ["Pz", "EEG017", "EEG 017", "eeg017"]),
        ("P4", ["P4", "EEG018", "EEG 018", "eeg018"]),
        ("P8", ["P8", "EEG019", "EEG 019", "eeg019"]),
        ("O1", ["O1", "EEG020", "EEG 020", "eeg020"]),
        ("Oz", ["Oz", "EEG021", "EEG 021", "eeg021"]),
        ("O2", ["O2", "EEG022", "EEG 022", "eeg022"]),
        ("AF3", ["AF3", "EEG023", "EEG 023", "eeg023"]),
        ("AFz", ["AFz", "EEG024", "EEG 024", "eeg024"]),
        ("AF4", ["AF4", "EEG025", "EEG 025", "eeg025"]),
        ("F1", ["F1", "EEG026", "EEG 026", "eeg026"]),
        ("F2", ["F2", "EEG027", "EEG 027", "eeg027"]),
        ("F5", ["F5", "EEG028", "EEG 028", "eeg028"]),
        ("F6", ["F6", "EEG029", "EEG 029", "eeg029"]),
        ("FC1", ["FC1", "EEG030", "EEG 030", "eeg030"]),
        ("FC2", ["FC2", "EEG031", "EEG 031", "eeg031"]),
        ("FC5", ["FC5", "EEG032", "EEG 032", "eeg032"]),
        ("FC6", ["FC6", "EEG033", "EEG 033", "eeg033"]),
        ("C5", ["C5", "EEG034", "EEG 034", "eeg034"]),
        ("C6", ["C6", "EEG035", "EEG 035", "eeg035"]),
        ("CP1", ["CP1", "EEG036", "EEG 036", "eeg036"]),
        ("CP2", ["CP2", "EEG037", "EEG 037", "eeg037"]),
        ("CP3", ["CP3", "EEG038", "EEG 038", "eeg038"]),
        ("CP4", ["CP4", "EEG039", "EEG 039", "eeg039"]),
        ("CP5", ["CP5", "EEG040", "EEG 040", "eeg040"]),
        ("CP6", ["CP6", "EEG041", "EEG 041", "eeg041"]),
        ("P1", ["P1", "EEG042", "EEG 042", "eeg042"]),
        ("P2", ["P2", "EEG043", "EEG 043", "eeg043"]),
        ("P5", ["P5", "EEG044", "EEG 044", "eeg044"]),
        ("P6", ["P6", "EEG045", "EEG 045", "eeg045"]),
        ("PO3", ["PO3", "EEG046", "EEG 046", "eeg046"]),
        ("POz", ["POz", "EEG047", "EEG 047", "eeg047"]),
        ("PO4", ["PO4", "EEG048", "EEG 048", "eeg048"]),
        ("FT7", ["FT7", "EEG049", "EEG 049", "eeg049"]),
        ("FT8", ["FT8", "EEG050", "EEG 050", "eeg050"]),
        ("TP7", ["TP7", "EEG051", "EEG 051", "eeg051"]),
        ("TP8", ["TP8", "EEG052", "EEG 052", "eeg052"]),
        ("PO7", ["PO7", "EEG053", "EEG 053", "eeg053"]),
        ("PO8", ["PO8", "EEG054", "EEG 054", "eeg054"]),
    ]
    
    for target, aliases in alias_groups:
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _parse_events_tsv(events_path: str) -> pd.DataFrame:
    """Parse events.tsv file and return dataframe.
    
    Source: BIDS standard events.tsv format
    """
    if not os.path.exists(events_path):
        return pd.DataFrame()
    
    df = pd.read_csv(events_path, sep="\t")
    return df


def _create_annotations_from_events(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    sfreq: float
) -> mne.Annotations:
    """Create MNE annotations from events.tsv dataframe.
    
    Handles both standard BIDS events and custom S1xx event codes.
    """
    if events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row.get("onset", 0)) / sfreq
        duration = float(row.get("duration", 0))
        
        # Handle different event value columns
        value = row.get("value", "")
        stim_type = row.get("stim_type", "")
        event_value = row.get("event_value", "")
        
        # Determine description
        desc = value if value else stim_type if stim_type else event_value
        
        # Map S1xx codes to descriptive labels
        if isinstance(desc, str) and desc.startswith("S"):
            desc = _S1XX_EVENT_MAP.get(desc, desc)
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(str(desc))
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions
    )


def _add_super_meta_annotations(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    sfreq: float,
    label_map: Dict[str, int]
) -> mne.Annotations:
    """Add super meta labels as separate annotation columns.
    
    Creates annotations for Task 1 (Reward Valence) and Task 2 (Feedback Modality).
    """
    base_annotations = raw.annotations
    
    if events_df.empty:
        return base_annotations
    
    # Create new annotations with super meta appended to description
    new_onsets = []
    new_durations = []
    new_descriptions = []
    
    for i, (onset, duration, desc) in enumerate(zip(
        base_annotations.onset,
        base_annotations.duration,
        base_annotations.description
    )):
        # Check if this annotation has a mapped label
        super_label = label_map.get(desc)
        
        if super_label is not None:
            # Create super meta annotation with task label appended
            task_desc = f"{desc}::super_task={super_label}"
            new_onsets.append(onset)
            new_durations.append(duration)
            new_descriptions.append(task_desc)
    
    if not new_onsets:
        return base_annotations
    
    return mne.Annotations(
        onset=new_onsets,
        duration=new_durations,
        description=new_descriptions
    )


@dataclass
class OpenNeuroDS003822Kernel:
    """Stage1 kernel for OpenNeuro ds003822 dataset.
    
    Probabilistic Learning with Affective Feedback - Experiment #1
    
    This kernel:
    - Reads BIDS-formatted EEG data from OpenNeuro
    - Renames channels to standard 10-20 names where applicable
    - Creates annotations from events.tsv
    - Maps S1xx event codes to descriptive labels
    - Sets eegunity_description with subject and device metadata
    """
    
    KERNEL_ID: str = "openneuro-ds003822-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", row.get("file_path", ""))
        subject_id = row.get("subject_id", row.get("Subject ID", "unknown"))
        
        # Build path to events.tsv
        base_dir = os.path.dirname(file_path)
        events_path = None
        
        # Search for events.tsv in BIDS structure
        for root, dirs, files in os.walk(base_dir):
            for f in files:
                if f.endswith("_events.tsv"):
                    events_path = os.path.join(root, f)
                    break
            if events_path:
                break
        
        # Parse events if available
        events_df = pd.DataFrame()
        if events_path and os.path.exists(events_path):
            events_df = _parse_events_tsv(events_path)
        
        # Rename channels to standard names BEFORE set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Try to set standard montage (66 channels suggests extended cap)
        try:
            # Standard 1020 system for 66 channels
            raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass  # Montage setting is optional if cap is non-standard
        
        # Create raw annotations from events
        sfreq = raw.info["sfreq"]
        raw_annotations = _create_annotations_from_events(raw, events_df, sfreq)
        raw.set_annotations(raw_annotations)
        
        # Add super meta annotations for Task 1: Reward Valence
        reward_annotations = _add_super_meta_annotations(
            raw, events_df, sfreq, _REWARD_VALENCE_MAP
        )
        
        # Add super meta annotations for Task 2: Feedback Modality
        modality_annotations = _add_super_meta_annotations(
            raw, events_df, sfreq, _FEEDBACK_MODALITY_MAP
        )
        
        # Create combined super meta annotations
        # Both task labels are appended to create rich metadata
        combined_onsets = []
        combined_durations = []
        combined_descriptions = []
        
        for onset, duration, desc in zip(
            raw_annotations.onset,
            raw_annotations.duration,
            raw_annotations.description
        ):
            reward_label = _REWARD_VALENCE_MAP.get(desc)
            modality_label = _FEEDBACK_MODALITY_MAP.get(desc)
            
            if reward_label is not None or modality_label is not None:
                parts = [desc]
                if reward_label is not None:
                    parts.append(f"reward_valence={reward_label}")
                if modality_label is not None:
                    parts.append(f"feedback_modality={modality_label}")
                combined_onsets.append(onset)
                combined_durations.append(duration)
                combined_descriptions.append("::".join(parts))
        
        if combined_onsets:
            super_meta = mne.Annotations(
                onset=combined_onsets,
                duration=combined_durations,
                description=combined_descriptions
            )
            # Combine with raw annotations
            all_onsets = list(raw_annotations.onset) + list(super_meta.onset)
            all_durations = list(raw_annotations.duration) + list(super_meta.duration)
            all_descriptions = list(raw_annotations.description) + list(super_meta.description)
            raw.set_annotations(mne.Annotations(
                onset=all_onsets,
                duration=all_durations,
                description=all_descriptions
            ))
        
        # Build eegunity_description
        # Annotator: LLM, 2026-04-08
        # Source: Paper DOI 10.3758/s13415-021-00950-5 indicates standard EEG lab setup
        # amplifier/cap/handedness: inferred by LLM, needs human review
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": "unknown",  # inferred by LLM, needs human review
                "sex": "unknown",  # inferred by LLM, needs human review
                "amplifier": "BrainProducts BrainAmp",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS003822Kernel()