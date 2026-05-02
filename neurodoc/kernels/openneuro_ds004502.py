"""OpenNeuro DS004502 stage1 kernel for EEGUnity.

Dataset: Anticipatory differences between Attention and Expectation
URL: https://openneuro.org/datasets/ds004502
DOI: https://doi.org/10.18112/openneuro.ds004502.v1.0.1

Paradigm: EEG study disentangling attention (stimulus-driven) from
expectation (predictive) effects on anticipatory neural activity.
63-channel BrainVision recording at 1000 Hz.

Event mapping:
  - S 17-S 32 (16 codes): Attention condition → y=0
  - S 33-S 48 (16 codes): Expectation condition → y=1
  - S 50 (49174 counts): long-duration status flag → EXCLUDE
  - S 60-S 105: continuous phase markers → verify before use

Task: Binary classification (attention vs expectation)
Epoch: tmin=-0.2 s, tmax=1.0 s relative to event onset
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import pandas as pd


# BrainVision stimulus onset codes for attention condition (y=0)
_ATTENTION_CODES = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
# BrainVision stimulus onset codes for expectation condition (y=1)
_EXPECTATION_CODES = [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]

# Event-to-label mapping (raw meta level)
_EVENT_MAP: Dict[str, str] = {
    f"S {code}": f"Attention-{code}" for code in _ATTENTION_CODES
}
_EVENT_MAP.update({f"S {code}": f"Expectation-{code}" for code in _EXPECTATION_CODES})

# Codes to exclude from epoch extraction
_EXCLUDE_CODES = {50}  # S 50: long-duration status flag
# Phase markers (S 60-S 105): verify in events.tsv before use; exclude by default
_EXCLUDE_CODES.update(range(60, 106))


def _normalize_trigger_code(description: str) -> str:
    """Normalize BrainVision trigger code to 'S N' format.

    Parameters
    ----------
    description : str
        Trigger description, e.g. "Stimulus/S  17", "S 17", or "17".

    Returns
    -------
    str
        Normalized code in "S N" format.
    """
    # Remove common prefixes
    cleaned = description.replace("Stimulus/", "").strip()
    # Remove leading zeros if present (e.g., "S 017" -> "S 17")
    parts = cleaned.split()
    if len(parts) == 2 and parts[0] in ("S", "Stimulus"):
        try:
            num = int(parts[1])
            return f"S {num}"
        except ValueError:
            pass
    return description


def _detect_subject_id(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path.

    Parameters
    ----------
    file_path : str
        Full path to the EEG file.

    Returns
    -------
    str or None
        Subject ID like "sub-01" or None if not found.
    """
    import re

    match = re.search(r"(sub-[A-Za-z0-9]+)", file_path)
    return match.group(1) if match else None


