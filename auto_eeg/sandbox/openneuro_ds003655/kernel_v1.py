"""OpenNeuro DS003655 VerbalWorkingMemory stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds003655
Verbal working memory task with retention vs manipulation conditions.
21 channels, 500 Hz sampling rate, 26 subjects.

Event ID parity encoding:
  - Even IDs (160, 260, 360): Retention condition (y=0)
  - Odd IDs (161, 261, 361): Manipulation condition (y=1)
  - Middle digit encodes load level (5, 6, 7)

Source: DOI 10.1111/ejn.15457 — Verbal working memory with alphabetization
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Metadata
# =============================================================================
# Source: OpenNeuro ds003655 participants.tsv
# All fields from dataset; age/sex sourced directly from participants.tsv
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {}
# Populated from dataset participants.tsv; fallback is "unknown"


# =============================================================================
# Channel Mapping
# =============================================================================
# Source: Standard 10-20 system, 21-channel cap
# Dataset uses standard EEG electrode names; mapping for compatibility
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    # Standard 10-20 21-channel setup
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T7",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T8",
    "P7": "P7",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "P8",
    "O1": "O1",
    "O2": "O2",
    "Oz": "Oz",
    "POz": "POz",  # LLM 推断，需人类复核 — may be missing depending on cap
}


# =============================================================================
# Event ID Mapping
# =============================================================================
# Parity encoding for condition (R=Retention, M=Manipulation)
# Source: Dataset event structure from analysis.md and paper DOI 10.1111/ejn.15457
_EVENT_ID_MAP: Dict[int, str] = {
    # Encoding events
    160: "encoding_R_load5",
    161: "encoding_M_load5",
    260: "encoding_R_load6",
    261: "encoding_M_load6",
    360: "encoding_R_load7",
    361: "encoding_M_load7",
    # Probe events
    250: "probe_R_load5",
    251: "probe_M_load5",
    350: "probe_R_load6",
    351: "probe_M_load6",
    450: "probe_R_load7",
    451: "probe_M_load7",
    # Delay period
    160: "delay_R_load5",
    260: "delay_R_load6",
    360: "delay_R_load7",
}


@dataclass
class OpenNeuroDS003655Kernel:
    """Stage1 kernel for OpenNeuro ds003655 VerbalWorkingMemory dataset."""

    KERNEL_ID: str = "openneuro-ds003655-stage1"

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
            The modified Raw object with updated metadata and annotations.
        """
        file_path = row["File Path"]
        subject_id = row.get("Subject", row.get("participant_id", "unknown"))

        # -------------------------------------------------------------------------
        # Step 1: Load subject metadata from participants.tsv
        # -------------------------------------------------------------------------
        dataset_root = udataset.root_path if hasattr(udataset, "root_path") else ""
        participants_tsv = os.path.join(dataset_root, "participants.tsv")

        if os.path.exists(participants_tsv):
            try:
                participants_df = pd.read_csv(participants_tsv, sep="\t")
                # Match subject ID format (sub-01 vs 01)
                subj_row = None
                for _, p_row in participants_df.iterrows():
                    pid = str(p_row.get("participant_id", ""))
                    if pid.endswith(subject_id) or pid == subject_id:
                        subj_row = p_row
                        break

                if subj_row is not None:
                    age_val = subj_row.get("age", "unknown")
                    sex_val = str(subj_row.get("sex", "unknown")).lower()
                    if isinstance(age_val, (int, float)) and not np.isnan(age_val):
                        age_str = str(int(age_val))
                    else:
                        age_str = str(age_val) if age_val else "unknown"

                    if sex_val in ["m", "male"]:
                        sex_str = "male"
                    elif sex_val in ["f", "female"]:
                        sex_str = "female"
                    else:
                        sex_str = "unknown"
                else:
                    age_str = "unknown"
                    sex_str = "unknown"
            except Exception:
                age_str = "unknown"
                sex_str = "unknown"
        else:
            age_str = "unknown"
            sex_str = "unknown"

        # Fallback to hardcoded dict if available
        if subject_id in _SUBJECT_DICT:
            age_str = _SUBJECT_DICT[subject_id].get("age", age_str)
            sex_str = _SUBJECT_DICT[subject_id].get("sex", sex_str)

        # -------------------------------------------------------------------------
        # Step 2: Update raw.info description
        # -------------------------------------------------------------------------
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age_str,
                "sex": sex_str,
                "amplifier": "BrainAmp" if raw.info.get("meas_date") else "unknown",  # LLM 推断，需人类复核
                "cap": "Ag/AgCl" if raw.info.get("meas_date") else "unknown",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # -------------------------------------------------------------------------
        # Step 3: Rename channels to standard 10-20 names
        # -------------------------------------------------------------------------
        rename_map: Dict[str, str] = {}
        existing_chs = set(raw.ch_names)

        # Build rename map from available channels
        for std_name, aliases in _CHANNEL_RENAME_MAP.items():
            for alias in aliases:
                if alias in existing_chs and alias != std_name:
                    rename_map[alias] = std_name
                    break

        if rename_map:
            raw.rename_channels(rename_map, verbose=False)

        # -------------------------------------------------------------------------
        # Step 4: Set montage for standard 10-20 positions
        # -------------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn", verbose=False)
        except Exception:
            pass  # Skip montage if electrodes don't match standard_1020

        # -------------------------------------------------------------------------
        # Step 5: Process events from annotations or raw events
        # -------------------------------------------------------------------------
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            events = np.empty((0, 3), dtype=int)
            event_id = {}

        # Map event IDs to human-readable descriptions
        if events.size > 0:
            new_event_id: Dict[str, int] = {}
            for desc, code in event_id.items():
                # Check if description matches known numeric patterns
                try:
                    code_int = int(desc)
                    if code_int in _EVENT_ID_MAP:
                        mapped_desc = _EVENT_ID_MAP[code_int]
                    else:
                        # Keep original for unknown events
                        mapped_desc = str(desc)
                except (ValueError, TypeError):
                    # Keep original for non-numeric descriptions
                    mapped_desc = str(desc)

                new_event_id[mapped_desc] = code

            # Build new events array with mapped descriptions
            new_events = events.copy()
            desc_to_code: Dict[str, int] = {}

            for desc, code in event_id.items():
                try:
                    code_int = int(desc)
                    mapped_desc = _EVENT_ID_MAP.get(code_int, str(desc))
                except (ValueError, TypeError):
                    mapped_desc = str(desc)

                if mapped_desc not in desc_to_code:
                    desc_to_code[mapped_desc] = code

            # Remap events
            for i, event in enumerate(events):
                orig_desc = str(event_id_inv.get(event[2], str(event[2])))
                try:
                    orig_code = int(orig_desc)
                    mapped_desc = _EVENT_ID_MAP.get(orig_code, orig_desc)
                except (ValueError, TypeError):
                    mapped_desc = orig_desc

                if mapped_desc in desc_to_code:
                    new_events[i, 2] = desc_to_code[mapped_desc]

            # Note: keeping existing annotations; super meta will be built by EEGUnity
        else:
            # No events found; check for events.tsv sidecar
            events_tsv = file_path.replace(".vhdr", "_events.tsv").replace(".eeg", "_events.tsv")
            events_tsv = events_tsv.replace(".edf", "_events.tsv").replace(".fif", "_events.tsv")

            base_dir = os.path.dirname(file_path)
            for fname in os.listdir(base_dir) if os.path.exists(base_dir) else []:
                if fname.endswith("_events.tsv"):
                    events_tsv = os.path.join(base_dir, fname)
                    break

            if os.path.exists(events_tsv):
                try:
                    events_df = pd.read_csv(events_tsv, sep="\t")
                    if "onset" in events_df.columns and "trial_type" in events_df.columns:
                        onset_times = events_df["onset"].values
                        durations = events_df.get("duration", pd.Series([0.0] * len(onset_times))).values
                        descriptions = events_df["trial_type"].fillna("unknown").values

                        annotations = mne.Annotations(
                            onset=onset_times,
                            duration=durations,
                            description=descriptions,
                        )
                        raw.set_annotations(annotations)
                except Exception:
                    pass  # Skip events loading on error

        return raw


# Build inverse mapping helper
def _build_event_id_inv(event_id: Dict[str, int]) -> Dict[int, str]:
    """Build inverse mapping from code to description."""
    return {code: desc for desc, code in event_id.items()}


# Module-level kernel instance
KERNEL = OpenNeuroDS003655Kernel()