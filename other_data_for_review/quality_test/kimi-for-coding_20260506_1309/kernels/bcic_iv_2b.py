import json
import os
import re
from pathlib import Path

import mne
import numpy as np
import pandas as pd
import scipy.io


class BCICompetitionIV2bKernel:
    KERNEL_ID = "bcic_iv_2b"
    HANDLES_UNAVAILABLE = False

    # Channel mapping for BCI Competition IV-2b
    # Source: BCI Competition IV-2b official documentation (desc_2b.pdf)
    # 3 EEG channels: C3, Cz, C4
    # 3 EOG channels: EOG1, EOG2, EOG3
    # Annotator: LLM, Date: 2026-04-08
    # inferred by LLM, needs human review
    CHANNEL_MAP = {
        "EEG:C3": "C3",
        "EEG:Cz": "Cz",
        "EEG:C4": "C4",
        "EOG:EOG1": "EOG1",
        "EOG:EOG2": "EOG2",
        "EOG:EOG3": "EOG3",
        # Handle common variants
        "C3": "C3",
        "Cz": "Cz",
        "C4": "C4",
        "EOG1": "EOG1",
        "EOG2": "EOG2",
        "EOG3": "EOG3",
    }

    # Standard 10-20 montage for the EEG channels
    # Source: BCI Competition IV-2b uses standard 10-20 cap with C3, Cz, C4
    # inferred by LLM, needs human review
    MONTAGE_KIND = "standard_1020"

    def _get_file_path(self, row):
        """Extract file path from row or string."""
        if isinstance(row, (str, os.PathLike)):
            return str(row)
        # Try common keys
        for key in ["File Path", "file_path", "filepath", "path"]:
            val = row.get(key) if hasattr(row, "get") else None
            if val is not None:
                return str(val)
        # Fallback: convert to string if it's a single value
        return str(row)

    def _find_companion_mat(self, gdf_path):
        """Find companion .mat file with classlabel."""
        base = str(gdf_path).replace(".gdf", "").replace(".GDF", "")
        mat_path = base + ".mat"
        if os.path.exists(mat_path):
            return mat_path
        # Try case variations
        for ext in [".mat", ".MAT"]:
            mat_path = base + ext
            if os.path.exists(mat_path):
                return mat_path
        return None

    def _load_classlabel(self, mat_path):
        """Load classlabel from companion .mat file."""
        if mat_path is None or not os.path.exists(mat_path):
            return None
        try:
            mat = scipy.io.loadmat(mat_path, simplify_cells=True)
            if "classlabel" in mat:
                cl = mat["classlabel"]
                if hasattr(cl, "flatten"):
                    cl = cl.flatten()
                return cl
        except Exception:
            pass
        return None

    def _parse_subject_info(self, file_path):
        """Parse subject ID and session type from filename."""
        fname = os.path.basename(file_path)
        # Pattern: B01T, B01E, B0101T, B0101E, B01-01T, etc.
        # Also handle B0204E format (subject 02, session 04, evaluation)
        m = re.match(r"B(\d+)(\d+)?([TE])", fname, re.IGNORECASE)
        if m:
            subject_num = m.group(1)
            session_num = m.group(2) if m.group(2) else ""
            session_type = m.group(3).upper()
            return {
                "subject_id": f"B{subject_num.zfill(2)}",
                "session_type": session_type,  # T=training, E=evaluation
            }
        # Try simpler pattern: B01, B02, etc.
        m = re.match(r"B(\d+)", fname, re.IGNORECASE)
        if m:
            return {
                "subject_id": f"B{m.group(1).zfill(2)}",
                "session_type": "unknown",
            }
        return {"subject_id": "unknown", "session_type": "unknown"}

    def _get_events_from_gdf(self, raw):
        """Extract events from GDF annotations, ensuring literal event IDs."""
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        # GDF files often have annotations with descriptions that may need cleaning
        # but we must preserve the literal numeric codes
        descriptions = []
        for desc in raw.annotations.description:
            # Clean up only formatting, preserve literal value
            s = str(desc).strip()
            # Remove any surrounding quotes or brackets
            s = s.strip("'\"[]")
            descriptions.append(s)

        # Create new annotations with cleaned but literal descriptions
        new_annot = mne.Annotations(
            onset=raw.annotations.onset,
            duration=raw.annotations.duration,
            description=descriptions,
            orig_time=raw.annotations.orig_time,
        )
        raw.set_annotations(new_annot)
        return raw

    def _ensure_required_events(self, raw, file_path):
        """Ensure all required event IDs are present in annotations."""
        required_events = ["1023", "768", "769", "770"]

        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        existing = set(raw.annotations.description)
        missing = set(required_events) - existing

        if not missing:
            return raw

        # Try to find companion .mat for additional event info
        # But we should not fabricate events - just ensure GDF annotations are properly read
        # GDF files should already contain all events; if missing, they may not exist in this file

        # For evaluation files (E), 769/770 may not be present (only 781/783)
        # This is expected per dataset documentation
        return raw

    def _rename_channels(self, raw):
        """Rename channels to standard names."""
        ch_names = raw.ch_names
        rename_map = {}

        for ch in ch_names:
            # Try exact match first
            if ch in self.CHANNEL_MAP:
                rename_map[ch] = self.CHANNEL_MAP[ch]
                continue

            # Try case-insensitive match
            ch_upper = ch.upper()
            for k, v in self.CHANNEL_MAP.items():
                if k.upper() == ch_upper:
                    rename_map[ch] = v
                    break

            # Try with common prefixes removed
            clean = ch
            for prefix in ["EEG ", "EEG:", "EOG ", "EOG:", "EEG", "EOG"]:
                if clean.upper().startswith(prefix.upper()):
                    clean = clean[len(prefix):].strip()
                    break
            if clean in self.CHANNEL_MAP:
                rename_map[ch] = self.CHANNEL_MAP[clean]

        # Ensure unique names
        used = set()
        final_rename = {}
        for old_name, new_name in rename_map.items():
            if new_name in used:
                # Append suffix to make unique
                i = 1
                while f"{new_name}_{i}" in used:
                    i += 1
                new_name = f"{new_name}_{i}"
            final_rename[old_name] = new_name
            used.add(new_name)

        if final_rename:
            raw.rename_channels(final_rename, allow_duplicates=True)

        return raw

    def _set_channel_types(self, raw):
        """Set channel types: EEG for C3,Cz,C4; EOG for EOG1,EOG2,EOG3."""
        eeg_channels = ["C3", "Cz", "C4"]
        eog_channels = ["EOG1", "EOG2", "EOG3"]

        # Map channel types
        ch_types = {}
        for ch in raw.ch_names:
            clean_ch = ch.strip().upper()
            # Remove suffixes from deduplication
            base_ch = clean_ch.split("_")[0]
            if base_ch in [c.upper() for c in eeg_channels]:
                ch_types[ch] = "eeg"
            elif base_ch in [c.upper() for c in eog_channels]:
                ch_types[ch] = "eog"

        if ch_types:
            raw.set_channel_types(ch_types)

        return raw

    def _set_montage(self, raw):
        """Set standard 10-20 montage for EEG channels."""
        try:
            montage = mne.channels.make_standard_montage(self.MONTAGE_KIND)
            # Strip whitespace from channel names for montage matching
            ch_names_stripped = [ch.strip() for ch in raw.ch_names]
            # Create mapping from stripped to original
            rename_for_montage = {ch: ch.strip() for ch in raw.ch_names}
            raw.rename_channels(rename_for_montage, allow_duplicates=True)
            raw.set_montage(montage, on_missing="ignore")
        except Exception:
            pass
        return raw

    def load(self, file_path, **kwargs):
        """Load a BCI Competition IV-2b GDF file."""
        file_path = self._get_file_path(file_path)

        # Load GDF file
        raw = mne.io.read_raw_gdf(file_path, preload=False, verbose=False)

        # Process annotations to ensure literal event IDs
        raw = self._get_events_from_gdf(raw)

        # Ensure required events are present
        raw = self._ensure_required_events(raw, file_path)

        # Rename channels to standard names
        raw = self._rename_channels(raw)

        # Set channel types
        raw = self._set_channel_types(raw)

        # Set montage
        raw = self._set_montage(raw)

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = self._get_file_path(row)

        # Process annotations to ensure literal event IDs
        raw = self._get_events_from_gdf(raw)

        # Ensure required events are present
        raw = self._ensure_required_events(raw, file_path)

        # Rename channels to standard names
        raw = self._rename_channels(raw)

        # Set channel types
        raw = self._set_channel_types(raw)

        # Set montage
        raw = self._set_montage(raw)

        # Parse subject info
        info = self._parse_subject_info(file_path)

        # Original description
        orig_desc = raw.info.get("description", "") or ""

        # Build eegunity_description with explicit canonical defaults
        eegunity_desc = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "standard_1020",
            "handedness": "unknown",
        }

        # Add any extra info from parsing
        eegunity_desc["subject_id"] = info["subject_id"]
        eegunity_desc["session_type"] = info["session_type"]

        raw.info["description"] = json.dumps({
            "original_description": orig_desc,
            "eegunity_description": eegunity_desc,
        })

        return raw


KERNEL = BCICompetitionIV2bKernel()