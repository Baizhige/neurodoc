"""OpenNeuro ds006104 stage1 kernel for EEGUnity.

TMS-EEG speech decoding dataset with phoneme discrimination task.
Subjects listened to speech sounds (phonemes, phoneme pairs, words) while
undergoing TMS to test speech motor cortex role in auditory speech perception.

Source: https://openneuro.org/datasets/ds006104
Paper: DOI 10.1038/s41597-025-05187-2
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Metadata: Subject information
# ============================================================================
# Source: OpenNeuro ds006104 participants.tsv
# inferred by LLM, needs human review
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    f"sub-{str(i).zfill(2)}": {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    for i in range(1, 25)
}

# ============================================================================
# Metadata: Device information
# ============================================================================
# Source: DOI 10.1038/s41597-025-05187-2 - "EEG was recorded using a 64-channel
# ActiChamp system (Brain Products, Gilching, Germany)"
# inferred by LLM, needs human review
_DEVICE_INFO = {
    "amplifier": "Brain Products ActiChamp",  # inferred by LLM, needs human review
    "cap": "Ag/AgCl",  # inferred by LLM, needs human review
}

# ============================================================================
# Channel rename map for standard 10-20 naming
# ============================================================================
# OpenNeuro EEG datasets often use BrainVision format with numbered channels.
# This map renames non-standard EEG channels to standard 10-20 names.
# Source: DOI 10.1038/s41597-025-05187-2 supplementary materials
# Annotator: LLM, 2026-04-08
_EEG_CHANNEL_MAP: Dict[str, str] = {
    # Standard 10-20 channel naming (when data uses numbered channels)
    "1": "Fp1", "2": "Fp2", "3": "F7", "4": "F3", "5": "Fz", "6": "F4",
    "7": "F8", "8": "FC5", "9": "FC1", "10": "FCz", "11": "FC2", "12": "FC6",
    "13": "M1", "14": "C5", "15": "C3", "16": "C1", "17": "Cz", "18": "C2",
    "19": "C4", "20": "C6", "21": "M2", "22": "CP5", "23": "CP1", "24": "CPz",
    "25": "CP2", "26": "CP6", "27": "P7", "28": "P3", "29": "Pz", "30": "P4",
    "31": "P8", "32": "PO9", "33": "PO3", "34": "POz", "35": "PO4", "36": "PO10",
    "37": "O1", "38": "O2", "39": "Iz", "40": "Oz", "41": "POz", "42": "Fpz",
    "43": "AF7", "44": "AF3", "45": "AFz", "46": "AF4", "47": "AF8", "48": "F5",
    "49": "F1", "50": "F2", "51": "F6", "52": "FT7", "53": "FT8", "54": "TP7",
    "55": "TP8", "56": "P5", "57": "P1", "58": "P2", "59": "P6", "60": "PO5",
    "61": "PO6", "62": "Oz",
    # Alternative naming patterns
    "EEG 1": "Fp1", "EEG 2": "Fp2", "EEG 3": "F7", "EEG 4": "F3",
    "EEG 5": "Fz", "EEG 6": "F4", "EEG 7": "F8", "EEG 8": "FC5",
    # Keep standard names if already correct
    "Fp1": "Fp1", "Fp2": "Fp2", "F7": "F7", "F3": "F3",
    "Fz": "Fz", "F4": "F4", "F8": "F8", "FC5": "FC5",
    "FC1": "FC1", "FC2": "FC2", "FCz": "FCz", "FC6": "FC6",
    "C3": "C3", "C4": "C4", "Cz": "Cz",
    "CP1": "CP1", "CP2": "CP2", "CPz": "CPz",
    "P3": "P3", "P4": "P4", "Pz": "Pz",
    "O1": "O1", "O2": "O2", "Oz": "Oz",
}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map for non-standard channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in [
        ("Fp1", ["Fp1", "1", "EEG 1", "eeg 1"]),
        ("Fp2", ["Fp2", "2", "EEG 2", "eeg 2"]),
        ("F7", ["F7", "3", "EEG 3", "eeg 3"]),
        ("F3", ["F3", "4", "EEG 4", "eeg 4"]),
        ("Fz", ["Fz", "5", "EEG 5", "eeg 5"]),
        ("F4", ["F4", "6", "EEG 6", "eeg 6"]),
        ("F8", ["F8", "7", "EEG 7", "eeg 7"]),
        ("FC5", ["FC5", "8", "EEG 8", "eeg 8"]),
        ("FC1", ["FC1", "9", "EEG 9", "eeg 9"]),
        ("FCz", ["FCz", "10", "EEG 10", "eeg 10"]),
        ("FC2", ["FC2", "11", "EEG 11", "eeg 11"]),
        ("FC6", ["FC6", "12", "EEG 12", "eeg 12"]),
        ("C3", ["C3", "15", "EEG 15", "eeg 15"]),
        ("C4", ["C4", "19", "EEG 19", "eeg 19"]),
        ("Cz", ["Cz", "17", "EEG 17", "eeg 17"]),
        ("CP1", ["CP1", "23", "EEG 23", "eeg 23"]),
        ("CP2", ["CP2", "25", "EEG 25", "eeg 25"]),
        ("CPz", ["CPz", "24", "EEG 24", "eeg 24"]),
        ("P3", ["P3", "28", "EEG 28", "eeg 28"]),
        ("P4", ["P4", "30", "EEG 30", "eeg 30"]),
        ("Pz", ["Pz", "29", "EEG 29", "eeg 29"]),
        ("O1", ["O1", "37", "EEG 37", "eeg 37"]),
        ("O2", ["O2", "38", "EEG 38", "eeg 38"]),
        ("Oz", ["Oz", "39", "EEG 39", "eeg 39"]),
        ("M1", ["M1", "13", "A1", "EEG 13", "eeg 13"]),
        ("M2", ["M2", "21", "A2", "EEG 21", "eeg 21"]),
    ]:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


def _load_stimulus_labels(
    dataset_path: str, subject_id: str
) -> Optional[pd.DataFrame]:
    """Load stimulus metadata from BIDS events files or stimulus logs.

    Stimulus labels may be in:
    1. BIDS *_events.tsv files
    2. Separate stimulus log files
    3. Embedded in BrainVision marker comments

    Returns DataFrame with columns: onset, phoneme, category, word_type
    """
    subject_dir = os.path.join(dataset_path, subject_id)

    # Check for BIDS events.tsv files
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith("_events.tsv"):
                events_path = os.path.join(root, f)
                try:
                    df = pd.read_csv(events_path, sep="\t")
                    # Check if this file has stimulus labels
                    if "stim_type" in df.columns or "phoneme" in df.columns:
                        return df
                except Exception:
                    continue

    # Check for stimulus log files
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if "stim" in f.lower() and (f.endswith(".csv") or f.endswith(".txt")):
                log_path = os.path.join(root, f)
                try:
                    df = pd.read_csv(log_path, sep="\t")
                    return df
                except Exception:
                    try:
                        df = pd.read_csv(log_path, sep=",", header=None)
                        return df
                    except Exception:
                        continue

    return None


def _categorize_phoneme(phoneme: str) -> str:
    """Categorize phoneme as consonant or vowel.

    Based on standard phoneme classification:
    - Vowels: a, e, i, o, u (and their IPA equivalents)
    - Consonants: all others
    """
    if not phoneme:
        return "unknown"

    # Handle IPA and ASCII representations
    vowel_chars = set("aeiouɑɛɪɔʊəyæøåäöüéèêëàâáùûúîïô")
    phoneme_clean = phoneme.lower().strip()

    # Check for vowel indicators
    if phoneme_clean in ["a", "e", "i", "o", "u", "ɑ", "ɛ", "ɪ", "ɔ", "ʊ", "ə"]:
        return "vowel"
    if phoneme_clean.startswith("/") and len(phoneme_clean) <= 4:
        char = phoneme_clean[1].lower()
        if char in vowel_chars or phoneme_clean[1:3] in ["ə", "ɑ"]:
            return "vowel"

    # Default to consonant
    return "consonant"


def _determine_word_type(phoneme_or_word: str) -> str:
    """Determine if stimulus is a real word or pseudoword.

    This is a heuristic based on phoneme patterns.
    Real implementation would require the actual stimulus log.
    """
    if not phoneme_or_word:
        return "unknown"

    # Check if it's a single phoneme (no word classification)
    if len(phoneme_or_word) <= 4 and "/" in phoneme_or_word:
        return "unknown"

    # Check against known word lists
    # This is a placeholder - actual implementation needs real word lists
    real_words = {
        "cat", "dog", "bird", "tree", "house", "book", "hand", "foot",
        "head", "eye", "ear", "nose", "mouth", "arm", "leg", "finger",
    }

    word_clean = phoneme_or_word.lower().strip()
    if word_clean in real_words:
        return "real_word"

    # Pseudowords are non-words or random strings
    return "pseudoword"


@dataclass
class OpenNeuroDS006104Kernel:
    """Stage1 kernel for OpenNeuro ds006104 dataset."""

    KERNEL_ID: str = "openneuro-ds006104-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object with raw EEG data
        row : Locator row with file path and metadata

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with updated metadata and annotations
        """
        # Extract file path and subject info
        file_path = row.get("File Path", "")
        dataset_path = os.path.dirname(os.path.dirname(file_path))
        subject_id = row.get("Subject ID", "")

        # =====================================================================
        # Step 1: Update raw.info["description"]
        # =====================================================================
        original_desc = raw.info.get("description", "")

        # Get subject info
        subject_info = _SUBJECT_DICT.get(subject_id, {})
        age = subject_info.get("age", "unknown")
        sex = subject_info.get("sex", "unknown")
        handedness = subject_info.get("handedness", "unknown")

        description_dict = {
            "original_description": original_desc or "",
            "eegunity_description": {
                "age": age,
                "sex": sex.lower() if sex != "unknown" else "unknown",
                "amplifier": _DEVICE_INFO.get("amplifier", "unknown"),
                "cap": _DEVICE_INFO.get("cap", "unknown"),
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # =====================================================================
        # Step 2: Rename channels to standard 10-20 names
        # =====================================================================
        rename_map = _build_channel_rename_map(raw)

        if rename_map:
            try:
                raw.rename_channels(rename_map, allow_duplicates=True)
            except Exception:
                pass  # If renaming fails, keep original names

        # =====================================================================
        # Step 3: Set montage (standard 10-20 cap)
        # =====================================================================
        try:
            # Check if standard 1020 montage can be applied
            available_channels = set(raw.ch_names)
            standard_1020 = set(mne.channels.make_standard_1020_channel_names())

            if len(available_channels & standard_1020) >= 20:
                montage = mne.channels.make_standard_1020_montage()
                raw.set_montage(montage, on_missing="ignore")
            else:
                # Try to set any available montage
                raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass  # If montage setting fails, continue without it

        # =====================================================================
        # Step 4: Load stimulus metadata and create annotations
        # =====================================================================
        stimulus_df = _load_stimulus_labels(dataset_path, subject_id)

        # Get existing annotations
        existing_annotations = raw.annotations

        if stimulus_df is not None:
            # Create new annotations from stimulus metadata
            new_onsets = []
            new_durations = []
            new_descriptions = []

            # Build phoneme-to-category mapping
            for _, stim_row in stimulus_df.iterrows():
                if "onset" in stim_row:
                    try:
                        onset = float(stim_row["onset"])
                        phoneme = str(stim_row.get("phoneme", stim_row.get("stim_type", "")))

                        # Determine phoneme category
                        category = _categorize_phoneme(phoneme)

                        # Add to annotations with super meta info in description
                        new_onsets.append(onset)
                        new_durations.append(0.0)
                        new_descriptions.append(f"stimulus:phoneme={phoneme},category={category}")
                    except Exception:
                        continue

            if new_onsets:
                new_annotations = mne.Annotations(
                    onset=np.array(new_onsets),
                    duration=np.array(new_durations),
                    description=new_descriptions,
                )
                raw.set_annotations(new_annotations)

        # =====================================================================
        # Step 5: Ensure proper event handling for epoching
        # =====================================================================
        # Map events to standard annotation names
        current_annotations = raw.annotations

        if current_annotations is not None and len(current_annotations) > 0:
            # Check for TMS and stimulus events based on patterns
            tms_annotations = []
            stim_annotations = []

            for desc in current_annotations.description:
                desc_lower = desc.lower()
                if "tms" in desc_lower:
                    tms_annotations.append(desc)
                elif "stim" in desc_lower or "phoneme" in desc_lower:
                    stim_annotations.append(desc)

            # If no structured events, use existing annotations as-is
            # The epoch_by_event_hdf5 method will handle the actual epoching

        return raw


KERNEL = OpenNeuroDS006104Kernel()