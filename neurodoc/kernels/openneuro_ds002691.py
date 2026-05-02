"""Stage1 kernel for OpenNeuro ds002691 - Internal Attention Study.

Dataset: https://openneuro.org/datasets/ds002691
Paradigm: Sustained internal attention (concentrate vs relax) with 15-second blocks.
Subjects: 20 | Channels: 32 | Sampling Rate: 250 Hz

This is a BIDS-compliant dataset with BrainVision .vhdr/.eeg/.vmrk files.
Events are stored in *_events.tsv sidecars with trial_type column containing
'wait', 'relax', 'getready', 'concentrate' labels.

Source: Ceh et al. (2020) Neurophysiological indicators of internal attention.
        DOI: 10.3389/fnins.2021.664490
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
# Required info fields from participants.tsv
# =============================================================================
_REQUIRED_INFO_FIELDS = [
    "Cooperativeness",
    "HarmAvoidance",
    "NoveltySeeking",
    "Persistence",
    "RewardDependence",
    "SelfDirectedness",
    "SelfTranscendence",
    "age",
    "gender",
]

# =============================================================================
# Channel mapping for standard_1020 montage
# =============================================================================
# Source: BrainVision standard 32-channel cap layout for internal attention study
# Annotator: LLM inferred from BIDS eeg.json and standard BrainAmp 32ch setup, 2026-04-08
_CHANNEL_RENAME_MAP = {
    "Fp1": ["Fp1"],
    "Fp2": ["Fp2"],
    "F7": ["F7"],
    "F3": ["F3"],
    "Fz": ["Fz"],
    "F4": ["F4"],
    "F8": ["F8"],
    "FC5": ["FC5"],
    "FC1": ["FC1"],
    "FC2": ["FC2"],
    "FC6": ["FC6"],
    "T7": ["T7", "FT7"],
    "C3": ["C3"],
    "Cz": ["Cz"],
    "C4": ["C4"],
    "T8": ["T8", "FT8"],
    "CP5": ["CP5"],
    "CP1": ["CP1"],
    "CP2": ["CP2"],
    "CP6": ["CP6"],
    "P7": ["P7"],
    "P3": ["P3"],
    "Pz": ["Pz"],
    "P4": ["P4"],
    "P8": ["P8"],
    "O1": ["O1"],
    "Oz": ["Oz"],
    "O2": ["O2"],
    "AFz": ["AFz"],
    "POz": ["POz"],
}


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build actual rename map from raw channel names to standard names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)
    for target, aliases in _CHANNEL_RENAME_MAP.items():
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break
    return rename_map


def _read_participants_tsv(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and return required fields for subject."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    df = pd.read_csv(participants_path, sep="\t")
    # Match subject_id like "sub-001" to "sub-001" or "sub-01" format
    subj_rows = df[df["participant_id"] == subject_id]
    if len(subj_rows) == 0:
        # Try zero-padded matching
        subj_num = re.search(r'sub-0*(\d+)', subject_id)
        if subj_num:
            num = subj_num.group(1)
            for pid in df["participant_id"]:
                m = re.search(r'sub-0*(\d+)', str(pid))
                if m and m.group(1) == num:
                    subj_rows = df[df["participant_id"] == pid]
                    break
    
    if len(subj_rows) == 0:
        return {}
    
    row = subj_rows.iloc[0]
    result: Dict[str, str] = {}
    for field in _REQUIRED_INFO_FIELDS:
        if field in row:
            val = row[field]
            if pd.isna(val):
                result[field] = "unknown"
            else:
                result[field] = str(val)
        else:
            result[field] = "unknown"
    
    return result


def _read_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Read sibling events.tsv for given EEG file."""
    base = file_path.replace(".eeg", "").replace(".vhdr", "").replace(".edf", "").replace(".set", "")
    events_path = base + "_events.tsv"
    if not os.path.exists(events_path):
        # Try BIDS-style path resolution
        dir_path = os.path.dirname(file_path)
        fname = os.path.basename(file_path)
        # Remove extension
        fname_no_ext = re.sub(r'\.(eeg|vhdr|edf|set)$', '', fname)
        events_path = os.path.join(dir_path, fname_no_ext + "_events.tsv")
    
    if os.path.exists(events_path):
        return pd.read_csv(events_path, sep="\t")
    return None


