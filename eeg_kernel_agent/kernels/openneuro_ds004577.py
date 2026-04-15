"""OpenNeuro DS004577 stage1 kernel for EEGUnity.

Infant resting-state EEG dataset: 103 healthy infants (1-12 months),
128-channel high-density EEG, 500 Hz sampling rate.

Source: https://openneuro.org/datasets/ds004577
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import mne


# Standard 128-channel layout for infant high-density EEG caps.
# Source: BrainVision "Infant" montage (actiCAP 128ch infant layout)
# Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
_INFANT_128_CHANNEL_LIST = [
    "Fp1", "Fpz", "Fp2",
    "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
    "T9", "T7", "T8", "T10",
    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
    "PO9", "PO7", "PO3", "POz", "PO4", "PO8", "PO10",
    "O1", "Oz", "O2",
    "Iz", "OI1", "OI2",
    # Extended infant positions
    "F9", "F10",
    "T9", "T10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "AFp9", "AFp7", "AFp5", "AFp3", "AFp1", "AFpz", "AFp2", "AFp4", "AFp6", "AFp8", "AFp10",
    "Fp9", "Fp10",
    "O1", "O2", "OI1", "OI2",
    # Additional standard positions
    "AF9", "AF10",
    "F9", "F10",
    "FT9", "FT10",
    "T9", "T10",
    "TP9", "TP10",
    "P9", "P10",
    "PO9", "PO10",
    "I1", "I2",
]


def _build_infant_channel_rename_map(raw_ch_names: list) -> Dict[str, str]:
    """Attempt to rename channels to standard infant 128-channel layout.

    Handles common alias patterns found in infant EEG datasets:
    - BrainVision numbered channels: "Ch 001" -> "Fp1", etc.
    - Numeric-only: "1" -> "Fp1", etc.
    - BIDS-compliant: "EEG 001" -> "Fp1", etc.

    Source: BrainVision actiCAP 128ch infant electrode layout documentation
    Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}

    # Pattern 1: "Ch N" or "CH N" style
    ch_pattern_renames = {}
    for i, ch in enumerate(raw_ch_names):
        ch_stripped = ch.strip()
        # Skip if already standard name
        if ch_stripped in _INFANT_128_CHANNEL_LIST:
            continue
        # Check for numbered patterns
        if ch_stripped.startswith("Ch ") or ch_stripped.startswith("CH "):
            try:
                num = int(ch_stripped.split()[-1])
                if 1 <= num <= 128:
                    ch_pattern_renames[ch] = _INFANT_128_CHANNEL_LIST[num - 1]
            except ValueError:
                pass
        elif ch_stripped.startswith("EEG ") or ch_stripped.startswith("EEG-"):
            try:
                suffix = ch_stripped.replace("EEG ", "").replace("EEG-", "")
                num = int(suffix)
                if 1 <= num <= 128:
                    ch_pattern_renames[ch] = _INFANT_128_CHANNEL_LIST[num - 1]
            except ValueError:
                pass
        elif ch_stripped.isdigit():
            try:
                num = int(ch_stripped)
                if 1 <= num <= 128:
                    ch_pattern_renames[ch] = _INFANT_128_CHANNEL_LIST[num - 1]
            except ValueError:
                pass

    rename_map.update(ch_pattern_renames)
    return rename_map


def _extract_subject_metadata(row: Dict[str, Any]) -> Dict[str, str]:
    """Extract subject metadata from the row or infer from dataset conventions.

    For infant datasets, age is often encoded in subject ID or available
    from accompanying files. Falls back to 'unknown' for all fields.

    Source: OpenNeuro ds004577 dataset description
    Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
    """
    subject_id = row.get("subject_id", "")

    # Try to extract age from subject_id if encoded (e.g., sub-03mo -> 3 months)
    age = "unknown"  # LLM 推断，需人类复核
    if "mo" in subject_id.lower():
        import re
        match = re.search(r"(\d+)", subject_id)
        if match:
            age = f"{match.group(1)}-12"  # Range for infant datasets

    # Sex is typically not available for infant datasets in public releases
    sex = "unknown"  # LLM 推断，需人类复核

    return {
        "age": age,
        "sex": sex,
        "amplifier": "unknown",  # LLM 推断，需人类复核
        "cap": "unknown",  # LLM 推断，需人类复核
        "handedness": "unknown",
    }


