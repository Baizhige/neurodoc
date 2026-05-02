"""openneuro_ds003645 stage1 kernel for EEGUnity.

Face Processing MEEG Dataset with HED Annotation.
Dataset: Wakeman & Henson (2015) face perception replication with HED tags.

This kernel handles the 395-channel MEEG dataset by isolating EEG channels,
parsing HED-annotated events from events.tsv, and mapping face stimulus events
to classification labels.

Source: https://openneuro.org/datasets/ds003645
References:
  - Wakeman & Henson (2015) DOI: 10.1038/sdata.2015.1
  - Henry et al. (2021) DOI: 10.1016/j.neuroimage.2021.118766 (HED annotation)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Set

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Dataset Metadata (from paper/references, LLM inference marked)
# =============================================================================

# Source: Paper DOI 10.1038/sdata.2015.1 - Wakeman & Henson face dataset
# inferred by LLM, needs human review: Age range 22-45 based on typical young adult subject pool
# inferred by LLM, needs human review: Device is likely Elekta/BTi MEG system with EEG
_SUBJECT_METADATA: Dict[str, Dict[str, str]] = {
    # Subjects were healthy adults; specific demographics from participants.tsv
    # will override these defaults when available
}

# EEG channel count in MEEG dataset - isolate from 395 total channels
# Source: Dataset documentation / paper
# inferred by LLM, needs human review: Approximately 70 EEG channels in standard 1020 layout
_EEG_CHANNEL_COUNT_APPROX: int = 70

# Amplifier/device information
# Source: Wakeman & Henson paper DOI 10.1038/sdata.2015.1
# inferred by LLM, needs human review: Elekta Neuromag MEG system with EEG acquisition
_AMPLIFIER: str = "Elekta Neuromag"  # inferred by LLM, needs human review
_CAP: str = "Ag/AgCl"  # inferred by LLM, needs human review - standard EEG cap

# =============================================================================
# Face Stimulus Event Mapping
# =============================================================================

# Trial type labels from events.tsv trial_type column
# Source: Dataset sidecar / analysis.md
_FACE_EVENT_MAP: Dict[str, int] = {
    "famous": 0,          # Famous/familiar face stimulus
    "familiar_face": 0,   # Alternative label for familiar faces
    "unfamiliar_face": 1, # Unfamiliar/non-famous face stimulus
    "scrambled_face": 2,  # Scrambled face stimulus (control)
    # Additional possible labels from dataset
    "Famous_Familiar": 0,
    "Famous": 0,
    "Unfamiliar": 1,
    "Scrambled": 2,
}

# Reverse mapping for label lookups
_EVENT_ID_MAP: Dict[int, str] = {v: k for k, v in _FACE_EVENT_MAP.items()}


# =============================================================================
# EEG Channel Name Standardization
# =============================================================================

# Standard 10-20 EEG channel names that may appear in MEEG data
_STANDARD_EEG_CHANNELS: Set[str] = {
    "Fp1", "Fpz", "Fp2",
    "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "FC5", "FC1", "FC2", "FC6",
    "CP5", "CP1", "CP2", "CP6",
    "PO7", "PO3", "PO4", "PO8",
    "FT7", "FT8",
    "TP7", "TP8",
    "POz",
    # Additional extended 10-20 positions
    "F1", "F2", "F5", "F6",
    "C1", "C2", "C5", "C6",
    "P1", "P2", "P5", "P6",
    "PO5", "PO6",
    "AFz", "FCz", "CPz", "POz",
}


def _is_eeg_channel(ch_name: str) -> bool:
    """Check if channel name is likely an EEG channel.
    
    EEG channels in MEEG data typically have standard 10-20 names
    or EEG prefix. MEG channels have MEG prefix or special codes.
    """
    ch_upper = ch_name.upper()
    
    # Exclude MEG channels
    if ch_upper.startswith("MEG"):
        return False
    if "MAG" in ch_upper or "GRAD" in ch_upper:
        return False
    
    # Exclude other non-EEG
    if ch_upper.startswith("EOG") or ch_upper.startswith("ECG"):
        return False
    if ch_upper.startswith("STIM") or ch_upper.startswith("MISC"):
        return False
    if "TRIGGER" in ch_upper:
        return False
    
    # Include EEG prefixed channels
    if ch_upper.startswith("EEG"):
        return True
    
    # Include standard 10-20 channel names
    if ch_name in _STANDARD_EEG_CHANNELS:
        return True
    
    # Include if matches standard pattern (letter + number)
    if re.match(r"^[A-Za-z]+[0-9]+$", ch_name):
        # Could be EEG channel like F3, P4, etc.
        base = re.match(r"^([A-Za-z]+)", ch_name).group(1)
        if base in ["Fp", "F", "T", "C", "P", "O", "AF", "FC", "CP", "PO", "FT", "TP"]:
            return True
    
    return False


def _rename_to_standard(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename channels to standard 10-20 nomenclature where possible.
    
    MEEG datasets may use various naming conventions. This attempts to
    standardize EEG channel names while preserving MEG channels.
    """
    rename_map: Dict[str, str] = {}
    
    for ch_name in raw.ch_names:
        if not _is_eeg_channel(ch_name):
            continue
            
        ch_upper = ch_name.upper()
        
        # Handle EEG-XXX format (e.g., EEG-001 -> try to map to standard)
        if ch_upper.startswith("EEG-"):
            # Extract number and try to infer position
            num_str = ch_name[4:]
            if num_str.isdigit():
                # Common mapping: EEG-001 often corresponds toFp1
                # This is dataset-specific; mark as needs verification
                pass  # Keep original if can't map
        
        # Handle alternative spellings/variants
        # e.g., 'Fpz' vs 'Fpz' - normalize to standard
        
        # Currently just ensure proper case
        if ch_name != ch_name.capitalize() and ch_name not in rename_map:
            # Check if it's a standard name with wrong case
            for std_ch in _STANDARD_EEG_CHANNELS:
                if std_ch.lower() == ch_name.lower():
                    rename_map[ch_name] = std_ch
                    break
    
    if rename_map:
        raw.rename_channels(rename_map)
    
    return raw


