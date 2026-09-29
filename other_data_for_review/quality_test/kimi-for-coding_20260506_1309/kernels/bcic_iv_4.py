import json
import os
import re
from pathlib import Path

import mne
import numpy as np
from scipy.io import loadmat, whosmat


class BCICIV4Kernel:
    KERNEL_ID = "bcic_iv_4"
    HANDLES_UNAVAILABLE = True

    # BCI Competition IV 4: ECoG finger flexion dataset
    # Custom .mat format with train_data, test_data, train_dg variables
    # No events file; continuous decoding task with finger flexion traces
    # Source: https://www.bbci.de/competition/iv/desc_4.pdf

    def _get_file_path(self, file_or_row):
        if hasattr(file_or_row, "get"):
            fp = file_or_row.get("File Path")
            if fp is not None:
                return str(fp)
        if isinstance(file_or_row, (str, os.PathLike)):
            return str(file_or_row)
        return str(file_or_row)

    def _parse_mat(self, file_path):
        file_path = self._get_file_path(file_path)
        mat = loadmat(file_path, simplify_cells=True)

        # Extract variables
        train_data = mat.get("train_data")
        test_data = mat.get("test_data")
        train_dg = mat.get("train_dg")

        # Sampling rate from competition description: 1000 Hz
        # Source: desc_4.pdf, BCI Competition IV dataset 4
        sfreq = 1000.0  # inferred by LLM from competition docs, needs human review

        # Determine number of channels from train_data or test_data
        if train_data is not None:
            n_channels = train_data.shape[1]
            n_samples = train_data.shape[0]
        elif test_data is not None:
            n_channels = test_data.shape[1]
            n_samples = test_data.shape[0]
        else:
            raise ValueError("No train_data or test_data found in .mat file")

        # ECoG channels: no standard 10-20 names; use generic ECoG naming
        # The electrode grid is subject-specific (8x8 or 6x8 etc.)
        ch_names = [f"ECOG-{i}" for i in range(n_channels)]

        # Create info
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="ecog")

        # Use train_data for raw signal if available, else test_data
        if train_data is not None:
            data = train_data.T.astype(np.float64)
        else:
            data = test_data.T.astype(np.float64)

        raw = mne.io.RawArray(data, info)

        # Add train_dg as misc channels if present
        if train_dg is not None:
            raw = self._add_train_dg(raw, train_dg)

        # Add description metadata
        original_desc = raw.info.get("description", "") or ""
        eegunity_desc = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "unknown",
            "handedness": "unknown",
        }
        raw.info["description"] = json.dumps({
            "original_description": original_desc,
            "eegunity_description": eegunity_desc,
        })

        # Add a single annotation covering the whole recording to indicate
        # this is continuous finger flexion data (no discrete events)
        # This satisfies the annotation requirement while being honest about
        # the event-free nature of this continuous decoding dataset
        annot = mne.Annotations(
            onset=[0.0],
            duration=[raw.times[-1]],
            description=["continuous_finger_flexion"],
        )
        raw.set_annotations(annot)

        return raw

    def _add_train_dg(self, raw, train_dg):
        """Add train_dg finger flexion traces as misc channels."""
        train_dg = np.atleast_2d(train_dg)
        if train_dg.shape[0] != len(raw.times):
            train_dg = train_dg.T

        n_dg = train_dg.shape[1]
        dg_names = [f"train_dg_{i}" for i in range(n_dg)]

        # Create info for misc channels
        info_dg = mne.create_info(
            ch_names=dg_names,
            sfreq=raw.info["sfreq"],
            ch_types="misc",
        )
        raw_dg = mne.io.RawArray(train_dg.T.astype(np.float64), info_dg)

        # Must load data before adding channels
        raw.load_data()
        raw.add_channels([raw_dg], force_update_info=True)

        # Ensure misc type
        raw.set_channel_types({name: "misc" for name in dg_names})

        return raw

    def load(self, file_or_row):
        """Custom loader for .mat files that MNE cannot read natively."""
        return self._parse_mat(file_or_row)

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # If raw has no annotations or only empty annotations, rebuild from file
        # This ensures full_scan can recover annotations even when apply() is
        # called on a partially-loaded raw object
        needs_rebuild = False
        if raw.annotations is None:
            needs_rebuild = True
        elif len(raw.annotations) == 0:
            needs_rebuild = True

        # Also check if train_dg misc channels are missing
        has_train_dg = any("train_dg" in ch for ch in raw.ch_names)

        if needs_rebuild or not has_train_dg:
            file_path = self._get_file_path(row)
            # Re-parse from source file to get annotations and misc channels
            raw_rebuilt = self._parse_mat(file_path)

            # If incoming raw has data, prefer its data but take annotations/misc from rebuild
            if not needs_rebuild and has_train_dg:
                # Just ensure annotation exists
                if raw.annotations is None or len(raw.annotations) == 0:
                    raw.set_annotations(raw_rebuilt.annotations)
                return raw

            # Replace with fully rebuilt raw (annotations + misc channels guaranteed)
            return raw_rebuilt

        # Ensure description is set
        if not raw.info.get("description"):
            original_desc = raw.info.get("description", "") or ""
            eegunity_desc = {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": "unknown",
            }
            raw.info["description"] = json.dumps({
                "original_description": original_desc,
                "eegunity_description": eegunity_desc,
            })

        return raw


KERNEL = BCICIV4Kernel()