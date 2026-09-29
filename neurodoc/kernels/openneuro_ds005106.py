"""Dataset-specific kernel for openneuro ds005106.

Human Infant EEG for 200 Object Images in Rapid Visual Streams (RSVP).
32-channel infant EEG at 500 Hz. Event codes 1-200 represent distinct object
images; code -1 is a baseline/inter-stimulus marker.

Source: https://doi.org/10.1038/s41597-025-04744-z
        https://doi.org/10.31234/osf.io/dzrkq
"""

from __future__ import annotations

import json
import os
import sys

import mne

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from kernels.openneuro_specific._base import OpenNeuroBaseKernel


# Channel naming for 32-channel infant EEG cap.
# Source: Dataset documentation / paper methodology (32-channel infant cap layout)
# inferred by LLM, needs human review
_EEG_CHANNEL_RENAME_MAP = {
    "EEG-1": "Fp1",
    "EEG-2": "Fpz",
    "EEG-3": "Fp2",
    "EEG-4": "AF3",
    "EEG-5": "AF4",
    "EEG-6": "F7",
    "EEG-7": "F3",
    "EEG-8": "Fz",
    "EEG-9": "F4",
    "EEG-10": "F8",
    "EEG-11": "FC5",
    "EEG-12": "FC3",
    "EEG-13": "FC1",
    "EEG-14": "FCz",
    "EEG-15": "FC2",
    "EEG-16": "FC4",
    "EEG-17": "FC6",
    "EEG-18": "M1",
    "EEG-19": "C5",
    "EEG-20": "C3",
    "EEG-21": "C1",
    "EEG-22": "Cz",
    "EEG-23": "C2",
    "EEG-24": "C4",
    "EEG-25": "C6",
    "EEG-26": "M2",
    "EEG-27": "CP5",
    "EEG-28": "CP3",
    "EEG-29": "CP1",
    "EEG-30": "CPz",
    "EEG-31": "CP2",
    "EEG-32": "CP4",
    "EEG-33": "CP6",
    "EEG-34": "P7",
    "EEG-35": "P3",
    "EEG-36": "Pz",
    "EEG-37": "P4",
    "EEG-38": "P8",
    "EEG-39": "PO3",
    "EEG-40": "PO4",
    "EEG-41": "O1",
    "EEG-42": "Oz",
    "EEG-43": "O2",
    "EEG-44": "POz",
    "EOG-left": "EOG-left",
    "EOG-right": "EOG-right",
    "EOG-up": "EOG-up",
    "EOG-down": "EOG-down",
}


def _rename_channels(raw, rename_map):
    """Rename channels using the provided map."""
    rename_dict = {}
    for old_name in raw.ch_names:
        if old_name in rename_map:
            rename_dict[old_name] = rename_map[old_name]
    if rename_dict:
        raw.rename_channels(rename_dict)
    return raw


def _apply_montage_if_possible(raw):
    """Attempt to set standard 10-20 montage."""
    try:
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage, on_missing="warn")
    except Exception:
        pass


class OpenNeuroDS005106Kernel(OpenNeuroBaseKernel):
    """Stage1 kernel for openneuro ds005106 infant RSVP EEG dataset."""

    KERNEL_ID: str = "openneuro-ds005106-stage1"

    # Event mapping for raw meta: numeric codes to readable labels
    # Codes 1-200 map to object IDs; -1 is baseline/inter-stimulus marker
    _EVENT_MAP = {
        -1: "baseline",
    }
    # Add object IDs 1-200
    _EVENT_MAP.update({i: f"object_{i}" for i in range(1, 201)})

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset : EEGUnity dataset context
        raw : mne.io.BaseRaw
            Raw EEG data loaded by EEGUnity.
        row : pandas.Series
            Locator row with file metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw data.
        """
        # Store original description
        original_desc = raw.info.get("description", "")

        # Update description with eegunity_description metadata.
        # Age: infants (specific age range unknown from dataset documentation)
        # inferred by LLM, needs human review
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": "unknown",
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        # Rename channels BEFORE set_montage()
        raw = _rename_channels(raw, _EEG_CHANNEL_RENAME_MAP)

        # Apply standard 10-20 montage if possible
        _apply_montage_if_possible(raw)

        # Extract events from annotations if available
        try:
            if len(raw.annotations) > 0:
                # Convert event annotations to numeric codes for consistency
                # The raw.annotations may contain string descriptions
                onset_list = []
                duration_list = []
                description_list = []

                for i, desc in enumerate(raw.annotations.description):
                    try:
                        code = int(desc) if desc.isdigit() or desc.startswith("-") else None
                        if code is not None:
                            if code == -1:
                                onset_list.append(raw.annotations.onset[i])
                                duration_list.append(raw.annotations.duration[i])
                                description_list.append("baseline")
                            elif 1 <= code <= 200:
                                onset_list.append(raw.annotations.onset[i])
                                duration_list.append(raw.annotations.duration[i])
                                description_list.append(f"object_{code}")
                    except (ValueError, AttributeError):
                        # Keep original description if not numeric
                        pass

                if onset_list:
                    new_annotations = mne.Annotations(
                        onset=onset_list,
                        duration=duration_list,
                        description=description_list,
                    )
                    raw.set_annotations(new_annotations)
        except Exception:
            # If annotation extraction fails, keep original
            pass

        return raw


KERNEL = OpenNeuroDS005106Kernel()