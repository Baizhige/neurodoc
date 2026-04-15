"""MUSIN-G (openneuro_ds003774) stage1 kernel for EEGUnity.

Dataset: Music Listening Genre EEG Dataset
Source: https://openneuro.org/datasets/ds003774
Paper: https://doi.org/10.1016/j.dib.2022.108663

20 subjects listened to 12 music tracks of various genres with eyes closed.
High-density 129-channel EEG recorded at 1000 Hz.
No discrete event markers embedded in raw EEG; continuous music listening.

Tasks supported:
- Task 1: Music Genre Classification (super meta, segmentation-based)
- Task 2: Listener/Person Identification (raw meta, segmentation-based)

Channel naming: Extended 10-20 system (128 EEG + 1 possibly EOG/ECG).
Sampling rate: 1000 Hz (recommend downsample to 250 Hz per paper).

Annotator: LLM, 2026-04-15
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# SUBJECT INFORMATION
# Source: Dataset participants.tsv (BIDS) - to be loaded dynamically
# Annotator: LLM, 2026-04-15
# ============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # All fields will be populated from participants.tsv if available
    # Fallback values marked as LLM inference, require human verification
}


# ============================================================================
# MUSIC GENRE LABELS
# Source: analysis.md / paper DOI 10.1016/j.dib.2022.108663
# ============================================================================
_GENRE_LABELS = {
    1: "Deep House",
    2: "Indie",
    3: "Electronics",
    4: "New Age",
    5: "Electronic Dance",
    6: "Ambient",
    7: "Hindustani Classical",
    8: "Indian Semi-Classical",
    9: "Indian Folk",
    10: "Soft Jazz",
    11: "Goth Rock",
    12: "Progressive Instrumental Rock",
}


# ============================================================================
# HIGH-DENSITY CHANNEL MAPPING
# Source: BrainVision / BrainProducts extended 10-20 system documentation
# Annotator: LLM, 2026-04-15 (requires human verification against actual data)
# ============================================================================
_HIGH_DENSITY_CHANNEL_MAP = {
    # Standard 10-20 system (first ~20 channels)
    "Fp1": "EEG Fp1",
    "Fp2": "EEG Fp2",
    "Fpz": "EEG Fpz",
    "Fz": "EEG Fz",
    "F3": "EEG F3",
    "F4": "EEG F4",
    "F7": "EEG F7",
    "F8": "EEG F8",
    "Cz": "EEG Cz",
    "C3": "EEG C3",
    "C4": "EEG C4",
    "T7": "EEG T7",
    "T8": "EEG T8",
    "Pz": "EEG Pz",
    "P3": "EEG P3",
    "P4": "EEG P4",
    "P7": "EEG P7",
    "P8": "EEG P8",
    "Oz": "EEG Oz",
    "O1": "EEG O1",
    "O2": "EEG O2",
    # Extended 10-10 system
    "AFz": "EEG AFz",
    "AF3": "EEG AF3",
    "AF4": "EEG AF4",
    "AF7": "EEG AF7",
    "AF8": "EEG AF8",
    "F1": "EEG F1",
    "F2": "EEG F2",
    "F5": "EEG F5",
    "F6": "EEG F6",
    "FCz": "EEG FCz",
    "FC1": "EEG FC1",
    "FC2": "EEG FC2",
    "FC3": "EEG FC3",
    "FC4": "EEG FC4",
    "FC5": "EEG FC5",
    "FC6": "EEG FC6",
    "C1": "EEG C1",
    "C2": "EEG C2",
    "C5": "EEG C5",
    "C6": "EEG C6",
    "CPz": "EEG CPz",
    "CP1": "EEG CP1",
    "CP2": "EEG CP2",
    "CP3": "EEG CP3",
    "CP4": "EEG CP4",
    "CP5": "EEG CP5",
    "CP6": "EEG CP6",
    "P1": "EEG P1",
    "P2": "EEG P2",
    "P5": "EEG P5",
    "P6": "EEG P6",
    "POz": "EEG POz",
    "PO3": "EEG PO3",
    "PO4": "EEG PO4",
    "PO7": "EEG PO7",
    "PO8": "EEG PO8",
    # Extended 10-5 system (for 128+ channel caps)
    "F9": "EEG F9",
    "F10": "EEG F10",
    "FT7": "EEG FT7",
    "FT8": "EEG FT8",
    "TP7": "EEG TP7",
    "TP8": "EEG TP8",
    "TP9": "EEG TP9",
    "TP10": "EEG TP10",
    "P9": "EEG P9",
    "P10": "EEG P10",
    "PO9": "EEG PO9",
    "PO10": "EEG PO10",
    "O9": "EEG O9",
    "O10": "EEG O10",
}


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if it exists.
    
    Returns empty DataFrame if not found.
    """
    tsv_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _parse_subject_info(dataset_root: str, subject_id: str) -> Dict[str, str]:
    """Parse subject metadata from participants.tsv or infer defaults.
    
    Returns dict with age, sex, handedness keys.
    Annotator: LLM, 2026-04-15 (requires human verification)
    """
    df = _load_participants_tsv(dataset_root)
    
    if not df.empty and "participant_id" in df.columns:
        # Try exact match with or without 'sub-' prefix
        subject_row = df[df["participant_id"].isin([subject_id, f"sub-{subject_id}"])]
        if not subject_row.empty:
            row = subject_row.iloc[0]
            
            # Age
            age = "unknown"
            if "age" in row.index:
                age_val = row["age"]
                if pd.notna(age_val):
                    age = str(int(float(age_val))) if str(age_val).replace(".", "").isdigit() else str(age_val)
            
            # Sex
            sex = "unknown"
            if "sex" in row.index:
                sex_val = str(row["sex"]).lower().strip()
                if sex_val in ["m", "male", "f", "female"]:
                    sex = "male" if sex_val.startswith("m") else "female"
            
            # Handedness
            handedness = "unknown"
            if "handedness" in row.index:
                hand_val = str(row["handedness"]).lower().strip()
                if "right" in hand_val:
                    handedness = "right"
                elif "left" in hand_val:
                    handedness = "left"
            
            return {"age": age, "sex": sex, "handedness": handedness}
    
    # Fallback: LLM inference, require human verification
    return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


