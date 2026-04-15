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
                subset_montage = mne.channels.make_eeg montage(ch_pos, head_pos=montage.get_positions().get("head_size", 0.095))
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

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
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
        eeg_channels = [ch for ch in raw.ch_names
                       if ch.startswith("EEG") or ch in _32CH_MONTAGE_CHANNELS]

        if eeg_channels:
            # Set all matching channels as EEG
            for ch in eeg_channels:
                try:
                    raw.set_channel_types({ch: "eeg"})
                except Exception:
                    pass

        # Check for EOG/ECG channels and set types if present
        for ch in raw.ch_names:
            if ch.upper() in ["EOG", "VEOG", "HEOG"]:
                try:
                    raw.set_channel_types({ch: "eog"})
                except Exception:
                    pass
            elif ch.upper() in ["ECG", "EKG"]:
                try:
                    raw.set_channel_types({ch: "ecg"})
                except Exception:
                    pass

        # ----------------------------------------------------------------
        # Step 3: Set montage for 32-channel standard 10-20 cap
        # ----------------------------------------------------------------
        raw = _apply_montage_32ch(raw)

        # ----------------------------------------------------------------
        # Step 4: Standardize reference
        # ----------------------------------------------------------------
        # Most EEG-fMRI recordings use average reference or CSR reference
        # Keep original reference unless explicitly set
        if raw.info.get("meas_date") is not None:
            pass  # Keep original reference

        # ----------------------------------------------------------------
        # Step 5: Downsample from 5000 Hz to 250 Hz
        # ----------------------------------------------------------------
        # Note: MRI gradient artifact removal should be done before this step
        # This kernel flags the data but does not perform artifact removal
        # as it requires specialized tools (e.g., AMRI, EEG-fMRI toolbox)
        if raw.info["sfreq"] == 5000:
            raw = _downsample_eeg(raw, target_sfreq=250)

        # ----------------------------------------------------------------
        # Step 6: Standardize events
        # ----------------------------------------------------------------
        # Get current annotations
        original_annotations = raw.annotations

        if len(original_annotations) > 0:
            # Remap annotation descriptions to standardized format
            new_descriptions = []
            for desc in original_annotations.description:
                # Normalize whitespace in event descriptions
                normalized_desc = desc.strip().replace("  ", " ")
                new_desc = self.EVENT_MAP.get(normalized_desc, normalized_desc)
                new_descriptions.append(new_desc)

            # Create new annotations with standardized descriptions
            standardized_annotations = mne.Annotations(
                onset=original_annotations.onset,
                duration=original_annotations.duration,
                description=new_descriptions,
                orig_time=original_annotations.orig_time,
            )
            raw.set_annotations(standardized_annotations)

        # ----------------------------------------------------------------
        # Step 7: Create super meta annotations (sleep stage labels)
        # ----------------------------------------------------------------
        # These are derived from raw trigger markers per AASM sleep scoring
        # Source: DOI: 10.1016/j.dib.2023.109059
        # Annotator: LLM, 2026-04-08
        # LLM 推断，需人类复核
        if len(raw.annotations) > 0:
            super_meta_onsets = []
            super_meta_durations = []
            super_meta_labels = []
            super_meta_descriptions = []

            for onset, duration, desc in zip(
                raw.annotations.onset,
                raw.annotations.duration,
                raw.annotations.description,
            ):
                if desc in self.SLEEP_STAGE_MAP:
                    super_meta_onsets.append(onset)
                    super_meta_durations.append(duration)
                    sleep_stage_idx = self.SLEEP_STAGE_MAP[desc]
                    super_meta_labels.append(sleep_stage_idx)
                    super_meta_descriptions.append(
                        f"sleep_stage:{self.SLEEP_STAGE_LABELS[sleep_stage_idx]}"
                    )

            if super_meta_onsets:
                # Append super meta as additional annotations with special prefix
                # Using 'meta:sleep_stage:' prefix to distinguish from raw events
                super_annotations = mne.Annotations(
                    onset=super_meta_onsets,
                    duration=super_meta_durations,
                    description=[
                        f"meta:sleep_stage:{label}:{desc}"
                        for label, desc in zip(super_meta_labels, super_meta_descriptions)
                    ],
                    orig_time=raw.annotations.orig_time,
                )

                # Combine with existing annotations
                combined = raw.annotations + super_annotations
                raw.set_annotations(combined)

        # ----------------------------------------------------------------
        # Step 8: Update description with eegunity_description
        # ----------------------------------------------------------------
        # Extract subject info if available from file path or row
        subject_id = row.get("subject_id", "unknown")
        if subject_id == "unknown":
            subject_id = row.get("participant_id", "unknown")

        # Age and sex are not available in the dataset metadata
        # Source: analysis.md - "subject_age: missing", "subject_sex: missing"
        # All subject info set to "unknown" per KERNEL_RULEBOOK requirements
        # Annotator: LLM, 2026-04-08
        # LLM 推断，需人类复核

        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",  # LLM 推断，需人类复核
                "sex": "unknown",  # LLM 推断，需人类复核
                "amplifier": "BrainAmp MR plus",  # LLM 推断，需人类复核 - Source: BrainVision format with EEG-fMRI context
                "cap": "32-channel EEG cap (standard 10-20)",  # LLM 推断，需人类复核
                "handedness": "unknown",  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ----------------------------------------------------------------
        # Step 9: Add kernel metadata to info
        # ----------------------------------------------------------------
        # Store kernel identification and processing notes
        raw.info.setdefault("kernel_info", {})
        raw.info["kernel_info"]["kernel_id"] = self.KERNEL_ID
        raw.info["kernel_info"]["dataset_id"] = "openneuro_ds003768"
        raw.info["kernel_info"]["original_sfreq"] = 5000
        raw.info["kernel_info"]["processed_sfreq"] = int(raw.info["sfreq"])
        raw.info["kernel_info"]["mri_artifact_flag"] = True  # EEG-fMRI data requires artifact removal
        raw.info["kernel_info"]["notes"] = (
            "Downsampled from 5000 Hz to 250 Hz. "
            "MRI gradient artifact removal recommended before epoching. "
            "Sleep stage labels (super meta) derived from S1/S2/S3 triggers."
        )

        # ----------------------------------------------------------------
        # Step 10: Set project/session info if available
        # ----------------------------------------------------------------
        if "subject_id" in row and row["subject_id"] != "unknown":
            raw.info["subject_info"] = {"his_id": str(row["subject_id"])}

        return raw


KERNEL = OpenNeuroDS003768Kernel()