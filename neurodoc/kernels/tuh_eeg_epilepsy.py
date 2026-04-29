"""TUH EEG Epilepsy stage1 kernel for EEGUnity.

Dataset: tuh_eeg_epilepsy (v2.0.1)
URL: https://isip.piconepress.com/projects/tuh_eeg/downloads/tuh_eeg_epilepsy/v2.0.1/
DOI: https://doi.org/10.3389/fnins.2016.00196

This kernel handles the TUH EEG Epilepsy Corpus where:
- Each recording is classified as epilepsy or no epilepsy based on patient-level
  clinical diagnosis (not real-time EEG pattern).
- The label is extracted from the directory path (00_epilepsy/ or 01_no_epilepsy/).
- Variable channels (17-41) and sampling rates (250-1000 Hz).
- Sex is not reliably available in the raw files.

The kernel creates:
1. A whole-recording annotation with the epilepsy label.
2. A derived misc channel 'epilepsy_label' broadcasting the binary label.

Required info fields: none (participants.tsv not reliably available in this dataset)
Required native misc channels: none
Derived misc channels: epilepsy_label (from events.tsv:epilepsy:1 or path-derived annotation)

Source: TUH EEG Epilepsy Corpus documentation and directory structure
Annotator: LLM, 2026-04-08
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass

import mne
import numpy as np


def _get_n_level_parent_dir(file_path, n):
    """Get the directory name n levels up from file_path."""
    parent_dir = file_path
    for _ in range(n):
        parent_dir = os.path.dirname(parent_dir)
    return os.path.basename(parent_dir)


def _find_events_tsv(file_path):
    """Find sibling events.tsv file for the given EEG file."""
    # BIDS-style: same directory, same basename with _events.tsv suffix
    base_dir = os.path.dirname(file_path)
    basename = os.path.splitext(os.path.basename(file_path))[0]
    
    # Try BIDS naming first
    events_path = os.path.join(base_dir, f"{basename}_events.tsv")
    if os.path.exists(events_path):
        return events_path
    
    # Try without the extra underscore pattern some TUH files use
    # TUH files are often named like sub-xxx_ses-xxx_task-xxx_eeg.edf
    # events might be sub-xxx_ses-xxx_task-xxx_events.tsv
    parts = basename.split('_')
    if len(parts) >= 2:
        # Try replacing last part with events
        candidate = '_'.join(parts[:-1]) + '_events.tsv'
        events_path = os.path.join(base_dir, candidate)
        if os.path.exists(events_path):
            return events_path
    
    # Look for any events.tsv in the same directory
    for f in os.listdir(base_dir):
        if f.endswith('_events.tsv'):
            return os.path.join(base_dir, f)
    
    return None


def _read_events_tsv(events_path):
    """Read events.tsv and return list of (onset, duration, description) tuples."""
    if events_path is None or not os.path.exists(events_path):
        return []
    
    try:
        import pandas as pd
        df = pd.read_csv(events_path, sep='\t')
        
        events = []
        for _, row in df.iterrows():
            onset = float(row.get('onset', 0))
            duration = float(row.get('duration', 0))
            # Prefer trial_type, fall back to value
            desc = str(row.get('trial_type', row.get('value', 'unknown')))
            events.append((onset, duration, desc))
        
        return events
    except Exception:
        return []


@dataclass
class TuhEegEpilepsyKernel:
    """Stage1 kernel for the tuh-eeg-epilepsy dataset."""

    KERNEL_ID: str = "tuh-eeg-epilepsy-stage1"
    
    # No required info fields from participants.tsv for this dataset
    # (TUH Epilepsy does not reliably provide participants.tsv with standard columns)
    required_info_fields: list = None
    required_native_misc: list = None
    derived_misc_channels: list = None

    def __post_init__(self):
        if self.required_info_fields is None:
            self.required_info_fields = []
        if self.required_native_misc is None:
            self.required_native_misc = []
        if self.derived_misc_channels is None:
            self.derived_misc_channels = ["epilepsy_label"]

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]

        # Determine epilepsy label from directory path (4 levels up)
        # TUH structure: .../00_epilepsy/ or .../01_no_epilepsy/
        parent_dir = _get_n_level_parent_dir(file_path, 4)

        if parent_dir == "00_epilepsy":
            epilepsy_desc = "epilepsy:1"
            epilepsy_binary = 1.0
        elif parent_dir == "01_no_epilepsy":
            epilepsy_desc = "no epilepsy:1"
            epilepsy_binary = 0.0
        else:
            # Fallback: try to infer from any parent directory name
            # LLM 推断，需人类复核
            epilepsy_desc = "unknown"
            epilepsy_binary = np.nan

        # Build eegunity_description
        # Sex is not reliably available in TUH files; use raw.info if present
        raw_sex = raw.info.get("sex", 0)
        if isinstance(raw_sex, int):
            sex_mapping = {0: "unknown", 1: "male", 2: "female"}
            sex_str = sex_mapping.get(raw_sex, "unknown")
        elif isinstance(raw_sex, str):
            sex_str = raw_sex.lower().strip()
            if sex_str not in ("male", "female"):
                sex_str = "unknown"
        else:
            sex_str = "unknown"

        # Age not available in raw files for this dataset
        # LLM 推断，需人类复核
        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap": "unknown",
                "age": "unknown",
                "sex": sex_str,
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Handle events: check for events.tsv sidecar first, then create from path
        events_tsv_path = _find_events_tsv(file_path)
        tsv_events = _read_events_tsv(events_tsv_path)

        # Create annotations
        if tsv_events:
            # Use events.tsv if available
            onsets = [e[0] for e in tsv_events]
            durations = [e[1] for e in tsv_events]
            descriptions = [e[2] for e in tsv_events]
            annotations = mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
        else:
            # Create whole-recording annotation from path-derived label
            duration = raw.times[-1] - raw.times[0] if len(raw.times) > 1 else 0.0
            annotations = mne.Annotations(
                onset=[0.0],
                duration=[duration],
                description=[epilepsy_desc],
            )
        
        raw.set_annotations(annotations)

        # Create derived misc channel: epilepsy_label
        # Broadcast binary label as constant for all time points
        n_samples = len(raw.times)
        epilepsy_data = np.full((1, n_samples), fill_value=epilepsy_binary, dtype=np.float64)
        
        # Handle NaN case for unknown labels
        if np.isnan(epilepsy_binary):
            epilepsy_data.fill(np.nan)

        # Create info for the new channel
        misc_info = mne.create_info(
            ch_names=["epilepsy_label"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"],
        )
        
        # Create RawArray and add to existing raw
        raw_misc = mne.io.RawArray(epilepsy_data, misc_info, verbose=False)
        raw.add_channels([raw_misc], force_update_info=True)

        # Ensure channel type is misc (should already be, but enforce)
        raw.set_channel_types({"epilepsy_label": "misc"})

        # Rename channels to standard names if needed (before set_montage)
        # TUH uses standard 10-20 naming, but some files may have prefixes
        rename_map = {}
        for ch_name in raw.ch_names:
            # Common TUH variations: EEG FP1 -> Fp1, EEG F3 -> F3, etc.
            clean_name = ch_name.strip().upper()
            if clean_name.startswith("EEG "):
                clean_name = clean_name[4:]
            elif clean_name.startswith("EEG"):
                clean_name = clean_name[3:]
            
            # Standard 10-20 corrections
            clean_name = clean_name.strip()
            if clean_name == "FP1":
                clean_name = "Fp1"
            elif clean_name == "FP2":
                clean_name = "Fp2"
            elif clean_name == "FPZ":
                clean_name = "Fpz"
            elif clean_name == "FZ":
                clean_name = "Fz"
            elif clean_name == "CZ":
                clean_name = "Cz"
            elif clean_name == "PZ":
                clean_name = "Pz"
            elif clean_name == "OZ":
                clean_name = "Oz"
            elif clean_name == "T3":
                clean_name = "T7"
            elif clean_name == "T4":
                clean_name = "T8"
            elif clean_name == "T5":
                clean_name = "P7"
            elif clean_name == "T6":
                clean_name = "P8"
            
            if clean_name != ch_name and clean_name:
                rename_map[ch_name] = clean_name

        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage if channels match
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="warn")
        except Exception:
            # Montage may fail for non-standard caps; that's acceptable per rulebook
            pass

        return raw


KERNEL = TuhEegEpilepsyKernel()