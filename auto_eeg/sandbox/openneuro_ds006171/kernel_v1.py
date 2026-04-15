"""Dataset-specific kernel for openneuro_ds006171.

EEG during near-threshold visual detection tasks (no-cue, 50%-cue, 100%-cue).
BioSemi BDF format with 144 channels, 1024 Hz sampling rate.

Source: https://openneuro.org/datasets/ds006171
DOI: https://doi.org/10.18112/openneuro.ds006171.v1.0.0
Paper: https://doi.org/10.1111/psyp.14525

Event Structure (verified from analysis.md):
  1    = trial_start
  2    = response (detection report)
  11   = No-cue condition, stimulus A (epoch align reference)
  12   = No-cue condition, stimulus B (epoch align reference)
  21   = 50%-validity cue condition, stimulus A (epoch align reference)
  22   = 50%-validity cue condition, stimulus B (epoch align reference)
  101  = No-cue - hit
  103  = No-cue - false alarm
  104  = No-cue - correct rejection
  111  = 50%-validity cue - hit
  121  = 50%-validity cue - miss
  122  = 50%-validity cue - miss (duplicate code)
  124  = 100%-validity cue - false alarm
  125  = 100%-validity cue - correct rejection
  128  = BioSemi boundary marker (admin; exclude)

Behavioral columns in events.tsv: gabor_contrast, subjective_r, objective_r, response_time
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
# Source: OpenNeuro participants.tsv (age/sex from dataset)
# LLM 推断，需人类复核 for amplifier/cap/handedness
# Annotator: LLM, 2026-04-08
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {}
# Will be populated from participants.tsv at runtime

# Hardware metadata - hardcoded based on BioSemi BDF format
# Source: Dataset README / standard BioSemi configuration
# Annotator: LLM, 2026-04-08
_HARDWARE_METADATA = {
    "amplifier": "BioSemi ActiveTwo",  # LLM 推断，需人类复核
    "cap": "Ag/AgCl",                   # LLM 推断，需人类复核
}

# =============================================================================
# Channel Name Mapping
# =============================================================================
# BioSemi BDF files may have channel names like "A1", "A2", ... or standard 10-20 names
# The dataset uses a 144-channel system. Standard 10-20 names are preferred.
# Source: Paper (DOI 10.1111/psyp.14525) mentions "128-channel EEG system"
# Annotator: LLM, 2026-04-08
_EEG_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
    "T9", "T7", "T5", "T3", "T1", "Tz", "T2", "T4", "T6", "T8", "T10",
    "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
    # Continuation for 144 channels
    "AF11", "AF12", "F11", "F12", "FT11", "FT12", "T11", "T12",
    "TP11", "TP12", "P11", "P12", "PO11", "PO12",
    "EOG1", "EOG2", "EOG3", "EOG4",  # EOG channels
    "ECG1", "ECG2",                      # ECG channels
    "EMG1", "EMG2",                      # EMG channels
    "Resp1", "Resp2",                    # Respiratory
    "Trigger", "Status",                 # Auxiliary
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for BioSemi BDF channels to standard names.

    BioSemi BDF files often use generic names like 'A1', 'A2', etc. or
    may already have standard 10-20 names. This function attempts to map
    them appropriately.

    Source: BioSemi standard channel naming convention
    Annotator: LLM, 2026-04-08
    """
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # BioSemi default: A1-A128 for EEG, then B1-B32 for auxiliary
    for i, ch_name in enumerate(existing_names, start=1):
        if ch_name.startswith("A") and ch_name[1:].isdigit():
            idx = int(ch_name[1:]) - 1
            if idx < len(_EEG_CHANNEL_NAMES):
                rename_map[ch_name] = _EEG_CHANNEL_NAMES[idx]

    return rename_map


