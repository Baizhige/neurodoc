import json
import os
import numpy as np
import pandas as pd
import mne


class OpenNeuroDS004447Kernel:
    KERNEL_ID = "openneuro_ds004447"
    KERNEL_NAME = "OpenNeuro ds004447 - SMR-BCI Neurofeedback EEG"
    KERNEL_DESCRIPTION = "EEG kernel for sensorimotor rhythm BCI neurofeedback with rest/task state detection and trial phase classification"
    KERNEL_CITATION = "10.1038/s41597-023-02260-6"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds004447"

    required_event_ids = ['event_1', 'event_2', 'event_3', 'event_4', 'event_5', 'event_6']
    required_info_fields = ['age', 'gender', 'handedness']
    required_native_misc = []
    derived_misc_channels = ['trial_index']

    # Standard 10-20 channel names expected in this dataset
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1', 'Fp2': 'Fp2', 'F3': 'F3', 'F4': 'F4', 'C3': 'C3',
        'C4': 'C4', 'P3': 'P3', 'P4': 'P4', 'O1': 'O1', 'O2': 'O2',
        'F7': 'F7', 'F8': 'F8', 'T7': 'T7', 'T8': 'T8', 'P7': 'P7',
        'P8': 'P8', 'Fz': 'Fz', 'Cz': 'Cz', 'Pz': 'Pz', 'Oz': 'Oz',
        'FC1': 'FC1', 'FC2': 'FC2', 'CP1': 'CP1', 'CP2': 'CP2',
        'FC5': 'FC5', 'FC6': 'FC6', 'CP5': 'CP5', 'CP6': 'CP6',
        'FT9': 'FT9', 'FT10': 'FT10', 'TP9': 'TP9', 'TP10': 'TP10',
        'F1': 'F1', 'F2': 'F2', 'C1': 'C1', 'C2': 'C2', 'P1': 'P1',
        'P2': 'P2', 'AF3': 'AF3', 'AF4': 'AF4', 'FC3': 'FC3',
        'FC4': 'FC4', 'CP3': 'CP3', 'CP4': 'CP4', 'PO3': 'PO3',
        'PO4': 'PO4', 'F5': 'F5', 'F6': 'F6', 'C5': 'C5', 'C6': 'C6',
        'P5': 'P5', 'P6': 'P6', 'AF7': 'AF7', 'AF8': 'AF8',
        'FT7': 'FT7', 'FT8': 'FT8', 'TP7': 'TP7', 'TP8': 'TP8',
        'PO7': 'PO7', 'PO8': 'PO8', 'Fpz': 'Fpz', 'AFz': 'AFz',
        'FCz': 'FCz', 'CPz': 'CPz', 'POz': 'POz', 'Nz': 'Nz', 'Iz': 'Iz',
    }

    def __init__(self):
        pass

    def _get_bids_root(self, raw_path):
        """Extract BIDS root from raw file path."""
        parts = os.path.normpath(raw_path).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith("sub-"):
                return os.sep.join(parts[:i])
        # Fallback
        current = os.path.dirname(raw_path)
        while current != os.sep:
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return None

    def _get_subject_id(self, raw_path):
        """Extract subject ID from file path."""
        parts = os.path.normpath(raw_path).split(os.sep)
        for part in parts:
            if part.startswith("sub-"):
                return part
        return None

    def _read_participants_info(self, bids_root, subject_id):
        """Read subject info from participants.tsv."""
        if bids_root is None:
            return {}
        p_tsv = os.path.join(bids_root, "participants.tsv")
        if not os.path.exists(p_tsv):
            return {}
        try:
            df = pd.read_csv(p_tsv, sep='\t')
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
            if len(subj_rows) == 0 and subject_id.startswith('sub-'):
                alt_id = subject_id[4:]
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

    def _find_events_tsv(self, raw_path):
        """Find sibling events.tsv for the given EEG file."""
        # EDF file: sub-XXX_ses-YY_task-smrbmi_eeg.edf -> events.tsv in same directory
        base = raw_path.replace('_eeg.edf', '_events.tsv')
        if os.path.exists(base):
            return base
        # Try without task
        dir_path = os.path.dirname(raw_path)
        fname = os.path.basename(raw_path)
        # Pattern: sub-001_ses-01_task-smrbmi_eeg.edf
        parts = fname.split('_')
        # Build events filename
        sub_ses = []
        for p in parts:
            if p.startswith('sub-') or p.startswith('ses-'):
                sub_ses.append(p)
            elif p.startswith('task-'):
                sub_ses.append(p)
                break
        if sub_ses:
            events_name = '_'.join(sub_ses) + '_events.tsv'
            alt_path = os.path.join(dir_path, events_name)
            if os.path.exists(alt_path):
                return alt_path
        # List directory
        try:
            for f in os.listdir(dir_path):
                if f.endswith('_events.tsv'):
                    return os.path.join(dir_path, f)
        except Exception:
            pass
        return None

    def _read_events_tsv(self, events_tsv_path):
        """Read events.tsv file."""
        if events_tsv_path is None or not os.path.exists(events_tsv_path):
            return None
        try:
            return pd.read_csv(events_tsv_path, sep='\t')
        except Exception:
            return None

    def _create_annotations_from_events_tsv(self, events_df, raw):
        """Create MNE Annotations from events.tsv dataframe."""
        if events_df is None or len(events_df) == 0:
            return None

        # Required columns: onset, duration, value (or trial_type)
        if 'onset' not in events_df.columns:
            return None

        # Get durations
        if 'duration' in events_df.columns:
            durations = events_df['duration'].fillna(0).astype(float).values
        else:
            durations = np.zeros(len(events_df))

        # Get descriptions - use trial_type if available, else value, else instruction
        if 'trial_type' in events_df.columns:
            descriptions = events_df['trial_type'].astype(str).values
        elif 'value' in events_df.columns:
            descriptions = events_df['value'].astype(str).values
        elif 'instruction' in events_df.columns:
            descriptions = events_df['instruction'].astype(str).values
        else:
            descriptions = np.array(['event'] * len(events_df))

        # Convert onset to seconds - events.tsv onset is in samples for this dataset
        # Based on the data, onset values are large (e.g., 18948) which suggests samples
        # We need to convert using sfreq
        sfreq = raw.info['sfreq']
        onsets_samples = events_df['onset'].astype(float).values
        onsets_sec = onsets_samples / sfreq

        # Create annotations
        annot = mne.Annotations(
            onset=onsets_sec,
            duration=durations,
            description=descriptions
        )
        return annot

    def _map_event_descriptions(self, descriptions):
        """Map raw event descriptions to required event IDs."""
        mapped = []
        for desc in descriptions:
            desc_str = str(desc).strip().lower()
            # Map based on value/trial_type
            if desc_str == '1' or desc_str == 'rest':
                mapped.append('event_1')
            elif desc_str == '2' or desc_str == 'task':
                mapped.append('event_2')
            elif desc_str == '3':
                mapped.append('event_3')
            elif desc_str == '4':
                mapped.append('event_4')
            elif desc_str == '5':
                mapped.append('event_5')
            elif desc_str == '6':
                mapped.append('event_6')
            else:
                # Keep original if no mapping
                mapped.append(str(desc))
        return mapped

    def _create_trial_index_misc(self, raw, events_df):
        """Create trial_index misc channel from events.tsv trial column."""
        if events_df is None or 'trial' not in events_df.columns:
            return raw

        sfreq = raw.info['sfreq']
        n_times = raw.n_times
        trial_data = np.zeros((1, n_times))

        # Get onsets and trial values
        onsets = events_df['onset'].astype(float).values / sfreq
        durations = events_df['duration'].fillna(0).astype(float).values
        trials = events_df['trial'].astype(float).values

        # For each event, set the trial number for the duration of that event
        for onset, duration, trial_val in zip(onsets, durations, trials):
            start_idx = max(0, int(onset * sfreq))
            if duration > 0:
                end_idx = min(n_times, int((onset + duration) * sfreq))
            else:
                # Default to 1 second if no duration
                end_idx = min(n_times, int((onset + 1.0) * sfreq))
            trial_data[0, start_idx:end_idx] = trial_val

        # Create RawArray for trial_index channel
        info = mne.create_info(['trial_index'], sfreq, ch_types=['misc'])
        trial_raw = mne.io.RawArray(trial_data, info, first_samp=raw.first_samp)

        # Add to existing raw
        raw.add_channels([trial_raw], force_update_info=True)

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row - handle both dict and Series
        if hasattr(row, 'get'):
            filepath = row.get('file_path', None)
            if filepath is None and hasattr(row, 'index'):
                # Try to get from index if it's a Series with named index
                if 'file_path' in row.index:
                    filepath = row['file_path']
        elif isinstance(row, dict):
            filepath = row.get('file_path', None)
        else:
            # Last resort: try to_string and parse
            filepath = None

        # Fallback: try to get from raw
        if filepath is None:
            filepath = raw.filenames[0] if raw.filenames else None

        if filepath is None:
            raise ValueError("Cannot determine file path from row or raw")

        # Ensure filepath is string
        filepath = str(filepath)

        # Get BIDS root and subject info
        bids_root = self._get_bids_root(filepath)
        subject_id = self._get_subject_id(filepath)

        # Read participants info
        info_dict = self._read_participants_info(bids_root, subject_id)

        # Build eegunity_description
        eegunity_desc = {}

        # age - always string
        age_val = info_dict.get('age', 'unknown')
        eegunity_desc['age'] = str(age_val) if age_val != 'unknown' else 'unknown'

        # sex - lowercase, map gender to sex
        gender_val = info_dict.get('gender', 'unknown')
        if gender_val.lower() in ['m', 'male']:
            eegunity_desc['sex'] = 'male'
        elif gender_val.lower() in ['f', 'female']:
            eegunity_desc['sex'] = 'female'
        else:
            eegunity_desc['sex'] = 'unknown'

        # handedness
        handedness_val = info_dict.get('handedness', 'unknown')
        eegunity_desc['handedness'] = str(handedness_val) if handedness_val != 'unknown' else 'unknown'

        # amplifier - not in participants, infer from context or omit
        # This dataset uses g.USBamp and g.HIamp based on paper
        eegunity_desc['amplifier'] = 'g.USBamp/g.HIamp'  # inferred by LLM, needs human review

        # cap - standard g.GAMMAcap
        eegunity_desc['cap'] = 'g.GAMMAcap'  # inferred by LLM, needs human review

        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_desc and field in info_dict:
                eegunity_desc[field] = str(info_dict[field])

        # Set description
        original_desc = raw.info.get('description', '')
        raw.info['description'] = json.dumps({
            'original_description': original_desc,
            'eegunity_description': eegunity_desc
        })

        # Channel rename BEFORE set_montage
        current_ch_names = raw.ch_names
        rename_map = {}
        for ch in current_ch_names:
            # Try exact match
            if ch in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch]
            else:
                # Try case-insensitive match
                ch_upper = ch.upper()
                for k, v in self.CHANNEL_RENAME_MAP.items():
                    if k.upper() == ch_upper:
                        rename_map[ch] = v
                        break

        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass

        # Find and read events.tsv
        events_tsv_path = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv_path)

        # Add annotations from events.tsv if raw doesn't have events
        # EDF files typically don't carry triggers, so we need to add from events.tsv
        has_events = False
        try:
            # Check if raw already has annotations with meaningful content
            if raw.annotations is not None and len(raw.annotations) > 0:
                has_events = True
        except Exception:
            pass

        if not has_events and events_df is not None and len(events_df) > 0:
            annot = self._create_annotations_from_events_tsv(events_df, raw)
            if annot is not None:
                # Map descriptions to event IDs
                mapped_descs = self._map_event_descriptions(annot.description)
                annot = mne.Annotations(
                    onset=annot.onset,
                    duration=annot.duration,
                    description=mapped_descs
                )
                raw.set_annotations(annot)

        # Create derived misc channel: trial_index from events.tsv:trial
        if events_df is not None and 'trial' in events_df.columns:
            raw = self._create_trial_index_misc(raw, events_df)

        return raw


KERNEL = OpenNeuroDS004447Kernel()