"""Healthy Brain Network (HBN) EEG - Release 7 stage1 kernel for EEGUnity.

Dataset: openneuro_ds005511
- 381 subjects, 3100+ files, 129 channels, 500 Hz
- Multi-paradigm: resting-state, contrast detection, movie watching
- Clinical phenotypic data for multi-label psychiatric diagnosis

Source: https://openneuro.org/datasets/ds005511
Reference: https://doi.org/10.1016/j.neuroimage.2022.119348
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# ============================================================================
# Clinical Labels (Super Meta) - Source: HBN phenotypic assessment tables
# Annotator: LLM, 2026-01-15
# Note: These labels are derived from clinical instruments by licensed clinicians
# ============================================================================
_CLINICAL_LABELS = [
    "ADHD", "ANX", "SLD", "ASD", "DISR", "COM", "DEP", "Other", "NoDiagnosis"
]

# Severity Scores (Super Meta) - Source: HBN phenotypic assessment tables
# Annotator: LLM, 2026-01-15
_SEVERITY_SCORES = [
    "SCARED_GAD", "SWAN_IN", "SWAN_HY", "SRS2_SCI", "SRS2_RRB", "WISC_VCI", "WISC_WMI"
]


def _extract_subject_id_from_path(file_path: str) -> str:
    """Extract subject ID from BIDS file path.

    Source: BIDS specification
    Annotator: Human, 2026-04-08
    """
    match = re.search(r"sub-([A-Z0-9]+)", file_path)
    if match:
        return match.group(1)
    return "unknown"


def _load_participants_tsv(dataset_root: str) -> pd.DataFrame:
    """Load participants.tsv for demographic data.

    Source: BIDS standard
    Annotator: Human, 2026-04-08
    """
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        df = pd.read_csv(participants_path, sep="\t")
        return df
    return pd.DataFrame()


def _load_phenotypic_data(dataset_root: str, subject_id: str) -> Dict[str, Any]:
    """Load phenotypic/clinical assessment data for a subject.

    Source: HBN datasetphenotypic files
    Annotator: Human, 2026-04-08
    Note: Phenotypic data may be in separate tabular files or participants.tsv
    """
    # Try to find phenotype file in dataset root
    phenotypic_paths = [
        os.path.join(dataset_root, f"sub-{subject_id}_phenotypic.tsv"),
        os.path.join(dataset_root, f"sub-{subject_id}_phenotypic.csv"),
        os.path.join(dataset_root, "phenotypic_data.tsv"),
    ]

    for path in phenotypic_paths:
        if os.path.exists(path):
            ext = os.path.splitext(path)[1].lower()
            if ext == ".tsv":
                df = pd.read_csv(path, sep="\t")
            else:
                df = pd.read_csv(path)
            if not df.empty:
                return df.iloc[0].to_dict()

    # Fallback: try to get from participants.tsv
    participants_df = _load_participants_tsv(dataset_root)
    if "participant_id" in participants_df.columns:
        subject_row = participants_df[
            participants_df["participant_id"] == f"sub-{subject_id}"
        ]
        if not subject_row.empty:
            return subject_row.iloc[0].to_dict()

    return {}


def _get_clinical_labels(phenotypic_data: Dict[str, Any]) -> Dict[str, int]:
    """Extract multi-label diagnosis from phenotypic data.

    Source: HBN DSM-V diagnosis derived from clinical instruments
    Annotator: LLM, 2026-01-15
    Note: Requires human verification for specific threshold/derivation rules
    """
    labels = {}
    for label in _CLINICAL_LABELS:
        # Map column names to canonical labels
        col_map = {
            "ADHD": ["ADHD", "adhd", "ADHD_Inatt", "ADHD_Hyp"],
            "ANX": ["ANX", "anxiety", "ANXIETY"],
            "SLD": ["SLD", "SpecificLearningDisorder", "SLD_Diagnosis"],
            "ASD": ["ASD", "autism", "AutismSpectrumDisorder"],
            "DISR": ["DISR", "DisruptiveBehavior", "ODD", "CD"],
            "COM": ["COM", "CommunicationDisorder", "SpeechLanguage"],
            "DEP": ["DEP", "Depression", "DepressiveDisorder", "MDD"],
            "Other": ["Other_Diagnosis", "OtherDiagnosis", "Other"],
            "NoDiagnosis": ["NoDiagnosis", "No_Diagnosis", "NoDiagnosisGroup"],
        }

        for col_name in col_map.get(label, []):
            if col_name in phenotypic_data:
                val = phenotypic_data[col_name]
                if isinstance(val, (int, float)):
                    labels[label] = 1 if val > 0 else 0
                elif isinstance(val, str):
                    labels[label] = 1 if val.lower() in ["yes", "true", "1", "dx"] else 0
                else:
                    labels[label] = 0
                break
        else:
            labels[label] = 0

    return labels


def _get_severity_scores(phenotypic_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract symptom severity scores from phenotypic data.

    Source: HBN standardized assessments (SCARED-GAD, SWAN, SRS-2, WISC-V)
    Annotator: LLM, 2026-01-15
    Note: Requires human verification for specific scale mappings
    """
    scores = {}

    # SCARED-GAD (0-9 anxiety range)
    if "SCARED_GAD" in phenotypic_data:
        scores["SCARED_GAD"] = float(phenotypic_data["SCARED_GAD"])
    elif "SCARED_GAD_Score" in phenotypic_data:
        scores["SCARED_GAD"] = float(phenotypic_data["SCARED_GAD_Score"])

    # SWAN-Inattention (0-27)
    if "SWAN_IN" in phenotypic_data:
        scores["SWAN_IN"] = float(phenotypic_data["SWAN_IN"])
    elif "SWAN_Inatt" in phenotypic_data:
        scores["SWAN_IN"] = float(phenotypic_data["SWAN_Inatt"])

    # SWAN-Hyperactivity (0-27)
    if "SWAN_HY" in phenotypic_data:
        scores["SWAN_HY"] = float(phenotypic_data["SWAN_HY"])
    elif "SWAN_Hyp" in phenotypic_data:
        scores["SWAN_HY"] = float(phenotypic_data["SWAN_HY"])

    # SRS-2 Social Communication Interaction (T-score)
    if "SRS2_SCI" in phenotypic_data:
        scores["SRS2_SCI"] = float(phenotypic_data["SRS2_SCI"])
    elif "SRS2_SCI_TScore" in phenotypic_data:
        scores["SRS2_SCI"] = float(phenotypic_data["SRS2_SCI_TScore"])

    # SRS-2 Restricted/Repetitive Behavior (T-score)
    if "SRS2_RRB" in phenotypic_data:
        scores["SRS2_RRB"] = float(phenotypic_data["SRS2_RRB"])
    elif "SRS2_RRB_TScore" in phenotypic_data:
        scores["SRS2_RRB"] = float(phenotypic_data["SRS2_RRB_TScore"])

    # WISC-V Verbal Comprehension Index
    if "WISC_VCI" in phenotypic_data:
        scores["WISC_VCI"] = float(phenotypic_data["WISC_VCI"])

    # WISC-V Working Memory Index
    if "WISC_WMI" in phenotypic_data:
        scores["WISC_WMI"] = float(phenotypic_data["WISC_WMI"])

    return scores


