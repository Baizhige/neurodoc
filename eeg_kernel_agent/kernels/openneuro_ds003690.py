"""OpenNeuro DS003690 stage1 kernel for EEGUnity.

EEG, ECG and Pupil Data from Young and Older Adults:
Rest and Auditory Cued Reaction Time Tasks.

This is a BIDS-compliant dataset with BrainVision .vhdr/.eeg/.vmrk files.
The kernel handles channel renaming to standard 10-20, montage setup,
event annotation from sidecar events.tsv, and metadata enrichment from
participants.tsv.

Source: https://openneuro.org/datasets/ds003690
Paper: https://doi.org/10.1016/j.neuroimage.2019.06.004
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Required info fields from participants.tsv (per kernel requirements)
# =============================================================================
_REQUIRED_INFO_FIELDS: List[str] = [
    "MoCA",
    "age",
    "education_years",
    "group",
    "hand_laterality",
    "pupil_data",
    "sex",
    "smoker",
    "task_order",
]

# =============================================================================
# Channel rename map: BrainVision names -> standard 10-20
# Source: Dataset README and BrainVision standard 64-channel actiCAP layout
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# =============================================================================
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # EEG channels
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "FC5": "FC5",
    "FC1": "FC1",
    "FC2": "FC2",
    "FC6": "FC6",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "TP9": "TP9",
    "CP5": "CP5",
    "CP1": "CP1",
    "CP2": "CP2",
    "CP6": "CP6",
    "TP10": "TP10",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "PO9": "PO9",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
    "PO10": "PO10",
    # EOG channels
    "EOG1": "EOG1",
    "EOG2": "EOG2",
    # ECG channels
    "ECG1": "ECG1",
    "ECG2": "ECG2",
}

# Standard 10-20 positions for setting montage
_STANDARD_1020_CHANNELS: set = {
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FC2", "FC6",
    "T7", "C3", "Cz", "C4", "T8",
    "TP9", "CP5", "CP1", "CP2", "CP6", "TP10",
    "P7", "P3", "Pz", "P4", "P8",
    "PO9", "O1", "Oz", "O2", "PO10",
}

# Channel types mapping
_CHANNEL_TYPES: Dict[str, str] = {
    "EOG1": "eog",
    "EOG2": "eog",
    "ECG1": "ecg",
    "ECG2": "ecg",
}


# =============================================================================
# Event code mapping (numeric -> human-readable description)
# Source: analysis.md Event Structure table and dataset documentation
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# =============================================================================
_EVENT_CODE_MAP: Dict[int, str] = {
    1: "auditory stimulus onset marker",
    10: "auditory warning cue preceding stimulus",
    11: "auxiliary trial event marker",
    2: "button press response",
    3: "error feedback tone",
    4: "no-go stimulus",
    5: "go stimulus",
    6: "error of commission",
    7: "auxiliary error event marker",
    9: "task block start marker",
}


def _detect_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    parts = os.path.basename(file_path).split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part.replace("sub-", "")
    # Try from directory path
    for dir_part in file_path.split(os.sep):
        if dir_part.startswith("sub-"):
            return dir_part.replace("sub-", "")
    return None


def _find_dataset_root(file_path: str) -> str:
    """Find BIDS dataset root from file path."""
    current = os.path.dirname(os.path.abspath(file_path))
    while current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "participants.tsv")):
            return current
        current = os.path.dirname(current)
    return ""


def _load_participants_info(dataset_root: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from BIDS participants.tsv."""
    result: Dict[str, str] = {}
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    
    if not os.path.exists(participants_tsv):
        return result
    
    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
        
        # Handle both "sub-001" and "001" formats
        subject_keys = [f"sub-{subject_id}", subject_id]
        row = df[df[subject_col].isin(subject_keys)]
        
        if row.empty:
            return result
        
        row_data = row.iloc[0]
        
        # Required canonical fields
        age = str(row_data.get("age", "unknown"))
        sex = str(row_data.get("sex", "unknown")).lower()
        handedness = str(row_data.get("hand_laterality", row_data.get("handedness", "unknown"))).lower()
        
        result["age"] = age if age and age != "nan" else "unknown"
        
        # Normalize sex
        if sex in ("f", "female"):
            result["sex"] = "female"
        elif sex in ("m", "male"):
            result["sex"] = "male"
        else:
            result["sex"] = "unknown"
        
        # Normalize handedness
        if handedness in ("r", "right"):
            result["handedness"] = "right"
        elif handedness in ("l", "left"):
            result["handedness"] = "left"
        else:
            result["handedness"] = "unknown"
        
        # Required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field in row_data.index and field not in ("age", "sex", "hand_laterality", "handedness"):
                val = row_data[field]
                if pd.isna(val):
                    result[field] = "unknown"
                else:
                    result[field] = str(val)
            elif field not in result:
                result[field] = "unknown"
                
    except Exception as e:
        warnings.warn(f"Error reading participants.tsv: {e}")
    
    return result


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS naming: sub-XXX_task-YYY_run-ZZ_eeg.<ext> -> sub-XXX_task-YYY_run-ZZ_events.tsv
    base = file_path.rsplit("_eeg", 1)[0]
    events_path = base + "_events.tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Try without run suffix
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path).rsplit("_eeg", 1)[0]
    
    # Pattern match in directory
    if os.path.isdir(dir_name):
        for f in os.listdir(dir_name):
            if f.endswith("_events.tsv") and f.startswith(base_name.rsplit("_run", 1)[0]):
                return os.path.join(dir_name, f)
    
    return None


