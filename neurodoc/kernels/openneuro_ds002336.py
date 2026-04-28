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
    current_dir = os.path.dirname(os.path.abspath(file_path))
    while current_dir != os.path.dirname(current_dir):
        candidate = os.path.join(current_dir, "participants.tsv")
        if os.path.exists(candidate):
            return candidate
        current_dir = os.path.dirname(current_dir)
    return None


class OpenNeuroDS002336Kernel:
    KERNEL_ID = "openneuro-ds002336-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", "")
        original_description = raw.info.get("description", "")

        raw = self._rename_channels(raw)
        raw = self._ensure_misc_channels(raw)
        raw = self._set_montage(raw)
        raw = self._process_events(raw, file_path)
        raw = self._add_derived_misc_channels(raw, file_path)

        participants_tsv = _find_participants_tsv(file_path)
        eegunity_description = {
            "age": "",
            "sex": "",
            "amplifier": "",
            "cap": "",
            "handedness": "",
        }
        if participants_tsv:
            df = pd.read_csv(participants_tsv, sep="\t")
            sub_match = re.search(r'(sub-\d+)', os.path.basename(file_path))
            if sub_match:
                sub_id = sub_match.group(1)
                sub_row = df[df["participant_id"] == sub_id]
                if not sub_row.empty:
                    eegunity_description["age"] = str(sub_row["age"].values[0]) if "age" in sub_row.columns else ""
                    eegunity_description["sex"] = str(sub_row["sex"].values[0]) if "sex" in sub_row.columns else ""
                    eegunity_description["amplifier"] = str(sub_row["amplifier"].values[0]) if "amplifier" in sub_row.columns else ""
                    eegunity_description["cap"] = str(sub_row["cap"].values[0]) if "cap" in sub_row.columns else ""
                    eegunity_description["handedness"] = str(sub_row["handedness"].values[0]) if "handedness" in sub_row.columns else ""

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw

    def _rename_channels(self, raw):
        original_ch_names = raw.ch_names.copy()
        rename_map = {}

        for ch_name in original_ch_names:
            if ch_name in _EEG_CHANNEL_MAP:
                rename_map[ch_name] = _EEG_CHANNEL_MAP[ch_name]
                continue
            
            normalized = _normalize_channel_name(ch_name)
            if normalized and normalized in _EEG_CHANNEL_MAP:
                rename_map[ch_name] = _EEG_CHANNEL_MAP[normalized]
                continue
            
            for key, value in _EEG_CHANNEL_MAP.items():
                if ch_name.upper() == key.upper():
                    rename_map[ch_name] = value
                    break

        if rename_map:
            raw = raw.rename_channels(rename_map)

        return raw

    def _ensure_misc_channels(self, raw):
        ch_types = raw.get_channel_types()
        misc_to_set = {}

        for ch_name in raw.ch_names:
            if ch_name.upper() == "ECG" and ch_types.get(ch_name) != "misc":
                misc_to_set[ch_name] = "misc"

        if misc_to_set:
            raw.set_channel_types(misc_to_set)

        return raw

    def _set_montage(self, raw):
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            montage_ch_names = set(montage.ch_names)
            raw_eeg_ch_names = [ch for ch in raw.ch_names if ch in montage_ch_names]
            if raw_eeg_ch_names:
                raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass
        return raw

    def _process_events(self, raw, file_path):
        events_tsv = _find_events_tsv(file_path)
        if events_tsv:
            try:
                events_df = pd.read_csv(events_tsv, sep="\t")
                if "onset" in events_df.columns and "trial_type" in events_df.columns:
                    onsets = events_df["onset"].values
                    durations = events_df["duration"].values if "duration" in events_df.columns else np.zeros(len(onsets))
                    descriptions = events_df["trial_type"].astype(str).values
                    annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                    raw.set_annotations(annotations)
            except Exception:
                pass
        return raw

    def _add_derived_misc_channels(self, raw, file_path):
        participants_tsv = _find_participants_tsv(file_path)
        if not participants_tsv:
            return raw
        
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            sub_match = re.search(r'(sub-\d+)', os.path.basename(file_path))
            if not sub_match:
                return raw
            sub_id = sub_match.group(1)
            sub_row = df[df["participant_id"] == sub_id]
            if sub_row.empty:
                return raw
            
            derived_misc_channels = []
            for col in sub_row.columns:
                if col not in ["participant_id", "age", "sex", "handedness", "amplifier", "cap"]:
                    derived_misc_channels.append(col)
            
            for ch_name in derived_misc_channels:
                if ch_name in raw.ch_names:
                    continue
                val = sub_row[ch_name].values[0]
                try:
                    float_val = float(val)
                except (ValueError, TypeError):
                    float_val = 0.0
                data = np.full((1, len(raw.times)), float_val)
                info = mne.create_info([ch_name], raw.info["sfreq"], ["misc"])
                raw_misc = mne.io.RawArray(data, info)
                raw.add_channels([raw_misc], force_update_info=True)
        except Exception:
            pass
        
        return raw


KERNEL = OpenNeuroDS002336Kernel()