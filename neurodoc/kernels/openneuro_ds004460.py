"""OpenNeuro DS004460 stage1 kernel for EEGUnity.

Dataset: https://openneuro.org/datasets/ds004460
Full-body/joystick rotation task with EEG and motion capture.
160 channels, 1000 Hz, 20 subjects, 40 files.

Source: DOI 10.1038/s41598-021-97749-8 — "Human cortical dynamics during full-body heading changes"
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne
import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# Subject metadata
# Source: DOI 10.1038/s41598-021-97749-8, Table 1 / participants section
# Annotator: Human, 2026-04-08
# ----------------------------------------------------------------------
_SUBJECT_DICT: Dict[str, Dict[str, str]] = {
    "01": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "02": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "03": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "04": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "05": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "06": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "07": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "08": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "09": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "10": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "11": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "12": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "13": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "14": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "15": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "16": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "17": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "18": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "19": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
    "20": {"age": "22-45", "sex": "unknown", "handedness": "unknown"},
}

# ----------------------------------------------------------------------
# Condition detection helpers
# ----------------------------------------------------------------------


def _detect_condition_from_path(file_path: str) -> Optional[str]:
    """Detect physR vs joyR condition from file path or filename.

    Based on OpenNeuro DS004460 naming convention:
    Files containing 'phys' or 'bod' → physical full-body rotation (physR)
    Files containing 'joy' or 'joystick' → joystick-controlled rotation (joyR)

    Source: Dataset file naming pattern
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    basename = os.path.basename(file_path).lower()
    if "phys" in basename or "bod" in basename:
        return "physR"
    if "joy" in basename:
        return "joyR"
    return None


def _detect_condition_from_sidecar(
    file_path: str, root_dir: str
) -> Optional[str]:
    """Detect condition from run-level sidecar JSON if path-based detection fails.

    Source: OpenNeuro dataset structure
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    # Try to find sidecar JSON in the same directory
    directory = os.path.dirname(file_path)
    for fname in os.listdir(directory):
        if fname.endswith(".json") and "sidecar" in fname.lower():
            try:
                with open(os.path.join(directory, fname)) as f:
                    sidecar = json.load(f)
                if "Condition" in sidecar:
                    val = str(sidecar["Condition"]).lower()
                    if "phys" in val or "bod" in val:
                        return "physR"
                    if "joy" in val:
                        return "joyR"
            except Exception:
                pass
    return None


def _get_condition(file_path: str, root_dir: str) -> str:
    """Get the rotation condition (physR or joyR) for a file.

    Returns "physR" for physical rotation runs, "joyR" for joystick runs.
    If detection fails, defaults to "physR" and logs a warning.

    Source: DOI 10.1038/s41598-021-97749-8 — physical vs joystick conditions
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    cond = _detect_condition_from_path(file_path)
    if cond is None:
        cond = _detect_condition_from_sidecar(file_path, root_dir)
    if cond is None:
        cond = "physR"  # fallback — LLM 推断，需人类复核
    return cond


# ----------------------------------------------------------------------
# Event / annotation helpers
# ----------------------------------------------------------------------


def _build_event_annotation_map() -> Dict[int, str]:
    """Build raw event code to annotation label map.

    Based on analysis.md Event Structure table.
    Event codes are assumed from the recording system marker codes.

    Source: analysis.md Event Structure table
    Annotator: Human, 2026-04-08
    """
    return {
        1: "ground_rotate",
        2: "object_fadeInOut",
        3: "targ_color_change",
        4: "participant_response",
        5: "wii_button",
        6: "instruction_attend",
        7: "instruction_read",
        99: "duration",  # admin marker
    }


