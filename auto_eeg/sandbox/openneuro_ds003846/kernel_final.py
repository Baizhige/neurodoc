"""openneuro_ds003846 stage1 kernel for EEGUnity.

Virtual reality haptic interaction study - prediction error detection task.
Participants reached out to touch virtual boxes with visual/vibrotactile/EMS feedback.
Normal (congruent) vs Conflict (incongruent/prediction error) classification.

Source: https://openneuro.org/datasets/ds003846
DOI: 10.3389/fnrgo.2024.1411305
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Device metadata - source: paper DOI 10.3389/fnrgo.2024.1411305
# LLM 推断，需人类复核
_DEVICE_AMPLIFIER: str = "unknown"
_DEVICE_CAP: str = "unknown"  # 64-channel setup, exact type not specified in paper


@dataclass
class OpenneuroDs003846Kernel:
    """Stage1 kernel for the openneuro_ds003846 dataset."""

    KERNEL_ID: str = "openneuro-ds003846-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and subject info.

        Returns
        -------
        mne.io.BaseRaw
            Processed raw object with standardized metadata and events.
        """
        # --- Channel renaming (if needed) ---
        raw = self._standardize_channels(raw)

        # --- Set montage if standard 10-20 system detected ---
        raw = self._set_montage_if_possible(raw)

        # --- Update description with eegunity metadata ---
        raw = self._update_description(raw, row)

        # --- Process annotations: parse raw events, derive super meta ---
        raw = self._process_events(raw)

        return raw

    def _standardize_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename non-standard channel names to standard 10-20 names.

        Common non-standard patterns in VR/VR-EEG datasets:
        - EEG-0, EEG-1, ... (numbered EEG channels)
        - eeg_0, eeg_1, ... (underscore prefix)
        - A1, A2, ... (alphanumeric)

        Source: Dataset documentation and channel count pattern (64 channels)
        LLM 推断，需人类复核 - exact mapping requires dataset documentation.
        """
        rename_map: Dict[str, str] = {}

        # Standard 10-20 64-channel layout (simplified mapping for common positions)
        # This kernel attempts to map numbered channels based on standard order
        standard_64 = [
            "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC1", "FC2", "FC6",
            "T7", "C3", "Cz", "C4", "T8", "TP9", "TP7", "CP3", "CP1", "CP2", "CP4",
            "TP10", "TP8", "P7", "P3", "Pz", "P4", "P8", "PO7", "PO3", "POz", "PO4",
            "PO8", "O1", "Oz", "O2", "AF7", "AF3", "AF4", "AF8", "F5", "F1", "F2",
            "F6", "FC3", "FC4", "FT7", "FT8", "C5", "C1", "C2", "C6", "TP7", "TP8",
            "CP5", "CPz", "CP6", "P5", "P1", "P2", "P6", "PO5", "PO6", "CB1", "CB2"
        ]

        existing = set(raw.ch_names)
        numbered_pattern = re.compile(r"^(?:EEG[-_]?(\d+)|eeg(\d+)|(\d+))$", re.IGNORECASE)

        for ch in raw.ch_names:
            match = numbered_pattern.match(ch)
            if match:
                # Extract numeric index from any matching pattern
                num_str = match.group(1) or match.group(2) or match.group(3)
                if num_str is not None:
                    idx = int(num_str)
                    if idx < len(standard_64):
                        rename_map[ch] = standard_64[idx]

        if rename_map:
            # Only rename if we have valid mappings and channel doesn't already match
            for old_name, new_name in rename_map.items():
                if new_name in existing and old_name != new_name:
                    pass  # Channel already has standard name
                elif old_name != new_name:
                    rename_map[old_name] = new_name
            mne.rename_channels(raw.info, rename_map)

        return raw

    def _set_montage_if_possible(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard montage if all channels are recognizable 10-20 names.

        Source: Standard 10-20 system montage available in MNE
        """
        standard_names = {
            "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
            "FC5", "FC1", "FCz", "FC2", "FC6",
            "T7", "C3", "Cz", "C4", "T8",
            "TP9", "TP7", "CP3", "CP1", "CPz", "CP2", "CP4", "TP10", "TP8",
            "P7", "P3", "Pz", "P4", "P8",
            "PO7", "PO3", "POz", "PO4", "PO8",
            "O1", "Oz", "O2",
            "AF7", "AF3", "AF4", "AF8",
        }

        ch_names_lower = {ch.lower() for ch in raw.ch_names}
        recognized = sum(1 for name in standard_names if name.lower() in ch_names_lower)

        # If >60% of channels match standard 10-20 names, set montage
        if recognized / len(raw.ch_names) > 0.6:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass  # Montage setting is best-effort

        return raw

    def _update_description(self, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Update raw.info['description'] with standardized eegunity metadata.

        Source: Dataset participants info + paper DOI 10.3389/fnrgo.2024.1411305
        LLM 推断，需人类复核 - age/sex/handedness from participants.tsv if available
        """
        original_desc = raw.info.get("description", "")

        # Try to get subject info from row or participants.tsv
        subject_id = row.get("subject_id", row.get("participant_id", "unknown"))

        # Attempt to read from participants.tsv if exists
        participants_info = self._get_participant_info(subject_id)

        age = participants_info.get("age", "unknown")
        sex = participants_info.get("sex", "unknown")
        handedness = participants_info.get("handedness", "unknown")

        description_dict = {
            "original_description": str(original_desc),
            "eegunity_description": {
                "age": str(age),  # Always string
                "sex": str(sex).lower() if sex != "unknown" else "unknown",
                "amplifier": _DEVICE_AMPLIFIER,
                "cap": _DEVICE_CAP,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw

    def _get_participant_info(self, subject_id: str) -> Dict[str, str]:
        """Attempt to read participant info from participants.tsv.

        Source: BIDS participants.tsv file
        LLM 推断，需人类复核
        """
        default_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        try:
            # Try to find participants.tsv relative to current file or dataset root
            possible_paths = [
                os.path.join(os.path.dirname(__file__), "..", "..", "participants.tsv"),
                "/data/participants.tsv",
                "./participants.tsv",
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    df = pd.read_csv(path, sep="\t")
                    # Match subject column (handles sub-01, S01, etc.)
                    subj_col = None
                    for col in df.columns:
                        if "participant" in col.lower() or "subject" in col.lower():
                            subj_col = col
                            break

                    if subj_col:
                        # Normalize subject ID for matching
                        norm_id = subject_id.replace("sub-", "").replace("sub_", "")
                        mask = df[subj_col].str.replace("sub-", "").str.replace("sub_", "") == norm_id
                        if mask.any():
                            row_data = df[mask].iloc[0]
                            info = {}
                            for field in ["age", "sex", "handedness"]:
                                if field in df.columns:
                                    val = row_data.get(field, "unknown")
                                    info[field] = str(val) if pd.notna(val) else "unknown"
                                else:
                                    info[field] = "unknown"
                            return info
                    break
        except Exception:
            pass

        return default_info

    def _process_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process raw annotations and derive super meta labels.

        Raw events: 'box', 'vibroFeedback', 'block', 'visualFeedback'
        Super meta: Parse 'box' events for normal_or_conflict label

        Source: Dataset event structure from analysis.md
        """
        # Ensure we have annotations
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        # Current annotations (raw meta)
        current_descriptions = [desc for desc in raw.annotations.description]

        # Check for 'box' events that need normal_or_conflict parsing
        box_annotations = []
        new_onsets = []
        new_durations = []
        new_descriptions = []

        for idx, desc in enumerate(current_descriptions):
            if desc == "box" or "box" in desc.lower():
                box_annotations.append(raw.annotations.description[idx])

                # Parse normal_or_conflict from annotation string
                # Format: 'box:...normal_or_conflict:normal...' or similar
                normal_or_conflict = self._parse_normal_or_conflict(desc)

                if normal_or_conflict:
                    # Add super meta label with explicit normal/conflict marking
                    super_label = f"box:{normal_or_conflict}"
                    new_onsets.append(raw.annotations.onset[idx])
                    new_durations.append(raw.annotations.duration[idx])
                    new_descriptions.append(super_label)

        # Add super meta annotations if we found parseable box events
        if new_onsets:
            super_annotations = mne.Annotations(
                onset=np.array(new_onsets),
                duration=np.array(new_durations),
                description=new_descriptions,
            )
            # Merge with existing annotations
            raw.set_annotations(raw.annotations + super_annotations)

        return raw

    def _parse_normal_or_conflict(self, annotation_string: str) -> Optional[str]:
        """Parse normal_or_conflict field from annotation string.

        Expected format examples:
        - 'box:touched;...normal_or_conflict:normal'
        - 'box:touched;...normal_or_conflict:conflict'

        Returns: 'normal', 'conflict', or None if not parseable
        """
        # Case-insensitive search for the pattern
        pattern = r"normal_or_conflict[:\s]+(\w+)"
        match = re.search(pattern, annotation_string, re.IGNORECASE)

        if match:
            value = match.group(1).lower()
            if value in ["normal", "conflict"]:
                return value

        return None


KERNEL = OpenneuroDs003846Kernel()