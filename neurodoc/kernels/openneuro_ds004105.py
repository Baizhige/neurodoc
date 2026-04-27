"""OpenNeuro ds004105 stage1 kernel for EEGUnity.

BCIT Auditory Cueing dataset - driving fatigue paradigm with auditory cueing.
74-channel BioSemi ActiveTwo, 1024 Hz sampling.

This kernel handles EEGLAB .set files with events.tsv sidecars.
Events are read from sidecar files and injected as annotations since EEGLAB
.set files in this dataset do not carry embedded event information (empty event field).

Source: https://openneuro.org/datasets/ds004105
Reference: https://doi.org/10.1016/j.neuroimage.2017.02.057
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
# BioSemi ActiveTwo amplifier
# Source: BCIT lab documentation, BioSemi ActiveTwo specifications
# Annotator: LLM, 2026-04-08
_AMPLIFIER = "BioSemi ActiveTwo"  # LLM 推断，需人类复核

# BioSemi standard cap uses Ag/AgCl sintered electrodes
# Source: BioSemi ActiveTwo product specifications
# Annotator: LLM, 2026-04-08
_CAP = "Ag/AgCl"  # LLM 推断，需人类复核


# ----------------------------------------------------------------------
# Required info fields from participants.tsv
# ----------------------------------------------------------------------
_REQUIRED_INFO_FIELDS = ["year_of_birth", "sex", "handedness"]


# ----------------------------------------------------------------------
# Derived misc channels
# ----------------------------------------------------------------------
_DERIVED_MISC_CHANNELS = [
    {"name": "age", "source_field": "participants.tsv:year_of_birth", "derivation": "constant_broadcast"}
]


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    base = re.sub(r'_eeg\.(edf|bdf|set|fif|eeg)$', '', file_path, flags=re.IGNORECASE)
    # Try standard BIDS naming patterns
    candidates = [
        base + "_events.tsv",
        re.sub(r'_task-[^_]+', '', base) + "_events.tsv",
        re.sub(r'_run-\d+', '', base) + "_events.tsv",
    ]
    # Also check parent directory
    dir_candidates = [
        os.path.join(os.path.dirname(file_path), "events.tsv"),
    ]
    for candidate in set(candidates + dir_candidates):
        if os.path.isfile(candidate):
            return candidate
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current = os.path.dirname(file_path)
    for _ in range(5):  # Search up to 5 levels up
        candidate = os.path.join(current, "participants.tsv")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def _extract_subject_id(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'(sub-[a-zA-Z0-9]+)', file_path)
    if match:
        return match.group(1)
    return None


def _read_participants_info(participants_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    try:
        df = pd.read_csv(participants_path, sep='\t')
        # Normalize subject_id column
        subj_col = None
        for col in df.columns:
            if col.lower() in ['participant_id', 'subject_id', 'participant id']:
                subj_col = col
                break
        if subj_col is None:
            return {}
        
        row = df[df[subj_col] == subject_id]
        if row.empty:
            return {}
        
        result = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in row.columns:
                val = row[field].values[0]
                # Handle missing values
                if pd.isna(val):
                    result[field] = "unknown"
                else:
                    result[field] = str(val)
            else:
                result[field] = "unknown"
        return result
    except Exception:
        return {}


def _compute_age(year_of_birth: str) -> str:
    """Compute age from year_of_birth. Dataset year is 2022 per analysis.md."""
    try:
        yob = int(float(year_of_birth))
        age = 2022 - yob
        if 0 < age < 120:
            return str(age)
    except (ValueError, TypeError):
        pass
    return "unknown"


def _create_age_misc_channel(raw: mne.io.BaseRaw, age: str) -> mne.io.RawArray:
    """Create a constant misc channel with age value."""
    try:
        age_val = float(age) if age != "unknown" else np.nan
    except (ValueError, TypeError):
        age_val = np.nan
    
    data = np.full((1, len(raw.times)), age_val)
    info = mne.create_info(ch_names=["age"], sfreq=raw.info["sfreq"], ch_types=["misc"])
    age_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
    return age_raw


@dataclass
class OpenNeuroDS004105Kernel:
    """Stage1 kernel for OpenNeuro ds004105 (BCIT Auditory Cueing)."""

    KERNEL_ID: str = "openneuro-ds004105-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # ------------------------------------------------------------------
        # 1. Channel rename (before set_montage)
        # ------------------------------------------------------------------
        # BioSemi 74-channel naming: standard 10-20 extended with BioSemi prefix
        # Channels may come as 'A1', 'A2', ... or 'EXG1', 'EXG2', etc.
        # Standard BioSemi 64+10 channel layout for ActiveTwo
        #
        # Source: BioSemi 64+10 channel cap documentation, standard_1020 extended
        # Annotator: LLM, 2026-04-08
        
        # Check if channels need renaming (BioSemi often uses numbered channels)
        rename_map = {}
        for ch_name in raw.ch_names:
            # Handle BioSemi A1-A64 -> standard names
            if re.match(r'^A\d+$', ch_name):
                # Map A1-A64 to standard 10-20 extended positions
                # This is a standard mapping for BioSemi caps
                pass  # Keep as-is if already standard, or map if needed
        
        # For this dataset, channels appear to already have reasonable names
        # or use standard BioSemi notation. Apply standard_1020 montage if possible.
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # ------------------------------------------------------------------
        # 2. Set channel types and montage
        # ------------------------------------------------------------------
        # Identify EXG channels as EOG/EMG/misc
        ch_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            if 'EXG' in upper:
                # EXG1-EXG8 typically used for EOG and reference
                ch_types[ch_name] = 'misc'
            elif 'STATUS' in upper or 'TRIGGER' in upper:
                ch_types[ch_name] = 'stim'
        
        if ch_types:
            raw.set_channel_types(ch_types)

        # Set standard montage for 64+ channel cap
        try:
            # Try standard 1005 for high-density coverage
            montage = mne.channels.make_standard_montage('standard_1005')
            # Select only channels that exist in raw
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(raw.ch_names)
            common = list(montage_ch_names & raw_ch_names)
            if len(common) >= 32:  # Require reasonable coverage
                montage = montage.copy()
                # Keep only common channels to avoid errors
                positions = montage.get_positions()
                ch_pos = {k: v for k, v in positions['ch_pos'].items() if k in raw_ch_names}
                montage = mne.channels.make_dig_montage(
                    ch_pos=ch_pos,
                    nasion=positions.get('nasion'),
                    lpa=positions.get('lpa'),
                    rpa=positions.get('rpa'),
                    hsp=positions.get('hsp'),
                    hpi=positions.get('hpi'),
                    coord_frame=positions.get('coord_frame')
                )
                raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass  # Montage optional

        # ------------------------------------------------------------------
        # 3. Read events from sidecar and inject as annotations
        # ------------------------------------------------------------------
        # EEGLAB .set files in this dataset have empty event fields
        # Events must be read from events.tsv sidecars
        # CRITICAL: Use the 'value' column as the annotation description, NOT 'trial_type'
        # The 'value' column contains the actual numeric trigger codes (e.g., 3111, 1211, 3200)
        # The 'trial_type' column does not exist in this dataset's events.tsv files
        events_tsv = _find_events_tsv(file_path)
        if events_tsv:
            try:
                events_df = pd.read_csv(events_tsv, sep='\t', dtype=str, na_values=['n/a', 'N/A', 'NA', 'nan', 'NaN', ''], keep_default_na=True)
                # BIDS events.tsv columns for this dataset: onset, duration, sample, value
                # The 'value' column carries the distinguishable trigger labels
                onsets = []
                durations = []
                descriptions = []
                for _, ev_row in events_df.iterrows():
                    # onset is in seconds in BIDS events.tsv
                    onset = float(ev_row['onset'])
                    # Handle duration: 'n/a' or missing should be 0.0
                    duration_raw = ev_row.get('duration', '0.0')
                    if pd.isna(duration_raw) or str(duration_raw).lower() in ('n/a', 'na', ''):
                        duration = 0.0
                    else:
                        duration = float(duration_raw)
                    if duration <= 0:
                        duration = 0.0
                    # Use 'value' column as the event description (literal string, no remapping)
                    # This preserves the actual trigger codes from the experiment
                    desc = str(ev_row.get('value', 'unknown'))
                    # Skip rows with missing/unknown values
                    if desc == 'nan' or desc == 'unknown' or pd.isna(desc):
                        continue
                    onsets.append(onset)
                    durations.append(duration)
                    descriptions.append(desc)
                
                # Create annotations and set on raw
                # onset is in seconds, which matches MNE's expectation
                if len(onsets) > 0:
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                        orig_time=None
                    )
                    raw.set_annotations(annotations)
            except Exception as e:
                # Log error for debugging but don't fail
                import warnings
                warnings.warn(f"Failed to load events from {events_tsv}: {e}")

        # ------------------------------------------------------------------
        # 4. Participant info and derived channels
        # ------------------------------------------------------------------
        # Extract subject ID and read participant info
        subject_id = _extract_subject_id(file_path)
        participants_info = {}
        if subject_id:
            participants_tsv = _find_participants_tsv(file_path)
            if participants_tsv:
                participants_info = _read_participants_info(participants_tsv, subject_id)

        # Compute age from year_of_birth and add as derived misc channel
        year_of_birth = participants_info.get('year_of_birth', 'unknown')
        age = _compute_age(year_of_birth)
        if age != "unknown":
            age_raw = _create_age_misc_channel(raw, age)
            raw = raw.add_channels([age_raw], force_update_info=True)

        # ------------------------------------------------------------------
        # 5. eegunity_description metadata
        # ------------------------------------------------------------------
        eegunity_description = {
            "age": age if age != "unknown" else "unknown",
            "sex": participants_info.get('sex', 'unknown'),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": participants_info.get('handedness', 'unknown'),
        }
        # Store in raw.info['description'] as JSON for downstream access
        raw.info['description'] = json.dumps(eegunity_description)

        return raw


KERNEL = OpenNeuroDS004105Kernel()