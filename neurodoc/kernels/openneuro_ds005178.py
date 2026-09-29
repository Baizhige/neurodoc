"""Ear-EEG Sleep Monitoring 2023 (EESM23) stage1 kernel for EEGUnity.

Dataset: openneuro_ds005178
Source: https://openneuro.org/datasets/ds005178
DOI: 10.3389/fnins.2023.987578, 10.1038/s41597-025-04579-8

Ear-EEG sleep monitoring dataset with 5 in-ear EEG channels at 250 Hz.
Sleep stage annotations (W/N1/N2/N3/REM) are stored in BIDS events.tsv files.
The kernel reads scoring annotations from BIDS *_events.tsv sidecars and maps
them to canonical sleep stage event IDs for 30-second epoching.

Channel names are non-standard ear-EEG labels and are kept as-is since they
do not map to standard 10-20 positions. No montage is set.
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


# BIDS scoring index to canonical event ID mapping.
# Source: task-sleep_acq-scoring_events.json in dataset
# scoring_idx values: 1=Wake, 2=REM, 3=N1, 4=N2, 5=N3, 6=Artefact
# Annotator: human, 2026-05-02
_SCORING_MAP = {
    1: "Sleep stage W",
    2: "Sleep stage R",
    3: "Sleep stage N1",
    4: "Sleep stage N2",
    5: "Sleep stage N3",
    6: "Artefact",
}

# Manual scoring labels from task-sleep_acq-scoring_events.tsv.
# Annotator: human, 2026-05-02
_SCORING_LABEL_MAP = {
    "Wake": "Sleep stage W",
    "W": "Sleep stage W",
    "REM": "Sleep stage R",
    "R": "Sleep stage R",
    "N1": "Sleep stage N1",
    "N2": "Sleep stage N2",
    "N3": "Sleep stage N3",
    "Artefact": "Artefact",
    "Artifact": "Artefact",
}

# Event descriptions exposed for NeuroDoc/EEGUnity metadata consumers.
# Annotator: human, 2026-05-02
_RAW_META = {
    "Sleep stage W": "Wake stage scored from BIDS scoring sidecar",
    "Sleep stage R": "REM sleep scored from BIDS scoring sidecar",
    "Sleep stage N1": "NREM stage N1 scored from BIDS scoring sidecar",
    "Sleep stage N2": "NREM stage N2 scored from BIDS scoring sidecar",
    "Sleep stage N3": "NREM stage N3 scored from BIDS scoring sidecar",
    "Artefact": "Artefact epoch from manual scoring sidecar",
    "trigger": "Manual trigger marker from ear-EEG/PSG trigger sidecar",
    "error -10": "Buffer overflow error in ear-EEG ASICs",
    "error -100": "Hard reset or power-cycle error in ear-EEG ASICs",
    "oLED": "Connection loss to ASIC due to loose cable",
    "event": "Generic event marker from native EEGLAB data",
    "event_2": "Secondary generic event marker from native/source data",
}

# Super-meta labels for sleep-stage tasks.
# Annotator: human, 2026-05-02
_SUPER_META = {
    "Sleep stage W": "sleep_stage_W",
    "Sleep stage N1": "sleep_stage_N1",
    "Sleep stage N2": "sleep_stage_N2",
    "Sleep stage N3": "sleep_stage_N3",
    "Sleep stage R": "sleep_stage_REM",
}

# Required info fields from participants.tsv to include in eegunity_description
_REQUIRED_INFO_FIELDS: List[str] = []

# Required native misc channels (none for this dataset)
_REQUIRED_NATIVE_MISC: List[str] = []

# Derived misc channels (none for this dataset)
_DERIVED_MISC_CHANNELS: List[str] = []


def _detect_subject(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    match = re.search(r"sub-(\w+)", file_path)
    return match.group(1) if match else "unknown"


def _find_bids_root(file_path: str) -> str:
    """Find BIDS root directory from a file path."""
    parts = file_path.split(os.sep)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].startswith("sub-"):
            return os.sep.join(parts[:i])
    # Fallback: search upward for participants.tsv
    for i in range(len(parts) - 1, -1, -1):
        candidate = os.sep.join(parts[:i])
        if candidate and os.path.exists(os.path.join(candidate, "participants.tsv")):
            return candidate
    return os.path.dirname(file_path)


def _read_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    """Read participants.tsv from BIDS root directory."""
    participants_path = os.path.join(bids_root, "participants.tsv")
    if os.path.exists(participants_path):
        try:
            return pd.read_csv(participants_path, sep="\t")
        except Exception:
            pass
    return None


def _load_subject_info(bids_root: str, subject_id: str) -> Dict[str, str]:
    """Load subject metadata from BIDS participants.tsv."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    
    df = _read_participants_tsv(bids_root)
    if df is None:
        return info
    
    subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
    if subject_col not in df.columns:
        return info
    
    subject_row = df[df[subject_col] == f"sub-{subject_id}"]
    if subject_row.empty:
        # Try without sub- prefix
        subject_row = df[df[subject_col] == subject_id]
    
    if subject_row.empty:
        return info
    
    row = subject_row.iloc[0]
    
    # Age
    if "age" in row and pd.notna(row["age"]):
        info["age"] = str(int(float(row["age"]))) if str(row["age"]).replace('.', '').isdigit() else str(row["age"])
    
    # Sex
    if "sex" in row and pd.notna(row["sex"]):
        sex_val = str(row["sex"]).strip().lower()
        if sex_val in ("m", "male"):
            info["sex"] = "male"
        elif sex_val in ("f", "female"):
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    elif "gender" in row and pd.notna(row["gender"]):
        gender_val = str(row["gender"]).strip().lower()
        if gender_val in ("m", "male"):
            info["sex"] = "male"
        elif gender_val in ("f", "female"):
            info["sex"] = "female"
        else:
            info["sex"] = "unknown"
    
    # Handedness
    if "handedness" in row and pd.notna(row["handedness"]):
        hand_val = str(row["handedness"]).strip().lower()
        if hand_val in ("r", "right"):
            info["handedness"] = "right"
        elif hand_val in ("l", "left"):
            info["handedness"] = "left"
        else:
            info["handedness"] = "unknown"
    
    return info


