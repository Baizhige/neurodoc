"""OpenNeuro DS004718 stage1 kernel for EEGUnity.

Le Petit Prince Hong Kong: Naturalistic fMRI and EEG Dataset.
Older Cantonese-speaking adults (65+) listened to a Cantonese translation
of "The Little Prince" during simultaneous EEG and fMRI recording.

Source: https://openneuro.org/datasets/ds004718
Paper: DOI 10.1038/s41597-024-03745-8

Tasks supported:
- Classical Task 1: Word-Onset ERP Classification (super meta, from NLP annotations)
- Classical Task 2: Story Section Code Classification (raw meta, codes 1-30+)
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


# Source: Paper DOI 10.1038/s41597-024-03745-8 - naturalistic listening study
# with older Cantonese-speaking adults (65+). Exact ages not in dataset.
# Annotator: LLM, 2025-01-15
_SUBJECT_METADATA_INFERENCE = {
    # All subjects are older adults (65+) per paper methodology
    # age/sex must come from participants.tsv or remain unknown
    "age_range": "65+",
    "population": "older Cantonese-speaking adults",
}

# Raw numeric event codes from STIM channel
# Source: Dataset events.tsv / analysis.md
_RAW_EVENT_MAP: Dict[str, str] = {
    "1": "story_code_1",
    "2": "story_code_2",
    "3": "story_code_3",
    "4": "story_code_4",
    "5": "story_code_5",
    "6": "story_code_6",
    "7": "story_code_7",
    "8": "story_code_8",
    "9": "story_code_9",
    "10": "story_code_10",
    "11": "story_code_11",
    "12": "story_code_12",
    "13": "story_code_13",
    "14": "story_code_14",
    "15": "story_code_15",
    "16": "story_code_16",
    "17": "story_code_17",
    "18": "story_code_18",
    "19": "story_code_19",
    "20": "story_code_20",
    "21": "story_code_21",
    "22": "story_code_22",
    "23": "story_code_23",
    "24": "story_code_24",
    "25": "story_code_25",
    "26": "story_code_26",
    "27": "story_code_27",
    "28": "story_code_28",
    "29": "story_code_29",
    "30": "story_code_30",
    # Additional codes observed in analysis
    "40": "story_code_40",
    "41": "story_code_41",
    "42": "story_code_42",
    "43": "story_code_43",
    "44": "story_code_44",
    "45": "story_code_45",
    "46": "story_code_46",
    "47": "story_code_47",
    "48": "story_code_48",
    "49": "story_code_49",
    "50": "story_code_50",
    "51": "story_code_51",
    "52": "story_code_52",
    "53": "story_code_53",
    "54": "story_code_54",
    "55": "story_code_55",
    "56": "story_code_56",
    "57": "story_code_57",
    "58": "story_code_58",
    "59": "story_code_59",
    "60": "story_code_60",
    "61": "story_code_61",
    "62": "story_code_62",
    "63": "story_code_63",
    "64": "story_code_64",
    "65": "story_code_65",
    "66": "story_code_66",
    "67": "story_code_67",
    "68": "story_code_68",
    "69": "story_code_69",
    "70": "story_code_70",
    "71": "story_code_71",
    "72": "story_code_72",
    "73": "story_code_73",
    "74": "story_code_74",
    "75": "story_code_75",
    "76": "story_code_76",
    "77": "story_code_77",
    "78": "story_code_78",
    "79": "story_code_79",
    "80": "story_code_80",
    "81": "story_code_81",
    "82": "story_code_82",
    "83": "story_code_83",
    "84": "story_code_84",
    "85": "story_code_85",
    "86": "story_code_86",
    "87": "story_code_87",
    "88": "story_code_88",
    "89": "story_code_89",
    "90": "story_code_90",
    "91": "story_code_91",
    "92": "story_code_92",
    "93": "story_code_93",
    "94": "story_code_94",
    "95": "story_code_95",
    "96": "story_code_96",
    "97": "story_code_97",
    "98": "story_code_98",
    "99": "story_code_99",
    "100": "story_code_100",
    "101": "story_code_101",
    "102": "story_code_102",
    "103": "story_code_103",
    "104": "story_code_104",
    "105": "story_code_105",
    "106": "story_code_106",
    "107": "story_code_107",
    "108": "story_code_108",
    "109": "story_code_109",
    "110": "story_code_110",
    "111": "story_code_111",
    "112": "story_code_112",
}


def _load_word_onset_annotations(dataset_path: str, row) -> Optional[mne.Annotations]:
    """Load word-onset timestamps from NLP-aligned annotations file.

    The paper (DOI 10.1038/s41597-024-03745-8) describes NLP text-audio alignment
    pipeline that provides word-onset timestamps separate from raw STIM triggers.

    Returns None if annotations file is not found.
    """
    # Try common annotation file locations in OpenNeuro BIDS structure
    file_path = row.get("File Path", "")
    if not file_path:
        return None

    base_dir = os.path.dirname(os.path.dirname(file_path))  # go up from sub-*/eeg/

    possible_annotation_paths = [
        os.path.join(base_dir, "annotations", "word_onsets.csv"),
        os.path.join(base_dir, "annotations", f"{row.get('subject_id', 'sub')}_word_onsets.csv"),
        os.path.join(base_dir, "stimuli", "word_onsets.csv"),
        os.path.join(base_dir, "stimuli", f"{os.path.basename(file_path).replace('.eeg', '_word_onsets.csv')}"),
    ]

    # Also try to find any CSV file containing word onset data
    stimuli_dir = os.path.join(base_dir, "stimuli")
    annotations_dir = os.path.join(base_dir, "annotations")

    for search_dir in [stimuli_dir, annotations_dir, base_dir]:
        if os.path.exists(search_dir):
            try:
                for fname in os.listdir(search_dir):
                    if "word" in fname.lower() and fname.endswith(".csv"):
                        possible_annotation_paths.insert(0, os.path.join(search_dir, fname))
            except OSError:
                pass

    for annotation_path in possible_annotation_paths:
        if os.path.exists(annotation_path):
            try:
                df = pd.read_csv(annotation_path)
                # Expected columns: onset, word, possibly duration
                if "onset" in df.columns:
                    onset_col = "onset"
                elif "timestamp" in df.columns:
                    onset_col = "timestamp"
                elif "time" in df.columns:
                    onset_col = "time"
                else:
                    # Try first numeric column
                    for col in df.columns:
                        if df[col].dtype in [np.float64, np.int64]:
                            onset_col = col
                            break
                    else:
                        continue

                onset_times = df[onset_col].values
                descriptions = df.get("word", df.get("stimulus", ["word_onset"] * len(onset_times)))
                if isinstance(descriptions, str):
                    descriptions = [descriptions] * len(onset_times)
                elif len(descriptions) != len(onset_times):
                    descriptions = ["word_onset"] * len(onset_times)

                return mne.Annotations(
                    onset=onset_times,
                    duration=[0.0] * len(onset_times),
                    description=["word_onset"] * len(onset_times),
                )
            except Exception:
                continue

    return None


def _remap_annotations_to_raw_events(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap numeric STIM annotations to descriptive event labels."""
    try:
        events, event_id = mne.events_from_annotations(raw, verbose=False)
    except Exception:
        return raw

    # Build reverse mapping from numeric code to new label
    new_descriptions = []
    for desc in raw.annotations.description:
        # Try to extract numeric code
        if desc.isdigit():
            new_desc = _RAW_EVENT_MAP.get(desc, f"event_{desc}")
        else:
            new_desc = _RAW_EVENT_MAP.get(str(desc), desc)
        new_descriptions.append(new_desc)

    # Create new annotations with remapped descriptions
    new_annotations = mne.Annotations(
        onset=raw.annotations.onset,
        duration=raw.annotations.duration,
        description=new_descriptions,
        orig_time=raw.annotations.orig_time,
    )
    raw.set_annotations(new_annotations)

    return raw


