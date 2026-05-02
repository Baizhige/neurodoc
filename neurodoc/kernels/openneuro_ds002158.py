"""OpenNeuro ds002158 stage1 kernel for EEGUnity.

Dataset: Disentangling the origins of confidence in speeded perceptual judgments
through multimodal imaging

Source: https://openneuro.org/datasets/ds002158
Paper DOI: 10.1073/pnas.1918335117

This kernel handles:
- BIDS-compliant dataset with BrainVision (.vhdr/.eeg/.vmrk) files
- High sampling rate (5000 Hz) - preserved; downsampling done at epoch stage
- 63-channel EEG data
- Standard 10-20 montage setup
- Event extraction from BrainVision annotations and events.tsv sidecars
- Derived misc channels from events.tsv: confidence, response_time, dots_difference, response_time2
- Required info fields from participants.tsv: age, sex, amplifier, cap, handedness

Annotator: LLM, 2026-04-08 - needs human review for all non-BIDS-standard inferences
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
# Dataset-specific constants
# =============================================================================

# Required info fields from participants.tsv
# Source: kernel requirements specification
# Annotator: LLM, 2026-04-08
_REQUIRED_INFO_FIELDS = ["age", "sex", "amplifier", "cap", "handedness"]

# Required derived misc channels (kernel must create these)
# Source: kernel requirements specification
# Annotator: LLM, 2026-04-08
_REQUIRED_DERIVED_MISC = ["confidence", "response_time", "dots_difference", "response_time2"]

# Derived misc channel specifications
# Format: (name, source_field)
# source_field: "events.tsv:<column>" means read from sibling events.tsv
_DERIVED_MISC_SPECS = [
    ("confidence", "events.tsv:confidence"),
    ("response_time", "events.tsv:response_time"),
    ("dots_difference", "events.tsv:dots_difference"),
    ("response_time2", "events.tsv:response_time2"),
]

# BrainVision channel naming to standard 10-20
# Source: BrainAmp standard 64-channel cap, extended 10-20 system
# Annotator: inferred by LLM, needs human review, 2026-04-08
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Lowercase variants to standard uppercase
    "fp1": "Fp1",
    "fp2": "Fp2",
    "f7": "F7",
    "f3": "F3",
    "fz": "Fz",
    "f4": "F4",
    "f8": "F8",
    "t7": "T7",
    "c3": "C3",
    "cz": "Cz",
    "c4": "C4",
    "t8": "T8",
    "p7": "P7",
    "p3": "P3",
    "pz": "Pz",
    "p4": "P4",
    "p8": "P8",
    "o1": "O1",
    "oz": "Oz",
    "o2": "O2",
    "fc1": "FC1",
    "fc2": "FC2",
    "fc5": "FC5",
    "fc6": "FC6",
    "cp1": "CP1",
    "cp2": "CP2",
    "cp5": "CP5",
    "cp6": "CP6",
    "afz": "AFz",
    "af3": "AF3",
    "af4": "AF4",
    "af7": "AF7",
    "af8": "AF8",
    "f1": "F1",
    "f2": "F2",
    "f5": "F5",
    "f6": "F6",
    "ft7": "FT7",
    "ft8": "FT8",
    "ft9": "FT9",
    "ft10": "FT10",
    "c1": "C1",
    "c2": "C2",
    "c5": "C5",
    "c6": "C6",
    "tp7": "TP7",
    "tp8": "TP8",
    "p1": "P1",
    "p2": "P2",
    "p5": "P5",
    "p6": "P6",
    "po7": "PO7",
    "po3": "PO3",
    "poz": "POz",
    "po4": "PO4",
    "po8": "PO8",
    "iz": "Iz",
    # Already correct mappings (identity)
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC5": "FC5",
    "FC6": "FC6",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP5": "CP5",
    "CP6": "CP6",
    "AFz": "AFz",
    "AF3": "AF3",
    "AF4": "AF4",
    "AF7": "AF7",
    "AF8": "AF8",
    "F1": "F1",
    "F2": "F2",
    "F5": "F5",
    "F6": "F6",
    "FT7": "FT7",
    "FT8": "FT8",
    "FT9": "FT9",
    "FT10": "FT10",
    "C1": "C1",
    "C2": "C2",
    "C5": "C5",
    "C6": "C6",
    "TP7": "TP7",
    "TP8": "TP8",
    "P1": "P1",
    "P2": "P2",
    "P5": "P5",
    "P6": "P6",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "Iz": "Iz",
}


# =============================================================================
# Helper functions
# =============================================================================

def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    # Pattern: sub-XX or sub-XXX in path
    match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_bids_root(file_path: str) -> Optional[str]:
    """Find BIDS root directory from file path."""
    # Walk up looking for participants.tsv
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        if os.path.exists(os.path.join(current_dir, "participants.tsv")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_tsv(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    participants_path = os.path.join(bids_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for this subject
        subj_row = df[df["participant_id"] == subject_id]
        if subj_row.empty:
            # Try without "sub-" prefix
            subj_row = df[df["participant_id"] == subject_id.replace("sub-", "")]
        if subj_row.empty:
            return {}
        
        result = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in subj_row.columns:
                val = subj_row[field].values[0]
                # Handle NaN/missing
                if pd.isna(val):
                    result[field] = "unknown"
                else:
                    result[field] = str(val).strip()
            else:
                result[field] = "unknown"
        return result
    except Exception:
        return {}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XX_ses-YY_task-ZZ_run-WW_eeg.<ext> -> sub-XX_ses-YY_task-ZZ_run-WW_events.tsv
    base = file_path
    # Remove extension
    for ext in [".vhdr", ".eeg", ".vmrk", ".edf", ".bdf", ".set", ".fif"]:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try without run suffix
    base_no_run = re.sub(r"_run-[0-9]+", "", base)
    events_path = base_no_run + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Search in same directory
    eeg_dir = os.path.dirname(file_path)
    pattern = re.compile(r".*_events\.tsv$")
    for f in os.listdir(eeg_dir):
        if pattern.match(f):
            return os.path.join(eeg_dir, f)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not events_path or not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _extract_event_value(row: pd.Series) -> str:
    """Extract event value/description from events.tsv row."""
    # Priority: trial_type > value > stim_type > description
    if "trial_type" in row and pd.notna(row["trial_type"]):
        return str(row["trial_type"])
    if "value" in row and pd.notna(row["value"]):
        return str(row["value"])
    if "stim_type" in row and pd.notna(row["stim_type"]):
        return str(row["stim_type"])
    if "description" in row and pd.notna(row["description"]):
        return str(row["description"])
    return "unknown"


def _create_annotations_from_events_tsv(events_df: pd.DataFrame, raw: mne.io.BaseRaw) -> mne.Annotations:
    """Create MNE Annotations from events.tsv DataFrame."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, evt_row in events_df.iterrows():
        onset = float(evt_row["onset"]) if "onset" in evt_row and pd.notna(evt_row["onset"]) else 0.0
        duration = float(evt_row["duration"]) if "duration" in evt_row and pd.notna(evt_row["duration"]) else 0.0
        desc = _extract_event_value(evt_row)
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    # Filter to valid time range
    max_time = raw.times[-1] if len(raw.times) > 0 else float('inf')
    valid_idx = [i for i, o in enumerate(onsets) if o < max_time]
    
    if not valid_idx:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    return mne.Annotations(
        onset=[onsets[i] for i in valid_idx],
        duration=[durations[i] for i in valid_idx],
        description=[descriptions[i] for i in valid_idx],
        orig_time=raw.info["meas_date"]
    )


