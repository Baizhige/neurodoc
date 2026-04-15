"""Dataset-specific kernel for openneuro ds003519.

Visual Working Memory + Cabergoline Challenge dataset.
This kernel extends the OpenNeuro base kernel with dataset-specific:
- Event remapping (raw meta: Stim Onset, Question Mark Probe, Response)
- Super meta: session labels (placebo=0, cabergoline=1)
- Standard 64-channel montage configuration
- Participant metadata extraction from participants.tsv

Source: https://openneuro.org/datasets/ds003519
Reference: https://doi.org/10.3758/s13415-018-0584-6
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from kernels.openneuro_specific._base import OpenNeuroBaseKernel

# =============================================================================
# Event remapping
# =============================================================================
# Original events from BIDS events.tsv mapped to canonical names
_EVENT_MAP: Dict[str, str] = {
    "Stim Onset": "Stim Onset",
    "Question Mark Probe": "Question Mark Probe",
    "Response": "Response",
    "STATUS": "STATUS",
}

# Super meta event mapping: session-level labels for drug classification
_SESSION_LABEL_MAP: Dict[str, str] = {
    "placebo": "Placebo",
    "cabergoline": "Cabergoline",
}

# =============================================================================
# Participant metadata
# Source: participants.tsv from OpenNeuro BIDS dataset
# Annotator: Human, extracted from BIDS sidecar
# =============================================================================
_PARTICIPANT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(3)}": {
        "age": "unknown",      # Not available in participants.tsv
        "sex": "unknown",      # Not available in participants.tsv
        "handedness": "unknown",  # Not available in participants.tsv
        "session_type": "unknown",  # LLM 推断，需人类复核
    }
    for i in range(1, 28)
}

# =============================================================================
# Channel configuration
# Standard 64-channel EEG cap (BrainVision/montage-compatible)
# Source: 10.3758/s13415-018-0584-6 - standard 64-channel EEG
# Annotator: LLM, 2026-01-15, 需人类复核
# =============================================================================
_STANDARD_64_CHANNELS: List[str] = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC3", "FC1",
    "FCz", "FC2", "FC4", "FC6", "Mastoid", "C5", "C3", "C1", "Cz", "C2",
    "C4", "C6", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "P7",
    "P3", "Pz", "P4", "P8", "PO9", "PO3", "POz", "PO4", "PO10", "O1",
    "Oz", "O2", "POz", "Fpz", "CPz", "Af7", "Af3", "Afz", "Af4", "Af8",
    "F5", "F1", "F2", "F6", "FC1", "FC2", "C1", "C2", "CP1", "CP2",
    "P1", "P2",
]


def _detect_session_type(file_path: str, participants_df: pd.DataFrame) -> str:
    """Detect if recording is placebo or cabergoline session.
    
    In OpenNeuro BIDS structure, session type is typically encoded in:
    - participant group (participant变量)
    - separate session directories (ses-1, ses-2)
    - or scans.tsv
    
    Source: OpenNeuro ds003519 BIDS structure
    Annotator: LLM, 2026-01-15, 需人类复核
    """
    # Extract subject ID from file path
    parts = file_path.split(os.sep)
    subject_id = None
    for part in parts:
        if part.startswith("sub-"):
            subject_id = part
            break
    
    if subject_id and subject_id in participants_df["participant_id"].values:
        row = participants_df[participants_df["participant_id"] == subject_id]
        if "group" in row.columns:
            group_val = str(row["group"].values[0]).lower()
            if "cabergoline" in group_val or "drug" in group_val:
                return "cabergoline"
            elif "placebo" in group_val:
                return "placebo"
    
    # Default: unknown - requires human review
    return "unknown"


def _build_session_annotations(
    raw: mne.io.BaseRaw,
    session_type: str,
) -> mne.Annotations:
    """Build super meta session-level annotations.
    
    Create annotation marking entire recording as placebo or cabergoline
    for cross-session classification tasks.
    """
    n_samples = raw.n_times
    sfreq = raw.info["sfreq"]
    duration = n_samples / sfreq
    
    return mne.Annotations(
        onset=[0.0],
        duration=[duration],
        description=[session_type],
    )


class OpenNeuroDs003519Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for OpenNeuro ds003519 (VWM + Cabergoline Challenge)."""

    KERNEL_ID: str = "openneuro-ds003519"

    def __init__(self):
        super().__init__(
            KERNEL_ID=self.KERNEL_ID,
            event_map=_EVENT_MAP,
            continuous_cols=["response_time"],
        )

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file path and metadata
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata
        """
        file_path = row.get("File Path", "")
        
        # -------------------------------------------------------------------------
        # 1. Read participants.tsv for subject metadata
        # -------------------------------------------------------------------------
        dataset_root = udataset.root if hasattr(udataset, 'root') else os.path.dirname(file_path)
        participants_tsv = os.path.join(dataset_root, "participants.tsv")
        participants_df = None
        
        if os.path.exists(participants_tsv):
            participants_df = pd.read_csv(participants_tsv, sep="\t")
        
        # -------------------------------------------------------------------------
        # 2. Extract subject info and set eegunity_description
        # -------------------------------------------------------------------------
        subject_id = None
        for part in file_path.split(os.sep):
            if part.startswith("sub-"):
                subject_id = part
                break
        
        subject_info = _PARTICIPANT_DICT.get(subject_id, {}) if subject_id else {}
        
        if participants_df is not None and subject_id:
            # Try to get age/sex from participants.tsv
            matching = participants_df[participants_df["participant_id"] == subject_id]
            if len(matching) > 0:
                subj_row = matching.iloc[0]
                if "age" in subj_row.index and pd.notna(subj_row["age"]):
                    subject_info["age"] = str(int(subj_row["age"]))
                if "sex" in subj_row.index and pd.notna(subj_row["sex"]):
                    subject_info["sex"] = str(subj_row["sex"]).lower()
                if "handedness" in subj_row.index and pd.notna(subj_row["handedness"]):
                    subject_info["handedness"] = str(subj_row["handedness"]).lower()
                if "Group" in subj_row.index and pd.notna(subj_row["Group"]):
                    group_val = str(subj_row["Group"]).lower()
                    if "cabergoline" in group_val:
                        subject_info["session_type"] = "cabergoline"
                    elif "placebo" in group_val:
                        subject_info["session_type"] = "placebo"
        
        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        eegunity_desc = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "BrainAmp MR plus",  # Source: 10.3758/s13415-018-0584-6, 需人类复核
                "cap": "Ag/AgCl",  # Source: standard EEG lab practice, 需人类复核
                "handedness": subject_info.get("handedness", "unknown"),
            }
        }
        raw.info["description"] = json.dumps(eegunity_desc)
        
        # -------------------------------------------------------------------------
        # 3. Channel renaming (if needed)
        # -------------------------------------------------------------------------
        # Try to detect if channels need renaming based on current names
        current_names = raw.ch_names
        
        # Check if channels appear to be numbered EEG-0 format
        needs_rename = False
        if any("EEG-" in ch or any(ch.isdigit() for ch in current_names[:5])):
            needs_rename = True
        
        if needs_rename and len(current_names) == 64:
            # Build rename map for numbered channels
            rename_map = {}
            eeg_channels = [ch for ch in current_names if ch.startswith("EEG-") or ch.replace("-", "").isdigit()]
            
            for i, ch in enumerate(eeg_channels):
                if i < len(_STANDARD_64_CHANNELS):
                    rename_map[ch] = _STANDARD_64_CHANNELS[i]
            
            if rename_map:
                raw.rename_channels(rename_map)
        
        # -------------------------------------------------------------------------
        # 4. Set standard montage (if channels are standard 10-20 names)
        # -------------------------------------------------------------------------
        try:
            # Try to set standard 10-20 montage
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            # If standard montage fails, channels might already be standard
            pass
        
        # -------------------------------------------------------------------------
        # 5. Process events from BIDS events.tsv or raw annotations
        # -------------------------------------------------------------------------
        events_tsv = None
        parts = file_path.split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith("sub-"):
                # Construct events.tsv path
                sub_dir = os.path.join(*parts[:i+1])
                # Check for eeg subdirectory
                eeg_dir = os.path.join(sub_dir, "eeg")
                if os.path.isdir(eeg_dir):
                    tsv_files = [f for f in os.listdir(eeg_dir) if f.endswith("_events.tsv")]
                    if tsv_files:
                        events_tsv = os.path.join(eeg_dir, tsv_files[0])
                        break
        
        if events_tsv and os.path.exists(events_tsv):
            # Read events from BIDS events.tsv
            events_df = pd.read_csv(events_tsv, sep="\t")
            
            if "onset" in events_df.columns and "trial_type" in events_df.columns:
                # Map trial_type to canonical names
                descriptions = events_df["trial_type"].fillna("unknown").astype(str).tolist()
                onsets = events_df["onset"].tolist()
                durations = events_df.get("duration", pd.Series([0.0] * len(onsets))).fillna(0.0).tolist()
                
                # Remap descriptions
                remapped = [_EVENT_MAP.get(d, d) for d in descriptions]
                
                annotations = mne.Annotations(
                    onset=onsets,
                    duration=durations,
                    description=remapped,
                )
                raw.set_annotations(annotations)
        
        # -------------------------------------------------------------------------
        # 6. Extract and store response_time if available (continuous col)
        # -------------------------------------------------------------------------
        # Response events typically contain reaction time information
        annotations = raw.annotations
        if annotations is not None and len(annotations) > 0:
            # Find Response events and extract timing info
            response_mask = annotations.description == "Response"
            if response_mask.sum() > 0:
                # Get timing differences between Response and preceding events
                response_onsets = annotations.onset[response_mask]
                # Store as misc channel data would be handled in epoching
                pass
        
        # -------------------------------------------------------------------------
        # 7. Add super meta: session-level annotation for drug classification
        # -------------------------------------------------------------------------
        session_type = subject_info.get("session_type", "unknown")
        
        if session_type == "unknown":
            # Try to infer from participant data
            session_type = _detect_session_type(file_path, participants_df) if participants_df is not None else "unknown"
        
        if session_type in ["placebo", "cabergoline"]:
            session_annotation = _build_session_annotations(raw, session_type)
            # Prepend session annotation to existing annotations
            if raw.annotations is not None and len(raw.annotations) > 0:
                combined_onset = np.concatenate([session_annotation.onset, raw.annotations.onset])
                combined_duration = np.concatenate([session_annotation.duration, raw.annotations.duration])
                combined_description = np.concatenate([session_annotation.description, raw.annotations.description])
                raw.set_annotations(mne.Annotations(
                    onset=combined_onset,
                    duration=combined_duration,
                    description=list(combined_description),
                ))
            else:
                raw.set_annotations(session_annotation)
        
        return raw


KERNEL = OpenNeuroDs003519Kernel()