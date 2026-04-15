"""OpenNeuro ds004284 (EEG Neuroforecasting) stage1 kernel for EEGUnity.

Dataset: eeg-neuroforecasting
Source: https://openneuro.org/datasets/ds004284
DOI: https://doi.org/10.18112/openneuro.ds004284.v1.0.0

This kernel handles the EEG neuroforecasting dataset with Kickstarter
decision-making paradigm. The dataset contains 129-channel EEG recordings
with no discrete event markers in the raw data; segmentation is based on
external Kickstarter metadata and valuation periods.

Primary Tasks:
- Kickstarter Outcome Prediction (classification)
- Individual Funding Decision Prediction (classification)
- Population-Level Outcome Regression (super-meta regression)

Channel Configuration:
- 129 EEG channels (high-density system, likely EGI Hydrocel or BioSemi)
- Sampling rate: 1000 Hz
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


# =============================================================================
# Subject Metadata
# =============================================================================

# Source: Dataset participants.tsv (BIDS)
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# Channel Configuration
# =============================================================================

# 129-channel high-density EEG systems (EGI Hydrocel 128 + 1 reference or similar)
# Source: Dataset README and paper DOI: 10.1038/s41598-023-41613-4
# Annotator: LLM, 2026-04-08
_EEG_CHANNEL_COUNT = 129

# Standard 10-5 system montage for 128+ channel caps
# Most OpenNeuro EEG datasets with 129 channels use EGI Hydrocel GSN
# Source: Veillette GitHub repository eeg-neuroforecasting
# Annotator: LLM, 2026-04-08
_CAP_TYPE = "EGI Hydrocel GSN 128"  # LLM 推断，需人类复核


# =============================================================================
# Helper Functions
# =============================================================================

def _detect_subject_id(row) -> str:
    """Extract subject ID from file path or row data."""
    file_path = row.get("File Path", "")
    # Try to extract from BIDS structure: sub-XX
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return f"sub-{match.group(1)}"
    return "unknown"


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv if it exists."""
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return pd.DataFrame()


def _get_subject_info(subject_id: str, dataset_root: str) -> Dict[str, str]:
    """Get subject metadata from participants.tsv or defaults."""
    if subject_id in _SUBJECT_DICT:
        info = _SUBJECT_DICT[subject_id]
        return {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "handedness": info.get("handedness", "unknown"),
        }
    
    # Try to load from participants.tsv
    df = _load_participants_tsv(dataset_root)
    if not df.empty and "participant_id" in df.columns:
        # Normalize participant_id (sub-01 -> sub-01 or 01)
        df["participant_id_norm"] = df["participant_id"].str.replace("sub-", "", regex=False)
        subject_num = subject_id.replace("sub-", "")
        matching = df[df["participant_id_norm"] == subject_num]
        if not matching.empty:
            row = matching.iloc[0]
            return {
                "age": str(row.get("age", "unknown")),
                "sex": str(row.get("sex", "unknown")).lower(),
                "handedness": str(row.get("handedness", "unknown")).lower(),
            }
    
    # Defaults - LLM推断，需人类复核
    return {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }


def _detect_kickstarter_outcome(file_path: str) -> Optional[int]:
    """Detect Kickstarter funding outcome from file path or metadata.
    
    Returns:
        1 if project was funded, 0 if not funded, None if unknown
    """
    # Source: Veillette eeg-neuroforecasting repository
    # Projects are named with funding outcome or this can be derived from external JSON
    # LLM 推断，需人类复核
    file_name = os.path.basename(file_path).lower()
    
    # Heuristic: check if path contains funding outcome indicators
    if "funded" in file_name:
        return 1
    elif "notfunded" in file_name or "not_funded" in file_name:
        return 0
    
    return None


def _build_segmentation_annotations(
    raw: mne.io.BaseRaw,
    segment_length: float = 2.0,
    overlap: Optional[float] = None,
) -> mne.Annotations:
    """Build segment annotations for Kickstarter prediction tasks.
    
    For the classification task, segments are created from continuous EEG
    during valuation periods. The actual label (funded/not_funded) should
    come from external Kickstarter metadata.
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object
    segment_length : float
        Length of each segment in seconds
    overlap : float, optional
        Overlap between segments in seconds
        
    Returns
    -------
    mne.Annotations
        Annotations with 'segment' description
    """
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    total_duration = n_samples / sfreq
    
    onsets = []
    durations = []
    descriptions = []
    
    # Sliding window segmentation
    step = segment_length
    if overlap is not None:
        step = segment_length - overlap
    
    current_onset = 0.0
    while current_onset + segment_length <= total_duration:
        onsets.append(current_onset)
        durations.append(segment_length)
        descriptions.append("segment")
        current_onset += step
    
    return mne.Annotations(
        onset=np.array(onsets),
        duration=np.array(durations),
        description=np.array(descriptions),
    )


