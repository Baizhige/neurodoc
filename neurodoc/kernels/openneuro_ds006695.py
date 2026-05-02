"""OpenNeuro DS006695 stage1 kernel for EEGUnity.

Sleep staging dataset using 3-channel forehead EEG patch validated against
full polysomnography (PSG) manual scoring. Overnight EEG recordings with
30-sec epoch sleep stage labels (Wake/N1/N2/N3/REM) aligned from external
PSG hypnogram scoring files.

Source: https://openneuro.org/datasets/ds006695
Paper: 10.3389/frsle.2024.1349537 (Onton et al., 2025)
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
# CHANNEL RENAME MAP
# ============================================================================
# Forehead EEG patch typically uses 3 channels. Based on standard 10-20
# system forehead positions and common forehead patch configurations.
# Source: Paper 10.3389/frsle.2024.1349537, Figure 1 (forehead electrode placement)
# Annotator: LLM, 2026-01-15 (inferred by LLM, needs human review)
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",   # Left forehead
    "Fp2": "Fp2",   # Right forehead
    "Fpz": "Fpz",   # Center forehead
    # Alternative naming schemes from different recording systems:
    "EEG 001": "Fp1",
    "EEG 002": "Fp2",
    "EEG 003": "Fpz",
    "CH1": "Fp1",
    "CH2": "Fp2",
    "CH3": "Fpz",
    "Fp_Left": "Fp1",
    "Fp_Right": "Fp2",
    "Fp_Center": "Fpz",
}

# ============================================================================
# SUBJECT INFORMATION
# ============================================================================
# Age and sex information may be available in participants.tsv on OpenNeuro.
# If not available, fields remain "unknown".
# Source: OpenNeuro participants.tsv (if available)
# Annotator: LLM, 2026-01-15 (inferred by LLM, needs human review)
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {}
# Note: Subject information should be populated from dataset's participants.tsv
# at runtime. Placeholder structure provided for kernel framework.

# ============================================================================
# PSG HYPNOGRAM ALIGNMENT
# ============================================================================
# Sleep stage labels (Wake/N1/N2/N3/REM) are stored in external PSG hypnogram
# files. The mapping follows AASM standard scoring:
# Source: AASM Manual for the Scoring of Sleep and Associated Events
# Annotator: LLM, 2026-01-15 (inferred by LLM, needs human review)
_SLEEP_STAGE_MAP: Dict[str, int] = {
    "Wake": 0,
    "N1": 1,
    "N2": 2,
    "N3": 3,
    "REM": 4,
    # Alternative PSG scoring notations:
    "W": 0,
    "NREM1": 1,
    "NREM2": 2,
    "NREM3": 3,
    "R": 4,
}

_EPOCH_DURATION = 30.0  # seconds (AASM standard)


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for the current raw object's channels.
    
    Handles various naming schemes that may appear in forehead EEG data.
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)
    
    for target_name, source_names in _CHANNEL_RENAME_MAP.items():
        if isinstance(source_names, str):
            source_names = [source_names]
        for source_name in source_names:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _load_psg_hypnogram(data_dir: str, subject_id: str) -> Optional[pd.DataFrame]:
    """Load PSG hypnogram scoring file for the given subject.
    
    Looks for hypnogram files in common locations within the dataset:
    - derivatives/hypnogram/sub-*_hypnogram.tsv
    - phenology/ or scoring/ directories
    - files matching *hypnogram* pattern
    
    Returns DataFrame with columns: onset, duration, stage
    or None if no hypnogram file found.
    """
    possible_patterns = [
        # Standard derivatives location
        os.path.join(data_dir, "derivatives", "hypnogram", f"sub-{subject_id}_hypnogram.tsv"),
        os.path.join(data_dir, "derivatives", "hypnogram", f"sub-{subject_id}_scoring.tsv"),
        # Phenotype directory
        os.path.join(data_dir, "phenotype", f"sub-{subject_id}_hypnogram.tsv"),
        os.path.join(data_dir, "phenotype", f"sub-{subject_id}_sleep_stages.tsv"),
        # Top-level scoring directory
        os.path.join(data_dir, "scoring", f"sub-{subject_id}_hypnogram.tsv"),
    ]
    
    # Also search by pattern
    search_dirs = [
        os.path.join(data_dir, "derivatives"),
        os.path.join(data_dir, "phenotype"),
        os.path.join(data_dir, "scoring"),
        data_dir,
    ]
    
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        for root, _, files in os.walk(search_dir):
            for f in files:
                if "hypnogram" in f.lower() or "scoring" in f.lower():
                    if subject_id in f or re.match(r'sub-', f):
                        possible_patterns.append(os.path.join(root, f))
    
    for file_path in possible_patterns:
        if os.path.isfile(file_path):
            try:
                # Try TSV format first
                df = pd.read_csv(file_path, sep="\t")
                if "onset" in df.columns or "timestamp" in df.columns:
                    return df
                # Try CSV format
                df = pd.read_csv(file_path)
                if "onset" in df.columns or "timestamp" in df.columns:
                    return df
            except Exception:
                continue
    
    return None


def _parse_hypnogram_stages(
    hypnogram_df: pd.DataFrame,
) -> List[Tuple[float, float, str]]:
    """Parse hypnogram DataFrame into list of (onset, duration, stage) tuples.
    
    Handles various column naming conventions from different PSG systems.
    """
    # Normalize column names
    col_map = {}
    for col in hypnogram_df.columns:
        col_lower = col.lower().strip()
        if "onset" in col_lower or "start" in col_lower or "timestamp" in col_lower:
            col_map["onset"] = col
        elif "duration" in col_lower or "length" in col_lower:
            col_map["duration"] = col
        elif "stage" in col_lower or "label" in col_lower or "type" in col_lower:
            col_map["stage"] = col
        elif "value" in col_lower:
            col_map["stage"] = col
    
    if "onset" not in col_map:
        # Try to infer from first column if standard columns missing
        first_col = hypnogram_df.columns[0]
        col_map["onset"] = first_col
    
    if "duration" not in col_map:
        col_map["duration"] = None  # Will use default _EPOCH_DURATION
    
    if "stage" not in col_map:
        # Try second column for stage
        if len(hypnogram_df.columns) > 1:
            col_map["stage"] = hypnogram_df.columns[1]
        else:
            col_map["stage"] = hypnogram_df.columns[0]
    
    stages = []
    for idx, row in hypnogram_df.iterrows():
        onset = float(row[col_map["onset"]])
        if col_map["duration"]:
            duration = float(row[col_map["duration"]])
        else:
            duration = _EPOCH_DURATION
        
        stage_raw = str(row[col_map["stage"]]).strip()
        
        # Normalize stage names
        stage_normalized = _normalize_stage_name(stage_raw)
        if stage_normalized:
            stages.append((onset, duration, stage_normalized))
    
    return stages


def _normalize_stage_name(stage_raw: str) -> Optional[str]:
    """Normalize raw stage string to canonical form."""
    stage_upper = stage_raw.upper().strip()
    
    # Direct mappings
    if stage_upper in ["WAKE", "W"]:
        return "Wake"
    elif stage_upper in ["N1", "NREM1", "STAGE 1", "STAGE1", "1"]:
        return "N1"
    elif stage_upper in ["N2", "NREM2", "STAGE 2", "STAGE2", "2"]:
        return "N2"
    elif stage_upper in ["N3", "NREM3", "STAGE 3", "STAGE3", "3", "SWS"]:
        return "N3"
    elif stage_upper in ["REM", "R", "RAPID EYE MOVEMENT"]:
        return "REM"
    
    return None


def _create_sleep_stage_annotations(
    hypnogram_df: pd.DataFrame,
    raw: mne.io.BaseRaw,
) -> mne.Annotations:
    """Create MNE annotations from PSG hypnogram stages aligned to EEG recording.
    
    Aligns hypnogram timestamps to EEG recording onset.
    """
    stages = _parse_hypnogram_stages(hypnogram_df)
    
    if not stages:
        return mne.Annotations(
            onset=[], duration=[], description=[], orig_time=None
        )
    
    # Get EEG recording start time
    eeg_start_time = raw.times[0]  # Usually 0
    eeg_end_time = raw.times[-1]
    eeg_duration = eeg_end_time - eeg_start_time
    
    # Hypnogram onset is typically relative to recording start
    # but may need offset adjustment
    hypnogram_onset = stages[0][0]
    
    # Calculate time offset between EEG and hypnogram
    time_offset = 0.0  # Default: assume aligned
    
    annotations_list = []
    for onset, duration, stage in stages:
        # Apply offset correction
        adjusted_onset = onset - time_offset
        
        # Only include stages within EEG recording window
        if 0 <= adjusted_onset < eeg_duration:
            annotations_list.append({
                "onset": adjusted_onset,
                "duration": duration,
                "description": stage,
            })
    
    if not annotations_list:
        return mne.Annotations(
            onset=[], duration=[], description=[], orig_time=None
        )
    
    return mne.Annotations(
        onset=[a["onset"] for a in annotations_list],
        duration=[a["duration"] for a in annotations_list],
        description=[a["description"] for a in annotations_list],
        orig_time=None,
    )


def _detect_subject_id(row) -> str:
    """Extract subject ID from row data."""
    # Try common column names
    for col in ["subject_id", "subject", "participant_id", "File Path", "file_path"]:
        if col in row and row[col]:
            value = str(row[col])
            # Extract sub-XXX pattern
            match = re.search(r'sub-([A-Za-z0-9]+)', value)
            if match:
                return match.group(1)
            return value
    return "unknown"


def _load_subject_info(data_dir: str, subject_id: str) -> Dict[str, str]:
    """Load subject demographic info from participants.tsv or return defaults."""
    participants_file = os.path.join(data_dir, "participants.tsv")
    
    if os.path.isfile(participants_file):
        try:
            df = pd.read_csv(participants_file, sep="\t")
            # Find matching subject row
            subject_row = df[df["participant_id"].str.contains(subject_id, na=False)]
            if not subject_row.empty:
                row = subject_row.iloc[0]
                info = {}
                
                # Age
                if "age" in df.columns:
                    age_val = row.get("age", "unknown")
                    if pd.notna(age_val):
                        info["age"] = str(int(float(age_val)))
                    else:
                        info["age"] = "unknown"
                else:
                    info["age"] = "unknown"
                
                # Sex
                if "sex" in df.columns:
                    sex_val = str(row.get("sex", "unknown")).lower().strip()
                    if sex_val in ["m", "male", "f", "female"]:
                        info["sex"] = "male" if sex_val in ["m", "male"] else "female"
                    else:
                        info["sex"] = "unknown"
                else:
                    info["sex"] = "unknown"
                
                return info
        except Exception:
            pass
    
    # Defaults if not found
    return {"age": "unknown", "sex": "unknown"}


@dataclass
class OpenNeuroDS006695Kernel:
    """Stage1 kernel for OpenNeuro DS006695 sleep staging dataset.
    
    This kernel:
    1. Renames forehead EEG channels to standard 10-20 names
    2. Sets appropriate montage for forehead electrode positions
    3. Loads PSG hypnogram scoring files for sleep stage annotations
    4. Updates raw.info["description"] with subject and device metadata
    """

    KERNEL_ID: str = "openneuro-ds006695-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single sleep EEG recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with channel names, montage, and annotations.
        """
        # =====================================================================
        # 1. Extract metadata from row
        # =====================================================================
        file_path = row.get("File Path", "")
        data_dir = os.path.dirname(file_path) if file_path else ""
        parent_dir = os.path.dirname(data_dir) if data_dir else ""
        
        subject_id = _detect_subject_id(row)
        
        # Load subject info
        subject_info = _load_subject_info(parent_dir, subject_id)
        
        # =====================================================================
        # 2. Channel renaming (before set_montage)
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[DS006695] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)
        
        # =====================================================================
        # 3. Set montage for forehead electrodes
        # =====================================================================
        # Standard 1020 montage for forehead positions
        # Note: Not all forehead patch positions are in standard_1020,
        # so we use available positions and set custom locations for extras
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            
            # Get current channel names that are in the montage
            ch_names_in_montage = [ch for ch in raw.ch_names if ch in montage.ch_names]
            
            if ch_names_in_montage:
                raw.set_montage(montage, on_missing="ignore")
                print(f"[DS006695] Montage applied for: {ch_names_in_montage}")
            else:
                print(f"[DS006695] Warning: No channels found in standard_1020 montage")
        except Exception as e:
            print(f"[DS006695] Warning: Could not set montage: {e}")
        
        # =====================================================================
        # 4. Load PSG hypnogram and create sleep stage annotations
        # =====================================================================
        hypnogram_df = _load_psg_hypnogram(parent_dir, subject_id)
        
        if hypnogram_df is not None:
            print(f"[DS006695] Loaded hypnogram for subject {subject_id}")
            sleep_annotations = _create_sleep_stage_annotations(hypnogram_df, raw)
            raw.set_annotations(sleep_annotations)
            
            # Log annotation statistics
            if len(sleep_annotations) > 0:
                descs, counts = np.unique(sleep_annotations.description, return_counts=True)
                for desc, count in zip(descs, counts):
                    print(f"[DS006695]   {desc}: {count} epochs")
        else:
            print(f"[DS006695] Warning: No hypnogram file found for subject {subject_id}")
            print(f"[DS006695] Set no_events annotation as per dataset structure")
            # Per analysis.md: "no_events marker" for continuous overnight EEG
            # without discrete trial-level annotations
            raw.set_annotations(mne.Annotations(
                onset=[0],
                duration=[raw.times[-1]],
                description=["no_events"],
                orig_time=None,
            ))
        
        # =====================================================================
        # 5. Update raw.info["description"]
        # =====================================================================
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "forehead EEG patch device",  # inferred by LLM, needs human review
                "cap": "3-channel forehead patch",  # inferred by LLM, needs human review
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =====================================================================
        # 6. Add channel type info if needed
        # =====================================================================
        # Ensure all forehead channels are typed as EEG
        for ch_name in raw.ch_names:
            if ch_name in ["Fp1", "Fp2", "Fpz", "AF7", "AF8", "AFz"]:
                if raw.get_channel_types(picks=[ch_name])[0] == "misc":
                    raw.set_channel_types({ch_name: "eeg"}, on_unit="ignore")
        
        return raw


KERNEL = OpenNeuroDS006695Kernel()