def _create_second_after_ready_misc(raw: mne.io.BaseRaw, events_df: pd.DataFrame) -> mne.io.BaseRaw:
    """Create derived misc channel 'second_after_ready' from events.tsv column."""
    if "second_after_ready" not in events_df.columns:
        return raw
    
    # Get DI## events (digital input markers that indicate wait/ready periods)
    # These are the events where second_after_ready values should be aligned
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    
    # Initialize channel with zeros
    misc_data = np.zeros((1, n_samples))
    
    # Find rows with second_after_ready values and their corresponding onsets
    for _, row in events_df.iterrows():
        onset = row.get("onset")
        val = row.get("second_after_ready")
        trial_type = str(row.get("trial_type", ""))
        
        if pd.isna(onset) or pd.isna(val):
            continue
        
        # Convert to sample index
        sample_idx = int(float(onset) * sfreq)
        if 0 <= sample_idx < n_samples:
            # Set value at onset and carry forward until next event
            misc_data[0, sample_idx:] = float(val)
    
    # Create RawArray for the misc channel
    info = mne.create_info(
        ch_names=["second_after_ready"],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    misc_raw = mne.io.RawArray(misc_data, info, first_samp=raw.first_samp)
    
    # Add to existing raw
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


def _events_tsv_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = row.get("onset")
        duration = row.get("duration", 0.0)
        trial_type = row.get("trial_type", "")
        value = row.get("value", "")
        
        if pd.isna(onset):
            continue
        
        # Use trial_type as description if available, otherwise value
        if pd.notna(trial_type) and str(trial_type).strip():
            desc = str(trial_type).strip()
        elif pd.notna(value):
            desc = str(value).strip()
        else:
            desc = "unknown"
        
        onsets.append(float(onset))
        durations.append(float(duration) if pd.notna(duration) else 0.0)
        descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions
    )


@dataclass
class OpenNeuroDS002691Kernel:
    """Stage1 kernel for OpenNeuro ds002691 - Internal Attention Study."""

    KERNEL_ID: str = "openneuro-ds002691-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_path = getattr(udataset, "path", os.path.dirname(os.path.dirname(file_path)))
        
        # Extract subject ID from file path
        fname = os.path.basename(file_path)
        subject_match = re.search(r'(sub-[0-9]+)', fname)
        if not subject_match:
            subject_match = re.search(r'(sub-[0-9]+)', file_path)
        subject_id = subject_match.group(1) if subject_match else "unknown"
        
        # =================================================================
        # 1. Channel renaming (BEFORE set_montage)
        # =================================================================
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 1020 montage if channels match
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            # Montage setting failed, continue without spatial info
            pass
        
        # =================================================================
        # 2. Read participants.tsv for metadata
        # =================================================================
        participant_info = _read_participants_tsv(dataset_path, subject_id)
        
        # Extract canonical fields
        age = participant_info.get("age", "unknown")
        gender = participant_info.get("gender", "unknown")
        # Normalize sex to lowercase
        sex = str(gender).lower() if gender not in ("unknown", "") else "unknown"
        if sex not in ("male", "female"):
            sex = "unknown"
        
        # Build eegunity_description with required info fields
        eegunity_desc = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex,
            "amplifier": "BrainAmp",  # Source: BrainVision format implies BrainAmp
            "cap": "Ag/AgCl",
            "handedness": "unknown",  # Not in participants.tsv
        }
        
        # Add required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field not in ("age", "gender"):  # age/gender handled separately
                eegunity_desc[field] = participant_info.get(field, "unknown")
        
        # =================================================================
        # 3. Update raw.info["description"]
        # =================================================================
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =================================================================
        # 4. Handle events from events.tsv sidecar
        # =================================================================
        events_df = _read_events_tsv(file_path)
        
        if events_df is not None and len(events_df) > 0:
            # Check if raw already has meaningful annotations
            has_native_events = False
            if raw.annotations is not None and len(raw.annotations) > 0:
                # Check if annotations are meaningful (not just boundary/edge)
                for desc in raw.annotations.description:
                    if desc not in ("BAD boundary", "EDGE boundary", "New Segment"):
                        has_native_events = True
                        break
            
            # BrainVision .eeg without .vmrk or with incomplete markers needs events.tsv
            # Also EDF without annotations, EEGLAB without events, plain .fif
            file_ext = os.path.splitext(file_path)[1].lower()
            needs_tsv_events = (
                not has_native_events or
                file_ext in (".edf", ".fif") or
                (file_ext == ".set" and not has_native_events) or
                (file_ext == ".eeg" and not has_native_events)
            )
            
            if needs_tsv_events:
                # Derive annotations from events.tsv
                annotations = _events_tsv_to_annotations(events_df)
                # Combine with existing if any
                if raw.annotations is not None and len(raw.annotations) > 0:
                    raw.set_annotations(raw.annotations + annotations)
                else:
                    raw.set_annotations(annotations)
            
            # =================================================================
            # 5. Create derived misc channels from events.tsv
            # =================================================================
            # second_after_ready: per-epoch scalar from events.tsv:second_after_ready
            raw = _create_second_after_ready_misc(raw, events_df)
        
        return raw


KERNEL = OpenNeuroDS002691Kernel()