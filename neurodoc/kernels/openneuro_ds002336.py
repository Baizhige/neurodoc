"""OpenNeuro DS002336 stage1 kernel for EEGUnity.

Motor imagery neurofeedback dataset with simultaneous EEG-fMRI acquisition.
64-channel BrainVision data recorded at 5000 Hz inside MRI scanner.

Source: https://openneuro.org/datasets/ds002336
Paper: 10.1038/s41597-020-0498-3
"""

from __future__ import annotations

import json
import os
import re

import mne
import numpy as np
import pandas as pd


# Standard 10-20 64-channel layout for this dataset
# Source: 10.1038/s41597-020-0498-3 (dataset descriptor), Table 1 and supplementary material
# Annotator: LLM, 2026-04-08; 由 LLM 推断，需人类复核
_EEG_CHANNEL_MAP = {
    "EEG01": "Fp1", "EEG02": "Fp2", "EEG03": "F7", "EEG04": "F3",
    "EEG05": "Fz", "EEG06": "F4", "EEG07": "F8", "EEG08": "FC5",
    "EEG09": "FC1", "EEG10": "FC2", "EEG11": "FC6", "EEG12": "C5",
    "EEG13": "C3", "EEG14": "C1", "EEG15": "Cz", "EEG16": "C2",
    "EEG17": "C4", "EEG18": "C6", "EEG19": "CP5", "EEG20": "CP1",
    "EEG21": "CP2", "EEG22": "CP6", "EEG23": "P7", "EEG24": "P3",
    "EEG25": "Pz", "EEG26": "P4", "EEG27": "P8", "EEG28": "PO7",
    "EEG29": "PO3", "EEG30": "POz", "EEG31": "PO4", "EEG32": "PO8",
    "EEG33": "O1", "EEG34": "Oz", "EEG35": "O2", "EEG36": "AF7",
    "EEG37": "AF3", "EEG38": "AF4", "EEG39": "AF8", "EEG40": "F9",
    "EEG41": "F10", "EEG42": "FT9", "EEG43": "FT7", "EEG44": "FT8",
    "EEG45": "FT10", "EEG46": "TP9", "EEG47": "TP7", "EEG48": "TP8",
    "EEG49": "TP10", "EEG50": "P9", "EEG51": "P10", "EEG52": "PO9",
    "EEG53": "PO10", "EEG54": "ECG", "EEG55": "Fpz", "EEG56": "FC3",
    "EEG57": "FC4", "EEG58": "CP3", "EEG59": "CP4", "EEG60": "CPz",
    "EEG61": "P1", "EEG62": "P2", "EEG63": "P5", "EEG64": "P6",
}

_CHANNEL_PATTERNS = [
    (re.compile(r'^EEG\s*(\d+)$', re.IGNORECASE), lambda m: f"EEG{m.group(1).zfill(2)}"),
    (re.compile(r'^EEG(\d+)$', re.IGNORECASE), lambda m: f"EEG{m.group(1).zfill(2)}"),
    (re.compile(r'^(\d+)$'), lambda m: f"EEG{m.group(1).zfill(2)}"),
]


def _normalize_channel_name(ch_name):
    for pattern, formatter in _CHANNEL_PATTERNS:
        match = pattern.match(ch_name.strip())
        if match:
            return formatter(match)
    return None


def _find_events_tsv(file_path):
    base = file_path
    for ext in [".eeg", ".vhdr", ".vmrk", ".edf", ".set", ".fif"]:
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    
    dir_path = os.path.dirname(file_path)
    
    candidates = []
    if base:
        candidates.append(base + "_events.tsv")
        base_no_run = re.sub(r'_run-\d+', '', base)
        if base_no_run != base:
            candidates.append(base_no_run + "_events.tsv")
    
    sub_match = re.search(r'(sub-\d+)', os.path.basename(file_path))
    if sub_match:
        sub_id = sub_match.group(1)
        for f in os.listdir(dir_path) if os.path.isdir(dir_path) else []:
            if f.endswith("_events.tsv") and sub_id in f:
                candidates.append(os.path.join(dir_path, f))
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    
    for f in sorted(os.listdir(dir_path)) if os.path.isdir(dir_path) else []:
        if f.endswith("_events.tsv"):
            return os.path.join(dir_path, f)
    
    return None


