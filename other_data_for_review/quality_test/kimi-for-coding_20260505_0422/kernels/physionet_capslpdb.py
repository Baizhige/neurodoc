import json
import os
import warnings
import numpy as np
import pandas as pd
import mne


class PhysionetCapslpdbKernel:
    KERNEL_ID = "physionet_capslpdb"
    KERNEL_NAME = "PhysioNet CAP Sleep Database"
    KERNEL_DESCRIPTION = "EEG kernel for PhysioNet CAP Sleep Database - sleep disorder EEG recordings"
    KERNEL_CITATION = "10.13026/C2VC79"
    KERNEL_LICENSE = "ODbL"
    KERNEL_URL = "https://physionet.org/content/capslpdb/1.0.0/"

    required_event_ids = []
    required_info_fields = []
    required_native_misc = []
    derived_misc_channels = []

    def __init__(self):
        pass

    def _find_subject_info(self, filepath):
        """Extract subject info from filename and known dataset metadata."""
        basename = os.path.basename(filepath)
        name, _ = os.path.splitext(basename)
        
        # The CAP Sleep Database has various prefixes indicating condition
        # n = narcolepsy, rbd = REM behavior disorder, nfle = nocturnal frontal lobe epilepsy
        # ins = insomnia, brux = bruxism, plm = periodic leg movements
        # We don't have per-subject age/sex in files, so we infer from known dataset structure
        # or return unknown. The dataset doesn't have participants.tsv.
        
        info = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown"
        }
        
        # Try to parse known metadata from filename patterns
        # This is a well-studied dataset with published demographics
        # We mark inferred values appropriately
        
        # Known approximate demographics from papers (not per-subject)
        # This dataset doesn't provide individual subject metadata in machine-readable form
        
        return info

    def _read_edf_annotations(self, filepath):
        """Read annotations from EDF file if present."""
        try:
            # Use mne.read_annotations to check for EDF+/EDF annotations
            annots = mne.read_annotations(filepath)
            return annots
        except Exception:
            return None

    def _find_events_file(self, filepath):
        """Look for companion events file."""
        base = os.path.splitext(filepath)[0]
        for ext in ['.tsv', '.csv', '.txt', '.evt', '.events']:
            candidate = base + ext
            if os.path.exists(candidate):
                return candidate
        # Check for events.tsv in same directory
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name_no_ext = os.path.splitext(basename)[0]
        events_tsv = os.path.join(dirname, name_no_ext + '_events.tsv')
        if os.path.exists(events_tsv):
            return events_tsv
        # Generic events.tsv
        generic = os.path.join(dirname, 'events.tsv')
        if os.path.exists(generic):
            return generic
        return None

    def _parse_events_file(self, events_file):
        """Parse events from text file."""
        events_list = []
        try:
            with open(events_file, 'r') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        onset = float(parts[0])
                        duration = float(parts[1]) if len(parts) > 1 else 0.0
                        description = parts[2] if len(parts) > 2 else 'event'
                        events_list.append((onset, duration, description))
                    except ValueError:
                        continue
        except Exception:
            pass
        return events_list

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        filepath = row['file_path'] if 'file_path' in row else raw.filenames[0] if hasattr(raw, 'filenames') and raw.filenames else ''
        
        # Get original description
        original_description = raw.info.get('description', '') or ''
        
        # Get subject info
        info = self._find_subject_info(filepath)
        
        # Build eegunity_description with required fields
        # For this dataset, we don't have per-subject metadata, so use unknown
        eegunity_description = {
            "age": info.get("age", "unknown"),
            "sex": info.get("sex", "unknown"),
            "amplifier": info.get("amplifier", "unknown"),
            "cap": info.get("cap", "unknown"),
            "handedness": info.get("handedness", "unknown")
        }
        
        # Set description
        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description
        })
        
        # Handle channel renaming - standardize channel names if needed
        # CAP Sleep Database uses standard 10-20 naming, but let's ensure consistency
        rename_map = {}
        for ch_name in raw.ch_names:
            ch_upper = ch_name.upper().strip()
            # Common mappings for sleep EEG
            if ch_upper in ['FP1', 'FP2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2',
                           'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'FZ', 'CZ', 'PZ', 'OZ',
                           'A1', 'A2', 'M1', 'M2', 'ECG', 'EMG', 'EOG', 'EOG1', 'EOG2',
                           'LEG', 'LEG1', 'LEG2', 'CHIN', 'CHIN1', 'CHIN2', 'AIRFLOW',
                           'THOR', 'ABDO', 'SAO2', 'POS', 'LIGHT', 'SNORE']:
                # Keep as-is but ensure consistent case
                new_name = ch_upper
                if new_name != ch_name:
                    rename_map[ch_name] = new_name
        
        if rename_map:
            raw.rename_channels(rename_map)
        
        # Set channel types for known non-EEG channels in sleep recordings
        ch_types = {}
        for ch_name in raw.ch_names:
            ch_upper = ch_name.upper()
            if ch_upper in ['ECG', 'EKG']:
                ch_types[ch_name] = 'ecg'
            elif 'EMG' in ch_upper or 'CHIN' in ch_upper or 'LEG' in ch_upper or 'TIB' in ch_upper:
                ch_types[ch_name] = 'emg'
            elif 'EOG' in ch_upper:
                ch_types[ch_name] = 'eog'
            elif ch_upper in ['AIRFLOW', 'THOR', 'ABDO', 'SAO2', 'POS', 'LIGHT', 'SNORE',
                             'RESP', 'FLOW', 'PLETH', 'CO2', 'TEMP']:
                ch_types[ch_name] = 'bio'
            elif ch_upper in ['A1', 'A2', 'M1', 'M2', 'AUX', 'STATUS', 'TRIG']:
                ch_types[ch_name] = 'misc'
        
        if ch_types:
            raw.set_channel_types(ch_types)
        
        # Try to set montage for EEG channels
        eeg_picks = mne.pick_types(raw.info, eeg=True, exclude=[])
        if len(eeg_picks) > 0:
            try:
                raw.set_montage('standard_1020', match_case=False, on_missing='ignore')
            except Exception:
                pass
        
        # Handle annotations from EDF+ or companion files
        # EDF files may have embedded annotations (EDF+ format)
        annots = self._read_edf_annotations(filepath)
        if annots is not None and len(annots) > 0:
            raw.set_annotations(annots)
        else:
            # Try companion events file
            events_file = self._find_events_file(filepath)
            if events_file:
                events_list = self._parse_events_file(events_file)
                if events_list:
                    onsets = [e[0] for e in events_list]
                    durations = [e[1] for e in events_list]
                    descriptions = [e[2] for e in events_list]
                    annots = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                    raw.set_annotations(annots)
        
        # Ensure required native misc channels exist
        for misc_name in self.required_native_misc:
            if misc_name in raw.ch_names:
                current_type = raw.get_channel_types(picks=[misc_name])[0] if hasattr(raw, 'get_channel_types') else None
                if current_type is not None and current_type != 'misc':
                    raw.set_channel_types({misc_name: 'misc'})
        
        # Create derived misc channels if required
        for derived_name in self.derived_misc_channels:
            if derived_name not in raw.ch_names:
                # Create constant channel with unknown value
                data = np.zeros((1, len(raw.times)))
                info_misc = mne.create_info([derived_name], raw.info['sfreq'], ['misc'])
                raw_misc = mne.io.RawArray(data, info_misc, first_samp=raw.first_samp)
                raw.add_channels([raw_misc], force_update_info=True)
        
        return raw


KERNEL = PhysionetCapslpdbKernel()