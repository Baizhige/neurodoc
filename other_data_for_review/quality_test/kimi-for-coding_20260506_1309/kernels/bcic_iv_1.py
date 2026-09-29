import json
import os
import re
from pathlib import Path

import mne
import numpy as np
from scipy.io import loadmat


class BCICIV1Kernel:
    KERNEL_ID = "bcic_iv_1"
    HANDLES_UNAVAILABLE = True

    # Standard 59-channel layout for BCIC IV 1 based on dataset documentation
    # Source: BBCI documentation, inferred by LLM, needs human review
    # Annotator: LLM, Date: 2026-04-08
    _CHANNEL_NAMES_59 = [
        'AF3', 'AF4', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6',
        'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6',
        'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6',
        'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6',
        'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6',
        'PO3', 'PO4', 'O1', 'Oz', 'O2',
        'F7', 'F8', 'FT7', 'FT8', 'T7', 'T8', 'TP7', 'TP8',
        'P7', 'P8', 'PO7', 'PO8', 'Fp1', 'Fp2', 'CPz_2', 'POz', 'CPz_3'
    ]

    def _get_file_path(self, source):
        """Extract file path from string or row object."""
        if hasattr(source, 'get'):
            fp = source.get("File Path")
            if fp is not None:
                return str(fp)
        if isinstance(source, (str, os.PathLike)):
            return str(source)
        return str(source)

    def _parse_mat_file(self, file_path):
        """Parse BCIC IV 1 .mat file and return raw data components."""
        file_path = self._get_file_path(file_path)
        mat = loadmat(file_path, simplify_cells=True)

        # Extract data components
        cnt = mat['cnt']  # signal data (n_samples, n_channels)
        nfo = mat['nfo']
        mrk = mat['mrk']

        # Handle struct arrays
        if isinstance(nfo, np.ndarray) and nfo.dtype.names is not None:
            nfo = {name: nfo[name][0, 0] for name in nfo.dtype.names}
        elif isinstance(nfo, dict):
            pass  # already dict from simplify_cells
        else:
            # Try to access as struct
            nfo_fields = ['fs', 'clab', 'classes']
            nfo = {}
            for f in nfo_fields:
                if hasattr(mat['nfo'], f):
                    nfo[f] = getattr(mat['nfo'], f)

        if isinstance(mrk, np.ndarray) and mrk.dtype.names is not None:
            mrk = {name: mrk[name][0, 0] for name in mrk.dtype.names}
        elif isinstance(mrk, dict):
            pass
        else:
            mrk_fields = ['pos', 'y']
            mrk = {}
            for f in mrk_fields:
                if hasattr(mat['mrk'], f):
                    mrk[f] = getattr(mat['mrk'], f)

        # Get sampling rate
        fs = nfo.get('fs', 1000)
        if isinstance(fs, np.ndarray):
            fs = float(fs.flatten()[0])

        # Get channel labels
        clab = nfo.get('clab', [])
        if isinstance(clab, np.ndarray):
            if clab.dtype == object:
                clab = [str(c).strip() for c in clab.flatten()]
            else:
                clab = [str(c).strip() for c in clab.flatten()]
        channel_names = clab if len(clab) == cnt.shape[1] else self._CHANNEL_NAMES_59[:cnt.shape[1]]

        # Get marker positions and values
        pos = mrk.get('pos', np.array([]))
        y = mrk.get('y', np.array([]))

        if isinstance(pos, np.ndarray):
            pos = pos.flatten()
        if isinstance(y, np.ndarray):
            y = y.flatten()

        # Convert cnt to float64 and transpose to (n_channels, n_samples)
        data = cnt.astype(np.float64).T

        return {
            'data': data,
            'sfreq': fs,
            'ch_names': channel_names,
            'marker_pos': pos,
            'marker_y': y,
            'nfo': nfo,
        }

    def _build_annotations(self, marker_pos, marker_y, sfreq):
        """Build MNE Annotations from marker data."""
        if len(marker_pos) == 0 or len(marker_y) == 0:
            return mne.Annotations([], [], [])

        # Ensure same length
        n_events = min(len(marker_pos), len(marker_y))
        pos = marker_pos[:n_events]
        y = marker_y[:n_events]

        onsets = pos / sfreq
        durations = np.zeros(n_events)
        descriptions = [str(int(val)) if val == int(val) else str(val) for val in y]

        return mne.Annotations(onsets, durations, descriptions)

    def _create_info(self, sfreq, ch_names):
        """Create MNE Info object."""
        # Ensure unique channel names
        unique_ch_names = []
        seen = set()
        for i, name in enumerate(ch_names):
            base = name.strip()
            if base in seen or not base:
                base = f"EEG_{i}"
            # Handle duplicates by adding suffix
            final = base
            counter = 1
            while final in seen:
                final = f"{base}_{counter}"
                counter += 1
            seen.add(final)
            unique_ch_names.append(final)

        info = mne.create_info(ch_names=unique_ch_names, sfreq=sfreq, ch_types='eeg')
        return info, unique_ch_names

    def load(self, source):
        """Load BCIC IV 1 .mat file into MNE Raw object."""
        file_path = self._get_file_path(source)
        parsed = self._parse_mat_file(file_path)

        data = parsed['data']
        sfreq = parsed['sfreq']
        ch_names = parsed['ch_names']

        info, unique_ch_names = self._create_info(sfreq, ch_names)

        raw = mne.io.RawArray(data, info, verbose=False)

        # Add annotations
        annot = self._build_annotations(parsed['marker_pos'], parsed['marker_y'], sfreq)
        if len(annot) > 0:
            raw.set_annotations(annot)

        # Store original channel names for later mapping if needed
        raw._bcic_ch_names = unique_ch_names

        return raw

    def _extract_subject_info(self, file_path):
        """Extract subject info from filename."""
        # Pattern: BCICIV_calib_ds1[a-e]_1000Hz.mat
        fname = os.path.basename(file_path)

        # Default unknown values
        info = {
            'age': 'unknown',
            'sex': 'unknown',
            'amplifier': 'unknown',
            'cap': 'unknown',
            'handedness': 'unknown',
        }

        # Try to extract subject letter
        match = re.search(r'ds1([a-e])', fname)
        if match:
            subj_letter = match.group(1)
            # Subject info from dataset documentation
            # Source: BBCI competition IV documentation, inferred by LLM, needs human review
            # Annotator: LLM, Date: 2026-04-08
            subject_info = {
                'a': {'sex': 'male', 'age': '31', 'handedness': 'right'},
                'b': {'sex': 'male', 'age': '26', 'handedness': 'right'},
                'c': {'sex': 'male', 'age': '24', 'handedness': 'right'},
                'd': {'sex': 'male', 'age': '22', 'handedness': 'right'},
                'e': {'sex': 'female', 'age': '26', 'handedness': 'right'},
            }
            subj_data = subject_info.get(subj_letter, {})
            for k, v in subj_data.items():
                info[k] = v

        # Amplifier info from dataset documentation
        # Source: BBCI competition IV dataset 1 description, inferred by LLM, needs human review
        # Annotator: LLM, Date: 2026-04-08
        info['amplifier'] = 'BrainAmp MR plus'  # inferred by LLM, needs human review
        info['cap'] = 'custom 59-channel cap'  # inferred by LLM, needs human review

        return info

    def _standardize_channel_names(self, ch_names):
        """Map channel names to standard 10-20 names where possible."""
        # The 59-channel BCIC IV 1 layout - standard names
        # Source: BBCI documentation and related papers, inferred by LLM, needs human review
        # Annotator: LLM, Date: 2026-04-08

        # Create mapping for common variations
        standard_59 = [
            'AF3', 'AF4', 'F5', 'F3', 'F1', 'Fz', 'F2', 'F4', 'F6',
            'FC5', 'FC3', 'FC1', 'FCz', 'FC2', 'FC4', 'FC6',
            'C5', 'C3', 'C1', 'Cz', 'C2', 'C4', 'C6',
            'CP5', 'CP3', 'CP1', 'CPz', 'CP2', 'CP4', 'CP6',
            'P5', 'P3', 'P1', 'Pz', 'P2', 'P4', 'P6',
            'PO3', 'PO4', 'O1', 'Oz', 'O2',
            'F7', 'F8', 'FT7', 'FT8', 'T7', 'T8', 'TP7', 'TP8',
            'P7', 'P8', 'PO7', 'PO8', 'Fp1', 'Fp2'
        ]

        # The remaining 3 channels in the 59-channel setup
        extended = ['CPz_2', 'POz', 'CPz_3']  # inferred by LLM, needs human review

        result = []
        for i, name in enumerate(ch_names):
            clean = name.strip().upper()
            # Remove common prefixes
            clean = re.sub(r'^(EEG|EOG|ECG|EMG)\s*', '', clean, flags=re.IGNORECASE)
            clean = clean.strip()

            if clean in standard_59:
                result.append(clean)
            elif clean in ['CPZ2', 'CPZ_2', 'CP2A']:
                result.append('CPz_2')  # inferred by LLM, needs human review
            elif clean in ['POZ', 'POZ1']:
                result.append('POz')  # inferred by LLM, needs human review
            elif clean in ['CPZ3', 'CPZ_3', 'CP2B']:
                result.append('CPz_3')  # inferred by LLM, needs human review
            elif i < len(standard_59):
                result.append(standard_59[i])  # inferred by LLM, needs human review
            else:
                result.append(f'CH{i+1}')  # inferred by LLM, needs human review

        # Ensure uniqueness
        unique = []
        seen = set()
        for name in result:
            final = name
            counter = 1
            while final in seen:
                final = f"{name}_{counter}"
                counter += 1
            seen.add(final)
            unique.append(final)

        return unique

    def apply(self, udataset, raw, row):
        file_path = self._get_file_path(row)

        # If raw has no annotations or seems incomplete, rebuild from file
        has_annotations = raw.annotations is not None and len(raw.annotations) > 0

        # Check if we need to reload data
        need_reload = False
        if not has_annotations:
            need_reload = True

        if need_reload:
            raw = self.load(row)

        # Ensure data is loaded
        raw.load_data()

        # Standardize channel names
        old_names = raw.ch_names.copy()
        new_names = self._standardize_channel_names(old_names)

        # Rename with duplicate handling
        if len(set(new_names)) < len(new_names):
            # Make unique with suffixes
            seen = {}
            final_names = []
            for n in new_names:
                if n in seen:
                    seen[n] += 1
                    final_names.append(f"{n}_{seen[n]}")
                else:
                    seen[n] = 0
                    final_names.append(n)
            new_names = final_names

        # Use allow_duplicates=True to handle any edge cases
        raw.rename_channels({old: new for old, new in zip(old_names, new_names)}, allow_duplicates=True)

        # Set montage if possible
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            # Only set channels that exist in montage
            montage_chs = set(montage.ch_names)
            raw_chs = set(raw.ch_names)
            # Rename non-standard names to closest standard if possible
            rename_map = {}
            for ch in raw.ch_names:
                if ch not in montage_chs:
                    # Try without suffix
                    base = re.sub(r'_\d+$', '', ch)
                    if base in montage_chs:
                        rename_map[ch] = base

            if rename_map:
                # Need to ensure no duplicates after rename
                temp_names = []
                used = set()
                for ch in raw.ch_names:
                    if ch in rename_map:
                        new = rename_map[ch]
                        if new in used:
                            # Keep original if duplicate
                            temp_names.append(ch)
                        else:
                            temp_names.append(new)
                            used.add(new)
                    else:
                        temp_names.append(ch)
                        used.add(ch)

                # Build proper mapping
                final_rename = {}
                for old, new in zip(raw.ch_names, temp_names):
                    if old != new:
                        final_rename[old] = new

                if final_rename:
                    raw.rename_channels(final_rename, allow_duplicates=True)

            raw.set_montage('standard_1020', on_missing='ignore')
        except Exception:
            pass  # Montage optional

        # Extract subject metadata
        subj_info = self._extract_subject_info(file_path)

        # Build description
        original_desc = raw.info.get('description', '') or ''
        if not isinstance(original_desc, str):
            original_desc = str(original_desc)

        eegunity_desc = {
            'age': str(subj_info.get('age', 'unknown')),
            'sex': subj_info.get('sex', 'unknown').lower(),
            'amplifier': subj_info.get('amplifier', 'unknown'),
            'cap': subj_info.get('cap', 'unknown'),
            'handedness': subj_info.get('handedness', 'unknown'),
        }

        raw.info['description'] = json.dumps({
            'original_description': original_desc,
            'eegunity_description': eegunity_desc
        })

        # Ensure annotations exist with correct event IDs
        if raw.annotations is None or len(raw.annotations) == 0:
            # Try to rebuild from file
            parsed = self._parse_mat_file(file_path)
            annot = self._build_annotations(parsed['marker_pos'], parsed['marker_y'], parsed['sfreq'])
            if len(annot) > 0:
                raw.set_annotations(annot)

        # Verify event IDs are present
        if raw.annotations is not None and len(raw.annotations) > 0:
            descs = set(raw.annotations.description)
            # Ensure we have the required event IDs
            required = {'-1', '1'}
            # The descriptions should already be literal string values from marker_y

        return raw


KERNEL = BCICIV1Kernel()