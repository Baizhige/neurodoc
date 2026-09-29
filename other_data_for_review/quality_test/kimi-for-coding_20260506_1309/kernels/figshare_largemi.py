import json
import os
import re
from pathlib import Path

import mne
import numpy as np
from scipy.io import loadmat


class FigshareLargeMIKernel:
    KERNEL_ID = "figshare_largemi"
    HANDLES_UNAVAILABLE = True

    # Standard 10-20 channel names from 1Description.txt
    # Source: 1Description.txt in dataset root
    # Annotator: LLM
    # Date: 2026-04-08
    # inferred by LLM, needs human review
    _CHANNEL_NAMES = [
        "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2",
        "A1", "A2", "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz", "X3"
    ]

    # Subject info from 1Description.txt
    # Source: 1Description.txt in dataset root
    # Annotator: LLM
    # Date: 2026-04-08
    # inferred by LLM, needs human review
    _SUBJECT_INFO = {
        "A": {"sex": "male", "age": "20-25"},
        "B": {"sex": "male", "age": "20-25"},
        "C": {"sex": "male", "age": "25-30"},
        "D": {"sex": "male", "age": "25-30"},
        "E": {"sex": "female", "age": "20-25"},
        "F": {"sex": "male", "age": "30-35"},
        "G": {"sex": "male", "age": "30-35"},
        "H": {"sex": "male", "age": "20-25"},
        "I": {"sex": "female", "age": "20-25"},
        "J": {"sex": "female", "age": "20-25"},
        "K": {"sex": "male", "age": "20-25"},
        "L": {"sex": "female", "age": "20-25"},
        "M": {"sex": "female", "age": "20-25"},
    }

    def _get_file_path(self, source):
        """Extract file path from string or row-like object."""
        if hasattr(source, "get"):
            fp = source.get("File Path")
            if fp is not None:
                return str(fp)
        if hasattr(source, "__getitem__") and not isinstance(source, str):
            try:
                return str(source["File Path"])
            except (KeyError, TypeError):
                pass
        return str(source)

    def _extract_subject_letter(self, file_path):
        """Extract subject letter from filename."""
        fname = os.path.basename(file_path)
        # Patterns: CLASubjectX..., FREEFORMSubjectX..., HaLTSubjectX..., etc.
        m = re.search(r'(?:Subject|Subject)([A-Z])', fname, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        # Try alternate pattern
        m = re.search(r'-Subject([A-Z])-', fname, re.IGNORECASE)
        if m:
            return m.group(1).upper()
        return None

    def _parse_mat_file(self, file_path):
        """Parse the .mat file and return data, sfreq, ch_names, markers."""
        mat = loadmat(file_path, simplify_cells=True)

        # Get the 'o' struct
        if "o" in mat:
            o = mat["o"]
        else:
            # Try to find struct
            for k, v in mat.items():
                if not k.startswith("__") and isinstance(v, np.ndarray) and v.dtype.names is not None:
                    o = v
                    break
            else:
                raise ValueError(f"Could not find data struct in {file_path}")

        # Handle nested struct array
        if isinstance(o, np.ndarray) and o.shape == (1, 1):
            o = o[0, 0]
        if hasattr(o, "dtype") and o.dtype.names is not None:
            o = {name: o[name] for name in o.dtype.names}

        # Extract fields
        data = np.array(o["data"])
        sfreq = float(o["sampFreq"])
        n_s = int(o["nS"])

        # Channel names
        ch_names = o.get("chnames")
        if ch_names is None:
            ch_names = self._CHANNEL_NAMES[:data.shape[1]]
        else:
            if isinstance(ch_names, np.ndarray):
                ch_names = [str(c).strip() for c in ch_names.flatten()]
            else:
                ch_names = [str(ch_names).strip()]

        # Ensure we have enough channel names
        while len(ch_names) < data.shape[1]:
            ch_names.append(f"EEG-{len(ch_names)}")

        # Marker channel
        marker = o.get("marker")
        if marker is None:
            marker = np.zeros(n_s, dtype=int)
        else:
            marker = np.array(marker).flatten()

        # bins per microvolt for scaling
        bins_uv = o.get("binsuV", 1)
        if isinstance(bins_uv, np.ndarray):
            bins_uv = float(bins_uv.flatten()[0])
        else:
            bins_uv = float(bins_uv)

        return data, sfreq, ch_names, marker, bins_uv, n_s

    def _build_annotations(self, marker, sfreq):
        """Build MNE annotations from continuous marker channel."""
        # Find transitions in marker
        changes = np.where(np.diff(marker) != 0)[0] + 1
        # Include start and end
        indices = np.concatenate(([0], changes, [len(marker)]))

        onsets = []
        durations = []
        descriptions = []

        for i in range(len(indices) - 1):
            start = indices[i]
            stop = indices[i + 1]
            val = int(marker[start])

            if val != 0:  # Non-zero markers are events
                onset_sec = start / sfreq
                duration_sec = (stop - start) / sfreq
                # Preserve literal marker code
                desc = str(val)
                onsets.append(onset_sec)
                durations.append(duration_sec)
                descriptions.append(desc)

        if len(onsets) == 0:
            return mne.Annotations([], [], [])

        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)

    def _create_raw(self, file_path):
        """Create MNE Raw from .mat file."""
        data, sfreq, ch_names, marker, bins_uv, n_s = self._parse_mat_file(file_path)

        # Transpose to (channels, samples)
        if data.shape[0] == n_s:
            data = data.T

        # Scale from bits to microvolts then to volts
        if bins_uv != 0:
            data = data * (1.0 / bins_uv) * 1e-6

        # Create info
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")

        raw = mne.io.RawArray(data, info, verbose=False)

        # Add annotations from marker channel
        annot = self._build_annotations(marker, sfreq)
        raw.set_annotations(annot)

        return raw

    def _process_raw(self, raw, file_path):
        """Apply standard processing: channel rename, montage, description."""
        # Rename channels to standard names if needed
        current_names = raw.ch_names.copy()

        # Map current names to standard names based on position
        rename_map = {}
        for i, name in enumerate(current_names):
            if i < len(self._CHANNEL_NAMES):
                std_name = self._CHANNEL_NAMES[i]
                if name != std_name:
                    rename_map[name] = std_name

        if rename_map:
            raw.rename_channels(rename_map, allow_duplicates=True)

        # Ensure unique channel names
        seen = set()
        final_names = []
        for name in raw.ch_names:
            if name in seen:
                # Find unique suffix
                suffix = 1
                new_name = f"{name}-{suffix}"
                while new_name in seen:
                    suffix += 1
                    new_name = f"{name}-{suffix}"
                final_names.append(new_name)
                seen.add(new_name)
            else:
                final_names.append(name)
                seen.add(name)

        if final_names != raw.ch_names:
            raw.rename_channels(dict(zip(raw.ch_names, final_names)))

        # Set channel types
        ch_types = {}
        for ch in raw.ch_names:
            if ch == "X3" or ch.startswith("X"):
                ch_types[ch] = "misc"
            else:
                ch_types[ch] = "eeg"
        raw.set_channel_types(ch_types)

        # Set montage for EEG channels
        eeg_chs = [ch for ch in raw.ch_names if ch not in ch_types or ch_types.get(ch) == "eeg"]
        if eeg_chs:
            # Strip whitespace from channel names for montage matching
            montage_map = {ch: ch.strip() for ch in eeg_chs}
            raw.rename_channels(montage_map)
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                pass

        return raw

    def load(self, source):
        """Load a .mat file and return an MNE Raw object."""
        file_path = self._get_file_path(source)
        raw = self._create_raw(file_path)
        # Apply full processing
        return self._process_raw(raw, file_path)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = self._get_file_path(row)
        subject_letter = self._extract_subject_letter(file_path)

        # Get subject info with defaults
        subj_info = self._SUBJECT_INFO.get(subject_letter, {}) if subject_letter else {}

        # Build eegunity_description with explicit canonical defaults
        eegunity_description = {
            "age": str(subj_info.get("age", "")),
            "sex": str(subj_info.get("sex", "")),
            "amplifier": "",
            "cap": "",
            "handedness": "",
        }

        # Get original description
        original_description = raw.info.get("description", "") if raw.info.get("description") is not None else ""

        # Rebuild annotations from the .mat file to ensure they are present
        # The raw passed in may have channels but no annotations
        try:
            _, sfreq, _, marker, _, _ = self._parse_mat_file(file_path)
            annot = self._build_annotations(marker, sfreq)
            raw.set_annotations(annot)
        except Exception:
            pass

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = FigshareLargeMIKernel()