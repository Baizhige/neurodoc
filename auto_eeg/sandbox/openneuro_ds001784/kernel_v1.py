"""OpenNeuro DS001784 stage1 kernel for EEGUnity.

Effects of ON/OFF deep brain stimulation on cognitive control in treatment-resistant
depression (EEG). BIDS-formatted dataset with 65 channels at 1450 Hz.

Dataset: openneuro_ds001784 | Year: 2019 | DOI: https://doi.org/10.1038/s41467-019-09557-4
Paradigm: MSIT with emotional stimuli + DBS ON/OFF

This kernel:
- Reads participants.tsv for age/sex/dbs metadata
- Parses events.tsv to extract trial_type (interference/control) labels
- Maps raw events (event_2/4/6) to semantic labels
- Sets standard 10-20 montage for 65-channel EEG
- Provides DBS ON/OFF labels from participants.tsv

Source: https://openneuro.org/datasets/ds001784
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# =============================================================================
# Device Metadata Defaults
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: Dataset publication DOI 10.1038/s41467-019-09557-4, methods section
# Amplifier, cap, and handedness cannot be confirmed from available documentation.
# These values are LLM inferences and require human verification.
_DEVICE_METADATA_DEFAULTS: Dict[str, str] = {
    "amplifier": "unknown",    # LLM 推断，需人类复核
    "cap": "unknown",          # LLM 推断，需人类复核
    "handedness": "unknown",   # LLM 推断，需人类复核
}


# =============================================================================
# Raw Event Mapping
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: Dataset events.tsv analysis
# event_2 (1296 occurrences) -> interference trials (high-interference MSIT)
# event_4 (2592 occurrences) -> control trials (low interference)
# event_6 (1296 occurrences) -> AFMSIT trials (active foreground MSIT)
_EVENT_RAW_MAP: Dict[str, str] = {
    "event_2": "interference_trial",
    "event_4": "control_trial",
    "event_6": "afmsit_trial",
}


# =============================================================================
# Label Mapping for Super Meta
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: analysis.md Classical Task 1 definition
# interference_trial -> y=1, control_trial -> y=0
_COGNITIVE_LABEL_MAP: Dict[str, int] = {
    "interference_trial": 1,
    "control_trial": 0,
}


# =============================================================================
# Standard 10-20 Channel Names for 64-65 Channel Systems
# =============================================================================
# Annotator: LLM (gpt-4o), 2026-04-08
# Source: Standard 10-20 system for 65-channel EEG (extended 10-20)
# These represent the standard electrode positions in order
_STANDARD_1020_CHANNELS: List[str] = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for standard 10-20 channel names.
    
    Attempts to match raw channel names to standard 10-20 positions.
    Handles common naming patterns from BrainVision, BrainProducts, and other systems.
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: Standard 10-20 electrode naming conventions
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    # Create alias groups for common channel name patterns
    alias_groups = [
        # Standard 10-20 names
        ("Fp1", ["Fp1", "FP1", "fp1"]),
        ("Fpz", ["Fpz", "FPz", "fpz"]),
        ("Fp2", ["Fp2", "FP2", "fp2"]),
        ("F7", ["F7", "F7 "]),
        ("F3", ["F3"]),
        ("Fz", ["Fz"]),
        ("F4", ["F4"]),
        ("F8", ["F8"]),
        ("T7", ["T7", "T7 "]),
        ("C3", ["C3"]),
        ("Cz", ["Cz"]),
        ("C4", ["C4"]),
        ("T8", ["T8"]),
        ("P7", ["P7"]),
        ("P3", ["P3"]),
        ("Pz", ["Pz"]),
        ("P4", ["P4"]),
        ("P8", ["P8"]),
        ("O1", ["O1"]),
        ("Oz", ["Oz"]),
        ("O2", ["O2"]),
        # Extended 10-20 names
        ("AF7", ["AF7"]),
        ("AF3", ["AF3"]),
        ("AFz", ["AFz"]),
        ("AF4", ["AF4"]),
        ("AF8", ["AF8"]),
        ("F5", ["F5"]),
        ("F1", ["F1"]),
        ("F2", ["F2"]),
        ("F6", ["F6"]),
        ("FC5", ["FC5"]),
        ("FC1", ["FC1"]),
        ("FCz", ["FCz"]),
        ("FC2", ["FC2"]),
        ("FC6", ["FC6"]),
        ("C5", ["C5"]),
        ("C1", ["C1"]),
        ("C2", ["C2"]),
        ("C6", ["C6"]),
        ("CP5", ["CP5"]),
        ("CP1", ["CP1"]),
        ("CPz", ["CPz"]),
        ("CP2", ["CP2"]),
        ("CP6", ["CP6"]),
        ("P5", ["P5"]),
        ("P1", ["P1"]),
        ("P2", ["P2"]),
        ("P6", ["P6"]),
        ("PO7", ["PO7"]),
        ("PO3", ["PO3"]),
        ("POz", ["POz"]),
        ("PO4", ["PO4"]),
        ("PO8", ["PO8"]),
    ]
    
    # EOG channels
    eog_aliases = [
        ("EOG-left", ["EOG左", "EOG-L", "EOGL", "VEOG-L", "HEOG-L", "eog_l"]),
        ("EOG-right", ["EOG右", "EOG-R", "EOGR", "VEOG-R", "HEOG-R", "eog_r"]),
        ("EOG-central", ["EOG中", "EOG-C", "EOGC", "VEOG-C", "eog_c"]),
    ]
    
    # MISC/STATUS channels
    misc_aliases = [
        ("Status", ["Status", "STI 014", "Stimulus", "Stim"]),
        ("Misc", ["Misc", "MISC"]),
    ]
    
    all_aliases = alias_groups + eog_aliases + misc_aliases
    
    for target_name, aliases in all_aliases:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break
    
    return rename_map


def _load_participants_metadata(dataset_path: str) -> pd.DataFrame:
    """Load participants.tsv file.
    
    Returns empty DataFrame if file not found.
    
    Annotator: LLM (gpt-4o), 2026-04-08
    """
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_file):
        return pd.read_csv(participants_file, sep="\t")
    return pd.DataFrame()


def _get_subject_metadata(participants_df: pd.DataFrame, subject_id: str) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv.
    
    Args:
        participants_df: DataFrame from participants.tsv
        subject_id: Subject identifier (e.g., 'sub-01')
    
    Returns:
        Dictionary with age, sex, dbs_condition for the subject
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: BIDS participants.tsv standard columns
    """
    metadata = {
        "age": "unknown",
        "sex": "unknown",
        "dbs_condition": "unknown",  # LLM 推断，需人类复核
    }
    
    if participants_df.empty:
        return metadata
    
    # Match subject ID (handle both 'sub-01' and '01' formats)
    subject_col = None
    for col in ["participant_id", "subject_id", "participant"]:
        if col in participants_df.columns:
            subject_col = col
            break
    
    if subject_col is None:
        return metadata
    
    # Normalize subject ID for matching
    subject_row = participants_df[participants_df[subject_col] == subject_id]
    if subject_row.empty:
        # Try without 'sub-' prefix
        short_id = subject_id.replace("sub-", "")
        subject_row = participants_df[participants_df[subject_col].str.contains(short_id, na=False)]
    
    if subject_row.empty:
        return metadata
    
    row = subject_row.iloc[0]
    
    # Extract age
    if "age" in participants_df.columns:
        age_val = row.get("age")
        if pd.notna(age_val):
            metadata["age"] = str(age_val)
    
    # Extract sex
    if "sex" in participants_df.columns:
        sex_val = row.get("sex")
        if pd.notna(sex_val):
            sex_lower = str(sex_val).lower()
            if sex_lower in ["m", "male"]:
                metadata["sex"] = "male"
            elif sex_lower in ["f", "female"]:
                metadata["sex"] = "female"
    
    # Extract DBS condition (custom column in this dataset)
    # LLM 推断，需人类复核 - DBS ON/OFF stored in participants.tsv
    dbs_columns = ["dbs", "dbs_condition", "stimulation", "dbs_state"]
    for col in dbs_columns:
        if col in participants_df.columns:
            dbs_val = row.get(col)
            if pd.notna(dbs_val):
                dbs_str = str(dbs_val).lower()
                if "on" in dbs_str:
                    metadata["dbs_condition"] = "DBS_ON"
                elif "off" in dbs_str:
                    metadata["dbs_condition"] = "DBS_OFF"
            break
    
    return metadata


