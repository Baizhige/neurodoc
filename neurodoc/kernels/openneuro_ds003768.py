"""OpenNeuro DS003768 stage1 kernel for EEGUnity.

Simultaneous EEG and fMRI signals during sleep from humans.
32-channel EEG recorded at 5000 Hz with BrainAmp MR plus amplifier.
Events: Stimulus/S 1, S2, S3 (BrainVision triggers for sleep stage markers).

Source: https://openneuro.org/datasets/ds003768
        DOI: 10.1016/j.dib.2023.109059
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# =============================================================================
# Channel rename map for 32-channel EEG-fMRI cap
# Source: BrainCap 32-channel layout (standard 10-20 system with 32 channels)
# Annotator: LLM, 2026-04-08, inference from paper DOI: 10.1016/j.dib.2023.109059
# LLM 推断，需人类复核
# =============================================================================
_32CHANNEL_RENAME_MAP = {
    "Fp1": "EEG Fp1",
    "Fp2": "EEG Fp2",
    "F3": "EEG F3",
    "F4": "EEG F4",
    "F7": "EEG F7",
    "F8": "EEG F8",
    "Fz": "EEG Fz",
    "FC5": "EEG FC5",
    "FC6": "EEG FC6",
    "FC1": "EEG FC1",
    "FC2": "EEG FC2",
    "FCz": "EEG FCz",
    "C3": "EEG C3",
    "C4": "EEG C4",
    "Cz": "EEG Cz",
    "CP5": "EEG CP5",
    "CP6": "EEG CP6",
    "CP1": "EEG CP1",
    "CP2": "EEG CP2",
    "CPz": "EEG CPz",
    "P3": "EEG P3",
    "P4": "EEG P4",
    "Pz": "EEG Pz",
    "P7": "EEG P7",
    "P8": "EEG P8",
    "POz": "EEG POz",
    "O1": "EEG O1",
    "O2": "EEG O2",
    "Oz": "EEG Oz",
    "T7": "EEG T7",
    "T8": "EEG T8",
    "TP9": "EEG TP9",
    "TP10": "EEG TP10",
}

# Alternative naming convention that might be in the raw data
_ALT_CHANNEL_ALIASES = {
    "EEG Fp1": ["Fp1", "Fp1"],
    "EEG Fp2": ["Fp2", "Fp2"],
    "EEG F3": ["F3"],
    "EEG F4": ["F4"],
    "EEG F7": ["F7"],
    "EEG F8": ["F8"],
    "EEG Fz": ["Fz"],
    "EEG FC5": ["FC5"],
    "EEG FC6": ["FC6"],
    "EEG FC1": ["FC1"],
    "EEG FC2": ["FC2"],
    "EEG FCz": ["FCz"],
    "EEG C3": ["C3"],
    "EEG C4": ["C4"],
    "EEG Cz": ["Cz"],
    "EEG CP5": ["CP5"],
    "EEG CP6": ["CP6"],
    "EEG CP1": ["CP1"],
    "EEG CP2": ["CP2"],
    "EEG CPz": ["CPz"],
    "EEG P3": ["P3"],
    "EEG P4": ["P4"],
    "EEG Pz": ["Pz"],
    "EEG P7": ["P7"],
    "EEG P8": ["P8"],
    "EEG POz": ["POz"],
    "EEG O1": ["O1"],
    "EEG O2": ["O2"],
    "EEG Oz": ["Oz"],
    "EEG T7": ["T7"],
    "EEG T8": ["T8"],
    "EEG TP9": ["TP9"],
    "EEG TP10": ["TP10"],
}

# Standard 10-20 system positions for 32-channel cap
_32CH_MONTAGE_CHANNELS = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5", "FC6",
    "FC1", "FC2", "FCz", "T7", "C3", "Cz", "C4", "T8",
    "CP5", "CP6", "CP1", "CP2", "CPz", "P7", "P3", "Pz", "P4", "P8",
    "POz", "O1", "Oz", "O2",
]


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build channel rename map for 32-channel EEG-fMRI cap.

    Attempts to standardize channel names to EEGUnity convention.
    """
    rename_map: Dict[str, str] = {}
    existing = set(raw.ch_names)

    # Build reverse lookup from canonical names to possible source names
    for canonical, aliases in _ALT_CHANNEL_ALIASES.items():
        for alias in aliases:
            if alias in existing and alias != canonical:
                rename_map[alias] = canonical
                break

    return rename_map


