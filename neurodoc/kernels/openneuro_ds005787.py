"""openneuro_ds005787 (NOD-EEG) stage1 kernel for EEGUnity.

Dataset: NOD-EEG — 64-channel EEG during ImageNet visual object recognition
Format: BIDS-compliant EDF (.edf) with events.tsv sidecars
Channels: 64
Sampling Rate: 250 Hz
Source: https://openneuro.org/datasets/ds005787

Notes:
- BIDS dataset with participants.tsv, events.tsv sidecars, and EDF recordings.
- Events: stim_on (value=4), resp (value=5), begin (value=1), end (value=2).
- events.tsv contains per-trial metadata: stim_is_animate, RT, image_id, class_id, etc.
- Kernel must expose raw meta annotations and derived misc channels for RT.
- Device info inferred from BIDS metadata / README; needs human verification.
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Dataset-specific constants
# ---------------------------------------------------------------------------

# Standard 64-channel extended 10-20 layout used by this dataset
# Source: BIDS channels.tsv + standard 10-20 system for 64 channels
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_NOD_EEG_CHANNEL_NAMES = [
    "Fp1", "AF7", "AF3", "F1", "F3", "F5", "F7", "FT7",
    "FC5", "FC3", "FC1", "C1", "C3", "C5", "T7", "TP7",
    "CP5", "CP3", "CP1", "P1", "P3", "P5", "P7", "P9",
    "PO7", "PO3", "O1", "Iz", "Oz", "POz", "Pz", "CPz",
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz", "F2", "F4",
    "F6", "F8", "FT8", "FC6", "FC4", "FC2", "FCz", "Cz",
    "C2", "C4", "C6", "T8", "TP8", "CP6", "CP4", "CP2",
    "P2", "P4", "P6", "P8", "P10", "PO8", "PO4", "O2"
]

# Expected channel names from BIDS channels.tsv for this dataset
# The EDF files may have channels named with "EEG " prefix or similar
# Source: BIDS channels.tsv sidecar pattern for this dataset
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核
_BIDS_CHANNEL_PATTERNS = [
    "EEG Fp1", "EEG AF7", "EEG AF3", "EEG F1", "EEG F3", "EEG F5", "EEG F7", "EEG FT7",
    "EEG FC5", "EEG FC3", "EEG FC1", "EEG C1", "EEG C3", "EEG C5", "EEG T7", "EEG TP7",
    "EEG CP5", "EEG CP3", "EEG CP1", "EEG P1", "EEG P3", "EEG P5", "EEG P7", "EEG P9",
    "EEG PO7", "EEG PO3", "EEG O1", "EEG Iz", "EEG Oz", "EEG POz", "EEG Pz", "EEG CPz",
    "EEG Fpz", "EEG Fp2", "EEG AF8", "EEG AF4", "EEG AFz", "EEG Fz", "EEG F2", "EEG F4",
    "EEG F6", "EEG F8", "EEG FT8", "EEG FC6", "EEG FC4", "EEG FC2", "EEG FCz", "EEG Cz",
    "EEG C2", "EEG C4", "EEG C6", "EEG T8", "EEG TP8", "EEG CP6", "EEG CP4", "EEG CP2",
    "EEG P2", "EEG P4", "EEG P6", "EEG P8", "EEG P10", "EEG PO8", "EEG PO4", "EEG O2"
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> dict[str, str]:
    """Build rename map for NOD-EEG 64-channel EDF files.
    
    EDF channels may have 'EEG ' prefix or other BIDS-derived naming.
    Map them to standard 10-20 names without prefix.
    """
    rename_map: dict[str, str] = {}
    existing_names = list(raw.ch_names)
    
    # Direct mapping from BIDS-pattern names to standard names
    for bids_name, std_name in zip(_BIDS_CHANNEL_PATTERNS, _NOD_EEG_CHANNEL_NAMES):
        if bids_name in existing_names and bids_name != std_name:
            rename_map[bids_name] = std_name
    
    # Also try without 'EEG ' prefix if channels are already clean
    for std_name in _NOD_EEG_CHANNEL_NAMES:
        if std_name in existing_names:
            continue  # Already correct
        # Try case-insensitive match
        for existing in existing_names:
            if existing.strip().upper() == std_name.upper():
                rename_map[existing] = std_name
                break
    
    # Handle numbered channels (EEG-0, EEG-1, etc.) if present
    for i, std_name in enumerate(_NOD_EEG_CHANNEL_NAMES):
        candidates = [
            f"EEG-{i}",
            f"EEG {i}",
            f"Ch{i+1}",
            f"ch{i+1}",
            f"Channel{i+1}",
            str(i),
        ]
        for candidate in candidates:
            if candidate in existing_names and candidate not in rename_map:
                rename_map[candidate] = std_name
                break
    
    return rename_map


def _find_events_tsv(file_path: str) -> str | None:
    """Find sibling events.tsv for a given EEG file."""
    base = file_path.replace(".edf", "").replace(".set", "").replace(".fif", "")
    # BIDS naming: sub-XX_ses-YY_task-ZZ_run-WW_eeg.edf -> sub-XX_ses-YY_task-ZZ_run-WW_events.tsv
    events_path = base.replace("_eeg", "_events")
    if not events_path.endswith("_events"):
        events_path += "_events"
    events_path += ".tsv"
    
    if os.path.exists(events_path):
        return events_path
    
    # Try alternative: just replace extension
    alt_path = os.path.splitext(file_path)[0] + "_events.tsv"
    if os.path.exists(alt_path):
        return alt_path
    
    # Try without _eeg suffix removal (some BIDS variants)
    alt_path2 = file_path.replace("_eeg.edf", "_events.tsv").replace(".edf", "_events.tsv")
    if os.path.exists(alt_path2):
        return alt_path2
    
    return None


def _find_participants_tsv(file_path: str) -> str | None:
    """Find participants.tsv going up from file path."""
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        candidates = [
            os.path.join(current_dir, "participants.tsv"),
            os.path.join(current_dir, "..", "participants.tsv"),
        ]
        for cand in candidates:
            cand = os.path.normpath(cand)
            if os.path.exists(cand):
                return cand
        current_dir = os.path.dirname(current_dir)
    return None


def _read_events_tsv(events_path: str) -> pd.DataFrame | None:
    """Read events.tsv with proper handling of BIDS columns."""
    try:
        df = pd.read_csv(events_path, sep="\t", dtype=str, keep_default_na=False)
        # Convert numeric columns
        for col in ["onset", "duration", "value", "sample", "RT"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # Convert boolean columns
        for col in ["stim_is_animate"]:
            if col in df.columns:
                df[col] = df[col].map({"True": True, "False": False, "true": True, "false": False, "1": True, "0": False, "": None}).fillna(df[col])
        return df
    except Exception:
        return None


def _subject_from_file_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path."""
    basename = os.path.basename(file_path)
    # Pattern: sub-XX_...
    parts = basename.split("_")
    for part in parts:
        if part.startswith("sub-"):
            return part
    return "unknown"


