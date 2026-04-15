"""Dataset-specific kernel for openneuro ds004448 (BMI-HDEEG dataset 4).

High-density EEG motor imagery dataset with 130 channels, 1000 Hz sampling rate.
Participants performed right-hand kinesthetic motor imagery vs relaxation/rest.
3-class paradigm: event_1 (left hand MI), event_2 (right hand MI), event_3 (relaxation).

Source: https://openneuro.org/datasets/ds004448 | DOI: 10.1038/s41597-023-02260-6
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import mne
import pandas as pd

# Import base kernel for BIDS functionality
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from kernels.openneuro_specific._base import OpenNeuroBaseKernel

# Inferred device metadata from paper (LLM 推断，需人类复核)
# Source: DOI 10.1038/s41597-023-02260-6, Section 2.1 Equipment
# LLM 推断，需人类复核
_DEVICE_METADATA: Dict[str, Dict[str, str]] = {
    "amplifier": "BrainAmp",
    "cap": "Ag/AgCl",
    "handedness": "right",  # BMI task explicitly uses right-hand MI
}

# Event mapping based on analysis.md task definitions
# Classical Task 1: Right hand MI vs relaxation
# Potential Task 1: Left vs right hand MI
_EVENT_MAP = {
    "event_1": "left_hand_MI",
    "event_2": "right_hand_MI",
    "event_3": "relaxation",
}


class OpenNeuroDS004448Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for the BMI-HDEEG dataset 4 (OpenNeuro ds004448)."""

    KERNEL_ID: str = "openneuro-ds004448"

    def __init__(self):
        super().__init__(
            KERNEL_ID=self.KERNEL_ID,
            event_map=_EVENT_MAP,
            continuous_cols=["response_time"],
        )

    def _format_channel_name(self, ch_name: str) -> str:
        """Format non-standard channel names to standard 10-20 names.

        The dataset uses BrainVision format with potentially non-standard names.
        This handles common aliases and formats them to standard 10-20 system.

        Source: Standard 10-20 electrode naming convention
        """
        # Remove common prefixes/suffixes
        ch_clean = ch_name.strip().upper()

        # Handle BrainVision format (e.g., 'EEG 001' -> 'Fp1')
        if ch_clean.startswith("EEG "):
            ch_clean = ch_clean.replace("EEG ", "EEG-")

        # Standard 10-20 channel mapping for high-density caps (130 ch)
        # Based on extended 10-20 system with intermediate positions
        standard_names = {
            "FP1": "Fp1", "FPZ": "Fpz", "FP2": "Fp2",
            "AF7": "AF7", "AF3": "AF3", "AFZ": "AFz", "AF4": "AF4", "AF8": "AF8",
            "F7": "F7", "F5": "F5", "F3": "F3", "F1": "F1", "FZ": "Fz",
            "F2": "F2", "F4": "F4", "F6": "F6", "F8": "F8",
            "FT7": "FT7", "FC5": "FC5", "FC3": "FC3", "FC1": "FC1",
            "FCZ": "FCz", "FC2": "FC2", "FC4": "FC4", "FC6": "FC6", "FT8": "FT8",
            "T7": "T7", "C5": "C5", "C3": "C3", "C1": "C1", "CZ": "Cz",
            "C2": "C2", "C4": "C4", "C6": "C6", "T8": "T8",
            "TP7": "TP7", "CP5": "CP5", "CP3": "CP3", "CP1": "CP1",
            "CPZ": "CPz", "CP2": "CP2", "CP4": "CP4", "CP6": "CP6", "TP8": "TP8",
            "P7": "P7", "P5": "P5", "P3": "P3", "P1": "P1", "PZ": "Pz",
            "P2": "P2", "P4": "P4", "P6": "P6", "P8": "P8",
            "PO7": "PO7", "PO3": "PO3", "POZ": "POz", "PO4": "PO4", "PO8": "PO8",
            "O1": "O1", "OZ": "Oz", "O2": "O2",
            # Additional high-density intermediate positions
            "AF5": "AF5", "AF6": "AF6",
            "F9": "F9", "F10": "F10",
            "FC9": "FC9", "FC10": "FC10",
            "C9": "C9", "C10": "C10",
            "CP9": "CP9", "CP10": "CP10",
            "P9": "P9", "P10": "P10",
            "PO9": "PO9", "PO10": "PO10",
            # Common alternative naming
            "EEG-FP1": "Fp1", "EEG-FPZ": "Fpz", "EEG-FP2": "Fp2",
            "EEG-F7": "F7", "EEG-F3": "F3", "EEG-FZ": "Fz", "EEG-F4": "F4", "EEG-F8": "F8",
            "EEG-T7": "T7", "EEG-C3": "C3", "EEG-CZ": "Cz", "EEG-C4": "C4", "EEG-T8": "T8",
            "EEG-P7": "P7", "EEG-P3": "P3", "EEG-PZ": "Pz", "EEG-P4": "P4", "EEG-P8": "P8",
            "EEG-O1": "O1", "EEG-OZ": "Oz", "EEG-O2": "O2",
            "EEG-FC1": "FC1", "EEG-FC2": "FC2", "EEG-FC3": "FC3", "EEG-FC4": "FC4",
            "EEG-CP1": "CP1", "EEG-CP2": "CP2", "EEG-CP3": "CP3", "EEG-CP4": "CP4",
            "EEG-PO3": "PO3", "EEG-PO4": "PO4", "EEG-PO7": "PO7", "EEG-PO8": "PO8",
            # Numbered EEG channels (e.g., EEG 001)
            "EEG-001": "Fp1", "EEG-002": "Fpz", "EEG-003": "Fp2",
            "EEG-004": "AF3", "EEG-005": "AF4",
            "EEG-006": "F7", "EEG-007": "F3", "EEG-008": "Fz", "EEG-009": "F4", "EEG-010": "F8",
            "EEG-011": "FC5", "EEG-012": "FC3", "EEG-013": "FC1", "EEG-014": "FCz",
            "EEG-015": "FC2", "EEG-016": "FC4", "EEG-017": "FC6",
            "EEG-018": "T7", "EEG-019": "C5", "EEG-020": "C3", "EEG-021": "C1",
            "EEG-022": "Cz", "EEG-023": "C2", "EEG-024": "C4", "EEG-025": "C6", "EEG-026": "T8",
            "EEG-027": "TP7", "EEG-028": "CP5", "EEG-029": "CP3", "EEG-030": "CP1",
            "EEG-031": "CPz", "EEG-032": "CP2", "EEG-033": "CP4", "EEG-034": "CP6", "EEG-035": "TP8",
            "EEG-036": "P7", "EEG-037": "P5", "EEG-038": "P3", "EEG-039": "P1",
            "EEG-040": "Pz", "EEG-041": "P2", "EEG-042": "P4", "EEG-043": "P6", "EEG-044": "P8",
            "EEG-045": "PO7", "EEG-046": "PO3", "EEG-047": "POz", "EEG-048": "PO4", "EEG-049": "PO8",
            "EEG-050": "O1", "EEG-051": "Oz", "EEG-052": "O2",
        }

        # Try exact match first
        if ch_clean in standard_names:
            return standard_names[ch_clean]

        # Try case-insensitive
        for key, val in standard_names.items():
            if key.upper() == ch_clean:
                return val

        # Return original if no mapping found
        return ch_name

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names before setting montage."""
        rename_map = {}
        for ch_name in raw.ch_names:
            if ch_name.upper().startswith("EEG"):
                formatted = self._format_channel_name(ch_name)
                if formatted != ch_name:
                    rename_map[ch_name] = formatted

        if rename_map:
            raw.rename_channels(rename_map)

        return raw

    def _get_subject_info(self, row: Any) -> Dict[str, str]:
        """Extract subject metadata from BIDS participants.tsv or infer defaults.

        Returns a dict with age, sex, amplifier, cap, handedness.
        All values are strings per EEGUnity requirements.

        Source: participants.tsv | LLM 推断，需人类复核
        """
        subject_id = row.get("participant_id", "unknown")

        # Try to get from participants.tsv if available
        age = "unknown"
        sex = "unknown"

        # Check for BIDS participants file
        dataset_path = row.get("dataset_path", "")
        participants_tsv = os.path.join(dataset_path, "participants.tsv")

        if os.path.exists(participants_tsv):
            try:
                df = pd.read_csv(participants_tsv, sep="\t")
                subj_col = "participant_id" if "participant_id" in df.columns else "subject_id"
                if subj_col in df.columns:
                    subj_row = df[df[subj_col] == subject_id]
                    if len(subj_row) > 0:
                        if "age" in df.columns:
                            raw_age = subj_row.iloc[0]["age"]
                            if pd.notna(raw_age):
                                age = str(int(raw_age)) if isinstance(raw_age, (int, float)) else str(raw_age)
                        if "sex" in df.columns:
                            raw_sex = str(subj_row.iloc[0]["sex"]).lower()
                            if raw_sex in ["m", "male"]:
                                sex = "male"
                            elif raw_sex in ["f", "female"]:
                                sex = "female"
                            else:
                                sex = "unknown"
            except Exception:
                pass

        # Apply inferred device metadata (LLM 推断，需人类复核)
        # Source: DOI 10.1038/s41597-023-02260-6
        device_info = _DEVICE_METADATA.get("amplifier", "unknown")
        cap_info = _DEVICE_METADATA.get("cap", "unknown")
        handedness_info = _DEVICE_METADATA.get("handedness", "unknown")

        return {
            "age": age,
            "sex": sex,
            "amplifier": device_info,
            "cap": cap_info,
            "handedness": handedness_info,
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            MNE Raw object loaded from BIDS format.
        row
            Locator row with dataset metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with standardized channels and metadata.
        """
        # Get original description
        original_description = raw.info.get("description", "")

        # Get subject metadata
        subject_info = self._get_subject_info(row)

        # Write eegunity_description to raw.info["description"]
        description_dict = {
            "original_description": original_description if original_description else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": subject_info["amplifier"],
                "cap": subject_info["cap"],
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard 10-20 names BEFORE set_montage
        raw = self._rename_channels(raw)

        # Set standard 10-20 montage for high-density EEG
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass

        # Parse events from annotations (BIDS format)
        # Events are stored in events.tsv, loaded as annotations by MNE-BIDS
        try:
            events, event_id = mne.events_from_annotations(raw)
        except Exception:
            events = None
            event_id = {}

        # Map events to standardized event names
        if events is not None and len(events) > 0:
            # Build reverse mapping from event_id values to names
            annotation_desc_map = {}
            if hasattr(raw, "annotations") and raw.annotations is not None:
                for i, desc in enumerate(raw.annotations.description):
                    if str(desc) in self.event_map:
                        annotation_desc_map[str(desc)] = self.event_map[str(desc)]
                    elif desc in self.event_map:
                        annotation_desc_map[desc] = self.event_map[desc]
                    else:
                        # Keep original description
                        annotation_desc_map[desc] = str(desc)

            # Create new annotations with standardized names
            if annotation_desc_map:
                new_descriptions = []
                for desc in raw.annotations.description:
                    desc_str = str(desc)
                    if desc_str in annotation_desc_map:
                        new_descriptions.append(annotation_desc_map[desc_str])
                    elif desc in annotation_desc_map:
                        new_descriptions.append(annotation_desc_map[desc])
                    else:
                        new_descriptions.append(desc_str)

                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time,
                )
                raw.set_annotations(new_annotations)

        return raw


KERNEL = OpenNeuroDS004448Kernel()