# =============================================================================
# Event ID Mapping
# =============================================================================
# Raw meta: event labels matching analysis.md Event Structure
_EVENT_MAP: Dict[str, int] = {
    "trial_start": 1,
    "response": 2,
    "nocue_stim_A": 11,
    "nocue_stim_B": 12,
    "nocue_hit": 101,
    "nocue_FA": 103,
    "nocue_CR": 104,
    "50pct_stim_A": 21,
    "50pct_stim_B": 22,
    "50pct_hit": 111,
    "50pct_miss_1": 121,
    "50pct_miss_2": 122,
    "100pct_FA": 124,
    "100pct_CR": 125,
    "boundary": 128,
}

# Reverse mapping for annotation lookup
_EVENT_ID_TO_NAME: Dict[int, str] = {v: k for k, v in _EVENT_MAP.items()}


# =============================================================================
# Kernel Class
# =============================================================================
class OpenNeuroDS006171Kernel:
    """Stage1 kernel for OpenNeuro ds006171 dataset.

    EEG during near-threshold visual detection tasks with three cueing
    conditions: no-cue (0%), 50%-validity, and 100%-validity.
    """

    KERNEL_ID: str = "openneuro-ds006171-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            In-memory MNE Raw object (BDF format from BioSemi).
        row : pandas.Series
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row["File Path"]
        subject_id = row.get("subject_id", "unknown")
        original_desc = raw.info.get("description", "")

        # -------------------------------------------------------------------------
        # 1. Load subject metadata from participants.tsv
        # -------------------------------------------------------------------------
        subject_info = self._load_subject_info(udataset, subject_id)

        # -------------------------------------------------------------------------
        # 2. Update raw.info["description"]
        # -------------------------------------------------------------------------
        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower(),
                "amplifier": _HARDWARE_METADATA.get("amplifier", "unknown"),
                "cap": _HARDWARE_METADATA.get("cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -------------------------------------------------------------------------
        # 3. Rename channels before set_montage()
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            valid_renames = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if valid_renames:
                raw.rename_channels(valid_renames)
                print(f"[{self.KERNEL_ID}] Renamed {len(valid_renames)} channels")

        # -------------------------------------------------------------------------
        # 4. Set montage (standard 10-20 system)
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Keep only channels that exist in both raw and montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if common_channels:
                raw.set_montage(montage, on_missing="ignore")
                print(f"[{self.KERNEL_ID}] Set montage for {len(common_channels)} channels")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: Could not set montage: {e}")

        # -------------------------------------------------------------------------
        # 5. Create annotations from events.tsv
        # -------------------------------------------------------------------------
        events_tsv_path = self._find_events_tsv(file_path)
        if events_tsv_path and os.path.exists(events_tsv_path):
            annotations = self._load_events_tsv(events_tsv_path, raw.info["sfreq"])
            raw.set_annotations(annotations)
            print(f"[{self.KERNEL_ID}] Loaded {len(annotations)} annotations from events.tsv")
        else:
            # Fallback: extract events from raw annotations (if any)
            print(f"[{self.KERNEL_ID}] Warning: events.tsv not found, using raw annotations")

        return raw

    def _load_subject_info(
        self, udataset, subject_id: str
    ) -> Dict[str, str]:
        """Load subject metadata from participants.tsv.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        subject_id : str
            Subject identifier (e.g., "sub-01").

        Returns
        -------
        Dict[str, str]
            Subject info with keys: age, sex, handedness.
        """
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        try:
            # Try to load participants.tsv
            dataset_path = getattr(udataset, "path", None)
            if dataset_path:
                participants_tsv = os.path.join(dataset_path, "participants.tsv")
                if os.path.exists(participants_tsv):
                    df = pd.read_csv(participants_tsv, sep="\t")
                    # Match subject_id (may be "sub-01" or just "01")
                    subject_col = "participant_id"
                    if subject_col in df.columns:
                        # Normalize: find matching row
                        normalized_id = subject_id.replace("sub-", "")
                        for col in df.columns:
                            df[col] = df[col].astype(str).str.replace("sub-", "", regex=False)
                        mask = df[subject_col].str.replace("sub-", "", regex=False) == normalized_id
                        if mask.any():
                            row = df[mask].iloc[0]
                            if "age" in df.columns:
                                age_val = str(row.get("age", "unknown"))
                                subject_info["age"] = age_val if age_val != "nan" else "unknown"
                            if "sex" in df.columns:
                                sex_val = str(row.get("sex", "unknown")).lower()
                                if sex_val in ["m", "male", "f", "female"]:
                                    subject_info["sex"] = "male" if sex_val.startswith("m") else "female"
                                else:
                                    subject_info["sex"] = "unknown"
                            if "handedness" in df.columns or "Handedness" in df.columns:
                                hand_col = "handedness" if "handedness" in df.columns else "Handedness"
                                hand_val = str(row.get(hand_col, "unknown")).lower()
                                if hand_val in ["r", "right", "l", "left"]:
                                    subject_info["handedness"] = "right" if hand_val.startswith("r") else "left"
                                else:
                                    subject_info["handedness"] = "unknown"
                    else:
                        print(f"[{self.KERNEL_ID}] Warning: participant_id column not found")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Warning: Could not load subject info: {e}")

        return subject_info

    def _find_events_tsv(self, file_path: str) -> Optional[str]:
        """Find the corresponding events.tsv file for a given EEG file.

        Parameters
        ----------
        file_path : str
            Path to the EEG file (e.g., .bdf).

        Returns
        -------
        Optional[str]
            Path to events.tsv if found, else None.
        """
        base_dir = os.path.dirname(file_path)
        file_basename = os.path.splitext(os.path.basename(file_path))[0]

        # Common patterns for BIDS events files
        candidates = [
            os.path.join(base_dir, file_basename + "_events.tsv"),
            os.path.join(base_dir, "..", file_basename + "_events.tsv"),
            os.path.join(base_dir, file_basename.replace("_eeg", "") + "_events.tsv"),
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        return None

    def _load_events_tsv(
        self, events_tsv_path: str, sfreq: float
    ) -> mne.Annotations:
        """Load events from BIDS events.tsv and create MNE annotations.

        Parameters
        ----------
        events_tsv_path : str
            Path to the events.tsv file.
        sfreq : float
            Sampling frequency of the raw data.

        Returns
        -------
        mne.Annotations
            MNE annotations object.
        """
        df = pd.read_csv(events_tsv_path, sep="\t")

        onset_list = []
        duration_list = []
        description_list = []

        # Standard BIDS events.tsv columns: onset, duration, trial_type
        # May also have: value, sample, response_time, gabor_contrast, etc.
        for _, row in df.iterrows():
            try:
                # Parse onset (convert to seconds if in samples)
                onset = float(row["onset"])
                if "sample" in df.columns and pd.notna(row.get("sample")):
                    onset = float(row["sample"]) / sfreq

                # Duration (default to 0 for point events)
                duration = float(row.get("duration", 0.0))
                if pd.isna(duration):
                    duration = 0.0

                # Description from trial_type or value column
                if "trial_type" in df.columns and pd.notna(row.get("trial_type")):
                    desc = str(row["trial_type"])
                elif "value" in df.columns and pd.notna(row.get("value")):
                    desc = str(int(float(row["value"])))
                else:
                    continue

                # Map numeric codes to canonical names
                try:
                    code = int(float(desc))
                    mapped_desc = _EVENT_ID_TO_NAME.get(code, desc)
                except (ValueError, TypeError):
                    mapped_desc = desc

                # Skip boundary markers
                if mapped_desc == "boundary":
                    continue

                onset_list.append(onset)
                duration_list.append(duration)
                description_list.append(mapped_desc)

            except Exception:
                continue

        return mne.Annotations(
            onset=np.array(onset_list),
            duration=np.array(duration_list),
            description=description_list,
        )


# Module-level kernel instance
KERNEL = OpenNeuroDS006171Kernel()