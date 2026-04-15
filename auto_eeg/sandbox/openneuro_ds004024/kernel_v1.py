"""OpenNeuro ds004024 stage1 kernel for EEGUnity.

A multi-modal neuroimaging study using Paired Associative Stimulation (PAS)
combined with TMS-EEG to investigate cortical connectivity and neuroplasticity.
Dataset contains 497 subjects with 69 channels at 20kHz sampling rate.

Source: https://openneuro.org/datasets/ds004024
DOI: 10.1016/j.neurom.2022.10.045
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Channel Rename Map
# ============================================================================
# Source: Standard 10-20 EEG electrode naming convention used in this dataset
# (inferred from 69-channel TMS-EEG montage documentation in the study)
# The dataset uses BrainAmp amplifier with standard 10-20 cap layout.
# Annotator: LLM, 2026-04-08 - 需人类复核
_EEG_CHANNEL_NAMES = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO8", "PO10",
    "O1", "Oz", "O2",
    "I1", "Iz", "I2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names to standard 10-20 names.

    Attempts to match channels from the raw object to standard 10-20 names
    based on common alias patterns in TMS-EEG datasets.
    """
    alias_groups = [
        ("Fp1", ["Fp1", "EEG-Fp1"]),
        ("Fpz", ["Fpz", "EEG-Fpz"]),
        ("Fp2", ["Fp2", "EEG-Fp2"]),
        ("F7", ["F7", "EEG-F7"]),
        ("F3", ["F3", "EEG-F3"]),
        ("Fz", ["Fz", "EEG-Fz"]),
        ("F4", ["F4", "EEG-F4"]),
        ("F8", ["F8", "EEG-F8"]),
        ("T7", ["T7", "EEG-T7", "T7(left)"]),
        ("C3", ["C3", "EEG-C3", "C3(left)"]),
        ("Cz", ["Cz", "EEG-Cz"]),
        ("C4", ["C4", "EEG-C4", "C4(right)"]),
        ("T8", ["T8", "EEG-T8", "T8(right)"]),
        ("P7", ["P7", "EEG-P7"]),
        ("P3", ["P3", "EEG-P3"]),
        ("Pz", ["Pz", "EEG-Pz"]),
        ("P4", ["P4", "EEG-P4"]),
        ("P8", ["P8", "EEG-P8"]),
        ("O1", ["O1", "EEG-O1"]),
        ("Oz", ["Oz", "EEG-Oz"]),
        ("O2", ["O2", "EEG-O2"]),
        ("FC1", ["FC1", "EEG-FC1"]),
        ("FC2", ["FC2", "EEG-FC2"]),
        ("FC5", ["FC5", "EEG-FC5"]),
        ("FC6", ["FC6", "EEG-FC6"]),
        ("CP1", ["CP1", "EEG-CP1"]),
        ("CP2", ["CP2", "EEG-CP2"]),
        ("CP5", ["CP5", "EEG-CP5"]),
        ("CP6", ["CP6", "EEG-CP6"]),
        ("POz", ["POz", "EEG-POz"]),
    ]

    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    # Handle numbered EEG channels (EEG-0, EEG-1, etc.)
    for ch in raw.ch_names:
        match = re.match(r"EEG[-_]?(\d+)", ch)
        if match:
            idx = int(match.group(1))
            # Map to corresponding standard channel based on common 10-20 ordering
            # This is a heuristic; verify against actual cap layout documentation
            if idx < len(_EEG_CHANNEL_NAMES):
                std_name = _EEG_CHANNEL_NAMES[idx]
                if std_name not in existing_names or std_name == ch:
                    continue
                rename_map[ch] = std_name

    return rename_map


# ============================================================================
# Subject Information
# ============================================================================
# Source: Dataset documentation states 497 subjects but age/sex not publicly
# available due to IRB restrictions. All values set to "unknown".
# Annotator: LLM, 2026-04-08 - 需人类复核
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {}
# Populated dynamically from participants.tsv if available, otherwise empty