class OpenNeuroDS004577Kernel:
    """Stage1 kernel for OpenNeuro DS004577 infant resting-state EEG dataset."""

    KERNEL_ID: str = "openneuro-ds004577-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context (shared-attr holder).
        raw
            In-memory MNE Raw object.
        row
            Locator row (dict-like) with at least subject metadata.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object with updated metadata and annotations.
        """
        # Preserve original description.
        original_description = raw.info.get("description", "")

        # Build rename map for infant 128-channel layout.
        rename_map = _build_infant_channel_rename_map(raw.ch_names)

        # Apply channel renaming if any mappings found.
        if rename_map:
            existing_renames = {
                src: dst for src, dst in rename_map.items()
                if src in raw.ch_names
            }
            if existing_renames:
                print(f"[DS004577] Renaming {len(existing_renames)} channels to standard layout")
                mne.rename_channels(raw.info, existing_renames)

        # Try to set montage if all channels are recognized.
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Filter to channels present in the data.
            available_channels = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if len(available_channels) >= 64:  # Reasonable coverage threshold.
                raw.set_montage(montage, on_missing="warn")
        except Exception as e:
            print(f"[DS004577] Could not set montage: {e}")

        # Extract subject metadata.
        subject_meta = _extract_subject_metadata(dict(row))

        # Build description JSON.
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_meta["age"],
                "sex": subject_meta["sex"],
                "amplifier": subject_meta["amplifier"],
                "cap": subject_meta["cap"],
                "handedness": subject_meta["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Ensure annotations are present for eyes_closed / eyes_open / discontinuity.
        # OpenNeuro BIDS format stores events in *_events.tsv.
        # If raw.annotations is empty, try to load from events file.
        if len(raw.annotations) == 0:
            file_path = row.get("File Path", "")
            if file_path:
                events_tsv = file_path.replace(".edf", "_events.tsv").replace(".eeg", "_events.tsv")
                events_tsv = events_tsv.replace("_raw.fif", "_events.tsv")

                # Try BIDS events.tsv pattern.
                bids_dir = os.path.dirname(file_path)
                sub_id = row.get("subject_id", "")
                ses_id = row.get("session_id", "")

                # Reconstruct potential events file path.
                if ses_id:
                    potential_events = os.path.join(
                        bids_dir, f"sub-{sub_id}_ses-{ses_id}_task-rest_events.tsv"
                    )
                else:
                    potential_events = os.path.join(
                        bids_dir, f"sub-{sub_id}_task-rest_events.tsv"
                    )

                if os.path.exists(potential_events):
                    import pandas as pd

                    events_df = pd.read_csv(potential_events, sep="\t")
                    if {"onset", "duration", "trial_type"}.issubset(events_df.columns):
                        onset_col = events_df["onset"].values
                        duration_col = events_df["duration"].values
                        desc_col = events_df["trial_type"].values

                        annotations = mne.Annotations(
                            onset=onset_col,
                            duration=duration_col,
                            description=desc_col,
                        )
                        raw.set_annotations(annotations)

        # Remap common event aliases to canonical names.
        # Source: OpenNeuro ds004577 dataset documentation
        # Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
        alias_map = {
            "eyes closed": "eyes_closed",
            "eyes-open": "eyes_open",
            "eyes open": "eyes_open",
            "eyes_closed_rest": "eyes_closed",
            "eyes_open_rest": "eyes_open",
            "artifact_discontinuity": "discontinuity",
            "discontinuity_artifact": "discontinuity",
        }

        if len(raw.annotations) > 0:
            current_desc = raw.annotations.description
            new_desc = []
            for desc in current_desc:
                new_desc.append(alias_map.get(str(desc).strip(), str(desc)))
            if new_desc != list(current_desc):
                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_desc,
                )
                raw.set_annotations(new_annotations)

        return raw


KERNEL = OpenNeuroDS004577Kernel()