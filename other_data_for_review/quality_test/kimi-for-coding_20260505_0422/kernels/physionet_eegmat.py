import json
import os
import numpy as np
import pandas as pd
import mne


class PhysionetEegmatKernel:
    KERNEL_ID = "physionet_eegmat"
    KERNEL_NAME = "PhysioNet EEGMAT - Rest vs Mental Arithmetic"
    KERNEL_DESCRIPTION = "EEG kernel for rest baseline vs mental arithmetic task classification. Each subject has two EDF files: _1 (rest) and _2 (mental arithmetic)."
    KERNEL_CITATION = "10.13026/C2JQ1P"
    KERNEL_LICENSE = "ODC-By"
    KERNEL_URL = "https://physionet.org/content/eegmat/1.0.0/"

    required_event_ids = ['mental_arithmetic', 'rest_baseline']
    required_info_fields = ['Count quality']
    required_native_misc = []
    derived_misc_channels = []

    # Standard 10-20 channel names for this dataset
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F3': 'F3',
        'F4': 'F4',
        'C3': 'C3',
        'C4': 'C4',
        'P3': 'P3',
        'P4': 'P4',
        'O1': 'O1',
        'O2': 'O2',
        'F7': 'F7',
        'F8': 'F8',
        'T3': 'T7',
        'T4': 'T8',
        'T5': 'P7',
        'T6': 'P8',
        'Fz': 'Fz',
        'Cz': 'Cz',
        'Pz': 'Pz',
        'A2-A1': 'A2',  # Reference channel, will be set as misc
    }

    def __init__(self):
        pass

    def _find_bids_root(self, filepath):
        """Find dataset root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if 'eegmat' in part.lower():
                return os.sep.join(parts[:i+1])
        # Fallback: look for 'sub-' pattern or go up to find participants.tsv
        for i, part in enumerate(parts):
            if part.startswith('sub-'):
                return os.sep.join(parts[:i])
        return None

    def _find_participants_tsv(self, root_dir):
        """Find participants.tsv file."""
        if root_dir is None:
            return None
        p_tsv = os.path.join(root_dir, 'participants.tsv')
        if os.path.exists(p_tsv):
            return p_tsv
        # Try one level up
        parent = os.path.dirname(root_dir)
        if parent:
            p_tsv = os.path.join(parent, 'participants.tsv')
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
        # Fallback: extract from filename
        basename = os.path.basename(filepath)
        # Files are like Subject00_1.edf, Subject00_2.edf
        if basename.startswith('Subject'):
            # Extract SubjectXX part
            subj_part = basename.split('_')[0]
            return 'sub-' + subj_part
        return None

    def _get_condition_from_filename(self, filepath):
        """Determine condition from filename suffix.
        _1 = rest_baseline, _2 = mental_arithmetic
        """
        basename = os.path.basename(filepath)
        name_no_ext = os.path.splitext(basename)[0]
        if name_no_ext.endswith('_1'):
            return 'rest_baseline'
        elif name_no_ext.endswith('_2'):
            return 'mental_arithmetic'
        return None

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get filepath from row using .get() to handle missing key
        filepath = row.get('file_path', None)
        if filepath is None:
            # Try alternative column names that might be present
            for key in ['filepath', 'path', 'filename', 'file_name']:
                if key in row:
                    filepath = row[key]
                    break
        # Fallback: use raw.filenames if available
        if filepath is None and hasattr(raw, 'filenames') and raw.filenames:
            filepath = raw.filenames[0]
        if filepath is None:
            filepath = "unknown"

        basename = os.path.basename(filepath) if filepath != "unknown" else "unknown"

        # Get subject ID
        subject_id = self._get_subject_id_from_path(filepath)
        if subject_id is None:
            subject_id = "unknown"

        # Find BIDS root and participants.tsv
        root_dir = self._find_bids_root(filepath)
        participants_tsv = self._find_participants_tsv(root_dir)

        # Read participants info
        participants_info = self._read_participants_info(participants_tsv, subject_id)

        # Determine condition from filename
        condition = self._get_condition_from_filename(filepath)

        # Get original description
        original_description = raw.info.get('description', '') or ''

        # Build description with required info fields
        eegunity_description = {
            "age": "unknown",  # not available in this dataset
            "sex": "unknown",  # not available in this dataset
            "amplifier": "unknown",  # inferred by LLM, needs human review
            "cap": "unknown",  # inferred by LLM, needs human review
            "handedness": "unknown",  # not available in this dataset
        }

        # Add required info fields from participants.tsv
        for field in self.required_info_fields:
            eegunity_description[field] = participants_info.get(field, "unknown")

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description
        })

        # Rename channels before set_montage
        # Map T3/T4/T5/T6 to T7/T8/P7/P8 for standard 10-20
        rename_map = {}
        for old_name in raw.ch_names:
            if old_name in self.CHANNEL_RENAME_MAP:
                new_name = self.CHANNEL_RENAME_MAP[old_name]
                if new_name != old_name:
                    rename_map[old_name] = new_name

        if rename_map:
            raw.rename_channels(rename_map)

        # Handle A2-A1 reference channel - set as misc
        if 'A2' in raw.ch_names:
            raw.set_channel_types({'A2': 'misc'})

        # Set standard 10-20 montage for EEG channels
        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
        if len(eeg_picks) > 0:
            try:
                montage = mne.channels.make_standard_montage('standard_1020')
                # Only set channels that exist in montage
                ch_names = [raw.ch_names[i] for i in eeg_picks]
                montage_chs = set(montage.ch_names)
                available_chs = [c for c in ch_names if c in montage_chs]
                if available_chs:
                    raw.set_montage(montage, on_missing='ignore')
            except Exception:
                pass

        # Create synthetic annotation for the entire recording based on condition
        # The dataset uses separate files per condition, so we create one long event
        if condition in self.required_event_ids:
            # Create annotation spanning the entire recording
            onset = 0.0
            duration = raw.times[-1] if len(raw.times) > 0 else 0.0
            description = condition
            annot = mne.Annotations(onset=[onset], duration=[duration], description=[description])
            raw.set_annotations(annot)

        # Add derived misc channels if specified
        for misc_ch in self.derived_misc_channels:
            # Create constant broadcast channel from participants info if available
            if misc_ch in participants_info:
                val = float(participants_info[misc_ch]) if participants_info[misc_ch].replace('.', '', 1).isdigit() else 1.0
            else:
                val = 1.0
            data = np.full((1, len(raw.times)), val)
            info_misc = mne.create_info([misc_ch], raw.info['sfreq'], ['misc'])
            raw_misc = mne.io.RawArray(data, info_misc)
            raw.add_channels([raw_misc], force_update_info=True)

        return raw


KERNEL = PhysionetEegmatKernel()