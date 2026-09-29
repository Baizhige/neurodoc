import json
import os
import re
import numpy as np
import pandas as pd
import mne
from mne import create_info, Annotations
from mne.io import RawArray


class OpenneuroDs002158Kernel:
    KERNEL_ID = "openneuro_ds002158"

    def __init__(self):
        self.dataset_name = "openneuro_ds002158"
        self.target_events = ["Response/R128"]
        self.required_info_fields = ["age", "sex"]
        self.required_native_misc = []
        self.derived_misc_channels = [
            "confidence",
            "response_time",
            "dots_difference",
            "stim_side",
            "response_time2",
            "age_binned",
        ]

    def _get_events_tsv_path(self, raw_path):
        """Get the path to the corresponding events.tsv file."""
        base = raw_path.replace(".set", "").replace(".edf", "").replace(".eeg", "").replace(".fif", "").replace(".vhdr", "")
        events_path = base + "_events.tsv"
        if os.path.exists(events_path):
            return events_path
        events_path = base + ".tsv"
        if os.path.exists(events_path):
            return events_path
        parent = os.path.dirname(raw_path)
        for f in os.listdir(parent):
            if f.endswith("_events.tsv"):
                return os.path.join(parent, f)
        return None

    def _get_participants_tsv_path(self, raw_path):
        """Get the path to participants.tsv."""
        current = os.path.dirname(raw_path)
        while current != os.path.dirname(current):
            p = os.path.join(current, "participants.tsv")
            if os.path.exists(p):
                return p
            current = os.path.dirname(current)
        return None

    def _read_events_tsv(self, events_path):
        """Read events.tsv and return DataFrame."""
        if events_path is None or not os.path.exists(events_path):
            return None
        try:
            df = pd.read_csv(events_path, sep='\t')
            return df
        except Exception:
            return None

    def _read_participants_tsv(self, participants_path, subject_id):
        """Read participants.tsv and return row for subject."""
        if participants_path is None or not os.path.exists(participants_path):
            return None
        try:
            df = pd.read_csv(participants_path, sep='\t')
            for col in df.columns:
                if col in ['participant_id', 'subject_id', 'sub_id']:
                    mask = (df[col] == subject_id) | (df[col] == subject_id.replace('sub-', '')) | (df[col] == 'sub-' + subject_id.replace('sub-', ''))
                    if mask.any():
                        return df[mask].iloc[0].to_dict()
            if len(df) > 0:
                first_col = df.columns[0]
                mask = (df[first_col] == subject_id) | (df[first_col] == subject_id.replace('sub-', '')) | (df[first_col] == 'sub-' + subject_id.replace('sub-', ''))
                if mask.any():
                    return df[mask].iloc[0].to_dict()
            return None
        except Exception:
            return None

    def _extract_subject_id(self, raw_path):
        """Extract subject ID from raw file path."""
        parts = raw_path.split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        basename = os.path.basename(raw_path)
        match = re.search(r'sub-(\w+)', basename)
        if match:
            return f"sub-{match.group(1)}"
        for part in parts:
            if 'sub' in part.lower():
                return part
        return "unknown"

    def _create_step_function_channel(self, raw, events_df, column_name, fill_value=0):
        """Create a step function misc channel from events.tsv column."""
        sfreq = raw.info['sfreq']
        n_samples = raw.n_times
        data = np.full(n_samples, float(fill_value), dtype=float)
        
        if events_df is None or column_name not in events_df.columns:
            return None
        
        ev = events_df.sort_values('onset').reset_index(drop=True)
        
        for i, row in ev.iterrows():
            onset = row['onset']
            if 'duration' in row and pd.notna(row['duration']) and row['duration'] > 0:
                duration = row['duration']
            elif i + 1 < len(ev):
                duration = ev.iloc[i + 1]['onset'] - onset
            else:
                duration = 1.0
            
            start_sample = int(np.floor(onset * sfreq))
            end_sample = int(np.floor((onset + duration) * sfreq))
            start_sample = max(0, min(start_sample, n_samples))
            end_sample = max(0, min(end_sample, n_samples))
            
            if start_sample < end_sample:
                val = row.get(column_name, fill_value)
                if pd.isna(val):
                    val = fill_value
                data[start_sample:end_sample] = float(val)
        
        return data

    def _create_constant_channel(self, raw, value):
        """Create a constant broadcast channel."""
        n_samples = raw.n_times
        return np.full(n_samples, float(value), dtype=float)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        raw_path = row['file_path'] if 'file_path' in row else raw.filenames[0] if hasattr(raw, 'filenames') and raw.filenames else ''
        subject_id = self._extract_subject_id(raw_path)
        
        events_path = self._get_events_tsv_path(raw_path)
        events_df = self._read_events_tsv(events_path)
        
        participants_path = self._get_participants_tsv_path(raw_path)
        participant_info = self._read_participants_tsv(participants_path, subject_id)
        
        age = "unknown"
        sex = "unknown"
        amplifier = "unknown"
        cap = "unknown"
        handedness = "unknown"
        
        if participant_info:
            if 'age' in participant_info and pd.notna(participant_info['age']):
                age = str(int(float(participant_info['age'])))
            if 'sex' in participant_info and pd.notna(participant_info['sex']):
                sex_val = str(participant_info['sex']).lower()
                if sex_val in ['m', 'male']:
                    sex = "male"
                elif sex_val in ['f', 'female']:
                    sex = "female"
                else:
                    sex = sex_val
            if 'amplifier' in participant_info and pd.notna(participant_info['amplifier']):
                amplifier = str(participant_info['amplifier'])
            if 'cap' in participant_info and pd.notna(participant_info['cap']):
                cap = str(participant_info['cap'])
            if 'handedness' in participant_info and pd.notna(participant_info['handedness']):
                handedness = str(participant_info['handedness'])
        
        age_binned_value = None
        if participants_path and os.path.exists(participants_path):
            try:
                all_participants = pd.read_csv(participants_path, sep='\t')
                if 'age' in all_participants.columns:
                    ages = pd.to_numeric(all_participants['age'], errors='coerce').dropna()
                    if len(ages) > 0:
                        median_age = ages.median()
                        if age != "unknown":
                            age_float = float(age)
                            age_binned_value = 0.0 if age_float <= median_age else 1.0
            except Exception:
                pass
        
        original_description = raw.info.get("description", "")
        
        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }
        
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })
        
        misc_data = []
        misc_names = []
        
        for ch_name in self.derived_misc_channels:
            if ch_name == "confidence":
                data = self._create_step_function_channel(raw, events_df, "confidence", fill_value=0)
            elif ch_name == "response_time":
                data = self._create_step_function_channel(raw, events_df, "response_time", fill_value=0)
            elif ch_name == "dots_difference":
                data = self._create_step_function_channel(raw, events_df, "dots_difference", fill_value=0)
            elif ch_name == "stim_side":
                data = self._create_step_function_channel(raw, events_df, "stim_side", fill_value=0)
            elif ch_name == "response_time2":
                data = self._create_step_function_channel(raw, events_df, "response_time2", fill_value=0)
            elif ch_name == "age_binned":
                if age_binned_value is not None:
                    data = self._create_constant_channel(raw, age_binned_value)
                else:
                    data = None
            else:
                data = None
            
            if data is not None:
                misc_data.append(data.reshape(1, -1))
                misc_names.append(ch_name)
        
        if misc_data:
            all_misc_data = np.vstack(misc_data)
            misc_info = create_info(ch_names=misc_names, sfreq=raw.info['sfreq'], ch_types='misc')
            misc_raw = RawArray(all_misc_data, misc_info, verbose=False)
            raw.add_channels([misc_raw], force_update_info=True)
        
        if events_df is not None and 'trial_type' in events_df.columns:
            onsets = events_df['onset'].values
            durations = events_df['duration'].values if 'duration' in events_df.columns else np.zeros(len(onsets))
            descriptions = events_df['trial_type'].astype(str).values
            annot = Annotations(onset=onsets, duration=durations, description=descriptions)
            raw.set_annotations(annot)
        
        return raw


KERNEL = OpenneuroDs002158Kernel()