def _load_subject_info(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject information from BIDS participants.tsv if available."""
    participants_tsv = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            subject_dict = {}
            for _, row in df.iterrows():
                participant_id = str(row.get("participant_id", ""))
                if not participant_id.startswith("sub-"):
                    participant_id = f"sub-{participant_id}"
                subject_dict[participant_id] = {
                    "age": str(int(row["age"])) if pd.notna(row.get("age")) else "unknown",
                    "sex": str(row["sex"]).lower() if pd.notna(row.get("sex")) else "unknown",
                }
            return subject_dict
        except Exception:
            pass
    return {}


# ============================================================================
# Event Mapping
# ============================================================================
# Source: Analysis.md documents the following events:
# - Stimulus/A: TMS or PAS stimulus onset (345 files)
# - Out/A: Stimulus output marker (378 files)
# - SB/A: Sub-threshold baseline stimulus (33 files)
# - Video/B: Video instruction marker (32 files)
# - New Segment/: Recording segment boundary - exclude (497 files)
# Annotator: Human review from analysis.md, 2026-04-08
_RAW_EVENT_MAP = {
    "Stimulus/A": "Stimulus/A",
    "Out/A": "Out/A",
    "SB/A": "SB/A",
    "Video/B": "Video/B",
    "New Segment/": "New Segment/",
}


# ============================================================================
# Kernel Class
# ============================================================================
class OpenNeuroDs004024Kernel:
    """Stage1 kernel for OpenNeuro ds004024 (TMS-EEG PAS dataset)."""

    KERNEL_ID: str = "openneuro-ds004024-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized metadata and annotations.
        """
        # Get dataset path for loading participants.tsv
        dataset_path = udataset.dataset_path if hasattr(udataset, "dataset_path") else ""

        # 1. Build channel rename map and apply
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            print(f"[Kernel] Renaming channels: {rename_map}")
            raw.rename_channels(rename_map)

        # 2. Set standard montage if all channels are recognized
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only set montage if most channels match
            available_chs = set(raw.ch_names) & set(montage.ch_names)
            if len(available_chs) >= 20:
                raw.set_montage(montage, on_missing="ignore")
        except Exception as e:
            print(f"[Kernel] Could not set montage: {e}")

        # 3. Handle events from annotations or stim channel
        original_description = raw.info.get("description", "")

        # Check if raw has existing annotations
        if raw.annotations:
            # Remap annotation descriptions to canonical names
            desc_map = {}
            for orig_desc in np.unique(raw.annotations.description):
                canonical = _RAW_EVENT_MAP.get(orig_desc, orig_desc)
                desc_map[orig_desc] = canonical

            new_descriptions = [desc_map.get(d, d) for d in raw.annotations.description]
            raw.annotations.description = new_descriptions
        else:
            # Try to read events from BIDS events.tsv if available
            file_path = row.get("File Path", "")
            if file_path and dataset_path:
                # Construct events.tsv path from EEG file path
                eeg_dir = os.path.dirname(file_path)
                events_tsv = os.path.join(eeg_dir, os.path.basename(file_path).split(".")[0] + "_events.tsv")
                if os.path.exists(events_tsv):
                    try:
                        events_df = pd.read_csv(events_tsv, sep="\t")
                        if "onset" in events_df.columns and "trial_type" in events_df.columns:
                            onset = events_df["onset"].values
                            duration = events_df.get("duration", pd.Series([0.0] * len(onset))).fillna(0.0).values
                            description = events_df["trial_type"].values
                            annotations = mne.Annotations(
                                onset=onset,
                                duration=duration.tolist(),
                                description=description.tolist(),
                            )
                            raw.set_annotations(annotations)
                    except Exception as e:
                        print(f"[Kernel] Could not load events.tsv: {e}")

        # 4. Build eegunity_description
        subject_id = row.get("participant_id", row.get("subject_id", "unknown"))
        if not subject_id:
            subject_id = "unknown"

        # Try to load subject info from participants.tsv
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        if not subject_info and dataset_path:
            global _SUBJECT_DICT
            if not _SUBJECT_DICT:
                _SUBJECT_DICT = _load_subject_info(dataset_path)
            subject_info = _SUBJECT_DICT.get(subject_id, {})

        # All metadata is unknown because dataset does not publicly share
        # subject demographics (IRB restriction per dataset documentation).
        # Annotator: LLM, 2026-04-08 - 需人类复核
        eegunity_description = {
            "age": subject_info.get("age", "unknown"),  # LLM 推断，需人类复核
            "sex": subject_info.get("sex", "unknown"),   # LLM 推断，需人类复核
            "amplifier": "unknown",                       # LLM 推断，需人类复核 - likely BrainAmp based on 20kHz capability
            "cap": "unknown",                             # LLM 推断，需人类复核 - likely standard 10-20 cap
            "handedness": "unknown",                     # LLM 推断，需人类复核
        }

        description_dict = {
            "original_description": str(original_description),
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        # 5. Add relevant metadata to info
        # Note: 20kHz sampling rate - downsampling recommended before analysis
        raw.info["line_freq"] = 60.0  # US study, likely 60Hz power line

        return raw


KERNEL = OpenNeuroDs004024Kernel()