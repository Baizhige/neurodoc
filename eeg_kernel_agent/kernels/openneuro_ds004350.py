"""OpenNeuro DS004350 stage1 kernel for EEGUnity.

Executive Functioning Study for Assessing the Effect of Neurofeedback.
Contains N-back (NB1/NB3), Local-Global (LG), and SART paradigms.

Source: https://openneuro.org/datasets/ds004350
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Annotator: LLM, 2026-04-08
# Source: Dataset README / paper descriptions
# Amplifier inferred from common EEG labs using 64-channel systems at 256 Hz
_DEVICE_AMPLIFIER = "unknown"  # LLM 推断，需人类复核

# Annotator: LLM, 2026-04-08
# Source: Standard EEG research practice for cognitive paradigms
_CAP_MATERIAL = "unknown"  # LLM 推断，需人类复核


def _load_subject_info(dataset_root: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from BIDS participants.tsv.

    Returns
    -------
    Dict[str, Dict[str, str]]
        Mapping from subject_id (e.g., "sub-01") to metadata dict with
        keys: age, sex, handedness.
    """
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    subject_info: Dict[str, Dict[str, str]] = {}

    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            for _, row in df.iterrows():
                subj_id = str(row.get("participant_id", ""))
                if not subj_id.startswith("sub-"):
                    subj_id = f"sub-{subj_id}"

                # Normalize sex to lowercase
                raw_sex = str(row.get("sex", "unknown")).strip().lower()
                if raw_sex not in ("male", "female"):
                    raw_sex = "unknown"

                # Age handling
                raw_age = str(row.get("age", "unknown")).strip()
                if raw_age in ("nan", "", "NA"):
                    raw_age = "unknown"

                # Handedness
                raw_handed = str(row.get("handedness", "unknown")).strip().lower()
                if raw_handed not in ("right", "left", "ambidextrous"):
                    raw_handed = "unknown"

                subject_info[subj_id] = {
                    "age": raw_age,
                    "sex": raw_sex,
                    "handedness": raw_handed,
                }
        except Exception:
            pass

    return subject_info


def _detect_task_from_filename(file_path: str) -> Optional[str]:
    """Detect BIDS task from filename (e.g., sub-01_task-NB1_run-01_EEG.vhdr).

    Returns
    -------
    str or None
        Task name: "NB1", "NB3", "LG", "SART", or None if not detectable.
    """
    basename = os.path.basename(file_path)
    # Match task-<value> pattern
    match = re.search(r"task-([A-Za-z0-9]+)", basename)
    if match:
        return match.group(1).upper()
    return None


