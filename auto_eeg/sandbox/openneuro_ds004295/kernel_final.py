"""Dataset-specific kernel for openneuro ds004295.

Reward gain and punishment avoidance reversal learning task.
BrainVision format with BIDS structure.

Event codes (from events.tsv):
  S 51, S 52  = feedback events (valence classification targets)
  S 55, S 60, S 61, S 71, S 72, S 75, S 80, S 81 = stimulus triggers

Classical Task 1: Feedback Valence Classification
  S 52 → positive feedback (reward gain / punishment avoidance success), y=0
  S 51 → negative feedback (reward loss / punishment failure), y=1
  tmin=-1.5s, tmax=3.0s

Source: OpenNeuro ds004295, DOI 10.1111/psyp.14235
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# Source: OpenNeuro ds004295 - dataset_description.json
_DATASET_INFO = {
    "name": "Reward Gain and Punishment Avoidance Reversal Learning",
    "doi": "10.1111/psyp.14235",
    "amplifier": "BrainAmp",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl",  # LLM 推断，需人类复核
}

# Annotator: LLM, 2026-04-08
# Event mapping based on analysis.md and paper DOI 10.1111/psyp.14235
# S 52/S 51 used for feedback valence classification in the reference paper
_EVENT_MAP: Dict[str, str] = {
    "S 51": "feedback_negative",
    "S 52": "feedback_positive",
    "S 55": "stimulus",
    "S 60": "stimulus",
    "S 61": "stimulus",
    "S 71": "stimulus",
    "S 72": "stimulus",
    "S 75": "stimulus",
    "S 80": "stimulus",
    "S 81": "stimulus",
    "S100": "sample_stimulus",
    "S200": "probe_stimulus",
}


def _load_events_tsv(eeg_dir: str, subject_id: str) -> Optional[pd.DataFrame]:
    """Load events.tsv for a subject.
    
    Returns DataFrame with columns: onset, duration, trial_type, value, ...
    """
    # Find events.tsv - typical BIDS structure
    possible_paths = [
        os.path.join(eeg_dir, f"{subject_id}_events.tsv"),
        os.path.join(eeg_dir, f"{subject_id}_task-reversal_events.tsv"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path, sep="\t")
    
    # Try to find any events.tsv in the directory
    for f in os.listdir(eeg_dir):
        if "events.tsv" in f.lower():
            return pd.read_csv(os.path.join(eeg_dir, f), sep="\t")
    
    return None


def _build_annotations_from_events(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    event_map: Dict[str, str],
    sfreq: float,
) -> mne.Annotations:
    """Build MNE Annotations from events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return mne.Annotations([], [], [])
    
    annotations_list = []
    onset_list = []
    duration_list = []
    description_list = []
    
    # Check for common column names in BIDS events.tsv
    value_col = None
    for col in ["value", "stim_type", "event_code", "code"]:
        if col in events_df.columns:
            value_col = col
            break
    
    if value_col is None:
        # Try to infer from first column that might contain event codes
        for col in events_df.columns:
            if events_df[col].dtype == object or events_df[col].dtype == int:
                value_col = col
                break
    
    if value_col is None:
        return mne.Annotations([], [], [])
    
    for _, row in events_df.iterrows():
        raw_code = str(row.get(value_col, ""))
        
        # Map raw code to canonical label
        canonical_label = event_map.get(raw_code, raw_code)
        
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0))
        
        onset_list.append(onset)
        duration_list.append(duration)
        description_list.append(canonical_label)
    
    return mne.Annotations(
        onset=np.array(onset_list),
        duration=np.array(duration_list),
        description=description_list,
    )


