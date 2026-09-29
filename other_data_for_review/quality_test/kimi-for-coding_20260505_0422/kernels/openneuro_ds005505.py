import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class OpenneuroDs005505Kernel:
    KERNEL_ID = "openneuro_ds005505"
    KERNEL_NAME = "OpenNeuro ds005505 - HBN-EEG Healthy Brain Network EEG"
    KERNEL_DESCRIPTION = "EEG kernel for HBN-EEG dataset with contrast change detection, sequence learning, and resting state tasks"
    KERNEL_CITATION = "10.1101/2024.10.03.615261"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds005505"

    # BIDS mapping
    required_event_ids = ['contrastChangeB1_start', 'contrastChangeB2_start', 'contrastChangeB3_start', 'dot_no1_ON', 'dot_no2_ON', 'dot_no3_ON', 'dot_no4_ON', 'dot_no5_ON', 'dot_no6_ON', 'dot_no7_ON', 'dot_no8_ON', 'instructed_toCloseEyes', 'instructed_toOpenEyes', 'learningBlock_1', 'learningBlock_2', 'learningBlock_3', 'learningBlock_4', 'learningBlock_5', 'left_buttonPress', 'left_target', 'newPage', 'resting_start', 'right_buttonPress', 'right_target', 'seqLearning_start', 'stim_ON', 'surroundSuppB1_start', 'surroundSuppB2_start', 'symbolSearch_start', 'trialResponse', 'video_start']
    required_info_fields = ['age', 'attention', 'ehq_total', 'externalizing', 'full_pheno', 'internalizing', 'p_factor', 'sex']
    required_native_misc = []
    derived_misc_channels = ['accuracy']

    # Channel renaming map for standard 10-20 system used in HBN-EEG
    CHANNEL_RENAME_MAP = {
        'E1': 'Fp1', 'E2': 'AF7', 'E3': 'AF3', 'E4': 'F1', 'E5': 'F3', 'E6': 'F5', 'E7': 'F7', 'E8': 'FT7',
        'E9': 'FC5', 'E10': 'FC3', 'E11': 'FC1', 'E12': 'C1', 'E13': 'C3', 'E14': 'C5', 'E15': 'T7', 'E16': 'TP7',
        'E17': 'CP5', 'E18': 'CP3', 'E19': 'CP1', 'E20': 'P1', 'E21': 'P3', 'E22': 'P5', 'E23': 'P7', 'E24': 'P9',
        'E25': 'PO7', 'E26': 'PO3', 'E27': 'O1', 'E28': 'Iz', 'E29': 'Oz', 'E30': 'POz', 'E31': 'Pz', 'E32': 'CPz',
        'E33': 'Fpz', 'E34': 'Fp2', 'E35': 'AF8', 'E36': 'AF4', 'E37': 'Fz', 'E38': 'F2', 'E39': 'F4', 'E40': 'F6',
        'E41': 'F8', 'E42': 'FT8', 'E43': 'FC6', 'E44': 'FC4', 'E45': 'FC2', 'E46': 'FCz', 'E47': 'Cz', 'E48': 'C2',
        'E49': 'C4', 'E50': 'C6', 'E51': 'T8', 'E52': 'TP8', 'E53': 'CP6', 'E54': 'CP4', 'E55': 'CP2', 'E56': 'P2',
        'E57': 'P4', 'E58': 'P6', 'E59': 'P8', 'E60': 'P10', 'E61': 'PO8', 'E62': 'PO4', 'E63': 'O2', 'E64': 'POz',
        'E65': 'E65', 'E66': 'E66', 'E67': 'E67', 'E68': 'E68', 'E69': 'E69', 'E70': 'E70', 'E71': 'E71', 'E72': 'E72',
        'E73': 'E73', 'E74': 'E74', 'E75': 'E75', 'E76': 'E76', 'E77': 'E77', 'E78': 'E78', 'E79': 'E79', 'E80': 'E80',
        'E81': 'E81', 'E82': 'E82', 'E83': 'E83', 'E84': 'E84', 'E85': 'E85', 'E86': 'E86', 'E87': 'E87', 'E88': 'E88',
        'E89': 'E89', 'E90': 'E90', 'E91': 'E91', 'E92': 'E92', 'E93': 'E93', 'E94': 'E94', 'E95': 'E95', 'E96': 'E96',
        'E97': 'E97', 'E98': 'E98', 'E99': 'E99', 'E100': 'E100', 'E101': 'E101', 'E102': 'E102', 'E103': 'E103', 'E104': 'E104',
        'E105': 'E105', 'E106': 'E106', 'E107': 'E107', 'E108': 'E108', 'E109': 'E109', 'E110': 'E110', 'E111': 'E111', 'E112': 'E112',
        'E113': 'E113', 'E114': 'E114', 'E115': 'E115', 'E116': 'E116', 'E117': 'E117', 'E118': 'E118', 'E119': 'E119', 'E120': 'E120',
        'E121': 'E121', 'E122': 'E122', 'E123': 'E123', 'E124': 'E124', 'E125': 'E125', 'E126': 'E126', 'E127': 'E127', 'E128': 'E128',
        'E129': 'E129', 'VREF': 'VREF', 'REF': 'REF',
    }

    def __init__(self):
        pass

    def _get_bids_root(self, raw_path):
        """Extract BIDS root from raw file path."""
        parts = raw_path.split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith("sub-"):
                return os.sep.join(parts[:i])
        current = os.path.dirname(raw_path)
        while current != os.sep:
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return None

    def _get_subject_id(self, raw_path):
        """Extract subject ID from file path."""
        parts = raw_path.split(os.sep)
        for part in parts:
            if part.startswith("sub-"):
                return part
        return None

    def _find_events_tsv(self, raw_path):
        """Find corresponding events.tsv file for a raw EEG file."""
        # For BIDS, events.tsv is alongside the eeg file with _events.tsv suffix
        base = raw_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.fif", "").replace("_eeg.eeg", "")
        events_tsv = base + "_events.tsv"
        if os.path.exists(events_tsv):
            return events_tsv
        # Try alternative: same directory, replace extension
        dir_name = os.path.dirname(raw_path)
        file_name = os.path.basename(raw_path)
        base_name = file_name.split("_eeg")[0] if "_eeg" in file_name else file_name.rsplit(".", 1)[0]
        events_tsv = os.path.join(dir_name, base_name + "_events.tsv")
        if os.path.exists(events_tsv):
            return events_tsv
        # Look for any events.tsv in same directory
        for f in os.listdir(dir_name) if os.path.exists(dir_name) else []:
            if f.endswith("_events.tsv"):
                return os.path.join(dir_name, f)
        return None

    def _read_participants_info(self, bids_root, subject_id):
        """Read subject info from participants.tsv."""
        if bids_root is None or subject_id is None:
            return {}
        participants_tsv = os.path.join(bids_root, "participants.tsv")
        if not os.path.exists(participants_tsv):
            return {}
        try:
            df = pd.read_csv(participants_tsv, sep="\t")
            # Find subject column
            subj_col = None
            for col in df.columns:
                if col.lower() in ["participant_id", "subject", "subject_id"]:
                    subj_col = col
                    break
            if subj_col is None:
                subj_col = df.columns[0]
            # Match subject
            subj_rows = df[df[subj_col] == subject_id]
            if len(subj_rows) == 0:
                if subject_id.startswith("sub-"):
                    alt_id = subject_id[4:]
                else:
                    alt_id = "sub-" + subject_id
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

    def _read_events_tsv(self, events_tsv):
        """Read events.tsv file."""
        if events_tsv is None or not os.path.exists(events_tsv):
            return None
        try:
            return pd.read_csv(events_tsv, sep="\t")
        except Exception:
            return None

    def _create_accuracy_misc(self, raw, events_df):
        """Create accuracy misc channel from events.tsv trialResponse events."""
        if events_df is None or len(events_df) == 0:
            # Create all-zero accuracy channel if no events
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['accuracy'], raw.info['sfreq'], ['misc'])
            acc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([acc_raw], force_update_info=True)
            return raw

        # Find trialResponse events with user_answer and correct_answer
        trial_mask = events_df['trial_type'].astype(str) == 'trialResponse'
        trial_events = events_df[trial_mask].copy()

        if len(trial_events) == 0:
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['accuracy'], raw.info['sfreq'], ['misc'])
            acc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([acc_raw], force_update_info=True)
            return raw

        # Ensure columns exist
        if 'user_answer' not in trial_events.columns or 'correct_answer' not in trial_events.columns:
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['accuracy'], raw.info['sfreq'], ['misc'])
            acc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([acc_raw], force_update_info=True)
            return raw

        # Compute accuracy for each trialResponse
        try:
            ua = pd.to_numeric(trial_events['user_answer'], errors='coerce')
            ca = pd.to_numeric(trial_events['correct_answer'], errors='coerce')
            trial_events['accuracy'] = (ua == ca).astype(float)
            trial_events['accuracy'] = trial_events['accuracy'].fillna(0.0)
        except Exception:
            data = np.zeros((1, len(raw.times)))
            info = mne.create_info(['accuracy'], raw.info['sfreq'], ['misc'])
            acc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
            raw.add_channels([acc_raw], force_update_info=True)
            return raw

        # Create step function channel: at each trialResponse onset, set accuracy value
        sfreq = raw.info['sfreq']
        n_samples = len(raw.times)
        acc_data = np.zeros((1, n_samples))

        for _, ev in trial_events.iterrows():
            onset = ev.get('onset', None)
            if onset is None or pd.isna(onset):
                continue
            # onset is in seconds
            sample_idx = int(round(float(onset) * sfreq))
            if sample_idx < 0:
                sample_idx = 0
            if sample_idx >= n_samples:
                sample_idx = n_samples - 1
            acc_val = ev.get('accuracy', 0.0)
            if pd.isna(acc_val):
                acc_val = 0.0
            # Set from this sample onward (carry-forward)
            acc_data[0, sample_idx:] = float(acc_val)

        info = mne.create_info(['accuracy'], sfreq, ['misc'])
        acc_raw = mne.io.RawArray(acc_data, info, first_samp=raw.first_samp)
        raw.add_channels([acc_raw], force_update_info=True)
        return raw

    def _add_annotations_from_events_tsv(self, raw, events_df):
        """Add mne.Annotations from events.tsv when raw lacks events."""
        if events_df is None or len(events_df) == 0:
            return raw

        # Check if raw already has meaningful annotations
        try:
            existing_annot = raw.annotations
            has_annot = len(existing_annot) > 0
        except Exception:
            has_annot = False

        # Also check if events can be extracted
        try:
            events, event_id = mne.events_from_annotations(raw)
            has_events = len(events) > 0
        except Exception:
            has_events = False

        # If raw already has events/annotations, keep them
        if has_annot and has_events:
            return raw

        # Build annotations from events.tsv
        onsets = []
        durations = []
        descriptions = []

        for _, row in events_df.iterrows():
            onset = row.get('onset', None)
            if onset is None or pd.isna(onset):
                continue
            duration = row.get('duration', 0.0)
            if pd.isna(duration):
                duration = 0.0

            # Use trial_type if available, else value, else description
            desc = None
            for col in ['trial_type', 'value', 'description', 'event_type']:
                if col in row and pd.notna(row[col]):
                    desc = str(row[col])
                    break
            if desc is None:
                continue

            onsets.append(float(onset))
            durations.append(float(duration))
            descriptions.append(desc)

        if len(onsets) == 0:
            return raw

        # Remove existing empty annotations if any, then add new
        try:
            raw.set_annotations(mne.Annotations(onsets, durations, descriptions))
        except Exception:
            pass

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path
        filepath = row.get('file_path', None)
        if filepath is None:
            filepath = row.get('Raw file', None)
        if filepath is None:
            # Try to get from udataset
            try:
                filepath = udataset.get_raw_path(row)
            except Exception:
                pass

        # BIDS root and subject info
        bids_root = None
        subject_id = None
        if filepath:
            bids_root = self._get_bids_root(filepath)
            subject_id = self._get_subject_id(filepath)

        # Read participants info
        participants_info = self._read_participants_info(bids_root, subject_id)

        # Read events.tsv
        events_tsv = None
        events_df = None
        if filepath:
            events_tsv = self._find_events_tsv(filepath)
            events_df = self._read_events_tsv(events_tsv)

        # Channel renaming
        ch_names = raw.ch_names
        rename_map = {}
        for ch in ch_names:
            if ch in self.CHANNEL_RENAME_MAP:
                rename_map[ch] = self.CHANNEL_RENAME_MAP[ch]
        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage if not already set
        try:
            if raw.get_montage() is None:
                raw.set_montage('standard_1020', match_case=False, on_missing='warn')
        except Exception:
            try:
                raw.set_montage('standard_1005', match_case=False, on_missing='warn')
            except Exception:
                pass

        # Add annotations from events.tsv if raw lacks events
        raw = self._add_annotations_from_events_tsv(raw, events_df)

        # Create derived accuracy misc channel
        raw = self._create_accuracy_misc(raw, events_df)

        # Ensure accuracy channel is misc type
        if 'accuracy' in raw.ch_names:
            try:
                current_types = raw.get_channel_types(picks=['accuracy'])
                if current_types != ['misc']:
                    raw.set_channel_types({'accuracy': 'misc'})
            except Exception:
                pass

        # Build eegunity_description with all required fields
        eegunity_desc = {
            "age": participants_info.get('age', 'unknown'),
            "sex": participants_info.get('sex', 'unknown').lower() if participants_info.get('sex') else 'unknown',
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }

        # Add all required info fields from participants.tsv
        for field in self.required_info_fields:
            if field in participants_info and field not in ['age', 'sex']:
                eegunity_desc[field] = participants_info[field]
            elif field not in ['age', 'sex']:
                eegunity_desc[field] = "unknown"

        # Handle original description
        original_desc = ""
        try:
            original_desc = raw.info.get('description', '') or ''
        except Exception:
            pass

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc
        })

        return raw


KERNEL = OpenneuroDs005505Kernel()