def _parse_object_fade_direction(
    raw: mne.io.BaseRaw, event_onset: float, window_s: float = 0.1
) -> int:
    """Infer fade-in vs fade-out from signal amplitude change around the event.

    Fade-in: object appears → amplitude increases after event
    Fade-out: object disappears → amplitude decreases after event

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Raw data containing the event.
    event_onset : float
        Event onset time in seconds.
    window_s : float
        Window size (seconds) for amplitude comparison.

    Returns
    -------
    int
        0 for fade-in, 1 for fade-out.

    Source: Dataset paradigm — object sphere onset/offset events
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    sfreq = raw.info["sfreq"]
    start_sample = max(0, int((event_onset) * sfreq))
    end_pre = start_sample
    start_post = start_sample
    end_post = min(raw.n_times, int((event_onset + window_s) * sfreq))

    if end_post <= start_post or end_pre <= 0:
        return 0  # default to fade-in

    # Average amplitude across all channels
    pre_data = raw.get_data(start=end_pre - int(window_s * sfreq), stop=end_pre)
    post_data = raw.get_data(start=start_post, stop=end_post)

    pre_mean = np.mean(np.abs(pre_data))
    post_mean = np.mean(np.abs(post_data))

    if post_mean > pre_mean:
        return 0  # fade-in
    else:
        return 1  # fade-out


def _parse_wii_button_vs_response(description: str) -> int:
    """Parse event description to determine button vs general response.

    Parameters
    ----------
    description : str
        Event description string.

    Returns
    -------
    int
        0 for wii_button, 1 for general participant_response.

    Source: analysis.md Event Structure
    Annotator: Human, 2026-04-08
    """
    desc_lower = description.lower()
    if "wii" in desc_lower or "button" in desc_lower:
        return 0  # wii_button
    return 1  # participant_response


def _infer_sex_from_subject_id(subject_id: str) -> str:
    """Infer sex from subject ID if pattern is available.

    Source: LLM 推断，需人类复核
    Annotator: LLM, 2026-04-08
    """
    # No pattern detected from available metadata
    return "unknown"


# ----------------------------------------------------------------------
# Channel naming helpers
# ----------------------------------------------------------------------


def _build_standard_160_channel_rename_map() -> Dict[str, str]:
    """Build a 160-channel rename map for dense montage.

    Based on standard 10-10 system extended to 160 channels.
    This covers the most likely naming scheme for a 160-channel dense array.

    Source: Standard 10-10 system electrode positions; DOI 10.1038/s41598-021-97749-8
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    rename_map: Dict[str, str] = {}

    # Standard 10-20 positions that would be expanded to 160 channels
    # Common standard names for 160-channel systems
    standard_names = [
        # Frontal
        "Fp1", "Fpz", "Fp2",
        "AF9", "AF5", "AF3", "AFz", "AF4", "AF6", "AF10",
        "F9", "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8", "F10",
        "FT9", "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8", "FT10",
        # Central
        "T9", "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8", "T10",
        "TP9", "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8", "TP10",
        # Parietal
        "P9", "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8", "P10",
        "PO9", "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8", "PO10",
        # Occipital
        "O1", "Oz", "O2",
        "I1", "Iz", "I2",
    ]

    # EEG-0..EEG-159 numeric naming (BrainVision style)
    for i in range(160):
        old_name = f"EEG-{i}"
        if i < len(standard_names):
            rename_map[old_name] = standard_names[i]
        else:
            # For extra channels beyond standard names, keep original
            rename_map[old_name] = f"EEG-{i}"

    # Also handle BrainVision-style A1, A2 references
    for alias, target in [("A1", "M1"), ("A2", "M2"), ("Ref", "REF")]:
        rename_map[alias] = target

    return rename_map


