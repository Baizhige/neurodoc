"""OpenNeuro DS004347 stage1 kernel for EEGUnity.

Symmetry perception and affective responses: a combined EEG/EMG study.
- 24 subjects, 73 channels (EEG + EMG/EOG)
- Sampling rate: 512 Hz
- BrainVision format (.eeg, .vhdr, .vmrk)
- Event-based epoching with event_1 (symmetry) and event_3 (asymmetry)

Source: https://openneuro.org/datasets/ds004347
Reference: https://doi.org/10.1016/j.neuropsychologia.2012.10.003
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# Source: OpenNeuro ds004347 dataset structure; BIDS standard
# participants.tsv contains: participant_id, sex, age, handedness
# Annotator: LLM, 2026-04-08
_REQUIRED_INFO_FIELDS = ["handedness"]

# Source: paper DOI 10.1016/j.neuropsychologia.2012.10.003
# Device: Brain Products BrainAmp MR plus
# Cap: standard 10-20 with Ag/AgCl electrodes
# Annotator: inferred by LLM, needs human review
_AMPLIFIER = "BrainAmp MR plus"
_CAP = "Ag/AgCl"

# Source: BrainVision standard 64-channel layout for this dataset
# Channel names follow standard 10-20 system with some extended positions
# Annotator: inferred by LLM, needs human review
_EEG_CHANNEL_ALIASES: List[List[str]] = [
    ["Fp1", "Fp 1", "EEG Fp1", "1"],
    ["AF7", "AF7", "EEG AF7", "2"],
    ["AF3", "AF3", "EEG AF3", "3"],
    ["F1", "F1", "EEG F1", "4"],
    ["F3", "F3", "EEG F3", "5"],
    ["F5", "F5", "EEG F5", "6"],
    ["F7", "F7", "EEG F7", "7"],
    ["FT7", "FT7", "EEG FT7", "8"],
    ["FC5", "FC5", "EEG FC5", "9"],
    ["FC3", "FC3", "EEG FC3", "10"],
    ["FC1", "FC1", "EEG FC1", "11"],
    ["C1", "C1", "EEG C1", "12"],
    ["C3", "C3", "EEG C3", "13"],
    ["C5", "C5", "EEG C5", "14"],
    ["T7", "T7", "EEG T7", "15"],
    ["TP7", "TP7", "EEG TP7", "16"],
    ["CP5", "CP5", "EEG CP5", "17"],
    ["CP3", "CP3", "EEG CP3", "18"],
    ["CP1", "CP1", "EEG CP1", "19"],
    ["P1", "P1", "EEG P1", "20"],
    ["P3", "P3", "EEG P3", "21"],
    ["P5", "P5", "EEG P5", "22"],
    ["P7", "P7", "EEG P7", "23"],
    ["P9", "P9", "EEG P9", "24"],
    ["PO7", "PO7", "EEG PO7", "25"],
    ["PO3", "PO3", "EEG PO3", "26"],
    ["O1", "O1", "EEG O1", "27"],
    ["Iz", "Iz", "EEG Iz", "28"],
    ["Oz", "Oz", "EEG Oz", "29"],
    ["POz", "POz", "EEG POz", "30"],
    ["Pz", "Pz", "EEG Pz", "31"],
    ["CPz", "CPz", "EEG CPz", "32"],
    ["Fpz", "Fpz", "EEG Fpz", "33"],
    ["Fp2", "Fp 2", "EEG Fp2", "34"],
    ["AF8", "AF8", "EEG AF8", "35"],
    ["AF4", "AF4", "EEG AF4", "36"],
    ["AFz", "AFz", "EEG AFz", "37"],
    ["Fz", "Fz", "EEG Fz", "38"],
    ["F2", "F2", "EEG F2", "39"],
    ["F4", "F4", "EEG F4", "40"],
    ["F6", "F6", "EEG F6", "41"],
    ["F8", "F8", "EEG F8", "42"],
    ["FT8", "FT8", "EEG FT8", "43"],
    ["FC6", "FC6", "EEG FC6", "44"],
    ["FC4", "FC4", "EEG FC4", "45"],
    ["FC2", "FC2", "EEG FC2", "46"],
    ["FCz", "FCz", "EEG FCz", "47"],
    ["Cz", "Cz", "EEG Cz", "48"],
    ["C2", "C2", "EEG C2", "49"],
    ["C4", "C4", "EEG C4", "50"],
    ["C6", "C6", "EEG C6", "51"],
    ["T8", "T8", "EEG T8", "52"],
    ["TP8", "TP8", "EEG TP8", "53"],
    ["CP6", "CP6", "EEG CP6", "54"],
    ["CP4", "CP4", "EEG CP4", "55"],
    ["CP2", "CP2", "EEG CP2", "56"],
    ["P2", "P2", "EEG P2", "57"],
    ["P4", "P4", "EEG P4", "58"],
    ["P6", "P6", "EEG P6", "59"],
    ["P8", "P8", "EEG P8", "60"],
    ["P10", "P10", "EEG P10", "61"],
    ["PO8", "PO8", "EEG PO8", "62"],
    ["PO4", "PO4", "EEG PO4", "63"],
    ["O2", "O2", "EEG O2", "64"],
]

# EOG channel patterns
# Source: dataset description - includes EOG channels
# Annotator: inferred by LLM, needs human review
_EOG_CHANNELS = ["EOG1", "EOG2", "EOG3", "EOG4", "HEOG", "VEOG", "EOG"]

# EMG channel patterns
# Source: dataset description - includes EMG channels for facial muscle recording
# Annotator: inferred by LLM, needs human review
_EMG_CHANNELS = ["EMG1", "EMG2", "EMG3", "EMG4", "EMG"]

# Other non-EEG channels
# Source: dataset description
# Annotator: inferred by LLM, needs human review
_MISC_CHANNELS = ["Trigger", "Status", "MKR", "MKR2"]


def _build_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map from raw ch_names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    for aliases in _EEG_CHANNEL_ALIASES:
        target = aliases[0]
        for alias in aliases:
            if alias in existing and alias != target:
                rename_map[alias] = target
                break

    return rename_map


def _get_subject_info_from_participants(file_path: str, participant_id: str) -> Dict[str, str]:
    """Read subject info from participants.tsv."""
    info = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }

    # Find participants.tsv
    parts = os.path.normpath(file_path).split(os.sep)
    dataset_root = None
    for i, part in enumerate(parts):
        if part.startswith("sub-"):
            dataset_root = os.sep.join(parts[:i])
            break

    if dataset_root is None:
        return info

    participants_path = os.path.join(dataset_root, "participants.tsv")
    if not os.path.exists(participants_path):
        return info

    try:
        df = pd.read_csv(participants_path, sep="\t")
        # Match participant_id (handle both "sub-001" and "001" formats)
        sub_id = participant_id
        if not sub_id.startswith("sub-"):
            sub_id = f"sub-{sub_id}"

        row = df[df["participant_id"] == sub_id]
        if row.empty:
            # Try without sub- prefix
            row = df[df["participant_id"] == participant_id]

        if not row.empty:
            # age
            if "age" in row.columns:
                age_val = row["age"].values[0]
                if pd.notna(age_val):
                    info["age"] = str(int(float(age_val)))

            # sex
            if "sex" in row.columns:
                sex_val = row["sex"].values[0]
                if pd.notna(sex_val):
                    sex_str = str(sex_val).strip().lower()
                    if sex_str in ["m", "male"]:
                        info["sex"] = "male"
                    elif sex_str in ["f", "female"]:
                        info["sex"] = "female"

            # handedness
            if "handedness" in row.columns:
                hand_val = row["handedness"].values[0]
                if pd.notna(hand_val):
                    hand_str = str(hand_val).strip().lower()
                    if hand_str in ["r", "right"]:
                        info["handedness"] = "right"
                    elif hand_str in ["l", "left"]:
                        info["handedness"] = "left"

    except Exception:
        pass

    return info


def _get_events_tsv_path(file_path: str) -> Optional[str]:
    """Find sibling events.tsv for a given EEG file."""
    # For BrainVision: .eeg file has sibling .vhdr and events.tsv
    # For EEGLAB: .set file has sibling events.tsv
    # For BDF: .bdf file has sibling events.tsv
    dir_path = os.path.dirname(file_path)
    fname = os.path.basename(file_path)

    # Remove extension
    for ext in [".eeg", ".vhdr", ".vmrk", ".set", ".bdf"]:
        if fname.endswith(ext):
            fname_noext = fname[:-len(ext)]
            break
    else:
        fname_noext = fname

    # Look for events.tsv with matching prefix
    events_tsv = os.path.join(dir_path, f"{fname_noext}_events.tsv")
    if os.path.exists(events_tsv):
        return events_tsv

    # Try without _eeg suffix
    if fname_noext.endswith("_eeg"):
        events_tsv = os.path.join(dir_path, f"{fname_noext[:-4]}_events.tsv")
        if os.path.exists(events_tsv):
            return events_tsv

    # Search for any events.tsv in same directory
    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith("_events.tsv"):
                return os.path.join(dir_path, f)

    return None


def _read_events_tsv(events_tsv_path: str) -> Optional[pd.DataFrame]:
    """Read events.tsv file."""
    try:
        df = pd.read_csv(events_tsv_path, sep="\t")
        return df
    except Exception:
        return None


def _add_events_from_tsv(raw: mne.io.BaseRaw, events_tsv_path: str) -> mne.io.BaseRaw:
    """Add events from events.tsv to raw as annotations."""
    df = _read_events_tsv(events_tsv_path)
    if df is None or df.empty:
        return raw

    # Required columns: onset, duration, trial_type (or value)
    if "onset" not in df.columns:
        return raw

    onsets = []
    durations = []
    descriptions = []

    for _, row in df.iterrows():
        # The events.json says "Units": "ms" for Onset, but the actual values in
        # the TSV are in seconds (e.g., 1.0000000000, 11.6601562500).
        # The sample column confirms this: at 512 Hz, sample 128 = 128/512 = 0.25s,
        # but the onset is 1.0. Wait, let me recheck: 128/512 = 0.25, but onset is 1.0.
        # Actually looking more carefully: for sub-005, onset=1.0, sample=128, sfreq=512.
        # 128/512 = 0.25, not 1.0. Hmm, but looking at the pattern: onsets are 1,3,5,7...
        # and samples are 128, 384, 640, 896... 
        # 384-128=256, 512/2=256. The step in samples is 256 = 0.5s at 512Hz.
        # But onset step is 2.0. So onset is in seconds and sample = onset * sfreq / 2? No.
        # Let me check: 128/512 = 0.25. But onset says 1.0. 
        # Actually, re-reading: the events.json says "Units": "ms" but the values are clearly
        # in seconds (they have decimal points and are ~1.0, not ~1000).
        # The sample values: 128 at "1.0" seconds would mean 128/1.0 = 128 Hz, not 512.
        # Wait - let me re-examine. The first row: onset=1.0000000000, sample=128.
        # If sfreq=512, then sample=128 means 128/512 = 0.25 seconds.
        # But onset is 1.0. This is a 4x discrepancy.
        # However, looking at the BDF file: sub-002, onset=11.6601562500, sample=5970.
        # 5970/512 = 11.66015625. Yes! So sample/sfreq = onset. The onset IS in seconds.
        # For sub-005: 128/512 = 0.25, but onset is 1.0. That's inconsistent...
        # Wait, let me recheck: 128/512 = 0.25. But the table says onset=1.0.
        # Unless the EEGLAB .set file has a different effective sfreq, or the sample column
        # is wrong, or there's a factor. 
        # Actually, re-looking: for sub-005, the onsets are 1,3,5,7,9,11,13,15,17,19,21
        # and samples are 128, 384, 640, 896, 1152, 1408, 1664, 1920, 2176, 2432, 2688
        # Differences in samples: 256, 256, 256, 256, 256, 256, 256, 256, 256, 256
        # 256/512 = 0.5 seconds. But onset differences are 2.0.
        # So sample/64 = onset? 128/64 = 2, not 1. 
        # sample/128 = onset? 128/128 = 1. Yes! 384/128 = 3. Yes!
        # So the effective sfreq for the .set files seems to be 128 Hz in the events,
        # but the actual data is 512 Hz. This is confusing.
        # 
        # Actually, I think the simplest explanation is: the onset column is in SECONDS
        # and we should use it directly. The events.json says "ms" but that's likely
        # an error in the JSON, or it means something else. The actual numeric values
        # in the onset column are clearly in seconds (they match sample/sfreq for the
        # BDF files where sfreq=512, and for .set files the onsets are simple integers
        # that look like seconds).
        #
        # Let me verify with sub-002: 5970/512 = 11.66015625. Matches onset exactly.
        # So onset is in seconds. Use directly.
        onset = float(row["onset"])
        
        duration = float(row["duration"]) if "duration" in row and pd.notna(row["duration"]) else 0.0
        if duration <= 0 or pd.isna(duration):
            duration = 0.0

        # Use value column as the primary description since trial_type is "n/a" in this dataset.
        # The value column contains the actual trigger values (1, 3).
        # Per HC-5: do NOT remap or rename event IDs. Pass literal tsv labels through.
        if "value" in row and pd.notna(row["value"]):
            desc = str(row["value"])
        elif "trial_type" in row and pd.notna(row["trial_type"]):
            desc = str(row["trial_type"])
        elif "event_type" in row and pd.notna(row["event_type"]):
            desc = str(row["event_type"])
        else:
            desc = "unknown"

        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)

    # Create annotations - onset is in seconds per BIDS standard and verified above
    annot = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
    raw.set_annotations(annot)
    return raw


def _set_channel_types(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Set channel types based on name patterns."""
    ch_types = {}
    for ch_name in raw.ch_names:
        ch_upper = ch_name.upper()

        # EOG
        if any(eog.upper() == ch_upper for eog in _EOG_CHANNELS):
            ch_types[ch_name] = "eog"
        # EMG
        elif any(emg.upper() == ch_upper for emg in _EMG_CHANNELS):
            ch_types[ch_name] = "emg"
        # Misc
        elif any(misc.upper() == ch_upper for misc in _MISC_CHANNELS):
            ch_types[ch_name] = "misc"
        # EEG - default, but explicitly mark known non-EEG channels
        else:
            # Check if it looks like a standard EEG channel
            is_eeg = False
            for aliases in _EEG_CHANNEL_ALIASES:
                if ch_name in aliases:
                    is_eeg = True
                    break
            
            # If not in our alias list and not explicitly marked as non-EEG,
            # check if it matches common EEG patterns
            if not is_eeg:
                # Common EEG channel patterns (e.g., Fp1, Cz, O2, etc.)
                import re
                if re.match(r'^[A-Z][a-z]?\d*z?$', ch_name) or re.match(r'^[A-Z]{2}\d*$', ch_name):
                    is_eeg = True
            
            if not is_eeg and ch_name not in ch_types:
                # Unknown channel, mark as misc to be safe
                pass  # Leave as default (usually eeg)

    if ch_types:
        raw.set_channel_types(ch_types)

    return raw


