"""openneuro_ds005169 stage1 kernel for EEGUnity.

Intracranial EEG during cortical stimulation evoking visual effects.
Dataset: 22 subjects, 112 files, 82 channels, 4096 Hz.

Clinical effect classification (6-class): cognitive, motor, sensory, autonomic, visual, language
Visual hallucination subtype classification (14-class): elementary, plus, minus, static, dynamic, 
    continuous, intermittent, whole_visual_field, center, peripheral, etc.

Source: https://openneuro.org/datasets/ds005169
Reference DOI: 10.1002/hbm.25749, 10.1016/j.brs.2025.05.138

NOTE: This dataset contains intracranial EEG (iEEG) from epilepsy patients undergoing 
presurgical evaluation with direct electrical stimulation (DES). Channel naming follows 
intracranial electrode naming conventions rather than standard 10-20 system.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import mne
import numpy as np


# Clinical effect labels (ILAE classification for stimulation-evoked effects)
# Source: DOI 10.1002/hbm.25749 - Table 1 ILAE classification
CLINICAL_EFFECT_LABELS = {
    "cognitive": 0,
    "motor": 1,
    "sensory": 2,
    "autonomic": 3,
    "visual": 4,
    "language": 5,
}

# Visual hallucination subtype labels
# Source: DOI 10.1016/j.brs.2025.05.138
VISUAL_HALLUCINATION_LABELS = {
    "elementary": 0,
    "plus": 1,
    "minus": 2,
    "static": 3,
    "dynamic": 4,
    "continuous": 5,
    "intermittent": 6,
    "whole_visual_field": 7,
    "center": 8,
    "peripheral": 9,
    "left_hemi": 10,
    "right_hemi": 11,
    "bilateral": 12,
    "unstructured": 13,
}

# Stimulation parameter annotation pattern
# Format: "Comment/[electrode] [mA] SYM"
STIM_PARAM_PATTERN = re.compile(r"Comment/(\S+)\s+(\d+\.?\d*)\s*(mA|uA)?\s*SYM?")

# UUID pattern for patient/trial-specific annotations to exclude
UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _detect_subject_id(row) -> str:
    """Extract subject ID from row file path."""
    file_path = str(row.get("File Path", ""))
    match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _detect_session_id(row) -> Optional[str]:
    """Extract session ID from row file path."""
    file_path = str(row.get("File Path", ""))
    match = re.search(r"ses-([A-Za-z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _load_bids_participants(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load participant information from BIDS participants.tsv.
    
    Returns dict of subject_id -> {age, sex, handedness}
    """
    participants_path = Path(dataset_path) / "participants.tsv"
    subject_info = {}
    
    if participants_path.exists():
        import pandas as pd
        try:
            df = pd.read_csv(participants_path, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", "")).replace("sub-", "")
                subject_info[subj_id] = {
                    "age": str(row.get("age", "unknown")),
                    "sex": str(row.get("sex", row.get("gender", "unknown"))).lower(),
                    "handedness": str(row.get("handedness", "unknown")).lower(),
                }
        except Exception:
            pass
    
    return subject_info


def _load_bids_channels(channel_file_path: str) -> Dict[str, str]:
    """Load channel type information from BIDS *_channels.tsv.
    
    Returns dict of channel_name -> channel_type (e.g., 'EEG', 'ECOG', 'SEEG')
    """
    channel_types = {}
    
    if Path(channel_file_path).exists():
        import pandas as pd
        try:
            df = pd.read_csv(channel_file_path, sep="\t")
            for _, row in df.iterrows():
                ch_name = str(row.get("name", ""))
                ch_type = str(row.get("type", "EEG")).upper()
                channel_types[ch_name] = ch_type
        except Exception:
            pass
    
    return channel_types


def _remap_raw_annotations(raw: mne.io.BaseRaw) -> Tuple[mne.Annotations, List[Dict[str, Any]]]:
    """Remap raw annotations to standardized event labels.
    
    Returns:
        - Processed annotations with standardized labels
        - List of event metadata dicts (for super meta derivation)
    """
    annotations = raw.annotations
    new_descriptions = []
    event_metadata = []
    
    stim_params = {}  # Track stimulation parameters per annotation
    
    for i, desc in enumerate(annotations.description):
        onset = annotations.onset[i]
        duration = annotations.duration[i]
        
        # Check for stimulation parameter annotation
        stim_match = STIM_PARAM_PATTERN.match(str(desc))
        if stim_match:
            electrode = stim_match.group(1)
            current = stim_match.group(2)
            stim_params[i] = {"electrode": electrode, "current_ma": float(current)}
            # Skip admin annotation
            new_descriptions.append("admin: stim_param")
            continue
        
        # Check for UUID annotation (patient/trial-specific, exclude)
        if UUID_PATTERN.search(str(desc)):
            new_descriptions.append("admin: uuid_annotation")
            continue
        
        # Standard event remapping
        desc_str = str(desc).strip()
        if desc_str == "Comment/prestim":
            new_descriptions.append("stimulation: baseline")
            event_metadata.append({
                "onset": onset,
                "duration": duration,
                "original_desc": desc_str,
                "event_type": "baseline",
                "idx": i,
            })
        elif desc_str == "Comment/poststim":
            new_descriptions.append("stimulation: response")
            event_metadata.append({
                "onset": onset,
                "duration": duration,
                "original_desc": desc_str,
                "event_type": "response",
                "idx": i,
            })
        else:
            # Keep original for unknown annotations
            new_descriptions.append(desc_str)
    
    # Create new annotations with remapped descriptions
    new_annotations = mne.Annotations(
        onset=annotations.onset,
        duration=annotations.duration,
        description=new_descriptions,
        orig_time=annotations.orig_time,
    )
    
    return new_annotations, event_metadata


def _derive_clinical_effects(event_metadata: List[Dict[str, Any]], 
                               clinical_notes: Optional[Dict[int, str]] = None) -> Dict[int, str]:
    """Derive clinical effect labels from event metadata and clinical notes.
    
    This maps patient-reported symptoms to the 6-class ILAE classification:
    - cognitive (0): changes in thinking, attention, memory
    - motor (1): movement, muscle contractions
    - sensory (2): tingling, sensations
    - autonomic (3): heart rate, breathing, sweating
    - visual (4): hallucinations, visual disturbances
    - language (5): speech, word finding difficulties
    
    NOTE: In the absence of explicit clinical notes in the raw data, this function
    returns empty dicts and relies on external annotation files or paper-based mapping.
    
    Parameters:
        event_metadata: List of event dicts with onset/duration/type
        clinical_notes: Optional dict mapping event idx -> clinical effect description
    
    Returns:
        Dict mapping annotation index -> clinical effect label string
    """
    # If no clinical notes provided, return empty dict
    # Clinical effect derivation requires external mapping from DOI 10.1002/hbm.25749
    if clinical_notes is None:
        return {}
    
    effect_map = {}
    for idx, note in clinical_notes.items():
        note_lower = str(note).lower()
        
        if any(k in note_lower for k in ["visual", "hallucination", "phosphene", "flash"]):
            effect_map[idx] = "visual"
        elif any(k in note_lower for k in ["motor", "movement", "twitch", "contraction"]):
            effect_map[idx] = "motor"
        elif any(k in note_lower for k in ["sensory", "tingling", "paresthesia", "numb"]):
            effect_map[idx] = "sensory"
        elif any(k in note_lower for k in ["cognitive", "memory", "attention", "confusion"]):
            effect_map[idx] = "cognitive"
        elif any(k in note_lower for k in ["autonomic", "heart", "sweat", "breath"]):
            effect_map[idx] = "autonomic"
        elif any(k in note_lower for k in ["language", "speech", "aphasia", "word"]):
            effect_map[idx] = "language"
        else:
            effect_map[idx] = "unknown"
    
    return effect_map


def _derive_visual_subtypes(event_metadata: List[Dict[str, Any]],
                             visual_notes: Optional[Dict[int, str]] = None) -> Dict[int, str]:
    """Derive visual hallucination subtype labels from event metadata.
    
    14-class classification:
    - elementary (0): basic shapes, colors, lights
    - plus (1): additional elements perceived
    - minus (2): missing elements from visual field
    - static (3): stationary hallucinations
    - dynamic (4): moving hallucinations
    - continuous (5): sustained perception
    - intermittent (6): episodic perception
    - whole_visual_field (7): entire visual field affected
    - center (8): central vision
    - peripheral (9): peripheral vision
    - left_hemi (10): left visual field
    - right_hemi (11): right visual field
    - bilateral (12): bilateral perception
    - unstructured (13): no clear structure
    
    Returns:
        Dict mapping annotation index -> visual subtype label string
    """
    if visual_notes is None:
        return {}
    
    subtype_map = {}
    for idx, note in visual_notes.items():
        note_lower = str(note).lower()
        
        if "whole" in note_lower or "entire" in note_lower:
            subtype_map[idx] = "whole_visual_field"
        elif "center" in note_lower or "central" in note_lower:
            subtype_map[idx] = "center"
        elif "peripheral" in note_lower:
            subtype_map[idx] = "peripheral"
        elif "left" in note_lower:
            subtype_map[idx] = "left_hemi"
        elif "right" in note_lower:
            subtype_map[idx] = "right_hemi"
        elif "bilateral" in note_lower:
            subtype_map[idx] = "bilateral"
        
        # Elementary vs structured
        if any(k in note_lower for k in ["color", "light", "flash", "phosphene", "dot"]):
            if idx not in subtype_map:
                subtype_map[idx] = "elementary"
        elif any(k in note_lower for k in ["face", "object", "person", "shape"]):
            if idx not in subtype_map:
                subtype_map[idx] = "structured"
        
        # Dynamic vs static
        if any(k in note_lower for k in ["moving", "motion", "dynamic"]):
            if idx not in subtype_map:
                subtype_map[idx] = "dynamic"
        elif any(k in note_lower for k in ["static", "still"]):
            if idx not in subtype_map:
                subtype_map[idx] = "static"
        
        # Continuous vs intermittent
        if any(k in note_lower for k in ["continuous", "constant", "sustained"]):
            if idx not in subtype_map:
                subtype_map[idx] = "continuous"
        elif any(k in note_lower for k in ["intermittent", "brief", "episodic"]):
            if idx not in subtype_map:
                subtype_map[idx] = "intermittent"
        
        if idx not in subtype_map:
            subtype_map[idx] = "unstructured"
    
    return subtype_map


def _infer_channel_types(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Infer channel types from naming conventions in intracranial EEG.
    
    Common patterns:
    - 'ECOG' or 'EcoG' -> ECoG (Electrocorticography)
    - 'SEEG' or 'Depth' -> SEEG (Stereo-EEG)
    - 'EEG' -> EEG
    - 'EMG', 'EOG', 'ECG' -> respective types
    
    Source: DOI 10.1002/hbm.25749 - intracranial electrode naming
    """
    type_map = {}
    
    for ch_name in raw.ch_names:
        ch_upper = ch_name.upper()
        
        if "ECOG" in ch_upper or "ECOG" in ch_upper:
            type_map[ch_name] = "ecog"
        elif "SEEG" in ch_upper or "DEPTH" in ch_upper:
            type_map[ch_name] = "seeg"
        elif ch_upper.startswith("EEG"):
            type_map[ch_name] = "eeg"
        elif ch_upper.startswith("EMG"):
            type_map[ch_name] = "emg"
        elif ch_upper.startswith("EOG"):
            type_map[ch_name] = "eog"
        elif ch_upper.startswith("ECG"):
            type_map[ch_name] = "ecg"
        elif ch_upper in ["GND", "REF", "GROUND"]:
            type_map[ch_name] = "misc"
        else:
            # Default to eeg for intracranial
            type_map[ch_name] = "eeg"
    
    return type_map


@dataclass
class OpenNeuroDS005169Kernel:
    """Stage1 kernel for the openneuro_ds005169 dataset.
    
    Intracranial EEG during cortical stimulation evoking visual effects.
    Contains events for pre-stimulation baseline (Comment/prestim) and 
    post-stimulation response (Comment/poststim).
    """
    
    KERNEL_ID: str = "openneuro-ds005169-stage1"
    
    # Dataset path for BIDS metadata lookup
    _dataset_path: Optional[str] = None
    _participants_info: Optional[Dict[str, Dict[str, str]]] = None
    
    def __post_init__(self):
        """Initialize BIDS metadata lookup."""
        # Try to find dataset path from environment or default location
        self._dataset_path = os.environ.get("OPENNEURO_DS005169_PATH", 
                                            "/data/openneuro_ds005169")
        
        if os.path.exists(self._dataset_path):
            self._participants_info = _load_bids_participants(self._dataset_path)
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = str(row.get("File Path", ""))
        
        # Extract subject and session info
        subject_id = _detect_subject_id(row)
        session_id = _detect_session_id(row)
        
        # Get subject info from BIDS participants.tsv
        subject_info = {}
        if self._participants_info and subject_id in self._participants_info:
            subject_info = self._participants_info[subject_id]
        else:
            # inferred by LLM, needs human review
            subject_info = {
                "age": "unknown",
                "sex": "unknown",
                "handedness": "unknown",
            }
        
        # Determine amplifier from file metadata or dataset description
        # inferred by LLM, needs human review - typically intracranial EEG systems
        amplifier = "unknown"
        
        # Determine cap type for intracranial EEG
        # inferred by LLM, needs human review - intracranial uses depth/grid electrodes
        cap = "unknown"
        
        # Update raw.info["description"] with eegunity_description
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower() if subject_info.get("sex") else "unknown",
                "amplifier": amplifier,
                "cap": cap,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Remap raw annotations to standardized event labels
        new_annotations, event_metadata = _remap_raw_annotations(raw)
        raw.set_annotations(new_annotations)
        
        # Infer and set channel types for intracranial EEG
        channel_type_map = _infer_channel_types(raw)
        try:
            raw.set_channel_types(channel_type_map)
        except Exception:
            # Some channels may not support type remapping
            pass
        
        # Add raw meta: stimulation protocol events
        # Events are already in annotations as 'stimulation: baseline' / 'stimulation: response'
        pass
        
        # Add super meta: clinical effect labels (6-class)
        # NOTE: Clinical effects require mapping from clinical notes which are not 
        # directly available in raw annotations. This kernel provides the infrastructure
        # for external mapping via _derive_clinical_effects().
        # 
        # To enable clinical effect labels, provide clinical_notes dict:
        # clinical_notes = {annotation_idx: "visual hallucination", ...}
        # effect_map = _derive_clinical_effects(event_metadata, clinical_notes)
        # 
        # For now, we mark events with placeholder for external derivation
        
        # Add super meta: visual hallucination subtypes (14-class)
        # Same note as above - requires clinical notes mapping
        
        # Store event metadata in raw.info for downstream kernel access
        raw.info["openneuro_ds005169_meta"] = json.dumps({
            "subject_id": subject_id,
            "session_id": session_id,
            "n_events": len(event_metadata),
            "stim_events": [e for e in event_metadata if e.get("event_type") in ["baseline", "response"]],
        })
        
        return raw


KERNEL = OpenNeuroDS005169Kernel()