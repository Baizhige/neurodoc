"""OpenNeuro DS003690 stage1 kernel for EEGUnity.

EEG, ECG and Pupil Data from Young and Older Adults:
Rest and Auditory Cued Reaction Time Tasks.

Source: https://openneuro.org/datasets/ds003690
Paper: https://doi.org/10.1016/j.neuroimage.2019.06.004
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# =============================================================================
# Event code mapping (numeric -> human-readable)
# Source: OpenNeuro dataset documentation and paper analysis
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# =============================================================================
_EVENT_CODE_MAP: Dict[int, str] = {
    4: "go",
    5: "button press",
    6: "error of commission",
    10: "cue",
    88: "error feedback tone",   # LLM 推断，需人类复核
    99: "task end",               # LLM 推断，需人类复核
    # 1500: no-go stimulus (appears in combined go/no-go block)
}


# =============================================================================
# Subject metadata
# Source: Paper DOI 10.1016/j.neurobiolaging.2018.09.028 indicates
#         36 young adults and 39 older adults (total 75 subjects)
# Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
# =============================================================================
_SUBJECT_METADATA: Dict[str, Dict[str, str]] = {
    # Format: sub-XXX -> {age, sex, handedness}
    # Ages unknown from public documentation; default to "unknown"
}


def _detect_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    parts = os.path.basename(file_path).split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part.replace("sub-", "")
    return None


def _load_subject_info(dataset_root: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from BIDS participants.tsv."""
    participants_tsv = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_tsv):
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
            row = df[df[subject_col] == f"sub-{subject_id}"]
            if not row.empty:
                age = str(row.iloc[0].get("age", "unknown"))
                sex = str(row.iloc[0].get("sex", "unknown")).lower()
                handedness = str(row.iloc[0].get("handedness", "unknown")).lower()
                return {
                    "age": age if age and age != "nan" else "unknown",
                    "sex": sex if sex and sex != "nan" else "unknown",
                    "handedness": handedness if handedness and handedness != "nan" else "unknown",
                }
        except Exception:
            pass
    return {"age": "unknown", "sex": "unknown", "handedness": "unknown"}


def _apply_channel_standardization(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Standardize channel names to 10-20 system."""
    ch_names = raw.ch_names
    rename_map = {}
    
    # Common patterns in EEG data
    for ch in ch_names:
        ch_upper = ch.upper()
        # Already standard names
        if ch in {"Fz", "Cz", "Pz", "Oz", "Fpz", "Fp1", "Fp2",
                  "F3", "F4", "F7", "F8", "C3", "C4", "T7", "T8",
                  "P3", "P4", "P7", "P8", "O1", "O2", "T3", "T4",
                  "F1", "F2", "F5", "F6", "C1", "C2", "C5", "C6",
                  "P1", "P2", "P5", "P6", "POz", "PO3", "PO4",
                  "FCz", "FC1", "FC2", "FC3", "FC4", "FC5", "FC6",
                  "CPz", "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
                  "AFz", "AF3", "AF4", "AF7", "AF8"}:
            continue
        # EEG-0, EEG-1, ... -> standard locations (66 channels)
        if ch.startswith("EEG-") and ch[4:].isdigit():
            idx = int(ch[4:])
            # Standard 64-channel layout mapping
            standard_64 = [
                "Fp1", "Fpz", "Fp2", "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
                "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
                "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
                "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
                "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
                "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
                "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
                "O1", "Oz", "O2", "OI1", "OIz", "OI2"
            ]
            if idx < len(standard_64):
                rename_map[ch] = standard_64[idx]
        # Other patterns
        elif ch.startswith("EEG ") or ch.startswith("EEG"):
            # Try to extract number
            parts = ch.replace("EEG", "").strip()
            if parts.isdigit():
                idx = int(parts)
                standard_64 = [
                    "Fp1", "Fpz", "Fp2", "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF6", "AF8", "AF10",
                    "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
                    "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
                    "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
                    "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
                    "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
                    "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
                    "O1", "Oz", "O2", "OI1", "OIz", "OI2"
                ]
                if idx < len(standard_64):
                    rename_map[ch] = standard_64[idx]
    
    if rename_map:
        renamed = mne.rename_channels(raw.info, rename_map)
        if renamed:
            pass  # Successfully renamed
    
    # Set montage if all channels are standard
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="ignore")
    except Exception:
        pass
    
    return raw


class OpenNeuroDS003690Kernel:
    """Stage1 kernel for OpenNeuro DS003690 dataset."""

    KERNEL_ID: str = "openneuro-ds003690-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Record metadata (pandas.Series-like) with File Path

        Returns
        -------
        mne.io.BaseRaw
        """
        file_path = row.get("File Path", "")
        dataset_root = row.get("Dataset Root", "")

        # Extract subject info
        subject_id = _detect_subject_id(file_path)
        if subject_id and subject_id not in _SUBJECT_METADATA:
            _SUBJECT_METADATA[subject_id] = _load_subject_info(dataset_root, subject_id)

        subject_info = _SUBJECT_METADATA.get(subject_id, {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        })

        # Build description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_info["age"],
                "sex": subject_info["sex"],
                "amplifier": "BrainAmp" if "brainamp" in original_desc.lower() else "unknown",
                "cap": "Ag/AgCl",  # LLM 推断，需人类复核
                "handedness": subject_info["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Apply channel standardization
        raw = _apply_channel_standardization(raw)

        # Map events from numeric codes to human-readable labels
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if events.size > 0:
                # Create reverse mapping for known codes
                numeric_to_label = {v: k for k, v in event_id.items()}
                
                # Map numeric event codes to canonical labels
                new_annotations = []
                for event in events:
                    onset = event[0] / raw.info["sfreq"]
                    original_desc = numeric_to_label.get(event[2], str(event[2]))
                    
                    # Try to parse as integer for code mapping
                    try:
                        code = int(float(original_desc))
                        if code in _EVENT_CODE_MAP:
                            label = _EVENT_CODE_MAP[code]
                        else:
                            label = original_desc
                    except (ValueError, TypeError):
                        label = original_desc
                    
                    new_annotations.append({
                        "onset": onset,
                        "duration": 0.0,
                        "description": label,
                    })

                if new_annotations:
                    onsets = [a["onset"] for a in new_annotations]
                    durations = [a["duration"] for a in new_annotations]
                    descriptions = [a["description"] for a in new_annotations]
                    
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                    )
                    raw.set_annotations(annotations)
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS003690Kernel()