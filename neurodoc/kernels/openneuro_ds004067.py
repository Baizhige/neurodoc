"""OpenNeuro DS004067 stage1 kernel for EEGUnity.

Dataset: Moral conviction and metacognitive ability shape multiple stages
of information processing.

Source: https://openneuro.org/datasets/ds004067
        DOI: https://doi.org/10.1016/j.cortex.2022.03.008

Task Events (raw meta):
- Stimulus/PhotoSupport, Stimulus/PhotoOppose (Photo Valence Classification)
- Stimulus/SocLow, Stimulus/SocMed, Stimulus/SocHigh (Social Influence)
- Stimulus/Moral_Support, Stimulus/Moral_Oppose, Stimulus/Moral_Neutral
- Stimulus/Nonmoral_Support, Stimulus/Nonmoral_Oppose, Stimulus/Nonmoral_Neutral
- Resp1-Resp5 (rating responses)
- Admin markers: ProtestStart/End, RestStart/End, ClipTaskStart/End, etc.

Classical Tasks Supported:
1. Photo Valence Classification (Support vs Oppose)
2. Social Influence Level Classification (High/Med/Low)
3. Moral Attitude Classification (6-class)
4. Full Trial Information Processing Pipeline

Note: 63-channel EEG recorded at 2000 Hz from BrainAmp amplifier.
       inferred by LLM, needs human review for device-specific metadata.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Subject Metadata
# Source: participants.tsv (BIDS sidecar from OpenNeuro)
# Annotator: LLM, 2026-04-08 — needs human review
# ---------------------------------------------------------------------------
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    # Format: "sub-XXX": {"age": str, "sex": str, "handedness": str}
    # Populated from participants.tsv at runtime; fallback defaults below.
}


def _load_subject_metadata(dataset_root: str) -> Dict[str, Dict[str, Any]]:
    """Load subject metadata from participants.tsv if available."""
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    subject_dict: Dict[str, Dict[str, Any]] = {}

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            for _, row in df.iterrows():
                participant_id = str(row.get("participant_id", ""))
                if not participant_id.startswith("sub-"):
                    participant_id = f"sub-{participant_id}"

                # Extract age
                age_val = row.get("age", "unknown")
                if isinstance(age_val, (int, float)) and not np.isnan(age_val):
                    age_str = str(int(age_val))
                elif isinstance(age_val, str) and age_val.strip():
                    age_str = age_val.strip()
                else:
                    age_str = "unknown"

                # Extract sex
                sex_val = row.get("sex", "unknown")
                if isinstance(sex_val, str):
                    sex_lower = sex_val.lower().strip()
                    if sex_lower in ("m", "male"):
                        sex_str = "male"
                    elif sex_lower in ("f", "female"):
                        sex_str = "female"
                    else:
                        sex_str = "unknown"
                else:
                    sex_str = "unknown"

                # Extract handedness
                hand_val = row.get("handedness", row.get("hand", "unknown"))
                if isinstance(hand_val, str):
                    hand_lower = hand_val.lower().strip()
                    if hand_lower in ("r", "right", "right-handed"):
                        hand_str = "right"
                    elif hand_lower in ("l", "left", "left-handed"):
                        hand_str = "left"
                    else:
                        hand_str = "unknown"
                else:
                    hand_str = "unknown"

                subject_dict[participant_id] = {
                    "age": age_str,
                    "sex": sex_str,
                    "handedness": hand_str,
                }
        except Exception:
            pass

    return subject_dict


# ---------------------------------------------------------------------------
# Channel Rename Map
# Source: Standard 64-channel BrainCap (62 EEG + 2 EOG)
# 63 channels used in this dataset (possibly missing some standard positions)
# Annotator: LLM, 2026-04-08 — needs human review
# ---------------------------------------------------------------------------
_EEG_CHANNEL_NAMES = {
    "Fp1", "Fp2", "Fpz", "F7", "F3", "Fz", "F4", "F8",
    "FC5", "FC1", "FC2", "FC6",
    "T7", "C3", "Cz", "C4", "T8",
    "CP5", "CP1", "CP2", "CP6",
    "P7", "P3", "Pz", "P4", "P8",
    "PO3", "POz", "PO4",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC3", "FC4",
    "C5", "C1", "C2", "C6",
    "CP3", "CP4",
    "P5", "P1", "P2", "P6",
    "PO5", "PO6",
    "EOG-left", "EOG-right", "EOG-central",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map based on standard 10-20 naming."""
    alias_groups = [
        ("Fp1", ["EEG-Fp1", "Fp1", "FP1"]),
        ("Fp2", ["EEG-Fp2", "Fp2", "FP2"]),
        ("Fpz", ["EEG-Fpz", "Fpz", "FPz"]),
        ("F7", ["EEG-F7", "F7"]),
        ("F3", ["EEG-F3", "F3"]),
        ("Fz", ["EEG-Fz", "Fz"]),
        ("F4", ["EEG-F4", "F4"]),
        ("F8", ["EEG-F8", "F8"]),
        ("FC5", ["EEG-FC5", "FC5"]),
        ("FC1", ["EEG-FC1", "FC1"]),
        ("FC2", ["EEG-FC2", "FC2"]),
        ("FC6", ["EEG-FC6", "FC6"]),
        ("T7", ["EEG-T7", "T7", "TP7"]),
        ("C3", ["EEG-C3", "C3"]),
        ("Cz", ["EEG-Cz", "Cz"]),
        ("C4", ["EEG-C4", "C4"]),
        ("T8", ["EEG-T8", "T8", "TP8"]),
        ("CP5", ["EEG-CP5", "CP5"]),
        ("CP1", ["EEG-CP1", "CP1"]),
        ("CP2", ["EEG-CP2", "CP2"]),
        ("CP6", ["EEG-CP6", "CP6"]),
        ("P7", ["EEG-P7", "P7"]),
        ("P3", ["EEG-P3", "P3"]),
        ("Pz", ["EEG-Pz", "Pz"]),
        ("P4", ["EEG-P4", "P4"]),
        ("P8", ["EEG-P8", "P8"]),
        ("PO3", ["EEG-PO3", "PO3"]),
        ("POz", ["EEG-POz", "POz"]),
        ("PO4", ["EEG-PO4", "PO4"]),
        ("O1", ["EEG-O1", "O1"]),
        ("Oz", ["EEG-Oz", "Oz"]),
        ("O2", ["EEG-O2", "O2"]),
        ("AF7", ["EEG-AF7", "AF7"]),
        ("AF3", ["EEG-AF3", "AF3"]),
        ("AF4", ["EEG-AF4", "AF4"]),
        ("AF8", ["EEG-AF8", "AF8"]),
        ("F5", ["EEG-F5", "F5"]),
        ("F1", ["EEG-F1", "F1"]),
        ("F2", ["EEG-F2", "F2"]),
        ("F6", ["EEG-F6", "F6"]),
        ("FC3", ["EEG-FC3", "FC3"]),
        ("FC4", ["EEG-FC4", "FC4"]),
        ("C5", ["EEG-C5", "C5"]),
        ("C1", ["EEG-C1", "C1"]),
        ("C2", ["EEG-C2", "C2"]),
        ("C6", ["EEG-C6", "C6"]),
        ("CP3", ["EEG-CP3", "CP3"]),
        ("CP4", ["EEG-CP4", "CP4"]),
        ("P5", ["EEG-P5", "P5"]),
        ("P1", ["EEG-P1", "P1"]),
        ("P2", ["EEG-P2", "P2"]),
        ("P6", ["EEG-P6", "P6"]),
        ("PO5", ["EEG-PO5", "PO5"]),
        ("PO6", ["EEG-PO6", "PO6"]),
        ("EOG-left", ["EOG-left", "EOGV", "VEO"]),
        ("EOG-right", ["EOG-right", "EOG-R"]),
        ("EOG-central", ["EOG-central", "EOG-C", "HEO"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


# ---------------------------------------------------------------------------
# Event ID Mapping (raw meta)
# Source: analysis.md / OpenNeuro dataset_description.json
# Annotator: Human, 2026-04-08
# ---------------------------------------------------------------------------
_EVENT_ID_MAP: Dict[str, int] = {
    "Stimulus/PhotoSupport": 1,
    "Stimulus/PhotoOppose": 2,
    "Stimulus/SocLow": 3,
    "Stimulus/SocMed": 4,
    "Stimulus/SocHigh": 5,
    "Stimulus/Moral_Support": 6,
    "Stimulus/Moral_Oppose": 7,
    "Stimulus/Moral_Neutral": 8,
    "Stimulus/Nonmoral_Support": 9,
    "Stimulus/Nonmoral_Oppose": 10,
    "Stimulus/Nonmoral_Neutral": 11,
    "Stimulus/Resp1": 12,
    "Stimulus/Resp2": 13,
    "Stimulus/Resp3": 14,
    "Stimulus/Resp4": 15,
    "Stimulus/Resp5": 16,
    "Stimulus/ProtestStart": 90,
    "Stimulus/ProtestEnd": 91,
    "Stimulus/RestStart": 92,
    "Stimulus/RestEnd": 93,
    "Stimulus/ClipTaskStart": 94,
    "Stimulus/ClipTaskEnd": 95,
    "Stimulus/S 2": 99,
    "admin: marker-unknown": 0,
}


def _build_events_annotations(
    raw: mne.io.BaseRaw,
    events_tsv: Optional[str] = None,
) -> mne.Annotations:
    """Build MNE annotations from events.tsv or raw annotations.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw EEG object.
    events_tsv : str, optional
        Path to *_events.tsv file if available.

    Returns
    -------
    mne.Annotations
        Annotations with standardized event descriptions.
    """
    onset_list: List[float] = []
    duration_list: List[float] = []
    description_list: List[str] = []

    # Try to load events from events.tsv first (BIDS format)
    if events_tsv and os.path.exists(events_tsv):
        try:
            events_df = pd.read_csv(events_tsv, sep="\t")
            if "onset" in events_df.columns and "value" in events_df.columns:
                for _, row in events_df.iterrows():
                    onset = float(row["onset"])
                    duration = float(row.get("duration", 0.0))
                    value = str(row.get("value", row.get("trial_type", "")))

                    # Map value to standardized description
                    description = _map_event_value(value)
                    onset_list.append(onset)
                    duration_list.append(duration)
                    description_list.append(description)
        except Exception:
            pass

    # Fall back to raw.annotations if no events loaded
    if not onset_list and raw.annotations:
        for idx in range(len(raw.annotations)):
            onset_list.append(raw.annotations.onset[idx])
            duration_list.append(raw.annotations.duration[idx])
            description_list.append(_map_event_value(raw.annotations.description[idx]))

    # If still no events, try mne.events_from_annotations
    if not onset_list:
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            for event in events:
                onset_list.append(float(event[0]) / raw.info["sfreq"])
                duration_list.append(0.0)
                description_list.append(_map_event_value(str(event[2])))
        except Exception:
            pass

    # Default to empty annotations if nothing found
    if not onset_list:
        return mne.Annotations(onset=[], duration=[], description=[])

    return mne.Annotations(
        onset=np.array(onset_list),
        duration=np.array(duration_list),
        description=np.array(description_list),
    )


def _map_event_value(value: str) -> str:
    """Map raw event value to standardized event description."""
    value_str = str(value).strip()

    # Direct mappings
    if value_str in _EVENT_ID_MAP:
        for desc, code in _EVENT_ID_MAP.items():
            if code == _EVENT_ID_MAP.get(value_str, -1):
                return desc

    # Pattern-based mapping
    if "PhotoSupport" in value_str or "photo_s" in value_str.lower():
        return "Stimulus/PhotoSupport"
    if "PhotoOppose" in value_str or "photo_o" in value_str.lower():
        return "Stimulus/PhotoOppose"
    if "SocLow" in value_str or "soc_low" in value_str.lower():
        return "Stimulus/SocLow"
    if "SocMed" in value_str or "soc_med" in value_str.lower() or "SocMedium" in value_str:
        return "Stimulus/SocMed"
    if "SocHigh" in value_str or "soc_high" in value_str.lower():
        return "Stimulus/SocHigh"
    if "Moral_Support" in value_str:
        return "Stimulus/Moral_Support"
    if "Moral_Oppose" in value_str:
        return "Stimulus/Moral_Oppose"
    if "Moral_Neutral" in value_str:
        return "Stimulus/Moral_Neutral"
    if "Nonmoral_Support" in value_str:
        return "Stimulus/Nonmoral_Support"
    if "Nonmoral_Oppose" in value_str:
        return "Stimulus/Nonmoral_Oppose"
    if "Nonmoral_Neutral" in value_str:
        return "Stimulus/Nonmoral_Neutral"
    if value_str.startswith("Resp") or "resp" in value_str.lower():
        # Extract rating number
        import re
        match = re.search(r'\d+', value_str)
        if match:
            num = match.group()
            return f"Stimulus/Resp{num}"
        return "Stimulus/RespUnknown"
    if "ProtestStart" in value_str or "BlockStart" in value_str:
        return "Stimulus/ProtestStart"
    if "ProtestEnd" in value_str or "BlockEnd" in value_str:
        return "Stimulus/ProtestEnd"
    if "RestStart" in value_str:
        return "Stimulus/RestStart"
    if "RestEnd" in value_str:
        return "Stimulus/RestEnd"
    if "ClipTaskStart" in value_str:
        return "Stimulus/ClipTaskStart"
    if "ClipTaskEnd" in value_str:
        return "Stimulus/ClipTaskEnd"
    if "Social" in value_str and ("start" in value_str.lower() or "end" in value_str.lower()):
        return f"admin: {value_str}"
    if "Heroic" in value_str and ("start" in value_str.lower() or "end" in value_str.lower()):
        return f"admin: {value_str}"
    if value_str.strip() in ("S 2", "S2", "sync"):
        return "Stimulus/S 2"

    # Unknown marker
    return f"admin: {value_str}"


# ---------------------------------------------------------------------------
# Super Meta Label Definitions
# Source: analysis.md Tasks section
# Annotator: LLM, 2026-04-08 — needs human review
# ---------------------------------------------------------------------------

# Task 1: Photo Valence Classification
_TASK1_EVENT_ID = {
    "Stimulus/PhotoSupport": 0,
    "Stimulus/PhotoOppose": 1,
}

# Task 2: Social Influence Level Classification
_TASK2_EVENT_ID = {
    "Stimulus/SocLow": 0,
    "Stimulus/SocMed": 1,
    "Stimulus/SocHigh": 2,
}

# Task 3: Moral Attitude Classification (6-class)
_TASK3_EVENT_ID = {
    "Stimulus/Moral_Support": 0,
    "Stimulus/Moral_Oppose": 1,
    "Stimulus/Moral_Neutral": 2,
    "Stimulus/Nonmoral_Support": 3,
    "Stimulus/Nonmoral_Oppose": 4,
    "Stimulus/Nonmoral_Neutral": 5,
}


# ---------------------------------------------------------------------------
# Kernel Class
# ---------------------------------------------------------------------------

class OpenNeuroDS004067Kernel:
    """Stage1 kernel for OpenNeuro DS004067 dataset.

    Parameters
    ----------
    udataset : EEGUnity dataset context.
    raw : mne.io.BaseRaw
        Raw EEG object to process.
    row : pandas.Series
        Locator row with dataset information.

    Returns
    -------
    mne.io.BaseRaw
        Processed raw EEG object with standardized metadata and annotations.
    """

    KERNEL_ID: str = "openneuro-ds004067-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (pandas.Series-like) with dataset/file information.

        Returns
        -------
        mne.io.BaseRaw
            The modified raw object with standardized metadata.
        """
        # Determine dataset root path
        file_path = row.get("File Path", "")
        dataset_root = row.get("Dataset Root", os.path.dirname(os.path.dirname(file_path)))

        # -----------------------------------------------------------------
        # Step 1: Channel Renaming
        # Must be done BEFORE set_montage()
        # -----------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[DS004067] Renaming {len(rename_map)} channels: {list(rename_map.keys())}")
            raw.rename_channels(rename_map)

        # -----------------------------------------------------------------
        # Step 2: Set Montage (standard 10-20 system)
        # -----------------------------------------------------------------
        existing_ch_names = set(raw.ch_names)
        try:
            # Try to set standard 1020 montage
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only pick channels that exist in both raw and montage
            common_channels = list(set(montage.ch_names) & existing_ch_names)
            if common_channels:
                raw.set_montage(montage, on_missing="ignore")
                print(f"[DS004067] Montage set with {len(common_channels)} channels")
        except Exception as e:
            print(f"[DS004067] Could not set montage: {e}")

        # -----------------------------------------------------------------
        # Step 3: Load Subject Metadata
        # -----------------------------------------------------------------
        subject_id = row.get("Subject ID", row.get("participant_id", "unknown"))
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"

        # Load from participants.tsv
        subject_dict = _load_subject_metadata(dataset_root)
        if subject_id in subject_dict:
            age = subject_dict[subject_id].get("age", "unknown")
            sex = subject_dict[subject_id].get("sex", "unknown")
            handedness = subject_dict[subject_id].get("handedness", "unknown")
        else:
            age = "unknown"
            sex = "unknown"
            handedness = "unknown"

        # -----------------------------------------------------------------
        # Step 4: Build Annotations from events.tsv
        # -----------------------------------------------------------------
        # Try to find events.tsv in same directory as EEG file
        eeg_dir = os.path.dirname(file_path)
        events_tsv = None
        for fname in os.listdir(eeg_dir):
            if fname.endswith("_events.tsv"):
                events_tsv = os.path.join(eeg_dir, fname)
                break

        annotations = _build_events_annotations(raw, events_tsv)
        raw.set_annotations(annotations)

        # -----------------------------------------------------------------
        # Step 5: Set Description (eegunity_description)
        # -----------------------------------------------------------------
        # Amplifier: BrainAmp (inferred from 2000Hz sampling rate typical for BrainAmp)
        # Source: inferred by LLM, needs human review
        amplifier = "BrainAmp"  # inferred by LLM, needs human review
        cap = "Ag/AgCl"  # inferred by LLM, needs human review

        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -----------------------------------------------------------------
        # Step 6: Print Summary
        # -----------------------------------------------------------------
        print(f"[DS004067] Subject: {subject_id}")
        print(f"[DS004067] Age: {age}, Sex: {sex}, Handedness: {handedness}")
        print(f"[DS004067] Amplifier: {amplifier}, Cap: {cap}")
        print(f"[DS004067] Channels: {len(raw.ch_names)}")
        print(f"[DS004067] Sampling Rate: {raw.info['sfreq']} Hz")
        print(f"[DS004067] Annotations: {len(raw.annotations)} events")
        print(f"[DS004067] Description set successfully")

        return raw


# Module-level kernel instance
KERNEL = OpenNeuroDS004067Kernel()