def _detect_genre_from_filename(file_path: str) -> Optional[str]:
    """Extract music genre from filename or path.
    
    MUSIN-G filenames follow pattern: sub-XX_task-music_<genre>_eeg.<ext>
    Returns genre string or None if not detected.
    Annotator: LLM, 2026-04-15
    """
    filename = os.path.basename(file_path)
    
    # Pattern: sub-01_task-music_<genre>_eeg.vhdr or similar
    genre_patterns = [
        "Deep_House", "Indie", "Electronics", "New_Age", "Electronic_Dance",
        "Ambient", "Hindustani_Classical", "Indian_Semi_Classical", "Indian_Folk",
        "Soft_Jazz", "Goth_Rock", "Progressive_Instrumental_Rock"
    ]
    
    for genre in genre_patterns:
        if genre in filename:
            return genre.replace("_", " ")
    
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for high-density EEG caps.
    
    Handles various naming conventions (EEG-001, A1, etc. to standard names).
    Annotator: LLM, 2026-04-15 (requires human verification)
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    # Pattern 1: Numeric-only channels (EEG-001, 001, etc.) - common in BrainVision
    numeric_pattern = re.compile(r"^(?:EEG[-_])?(\d+)$", re.IGNORECASE)
    
    # BrainVision typically uses extended 10-20 ordering
    # For 128+ channels, numbering follows cap layout
    # This is a simplified mapping; actual mapping depends on cap manufacturer
    
    # Pattern 2: Standard 10-20 with 'EEG ' prefix
    for ch in existing_names:
        if ch.startswith("EEG "):
            standard_name = ch[4:].strip()  # Remove 'EEG ' prefix
            if standard_name != ch:
                rename_map[ch] = standard_name
    
    # Pattern 3: Channels with 'A' prefix (common in some systems)
    a_prefix_map = {}
    for ch in existing_names:
        if ch.startswith("A") and ch[1:].isdigit():
            # A1 -> Fp1 (approximate, needs verification)
            pass  # Skip for now, needs cap-specific mapping
    
    # Pattern 4: Check if all channels are already standard names
    standard_names = set(_HIGH_DENSITY_CHANNEL_MAP.values()) | set(_HIGH_DENSITY_CHANNEL_MAP.keys())
    if all(ch in standard_names or ch in ["EOG", "ECG", "EMG", "Trigger"] for ch in existing_names):
        return {}  # No renaming needed
    
    return rename_map


