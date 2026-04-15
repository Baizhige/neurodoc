"""Ear-EEG Sleep Monitoring 2023 (EESM23) stage1 kernel for EEGUnity.

Dataset: openneuro_ds005178
Source: https://openneuro.org/datasets/ds005178
DOI: 10.3389/fnins.2023.987578, 10.1038/s41597-025-04579-8

Ear-EEG sleep monitoring dataset with 5 in-ear EEG channels at 250 Hz.
Sleep stage annotations (W/N1/N2/N3/REM) are stored in BIDS events.tsv files.
Manual PSG scoring following AASM standard performed by trained technicians.

Channel naming: ch1-ch5 (left ear, right ear, left ear ref, right ear ref, ref)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Sleep stage event labels from BIDS events.tsv
# Source: EESM23 dataset documentation, DOI: 10.1038/s41597-025-04579-8
_SLEEP_STAGE_LABELS = [
    "sleep_stage_W",
    "sleep_stage_N1",
    "sleep_stage_N2",
    "sleep_stage_N3",
    "sleep_stage_REM",
]


def _detect_subject(file_path: str) -> str:
    """Extract subject ID from BIDS file path (e.g., sub-01 -> 01)."""
    match = re.search(r"sub-(\d+)", file_path)
    return match.group(1) if match else "unknown"


def _read_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from BIDS root directory."""
    participants_path = os.path.join(bids_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return None


def _load_subject_info(bids_root: str, subject_id: str) -> Tuple[str, str]:
    """Load subject age and sex from BIDS participants.tsv.
    
    Returns:
        Tuple of (age, sex). Unknown values are marked with # LLM 推断，需人类复核.
    """
    df = _read_participants_tsv(bids_root)
    if df is None:
        return "unknown", "unknown"
    
    # Find matching subject row (participant_id format: sub-01)
    subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
    if subject_col not in df.columns:
        return "unknown", "unknown"
    
    subject_row = df[df[subject_col] == f"sub-{subject_id}"]
    if subject_row.empty:
        return "unknown", "unknown"
    
    row = subject_row.iloc[0]
    
    # Extract age (may be stored as integer or string)
    age_val = row.get("age", "unknown")
    if pd.notna(age_val):
        age = str(int(age_val)) if isinstance(age_val, float) else str(age_val)
    else:
        age = "unknown"  # LLM 推断，需人类复核
    
    # Extract sex (convert to lowercase)
    sex_val = row.get("sex", row.get("gender", "unknown"))
    if pd.notna(sex_val):
        sex_lower = str(sex_val).strip().lower()
        if sex_lower in ["m", "male", "f", "female"]:
            sex = "male" if sex_lower.startswith("m") else "female"
        else:
            sex = "unknown"  # LLM 推断，需人类复核
    else:
        sex = "unknown"  # LLM 推断，需人类复核
    
    return age, sex


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for ear-EEG channel naming.
    
    Ear-EEG channels are typically named ch1-ch5 or similar patterns.
    Standard ear-EEG naming: E1/E2 (ears), E3/E4 (references), REF.
    
    Source: Ear-EEG standard naming conventions, DOI: 10.3389/fnins.2023.987578
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    
    # Pattern 1: ch1, ch2, ch3, ch4, ch5 -> E1, E2, E3, E4, REF
    for i in range(1, 6):
        old_name = f"ch{i}"
        if old_name in existing:
            if i <= 4:
                rename_map[old_name] = f"E{i}"
            else:
                rename_map[old_name] = "REF"
    
    # Pattern 2: EEG 1, EEG 2, etc. (space separated)
    for i in range(1, 6):
        old_name = f"EEG {i}"
        if old_name in existing:
            if i <= 4:
                rename_map[old_name] = f"E{i}"
            else:
                rename_map[old_name] = "REF"
    
    # Pattern 3: Already standard ear-EEG names (E1-E4, REF, or similar)
    ear_eeg_aliases = {
        "E1": ["E1", "e1", "LE", "L"],
        "E2": ["E2", "e2", "RE", "R"],
        "E3": ["E3", "e3", "LRef", "LR"],
        "E4": ["E4", "e4", "RRef", "RR"],
        "REF": ["REF", "ref", "GND", "Ground", " Cz"],
    }
    for target, aliases in ear_eeg_aliases.items():
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    
    return rename_map


def _set_ear_eeg_montage(raw: mne.io.BaseRaw) -> None:
    """Set approximate montage for ear-EEG channels.
    
    Ear-EEG electrodes are placed in/around the ear canal.
    Using approximate 10-20 system positions for visualization.
    
    Note: Precise ear-EEG montage requires specialized ear templates.
    This provides approximate spatial distribution for visualization only.
    """
    try:
        # Standard 10-20 positions for approximate ear locations
        # T7/T8 for ears, Oz for reference position
        ch_names = raw.ch_names
        
        # Find ear channel positions
        montage_names = []
        positions = []
        
        for ch in ch_names:
            ch_upper = ch.upper()
            if ch_upper in ["E1", "E3"]:
                # Left ear: use T7 approximate
                montage_names.append(ch)
                positions.append((-0.08, -0.05, 0.0))  # Left side
            elif ch_upper in ["E2", "E4"]:
                # Right ear: use T8 approximate
                montage_names.append(ch)
                positions.append((0.08, -0.05, 0.0))  # Right side
            elif ch_upper in ["REF", "CZ"]:
                # Reference: use Cz approximate
                montage_names.append(ch)
                positions.append((0.0, 0.08, 0.0))  # Top center
        
        if len(positions) >= 2:
            # Create custom montage with available channels
            dig_points = [
                {
                    "kind": mne.io.constants.FIFF.FIFFV_POINT_EEG,
                    "ident": i,
                    "r": np.array(pos),
                    "frame": "head",
                }
                for i, pos in enumerate(positions)
            ]
            
            info = mne.create_info(ch_names=montage_names, sfreq=raw.info["sfreq"], ch_types="eeg")
            montage = mne.channels.DigMontage(dig_points=dig_points, ch_names=montage_names)
            raw.set_montage(montage, on_missing="warn")
        else:
            # Fallback: use standard 1020 for any matching channels
            raw.set_montage("standard_1020", on_missing="warn")
    except Exception:
        # If montage setting fails, continue without it
        pass


def _load_sleep_events(file_path: str) -> Optional[mne.Annotations]:
    """Load sleep stage events from BIDS events.tsv file.
    
    Sleep stages are stored in events.tsv with labels like:
    sleep_stage_W, sleep_stage_N1, sleep_stage_N2, sleep_stage_N3, sleep_stage_REM
    
    Source: EESM23 BIDS format, DOI: 10.1038/s41597-025-04579-8
    """
    # Find events.tsv file
    eeg_dir = os.path.dirname(file_path)
    
    # BIDS structure: sub-XX/eeg/sub-XX_task-sleep_events.tsv
    events_path = os.path.join(eeg_dir, os.path.basename(file_path).split(".")[0] + "_events.tsv")
    
    if not os.path.exists(events_path):
        # Try alternate naming pattern
        import glob
        events_files = glob.glob(os.path.join(eeg_dir, "*_events.tsv"))
        if events_files:
            events_path = events_files[0]
        else:
            return None
    
    try:
        events_df = pd.read_csv(events_path, sep="\t")
        
        # Identify event label column (trial_type, value, or similar)
        label_col = None
        for col in ["trial_type", "value", "event_label", "event_name"]:
            if col in events_df.columns:
                label_col = col
                break
        
        if label_col is None:
            return None
        
        # Filter for sleep stage events only
        mask = events_df[label_col].isin(_SLEEP_STAGE_LABELS)
        sleep_events = events_df[mask].copy()
        
        if sleep_events.empty:
            return None
        
        # Get onset and duration
        onset = sleep_events["onset"].values.astype(float)
        
        if "duration" in sleep_events.columns:
            duration = sleep_events["duration"].values.astype(float)
        else:
            # Default 30-second epochs for sleep staging
            duration = np.full(len(onset), 30.0)
        
        # Get event labels
        descriptions = sleep_events[label_col].values.tolist()
        
        # Create annotations
        annotations = mne.Annotations(
            onset=onset,
            duration=duration,
            description=descriptions,
        )
        
        return annotations
        
    except Exception:
        return None


class EESM23Kernel:
    """Stage1 kernel for EESM23 (Ear-EEG Sleep Monitoring 2023) dataset."""
    
    KERNEL_ID: str = "eesm23-stage1"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to EESM23 ear-EEG recording.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object with raw EEG data
        row : Locator row with file metadata
        
        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with metadata and annotations
        """
        file_path = row.get("File Path", str(row.get("file_path", "")))
        subject_id = _detect_subject(file_path)
        
        # Get BIDS root directory
        bids_root = os.path.dirname(os.path.dirname(file_path))
        
        # Load subject info from participants.tsv
        age, sex = _load_subject_info(bids_root, subject_id)
        
        # Build eegunity_description
        # Amplifier/cap/handedness: LLM 推断，需人类复核
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Rename channels BEFORE set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set ear-EEG montage (approximate positions)
        _set_ear_eeg_montage(raw)
        
        # Load sleep stage events from events.tsv
        sleep_annotations = _load_sleep_events(file_path)
        if sleep_annotations is not None:
            raw.set_annotations(sleep_annotations)
        
        return raw


KERNEL = EESM23Kernel()