def _try_set_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Attempt to set standard 10-20 montage for EEG channels."""
    try:
        # Get current EEG channel names
        eeg_chs = [ch for ch in raw.ch_names if _is_eeg_channel(ch)]
        
        # Try standard 1020 montage
        montage = mne.channels.make_standard_montage("standard_1020")
        
        # Find matching channels
        available = set(montage.ch_names) & set(eeg_chs)
        if len(available) >= 10:  # At least 10 channels should match
            raw.set_montage(montage, on_missing="ignore")
        else:
            # Try to match more loosely
            raw.set_montage(montage, on_missing="warn")
    except Exception:
        # Montage setting failed; continue without spatial info
        pass
    
    return raw


def _parse_events_tsv(events_tsv_path: str) -> pd.DataFrame:
    """Parse events.tsv file and extract face stimulus events.
    
    Returns DataFrame with onset, duration, trial_type columns.
    """
    if not os.path.exists(events_tsv_path):
        return pd.DataFrame()
    
    try:
        events_df = pd.read_csv(events_tsv_path, sep="\t")
        
        # Standard BIDS events.tsv columns
        required_cols = ["onset", "duration"]
        if not all(col in events_df.columns for col in required_cols):
            return pd.DataFrame()
        
        # trial_type column contains face stimulus labels
        if "trial_type" in events_df.columns:
            # Filter to face stimulus events only
            face_labels = list(_FACE_EVENT_MAP.keys()) + [
                "Famous", "famous", "Famous_Familiar",
                "unfamiliar", "Unfamiliar",
                "scrambled", "Scrambled"
            ]
            events_df = events_df[
                events_df["trial_type"].isin(face_labels) |
                events_df["trial_type"].str.contains("face", case=False, na=False)
            ]
        
        return events_df
    except Exception:
        return pd.DataFrame()


def _build_annotations_from_events(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame
) -> mne.Annotations:
    """Convert events DataFrame to MNE Annotations."""
    if events_df.empty:
        return mne.Annotations(
            onset=np.array([]),
            duration=np.array([]),
            description=np.array([], dtype=str)
        )
    
    onsets = events_df["onset"].values
    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(events_df))
    descriptions = events_df["trial_type"].values
    
    # Standardize trial_type names
    standardized = []
    for desc in descriptions:
        desc_str = str(desc).lower().strip()
        if desc_str in ["famous", "famous_familiar", "familiar_face"]:
            standardized.append("famous")
        elif desc_str in ["unfamiliar", "unfamiliar_face"]:
            standardized.append("unfamiliar")
        elif desc_str in ["scrambled", "scrambled_face"]:
            standardized.append("scrambled")
        else:
            standardized.append(str(desc))
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=np.array(standardized)
    )


def _get_subject_info(udataset, row) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or defaults."""
    subject_id = row.get("participant_id", "")
    
    # Try to load from participants.tsv
    dataset_path = udataset.dataset_path if hasattr(udataset, 'dataset_path') else ""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    
    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t")
            if "participant_id" in df.columns:
                subj_row = df[df["participant_id"] == subject_id]
                if not subj_row.empty:
                    row_data = subj_row.iloc[0]
                    
                    # Extract age
                    age = "unknown"
                    if "age" in df.columns:
                        age_val = row_data.get("age")
                        if pd.notna(age_val):
                            age = str(age_val).strip()
                    
                    # Extract sex
                    sex = "unknown"
                    if "sex" in df.columns:
                        sex_val = row_data.get("sex")
                        if pd.notna(sex_val):
                            sex_str = str(sex_val).lower().strip()
                            if sex_str in ["m", "male", "f", "female"]:
                                sex = "male" if sex_str.startswith("m") else "female"
                    
                    return {
                        "age": age,
                        "sex": sex,
                        "handedness": "unknown"  # Not typically in participants.tsv
                    }
        except Exception:
            pass
    
    # Default from metadata dict if available
    if subject_id in _SUBJECT_METADATA:
        return _SUBJECT_METADATA[subject_id]
    
    # Unknown defaults
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown"
    }