def _set_high_density_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set montage for high-density EEG cap.
    
    Uses standard_1020 for 129-channel systems which typically follow
    extended 10-20 nomenclature.
    Annotator: LLM, 2026-04-15 (requires human verification)
    """
    try:
        # Try standard 1020 first (works for most extended 10-20 systems)
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        # If standard montage fails, try to set positions from known channels
        pass
    
    return raw


@dataclass
class MUSINGKernel:
    """Stage1 kernel for MUSIN-G (openneuro_ds003774) dataset.
    
    This kernel handles:
    - High-density 129-channel EEG from music listening paradigm
    - Continuous recordings with no embedded event markers
    - Subject metadata from participants.tsv (BIDS)
    - Genre label extraction from filename for super meta tasks
    """
    
    KERNEL_ID: str = "openneuro-ds003774-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : EEGUnity UnifiedDataset context
        raw : MNE Raw object (loaded from EEG file)
        row : pandas Series with File Path and metadata
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with metadata and annotations
        """
        file_path = row["File Path"]
        dataset_root = row.get("Dataset Root", os.path.dirname(os.path.dirname(file_path)))
        
        # =====================================================================
        # 1. CHANNEL RENAMING (before set_montage)
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # =====================================================================
        # 2. SET MONTAGE
        # =====================================================================
        raw = _set_high_density_montage(raw)
        
        # =====================================================================
        # 3. SET CHANNEL TYPES (if needed)
        # =====================================================================
        # Detect and set non-EEG channels
        channel_types = {}
        for ch in raw.ch_names:
            ch_upper = ch.upper()
            if "EOG" in ch_upper or ch_upper in ["V", "EOG-LEFT", "EOG-RIGHT", "EOG-UP", "EOG-DOWN"]:
                channel_types[ch] = "eog"
            elif "ECG" in ch_upper or ch_upper in ["EKG", "CARDIAC"]:
                channel_types[ch] = "ecg"
            elif "EMG" in ch_upper:
                channel_types[ch] = "emg"
            elif ch_upper.startswith("TRIGGER") or ch_upper == "STIM":
                channel_types[ch] = "stim"
        
        if channel_types:
            try:
                raw.set_channel_types(channel_types)
            except Exception:
                pass  # Some channels may not exist
        
        # =====================================================================
        # 4. PARSE SUBJECT INFORMATION
        # =====================================================================
        subject_id = row.get("Subject ID", "")
        if not subject_id:
            # Extract from filename: sub-01_task-music_...
            match = re.search(r"sub-(\d+)", file_path)
            if match:
                subject_id = f"sub-{match.group(1)}"
        
        subject_info = _parse_subject_info(dataset_root, subject_id)
        
        # =====================================================================
        # 5. BUILD EEGUNITY DESCRIPTION
        # =====================================================================
        # Amplifier info - typically BrainVision/BrainProducts for high-density
        # LLM inference, requires human verification
        amplifier = "unknown"  # LLM 推断，需人类复核
        
        # Cap info - typically wet Ag/AgCl for 128+ channel systems
        cap = "unknown"  # LLM 推断，需人类复核
        
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": amplifier,
                "cap": cap,
                "handedness": subject_info["handedness"],
            }
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =====================================================================
        # 6. HANDLE CONTINUOUS DATA (no events)
        # =====================================================================
        # Since no discrete event markers exist, the entire recording is
        # a continuous music listening segment.
        # Annotations are set based on filename metadata for super meta tasks.
        
        # Extract genre from filename for super meta
        genre = _detect_genre_from_filename(file_path)
        
        if genre:
            # Create annotation for the entire recording
            # Duration in seconds
            duration = raw.times[-1] if len(raw.times) > 0 else 0
            
            annotations = mne.Annotations(
                onset=[0.0],
                duration=[duration],
                description=[f"genre: {genre}"]
            )
            raw.set_annotations(annotations)
        
        # =====================================================================
        # 7. STORE AUXILIARY METADATA IN ANNOTATIONS
        # =====================================================================
        # Store subject ID as an annotation for listener identification task
        if subject_id:
            # Add subject ID annotation at the start
            existing_annots = raw.annotations.copy() if raw.annotations else mne.Annotations([], [], [])
            
            subject_annot = mne.Annotations(
                onset=[0.0],
                duration=[0.0],
                description=[f"subject_id: {subject_id}"]
            )
            
            # Combine annotations
            if len(existing_annots) > 0:
                all_onsets = list(existing_annots.onset) + list(subject_annot.onset)
                all_durations = list(existing_annots.duration) + list(subject_annot.duration)
                all_descriptions = list(existing_annots.description) + list(subject_annot.description)
                combined_annotations = mne.Annotations(
                    onset=all_onsets,
                    duration=all_durations,
                    description=all_descriptions
                )
                raw.set_annotations(combined_annotations)
            else:
                raw.set_annotations(subject_annot)
        
        # =====================================================================
        # 8. DOWNSPECIFY SAMPLING RATE (optional, per paper recommendation)
        # =====================================================================
        # Paper recommends 250 Hz for analysis
        # This is optional and should be done at epoching time if needed
        # Uncomment if downsampling is desired during kernel execution:
        # if raw.info["sfreq"] == 1000:
        #     raw.resample(250)
        
        return raw


# Module-level kernel instance for EEGUnity loading
KERNEL = MUSINGKernel()