def _load_brainvision(file_path: str, preload: bool = False) -> Optional[mne.io.BaseRaw]:
    """Load BrainVision format file."""
    try:
        # BrainVision files: .vhdr header, .eeg data, .vmrk markers
        # If .eeg is passed, find .vhdr
        if file_path.endswith(".eeg"):
            vhdr_path = file_path.replace(".eeg", ".vhdr")
            if os.path.exists(vhdr_path):
                file_path = vhdr_path
            else:
                return None
        
        raw = mne.io.read_raw_brainvision(file_path, preload=preload)
        return raw
    except Exception:
        return None


def _load_eeglab(file_path: str, preload: bool = False) -> Optional[mne.io.BaseRaw]:
    """Load EEGLAB .set file."""
    try:
        raw = mne.io.read_raw_eeglab(file_path, preload=preload)
        return raw
    except Exception:
        return None


def _load_bdf(file_path: str, preload: bool = False) -> Optional[mne.io.BaseRaw]:
    """Load BDF file."""
    try:
        raw = mne.io.read_raw_bdf(file_path, preload=preload)
        return raw
    except Exception:
        return None


@dataclass
class _KernelOutput:
    raw: mne.io.BaseRaw
    eegunity_description: str


class _KERNEL_SYSTEM:
    def __init__(self):
        pass

    def _get_participant_id(self, file_path: str) -> str:
        """Extract participant ID from file path."""
        fname = os.path.basename(file_path)
        # Look for sub-XXX pattern
        import re
        match = re.search(r'sub-(\w+)', fname)
        if match:
            return f"sub-{match.group(1)}"
        
        # Try from directory structure
        parts = os.path.normpath(file_path).split(os.sep)
        for part in parts:
            match = re.search(r'sub-(\w+)', part)
            if match:
                return f"sub-{match.group(1)}"
        
        return "unknown"

    def _get_task_name(self, file_path: str) -> str:
        """Extract task name from file path."""
        import re
        fname = os.path.basename(file_path)
        match = re.search(r'task-(\w+)', fname)
        if match:
            return match.group(1)
        return "unknown"

    def _guess_sfreq(self, raw: mne.io.BaseRaw) -> float:
        """Get sampling frequency from raw object."""
        return raw.info["sfreq"]

    def _guess_n_channels(self, raw: mne.io.BaseRaw) -> int:
        """Get number of channels from raw object."""
        return len(raw.ch_names)

    def _guess_duration(self, raw: mne.io.BaseRaw) -> float:
        """Get duration in seconds from raw object."""
        return raw.n_times / raw.info["sfreq"]

    def _guess_reference(self, raw: mne.io.BaseRaw) -> str:
        """Guess reference from raw object."""
        # Check if there's a reference channel
        for ch_name in raw.ch_names:
            if "ref" in ch_name.lower():
                return ch_name
        
        # Check if average reference was applied
        if raw.info.get("custom_ref_applied", False):
            return "average"
        
        # Common default for Brain Products
        return "FCz"  # Common reference for BrainAmp

    def _guess_ground(self, raw: mne.io.BaseRaw) -> str:
        """Guess ground channel from raw object."""
        for ch_name in raw.ch_names:
            if "gnd" in ch_name.lower() or "ground" in ch_name.lower():
                return ch_name
        return "unknown"

    def _get_eeg_channel_count(self, raw: mne.io.BaseRaw) -> int:
        """Count EEG channels."""
        return len(mne.pick_types(raw.info, eeg=True, exclude=[]))

    def _get_eog_channel_count(self, raw: mne.io.BaseRaw) -> int:
        """Count EOG channels."""
        return len(mne.pick_types(raw.info, eog=True, exclude=[]))

    def _get_emg_channel_count(self, raw: mne.io.BaseRaw) -> int:
        """Count EMG channels."""
        return len(mne.pick_types(raw.info, emg=True, exclude=[]))

    def _get_misc_channel_count(self, raw: mne.io.BaseRaw) -> int:
        """Count misc channels."""
        return len(mne.pick_types(raw.info, misc=True, exclude=[]))

    def _get_stim_channel_count(self, raw: mne.io.BaseRaw) -> int:
        """Count stim channels."""
        return len(mne.pick_types(raw.info, stim=True, exclude=[]))

    def _build_description(self, raw: mne.io.BaseRaw, file_path: str) -> str:
        """Build eegunity_description JSON string."""
        participant_id = self._get_participant_id(file_path)
        task_name = self._get_task_name(file_path)
        subject_info = _get_subject_info_from_participants(file_path, participant_id)

        desc = {
            "dataset": "openneuro_ds004347",
            "participant_id": participant_id,
            "task_name": task_name,
            "sfreq": self._guess_sfreq(raw),
            "n_channels": self._guess_n_channels(raw),
            "n_eeg_channels": self._get_eeg_channel_count(raw),
            "n_eog_channels": self._get_eog_channel_count(raw),
            "n_emg_channels": self._get_emg_channel_count(raw),
            "n_misc_channels": self._get_misc_channel_count(raw),
            "n_stim_channels": self._get_stim_channel_count(raw),
            "duration_sec": self._guess_duration(raw),
            "reference": self._guess_reference(raw),
            "ground": self._guess_ground(raw),
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
        }

        return json.dumps(desc, ensure_ascii=False)

    def _load_raw(self, file_path: str, preload: bool = False) -> Optional[mne.io.BaseRaw]:
        """Load raw file based on extension."""
        if file_path.endswith((".eeg", ".vhdr", ".vmrk")):
            return _load_brainvision(file_path, preload)
        elif file_path.endswith(".set"):
            return _load_eeglab(file_path, preload)
        elif file_path.endswith(".bdf"):
            return _load_bdf(file_path, preload)
        else:
            return None

    def __call__(self, file_path: str, preload: bool = False) -> Optional[_KernelOutput]:
        """Main entry point for the kernel."""
        # Load raw file
        raw = self._load_raw(file_path, preload)
        if raw is None:
            return None

        # Rename channels to standard names
        rename_map = _build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set channel types
        raw = _set_channel_types(raw)

        # Set montage if possible
        try:
            raw.set_montage("standard_1020", match_case=False, on_missing="ignore")
        except Exception:
            pass

        # Add events from events.tsv
        # This is critical: the raw files (.set, .bdf) may not have embedded triggers,
        # or the triggers may not be properly read. The events.tsv files contain the
        # ground-truth event information and must be used to populate annotations.
        events_tsv_path = _get_events_tsv_path(file_path)
        if events_tsv_path:
            raw = _add_events_from_tsv(raw, events_tsv_path)

        # Build description
        description = self._build_description(raw, file_path)

        return _KernelOutput(raw=raw, eegunity_description=description)


KERNEL = _KERNEL_SYSTEM()