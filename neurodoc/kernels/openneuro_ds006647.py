"""openneuro_ds006647 stage1 kernel for EEGUnity.

Poetry EEG Study — Haiku / Senryu vs non-poetic control texts.
64-channel BioSemi ActiveTwo, 512 Hz, BIDS format (OpenNeuro).

BioSemi trigger codes 65280-65288 encode stimulus/condition onset.
Event 65284 has 852 occurrences; 65281-65283 and 65280, 65285-65288 have 848 each.
Primary classification task uses 65281-65284 (Haiku / Senryu / control).
'boundary' annotations are admin segment markers and are excluded from analysis.

Source  : https://openneuro.org/datasets/ds006647
DOI     : https://doi.org/10.18112/openneuro.ds006647.v1.0.1
Paper   : https://doi.org/10.1038/s41597-025-06189-w

Amplifier : BioSemi ActiveTwo               # inferred by LLM, needs human review
Cap       : BioSemi 64-ch Ag/AgCl sintered  # inferred by LLM, needs human review

Raw-meta event label map (65280-65288 → string description):
  All nine trigger codes are preserved as their numeric string; downstream
  task configs select the relevant subset.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Raw-meta event label map
# Source: analysis.md § Event Structure; inferred by LLM, needs human review
# ---------------------------------------------------------------------------
_EVENT_LABEL_MAP: Dict[int, str] = {
    65280: "65280",
    65281: "65281",
    65282: "65282",
    65283: "65283",
    65284: "65284",
    65285: "65285",
    65286: "65286",
    65287: "65287",
    65288: "65288",
}

# ---------------------------------------------------------------------------
# BioSemi 64-channel standard cap — A/B legacy naming → standard 10-20 names
# Source: BioSemi website cap layout chart; inferred by LLM, needs human review
# ---------------------------------------------------------------------------
_BIOSEMI64_ORDERED: tuple = (
    "Fp1", "AF7", "AF3", "F1",  "F3",  "F5",  "F7",
    "FT7", "FC5", "FC3", "FC1", "C1",  "C3",  "C5",
    "T7",  "TP7", "CP5", "CP3", "CP1", "P1",  "P3",
    "P5",  "P7",  "P9",  "PO7", "PO3", "O1",  "Iz",
    "Oz",  "POz", "Pz",  "CPz",
    # bank B
    "Fpz", "Fp2", "AF8", "AF4", "AFz", "Fz",  "F2",
    "F4",  "F6",  "F8",  "FT8", "FC6", "FC4", "FC2",
    "FCz", "Cz",  "C2",  "C4",  "C6",  "T8",  "TP8",
    "CP6", "CP4", "CP2", "P2",  "P4",  "P6",  "P8",
    "P10", "PO8", "PO4", "O2",
)


def _build_ab_rename_map(ch_names: list) -> Dict[str, str]:
    """Map A1-A32 / B1-B32 BioSemi channel names to standard 10-20 names.

    In some BioSemi BDF files the electrodes are labelled A1…A32 B1…B32
    rather than the standard 10-20 identifiers. This function builds the
    rename dict only for channels that are actually present.

    Source: BioSemi ActiveTwo hardware documentation; inferred by LLM, needs human review
    """
    rename: Dict[str, str] = {}
    existing = set(ch_names)
    bank_a = _BIOSEMI64_ORDERED[:32]
    bank_b = _BIOSEMI64_ORDERED[32:]
    for idx, std in enumerate(bank_a):
        legacy = f"A{idx + 1}"
        if legacy in existing and legacy != std:
            rename[legacy] = std
    for idx, std in enumerate(bank_b):
        legacy = f"B{idx + 1}"
        if legacy in existing and legacy != std:
            rename[legacy] = std
    return rename


# ---------------------------------------------------------------------------
# BIDS participant helpers
# ---------------------------------------------------------------------------

def _find_bids_root(file_path: str) -> str:
    """Walk up the directory tree to locate the BIDS dataset root.

    The root is identified by the presence of participants.tsv.
    """
    current = os.path.dirname(os.path.abspath(file_path))
    for _ in range(8):
        if os.path.isfile(os.path.join(current, "participants.tsv")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.dirname(os.path.abspath(file_path))


def _load_participants_tsv(bids_root: str) -> Optional[pd.DataFrame]:
    tsv = os.path.join(bids_root, "participants.tsv")
    if os.path.isfile(tsv):
        return pd.read_csv(tsv, sep="\t", dtype=str)
    return None


def _extract_subject_id(file_path: str) -> Optional[str]:
    """Return the BIDS subject label (e.g. 'sub-01') from the file path."""
    for part in file_path.replace("\\", "/").split("/"):
        if part.startswith("sub-"):
            return part
    return None


def _parse_sex(raw_value: str) -> str:
    v = raw_value.strip().lower()
    if v in ("m", "male"):
        return "male"
    if v in ("f", "female"):
        return "female"
    return "unknown"


def _parse_handedness(raw_value: str) -> str:
    v = raw_value.strip().lower()
    if v in ("r", "right"):
        return "right"
    if v in ("l", "left"):
        return "left"
    return "unknown"


def _get_subject_info(
    df: Optional[pd.DataFrame], subject_id: Optional[str]
) -> Dict[str, str]:
    defaults: Dict[str, str] = {
        "age": "unknown",
        "sex": "unknown",
        "handedness": "unknown",
    }
    if df is None or subject_id is None:
        return defaults

    mask = df["participant_id"] == subject_id
    if not mask.any():
        return defaults

    r = df[mask].iloc[0]
    result: Dict[str, str] = {}

    # age
    for col in ("age", "Age"):
        if col in r.index and pd.notna(r[col]):
            v = str(r[col]).strip()
            if v.lower() not in ("nan", "n/a", "na", ""):
                result["age"] = v
                break
    result.setdefault("age", "unknown")

    # sex / gender
    for col in ("sex", "gender", "Sex", "Gender"):
        if col in r.index and pd.notna(r[col]):
            v = str(r[col])
            if v.lower() not in ("nan", "n/a", "na", ""):
                result["sex"] = _parse_sex(v)
                break
    result.setdefault("sex", "unknown")

    # handedness
    for col in ("handedness", "Handedness"):
        if col in r.index and pd.notna(r[col]):
            v = str(r[col])
            if v.lower() not in ("nan", "n/a", "na", ""):
                result["handedness"] = _parse_handedness(v)
                break
    result.setdefault("handedness", "unknown")

    return result


# ---------------------------------------------------------------------------
# Annotation normalisation
# ---------------------------------------------------------------------------

def _normalise_annotations(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Remap BioSemi numeric trigger codes in annotations to string labels.

    BDF files read by MNE may already carry annotations with numeric string
    descriptions (e.g. '65281') from the Status channel.  This function
    normalises those descriptions using _EVENT_LABEL_MAP and preserves
    unrecognised annotations (including 'boundary') unchanged.

    If no annotations are present the function attempts to extract events
    from the STIM channel.
    """
    ann = raw.annotations

    if ann is not None and len(ann) > 0:
        new_desc = []
        for desc in ann.description:
            try:
                code = int(float(desc))
                new_desc.append(_EVENT_LABEL_MAP.get(code, desc))
            except (ValueError, TypeError):
                new_desc.append(desc)  # keep 'boundary' and any other strings

        new_ann = mne.Annotations(
            onset=ann.onset,
            duration=ann.duration,
            description=new_desc,
            orig_time=ann.orig_time,
        )
        raw.set_annotations(new_ann)
        return raw

    # No annotations — try extracting from STIM channel
    stim_chs = [
        ch for ch in raw.ch_names
        if raw.get_channel_types([ch])[0] == "stim"
    ]
    if not stim_chs:
        return raw

    try:
        events = mne.find_events(
            raw, stim_channel=stim_chs[0], verbose=False
        )
        if events is None or len(events) == 0:
            return raw
        onsets = events[:, 0] / raw.info["sfreq"]
        descriptions = [
            _EVENT_LABEL_MAP.get(int(ev_id), str(int(ev_id)))
            for ev_id in events[:, 2]
        ]
        new_ann = mne.Annotations(
            onset=onsets,
            duration=np.zeros(len(onsets)),
            description=descriptions,
        )
        raw.set_annotations(new_ann)
    except Exception:
        pass

    return raw