def _create_derived_misc_channel(raw: mne.io.BaseRaw, channel_name: str, events_df: pd.DataFrame, 
                                  align_column: str, align_event: Optional[str] = None,
                                  default_value: float = 0.0) -> mne.io.BaseRaw:
    """Create a derived MISC channel from events.tsv column data.
    
    Creates a step-function channel where the value from events.tsv is held
    from each trial's onset until the next trial's onset.
    """
    if events_df is None or events_df.empty or align_column not in events_df.columns:
        # Skip if source not available - do not fabricate
        return raw
    
    # Get trial onsets and values
    trial_onsets = []
    trial_values = []
    
    for _, evt_row in events_df.iterrows():
        onset = float(evt_row["onset"]) if "onset" in evt_row and pd.notna(evt_row["onset"]) else None
        if onset is None:
            continue
        
        # Check if this row matches alignment event (if specified)
        if align_event is not None:
            evt_desc = _extract_event_value(evt_row)
            if evt_desc != align_event:
                continue
        
        # Get value from column
        val = evt_row.get(align_column, np.nan)
        if pd.isna(val):
            continue  # Skip rows with missing values rather than using default
        
        trial_onsets.append(onset)
        trial_values.append(float(val))
    
    if not trial_onsets:
        # No matching events with valid values, skip
        return raw
    
    # Sort by onset
    sorted_pairs = sorted(zip(trial_onsets, trial_values))
    trial_onsets = [p[0] for p in sorted_pairs]
    trial_values = [p[1] for p in sorted_pairs]
    
    # Create step function
    sfreq = raw.info["sfreq"]
    n_samples = len(raw.times)
    data = np.full(n_samples, np.nan, dtype=np.float64)  # Start with NaN to identify gaps
    
    for i, (onset, value) in enumerate(zip(trial_onsets, trial_values)):
        start_idx = int(round(onset * sfreq))
        # Hold until next trial or end
        if i + 1 < len(trial_onsets):
            end_idx = int(round(trial_onsets[i + 1] * sfreq))
        else:
            end_idx = n_samples
        
        start_idx = max(0, min(start_idx, n_samples))
        end_idx = max(0, min(end_idx, n_samples))
        
        if start_idx < end_idx:
            data[start_idx:end_idx] = value
    
    # Fill any remaining NaNs with forward fill, then backward fill if needed
    # This ensures continuous data without gaps
    mask = np.isnan(data)
    if np.any(mask):
        # Forward fill
        idx = np.where(~mask, np.arange(n_samples), 0)
        np.maximum.accumulate(idx, out=idx)
        data[mask] = data[idx[mask]]
        # Backward fill for any leading NaNs
        mask = np.isnan(data)
        if np.any(mask):
            idx = np.where(~mask, np.arange(n_samples), n_samples - 1)
            np.minimum.accumulate(idx[::-1], out=idx[::-1])
            data[mask] = data[idx[mask]]
        # If still any NaNs (all NaN case), use default
        mask = np.isnan(data)
        if np.any(mask):
            data[mask] = default_value
    
    # Add as new channel
    info = mne.create_info([channel_name], raw.info["sfreq"], ch_types=["misc"])
    misc_raw = mne.io.RawArray(data.reshape(1, -1), info, first_samp=raw.first_samp)
    misc_raw.set_meas_date(raw.info["meas_date"])
    raw.add_channels([misc_raw], force_update_info=True)
    return raw