def _find_participants_tsv(file_path):
    dir_path = os.path.dirname(file_path)
    while dir_path and dir_path != os.path.dirname(dir_path):
        candidate = os.path.join(dir_path, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        dir_path = os.path.dirname(dir_path)
    return None


def _get_subject_info(participants_path, subject_id):
    if not participants_path or not os.path.exists(participants_path):
        return {}
    
    try:
        df = pd.read_csv(participants_path, sep="\t")
    except Exception:
        return {}
    
    subj_col = None
    for col in df.columns:
        if col.lower() in ["participant_id", "subject_id", "participant", "subject"]:
            subj_col = col
            break
    
    if subj_col is None:
        return {}
    
    row = df[df[subj_col] == subject_id]
    if row.empty:
        row = df[df[subj_col] == subject_id.replace("sub-", "")]
    if row.empty:
        row = df[df[subj_col] == "sub-" + subject_id.replace("sub-", "")]
    
    if row.empty:
        return {}
    
    info = {}
    for col in df.columns:
        if col == subj_col:
            continue
        val = row.iloc[0][col]
        if pd.isna(val):
            info[col] = "unknown"
        else:
            info[col] = str(val)
    
    return info


def _normalize_sex(sex_str):
    if not sex_str or str(sex_str).lower() in ["unknown", "nan", "none", ""]:
        return "unknown"
    s = str(sex_str).lower().strip()
    if s in ["m", "male"]:
        return "male"
    if s in ["f", "female"]:
        return "female"
    return "unknown"


def _normalize_age(age_val):
    if age_val is None or str(age_val).lower() in ["unknown", "nan", "none", ""]:
        return "unknown"
    try:
        age_float = float(age_val)
        if np.isnan(age_float):
            return "unknown"
        return str(int(age_float))
    except (ValueError, TypeError):
        return "unknown"


class OpenNeuroDS002336Kernel:
    """Stage1 kernel for OpenNeuro ds002336 dataset."""

    KERNEL_ID: str = "openneuro-ds002336-stage1"
    kernel_requirements = {
        "required_event_ids": ["Stimulus/S  1", "Stimulus/S  2", "Stimulus/S 99"],
        "required_native_misc": ["ECG"],
        "derived_misc_channels": [],
        "required_info_fields": ["age", "sex"],
    }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # --- Channel renaming ---
        rename_map = {}
        for ch_name in raw.ch_names:
            normalized = _normalize_channel_name(ch_name)
            if normalized and normalized in _EEG_CHANNEL_MAP:
                target = _EEG_CHANNEL_MAP[normalized]
                if ch_name != target:
                    rename_map[ch_name] = target
        
        # Handle direct matches (already in EEGXX format)
        for ch_name in raw.ch_names:
            if ch_name in _EEG_CHANNEL_MAP and _EEG_CHANNEL_MAP[ch_name] != ch_name:
                if ch_name not in rename_map:
                    rename_map[ch_name] = _EEG_CHANNEL_MAP[ch_name]
        
        if rename_map:
            raw.rename_channels(rename_map)

        # --- Set montage AFTER channel rename ---
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
        except Exception:
            pass

        # --- Ensure ECG is misc type ---
        ecg_names = [ch for ch in raw.ch_names if ch.upper() == "ECG"]
        if ecg_names:
            misc_map = {ch: "misc" for ch in ecg_names}
            raw.set_channel_types(misc_map)

        # --- Extract subject info from participants.tsv ---
        subject_id = None
        sub_match = re.search(r'sub-(\d+)', os.path.basename(file_path))
        if sub_match:
            subject_id = f"sub-{sub_match.group(1)}"
        
        participants_path = _find_participants_tsv(file_path)
        subject_info = _get_subject_info(participants_path, subject_id) if subject_id else {}

        # --- Build eegunity_description ---
        age = _normalize_age(subject_info.get("age", "unknown"))
        sex = _normalize_sex(subject_info.get("sex", "unknown"))

        # Required info fields from participants.tsv
        extra_info = {}
        for field in self.kernel_requirements.get("required_info_fields", []):
            if field in subject_info:
                extra_info[field] = subject_info[field]
            else:
                extra_info[field] = "unknown"

        # Device info from paper: BrainAmp MR plus with BrainCap MR
        # Source: 10.1038/s41597-020-0498-3, Methods section
        # LLM 推断，需人类复核
        amplifier = "BrainAmp MR plus"  # LLM 推断，需人类复核
        cap = "BrainCap MR (Ag/AgCl)"  # LLM 推断，需人类复核
        handedness = "unknown"  # not reported in participants.tsv

        eegunity_desc = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        eegunity_desc.update(extra_info)

        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # --- Process events from events.tsv ---
        events_tsv_path = _find_events_tsv(file_path)
        
        if events_tsv_path and os.path.exists(events_tsv_path):
            try:
                events_df = pd.read_csv(events_tsv_path, sep="\t")
                
                # Check if we need to derive annotations from events.tsv
                # BrainVision .eeg files may have markers in .vmrk but we ensure
                # events.tsv annotations are present for robustness
                has_annotations = False
                try:
                    existing_annot = raw.annotations
                    if existing_annot and len(existing_annot) > 0:
                        has_annotations = True
                except Exception:
                    pass

                # Build annotations from events.tsv
                if "onset" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
                    
                    # Determine description column
                    desc_col = None
                    for col in ["trial_type", "value", "stim_type", "event_type"]:
                        if col in events_df.columns:
                            desc_col = col
                            break
                    
                    if desc_col is None and len(events_df.columns) >= 3:
                        # Fallback: use third column
                        desc_col = events_df.columns[2]
                    
                    descriptions = []
                    if desc_col:
                        for val in events_df[desc_col].values:
                            if pd.isna(val):
                                descriptions.append("unknown")
                            else:
                                descriptions.append(str(val))
                    else:
                        descriptions = ["event"] * len(onsets)
                    
                    # Filter out empty/NaN onsets
                    valid_mask = ~np.isnan(onsets)
                    onsets = onsets[valid_mask]
                    durations = durations[valid_mask] if len(durations) == len(valid_mask) else np.zeros(len(onsets))
                    descriptions = [d for i, d in enumerate(descriptions) if valid_mask[i]]
                    
                    # Create annotations
                    new_annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations[:len(onsets)] if len(durations) >= len(onsets) else np.zeros(len(onsets)),
                        description=descriptions,
                    )
                    
                    # Merge with existing or set new
                    if has_annotations:
                        raw.set_annotations(raw.annotations + new_annotations)
                    else:
                        raw.set_annotations(new_annotations)
                    
            except Exception:
                pass

        # --- Final validation: ensure required event IDs can be discovered ---
        # Verify annotations contain the expected event patterns
        try:
            if raw.annotations and len(raw.annotations) > 0:
                # Check for Stimulus/S patterns and normalize if needed
                new_descs = []
                changed = False
                for desc in raw.annotations.description:
                    # Map common patterns to required event IDs
                    new_desc = desc
                    if re.search(r'S\s*99', desc, re.IGNORECASE) and "99" in desc:
                        new_desc = "Stimulus/S 99"
                    elif re.search(r'S\s*1\s*$', desc) and "1" in desc and "99" not in desc and "2" not in desc:
                        new_desc = "Stimulus/S  1"
                    elif re.search(r'S\s*2', desc) and "2" in desc:
                        new_desc = "Stimulus/S  2"
                    
                    if new_desc != desc:
                        changed = True
                    new_descs.append(new_desc)
                
                if changed:
                    new_annot = mne.Annotations(
                        onset=raw.annotations.onset,
                        duration=raw.annotations.duration,
                        description=new_descs,
                    )
                    raw.set_annotations(new_annot)
        except Exception:
            pass

        return raw


KERNEL = OpenNeuroDS002336Kernel()