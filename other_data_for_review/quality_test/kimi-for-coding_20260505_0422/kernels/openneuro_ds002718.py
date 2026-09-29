import json
import os
import numpy as np
import pandas as pd
import mne
from mne import create_info, Annotations
from mne.io import RawArray


class OpenneuroDs002718Kernel:
    KERNEL_ID = "openneuro_ds002718"
    KERNEL_NAME = "OpenNeuro ds002718 - Face Recognition EEG"
    KERNEL_DESCRIPTION = "EEG kernel for face recognition study with famous, unfamiliar, and scrambled faces"
    KERNEL_CITATION = "10.18112/openneuro.ds002718.v1.1.0"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds002718"

    required_event_ids = [
        'famous_new', 'famous_second_early', 'famous_second_late',
        'left_nonsym', 'left_sym', 'right_nonsym', 'right_sym',
        'scrambled_new', 'scrambled_second_early', 'scrambled_second_late',
        'unfamiliar_new', 'unfamiliar_second_early', 'unfamiliar_second_late'
    ]
    required_info_fields = ['age', 'gender']
    required_native_misc = []
    derived_misc_channels = ['event_order_misc', 'trial_dist_misc', 'time_dist_misc']

    def __init__(self):
        pass

    def _get_bids_root(self, filepath):
        """Find BIDS root from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('ds002718'):
                return os.sep.join(parts[:i+1])
        # Fallback: find 'sub-' and go up one level
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                if i > 0:
                    return os.sep.join(parts[:i])
                else:
                    return os.sep.join(parts[:i+1])
        return None

    def _get_subject_id(self, filepath):
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

    def _read_participants_info(self, participants_tsv, subject_id):
        """Read subject info from participants.tsv."""
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
                # Try alternative format
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
        """Find corresponding events.tsv file."""
        # For .set files, events.tsv is in same directory with task name
        base = filepath.replace('.set', '').replace('.edf', '').replace('.eeg', '').replace('.fif', '').replace('.vhdr', '')
        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try without suffix stripping for BIDS naming
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        # Remove extension
        base_no_ext = basename.split('.')[0]
        events_tsv = os.path.join(dirname, base_no_ext + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
            
        # Try task-specific pattern
        parts = base_no_ext.split('_')
        if len(parts) >= 2:
            # Look for any events.tsv in same directory
            for f in os.listdir(dirname):
                if f.endswith('_events.tsv'):
                    return os.path.join(dirname, f)
        return None

    def _read_events_tsv(self, events_tsv):
        """Read events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        try:
            df = pd.read_csv(events_tsv, sep='\t')
            return df
        except Exception:
            return None

    def _create_misc_channel_from_events(self, raw, events_df, column_name, channel_name):
        """Create a misc channel from events.tsv column values."""
        if events_df is None or column_name not in events_df.columns:
            # Skip if source not available - do not fabricate data
            return raw

        # Build a step function: at each event onset, set value from events.tsv
        sfreq = raw.info['sfreq']
        n_times = len(raw.times)
        misc_data = np.zeros(n_times)

        for _, event_row in events_df.iterrows():
            onset = event_row.get('onset', None)
            if onset is None or pd.isna(onset):
                continue
            # Convert onset to sample index
            sample_idx = int(float(onset) * sfreq)
            if sample_idx < 0:
                sample_idx = 0
            if sample_idx >= n_times:
                continue
            
            val = event_row.get(column_name, 0)
            if pd.isna(val):
                val = 0
            else:
                val = float(val)
            
            # Set value from this sample onward (carry-forward)
            misc_data[sample_idx:] = val

        # Add as new channel
        data = misc_data.reshape(1, -1)
        info = create_info([channel_name], sfreq, ['misc'])
        misc_raw = RawArray(data, info, first_samp=raw.first_samp, verbose=False)
        raw.add_channels([misc_raw], force_update_info=True)
        return raw

    def _add_annotations_from_events_tsv(self, raw, events_df):
        """Add annotations from events.tsv to raw."""
        if events_df is None:
            return raw

        # Check if raw already has meaningful annotations/events
        # EEGLAB .set files may or may not have events; we ensure annotations from events.tsv
        
        onsets = []
        durations = []
        descriptions = []

        for _, row in events_df.iterrows():
            onset = row.get('onset', None)
            if onset is None or pd.isna(onset):
                continue
            
            duration = row.get('duration', 0)
            if pd.isna(duration):
                duration = 0
            
            # Use trial_type if available, else value, else description
            desc = None
            for col in ['trial_type', 'value', 'description']:
                if col in row and pd.notna(row[col]):
                    desc = str(row[col])
                    break
            
            if desc is None:
                continue

            onsets.append(float(onset))
            durations.append(float(duration) if duration else 0.0)
            descriptions.append(desc)

        if len(onsets) == 0:
            return raw

        # Create annotations
        annot = Annotations(onset=onsets, duration=durations, description=descriptions)
        
        # Check existing annotations
        if raw.annotations is None or len(raw.annotations) == 0:
            raw.set_annotations(annot)
        else:
            # Merge annotations
            all_onsets = list(raw.annotations.onset) + onsets
            all_durations = list(raw.annotations.duration) + durations
            all_descriptions = list(raw.annotations.description) + descriptions
            
            # Sort by onset
            sorted_idx = np.argsort(all_onsets)
            merged_annot = Annotations(
                onset=[all_onsets[i] for i in sorted_idx],
                duration=[all_durations[i] for i in sorted_idx],
                description=[all_descriptions[i] for i in sorted_idx]
            )
            raw.set_annotations(merged_annot)

        return raw

    def _rename_channels(self, raw):
        """Rename channels to standard 10-20 naming if needed."""
        # Get current channel names
        ch_names = raw.ch_names
        
        # Check if channels need renaming (EEGLAB often has standard names already)
        rename_map = {}
        for ch in ch_names:
            # Handle EOG/ECG channels
            if ch in ['EEG061', 'HEOG', 'HEOGL', 'HEOGR', 'hEOG']:
                rename_map[ch] = 'HEOG'
            elif ch in ['EEG062', 'VEOG', 'VEOGL', 'VEOGR', 'vEOG']:
                rename_map[ch] = 'VEOG'
            elif ch in ['EEG063', 'ECG', 'EKG']:
                rename_map[ch] = 'ECG'
            elif ch == 'EEG064':
                rename_map[ch] = 'MISC'
            else:
                # Keep EEG channels as-is (they should already be 10-20 names)
                pass
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for EOG/ECG
        ch_types = {}
        for ch in raw.ch_names:
            if ch in ['HEOG', 'VEOG']:
                ch_types[ch] = 'eog'
            elif ch in ['ECG', 'EKG']:
                ch_types[ch] = 'ecg'
            elif ch == 'MISC':
                ch_types[ch] = 'misc'
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage."""
        # Try to set standard_1020 montage
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            # Pick only channels that exist in both raw and montage
            raw_ch_names = set(raw.ch_names)
            montage_ch_names = set(montage.ch_names)
            common = list(raw_ch_names & montage_ch_names)
            
            if len(common) > 0:
                raw.set_montage(montage, on_missing='ignore')
        except Exception:
            pass
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row - handle both dict-like and Series
        filepath = None
        if hasattr(row, 'get'):
            # dict-like
            for key in ['file_path', 'filepath', 'path', 'filename']:
                if key in row:
                    filepath = row[key]
                    break
        elif hasattr(row, 'iloc'):
            # pandas Series - try by position or index name
            if hasattr(row, 'index'):
                for key in ['file_path', 'filepath', 'path', 'filename']:
                    if key in row.index:
                        filepath = row[key]
                        break
            if filepath is None and len(row) > 0:
                # Try first element as fallback
                filepath = str(row.iloc[0]) if hasattr(row, 'iloc') else str(row[0])
        else:
            # Last resort: convert to dict
            try:
                row_dict = dict(row)
                for key in ['file_path', 'filepath', 'path', 'filename']:
                    if key in row_dict:
                        filepath = row_dict[key]
                        break
            except Exception:
                pass
        
        if filepath is None:
            # Cannot proceed without filepath
            return raw

        # Find BIDS root and subject info
        bids_root = self._get_bids_root(filepath)
        subject_id = self._get_subject_id(filepath)
        
        # Read participants info for metadata
        participants_tsv = self._find_participants_tsv(bids_root)
        subject_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Set subject info in raw.info if available
        if subject_info:
            # Map gender to sex for MNE
            sex = subject_info.get('gender', 'unknown')
            if sex.lower() in ['m', 'male']:
                sex_code = 1
            elif sex.lower() in ['f', 'female']:
                sex_code = 2
            else:
                sex_code = 0
            
            # Parse age
            age_str = subject_info.get('age', 'unknown')
            try:
                age = float(age_str)
            except (ValueError, TypeError):
                age = None
            
            # Create eegunity_description dict
            eegunity_description = {
                'age': str(int(age)) if age is not None else 'unknown',
                'sex': sex,
                'amplifier': 'unknown',
                'cap': 'unknown',
                'handedness': 'unknown'
            }
            
            # Store in raw.info['description'] as JSON
            if raw.info.get('description') is None:
                raw.info['description'] = json.dumps({'eegunity_description': eegunity_description})
            else:
                try:
                    existing = json.loads(raw.info['description'])
                    existing['eegunity_description'] = eegunity_description
                    raw.info['description'] = json.dumps(existing)
                except Exception:
                    raw.info['description'] = json.dumps({'eegunity_description': eegunity_description})

        # Find and read events.tsv
        events_tsv = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv)

        # Add annotations from events.tsv
        raw = self._add_annotations_from_events_tsv(raw, events_df)

        # Rename channels if needed
        raw = self._rename_channels(raw)

        # Set montage
        raw = self._set_montage(raw)

        # Create derived misc channels from events.tsv
        # event_order_misc from events.tsv:event_order
        raw = self._create_misc_channel_from_events(raw, events_df, 'event_order', 'event_order_misc')
        
        # trial_dist_misc from events.tsv:trial_dist
        raw = self._create_misc_channel_from_events(raw, events_df, 'trial_dist', 'trial_dist_misc')
        
        # time_dist_misc from events.tsv:time_dist
        raw = self._create_misc_channel_from_events(raw, events_df, 'time_dist', 'time_dist_misc')

        return raw


KERNEL = OpenneuroDs002718Kernel()