"""SEED (SJTU Emotion EEG Dataset) stage1 kernel for EEGUnity.

Dataset: SEED / other_seed
Source: https://bcmi.sjtu.edu.cn/home/seed/
Reference: Zheng & Lu, 2015. IEEE Transactions on Autonomous Mental Development

The SEED dataset contains EEG recordings from 15 subjects watching emotional
film clips across 3 sessions. EEG was recorded with 62 channels using an
ESI NeuroScan system at 1000 Hz.

File format: .cnt (NeuroScan continuous EEG)
- EEGUnity uses mne.io.read_raw_cnt to load these files
- Event markers are embedded in the .cnt files as KeyPad Response codes
- Emotion valence labels are stored in separate *_label.mat files (+1, 0, -1)

Kernel responsibilities:
1. Map 62-channel NeuroScan names to standard 10-20 names
2. Set montage (standard_1020 for 62-channel NeuroScan cap)
3. Extract embedded event markers as annotations
4. Create derived misc channels for emotion labels from *_label.mat files
5. Populate eegunity_description with available metadata

Channel naming:
- NeuroScan .cnt files use names like "FP1", "FPZ", "FP2", "AF3", etc.
- These need to be mapped to MNE-standard names: "Fp1", "Fpz", "Fp2", "AF3", etc.
- The 62-channel layout follows the extended 10-20 system used by NeuroScan

Note: Subject age/sex/handedness are not provided in the dataset; all marked unknown.
Amplifier and cap information from dataset documentation (Zheng & Lu, 2015).

Annotator: LLM, 2026-04-08
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import scipy.io as sio


# ---------------------------------------------------------------------------
# 62-channel NeuroScan to standard 10-20 rename map
# Source: NeuroScan 62-channel cap layout, standard extended 10-20 system
# Paper: Zheng & Lu, 2015. "Investigating Critical Frequency Bands and Channels 
#        for EEG-Based Emotion Recognition with Deep Neural Networks"
#        IEEE Transactions on Autonomous Mental Development
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
# ---------------------------------------------------------------------------
_NEUROSCAN_62_RENAME_MAP: Dict[str, str] = {
    # Frontal polar
    "FP1": "Fp1",
    "FPZ": "Fpz",
    "FP2": "Fp2",
    # Frontal
    "AF3": "AF3",
    "AF4": "AF4",
    "F7": "F7",
    "F5": "F5",
    "F3": "F3",
    "F1": "F1",
    "FZ": "Fz",
    "F2": "F2",
    "F4": "F4",
    "F6": "F6",
    "F8": "F8",
    # Frontal-temporal
    "FT7": "FT7",
    "FT8": "FT8",
    # Temporal
    "T7": "T7",
    "T8": "T8",
    # Central
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FCZ": "FCz",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "C5": "C5",
    "C3": "C3",
    "C1": "C1",
    "CZ": "Cz",
    "C2": "C2",
    "C4": "C4",
    "C6": "C6",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CPZ": "CPz",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    # Parietal
    "P7": "P7",
    "P5": "P5",
    "P3": "P3",
    "P1": "P1",
    "PZ": "Pz",
    "P2": "P2",
    "P4": "P4",
    "P6": "P6",
    "P8": "P8",
    # Parietal-occipital
    "PO7": "PO7",
    "PO5": "PO5",
    "PO3": "PO3",
    "POZ": "POz",
    "PO4": "PO4",
    "PO6": "PO6",
    "PO8": "PO8",
    # Occipital
    "CB1": "CB1",  # Non-standard, keep as-is or map to Iz alternative
    "O1": "O1",
    "OZ": "Oz",
    "O2": "O2",
    "CB2": "CB2",  # Non-standard, keep as-is
    # Mastoids / reference (often present in NeuroScan)
    "M1": "M1",
    "M2": "M2",
    # EOG channels (if present)
    "VEO": "VEOG",
    "HEO": "HEOG",
    # Sometimes alternative naming
    "FP1.": "Fp1",
    "FP2.": "Fp2",
    "FZ.": "Fz",
    "CZ.": "Cz",
    "PZ.": "Pz",
    "OZ.": "Oz",
}


# Event codes from NeuroScan .cnt files (KeyPad responses)
# Source: SEED dataset documentation and observed event structure
# These are raw marker codes embedded in the continuous EEG files
# Annotator: LLM, 2026-04-08 — 由 LLM 推断，需人类复核
_KEYPAD_EVENT_MAP: Dict[int, str] = {
    1: "KeyPad Response 1",
    4: "KeyPad Response 4",
    7: "KeyPad Response 7",
    13: "KeyPad Response 13",
    15: "KeyPad Response 15",
}


def _find_label_mat(file_path: str) -> Optional[str]:
    """Find the corresponding *_label.mat file for a given .cnt file.
    
    SEED naming convention:
    - EEG: sub_01_session_01.cnt, sub_01_session_02.cnt, etc.
    - Labels: sub_01_session_01_label.mat, sub_01_session_02_label.mat, etc.
    Or alternative: 1_1.mat, 1_2.mat for subject 1, sessions 1-3
    """
    base = os.path.splitext(file_path)[0]
    
    # Try direct suffix
    label_path = base + "_label.mat"
    if os.path.exists(label_path):
        return label_path
    
    # Try alternative: remove session number pattern and add label
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(base)
    
    # Pattern: sub_XX_session_YY -> sub_XX_session_YY_label.mat
    # Pattern: XX_YY (subject_session) -> XX_YY_label.mat or XX_YY.mat with label inside
    
    # Try various patterns
    for suffix in ["_label.mat", "label.mat"]:
        alt_path = base + suffix
        if os.path.exists(alt_path):
            return alt_path
    
    # Search in same directory for matching label files
    if os.path.exists(dir_name):
        for f in os.listdir(dir_name):
            if "label" in f.lower() and f.endswith(".mat"):
                # Check if subject/session matches
                f_base = os.path.splitext(f)[0].replace("_label", "").replace("label", "")
                if f_base in file_name or file_name in f_base:
                    return os.path.join(dir_name, f)
    
    return None


def _parse_subject_session(file_path: str) -> Tuple[str, str]:
    """Extract subject ID and session ID from file path.
    
    Returns (subject_id, session_id) strings.
    """
    file_name = os.path.basename(file_path)
    base = os.path.splitext(file_name)[0]
    
    # Pattern: sub_01_session_01 or sub1_session1 or 1_1 etc.
    # Try to extract numbers
    patterns = [
        r"sub[_-]?(\d+)[_-]?session[_-]?(\d+)",
        r"(\d+)[_-](\d+)$",  # ending with X_Y
        r"subject[_-]?(\d+)[_-]?session[_-]?(\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, base, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2)
    
    # Fallback: extract all numbers
    numbers = re.findall(r'\d+', base)
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    elif len(numbers) == 1:
        return numbers[0], "1"
    
    return "unknown", "unknown"


def _load_valence_labels(label_path: str) -> Optional[np.ndarray]:
    """Load valence labels from *_label.mat file.
    
    SEED label files contain a vector with values +1 (positive), 0 (neutral), -1 (negative)
    representing the valence of each film clip shown in the session.
    
    Returns array of shape (n_trials,) or None if loading fails.
    """
    try:
        mat = sio.loadmat(label_path, simplify_cells=True)
        
        # Try common variable names
        for key in ["label", "labels", "valence", "y", "Y"]:
            if key in mat:
                labels = mat[key]
                if isinstance(labels, np.ndarray):
                    return np.asarray(labels).flatten()
        
        # If no known key, try the first non-meta key
        for key in mat.keys():
            if not key.startswith("__"):
                val = mat[key]
                if isinstance(val, np.ndarray) and val.size > 0:
                    # Check if it looks like labels (1D, small integer values)
                    flat = np.asarray(val).flatten()
                    if len(flat) <= 20:  # SEED has ~15 trials per session
                        return flat
        
        return None
    except Exception:
        return None


def _create_label_misc_channel(
    raw: mne.io.BaseRaw,
    labels: np.ndarray,
    channel_name: str,
    value_map: Optional[Dict[Any, Any]] = None,
    filter_values: Optional[List[Any]] = None,
) -> mne.io.BaseRaw:
    """Create a derived MISC channel from trial labels.
    
    For SEED, we need to broadcast per-trial labels to the continuous EEG.
    Since .cnt files have embedded event markers for trial onsets, we use
    those to segment the data and assign labels.
    
    If no event markers found, we divide the recording into equal segments
    (assuming fixed trial durations ~4 minutes each with some rest).
    
    Parameters
    ----------
    raw : mne.io.BaseRaw
        The raw EEG data
    labels : np.ndarray
        Array of label values, one per trial
    channel_name : str
        Name for the derived misc channel
    value_map : dict, optional
        Mapping from original label values to output values
    filter_values : list, optional
        If provided, only include trials with these values (set others to 0/NaN)
    
    Returns
    -------
    raw : mne.io.BaseRaw
        Raw with added misc channel
    """
    sfreq = raw.info["sfreq"]
    n_samples = raw.n_times
    
    # Initialize channel data with zeros
    misc_data = np.zeros((1, n_samples))
    
    # Get event onsets from annotations
    events, event_id = mne.events_from_annotations(raw, verbose=False)
    
    # Filter to keypad response events (trial onsets)
    trial_onset_samples = []
    if len(events) > 0:
        for event_code in sorted(event_id.values()):
            desc = [k for k, v in event_id.items() if v == event_code][0]
            if "KeyPad" in desc or "Response" in desc:
                mask = events[:, 2] == event_code
                trial_onset_samples.extend(sorted(events[mask, 0].tolist()))
    
    trial_onset_samples = sorted(trial_onset_samples)
    
    # If no keypad events found, try to use any annotations
    if len(trial_onset_samples) == 0 and len(events) > 0:
        trial_onset_samples = sorted(events[:, 0].tolist())
    
    # If still no events, estimate trial boundaries from data length
    # SEED: ~15 trials per session, each ~4 minutes (240s) of film + rest
    if len(trial_onset_samples) == 0:
        n_trials = len(labels)
        # Estimate: divide recording into n_trials equal parts
        # Use middle portion of each segment to avoid transitions
        segment_length = n_samples // n_trials
        trial_onset_samples = [int(i * segment_length) for i in range(n_trials)]
    
    # Match labels to trials
    n_labels = len(labels)
    n_trials_found = len(trial_onset_samples)
    
    # Use minimum of available labels and detected trials
    n_use = min(n_labels, n_trials_found)
    
    for i in range(n_use):
        onset = trial_onset_samples[i]
        # Determine trial end (next onset or end of recording)
        if i + 1 < n_trials_found:
            offset = trial_onset_samples[i + 1]
        else:
            offset = n_samples
        
        label_val = labels[i]
        
        # Apply filter if specified
        if filter_values is not None and label_val not in filter_values:
            continue  # Leave as 0
        
        # Apply value mapping if specified
        if value_map is not None:
            mapped_val = value_map.get(label_val, 0)
        else:
            mapped_val = float(label_val)
        
        # Fill the segment
        misc_data[0, onset:offset] = mapped_val
    
    # Create RawArray for the misc channel
    info_misc = mne.create_info(
        ch_names=[channel_name],
        sfreq=sfreq,
        ch_types=["misc"]
    )
    raw_misc = mne.io.RawArray(misc_data, info_misc, verbose=False)
    
    # Add to original raw
    raw.add_channels([raw_misc], force_update_info=True)
    
    return raw


def _extract_cnt_events_to_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Extract embedded event markers from NeuroScan .cnt file and convert to annotations.
    
    NeuroScan .cnt files store events as triggers in an internal event table.
    MNE's read_raw_cnt should already extract these, but we ensure they're
    properly exposed as annotations for downstream processing.
    """
    # Check if annotations already exist
    if raw.annotations is not None and len(raw.annotations) > 0:
        # Already has annotations, verify they're readable
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            if len(events) > 0:
                return raw
        except Exception:
            pass
    
    # Try to extract from STIM channel if present
    stim_picks = mne.pick_types(raw.info, stim=True, exclude=[])
    if len(stim_picks) > 0:
        try:
            events = mne.find_events(raw, stim_channel=raw.ch_names[stim_picks[0]], 
                                    shortest_event=1, verbose=False)
            if len(events) > 0:
                # Convert to annotations
                onsets = events[:, 0] / raw.info["sfreq"]
                durations = np.zeros(len(events))
                # Map event codes to descriptions
                descriptions = []
                for code in events[:, 2]:
                    desc = _KEYPAD_EVENT_MAP.get(code, f"event-{code}")
                    descriptions.append(desc)
                
                annot = mne.Annotations(onset=onsets, duration=durations,
                                       description=descriptions)
                raw.set_annotations(annot)
                return raw
        except Exception:
            pass
    
    return raw