# ---------------------------------------------------------------------------
# Kernel class
# ---------------------------------------------------------------------------

@dataclass
class OpenNeuroDS006647Kernel:
    """Stage1 kernel for openneuro_ds006647 — Poetry EEG Study."""

    KERNEL_ID: str = "openneuro-ds006647-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        file_path = str(row["File Path"])

        # ------------------------------------------------------------------
        # 1. Resolve BIDS participant info from participants.tsv
        # ------------------------------------------------------------------
        bids_root = _find_bids_root(file_path)
        participants_df = _load_participants_tsv(bids_root)
        subject_id = _extract_subject_id(file_path)
        subj = _get_subject_info(participants_df, subject_id)

        # ------------------------------------------------------------------
        # 2. Write eegunity_description
        # ------------------------------------------------------------------
        original_description = raw.info.get("description") or ""
        if not isinstance(original_description, str):
            original_description = str(original_description)

        raw.info["description"] = json.dumps({
            "original_description": original_description,
            "eegunity_description": {
                "age": subj["age"],
                "sex": subj["sex"],
                "amplifier": "BioSemi ActiveTwo",   # inferred by LLM, needs human review
                "cap": "BioSemi 64-ch Ag/AgCl sintered electrodes",  # inferred by LLM, needs human review
                "handedness": subj["handedness"],
            },
        })

        # ------------------------------------------------------------------
        # 3. Channel renaming BEFORE set_montage
        # Handle legacy A1-A32 / B1-B32 BioSemi channel naming if present.
        # Source: BioSemi hardware documentation; inferred by LLM, needs human review
        # ------------------------------------------------------------------
        rename_map = _build_ab_rename_map(raw.ch_names)
        if rename_map:
            raw.rename_channels(rename_map)

        # ------------------------------------------------------------------
        # 4. Set montage (biosemi64 → fallback standard_1020)
        # Source: BioSemi 64-channel standard cap layout; inferred by LLM, needs human review
        # ------------------------------------------------------------------
        try:
            montage = mne.channels.make_standard_montage("biosemi64")
            raw.set_montage(montage, on_missing="ignore", verbose=False)
        except Exception:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore", verbose=False)
            except Exception:
                pass

        # ------------------------------------------------------------------
        # 5. Normalise BioSemi trigger annotations (raw meta)
        # Codes 65280-65288 → their numeric string labels.
        # 'boundary' admin markers are preserved unchanged.
        # ------------------------------------------------------------------
        raw = _normalise_annotations(raw)

        return raw


KERNEL = OpenNeuroDS006647Kernel()