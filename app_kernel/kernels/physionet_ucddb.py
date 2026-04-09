"""Physionet UCD Sleep Apnea Database stage1 kernel for EEGUnity.

Sleep stage encoding in _stage.txt (R&K system, one integer per 30-second epoch):
  0 → Sleep stage W   (Wake)
  1 → Sleep stage 1   (NREM Stage 1)
  2 → Sleep stage 2   (NREM Stage 2)
  3 → Sleep stage 3   (NREM Stage 3, slow-wave sleep)
  4 → Sleep stage 4   (NREM Stage 4, deep SWS)
  5 → Sleep stage REM (REM sleep)
  8 → Sleep stage 8   (undefined / movement artifact epoch)

_lifecard.edf files (ECG-only) are skipped — no annotations applied.
Subject demographics are available in SubjectDetails.xls but not parsed here
(individual subject-to-file mapping is not in the public EDF headers).

Source: https://physionet.org/content/ucddb/1.0.0/
Kernel added: 2026-04-09 — LLM-assisted, requires human review.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import mne


_STAGE_MAP = {
    0: "Sleep stage W",
    1: "Sleep stage 1",
    2: "Sleep stage 2",
    3: "Sleep stage 3",
    4: "Sleep stage 4",
    5: "Sleep stage REM",
    8: "Sleep stage 8",
}

_EPOCH_DURATION = 30.0  # seconds per epoch (fixed by dataset)


@dataclass
class PhysionetUcddbKernel:
    """Stage1 kernel for the physionet-ucddb dataset."""

    KERNEL_ID: str = "physionet-ucddb-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row["File Path"]
        file_name = os.path.basename(file_path)

        description_dict = {
            "original_description": raw.info.get("description", ""),
            "eegunity_description": {
                "amplifier": "unknown",
                "cap":       "unknown",
                "age":       "unknown",
                "sex":       "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # _lifecard.edf files are ECG-only; skip annotation injection.
        if "_lifecard" in file_name:
            raw.set_annotations(mne.Annotations([], [], []))
            return raw

        # Companion stage file: ucddbXXX.rec → ucddbXXX_stage.txt
        stage_path = file_path.replace(".rec", "_stage.txt")
        if not os.path.exists(stage_path):
            return raw

        # Parse stage file — one integer per line, each = 30-second epoch.
        onsets, durations, descriptions = [], [], []
        with open(stage_path, "r") as fh:
            for epoch_idx, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                try:
                    code = int(line)
                except ValueError:
                    continue
                label = _STAGE_MAP.get(code)
                if label is None:
                    continue
                onsets.append(epoch_idx * _EPOCH_DURATION)
                durations.append(_EPOCH_DURATION)
                descriptions.append(label)

        raw.set_annotations(
            mne.Annotations(
                onset=onsets,
                duration=durations,
                description=descriptions,
            )
        )
        return raw


KERNEL = PhysionetUcddbKernel()