def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given data file."""
    # BIDS naming: remove extension and add _events.tsv
    base = file_path
    # Handle common EEG extensions
    for ext in (".edf", ".bdf", ".set", ".eeg", ".vhdr", ".vmrk", ".fif", ".cnt", ".trc", ".mff"):
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    events_path = base + "_events.tsv"
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: some files have task-specific events
    # e.g., sub-001_ses-001_task-sleep_acq-PSGtrigger_eeg.edf
    # might have sub-001_ses-001_task-sleep_acq-scoring_events.tsv
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(base)
    
    # Look for any events.tsv in the same directory
    if os.path.isdir(dir_name):
        for f in os.listdir(dir_name):
            if f.endswith("_events.tsv"):
                candidate = os.path.join(dir_name, f)
                # Check if it's for the same subject/session
                if re.search(r"sub-(\w+)", file_name) and re.search(r"sub-(\w+)", f):
                    sub_file = re.search(r"sub-(\w+)", file_name).group(1)
                    sub_evt = re.search(r"sub-(\w+)", f).group(1)
                    if sub_file == sub_evt:
                        return candidate
    
    # Try scoring-specific events
    scoring_events = base.replace("_acq-PSGtrigger", "_acq-scoring") + "_events.tsv"
    if os.path.exists(scoring_events):
        return scoring_events
    
    # More general: try replacing acquisition label
    for acq in ["PSGtrigger", "PSG", "scoring", "earEEG"]:
        if f"_acq-{acq}" in base:
            for replacement in ["scoring", "PSGtrigger", "PSG", "earEEG"]:
                if replacement != acq:
                    candidate = base.replace(f"_acq-{acq}", f"_acq-{replacement}") + "_events.tsv"
                    if os.path.exists(candidate):
                        return candidate
    
    return None


def _find_scoring_events_tsv(file_path: str) -> Optional[str]:
    """Find the scoring events.tsv specifically."""
    base = file_path
    for ext in (".edf", ".bdf", ".set", ".eeg", ".vhdr", ".vmrk", ".fif", ".cnt", ".trc", ".mff"):
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Direct scoring replacement
    scoring_path = base.replace("_acq-PSGtrigger", "_acq-scoring") + "_events.tsv"
    if os.path.exists(scoring_path):
        return scoring_path
    
    # Try with task-sleep
    if "_task-sleep_" in base:
        scoring_path = re.sub(r"_acq-\w+", "_acq-scoring", base) + "_events.tsv"
        if os.path.exists(scoring_path):
            return scoring_path
    
    # Search in same directory
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(base)
    sub_match = re.search(r"sub-(\w+)", file_name)
    ses_match = re.search(r"ses-(\w+)", file_name)
    
    if os.path.isdir(dir_name):
        for f in os.listdir(dir_name):
            if "scoring" in f and f.endswith("_events.tsv"):
                # Match subject and session
                sub_evt = re.search(r"sub-(\w+)", f)
                ses_evt = re.search(r"ses-(\w+)", f)
                if sub_match and sub_evt and sub_match.group(1) == sub_evt.group(1):
                    if ses_match and ses_evt:
                        if ses_match.group(1) == ses_evt.group(1):
                            return os.path.join(dir_name, f)
                    else:
                        return os.path.join(dir_name, f)
    
    return None


def _read_events_tsv(events_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    if not events_path or not os.path.exists(events_path):
        return None
    try:
        return pd.read_csv(events_path, sep="\t")
    except Exception:
        return None


def _detect_acquisition(file_path: str) -> str:
    """Return the BIDS acquisition label from a file name, if present."""
    match = re.search(r"_acq-([^_]+)", os.path.basename(file_path))
    return match.group(1) if match else ""


def _sidecar_matches_recording(file_name: str, sidecar_name: str) -> bool:
    """Check subject/session identity between a recording and an events sidecar."""
    for key in ("sub", "ses"):
        rec_match = re.search(rf"{key}-(\w+)", file_name)
        sidecar_match = re.search(rf"{key}-(\w+)", sidecar_name)
        if rec_match and sidecar_match and rec_match.group(1) != sidecar_match.group(1):
            return False
    return True


def _find_sidecar_events_tsvs(file_path: str, token: str) -> List[str]:
    """Find same-subject/session events.tsv sidecars whose name contains token."""
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    if not os.path.isdir(dir_name):
        return []

    token_lower = token.lower()
    matches = []
    for sidecar_name in sorted(os.listdir(dir_name)):
        sidecar_lower = sidecar_name.lower()
        if not sidecar_lower.endswith("_events.tsv"):
            continue
        if token_lower not in sidecar_lower:
            continue
        if not _sidecar_matches_recording(file_name, sidecar_name):
            continue
        matches.append(os.path.join(dir_name, sidecar_name))
    return matches


def _find_trigger_events_tsvs(file_path: str) -> List[str]:
    """Find trigger sidecars relevant to the current acquisition."""
    candidates = _find_sidecar_events_tsvs(file_path, "trigger")
    if not candidates:
        return []

    acq = _detect_acquisition(file_path).lower()
    if acq == "eareeg":
        preferred = [p for p in candidates if "eareegtrigger" in os.path.basename(p).lower()]
        return preferred or candidates
    if acq == "psg":
        preferred = [
            p for p in candidates
            if "psgtrigger" in os.path.basename(p).lower()
            and "eareegtrigger" not in os.path.basename(p).lower()
        ]
        return preferred or candidates
    return candidates


def _find_recording_failure_events_tsv(file_path: str) -> Optional[str]:
    """Find the ear-EEG recording-failure sidecar for ear-EEG recordings."""
    if _detect_acquisition(file_path).lower() != "eareeg":
        return None
    candidates = _find_sidecar_events_tsvs(file_path, "recordingfailures")
    return candidates[0] if candidates else None


def _dedupe_annotations(annotations: mne.Annotations) -> mne.Annotations:
    """Remove exact duplicate annotations while preserving order."""
    seen = set()
    onsets = []
    durations = []
    descriptions = []
    for onset, duration, description in zip(
        annotations.onset,
        annotations.duration,
        annotations.description,
    ):
        key = (round(float(onset), 6), round(float(duration), 6), str(description))
        if key in seen:
            continue
        seen.add(key)
        onsets.append(float(onset))
        durations.append(float(duration))
        descriptions.append(str(description))

    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
        orig_time=annotations.orig_time,
    )


def _merge_annotations(raw: mne.io.BaseRaw, annotations: mne.Annotations) -> mne.io.BaseRaw:
    """Merge annotations into raw, avoiding exact duplicate sidecar/native events."""
    if annotations is None or len(annotations) == 0:
        return raw

    existing = raw.annotations
    if existing is None or len(existing) == 0:
        raw.set_annotations(_dedupe_annotations(annotations))
    else:
        raw.set_annotations(_dedupe_annotations(existing + annotations))
    return raw


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events dataframe to MNE Annotations."""
    if events_df is None or events_df.empty:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    # Required columns
    if "onset" not in events_df.columns:
        return mne.Annotations(onset=[], duration=[], description=[])
    
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float) if "duration" in events_df.columns else np.zeros(len(onsets))
    
    # Determine description column
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        # Map numeric values if possible
        values = events_df["value"].values
        descriptions = []
        for v in values:
            if pd.isna(v):
                descriptions.append("unknown")
            elif v in _SCORING_MAP:
                descriptions.append(_SCORING_MAP[v])
            else:
                descriptions.append(str(v))
        descriptions = np.array(descriptions)
    elif "stim_type" in events_df.columns:
        descriptions = events_df["stim_type"].astype(str).values
    elif "scoring" in events_df.columns:
        descriptions = np.array([
            _SCORING_LABEL_MAP.get(str(v).strip(), str(v).strip())
            for v in events_df["scoring"].values
        ])
    else:
        # Use any available column as description
        desc_cols = [c for c in events_df.columns if c not in ("onset", "duration", "sample", "channel")]
        if desc_cols:
            descriptions = events_df[desc_cols[0]].astype(str).values
        else:
            descriptions = np.array(["event"] * len(onsets))
    
    # Handle scoring_idx specifically for sleep staging
    if "scoring_idx" in events_df.columns and "trial_type" not in events_df.columns:
        scoring_values = events_df["scoring_idx"].values
        descriptions = []
        for v in scoring_values:
            if pd.isna(v):
                descriptions.append("unknown")
            elif int(v) in _SCORING_MAP:
                descriptions.append(_SCORING_MAP[int(v)])
            else:
                descriptions.append(str(int(v)))
        descriptions = np.array(descriptions)
    
    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