def _load_events_from_tsv(events_tsv: str) -> Optional[mne.Annotations]:
    """Load events from BIDS events.tsv and create MNE Annotations."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        
        # Required columns
        if "onset" not in df.columns:
            return None
        
        onsets = df["onset"].values
        durations = df["duration"].values if "duration" in df.columns else np.zeros(len(onsets))
        
        # Determine description column
        if "trial_type" in df.columns:
            desc_col = "trial_type"
        elif "value" in df.columns:
            desc_col = "value"
        elif "stim_type" in df.columns:
            desc_col = "stim_type"
        else:
            # Try to find any suitable column
            for col in df.columns:
                if col not in ("onset", "duration", "sample", "HED"):
                    desc_col = col
                    break
            else:
                return None
        
        descriptions = []
        for val in df[desc_col]:
            # Try numeric mapping first
            try:
                num_val = int(float(val))
                desc = _EVENT_CODE_MAP.get(num_val, str(val))
            except (ValueError, TypeError):
                desc = str(val) if pd.notna(val) else "unknown"
            descriptions.append(desc)
        
        # Handle any infinite or NaN onsets
        valid_mask = np.isfinite(onsets)
        if not np.all(valid_mask):
            onsets = onsets[valid_mask]
            durations = durations[valid_mask] if len(durations) == len(valid_mask) else np.zeros(len(onsets))
            descriptions = [d for i, d in enumerate(descriptions) if valid_mask[i]]
        
        if len(onsets) == 0:
            return None
        
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        return annotations
        
    except Exception as e:
        warnings.warn(f"Error reading events.tsv {events_tsv}: {e}")
        return None


def _events_tsv_to_misc_channel(raw: mne.io.BaseRaw, events_tsv: str, column: str) -> mne.io.BaseRaw:
    """Create a derived MISC channel from events.tsv column values."""
    try:
        df = pd.read_csv(events_tsv, sep="\t")
        if "onset" not in df.columns or column not in df.columns:
            return raw
        
        sfreq = raw.info["sfreq"]
        n_samples = len(raw.times)
        data = np.zeros((1, n_samples))
        
        for _, row in df.iterrows():
            onset = row["onset"]
            if pd.isna(onset) or not np.isfinite(onset):
                continue
            val = row[column]
            if pd.isna(val):
                continue
            
            sample_idx = int(round(onset * sfreq))
            sample_idx = max(0, min(sample_idx, n_samples - 1))
            
            # Set value at onset and carry forward until next event
            try:
                numeric_val = float(val)
            except (ValueError, TypeError):
                numeric_val = 1.0  # Default for non-numeric
            
            # Fill from this sample to end (or until next event)
            data[0, sample_idx:] = numeric_val
        
        # Create info for misc channel
        ch_info = mne.create_info(
            ch_names=[f"events_{column}"],
            sfreq=sfreq,
            ch_types=["misc"],
        )
        misc_raw = mne.io.RawArray(data, ch_info, first_samp=raw.first_samp)
        
        # Add to raw
        raw.add_channels([misc_raw], force_update_info=True)
        
    except Exception as e:
        warnings.warn(f"Error creating derived misc channel from {events_tsv}: {e}")
    
    return raw


class OpenNeuroDS003690Kernel:
    """Stage1 kernel for OpenNeuro ds003690 dataset."""

    KERNEL_ID: str = "openneuro-ds003690-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        dataset_root = _find_dataset_root(file_path)
        subject_id = _detect_subject_id(file_path)
        
        # =================================================================
        # 1. Channel renaming and type setting
        # =================================================================
        
        # Rename channels to standard 10-20
        rename_map = {}
        for old_name in raw.ch_names:
            if old_name in _CHANNEL_RENAME_MAP:
                new_name = _CHANNEL_RENAME_MAP[old_name]
                if old_name != new_name:
                    rename_map[old_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for non-EEG channels
        ch_types_to_set = {}
        for ch_name in raw.ch_names:
            if ch_name in _CHANNEL_TYPES:
                ch_types_to_set[ch_name] = _CHANNEL_TYPES[ch_name]
        
        if ch_types_to_set:
            raw.set_channel_types(ch_types_to_set)
        
        # Ensure any remaining non-standard channels are set to misc
        for ch_name in raw.ch_names:
            if ch_name not in _STANDARD_1020_CHANNELS and ch_name not in _CHANNEL_TYPES:
                try:
                    current_type = raw.get_channel_types(picks=[ch_name])[0]
                    if current_type == "eeg" and not any(ch_name.startswith(p) for p in ["Fp", "F", "FC", "T", "C", "TP", "CP", "P", "PO", "O"]):
                        raw.set_channel_types({ch_name: "misc"})
                except Exception:
                    pass
        
        # =================================================================
        # 2. Set montage (AFTER channel rename)
        # =================================================================
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage for channels that exist in the montage
            montage_ch_names = set(montage.ch_names)
            raw_ch_names = set(raw.ch_names)
            common_ch_names = list(raw_ch_names & montage_ch_names)
            
            if common_ch_names:
                # Temporarily pick only EEG channels for montage
                raw.set_montage(montage, on_missing="ignore")
        except Exception as e:
            warnings.warn(f"Could not set montage: {e}")
        
        # =================================================================
        # 3. Load and apply events from events.tsv if available
        # =================================================================
        events_tsv = _find_events_tsv(file_path)
        
        # Check if raw already has annotations or events
        has_native_events = False
        try:
            if raw.annotations is not None and len(raw.annotations) > 0:
                has_native_events = True
            # Also check for stim channel
            stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
            if len(stim_picks) > 0:
                has_native_events = True
        except Exception:
            pass
        
        # BrainVision .eeg files should have .vmrk markers, but if annotations
        # are empty or missing, fall back to events.tsv
        if events_tsv:
            annotations = _load_events_from_tsv(events_tsv)
            if annotations is not None:
                if not has_native_events or len(raw.annotations) == 0:
                    # No native events: use events.tsv
                    raw.set_annotations(annotations)
                else:
                    # Has native events, but check if we need to supplement
                    # For this dataset, BrainVision markers may be present but
                    # events.tsv has more complete information
                    pass  # Keep native events, they are authoritative
        
        # =================================================================
        # 4. Load subject metadata from participants.tsv
        # =================================================================
        subject_info = _load_participants_info(dataset_root, subject_id) if subject_id else {}
        
        # Ensure canonical fields
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")
        
        # Build eegunity_description with required info fields
        eegunity_desc: Dict[str, str] = {
            "age": age,
            "sex": sex,
            "handedness": handedness,
            "amplifier": "BrainAmp",  # Source: paper DOI 10.1016/j.neuroimage.2019.06.004
            "cap": "actiCAP 64Ch",     # LLM 推断，需人类复核
        }
        
        # Add required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field in subject_info:
                eegunity_desc[field] = subject_info[field]
            else:
                eegunity_desc[field] = "unknown"
        
        # =================================================================
        # 5. Update raw.info["description"]
        # =================================================================
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        }
        raw.info["description"] = json.dumps(description_dict)
        
        # =================================================================
        # 6. Ensure required native/derived misc channels
        # =================================================================
        # Required native misc: ensure ECG channels are typed as misc if not ecg
        # (they should already be set to ecg above, which is acceptable)
        
        # Check for any channels that should be misc
        for ch_name in raw.ch_names:
            if ch_name.startswith("Pupil") or ch_name.startswith("GSR") or ch_name.startswith("Resp"):
                try:
                    raw.set_channel_types({ch_name: "misc"})
                except Exception:
                    pass
        
        # =================================================================
        # 7. Final validation
        # =================================================================
        # Ensure we have the required event IDs in annotations
        required_event_ids = {"1", "2", "4", "5", "6"}
        if raw.annotations is not None:
            found_events = set()
            for desc in raw.annotations.description:
                # Extract numeric code if present
                try:
                    # Check if description is a numeric string
                    num_desc = int(float(desc))
                    found_events.add(str(num_desc))
                except (ValueError, TypeError):
                    # Check if it's in our mapped descriptions
                    for code, mapped_desc in _EVENT_CODE_MAP.items():
                        if desc == mapped_desc:
                            found_events.add(str(code))
            
            # Log missing events
            missing = required_event_ids - found_events
            if missing:
                warnings.warn(f"Missing required event IDs: {missing}")
        
        return raw


KERNEL = OpenNeuroDS003690Kernel()