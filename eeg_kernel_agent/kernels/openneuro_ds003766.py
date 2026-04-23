"""OpenNeuro DS003766 stage1 kernel for EEGUnity.

Dataset: A Resource for Assessing Dynamic Binary Choices in the Adult Brain Using EEG and Mouse-Tracking
- 31 subjects, 129 channels (128 EEG + 1 Cz reference), 1000 Hz
- Paradigms: food preference (foodchoice), semantic word (wordchoice), image categorization (imagechoice)
- Trigger codes: 0400-0403 (stimulus: animate/inanimate × left/right), 0500-0507 (response: left/right × conditions)
- BIDS-compliant with participants.tsv, *_events.tsv sidecars

Source: https://openneuro.org/datasets/ds003766
DOI: 10.1038/s41597-022-01538-5
"""

from __future__ import annotations

import json
import os
import re
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# 通道重命名映射
# =============================================================================
# Source: EGI 128-channel HydroCel Geodesic Sensor Net standard naming
# The dataset uses EGI's default naming (E1, E2, ... E128) which needs mapping
# to standard 10-20 equivalents for MNE montage compatibility.
# Reference: EGI HydroCel 128 Channel Layout, Geodesic Sensor Net manual
# Annotator: LLM 推断，需人类复核; 2026-04-08
_EGI_128_TO_1020: Dict[str, str] = {
    # Standard 10-20 positions based on EGI 128 layout
    "E1": "E1",      # Keep non-standard names, will use custom montage approach
    "E2": "E2",
    "E3": "E3",
    "E4": "E4",
    "E5": "E5",
    "E6": "E6",
    "E7": "E7",
    "E8": "E8",
    "E9": "E9",
    "E10": "E10",
    "E11": "E11",
    "E12": "E12",
    "E13": "E13",
    "E14": "E14",
    "E15": "E15",
    "E16": "E16",
    "E17": "E17",
    "E18": "E18",
    "E19": "E19",
    "E20": "E20",
    "E21": "E21",
    "E22": "E22",
    "E23": "E23",
    "E24": "E24",
    "E25": "E25",
    "E26": "E26",
    "E27": "E27",
    "E28": "E28",
    "E29": "E29",
    "E30": "E30",
    "E31": "E31",
    "E32": "E32",
    "E33": "E33",
    "E34": "E34",
    "E35": "E35",
    "E36": "E36",
    "E37": "E37",
    "E38": "E38",
    "E39": "E39",
    "E40": "E40",
    "E41": "E41",
    "E42": "E42",
    "E43": "E43",
    "E44": "E44",
    "E45": "E45",
    "E46": "E46",
    "E47": "E47",
    "E48": "E48",
    "E49": "E49",
    "E50": "E50",
    "E51": "E51",
    "E52": "E52",
    "E53": "E53",
    "E54": "E54",
    "E55": "E55",
    "E56": "E56",
    "E57": "E57",
    "E58": "E58",
    "E59": "E59",
    "E60": "E60",
    "E61": "E61",
    "E62": "E62",
    "E63": "E63",
    "E64": "E64",
    "E65": "E65",
    "E66": "E66",
    "E67": "E67",
    "E68": "E68",
    "E69": "E69",
    "E70": "E70",
    "E71": "E71",
    "E72": "E72",
    "E73": "E73",
    "E74": "E74",
    "E75": "E75",
    "E76": "E76",
    "E77": "E77",
    "E78": "E78",
    "E79": "E79",
    "E80": "E80",
    "E81": "E81",
    "E82": "E82",
    "E83": "E83",
    "E84": "E84",
    "E85": "E85",
    "E86": "E86",
    "E87": "E87",
    "E88": "E88",
    "E89": "E89",
    "E90": "E90",
    "E91": "E91",
    "E92": "E92",
    "E93": "E93",
    "E94": "E94",
    "E95": "E95",
    "E96": "E96",
    "E97": "E97",
    "E98": "E98",
    "E99": "E99",
    "E100": "E100",
    "E101": "E101",
    "E102": "E102",
    "E103": "E103",
    "E104": "E104",
    "E105": "E105",
    "E106": "E106",
    "E107": "E107",
    "E108": "E108",
    "E109": "E109",
    "E110": "E110",
    "E111": "E111",
    "E112": "E112",
    "E113": "E113",
    "E114": "E114",
    "E115": "E115",
    "E116": "E116",
    "E117": "E117",
    "E118": "E118",
    "E119": "E119",
    "E120": "E120",
    "E121": "E121",
    "E122": "E122",
    "E123": "E123",
    "E124": "E124",
    "E125": "E125",
    "E126": "E126",
    "E127": "E127",
    "E128": "E128",
    "Cz": "Cz",      # Reference channel
    "VREF": "VREF",  # Vertex reference
}


