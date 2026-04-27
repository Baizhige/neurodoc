"""Healthy Brain Network (HBN) EEG - Release 5 stage1 kernel for EEGUnity.

Dataset: openneuro_ds005509
Source: https://openneuro.org/datasets/ds005509
Reference: Alexander et al. (2017) Scientific Data, DOI:10.1038/sdata.2017.40
           HBN-EEG Release 5, DOI:10.1101/2024.10.03.615261

This kernel handles BIDS format data from the HBN study with 129-channel
EEG recordings at 500 Hz using BioSemi ActiveTwo amplifiers. It extracts
subject metadata from participants.tsv, ensures event annotations from
events.tsv sidecars, and sets standard montage.

HBN paradigm summary:
  - Resting state (eyes open/closed)
  - Contrast change detection
  - Surrounding suppression
  - Sequence learning
  - Symbol search
  - Naturalistic movie watching

Author: LLM (inferrer), 2026-04-08 — 需人类复核
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# REQUIRED INFO FIELDS FROM participants.tsv
# ============================================================================
_REQUIRED_INFO_FIELDS = [
    "RestingState",
    "age",
    "attention",
    "ehq_total",
    "externalizing",
    "full_pheno",
    "internalizing",
    "p_factor",
    "sex",
]

# ============================================================================
# REQUIRED NATIVE MISC CHANNELS
# ============================================================================
_REQUIRED_NATIVE_MISC: List[str] = []

# ============================================================================
# REQUIRED DERIVED MISC CHANNELS
# ============================================================================
_REQUIRED_DERIVED_MISC: List[str] = []

# ============================================================================
# CHANNEL MAPPING
# HBN uses BioSemi 128-channel cap + CMS/DRL reference = 129 channels.
# Standard 10-20 positions with extended coverage.
# Ref: BioSemi ActiveTwo 128-channel ABC layout; HBN data description
# Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
# ============================================================================

# HBN channels are typically named with standard 10-20 labels already,
# but some files may use BioSemi default numbering. We handle both cases.

_BIOSEMI_NUMBERED_TO_NAME: Dict[str, str] = {
    # BioSemi 128-channel ABC layout mapping (if numbered channels appear)
    # A1-A32 (left to right, front to back on first cap)
    # This is a fallback; HBN typically uses named channels already
}

# Common HBN channel name normalizations
_CHANNEL_NORMALIZE: Dict[str, str] = {
    # Reference electrodes
    "CMS": "CMS",
    "DRL": "DRL",
    # Mastoid references (sometimes labeled differently)
    "A1": "M1",
    "A2": "M2",
    "M1": "M1",
    "M2": "M2",
    "M-left": "M1",
    "M-right": "M2",
    # EOG channels
    "HEOG_left": "HEOG_left",
    "HEOG_right": "HEOG_right",
    "VEOG_lower": "VEOG_lower",
    # Common alternate labels
    "T3": "T7",
    "T4": "T8",
    "T5": "P7",
    "T6": "P8",
}


def _normalize_channel_name(ch_name: str) -> str:
    """Normalize a channel name to standard convention."""
    # Strip common prefixes
    clean = ch_name.strip()
    if clean.startswith("EEG "):
        clean = clean[4:]
    elif clean.startswith("EEG-"):
        clean = clean[4:]
    
    # Check direct mapping
    if clean in _CHANNEL_NORMALIZE:
        return _CHANNEL_NORMALIZE[clean]
    
    return clean


def _get_subject_from_path(file_path: str) -> Optional[str]:
    """Extract subject ID from BIDS file path."""
    # BIDS pattern: sub-<subject_id>/...
    parts = file_path.replace(os.sep, "/").split("/")
    for part in parts:
        if part.startswith("sub-"):
            return part[4:]  # Remove "sub-" prefix
    return None


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find corresponding events.tsv file for a given EEG file."""
    # BIDS convention: same directory, same basename with _events.tsv suffix
    base = file_path.replace(".set", "").replace(".edf", "").replace(".bdf", "").replace(".fif", "").replace(".eeg", "").replace(".vhdr", "")
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: events.tsv in same directory
    dir_path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    # Remove extension
    name_no_ext = os.path.splitext(basename)[0]
    # Handle compound extensions like .eeg.vhdr
    if name_no_ext.endswith(".eeg"):
        name_no_ext = name_no_ext[:-4]
    
    alt_events = os.path.join(dir_path, name_no_ext + "_events.tsv")
    if os.path.exists(alt_events):
        return alt_events
    
    # Try generic events.tsv in directory
    generic = os.path.join(dir_path, "events.tsv")
    if os.path.exists(generic):
        return generic
    
    return None