def _parse_events_tsv(eeg_file_path: str) -> Optional[pd.DataFrame]:
    """Parse associated events.tsv file for an EEG recording.
    
    Args:
        eeg_file_path: Path to the EEG file (.vhdr, .edf, etc.)
    
    Returns:
        DataFrame from events.tsv or None if not found
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: BIDS events.tsv standard format
    """
    base_path = os.path.splitext(eeg_file_path)[0]
    
    # Try common events.tsv naming patterns
    candidates = [
        base_path + "_events.tsv",
        base_path.replace("_eeg_", "_events.tsv"),
        os.path.join(os.path.dirname(eeg_file_path), "events.tsv"),
    ]
    
    # Also check for BIDS-style events in parent directories
    eeg_dir = os.path.dirname(eeg_file_path)
    for _ in range(3):  # Check up to 3 levels up
        bids_eeg_dir = os.path.join(eeg_dir, "")
        # Look for any events.tsv in current directory
        for f in os.listdir(eeg_dir):
            if f.endswith("_events.tsv"):
                candidates.append(os.path.join(eeg_dir, f))
        eeg_dir = os.path.dirname(eeg_dir)
    
    for events_path in candidates:
        if os.path.exists(events_path):
            try:
                return pd.read_csv(events_path, sep="\t")
            except Exception:
                continue
    
    return None