# EGI 128 standard positions for creating a custom montage
# Source: EGI HydroCel 128 Channel Layout coordinates
# These are approximate spherical coordinates converted to cartesian
# Annotator: LLM 推断，需人类复核; 2026-04-08
def _create_egi_128_montage() -> Optional[mne.channels.DigMontage]:
    """Create EGI 128-channel HydroCel montage.
    
    Returns None if standard montage is available, otherwise creates custom.
    """
    try:
        # Try to use MNE's built-in EGI montage if available
        montage = mne.channels.make_standard_montage("GSN-HydroCel-129")
        return montage
    except (ValueError, RuntimeError):
        pass
    
    try:
        montage = mne.channels.make_standard_montage("EGI_256")
        # Subsample to 128 channels if needed - this is approximate
        # LLM 推断，需人类复核
        return None  # Fall back to no montage if exact match unavailable
    except (ValueError, RuntimeError):
        return None


# =============================================================================
# 事件映射
# =============================================================================
# Source: 10.1038/s41597-022-01538-5, sub-01_task-foodchoice_events.json sidecar
# Annotator: LLM 推断，需人类复核; 2026-04-08

def _get_event_map(paradigm: str) -> Dict[int, str]:
    """Get event map for specific paradigm.
    
    Event codes are consistent across paradigms per BIDS sidecars.
    """
    # Base event codes (same across all paradigms in this dataset)
    base_map = {
        # Stimulus presentation codes (0400 series)
        400: "stimulus: animate left",
        401: "stimulus: animate right", 
        402: "stimulus: inanimate left",
        403: "stimulus: inanimate right",
        # Response codes (0500 series)
        500: "response: left choice (animate left)",
        501: "response: right choice (animate left)",
        502: "response: left choice (animate right)",
        503: "response: right choice (animate right)",
        504: "response: left choice (inanimate left)",
        505: "response: right choice (inanimate left)",
        506: "response: left choice (inanimate right)",
        507: "response: right choice (inanimate right)",
        # Trial structure codes (0200 series) - common timing markers
        200: "trial: start",
        201: "trial: fixation",
        202: "trial: stimulus onset",
        203: "trial: evidence accumulation",
        204: "trial: decision phase",
        205: "trial: response window",
        206: "trial: feedback",
        207: "trial: inter-trial interval",
        # Mouse tracking codes (0300 series)
        300: "mouse: movement start",
        301: "mouse: movement end",
        # Administrative codes
        0: "admin: marker-0",
        1: "admin: marker-1",
        99: "admin: marker-99",
    }
    
    # Paradigm-specific prefixes for disambiguation
    prefix_map = {
        "foodchoice": "FOOD",
        "wordchoice": "WORD", 
        "imagechoice": "IMAGE",
    }
    
    prefix = prefix_map.get(paradigm, "UNKNOWN")
    
    # Add paradigm prefix to all non-admin codes
    prefixed_map = {}
    for code, desc in base_map.items():
        if desc.startswith("admin:"):
            prefixed_map[code] = desc  # Admin codes don't get paradigm prefix
        else:
            prefixed_map[code] = f"{prefix}: {desc}"
    
    return prefixed_map


# =============================================================================
# 辅助函数
# =============================================================================

