import json
import os
import re
import warnings
import numpy as np
import pandas as pd
import mne


class OpenNeuroDs005178Kernel:
    KERNEL_ID = "openneuro_ds005178"
    KERNEL_NAME = "OpenNeuro ds005178 - Ear-EEG Sleep Monitoring (EESM23)"
    KERNEL_DESCRIPTION = "EEG kernel for ear-EEG sleep monitoring dataset with 5-class sleep stage classification (Wake, REM, N1, N2, N3) and 30-second PSG-scored epochs"
    KERNEL_CITATION = "10.3389/fnins.2023.987578"
    KERNEL_LICENSE = "CC0"
    KERNEL_URL = "https://openneuro.org/datasets/ds005178"

    required_event_ids = ['event_2', 'trigger']
    required_info_fields = ['age', 'sex']
    required_native_misc = []
    derived_misc_channels = [
        {'name': 'subject_id_label', 'source_field': 'events.tsv:subject_id', 'derivation': 'Extract subject identifier from BIDS filename (sub-XXX) and broadcast as constant integer label per recording for subject-level stratification or subject-invariant learning objectives; evidence = No participants.tsv columns available; subject identity inferable from filename structure per BIDS specification'}
    ]

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

    def _get_subject_id_from_path(self, raw_path):
        """Extract subject ID from BIDS file path."""
        parts = os.path.normpath(raw_path).split(os.sep)
        for part in parts:
            if part.startswith("sub-"):
                return part
        # Try regex fallback
        match = re.search(r'(sub-\d+)', raw_path)
        if match:
            return match.group(1)
        return None

    def _find_participants_tsv(self, bids_root):
        """Find participants.tsv file."""
        if bids_root is None:
            return None
        p_tsv = os.path.join(bids_root, "participants.tsv")
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
                # Try alternative formats
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

    def _find_events_tsv(self, raw_path):
        """Find corresponding events.tsv file for a raw EEG file."""
        # raw_path is a string path
        if raw_path is None:
            return None
        
        # Get the directory containing the EEG file
        eeg_dir = os.path.dirname(raw_path)
        
        # Get base filename without extension
        basename = os.path.basename(raw_path)
        # Remove known EEG extensions
        for ext in ['.set', '.edf', '.eeg', '.fif', '.vhdr', '.vmrk', '.cnt', '.bdf']:
            if basename.lower().endswith(ext):
                basename = basename[:-len(ext)]
                break
        
        # Look for events.tsv in same directory
        events_tsv = os.path.join(eeg_dir, basename + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
        
        # Try without any suffix (BIDS pattern: sub-xxx_ses-xxx_task-xxx_events.tsv)
        # The basename should already be the BIDS entity string
        events_tsv = os.path.join(eeg_dir, basename + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
            
        # Look for any events.tsv in the same directory
        if os.path.isdir(eeg_dir):
            for f in os.listdir(eeg_dir):
                if f.endswith('_events.tsv'):
                    return os.path.join(eeg_dir, f)
        
        return None

    def _read_events_tsv(self, events_tsv_path):
        """Read events.tsv file."""
        if events_tsv_path is None or not os.path.exists(events_tsv_path):
            return None
        try:
            return pd.read_csv(events_tsv_path, sep='\t')
        except Exception:
            return None

    def _events_to_annotations(self, events_df, raw):
        """Convert events.tsv DataFrame to mne.Annotations."""
        if events_df is None or len(events_df) == 0:
            return None
        
        # Required columns for annotations
        if 'onset' not in events_df.columns:
            return None
        
        onsets = events_df['onset'].values.astype(float)
        durations = events_df['duration'].values.astype(float) if 'duration' in events_df.columns else np.zeros(len(onsets))
        
        # Use trial_type if available, otherwise value, otherwise description
        if 'trial_type' in events_df.columns:
            descriptions = events_df['trial_type'].astype(str).values
        elif 'value' in events_df.columns:
            descriptions = events_df['value'].astype(str).values
        elif 'description' in events_df.columns:
            descriptions = events_df['description'].astype(str).values
        else:
            descriptions = np.array(['event'] * len(onsets))
        
        # Filter out any NaN onsets
        valid_mask = ~np.isnan(onsets)
        onsets = onsets[valid_mask]
        durations = durations[valid_mask] if len(durations) == len(valid_mask) else durations[valid_mask[:len(durations)]]
        descriptions = descriptions[valid_mask]
        
        # Ensure durations are non-negative
        durations = np.maximum(durations, 0)
        
        # Create annotations
        annotations = mne.Annotations(
            onset=onsets,
            duration=durations,
            description=descriptions,
            orig_time=raw.info['meas_date'] if raw.info['meas_date'] is not None else None
        )
        return annotations

    def _extract_subject_id_label(self, subject_id):
        """Extract numeric subject ID from 'sub-XXX' format."""
        if subject_id is None:
            return 0
        match = re.search(r'sub-(\d+)', subject_id)
        if match:
            return int(match.group(1))
        return 0

    def _create_derived_misc_channel(self, raw, channel_name, values):
        """Create a derived misc channel with constant values."""
        data = np.full((1, len(raw.times)), float(values), dtype=np.float64)
        info = mne.create_info([channel_name], raw.info['sfreq'], ['misc'])
        misc_raw = mne.io.RawArray(data, info, first_samp=raw.first_samp)
        
        # Match annotations if any
        if raw.annotations is not None:
            misc_raw.set_annotations(raw.annotations)
        
        return misc_raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # Get file path from row - handle both dict-like and pandas Series
        raw_path = None
        if hasattr(row, 'get'):
            # dict-like
            for key in ['file_path', 'filepath', 'path', 'filename']:
                if key in row:
                    raw_path = row.get(key)
                    break
        elif hasattr(row, 'iloc') and hasattr(row, 'index'):
            # pandas Series - try by index name or position
            for key in ['file_path', 'filepath', 'path', 'filename']:
                if key in row.index:
                    raw_path = row[key]
                    break
            if raw_path is None and len(row) > 0:
                # Try first column as fallback
                raw_path = row.iloc[0] if isinstance(row.iloc[0], str) else None
        elif hasattr(row, '__getitem__'):
            try:
                raw_path = row['file_path']
            except (KeyError, TypeError):
                try:
                    raw_path = row[0] if isinstance(row[0], str) else None
                except (IndexError, TypeError):
                    pass
        
        # If still no path, try to get from raw
        if raw_path is None and hasattr(raw, 'filenames') and raw.filenames is not None and len(raw.filenames) > 0:
            raw_path = raw.filenames[0]
        
        # Get BIDS info
        bids_root = self._get_bids_root(raw_path) if raw_path else None
        subject_id = self._get_subject_id_from_path(raw_path) if raw_path else None
        
        # Read participants info
        participants_tsv = self._find_participants_tsv(bids_root)
        participants_info = self._read_participants_info(participants_tsv, subject_id)
        
        # Handle age and sex with defaults
        age = participants_info.get('age', 'unknown')
        sex = participants_info.get('sex', 'unknown')
        
        # Normalize sex to lowercase
        if sex is not None and sex != 'unknown':
            sex = sex.lower()
            if sex in ['m', 'male']:
                sex = 'male'
            elif sex in ['f', 'female']:
                sex = 'female'
            else:
                sex = 'unknown'
        else:
            sex = 'unknown'
        
        # Get original description
        original_description = raw.info.get('description', '')
        if original_description is None:
            original_description = ''
        
        # Build eegunity_description
        eegunity_description = {
            'age': str(age) if age is not None else 'unknown',
            'sex': sex,
            'amplifier': 'unknown',  # inferred by LLM, needs human review
            'cap': 'ear-EEG',  # inferred by LLM, needs human review
            'handedness': 'unknown',  # inferred by LLM, needs human review
        }
        
        # Add any extra required info fields from participants.tsv
        for field in self.required_info_fields:
            if field not in eegunity_description and field in participants_info:
                eegunity_description[field] = str(participants_info[field]) if participants_info[field] is not None else 'unknown'
        
        # Set description
        raw.info['description'] = json.dumps({
            'original_description': original_description,
            'eegunity_description': eegunity_description
        })
        
        # Channel renaming - standardize channel names before set_montage
        # For ear-EEG, channels are typically already named appropriately
        # but we ensure consistency
        current_ch_names = raw.ch_names
        
        # Check if we need to rename any channels (ear-EEG specific mappings if needed)
        rename_map = {}
        for ch_name in current_ch_names:
            # Handle any known variations
            new_name = ch_name.strip()
            if new_name != ch_name:
                rename_map[ch_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set standard 10-20 montage if applicable, or custom ear-EEG montage
        # For ear-EEG, we might not have a standard montage, so we skip if it fails
        try:
            # Try to set a standard montage for any scalp channels
            raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
        except Exception:
            pass  # ear-EEG may not have standard montage
        
        # Handle events from events.tsv if needed
        # EEGLAB .set files may or may not have events baked in
        events_tsv_path = self._find_events_tsv(raw_path) if raw_path else None
        events_df = self._read_events_tsv(events_tsv_path)
        
        # Check if raw already has annotations/events
        has_native_events = False
        try:
            # Check for annotations
            if raw.annotations is not None and len(raw.annotations) > 0:
                has_native_events = True
            # Check for events in stim channels
            events = mne.find_events(raw, shortest_event=1, initial_event=True)
            if len(events) > 0:
                has_native_events = True
        except Exception:
            pass
        
        # If no native events and we have events.tsv, create annotations
        if not has_native_events and events_df is not None and len(events_df) > 0:
            annotations = self._events_to_annotations(events_df, raw)
            if annotations is not None:
                raw.set_annotations(annotations)
        
        # Create derived misc channels
        # subject_id_label from events.tsv:subject_id or filename
        subject_id_label = self._extract_subject_id_label(subject_id)
        
        # Create subject_id_label misc channel
        misc_raw = self._create_derived_misc_channel(raw, 'subject_id_label', subject_id_label)
        raw.add_channels([misc_raw], force_update_info=True)
        
        # Ensure the misc channel type is set correctly
        raw.set_channel_types({'subject_id_label': 'misc'})
        
        # Verify required event IDs exist
        # event_2 should correspond to sleep stage scoring annotations
        # We ensure annotations have proper descriptions
        
        # If we have events_df with scoring_idx, ensure proper event descriptions
        if events_df is not None and 'scoring_idx' in events_df.columns:
            # The scoring_idx column provides labels 1-6
            # We need to ensure these are accessible as annotations
            if raw.annotations is None or len(raw.annotations) == 0:
                # Create annotations from scoring data
                if 'onset' in events_df.columns:
                    onsets = events_df['onset'].values.astype(float)
                    durations = events_df['duration'].values.astype(float) if 'duration' in events_df.columns else np.full(len(onsets), 30.0)
                    
                    # Map scoring_idx to event descriptions for event_2
                    scoring_map = {
                        1: 'event_2/Wake',
                        2: 'event_2/REM', 
                        3: 'event_2/N1',
                        4: 'event_2/N2',
                        5: 'event_2/N3',
                        6: 'event_2/Artefact'
                    }
                    
                    descriptions = []
                    for idx in events_df['scoring_idx'].values:
                        desc = scoring_map.get(int(idx), 'event_2/unknown') if not pd.isna(idx) else 'event_2/unknown'
                        descriptions.append(desc)
                    
                    valid_mask = ~np.isnan(onsets)
                    onsets = onsets[valid_mask]
                    durations = durations[valid_mask[:len(durations)]]
                    descriptions = [d for i, d in enumerate(descriptions) if valid_mask[i]]
                    
                    durations = np.maximum(durations, 0)
                    
                    annotations = mne.Annotations(
                        onset=onsets,
                        duration=durations,
                        description=descriptions,
                        orig_time=raw.info['meas_date'] if raw.info['meas_date'] is not None else None
                    )
                    raw.set_annotations(annotations)
        
        # Ensure trigger event exists - create dummy trigger if needed for task compatibility
        # Check if we have any trigger-like annotations
        has_trigger = False
        if raw.annotations is not None:
            for desc in raw.annotations.description:
                if 'trigger' in str(desc).lower() or desc == 'trigger':
                    has_trigger = True
                    break
        
        # If no trigger exists, we don't create a dummy one - the task system will handle missing events
        
        return raw


KERNEL = OpenNeuroDs005178Kernel()