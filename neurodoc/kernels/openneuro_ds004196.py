"""Inner Speech EEG-fMRI Dataset stage1 kernel for EEGUnity.

Source: https://openneuro.org/datasets/ds004196
Paper: DOI 10.1038/s41597-023-02286-w
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


# Source: DOI 10.1038/s41597-023-02286-w Table 1
# Event ID mapping: word stimuli with categories
# Social category: child (111), daughter (112), father (113), wife (114)
# Numeric category: four (125), three (126), ten (127), six (128)
# Annotator: Human, 2026-04-08
_EVENT_WORD_MAP: Dict[int, str] = {
    111: "child",
    112: "daughter",
    113: "father",
    114: "wife",
    125: "four",
    126: "three",
    127: "ten",
    128: "six",
}

# Social category event IDs for binary classification
_SOCIAL_EVENT_IDS = {111, 112, 113, 114}

# Numeric category event IDs for binary classification
_NUMERIC_EVENT_IDS = {125, 126, 127, 128}

# Standard 10-20 EEG channel names expected for 73-channel cap
# This dataset uses BrainCap MR 64-channel cap (64 EEG + 9 auxiliary)
# Annotator: LLM, 2026-04-08, needs human verification
_STANDARD_1020_CHANNELS = [
    "Fp1", "Fpz", "Fp2",
    "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT5", "FC3", "FC1", "FCz", "FC2", "FC4", "FT6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "TP5", "CP3", "CP1", "CPz", "CP2", "CP4", "TP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8",
    "O1", "Oz", "O2",
]


@dataclass
class InnerSpeechKernel:
    """Stage1 kernel for the Inner Speech EEG-fMRI dataset (ds004196)."""

    KERNEL_ID: str = "openneuro-ds004196-stage1"

    def _find_events_tsv(self, eeg_file_path: str) -> Optional[str]:
        """Locate events.tsv sidecar file for the EEG file."""
        base_dir = os.path.dirname(eeg_file_path)
        eeg_basename = os.path.basename(eeg_file_path)

        # Match patterns like sub-01_task-innerSpeech_events.tsv
        match = re.match(r'(sub-\d+)', eeg_basename)
        if not match:
            return None

        sub_id = match.group(1)

        # Try common BIDS events.tsv locations
        candidates = [
            os.path.join(base_dir, f"{sub_id}_events.tsv"),
            os.path.join(base_dir, "..", "..", f"{sub_id}_events.tsv"),
            os.path.join(base_dir, "events.tsv"),
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return None

    def _load_participants_tsv(self, dataset_root: str) -> Optional[pd.DataFrame]:
        """Load participants.tsv if it exists."""
        participants_file = os.path.join(dataset_root, "participants.tsv")
        if os.path.exists(participants_file):
            return pd.read_csv(participants_file, sep="\t")
        return None

    def _get_subject_info(
        self, row, dataset_root: str, participants_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, str]:
        """Extract subject metadata."""
        subject_id = row.get("subject_id", "unknown")
        info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }

        # Try to get from participants.tsv
        if participants_df is not None:
            subject_col = participants_df.columns[0]
            subject_row = participants_df[
                participants_df[subject_col].str.contains(subject_id, na=False)
            ]
            if len(subject_row) > 0:
                row_data = subject_row.iloc[0]
                if "age" in participants_df.columns:
                    age_val = row_data.get("age", "unknown")
                    if pd.notna(age_val):
                        info["age"] = str(int(float(age_val)))
                if "sex" in participants_df.columns:
                    sex_val = row_data.get("sex", "unknown")
                    if pd.notna(sex_val):
                        info["sex"] = str(sex_val).lower().strip()
                if "handedness" in participants_df.columns:
                    handedness_val = row_data.get("handedness", "unknown")
                    if pd.notna(handedness_val):
                        info["handedness"] = str(handedness_val).lower().strip()

        # LLM inference from dataset description - needs human verification
        # Source: DOI 10.1038/s41597-023-02286-w - typical age range reported
        if info["age"] == "unknown":
            info["age"] = "unknown"  # inferred by LLM, needs human review

        # BrainCap MR is standard for EEG-fMRI studies
        if info["amplifier"] == "unknown":
            info["amplifier"] = "BrainAmp MR plus"  # inferred by LLM, needs human review
        if info["cap"] == "unknown":
            info["cap"] = "BrainCap MR 64-channel (Ag/AgCl)"  # inferred by LLM, needs human review

        return info

    def _create_annotations_from_events_tsv(
        self, events_file: str, sfreq: float
    ) -> mne.Annotations:
        """Parse events.tsv and create MNE annotations."""
        try:
            events_df = pd.read_csv(events_file, sep="\t")
        except Exception:
            return mne.Annotations(onset=[], duration=[], description=[])

        onsets = []
        durations = []
        descriptions = []

        # Standard BIDS events.tsv columns: onset, duration, trial_type
        onset_col = "onset" if "onset" in events_df.columns else events_df.columns[0]
        duration_col = "duration" if "duration" in events_df.columns else None

        for idx, row_data in events_df.iterrows():
            try:
                onset = float(row_data.get(onset_col, 0))
                duration = float(row_data.get(duration_col, 0)) if duration_col else 0.0

                # Try to find event value
                event_val = None
                for col in ["trial_type", "value", "event_id", "stim_type"]:
                    if col in events_df.columns:
                        val = row_data.get(col)
                        if pd.notna(val):
                            event_val = str(val)
                            break

                if event_val is None:
                    # Use row index if no event column found
                    event_val = str(idx)

                # Map event to word label if in known range
                try:
                    event_id_int = int(float(event_val))
                    if event_id_int in _EVENT_WORD_MAP:
                        event_val = _EVENT_WORD_MAP[event_id_int]
                except (ValueError, TypeError):
                    pass

                onsets.append(onset)
                durations.append(duration)
                descriptions.append(event_val)

            except (ValueError, TypeError):
                continue

        return mne.Annotations(
            onset=np.array(onsets),
            duration=np.array(durations),
            description=descriptions,
        )

    def _rename_channels_to_standard(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard 10-20 names if needed."""
        ch_names = raw.ch_names
        rename_map = {}

        # Common channel name patterns that need renaming
        # Source: Dataset documentation and standard EEG naming conventions
        # Annotator: LLM, 2026-04-08, needs human verification
        common_patterns = [
            # BrainCap standard names
            (r"^Fp\d?$", lambda m: f"Fp{'z' if m.group(0) == 'Fpz' else m.group(0)[-1]}"),
        ]

        # Check for numbered EEG channels (EEG-01, EEG-02, etc.)
        numbered_eeg = []
        for ch in ch_names:
            if re.match(r"^EEG-\d+$", ch):
                numbered_eeg.append(ch)

        if numbered_eeg:
            # Sort by number
            numbered_eeg.sort(key=lambda x: int(x.split("-")[1]))

            # Map to standard 10-20 positions
            if len(numbered_eeg) == len(_STANDARD_1020_CHANNELS):
                for old_name, new_name in zip(numbered_eeg, _STANDARD_1020_CHANNELS):
                    if old_name != new_name:
                        rename_map[old_name] = new_name
            elif len(numbered_eeg) <= len(_STANDARD_1020_CHANNELS):
                # Partial mapping - only rename those that match positions
                for old_name in numbered_eeg:
                    idx = int(old_name.split("-")[1]) - 1
                    if idx < len(_STANDARD_1020_CHANNELS):
                        new_name = _STANDARD_1020_CHANNELS[idx]
                        if old_name != new_name:
                            rename_map[old_name] = new_name

        # Rename other non-standard patterns
        for ch in ch_names:
            # EOG channels
            if re.match(r"EOG[_-]?(left|right|up|down|central)", ch, re.IGNORECASE):
                direction = re.search(r"(left|right|up|down|central)", ch, re.IGNORECASE).group(1)
                new_name = f"EOG-{direction.capitalize()}"
                if ch != new_name:
                    rename_map[ch] = new_name
            # ECG channels
            elif re.match(r"ECG|heart|cardiac", ch, re.IGNORECASE):
                if ch != "ECG":
                    rename_map[ch] = "ECG"
            # EMG channels
            elif re.match(r"EMG|trigger", ch, re.IGNORECASE):
                if ch.upper() != "EMG":
                    rename_map[ch] = "EMG"
            # Reference channels
            elif re.match(r"Ref|reference|bias", ch, re.IGNORECASE):
                if ch != "REF":
                    rename_map[ch] = "REF"

        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Keep original names if renaming fails

        # Set standard montage if channels are recognizable
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            existing_montage_chs = set(raw.ch_names) & set(montage.ch_names)
            if len(existing_montage_chs) >= 20:  # At least 20 channels match
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass  # Skip montage if setting fails

        return raw

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : object
            EEGUnity dataset context.
        raw : mne.io.BaseRaw
            MNE Raw object containing EEG data.
        row : dict
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        # Get file path
        file_path = row.get("File Path", row.get("file_path", ""))

        # Find events.tsv for this recording
        events_file = self._find_events_tsv(file_path)

        # Create annotations from events.tsv
        if events_file and os.path.exists(events_file):
            sfreq = raw.info["sfreq"]
            annotations = self._create_annotations_from_events_tsv(events_file, sfreq)
            raw.set_annotations(annotations)

        # Get dataset root for participants.tsv
        dataset_root = os.path.dirname(os.path.dirname(file_path))
        participants_df = self._load_participants_tsv(dataset_root)

        # Get subject metadata
        subject_info = self._get_subject_info(row, dataset_root, participants_df)

        # Get original description
        original_description = raw.info.get("description", "")

        # Update description with EEGUnity metadata
        description_dict = {
            "original_description": str(original_description) if original_description else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": subject_info["amplifier"],
                "cap": subject_info["cap"],
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels to standard names BEFORE set_montage
        raw = self._rename_channels_to_standard(raw)

        return raw


KERNEL = InnerSpeechKernel()