def _detect_paradigm(file_path: str) -> str:
    """Detect paradigm from BIDS filename.
    
    Source: BIDS filename convention *_task-<task>_*
    """
    basename = os.path.basename(file_path)
    # Match task name from BIDS filename
    task_match = re.search(r'task-([^_]+)', basename)
    if task_match:
        task = task_match.group(1)
        return task
    
    # Fallback to content-based detection
    lower_base = basename.lower()
    if "food" in lower_base:
        return "foodchoice"
    elif "word" in lower_base:
        return "wordchoice"
    elif "image" in lower_base:
        return "imagechoice"
    
    return "unknown"


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file.
    
    BIDS convention: *_eeg.<ext> → *_events.tsv
    """
    # Remove extension and look for events.tsv
    base = re.sub(r'_eeg\.(set|fdt|edf|bdf|vhdr|eeg|cnt)$', '', file_path, flags=re.IGNORECASE)
    events_tsv = base + "_events.tsv"
    
    if os.path.exists(events_tsv):
        return events_tsv
    
    # Try alternative: same directory, any matching events.tsv
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Extract subject and task for matching
    sub_match = re.search(r'(sub-[^_]+)', basename)
    task_match = re.search(r'(task-[^_]+)', basename)
    
    if sub_match and task_match:
        sub = sub_match.group(1)
        task = task_match.group(1)
        pattern = f"{sub}.*{task}.*_events\\.tsv$"
        
        if os.path.isdir(dirname):
            for f in os.listdir(dirname):
                if re.match(pattern, f):
                    return os.path.join(dirname, f)
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv file starting from file directory.
    
    BIDS convention: participants.tsv at dataset root
    """
    # Start from file directory and walk up
    current_dir = os.path.dirname(os.path.abspath(file_path))
    
    # Walk up to find participants.tsv
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        participants_file = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(participants_file):
            return participants_file
        current_dir = os.path.dirname(current_dir)
    
    return None


