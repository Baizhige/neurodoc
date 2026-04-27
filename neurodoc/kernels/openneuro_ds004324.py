"""ToonFaces (openneuro_ds004324) stage1 kernel for EEGUnity.

Dataset: OpenNeuro ds004324 | Year: 2023
Paradigm: RSVP face stimuli (real photo, toon, schematic) at 5 intensity levels
38 EEG channels, 500 Hz sampling rate, 26 subjects

Source: https://openneuro.org/datasets/ds004324
Reference: DOI 10.3389/fnhum.2023.1160800
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# Default values when not available from participants.tsv
# Source: analysis.md Info section - "subject_age: missing", "subject_sex: missing"
# Annotator: LLM, 2026-04-08
_DEFAULT_AMPLIFIER = "unknown"  # LLM 推断，需人类复核
_DEFAULT_CAP = "unknown"        # LLM 推断，需人类复核


def _load_participants_tsv(bids_dir: str) -> Optional[pd.DataFrame]:
    """Load participants.tsv if it exists in the BIDS directory."""
    participants_path = os.path.join(bids_dir, "participants.tsv")
    if os.path.exists(participants_path):
        return pd.read_csv(participants_path, sep="\t")
    return None


def _extract_subject_info(
    participants_df: Optional[pd.DataFrame],
    subject_id: str,
) -> Dict[str, str]:
    """Extract subject metadata from participants.tsv or return defaults."""
    if participants_df is None:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    # Find the row for this subject
    subject_row = participants_df[
        participants_df.get("participant_id", pd.Series()) == subject_id
    ]
    if subject_row.empty:
        # Try alternate column names
        for col in ["subject_id", "subject", "id"]:
            if col in participants_df.columns:
                subject_row = participants_df[participants_df[col] == subject_id]
                if not subject_row.empty:
                    break

    if subject_row.empty:
        return {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

    row = subject_row.iloc[0]

    # Extract age (must be string per KERNEL_RULEBOOK)
    age_val = "unknown"
    for age_col in ["age", "Age", "AGE"]:
        if age_col in row.index:
            val = row[age_col]
            if pd.notna(val):
                age_val = str(val)
                break

    # Extract sex (must be lowercase)
    sex_val = "unknown"
    for sex_col in ["sex", "Sex", "gender", "Gender"]:
        if sex_col in row.index:
            val = row[sex_col]
            if pd.notna(val):
                val_lower = str(val).lower()
                if val_lower in ["m", "male", "f", "female"]:
                    sex_val = "male" if val_lower.startswith("m") else "female"
                break

    # Extract handedness
    handed_val = "unknown"
    for hand_col in ["handedness", "Handedness", "hand"]:
        if hand_col in row.index:
            val = row[hand_col]
            if pd.notna(val):
                val_lower = str(val).lower()
                if val_lower.startswith("r"):
                    handed_val = "right"
                elif val_lower.startswith("l"):
                    handed_val = "left"
                break

    return {
        "age": age_val,
        "sex": sex_val,
        "handedness": handed_val,
    }


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for standard 10-20 naming.

    Source: Dataset description - 38 channels likely standard 10-20 cap
    Annotator: LLM, 2026-04-08  # LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    # Common channel mapping for standard 10-20 systems
    # Assuming standard naming like EEG 001 -> FC3, etc.
    # This is a heuristic; actual mapping should be verified from dataset docs
    standard_1020 = [
        "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "FC1", "FC2", "FC5", "FC6",
        "CP1", "CP2", "CP5", "CP6",
        "AF7", "AF8",
        "FT7", "FT8",
        "TP7", "TP8",
        "PO7", "PO8",
    ]

    # Match based on common patterns
    for ch in ch_names:
        ch_upper = ch.upper()
        # Skip if already standard
        if ch in standard_1020:
            continue
        # Handle common alias patterns
        if ch.startswith("EEG ") or ch.startswith("EEG-"):
            # Try to match by position number
            for i, std_ch in enumerate(standard_1020):
                if f"EEG {i+1:02d}" == ch or f"EEG-{i+1:02d}" == ch:
                    rename_map[ch] = std_ch
                    break
        elif ch.startswith("E") and ch[1:].isdigit():
            # Handle E1, E2, etc.
            idx = int(ch[1:]) - 1
            if 0 <= idx < len(standard_1020):
                rename_map[ch] = standard_1020[idx]

    return rename_map


@dataclass
class ToonFacesKernel:
    """Stage1 kernel for the ToonFaces (openneuro_ds004324) dataset."""

    KERNEL_ID: str = "toonfaces-stage1"

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
            The modified raw object with updated metadata.
        """
        file_path = row.get("File Path", "")
        subject_id = row.get("Subject", row.get("subject_id", "unknown"))

        # Determine BIDS directory for participants.tsv
        bids_dir = os.path.dirname(file_path)
        # Go up to find the dataset root
        if os.path.basename(bids_dir) == "eeg":
            bids_dir = os.path.dirname(bids_dir)

        # Load participants.tsv if available
        participants_df = _load_participants_tsv(bids_dir)

        # Extract subject info
        subject_info = _extract_subject_info(participants_df, subject_id)

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": _DEFAULT_AMPLIFIER,
                "cap": _DEFAULT_CAP,
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names before set_montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            # Filter to only existing channels
            valid_renames = {
                k: v for k, v in rename_map.items()
                if k in raw.ch_names
            }
            if valid_renames:
                raw.rename_channels(valid_renames)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            # Only keep channels that exist in both raw and montage
            common_channels = set(raw.ch_names) & set(montage.ch_names)
            if common_channels:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip if montage can't be applied

        # Process annotations - rename events to canonical format
        if raw.annotations:
            new_descriptions = []
            for desc in raw.annotations.description:
                # Convert to lowercase and standardize
                desc_lower = str(desc).lower().strip()
                # Map various formats to canonical event IDs
                # e.g., "img_0" -> "img/0", "Image 0" -> "img/0"
                new_desc = _canonicalize_event_desc(desc)
                new_descriptions.append(new_desc)

            # Create new annotations with canonical descriptions
            new_annotations = mne.Annotations(
                onset=raw.annotations.onset,
                duration=raw.annotations.duration,
                description=new_descriptions,
                orig_time=raw.annotations.orig_time,
            )
            raw.set_annotations(new_annotations)

        return raw


def _canonicalize_event_desc(desc: str) -> str:
    """Canonicalize event description to standard format.

    Maps various input formats to canonical event IDs:
    - img_0 -> img/0
    - toon_1 -> toon/1
    - sf_2 -> sf/2
    - block1 -> block1 (admin events stay as-is)
    """
    desc = str(desc).strip()

    # Map admin events (preserve as-is)
    admin_events = {
        "blockend", "block1", "block2", "block3",
        "intro", "instructions1", "instructions2", "instructions3",
        "practiceinstructions"
    }
    if desc.lower() in admin_events:
        return desc

    # Map face stimuli events
    # Pattern: type_level where type is img/toon/sf and level is 0-4
    import re

    # Match patterns like "img_0", "toon_1", "sf_2", "img-0", etc.
    match = re.match(r'^(img|toon|sf)[-_]?(\d+)$', desc, re.IGNORECASE)
    if match:
        face_type = match.group(1).lower()
        level = match.group(2)
        return f"{face_type}/{level}"

    # If already in canonical format, return as-is
    match = re.match(r'^(img|toon|sf)/(\d+)$', desc, re.IGNORECASE)
    if match:
        return f"{match.group(1).lower()}/{match.group(2)}"

    # Return original for unknown events
    return desc


KERNEL = ToonFacesKernel()