import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class OpenneuroDs003810Kernel:
    KERNEL_ID = "openneuro_ds003810"
    KERNEL_NAME = "OpenNeuro ds003810 - Motor Imagery vs Rest with Low-Cost EEG"
    KERNEL_DESCRIPTION = "EEG kernel for motor imagery vs rest classification using low-cost consumer-grade BCI system. Modified Graz protocol with right hand grasping MI and rest/idle conditions."
    KERNEL_CITATION = "10.1016/j.heliyon.2020.e03425"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds003810"

    # BIDS mapping
    required_event_ids = ['OVTK_GDF_Right', 'OVTK_GDF_Tongue']
    required_info_fields = ['age', 'gender']
    required_native_misc = []
    derived_misc_channels = []

    # Channel renaming map for this dataset (14 channels + 1 reference based on dataset docs)
    CHANNEL_RENAME_MAP = {
        'Fp1': 'Fp1',
        'Fp2': 'Fp2',
        'F7': 'F7',
        'F3': 'F3',
        'Fz': 'Fz',
        'F4': 'F4',
        'F8': 'F8',
        'T3': 'T7',  # T3 -> T7 (10-20 equivalent)
        'C3': 'C3',
        'Cz': 'Cz',
        'C4': 'C4',
        'T4': 'T8',  # T4 -> T8 (10-20 equivalent)
        'T5': 'P7',  # T5 -> P7 (10-20 equivalent)
        'P3': 'P3',
        'Pz': 'Pz',
        'P4': 'P4',
        'T6': 'P8',  # T6 -> P8 (10-20 equivalent)
        'O1': 'O1',
        'O2': 'O2',
        'A2': 'A2',  # Reference/ear electrode
        'A1': 'A1',  # Reference/ear electrode
        'Ref': 'Ref',
        'REF': 'REF',
    }

    def __init__(self):
        pass

    def _get_bids_root(self, raw_path):
        """Extract BIDS root from raw file path."""
        parts = os.path.normpath(raw_path).split(os.sep)
        for i, part in enumerate(parts):
            if part.startswith("sub-"):
                return os.sep.join(parts[:i])
        # Fallback: go up until we find participants.tsv
        current = os.path.dirname(raw_path)
        while current != os.sep:
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            current = os.path.dirname(current)
        return None

    def _get_subject_id(self, raw_path):
        """Extract subject ID from raw file path."""
        parts = os.path.normpath(raw_path).split(os.sep)
        for part in parts:
            if part.startswith("sub-"):
                return part
        return None

    def _read_participants_info(self, bids_root, subject_id):
        """Read subject info from participants.tsv."""
        if bid_root is None:
            return {}
        participants_tsv = os.path.join(bids_root, "participants.tsv")
        if not os.path.exists(participants_tsv):
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

    def _find_events_tsv(self, eeg_file_path):
        """Find corresponding events.tsv file for an EEG file."""
        # BIDS naming: sub-X_task-Y_run-Z_eeg.edf -> sub-X_task-Y_run-Z_events.tsv
        base = eeg_file_path.replace('_eeg.edf', '_events.tsv')
        base = base.replace('_eeg.set', '_events.tsv')
        base = base.replace('_eeg.vhdr', '_events.tsv')
        base = base.replace('_eeg.fif', '_events.tsv')
        if os.path.exists(base):
            return base
        # Try without run
        base_no_run = base.replace('_run-1', '').replace('_run-2', '').replace('_run-3', '').replace('_run-4', '')
        if os.path.exists(base_no_run):
            return base_no_run
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

    def _map_event_value_to_name(self, value):
        """Map event value to event name based on task-MIvsRest_events.json mapping."""
        # From task-MIvsRest_events.json: 770=MI, 772=Rest
        # OVTK_GDF_Right (value 102) = MI cue, OVTK_GDF_Tongue (value 107) = Rest cue
        value_map = {
            '770': 'OVTK_GDF_Right',  # MI
            '772': 'OVTK_GDF_Tongue',  # Rest
            '102': 'OVTK_GDF_Right',   # OVTK GDF Right
            '107': 'OVTK_GDF_Tongue',  # OVTK GDF Tongue
            770: 'OVTK_GDF_Right',
            772: 'OVTK_GDF_Tongue',
            102: 'OVTK_GDF_Right',
            107: 'OVTK_GDF_Tongue',
        }
        if value in value_map:
            return value_map[value]
        # Try string conversion
        str_val = str(value)
        if str_val in value_map:
            return value_map[str_val]
        return str(value)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row - handle both dict-like and Series
        if hasattr(row, 'get'):
            filepath = row.get('file_path', None)
            if filepath is None:
                # Try common alternatives
                for key in ['filepath', 'path', 'filename', 'file', 'raw_path']:
                    filepath = row.get(key, None)
                    if filepath is not None:
                        break
        elif hasattr(row, 'file_path'):
            filepath = row.file_path
        elif hasattr(row, 'filepath'):
            filepath = row.filepath
        elif hasattr(row, 'path'):
            filepath = row.path
        else:
            # Last resort: try to get from raw
            filepath = raw.filenames[0] if hasattr(raw, 'filenames') and raw.filenames else None
        
        if filepath is None:
            filepath = raw.filenames[0] if hasattr(raw, 'filenames') and raw.filenames else "unknown"

        # Get BIDS root and subject info
        bids_root = self._get_bids_root(filepath)
        subject_id = self._get_subject_id(filepath)

        # Read participants info
        participants_info = self._read_participants_info(bids_root, subject_id)

        # Build eegunity_description with required fields
        eegunity_description = {}

        # age: from participants.tsv, always string
        age_val = participants_info.get('age', 'unknown')
        eegunity_description['age'] = str(age_val) if age_val != 'unknown' else 'unknown'

        # sex/gender: lowercase male/female/unknown
        gender_val = participants_info.get('gender', 'unknown')
        if gender_val.lower() in ['m', 'male']:
            eegunity_description['sex'] = 'male'
        elif gender_val.lower() in ['f', 'female']:
            eegunity_description['sex'] = 'female'
        else:
            eegunity_description['sex'] = 'unknown'

        # amplifier: inferred from dataset description (low-cost consumer-grade BCI)
        eegunity_description['amplifier'] = 'OpenBCI Cyton (8-channel)'  # inferred by LLM, needs human review

        # cap: inferred from dataset docs
        eegunity_description['cap'] = 'custom 14-channel cap'  # inferred by LLM, needs human review

        # handedness: inferred from protocol (dominant hand used for MI)
        eegunity_description['handedness'] = 'right'  # inferred by LLM, needs human review

        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_description and field in participants_info:
                eegunity_description[field] = str(participants_info[field])

        # Set description
        original_desc = raw.info.get("description", "")
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description
        })

        # Channel rename BEFORE set_montage()
        # Apply channel renaming for known channels
        rename_map = {}
        for ch_name in raw.ch_names:
            if ch_name in self.CHANNEL_RENAME_MAP:
                new_name = self.CHANNEL_RENAME_MAP[ch_name]
                if new_name != ch_name:
                    rename_map[ch_name] = new_name
            # Also check case-insensitive
            elif ch_name.upper() in [k.upper() for k in self.CHANNEL_RENAME_MAP]:
                for k, v in self.CHANNEL_RENAME_MAP.items():
                    if k.upper() == ch_name.upper():
                        if v != ch_name:
                            rename_map[ch_name] = v
                        break

        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage for EEG channels
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            # Only set montage for channels that exist in the montage
            eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
            eeg_ch_names = [raw.ch_names[i] for i in eeg_picks]
            montage_ch_names = set(montage.ch_names)
            valid_ch_names = [ch for ch in eeg_ch_names if ch in montage_ch_names]
            if valid_ch_names:
                raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass

        # Handle events from events.tsv for formats that don't carry triggers
        # EDF files typically don't have embedded event annotations in this dataset
        events_tsv_path = self._find_events_tsv(filepath)
        events_df = self._read_events_tsv(events_tsv_path)

        if events_df is not None and len(events_df) > 0:
            # Check if raw already has annotations
            has_annotations = hasattr(raw, 'annotations') and raw.annotations is not None and len(raw.annotations) > 0

            if not has_annotations:
                # Create annotations from events.tsv
                onsets = []
                durations = []
                descriptions = []

                for _, event_row in events_df.iterrows():
                    onset = event_row.get('onset', 0)
                    duration = event_row.get('duration', 0)
                    if pd.isna(duration):
                        duration = 0

                    # Get event value/name
                    trial_type = event_row.get('trial_type', None)
                    value = event_row.get('value', None)

                    # Determine description
                    if trial_type is not None and not pd.isna(trial_type):
                        desc = self._map_event_value_to_name(trial_type)
                    elif value is not None and not pd.isna(value):
                        desc = self._map_event_value_to_name(value)
                    else:
                        desc = 'unknown'

                    onsets.append(float(onset))
                    durations.append(float(duration))
                    descriptions.append(str(desc))

                if len(onsets) > 0:
                    annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                    raw.set_annotations(annot)

        # Ensure required event IDs exist in annotations
        # Verify by checking annotations
        if raw.annotations is not None:
            existing_descs = set(raw.annotations.description)
            # Map any numeric descriptions to proper names
            new_descriptions = []
            need_update = False
            for desc in raw.annotations.description:
                mapped = self._map_event_value_to_name(desc)
                if mapped != desc:
                    new_descriptions.append(mapped)
                    need_update = True
                else:
                    new_descriptions.append(desc)

            if need_update:
                new_annot = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    orig_time=raw.annotations.orig_time
                )
                raw.set_annotations(new_annot)

        # Handle derived misc channels (none required for this dataset)
        # Handle native misc channels (none required for this dataset)

        return raw


KERNEL = OpenneuroDs003810Kernel()