@dataclass
class OpenNeuroDS005787Kernel:
    """Stage1 kernel for OpenNeuro ds005787 (NOD-EEG)."""

    KERNEL_ID: str = "openneuro-ds005787-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Ensure data is loaded before adding channels
        if not raw.preload:
            raw.load_data()

        # -------------------------------------------------------------------
        # 1. Channel renaming (BEFORE montage)
        # -------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Ensure all channels are EEG type
        ch_types = {}
        for ch_name in raw.ch_names:
            if ch_name.upper().startswith("EOG") or "EOG" in ch_name.upper():
                ch_types[ch_name] = "eog"
            elif ch_name.upper().startswith("EMG") or "EMG" in ch_name.upper():
                ch_types[ch_name] = "emg"
            elif ch_name.upper().startswith("ECG") or "EKG" in ch_name.upper():
                ch_types[ch_name] = "ecg"
            elif ch_name.upper().startswith("STIM") or "STIM" in ch_name.upper():
                ch_types[ch_name] = "stim"
            else:
                ch_types[ch_name] = "eeg"
        raw.set_channel_types(ch_types)

        # -------------------------------------------------------------------
        # 2. Set montage (10-20 standard)
        # -------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception as e:
            warnings.warn(f"Could not set montage: {e}")

        # -------------------------------------------------------------------
        # 3. Read participants.tsv for subject metadata
        # -------------------------------------------------------------------
        participants_path = _find_participants_tsv(file_path)
        subject_id = _subject_from_file_path(file_path)
        participant_info = {
            "age": "",
            "sex": "",
            "handedness": "",
            "amplifier": "BrainAmp MR Plus (inferred)",  # From README / BIDS
            "cap": "64-channel extended 10-20 actiCap (inferred)",  # From README / BIDS
        }
        if participants_path:
            try:
                p_df = pd.read_csv(participants_path, sep="\t", dtype=str, keep_default_na=False)
                sub_row = p_df[p_df["participant_id"] == subject_id.replace("sub-", "")]
                if sub_row.empty:
                    sub_row = p_df[p_df["participant_id"] == subject_id]
                if not sub_row.empty:
                    for field in ["age", "sex", "handedness"]:
                        if field in sub_row.columns:
                            val = sub_row[field].values[0]
                            participant_info[field] = str(val) if val != "" else ""
                        # Also try BIDS-style variants
                        elif field == "age" and "age" in [c.lower() for c in sub_row.columns]:
                            for c in sub_row.columns:
                                if c.lower() == "age":
                                    val = sub_row[c].values[0]
                                    participant_info["age"] = str(val) if val != "" else ""
                                    break
                        elif field == "sex" and "sex" in [c.lower() for c in sub_row.columns]:
                            for c in sub_row.columns:
                                if c.lower() == "sex":
                                    val = sub_row[c].values[0]
                                    participant_info["sex"] = str(val) if val != "" else ""
                                    break
                        elif field == "handedness" and "handedness" in [c.lower() for c in sub_row.columns]:
                            for c in sub_row.columns:
                                if c.lower() == "handedness":
                                    val = sub_row[c].values[0]
                                    participant_info["handedness"] = str(val) if val != "" else ""
                                    break
            except Exception as e:
                warnings.warn(f"Could not read participants.tsv: {e}")

        # -------------------------------------------------------------------
        # 4. Read events.tsv and create annotations + derived misc channels
        # -------------------------------------------------------------------
        events_path = _find_events_tsv(file_path)
        events_df = None
        if events_path:
            events_df = _read_events_tsv(events_path)

        # Build annotations from events.tsv
        if events_df is not None and not events_df.empty:
            # events.tsv has columns: onset, duration, trial_type, value, sample, RT, etc.
            onsets = events_df["onset"].values
            durations = events_df["duration"].fillna(0).values
            descriptions = []
            for _, ev_row in events_df.iterrows():
                trial_type = str(ev_row.get("trial_type", ""))
                value = str(ev_row.get("value", ""))
                if trial_type and value:
                    desc = f"{trial_type}/{value}"
                elif trial_type:
                    desc = trial_type
                else:
                    desc = value if value else "unknown"
                descriptions.append(desc)
            
            # Create annotations, filtering out invalid onsets
            valid_mask = ~np.isnan(onsets)
            if valid_mask.any():
                annot = mne.Annotations(
                    onset=onsets[valid_mask],
                    duration=durations[valid_mask],
                    description=[descriptions[i] for i in range(len(descriptions)) if valid_mask[i]],
                )
                raw.set_annotations(annot)

        # -------------------------------------------------------------------
        # 5. Derived misc channels from events.tsv:RT
        # -------------------------------------------------------------------
        # We need to create:
        #   - RT_misc: step function with RT value at each stim_on event onset
        #   - RT_resp_locked: step function with RT value at each resp event onset
        
        derived_channels_to_add = []
        
        if events_df is not None and not events_df.empty and "RT" in events_df.columns:
            sfreq = raw.info["sfreq"]
            n_times = raw.n_times
            times = raw.times
            
            # --- RT_misc: stim_on-locked RT step function ---
            stim_mask = events_df["trial_type"].astype(str).str.lower() == "stim_on"
            stim_events = events_df[stim_mask].copy()
            
            if not stim_events.empty and stim_events["RT"].notna().any():
                rt_misc_data = np.zeros((1, n_times))
                for _, ev in stim_events.iterrows():
                    onset = ev["onset"]
                    rt_val = ev["RT"]
                    if pd.isna(onset) or pd.isna(rt_val):
                        continue
                    # Find sample index for onset
                    sample_idx = int(round(onset * sfreq))
                    if sample_idx < n_times:
                        rt_misc_data[0, sample_idx:] = rt_val
                # Only add if we have valid data
                if np.any(rt_misc_data != 0) or stim_events["RT"].notna().any():
                    rt_misc_info = mne.create_info(
                        ch_names=["RT_misc"],
                        sfreq=sfreq,
                        ch_types=["misc"],
                    )
                    rt_misc_raw = mne.io.RawArray(rt_misc_data, rt_misc_info, verbose=False)
                    derived_channels_to_add.append(rt_misc_raw)
            
            # --- RT_resp_locked: resp-locked RT step function ---
            # Match each resp event to preceding stim_on to get RT
            # If RT column already present, use it directly for resp events
            resp_mask = events_df["trial_type"].astype(str).str.lower() == "resp"
            resp_events = events_df[resp_mask].copy()
            
            if not resp_events.empty and resp_events["RT"].notna().any():
                rt_resp_data = np.zeros((1, n_times))
                for _, ev in resp_events.iterrows():
                    onset = ev["onset"]
                    rt_val = ev["RT"]
                    if pd.isna(onset) or pd.isna(rt_val):
                        continue
                    # Find sample index for onset
                    sample_idx = int(round(onset * sfreq))
                    if sample_idx < n_times:
                        rt_resp_data[0, sample_idx:] = rt_val
                if np.any(rt_resp_data != 0) or resp_events["RT"].notna().any():
                    rt_resp_info = mne.create_info(
                        ch_names=["RT_resp_locked"],
                        sfreq=sfreq,
                        ch_types=["misc"],
                    )
                    rt_resp_raw = mne.io.RawArray(rt_resp_data, rt_resp_info, verbose=False)
                    derived_channels_to_add.append(rt_resp_raw)
            else:
                # Alternative: try to match resp events to stim_on events by trial
                # If no direct RT on resp events, compute from stim_on RT and use at resp time
                if not resp_events.empty and not stim_events.empty:
                    # Use stim_on RT values but place them at resp onsets
                    # This requires matching by trial or temporal proximity
                    rt_resp_data = np.zeros((1, n_times))
                    for _, resp_ev in resp_events.iterrows():
                        resp_onset = resp_ev["onset"]
                        if pd.isna(resp_onset):
                            continue
                        # Find preceding stim_on with valid RT
                        preceding_stim = stim_events[stim_events["onset"] < resp_onset]
                        if not preceding_stim.empty:
                            # Get most recent stim_on
                            last_stim = preceding_stim.loc[preceding_stim["onset"].idxmax()]
                            rt_val = last_stim["RT"]
                            if pd.isna(rt_val):
                                continue
                            sample_idx = int(round(resp_onset * sfreq))
                            if sample_idx < n_times:
                                rt_resp_data[0, sample_idx:] = rt_val
                    if np.any(rt_resp_data != 0):
                        rt_resp_info = mne.create_info(
                            ch_names=["RT_resp_locked"],
                            sfreq=sfreq,
                            ch_types=["misc"],
                        )
                        rt_resp_raw = mne.io.RawArray(rt_resp_data, rt_resp_info, verbose=False)
                        derived_channels_to_add.append(rt_resp_raw)

        # Add all derived channels to raw
        for derived_raw in derived_channels_to_add:
            raw.add_channels([derived_raw], force_update_info=True)

        # -------------------------------------------------------------------
        # 6. Store metadata in raw.info["description"] as JSON
        # -------------------------------------------------------------------
        eegunity_description = {
            "age": participant_info["age"],
            "sex": participant_info["sex"],
            "amplifier": participant_info["amplifier"],
            "cap": participant_info["cap"],
            "handedness": participant_info["handedness"],
        }
        
        # Merge with existing description if present
        existing_desc = raw.info.get("description", "")
        try:
            existing_dict = json.loads(existing_desc) if existing_desc else {}
        except json.JSONDecodeError:
            existing_dict = {"original_description": existing_desc}
        
        existing_dict.update({"eegunity": eegunity_description})
        raw.info["description"] = json.dumps(existing_dict, ensure_ascii=False)

        return raw


KERNEL = OpenNeuroDS005787Kernel()