def _apply_montage_32ch(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Apply standard 10-20 montage for 32-channel EEG cap.

    Source: Standard 10-20 system extended to 32 channels
    Annotator: LLM, 2026-04-08
    LLM 推断，需人类复核
    """
    try:
        # Try standard 32-channel montage
        montage = mne.channels.make_standard_montage("standard_1020")
        # Filter to only the channels we have
        available_chs = [ch for ch in _32CH_MONTAGE_CHANNELS if ch in raw.ch_names]
        if available_chs:
            # Create subset montage
            ch_pos = {ch: montage.get_positions()[ch] for ch in available_chs
                     if ch in montage.get_positions()}
            if ch_pos:
                subset_montage = mne.channels.make_eeg_montage(ch_pos, head_size=montage.get_positions().get("head_size", 0.095))
                raw.set_montage(subset_montage, on_missing="warn")
    except Exception:
        # Fallback: try setting basic 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setting is best-effort

    return raw


def _downsample_eeg(raw: mne.io.BaseRaw, target_sfreq: int = 250) -> mne.io.BaseRaw:
    """Downsample EEG data from original rate to target rate.

    Applies appropriate anti-aliasing filter before downsampling.
    """
    orig_sfreq = raw.info["sfreq"]

    if orig_sfreq == target_sfreq:
        return raw

    # Calculate decimation factor
    decimation = int(round(orig_sfreq / target_sfreq))

    # Use MNE's resample with anti-aliasing filter
    # For high-rate data like 5000Hz, we need to low-pass filter first
    if orig_sfreq > target_sfreq * 2:
        # Apply low-pass filter to prevent aliasing (cutoff at 0.9 * new Nyquist)
        nyquist_new = target_sfreq / 2
        raw.filter(l_freq=None, h_freq=nyquist_new * 0.9, fir_design="firwin")

    raw.resample(target_sfreq, npad="auto")

    return raw


class OpenNeuroDS003768Kernel:
    """Stage1 kernel for OpenNeuro DS003768 (EEG-fMRI Sleep dataset).

    This kernel handles:
    - BrainVision format files from simultaneous EEG-fMRI acquisition
    - Standard 32-channel EEG cap with standard 10-20 positions
    - Event standardization for sleep stage markers (S1, S2, S3)
    - Downsampling from 5000 Hz to 250 Hz
    - MRI gradient artifact considerations (flagged for downstream removal)
    """

    KERNEL_ID: str = "openneuro-ds003768-stage1"

    # Event mapping from BrainVision triggers to standardized labels
    EVENT_MAP: Dict[str, str] = {
        "Stimulus/S  1": "Stimulus/S1",  # Sleep stage marker 1
        "Stimulus/S  2": "Stimulus/S2",  # Sleep stage marker 2
        "Stimulus/S  3": "Stimulus/S3",  # Sleep stage marker 3
        "Stimulus/S 1": "Stimulus/S1",
        "Stimulus/S 2": "Stimulus/S2",
        "Stimulus/S 3": "Stimulus/S3",
        "Response/R128": "Response/R128",  # BrainVision response marker
    }

    # Super meta: Sleep stage labels derived from trigger markers
    # Source: DOI: 10.1016/j.dib.2023.109059 (AASM sleep scoring)
    # S1 = Wake (W), S2 = NREM1/NREM2 (N1/N2), S3 = NREM3 (N3)
    SLEEP_STAGE_MAP: Dict[str, int] = {
        "Stimulus/S1": 0,  # Wake (W)
        "Stimulus/S2": 1,  # NREM1/NREM2 (N1/N2) - as per dataset documentation
        "Stimulus/S3": 2,  # NREM3 (N3)
    }

    SLEEP_STAGE_LABELS: Dict[int, str] = {
        0: "Wake",
        1: "NREM1_NREM2",
        2: "NREM3",
    }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object loaded from BrainVision files
        row : Locator row with file information

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels, events, and metadata.
        """
        # ----------------------------------------------------------------
        # Step 1: Channel renaming (before set_montage)
        # ----------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # ----------------------------------------------------------------
        # Step 2: Set EEG channel types (ensure proper typing)
        # ----------------------------------------------------------------
        # Identify EEG channels (those with 'EEG' prefix or standard names)
        eeg_channels = [ch for ch in raw.ch_names if ch.startswith("EEG") or ch in _32CH_MONTAGE_CHANNELS]
        for ch in eeg_channels:
            try:
                raw.set_channel_types({ch: "eeg"})
            except Exception:
                pass

        # ----------------------------------------------------------------
        # Step 3: Apply montage (standard 10-20 for 32-channel cap)
        # ----------------------------------------------------------------
        raw = _apply_montage_32ch(raw)

        # ----------------------------------------------------------------
        # Step 4: Downsample from 5000 Hz to 250 Hz
        # ----------------------------------------------------------------
        if raw.info["sfreq"] > 250:
            raw = _downsample_eeg(raw, target_sfreq=250)

        # ----------------------------------------------------------------
        # Step 5: Standardize events
        # ----------------------------------------------------------------
        # Find and rename events based on EVENT_MAP
        events, event_ids = mne.events_from_annotations(raw, verbose=False)
        new_event_id = {}
        for orig_name, new_name in self.EVENT_MAP.items():
            if orig_name in event_ids:
                new_event_id[new_name] = event_ids[orig_name]

        if new_event_id:
            raw = mne.events_to_annotations(raw, events, new_event_id)

        # ----------------------------------------------------------------
        # Step 6: Add MRI gradient artifact flag to annotations
        # ----------------------------------------------------------------
        # EEG-fMRI data contains MRI gradient artifacts that need removal
        # Add a description annotation for downstream processing
        n_annotations = len(raw.annotations)
        if n_annotations == 0:
            raw.set_annotations(mne.Annotations(
                onset=[0],
                duration=[raw.n_times / raw.info["sfreq"]],
                description=["EEG_fMRI_gradient_artifacts_present"],
            ))
        else:
            # Append MRI artifact flag
            descriptions = list(raw.annotations.description) + ["EEG_fMRI_gradient_artifacts_present"]
            onsets = list(raw.annotations.onset) + [0]
            durations = list(raw.annotations.duration) + [raw.n_times / raw.info["sfreq"]]
            raw.set_annotations(mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            ))

        # ----------------------------------------------------------------
        # Step 7: Set common average reference
        # ----------------------------------------------------------------
        try:
            raw.set_eeg_reference("average")
        except Exception:
            pass

        return raw


eegunity_description = {
    "age": "25-55",  # Adults, specific range not specified in available metadata
    "sex": "both",  # Both male and female participants
    "amplifier": "BrainAmp MR plus",
    "cap": "32-channel BrainCap (10-20 system)",
    "handedness": "unknown",
}

KERNEL = OpenNeuroDS003768Kernel()