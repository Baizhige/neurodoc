import json
import os
import re
from pathlib import Path

import mne
import numpy as np
from scipy.io import loadmat


class FigshareMeng2019Kernel:
    KERNEL_ID = "figshare_meng2019"
    HANDLES_UNAVAILABLE = True

    # Standard 64-channel cap used in this dataset
    # Source: 10.3389/fnhum.2019.00128, Meng & He (2019)
    # Annotator: inferred by LLM from paper, needs human review
    # Date: 2026-04-08
    # inferred by LLM, needs human review
    CHANNEL_NAMES_64 = [
        "FP1", "FPZ", "FP2", "AF3", "AF4", "F7", "F5", "F3", "F1", "FZ",
        "F2", "F4", "F6", "F8", "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2",
        "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "CZ", "C2", "C4",
        "C6", "T8", "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6",
        "TP8", "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8",
        "PO7", "PO5", "PO3", "POZ", "PO4", "PO6", "PO8", "CB1", "O1", "OZ",
        "O2", "CB2", "M1", "M2"
    ]

    def _get_file_path(self, source):
        if isinstance(source, str):
            return source
        fp = source.get("File Path") if hasattr(source, "get") else str(source)
        if isinstance(fp, Path):
            fp = str(fp)
        return fp

    def _parse_sampling_frequency(self, sfreq_val):
        """Parse sampling frequency from various formats."""
        if isinstance(sfreq_val, (int, float)):
            return float(sfreq_val)
        sfreq_str = str(sfreq_val).strip()
        # Remove 'Hz' suffix if present
        sfreq_str = sfreq_str.replace('Hz', '').replace('hz', '').strip()
        return float(sfreq_str)

    def _parse_mat_file(self, file_path):
        """Parse the .mat file and return signal data, sfreq, channel names, and experimental states."""
        mat = loadmat(file_path, simplify_cells=True)

        # Extract data
        data = mat["output_data"]  # shape: (n_samples, n_channels)
        n_samples, n_channels = data.shape

        # Transpose to (n_channels, n_samples) for MNE
        data = data.T

        # Sampling frequency - handle string formats like '100Hz', '128Hz'
        sfreq = self._parse_sampling_frequency(mat["Experiment_Parm"]["SamplingFrequency"])

        # Channel names from file, or use standard 64 if mismatch
        ch_names_from_file = mat["Experiment_Parm"]["Channels"]
        if isinstance(ch_names_from_file, np.ndarray):
            ch_names_from_file = ch_names_from_file.tolist()
            if isinstance(ch_names_from_file, list) and len(ch_names_from_file) > 0:
                if isinstance(ch_names_from_file[0], (list, np.ndarray)):
                    ch_names_from_file = [str(c[0]) if isinstance(c, (list, np.ndarray)) else str(c) for c in ch_names_from_file]
                else:
                    ch_names_from_file = [str(c) for c in ch_names_from_file]

        if len(ch_names_from_file) == n_channels:
            ch_names = ch_names_from_file
        else:
            ch_names = self.CHANNEL_NAMES_64[:n_channels]

        # Ensure channel names are strings and unique
        ch_names = [str(c).strip() for c in ch_names]
        # Make unique if duplicates exist
        seen = set()
        unique_ch_names = []
        for c in ch_names:
            base = c
            suffix = 1
            while c in seen:
                c = f"{base}_{suffix}"
                suffix += 1
            seen.add(c)
            unique_ch_names.append(c)
        ch_names = unique_ch_names

        # Experimental states
        exp_states = mat.get("Experimental_states", {})

        # Extract target code (continuous per-sample markers)
        target_code = exp_states.get("TargetCode", np.zeros(n_samples))
        if isinstance(target_code, np.ndarray):
            target_code = target_code.flatten()

        # Extract feedback state
        feedback = exp_states.get("Feedback", np.zeros(n_samples))
        if isinstance(feedback, np.ndarray):
            feedback = feedback.flatten()

        # Extract other states if available
        result_code = exp_states.get("ResultCode", np.zeros(n_samples))
        if isinstance(result_code, np.ndarray):
            result_code = result_code.flatten()

        return {
            "data": data,
            "sfreq": sfreq,
            "ch_names": ch_names,
            "n_samples": n_samples,
            "n_channels": n_channels,
            "target_code": target_code,
            "feedback": feedback,
            "result_code": result_code,
            "experiment_parm": mat.get("Experiment_Parm", {}),
        }

    def _build_annotations(self, target_code, sfreq, n_samples):
        """Build MNE Annotations from continuous target code."""
        # Find transitions in target code
        # TargetCode is 0 for rest/baseline, 1 or 2 for actual classes
        # But per evidence, values are 0 and 1 for two classes

        # Find onsets where target_code changes from 0 to non-0
        annotations = []
        prev_val = 0
        onset_samples = []

        for i, val in enumerate(target_code):
            if val != prev_val:
                if prev_val == 0 and val != 0:
                    # Start of a trial
                    onset_samples.append((i, int(val)))
                prev_val = val

        # Build annotations
        onsets = []
        durations = []
        descriptions = []

        for idx, (sample, code) in enumerate(onset_samples):
            onset_time = sample / sfreq
            # Determine duration: until next onset or end of data
            if idx + 1 < len(onset_samples):
                next_onset = onset_samples[idx + 1][0]
                duration = (next_onset - sample) / sfreq
            else:
                # Last annotation goes to end
                duration = (n_samples - sample) / sfreq

            # Use literal code as description (HC-5)
            desc = str(int(code))

            onsets.append(onset_time)
            durations.append(duration)
            descriptions.append(desc)

        if len(onsets) == 0:
            return mne.Annotations([], [], [])

        return mne.Annotations(onset=onsets, duration=durations, description=descriptions)

    def load(self, source):
        """Custom loader for .mat files that MNE cannot natively read."""
        file_path = self._get_file_path(source)

        parsed = self._parse_mat_file(file_path)

        # Create MNE info
        info = mne.create_info(
            ch_names=parsed["ch_names"],
            sfreq=parsed["sfreq"],
            ch_types="eeg",
        )

        # Create RawArray
        raw = mne.io.RawArray(parsed["data"], info)

        # Build and set annotations
        annot = self._build_annotations(
            parsed["target_code"],
            parsed["sfreq"],
            parsed["n_samples"],
        )
        raw.set_annotations(annot)

        # Store original description
        desc_dict = {
            "original_description": "",
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "64-channel standard cap",
                "handedness": "unknown",
            }
        }

        # Try to extract subject info from filename
        # Format: SubjXX_SYY_ExpZ.mat
        fname = os.path.basename(file_path)
        match = re.match(r"Subj(\d+)_S(\d+)_Exp(\d+)\.mat", fname)
        if match:
            subj_num = match.group(1)
            session = match.group(2)
            exp = match.group(3)
            # inferred by LLM, needs human review
            desc_dict["eegunity_description"]["subject_id"] = f"Subj{subj_num}"
            desc_dict["eegunity_description"]["session"] = session
            desc_dict["eegunity_description"]["experiment"] = exp

        raw.info["description"] = json.dumps(desc_dict)

        return raw

    def apply(self, udataset, raw, row):
        file_path = self._get_file_path(row)

        # If raw has no annotations or is incomplete, rebuild from file
        if raw is None or len(raw.annotations) == 0:
            # Need to load from scratch or rebuild annotations
            parsed = self._parse_mat_file(file_path)

            # If raw is None, create new raw
            if raw is None:
                info = mne.create_info(
                    ch_names=parsed["ch_names"],
                    sfreq=parsed["sfreq"],
                    ch_types="eeg",
                )
                raw = mne.io.RawArray(parsed["data"], info)

            # Build and set annotations
            annot = self._build_annotations(
                parsed["target_code"],
                parsed["sfreq"],
                parsed["n_samples"],
            )
            raw.set_annotations(annot)

        # Build eegunity_description with required fields
        eegunity_description = {
            "age": "unknown",
            "sex": "unknown",
            "amplifier": "unknown",
            "cap": "64-channel standard cap",
            "handedness": "unknown",
        }

        # Try to extract subject info from filename
        fname = os.path.basename(file_path)
        match = re.match(r"Subj(\d+)_S(\d+)_Exp(\d+)\.mat", fname)
        if match:
            subj_num = match.group(1)
            session = match.group(2)
            exp = match.group(3)
            eegunity_description["subject_id"] = f"Subj{subj_num}"
            eegunity_description["session"] = session
            eegunity_description["experiment"] = exp

        # Set description as JSON string
        raw.info["description"] = json.dumps({
            "original_description": raw.info.get("description", ""),
            "eegunity_description": eegunity_description,
        })

        return raw


KERNEL = FigshareMeng2019Kernel()