@dataclass
class SEEDKernel:
    """Stage1 kernel for the SEED (SJTU Emotion EEG) dataset."""

    KERNEL_ID: str = "other_seed-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        
        # ------------------------------------------------------------------
        # 1. Channel renaming to standard 10-20
        # ------------------------------------------------------------------
        rename_map = {}
        for old_name in raw.ch_names:
            # Try exact match first
            if old_name in _NEUROSCAN_62_RENAME_MAP:
                rename_map[old_name] = _NEUROSCAN_62_RENAME_MAP[old_name]
            else:
                # Try case-insensitive match
                old_upper = old_name.upper()
                for key, val in _NEUROSCAN_62_RENAME_MAP.items():
                    if key.upper() == old_upper:
                        rename_map[old_name] = val
                        break
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # ------------------------------------------------------------------
        # 2. Set channel types and montage
        # ------------------------------------------------------------------
        # Set EOG channels if present
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in ["VEOG", "HEOG", "VEO", "HEO", "EOG"]:
                ch_types[ch_name] = "eog"
            elif ch_name in ["M1", "M2", "A1", "A2", "TP9", "TP10"]:
                ch_types[ch_name] = "misc"  # Mastoid/reference channels
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Set montage for standard 10-20
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="ignore")
        except Exception:
            pass  # Montage setting failed, continue without
        
        # ------------------------------------------------------------------
        # 3. Extract/ensure events are available as annotations
        # ------------------------------------------------------------------
        raw = _extract_cnt_events_to_annotations(raw)
        
        # Ensure KeyPad events are properly exposed
        # If raw still has no annotations, create from any available event info
        if raw.annotations is None or len(raw.annotations) == 0:
            # Last resort: check if there's an events.tsv sidecar
            events_tsv_path = os.path.splitext(file_path)[0] + "_events.tsv"
            if not os.path.exists(events_tsv_path):
                # Try BIDS-style events file
                dir_name = os.path.dirname(file_path)
                base_name = os.path.basename(os.path.splitext(file_path)[0])
                events_tsv_path = os.path.join(dir_name, base_name + "_events.tsv")
            
            if os.path.exists(events_tsv_path):
                try:
                    import pandas as pd
                    events_df = pd.read_csv(events_tsv_path, sep="\t")
                    if "onset" in events_df.columns and "trial_type" in events_df.columns:
                        onsets = events_df["onset"].values
                        durations = events_df.get("duration", np.zeros(len(events_df))).values
                        descriptions = events_df["trial_type"].astype(str).values
                        annot = mne.Annotations(onset=onsets, duration=durations,
                                               description=descriptions)
                        raw.set_annotations(annot)
                except Exception:
                    pass
        
        # ------------------------------------------------------------------
        # 4. Load valence labels and create derived misc channels
        # ------------------------------------------------------------------
        label_path = _find_label_mat(file_path)
        labels = None
        
        if label_path is not None:
            labels = _load_valence_labels(label_path)
        
        if labels is not None and len(labels) > 0:
            # emotion_valence_binary: +1→0 (positive), -1→1 (negative), exclude 0
            raw = _create_label_misc_channel(
                raw, labels, "emotion_valence_binary",
                value_map={1: 0, -1: 1},
                filter_values=[1, -1]
            )
            
            # emotion_arousal_binary: +1/-1→1 (high), 0→0 (low)
            raw = _create_label_misc_channel(
                raw, labels, "emotion_arousal_binary",
                value_map={1: 1, 0: 0, -1: 1}
            )
            
            # valence_continuous: raw values -1, 0, +1
            raw = _create_label_misc_channel(
                raw, labels, "valence_continuous",
                value_map=None  # Use raw values
            )
        else:
            # Create empty misc channels as placeholders if labels not found
            # This ensures channel names exist for downstream compatibility
            sfreq = raw.info["sfreq"]
            n_samples = raw.n_times
            empty_data = np.zeros((1, n_samples))
            
            for ch_name in ["emotion_valence_binary", "emotion_arousal_binary", "valence_continuous"]:
                info_misc = mne.create_info(ch_names=[ch_name], sfreq=sfreq, ch_types=["misc"])
                raw_misc = mne.io.RawArray(empty_data, info_misc, verbose=False)
                raw.add_channels([raw_misc], force_update_info=True)
        
        # ------------------------------------------------------------------
        # 5. Ensure required native/derived misc channels exist
        # ------------------------------------------------------------------
        # Verify all derived misc channels have correct type
        final_ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name in ["emotion_valence_binary", "emotion_arousal_binary", 
                          "valence_continuous"]:
                final_ch_types[ch_name] = "misc"
        
        if final_ch_types:
            raw.set_channel_types(final_ch_types)
        
        # ------------------------------------------------------------------
        # 6. Populate eegunity_description
        # ------------------------------------------------------------------
        # Extract subject info if available
        subject_id, session_id = _parse_subject_session(file_path)
        
        # SEED dataset: 15 subjects, age/sex not publicly disclosed
        # Device: ESI NeuroScan system with Neuroscan cap
        # Source: Zheng & Lu, 2015 paper and dataset website
        # LLM 推断，需人类复核
        description_dict = {
            "original_description": raw.info.get("description", "") or "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "ESI NeuroScan",  # LLM 推断，需人类复核
                "cap": "Neuroscan 62-channel",  # LLM 推断，需人类复核
                "handedness": "unknown",
            }
        }
        
        raw.info["description"] = json.dumps(description_dict)
        
        return raw


KERNEL = SEEDKernel()