def _infer_amplifier_from_metadata(raw: mne.io.BaseRaw) -> str:
    """Try to infer amplifier from raw info or metadata.
    
    Source: Dataset documentation or raw.info
    LLM 推断，需人类复核
    """
    # Check raw info for amplifier hints
    if "device_info" in raw.info:
        return raw.info["device_info"].get("type", "unknown")
    
    # Common EEG amplifiers in OpenNeuro datasets
    # LLM 推断，需人类复核
    return "unknown"


# =============================================================================
# Main Kernel Class
# =============================================================================

@dataclass
class EEGNeuroforecastingKernel:
    """Stage1 kernel for OpenNeuro ds004284 (EEG Neuroforecasting).
    
    This kernel processes EEG recordings during Kickstarter decision-making
    tasks. Since no discrete event markers are present in the raw data,
    segmentation is based on continuous EEG periods that can be further
    labeled using external Kickstarter metadata.
    
    Supported Tasks:
    - Kickstarter Outcome Prediction (Classification)
    - Individual Funding Decision Prediction (Classification)
    - Population-Level Outcome Regression (Super-meta)
    """

    KERNEL_ID: str = "openneuro-ds004284-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed MNE Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        dataset_root = row.get("Dataset Root", "")
        subject_id = _detect_subject_id(row)

        # -------------------------------------------------------------------------
        # 1. Channel Name Standardization
        # -------------------------------------------------------------------------
        raw = self._standardize_channels(raw)

        # -------------------------------------------------------------------------
        # 2. Set Montage (must be after channel rename)
        # -------------------------------------------------------------------------
        raw = self._set_montage(raw)

        # -------------------------------------------------------------------------
        # 3. Build Annotations for Segmentation Tasks
        # -------------------------------------------------------------------------
        raw = self._add_segmentation_annotations(raw)

        # -------------------------------------------------------------------------
        # 4. Subject Metadata
        # -------------------------------------------------------------------------
        subject_info = _get_subject_info(subject_id, dataset_root)
        amplifier = _infer_amplifier_from_metadata(raw)

        # -------------------------------------------------------------------------
        # 5. Write eegunity_description
        # -------------------------------------------------------------------------
        original_description = raw.info.get("description", "") or ""
        if isinstance(original_description, dict):
            original_description = json.dumps(original_description)

        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": amplifier,
                "cap": _CAP_TYPE,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw

    def _standardize_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Standardize channel names for the 129-channel system.
        
        The dataset uses EGI Hydrocel GSN channel naming conventions.
        Standardize to common format before setting montage.
        
        Source: EGI Hydrocel GSN channel naming
        """
        ch_names = raw.ch_names
        new_names = []
        
        for i, name in enumerate(ch_names):
            name_upper = name.upper().strip()
            
            # EGI standard naming: E1, E2, ..., E128, or with GSN prefix
            if name_upper.startswith("E") and name_upper[1:].isdigit():
                # E1, E2, ... E128 -> EEG001, EEG002, ...
                egi_num = int(name_upper[1:])
                if 1 <= egi_num <= 256:
                    new_names.append(f"EEG{egi_num:03d}")
                    continue
            
            # Already standardized or other channel types
            if name_upper.startswith("EEG") or name_upper.startswith("VEO"):
                new_names.append(name)
            else:
                # Keep original but capitalize properly
                new_names.append(name)
        
        # Apply renames only if different
        rename_map = {
            old: new for old, new in zip(ch_names, new_names)
            if old != new
        }
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard montage for the high-density EEG cap.
        
        Source: EGI Hydrocel GSN 128 standard 10-5 system positions
        Annotator: LLM, 2026-04-08
        """
        try:
            # Try EGI Hydrocel GSN 128 montage (standard 10-5 system)
            montage = mne.channels.make_standard_montage("GSN-Hydrocel-128")
            raw = raw.set_montage(montage, on_missing="warn")
        except Exception:
            # Fallback: try standard 10-5 system
            try:
                montage = mne.channels.make_standard_montage("standard_alphabetic")
                raw = raw.set_montage(montage, on_missing="warn")
            except Exception:
                # If montage setting fails, continue without it
                pass
        
        return raw

    def _add_segmentation_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Add segmentation annotations for classification/regression tasks.
        
        Creates 'segment' annotations for sliding window segmentation.
        The actual outcome labels (funded/not_funded) should be derived
        from external Kickstarter metadata in downstream processing.
        """
        # Default segmentation: 2-second windows (matching Kickstarter task)
        annotations = _build_segmentation_annotations(
            raw,
            segment_length=2.0,
            overlap=None,
        )
        raw = raw.set_annotations(annotations)
        return raw


# =============================================================================
# Kernel Instance
# =============================================================================

KERNEL = EEGNeuroforecastingKernel()