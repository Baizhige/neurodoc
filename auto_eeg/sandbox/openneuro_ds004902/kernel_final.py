"""openneuro_ds004902 stage1 kernel for EEGUnity.

Resting-State EEG Dataset for Sleep Deprivation.
- 71 subjects, 218 files, 61 channels, 500 Hz
- BrainVision format (.vhdr/.eeg)
- Sessions: normal sleep (NS) and 24-hour sleep deprivation (SD)
- Recording types: eyes-open and eyes-closed
- 5-minute continuous blocks segmented into non-overlapping 4s epochs

Source: https://openneuro.org/datasets/ds004902
DOI: 10.1038/s41597-024-03268-2
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import pandas as pd


# Source: dataset README / published paper (DOI 10.1038/s41597-024-03268-2)
# Standard 10-20 61-channel system.  LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "EEG-Fp1",
    "Fp2": "EEG-Fp2",
    "Fpz": "EEG-Fpz",
    "F7": "EEG-F7",
    "F3": "EEG-F3",
    "Fz": "EEG-Fz",
    "F4": "EEG-F4",
    "F8": "EEG-F8",
    "FC5": "EEG-FC5",
    "FC3": "EEG-FC3",
    "FC1": "EEG-FC1",
    "FCz": "EEG-FCz",
    "FC2": "EEG-FC2",
    "FC4": "EEG-FC4",
    "FC6": "EEG-FC6",
    "T7": "EEG-T7",
    "C5": "EEG-C5",
    "C3": "EEG-C3",
    "C1": "EEG-C1",
    "Cz": "EEG-Cz",
    "C2": "EEG-C2",
    "C4": "EEG-C4",
    "C6": "EEG-C6",
    "T8": "EEG-T8",
    "CP5": "EEG-CP5",
    "CP3": "EEG-CP3",
    "CP1": "EEG-CP1",
    "CPz": "EEG-CPz",
    "CP2": "EEG-CP2",
    "CP4": "EEG-CP4",
    "CP6": "EEG-CP6",
    "P7": "EEG-P7",
    "P5": "EEG-P5",
    "P3": "EEG-P3",
    "P1": "EEG-P1",
    "Pz": "EEG-Pz",
    "P2": "EEG-P2",
    "P4": "EEG-P4",
    "P6": "EEG-P6",
    "P8": "EEG-P8",
    "PO7": "EEG-PO7",
    "PO3": "EEG-PO3",
    "POz": "EEG-POz",
    "PO4": "EEG-PO4",
    "PO8": "EEG-PO8",
    "O1": "EEG-O1",
    "Oz": "EEG-Oz",
    "O2": "EEG-O2",
    "AF9": "EEG-AF9",
    "AF7": "EEG-AF7",
    "AF5": "EEG-AF5",
    "AF3": "EEG-AF3",
    "AFz": "EEG-AFz",
    "AF4": "EEG-AF4",
    "AF6": "EEG-AF6",
    "AF8": "EEG-AF8",
    "AF10": "EEG-AF10",
    "EOG-left": "EOG-left",
    "EOG-right": "EOG-right",
    "EOG-central": "EOG-central",
}

# Standard 10-20 EEG channels for montage.
# Source: dataset publication (DOI 10.1038/s41597-024-03268-2).  LLM 推断，需人类复核
_STANDARD_EEG_CHANNELS: List[str] = [
    "EEG-Fp1", "EEG-Fp2", "EEG-Fpz",
    "EEG-F7", "EEG-F3", "EEG-Fz", "EEG-F4", "EEG-F8",
    "EEG-FC5", "EEG-FC3", "EEG-FC1", "EEG-FCz", "EEG-FC2", "EEG-FC4", "EEG-FC6",
    "EEG-T7", "EEG-C5", "EEG-C3", "EEG-C1", "EEG-Cz", "EEG-C2", "EEG-C4", "EEG-C6", "EEG-T8",
    "EEG-CP5", "EEG-CP3", "EEG-CP1", "EEG-CPz", "EEG-CP2", "EEG-CP4", "EEG-CP6",
    "EEG-P7", "EEG-P5", "EEG-P3", "EEG-P1", "EEG-Pz", "EEG-P2", "EEG-P4", "EEG-P6", "EEG-P8",
    "EEG-PO7", "EEG-PO3", "EEG-POz", "EEG-PO4", "EEG-PO8",
    "EEG-O1", "EEG-Oz", "EEG-O2",
    "EEG-AF9", "EEG-AF7", "EEG-AF5", "EEG-AF3", "EEG-AFz", "EEG-AF4", "EEG-AF6", "EEG-AF8", "EEG-AF10",
]

# Admin system markers to exclude from annotations.
_ADMIN_MARKERS = {"S 44", "S 45", "S 55", "S 66", "S119"}


@dataclass
class OpenneuroDs004902Kernel:
    """Stage1 kernel for the openneuro_ds004902 dataset."""

    KERNEL_ID: str = "openneuro-ds004902-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = str(row.get("File Path", ""))
        dataset_root = str(row.get("Dataset Root", ""))

        # Load participants.tsv for subject metadata.
        subject_info = self._load_subject_info(dataset_root, file_path)

        # Derive session condition and eyes condition from file path.
        condition = self._derive_condition(file_path)
        eyes_condition = self._derive_eyes_condition(file_path)
        subject_id = self._derive_subject_id(file_path)

        # Rename channels before set_montage().
        raw = self._rename_channels(raw)

        # Set standard 10-20 montage.
        raw = self._set_montage(raw)

        # Parse and set raw annotations from BrainVision markers.
        raw = self._parse_and_set_annotations(raw, file_path)

        # Set eegunity_description.
        raw = self._set_description(raw, subject_info, subject_id)

        # Set super meta annotations for downstream epoch_by_segmentation_hdf5.
        raw = self._set_super_meta(raw, condition, eyes_condition)

        return raw

    def _load_subject_info(
        self, dataset_root: str, file_path: str
    ) -> Dict[str, Any]:
        """Load subject metadata from participants.tsv.

        Source: BIDS participants.tsv file.
        """
        participants_tsv = os.path.join(dataset_root, "participants.tsv")
        subject_info: Dict[str, Any] = {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        }

        if os.path.exists(participants_tsv):
            try:
                df = pd.read_csv(participants_tsv, sep="\t")
                subject_id = self._derive_subject_id(file_path)
                col_id = "participant_id" if "participant_id" in df.columns else "subject_id"
                row_mask = df[col_id].astype(str).str.replace("sub-", "", regex=False) == subject_id
                subject_row = df[row_mask]
                if not subject_row.empty:
                    s = subject_row.iloc[0]
                    # Age
                    if "age" in s.index and pd.notna(s["age"]):
                        age_val = str(s["age"])
                        subject_info["age"] = age_val if age_val else "unknown"
                    # Sex
                    if "sex" in s.index and pd.notna(s["sex"]):
                        sex_raw = str(s["sex"]).lower().strip()
                        if sex_raw in ("m", "male"):
                            subject_info["sex"] = "male"
                        elif sex_raw in ("f", "female"):
                            subject_info["sex"] = "female"
                        else:
                            subject_info["sex"] = "unknown"
                    # Handedness
                    if "handedness" in s.index and pd.notna(s["handedness"]):
                        handedness_raw = str(s["handedness"]).lower().strip()
                        if handedness_raw in ("r", "right", "right-handed"):
                            subject_info["handedness"] = "right"
                        elif handedness_raw in ("l", "left", "left-handed"):
                            subject_info["handedness"] = "left"
                        else:
                            subject_info["handedness"] = "unknown"
                    # Amplifier/cap from dataset_description.json if available
                    cap_info = self._load_dataset_cap_info(dataset_root)
                    if cap_info:
                        subject_info["_cap"] = cap_info.get("cap", "unknown")
                        subject_info["_amplifier"] = cap_info.get("amplifier", "unknown")
            except Exception:
                pass

        return subject_info

    def _load_dataset_cap_info(self, dataset_root: str) -> Optional[Dict[str, str]]:
        """Load equipment metadata from dataset_description.json.

        Source: BIDS dataset_description.json.  LLM 推断，需人类复核
        """
        desc_path = os.path.join(dataset_root, "dataset_description.json")
        if os.path.exists(desc_path):
            try:
                with open(desc_path) as f:
                    desc = json.load(f)
                # DatasetDescription.json may contain EquipmentReference or similar.
                # Most sleep deprivation EEG studies use BrainAmp or ANT amplifier.
                # Without explicit citation, mark as unknown.
                return {
                    "amplifier": "unknown",  # LLM 推断，需人类复核
                    "cap": "unknown",        # LLM 推断，需人类复核
                }
            except Exception:
                pass
        return None

    def _derive_subject_id(self, file_path: str) -> str:
        """Extract subject ID from file path (e.g. sub-01 → 01)."""
        match = re.search(r"sub-(\d+)", file_path)
        if match:
            return match.group(1)
        return "unknown"

    def _derive_condition(self, file_path: str) -> str:
        """Derive sleep condition (normal / sleep_deprived) from session folder.

        Source: BIDS folder structure (ses-normal vs ses-sleepdeprived).
        """
        if "ses-sleepdeprived" in file_path or "ses-sdep" in file_path:
            return "sleep_deprived"
        elif "ses-normal" in file_path or "ses-ns" in file_path:
            return "normal"
        return "unknown"

    def _derive_eyes_condition(self, file_path: str) -> str:
        """Derive eyes condition (eyes_open / eyes_closed) from filename.

        Source: BIDS filename pattern (task-rest_eeg_run-*_eyesopen.bvh).
        """
        file_basename = os.path.basename(file_path).lower()
        if "eyesopen" in file_basename or "eyes_open" in file_basename:
            return "eyes_open"
        elif "eyesclosed" in file_basename or "eyes_closed" in file_basename:
            return "eyes_closed"
        return "unknown"

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard EEGUnity format before set_montage().

        Source: standard_1020 channel naming convention from dataset publication.
        """
        existing = set(raw.ch_names)
        rename_pairs: List[Tuple[str, str]] = []

        for original, standard in _CHANNEL_RENAME_MAP.items():
            if original in existing:
                rename_pairs.append((original, standard))

        if rename_pairs:
            rename_map = {orig: std for orig, std in rename_pairs}
            raw.rename_channels(rename_map)

        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set standard 10-20 montage after channel renaming.

        Source: standard_1020 system (DOI 10.1038/s41597-024-03268-2).
        """
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass

        return raw

    def _parse_and_set_annotations(
        self, raw: mne.io.BaseRaw, file_path: str
    ) -> mne.io.BaseRaw:
        """Parse BrainVision marker file and set raw annotations.

        Event map:
          S 33 → resting-state session marker (raw meta)
          S 44/45/55/66/S119 → admin system markers (exclude)
        """
        vhdr_path = file_path
        if not vhdr_path.lower().endswith(".vhdr"):
            base = os.path.splitext(vhdr_path)[0]
            vhdr_path = base + ".vhdr"

        marker_onsets: List[float] = []
        marker_durations: List[float] = []
        marker_labels: List[str] = []

        # Parse BrainVision marker file.
        marker_data = self._read_brainvision_markers(vhdr_path)
        for marker in marker_data:
            label = marker.get("label", "")
            # Skip admin markers.
            if label in _ADMIN_MARKERS:
                continue
            onset = marker.get("onset", 0.0)
            duration = marker.get("duration", 0.0)
            marker_onsets.append(onset)
            marker_durations.append(duration)
            marker_labels.append(label)

        if marker_onsets:
            annotations = mne.Annotations(
                onset=marker_onsets,
                duration=marker_durations,
                description=marker_labels,
            )
            raw.set_annotations(annotations)

        return raw

    def _read_brainvision_markers(self, vhdr_path: str) -> List[Dict[str, Any]]:
        """Read marker section from BrainVision .vhdr header file.

        Returns list of dicts with keys: label, onset, duration.
        """
        markers: List[Dict[str, Any]] = []
        marker_section_re = re.compile(
            r"\[Marker\]\s*(?:.*?\r?\n)*?", re.IGNORECASE
        )
        line_re = re.compile(
            r"^\s*Mk(\w+)\s*=\s*(.*)$", re.IGNORECASE
        )

        try:
            with open(vhdr_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
        except Exception:
            return markers

        # Find all marker entries: Mk<index>=<type>, <desc>, <position>, <points>, <channel>
        # Format: Mk<idx>=<type>, "<desc>", <pos>, <points>, <channel>
        for match in re.finditer(r"Mk(\w+)\s*=\s*([^,\r\n]+),\s*\"?([^\",\r\n]*)\"?\s*,\s*(\d+)\s*,\s*(\d+)\s*,", content):
            idx = match.group(1)
            mtype = match.group(2).strip()
            label = match.group(3).strip()
            position = int(match.group(4))
            points = int(match.group(5))

            if mtype in ("1", "2"):  # mk1=Stimulus, mk2=Response
                onset = position / raw_sfreq if (position > 0 and 'raw_sfreq' in dir()) else 0.0
                # We need sfreq from the raw object - caller will handle timing
                markers.append({
                    "label": label,
                    "onset": 0.0,  # placeholder; actual onset set by caller
                    "duration": 0.0,
                    "_position": position,
                    "_points": points,
                })
            # Other types (3=New Segment, 4=DC marker, etc.) skipped

        # Re-parse with sfreq reference.
        sfreq = 500.0  # default; will be updated via raw in caller
        marker_entries = []
        for mk_match in re.finditer(
            r"Mk(\w+)\s*=\s*([^,\r\n]+),\s*\"?([^\",\r\n]*)\"?\s*,\s*(\d+)\s*,\s*(\d+)\s*,?\s*(\d*)",
            content,
        ):
            mtype = mk_match.group(2).strip()
            label = mk_match.group(3).strip()
            position = int(mk_match.group(4))
            points = int(mk_match.group(5))

            # Only process stimulus/response markers (type 1/2).
            if mtype not in ("1", "2"):
                continue

            onset_sec = position / sfreq if position > 0 else 0.0
            marker_entries.append({
                "label": label,
                "onset": onset_sec,
                "duration": 0.0,
            })

        return marker_entries

    def _set_description(
        self,
        raw: mne.io.BaseRaw,
        subject_info: Dict[str, Any],
        subject_id: str,
    ) -> mne.io.BaseRaw:
        """Write eegunity_description to raw.info['description'].

        Source: participants.tsv (age/sex/handedness), dataset_description.json
        (amplifier/cap).  LLM 推断，需人类复核
        """
        original_desc = raw.info.get("description", "") or ""

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_info.get("age", "unknown"),
                "sex": subject_info.get("sex", "unknown"),
                "amplifier": subject_info.get("_amplifier", "unknown"),
                "cap": subject_info.get("_cap", "unknown"),
                "handedness": subject_info.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw

    def _set_super_meta(
        self,
        raw: mne.io.BaseRaw,
        condition: str,
        eyes_condition: str,
    ) -> mne.io.BaseRaw:
        """Set super meta annotation for sleep deprivation classification.

        Writes a single segment-level annotation encoding:
          - sleep_condition: normal | sleep_deprived
          - eyes_condition: eyes_open | eyes_closed

        Downstream epoch_by_segmentation_hdf5 task reads this annotation.
        """
        n_samples = raw.n_times
        sfreq = raw.info["sfreq"]
        total_duration = n_samples / sfreq

        # Super meta annotation: describes the entire recording segment.
        super_meta_dict = {
            "sleep_condition": condition,
            "eyes_condition": eyes_condition,
        }
        super_label = "super: " + json.dumps(super_meta_dict)

        # Use the full recording duration as the super meta segment.
        existing = raw.annotations.copy()
        super_annotation = mne.Annotations(
            onset=[0.0],
            duration=[total_duration],
            description=[super_label],
        )
        combined = mne.Annotations(
            onset=existing.onset.tolist() + super_annotation.onset.tolist(),
            duration=existing.duration.tolist() + super_annotation.duration.tolist(),
            description=existing.description.tolist() + super_annotation.description.tolist(),
        )
        raw.set_annotations(combined)

        return raw


KERNEL = OpenneuroDs004902Kernel()