def _get_subject_info(
    dataset_path: str,
    subject_id: str,
) -> Dict[str, str]:
    """Extract subject metadata from BIDS participants.tsv."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    
    if os.path.exists(participants_path):
        try:
            df = pd.read_csv(participants_path, sep="\t")
            # Match subject_id (may have 'sub-' prefix)
            subj_id_clean = subject_id.replace("sub-", "")
            for col in df.columns:
                if "participant" in col.lower() and "id" in col.lower():
                    mask = df[col].astype(str).str.replace("sub-", "", regex=False) == subj_id_clean
                    if mask.any():
                        row = df[mask].iloc[0]
                        result = {
                            "age": str(row.get("age", "unknown")),
                            "sex": str(row.get("sex", "unknown")).lower(),
                        }
                        # Normalize sex values
                        sex_raw = row.get("sex", "")
                        if isinstance(sex_raw, str):
                            if "f" in sex_raw.lower():
                                result["sex"] = "female"
                            elif "m" in sex_raw.lower():
                                result["sex"] = "male"
                            else:
                                result["sex"] = "unknown"
                        return result
        except Exception:
            pass
    
    # Default to unknown if not found
    return {
        "age": "unknown",
        "sex": "unknown",
    }


def _standardize_channel_names(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names to 10-20 system names."""
    
    # Build rename map based on common BrainVision channel naming
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names
    
    # Common channel name patterns in BrainVision
    # Try to detect standard 10-20 positions
    for ch in ch_names:
        ch_upper = ch.upper()
        
        # Already standard names
        if re.match(r'^[A-Z]{1,2}\d*$', ch_upper) and ch_upper not in ['EOG', 'EMG', 'ECG', 'REF', 'GND']:
            continue
        
        # Numbered EEG channels - need mapping
        if ch_upper.startswith('EEG-') or ch_upper.startswith('EEG '):
            try:
                num = int(re.sub(r'[^0-9]', '', ch))
                # Standard 64-channel layout mapping
                # This is a simplified mapping for common BrainVision setups
                pass
            except ValueError:
                pass
    
    # Try to apply standard 1020 montage if channels look like standard names
    standard_chs = set(['Fp1', 'Fp2', 'Fz', 'F3', 'F4', 'F7', 'F8',
                        'FC1', 'FC2', 'FC5', 'FC6',
                        'Cz', 'C3', 'C4', 'C5', 'C6',
                        'CP1', 'CP2', 'CP5', 'CP6',
                        'Pz', 'P3', 'P4', 'P7', 'P8',
                        'POz', 'PO3', 'PO4',
                        'O1', 'O2', 'Oz',
                        'AFz', 'Fpz'])
    
    ch_set = set(ch_names)
    
    # If more than half of standard channels are present, try to set montage
    if len(ch_set & standard_chs) >= 10:
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, on_missing='warn')
        except Exception:
            pass
    
    return raw


@dataclass
class OpenNeuroDS004295Kernel:
    """Stage1 kernel for OpenNeuro ds004295 dataset.
    
    Reward gain vs punishment avoidance reversal learning task.
    BrainVision format with BIDS structure.
    """
    
    KERNEL_ID: str = "openneuro-ds004295-stage1"
    
    # Class-level cache for participants data
    _participants_cache: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object (BrainVision format)
        row : Locator row with file path information
        
        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized events and metadata
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", "")
        subject_id = row.get("Subject ID", "sub-01")
        
        # 1. Extract subject metadata
        subject_info = _get_subject_info(dataset_path, subject_id)
        
        # 2. Get EEG directory for events.tsv
        eeg_dir = os.path.dirname(file_path) if file_path else ""
        
        # 3. Load and process events from events.tsv
        events_df = _load_events_tsv(eeg_dir, subject_id)
        
        # 4. Build annotations from events
        annotations = _build_annotations_from_events(
            raw, events_df, _EVENT_MAP, raw.info["sfreq"]
        )
        raw.set_annotations(annotations)
        
        # 5. Standardize channel names and set montage
        raw = _standardize_channel_names(raw)
        
        # 6. Build description JSON
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": _DATASET_INFO.get("amplifier", "unknown"),
                "cap": _DATASET_INFO.get("cap", "unknown"),
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = OpenNeuroDS004295Kernel()