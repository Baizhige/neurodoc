"""Dataset-specific kernel for openneuro ds002833.

Visual Object Naming EEG (High-Density) - 257-channel EGI HydroCell array.
Supports stimulus-locked ERP analysis (regression with response_time)
and visual object category classification (from events.tsv trial_type).

Source: https://openneuro.org/datasets/ds002833
DOI: https://doi.org/10.18112/openneuro.ds002833.v1.0.0
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Channel Rename Map for EGI 257-channel HydroCell
# =============================================================================
# Source: EGI HydroCell 257-channel system naming convention
# Each channel is named E1, E2, ... E257 in native EGI format.
# Some files may use numeric strings like "1", "2", ..., "257".
# Source: Human annotator based on EGI documentation, 2026-04-08

def _build_egi_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for EGI 257-channel HydroCell array.

    EGI systems typically name channels as E1, E2, ... E257 or as
    plain numeric strings "1", "2", ..., "257". This function
    creates a mapping to standardize them for 10-20 compatibility
    where possible, or keeps EGI naming if no standard mapping exists.
    """
    rename_map: Dict[str, str] = {}
    existing = raw.ch_names

    # Pattern 1: EGI "E1", "E2", ... format
    for ch in existing:
        if re.match(r'^E\d+$', ch):
            # Keep EGI naming as-is for HydroCell (no standard 10-20 equivalent)
            # Just ensure consistent formatting
            rename_map[ch] = ch.upper()

    # Pattern 2: Numeric string "1", "2", ... format
    for ch in existing:
        if re.match(r'^\d+$', ch):
            # Map to E1, E2, ... format for consistency
            rename_map[ch] = f"E{int(ch)}"

    return rename_map


# =============================================================================
# Subject Information (from participants.tsv)
# =============================================================================
# Source: participants.tsv from BIDS dataset
# Fields: participant_id, age, sex, group, handedness
# Annotator: Human, 2026-04-08


def _load_participant_info(
    dataset_path: str, participant_id: str
) -> Dict[str, str]:
    """Load subject metadata from participants.tsv.

    Parameters
    ----------
    dataset_path : str
        Root path of the BIDS dataset.
    participant_id : str
        Subject identifier (e.g., "sub-01").

    Returns
    -------
    dict
        Dictionary with age, sex, handedness fields.
    """
    participants_tsv = os.path.join(dataset_path, "participants.tsv")

    defaults = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    if not os.path.exists(participants_tsv):
        # inferred by LLM, needs human review
        return defaults

    try:
        df = pd.read_csv(participants_tsv, sep="\t")
        row = df[df["participant_id"] == participant_id]
        if row.empty:
            return defaults

        row = row.iloc[0]

        # age: ensure string format
        age_val = row.get("age", "unknown")
        if pd.notna(age_val):
            age_str = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)
        else:
            age_str = "unknown"

        # sex: lowercase
        sex_val = row.get("sex", "unknown")
        if pd.notna(sex_val):
            sex_str = str(sex_val).lower().strip()
            if sex_str not in ("male", "female"):
                sex_str = "unknown"
        else:
            sex_str = "unknown"

        # handedness
        handed_val = row.get("handedness", "unknown")
        if pd.notna(handed_val):
            handed_str = str(handed_val).lower().strip()
        else:
            handed_str = "unknown"

        return {
            "age": age_str,
            "sex": sex_str,
            "handedness": handed_str,
        }
    except Exception:
        return defaults


# =============================================================================
# Event Extraction from events.tsv
# =============================================================================