def _set_eegunity_description(raw: mne.io.BaseRaw, subject_info: Dict[str, str]) -> None:
    """Set standardized eegunity_description in raw.info['description']."""
    original_desc = raw.info.get("description", "")

    description_dict = {
        "original_description": str(original_desc) if original_desc else "",
        "eegunity_description": {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown").lower(),
            "amplifier": subject_info.get("amplifier", "unknown"),
            "cap": subject_info.get("cap", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
        },
    }
    raw.info["description"] = json.dumps(description_dict)


@dataclass
class OpenNeuroDS004718Kernel:
    """Stage1 kernel for OpenNeuro DS004718 - Le Petit Prince Hong Kong."""

    KERNEL_ID: str = "openneuro-ds004718-stage1"

    HANDLES_UNAVAILABLE: bool = True  # Set to True to use custom load()

    def load(self, file_path: str, udataset=None) -> mne.io.BaseRaw:
        """Load EEG file and build Raw object.

        This method handles files that EEGUnity cannot parse directly.
        """
        # Try standard MNE loaders first
        try:
            raw = mne.io.read_raw_brainvision(file_path, preload=False, verbose=False)
            return raw
        except Exception:
            pass

        try:
            raw = mne.io.read_raw_eeglab(file_path, preload=False, verbose=False)
            return raw
        except Exception:
            pass

        try:
            raw = mne.io.read_raw_fif(file_path, preload=False, verbose=False)
            return raw
        except Exception:
            pass

        try:
            raw = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
            return raw
        except Exception:
            pass

        try:
            raw = mne.io.read_raw_bdf(file_path, preload=False, verbose=False)
            return raw
        except Exception:
            pass

        # Last resort: use auto-detection
        raw = mne.io.read_raw(file_path, preload=False, verbose=False)
        return raw

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized metadata and annotations.
        """
        # Extract subject information from row or participants.tsv
        subject_info = self._extract_subject_info(udataset, row)

        # Set eegunity_description
        _set_eegunity_description(raw, subject_info)

        # Remap numeric STIM events to descriptive labels (raw meta)
        raw = _remap_annotations_to_raw_events(raw)

        # Attempt to load word-onset annotations (super meta)
        word_annotations = _load_word_onset_annotations(
            udataset.dataset_path if hasattr(udataset, "dataset_path") else "",
            row,
        )

        if word_annotations is not None:
            # Merge with existing annotations
            existing = raw.annotations
            merged_onset = list(existing.onset) + list(word_annotations.onset)
            merged_duration = list(existing.duration) + list(word_annotations.duration)
            merged_description = list(existing.description) + list(word_annotations.description)

            merged_annotations = mne.Annotations(
                onset=merged_onset,
                duration=merged_duration,
                description=merged_description,
                orig_time=existing.orig_time,
            )
            raw.set_annotations(merged_annotations)

        return raw

    def _extract_subject_info(self, udataset, row) -> Dict[str, str]:
        """Extract subject metadata from participants.tsv or row."""
        subject_info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }

        # Try to get from participants.tsv via udataset
        if hasattr(udataset, "participants_df") and udataset.participants_df is not None:
            subject_id = row.get("subject_id", "")
            if subject_id:
                # Remove 'sub-' prefix if present
                subject_id_clean = re.sub(r"^sub-", "", subject_id)
                row_filter = udataset.participants_df[
                    udataset.participants_df["participant_id"].str.contains(subject_id_clean, na=False)
                ]
                if not row_filter.empty:
                    p_row = row_filter.iloc[0]
                    if "age" in udataset.participants_df.columns:
                        age_val = p_row.get("age")
                        if pd.notna(age_val):
                            subject_info["age"] = str(age_val)
                    if "sex" in udataset.participants_df.columns:
                        sex_val = p_row.get("sex")
                        if pd.notna(sex_val):
                            subject_info["sex"] = str(sex_val).lower()
                    if "handedness" in udataset.participants_df.columns:
                        handedness_val = p_row.get("handedness")
                        if pd.notna(handedness_val):
                            subject_info["handedness"] = str(handedness_val).lower()

        # Fallback: check row directly
        if subject_info["age"] == "unknown":
            age = row.get("age")
            if age:
                subject_info["age"] = str(age)

        if subject_info["sex"] == "unknown":
            sex = row.get("sex")
            if sex:
                subject_info["sex"] = str(sex).lower()

        # inferred by LLM, needs human review - amplifier and cap info from paper
        # Paper DOI 10.1038/s41597-024-03745-8 mentions "MRI-compatible EEG system"
        # but specific amplifier model not documented in dataset metadata
        # Annotator: LLM, 2025-01-15
        if subject_info["amplifier"] == "unknown":
            # Check dataset_description.json for equipment info
            if hasattr(udataset, "dataset_path"):
                desc_path = os.path.join(udataset.dataset_path, "dataset_description.json")
                if os.path.exists(desc_path):
                    try:
                        with open(desc_path) as f:
                            desc = json.load(f)
                        if "EEGReference" in desc:
                            subject_info["cap"] = desc["EEGReference"]
                    except Exception:
                        pass

        return subject_info


KERNEL = OpenNeuroDS004718Kernel()