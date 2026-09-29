import json
import os
import re
from pathlib import Path

import mne
import numpy as np
import pandas as pd


class OpenneuroDs001787Kernel:
    KERNEL_ID = "openneuro_ds001787"

    def __init__(self):
        self._dataset_root = None
        self._participants_df = None
        self._channels_tsv_cache = {}

    def _get_dataset_root(self, file_path):
        """Infer dataset root from file path."""
        fp = str(file_path)
        p = Path(fp).resolve()
        for parent in [p] + list(p.parents):
            try:
                if (parent / "participants.tsv").exists():
                    return str(parent)
            except (PermissionError, OSError):
                pass
            if "openneuro_raw" in str(parent) or "ds001787" in str(parent.name):
                return str(parent)
        return str(p.parents[3]) if len(p.parents) >= 4 else str(p.parent)

    def _load_participants(self, dataset_root):
        """Load participants.tsv once and cache."""
        if self._participants_df is not None:
            return self._participants_df
        participants_path = Path(dataset_root) / "participants.tsv"
        if participants_path.exists():
            self._participants_df = pd.read_csv(participants_path, sep="\t")
        else:
            self._participants_df = pd.DataFrame()
        return self._participants_df

    def _get_subject_from_path(self, file_path):
        """Extract subject ID from BIDS file path."""
        fp = str(file_path)
        match = re.search(r"sub-(\w+)", fp)
        if match:
            return f"sub-{match.group(1)}"
        return None

    def _get_ses_from_path(self, file_path):
        """Extract session ID from BIDS file path."""
        fp = str(file_path)
        match = re.search(r"ses-(\w+)", fp)
        if match:
            return f"ses-{match.group(1)}"
        return None

    def _get_participant_info(self, dataset_root, subject_id):
        """Get participant info from participants.tsv."""
        df = self._load_participants(dataset_root)
        if df.empty or subject_id is None:
            return {}
        row = df[df["participant_id"] == subject_id]
        if row.empty:
            row = df[df["participant_id"] == subject_id.replace("sub-", "")]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()

    def _find_events_tsv(self, file_path):
        """Find sibling events.tsv for a given EEG file."""
        fp = Path(file_path)
        stem = fp.stem
        events_file = fp.parent / f"{stem.replace('_eeg', '')}_events.tsv"
        if not events_file.exists():
            events_file = fp.parent / f"{stem}_events.tsv"
        if events_file.exists():
            return str(events_file)
        alt_stem = stem.replace("_eeg", "")
        events_file = fp.parent / f"{alt_stem}_events.tsv"
        if events_file.exists():
            return str(events_file)
        return None

    def _find_channels_tsv(self, file_path):
        """Find sibling channels.tsv for a given EEG file."""
        fp = Path(file_path)
        stem = fp.stem
        channels_file = fp.parent / f"{stem.replace('_eeg', '')}_channels.tsv"
        if not channels_file.exists():
            channels_file = fp.parent / f"{stem}_channels.tsv"
        if channels_file.exists():
            return str(channels_file)
        alt_stem = stem.replace("_eeg", "")
        channels_file = fp.parent / f"{alt_stem}_channels.tsv"
        if channels_file.exists():
            return str(channels_file)
        return None

    def _load_events_tsv(self, events_tsv_path):
        """Load events.tsv file."""
        if events_tsv_path is None or not Path(events_tsv_path).exists():
            return None
        return pd.read_csv(events_tsv_path, sep="\t")

    def _events_to_annotations(self, events_df, sfreq):
        """Convert events.tsv DataFrame to mne.Annotations."""
        if events_df is None or events_df.empty:
            return None

        onsets = []
        durations = []
        descriptions = []

        for _, row in events_df.iterrows():
            if "onset" in row:
                onset = float(row["onset"])
            elif "sample" in row:
                onset = float(row["sample"]) / sfreq
            else:
                continue

            if "duration" in row and pd.notna(row["duration"]):
                duration = float(row["duration"])
            else:
                duration = 0.0

            if "value" in row and pd.notna(row["value"]):
                desc = str(row["value"]).strip()
            elif "trial_type" in row and pd.notna(row["trial_type"]):
                desc = str(row["trial_type"]).strip()
            else:
                continue

            onsets.append(onset)
            durations.append(duration)
            descriptions.append(desc)

        if not onsets:
            return None

        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)

    def _rename_channels(self, raw, channels_tsv_path):
        """Rename channels based on channels.tsv if available."""
        if channels_tsv_path is None or not Path(channels_tsv_path).exists():
            return raw

        try:
            ch_df = pd.read_csv(channels_tsv_path, sep="\t")
        except Exception:
            return raw

        if "name" not in ch_df.columns or "new_name" not in ch_df.columns:
            return raw

        rename_map = {}
        for _, row in ch_df.iterrows():
            old_name = str(row["name"]).strip()
            new_name = str(row["new_name"]).strip()
            if old_name and new_name and old_name in raw.ch_names:
                rename_map[old_name] = new_name

        if rename_map:
            raw.rename_channels(rename_map, allow_duplicates=True)

        return raw

    def _set_channel_types(self, raw, channels_tsv_path):
        """Set channel types based on channels.tsv."""
        if channels_tsv_path is None or not Path(channels_tsv_path).exists():
            return raw

        try:
            ch_df = pd.read_csv(channels_tsv_path, sep="\t")
        except Exception:
            return raw

        if "name" not in ch_df.columns or "type" not in ch_df.columns:
            return raw

        type_mapping = {
            "eeg": "eeg",
            "eog": "eog",
            "ecg": "ecg",
            "emg": "emg",
            "trigger": "stim",
            "stim": "stim",
            "misc": "misc",
            "ref": "misc",
            "resp": "resp",
        }

        ch_types = {}
        for _, row in ch_df.iterrows():
            ch_name = str(row["name"]).strip()
            ch_type = str(row["type"]).lower().strip() if pd.notna(row["type"]) else "eeg"
            if ch_name in raw.ch_names:
                mapped = type_mapping.get(ch_type, "eeg")
                ch_types[ch_name] = mapped

        if ch_types:
            raw.set_channel_types(ch_types, on_unit_change="ignore")

        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage if channels match."""
        try:
            ch_names = [c.strip().upper() for c in raw.ch_names]
            standard_1020 = [
                "FP1", "FP2", "AF3", "AF4", "AF7", "AF8", "AFZ",
                "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "FZ",
                "FC1", "FC2", "FC3", "FC4", "FC5", "FC6", "FCZ",
                "C1", "C2", "C3", "C4", "C5", "C6", "CZ",
                "CP1", "CP2", "CP3", "CP4", "CP5", "CP6", "CPZ",
                "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "PZ",
                "PO3", "PO4", "PO7", "PO8", "POZ",
                "O1", "O2", "OZ",
                "T7", "T8", "TP7", "TP8", "FT7", "FT8",
                "FPZ", "IZ",
            ]
            has_standard = any(c in standard_1020 for c in ch_names)
            if has_standard:
                raw.set_montage("standard_1020", on_missing="ignore")
        except Exception:
            pass
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = str(row.get("File Path", ""))
        dataset_root = self._get_dataset_root(file_path)
        subject_id = self._get_subject_from_path(file_path)
        participant_info = self._get_participant_info(dataset_root, subject_id)

        eegunity_description = {
            "age": str(participant_info.get("age", "")),
            "sex": str(participant_info.get("sex", "")),
            "amplifier": str(participant_info.get("amplifier", "")),
            "cap": str(participant_info.get("cap", "")),
            "handedness": str(participant_info.get("handedness", "")),
        }

        if "gender" in participant_info:
            eegunity_description["gender"] = str(participant_info["gender"])

        original_desc = raw.info.get("description", "")

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        channels_tsv = self._find_channels_tsv(file_path)
        if channels_tsv:
            raw = self._rename_channels(raw, channels_tsv)
            raw = self._set_channel_types(raw, channels_tsv)

        raw = self._set_montage(raw)

        events_tsv = self._find_events_tsv(file_path)
        events_df = self._load_events_tsv(events_tsv)
        annotations = self._events_to_annotations(events_df, raw.info["sfreq"])
        if annotations is not None:
            raw.set_annotations(annotations)

        return raw


KERNEL = OpenneuroDs001787Kernel()