def _load_events_tsv(eeg_file_path: str) -> pd.DataFrame:
    """Load events.tsv corresponding to the given EEG file.

    Parameters
    ----------
    eeg_file_path : str
        Path to the EEG file (.edf, .vhdr, etc.).

    Returns
    -------
    pd.DataFrame or None
        Events dataframe if found, else None.
    """
    base_dir = os.path.dirname(eeg_file_path)
    stem = os.path.splitext(os.path.basename(eeg_file_path))[0]

    # Common BIDS events.tsv naming patterns
    candidates = [
        os.path.join(base_dir, stem + "_events.tsv"),
        os.path.join(base_dir, "..", f"{stem}_events.tsv"),
        os.path.join(base_dir, "events.tsv"),
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            try:
                return pd.read_csv(candidate, sep="\t")
            except Exception:
                pass

    return None


def _extract_trial_type_from_events(events_df: pd.DataFrame) -> Dict[float, str]:
    """Extract trial_type mapping from events.tsv.

    Creates a mapping from onset time to trial_type label.
    """
    if events_df is None:
        return {}

    mapping: Dict[float, str] = {}
    if "onset" in events_df.columns and "trial_type" in events_df.columns:
        for _, row in events_df.iterrows():
            onset = float(row["onset"])
            trial_type = str(row["trial_type"]) if pd.notna(row["trial_type"]) else "unknown"
            mapping[onset] = trial_type

    return mapping


# =============================================================================
# Response Time Extraction from misc channel
# =============================================================================


def _extract_response_times(raw: mne.io.BaseRaw) -> List[float]:
    """Extract response_time values from misc channel.

    EGI systems store response times in a misc channel. This function
    looks for a channel named 'response_time' or similar and extracts
    the values.

    Returns
    -------
    List of response times in seconds, or empty list if not found.
    """
    response_times: List[float] = []

    # Look for response_time channel
    for ch_name in raw.ch_names:
        if "response_time" in ch_name.lower() or "resp" in ch_name.lower():
            ch_idx = raw.ch_names.index(ch_name)
            data, times = raw[ch_idx, :]
            # Filter out zeros/near-zeros (baseline) and extract valid values
            valid_mask = data.flatten() > 0.001
            if np.any(valid_mask):
                response_times = times[valid_mask].tolist()
                break

    return response_times


# =============================================================================
# Kernel Class
# =============================================================================


class OpenNeuroDS002833Kernel:
    """Stage1 kernel for OpenNeuro ds002833 - Visual Object Naming EEG.

    This kernel handles:
    - EGI 257-channel HydroCell naming standardization
    - DIN1 stimulus onset event extraction
    - response_time from misc channel for regression tasks
    - trial_type from events.tsv for classification tasks
    - Proper eegunity_description metadata
    """

    KERNEL_ID: str = "openneuro-ds002833-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        file_path = row.get("File Path", "")
        dataset_path = row.get("Dataset Path", os.path.dirname(os.path.dirname(file_path)))
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))

        # =========================================================================
        # 1. Channel Renaming (BEFORE set_montage)
        # =========================================================================
        rename_map = _build_egi_rename_map(raw)
        if rename_map:
            print(f"[{self.KERNEL_ID}] Renaming channels: {len(rename_map)} mappings")
            raw.rename_channels(rename_map)

        # =========================================================================
        # 2. Set Montage (EGI HydroCell - high-density, use standard_1020 as fallback)
        # =========================================================================
        # EGI HydroCell 257-channel system does not map directly to standard_1020.
        # Try to set montage for known channels only (EOG, reference, etc.)
        try:
            # Attempt with high-density montage as fallback
            montage = mne.channels.make_standard_montage("standard_1020")
            # Find intersection of raw channels and montage channels
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if common_channels:
                raw.set_montage(montage, on_missing="ignore")
            else:
                print(f"[{self.KERNEL_ID}] No standard_1020 channels found, skipping montage")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] Montage setting skipped: {e}")

        # =========================================================================
        # 3. Load Subject Information
        # =========================================================================
        subject_info = _load_participant_info(dataset_path, subject_id)

        # =========================================================================
        # 4. Build eegunity_description
        # =========================================================================
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": str(original_desc) if original_desc else "",
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": "EGI Geodesic System",  # Source: dataset description
                "cap": "EGI HydroCell 257-channel",  # Source: dataset description
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # =========================================================================
        # 5. Extract Events from raw annotations/triggers
        # =========================================================================
        # DIN1 triggers mark stimulus onset (EGI digital input)
        # Look for DIN1 in raw annotations
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            print(f"[{self.KERNEL_ID}] Raw events found: {list(event_id.keys())}")
        except Exception as e:
            print(f"[{self.KERNEL_ID}] No raw events found: {e}")
            events = np.array([]).reshape(0, 3)
            event_id = {}

        # Build annotation descriptions for DIN1 and unknown events
        onset_list: List[float] = []
        duration_list: List[float] = []
        description_list: List[str] = []

        # Process DIN1 events
        din1_id = event_id.get("DIN1")
        if din1_id is not None and len(events) > 0:
            din1_events = events[events[:, 2] == din1_id]
            for ev in din1_events:
                onset_list.append(float(ev[0]) / raw.info["sfreq"])
                duration_list.append(0.0)
                description_list.append("DIN1")

        # Mark unknown/admin events
        for desc, ev_id in event_id.items():
            if desc.lower() == "unknown" or desc.startswith("admin"):
                unknown_events = events[events[:, 2] == ev_id]
                for ev in unknown_events:
                    onset_list.append(float(ev[0]) / raw.info["sfreq"])
                    duration_list.append(0.0)
                    description_list.append(f"admin: {desc}")

        # =========================================================================
        # 6. Load events.tsv for trial_type (classification labels)
        # =========================================================================
        events_tsv = _load_events_tsv(file_path)
        trial_type_map = _extract_trial_type_from_events(events_tsv)

        # =========================================================================
        # 7. Extract response_time from misc channel
        # =========================================================================
        response_times = _extract_response_times(raw)

        # =========================================================================
        # 8. Create annotations with combined labels
        # =========================================================================
        annotations = mne.Annotations(
            onset=onset_list,
            duration=duration_list,
            description=description_list,
        )

        # Add response_time as description suffix for DIN1 events
        # (for super meta regression target)
        if response_times and onset_list:
            # Match response times to nearest DIN1 events
            rt_onsets = []
            rt_durations = []
            rt_descriptions = []

            for rt in response_times:
                # Find closest DIN1 onset
                closest_idx = None
                min_diff = float("inf")
                for i, (onset, desc) in enumerate(zip(onset_list, description_list)):
                    if desc == "DIN1":
                        diff = abs(rt - onset)
                        if diff < min_diff:
                            min_diff = diff
                            closest_idx = i

                if closest_idx is not None and min_diff < 5.0:  # Within 5 seconds
                    # Create super meta annotation with response_time
                    rt_onsets.append(onset_list[closest_idx])
                    rt_durations.append(0.0)
                    rt_descriptions.append(f"response_time:{rt:.4f}")

            if rt_onsets:
                rt_annotations = mne.Annotations(
                    onset=rt_onsets,
                    duration=rt_durations,
                    description=rt_descriptions,
                )
                annotations = annotations + rt_annotations

        raw.set_annotations(annotations)

        # =========================================================================
        # 9. Add trial_type annotations from events.tsv (super meta for classification)
        # =========================================================================
        if trial_type_map and onset_list:
            trial_onsets = []
            trial_durations = []
            trial_descriptions = []

            for onset, desc in zip(onset_list, description_list):
                if desc == "DIN1":
                    # Match to nearest trial_type
                    closest_trial = None
                    min_diff = float("inf")
                    for tsv_onset, trial_type in trial_type_map.items():
                        diff = abs(onset - tsv_onset)
                        if diff < min_diff:
                            min_diff = diff
                            closest_trial = trial_type

                    if closest_trial and min_diff < 1.0:  # Within 1 second
                        trial_onsets.append(onset)
                        trial_durations.append(0.0)
                        trial_descriptions.append(f"trial_type:{closest_trial}")

            if trial_onsets:
                trial_annotations = mne.Annotations(
                    onset=trial_onsets,
                    duration=trial_durations,
                    description=trial_descriptions,
                )
                raw.set_annotations(annotations + trial_annotations)

        print(f"[{self.KERNEL_ID}] Processed: {len(raw.ch_names)} channels, "
              f"{len(raw.annotations)} annotations")

        return raw


KERNEL = OpenNeuroDS002833Kernel()