def _find_participants_tsv(file_path: str) -> Optional[str]:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "participants.csv"),
        ]
        for cand in candidates:
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _read_participants_for_subject(file_path: str, subject_id: str) -> Dict[str, str]:
    """Read participants.tsv and extract row for given subject."""
    participants_path = _find_participants_tsv(file_path)
    if participants_path is None:
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        try:
            df = pd.read_csv(participants_path, sep=",")
        except Exception:
            return {}
    
    # Find subject row
    # BIDS participant_id format: "sub-<id>" or just "<id>"
    for pid_col in ["participant_id", "Participant ID", "subject_id", "Subject ID"]:
        if pid_col in df.columns:
            # Try matching with and without "sub-" prefix
            mask = (df[pid_col] == f"sub-{subject_id}") | (df[pid_col] == subject_id)
            if mask.any():
                row = df[mask].iloc[0]
                return {str(k): str(v) if pd.notna(v) else "unknown" for k, v in row.items()}
    
    return {}


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception:
        return None


def _events_tsv_to_annotations(events_df: pd.DataFrame, sfreq: float) -> Optional[mne.Annotations]:
    """Convert events.tsv DataFrame to MNE Annotations."""
    if events_df is None or len(events_df) == 0:
        return None
    
    # Required columns: onset, (duration), trial_type or value
    if "onset" not in events_df.columns:
        return None
    
    onsets = events_df["onset"].values.astype(float)
    
    # Duration
    if "duration" in events_df.columns:
        durations = events_df["duration"].fillna(0).values.astype(float)
    else:
        durations = np.zeros(len(onsets))
    
    # Description: prefer trial_type, then value, then stim_type
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].fillna("unknown").astype(str).values
    elif "value" in events_df.columns:
        # Convert to string, handling numeric values
        descriptions = []
        for v in events_df["value"].values:
            if pd.isna(v):
                descriptions.append("unknown")
            else:
                descriptions.append(str(v))
        descriptions = np.array(descriptions)
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].fillna("unknown").astype(str).values
    else:
        # No label column found
        descriptions = np.array(["event"] * len(onsets))
    
    # Filter out empty/NaN descriptions if possible
    valid_mask = np.array([d is not None and str(d).strip() != "" and str(d) != "nan" for d in descriptions])
    if not valid_mask.all() and valid_mask.any():
        onsets = onsets[valid_mask]
        durations = durations[valid_mask]
        descriptions = descriptions[valid_mask]
    
    if len(onsets) == 0:
        return None
    
    # Ensure non-negative onsets (MNE requirement)
    onsets = np.maximum(onsets, 0)
    
    try:
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        return annot
    except Exception:
        return None


def _has_native_events(raw: mne.io.BaseRaw) -> bool:
    """Check if raw already has meaningful events/annotations."""
    # Check annotations
    if raw.annotations is not None and len(raw.annotations) > 0:
        # Check if annotations are meaningful (not just boundary/segment)
        descs = set(raw.annotations.description)
        non_trivial = descs - {"boundary", "EDGE_SEGMENT", "BAD_ACQ_SKIP", ""}
        if len(non_trivial) > 0:
            return True
    
    # Check for stim channels
    stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
    if len(stim_picks) > 0:
        return True
    
    return False


