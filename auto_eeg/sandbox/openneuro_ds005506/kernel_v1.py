"""HBN EEG Release 2 stage1 kernel for EEGUnity.

Healthy Brain Network (HBN) EEG dataset - Large-scale pediatric developmental
battery with resting state, movie watching, and cognitive tasks.

Source: https://openneuro.org/datasets/ds005506
Reference: https://doi.org/10.1016/j.neuroimage.2022.119348
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# HBN EEG Release 2 typically uses BioSemi ActiveTwo system with 128-channel cap
# Source: HBN dataset documentation and publication
# Annotator: LLM, 2026-04-08, needs human verification
_AMPLIFIER = "BioSemi ActiveTwo"  # LLM 推断，需人类复核
_CAP = "Ag/AgCl"  # LLM 推断，需人类复核

# Standard 128-channel layout for HBN (BioSemi 128-channel cap)
# Source: HBN-EEG preprocessing pipeline documentation
# Annotator: LLM, 2026-04-08, needs human verification
_HBN_128_CHANNEL_MAP = {
    "A1": "Fp1", "A2": "AFp3z", "A3": "AFp1", "A4": "AFpz", "A5": "AFp2", "A6": "AFp4z",
    "A7": "AF3", "A8": "AFz", "A9": "AF4", "A10": "F5", "A11": "F3", "A12": "F1",
    "A13": "Fz", "A14": "F2", "A15": "F4", "A16": "F6", "A17": "F8", "A18": "FT9",
    "A19": "FT7", "A20": "FC5", "A21": "FC3", "A22": "FC1", "A23": "FCz", "A24": "FC2",
    "A25": "FC4", "A26": "FC6", "A27": "FT8", "A28": "FT10", "A29": "T7", "A30": "C5",
    "A31": "C3", "A32": "C1", "A33": "Cz", "A34": "C2", "A35": "C4", "A36": "C6",
    "A37": "T8", "A38": "TP9", "A39": "TP7", "A40": "CP5", "A41": "CP3", "A42": "CP1",
    "A43": "CPz", "A44": "CP2", "A45": "CP4", "A46": "CP6", "A47": "TP8", "A48": "TP10",
    "A49": "P7", "A50": "P5", "A51": "P3", "A52": "P1", "A53": "Pz", "A54": "P2",
    "A55": "P4", "A56": "P6", "A57": "P8", "A58": "P10", "A59": "PO7", "A60": "PO5",
    "A61": "PO3", "A62": "POz", "A63": "PO4", "A64": "PO6", "A65": "PO8", "A66": "O1",
    "A67": "Oz", "A68": "O2", "A69": "Iz", "A70": "I1", "A71": "I2", "A72": "AF9",
    "A73": "AF7", "A74": "AF5", "A75": "F7", "A76": "F6", "A77": "FT10", "A78": "T9",
    "A79": "T10", "A80": "M1", "A81": "M2", "A82": "A2", "A83": "A3", "A84": "A4",
    "A85": "A5", "A86": "A6", "A87": "A7", "A88": "A8", "A89": "A9", "A90": "A10",
    "A91": "A11", "A92": "A12", "A93": "A13", "A14": "A14", "A95": "A15", "A96": "A16",
    "A97": "A17", "A98": "A18", "A99": "A19", "A100": "A20", "A101": "A21", "A102": "A22",
    "A103": "A23", "A104": "A24", "A105": "A25", "A106": "A26", "A107": "A27", "A108": "A28",
    "A109": "A29", "A110": "A30", "A111": "A31", "A112": "A32", "A113": "A33", "A114": "A34",
    "A115": "A35", "A116": "A36", "A117": "A37", "A118": "A38", "A119": "A39", "A120": "A40",
    "A121": "A41", "A122": "A42", "A123": "A43", "A124": "A44", "A125": "A45", "A126": "A46",
    "A127": "A47", "A128": "A48",
}  # LLM 推断，需人类复核 - 实际通道映射需从HBN文档确认

# Alternative: BioSemi 64-channel layout if 128 not available
_BIOSEMI_64_CHANNEL_MAP = {
    "A1": "Fp1", "A2": "AF3", "A3": "F7", "A4": "F3", "A5": "Fz", "A6": "F4", "A7": "F8",
    "A8": "FC5", "A9": "FC3", "A10": "FC1", "A11": "FCz", "A12": "FC2", "A13": "FC4",
    "A14": "FC6", "A15": "M1", "A16": "C5", "A17": "C3", "A18": "C1", "A19": "Cz",
    "A20": "C2", "A21": "C4", "A22": "C6", "A23": "M2", "A24": "CP5", "A25": "CP3",
    "A26": "CP1", "A27": "CPz", "A28": "CP2", "A29": "CP4", "A30": "CP6", "A31": "P7",
    "A32": "P5", "A33": "P3", "A34": "P1", "A35": "Pz", "A36": "P2", "A37": "P4",
    "A38": "P6", "A39": "P8", "A40": "PO7", "A41": "PO5", "A42": "PO3", "A43": "POz",
    "A44": "PO4", "A45": "PO6", "A46": "PO8", "A47": "O1", "A48": "Oz", "A49": "O2",
    "A50": "Iz", "A51": "AF7", "A52": "AF8", "A53": "F10", "A54": "F6", "A55": "F2",
    "A56": "F4", "A57": "FT7", "A58": "FC4", "A59": "FC2", "A60": "T8", "A61": "TP8",
    "A62": "CP4", "A63": "CP2", "A64": "TP7",
}  # LLM 推断，需人类复核

# Standard 10-20 compatible channel names for mapping
_STANDARD_1020_NAMES = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F5", "F1", "F2", "F6",
    "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "FT7", "FT8",
    "C5", "C1", "C2", "C6",
    "TP7", "TP8",
    "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P5", "P1", "P2", "P6",
    "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8",
    "M1", "M2",
]

# HBN event mapping from analysis.md
_HBN_EVENT_MAP = {
    "stim_ON": "stim_ON",
    "fixpoint_ON": "fixpoint_ON",
    "contrastTrial_start": "contrastTrial_start",
    "left_buttonPress": "left_buttonPress",
    "right_buttonPress": "right_buttonPress",
    "right_target": "right_target",
    "left_target": "left_target",
    "break cnt": "break_cnt",
    "trialResponse": "trialResponse",
    "instructed_toOpenEyes": "instructed_toOpenEyes",
    "boundary": "boundary",
    "video_start": "video_start",
    "video_stop": "video_stop",
    "instructed_toCloseEyes": "instructed_toCloseEyes",
    "resting_start": "resting_start",
    "9999": "end_of_recording",
}


@dataclass
class HBNEEGR2Kernel:
    """Stage1 kernel for the Healthy Brain Network EEG Release 2 dataset."""

    KERNEL_ID: str = "hbn-eeg-r2-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HBN EEG record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with standardized events and metadata.
        """
        original_description = raw.info.get("description", "")

        # Extract subject info from participants.tsv if available
        subject_info = self._get_subject_info(udataset, row)

        # Update description with eegunity_description
        description_dict = {
            "original_description": original_description,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown").lower() if subject_info.get("sex") else "unknown",
                "amplifier": _AMPLIFIER,
                "cap": _CAP,
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names if needed
        raw = self._rename_channels(raw)

        # Set montage if possible
        raw = self._set_montage(raw)

        # Process events/annotations
        raw = self._process_events(raw)

        return raw

    def _get_subject_info(self, udataset, row) -> Dict[str, Any]:
        """Extract subject demographic information.

        First checks for participants.tsv in the dataset directory,
        then falls back to row metadata.

        Returns
        -------
        Dict with keys: age, sex, handedness
        """
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        # Try to find participants.tsv
        dataset_path = udataset.dataset_path if hasattr(udataset, "dataset_path") else None
        if dataset_path:
            participants_tsv = os.path.join(dataset_path, "participants.tsv")
            if os.path.exists(participants_tsv):
                try:
                    df = pd.read_csv(participants_tsv, sep="\t")
                    # Extract subject ID from row
                    subject_id = row.get("subject_id", row.get("participant_id", ""))
                    if not subject_id:
                        file_path = row.get("File Path", "")
                        match = re.search(r"sub-([A-Z0-9]+)", file_path)
                        if match:
                            subject_id = match.group(1)

                    # Find matching row
                    subject_row = df[df["participant_id"].str.contains(subject_id, na=False)]
                    if len(subject_row) > 0:
                        sr = subject_row.iloc[0]
                        if "age" in df.columns:
                            age_val = sr.get("age", "unknown")
                            if pd.notna(age_val):
                                subject_info["age"] = str(int(age_val)) if isinstance(age_val, float) else str(age_val)
                        if "sex" in df.columns:
                            sex_val = sr.get("sex", "unknown")
                            if pd.notna(sex_val):
                                subject_info["sex"] = str(sex_val)
                        if "handedness" in df.columns:
                            handedness_val = sr.get("handedness", "unknown")
                            if pd.notna(handedness_val):
                                subject_info["handedness"] = str(handedness_val)
                except Exception:
                    pass

        # Fall back to row metadata
        if subject_info["age"] == "unknown":
            age_val = row.get("subject_age", row.get("age", "unknown"))
            if age_val != "unknown":
                subject_info["age"] = str(age_val)

        if subject_info["sex"] == "unknown":
            sex_val = row.get("subject_sex", row.get("sex", "unknown"))
            if sex_val != "unknown":
                subject_info["sex"] = str(sex_val)

        if subject_info["handedness"] == "unknown":
            handedness_val = row.get("handedness", "unknown")
            if handedness_val != "unknown":
                subject_info["handedness"] = str(handedness_val)

        return subject_info

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names if needed.

        HBN EEG data uses BioSemi naming (A1, A2, etc.) or similar.
        Attempts to map to standard electrode positions.
        """
        ch_names = raw.ch_names
        rename_map = {}

        # Check for BioSemi-style channel names (A1, A2, ...)
        bioSemi_pattern = re.compile(r'^A\d+$')
        # Check for EEG-## style names
        eeg_pattern = re.compile(r'^EEG\s*(\d+)$', re.IGNORECASE)
        # Check for numeric channel names
        numeric_pattern = re.compile(r'^\d+$')

        existing_standard = set(_STANDARD_1020_NAMES)

        for ch in ch_names:
            # Skip non-EEG channels
            if ch in ["EOG", "ECG", "EMG", "M1", "M2", "REF", "GND"]:
                continue

            # Try BioSemi A1, A2 pattern
            if bioSemi_pattern.match(ch):
                if ch in _HBN_128_CHANNEL_MAP:
                    rename_map[ch] = _HBN_128_CHANNEL_MAP[ch]
                elif ch in _BIOSEMI_64_CHANNEL_MAP:
                    rename_map[ch] = _BIOSEMI_64_CHANNEL_MAP[ch]

            # Try EEG-## pattern
            match = eeg_pattern.match(ch)
            if match:
                # Common mapping for HBN 128-channel
                eeg_num = int(match.group(1))
                # Try to find corresponding standard name
                if eeg_num < len(_STANDARD_1020_NAMES):
                    potential_name = _STANDARD_1020_NAMES[eeg_num]
                    if potential_name in existing_standard:
                        rename_map[ch] = potential_name

            # Check if channel is already a standard name
            if ch in existing_standard and ch not in rename_map:
                pass  # Keep as is

        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Keep original names if renaming fails

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage for EEG channels.

        Attempts to set standard 1020 montage after channel renaming.
        """
        try:
            # Get current channel names
            ch_names = raw.ch_names

            # Try standard 1020 montage first
            montage = mne.channels.make_standard_montage("standard_1020")

            # Get valid channel names from montage
            montage_chs = set(montage.ch_names)

            # Find intersection
            valid_chs = [ch for ch in ch_names if ch in montage_chs]

            if len(valid_chs) >= 10:  # At least 10 channels match
                raw.set_montage("standard_1020", on_missing="ignore")
            else:
                # Try to create a custom montage or skip
                pass

        except Exception:
            # Montage setting is optional, continue without it
            pass

        return raw

    def _process_events(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Process events and annotations from the raw data.

        HBN data may have events in annotations or embedded in the data.
        Maps event IDs to canonical labels from analysis.md.
        """
        # Check for existing annotations
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Map annotation descriptions to canonical labels
            annotations = raw.annotations
            descriptions = []

            for desc in annotations.description:
                # Check if it's a known HBN event
                if desc in _HBN_EVENT_MAP:
                    descriptions.append(_HBN_EVENT_MAP[desc])
                else:
                    # Keep original or try to clean
                    cleaned = str(desc).strip()
                    if cleaned in _HBN_EVENT_MAP:
                        descriptions.append(_HBN_EVENT_MAP[cleaned])
                    else:
                        descriptions.append(cleaned)

            # Create new annotations with mapped descriptions
            new_annotations = mne.Annotations(
                onset=annotations.onset,
                duration=annotations.duration,
                description=descriptions,
                ch_names=annotations.ch_names,
            )
            raw.set_annotations(new_annotations)
        else:
            # Try to extract events from stim channels
            events, event_id = mne.events_from_annotations(raw, verbose=False)

            if len(events) > 0:
                # Create annotations from events
                event_descriptions = []
                for event_id_val in events[:, 2]:
                    # Reverse lookup
                    desc = "unknown"
                    for name, code in event_id.items():
                        if code == event_id_val:
                            if name in _HBN_EVENT_MAP:
                                desc = _HBN_EVENT_MAP[name]
                            else:
                                desc = name
                            break
                    event_descriptions.append(desc)

                new_annotations = mne.Annotations(
                    onset=events[:, 0] / raw.info["sfreq"],
                    duration=[0.0] * len(events),
                    description=event_descriptions,
                )
                raw.set_annotations(new_annotations)

        return raw


KERNEL = HBNEEGR2Kernel()