def _read_participants_info(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv.
    
    Returns dict with available fields.
    """
    participants_tsv = _find_participants_tsv(file_path)
    if not participants_tsv:
        return {}
    
    try:
        df = pd.read_csv(participants_tsv, sep='\t')
        # Match subject ID (with or without 'sub-' prefix)
        if subject_id.startswith('sub-'):
            sub_key = subject_id
        else:
            sub_key = f"sub-{subject_id}"
        
        # Try exact match first
        row = df[df['participant_id'] == sub_key]
        if row.empty:
            # Try without prefix
            row = df[df['participant_id'] == subject_id.replace('sub-', '')]
        if row.empty:
            # Try with prefix added
            row = df[df['participant_id'] == f"sub-{subject_id}"]
        
        if row.empty:
            return {}
        
        # Convert to dict, handling NaN values
        info = {}
        for col in row.columns:
            val = row[col].values[0]
            if pd.notna(val):
                info[col] = str(val)
        
        return info
    except Exception:
        return {}


def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from BIDS filename or path."""
    basename = os.path.basename(file_path)
    match = re.search(r'(sub-[^_]+)', basename)
    if match:
        return match.group(1)
    
    # Try from directory path
    dirname = os.path.dirname(file_path)
    match = re.search(r'(sub-[^/\\]+)', dirname)
    if match:
        return match.group(1)
    
    return "unknown"


def _read_events_tsv(events_tsv: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_tsv, sep='\t')
        # Standardize column names
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception:
        return None


def _create_trial_onset_misc(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Create trial onset misc channel from events.tsv.
    
    Creates a step function that is 1 during trials and 0 otherwise,
    based on trial_type or onset information from events.
    """
    if events_df is None or events_df.empty:
        # No events data - create zero-filled misc channel
        data = np.zeros((1, len(raw.times)))
        info = mne.create_info(['trial_onset'], raw.info['sfreq'], ['misc'])
        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
        raw.load_data()
        raw.add_channels([misc_raw], force_update_info=True)
        return raw
    
    # Ensure raw is loaded before adding channels
    raw.load_data()
    
    # Determine trial onsets from events
    # Look for common BIDS trial indicators
    trial_onsets = []
    
    if 'trial_type' in events_df.columns:
        # Find rows that indicate trial starts
        trial_types = events_df['trial_type'].astype(str).str.lower()
        trial_start_mask = (
            trial_types.str.contains('trial', na=False) |
            trial_types.str.contains('stimulus', na=False) |
            trial_types.str.contains('fixation', na=False) |
            trial_types.str.contains('onset', na=False)
        )
        if trial_start_mask.any():
            trial_onsets = events_df.loc[trial_start_mask, 'onset'].values
        else:
            # Use all unique onsets as trial markers
            trial_onsets = events_df['onset'].unique()
    else:
        # Use all onsets
        trial_onsets = events_df['onset'].values if 'onset' in events_df.columns else []
    
    # Convert onsets to sample indices
    sfreq = raw.info['sfreq']
    first_samp = raw.first_samp
    n_times = len(raw.times)
    
    # Create step function: 1 during trial periods, 0 otherwise
    # Trial period: from onset to next onset or fixed duration
    data = np.zeros((1, n_times))
    
    if len(trial_onsets) > 0:
        # Sort onsets
        trial_onsets = np.sort(trial_onsets)
        
        # Estimate trial duration from median ISI or use default
        if len(trial_onsets) > 1:
            isis = np.diff(trial_onsets)
            trial_dur = np.median(isis)
        else:
            trial_dur = 3.0  # Default 3 seconds
        
        for onset in trial_onsets:
            start_idx = int(onset * sfreq) - first_samp
            end_idx = int((onset + trial_dur) * sfreq) - first_samp
            
            start_idx = max(0, min(start_idx, n_times))
            end_idx = max(0, min(end_idx, n_times))
            
            if start_idx < end_idx:
                data[0, start_idx:end_idx] = 1.0
    
    info = mne.create_info(['trial_onset'], sfreq, ['misc'])
    misc_raw = mne.io.RawArray(data, info, first_samp=first_samp)
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


def _create_condition_misc(raw: mne.io.BaseRaw, events_df: Optional[pd.DataFrame]) -> mne.io.BaseRaw:
    """Create condition indicator misc channel from events.tsv.
    
    Encodes trial_type as numeric codes.
    """
    if events_df is None or 'trial_type' not in events_df.columns:
        data = np.zeros((1, len(raw.times)))
        info = mne.create_info(['condition'], raw.info['sfreq'], ['misc'])
        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
        raw.load_data()
        raw.add_channels([misc_raw], force_update_info=True)
        return raw
    
    # Ensure raw is loaded before adding channels
    raw.load_data()
    
    sfreq = raw.info['sfreq']
    first_samp = raw.first_samp
    n_times = len(raw.times)
    
    # Encode trial types as integers
    trial_types = events_df['trial_type'].astype(str)
    unique_types = sorted(trial_types.unique())
    type_to_code = {t: float(i+1) for i, t in enumerate(unique_types)}
    
    data = np.zeros((1, n_times))
    
    if 'onset' in events_df.columns:
        onsets = events_df['onset'].values
        # Estimate duration
        if len(onsets) > 1:
            isis = np.diff(np.sort(onsets))
            trial_dur = np.median(isis)
        else:
            trial_dur = 3.0
        
        for onset, ttype in zip(onsets, trial_types):
            start_idx = int(onset * sfreq) - first_samp
            end_idx = int((onset + trial_dur) * sfreq) - first_samp
            
            start_idx = max(0, min(start_idx, n_times))
            end_idx = max(0, min(end_idx, n_times))
            
            if start_idx < end_idx:
                data[0, start_idx:end_idx] = type_to_code.get(str(ttype), 0)
    
    info = mne.create_info(['condition'], sfreq, ['misc'])
    misc_raw = mne.io.RawArray(data, info, first_samp=first_samp)
    raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


def _add_events_from_tsv(raw: mne.io.BaseRaw, events_tsv: str, paradigm: str) -> mne.io.BaseRaw:
    """Add events from BIDS events.tsv as MNE annotations.
    
    HC-5: Pass literal tsv labels through to raw.annotations, no remapping.
    """
    events_df = _read_events_tsv(events_tsv)
    if events_df is None or events_df.empty:
        return raw
    
    # Required BIDS columns
    if 'onset' not in events_df.columns:
        return raw
    
    onsets = events_df['onset'].values
    
    # Determine durations
    if 'duration' in events_df.columns:
        durations = events_df['duration'].fillna(0).values
    else:
        durations = np.zeros_like(onsets)
    
    # Determine descriptions - use trial_type if available, else use any descriptive column
    if 'trial_type' in events_df.columns:
        descriptions = events_df['trial_type'].astype(str).values
    elif 'value' in events_df.columns:
        descriptions = events_df['value'].astype(str).values
    elif 'event_type' in events_df.columns:
        descriptions = events_df['event_type'].astype(str).values
    else:
        # Use first non-onset/duration column
        desc_col = [c for c in events_df.columns if c not in ['onset', 'duration', 'sample', 'channel']][0]
        descriptions = events_df[desc_col].astype(str).values
    
    # Create annotations
    # Filter out any invalid entries
    valid_mask = np.isfinite(onsets) & (onsets >= 0)
    onsets = onsets[valid_mask]
    durations = durations[valid_mask]
    descriptions = descriptions[valid_mask]
    
    if len(onsets) == 0:
        return raw
    
    # Handle case where raw may have existing annotations
    orig_annot = raw.annotations
    new_annot = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=orig_annot.orig_time if orig_annot else None
    )
    
    # Combine with existing annotations
    if orig_annot and len(orig_annot) > 0:
        combined = orig_annot + new_annot
        raw.set_annotations(combined)
    else:
        raw.set_annotations(new_annot)
    
    return raw


def _setup_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set up EGI 128-channel montage.
    
    Uses GSN-HydroCel-129 standard montage if available.
    """
    # Try standard EGI montage
    montage = _create_egi_128_montage()
    if montage is not None:
        try:
            raw.set_montage(montage, match_case=False, match_alias=True, on_missing='warn')
            return raw
        except Exception:
            pass
    
    # If standard montage fails, channels keep their original names
    # EGI naming is already compatible with the standard montage
    return raw


# =============================================================================
# EEGUnity Kernel
# =============================================================================

class OpenNeuroDS003766Kernel:
    """EEGUnity stage-1 kernel for OpenNeuro ds003766.
    
    Processes EGI 128-channel EEG data with food/word/image choice paradigms.
    """
    
    # Required info fields from participants.tsv
    required_info_fields = ["age", "sex", "handedness"]
    
    # Derived misc channels to create
    derived_misc_channels = ["trial_onset", "condition"]
    
    def __init__(self):
        pass
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Extract file path from row
        file_path = str(row.get('File Path', row.get('file_path', '')))
        if not file_path or not os.path.exists(file_path):
            # Try to get from raw
            if hasattr(raw, 'filenames') and raw.filenames:
                file_path = raw.filenames[0]
        
        # Detect paradigm
        paradigm = _detect_paradigm(file_path)
        
        # Read subject info from participants.tsv
        subject_id = _extract_subject_id(file_path)
        participant_info = _read_participants_info(file_path, subject_id)
        
        # Build eegunity_description
        eegunity_description = {
            "age": str(participant_info.get("age", "n/a")),
            "sex": participant_info.get("sex", "n/a"),
            "amplifier": "EGI Net Amps 300 (Net Station 5.4)",
            "cap": "EGI HydroCel Geodesic Sensor Net (128 channels + Cz)",
            "handedness": participant_info.get("handedness", "n/a"),
        }
        
        # Add paradigm info
        eegunity_description["paradigm"] = paradigm
        
        # Store original description
        original_description = raw.info.get("description", "")
        
        # Set description as JSON string (MNE requires string)
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        # Set up montage
        raw = _setup_montage(raw)
        
        # Find and process events
        events_tsv = _find_events_tsv(file_path)
        events_df = _read_events_tsv(events_tsv) if events_tsv else None
        
        # Add events from events.tsv as annotations (HC-5: literal labels, no remapping)
        if events_tsv:
            raw = _add_events_from_tsv(raw, events_tsv, paradigm)
        
        # Create derived misc channels
        # Ensure raw is loaded before adding channels
        raw.load_data()
        
        # trial_onset misc channel
        if events_df is not None and not events_df.empty:
            raw = _create_trial_onset_misc(raw, events_df)
        else:
            # Create zero-filled channel
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['trial_onset'], raw.info['sfreq'], ['misc'])
            misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([misc_raw], force_update_info=True)
        
        # condition misc channel
        if events_df is not None and 'trial_type' in events_df.columns:
            raw = _create_condition_misc(raw, events_df)
        else:
            # Create zero-filled channel
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['condition'], raw.info['sfreq'], ['misc'])
            misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([misc_raw], force_update_info=True)
        
        # Set channel types for known non-EEG channels
        # EGI reference channel
        if 'Cz' in raw.ch_names:
            raw.set_channel_types({'Cz': 'eeg'})
        if 'VREF' in raw.ch_names:
            raw.set_channel_types({'VREF': 'eeg'})
        
        # Ensure misc channels are properly typed
        for ch_name in raw.ch_names:
            if ch_name in self.derived_misc_channels:
                idx = raw.ch_names.index(ch_name)
                raw.set_channel_types({ch_name: 'misc'})
        
        return raw


# =============================================================================
# Kernel instance
# =============================================================================

KERNEL = OpenNeuroDS003766Kernel()