def _add_scoring_annotations(raw: mne.io.BaseRaw, scoring_events_path: str) -> mne.io.BaseRaw:
    """Add sleep stage scoring annotations from scoring events.tsv."""
    scoring_df = _read_events_tsv(scoring_events_path)
    if scoring_df is None or scoring_df.empty:
        return raw
    
    if "scoring_idx" in scoring_df.columns:
        onsets = scoring_df["onset"].values.astype(float)
        durations = scoring_df["duration"].values.astype(float) if "duration" in scoring_df.columns else np.zeros(len(onsets))
        
        descriptions = []
        for v in scoring_df["scoring_idx"].values:
            if pd.isna(v):
                descriptions.append("unknown")
            else:
                try:
                    int_v = int(float(v))
                    descriptions.append(_SCORING_MAP.get(int_v, str(int_v)))
                except (ValueError, TypeError):
                    descriptions.append(str(v))
        
        scoring_annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
        )
        
        return _merge_annotations(raw, scoring_annot)
    if "scoring" in scoring_df.columns:
        return _merge_annotations(raw, _events_to_annotations(scoring_df))
    
    return raw


def _add_trigger_annotations(raw: mne.io.BaseRaw, trigger_events_path: str) -> mne.io.BaseRaw:
    """Add trigger annotations from trigger events.tsv."""
    trigger_df = _read_events_tsv(trigger_events_path)
    if trigger_df is None or trigger_df.empty:
        return raw
    
    onsets = trigger_df["onset"].values.astype(float)
    durations = trigger_df["duration"].values.astype(float) if "duration" in trigger_df.columns else np.zeros(len(onsets))
    
    # Use trial_type or value as description
    if "trial_type" in trigger_df.columns:
        descriptions = trigger_df["trial_type"].astype(str).values
    elif "value" in trigger_df.columns:
        descriptions = trigger_df["value"].astype(str).values
    else:
        descriptions = np.array(["trigger"] * len(onsets))
    
    trigger_annot = mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )
    
    return _merge_annotations(raw, trigger_annot)


