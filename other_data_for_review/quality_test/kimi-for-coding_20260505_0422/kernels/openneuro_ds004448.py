import json
import os
import numpy as np
import pandas as pd
import mne


class OpenneuroDs004448Kernel:
    KERNEL_ID = "openneuro_ds004448"
    KERNEL_NAME = "OpenNeuro ds004448 - SMR-BCI Motor Imagery Neurofeedback"
    KERNEL_DESCRIPTION = "EEG kernel for SMR-based BCI motor imagery neurofeedback with rest and motor imagery periods"
    KERNEL_CITATION = "10.1038/s41597-023-02260-6"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds004448"

    required_event_ids = ['event_1', 'event_2', 'event_3']
    required_info_fields = ['age', 'gender', 'handedness']
    required_native_misc = []
    derived_misc_channels = ['trial_index']

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('ds004448'):
                return os.sep.join(parts[:i+1])
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        current = os.path.dirname(filepath)
        while current and current != os.sep:
            if os.path.exists(os.path.join(current, 'participants.tsv')):
                return current
            current = os.path.dirname(current)
        return None

    def _get_subject_id(self, filepath):
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        return None

    def _read_participants_info(self, bids_root, subject_id):
        if bids_root is None:
            return {}
        p_tsv = os.path.join(bids_root, 'participants.tsv')
        if not os.path.exists(p_tsv):
            return {}
        try:
            df = pd.read_csv(p_tsv, sep='\t')
            subj_col = None
            for col in df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]
            subj_rows = df[df[subj_col] == subject_id]
            if len(subj_rows) == 0:
                if subject_id.startswith('sub-'):
                    alt_id = subject_id[4:]
                else:
                    alt_id = 'sub-' + subject_id
                subj_rows = df[df[subj_col] == alt_id]
            if len(subj_rows) == 0:
                return {}
            row = subj_rows.iloc[0]
            info = {}
            for field in self.required_info_fields:
                if field in row:
                    val = row[field]
                    if pd.isna(val):
                        info[field] = "unknown"
                    else:
                        info[field] = str(val)
                else:
                    info[field] = "unknown"
            return info
        except Exception:
            return {}

    def _find_events_tsv(self, filepath):
        base = filepath.replace('.edf', '').replace('.set', '').replace('.fif', '').replace('.eeg', '').replace('.vhdr', '').replace('.vmrk', '')
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        dir_path = os.path.dirname(filepath)
        for f in os.listdir(dir_path):
            if f.endswith('_events.tsv'):
                return os.path.join(dir_path, f)
        return None

    def _read_events_tsv(self, events_tsv):
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        try:
            return pd.read_csv(events_tsv, sep='\t')
        except Exception:
            return None

    def _build_trial_index_misc(self, raw, events_df):
        if events_df is None or 'trial' not in events_df.columns:
            return raw
        sfreq = raw.info['sfreq']
        n_samples = len(raw.times)
        trial_data = np.zeros((1, n_samples))
        for _, ev_row in events_df.iterrows():
            onset = ev_row.get('onset', None)
            duration = ev_row.get('duration', 6.0)
            trial_val = ev_row.get('trial', 0)
            if pd.isna(onset):
                continue
            start_idx = int(onset * sfreq)
            end_idx = int((onset + duration) * sfreq)
            start_idx = max(0, start_idx)
            end_idx = min(n_samples, end_idx)
            if start_idx < n_samples and end_idx > start_idx:
                trial_data[0, start_idx:end_idx] = float(trial_val)
        info = mne.create_info(['trial_index'], sfreq=sfreq, ch_types=['misc'])
        trial_raw = mne.io.RawArray(trial_data, info)
        raw.add_channels([trial_raw], force_update_info=True)
        return raw

    def _rename_channels(self, raw):
        rename_map = {}
        for ch_name in raw.ch_names:
            ch_upper = ch_name.upper()
            if ch_upper.startswith('EEG '):
                new_name = ch_upper.replace('EEG ', '')
                rename_map[ch_name] = new_name
            elif ch_upper.startswith('EEG'):
                new_name = ch_upper.replace('EEG', '', 1)
                rename_map[ch_name] = new_name
        if rename_map:
            raw.rename_channels(rename_map)
        return raw

    def _set_montage(self, raw):
        try:
            raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            pass
        return raw

    def _derive_annotations_from_events_tsv(self, raw, events_df):
        if events_df is None or len(events_df) == 0:
            return raw
        onsets = []
        durations = []
        descriptions = []
        for _, row in events_df.iterrows():
            onset = row.get('onset', None)
            duration = row.get('duration', 0.0)
            trial_type = row.get('trial_type', None)
            value = row.get('value', None)
            if pd.isna(onset):
                continue
            if pd.isna(duration):
                duration = 0.0
            desc = None
            if pd.notna(trial_type) and str(trial_type).strip():
                desc = str(trial_type).strip()
            elif pd.notna(value):
                val_str = str(value).strip()
                if val_str == '1':
                    desc = 'event_1'
                elif val_str == '2':
                    desc = 'event_2'
                elif val_str == '3':
                    desc = 'event_3'
                else:
                    desc = val_str
            else:
                desc = 'unknown'
            onsets.append(float(onset))
            durations.append(float(duration))
            descriptions.append(desc)
        if len(onsets) > 0:
            annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
            raw.set_annotations(annot)
        return raw

    def _add_derived_misc_channels(self, raw, events_df, participants_info):
        sfreq = raw.info['sfreq']
        n_samples = len(raw.times)
        
        for channel_name in self.derived_misc_channels:
            if channel_name == 'trial_index':
                # source_field: "events.tsv:trial"
                if events_df is None or 'trial' not in events_df.columns:
                    continue
                
                trial_data = np.zeros((1, n_samples))
                has_valid_trial = False
                
                for _, ev_row in events_df.iterrows():
                    onset = ev_row.get('onset', None)
                    duration = ev_row.get('duration', 6.0)
                    trial_val = ev_row.get('trial', 0)
                    
                    if pd.isna(onset) or pd.isna(trial_val):
                        continue
                    
                    has_valid_trial = True
                    start_idx = int(onset * sfreq)
                    end_idx = int((onset + duration) * sfreq)
                    start_idx = max(0, start_idx)
                    end_idx = min(n_samples, end_idx)
                    
                    if start_idx < n_samples and end_idx > start_idx:
                        trial_data[0, start_idx:end_idx] = float(trial_val)
                
                if not has_valid_trial:
                    continue
                
                info = mne.create_info([channel_name], sfreq=sfreq, ch_types=['misc'])
                misc_raw = mne.io.RawArray(trial_data, info)
                raw.add_channels([misc_raw], force_update_info=True)
        
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)
        if hasattr(raw, 'filenames') and raw.filenames:
            filepath = raw.filenames[0]
        elif hasattr(raw, 'fname') and raw.fname:
            filepath = raw.fname

        bids_root = self._find_bids_root(filepath)
        subject_id = self._get_subject_id(filepath)

        info = self._read_participants_info(bids_root, subject_id)

        age = info.get('age', 'unknown')
        gender = info.get('gender', 'unknown')
        handedness = info.get('handedness', 'unknown')

        if gender.lower() in ['m', 'male']:
            sex = 'male'
        elif gender.lower() in ['f', 'female']:
            sex = 'female'
        else:
            sex = 'unknown'

        original_desc = raw.info.get('description', '') if raw.info.get('description') else ''
        if original_desc is None:
            original_desc = ''

        eegunity_desc = {
            "age": str(age),
            "sex": sex,
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": str(handedness),
        }

        for field in self.required_info_fields:
            if field in info and field not in ['age', 'gender', 'handedness']:
                eegunity_desc[field] = str(info[field])

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })

        raw = self._rename_channels(raw)
        raw = self._set_montage(raw)

        events_tsv_path = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv_path)

        has_native_events = False
        try:
            if hasattr(raw, 'annotations') and raw.annotations is not None and len(raw.annotations) > 0:
                has_native_events = True
            else:
                events, event_id = mne.events_from_annotations(raw)
                if len(events) > 0:
                    has_native_events = True
        except Exception:
            has_native_events = False

        if not has_native_events and events_df is not None:
            raw = self._derive_annotations_from_events_tsv(raw, events_df)

        raw = self._add_derived_misc_channels(raw, events_df, info)

        return raw


KERNEL = OpenneuroDs004448Kernel()