def _isolate_eeg_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Create a copy with only EEG channels from MEEG data.
    
    The original dataset has 395 channels (MEG + EEG). This extracts
    only the EEG channels for EEGUnity analysis.
    """
    eeg_channels = [ch for ch in raw.ch_names if _is_eeg_channel(ch)]
    
    if len(eeg_channels) == 0:
        # No EEG channels found, return original
        return raw
    
    # Pick only EEG channels
    raw_eeg = raw.pick_channels(eeg_channels, ordered=False)
    
    return raw_eeg


# =============================================================================
# Main Kernel Class
# =============================================================================

class OpenNeuroDS003645Kernel:
    """Stage1 kernel for openneuro_ds003645 face processing MEEG dataset.
    
    This kernel:
    1. Isolates EEG channels from 395-channel MEEG data
    2. Parses HED-annotated events from events.tsv
    3. Standardizes face stimulus event labels
    4. Sets channel names and optional montage
    5. Populates eegunity_description metadata
    """
    
    KERNEL_ID: str = "openneuro-ds003645-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single MEEG record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (MEEG format)
        row : Locator row with file path and subject info
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed EEG data with annotations and metadata
        """
        # Step 1: Isolate EEG channels from MEEG
        raw = _isolate_eeg_channels(raw)
        
        # Step 2: Rename channels to standard 10-20 nomenclature
        raw = _rename_to_standard(raw)
        
        # Step 3: Try to set montage for spatial positions
        raw = _try_set_montage(raw)
        
        # Step 4: Parse events from events.tsv
        file_path = row.get("file_path", row.get("File Path", ""))
        events_tsv_path = _find_events_tsv(file_path, udataset)
        
        if events_tsv_path and os.path.exists(events_tsv_path):
            events_df = _parse_events_tsv(events_tsv_path)
            if not events_df.empty:
                annotations = _build_annotations_from_events(raw, events_df)
                raw.set_annotations(annotations)
        
        # Step 5: Set eegunity_description metadata
        subject_info = _get_subject_info(udataset, row)
        
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


def _find_events_tsv(file_path: str, udataset) -> Optional[str]:
    """Find the events.tsv file corresponding to the given data file.
    
    In BIDS datasets, events.tsv is typically in the same directory as
    the data file or in a sibling task directory.
    """
    if not file_path:
        return None
    
    base_dir = os.path.dirname(file_path)
    
    # Check common locations
    search_paths = [
        os.path.join(base_dir, "events.tsv"),
        os.path.join(base_dir, "..", "events.tsv"),
        os.path.join(base_dir, "..", "..", "events.tsv"),
        os.path.join(base_dir.replace("_eeg", "_beh"), "events.tsv"),
    ]
    
    # Also check for task-specific events
    # Pattern: sub-XX/ses-XX/func/sub-XX_ses-XX_task-XX_events.tsv
    filename = os.path.basename(file_path)
    if filename.startswith("sub-"):
        # Extract subject and task info from filename
        parts = filename.split("_")
        for part in parts:
            if part.startswith("sub-"):
                sub = part
            elif part.startswith("ses-"):
                ses = part
            elif part.startswith("task-"):
                task = part
        
        # Construct expected events path
        if "sub" in locals():
            events_name = f"{sub}_{ses}_{task}_events.tsv" if "ses" in locals() else f"{sub}_task-{task.split('-')[1]}_events.tsv"
            search_paths.append(os.path.join(base_dir, events_name))
    
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    return None


# Module-level kernel instance for EEGUnity loading
KERNEL = OpenNeuroDS003645Kernel()