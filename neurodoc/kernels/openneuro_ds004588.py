"""OpenNeuro DS004588 (Neuma Neuromarketing) stage1 kernel for EEGUnity.

Dataset: 42 subjects, 6 EEG channels, 300 Hz sampling rate.
Paradigm: Participants browsed supermarket product brochures and clicked
          products they intended to purchase. EEG recorded alongside mouse
          interaction data.

Source: https://openneuro.org/datasets/ds004588
        DOI: 10.1038/s41597-023-02392-9
        DOI: 10.1186/s40708-025-00272-z
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mne


# ============================================================================
# Channel Mapping
# ============================================================================
# The dataset contains only 6 EEG channels. Based on the NeuMa dataset paper
# (DOI: 10.1038/s41597-023-02392-9), the original 19-channel 10-20 system
# includes: Fp1, Fp2, F7, F3, Fz, F4, F8, T7, C3, Cz, C4, T8, P7, P3, Pz, P4,
# P8, O1, Oz. With only 6 channels, typical neuromarketing studies focus on
# frontal/central/parietal regions.
#
# LLM inference (2026-01-20): Based on standard neuromarketing paradigms and
# the 10-20 system, the 6 channels are most likely: Fz, Cz, Pz, C3, C4, Oz.
# These cover key decision-making regions (frontal) and visual processing
# (occipital). This mapping should be verified against the original data
# documentation or by inspecting raw channel names.
# Annotator: LLM, 2026-01-20, Source: DOI 10.1038/s41597-023-02392-9 (NeuMa paper)
_CH_RENAME_MAP: Dict[str, str] = {
    "EEG-1": "Fz",
    "EEG-2": "Cz",
    "EEG-3": "Pz",
    "EEG-4": "C3",
    "EEG-5": "C4",
    "EEG-6": "Oz",
}


# ============================================================================
# Event ID Mapping (raw meta)
# ============================================================================
# Raw events from the dataset. These are mapped to standardized names.
# Admin events (MouseWheel) are prefixed with "admin:" as per rulebook.
_RAW_EVENT_MAP: Dict[int, str] = {
    1: "MouseButtonLeft pressed",
    2: "MouseButtonLeft released",
    3: "Category:IMG=ID:FYLLADIO_1.tif=Type:Leaflet_Images_1",
    4: "Category:IMG=ID:FYLLADIO_2.tif=Type:Leaflet_Images_1",
    5: "MouseWheelDown120 pressed",
    6: "MouseWheelUp120 pressed",
    7: "fixation_cross",
    8: "EOE",
}


@dataclass
class NeumaKernel:
    """Stage1 kernel for the Neuma (Neuromarketing) dataset.

    This kernel handles the OpenNeuro ds004588 dataset, which contains
    neuromarketing EEG data with mouse interaction events.

    Attributes
    ----------
    KERNEL_ID : str
        Unique identifier for this kernel.

    Notes
    -----
    - Subject age/sex: Not provided in dataset (inferred as "unknown").
    - Amplifier: Not specified in dataset documentation (inferred).
    - Channel mapping: LLM inference based on standard neuromarking paradigms.
    """

    KERNEL_ID: str = "openneuro-ds004588-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path and other metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with standardized channels, events,
            and metadata.
        """
        # ------------------------------------------------------------------
        # Step 1: Channel Renaming (before set_montage)
        # ------------------------------------------------------------------
        existing_chs = set(raw.ch_names)
        rename_map = {}

        for old_name, new_name in _CH_RENAME_MAP.items():
            if old_name in existing_chs:
                rename_map[old_name] = new_name
            elif old_name.replace("EEG-", "") in existing_chs:
                # Handle case where channels are numbered 1-6
                rename_map[old_name.replace("EEG-", "")] = new_name

        if rename_map:
            mne.rename_channels(raw.info, rename_map)

        # ------------------------------------------------------------------
        # Step 2: Set Montage (10-20 system)
        # ------------------------------------------------------------------
        # After renaming, set standard 10-20 montage if all expected
        # channels are present
        try:
            montage = mne.channels.make_standard_montage("standard_1020")
            raw.set_montage(montage, on_missing="warn")
        except Exception:
            pass  # Montage setting is best-effort

        # ------------------------------------------------------------------
        # Step 3: Remap Annotations/Events
        # ------------------------------------------------------------------
        if raw.annotations is not None and len(raw.annotations) > 0:
            desc_map = {}
            for orig_id, new_name in _RAW_EVENT_MAP.items():
                if str(orig_id) in raw.annotations.description:
                    desc_map[str(orig_id)] = new_name
                elif orig_id in raw.annotations.description:
                    desc_map[str(orig_id)] = new_name

            if desc_map:
                new_descriptions = []
                for desc in raw.annotations.description:
                    new_desc = desc_map.get(str(desc), desc)
                    new_descriptions.append(new_desc)

                new_annotations = mne.Annotations(
                    onset=raw.annotations.onset,
                    duration=raw.annotations.duration,
                    description=new_descriptions,
                    ch_names=raw.annotations.ch_names,
                )
                raw.set_annotations(new_annotations)

        # ------------------------------------------------------------------
        # Step 4: Update description with eegunity metadata
        # ------------------------------------------------------------------
        original_desc = raw.info.get("description", "")

        # Subject information (from dataset - all missing)
        # Source: Dataset documentation (participants.tsv not available)
        # inferred by LLM, needs human review
        subject_id = row.get("subject_id", "unknown")
        age = "unknown"  # Not provided in dataset
        sex = "unknown"  # Not provided in dataset
        handedness = "unknown"  # Not provided in dataset

        # Amplifier information
        # Source: DOI 10.1038/s41597-023-02392-9 (NeuMa paper)
        # The paper mentions "19 EEG channels" but actual data has 6.
        # Specific amplifier model not documented. inferred by LLM, needs human review
        amplifier = "unknown"

        # Cap information
        # Source: DOI 10.1038/s41597-023-02392-9
        # Not specified in documentation. inferred by LLM, needs human review
        cap = "unknown"

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": age,
                "sex": sex,
                "amplifier": amplifier,
                "cap": cap,
                "handedness": handedness,
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = NeumaKernel()