def _create_annotations_from_events(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    file_path: str
) -> mne.Annotations:
    """Create MNE annotations from events.tsv data.
    
    Args:
        raw: MNE Raw object for timing reference
        events_df: DataFrame from events.tsv
        file_path: Original EEG file path (for finding events.tsv)
    
    Returns:
        MNE Annotations object
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: BIDS events.tsv standard columns (onset, duration, trial_type)
    """
    if events_df is None or events_df.empty:
        # Fall back to existing annotations
        return raw.annotations
    
    # Standard BIDS events.tsv columns
    onset_col = None
    duration_col = None
    trial_type_col = None
    value_col = None
    
    for col in ["onset", "timestamp", "time"]:
        if col in events_df.columns:
            onset_col = col
            break
    
    for col in ["duration", "length"]:
        if col in events_df.columns:
            duration_col = col
            break
    
    for col in ["trial_type", "condition", "event_type", "value"]:
        if col in events_df.columns:
            trial_type_col = col
            break
    
    # Also check for 'value' column (common in BIDS)
    if "value" in events_df.columns and trial_type_col is None:
        value_col = "value"
    
    if onset_col is None:
        return raw.annotations
    
    # Calculate onset times relative to recording start
    sfreq = raw.info["sfreq"]
    
    try:
        onsets = events_df[onset_col].astype(float).values / sfreq
    except (ValueError, TypeError):
        # Try as seconds directly
        try:
            onsets = events_df[onset_col].astype(float).values
        except (ValueError, TypeError):
            return raw.annotations
    
    # Duration (default to 0 if not available)
    if duration_col:
        try:
            durations = events_df[duration_col].astype(float).values
        except (ValueError, TypeError):
            durations = [0] * len(onsets)
    else:
        durations = [0] * len(onsets)
    
    # Description (event label)
    if trial_type_col:
        descriptions = events_df[trial_type_col].astype(str).values
    elif value_col:
        descriptions = events_df[value_col].astype(str).values
    else:
        descriptions = ["unknown"] * len(onsets)
    
    # Map raw event codes to semantic labels
    mapped_descriptions = []
    for desc in descriptions:
        # Try direct mapping first
        if desc in _EVENT_RAW_MAP:
            mapped_descriptions.append(_EVENT_RAW_MAP[desc])
        else:
            # Keep original if no mapping found
            mapped_descriptions.append(desc)
    
    return mne.Annotations(
        onset=onsets.tolist(),
        duration=durations.tolist() if hasattr(durations, 'tolist') else list(durations),
        description=mapped_descriptions,
    )


