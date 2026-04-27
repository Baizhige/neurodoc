"""openneuro_ds004367 stage1 kernel for EEGUnity.

Meta-RDK: Raw EEG from visual motion discrimination task with metacognitive confidence assessment.
Source: https://openneuro.org/datasets/ds004367
DOI: https://doi.org/10.1101/2022.10.19.22281249

Paradigm: Visual random dot kinematogram (RDK) motion discrimination with left/right
direction decisions followed by metacognitive confidence rating using visual analog scale.

This dataset is BIDS-formatted with .set files (EEGLAB). The files load via MNE's
read_raw_eeglab but may not carry embedded events; we derive annotations from
sibling *_events.tsv files when present.

Event Structure:
  - Block onset markers: 25984, 26112, 26496, 26624, 27008, 27136
  - Post-onset: 3072
  - Pre-stimulus: 3456
  - Stimulus/response: 3584, 3840, 3968, 4096
  - Termination: 4480

Recording: 68 channels including EEG/EOG/ECG, 1200 Hz sampling rate, BioSemi system.
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


# ============================================================================
# Required info fields from participants.tsv
# ============================================================================
_REQUIRED_INFO_FIELDS: List[str] = ["Age", "Gender", "Group"]

# ============================================================================
# Required native misc channels (already physical channels, ensure type='misc')
# ============================================================================
_REQUIRED_NATIVE_MISC: List[str] = []

# ============================================================================
# Derived misc channels to create
# ============================================================================
_DERIVED_MISC_CHANNELS: List[str] = []

# ============================================================================
# Subject metadata fallback
# Source: Paper DOI 10.1101/2022.10.19.22281249 - "22–45 years" age range
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
# ============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"{i:02d}": {"sex": "unknown", "age": "22-45", "handedness": "unknown"}
    for i in range(1, 43)
}


# ============================================================================
# Channel rename map: BioSemi 64+4 convention -> standard names
# Source: BioSemi 64-channel extended 10-20 layout with 4 auxiliary channels
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
# ============================================================================
_BIOSEMI_64_RENAME: Dict[str, str] = {
    # Standard BioSemi 64 names if present
    "A1": "Fp1",
    "A2": "AF7",
    "A3": "AF3",
    "A4": "F1",
    "A5": "F3",
    "A6": "F5",
    "A7": "F7",
    "A8": "FT7",
    "A9": "FC5",
    "A10": "FC3",
    "A11": "FC1",
    "A12": "C1",
    "A13": "C3",
    "A14": "C5",
    "A15": "T7",
    "A16": "TP7",
    "A17": "CP5",
    "A18": "CP3",
    "A19": "CP1",
    "A20": "P1",
    "A21": "P3",
    "A22": "P5",
    "A23": "P7",
    "A24": "P9",
    "A25": "PO7",
    "A26": "PO3",
    "A27": "O1",
    "A28": "Iz",
    "A29": "Oz",
    "A30": "POz",
    "A31": "Pz",
    "A32": "CPz",
    "B1": "Fpz",
    "B2": "Fp2",
    "B3": "AF8",
    "B4": "AF4",
    "B5": "AFz",
    "B6": "Fz",
    "B7": "F2",
    "B8": "F4",
    "B9": "F6",
    "B10": "F8",
    "B11": "FT8",
    "B12": "FC6",
    "B13": "FC4",
    "B14": "FC2",
    "B15": "FCz",
    "B16": "Cz",
    "B17": "C2",
    "B18": "C4",
    "B19": "C6",
    "B20": "T8",
    "B21": "TP8",
    "B22": "CP6",
    "B23": "CP4",
    "B24": "CP2",
    "B25": "P2",
    "B26": "P4",
    "B27": "P6",
    "B28": "P8",
    "B29": "P10",
    "B30": "PO8",
    "B31": "PO4",
    "B32": "O2",
    # Common alternative naming
    "EXG1": "EXG1",
    "EXG2": "EXG2",
    "EXG3": "EXG3",
    "EXG4": "EXG4",
    "EXG5": "EXG5",
    "EXG6": "EXG6",
    "EXG7": "EXG7",
    "EXG8": "EXG8",
    # EOG/ECG common labels
    "HEOGL": "HEOGL",
    "HEOGR": "HEOGR",
    "VEOGU": "VEOGU",
    "VEOGL": "VEOGL",
}

# Standard 64 channel names in order for montage
_STANDARD_64: List[str] = [
    "Fp1", "Fpz", "Fp2", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8", "O1", "Oz", "O2",
    "Iz", "P9", "P10",
]


def _get_subject_id_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    match = re.search(r'sub-([A-Za-z0-9]+)', file_path)
    if match:
        return match.group(1)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for a given EEG file."""
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    
    # Try to construct events filename from BIDS pattern
    if "_eeg." in basename:
        # Replace _eeg.ext with _events.tsv
        events_name = re.sub(r'_eeg\.[^.]+$', '_events.tsv', basename)
        candidate = os.path.join(dirname, events_name)
        if os.path.exists(candidate):
            return candidate
    
    # Look for any events.tsv in same directory matching subject
    if os.path.isdir(dirname):
        sub_prefix = None
        match = re.search(r'(sub-[A-Za-z0-9]+)', basename)
        if match:
            sub_prefix = match.group(1)
        for f in os.listdir(dirname):
            if f.endswith("_events.tsv"):
                if sub_prefix is None or f.startswith(sub_prefix):
                    return os.path.join(dirname, f)
    
    # Fallback: try direct path replacements
    base = file_path.replace(".set", "").replace(".fdt", "")
    candidates = [
        base.replace("_eeg.set", "_events.tsv"),
        base.replace("_eeg", "_events") + ".tsv" if not base.endswith("_eeg") else base + "_events.tsv",
        base.rsplit("_", 1)[0] + "_events.tsv",
    ]
    
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current = os.path.dirname(file_path)
    for _ in range(5):  # Search up to 5 levels
        candidate = os.path.join(current, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def _read_participants_info(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info: Dict[str, str] = {}
    participants_tsv = _find_participants_tsv(file_path)
    if participants_tsv is None:
        return info
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        # Find subject column
        sub_col = "participant_id"
        if sub_col not in df.columns:
            for col in df.columns:
                if "participant" in col.lower() or "subject" in col.lower():
                    sub_col = col
                    break
        
        # Normalize subject ID for matching
        subject_patterns = [
            f"sub-{subject_id}",
            subject_id,
            f"{int(subject_id):02d}" if subject_id.isdigit() else subject_id,
        ]
        
        for pattern in subject_patterns:
            row = df[df[sub_col] == pattern]
            if len(row) == 1:
                for field in _REQUIRED_INFO_FIELDS:
                    if field in df.columns:
                        val = row[field].values[0]
                        if pd.isna(val):
                            info[field] = "unknown"
                        else:
                            info[field] = str(val)
                    else:
                        info[field] = "unknown"
                return info
        
        # Subject not found
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
            
    except Exception:
        for field in _REQUIRED_INFO_FIELDS:
            info[field] = "unknown"
    
    return info


def _derive_annotations_from_events_tsv(raw: mne.io.BaseRaw, events_tsv_path: str) -> mne.Annotations:
    """Create MNE Annotations from BIDS events.tsv file."""
    df = pd.read_csv(events_tsv_path, sep="\t")
    
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in df.iterrows():
        onset = float(row["onset"])
        duration = float(row.get("duration", 0)) if not pd.isna(row.get("duration", 0)) else 0.0
        
        # Use 'value' column for description (contains the numeric trigger codes)
        # Per BIDS and evidence, 'value' column carries the distinguishable trigger labels
        desc = None
        if "value" in df.columns:
            val = row["value"]
            if not pd.isna(val):
                # Preserve as string without remapping (HC-5 compliance)
                desc = str(int(val)) if isinstance(val, (int, float)) and val == int(val) else str(val)
        if desc is None and "trial_type" in df.columns:
            val = row["trial_type"]
            if not pd.isna(val):
                desc = str(val)
        if desc is None:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    # Filter to valid time range
    max_time = raw.times[-1] if len(raw.times) > 0 else float('inf')
    valid = [(o, d, desc) for o, d, desc in zip(onsets, durations, descriptions) 
             if o >= 0 and o < max_time]
    
    if not valid:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets, durations, descriptions = zip(*valid)
    
    return mne.Annotations(
        onset=list(onsets),
        duration=list(durations),
        description=list(descriptions),
        orig_time=raw.info["meas_date"],
    )


@dataclass
class OpenNeuroDS004367Kernel:
    """Stage1 kernel for OpenNeuro ds004367 (Meta-RDK)."""

    KERNEL_ID: str = "openneuro-ds004367-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # =====================================================================
        # 1. Channel renaming to standard 10-20
        # =====================================================================
        rename_map: Dict[str, str] = {}
        for old_name, new_name in _BIOSEMI_64_RENAME.items():
            if old_name in raw.ch_names and old_name != new_name:
                # Only rename if target not already occupied
                if new_name not in raw.ch_names or old_name == new_name:
                    rename_map[old_name] = new_name
        
        if rename_map:
            raw = raw.rename_channels(rename_map)

        # =====================================================================
        # 2. Set channel types for non-EEG channels
        # =====================================================================
        channel_types: Dict[str, str] = {}
        for ch in raw.ch_names:
            uch = ch.upper()
            if any(x in uch for x in ["EOG", "HEOG", "VEOG", "EXG"]):
                if "HEOG" in uch or "VEOG" in uch or "EOG" in uch:
                    channel_types[ch] = "eog"
                elif "EXG" in uch:
                    # EXG1-EXG8: typically EOG/ECG/misc
                    channel_types[ch] = "misc"
            elif any(x in uch for x in ["ECG", "EKG"]):
                channel_types[ch] = "ecg"
        
        if channel_types:
            raw = raw.set_channel_types(channel_types)

        # =====================================================================
        # 3. Set EEG channel type for remaining channels
        # =====================================================================
        for ch in raw.ch_names:
            if ch not in channel_types:
                if raw.info["chs"][raw.ch_names.index(ch)]["kind"] != mne.io.constants.FIFF.FIFFV_EEG_CH:
                    # Force to EEG if not already set
                    pass  # Will be handled by set_channel_types
        # Set all unset channels to EEG
        eeg_channels = [ch for ch in raw.ch_names if ch not in channel_types]
        if eeg_channels:
            eeg_map = {ch: "eeg" for ch in eeg_channels}
            raw = raw.set_channel_types(eeg_map)

        # =====================================================================
        # 4. Set montage
        # =====================================================================
        try:
            montage = mne.channels.make_standard_montage("biosemi64")
            # Pick only channels that exist in raw
            montage_ch_names = [ch for ch in montage.ch_names if ch in raw.ch_names]
            if montage_ch_names:
                montage = montage.copy()
                # Keep only matching channels
                inds = [montage.ch_names.index(ch) for ch in montage_ch_names]
                montage = mne.channels.DigMontage(
                    ch_names=[montage.ch_names[i] for i in inds],
                    dig=[montage.dig[i] for i in inds] if hasattr(montage, 'dig') else None,
                )
                raw = raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass

        # =====================================================================
        # 5. Load annotations from sibling events.tsv (CRITICAL FIX)
        # =====================================================================
        # EEGLAB .set files in this dataset have empty event fields
        # Events MUST come from the sibling *_events.tsv files
        events_tsv = _find_events_tsv(file_path)
        if events_tsv and os.path.exists(events_tsv):
            annotations = _derive_annotations_from_events_tsv(raw, events_tsv)
            if len(annotations) > 0:
                raw = raw.set_annotations(annotations)
        # If no events.tsv found, raw.annotations remains as loaded (likely empty for .set)

        # =====================================================================
        # 6. Subject metadata
        # =====================================================================
        subject_id = _get_subject_id_from_path(file_path)
        if subject_id is None:
            subject_id = "unknown"
        
        participants_info = _read_participants_info(file_path, subject_id)
        
        # Build subject info
        subject_info: Dict[str, Any] = {}
        if "Age" in participants_info and participants_info["Age"] != "unknown":
            try:
                subject_info["age"] = int(float(participants_info["Age"]))
            except (ValueError, TypeError):
                subject_info["age"] = None
        else:
            # Fallback to paper metadata
            subject_info["age"] = None
        
        if "Gender" in participants_info and participants_info["Gender"] != "unknown":
            sex_map = {"M": 1, "F": 2, "m": 1, "f": 2, "male": 1, "female": 2, "Male": 1, "Female": 2}
            subject_info["sex"] = sex_map.get(participants_info["Gender"], 0)
        else:
            subject_info["sex"] = 0
        
        if subject_info:
            raw.info["subject_info"] = subject_info

        # =====================================================================
        # 7. Line frequency
        # =====================================================================
        raw.info["line_freq"] = 50  # Europe/Netherlands (BioSemi)

        # =====================================================================
        # 8. eegunity_description
        # =====================================================================
        description = {
            "dataset": "openneuro_ds004367",
            "task": "Meta-RDK",
            "paradigm": "visual motion discrimination with metacognitive confidence",
            "sampling_rate_hz": raw.info["sfreq"],
            "n_channels": len(raw.ch_names),
            "n_eeg_channels": len([ch for ch in raw.ch_names if raw.info["chs"][raw.ch_names.index(ch)]["kind"] == mne.io.constants.FIFF.FIFFV_EEG_CH]),
            "recording_system": "BioSemi",
            "reference": "CMS/DRL (BioSemi common mode sense / driven right leg)",
            "has_annotations": raw.annotations is not None and len(raw.annotations) > 0,
            "n_annotations": len(raw.annotations) if raw.annotations is not None else 0,
            "events_source": "events.tsv" if (events_tsv and os.path.exists(events_tsv)) else "raw_file",
            "subject_id": subject_id,
        }
        
        # Store in raw.info["description"] as JSON
        raw.info["description"] = json.dumps(description)

        return raw


KERNEL = OpenNeuroDS004367Kernel()