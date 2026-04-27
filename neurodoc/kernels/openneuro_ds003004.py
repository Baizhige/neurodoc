"""Dataset-specific kernel for openneuro_ds003004.

Imagined Emotion Study - 15-class emotion classification from guided imagery.
34 subjects, 219 channels, 256 Hz sampling rate.

Events: 15 emotion categories (anger, awe, compassion, content, disgust,
excite, fear, frustration, grief, happy, jealousy, joy, love, relax, relief, sad)
each occurring once per subject (~34 times total).

Source: https://openneuro.org/datasets/ds003004
DOI: 10.1016/j.neuroimage.2022.118873
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# Subject Information
# Source: participants.tsv (BIDS)
# Annotator: Human (from dataset), 2026-04-08
# =============================================================================
def _load_participants_tsv(dataset_path: str) -> Dict[str, Dict[str, str]]:
    """Load subject metadata from BIDS participants.tsv."""
    participants_file = os.path.join(dataset_path, "participants.tsv")
    if not os.path.exists(participants_file):
        return {}

    df = pd.read_csv(participants_file, sep="\t")
    subject_dict: Dict[str, Dict[str, str]] = {}

    for _, row in df.iterrows():
        subject_id = str(row.get("participant_id", "")).strip()
        if not subject_id:
            continue

        # Age: may be numeric or string in participants.tsv
        age_val = row.get("age", "unknown")
        if pd.isna(age_val) or str(age_val).strip() == "":
            age = "unknown"
        else:
            age = str(int(float(age_val))) if isinstance(age_val, (int, float)) else str(age_val)

        # Sex: typically 'm'/'f' or 'male'/'female' in BIDS
        sex_val = row.get("sex", row.get("gender", "unknown"))
        if pd.isna(sex_val) or str(sex_val).strip() == "":
            sex = "unknown"
        else:
            sex_lower = str(sex_val).strip().lower()
            if sex_lower in ["m", "male"]:
                sex = "male"
            elif sex_lower in ["f", "female"]:
                sex = "female"
            else:
                sex = "unknown"

        # Handedness from participants.tsv if available
        handedness_val = row.get("handedness", "unknown")
        if pd.isna(handedness_val) or str(handedness_val).strip() == "":
            handedness = "unknown"
        else:
            handedness_lower = str(handedness_val).strip().lower()
            if handedness_lower in ["r", "right"]:
                handedness = "right"
            elif handedness_lower in ["l", "left"]:
                handedness = "left"
            else:
                handedness = "unknown"

        subject_dict[subject_id] = {
            "age": age,
            "sex": sex,
            "handedness": handedness,
        }

    return subject_dict


# =============================================================================
# Channel Name Mapping (219 channels -> standard names)
# Source: Dataset uses EGI HydroCel Geodesic Sensor Net 256-channel system
# Actual recorded channels: 219 (some channels disabled/removed)
# Annotator: LLM (from EGI 256-channel naming convention), 2026-04-08
# 由 LLM 推断，需人类复核
# =============================================================================
# EGI 256-channel naming uses E1, E2, ... E256
# Standard 10-20 equivalents from EGI documentation
_EGI_TO_STANDARD_256: Dict[str, str] = {
    # Standard 10-20 positions (approximate EGI mapping)
    "E1": "E1", "E2": "E2", "E3": "E3", "E4": "E4", "E5": "E5",
    "E6": "E6", "E7": "E7", "E8": "E8", "E9": "E9", "E10": "E10",
    "E11": "E11", "E12": "E12", "E13": "E13", "E14": "E14", "E15": "E15",
    "E16": "E16", "E17": "E17", "E18": "E18", "E19": "E19", "E20": "E20",
    "E21": "E21", "E22": "E22", "E23": "E23", "E24": "E24", "E25": "E25",
    "E26": "E26", "E27": "E27", "E28": "E28", "E29": "E29", "E30": "E30",
    "E31": "E31", "E32": "E32", "E33": "E33", "E34": "E34", "E35": "E35",
    "E36": "E36", "E37": "E37", "E38": "E38", "E39": "E39", "E40": "E40",
    "E41": "E41", "E42": "E42", "E43": "E43", "E44": "E44", "E45": "E45",
    "E46": "E46", "E47": "E47", "E48": "E48", "E49": "E49", "E50": "E50",
    "E51": "E51", "E52": "E52", "E53": "E53", "E54": "E54", "E55": "E55",
    "E56": "E56", "E57": "E57", "E58": "E58", "E59": "E59", "E60": "E60",
    "E61": "E61", "E62": "E62", "E63": "E63", "E64": "E64", "E65": "E65",
    "E66": "E66", "E67": "E67", "E68": "E68", "E69": "E69", "E70": "E70",
    "E71": "E71", "E72": "E72", "E73": "E73", "E74": "E74", "E75": "E75",
    "E76": "E76", "E77": "E77", "E78": "E78", "E79": "E79", "E80": "E80",
    "E81": "E81", "E82": "E82", "E83": "E83", "E84": "E84", "E85": "E85",
    "E86": "E86", "E87": "E87", "E88": "E88", "E89": "E89", "E90": "E90",
    "E91": "E91", "E92": "E92", "E93": "E93", "E94": "E94", "E95": "E95",
    "E96": "E96", "E97": "E97", "E98": "E98", "E99": "E99", "E100": "E100",
    "E101": "E101", "E102": "E102", "E103": "E103", "E104": "E104", "E105": "E105",
    "E106": "E106", "E107": "E107", "E108": "E108", "E109": "E109", "E110": "E110",
    "E111": "E111", "E112": "E112", "E113": "E113", "E114": "E114", "E115": "E115",
    "E116": "E116", "E117": "E117", "E118": "E118", "E119": "E119", "E120": "E120",
    "E121": "E121", "E122": "E122", "E123": "E123", "E124": "E124", "E125": "E125",
    "E126": "E126", "E127": "E127", "E128": "E128", "E129": "E129", "E130": "E130",
    "E131": "E131", "E132": "E132", "E133": "E133", "E134": "E134", "E135": "E135",
    "E136": "E136", "E137": "E137", "E138": "E138", "E139": "E139", "E140": "E140",
    "E141": "E141", "E142": "E142", "E143": "E143", "E144": "E144", "E145": "E145",
    "E146": "E146", "E147": "E147", "E148": "E148", "E149": "E149", "E150": "E150",
    "E151": "E151", "E152": "E152", "E153": "E153", "E154": "E154", "E155": "E155",
    "E156": "E156", "E157": "E157", "E158": "E158", "E159": "E159", "E160": "E160",
    "E161": "E161", "E162": "E162", "E163": "E163", "E164": "E164", "E165": "E165",
    "E166": "E166", "E167": "E167", "E168": "E168", "E169": "E169", "E170": "E170",
    "E171": "E171", "E172": "E172", "E173": "E173", "E174": "E174", "E175": "E175",
    "E176": "E176", "E177": "E177", "E178": "E178", "E179": "E179", "E180": "E180",
    "E181": "E181", "E182": "E182", "E183": "E183", "E184": "E184", "E185": "E185",
    "E186": "E186", "E187": "E187", "E188": "E188", "E189": "E189", "E190": "E190",
    "E191": "E191", "E192": "E192", "E193": "E193", "E194": "E194", "E195": "E195",
    "E196": "E196", "E197": "E197", "E198": "E198", "E199": "E199", "E200": "E200",
    "E201": "E201", "E202": "E202", "E203": "E203", "E204": "E204", "E205": "E205",
    "E206": "E206", "E207": "E207", "E208": "E208", "E209": "E209", "E210": "E210",
    "E211": "E211", "E212": "E212", "E213": "E213", "E214": "E214", "E215": "E215",
    "E216": "E216", "E217": "E217", "E218": "E218", "E219": "E219", "E220": "E220",
    "E221": "E221", "E222": "E222", "E223": "E223", "E224": "E224", "E225": "E225",
    "E226": "E226", "E227": "E227", "E228": "E228", "E229": "E229", "E230": "E230",
    "E231": "E231", "E232": "E232", "E233": "E233", "E234": "E234", "E235": "E235",
    "E236": "E236", "E237": "E237", "E238": "E238", "E239": "E239", "E240": "E240",
    "E241": "E241", "E242": "E242", "E243": "E243", "E244": "E244", "E245": "E245",
    "E246": "E246", "E247": "E247", "E248": "E248", "E249": "E249", "E250": "E250",
    "E251": "E251", "E252": "E252", "E253": "E253", "E254": "E254", "E255": "E255",
    "E256": "E256",
}


def _get_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for EGI channels to standard names."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    # Check if channels already use EGI naming
    for ch_name in existing_names:
        # If channel is already in standard EGI format, keep it
        if ch_name.startswith("E") and ch_name[1:].isdigit():
            continue
        # Try to map from other naming conventions if needed
        # For now, assume EGI naming or keep original

    return rename_map


# =============================================================================
# Event Handling
# =============================================================================
def _load_events_tsv(file_path: str) -> Optional[pd.DataFrame]:
    """Load events from BIDS events.tsv sidecar file."""
    # Construct events.tsv path from eeg file path
    base_path = file_path.replace("_eeg.edf", "").replace("_eeg.set", "").replace("_eeg.vhdr", "").replace("_eeg.eeg", "")
    events_file = base_path + "_events.tsv"

    if not os.path.exists(events_file):
        # Try alternative: look for events.tsv in same directory
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path).split("_eeg")[0]
        alt_events_file = os.path.join(dir_name, base_name + "_events.tsv")
        if os.path.exists(alt_events_file):
            events_file = alt_events_file
        else:
            return None

    try:
        df = pd.read_csv(events_file, sep="\t")
        return df
    except Exception:
        return None


def _events_to_annotations(events_df: pd.DataFrame) -> mne.Annotations:
    """Convert BIDS events.tsv to MNE Annotations."""
    onsets = events_df["onset"].values.astype(float)
    durations = events_df["duration"].values.astype(float)
    # Use trial_type if available, otherwise value
    if "trial_type" in events_df.columns:
        descriptions = events_df["trial_type"].astype(str).values
    elif "value" in events_df.columns:
        descriptions = events_df["value"].astype(str).values
    else:
        descriptions = np.array(["unknown"] * len(events_df))

    # Handle NaN durations (common in BIDS where duration=0 means instantaneous)
    durations = np.where(np.isnan(durations), 0.0, durations)

    return mne.Annotations(
        onset=onsets,
        duration=durations,
        description=descriptions,
    )


# =============================================================================
# Kernel Class
# =============================================================================
class OpenNeuroDS003004Kernel:
    """Stage1 kernel for OpenNeuro ds003004 (Imagined Emotion Study)."""

    KERNEL_ID: str = "openneuro-ds003004-stage1"
    HANDLES_UNAVAILABLE: bool = False

    # Required info fields from participants.tsv
    REQUIRED_INFO_FIELDS: List[str] = ["Age", "Gender", "Handedness", "YOB"]

    def __init__(self):
        self._participants_cache: Optional[Dict[str, Dict[str, str]]] = None
        self._dataset_path: Optional[str] = None

    def _get_dataset_path(self, udataset) -> str:
        """Extract dataset path from udataset."""
        if hasattr(udataset, "dataset_path"):
            return str(udataset.dataset_path)
        # Try to infer from file paths
        return ""

    def _get_subject_info(self, udataset, row) -> Dict[str, str]:
        """Get subject info from participants.tsv with required fields."""
        dataset_path = self._get_dataset_path(udataset)

        # Load participants.tsv if not cached
        if self._participants_cache is None or self._dataset_path != dataset_path:
            self._participants_cache = _load_participants_tsv(dataset_path)
            self._dataset_path = dataset_path

        # Extract subject ID from file path
        file_path = row.get("File Path", "")
        subject_id = "unknown"

        # Parse sub-XX from path
        import re
        match = re.search(r'sub-(\w+)', file_path)
        if match:
            subject_id = f"sub-{match.group(1)}"

        # Get base subject info
        base_info = self._participants_cache.get(subject_id, {})

        # Build required fields from participants.tsv columns
        # Read participants.tsv directly for required fields
        participants_file = os.path.join(dataset_path, "participants.tsv")
        required_fields: Dict[str, str] = {}

        if os.path.exists(participants_file):
            try:
                df = pd.read_csv(participants_file, sep="\t")
                subject_row = df[df["participant_id"] == subject_id]
                if len(subject_row) > 0:
                    sr = subject_row.iloc[0]
                    for field in self.REQUIRED_INFO_FIELDS:
                        val = sr.get(field, "unknown")
                        if pd.isna(val) or str(val).strip() == "":
                            required_fields[field] = "unknown"
                        else:
                            required_fields[field] = str(val)
                else:
                    for field in self.REQUIRED_INFO_FIELDS:
                        required_fields[field] = "unknown"
            except Exception:
                for field in self.REQUIRED_INFO_FIELDS:
                    required_fields[field] = "unknown"
        else:
            for field in self.REQUIRED_INFO_FIELDS:
                required_fields[field] = "unknown"

        # Merge base info with required fields
        info = {
            "age": base_info.get("age", "unknown"),
            "sex": base_info.get("sex", "unknown"),
            "handedness": base_info.get("handedness", "unknown"),
            **required_fields,  # Include all required fields from participants.tsv
        }

        return info

    def _get_device_info(self) -> Dict[str, str]:
        """Get device info for this dataset."""
        # Source: Paper DOI 10.1016/j.neuroimage.2022.118873
        # "Electrical Geodesics Inc. (EGI) 256-channel system"
        # Annotator: LLM (from paper), 2026-04-08
        # 由 LLM 推断，需人类复核
        return {
            "amplifier": "EGI Net Amps 400",  # LLM 推断，需人类复核
            "cap": "HydroCel Geodesic Sensor Net 256",  # LLM 推断，需人类复核
        }

    def _ensure_misc_channels(self, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Ensure required native and derived misc channels exist."""
        # Required native misc channels: none specifically required for this dataset
        # Required derived misc channels: none specifically required
        # But we need to ensure any stimulus channels are properly typed

        # Check for any channels that should be misc
        ch_types = raw.get_channel_types()
        ch_names = raw.ch_names

        # EGI systems often have reference channels or other non-EEG channels
        misc_channels = []
        for ch_name, ch_type in zip(ch_names, ch_types):
            # Channels like VREF, Cz reference, etc. should be misc
            if ch_name.upper() in ["VREF", "REF", "CzREF", "REFCz"]:
                misc_channels.append(ch_name)

        if misc_channels:
            type_updates = {ch: "misc" for ch in misc_channels}
            raw.set_channel_types(type_updates)

        return raw

    def _rename_channels(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Rename channels to standard names if needed."""
        rename_map = _get_channel_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
        return raw

    def _set_montage(self, raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
        """Set EEG montage for EGI 256-channel system."""
        try:
            # Try to use standard EGI 256 montage
            montage = mne.channels.make_standard_montage("GSN-HydroCel-256")
            # Rename montage channels to match raw if needed
            raw.set_montage(montage, match_case=False, on_missing="warn")
        except Exception:
            # If standard montage fails, try to create from channel positions
            # or skip montage setting
            pass
        return raw

    def _add_events_from_tsv(self, raw: mne.io.BaseRaw, file_path: str) -> mne.io.BaseRaw:
        """Add annotations from BIDS events.tsv if raw lacks events."""
        # Check if raw already has meaningful annotations
        existing_annotations = raw.annotations
        has_events = len(existing_annotations) > 0

        # For EDF files without annotations, or SET files without events
        needs_events = False
        if file_path.endswith(".edf"):
            # EDF may not have annotations
            needs_events = not has_events
        elif file_path.endswith(".set"):
            # EEGLAB .set may or may not have events
            needs_events = not has_events
        elif file_path.endswith(".fif"):
            # Plain .fif without events
            needs_events = not has_events

        if not needs_events and has_events:
            # Check if existing annotations are meaningful
            descs = set(existing_annotations.description)
            if len(descs) <= 1 and "" in descs:
                needs_events = True

        if needs_events:
            events_df = _load_events_tsv(file_path)
            if events_df is not None and len(events_df) > 0:
                annotations = _events_to_annotations(events_df)
                raw.set_annotations(annotations)

        return raw

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            The modified Raw object.
        """
        file_path = row.get("File Path", "")

        # 1. Channel rename BEFORE set_montage()
        raw = self._rename_channels(raw)

        # 2. Set montage for EGI 256-channel system
        raw = self._set_montage(raw)

        # 3. Ensure misc channels
        raw = self._ensure_misc_channels(raw, row)

        # 4. Add events from events.tsv if raw lacks them
        raw = self._add_events_from_tsv(raw, file_path)

        # 5. Get subject and device info
        subject_info = self._get_subject_info(udataset, row)
        device_info = self._get_device_info()

        # 6. Build eegunity_description
        original_desc = raw.info.get("description", "")
        if original_desc is None:
            original_desc = ""

        # Prepare required info fields for eegunity_description
        required_info: Dict[str, str] = {}
        for field in self.REQUIRED_INFO_FIELDS:
            required_info[field] = subject_info.get(field, "unknown")

        eegunity_description = {
            "age": subject_info.get("age", "unknown"),
            "sex": subject_info.get("sex", "unknown"),
            "amplifier": device_info.get("amplifier", "unknown"),
            "cap": device_info.get("cap", "unknown"),
            "handedness": subject_info.get("handedness", "unknown"),
            **required_info,  # Include all required participants.tsv fields
        }

        description_dict = {
            "original_description": original_desc,
            "eegunity_description": eegunity_description,
        }

        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003004Kernel()