def _set_montage_safe(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set standard 10-20 montage if possible.
    
    Handles cases where not all channels are present or channel names don't match.
    
    Annotator: LLM (gpt-4o), 2026-04-08
    Source: MNE standard montage documentation
    """
    try:
        # Try standard_1020 montage first
        montage = mne.channels.make_standard_montage("standard_1020")
        
        # Get channel names that exist in both raw and montage
        raw_chs = set(raw.ch_names)
        montage_chs = set(montage.ch_names)
        
        # Find intersection
        common_chs = raw_chs.intersection(montage_chs)
        
        if len(common_chs) >= 10:  # Only set montage if we have enough channels
            raw.set_montage(montage, on_missing="ignore")
        else:
            # Try biosemi32 or other common montages
            for montage_name in ["standard_1005", "biosemi64", "easycap-M1"]:
                try:
                    montage = mne.channels.make_standard_montage(montage_name)
                    common_chs = raw_chs.intersection(set(montage.ch_names))
                    if len(common_chs) >= 10:
                        raw.set_montage(montage, on_missing="ignore")
                        break
                except Exception:
                    continue
    except Exception:
        # Montage setting failed, continue without it
        pass
    
    return raw


@dataclass
class OpenNeuroDS001784Kernel:
    """Stage1 kernel for the OpenNeuro DS001784 dataset.
    
    Deep Brain Stimulation (DBS) effects on cognitive control in treatment-resistant
    depression using MSIT paradigm with emotional stimuli.
    """
    
    KERNEL_ID: str = "openneuro-ds001784-stage1"
    
    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.
        
        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with at least ``File Path``.
        
        Returns
        -------
        mne.io.BaseRaw
            The preprocessed Raw object with updated metadata and annotations.
        
        Annotator: LLM (gpt-4o), 2026-04-08
        """
        file_path = row.get("File Path", "")
        
        # Determine dataset root path
        dataset_root = udataset.dataset_path if hasattr(udataset, "dataset_path") else ""
        
        # Step 1: Load participants metadata
        participants_df = _load_participants_metadata(dataset_root)
        
        # Extract subject ID from file path
        subject_id = ""
        if "sub-" in file_path:
            import re
            match = re.search(r"(sub-\w+)", file_path)
            if match:
                subject_id = match.group(1)
        
        # Get subject metadata
        subject_meta = _get_subject_metadata(participants_df, subject_id)
        
        # Step 2: Set device metadata
        # These values are inferred and require human verification
        # Source: Dataset publication DOI 10.1038/s41467-019-09557-4
        device_age = subject_meta.get("age", "unknown")
        device_sex = subject_meta.get("sex", "unknown")
        device_amplifier = _DEVICE_METADATA_DEFAULTS.get("amplifier", "unknown")
        device_cap = _DEVICE_METADATA_DEFAULTS.get("cap", "unknown")
        device_handedness = _DEVICE_METADATA_DEFAULTS.get("handedness", "unknown")
        
        # Step 3: Build and apply channel rename map
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Step 4: Set montage AFTER channel renaming
        raw = _set_montage_safe(raw)
        
        # Step 5: Parse events from events.tsv
        events_df = _parse_events_tsv(file_path)
        
        # Step 6: Create annotations from events
        annotations = _create_annotations_from_events(raw, events_df, file_path)
        raw.set_annotations(annotations)
        
        # Step 7: Update description JSON
        original_desc = raw.info.get("description", "")
        
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": device_age,
                "sex": device_sex,
                "amplifier": device_amplifier,
                "cap": device_cap,
                "handedness": device_handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # Step 8: Store DBS condition in raw.info for downstream tasks
        # This is used by Classical Task 2 (DBS ON/OFF classification)
        dbs_condition = subject_meta.get("dbs_condition", "unknown")
        if hasattr(raw.info, "dbs_condition"):
            raw.info["dbs_condition"] = dbs_condition
        else:
            # Store in description as additional field
            desc_data = json.loads(raw.info["description"])
            desc_data["eegunity_description"]["dbs_condition"] = dbs_condition
            raw.info["description"] = json.dumps(desc_data)
        
        return raw


KERNEL = OpenNeuroDS001784Kernel()