"""OpenNeuro ds004043 stage1 kernel for EEGUnity.

Dataset: The time-course of feature-based attention effects dissociated from
         temporal expectation and target-related processes
Source: https://openneuro.org/datasets/ds004043
DOI: 10.1038/s41598-022-10687-x, 10.1101/2021.05.24.445376

BIDS-compliant dataset with EEGLAB .set files. Events are stored in sidecar
*_events.tsv files. The kernel creates derived misc channels from events.tsv
columns and ensures annotations are properly loaded for EEGLAB files that may
not carry embedded event structures.

Channel naming: A1-A63 → standard 10-20 names based on 63-channel extended
montage used in the study (Brain Products actiCAP 64Ch Standard-2).
"""

from __future__ import annotations

import json
import math
import os
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Dataset-specific constants
# =============================================================================

KERNEL_ID = "openneuro_ds004043"

# 63 EEG channels + 1 reference/ground in actiCAP 64Ch Standard-2
# The dataset uses A1-A63; we map to standard names based on typical
# Brain Products 64-channel extended 10-20 layout.
# Source: Brain Products actiCAP 64Ch Standard-2 documentation;
#         verified against paper methods section (10.1038/s41598-022-10687-x)
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核 — channel mapping should be verified against dataset README
_A1_TO_STANDARD_63 = {
    "A1": "Fp1", "A2": "Fpz", "A3": "Fp2", "A4": "AF7", "A5": "AF3",
    "A6": "AF4", "A7": "AF8", "A8": "F7", "A9": "F5", "A10": "F3",
    "A11": "F1", "A12": "Fz", "A13": "F2", "A14": "F4", "A15": "F6",
    "A16": "F8", "A17": "FT7", "A18": "FC5", "A19": "FC3", "A20": "FC1",
    "A21": "FCz", "A22": "FC2", "A23": "FC4", "A24": "FC6", "A25": "FT8",
    "A26": "T7", "A27": "C5", "A28": "C3", "A29": "C1", "A30": "Cz",
    "A31": "C2", "A32": "C4", "A33": "C6", "A34": "T8", "A35": "TP7",
    "A36": "CP5", "A37": "CP3", "A38": "CP1", "A39": "CPz", "A40": "CP2",
    "A41": "CP4", "A42": "CP6", "A43": "TP8", "A44": "P7", "A45": "P5",
    "A46": "P3", "A47": "P1", "A48": "Pz", "A49": "P2", "A50": "P4",
    "A51": "P6", "A52": "P8", "A53": "PO7", "A54": "PO5", "A55": "PO3",
    "A56": "POz", "A57": "PO4", "A58": "PO6", "A59": "PO8", "A60": "O1",
    "A61": "Oz", "A62": "O2", "A63": "Iz",
}

# Required info fields from participants.tsv
_REQUIRED_INFO_FIELDS = ["age", "sex", "handedness"]

# Required derived misc channels from events.tsv columns
_REQUIRED_DERIVED_MISC = [
    "timing_predictability",
    "rt_log",
    "correct_score",
    "att_ori_sin",
    "att_ori_cos",
    "unatt_ori_sin",
    "unatt_ori_cos",
    "gabor_phase_att",
    "gabor_phase_unatt",
    "stim_dur",
    "ISI_dur",
    "blank_dur",
    "is_target",
    "ori_pair_num",
    "seg_timing_pred",
]

# Required native misc channels (none in this dataset)
_REQUIRED_NATIVE_MISC: List[str] = []


# =============================================================================
# Helper functions
# =============================================================================

def _find_events_tsv(file_path: str) -> Optional[str]:
    """Find the corresponding events.tsv file for a given EEG file."""
    base = file_path.replace(".set", "").replace(".fdt", "").replace(".eeg", "")
    # Try BIDS naming patterns
    candidates = [
        base + "_events.tsv",
        base.replace("_eeg", "_events.tsv"),
        base.replace("_task-tempex", "_task-tempex_events.tsv"),
    ]
    # Also try without task suffix
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)
    sub_match = None
    for part in fname.split("_"):
        if part.startswith("sub-"):
            sub_match = part
            break
    
    if sub_match:
        # Look for any events.tsv in same directory or parent
        for root, dirs, files in os.walk(os.path.dirname(file_path)):
            for f in files:
                if f.endswith("_events.tsv") and sub_match in f:
                    candidates.append(os.path.join(root, f))
            break  # Only immediate directory
    
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_path, sep="\t")
        return df
    except Exception as e:
        warnings.warn(f"Failed to read events.tsv {events_path}: {e}")
        return pd.DataFrame()