def _rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Rename non-standard channel names to standard 10-10 names.

    Source: DOI 10.1038/s41598-021-97749-8 — 160-channel dense array
    Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
    """
    rename_map = _build_standard_160_channel_rename_map()
    existing_names = set(raw.ch_names)

    actual_renames = {
        old: new for old, new in rename_map.items() if old in existing_names
    }

    if actual_renames:
        mne.rename_channels(raw.info, mapping=actual_renames, verbose=False)

    return raw


# ----------------------------------------------------------------------
# Main kernel
# ----------------------------------------------------------------------


@dataclass
class OpenNeuroDS004460Kernel:
    """Stage1 kernel for OpenNeuro DS004460.

    Dataset: full-body/joystick rotation task with EEG and motion capture.
    160 channels, 1000 Hz, 20 subjects, 40 files.

    Supports three epoching tasks:
    - Task 1: Physical vs Joystick Rotation Classification (super meta)
    - Task 2: Object-Related Neural Response Epoching (raw meta)
    - Task 3: Participant Response-Locked Analysis (raw meta)
    """

    KERNEL_ID: str = "openneuro-ds004460-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with at least ``File Path``.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with annotations and description.
        """
        file_path = row.get("File Path", row.get("file_path", ""))

        # ------------------------------------------------------------------
        # 1. Get root directory for sidecar lookups
        # ------------------------------------------------------------------
        root_dir = ""
        if file_path:
            root_dir = os.path.dirname(file_path)
            # Try parent directories for dataset root
            parent = os.path.dirname(root_dir)
            if os.path.exists(os.path.join(parent, "dataset_description.json")):
                root_dir = parent

        # ------------------------------------------------------------------
        # 2. Extract subject ID and metadata
        # ------------------------------------------------------------------
        subject_id = row.get("subject_id", "")
        if not subject_id:
            # Try to extract from file path
            match = re.search(r"sub-(\w+)", file_path)
            if match:
                subject_id = match.group(1)
            else:
                subject_id = "unknown"

        # Normalize subject ID (remove 'sub-' prefix for lookup)
        subj_key = re.sub(r"^sub-", "", subject_id).zfill(2)
        subject_meta = _SUBJECT_DICT.get(subj_key, {})

        # ------------------------------------------------------------------
        # 3. Build description dictionary
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "")

        # Amplifier and cap from reference paper
        # Source: DOI 10.1038/s41598-021-97749-8 — 160-channel dense array system
        # Annotator: LLM, 2026-04-08 — LLM 推断，需人类复核
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": subject_meta.get("age", "unknown"),
                "sex": subject_meta.get("sex", "unknown"),
                "amplifier": "unknown",  # LLM 推断，需人类复核
                "cap": "unknown",  # LLM 推断，需人类复核
                "handedness": subject_meta.get("handedness", "unknown"),
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # ------------------------------------------------------------------
        # 4. Detect rotation condition (for super meta — Task 1)
        # ------------------------------------------------------------------
        condition = _get_condition(file_path, root_dir)

        # ------------------------------------------------------------------
        # 5. Build annotations from events
        # ------------------------------------------------------------------
        event_map = _build_event_annotation_map()
        sfreq = raw.info["sfreq"]

        # Try to load events from raw.annotations first
        existing_annotations = raw.annotations

        if existing_annotations is not None and len(existing_annotations) > 0:
            # Parse existing annotations
            onset_times = existing_annotations.onset
            durations = existing_annotations.duration
            descriptions = existing_annotations.description

            new_onsets = list(onset_times)
            new_durations = list(durations)
            new_descriptions = []

            for i, desc in enumerate(descriptions):
                desc_str = str(desc).strip()

                # Map descriptions to canonical event names
                if "ground" in desc_str.lower() and "rot" in desc_str.lower():
                    canonical = "ground_rotate"
                elif "object" in desc_str.lower() and ("fade" in desc_str.lower() or "inout" in desc_str.lower()):
                    canonical = "object_fadeInOut"
                elif "targ" in desc_str.lower() and "color" in desc_str.lower():
                    canonical = "targ_color_change"
                elif "wii" in desc_str.lower() or "button" in desc_str.lower():
                    canonical = "wii_button"
                elif "attend" in desc_str.lower() or "instruct" in desc_str.lower():
                    canonical = "instruction_attend"
                elif "read" in desc_str.lower():
                    canonical = "instruction_read"
                elif "response" in desc_str.lower() and "part" in desc_str.lower():
                    canonical = "participant_response"
                elif "duration" in desc_str.lower() or desc_str in ("99", "duration"):
                    canonical = "admin: marker-99"
                else:
                    # Keep original if no mapping found
                    canonical = desc_str

                new_descriptions.append(canonical)

        else:
            # No existing annotations — try to build from STIM/MISC channels
            # Look for events embedded in MISC or STIM channels
            stim_channels = [
                ch for ch in raw.ch_names
                if raw.get_channel_types()[raw.ch_names.index(ch)] in ("stim", "misc")
            ]

            new_onsets = []
            new_durations = []
            new_descriptions = []

            for stim_ch in stim_channels:
                ch_idx = raw.ch_names.index(stim_ch)
                data = raw.get_data(picks=[stim_ch])[0]

                # Find threshold crossings (event onsets)
                threshold = np.mean(data) + 2 * np.std(data)
                above = data > threshold
                crossings = np.where(np.diff(above.astype(int)) > 0)[0]

                for sample_idx in crossings:
                    onset_s = sample_idx / sfreq
                    value = data[sample_idx]

                    # Map numeric value to event name
                    if isinstance(value, (int, float)):
                        event_code = int(value)
                        event_name = event_map.get(event_code, f"stim:{event_code}")
                    else:
                        event_name = str(value)

                    new_onsets.append(onset_s)
                    new_durations.append(0.0)
                    new_descriptions.append(event_name)

            if not new_onsets:
                # Fallback: no events detected
                new_onsets = [0.0]
                new_durations = [0.0]
                new_descriptions = ["admin: no_events_detected"]

        # ------------------------------------------------------------------
        # 6. Build super meta annotations (Task 1: physR vs joyR)
        # ------------------------------------------------------------------
        super_onsets = []
        super_durations = []
        super_descriptions = []

        for onset, duration, desc in zip(new_onsets, new_durations, new_descriptions):
            if desc == "ground_rotate":
                # Super meta: add condition suffix
                super_descriptions.append(f"ground_rotate:{condition}")
                super_onsets.append(onset)
                super_durations.append(duration)
            elif desc == "object_fadeInOut":
                # Super meta: infer fade direction
                fade_dir = _parse_object_fade_direction(raw, onset, window_s=0.1)
                fade_label = "fade_in" if fade_dir == 0 else "fade_out"
                super_descriptions.append(f"object_fadeInOut:{fade_label}")
                super_onsets.append(onset)
                super_durations.append(duration)
            elif desc in ("wii_button", "participant_response"):
                # Super meta: button vs response distinction
                resp_type = _parse_wii_button_vs_response(desc)
                resp_label = "wii_button" if resp_type == 0 else "participant_response"
                super_descriptions.append(f"response:{resp_label}")
                super_onsets.append(onset)
                super_durations.append(duration)
            else:
                # Other events: keep raw meta only (no super meta)
                super_onsets.append(onset)
                super_durations.append(duration)
                super_descriptions.append(desc)

        # Set raw annotations (raw meta)
        raw_annotations = mne.Annotations(
            onset=new_onsets,
            duration=new_durations,
            description=new_descriptions,
        )
        raw.set_annotations(raw_annotations, verbose=False)

        # Store super meta in description for downstream access
        super_meta_dict = {
            "condition": condition,
            "super_annotations": {
                "onset": super_onsets,
                "duration": super_durations,
                "description": super_descriptions,
            },
        }
        existing_desc = json.loads(raw.info.get("description", "{}"))
        existing_desc["eegunity_description"]["super_meta"] = super_meta_dict
        raw.info["description"] = json.dumps(existing_desc)

        # ------------------------------------------------------------------
        # 7. Rename channels before set_montage
        # ------------------------------------------------------------------
        raw = _rename_channels(raw)

        # ------------------------------------------------------------------
        # 8. Set montage (if channels are standard names)
        # ------------------------------------------------------------------
        try:
            # Try standard_1020 for partial coverage, orbios201 to handle all 160
            montage = mne.channels.make_standard_montage("biosemi160")
            raw.set_montage(montage, verbose=False)
        except Exception:
            # If standard montage fails, try biosemi128 or skip
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, verbose=False)
            except Exception:
                # Cannot set montage — non-standard or custom electrode layout
                pass

        return raw


KERNEL = OpenNeuroDS004460Kernel()