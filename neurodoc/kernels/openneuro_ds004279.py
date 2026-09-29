"""openneuro_ds004279 stage1 kernel for EEGUnity.

Large Spanish EEG dataset with 56 subjects performing speech perception
and silent production tasks with 30 Spanish sentences.

Source: https://openneuro.org/datasets/ds004279
Paper: DOI 10.1088/1741-2552/ad88a3
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# Standard 10-20 montage for 64+ channel systems
_STANDARD_MONTAGE = "standard_1020"

# Device metadata - amplifier and cap not specified in dataset
# Source: dataset_description.json and papers do not specify device
# inferred by LLM, needs human review
_DEVICE_AMPLIFIER = "unknown"
_DEVICE_CAP = "unknown"

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex"]


def _get_subject_from_path(file_path: str) -> Optional[str]:
    """Extract BIDS subject ID from file path."""
    match = re.search(r"(sub-[a-zA-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find sibling events.tsv file for the given EEG file."""
    base = file_path.replace(".edf", "").replace(".set", "").replace(".vhdr", "").replace(".eeg", "").replace(".fif", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: events.tsv in same directory with matching task/entities
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Extract entities like sub-XXX_ses-XX_task-XXX
    match = re.search(r"(sub-[a-zA-Z0-9]+(?:_ses-[a-zA-Z0-9]+)?(?:_task-[a-zA-Z0-9]+)?)", basename)
    if match:
        prefix = match.group(1)
        for f in os.listdir(dirname):
            if f.startswith(prefix) and f.endswith("_events.tsv"):
                return os.path.join(dirname, f)
    return None


def _read_events_tsv(events_path: str) -> Optional[Dict[str, Any]]:
    """Read events.tsv and return columns as dict of lists."""
    try:
        import pandas as pd
        df = pd.read_csv(events_path, sep="\t")
        return {
            "onset": df["onset"].values if "onset" in df.columns else [],
            "duration": df["duration"].values if "duration" in df.columns else [],
            "trial_type": df["trial_type"].values if "trial_type" in df.columns else [],
            "value": df["value"].values if "value" in df.columns else [],
            "sample": df["sample"].values if "sample" in df.columns else [],
        }
    except Exception:
        return None


def _read_participants_tsv(dataset_path: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and return info for subject."""
    participants_path = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_path):
        return {}
    
    try:
        import pandas as pd
        df = pd.read_csv(participants_path, sep="\t")
        # Match subject_id (could be "sub-002" or just "002")
        sub_match = subject_id.replace("sub-", "")
        # Try exact match first
        row = df[df["participant_id"] == subject_id]
        if row.empty:
            row = df[df["participant_id"] == sub_match]
        if row.empty:
            # Try with sub- prefix
            row = df[df["participant_id"] == f"sub-{sub_match}"]
        if row.empty:
            return {}
        return {col: str(row.iloc[0][col]) for col in row.columns if col != "participant_id"}
    except Exception:
        return {}


def _find_dataset_root(file_path: str) -> Optional[str]:
    """Find BIDS dataset root from file path."""
    current = os.path.dirname(file_path)
    for _ in range(10):  # Search up to 10 levels
        if os.path.exists(os.path.join(current, "participants.tsv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


class OpenNeuroDS004279Kernel:
    """Stage1 kernel for openneuro_ds004279 dataset."""

    KERNEL_ID: str = "openneuro-ds004279-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        subject_id = _get_subject_from_path(file_path)
        dataset_root = _find_dataset_root(file_path)

        # --- Channel rename: standardize to 10-20 names before montage ---
        # BIDS datasets often use standard names already, but ensure consistency
        rename_map = {}
        for ch in raw.ch_names:
            # Handle common BIDS variations
            new_name = ch
            # Remove EEG- prefix if present for standard names
            if ch.startswith("EEG-") and len(ch) > 4:
                potential = ch[4:]
                if potential in ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "T7", "C3", "Cz",
                                "C4", "T8", "P7", "P3", "Pz", "P4", "P8", "O1", "O2", "A1",
                                "A2", "FT9", "FT10", "TP9", "TP10", "POz", "FC1", "FC2",
                                "CP1", "CP2", "FC5", "FC6", "CP5", "CP6", "AFz", "AF3",
                                "AF4", "AF7", "AF8", "F1", "F2", "F5", "F6", "FT7", "FT8",
                                "C1", "C2", "C5", "C6", "TP7", "TP8", "P1", "P2", "P5",
                                "P6", "PO3", "PO4", "PO7", "PO8", "Oz", "Iz", "T9", "T10",
                                "M1", "M2", "VEOG", "HEOG", "EOG", "ECG", "EMG"]:
                    new_name = potential
            if new_name != ch:
                rename_map[ch] = new_name
        
        # Also handle numeric EEG-0..EEG-N mapping if needed
        # This dataset uses standard names per BIDS, so minimal renaming needed
        
        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage if channels match standard 1020
        try:
            montage = mne.channels.make_standard_montage(_STANDARD_MONTAGE)
            # Check overlap
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            if len(raw_chs & montage_chs) >= 32:  # At least half of 64 channels match
                raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            pass  # Montage not critical

        # --- Read participants.tsv for subject info ---
        participant_info = {}
        if dataset_root and subject_id:
            participant_info = _read_participants_tsv(dataset_root, subject_id)

        # Build eegunity_description
        age = str(participant_info.get("age", "unknown"))
        sex = participant_info.get("sex", "unknown").lower()
        if sex not in ["male", "female"]:
            sex = "unknown"
        
        # Required info fields
        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": _DEVICE_AMPLIFIER,
            "cap": _DEVICE_CAP,
            "handedness": participant_info.get("handedness", "unknown"),
        }
        
        # Add any extra required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field in participant_info and field not in eegunity_desc:
                eegunity_desc[field] = str(participant_info[field])
        
        # Include all non-canonical keys from participants.tsv as strings
        canonical_keys = {"age", "sex", "amplifier", "cap", "handedness"}
        for key, val in participant_info.items():
            if key not in canonical_keys:
                eegunity_desc[key] = str(val)

        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""
        
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # --- Process events from events.tsv ---
        events_path = _find_events_tsv(file_path)
        
        if events_path:
            events_data = _read_events_tsv(events_path)
            
            if events_data is not None and len(events_data.get("onset", [])) > 0:
                onsets = events_data["onset"]
                durations = events_data.get("duration", [0.0] * len(onsets))
                if len(durations) == 0 or len(durations) != len(onsets):
                    durations = [0.0] * len(onsets)
                
                # Build descriptions from value or trial_type
                descriptions = []
                values = events_data.get("value", [])
                trial_types = events_data.get("trial_type", [])
                
                for i in range(len(onsets)):
                    # Prefer trial_type if available, else use value
                    if len(trial_types) > i and str(trial_types[i]) not in ["nan", "None", ""]:
                        desc = str(trial_types[i])
                    elif len(values) > i and str(values[i]) not in ["nan", "None", ""]:
                        desc = str(values[i])
                    else:
                        desc = "unknown"
                    descriptions.append(desc)
                
                # Create annotations from events.tsv
                # Filter out any NaN onsets
                valid_idx = [i for i, o in enumerate(onsets) if not (isinstance(o, float) and np.isnan(o))]
                if valid_idx:
                    valid_onsets = [float(onsets[i]) for i in valid_idx]
                    valid_durations = [float(durations[i]) if i < len(durations) else 0.0 for i in valid_idx]
                    valid_descriptions = [descriptions[i] for i in valid_idx]
                    
                    annotations = mne.Annotations(
                        onset=valid_onsets,
                        duration=valid_durations,
                        description=valid_descriptions,
                    )
                    raw.set_annotations(annotations)

                # --- Create derived misc channel: trial_onset ---
                # Read onset column from events.tsv; for each perception-phase trial,
                # create constant-valued misc channel segment with trial's onset time
                try:
                    import pandas as pd
                    events_df = pd.read_csv(events_path, sep="\t")
                    
                    # Identify perception-phase rows (event values 1-30 based on analysis)
                    perception_mask = None
                    if "value" in events_df.columns:
                        # Try to identify perception events (values 1-30 per event structure)
                        try:
                            vals = pd.to_numeric(events_df["value"], errors="coerce")
                            perception_mask = (vals >= 1) & (vals <= 30)
                        except Exception:
                            pass
                    
                    if perception_mask is None and "trial_type" in events_df.columns:
                        # Fallback: check trial_type for perception indicators
                        tt = events_df["trial_type"].astype(str)
                        perception_mask = tt.str.contains("perception", case=False, na=False)
                    
                    if perception_mask is None:
                        perception_mask = pd.Series([True] * len(events_df))
                    
                    # Build trial_onset channel: step function with onset values at trial times
                    sfreq = raw.info["sfreq"]
                    n_samples = len(raw.times)
                    trial_onset_data = np.zeros((1, n_samples), dtype=np.float64)
                    
                    for idx in events_df[perception_mask].index:
                        onset_time = float(events_df.loc[idx, "onset"])
                        # Find sample index
                        sample_idx = int(round(onset_time * sfreq))
                        if sample_idx < n_samples:
                            # Set value from onset column (the actual onset time in seconds)
                            onset_value = float(events_df.loc[idx, "onset"])
                            # Fill until next event or end
                            next_idx = None
                            later_events = events_df[events_df["onset"] > onset_time]
                            if len(later_events) > 0:
                                next_time = float(later_events["onset"].min())
                                next_sample = int(round(next_time * sfreq))
                            else:
                                next_sample = n_samples
                            trial_onset_data[0, sample_idx:min(next_sample, n_samples)] = onset_value
                    
                    # Create as RawArray and add to raw
                    info = mne.create_info(
                        ch_names=["trial_onset"],
                        sfreq=sfreq,
                        ch_types=["misc"],
                    )
                    trial_raw = mne.io.RawArray(trial_onset_data, info, first_samp=raw.first_samp)
                    raw.add_channels([trial_raw], force_update_info=True)
                    
                except Exception:
                    pass  # Derived misc channel creation failed, continue without it

        # --- Ensure required native/derived misc channels exist ---
        # Check if any native misc channels need type correction
        current_types = {ch: t for ch, t in zip(raw.ch_names, raw.get_channel_types())}
        misc_fixes = {}
        for ch in raw.ch_names:
            # Common non-EEG channels that should be misc
            if ch.upper() in ["STI", "STIM", "STATUS", "TRIGGER"] or ch.startswith("STI"):
                if current_types.get(ch) != "misc":
                    misc_fixes[ch] = "misc"
        
        if misc_fixes:
            raw.set_channel_types(misc_fixes)

        return raw


KERNEL = OpenNeuroDS004279Kernel()