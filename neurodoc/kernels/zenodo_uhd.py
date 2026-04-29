"""zenodo_uhd stage1 kernel for EEGUnity.

Ultra High-Density 256-Channel EEG AAD Dataset.
13 subjects listened to two simultaneously presented stories and attended
to one speaker while ignoring the other. Each file is one trial with
attended direction (left/right) encoded in the filename.

This dataset uses .dap files (BioSemi ActiveTwo format). EEGUnity's
standard parser handles .dap via MNE's read_raw_bdf or internal parser.
The kernel adds whole-trial annotations based on filename parsing and
sets metadata.

Same structure as zenodo_4518754; identical kernel implementation.

Source: 10.1088/1741-2552.ac2629
"""

from __future__ import annotations

import json
import os
import re

import mne
import numpy as np


# No participants.tsv available; all demographic fields unknown.
# Source: analysis.md notes "No age or sex information available"
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核

# BioSemi ActiveTwo with 256-channel ultra-high-density cap
# Source: analysis.md "BioSemi ActiveTwo, Ag/AgCl"
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核

# Standard BioSemi 256-channel naming pattern: A1-A32, B1-B32, C1-C32, D1-D32,
# E1-E32, F1-F32, G1-G32, H1-H32
# These are already standard in BioSemi format; no rename needed typically.
# If the raw has non-standard names, they would need mapping here.
# Source: BioSemi ActiveTwo 256-channel cap documentation
# Annotator: LLM, 2026-04-08
# LLM 推断，需人类复核

# Filename pattern: S{N}_AAD_{trial}{L/R}.dap
# Examples: S1_AAD_1L.dap, S2_AAD_3R.dap
_FILENAME_PATTERN = re.compile(r"S\d+_AAD_.*?([LR])\.dap$", re.IGNORECASE)


def _parse_attended_side(file_path: str) -> str | None:
    """Parse attended side from filename."""
    basename = os.path.basename(file_path)
    match = _FILENAME_PATTERN.search(basename)
    if match:
        side = match.group(1).upper()
        if side == "L":
            return "attend_left"
        elif side == "R":
            return "attend_right"
    return None


@dataclass
class ZenodoUHDKernel:
    """Stage1 kernel for the zenodo_uhd dataset."""

    KERNEL_ID: str = "zenodo-uhd-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Parse attended direction from filename
        attended_event = _parse_attended_side(file_path)
        if attended_event is None:
            # Fallback: try looser pattern matching
            basename = os.path.basename(file_path).upper()
            if "L.DAP" in basename or "_L." in basename or "1L." in basename:
                attended_event = "attend_left"
            elif "R.DAP" in basename or "_R." in basename or "1R." in basename:
                attended_event = "attend_right"
            else:
                attended_event = "unknown"  # LLM 推断，需人类复核

        # Create whole-trial annotation
        # Each file is one trial; annotation spans entire recording
        sfreq = raw.info["sfreq"]
        n_samples = raw.n_times
        duration = n_samples / sfreq

        # Check if annotations already exist (from file format)
        existing_annotations = raw.annotations
        has_existing = len(existing_annotations) > 0

        # Add whole-trial attended annotation
        # This is the primary target label for AAD classification
        trial_annotations = mne.Annotations(
            onset=[0.0],
            duration=[duration],
            description=[attended_event],
        )

        if has_existing:
            # Combine with existing annotations (e.g., stimulus codes)
            raw.set_annotations(existing_annotations + trial_annotations)
        else:
            raw.set_annotations(trial_annotations)

        # Handle any numeric stimulus event codes if present in annotations
        # The analysis mentions codes like 1000001, 100255, 800000, 800001
        # These are from stimulus delivery system; we keep them as-is (raw meta)
        # but ensure the attend_left/attend_right label is present for the task

        # Set channel types for BioSemi 256-channel layout
        # BioSemi channels are typically already typed correctly by MNE
        # but we ensure any non-EEG channels are properly typed
        ch_types = raw.get_channel_types()
        ch_names = raw.ch_names

        # BioSemi often has EXG channels for external sensors
        type_updates = {}
        for ch_name, ch_type in zip(ch_names, ch_types):
            upper_name = ch_name.upper()
            # EXG channels (external inputs, often used for EOG/ECG)
            if upper_name.startswith("EXG") or upper_name.startswith("EX"):
                if ch_type == "eeg":
                    type_updates[ch_name] = "misc"
            # Status/Trigger channel
            elif upper_name in ("STATUS", "TRIGGER", "STI", "STIM"):
                if ch_type == "eeg":
                    type_updates[ch_name] = "stim"
            # CMS/DRL reference channels
            elif upper_name in ("CMS", "DRL"):
                if ch_type == "eeg":
                    type_updates[ch_name] = "misc"

        if type_updates:
            raw.set_channel_types(type_updates)

        # Set montage for 256-channel BioSemi layout
        # BioSemi 256 uses a specific extended 10-20 layout
        # Try to set standard montage; if not available, skip
        try:
            # Check if channel names follow standard BioSemi naming
            # A1-A32, B1-B32, C1-C32, D1-D32, E1-E32, F1-F32, G1-G32, H1-H32
            has_bosemi_names = all(
                re.match(r"^[A-H]\d{1,2}$", name.upper()) or
                re.match(r"^[A-H]0\d$", name.upper())
                for name in ch_names if raw.get_channel_types(picks=[name])[0] == "eeg"
            )

            if has_bosemi_names:
                # Use standard 10-20 extended for high-density caps
                # MNE has biosemi256 montage
                montage = mne.channels.make_standard_montage("biosemi256")
                # Rename channels to match if needed (BioSemi often uses lowercase)
                # First, ensure our channels match the montage naming
                raw.rename_channels({name: name.upper() for name in raw.ch_names})
                raw.set_montage(montage, match_case=False, on_missing="warn")
            else:
                # Try generic standard_1020 if fewer channels or different naming
                try:
                    montage = mne.channels.make_standard_montage("standard_1020")
                    raw.set_montage(montage, match_case=False, on_missing="ignore")
                except Exception:
                    pass  # Skip montage if not applicable
        except Exception:
            # Montage setting failed; continue without spatial info
            # This is acceptable for datasets with non-standard layouts
            pass

        # Build eegunity_description
        # No participants.tsv available for this dataset
        original_desc = raw.info.get("description", "") or ""

        eegunity_description = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "BioSemi ActiveTwo",  # LLM 推断，需人类复核
            "cap": "Ag/AgCl",  # LLM 推断，需人类复核
            "handedness": "unknown",
        }

        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = ZenodoUHDKernel()