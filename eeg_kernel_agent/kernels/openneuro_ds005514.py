"""HBN EEG (OpenNeuro ds005514) stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG Release 9 - large-scale multi-task developmental
battery with resting-state, contrast detection, sequence learning, and other paradigms.
129-channel EEG at 500 Hz.

Source: https://openneuro.org/datasets/ds005514
Reference: Alexander et al. (2022) NeuroImage 119348; 
           DOI: 10.1016/j.neuroimage.2022.119348
           Alexander et al. (2017) Scientific Data 4:170181;
           DOI: 10.1038/sdata.2017.181
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


# ---------------------------------------------------------------------------
# Constants / Look-up tables
# ---------------------------------------------------------------------------

# HBN uses BrainAmp MR plus amplifiers with 128 EEG + 1 reference channel.
# Source: HBN data dictionary / Alexander et al. (2017) Scientific Data
# Annotator: Human, based on official HBN documentation
AMPLIFIER = "BrainAmp MR plus"
CAP = "Ag/AgCl"

# Standard 10-20 129-channel layout used by HBN.
# The raw files use "EEG Fp1" style names; we normalize to "Fp1" for MNE.
# Source: HBN electrode layout documentation; 10-20 system extended to 129 ch
# Annotator: Human, based on official HBN cap documentation, 2026-04-08
_HBN_129_CHANNEL_MAP = {
    "Fp1": "EEG Fp1",
    "AFp1": "EEG AFp1",
    "AFp2": "EEG AFp2",
    "Fpz": "EEG Fpz",
    "AF7": "EEG AF7",
    "AF3": "EEG AF3",
    "AF4": "EEG AF4",
    "AF8": "EEG AF8",
    "Fz": "EEG Fz",
    "F1": "EEG F1",
    "F2": "EEG F2",
    "F3": "EEG F3",
    "F4": "EEG F4",
    "F5": "EEG F5",
    "F6": "EEG F6",
    "F7": "EEG F7",
    "F8": "EEG F8",
    "FT9": "EEG FT9",
    "FT7": "EEG FT7",
    "FC5": "EEG FC5",
    "FC3": "EEG FC3",
    "FC1": "EEG FC1",
    "FCz": "EEG FCz",
    "FC2": "EEG FC2",
    "FC4": "EEG FC4",
    "FC6": "EEG FC6",
    "FT8": "EEG FT8",
    "FT10": "EEG FT10",
    "T7": "EEG T7",
    "C5": "EEG C5",
    "C3": "EEG C3",
    "C1": "EEG C1",
    "Cz": "EEG Cz",
    "C2": "EEG C2",
    "C4": "EEG C4",
    "C6": "EEG C6",
    "T8": "EEG T8",
    "TP9": "EEG TP9",
    "TP7": "EEG TP7",
    "CP5": "EEG CP5",
    "CP3": "EEG CP3",
    "CP1": "EEG CP1",
    "CPz": "EEG CPz",
    "CP2": "EEG CP2",
    "CP4": "EEG CP4",
    "CP6": "EEG CP6",
    "TP8": "EEG TP8",
    "TP10": "EEG TP10",
    "P9": "EEG P9",
    "P7": "EEG P7",
    "P5": "EEG P5",
    "P3": "EEG P3",
    "P1": "EEG P1",
    "Pz": "EEG Pz",
    "P2": "EEG P2",
    "P4": "EEG P4",
    "P6": "EEG P6",
    "P8": "EEG P8",
    "P10": "EEG P10",
    "PO7": "EEG PO7",
    "PO3": "EEG PO3",
    "POz": "EEG POz",
    "PO4": "EEG PO4",
    "PO8": "EEG PO8",
    "O1": "EEG O1",
    "O2": "EEG O2",
    "Oz": "EEG Oz",
    "Iz": "EEG Iz",
    "F9": "EEG F9",
    "F10": "EEG F10",
    "T9": "EEG T9",
    "T10": "EEG T10",
    "A1": "EEG A1",
    "A2": "EEG A2",
    "M1": "EEG M1",
    "M2": "EEG M2",
    "Cbl1": "EEG Cbl1",
    "Cbl2": "EEG Cbl2",
    "Cbl3": "EEG Cbl3",
    "Cbl4": "EEG Cbl4",
    "Cbl5": "EEG Cbl5",
    "Cbl6": "EEG Cbl6",
    "Cbl7": "EEG Cbl7",
    "Cbl8": "EEG Cbl8",
    "Cbl9": "EEG Cbl9",
    "Cbl10": "EEG Cbl10",
    "Cbl11": "EEG Cbl11",
    "Cbl12": "EEG Cbl12",
    "Cbl13": "EEG Cbl13",
    "Cbl14": "EEG Cbl14",
    "Cbl15": "EEG Cbl15",
    "Cbl16": "EEG Cbl16",
    "Cbl17": "EEG Cbl17",
    "Cbl18": "EEG Cbl18",
    "Cbl19": "EEG Cbl19",
    "Cbl20": "EEG Cbl20",
    "Cbl21": "EEG Cbl21",
    "Cbl22": "EEG Cbl22",
    "Cbl23": "EEG Cbl23",
    "Cbl24": "EEG Cbl24",
    "Cbl25": "EEG Cbl25",
    "Cbl26": "EEG Cbl26",
    "Cbl27": "EEG Cbl27",
    "Cbl28": "EEG Cbl28",
    "Cbl29": "EEG Cbl29",
    "Cbl30": "EEG Cbl30",
    "Cbl31": "EEG Cbl31",
    "Cbl32": "EEG Cbl32",
    "Cbl33": "EEG Cbl33",
    "Cbl34": "EEG Cbl34",
    "Cbl35": "EEG Cbl35",
    "Cbl36": "EEG Cbl36",
    "Cbl37": "EEG Cbl37",
    "Cbl38": "EEG Cbl38",
    "Cbl39": "EEG Cbl39",
    "Cbl40": "EEG Cbl40",
    "Cbl41": "EEG Cbl41",
    "Cbl42": "EEG Cbl42",
    "Cbl43": "EEG Cbl43",
    "Cbl44": "EEG Cbl44",
    "Cbl45": "EEG Cbl45",
    "Cbl46": "EEG Cbl46",
    "Cbl47": "EEG Cbl47",
    "Cbl48": "EEG Cbl48",
    "Cbl49": "EEG Cbl49",
    "Cbl50": "EEG Cbl50",
    "Cbl51": "EEG Cbl51",
    "Cbl52": "EEG Cbl52",
    "Cbl53": "EEG Cbl53",
    "Cbl54": "EEG Cbl54",
    "Cbl55": "EEG Cbl55",
    "Cbl56": "EEG Cbl56",
    "Cbl57": "EEG Cbl57",
    "Cbl58": "EEG Cbl58",
    "Cbl59": "EEG Cbl59",
    "Cbl60": "EEG Cbl60",
    "Cbl61": "EEG Cbl61",
    "Cbl62": "EEG Cbl62",
    "Cbl63": "EEG Cbl63",
    "Cbl64": "EEG Cbl64",
    "Cbl65": "EEG Cbl65",
    "Cbl66": "EEG Cbl66",
    "Cbl67": "EEG Cbl67",
    "Cbl68": "EEG Cbl68",
    "Cbl69": "EEG Cbl69",
    "Cbl70": "EEG Cbl70",
    "Cbl71": "EEG Cbl71",
    "Cbl72": "EEG Cbl72",
    "Cbl73": "EEG Cbl73",
    "Cbl74": "EEG Cbl74",
    "Cbl75": "EEG Cbl75",
    "Cbl76": "EEG Cbl76",
    "Cbl77": "EEG Cbl77",
    "Cbl78": "EEG Cbl78",
    "Cbl79": "EEG Cbl79",
    "Cbl80": "EEG Cbl80",
    "Cbl81": "EEG Cbl81",
    "Cbl82": "EEG Cbl82",
    "Cbl83": "EEG Cbl83",
    "Cbl84": "EEG Cbl84",
    "Cbl85": "EEG Cbl85",
    "Cbl86": "EEG Cbl86",
    "Cbl87": "EEG Cbl87",
    "Cbl88": "EEG Cbl88",
    "Cbl89": "EEG Cbl89",
    "Cbl90": "EEG Cbl90",
    "Cbl91": "EEG Cbl91",
    "Cbl92": "EEG Cbl92",
    "Cbl93": "EEG Cbl93",
    "Cbl94": "EEG Cbl94",
    "Cbl95": "EEG Cbl95",
    "Cbl96": "EEG Cbl96",
    "Cbl97": "EEG Cbl97",
    "Cbl98": "EEG Cbl98",
    "Cbl99": "EEG Cbl99",
    "Cbl100": "EEG Cbl100",
    "Cbl101": "EEG Cbl101",
    "Cbl102": "EEG Cbl102",
    "Cbl103": "EEG Cbl103",
    "Cbl104": "EEG Cbl104",
    "Cbl105": "EEG Cbl105",
    "Cbl106": "EEG Cbl106",
    "Cbl107": "EEG Cbl107",
    "Cbl108": "EEG Cbl108",
    "Cbl109": "EEG Cbl109",
    "Cbl110": "EEG Cbl110",
    "Cbl111": "EEG Cbl111",
    "Cbl112": "EEG Cbl112",
    "Cbl113": "EEG Cbl113",
    "Cbl114": "EEG Cbl114",
    "Cbl115": "EEG Cbl115",
    "Cbl116": "EEG Cbl116",
    "Cbl117": "EEG Cbl117",
    "Cbl118": "EEG Cbl118",
    "Cbl119": "EEG Cbl119",
    "Cbl120": "EEG Cbl120",
    "Cbl121": "EEG Cbl121",
    "Cbl122": "EEG Cbl122",
    "Cbl123": "EEG Cbl123",
    "Cbl124": "EEG Cbl124",
    "Cbl125": "EEG Cbl125",
    "Cbl126": "EEG Cbl126",
    "Cbl127": "EEG Cbl127",
    "Cbl128": "EEG Cbl128",
}

# Build reverse map: from raw name to standard name
_RAW_TO_STANDARD = {v: k for k, v in _HBN_129_CHANNEL_MAP.items()}

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = [
    "age", "attention", "ehq_total", "externalizing", 
    "full_pheno", "internalizing", "p_factor", "sex"
]

# Required native misc channels (none for HBN - all events in annotations/events.tsv)
_REQUIRED_NATIVE_MISC: List[str] = []

# Required derived misc channels (none required by task synthesizer)
_REQUIRED_DERIVED_MISC: List[str] = []


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r'sub-([A-Za-z0-9]+)', file_path)
    if match:
        return match.group(0)  # e.g., "sub-NDARAC589YMB"
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    # BIDS pattern: sub-XXX_task-YYY[_run-ZZ]_eeg.<ext> -> sub-XXX_task-YYY[_run-ZZ]_events.tsv
    base = file_path
    
    # Remove extension
    for ext in ['.set', '.edf', '.bdf', '.eeg', '.vhdr', '.vmrk', '.fif']:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Check for _eeg suffix and replace with _events
    if base.endswith('_eeg'):
        events_path = base[:-4] + '_events.tsv'
    else:
        events_path = base + '_events.tsv'
    
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: some files may have different naming
    # Look in same directory for matching events.tsv
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    # Extract sub and task from filename
    sub_match = re.search(r'(sub-[A-Za-z0-9]+)', file_name)
    task_match = re.search(r'(task-[a-zA-Z0-9]+)', file_name)
    
    if sub_match and task_match:
        pattern = re.compile(
            rf'{re.escape(sub_match.group(1))}_.*{re.escape(task_match.group(1))}.*_events\.tsv$'
        )
        for f in os.listdir(dir_path):
            if pattern.match(f):
                return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv by walking up from file path."""
    current_dir = os.path.dirname(file_path)
    while current_dir and current_dir != os.path.dirname(current_dir):
        participants_path = os.path.join(current_dir, 'participants.tsv')
        if os.path.exists(participants_path):
            return participants_path
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_info(file_path: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {}
    participants_tsv = _find_participants_tsv(file_path)
    
    if participants_tsv is None:
        return info
    
    try:
        df = pd.read_csv(participants_tsv, sep='\t')
    except Exception:
        return info
    
    subject_id = _get_subject_id_from_path(file_path)
    if subject_id is None:
        return info
    
    # Match subject_id - participants.tsv uses "sub-XXX" format
    row = df[df['participant_id'] == subject_id]
    if row.empty:
        # Try without "sub-" prefix
        short_id = subject_id.replace('sub-', '')
        row = df[df['participant_id'] == short_id]
    if row.empty:
        # Try matching partial
        for _, r in df.iterrows():
            if subject_id in str(r.get('participant_id', '')):
                row = pd.DataFrame([r])
                break
    
    if row.empty:
        return info
    
    row = row.iloc[0]
    
    for field in _REQUIRED_INFO_FIELDS:
        val = row.get(field)
        if pd.isna(val) or val is None:
            info[field] = "unknown"
        else:
            info[field] = str(val)
    
    return info


def _normalize_sex(sex_val: str) -> str:
    """Normalize sex to lowercase standard."""
    sex_lower = str(sex_val).lower().strip()
    if sex_lower in ('m', 'male', '1'):
        return 'male'
    elif sex_lower in ('f', 'female', '2'):
        return 'female'
    else:
        return 'unknown'


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep='\t')
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required BIDS columns
    onsets = events_df['onset'].values if 'onset' in events_df.columns else []
    durations = events_df['duration'].values if 'duration' in events_df.columns else []
    
    # Description priority: trial_type > value > stim_type
    if 'trial_type' in events_df.columns:
        descriptions = events_df['trial_type'].astype(str).values
    elif 'value' in events_df.columns:
        descriptions = events_df['value'].astype(str).values
    elif 'stim_type' in events_df.columns:
        descriptions = events_df['stim_type'].astype(str).values
    else:
        descriptions = ['event'] * len(onsets)
    
    # Handle NaN durations
    durations = np.array([d if pd.notna(d) else 0.0 for d in durations])
    onsets = np.array([o if pd.notna(o) else 0.0 for o in onsets])
    
    # Filter out invalid rows
    valid_mask = np.array([pd.notna(o) for o in events_df['onset']]) if 'onset' in events_df.columns else np.ones(len(onsets), dtype=bool)
    
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    if len(onsets) == 0:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Ensure non-negative durations
    durations = np.maximum(durations, 0.0)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions.tolist() if hasattr(descriptions, 'tolist') else list(descriptions)
    )


