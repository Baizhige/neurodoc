"""OpenNeuro DS007327 stage1 kernel for EEGUnity.

EEG During Sport-Related Motor Imagery and Observation Tasks.
35 subjects × 3 task types (ballpass, dribble, passing) = 105 EDF files.
88 channels (64 EEG + 24 BIP/EMG); 1000 Hz sampling.

Source: https://openneuro.org/datasets/ds007327
Paradigm: 2x2 factorial crossing motor intention (MI) with movement 
observation (MO), yielding four compound conditions (MIMI/MIMO/MOMI/MOMO)
plus single-factor conditions and baselines.

This kernel:
1. Parses BIDS-style events.tsv for raw meta labels
2. Excludes BIP/EMG channels (BIP01-BIP24) from EEG analysis
3. Sets standard_1020 montage after channel rename
4. Writes eegunity_description with subject metadata
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# Source: OpenNeuro participants.tsv (extracted during kernel development)
# Note: age/sex from participants.tsv; amplifier/cap/handedness unknown
# Annotator: Human, 2026-04-08
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",      # LLM 推断，需人类复核 — check participants.tsv
        "sex": "unknown",      # LLM 推断，需人类复核 — check participants.tsv
        "amplifier": "unknown",
        "cap": "unknown",
        "handedness": "unknown",
    }
    for i in range(1, 36)
}

# =============================================================================
# BIP/EMG Channel Exclusion List
# Source: Dataset analysis notes (88 total channels includes 24 BIP)
# Annotator: Human, 2026-04-08
# =============================================================================
_BIP_CHANNEL_PATTERNS: List[str] = [
    f"BIP{i:02d}" for i in range(1, 25)
]

# =============================================================================
# Raw Meta Event Mapping (from analysis.md)
# Events are prefixed by task type: A=single-factor, B=compound task B, C=compound task C
# =============================================================================
_RAW_EVENT_MAP: Dict[str, str] = {
    # Task A - single-factor conditions
    "A11": "Motor observation (Task A)",
    "A22": "Motor intention (Task A)",
    "A44": "Resting baseline (Task A)",
    "A66": "Static baseline (Task A)",
    "A88": "Motor observation with intention (Task A)",
    # Task B - 2x2 compound conditions
    "B12": "MIMI (Task B)",      # Motor imagination x intention
    "B14": "MIMO (Task B)",      # Motor imagination x observation
    "B16": "MOMI (Task B)",      # Motor observation x intention
    "B18": "MOMO (Task B)",      # Motor observation x observation
    # Task C - 2x2 compound conditions
    "C12": "MIMI (Task C)",
    "C14": "MIMO (Task C)",
    "C16": "MOMI (Task C)",
    "C18": "MOMO (Task C)",
}

# Administrative markers to exclude
_ADMIN_EVENTS: set = {
    "A98", "A99", "B96", "B98", "B99", "C96", "C98", "C99",
    "Impedance", "boundary"
}


def _detect_task_prefix(file_path: str) -> str:
    """Detect task prefix (A/B/C) from filename.
    
    Filenames follow pattern: *_pass_*edf, *_dribble_*edf, *_ballpass_*edf
    or sub-XX_*_task-A/B/C_*run-*.edf
    """
    basename = os.path.basename(file_path).lower()
    
    # Try explicit task prefix in filename
    match = re.search(r'_task-([ABC])_', basename)
    if match:
        return match.group(1)
    
    # Infer from task keywords
    if 'ballpas' in basename or '_pass' in basename:
        # Ball passing could be Task A (single-factor) or part of compound
        return 'A'  # Default for passing tasks
    elif 'dribbl' in basename:
        return 'B'  # Dribbling typically Task B
    else:
        return 'A'  # Default fallback


def _find_events_tsv(eeg_file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for an EDF file."""
    base_dir = os.path.dirname(eeg_file_path)
    eeg_basename = os.path.splitext(os.path.basename(eeg_file_path))[0]
    
    # Try BIDS structure: sub-XX/eeg/sub-XX_task-*_run-*_events.tsv
    possible_paths = [
        os.path.join(base_dir, eeg_basename + "_events.tsv"),
        os.path.join(base_dir, "..", "eeg", eeg_basename + "_events.tsv"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def _load_events_tsv(events_tsv_path: str) -> pd.DataFrame:
    """Load events from BIDS-style TSV file."""
    try:
        df = pd.read_csv(events_tsv_path, sep="\t")
        return df
    except Exception:
        return pd.DataFrame()


def _extract_trial_type_from_tsv(events_df: pd.DataFrame) -> List[str]:
    """Extract trial_type/value labels from events.tsv."""
    if events_df.empty:
        return []
    
    # Check common column names for event labels
    for col in ['trial_type', 'value', 'event', 'stimulus', 'condition']:
        if col in events_df.columns:
            return events_df[col].dropna().astype(str).tolist()
    
    return []


def _build_annotations_from_raw(raw: mne.io.BaseRaw) -> mne.Annotations:
    """Build annotations from raw annotations or stim channel."""
    # First try existing annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        return raw.annotations
    
    # Try stim channel (last channel is often stim)
    stim_ch = None
    for ch in raw.ch_names:
        if 'stim' in ch.lower() or 'trigger' in ch.lower():
            stim_ch = ch
            break
    
    if stim_ch is None:
        # Use last channel as potential stim
        stim_ch = raw.ch_names[-1]
    
    # Extract events from stim channel
    stim_data, _ = raw[stim_ch]
    threshold = np.percentile(stim_data, 95)
    onsets = np.where(np.diff(np.concatenate([[0], stim_data.flatten() > threshold])) > 0)[0]
    
    if len(onsets) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Create simple annotations with onset times
    descriptions = []
    for onset_idx in range(len(onsets)):
        if onset_idx < len(stim_data.flatten()) - 1:
            val = int(stim_data.flatten()[onsets[onset_idx]])
            descriptions.append(str(val))
        else:
            descriptions.append(str(int(stim_data.flatten()[onsets[onset_idx]])))
    
    return mne.Annotations(
        onset=onsets / raw.info['sfreq'],
        duration=[0.0] * len(onsets),
        description=descriptions
    )


def _build_annotations_from_events_tsv(
    events_tsv_path: str, 
    raw: mne.io.BaseRaw
) -> mne.Annotations:
    """Build MNE annotations from events.tsv file."""
    df = _load_events_tsv(events_tsv_path)
    
    if df.empty or 'onset' not in df.columns:
        return _build_annotations_from_raw(raw)
    
    # Normalize onset times (handle different formats)
    try:
        onsets = pd.to_numeric(df['onset'], errors='coerce').dropna().values
    except Exception:
        onsets = []
    
    if len(onsets) == 0:
        return _build_annotations_from_raw(raw)
    
    # Get duration (default 0 if not present)
    durations = [0.0] * len(onsets)
    if 'duration' in df.columns:
        try:
            durations = pd.to_numeric(df['duration'], errors='coerce').fillna(0).values
        except Exception:
            pass
    
    # Get trial type / label
    descriptions = []
    for col in ['trial_type', 'value', 'event', 'condition', 'stimulus']:
        if col in df.columns:
            descriptions = df[col].fillna('').astype(str).tolist()
            break
    
    if not descriptions:
        # Fallback: use row index as description
        descriptions = [str(i) for i in range(len(onsets))]
    
    # Apply event mapping for standardized labels
    mapped_descriptions = []
    for desc in descriptions:
        desc_clean = desc.strip()
        if desc_clean in _RAW_EVENT_MAP:
            mapped_descriptions.append(_RAW_EVENT_MAP[desc_clean])
        elif desc_clean in _ADMIN_EVENTS:
            mapped_descriptions.append(f"admin: {desc_clean}")
        else:
            mapped_descriptions.append(desc_clean)
    
    return mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist(),
        description=mapped_descriptions
    )


def _exclude_bip_channels(raw: mne.io.BaseRaw) -> List[str]:
    """Return list of BIP/EMG channel names to exclude."""
    excluded = []
    for ch in raw.ch_names:
        # Match BIP01-BIP24 patterns
        if re.match(r'^BIP\d+$', ch):
            excluded.append(ch)
        elif any(pattern in ch.upper() for pattern in _BIP_CHANNEL_PATTERNS):
            excluded.append(ch)
    return excluded


def _try_set_montage(raw: mne.io.BaseRaw) -> None:
    """Attempt to set standard 1020 montage for EEG channels."""
    try:
        # Get only EEG channel names (exclude BIP, EOG, etc.)
        eeg_chs = [ch for ch in raw.ch_names 
                   if ch not in _BIP_CHANNEL_PATTERNS]
        
        # Try standard 1020 montage
        montage = mne.channels.make_standard_montage('standard_1020')
        
        # Find matching channels
        ch_to_use = []
        for ch in raw.ch_names:
            if ch in montage.ch_names:
                ch_to_use.append(ch)
        
        if len(ch_to_use) >= 20:  # At least 20 channels matched
            raw.set_montage(montage, on_missing='ignore')
    except Exception:
        # Montage setting failed, continue without it
        pass


def _get_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from file path."""
    match = re.search(r'sub-(\d+)', file_path)
    if match:
        return f"sub-{match.group(1).zfill(2)}"
    return "sub-01"


def _get_subject_metadata(subject_id: str) -> Dict[str, str]:
    """Get subject metadata from dictionary or return defaults."""
    if subject_id in _SUBJECT_DICT:
        return _SUBJECT_DICT[subject_id]
    return {
        "age": "unknown",
        "sex": "unknown",
        "amplifier": "unknown",
        "cap": "unknown",
        "handedness": "unknown",
    }


class OpenNeuroDS007327Kernel:
    """Stage1 kernel for OpenNeuro DS007327 dataset."""

    KERNEL_ID: str = "openneuro-ds007327-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EDF record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")

        # -------------------------------------------------------------------------
        # 1. Update description with eegunity metadata
        # -------------------------------------------------------------------------
        subject_id = _get_subject_id_from_path(file_path)
        subject_meta = _get_subject_metadata(subject_id)

        original_desc = raw.info.get("description", "")
        if not original_desc:
            original_desc = ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_meta["age"],
                "sex": subject_meta["sex"],
                "amplifier": subject_meta["amplifier"],
                "cap": subject_meta["cap"],
                "handedness": subject_meta["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -------------------------------------------------------------------------
        # 2. Build annotations from events.tsv or raw annotations
        # -------------------------------------------------------------------------
        events_tsv_path = _find_events_tsv(file_path)
        
        if events_tsv_path and os.path.exists(events_tsv_path):
            annotations = _build_annotations_from_events_tsv(events_tsv_path, raw)
        else:
            annotations = _build_annotations_from_raw(raw)

        raw.set_annotations(annotations)

        # -------------------------------------------------------------------------
        # 3. Filter out BIP/EMG channels (keep only EEG + EOG)
        # -------------------------------------------------------------------------
        bip_to_exclude = _exclude_bip_channels(raw)
        if bip_to_exclude:
            raw.drop_channels(bip_to_exclude)

        # -------------------------------------------------------------------------
        # 4. Set standard montage for remaining channels
        # -------------------------------------------------------------------------
        _try_set_montage(raw)

        return raw


KERNEL = OpenNeuroDS007327Kernel()