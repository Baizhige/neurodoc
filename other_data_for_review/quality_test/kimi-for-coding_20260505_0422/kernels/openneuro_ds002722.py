import json
import os
import numpy as np
import pandas as pd
import mne


class OpenNeuroDS002722Kernel:
    KERNEL_ID = "openneuro_ds002722"
    KERNEL_NAME = "OpenNeuro ds002722 - Affective Music Listening BCMI-MIdAS"
    KERNEL_DESCRIPTION = "EEG kernel for 9-class valence-arousal affective music listening with BCMI-MIdAS dataset"
    KERNEL_CITATION = "10.1038/s41597-020-0507-6"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds002722"

    required_event_ids = ['1', '101-209', '2', '3', '4', '5', '6', '7', '8', '9']
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = []

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('ds002722'):
                return os.sep.join(parts[:i + 1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        return None

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        p_tsv = os.path.join(bids_root, 'participants.tsv')
        if os.path.exists(p_tsv):
            return p_tsv
        return None

    def _read_participants_info(self, bids_root, subject_id):
        """Read subject info from participants.tsv."""
        participants_tsv = self._find_participants_tsv(bids_root)
        if participants_tsv is None or not os.path.exists(participants_tsv):
            return {}
        try:
            df = pd.read_csv(participants_tsv, sep='\t')
            # Find subject column
            subj_col = None
            for col in df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]

            # Match subject
            subj_rows = df[df[subj_col] == subject_id]
            if len(subj_rows) == 0:
                # Try without 'sub-' prefix
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

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # BIDS naming: sub-X_task-Y_eeg.edf -> sub-X_task-Y_events.tsv
        base = os.path.splitext(eeg_file_path)[0]
        # Handle potential .eeg or .edf extensions
        # Remove any _eeg suffix first, then add _events
        if base.endswith('_eeg'):
            base = base[:-4]
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv

        # Try with _eeg suffix kept
        base = os.path.splitext(eeg_file_path)[0]
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv

        # Try in same directory with glob pattern
        dirname = os.path.dirname(eeg_file_path)
        basename = os.path.basename(base)
        # Remove _eeg if present for pattern matching
        if basename.endswith('_eeg'):
            basename = basename[:-4]
        
        # Look for any matching events file
        if os.path.isdir(dirname):
            for f in os.listdir(dirname):
                if f.endswith('_events.tsv') and basename in f:
                    return os.path.join(dirname, f)

        return None

    def _read_events_tsv(self, events_tsv):
        """Read events from events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            return df
        except Exception:
            return None

    def _add_annotations_from_events_tsv(self, raw, events_df):
        """Add annotations from events.tsv DataFrame."""
        if events_df is None or len(events_df) == 0:
            return raw

        # Check required columns
        if 'onset' not in events_df.columns:
            return raw

        onsets = []
        durations = []
        descriptions = []

        for _, row in events_df.iterrows():
            onset = float(row['onset'])
            duration = float(row['duration']) if 'duration' in row and pd.notna(row['duration']) else 0.0
            if duration <= 0:
                duration = 0.0

            # Use trial_type if available, else value, else event_id
            # For this dataset, trial_type contains the event labels we need
            if 'trial_type' in row and pd.notna(row['trial_type']):
                desc = str(int(float(row['trial_type']))) if str(row['trial_type']).replace('.','',1).isdigit() else str(row['trial_type'])
            elif 'value' in row and pd.notna(row['value']):
                desc = str(int(float(row['value']))) if str(row['value']).replace('.','',1).isdigit() else str(row['value'])
            elif 'event_id' in row and pd.notna(row['event_id']):
                desc = str(int(float(row['event_id']))) if str(row['event_id']).replace('.','',1).isdigit() else str(row['event_id'])
            else:
                desc = 'unknown'

            onsets.append(onset)
            durations.append(duration)
            descriptions.append(desc)

        if len(onsets) > 0:
            # Create new annotations, replacing any existing
            annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
            raw.set_annotations(annot)

        return raw

    def _get_standard_1020_channels(self):
        """Return standard 10-20 channel names."""
        return [
            'Fp1', 'Fpz', 'Fp2', 'AF7', 'AF3', 'AFz', 'AF4', 'AF8',
            'F7', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6', 'F8',
            'FT7', 'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6', 'FT8',
            'T7', 'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6', 'T8',
            'TP7', 'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6', 'TP8',
            'P7', 'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6', 'P8',
            'PO7', 'PO3', 'POz', 'PO4', 'PO8', 'O1', 'Oz', 'O2',
            'A1', 'A2', 'M1', 'M2', 'TP9', 'TP10', 'P9', 'P10',
            'EOG', 'VEOG', 'HEOG', 'ECG', 'EMG', 'RESP'
        ]

    def _standardize_channel_names(self, raw):
        """Standardize channel names to 10-20 naming."""
        ch_names = raw.ch_names
        rename_map = {}

        standard_chs = self._get_standard_1020_channels()

        for ch in ch_names:
            ch_clean = ch.strip()
            # Direct match
            if ch_clean in standard_chs:
                rename_map[ch] = ch_clean
                continue

            # Common variations
            upper = ch_clean.upper()
            if upper in [c.upper() for c in standard_chs]:
                for std in standard_chs:
                    if std.upper() == upper:
                        rename_map[ch] = std
                        break
                continue

            # Handle EOG variations
            if 'EOG' in upper or 'EYE' in upper:
                if any(x in upper for x in ['V', 'UP', 'DOWN', 'VERT']):
                    rename_map[ch] = 'VEOG'
                elif any(x in upper for x in ['H', 'LAT', 'HOR']):
                    rename_map[ch] = 'HEOG'
                else:
                    rename_map[ch] = 'EOG'
                continue

            # Handle ECG variations
            if any(x in upper for x in ['ECG', 'EKG', 'HEART']):
                rename_map[ch] = 'ECG'
                continue

            # Handle EMG variations
            if 'EMG' in upper:
                rename_map[ch] = 'EMG'
                continue

            # Handle mastoid/reference variations
            if ch_clean in ['A1', 'A2', 'M1', 'M2', 'TP9', 'TP10', 'P9', 'P10',
                           'REF', 'REFERENCE', 'CzREF', 'Cz_REF']:
                if '1' in ch_clean or '9' in ch_clean:
                    rename_map[ch] = 'M1'
                elif '2' in ch_clean or '10' in ch_clean:
                    rename_map[ch] = 'M2'
                else:
                    rename_map[ch] = 'M1'  # default
                continue

            # Try to match by removing common prefixes/suffixes
            cleaned = ch_clean
            for prefix in ['EEG ', 'EEG', 'E ', 'E']:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
                    break

            # Check if cleaned version matches standard
            if cleaned in standard_chs:
                rename_map[ch] = cleaned
            elif cleaned.upper() in [c.upper() for c in standard_chs]:
                for std in standard_chs:
                    if std.upper() == cleaned.upper():
                        rename_map[ch] = std
                        break

        if rename_map:
            raw = raw.rename_channels(rename_map)

        return raw

    def _set_channel_types(self, raw):
        """Set appropriate channel types."""
        ch_types = {}
        for ch in raw.ch_names:
            upper = ch.upper()
            if ch in ['VEOG', 'HEOG', 'EOG']:
                ch_types[ch] = 'eog'
            elif ch == 'ECG':
                ch_types[ch] = 'ecg'
            elif ch == 'EMG':
                ch_types[ch] = 'emg'
            elif ch in ['M1', 'M2', 'A1', 'A2', 'TP9', 'TP10', 'P9', 'P10']:
                ch_types[ch] = 'misc'
            elif 'REF' in upper:
                ch_types[ch] = 'misc'
            elif ch in ['RESP', 'RESP1', 'RESP2']:
                ch_types[ch] = 'misc'

        if ch_types:
            raw.set_channel_types(ch_types)

        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage."""
        try:
            raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            try:
                raw.set_montage('standard_1020', match_case=False, on_missing='warn')
            except Exception:
                pass
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('File Path', '') if hasattr(row, 'get') else str(row)

        # Find BIDS root and subject ID
        bids_root = self._find_bids_root(filepath)
        subject_id = self._get_subject_id_from_path(filepath)

        # Read participants info
        participants_info = self._read_participants_info(bids_root, subject_id)

        # Ensure age and sex are present
        age = participants_info.get('age', 'unknown')
        sex = participants_info.get('sex', 'unknown')

        # Standardize sex to lowercase
        sex = sex.lower().strip() if sex != 'unknown' else 'unknown'
        if sex not in ['male', 'female', 'unknown']:
            if sex in ['m', '1']:
                sex = 'male'
            elif sex in ['f', '2']:
                sex = 'female'
            else:
                sex = 'unknown'

        # Build eegunity_description with required fields
        eegunity_description = {
            "age": str(age),
            "sex": sex,
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
            "dataset": self.KERNEL_ID,
            "task": "affective music listening"
        }

        # Standardize channel names and types
        raw = self._standardize_channel_names(raw)
        raw = self._set_channel_types(raw)
        raw = self._set_montage(raw)

        # Find and add events from events.tsv
        events_tsv = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv)
        raw = self._add_annotations_from_events_tsv(raw, events_df)

        # Store eegunity_description in raw.info['description'] as JSON
        existing_desc = raw.info.get('description', '')
        if existing_desc is None:
            existing_desc = ''
        
        # Merge any existing description
        try:
            existing_json = json.loads(existing_desc) if existing_desc.strip() else {}
            if isinstance(existing_json, dict):
                existing_json.update(eegunity_description)
                raw.info['description'] = json.dumps(existing_json)
            else:
                eegunity_description['_original_description'] = str(existing_desc)
                raw.info['description'] = json.dumps(eegunity_description)
        except (json.JSONDecodeError, ValueError):
            eegunity_description['_original_description'] = str(existing_desc)
            raw.info['description'] = json.dumps(eegunity_description)

        return raw


KERNEL = OpenNeuroDS002722Kernel()