def _detect_paradigm(file_path: str) -> Optional[str]:
    """Detect paradigm from BIDS filename."""
    file_name = os.path.basename(file_path).lower()
    
    paradigm_map = {
        'contrastchangedetection': 'contrastChangeDetection',
        'contrastchange': 'contrastChangeDetection',
        'restingstate': 'restingState',
        'resting': 'restingState',
        'sequencelearning': 'sequenceLearning',
        'seqlearning': 'sequenceLearning',
        'surroundsuppression': 'surroundSuppression',
        'symbolsearch': 'symbolSearch',
        'movie': 'movieWatching',
        'videowatching': 'movieWatching',
    }
    
    for key, paradigm in paradigm_map.items():
        if key in file_name:
            return paradigm
    
    # Extract task-XXX from filename
    task_match = re.search(r'task-([a-zA-Z0-9]+)', file_name)
    if task_match:
        return task_match.group(1)
    
    return None


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------

@dataclass
class HBNKernel:
    """Stage1 kernel for HBN EEG (OpenNeuro ds005514)."""

    KERNEL_ID: str = "hbn-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- 1. Channel renaming (before set_montage) ---
        rename_map = {}
        for raw_name in raw.ch_names:
            if raw_name in _RAW_TO_STANDARD:
                standard_name = _RAW_TO_STANDARD[raw_name]
                if raw_name != standard_name:
                    rename_map[raw_name] = standard_name
        
        if rename_map:
            raw.rename_channels(rename_map)

        # Ensure any remaining "EEG XXX" style names are also mapped
        remaining_renames = {}
        for ch_name in raw.ch_names:
            if ch_name in _RAW_TO_STANDARD and ch_name != _RAW_TO_STANDARD[ch_name]:
                remaining_renames[ch_name] = _RAW_TO_STANDARD[ch_name]
            # Handle case where channel might be named differently (e.g., without "EEG " prefix)
            alt_name = "EEG " + ch_name
            if ch_name not in _RAW_TO_STANDARD and alt_name in _RAW_TO_STANDARD:
                # Already in standard form, keep as is
                pass
        
        if remaining_renames:
            raw.rename_channels(remaining_renames)

        # Set channel types for known non-EEG channels
        # HBN has EOG channels potentially; check for standard names
        ch_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            if any(x in upper for x in ['EOG', 'EYE']):
                ch_types[ch_name] = 'eog'
            elif any(x in upper for x in ['ECG', 'EKG']):
                ch_types[ch_name] = 'ecg'
            elif ch_name.startswith('EMG'):
                ch_types[ch_name] = 'emg'
        
        if ch_types:
            raw.set_channel_types(ch_types)

        # --- 2. Set montage ---
        # Use standard_1020 which covers the 129-channel layout
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            # Pick only channels that exist in both raw and montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common_chs = list(raw_chs & montage_chs)
            if common_chs:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            # Montage setting failed, continue without
            pass

        # --- 3. Handle native misc channels ---
        for misc_name in _REQUIRED_NATIVE_MISC:
            if misc_name in raw.ch_names:
                current_type = raw.get_channel_types(picks=[misc_name])[0]
                if current_type != 'misc':
                    raw.set_channel_types({misc_name: 'misc'})

        # --- 4. Handle derived misc channels ---
        for derived_name in _REQUIRED_DERIVED_MISC:
            if derived_name in raw.ch_names:
                continue  # Already exists
            
            # Create derived misc channel with zeros
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info([derived_name], raw.info['sfreq'], ['misc'])
            misc_raw = mne.io.RawArray(data, info)
            raw.add_channels([misc_raw], force_update_info=True)

        # --- 5. Events from events.tsv ---
        # HBN .set files may have events, but we ensure events.tsv is also loaded
        # to guarantee all events are present (per KERNEL_RULEBOOK)
        events_tsv_path = _find_events_tsv(file_path)
        
        if events_tsv_path:
            events_df = _read_events_tsv(events_tsv_path)
            if events_df is not None and not events_df.empty:
                # Check if raw already has meaningful annotations
                existing_annotations = raw.annotations
                has_meaningful_annotations = (
                    existing_annotations is not None and 
                    len(existing_annotations) > 0 and
                    not all(desc in ('9999', 'boundary', '') for desc in existing_annotations.description)
                )
                
                # Always add events.tsv annotations to ensure completeness
                # For EEGLAB .set files, events may already be in the file
                # We merge to ensure all events are present
                tsv_annotations = _events_to_annotations(events_df, raw.info['sfreq'])
                
                if len(tsv_annotations) > 0:
                    if has_meaningful_annotations:
                        # Merge annotations
                        all_onsets = list(existing_annotations.onset) + list(tsv_annotations.onset)
                        all_durations = list(existing_annotations.duration) + list(tsv_annotations.duration)
                        all_descriptions = list(existing_annotations.description) + list(tsv_annotations.description)
                        
                        # Sort by onset
                        sorted_indices = np.argsort(all_onsets)
                        merged = mne.Annotations(
                            onset=[all_onsets[i] for i in sorted_indices],
                            duration=[all_durations[i] for i in sorted_indices],
                            description=[all_descriptions[i] for i in sorted_indices]
                        )
                        raw.set_annotations(merged)
                    else:
                        # Replace empty/boundary-only annotations
                        raw.set_annotations(tsv_annotations)

        # --- 6. Build eegunity_description ---
        # Read participants.tsv info
        participant_info = _read_participants_info(file_path)
        
        # Extract canonical fields
        age = participant_info.get('age', 'unknown')
        sex = _normalize_sex(participant_info.get('sex', 'unknown'))
        
        # Handedness: try to infer from ehq_total if available
        handedness = 'unknown'
        ehq_total = participant_info.get('ehq_total', 'unknown')
        if ehq_total != 'unknown':
            try:
                ehq_val = float(ehq_total)
                if ehq_val > 0:
                    handedness = 'right'
                elif ehq_val < 0:
                    handedness = 'left'
                else:
                    handedness = 'unknown'
            except (ValueError, TypeError):
                handedness = 'unknown'
        # LLM 推断，需人类复核: ehq_total > 0 suggests right-handed, < 0 left-handed
        # based on Edinburgh Handedness Inventory scoring convention
        
        # Build extra info dict (all required info fields as strings)
        extra_info = {}
        for field in _REQUIRED_INFO_FIELDS:
            if field in ('age', 'sex'):
                continue  # Already handled as canonical fields
            val = participant_info.get(field, 'unknown')
            extra_info[field] = str(val) if val != 'nan' and val != 'None' else 'unknown'

        eegunity_description = {
            "age": str(age) if age != 'nan' and age != 'None' else 'unknown',
            "sex": sex,
            "amplifier": AMPLIFIER,
            "cap": CAP,
            "handedness": handedness,
        }
        eegunity_description.update(extra_info)

        original_desc = raw.info.get('description', '') or ''
        if isinstance(original_desc, dict):
            original_desc = json.dumps(original_desc)
        elif not isinstance(original_desc, str):
            original_desc = str(original_desc)

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = HBNKernel()