class OpenNeuroDS004502Kernel:
    """Stage1 kernel for OpenNeuro DS004502 dataset."""

    KERNEL_ID: str = "openneuro-ds004502-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single EEG recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context.
        raw : MNE Raw object loaded from BrainVision files.
        row : Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Processed Raw object with annotations and description.
        """
        file_path = row.get("File Path", "")
        subject_id = _detect_subject_id(file_path)

        # ─── 1. Build trigger-to-label mapping ───────────────────────────────
        # Combine BrainVision trigger codes with events.tsv (if available)
        label_map: Dict[str, str] = {}
        label_map.update(_EVENT_MAP)

        # Try to load events.tsv for semantic label enrichment
        events_tsv = _find_events_tsv(file_path)
        if events_tsv and os.path.exists(events_tsv):
            try:
                events_df = pd.read_csv(events_tsv, sep="\t")
                # Standard BIDS events.tsv columns: onset, duration, trial_type
                if "trial_type" in events_df.columns or "value" in events_df.columns:
                    label_col = "trial_type" if "trial_type" in events_df.columns else "value"
                    # events.tsv may have more descriptive labels; merge
                    for _, evt_row in events_df.iterrows():
                        raw_desc = str(evt_row.get("value", ""))
                        label = str(evt_row.get(label_col, raw_desc))
                        normalized = _normalize_trigger_code(raw_desc)
                        if normalized.startswith("S "):
                            code_num = int(normalized.split()[1])
                            if code_num not in _EXCLUDE_CODES:
                                label_map[normalized] = label
            except Exception:
                pass  # Fall back to _EVENT_MAP

        # ─── 2. Extract events from raw annotations ───────────────────────────
        try:
            events, event_id = mne.events_from_annotations(raw)
            raw_annots = raw.annotations
        except ValueError:
            events = []
            event_id = {}
            raw_annots = mne.Annotations(onset=[], duration=[], description=[])

        # Build new annotation descriptions using label_map
        new_descriptions: List[str] = []
        new_onsets: List[float] = []
        new_durations: List[float] = []

        for i, desc in enumerate(raw_annots.description):
            normalized = _normalize_trigger_code(str(desc))
            code_num = int(normalized.split()[1]) if normalized.startswith("S ") else None

            # Exclude long-duration status flags and phase markers
            if code_num is not None and code_num in _EXCLUDE_CODES:
                continue

            # Map to semantic label if available
            mapped_label = label_map.get(normalized)
            if mapped_label is None:
                # Fall back to normalized code
                mapped_label = normalized if normalized.startswith("S ") else str(desc)

            new_descriptions.append(mapped_label)
            new_onsets.append(raw_annots.onset[i])
            new_durations.append(raw_annots.duration[i])

        # Set filtered annotations
        if new_descriptions:
            filtered_annotations = mne.Annotations(
                onset=new_onsets,
                duration=new_durations,
                description=new_descriptions,
                orig_time=raw_annots.orig_time,
            )
            raw.set_annotations(filtered_annotations)

        # ─── 3. Channel renaming ─────────────────────────────────────────────
        # Source: Dataset paper (NeuroImage 2022, 119789) indicates standard
        # 64-channel BrainVision system. 63 channels suggests no explicit
        # reference channel or Cz treated as reference.
        # Channel naming convention: standard 10-20 names.
        rename_map = _build_channel_rename_map(raw)

        if rename_map:
            try:
                raw.rename_channels(rename_map)
            except Exception:
                pass  # Skip if rename fails

        # ─── 4. Set montage ───────────────────────────────────────────────────
        # Standard 10-20 cap with 63 channels; use standard_1020 with fallback
        try:
            montage = mne.channels.make_standard_standard_montage(
                kind="standard_1020"
            )
            # Remove any channels not in standard_1020 before setting
            present_chs = [ch for ch in raw.ch_names if ch in montage.ch_names]
            if len(present_chs) >= 10:
                raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage optional for stage1 kernel

        # ─── 5. Write eegunity_description ───────────────────────────────────
        # Attempt to load from participants.tsv
        age_val = "unknown"
        sex_val = "unknown"
        handedness_val = "unknown"

        participants_tsv = _find_participants_tsv(file_path)
        if participants_tsv and os.path.exists(participants_tsv):
            try:
                subj_df = pd.read_csv(participants_tsv, sep="\t")
                subj_id_short = subject_id.replace("sub-", "") if subject_id else None
                if subj_id_short and "participant_id" in subj_df.columns:
                    row_match = subj_df[subj_df["participant_id"] == subject_id]
                    if not row_match.empty:
                        # age: may be numeric or string
                        age_raw = row_match.iloc[0].get("age", "unknown")
                        if age_raw != "unknown" and pd.notna(age_raw):
                            age_val = str(int(float(age_raw)))
                        # sex/gender: normalize to lowercase
                        sex_raw = row_match.iloc[0].get("sex", row_match.iloc[0].get("gender", "unknown"))
                        if sex_raw != "unknown" and pd.notna(sex_raw):
                            sex_val = str(sex_raw).strip().lower()
                            if sex_val not in ("male", "female"):
                                sex_val = "unknown"
                        # handedness: may be "handedness" or "hand"
                        handedness_raw = row_match.iloc[0].get("handedness", row_match.iloc[0].get("hand", "unknown"))
                        if handedness_raw != "unknown" and pd.notna(handedness_raw):
                            handedness_val = str(handedness_raw).strip().lower()
                            if handedness_val not in ("right", "left"):
                                handedness_val = "unknown"
            except Exception:
                pass  # All fields remain "unknown"

        # Amplifier/cap from dataset metadata (BrainVision system)
        # Source: OpenNeuro dataset_description.json and paper methods
        # inferred by LLM, needs human review
        amplifier_val = "BrainAmp"  # BrainVision amplifier family
        cap_val = "Ag/AgCl"  # Standard EEG cap material

        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": age_val,
                "sex": sex_val,
                "amplifier": amplifier_val,
                "cap": cap_val,
                "handedness": handedness_val,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Locate events.tsv sidecar for a given EEG file.

    Parameters
    ----------
    file_path : str
        Path to the .eeg or .vhdr file.

    Returns
    -------
    str or None
        Path to events.tsv if found.
    """
    base = os.path.splitext(file_path)[0]
    candidates = [
        base + "_events.tsv",
        base.replace("_eeg/", "_beh/") + "_events.tsv",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    # Fall back to directory search
    eeg_dir = os.path.dirname(file_path)
    for fname in os.listdir(eeg_dir):
        if fname.endswith("_events.tsv"):
            return os.path.join(eeg_dir, fname)
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Locate participants.tsv for a given file.

    Parameters
    ----------
    file_path : str
        Path to any file within the BIDS dataset.

    Returns
    -------
    str or None
        Path to participants.tsv if found.
    """
    # Walk up from file to dataset root
    current = os.path.dirname(file_path)
    while current and current != os.path.dirname(current):
        candidate = os.path.join(current, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        current = os.path.dirname(current)
    return None


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a channel rename map for non-standard BrainVision channel names.

    BrainVision recordings may use names like "EEG001", "EEG002", etc.
    or standard 10-20 names depending on export settings. This function
    attempts to map both conventions to the standard 10-20 names.

    Source: Standard 10-20 electrode positions (64-channel cap, 63 used).
    Channel order follows BrainVision standard arrangement.
    Annotator: LLM, 2026-04-08 — inferred by LLM, needs human review

    Parameters
    ----------
    raw : MNE Raw object.

    Returns
    -------
    Dict[str, str]
        Mapping from source channel names to standard names.
    """
    # Standard 10-20 names for 63-channel BrainVision system
    # Ordering follows BrainVision standard export
    standard_63 = [
        "Fp1", "Fpz", "Fp2",
        "AF7", "AF3", "AFz", "AF4", "AF8",
        "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
        "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
        "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
        "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
        "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
        "PO7", "PO3", "POz", "PO4", "PO8",
        "O1", "Oz", "O2",
        "POz",  # already included above, duplicates possible
    ]
    standard_63 = list(dict.fromkeys(standard_63))  # Remove duplicates, preserve order

    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Pattern 1: EEG001, EEG002, ... (numeric suffix)
    import re
    eeg_pattern = re.compile(r"^EEG(-?\d+)$", re.IGNORECASE)
    for ch in raw.ch_names:
        match = eeg_pattern.match(ch)
        if match:
            idx = int(match.group(1))
            # Map EEG index to standard_1020 name (0-indexed into standard list)
            if 0 <= idx < len(standard_63):
                target = standard_63[idx]
                if target != ch and target in existing:
                    rename_map[ch] = target

    # Pattern 2: Already standard names that just need capitalization fix
    for ch in raw.ch_names:
        for std_ch in standard_63:
            if ch.lower() == std_ch.lower() and ch != std_ch:
                if std_ch in existing:
                    rename_map[ch] = std_ch
                    break

    return rename_map


KERNEL = OpenNeuroDS004502Kernel()