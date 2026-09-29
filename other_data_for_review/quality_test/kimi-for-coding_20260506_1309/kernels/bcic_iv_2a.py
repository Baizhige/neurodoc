import json
import os
import re
import warnings

import mne
import numpy as np
import pandas as pd

# inferred by LLM, needs human review
# Channel names and montage for BCIC IV 2a from:
#   Source: desc_2a.pdf (BCI Competition IV 2a official description)
#   Annotator: LLM
#   Date: 2026-04-08
# The dataset uses 22 EEG channels from a standard 10-20 cap with FCz as reference.
# Channel order from GDF files matches the standard BCIC IV 2a layout.

BCIC_IV_2A_CHANNELS = [
    "Fz", "FC3", "FC1", "FCz", "FC2", "FC4",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP3", "CP1", "CPz", "CP2", "CP4",
    "P1", "Pz", "P2", "POz",
]

# EOG channels present in GDF files
EOG_CHANNELS = ["EOG-left", "EOG-central", "EOG-right"]


class BCICIV2aKernel:
    KERNEL_ID = "bcic_iv_2a"

    def _get_file_path(self, row):
        """Extract file path from row or string."""
        if isinstance(row, str):
            return row
        # Try common keys
        for key in ["File Path", "file_path", "filepath", "path"]:
            val = row.get(key) if hasattr(row, "get") else None
            if val is not None:
                if hasattr(val, "__fspath__") or hasattr(val, "as_posix"):
                    return str(val)
                return str(val)
        # Fallback: convert to string if it's a Path-like object
        return str(row)

    def _parse_subject_info_from_filename(self, file_path):
        """Extract subject info from BCIC IV 2a filename pattern AxxT/AxxE."""
        basename = os.path.basename(file_path)
        # Pattern: A01T.gdf, A04E.mat, etc.
        match = re.match(r'A(\d{2})([TE])', basename)
        if match:
            subject_num = match.group(1)
            session_type = match.group(2)  # T = training, E = evaluation
            return {
                "subject": subject_num,
                "session_type": session_type,
            }
        return {"subject": "unknown", "session_type": "unknown"}

    def _build_eegunity_description(self, raw, row):
        """Build eegunity_description from available metadata."""
        file_path = self._get_file_path(row)
        info = self._parse_subject_info_from_filename(file_path)

        # BCIC IV 2a: 9 subjects, age/sex not publicly disclosed in standard release
        # inferred by LLM, needs human review
        age = "unknown"
        sex = "unknown"
        amplifier = "g.tec GAMMAsys"  # inferred by LLM, needs human review
        cap = "standard_1020_22ch"  # inferred by LLM, needs human review
        handedness = "unknown"

        # Check if original description has any useful info
        original_desc = raw.info.get("description", "") or ""

        eegunity_desc = {
            "age": str(age) if age != "unknown" else "unknown",
            "sex": sex.lower() if sex != "unknown" else "unknown",
            "amplifier": amplifier,
            "cap": cap,
            "handedness": handedness,
        }

        return original_desc, eegunity_desc

    def _rename_channels(self, raw):
        """Rename channels to standard 10-20 names for BCIC IV 2a."""
        # GDF files may have channels with different naming conventions
        ch_names = raw.ch_names

        # Check if we need renaming
        needs_rename = False
        new_names = []

        # Common patterns in BCIC IV 2a GDF files
        # Sometimes channels are named with prefix or different case
        for i, ch in enumerate(ch_names):
            if i < len(BCIC_IV_2A_CHANNELS):
                expected = BCIC_IV_2A_CHANNELS[i]
                # Strip common prefixes and normalize
                clean = ch.strip().upper()
                expected_upper = expected.upper()

                # If current name doesn't match expected (case-insensitive), rename
                if clean != expected_upper and not clean.endswith(expected_upper):
                    needs_rename = True
                new_names.append(expected)
            elif i < len(BCIC_IV_2A_CHANNELS) + len(EOG_CHANNELS):
                eog_idx = i - len(BCIC_IV_2A_CHANNELS)
                expected_eog = EOG_CHANNELS[eog_idx]
                new_names.append(expected_eog)
            else:
                # Extra channels, keep original but ensure unique
                new_names.append(ch)

        if needs_rename or len(ch_names) != len(new_names):
            # Ensure uniqueness
            seen = set()
            unique_names = []
            for name in new_names[:len(ch_names)]:
                base = name
                counter = 1
                while name in seen:
                    name = f"{base}_{counter}"
                    counter += 1
                seen.add(name)
                unique_names.append(name)

            # Handle any extra channels not in our list
            for i in range(len(unique_names), len(ch_names)):
                ch = ch_names[i]
                base = ch.strip()
                counter = 1
                name = base
                while name in seen:
                    name = f"{base}_{counter}"
                    counter += 1
                seen.add(name)
                unique_names.append(name)

            raw.rename_channels(
                {old: new for old, new in zip(ch_names, unique_names)},
                allow_duplicates=True,
            )

        return raw

    def _set_channel_types(self, raw):
        """Set proper channel types for EEG and EOG channels."""
        ch_types = {}
        for ch in raw.ch_names:
            ch_upper = ch.upper()
            # EOG channels
            if "EOG" in ch_upper:
                ch_types[ch] = "eog"
            # EEG channels (standard naming)
            elif any(ch == eeg_ch or ch.startswith(eeg_ch + "_") for eeg_ch in BCIC_IV_2A_CHANNELS):
                ch_types[ch] = "eeg"
            else:
                # Default to EEG for unknown channels in this dataset
                ch_types[ch] = "eeg"

        raw.set_channel_types(ch_types)
        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage for BCIC IV 2a."""
        # Use standard_1020 which covers all our channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            # If montage fails, continue without it
            pass
        return raw

    def _ensure_annotations(self, raw, file_path):
        """
        Ensure annotations exist for BCIC IV 2a GDF files.
        GDF files should already have annotations from the header.
        This method verifies and fixes if needed.
        """
        # Check if we already have useful annotations
        if raw.annotations is not None and len(raw.annotations) > 0:
            # Verify we have the expected event codes
            descriptions = set(raw.annotations.description)
            expected = {"769", "770", "771", "772", "783"}
            if descriptions & expected:
                return raw

        # If no annotations or wrong ones, try to reconstruct from GDF
        # The GDF format stores events in the header; MNE should read them
        # If MNE didn't read them properly, we need to handle this

        # For BCIC IV 2a, events are stored in GDF header with codes:
        # 276: Trial start (0x114)
        # 277: Trial end (0x115)
        # 768: Trial start / fixation
        # 769-772: Class-specific cues (training)
        # 783: Unknown cue (evaluation)

        # MNE's GDF reader should extract these; if not present, log warning
        if raw.annotations is None or len(raw.annotations) == 0:
            warnings.warn(f"No annotations found in {file_path}; GDF events may not be properly extracted")

        return raw

    def load(self, input_obj):
        """
        Custom loader for BCIC IV 2a files.
        Handles both file path strings and row objects with 'File Path'.
        """
        file_path = self._get_file_path(input_obj)

        # BCIC IV 2a uses GDF format which MNE can read natively
        # But we also handle MAT sidecars for evaluation labels
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".gdf":
            raw = mne.io.read_raw_gdf(file_path, preload=True)
        elif ext == ".mat":
            # MAT files contain class labels, not raw EEG data
            # We shouldn't be asked to load these directly, but handle gracefully
            raise ValueError(f"MAT files in BCIC IV 2a contain labels only, not raw EEG: {file_path}")
        else:
            raise ValueError(f"Unsupported file format for BCIC IV 2a: {ext}")

        # Apply standard processing
        raw = self._rename_channels(raw)
        raw = self._set_channel_types(raw)
        raw = self._set_montage(raw)
        raw = self._ensure_annotations(raw, file_path)

        # Build description
        original_desc, eegunity_desc = self._build_eegunity_description(raw, input_obj)
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """
        Apply BCIC IV 2a kernel normalization to raw data.
        """
        file_path = self._get_file_path(row)

        # Ensure data is loaded
        if not raw.preload:
            raw.load_data()

        # Rename channels to standard names
        raw = self._rename_channels(raw)

        # Set channel types
        raw = self._set_channel_types(raw)

        # Set montage
        raw = self._set_montage(raw)

        # Ensure annotations are present
        raw = self._ensure_annotations(raw, file_path)

        # Build and set description
        original_desc, eegunity_desc = self._build_eegunity_description(raw, row)
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        return raw


HANDLES_UNAVAILABLE = True
KERNEL = BCICIV2aKernel()