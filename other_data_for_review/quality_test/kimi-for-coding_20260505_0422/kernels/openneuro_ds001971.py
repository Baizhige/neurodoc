import json
import os
import numpy as np
import pandas as pd
import mne


class OpenNeuroDS001971Kernel:
    KERNEL_ID = "openneuro_ds001971"
    KERNEL_NAME = "OpenNeuro ds001971 - Rhythmic Auditory Cueing Gait Adaptation"
    KERNEL_DESCRIPTION = "EEG kernel for rhythmic auditory cueing gait adaptation study with uncued/cued walking heel strike markers"
    KERNEL_CITATION = "10.1038/s41597-019-0223-2"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds001971"

    # BIDS mapping
    required_event_ids = ['100', '101', '103', '109', '113', '114', '119', '151', '153', '159', '171', '200', '201', '271']
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = []

    # Channel renaming map for this dataset
    CHANNEL_RENAME_MAP = {
        'Fpz': 'Fpz',
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'AF3': 'AF3',
        'AF4': 'AF4',
        'AF7': 'AF7',
        'AF8': 'AF8',
        'AFz': 'AFz',
        'F1': 'F1',
        'F2': 'F2',
        'F3': 'F3',
        'F4': 'F4',
        'F5': 'F5',
        'F6': 'F6',
        'F7': 'F7',
        'F8': 'F8',
        'Fz': 'Fz',
        'FC1': 'FC1',
        'FC2': 'FC2',
        'FC3': 'FC3',
        'FC4': 'FC4',
        'FC5': 'FC5',
        'FC6': 'FC6',
        'FCz': 'FCz',
        'FT7': 'FT7',
        'FT8': 'FT8',
        'C1': 'C1',
        'C2': 'C2',
        'C3': 'C3',
        'C4': 'C4',
        'C5': 'C5',
        'C6': 'C6',
        'Cz': 'Cz',
        'CP1': 'CP1',
        'CP2': 'CP2',
        'CP3': 'CP3',
        'CP4': 'CP4',
        'CP5': 'CP5',
        'CP6': 'CP6',
        'CPz': 'CPz',
        'TP7': 'TP7',
        'TP8': 'TP8',
        'P1': 'P1',
        'P2': 'P2',
        'P3': 'P3',
        'P4': 'P4',
        'P5': 'P5',
        'P6': 'P6',
        'P7': 'P7',
        'P8': 'P8',
        'Pz': 'Pz',
        'PO3': 'PO3',
        'PO4': 'PO4',
        'PO7': 'PO7',
        'PO8': 'PO8',
        'POz': 'POz',
        'O1': 'O1',
        'O2': 'O2',
        'Oz': 'Oz',
        'Iz': 'Iz',
        # EMG channels
        'TIBR1': 'TIBR1',
        'TIBR2': 'TIBR2',
        'TIBL1': 'TIBL1',
        'TIBL2': 'TIBL2',
        # Misc/kinematic channels
        'ANKLE': 'ANKLE',
        'HIP': 'HIP',
        'KNEE': 'KNEE',
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find BIDS root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith('ds001971'):
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
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
            # Find subject row
            subj_col = None
            for col in df.columns:
                if col.lower() in ['participant_id', 'subject', 'subject_id']:
                    subj_col = col
                    break
            if subj_col is None:
                # Try first column
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

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            if part.startswith('sub-'):
                return part
        return None

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # For BIDS, events.tsv is in the same directory with same base name
        base = os.path.splitext(eeg_file_path)[0]
        # Handle .eeg (BrainVision) which has .vhdr/.vmrk
        if eeg_file_path.endswith('.eeg'):
            base = os.path.splitext(eeg_file_path)[0]
        elif eeg_file_path.endswith('.set'):
            base = os.path.splitext(eeg_file_path)[0]
        elif eeg_file_path.endswith('.fif'):
            base = os.path.splitext(eeg_file_path)[0]
        elif eeg_file_path.endswith('.edf'):
            base = os.path.splitext(eeg_file_path)[0]

        events_tsv = base + '_events.tsv'
        if os.path.exists(events_tsv):
            return events_tsv

        # Try without run suffix variations
        dir_name = os.path.dirname(eeg_file_path)
        base_name = os.path.basename(base)

        # Look for any events.tsv in same directory matching subject/task
        if os.path.exists(dir_name):
            for f in os.listdir(dir_name):
                if f.endswith('_events.tsv') and f.startswith(base_name.split('_run-')[0] if '_run-' in base_name else base_name):
                    return os.path.join(dir_name, f)

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

    def _events_to_annotations(self, raw, events_df):
        """Convert events DataFrame to mne.Annotations."""
        if events_df is None or len(events_df) == 0:
            return raw

        # Determine onset column
        onset_col = None
        for col in ['onset', 'sample']:
            if col in events_df.columns:
                onset_col = col
                break

        if onset_col is None:
            # Try to find any numeric column that could be onset
            for col in events_df.columns:
                if pd.api.types.is_numeric_dtype(events_df[col]):
                    onset_col = col
                    break

        if onset_col is None:
            return raw

        # Determine duration column
        duration_col = None
        for col in ['duration']:
            if col in events_df.columns:
                duration_col = col
                break

        # Determine description column (event value/trial_type)
        desc_col = None
        for col in ['trial_type', 'value', 'event_id', 'stim_type']:
            if col in events_df.columns:
                desc_col = col
                break

        if desc_col is None:
            # Use first non-onset, non-duration column
            for col in events_df.columns:
                if col not in [onset_col, duration_col]:
                    desc_col = col
                    break

        # Build annotations
        onsets = []
        durations = []
        descriptions = []

        sfreq = raw.info['sfreq']

        for _, row in events_df.iterrows():
            # Skip rows with missing onset
            if pd.isna(row[onset_col]):
                continue

            if onset_col == 'sample':
                onset = float(row[onset_col]) / sfreq
            else:
                onset = float(row[onset_col])

            if duration_col and not pd.isna(row.get(duration_col, np.nan)):
                dur = float(row[duration_col])
            else:
                dur = 0.0

            if desc_col and not pd.isna(row.get(desc_col, np.nan)):
                desc = str(row[desc_col])
            else:
                desc = 'unknown'

            onsets.append(onset)
            durations.append(dur)
            descriptions.append(desc)

        if len(onsets) == 0:
            return raw

        # Remove existing annotations if they are empty or minimal
        # Add new annotations
        annot = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions
        )

        raw.set_annotations(annot)
        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('file_path', '') if hasattr(row, 'get') else str(row)

        # Find BIDS root and participants.tsv
        bids_root = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(bids_root)

        # Get subject ID
        subject_id = self._get_subject_id_from_path(filepath)

        # Read participant info
        participant_info = {}
        if participants_tsv and subject_id:
            participant_info = self._read_participants_info(participants_tsv, subject_id)

        # Ensure age and sex are present
        age = participant_info.get('age', 'unknown')
        sex = participant_info.get('sex', 'unknown')

        # Normalize sex to lowercase
        sex = sex.lower().strip() if sex != 'unknown' else 'unknown'
        if sex in ['m', 'male']:
            sex = 'male'
        elif sex in ['f', 'female']:
            sex = 'female'
        else:
            sex = 'unknown'

        # Build eegunity_description
        eegunity_desc = {
            'age': str(age),
            'sex': sex,
            'amplifier': 'unknown',  # inferred by LLM, needs human review
            'cap': 'unknown',  # inferred by LLM, needs human review
            'handedness': 'unknown',  # inferred by LLM, needs human review
        }

        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_desc and field in participant_info:
                eegunity_desc[field] = str(participant_info[field])

        # Get original description
        original_desc = raw.info.get('description', '') if raw.info.get('description') else ''

        # Set description
        raw.info['description'] = json.dumps({
            'original_description': original_desc,
            'eegunity_description': eegunity_desc
        })

        # Rename channels BEFORE set_montage
        # Get current channel names
        ch_names = raw.ch_names

        # Build rename mapping for channels that need renaming
        rename_map = {}
        for ch in ch_names:
            if ch in self.CHANNEL_RENAME_MAP:
                new_name = self.CHANNEL_RENAME_MAP[ch]
                if new_name != ch:
                    rename_map[ch] = new_name

        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types for known non-EEG channels
        # EMG channels
        emg_channels = ['TIBR1', 'TIBR2', 'TIBL1', 'TIBL2']
        ch_type_map = {}
        for ch in raw.ch_names:
            if ch in emg_channels:
                ch_type_map[ch] = 'emg'
            elif ch in ['ANKLE', 'HIP', 'KNEE']:
                ch_type_map[ch] = 'misc'

        if ch_type_map:
            raw.set_channel_types(ch_type_map)

        # Set montage for EEG channels
        try:
            raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            pass

        # Handle events from events.tsv for EEGLAB .set files that may not have embedded events
        # This dataset uses EEGLAB .set format which may not always have events populated
        events_tsv = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv)

        # Check if raw has meaningful annotations/events
        has_events = False
        if raw.annotations is not None and len(raw.annotations) > 0:
            has_events = True
        try:
            # Try to get events from annotations
            test_events, _ = mne.events_from_annotations(raw, verbose=False)
            if len(test_events) > 0:
                has_events = True
        except Exception:
            pass

        # If no events in raw and we have events.tsv, derive annotations from it
        if not has_events and events_df is not None:
            raw = self._events_to_annotations(raw, events_df)
        elif events_df is not None:
            # Even if raw has some events, ensure we have all from events.tsv
            # Check if the number of annotations matches events.tsv rows
            raw_annot_count = len(raw.annotations) if raw.annotations else 0
            tsv_event_count = len(events_df)

            # If significantly fewer annotations in raw, supplement from events.tsv
            if raw_annot_count < tsv_event_count:
                raw = self._events_to_annotations(raw, events_df)

        # Handle derived misc channels if any
        # (None for this dataset per requirements)

        # Handle native misc channels if any
        # Ensure required native misc channels have correct type
        for misc_ch in self.required_native_misc:
            if misc_ch in raw.ch_names:
                current_type = raw.get_channel_types(picks=[misc_ch])[0] if hasattr(raw, 'get_channel_types') else None
                if current_type != 'misc':
                    raw.set_channel_types({misc_ch: 'misc'})

        return raw


KERNEL = OpenNeuroDS001971Kernel()