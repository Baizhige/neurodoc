"""Dataset-specific kernel for openneuro ds007181.

Sleep-stage annotations live in events.tsv under the `stage` column rather than
the usual BIDS label columns. Rebuild long annotations from that column so the
locator can reflect 30-second PSG staging directly.

Source: https://openneuro.org/datasets/ds007181
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Optional

import mne
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from kernels.bids import _find_events_tsv
from kernels.openneuro_specific._base import OpenNeuroBaseKernel

STAGE_MAP = {
    "W": "Sleep stage W",
    "N1": "Sleep stage N1",
    "N2": "Sleep stage N2",
    "N3": "Sleep stage N3",
    "R": "Sleep stage R (REM)",
    "REM": "Sleep stage R (REM)",
}

# Source: OpenNeuro ds007181 dataset description and typical PSG 24-channel montage
# LLM 推断，需人类复核
_AMPLIFIER = "unknown"
_CAP = "unknown"
_HANDEDNESS = "unknown"


def _summarize_annotations(raw: mne.io.BaseRaw) -> str:
    counts = Counter(str(desc) for desc in raw.annotations.description if str(desc).strip())
    if not counts:
        return "no_events"
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{label}: {count}" for label, count in ordered)


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for standard PSG 24-channel EEG montage.

    The dataset uses standard 10-20 electrode positions. Attempt to normalize
    any non-standard naming variants to the standard names before montage.
    Source: 10-20 international electrode system standard naming
    """
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names

    # Common alias patterns for 10-20 system
    alias_groups = [
        ("Fp1", ["Fp1", "EEG Fp1", "EEG-Fp1"]),
        ("Fp2", ["Fp2", "EEG Fp2", "EEG-Fp2"]),
        ("F7", ["F7", "EEG F7", "EEG-F7"]),
        ("F3", ["F3", "EEG F3", "EEG-F3"]),
        ("Fz", ["Fz", "EEG Fz", "EEG-Fz"]),
        ("F4", ["F4", "EEG F4", "EEG-F4"]),
        ("F8", ["F8", "EEG F8", "EEG-F8"]),
        ("T3", ["T3", "T7", "EEG T3", "EEG-T3"]),
        ("C3", ["C3", "EEG C3", "EEG-C3"]),
        ("Cz", ["Cz", "EEG Cz", "EEG-Cz"]),
        ("C4", ["C4", "EEG C4", "EEG-C4"]),
        ("T4", ["T4", "T8", "EEG T4", "EEG-T4"]),
        ("T5", ["T5", "P7", "EEG T5", "EEG-T5"]),
        ("P3", ["P3", "EEG P3", "EEG-P3"]),
        ("Pz", ["Pz", "EEG Pz", "EEG-Pz"]),
        ("P4", ["P4", "EEG P4", "EEG-P4"]),
        ("T6", ["T6", "P8", "EEG T6", "EEG-T6"]),
        ("O1", ["O1", "EEG O1", "EEG-O1"]),
        ("Oz", ["Oz", "EEG Oz", "EEG-Oz"]),
        ("O2", ["O2", "EEG O2", "EEG-O2"]),
        ("A1", ["A1", "LE", "EEG A1"]),
        ("A2", ["A2", "RE", "EEG A2"]),
        ("EOG-left", ["EOG-L", "EOG1", "LEOG"]),
        ("EOG-right", ["EOG-R", "EOG2", "REOG"]),
        ("EMG-chin", ["Chin", "EMG", "EMG-chin"]),
    ]

    existing_names = set(ch_names)
    for target_name, aliases in alias_groups:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    return rename_map


@dataclass
class OpenNeuroDS007181Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for OpenNeuro ds007181 dataset.

    Dataset includes resting-state PSG/EEG recordings from patients with
    zoster-associated neuralgia and healthy controls. Sleep stage annotations
    are stored in events.tsv with the `stage` column.
    """

    KERNEL_ID: str = "openneuro-ds007181"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object loaded by EEGUnity
        row : Locator row with file path and metadata

        Returns
        -------
        mne.io.BaseRaw : Preprocessed Raw object
        """
        # Call parent to handle base BIDS processing
        raw = super().apply(udataset, raw, row)

        # Rename channels before setting montage
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
            print(f"[{self.KERNEL_ID}] Renamed channels: {rename_map}")

        # Try to set standard 10-20 montage for EEG channels
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, raise_errors=False)
        except Exception:
            pass

        # Read sleep stage annotations from events.tsv
        events_path = _find_events_tsv(row["File Path"])
        if events_path is not None and os.path.exists(events_path):
            try:
                events_df = pd.read_csv(events_path, sep="\t")
                required = {"onset", "duration", "stage"}
                if required.issubset(events_df.columns):
                    onsets = []
                    durations = []
                    descriptions = []
                    eps = 1.0 / float(raw.info["sfreq"])

                    for _, event_row in events_df.iterrows():
                        onset = event_row.get("onset")
                        duration = event_row.get("duration")
                        stage = str(event_row.get("stage", "")).strip()
                        if pd.isna(onset) or pd.isna(duration) or not stage:
                            continue
                        if stage.lower() in {"n/a", "na", "nan", ""}:
                            continue
                        label = STAGE_MAP.get(stage, stage)
                        try:
                            duration_value = float(duration)
                        except Exception:
                            continue
                        onsets.append(float(onset))
                        durations.append(duration_value if duration_value > 0 else eps)
                        descriptions.append(label)

                    if descriptions:
                        raw.set_annotations(
                            mne.Annotations(
                                onset=onsets,
                                duration=durations,
                                description=descriptions,
                            )
                        )
                        print(f"[{self.KERNEL_ID}] Set {len(descriptions)} sleep stage annotations")
            except Exception as e:
                print(f"[{self.KERNEL_ID}] Failed to read events.tsv: {e}")

        # Update description with eegunity_description
        try:
            description_dict = json.loads(raw.info.get("description", "") or "{}")
        except Exception:
            description_dict = {}

        original_description = description_dict.get("original_description", "")

        # Get subject info from participants.tsv if available
        age = description_dict.get("eegunity_description", {}).get("age", "unknown")
        sex = description_dict.get("eegunity_description", {}).get("sex", "unknown")

        # Ensure age is string and sex is lowercase
        if not isinstance(age, str):
            age = str(age) if age else "unknown"
        if isinstance(sex, str):
            sex = sex.lower()
        else:
            sex = "unknown"

        eegunity_description = {
            "age": age,
            "sex": sex,
            "amplifier": _AMPLIFIER,
            "cap": _CAP,
            "handedness": _HANDEDNESS,
        }

        description_dict = {
            "original_description": original_description,
            "eegunity_description": eegunity_description,
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS007181Kernel()