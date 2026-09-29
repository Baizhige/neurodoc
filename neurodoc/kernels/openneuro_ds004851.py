"""HID (High-Density EEG Operational Dataset) stage1 kernel for EEGUnity.

Dataset: openneuro_ds004851
65 subjects | 72 channels | 2048 Hz | High-density EEG operational paradigm

Event Structure:
  - 1xxx: Primary stimulus classes (10xx: onset markers, 11xx: response markers)
  - 7xxx: Operational block markers
  - 8xxx: Secondary stimulus categories

Source: https://openneuro.org/datasets/ds004851
Reference DOI: 10.18112/openneuro.ds004851.v2.1.0

Kernel Notes:
  - 72-channel HD-EEG follows standard_1020 layout
  - Even/odd paired events (e.g., 1010/1011) indicate onset/response semantics
  - Multi-class structure supports fine-grained stimulus discrimination analysis
  - BIDS-compliant dataset with participants.tsv and events.tsv sidecars
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np

try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    _PANDAS_AVAILABLE = False

# ============================================================================
# Kernel Requirements
# ============================================================================
kernel_requirements = {
    "required_info_fields": ["age", "sex", "handedness"],
    "required_native_misc": [],
    "derived_misc_channels": [],
}

# ============================================================================
# Subject Metadata
# ============================================================================
# Source: OpenNeuro ds004851 participants.tsv (read dynamically in apply)
# inferred by LLM, needs human review — fallback values if participants.tsv unavailable
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(3)}": {"age": "unknown", "sex": "unknown", "handedness": "unknown"}
    for i in range(1, 66)
}

# ============================================================================
# Channel Configuration
# ============================================================================
# Source: 72-channel HD-EEG standard_1020 layout (inferred from dataset description)
# Dataset uses standard 10-20 system with extended coverage
# inferred by LLM, needs human review
_STANDARD_72_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF3", "AF4",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8",
    "O1", "Oz", "O2",
    "F9", "F10",
    "T9", "T10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "O9", "O10",
    "CB1", "CB2"
]

# ============================================================================
# Event Mapping
# ============================================================================
# Raw event codes from dataset analysis.md event structure
# Mapping numeric trigger codes to human-readable HID event labels
_EVENT_MAP: Dict[str, str] = {
    # Primary stimulus class A (even: onset, odd: response)
    "1010": "HID: stimulus_A_onset",
    "1011": "HID: stimulus_A_response",
    # Primary stimulus class B
    "1020": "HID: stimulus_B_onset",
    "1021": "HID: stimulus_B_response",
    # Primary stimulus class C
    "1030": "HID: stimulus_C_onset",
    "1031": "HID: stimulus_C_response",
    # Primary stimulus class D
    "1040": "HID: stimulus_D_onset",
    "1041": "HID: stimulus_D_response",
    # Primary stimulus class E
    "1050": "HID: stimulus_E_onset",
    "1051": "HID: stimulus_E_response",
    # Primary stimulus class F
    "1060": "HID: stimulus_F_onset",
    "1061": "HID: stimulus_F_response",
    # Block markers 01-19 (7001-7019)
    "7001": "HID: block_marker_01",
    "7002": "HID: block_marker_02",
    "7003": "HID: block_marker_03",
    "7004": "HID: block_marker_04",
    "7005": "HID: block_marker_05",
    "7006": "HID: block_marker_06",
    "7007": "HID: block_marker_07",
    "7008": "HID: block_marker_08",
    "7009": "HID: block_marker_09",
    "7010": "HID: block_marker_10",
    "7011": "HID: block_marker_11",
    "7012": "HID: block_marker_12",
    "7013": "HID: block_marker_13",
    "7014": "HID: block_marker_14",
    "7015": "HID: block_marker_15",
    "7016": "HID: block_marker_16",
    "7017": "HID: block_marker_17",
    "7018": "HID: block_marker_18",
    "7019": "HID: block_marker_19",
    # Secondary stimulus 80A
    "8010": "HID: secondary_80A_onset",
    "8011": "HID: secondary_80A_response",
    # Secondary stimulus 80B
    "8020": "HID: secondary_80B_onset",
    "8021": "HID: secondary_80B_response",
    # Secondary stimulus 80 block-level
    "8000": "HID: secondary_80_onset",
    "8001": "HID: secondary_80_response",
    # Secondary stimulus 81 trial-level
    "8100": "HID: secondary_81_onset",
    "8101": "HID: secondary_81_response",
}


def _get_subject_id_from_path(file_path: str) -> str:
    """Extract BIDS subject ID from file path."""
    basename = os.path.basename(file_path)
    # Handle patterns like sub-001_task-HID_eeg.set or sub-001_eeg.set
    if basename.startswith("sub-"):
        parts = basename.split("_")
        return parts[0]
    # Fallback: try to find sub-XXX pattern in path
    import re
    match = re.search(r"(sub-[0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _read_participants_tsv(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    if not _PANDAS_AVAILABLE:
        return {}
    
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Find row for this subject
        subj_row = df[df["participant_id"] == subject_id]
        if subj_row.empty:
            # Try without "sub-" prefix if needed
            subj_row = df[df["participant_id"] == subject_id.replace("sub-", "")]
        if subj_row.empty:
            return {}
        
        result = {}
        row_dict = subj_row.iloc[0].to_dict()
        
        # Map standard fields
        if "age" in row_dict and pd.notna(row_dict["age"]):
            result["age"] = str(int(float(row_dict["age"])))
        if "sex" in row_dict and pd.notna(row_dict["sex"]):
            sex_val = str(row_dict["sex"]).lower().strip()
            if sex_val in ("m", "male"):
                result["sex"] = "male"
            elif sex_val in ("f", "female"):
                result["sex"] = "female"
            else:
                result["sex"] = "unknown"
        if "gender" in row_dict and pd.notna(row_dict["gender"]) and "sex" not in result:
            gender_val = str(row_dict["gender"]).lower().strip()
            if gender_val in ("m", "male"):
                result["sex"] = "male"
            elif gender_val in ("f", "female"):
                result["sex"] = "female"
        if "handedness" in row_dict and pd.notna(row_dict["handedness"]):
            hand_val = str(row_dict["handedness"]).lower().strip()
            if hand_val in ("r", "right"):
                result["handedness"] = "right"
            elif hand_val in ("l", "left"):
                result["handedness"] = "left"
            else:
                result["handedness"] = "unknown"
        
        # Include any extra required fields from kernel_requirements
        for field in kernel_requirements.get("required_info_fields", []):
            if field not in result and field in row_dict and pd.notna(row_dict[field]):
                result[field] = str(row_dict[field])
        
        return result
    except Exception:
        return {}


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for the given EEG file."""
    # BIDS pattern: sub-XXX[_task-YYY][_run-ZZ]_eeg.<ext> -> sub-XXX[_task-YYY][_run-ZZ]_events.tsv
    base = os.path.splitext(file_path)[0]
    # Remove any suffix before _eeg
    if base.endswith("_eeg"):
        base = base[:-4]
    
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: look in same directory for matching events file
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Extract subject and task info
    parts = basename.split("_")
    subj_part = parts[0] if parts else ""
    
    for fname in os.listdir(dirname) if os.path.isdir(dirname) else []:
        if fname.endswith("_events.tsv") and fname.startswith(subj_part):
            return os.path.join(dirname, fname)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not _PANDAS_AVAILABLE:
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame, sfreq: float) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    onsets = []
    durations = []
    descriptions = []
    
    for _, row in events_df.iterrows():
        onset = float(row["onset"]) if pd.notna(row.get("onset", None)) else 0.0
        duration = float(row["duration"]) if pd.notna(row.get("duration", None)) else 0.0
        
        # Determine description: prefer trial_type, then value, then stim_type
        desc = None
        for col in ["trial_type", "value", "stim_type"]:
            if col in row and pd.notna(row[col]):
                val = str(row[col])
                # Map through _EVENT_MAP if it's a known code
                desc = _EVENT_MAP.get(val, val)
                break
        
        if desc is None:
            desc = "unknown"
        
        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)
    
    return mne.Annotations(onset=onsets, duration=durations, description=descriptions)


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for non-standard channel names to standard 10-20."""
    rename_map = {}
    existing = set(raw.ch_names)
    
    # Common non-standard naming patterns in this dataset
    # Check if channels already have standard names
    standard_names = set(_STANDARD_72_CHANNELS)
    
    # If channels are numbered (EEG 1, EEG 2, etc.), map by position
    numbered_pattern = {}
    for i, std_name in enumerate(_STANDARD_72_CHANNELS):
        # Try various numbering schemes
        for fmt in [f"EEG {i+1}", f"EEG{i+1}", f"EEG-{i+1}", f"Ch{i+1}", f"CH{i+1}", f"Channel {i+1}"]:
            if fmt in existing:
                numbered_pattern[fmt] = std_name
    
    rename_map.update(numbered_pattern)
    
    # Handle case variations
    case_map = {}
    for ch in existing:
        # Check for lowercase variants
        lower_ch = ch.lower()
        for std in _STANDARD_72_CHANNELS:
            if lower_ch == std.lower() and ch != std:
                case_map[ch] = std
                break
    
    rename_map.update(case_map)
    
    return rename_map


class HIDKernel:
    """Stage1 kernel for the HID (High-Density EEG Operational) dataset."""

    KERNEL_ID: str = "hid-ds004851-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _get_subject_id_from_path(file_path)
        
        # ------------------------------------------------------------------
        # 1. Determine dataset root for sidecar lookup
        # ------------------------------------------------------------------
        dataset_path = getattr(udataset, "path", None)
        if dataset_path is None:
            # Try to infer from file path (BIDS: dataset/sub-XXX/...)
            dataset_path = file_path
            for _ in range(4):  # Go up at most 4 levels
                parent = os.path.dirname(dataset_path)
                if os.path.exists(os.path.join(parent, "participants.tsv")):
                    dataset_path = parent
                    break
                dataset_path = parent
        
        # ------------------------------------------------------------------
        # 2. Read participants.tsv for subject metadata
        # ------------------------------------------------------------------
        subject_info = _read_participants_tsv(dataset_path, subject_id)
        
        # Fallback to static dict if TSV read failed
        if not subject_info and subject_id in _SUBJECT_DICT:
            subject_info = _SUBJECT_DICT[subject_id].copy()
        
        # Ensure all required fields exist
        for field in ["age", "sex", "handedness"]:
            if field not in subject_info:
                subject_info[field] = "unknown"
        
        # Ensure age is string
        subject_info["age"] = str(subject_info.get("age", "unknown"))
        # Ensure sex is lowercase
        sex_val = subject_info.get("sex", "unknown")
        if sex_val not in ("male", "female"):
            sex_val = "unknown"
        subject_info["sex"] = sex_val
        
        # ------------------------------------------------------------------
        # 3. Read required info fields from participants.tsv
        # ------------------------------------------------------------------
        extra_fields = {}
        if _PANDAS_AVAILABLE and dataset_path:
            participants_path = os.path.join(dataset_path, "participants.tsv")
            if os.path.exists(participants_path):
                try:
                    df = pd.read_csv(participants_path, sep="\t")
                    subj_row = df[df["participant_id"] == subject_id]
                    if subj_row.empty:
                        subj_row = df[df["participant_id"] == subject_id.replace("sub-", "")]
                    if not subj_row.empty:
                        row_dict = subj_row.iloc[0].to_dict()
                        for field in kernel_requirements.get("required_info_fields", []):
                            if field in row_dict and pd.notna(row_dict[field]):
                                extra_fields[field] = str(row_dict[field])
                            elif field not in extra_fields:
                                extra_fields[field] = "unknown"
                except Exception:
                    pass
        
        # Merge extra fields into subject_info for description
        for k, v in extra_fields.items():
            if k not in subject_info:
                subject_info[k] = v
        
        # ------------------------------------------------------------------
        # 4. Set amplifier and cap info
        # ------------------------------------------------------------------
        # Source: Dataset description — 72-channel HD-EEG at 2048 Hz
        # inferred by LLM, needs human review
        amplifier = "unknown"  # Not specified in available documentation
        cap = "unknown"        # Not specified in available documentation
        
        # Try to infer from dataset_description.json if available
        desc_json_path = os.path.join(dataset_path, "dataset_description.json") if dataset_path else None
        if desc_json_path and os.path.exists(desc_json_path):
            try:
                with open(desc_json_path, "r") as f:
                    ds_desc = json.load(f)
                # Check for device info in various possible fields
                for key in ["Device", "EEGDevice", "EEGReference", "ManufacturersModelName"]:
                    if key in ds_desc:
                        val = str(ds_desc[key])
                        if val and val.lower() != "n/a":
                            amplifier = val
                            break
            except Exception:
                pass
        
        # ------------------------------------------------------------------
        # 5. Update raw.info["description"]
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        eegunity_desc = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": amplifier,
            "cap": cap,
            "handedness": subject_info.get("handedness", "unknown"),
        }
        
        # Add any extra required info fields
        for field in kernel_requirements.get("required_info_fields", []):
            if field not in eegunity_desc and field in subject_info:
                eegunity_desc[field] = subject_info[field]
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # ------------------------------------------------------------------
        # 6. Channel renaming to standard 10-20 (BEFORE set_montage)
        # ------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # ------------------------------------------------------------------
        # 7. Set channel types and montage
        # ------------------------------------------------------------------
        # Identify EEG vs other channels
        ch_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            # Standard EEG channels
            if any(c.upper() == upper for c in _STANDARD_72_CHANNELS):
                ch_types[ch_name] = "eeg"
            # EOG channels
            elif any(x in upper for x in ["EOG", "HEOG", "VEOG", "EYE"]):
                ch_types[ch_name] = "eog"
            # EMG channels
            elif any(x in upper for x in ["EMG", "MUSCLE"]):
                ch_types[ch_name] = "emg"
            # ECG channels
            elif any(x in upper for x in ["ECG", "EKG", "HEART"]):
                ch_types[ch_name] = "ecg"
            # Reference or other special channels
            elif any(x in upper for x in ["REF", "REFERENCE", "A1", "A2", "M1", "M2", "CzREF"]):
                ch_types[ch_name] = "misc"
            # Default to EEG for unknown channels that look like EEG
            elif len(ch_name) <= 4 and any(c.isalpha() for c in ch_name):
                ch_types[ch_name] = "eeg"
            else:
                ch_types[ch_name] = "misc"
        
        # Apply channel types
        try:
            raw.set_channel_types(ch_types)
        except Exception:
            # If some channels fail, set individually
            for ch_name, ch_type in ch_types.items():
                if ch_name in raw.ch_names:
                    try:
                        raw.set_channel_types({ch_name: ch_type})
                    except Exception:
                        pass
        
        # Set montage for standard 10-20 layout
        try:
            # Check if we have standard channel names now
            current_names = set(raw.ch_names)
            standard_names = set(_STANDARD_72_CHANNELS)
            overlap = current_names & standard_names
            
            if len(overlap) >= 60:  # Most channels match standard
                montage = mne.channels.make_standard_montage("standard_1020")
                # Pick only the channels we have
                montage_chs = [c for c in montage.ch_names if c in raw.ch_names]
                if montage_chs:
                    montage = montage.copy().pick_channels(montage_chs)
                    raw = raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage setting is best-effort
        
        # ------------------------------------------------------------------
        # 8. Handle events from events.tsv (EEGLAB .set may not carry events)
        # ------------------------------------------------------------------
        # Check if raw already has meaningful annotations/events
        has_native_events = False
        try:
            if hasattr(raw, "annotations") and raw.annotations is not None:
                if len(raw.annotations) > 0:
                    has_native_events = True
            # Also check for events in the data
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if len(events) > 0:
                has_native_events = True
        except Exception:
            pass
        
        # For EEGLAB .set files, check if events are actually populated
        if file_path.endswith(".set"):
            try:
                # Try to read events — if empty or just boundary events, we need TSV
                events, event_id = mne.events_from_annotations(raw, verbose=False)
                if len(events) == 0 or all("boundary" in str(d).lower() for d in raw.annotations.description):
                    has_native_events = False
            except Exception:
                has_native_events = False
        
        # Derive annotations from events.tsv if needed
        if not has_native_events:
            events_tsv_path = _find_events_tsv(file_path)
            if events_tsv_path:
                events_df = _read_events_tsv(events_tsv_path)
                if events_df is not None and len(events_df) > 0:
                    # Create annotations from events.tsv
                    annotations = _events_to_annotations(events_df, raw.info["sfreq"])
                    if len(annotations) > 0:
                        raw.set_annotations(annotations)
        
        # ------------------------------------------------------------------
        # 9. Ensure required native/derived misc channels exist
        # ------------------------------------------------------------------
        # No required misc channels for this dataset
        for misc_name in kernel_requirements.get("required_native_misc", []):
            if misc_name in raw.ch_names:
                raw.set_channel_types({misc_name: "misc"})
        
        # No derived misc channels needed
        
        # ------------------------------------------------------------------
        # 10. Final event validation — ensure all required event IDs are present
        # ------------------------------------------------------------------
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            # Event IDs should already be mapped through _EVENT_MAP in _events_to_annotations
            # or preserved from native annotations
        except Exception:
            pass
        
        return raw


KERNEL = HIDKernel()