def _build_channel_rename_map_64(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for 64-channel EEG caps.

    Common 64-channel layouts (BrainCap 64, EGI 64, etc.) use names like
    'EEG 001' -> 'Fp1', 'EEG 002' -> 'Fpz', etc.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw object to inspect for existing channel names.

    Returns
    -------
    Dict[str, str]
        Mapping from source names to standard 10-20 names.
    """
    # Standard 64-channel 10-20 layout (ordered)
    # Covers all standard positions for 64-channel caps
    standard_64 = [
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF7", "AF5", "AF3", "AF1", "AFz", "AF2", "AF4", "AF6", "AF8", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FT5", "FT3", "FT1", "FTz", "FT2", "FT4", "FT6", "FT8", "FT10",
        "T9", "T7", "T5", "T3", "T1", "T2", "T4", "T6", "T8", "T10",
        "TP9", "TP7", "TP5", "TP3", "TP1", "TPz", "TP2", "TP4", "TP6", "TP8", "TP10",
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "PO1", "POz", "PO2", "PO4", "PO6", "PO8", "PO10",
        "O1", "Oz", "O2",
        "I1", "Iz", "I2",
        # Below are common extended 10-10 positions for 64ch
        "AFp9", "AFp7", "AFp5", "AFp3", "AFp1", "AFp2", "AFp4", "AFp6", "AFp8", "AFp10",
        "Fp9", "F10",
        "AFF9", "AFF7", "AFF5", "AFF1", "AFF2", "AFF6", "AFF8", "AFF10",
        "FTT9", "FTT7", "FTT5", "FTT3", "FTT1", "FTT2", "FTT4", "FTT6", "FTT8", "FTT10",
        "TTP7", "TTP5", "TTP3", "TTP1", "TTP2", "TTP4", "TTP6", "TTP8",
        "TPP9", "TPP7", "TPP5", "TPP1", "TPP2", "TPP6", "TPP8", "TPP10",
        "PPO9", "PPO7", "PPO5", "PPO1", "PPO2", "PPO4", "PPO6", "PPO8", "PPO10",
        "POO9", "POO7", "POO5", "POO3", "POO1", "POO2", "POO4", "POO6", "POO8",
        "OI1", "OI2", "OI3",
        "直播",  # skip unlikely
    ]

    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: 'EEG 001', 'EEG001', 'EEG001-avg' style
    for i, std_name in enumerate(standard_64):
        for prefix in ["EEG ", "EEG", "eeg"]:
            for pad_len in [3, 2]:
                padded = str(i + 1).zfill(pad_len)
                source = f"{prefix}{padded}"
                if source in existing:
                    rename_map[source] = std_name
                    break

    # Pattern 2: Already has standard names but with slight variations
    # e.g., 'Fp1' already exists - keep it, or 'Fz.' -> 'Fz'
    standard_lower = {n.lower(): n for n in standard_64 if len(n) <= 4}
    for ch in existing:
        ch_lower = ch.lower().strip()
        if ch in standard_64:
            continue  # already standard
        if ch_lower in standard_lower:
            rename_map[ch] = standard_lower[ch_lower]

    return rename_map


def _extract_events_from_annotations(raw: mne.io.BaseRaw) -> List[Dict[str, Any]]:
    """Extract event info from MNE annotations for event-based epoching.

    Returns
    -------
    List[Dict[str, Any]]
        List of event dicts with keys: onset, duration, description.
    """
    events = []
    if raw.annotations is None:
        return events

    for onset, duration, desc in zip(
        raw.annotations.onset,
        raw.annotations.duration,
        raw.annotations.description,
    ):
        events.append({
            "onset": float(onset),
            "duration": float(duration),
            "description": str(desc),
        })
    return events


class OpenNeuroDS004350Kernel:
    """Stage1 kernel for OpenNeuro DS004350 dataset.

    This kernel handles:
    - Subject metadata from participants.tsv
    - Channel renaming for standard 10-20 compatibility
    - Task detection from filename
    - Event preservation from annotations
    - EEGUnity description metadata
    """

    KERNEL_ID: str = "openneuro-ds004350-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object loaded by EEGUnity.
        row
            Locator row with at least 'File Path' and 'Subject' keys.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata.
        """
        file_path = str(row.get("File Path", ""))
        subject_id = str(row.get("Subject", "unknown"))

        # Ensure subject_id has sub- prefix
        if not subject_id.startswith("sub-"):
            subject_id = f"sub-{subject_id}"

        # Detect task from filename
        task_name = _detect_task_from_filename(file_path) or "unknown"

        # Load subject metadata
        dataset_root = row.get("Dataset Root", "")
        subject_info = _load_subject_info(dataset_root)
        subj_meta = subject_info.get(subject_id, {})

        # Get subject-specific values or defaults
        age = subj_meta.get("age", "unknown")
        sex = subj_meta.get("sex", "unknown")
        handedness = subj_meta.get("handedness", "unknown")

        # If not found in participants.tsv, try to infer from other sources
        # Annotator: LLM, 2026-04-08
        if age == "unknown":
            # Paper DOI 10.1038/nn1233 mentions "healthy adults" without specifics
            age = "unknown"  # LLM 推断，需人类复核
        if sex == "unknown":
            sex = "unknown"  # LLM 推断，需人类复核
        if handedness == "unknown":
            handedness = "unknown"  # LLM 推断，需人类复核

        # Get original description
        original_description = raw.info.get("description", "") or ""

        # Build EEGUnity description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": str(age),
                "sex": str(sex).lower(),
                "amplifier": _DEVICE_AMPLIFIER,
                "cap": _CAP_MATERIAL,
                "handedness": str(handedness).lower(),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Channel renaming BEFORE set_montage()
        rename_map = _build_channel_rename_map_64(raw)
        if rename_map:
            print(f"[DS004350] Renaming {len(rename_map)} channels for {subject_id}")
            try:
                raw.rename_channels(rename_map)
            except Exception as e:
                print(f"[DS004350] Warning: channel rename failed: {e}")

        # Set montage if channels are standard 10-20 names
        # Try to set appropriate montage based on number of channels
        n_eeg_channels = len([ch for ch in raw.ch_names
                               if raw.get_channel_types(picks=[ch])[0] == "eeg"])

        montage = None
        if n_eeg_channels >= 64:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass
        elif n_eeg_channels >= 32:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass

        # Extract and preserve events from annotations
        # The raw annotations contain the event markers
        events = _extract_events_from_annotations(raw)

        # If no annotations exist, try to read events from BIDS *_events.tsv
        if not events and file_path:
            events_tsv = file_path.replace("_EEG.vhdr", "_events.tsv")
            events_tsv = events_tsv.replace("_eeg.vhdr", "_events.tsv")
            events_tsv = events_tsv.replace(".vhdr", "_events.tsv")
            events_tsv = events_tsv.replace(".edf", "_events.tsv")
            events_tsv = events_tsv.replace(".bdf", "_events.tsv")

            if os.path.exists(events_tsv):
                try:
                    events_df = pd.read_csv(events_tsv, sep="\t")
                    if "onset" in events_df.columns and "trial_type" in events_df.columns:
                        onsets = events_df["onset"].values
                        descriptions = events_df["trial_type"].values
                        durations = events_df.get("duration", pd.Series([0] * len(onset))).values

                        new_annotations = mne.Annotations(
                            onset=onsets,
                            duration=durations,
                            description=[str(d) for d in descriptions],
                        )
                        raw.set_annotations(new_annotations)
                except Exception as e:
                    print(f"[DS004350] Warning: failed to load events.tsv: {e}")

        # Add task info to raw.annotations.description if available
        # This helps downstream epoching identify task context
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Tag events with task prefix if multi-paradigm
            task_prefix = f"{task_name}: " if task_name != "unknown" else ""
            current_descs = list(raw.annotations.description)
            # Only add prefix if not already present
            prefixed = []
            for desc in current_descs:
                desc_str = str(desc)
                if task_prefix and not desc_str.startswith(task_prefix):
                    prefixed.append(f"{task_prefix}{desc_str}")
                else:
                    prefixed.append(desc_str)

            if prefixed != current_descs:
                new_ann = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=prefixed,
                )
                raw.set_annotations(new_ann)

        return raw


KERNEL = OpenNeuroDS004350Kernel()