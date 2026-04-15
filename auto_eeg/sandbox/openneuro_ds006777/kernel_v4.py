"""openneuro_ds006777 stage1 kernel for EEGUnity.

SFARI AVSRT EEG dataset — audiovisual simple reaction-time task.
132 subjects (ASD cohort + neurotypical controls), 73 channels, 512 Hz.

Events (raw meta):
  Response_button    — button-press response (motor event, y=0)
  Audiovisual_stim   — simultaneous audiovisual stimulus onset (y=1)
  Auditory_stim      — auditory-only stimulus onset (y=2)
  Visual_stim        — visual-only stimulus onset (y=3)

Label routes:
  Annotation — stimulus modality labels (raw meta, Classical Task 1)
  misc       — reaction_time channel, RT in ms at stimulus onset samples
               (super meta, Potential Task 1)
               derivation metadata: unit=ms, version=1.0, source=event_pairing

Kernel mode: Type 2 + Type 3
Source: https://openneuro.org/datasets/ds006777
DOI:    https://doi.org/10.18112/openneuro.ds006777.v1.0.0

Channel layout: assumed standard_1020 as per BIDS convention.
  LLM 推断，需人类复核 — if non-standard rename map is required, update
  _CHANNEL_RENAME_MAP below after consulting the dataset's electrode file.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Canonical annotation labels expected from BIDS *_events.tsv
_STIM_LABELS: set[str] = {"Audiovisual_stim", "Auditory_stim", "Visual_stim"}
_RESPONSE_LABEL: str = "Response_button"

# Lower-case normalisation map for annotation descriptions
# LLM 推断，需人类复核
_LABEL_NORM: dict[str, str] = {
    "response_button": "Response_button",
    "visual_stim": "Visual_stim",
    "audiovisual_stim": "Audiovisual_stim",
    "auditory_stim": "Auditory_stim",
}

# Reaction-time validity window (ms)
# LLM 推断，需人类复核
_RT_MIN_MS: float = 50.0
_RT_MAX_MS: float = 2000.0

# Channel rename map: raw name → standard_1020 name.
# Populate if actual channel names deviate from standard_1020.
# LLM 推断，需人类复核 — verify against dataset electrode documentation.
_CHANNEL_RENAME_MAP: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------


@dataclass
class DS006777Kernel:
    """Stage1 kernel for openneuro_ds006777 (SFARI AVSRT EEG)."""

    KERNEL_ID: str = field(default="openneuro-ds006777-stage1")

    # ------------------------------------------------------------------
    # Subject-info helpers
    # ------------------------------------------------------------------

    def _find_dataset_root(self, file_path: str) -> str | None:
        """Walk up the directory tree to find the BIDS dataset root."""
        current = os.path.dirname(os.path.abspath(file_path))
        for _ in range(8):
            if os.path.exists(os.path.join(current, "participants.tsv")):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return None

    def _get_subject_info(self, file_path: str) -> tuple[str, str]:
        """Return (age_str, sex_str) from BIDS participants.tsv.

        Falls back to "unknown" for any field that cannot be determined.
        """
        match = re.search(r"sub-([A-Za-z0-9]+)", file_path)
        if not match:
            return "unknown", "unknown"

        sub_id = "sub-" + match.group(1)
        root = self._find_dataset_root(file_path)
        if root is None:
            return "unknown", "unknown"

        tsv_path = os.path.join(root, "participants.tsv")
        if not os.path.exists(tsv_path):
            return "unknown", "unknown"

        try:
            df = pd.read_csv(tsv_path, sep="\t", dtype=str)
        except Exception:
            return "unknown", "unknown"

        mask = df["participant_id"] == sub_id
        if not mask.any():
            return "unknown", "unknown"

        sub_row = df[mask].iloc[0]

        # Age
        age = "unknown"
        if "age" in df.columns:
            raw_age = sub_row.get("age", "n/a")
            if str(raw_age).strip().lower() not in ("n/a", "nan", "none", ""):
                try:
                    age = str(int(float(str(raw_age))))
                except (ValueError, TypeError):
                    age = str(raw_age).strip()

        # Sex / gender (prefer 'sex' column)
        sex = "unknown"
        for col in ("sex", "gender"):
            if col in df.columns:
                raw_sex = sub_row.get(col, "n/a")
                sv = str(raw_sex).strip().lower()
                if sv not in ("n/a", "nan", "none", ""):
                    if sv in ("m", "male"):
                        sex = "male"
                    elif sv in ("f", "female"):
                        sex = "female"
                break

        return age, sex

    # ------------------------------------------------------------------
    # Annotation normalisation (raw meta)
    # ------------------------------------------------------------------

    def _normalise_annotations(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Normalise annotation description strings to canonical labels.

        LLM 推断，需人类复核
        """
        if raw.annotations is None or len(raw.annotations) == 0:
            return raw

        descs = list(raw.annotations.description)
        changed = False
        for i, d in enumerate(descs):
            norm = _LABEL_NORM.get(d.strip().lower(), d)
            if norm != d:
                descs[i] = norm
                changed = True

        if changed:
            raw.annotations.description[:] = np.array(descs, dtype=raw.annotations.description.dtype)

        return raw

    # ------------------------------------------------------------------
    # Reaction-time derivation (super meta)
    # ------------------------------------------------------------------

    def _derive_rt_array(self, raw: mne.io.BaseRaw) -> np.ndarray:
        """Compute reaction times by pairing stimulus onsets with next Response_button.

        Returns ndarray of shape (1, n_times) with RT values in ms at each
        stimulus onset sample and NaN everywhere else.

        Derivation metadata: unit=ms, version=1.0, source=event_pairing
        LLM 推断，需人类复核
        """
        sfreq = raw.info["sfreq"]
        n_times = raw.n_times
        rt_data = np.full((1, n_times), np.nan, dtype=np.float64)

        if raw.annotations is None or len(raw.annotations) == 0:
            return rt_data

        # Sort all events by onset
        events_list: list[tuple[float, str]] = sorted(
            [(float(ann["onset"]), str(ann["description"])) for ann in raw.annotations],
            key=lambda x: x[0],
        )

        if not events_list:
            return rt_data

        # Pre-filter into stimulus and response lists for O(n) matching
        stim_onsets = []
        stim_descs = []
        resp_onsets = []

        for onset, desc in events_list:
            if desc in _STIM_LABELS:
                stim_onsets.append(onset)
                stim_descs.append(desc)
            elif desc == _RESPONSE_LABEL:
                resp_onsets.append(onset)

        if not stim_onsets or not resp_onsets:
            return rt_data

        # Sort response onsets (events_list is already sorted, but defensive)
        resp_onsets = sorted(resp_onsets)
        n_stim = len(stim_onsets)
        n_resp = len(resp_onsets)

        # Linear O(n) pass: match each stimulus with the next response
        resp_idx = 0
        for i in range(n_stim):
            stim_onset = stim_onsets[i]

            # Advance response pointer past any responses before this stimulus
            while resp_idx < n_resp and resp_onsets[resp_idx] < stim_onset:
                resp_idx += 1

            if resp_idx >= n_resp:
                break

            resp_onset = resp_onsets[resp_idx]
            rt_sec = resp_onset - stim_onset
            rt_ms = rt_sec * 1000.0

            if _RT_MIN_MS <= rt_ms <= _RT_MAX_MS:
                sample = int(round(stim_onset * sfreq))
                if 0 <= sample < n_times:
                    rt_data[0, sample] = rt_ms

        return rt_data

    # ------------------------------------------------------------------
    # RT misc channel assembly
    # ------------------------------------------------------------------

    def _add_rt_misc_channel(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Append a reaction_time (misc) channel to the Raw object.

        Derivation metadata: unit=ms, version=1.0, source=event_pairing
        LLM 推断，需人类复核
        """
        rt_data = self._derive_rt_array(raw)

        # Create a single-channel Info object
        rt_info = mne.create_info(
            ch_names=["reaction_time"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc"],
        )
        # Set meas_date using the proper method instead of direct assignment
        rt_info.set_meas_date(raw.info["meas_date"])

        rt_raw = mne.io.RawArray(rt_data, rt_info, verbose=False)

        # Concatenate along channels
        combined = raw.add_channels([rt_raw], verbose=False)
        return combined

    # ------------------------------------------------------------------
    # Channel renaming
    # ------------------------------------------------------------------

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Apply _CHANNEL_RENAME_MAP if non-empty.

        LLM 推断，需人类复核
        """
        if not _CHANNEL_RENAME_MAP:
            return raw

        rename_map = {k: v for k, v in _CHANNEL_RENAME_MAP.items() if k in raw.ch_names}
        if rename_map:
            raw.rename_channels(rename_map, verbose=False)

        return raw

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Full stage-1 kernel: normalise → rename → add_rt_misc.

        Parameters
        ----------
        udataset : udataset object (not used in this kernel)
        raw      : mne.io.BaseRaw — the raw EEG recording
        row      : dict — metadata row (must contain 'file_path')

        Returns
        -------
        mne.io.BaseRaw — processed raw object
        """
        file_path = row.get("file_path", "") if row else ""

        # 1. Normalise annotation labels
        raw = self._normalise_annotations(raw)

        # 2. Rename channels if needed
        raw = self._rename_channels(raw)

        # 3. Add reaction_time misc channel
        raw = self._add_rt_misc_channel(raw)

        return raw


# ---------------------------------------------------------------------------
# Kernel singleton and description
# ---------------------------------------------------------------------------

eegunity_description = {
    "age": "unknown",
    "sex": "unknown",
    "amplifier": "BioSemi ActiveTwo",
    "cap": "BioSemi ActiveTwo 64-channel cap (extended to 73 channels)",
    "handedness": "unknown",
}

KERNEL = DS006777Kernel()