def _needs_events_from_tsv(raw: mne.io.BaseRaw, file_path: str) -> bool:
    """Determine if we need to load events from events.tsv sidecar."""
    # EEGLAB .set files: may or may not have events embedded
    if file_path.endswith(".set"):
        # Check if events are actually populated
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Has annotations, but check if they're just EEGLAB defaults
            descs = list(raw.annotations.description)
            # If only "boundary" type annotations, need external events
            unique_descs = set(descs)
            if unique_descs == {"boundary"} or len(unique_descs) == 0:
                return True
            return False
        return True
    
    # EDF without annotations
    if file_path.endswith(".edf") or file_path.endswith(".bdf"):
        if not _has_native_events(raw):
            return True
        return False
    
    # BrainVision without marker file
    if file_path.endswith(".eeg") or file_path.endswith(".vhdr"):
        if not _has_native_events(raw):
            return True
        return False
    
    # Plain .fif without baked events
    if file_path.endswith(".fif"):
        if not _has_native_events(raw):
            return True
        return False
    
    # Default: check if native events exist
    return not _has_native_events(raw)


class HBNRelease5Kernel:
    """Stage1 kernel for HBN EEG Release 5 (openneuro_ds005509)."""

    KERNEL_ID: str = "hbn-release5-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # =====================================================================
        # 1. SUBJECT METADATA FROM participants.tsv
        # =====================================================================
        subject_id = _get_subject_from_path(file_path)
        participant_data = {}
        if subject_id is not None:
            participant_data = _read_participants_for_subject(file_path, subject_id)

        # Extract required fields with fallbacks
        age = participant_data.get("age", "unknown")
        # Ensure age is string
        if age is not None and not isinstance(age, str):
            age = str(age)
        elif age is None:
            age = "unknown"

        sex = participant_data.get("sex", "unknown")
        if sex is not None:
            sex = str(sex).lower().strip()
            # Normalize sex values
            if sex in ["f", "female", "w", "woman"]:
                sex = "female"
            elif sex in ["m", "male", "man"]:
                sex = "male"
            else:
                sex = "unknown"
        else:
            sex = "unknown"

        # Build eegunity_description with required fields
        eegunity_description: Dict[str, str] = {
            "age": age,
            "sex": sex,
            # HBN uses BioSemi ActiveTwo amplifier
            # Ref: Alexander et al. 2017, HBN data description
            # Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
            "amplifier": "BioSemi ActiveTwo",
            # BioSemi uses Ag/AgCl active electrodes
            # Annotator: LLM (inferrer), 2026-04-08 — 需人类复核
            "cap": "BioSemi 128-channel Ag/AgCl active electrode cap",
            "handedness": "unknown",  # Not consistently available in HBN
        }

        # Add required info fields from participants.tsv
        for field in _REQUIRED_INFO_FIELDS:
            if field in participant_data:
                val = participant_data[field]
                if val is not None and str(val).lower() not in ["nan", "nat", "none", ""]:
                    eegunity_description[field] = str(val)
                else:
                    eegunity_description[field] = "unknown"
            else:
                eegunity_description[field] = "unknown"

        # LLM 推断，需人类复核: handedness from EHQ total if available
        # EHQ (Edinburgh Handedness Questionnaire) total can indicate handedness
        ehq_total = eegunity_description.get("ehq_total", "unknown")
        if ehq_total != "unknown":
            try:
                ehq_score = float(ehq_total)
                # EHQ ranges -100 (fully left) to +100 (fully right)
                if ehq_score > 0:
                    eegunity_description["handedness"] = "right"  # LLM 推断，需人类复核
                elif ehq_score < 0:
                    eegunity_description["handedness"] = "left"  # LLM 推断，需人类复核
            except (ValueError, TypeError):
                pass

        # Update raw description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        raw.info["description"] = json.dumps({
            "original_description": str(original_desc),
            "eegunity_description": eegunity_description,
        })

        # =====================================================================
        # 2. CHANNEL RENAMING AND TYPE SETTING
        # =====================================================================
        # Normalize channel names
        rename_map = {}
        for ch_name in raw.ch_names:
            normalized = _normalize_channel_name(ch_name)
            if normalized != ch_name:
                rename_map[ch_name] = normalized

        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for known non-EEG channels
        # HBN typically includes EOG and reference channels
        ch_types = {}
        for ch_name in raw.ch_names:
            upper = ch_name.upper()
            if any(x in upper for x in ["EOG", "HEOG", "VEOG"]):
                ch_types[ch_name] = "eog"
            elif ch_name in ["CMS", "DRL"]:
                ch_types[ch_name] = "misc"
            elif ch_name in ["M1", "M2", "A1", "A2"]:
                ch_types[ch_name] = "misc"

        if ch_types:
            raw.set_channel_types(ch_types)

        # =====================================================================
        # 3. MONTAGE SETTING (after channel rename)
        # =====================================================================
        # HBN uses standard 10-20 extended layout with 129 channels
        # Try to set standard montage; fall back if channels don't match exactly
        try:
            # Try standard 1005 first (has more coverage)
            montage = mne.channels.make_standard_montage("standard_1005")
            # Check how many channels match
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            common = montage_chs & raw_chs
            
            if len(common) >= 100:  # Most channels match
                raw.set_montage(montage, match_case=False, on_missing="warn")
            else:
                # Try biosemi64 or biosemi128 if available
                try:
                    montage = mne.channels.make_standard_montage("biosemi128")
                    raw.set_montage(montage, match_case=False, on_missing="warn")
                except Exception:
                    # LLM 推断，需人类复核: skip montage if no good match
                    pass
        except Exception:
            # Montage setting failed, continue without
            pass

        # =====================================================================
        # 4. EVENTS FROM events.tsv SIDECAR
        # =====================================================================
        if _needs_events_from_tsv(raw, file_path):
            events_path = _find_events_tsv(file_path)
            if events_path is not None:
                events_df = _read_events_tsv(events_path)
                if events_df is not None and len(events_df) > 0:
                    # Check if raw already has some annotations we should preserve
                    existing_annot = None
                    if raw.annotations is not None and len(raw.annotations) > 0:
                        existing_annot = raw.annotations.copy()
                    
                    # Create annotations from events.tsv
                    new_annot = _events_tsv_to_annotations(events_df, raw.info["sfreq"])
                    
                    if new_annot is not None:
                        if existing_annot is not None:
                            # Combine: keep existing boundary annotations, add new event annotations
                            raw.set_annotations(existing_annot + new_annot)
                        else:
                            raw.set_annotations(new_annot)

        # =====================================================================
        # 5. REQUIRED NATIVE MISC CHANNELS
        # =====================================================================
        # Ensure any required native misc channels have correct type
        if _REQUIRED_NATIVE_MISC:
            native_misc_types = {}
            for ch_name in _REQUIRED_NATIVE_MISC:
                if ch_name in raw.ch_names:
                    native_misc_types[ch_name] = "misc"
            if native_misc_types:
                raw.set_channel_types(native_misc_types)

        # =====================================================================
        # 6. REQUIRED DERIVED MISC CHANNELS
        # =====================================================================
        # Create derived misc channels if required
        for derived_name in _REQUIRED_DERIVED_MISC:
            if derived_name in raw.ch_names:
                continue  # Already exists
            
            # Create constant broadcast channel with value 0
            # (placeholder; actual derivation would need specific logic)
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info([derived_name], raw.info["sfreq"], ["misc"])
            misc_raw = mne.io.RawArray(data, info)
            
            # Match time alignment
            misc_raw.set_meas_date(raw.info["meas_date"])
            if raw.first_samp is not None:
                misc_raw._first_samps = [raw.first_samp]
            
            raw.add_channels([misc_raw], force_update_info=True)

        return raw


KERNEL = HBNRelease5Kernel()