# =============================================================================
# Kernel class
# =============================================================================

class OpenNeuroDS002158Kernel:
    """Stage1 kernel for OpenNeuro ds002158.
    
    Handles BrainVision EEG files with BIDS structure, extracting events from
    both BrainVision markers and events.tsv sidecars, and creating derived
    misc channels for trial-level variables.
    """
    
    def __init__(self):
        self.name = "openneuro_ds002158"
        self.version = "1.0.0"
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply kernel processing to a single EEG file.
        
        Parameters
        ----------
        udataset : object
            EEGUnity dataset object with metadata and file information.
        raw : mne.io.BaseRaw
            Loaded MNE Raw object.
        row : pd.Series
            Metadata row for this file from the dataset index.
        
        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with standardized channels, annotations,
            and derived misc channels.
        """
        # ---------------------------------------------------------------------
        # 1. Standardize channel names to uppercase 10-20
        # ---------------------------------------------------------------------
        rename_map = {}
        for ch_name in raw.ch_names:
            ch_lower = ch_name.lower()
            if ch_lower in _CHANNEL_RENAME_MAP:
                new_name = _CHANNEL_RENAME_MAP[ch_lower]
                if new_name != ch_name:
                    rename_map[ch_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # ---------------------------------------------------------------------
        # 2. Set channel types: EEG for data channels, exclude non-EEG
        # ---------------------------------------------------------------------
        eeg_pattern = re.compile(r'^[a-zA-Z]+[0-9]+[zZ]?$|^[a-zA-Z]{2}[0-9]+$')
        channel_types = {}
        for ch_name in raw.ch_names:
            ch_upper = ch_name.upper()
            # Standard 10-20 channel names are EEG
            if ch_upper in _CHANNEL_RENAME_MAP.values():
                channel_types[ch_name] = 'eeg'
            elif eeg_pattern.match(ch_name):
                channel_types[ch_name] = 'eeg'
            else:
                # Check if already typed
                pass
        
        if channel_types:
            raw.set_channel_types(channel_types)
        
        # ---------------------------------------------------------------------
        # 3. Set montage to standard 10-20
        # ---------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass
        
        # ---------------------------------------------------------------------
        # 4. Extract file path and find BIDS resources
        # ---------------------------------------------------------------------
        file_path = str(row.get('file_path', ''))
        if not file_path and hasattr(udataset, 'index'):
            # Try to get from udataset index
            pass
        
        # Find BIDS root and subject ID
        bids_root = _find_bids_root(file_path)
        subject_id = _get_subject_id_from_path(file_path)
        
        # ---------------------------------------------------------------------
        # 5. Read participants.tsv for subject info
        # ---------------------------------------------------------------------
        eegunity_description = {}
        if bids_root and subject_id:
            participant_info = _read_participants_tsv(bids_root, subject_id)
            eegunity_description.update(participant_info)
        
        # Ensure all required fields exist
        for field in _REQUIRED_INFO_FIELDS:
            if field not in eegunity_description:
                eegunity_description[field] = "unknown"
        
        # Store in raw.info['description'] as JSON
        try:
            existing_desc = raw.info.get('description', '{}')
            if existing_desc:
                try:
                    desc_dict = json.loads(existing_desc)
                except (json.JSONDecodeError, TypeError):
                    desc_dict = {'original_description': str(existing_desc)}
            else:
                desc_dict = {}
            desc_dict.update(eegunity_description)
            raw.info['description'] = json.dumps(desc_dict)
        except Exception:
            pass
        
        # ---------------------------------------------------------------------
        # 6. Process events from events.tsv
        # ---------------------------------------------------------------------
        events_path = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_path)
        
        # Create annotations from events.tsv
        if events_df is not None and not events_df.empty:
            annotations = _create_annotations_from_events_tsv(events_df, raw)
            if len(annotations) > 0:
                # Merge with existing annotations
                existing_annotations = raw.annotations
                if len(existing_annotations) > 0:
                    raw.set_annotations(existing_annotations + annotations)
                else:
                    raw.set_annotations(annotations)
        
        # ---------------------------------------------------------------------
        # 7. Create derived misc channels from events.tsv columns
        # ---------------------------------------------------------------------
        for channel_name, source_field in _DERIVED_MISC_SPECS:
            # Parse source_field
            if source_field.startswith("events.tsv:"):
                column_name = source_field.split(":", 1)[1]
                # Create step-function channel from events.tsv
                raw = _create_derived_misc_channel(
                    raw, channel_name, events_df, column_name,
                    align_event=None, default_value=0.0
                )
            elif source_field.startswith("participants.tsv:"):
                # Not used in this dataset, but handle for completeness
                column_name = source_field.split(":", 1)[1]
                if bids_root and subject_id:
                    participant_info = _read_participants_tsv(bids_root, subject_id)
                    if column_name in participant_info:
                        try:
                            value = float(participant_info[column_name])
                        except (ValueError, TypeError):
                            continue  # Skip non-numeric values
                        # Broadcast as constant channel
                        data = np.full((1, len(raw.times)), value, dtype=np.float64)
                        info = mne.create_info([channel_name], raw.info["sfreq"], ch_types=["misc"])
                        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
                        misc_raw.set_meas_date(raw.info["meas_date"])
                        raw.add_channels([misc_raw], force_update_info=True)
            # else: unknown source format, skip
        
        # ---------------------------------------------------------------------
        # 8. Final validation
        # ---------------------------------------------------------------------
        # Ensure derived misc channels exist and have correct type
        for channel_name, _ in _DERIVED_MISC_SPECS:
            if channel_name in raw.ch_names:
                # Ensure it's typed as misc
                current_types = raw.get_channel_types(picks=[channel_name])
                if current_types and current_types[0] != 'misc':
                    raw.set_channel_types({channel_name: 'misc'})
        
        return raw


# =============================================================================
# Kernel instance
# =============================================================================

KERNEL = OpenNeuroDS002158Kernel()