@dataclass
class HBNEEGKernel:
    """Stage1 kernel for the Healthy Brain Network (HBN) EEG dataset.

    This kernel handles:
    - BIDS-compliant EEG data from OpenNeuro ds005511
    - 129-channel recordings (128 EEG + 1 reference or auxiliary)
    - Clinical phenotypic data for super meta construction
    """

    KERNEL_ID: str = "hbn-eeg-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single HBN EEG recording.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : MNE Raw object
        row : Locator row with file path information

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with metadata and annotations
        """
        # Extract subject ID from file path
        file_path = row.get("File Path", "")
        subject_id = _extract_subject_id_from_path(file_path)

        # Get dataset root (parent of subject folder)
        dataset_root = os.path.dirname(os.path.dirname(file_path))

        # Load phenotypic/clinical data
        phenotypic_data = _load_phenotypic_data(dataset_root, subject_id)

        # Extract demographic info
        age = "unknown"
        sex = "unknown"
        handedness = "unknown"

        if phenotypic_data:
            # Extract age
            age_fields = ["age", "Age", "AGE", "subject_age"]
            for field in age_fields:
                if field in phenotypic_data:
                    val = phenotypic_data[field]
                    if isinstance(val, (int, float)) and val > 0:
                        age = str(int(val))
                    elif isinstance(val, str) and val.strip():
                        age = val.strip()
                    break

            # Extract sex
            sex_fields = ["sex", "Sex", "gender", "Gender"]
            for field in sex_fields:
                if field in phenotypic_data:
                    val = str(phenotypic_data[field]).lower().strip()
                    if val in ["m", "male", "man", "boy"]:
                        sex = "male"
                    elif val in ["f", "female", "woman", "girl"]:
                        sex = "female"
                    break

            # Extract handedness
            handed_fields = ["handedness", "Handedness", "hand", "Hand"]
            for field in handed_fields:
                if field in phenotypic_data:
                    val = str(phenotypic_data[field]).lower().strip()
                    if val.startswith("r"):
                        handedness = "right"
                    elif val.startswith("l"):
                        handedness = "left"
                    break

        # Build eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": "BioSemi ActiveTwo",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Set clinical labels (super meta) if phenotypic data available
        if phenotypic_data:
            clinical_labels = _get_clinical_labels(phenotypic_data)
            if clinical_labels and any(v > 0 for v in clinical_labels.values()):
                raw.info["clinical_labels"] = clinical_labels

            severity_scores = _get_severity_scores(phenotypic_data)
            if severity_scores:
                raw.info["severity_scores"] = severity_scores

        # Rename channels if needed (HBN uses standard 10-20 naming)
        # Common HBN channel patterns need mapping
        rename_map = {}
        for ch_name in raw.ch_names:
            # Handle EEG-001 format
            if re.match(r"EEG-\d+$", ch_name):
                continue  # Already standard, will be set by MNE
            # Handle other non-standard patterns
            if ch_name.startswith("EEG") and not re.match(r"EEG-[A-Z]", ch_name):
                continue

        if rename_map:
            raw.rename_channels(rename_map)

        # Set standard 10-20 montage
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Non-standard cap or layout

        return raw


KERNEL = HBNEEGKernel()