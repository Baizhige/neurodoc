import json
import os
import re
import numpy as np
import pandas as pd
import mne


class PhysionetChbmitKernel:
    KERNEL_ID = "physionet_chbmit"
    KERNEL_NAME = "PhysioNet CHB-MIT Scalp EEG Database"
    KERNEL_DESCRIPTION = "CHB-MIT scalp EEG database for seizure detection. Contains continuous EEG recordings from pediatric subjects with intractable seizures, with seizure onset/offset annotations in EDF+ headers or .seizure companion files."
    KERNEL_CITATION = "10.13026/C2K01R"
    KERNEL_LICENSE = "ODbL 1.0"
    KERNEL_URL = "https://physionet.org/content/chbmit/1.0.0/"

    required_event_ids = []
    required_info_fields = []
    required_native_misc = []
    derived_misc_channels = [
        {"name": "seizure_state_label", "source_field": "events.tsv:seizure_start", "derivation": "For each 30-second segment, determine if it falls entirely before a seizure (pre-ictal), during a seizure (ictal, between seizure_start and seizure_end events), or neither (inter-ictal). Requires parsing seizure onset/offset annotations from EDF+ annotations or separate .seizure files in CHB-MIT. Pre-ictal window typically defined as 30-90 min before onset per domain convention.", "evidence": "No events.tsv columns discovered; annotations are embedded in EDF headers or .seizure companion files. Kernel must extract seizure onset/offset times from native CHB-MIT annotation format."},
        {"name": "seizure_binary_label", "source_field": "events.tsv:seizure_start", "derivation": "For each segment, label=1 if any portion overlaps with seizure interval [seizure_start, seizure_end], else label=0. CHB-MIT annotations are in EDF+ header or .seizure files. Kernel must extract precise onset/offset times and perform overlap check.", "evidence": "No native events.tsv columns; annotations embedded in EDF headers or companion .seizure files per CHB-MIT documentation."},
    ]

    # Standard 10-20 channel names used in CHB-MIT
    CHANNEL_RENAME_MAP = {
        'FP1-F7': 'Fp1',
        'F7-T7': 'F7',
        'T7-P7': 'T7',
        'P7-O1': 'P7',
        'FP1-F3': 'Fp1',
        'F3-C3': 'F3',
        'C3-P3': 'C3',
        'P3-O1': 'P3',
        'FP2-F4': 'Fp2',
        'F4-C4': 'F4',
        'C4-P4': 'C4',
        'P4-O2': 'P4',
        'FP2-F8': 'Fp2',
        'F8-T8': 'F8',
        'T8-P8': 'T8',
        'P8-O2': 'P8',
        'FZ-CZ': 'Fz',
        'CZ-PZ': 'Cz',
        'P7-T7': 'P7',
        'T7-FT9': 'T7',
        'FT9-FT10': 'FT9',
        'FT10-T8': 'FT8',
        'T8-P8': 'T8',
        'FP1-FP2': 'Fp1',
        'F3-F7': 'F3',
        'F4-F8': 'F4',
        'C3-C4': 'C3',
        'P3-P4': 'P3',
        'O1-O2': 'O1',
        'F7-F3': 'F7',
        'F8-F4': 'F8',
        'T7-C3': 'T7',
        'T8-C4': 'T8',
        'P7-P3': 'P7',
        'P8-P4': 'P8',
        'FZ-CZ': 'Fz',
        'CZ-PZ': 'Cz',
        'A1': 'A1',
        'A2': 'A2',
        'T7-FT9': 'T7',
        'FT9-FT10': 'FT9',
        'FT10-T8': 'FT8',
        'P7-T7': 'P7',
        'T7-FT9': 'T7',
        'FT9-FT10': 'FT9',
        'FT10-T8': 'FT8',
    }

    def __init__(self):
        pass

    def _find_dataset_root(self, filepath):
        """Find CHB-MIT dataset root directory from file path."""
        parts = os.path.normpath(filepath).split(os.sep)
        for i, part in enumerate(parts):
            if 'chb' in part.lower() or 'chbmit' in part.lower():
                # The root is typically the parent of chbXX folders
                return os.sep.join(parts[:i+1])
        # Fallback: look for pattern like chb01, chb02, etc.
        for i, part in enumerate(parts):
            if re.match(r'^chb\d+$', part):
                return os.sep.join(parts[:i+1])
        return os.path.dirname(filepath)

    def _get_subject_id_from_path(self, filepath):
        """Extract subject ID from file path (e.g., chb01)."""
        parts = os.path.normpath(filepath).split(os.sep)
        for part in parts:
            match = re.match(r'^(chb\d+)$', part)
            if match:
                return match.group(1)
        # Try from filename
        basename = os.path.basename(filepath)
        match = re.match(r'^(chb\d+)', basename)
        if match:
            return match.group(1)
        return None

    def _find_seizure_file(self, filepath):
        """Find .seizure companion file for a given EDF file."""
        base = os.path.splitext(filepath)[0]
        seizure_file = base + '.seizure'
        if os.path.exists(seizure_file):
            return seizure_file
        
        # Try in same directory with same base name
        dirname = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]
        seizure_file = os.path.join(dirname, basename + '.seizure')
        if os.path.exists(seizure_file):
            return seizure_file
        
        # CHB-MIT sometimes has seizure info in a summary file
        # Look for summary files in the subject directory
        subject_id = self._get_subject_id_from_path(filepath)
        if subject_id:
            dirname = os.path.dirname(filepath)
            # Check parent directory for summary
            parent = os.path.dirname(dirname)
            for root, dirs, files in os.walk(parent):
                for f in files:
                    if 'summary' in f.lower() and f.endswith('.txt'):
                        return os.path.join(root, f)
            # Check same directory
            for f in os.listdir(dirname):
                if 'summary' in f.lower() and f.endswith('.txt'):
                    return os.path.join(dirname, f)
        
        return None

    def _parse_seizure_times_from_summary(self, summary_path, edf_basename):
        """Parse seizure onset/offset times from CHB-MIT summary file."""
        seizures = []
        try:
            with open(summary_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # CHB-MIT summary format: look for file-specific sections
            # Pattern: "File Name: chb01_01.edf" followed by seizure info
            file_pattern = r'File Name:\s*' + re.escape(edf_basename) + r'.*?(?=File Name:|$)'
            file_match = re.search(file_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if file_match:
                section = file_match.group(0)
                # Look for seizure start/end times
                start_times = re.findall(r'Seizure\s*\d*\s*Start Time:\s*(\d+)\s*seconds', section, re.IGNORECASE)
                end_times = re.findall(r'Seizure\s*\d*\s*End Time:\s*(\d+)\s*seconds', section, re.IGNORECASE)
                
                for start, end in zip(start_times, end_times):
                    seizures.append((int(start), int(end)))
            else:
                # Try global search for this file
                lines = content.split('\n')
                in_file_section = False
                current_seizure_starts = []
                current_seizure_ends = []
                
                for line in lines:
                    if 'File Name:' in line and edf_basename in line:
                        in_file_section = True
                        # Save any previous seizures
                        for s, e in zip(current_seizure_starts, current_seizure_ends):
                            seizures.append((s, e))
                        current_seizure_starts = []
                        current_seizure_ends = []
                    elif 'File Name:' in line and in_file_section:
                        in_file_section = False
                        # Save seizures from previous section
                        for s, e in zip(current_seizure_starts, current_seizure_ends):
                            seizures.append((s, e))
                        current_seizure_starts = []
                        current_seizure_ends = []
                    
                    if in_file_section:
                        start_match = re.search(r'Seizure\s*\d*\s*Start Time:\s*(\d+)', line, re.IGNORECASE)
                        end_match = re.search(r'Seizure\s*\d*\s*End Time:\s*(\d+)', line, re.IGNORECASE)
                        if start_match:
                            current_seizure_starts.append(int(start_match.group(1)))
                        if end_match:
                            current_seizure_ends.append(int(end_match.group(1)))
                
                # Don't forget last section
                for s, e in zip(current_seizure_starts, current_seizure_ends):
                    seizures.append((s, e))
                    
        except Exception:
            pass
        
        return seizures

    def _parse_seizure_times_from_edf_annotations(self, raw):
        """Parse seizure times from EDF+ annotations if present."""
        seizures = []
        try:
            # Check for annotations in the raw object
            if hasattr(raw, 'annotations') and raw.annotations is not None:
                for desc, onset, duration in zip(raw.annotations.description,
                                                  raw.annotations.onset,
                                                  raw.annotations.duration):
                    desc_lower = str(desc).lower()
                    if 'seizure' in desc_lower or 'sz' in desc_lower:
                        start = onset
                        end = onset + duration if duration > 0 else onset + 1
                        seizures.append((int(start), int(end)))
        except Exception:
            pass
        
        # Also try reading from EDF header directly via mne
        try:
            # Some CHB-MIT files have annotations as a TAL channel
            if hasattr(raw, 'read_annotations'):
                annot = raw.read_annotations()
                for desc, onset, duration in zip(annot.description,
                                                  annot.onset,
                                                  annot.duration):
                    desc_lower = str(desc).lower()
                    if 'seizure' in desc_lower or 'sz' in desc_lower:
                        start = onset
                        end = onset + duration if duration > 0 else onset + 1
                        seizures.append((int(start), int(end)))
        except Exception:
            pass
            
        return seizures

    def _get_seizure_times(self, filepath, raw):
        """Get all seizure onset/offset times for this file."""
        seizures = []
        
        # First try EDF+ annotations
        seizures = self._parse_seizure_times_from_edf_annotations(raw)
        if seizures:
            return seizures
        
        # Try .seizure file or summary file
        seizure_file = self._find_seizure_file(filepath)
        if seizure_file:
            if seizure_file.endswith('.seizure'):
                try:
                    with open(seizure_file, 'r') as f:
                        # Simple format: start end pairs
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                try:
                                    start = int(float(parts[0]))
                                    end = int(float(parts[1]))
                                    seizures.append((start, end))
                                except ValueError:
                                    pass
                except Exception:
                    pass
            elif seizure_file.endswith('.txt') and 'summary' in seizure_file.lower():
                basename = os.path.basename(filepath)
                seizures = self._parse_seizure_times_from_summary(seizure_file, basename)
        
        return seizures

    def _create_seizure_misc_channels(self, raw, seizure_times):
        """Create derived misc channels for seizure state and binary labels."""
        n_samples = raw.n_times
        sfreq = raw.info['sfreq']
        times = raw.times
        
        # Initialize channels with zeros (inter-ictal / no seizure)
        seizure_binary = np.zeros((1, n_samples))
        seizure_state = np.zeros((1, n_samples))  # 0=inter-ictal, 1=pre-ictal, 2=ictal
        
        # Pre-ictal window: 30-90 minutes before seizure (using 30 min = 1800 sec)
        pre_ictal_window = 1800  # 30 minutes in seconds
        
        for start_sec, end_sec in seizure_times:
            # Convert to sample indices
            start_sample = int(start_sec * sfreq)
            end_sample = int(end_sec * sfreq)
            
            # Clamp to valid range
            start_sample = max(0, min(start_sample, n_samples - 1))
            end_sample = max(0, min(end_sample, n_samples - 1))
            
            # Set binary label: 1 during seizure
            seizure_binary[0, start_sample:end_sample+1] = 1.0
            
            # Set state label: 2 = ictal during seizure
            seizure_state[0, start_sample:end_sample+1] = 2.0
            
            # Set pre-ictal: 30-90 min before seizure (we use up to 30 min before)
            pre_ictal_start = max(0, start_sample - int(pre_ictal_window * sfreq))
            # Only mark as pre-ictal where it's not already ictal
            pre_ictal_mask = (seizure_state[0, pre_ictal_start:start_sample] == 0)
            seizure_state[0, pre_ictal_start:start_sample][pre_ictal_mask] = 1.0
        
        # Create info for new channels
        info_binary = mne.create_info(['seizure_binary_label'], sfreq, ch_types='misc')
        info_state = mne.create_info(['seizure_state_label'], sfreq, ch_types='misc')
        
        # Create RawArray objects
        raw_binary = mne.io.RawArray(seizure_binary, info_binary, first_samp=raw.first_samp)
        raw_state = mne.io.RawArray(seizure_state, info_state, first_samp=raw.first_samp)
        
        # Add channels to original raw
        raw.add_channels([raw_binary, raw_state], force_update_info=True)
        
        return raw

    def _standardize_channel_names(self, raw):
        """Standardize channel names to 10-20 system."""
        ch_names = raw.ch_names
        rename_map = {}
        
        for ch_name in ch_names:
            ch_upper = ch_name.upper()
            # Direct mapping from bipolar to monopolar approximation
            if ch_upper in self.CHANNEL_RENAME_MAP:
                rename_map[ch_name] = self.CHANNEL_RENAME_MAP[ch_upper]
            else:
                # Try to extract meaningful name
                # Handle patterns like "FP1-F7" -> "Fp1"
                parts = ch_upper.split('-')
                if len(parts) == 2:
                    # Use first part as approximate location
                    if parts[0] in self.CHANNEL_RENAME_MAP:
                        rename_map[ch_name] = self.CHANNEL_RENAME_MAP[parts[0]]
                    elif parts[1] in self.CHANNEL_RENAME_MAP:
                        rename_map[ch_name] = self.CHANNEL_RENAME_MAP[parts[1]]
                    else:
                        # Keep original if no mapping
                        rename_map[ch_name] = ch_name
                else:
                    rename_map[ch_name] = ch_name
        
        # Apply renaming
        raw.rename_channels(rename_map)
        
        # Handle duplicate channel names by adding suffixes
        ch_names = raw.ch_names
        seen = {}
        new_names = []
        for name in ch_names:
            if name in seen:
                seen[name] += 1
                new_name = f"{name}_{seen[name]}"
                new_names.append(new_name)
            else:
                seen[name] = 0
                new_names.append(name)
        
        if new_names != ch_names:
            raw.rename_channels(dict(zip(ch_names, new_names)))
        
        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage for CHB-MIT data."""
        try:
            # Try standard 10-20 montage
            montage = mne.channels.make_standard_montage('standard_1020')
            # Only include channels that exist in raw
            available_chs = [ch for ch in montage.ch_names if ch in raw.ch_names]
            if available_chs:
                montage = montage.pick_channels(available_chs)
                raw.set_montage(montage, match_case=False, on_missing='ignore')
        except Exception:
            pass
        
        return raw

    def _read_participants_info(self, filepath):
        """Read participant info from CHB-MIT dataset."""
        info = {}
        
        # CHB-MIT doesn't have a standard participants.tsv
        # Extract subject ID and use known demographics if available
        subject_id = self._get_subject_id_from_path(filepath)
        
        # CHB-MIT subjects are pediatric patients; ages are approximate from paper
        # These are inferred values based on published information about the dataset
        chb_ages = {
            'chb01': '11', 'chb02': '11', 'chb03': '14', 'chb04': '22',
            'chb05': '7', 'chb06': '1.5', 'chb07': '14.5', 'chb08': '3.5',
            'chb09': '10', 'chb10': '3', 'chb11': '12', 'chb12': '2',
            'chb13': '3', 'chb14': '9', 'chb15': '16', 'chb16': '7',
            'chb17': '12', 'chb18': '18', 'chb19': '19', 'chb20': '6',
            'chb21': '13', 'chb22': '9', 'chb23': '6', 'chb24': 'nan',
        }
        
        if subject_id and subject_id in chb_ages:
            info['age'] = chb_ages[subject_id]  # inferred by LLM, needs human review
        else:
            info['age'] = 'unknown'
        
        # Sex information not consistently available in CHB-MIT
        info['sex'] = 'unknown'
        
        # Equipment info from CHB-MIT documentation
        info['amplifier'] = 'Nihon Kohden EEG-1200'  # inferred by LLM, needs human review
        info['cap'] = 'unknown'
        info['handedness'] = 'unknown'
        
        return info

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        filepath = row['file_path']
        
        # Standardize channel names first (before montage)
        raw = self._standardize_channel_names(raw)
        
        # Set montage
        raw = self._set_montage(raw)
        
        # Get seizure times from annotations or companion files
        seizure_times = self._get_seizure_times(filepath, raw)
        
        # Create derived misc channels for seizure labels
        raw = self._create_seizure_misc_channels(raw, seizure_times)
        
        # Ensure misc channel types are set correctly
        misc_chs = ['seizure_binary_label', 'seizure_state_label']
        ch_type_map = {}
        for ch in misc_chs:
            if ch in raw.ch_names:
                ch_type_map[ch] = 'misc'
        if ch_type_map:
            raw.set_channel_types(ch_type_map)
        
        # Add annotations from seizure times if not already present
        if seizure_times and (not hasattr(raw, 'annotations') or raw.annotations is None or len(raw.annotations) == 0):
            onsets = []
            durations = []
            descriptions = []
            for start_sec, end_sec in seizure_times:
                onsets.append(float(start_sec))
                durations.append(float(end_sec - start_sec))
                descriptions.append('seizure')
            
            if onsets:
                annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
                raw.set_annotations(annot)
        
        # Get participant info
        participant_info = self._read_participants_info(filepath)
        
        # Build description
        original_desc = raw.info.get('description', '')
        if original_desc is None:
            original_desc = ''
        
        eegunity_description = {
            'age': str(participant_info.get('age', 'unknown')),
            'sex': participant_info.get('sex', 'unknown').lower(),
            'amplifier': participant_info.get('amplifier', 'unknown'),
            'cap': participant_info.get('cap', 'unknown'),
            'handedness': participant_info.get('handedness', 'unknown'),
        }
        
        raw.info['description'] = json.dumps({
            'original_description': original_desc,
            'eegunity_description': eegunity_description
        })
        
        return raw


KERNEL = PhysionetChbmitKernel()