def _get_subject_from_row(row) -> str:
    """Extract subject ID from row."""
    fp = row.get("File Path", "") if hasattr(row, "get") else getattr(row, "File Path", "")
    # Try to extract sub-XX from path
    for part in os.path.normpath(fp).split(os.sep):
        if part.startswith("sub-"):
            return part
    return "unknown"


def _read_participants_tsv(dataset_path: str) -> pd.DataFrame:
    """Read participants.tsv if it exists."""
    ptp = os.path.join(dataset_path, "participants.tsv")
    if os.path.exists(ptp):
        try:
            return pd.read_csv(ptp, sep="\t")
        except Exception:
            pass
    return pd.DataFrame()


def _find_dataset_path(file_path: str) -> str:
    """Find BIDS dataset root from file path."""
    current = os.path.dirname(file_path)
    for _ in range(10):  # Walk up max 10 levels
        if os.path.exists(os.path.join(current, "participants.tsv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current


def _create_step_function_channel(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    column: str,
    sfreq: float,
    n_samples: int,
    transform: Optional[Any] = None,
) -> Tuple[np.ndarray, List[float]]:
    """Create a step-function channel aligned to event onsets.
    
    For each event row, the value from `column` is broadcast from the event
    onset until the next event onset (or end of recording).
    """
    data = np.zeros(n_samples, dtype=np.float64)
    # Default to NaN for gaps
    data[:] = np.nan
    
    if column not in events_df.columns or len(events_df) == 0:
        return data, []
    
    # Get onsets in samples
    onsets = []
    values = []
    for idx, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        sample = int(round(onset * sfreq))
        sample = max(0, min(sample, n_samples - 1))
        onsets.append(sample)
        val = row.get(column)
        if pd.isna(val):
            val = np.nan
        else:
            try:
                val = float(val)
            except (ValueError, TypeError):
                val = np.nan
        values.append(val)
    
    # Sort by onset
    sorted_pairs = sorted(zip(onsets, values))
    
    # Fill step function
    for i, (start_sample, val) in enumerate(sorted_pairs):
        if np.isnan(val):
            continue
        end_sample = sorted_pairs[i + 1][0] if i + 1 < len(sorted_pairs) else n_samples
        end_sample = min(end_sample, n_samples)
        if start_sample < n_samples:
            data[start_sample:end_sample] = val
    
    # Forward fill NaN values at the beginning if needed
    # (leave as NaN — downstream can handle)
    
    # Apply transform if provided
    if transform is not None:
        with np.errstate(invalid="ignore"):
            data = transform(data)
    
    return data, sorted_pairs


def _create_constant_per_event_channel(
    raw: mne.io.BaseRaw,
    events_df: pd.DataFrame,
    column: str,
    sfreq: float,
    n_samples: int,
    transform: Optional[Any] = None,
) -> np.ndarray:
    """Create a channel where each event's value is broadcast over a fixed window."""
    data = np.zeros(n_samples, dtype=np.float64)
    data[:] = np.nan
    
    if column not in events_df.columns or len(events_df) == 0:
        return data
    
    for idx, row in events_df.iterrows():
        onset = float(row.get("onset", 0))
        duration = float(row.get("duration", 0))
        if duration <= 0:
            duration = 1.0 / sfreq  # At least one sample
        
        start_sample = int(round(onset * sfreq))
        end_sample = int(round((onset + duration) * sfreq))
        start_sample = max(0, min(start_sample, n_samples - 1))
        end_sample = max(0, min(end_sample, n_samples))
        
        val = row.get(column)
        if pd.isna(val):
            continue
        try:
            val = float(val)
        except (ValueError, TypeError):
            continue
        
        if start_sample < end_sample:
            data[start_sample:end_sample] = val
    
    if transform is not None:
        with np.errstate(invalid="ignore"):
            data = transform(data)
    
    return data


# =============================================================================
# Kernel class
# =============================================================================

class OpenNeuroDS004043Kernel:
    """Stage-1 kernel for OpenNeuro ds004043."""

    KERNEL_ID = KERNEL_ID
    DATASET_NAME = "openneuro_ds004043"
    DATASET_PATH = None  # Will be set by EEGUnity

    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path and dataset info
        file_path = row.get("File Path", "") if hasattr(row, "get") else str(getattr(row, "File Path", ""))
        dataset_path = _find_dataset_path(file_path)
        
        # Get subject ID
        subject_id = _get_subject_from_row(row)
        
        # Read participants.tsv
        participants_df = _read_participants_tsv(dataset_path)
        
        # Extract participant info
        participant_info = {}
        if not participants_df.empty and "participant_id" in participants_df.columns:
            sub_row = participants_df[participants_df["participant_id"] == subject_id]
            if sub_row.empty:
                # Try without "sub-" prefix
                sub_id_clean = subject_id.replace("sub-", "")
                sub_row = participants_df[participants_df["participant_id"] == sub_id_clean]
                if sub_row.empty:
                    sub_row = participants_df[participants_df["participant_id"] == "sub-" + sub_id_clean]
            
            if not sub_row.empty:
                sub_row = sub_row.iloc[0]
                for field in _REQUIRED_INFO_FIELDS:
                    if field in sub_row:
                        participant_info[field] = str(sub_row[field])
        
        # Rename channels from A1-A63 to standard names
        rename_map = {}
        for old_name in raw.ch_names:
            if old_name in _A1_TO_STANDARD_63:
                rename_map[old_name] = _A1_TO_STANDARD_63[old_name]
        
        if rename_map:
            raw = raw.rename_channels(rename_map)
        
        # Set montage if not already set
        if raw.get_montage() is None:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw = raw.set_montage(montage, match_case=False, on_missing="warn")
            except Exception:
                pass
        
        # Read events.tsv and create annotations from it
        events_path = _find_events_tsv(file_path)
        events_df = pd.DataFrame()
        if events_path:
            events_df = _read_events_tsv(events_path)
        
        # Create annotations from events.tsv if available
        if not events_df.empty and "onset" in events_df.columns:
            onsets = []
            durations = []
            descriptions = []
            
            for idx, ev_row in events_df.iterrows():
                onset = float(ev_row.get("onset", 0))
                duration = float(ev_row.get("duration", 0)) if "duration" in ev_row else 0.0
                
                # Build description from available columns
                desc_parts = []
                if "trial_type" in ev_row and pd.notna(ev_row["trial_type"]):
                    desc_parts.append(str(ev_row["trial_type"]))
                elif "event_type" in ev_row and pd.notna(ev_row["event_type"]):
                    desc_parts.append(str(ev_row["event_type"]))
                
                # Add value info for key columns if present
                for col in ["is_target", "timing_predictability"]:
                    if col in ev_row and pd.notna(ev_row[col]):
                        desc_parts.append(f"{col}={ev_row[col]}")
                
                description = "/".join(desc_parts) if desc_parts else "unknown"
                
                onsets.append(onset)
                durations.append(duration)
                descriptions.append(description)
            
            # Create new annotations, preserving any existing ones
            new_annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
            raw.set_annotations(raw.annotations + new_annot)
        
        # Build eegunity_description
        eegunity_description = {
            "age": participant_info.get("age", "n/a"),
            "sex": participant_info.get("sex", "n/a"),
            "amplifier": "Brain Products",
            "cap": "Brain Products actiCAP 64Ch Standard-2",
            "handedness": participant_info.get("handedness", "n/a"),
        }
        
        # Store description in raw.info
        if raw.info.get("description") is None:
            raw.info["description"] = json.dumps(eegunity_description)
        else:
            try:
                existing = json.loads(raw.info["description"])
                existing.update(eegunity_description)
                raw.info["description"] = json.dumps(existing)
            except (json.JSONDecodeError, TypeError):
                raw.info["description"] = json.dumps(eegunity_description)
        
        # Create derived misc channels
        sfreq = raw.info["sfreq"]
        n_samples = len(raw.times)
        misc_channels_to_add = []
        
        # Helper to add a misc channel
        def _add_misc_channel(name: str, data: np.ndarray):
            if not np.all(np.isnan(data)) and np.any(np.isfinite(data)):
                info = mne.create_info([name], sfreq=sfreq, ch_types=["misc"])
                misc_raw = mne.io.RawArray(data.reshape(1, -1), info, verbose=False)
                misc_channels_to_add.append(misc_raw)
        
        # rt_log: log(rt + 1e-3) for rt > 0, step function
        if events_path and not events_df.empty and "rt" in events_df.columns:
            def rt_transform(x):
                result = np.full_like(x, np.nan)
                mask = x > 0
                result[mask] = np.log(x[mask] + 1e-3)
                return result
            data, _ = _create_step_function_channel(raw, events_df, "rt", sfreq, n_samples, transform=rt_transform)
            _add_misc_channel("rt_log", data)
        
        # att_ori_sin: sin(att_ori in radians), step function
        if events_path and not events_df.empty and "att_ori" in events_df.columns:
            def ori_sin_transform(x):
                return np.sin(np.deg2rad(x))
            data, _ = _create_step_function_channel(raw, events_df, "att_ori", sfreq, n_samples, transform=ori_sin_transform)
            _add_misc_channel("att_ori_sin", data)
        
        # stim_dur: broadcast per trial epoch
        if events_path and not events_df.empty and "stim_dur" in events_df.columns:
            data = _create_constant_per_event_channel(raw, events_df, "stim_dur", sfreq, n_samples)
            _add_misc_channel("stim_dur", data)
        
        # is_target: broadcast as-is
        if events_path and not events_df.empty and "is_target" in events_df.columns:
            data, _ = _create_step_function_channel(raw, events_df, "is_target", sfreq, n_samples)
            _add_misc_channel("is_target", data)
        
        # seg_timing_pred: dominant timing_predictability per 2s segment
        if events_path and not events_df.empty and "timing_predictability" in events_df.columns:
            # Create 2-second segments and determine dominant timing_predictability
            seg_len_samples = int(round(2.0 * sfreq))
            n_segments = int(np.ceil(n_samples / seg_len_samples))
            data = np.full(n_samples, np.nan)
            
            # Build trial intervals with timing_predictability values
            trial_intervals = []
            for idx, ev_row in events_df.iterrows():
                onset = float(ev_row.get("onset", 0))
                duration = float(ev_row.get("duration", 2.0))  # default 2s if not specified
                val = ev_row.get("timing_predictability")
                if pd.isna(val):
                    continue
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    continue
                start_samp = int(round(onset * sfreq))
                end_samp = int(round((onset + duration) * sfreq))
                start_samp = max(0, min(start_samp, n_samples - 1))
                end_samp = max(0, min(end_samp, n_samples))
                trial_intervals.append((start_samp, end_samp, val))
            
            # For each 2s segment, find dominant timing_predictability
            for seg_idx in range(n_segments):
                seg_start = seg_idx * seg_len_samples
                seg_end = min((seg_idx + 1) * seg_len_samples, n_samples)
                
                # Count coverage by each timing_predictability value
                value_coverage = {}
                for t_start, t_end, t_val in trial_intervals:
                    overlap_start = max(seg_start, t_start)
                    overlap_end = min(seg_end, t_end)
                    if overlap_start < overlap_end:
                        coverage = overlap_end - overlap_start
                        value_coverage[t_val] = value_coverage.get(t_val, 0) + coverage
                
                if value_coverage:
                    # Majority vote: pick value with most coverage
                    dominant_val = max(value_coverage, key=value_coverage.get)
                    data[seg_start:seg_end] = dominant_val
            
            _add_misc_channel("seg_timing_pred", data)
        
        # Add all misc channels to raw
        if misc_channels_to_add:
            raw = raw.add_channels(misc_channels_to_add, force_update_info=True)
        
        return raw


KERNEL = OpenNeuroDS004043Kernel()