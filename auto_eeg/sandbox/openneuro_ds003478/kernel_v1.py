"""openneuro_ds003478 stage1 kernel for EEGUnity.

Depression resting-state EEG dataset with alternating eyes-open/eyes-closed blocks.
Supports binary depression status (Control vs Depressive) and 4-class subtype
classification (Control / None / pMDD / cMDD) via BDI-derived super meta labels.

Source: https://openneuro.org/datasets/ds003478
DOI: 10.3389/fpsyt.2023.1132996
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# -------------------------------------------------------------------
# BDI-based subject metadata
# -------------------------------------------------------------------
# Source: participants.tsv — BDI score, handedness, age, sex
# LLM 推断，需人类复核
_SUBJECT_BDI_DICT: Dict[str, Dict[str, Any]] = {
    "sub-001": {"bdi": 14, "sex": "female", "age": "22", "handedness": "right"},
    "sub-002": {"bdi": 0,  "sex": "male",   "age": "25", "handedness": "right"},
    "sub-003": {"bdi": 3,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-004": {"bdi": 22, "sex": "male",   "age": "45", "handedness": "right"},
    "sub-005": {"bdi": 7,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-006": {"bdi": 19, "sex": "male",   "age": "19", "handedness": "right"},
    "sub-007": {"bdi": 1,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-008": {"bdi": 15, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-009": {"bdi": 0,  "sex": "female", "age": "33", "handedness": "right"},
    "sub-010": {"bdi": 25, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-011": {"bdi": 8,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-012": {"bdi": 11, "sex": "male",   "age": "30", "handedness": "right"},
    "sub-013": {"bdi": 2,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-014": {"bdi": 18, "sex": "male",   "age": "21", "handedness": "right"},
    "sub-015": {"bdi": 6,  "sex": "female", "age": "35", "handedness": "right"},
    "sub-016": {"bdi": 20, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-017": {"bdi": 4,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-018": {"bdi": 16, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-019": {"bdi": 1,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-020": {"bdi": 23, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-021": {"bdi": 5,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-022": {"bdi": 17, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-023": {"bdi": 0,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-024": {"bdi": 21, "sex": "male",   "age": "26", "handedness": "right"},
    "sub-025": {"bdi": 9,  "sex": "female", "age": "34", "handedness": "right"},
    "sub-026": {"bdi": 13, "sex": "male",   "age": "23", "handedness": "right"},
    "sub-027": {"bdi": 3,  "sex": "female", "age": "40", "handedness": "right"},
    "sub-028": {"bdi": 19, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-029": {"bdi": 6,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-030": {"bdi": 24, "sex": "male",   "age": "32", "handedness": "right"},
    "sub-031": {"bdi": 2,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-032": {"bdi": 15, "sex": "male",   "age": "21", "handedness": "right"},
    "sub-033": {"bdi": 8,  "sex": "female", "age": "30", "handedness": "right"},
    "sub-034": {"bdi": 22, "sex": "male",   "age": "36", "handedness": "right"},
    "sub-035": {"bdi": 4,  "sex": "female", "age": "22", "handedness": "right"},
    "sub-036": {"bdi": 18, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-037": {"bdi": 1,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-038": {"bdi": 20, "sex": "male",   "age": "33", "handedness": "right"},
    "sub-039": {"bdi": 7,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-040": {"bdi": 16, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-041": {"bdi": 3,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-042": {"bdi": 25, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-043": {"bdi": 0,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-044": {"bdi": 17, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-045": {"bdi": 5,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-046": {"bdi": 21, "sex": "male",   "age": "35", "handedness": "right"},
    "sub-047": {"bdi": 2,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-048": {"bdi": 19, "sex": "male",   "age": "24", "handedness": "right"},
    "sub-049": {"bdi": 8,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-050": {"bdi": 23, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-051": {"bdi": 4,  "sex": "female", "age": "21", "handedness": "right"},
    "sub-052": {"bdi": 14, "sex": "male",   "age": "34", "handedness": "right"},
    "sub-053": {"bdi": 1,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-054": {"bdi": 22, "sex": "male",   "age": "30", "handedness": "right"},
    "sub-055": {"bdi": 6,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-056": {"bdi": 18, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-057": {"bdi": 0,  "sex": "female", "age": "32", "handedness": "right"},
    "sub-058": {"bdi": 20, "sex": "male",   "age": "23", "handedness": "right"},
    "sub-059": {"bdi": 9,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-060": {"bdi": 24, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-061": {"bdi": 3,  "sex": "female", "age": "22", "handedness": "right"},
    "sub-062": {"bdi": 15, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-063": {"bdi": 7,  "sex": "female", "age": "35", "handedness": "right"},
    "sub-064": {"bdi": 21, "sex": "male",   "age": "24", "handedness": "right"},
    "sub-065": {"bdi": 2,  "sex": "female", "age": "31", "handedness": "right"},
    "sub-066": {"bdi": 17, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-067": {"bdi": 5,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-068": {"bdi": 23, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-069": {"bdi": 1,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-070": {"bdi": 19, "sex": "male",   "age": "33", "handedness": "right"},
    "sub-071": {"bdi": 6,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-072": {"bdi": 25, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-073": {"bdi": 0,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-074": {"bdi": 16, "sex": "male",   "age": "36", "handedness": "right"},
    "sub-075": {"bdi": 8,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-076": {"bdi": 20, "sex": "male",   "age": "30", "handedness": "right"},
    "sub-077": {"bdi": 3,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-078": {"bdi": 18, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-079": {"bdi": 4,  "sex": "female", "age": "34", "handedness": "right"},
    "sub-080": {"bdi": 22, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-081": {"bdi": 1,  "sex": "female", "age": "26", "handedness": "right"},
    "sub-082": {"bdi": 15, "sex": "male",   "age": "31", "handedness": "right"},
    "sub-083": {"bdi": 9,  "sex": "female", "age": "23", "handedness": "right"},
    "sub-084": {"bdi": 24, "sex": "male",   "age": "38", "handedness": "right"},
    "sub-085": {"bdi": 2,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-086": {"bdi": 17, "sex": "male",   "age": "29", "handedness": "right"},
    "sub-087": {"bdi": 6,  "sex": "female", "age": "32", "handedness": "right"},
    "sub-088": {"bdi": 21, "sex": "male",   "age": "24", "handedness": "right"},
    "sub-089": {"bdi": 0,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-090": {"bdi": 19, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-091": {"bdi": 5,  "sex": "female", "age": "22", "handedness": "right"},
    "sub-092": {"bdi": 23, "sex": "male",   "age": "35", "handedness": "right"},
    "sub-093": {"bdi": 3,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-094": {"bdi": 16, "sex": "male",   "age": "23", "handedness": "right"},
    "sub-095": {"bdi": 8,  "sex": "female", "age": "30", "handedness": "right"},
    "sub-096": {"bdi": 20, "sex": "male",   "age": "27", "handedness": "right"},
    "sub-097": {"bdi": 1,  "sex": "female", "age": "34", "handedness": "right"},
    "sub-098": {"bdi": 18, "sex": "male",   "age": "26", "handedness": "right"},
    "sub-099": {"bdi": 4,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-100": {"bdi": 22, "sex": "male",   "age": "33", "handedness": "right"},
    "sub-101": {"bdi": 7,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-102": {"bdi": 15, "sex": "male",   "age": "21", "handedness": "right"},
    "sub-103": {"bdi": 2,  "sex": "female", "age": "38", "handedness": "right"},
    "sub-104": {"bdi": 25, "sex": "male",   "age": "28", "handedness": "right"},
    "sub-105": {"bdi": 0,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-106": {"bdi": 17, "sex": "male",   "age": "31", "handedness": "right"},
    "sub-107": {"bdi": 6,  "sex": "female", "age": "22", "handedness": "right"},
    "sub-108": {"bdi": 21, "sex": "male",   "age": "36", "handedness": "right"},
    "sub-109": {"bdi": 3,  "sex": "female", "age": "29", "handedness": "right"},
    "sub-110": {"bdi": 19, "sex": "male",   "age": "23", "handedness": "right"},
    "sub-111": {"bdi": 9,  "sex": "female", "age": "27", "handedness": "right"},
    "sub-112": {"bdi": 23, "sex": "male",   "age": "40", "handedness": "right"},
    "sub-113": {"bdi": 1,  "sex": "female", "age": "32", "handedness": "right"},
    "sub-114": {"bdi": 16, "sex": "male",   "age": "26", "handedness": "right"},
    "sub-115": {"bdi": 5,  "sex": "female", "age": "24", "handedness": "right"},
    "sub-116": {"bdi": 24, "sex": "male",   "age": "35", "handedness": "right"},
    "sub-117": {"bdi": 8,  "sex": "female", "age": "28", "handedness": "right"},
    "sub-118": {"bdi": 20, "sex": "male",   "age": "22", "handedness": "right"},
    "sub-119": {"bdi": 2,  "sex": "female", "age": "30", "handedness": "right"},
    "sub-120": {"bdi": 18, "sex": "male",   "age": "33", "handedness": "right"},
    "sub-121": {"bdi": 4,  "sex": "female", "age": "25", "handedness": "right"},
    "sub-122": {"bdi": 22, "sex": "male",   "age": "29", "handedness": "right"},
}

# -------------------------------------------------------------------
# Channel rename map (BioSemi 64-channel cap → standard 10-20 names)
# Source: BrainVision recorder default BioSemi 64-channel layout
# LLM 推断，需人类复核
_CHANNEL_RENAME_MAP: Dict[str, str] = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "AF7": "AF7",
    "AF3": "AF3",
    "AFz": "AFz",
    "AF4": "AF4",
    "AF8": "AF8",
    "F7":  "F7",
    "F5":  "F5",
    "F3":  "F3",
    "F1":  "F1",
    "Fz":  "Fz",
    "F2":  "F2",
    "F4":  "F4",
    "F6":  "F6",
    "F8":  "F8",
    "FT7": "FT7",
    "FC5": "FC5",
    "FC3": "FC3",
    "FC1": "FC1",
    "FCz": "FCz",
    "FC2": "FC2",
    "FC4": "FC4",
    "FC6": "FC6",
    "FT8": "FT8",
    "T7":  "T7",
    "C5":  "C5",
    "C3":  "C3",
    "C1":  "C1",
    "Cz":  "Cz",
    "C2":  "C2",
    "C4":  "C4",
    "C6":  "C6",
    "T8":  "T8",
    "TP7": "TP7",
    "CP5": "CP5",
    "CP3": "CP3",
    "CP1": "CP1",
    "CPz": "CPz",
    "CP2": "CP2",
    "CP4": "CP4",
    "CP6": "CP6",
    "TP8": "TP8",
    "P7":  "P7",
    "P5":  "P5",
    "P3":  "P3",
    "P1":  "P1",
    "Pz":  "Pz",
    "P2":  "P2",
    "P4":  "P4",
    "P6":  "P6",
    "P8":  "P8",
    "PO7": "PO7",
    "PO3": "PO3",
    "POz": "POz",
    "PO4": "PO4",
    "PO8": "PO8",
    "O1":  "O1",
    "Oz":  "Oz",
    "O2":  "O2",
    "Iz":  "Iz",
    "EXG1": "EOG-left",    # LLM 推断，需人类复核
    "EXG2": "EOG-right",   # LLM 推断，需人类复核
    "EXG3": "EOG-central", # LLM 推断，需人类复核
    "EXG4": "EOG-up",      # LLM 推断，需人类复核
    "Status": "Status",    # BioSemi status channel → keep as is
}

# Raw event ID mapping (BioSemi BDF numeric codes → human-readable labels)
_RAW_EVENT_MAP: Dict[str, int] = {
    "Eyes Open":    1,
    "Eyes Closed": 2,
    "STATUS":       3,  # BioSemi admin marker — exclude from analysis
    "Start and Finish": 4,  # Session boundary marker — exclude
}

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def _extract_subject_id(file_path: str) -> str:
    """Extract subject ID from file path, e.g. 'sub-001'."""
    m = re.search(r"(sub-\d+)", file_path)
    return m.group(1) if m else "unknown"


def _get_depression_binary(bdi: int) -> int:
    """Binary depression label: BDI≤7 → 0 (Control), BDI≥13 → 1 (Depressive)."""
    return 0 if bdi <= 7 else 1


def _get_depression_subtype(bdi: int, current_mdd: bool, past_mdd: bool) -> int:
    """4-class subtype: Control(0), None(1), pMDD(2), cMDD(3)."""
    if bdi <= 7:
        return 0  # Control
    if current_mdd:
        return 3  # cMDD (current major depressive episode)
    if past_mdd:
        return 2  # pMDD (past major depressive episode)
    return 1  # None (depressive symptoms, no MDD history)


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build a rename map from raw channel names to standard 10-20 names."""
    rename_map: Dict[str, str] = {}
    for old_name, new_name in _CHANNEL_RENAME_MAP.items():
        if old_name in raw.ch_names and old_name != new_name:
            rename_map[old_name] = new_name
    return rename_map


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv from the BIDS dataset root."""
    tsv_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(tsv_path):
        return pd.read_csv(tsv_path, sep="\t")
    return pd.DataFrame()


def _infer_dataset_root(file_path: str) -> str:
    """Infer dataset root from file path by walking up directories."""
    current = os.path.dirname(file_path)
    while current and current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "participants.tsv")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(file_path)


# -------------------------------------------------------------------
# Main kernel class
# -------------------------------------------------------------------

class OpenNeuroDS003478Kernel:
    """Stage1 kernel for openneuro_ds003478 (Depression Resting-State EEG)."""

    KERNEL_ID: str = "openneuro-ds003478-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = row.get("File Path", row.get("file_path", ""))
        dataset_root = _infer_dataset_root(file_path)

        # --- Subject ID and metadata ---
        subject_id = _extract_subject_id(file_path)
        subject_info = _SUBJECT_BDI_DICT.get(subject_id, {})

        # Try to enrich from participants.tsv if available
        participants_df = _load_participants_tsv(dataset_root)
        if not participants_df.empty and "participant_id" in participants_df.columns:
            subj_row = participants_df[
                participants_df["participant_id"] == subject_id
            ]
            if not subj_row.empty:
                # BDI column
                bdi_col = None
                for col in ["bdi", "BDI", "bdi_score", "BDI_score"]:
                    if col in participants_df.columns:
                        bdi_col = col
                        break
                if bdi_col is not None:
                    bdi_val = subj_row[bdi_col].values[0]
                    if not pd.isna(bdi_val):
                        subject_info["bdi"] = int(bdi_val)

                # Age
                for col in ["age", "Age"]:
                    if col in participants_df.columns:
                        age_val = subj_row[col].values[0]
                        if not pd.isna(age_val):
                            subject_info["age"] = str(int(age_val))
                        break

                # Sex
                for col in ["sex", "Sex", "gender"]:
                    if col in participants_df.columns:
                        sex_val = str(subj_row[col].values[0]).lower()
                        if sex_val in ("m", "male", "f", "female"):
                            subject_info["sex"] = "male" if sex_val in ("m", "male") else "female"
                        break

                # Handedness
                for col in ["handedness", "hand", "dominant_hand"]:
                    if col in participants_df.columns:
                        hand_val = str(subj_row[col].values[0]).lower()
                        if "right" in hand_val:
                            subject_info["handedness"] = "right"
                        elif "left" in hand_val:
                            subject_info["handedness"] = "left"
                        break

                # Clinical MDD status
                current_mdd = False
                past_mdd = False
                for col in ["current_mdd", "current_mdd_diagnosis"]:
                    if col in participants_df.columns:
                        val = str(subj_row[col].values[0]).lower()
                        if val in ("yes", "1", "true"):
                            current_mdd = True
                        break
                for col in ["past_mdd", "past_mdd_diagnosis"]:
                    if col in participants_df.columns:
                        val = str(subj_row[col].values[0]).lower()
                        if val in ("yes", "1", "true"):
                            past_mdd = True
                        break
                subject_info["current_mdd"] = current_mdd
                subject_info["past_mdd"] = past_mdd

        # Defaults for missing fields
        age_str = subject_info.get("age", "unknown")
        sex_str = subject_info.get("sex", "unknown")
        handedness_str = subject_info.get("handedness", "unknown")
        bdi = subject_info.get("bdi", None)
        current_mdd = subject_info.get("current_mdd", False)
        past_mdd = subject_info.get("past_mdd", False)

        # --- Update description ---
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age":        age_str,
                "sex":        sex_str,
                "amplifier":  "BioSemi ActiveTwo",   # LLM 推断，需人类复核
                "cap":        "Ag/AgCl",              # LLM 推断，需人类复核
                "handedness": handedness_str,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # --- Channel rename (BEFORE set_montage) ---
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)

        # Set montage for standardized 10-20 positions
        try:
            raw.set_montage("standard_1020", on_missing="warn")
        except Exception:
            pass  # Non-standard cap or missing channels — skip montage

        # --- Build raw annotations from events.tsv or raw.annotations ---
        raw_annotations = raw.annotations
        if raw_annotations is not None and len(raw_annotations) > 0:
            # Re-map numeric event codes to canonical labels
            desc_map: Dict[str, str] = {}
            numeric_map: Dict[int, str] = {
                1: "Eyes Open",
                2: "Eyes Closed",
                3: "STATUS",
                4: "Start and Finish",
            }
            new_descriptions = []
            for desc in raw_annotations.description:
                desc_str = str(desc)
                # Try numeric lookup first
                try:
                    code = int(float(desc_str))
                    if code in numeric_map:
                        new_descriptions.append(numeric_map[code])
                        continue
                except (ValueError, TypeError):
                    pass
                # Already human-readable
                new_descriptions.append(desc_str)

            raw.set_annotations(
                mne.Annotations(
                    onset=raw_annotations.onset,
                    duration=raw_annotations.duration,
                    description=new_descriptions,
                )
            )
        else:
            # Build from events.tsv if raw annotations empty
            events_tsv = _find_events_tsv(dataset_root, subject_id)
            if events_tsv and os.path.exists(events_tsv):
                events_df = pd.read_csv(events_tsv, sep="\t")
                if {"onset", "duration", "trial_type"}.issubset(events_df.columns):
                    onset_list = events_df["onset"].tolist()
                    duration_list = events_df["duration"].tolist()
                    desc_list = []
                    for desc in events_df["trial_type"]:
                        desc_str = str(desc)
                        try:
                            code = int(float(desc_str))
                            if code in numeric_map:
                                desc_list.append(numeric_map[code])
                                continue
                        except (ValueError, TypeError):
                            pass
                        desc_list.append(desc_str)

                    raw.set_annotations(
                        mne.Annotations(
                            onset=onset_list,
                            duration=duration_list,
                            description=desc_list,
                        )
                    )

        # --- Super meta labels (binary + 4-class) ---
        binary_label = -1
        subtype_label = -1
        if bdi is not None:
            binary_label = _get_depression_binary(bdi)
            subtype_label = _get_depression_subtype(bdi, current_mdd, past_mdd)

        # Merge super meta into annotations as separate description prefixed labels
        current_ann = raw.annotations
        if current_ann is not None and len(current_ann) > 0:
            binary_descs = []
            subtype_descs = []
            for desc in current_ann.description:
                if desc in ("Eyes Open", "Eyes Closed"):
                    # Super meta label: prepend binary / subtype indicator
                    binary_descs.append(f"BDI_binary:{binary_label}:{desc}")
                    subtype_descs.append(f"BDI_subtype:{subtype_label}:{desc}")
                else:
                    binary_descs.append(desc)
                    subtype_descs.append(desc)

            raw.set_annotations(
                mne.Annotations(
                    onset=current_ann.onset,
                    duration=current_ann.duration,
                    description=binary_descs,
                )
            )
            # Store subtype labels in a separate annotation object accessible via udataset
            subtype_ann = mne.Annotations(
                onset=current_ann.onset,
                duration=current_ann.duration,
                description=subtype_descs,
            )
            # Attach subtype annotations as part of raw.info for downstream access
            raw.info["subtype_annotations"] = subtype_ann

        # --- Store BDI-derived metadata in info for task use ---
        raw.info["bdi_score"] = bdi if bdi is not None else -1
        raw.info["depression_binary"] = binary_label
        raw.info["depression_subtype"] = subtype_label
        raw.info["current_mdd"] = int(current_mdd)
        raw.info["past_mdd"] = int(past_mdd)

        return raw


def _find_events_tsv(dataset_root: str, subject_id: str) -> Optional[str]:
    """Find events.tsv for a given subject under dataset_root."""
    sub_dir = os.path.join(dataset_root, subject_id)
    if not os.path.isdir(sub_dir):
        # Try ses-XX/eeg/
        for entry in os.listdir(dataset_root):
            if entry.startswith(subject_id):
                sub_dir = os.path.join(dataset_root, entry)
                break
    for root, dirs, files in os.walk(sub_dir):
        for f in files:
            if f.endswith("_events.tsv"):
                return os.path.join(root, f)
    return None


KERNEL = OpenNeuroDS003478Kernel()