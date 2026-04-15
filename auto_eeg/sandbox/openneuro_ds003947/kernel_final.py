"""openneuro_ds003947 stage1 kernel for EEGUnity.

Dataset: First Episode Psychosis vs. Control Resting-State EEG
Source: https://openneuro.org/datasets/ds003947

This kernel handles a BIDS-format resting-state EEG dataset with:
- 61 subjects, 64 channels, 3000 Hz sampling rate
- 5-minute recording per subject
- Diagnosis labels from participants.tsv (clinical_status column)

Annotations:
- Raw data contains only "unknown" admin markers (excluded from analysis)
- Segmentation and label assignment handled at epoching stage

Reference: DOI 10.48550/arxiv.2411.18392
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Subject metadata sourced from participants.tsv
# Source: openneuro_ds003947/participants.tsv (columns: participant_id, age, sex, clinical_status, etc.)
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# ============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Ages and sex will be loaded dynamically from participants.tsv
    # Hardcoding is not applicable as values vary per subject
}


def _load_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv from BIDS dataset root."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_metadata(row: pd.Series, dataset_path: str) -> Dict[str, str]:
    """Extract subject metadata from row or participants.tsv."""
    subject_id = row.get("participant_id", row.get("subject_id", "unknown"))
    
    # Try to load from participants.tsv
    participants_df = _load_participants_tsv(dataset_path)
    
    subject_info = {
        "age": "unknown",
        "sex": "unknown",
        "clinical_status": "unknown",
    }
    
    if not participants_df.empty:
        subject_row = participants_df[
            participants_df.get("participant_id", pd.Series()) == subject_id
        ]
        if subject_row.empty:
            subject_row = participants_df[
                participants_df.get("subject_id", pd.Series()) == subject_id
            ]
        
        if not subject_row.empty:
            first_row = subject_row.iloc[0]
            # Extract age
            if "age" in first_row.index:
                age_val = first_row["age"]
                if pd.notna(age_val):
                    subject_info["age"] = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)
            
            # Extract sex
            for sex_col in ["sex", "gender"]:
                if sex_col in first_row.index:
                    sex_val = first_row[sex_col]
                    if pd.notna(sex_val):
                        sex_lower = str(sex_val).lower().strip()
                        if sex_lower in ["m", "male", "f", "female"]:
                            subject_info["sex"] = "male" if sex_lower in ["m", "male"] else "female"
                        break
            
            # Extract clinical status (diagnosis)
            for status_col in ["clinical_status", "group", "diagnosis", "diagnosis_group"]:
                if status_col in first_row.index:
                    status_val = first_row[status_col]
                    if pd.notna(status_val):
                        subject_info["clinical_status"] = str(status_val).lower().strip()
                        break
    
    return subject_info


def _map_clinical_status_to_y(clinical_status: str) -> Optional[int]:
    """Map clinical status to classification label."""
    status_lower = clinical_status.lower().strip()
    
    if status_lower in ["control", "healthy", "hc", "ctrl"]:
        return 0
    elif status_lower in ["first_episode_psychosis", "fep", "patient", "case", "psychosis"]:
        return 1
    
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20 names.
    
    This dataset uses standard electrode naming (EEG- followed by standard 10-20 names)
    but MNE may not auto-detect them. We map EEG-prefixed names to standard names.
    
    Source: OpenNeuro ds003947 channel layout documentation
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    # Standard 10-20 channels used in this dataset
    standard_channels = [
        "Fp1", "Fpz", "Fp2",
        "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "FC1", "FC2", "CP1", "CP2",
        "FC5", "FC6", "CP5", "CP6",
        "FT9", "FT10",
    ]
    
    for std_ch in standard_channels:
        # Check for EEG- prefix variations
        for prefix in ["EEG-", "EEG ", "eeg"]:
            prefixed = f"{prefix}{std_ch}"
            if prefixed in existing_names:
                rename_map[prefixed] = std_ch
                break
    
    return rename_map


class openneuro_ds003947_Kernel:
    """Stage1 kernel for openneuro_ds003947 dataset.
    
    Applies:
    - Channel name standardization
    - Montage setting (standard_1020)
    - Resampling from 3000 Hz to 250 Hz
    - eegunity_description metadata population
    - Raw annotations (only 'unknown' admin markers)
    """
    
    KERNEL_ID: str = "openneuro-ds003947-stage1"
    HANDLES_UNAVAILABLE: bool = False
    
    TARGET_SFREQ: float = 250.0  # Target sampling rate for analysis
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object
        row : pandas.Series
            Locator row with at least 'File Path' and subject identifiers
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object
        """
        # Get dataset path for participants.tsv access
        dataset_path = getattr(udataset, "base_path", os.path.dirname(row.get("File Path", "")))
        
        # =====================================================================
        # Step 1: Get subject metadata from participants.tsv
        # =====================================================================
        subject_info = _get_subject_metadata(row, dataset_path)
        
        # =====================================================================
        # Step 2: Rename channels to standard 10-20 names
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Only rename EEG-type channels
            eeg_channels = [ch for ch in raw.ch_names if ch.startswith("EEG")]
            mne.rename_channels(raw, rename_map)
        
        # =====================================================================
        # Step 3: Set montage (standard 1020)
        # =====================================================================
        # Check if channels are now standard names
        standard_chs = [ch for ch in raw.ch_names if ch in mne.channels.get_montage_units("standard_1020")]
        if len(standard_chs) >= 60:  # Most channels are standard
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage setting is best-effort
        
        # =====================================================================
        # Step 4: Resample to target frequency
        # =====================================================================
        original_sfreq = raw.info["sfreq"]
        if original_sfreq > self.TARGET_SFREQ * 1.1:  # Only resample if significantly higher
            # Low-pass filter at Nyquist of target (125 Hz) to prevent aliasing
            cutoff = self.TARGET_SFREQ * 0.45  # 112.5 Hz cutoff
            raw.filter(l_freq=None, h_freq=cutoff, fir_design="firwin", verbose=False)
            raw.resample(self.TARGET_SFREQ, verbose=False)
        
        # =====================================================================
        # Step 5: Update info description with metadata
        # =====================================================================
        # Get clinical status for super meta (stored but not used in raw annotations)
        clinical_status = subject_info.get("clinical_status", "unknown")
        y_label = _map_clinical_status_to_y(clinical_status)
        
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "unknown",  # Not specified in available documentation
                "cap": "unknown",       # Not specified in available documentation
                "handedness": "unknown",  # Not in participants.tsv
            },
            # Super meta fields (available for epoching stage)
            "clinical_status": clinical_status,
            "y_label": y_label,  # None if unknown, 0/1 if determinable
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =====================================================================
        # Step 6: Annotations from raw data
        # =====================================================================
        # Raw data has only 'unknown' admin markers - these are not meaningful
        # for analysis and should be excluded
        existing_annotations = raw.annotations
        if existing_annotations:
            # Keep only meaningful annotations (exclude 'unknown' admin markers)
            meaningful_mask = [
                desc.lower() != "unknown" 
                for desc in existing_annotations.description
            ]
            if any(meaningful_mask):
                meaningful_onsets = existing_annotations.onset[meaningful_mask]
                meaningful_durations = existing_annotations.duration[meaningful_mask]
                meaningful_descriptions = [
                    desc for desc, m in zip(existing_annotations.description, meaningful_mask) 
                    if m
                ]
                raw.set_annotations(mne.Annotations(
                    onset=meaningful_onsets,
                    duration=meaningful_durations,
                    description=meaningful_descriptions,
                ))
            else:
                # No meaningful annotations - clear them
                raw.set_annotations(mne.Annotations(
                    onset=np.array([]),
                    duration=np.array([]),
                    description=[],
                ))
        
        return raw


KERNEL = openneuro_ds003947_Kernel()