def _add_generic_events_annotations(raw: mne.io.BaseRaw, events_path: str) -> mne.io.BaseRaw:
    """Add annotations from a non-scoring/non-trigger BIDS events.tsv sidecar."""
    events_df = _read_events_tsv(events_path)
    if events_df is None or events_df.empty:
        return raw
    return _merge_annotations(raw, _events_to_annotations(events_df))


def _ensure_misc_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Ensure required native and derived misc channels exist."""
    # Handle native misc channels
    for ch_name in _REQUIRED_NATIVE_MISC:
        if ch_name in raw.ch_names:
            current_type = raw.get_channel_types(picks=[ch_name])[0]
            if current_type != "misc":
                raw.set_channel_types({ch_name: "misc"})
    
    # Handle derived misc channels
    for ch_name in _DERIVED_MISC_CHANNELS:
        if ch_name not in raw.ch_names:
            # Create derived misc channel with zeros
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info([ch_name], raw.info["sfreq"], ["misc"])
            misc_raw = mne.io.RawArray(data, info)
            raw.add_channels([misc_raw], force_update_info=True)
    
    return raw


@dataclass
class EESM23Kernel:
    """Stage1 kernel for the Ear-EEG Sleep Monitoring 2023 (EESM23) dataset."""

    KERNEL_ID: str = "eesm23-stage1"
    required_info_fields: List[str] = field(default_factory=lambda: list(_REQUIRED_INFO_FIELDS))
    raw_meta: Dict[str, str] = field(default_factory=lambda: dict(_RAW_META))
    super_meta: Dict[str, str] = field(default_factory=lambda: dict(_SUPER_META))

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # Extract subject ID and BIDS root
        subject_id = _detect_subject(file_path)
        bids_root = _find_bids_root(file_path)
        
        # Load subject info from participants.tsv
        subject_info = _load_subject_info(bids_root, subject_id)
        
        # Build eegunity_description
        eegunity_desc = {
            "age": subject_info["age"],
            "sex": subject_info["sex"],
            "amplifier": "unknown",  # inferred by LLM, needs human review: device info not in BIDS sidecars
            "cap": "unknown",  # inferred by LLM, needs human review: ear-EEG uses custom in-ear electrodes, not standard cap
            "handedness": subject_info["handedness"],
        }
        
        # Add required info fields from participants.tsv if any
        if _REQUIRED_INFO_FIELDS:
            df = _read_participants_tsv(bids_root)
            if df is not None:
                subject_col = "participant_id" if "participant_id" in df.columns else "subject_id"
                subject_row = df[df[subject_col] == f"sub-{subject_id}"]
                if subject_row.empty:
                    subject_row = df[df[subject_col] == subject_id]
                if not subject_row.empty:
                    row_data = subject_row.iloc[0]
                    for field in _REQUIRED_INFO_FIELDS:
                        if field in row_data and pd.notna(row_data[field]):
                            eegunity_desc[field] = str(row_data[field])
                        else:
                            eegunity_desc[field] = "unknown"
        
        # Set description
        original_desc = raw.info.get("description", "") or ""
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })
        
        # Channel handling: ear-EEG channels are non-standard, keep as-is
        # No renaming or montage for in-ear electrodes (not 10-20 compatible)
        # Source: 10.3389/fnins.2023.987578 — custom ear-EEG electrode placement
        # Annotator: LLM, 2026-04-08
        
        # Ensure misc channels
        raw = _ensure_misc_channels(raw)
        
        # Handle events from BIDS sidecars
        # The dataset has multiple event files:
        # - *_acq-PSGtrigger_events.tsv: trigger synchronization events
        # - *_acq-scoring_events.tsv: sleep stage scoring annotations
        
        loaded_sidecars = set()

        # Find and add scoring annotations (primary for sleep staging tasks)
        scoring_events_path = _find_scoring_events_tsv(file_path)
        if scoring_events_path:
            raw = _add_scoring_annotations(raw, scoring_events_path)
            loaded_sidecars.add(scoring_events_path)

        # Find and add trigger annotations. Trigger sidecars can coexist with
        # scoring and recording-failure sidecars for the same session.
        for trigger_events_path in _find_trigger_events_tsvs(file_path):
            if trigger_events_path not in loaded_sidecars:
                raw = _add_trigger_annotations(raw, trigger_events_path)
                loaded_sidecars.add(trigger_events_path)

        # Find and add ear-EEG recording-failure annotations.
        failure_events_path = _find_recording_failure_events_tsv(file_path)
        if failure_events_path and failure_events_path not in loaded_sidecars:
            raw = _add_generic_events_annotations(raw, failure_events_path)
            loaded_sidecars.add(failure_events_path)
        
        # If no annotations were loaded from sidecars, try to derive from any available events.tsv
        if raw.annotations is None or len(raw.annotations) == 0:
            # Try generic events.tsv finding
            generic_events = _find_events_tsv(file_path)
            if generic_events and generic_events not in loaded_sidecars:
                events_df = _read_events_tsv(generic_events)
                if events_df is not None and not events_df.empty:
                    annot = _events_to_annotations(events_df)
                    if len(annot) > 0:
                        raw = _merge_annotations(raw, annot)
        
        # Final check: ensure we have annotations if sidecars exist
        # For EDF files without embedded events, the sidecars are essential
        if (raw.annotations is None or len(raw.annotations) == 0) and file_path.lower().endswith(".edf"):
            # Last resort: search more broadly for any events file
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            sub_id = re.search(r"sub-(\w+)", base_name)
            if sub_id and os.path.isdir(dir_name):
                for f in os.listdir(dir_name):
                    if f.endswith("_events.tsv"):
                        full_path = os.path.join(dir_name, f)
                        events_df = _read_events_tsv(full_path)
                        if events_df is not None and not events_df.empty:
                            annot = _events_to_annotations(events_df)
                            if len(annot) > 0:
                                raw = _merge_annotations(raw, annot)
                                break
        
        return raw


KERNEL = EESM23Kernel()
