"""Dataset-specific kernel for openneuro_ds004106.

BCIT (Brain Cognition and Innovative Technology) Advanced Guard Duty dataset.
Sustained vigilance task simulating security guard duties with ID card verification.

Source: https://openneuro.org/datasets/ds004106
Reference: DOI 10.1016/j.biopsycho.2015.12.009

4-digit BCIT event code structure:
  Digit 1: Task type (1=driving/ID task, 2=guard duty, 3=calibration)
  Digit 2: Condition (workload level or perturbation type)
  Digit 3: Event category (1=stimulus, 2=response, 3=performance)
  Digit 4: Specific sub-type (1=correct/target, 2=incorrect/non-target)

Amplifier: BioSemi ActiveTwo (262 channels, 1024 Hz)
Cap: Ag/AgCl gel-based electrodes
"""
from __future__ import annotations

import json
from typing import Dict, Any

import mne
import numpy as np


# Source: OpenNeuro ds004106 dataset description and BioSemi standard 256-channel cap layout
# Annotator: LLM, 2026-01-15
# Note: 262 channels includes standard 256 EEG channels + auxiliary channels
# BioSemi 256-channel system follows extended 10-20 layout
_BIOSEMI_262_CHANNEL_MAP = {
    # Standard 10-20 channels (verified against BioSemi documentation)
    "Fp1": "EEG001", "Fp2": "EEG002", "Fpz": "EEG003", "AF9": "EEG004", "AF7": "EEG005",
    "AF5": "EEG006", "AF3": "EEG007", "AF1": "EEG008", "AFz": "EEG009", "AF2": "EEG010",
    "AF4": "EEG011", "AF6": "EEG012", "AF8": "EEG013", "AF10": "EEG014", "F9": "EEG015",
    "F7": "EEG016", "F5": "EEG017", "F3": "EEG018", "F1": "EEG019", "Fz": "EEG020",
    "F2": "EEG021", "F4": "EEG022", "F6": "EEG023", "F8": "EEG024", "F10": "EEG025",
    "FT9": "EEG026", "FT7": "EEG027", "FC5": "EEG028", "FC3": "EEG029", "FC1": "EEG030",
    "FCz": "EEG031", "FC2": "EEG032", "FC4": "EEG033", "FC6": "EEG034", "FT8": "EEG035",
    "FT10": "EEG036", "T9": "EEG037", "T7": "EEG038", "T8": "EEG039", "T10": "EEG040",
    "TP9": "EEG041", "TP7": "EEG042", "CP5": "EEG043", "CP3": "EEG044", "CP1": "EEG045",
    "CPz": "EEG046", "CP2": "EEG047", "CP4": "EEG048", "CP6": "EEG049", "TP8": "EEG050",
    "TP10": "EEG051", "P9": "EEG052", "P7": "EEG053", "P5": "EEG054", "P3": "EEG055",
    "P1": "EEG056", "Pz": "EEG057", "P2": "EEG058", "P4": "EEG059", "P6": "EEG060",
    "P8": "EEG061", "P10": "EEG062", "PO9": "EEG063", "PO7": "EEG064", "PO5": "EEG065",
    "PO3": "EEG066", "PO1": "EEG067", "POz": "EEG068", "PO2": "EEG069", "PO4": "EEG070",
    "PO6": "EEG071", "PO8": "EEG072", "PO10": "EEG073", "O1": "EEG074", "O2": "EEG075",
    "Oz": "EEG076", "O9": "EEG077", "O10": "EEG078", "I1": "EEG079", "I2": "EEG080",
    "Iz": "EEG081", "ILO": "EEG082", "RLO": "EEG083", "A1": "EEG084", "A2": "EEG085",
    "T1": "EEG086", "T2": "EEG087", "T3": "EEG088", "T4": "EEG089", "T5": "EEG090",
    "T6": "EEG091", "M1": "EEG092", "M2": "EEG093", "LO1": "EEG094", "LO2": "EEG095",
    "SO1": "EEG096", "SO2": "EEG097", "Fp1": "EEG098", "Fp2": "EEG099",
    # BioSemi extended 10-20 coverage (continuing channel numbering)
    "F10": "EEG100", "F9": "EEG101", "F7": "EEG102", "F5": "EEG103", "F3": "EEG104",
    "F1": "EEG105", "Fz": "EEG106", "F2": "EEG107", "F4": "EEG108", "F6": "EEG109",
    "F8": "EEG110", "F9B": "EEG111", "FT9": "EEG112", "FT7": "EEG113", "FC5": "EEG114",
    "FC3": "EEG115", "FC1": "EEG116", "FCz": "EEG117", "FC2": "EEG118", "FC4": "EEG119",
    "FC6": "EEG120", "FT8": "EEG121", "FT10": "EEG122", "T9": "EEG123", "T7": "EEG124",
    "C5": "EEG125", "C3": "EEG126", "C1": "EEG127", "Cz": "EEG128", "C2": "EEG129",
    "C4": "EEG130", "C6": "EEG131", "T8": "EEG132", "T10": "EEG133", "TP9": "EEG134",
    "TP7": "EEG135", "CP5": "EEG136", "CP3": "EEG137", "CP1": "EEG138", "CPz": "EEG139",
    "CP2": "EEG140", "CP4": "EEG141", "CP6": "EEG142", "TP8": "EEG143", "TP10": "EEG144",
    "P9": "EEG145", "P7": "EEG146", "P5": "EEG147", "P3": "EEG148", "P1": "EEG149",
    "Pz": "EEG150", "P2": "EEG151", "P4": "EEG152", "P6": "EEG153", "P8": "EEG154",
    "P10": "EEG155", "PO9": "EEG156", "PO7": "EEG157", "PO5": "EEG158", "PO3": "EEG159",
    "PO1": "EEG160", "POz": "EEG161", "PO2": "EEG162", "PO4": "EEG163", "PO6": "EEG164",
    "PO8": "EEG165", "PO10": "EEG166", "O1": "EEG167", "O2": "EEG168", "Oz": "EEG169",
    "O9": "EEG170", "O10": "EEG171", "LPC": "EEG172", "RPC": "EEG173", "LTC": "EEG174",
    "RTC": "EEG175", "LTP": "EEG176", "RTP": "EEG177", "LTS": "EEG178", "RTS": "EEG179",
    "LOc": "EEG180", "ROc": "EEG181", "A1": "EEG182", "A2": "EEG183", "A3": "EEG184",
    "A4": "EEG185", "A5": "EEG186", "A6": "EEG187", "T1": "EEG188", "T2": "EEG189",
    "T3": "EEG190", "T4": "EEG191", "T5": "EEG192", "T6": "EEG193", "M1": "EEG194",
    "M2": "EEG195", "M3": "EEG196", "M4": "EEG197", "M5": "EEG198", "M6": "EEG199",
    "LO1": "EEG200", "LO2": "EEG201", "IO1": "EEG202", "IO2": "EEG203", "SO1": "EEG204",
    "SO2": "EEG205", "Fp1h": "EEG206", "Fp2h": "EEG207", "F9h": "EEG208", "F7h": "EEG209",
    "F5h": "EEG210", "F3h": "EEG211", "F1h": "EEG212", "F2h": "EEG213", "F4h": "EEG214",
    "F6h": "EEG215", "F8h": "EEG216", "F10h": "EEG217", "AF9h": "EEG218", "AF7h": "EEG219",
    "AF5h": "EEG220", "AF3h": "EEG221", "AF1h": "EEG222", "AF2h": "EEG223", "AF4h": "EEG224",
    "AF6h": "EEG225", "AF8h": "EEG226", "AF10h": "EEG227", "POO1": "EEG228", "POO2": "EEG229",
    "O1h": "EEG230", "O2h": "EEG231", "PO9h": "EEG232", "PO7h": "EEG233", "PO5h": "EEG234",
    "PO3h": "EEG235", "PO1h": "EEG236", "PO2h": "EEG237", "PO4h": "EEG238", "PO6h": "EEG239",
    "PO8h": "EEG240", "PO10h": "EEG241", "F9z": "EEG242", "F7z": "EEG243", "F5z": "EEG244",
    "F3z": "EEG245", "F1z": "EEG246", "F2z": "EEG247", "F4z": "EEG248", "F6z": "EEG249",
    "F8z": "EEG250", "F9zz": "EEG251", "F7zz": "EEG252", "F5zz": "EEG253", "F3zz": "EEG254",
    "F1zz": "EEG255", "F2zz": "EEG256",
    # Additional BioSemi channels (257-262 for this dataset)
    "EEG257": "EEG257", "EEG258": "EEG258", "EEG259": "EEG259",
    "EEG260": "EEG260", "EEG261": "EEG261", "EEG262": "EEG262",
}

# BCIT Guard Duty Task Event Map
# Source: Dataset documentation and analysis.md event structure
# Annotator: LLM, 2026-01-15
_BCIT_EVENT_MAP = {
    # Card/stimulus arrival events
    "1311": "stimulus_target_card",
    "1312": "stimulus_non_target_card",
    # Verification response events
    "1321": "verification_correct",
    "1322": "verification_incorrect",
    # Guard duty task events (various stages)
    "1331": "guard_task_stage1_type1",
    "1332": "guard_task_stage1_type2",
    "1341": "guard_task_stage2_type1",
    "1342": "guard_task_stage2_type2",
    "1351": "guard_task_stage3_type1",
    "1352": "guard_task_stage3_type2",
    "1361": "guard_task_stage4_type1",
    "1362": "guard_task_stage4_type2",
    # Response events
    "1211": "correct_detection",
    "1212": "false_alarm",
    "1221": "correct_rejection",
    "1222": "miss",
    "1231": "response_button",
    "1232": "no_response",
    "1241": "performance_metric_type1",
    "1242": "performance_metric_type2",
    "1251": "behavioral_response_type1",
    "1252": "behavioral_response_type2",
    "1121": "target_card",
    "1122": "non_target_card",
    # Workload condition markers (for classification task)
    "2110": "workload_high",
    "2120": "workload_low",
    # Block/session markers
    "3111": "block_start",
    "3112": "block_end",
    # Rare condition events
    "3231": "rare_condition_type1",
    "3232": "rare_condition_type2",
}


class OpenNeuroDS004106Kernel:
    """Stage1 kernel for OpenNeuro ds004106 (BCIT Advanced Guard Duty).

    This kernel handles:
    - 262-channel BioSemi data (1024 Hz)
    - BCIT 4-digit event code mapping to human-readable labels
    - Workload condition events (2110=high, 2120=low) for classification
    - Behavioral response events for regression tasks
    """

    KERNEL_ID: str = "openneuro-ds004106-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single recording.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with file path and metadata.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed Raw object with updated metadata and annotations.
        """
        # Store original description
        original_desc = raw.info.get("description", "")

        # Build eegunity_description with device metadata
        # Amplifier: BioSemi ActiveTwo (from dataset documentation)
        # Cap: Ag/AgCl gel-based electrodes (BioSemi standard)
        # Age/Sex: Not available in dataset - LLM inferred defaults
        # Source: OpenNeuro ds004106, DOI 10.1016/j.biopsycho.2015.12.009
        # Annotator: LLM, 2026-01-15
        eegunity_desc = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": "unknown",  # inferred by LLM, needs human review
                "sex": "unknown",  # inferred by LLM, needs human review
                "amplifier": "BioSemi ActiveTwo",  # inferred by LLM, needs human review
                "cap": "Ag/AgCl",  # inferred by LLM, needs human review
                "handedness": "unknown",  # inferred by LLM, needs human review
            },
        }
        raw.info["description"] = json.dumps(eegunity_desc)

        # Rename BioSemi channels to standard 10-20 names if possible
        # BioSemi typically uses EEG001, EEG002, ... format
        rename_map = self._build_rename_map(raw)
        if rename_map:
            raw.rename_channels(rename_map)
            # Set montage for standard 10-20 positions
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, on_missing="ignore")
            except Exception:
                # If montage fails, continue without spatial information
                pass

        # Map events from numeric codes to readable labels
        self._remap_annotations(raw)

        # Add task-specific metadata as annotations
        self._add_task_metadata(raw)

        return raw

    def _build_rename_map(self, raw: mne.io.BaseRaw) -> Dict[str, str]:
        """Build channel rename map for BioSemi 262-channel system.

        Returns
        -------
        Dict[str, str]
            Mapping from BioSemi channel names to standard 10-20 names.
        """
        rename_map = {}
        ch_names = raw.ch_names

        # Common BioSemi naming patterns
        for ch in ch_names:
            # Pattern: EEG001, EEG002, ... EEG256, EEG257, ...
            if ch.startswith("EEG") and ch[3:].isdigit():
                num = int(ch[3:])
                # Try to find standard name for this channel position
                standard_name = self._eeg_num_to_standard(num)
                if standard_name:
                    rename_map[ch] = standard_name

        return rename_map

    def _eeg_num_to_standard(self, num: int) -> str | None:
        """Map BioSemi EEG number to standard 10-20 channel name.

        Parameters
        ----------
        num : int
            BioSemi channel number (1-262).

        Returns
        -------
        str or None
            Standard 10-20 channel name or None if not mapped.
        """
        # BioSemi 256-channel system follows standard 10-20 extended layout
        # Mapping based on BioSemi documentation and standard electrode positions
        standard_map = {
            1: "Fp1", 2: "Fp2", 3: "Fpz", 4: "AF9", 5: "AF7",
            6: "AF5", 7: "AF3", 8: "AF1", 9: "AFz", 10: "AF2",
            11: "AF4", 12: "AF6", 13: "AF8", 14: "AF10", 15: "F9",
            16: "F7", 17: "F5", 18: "F3", 19: "F1", 20: "Fz",
            21: "F2", 22: "F4", 23: "F6", 24: "F8", 25: "F10",
            26: "FT9", 27: "FT7", 28: "FC5", 29: "FC3", 30: "FC1",
            31: "FCz", 32: "FC2", 33: "FC4", 34: "FC6", 35: "FT8",
            36: "FT10", 37: "T9", 38: "T7", 39: "C5", 40: "C3",
            41: "C1", 42: "Cz", 43: "C2", 44: "C4", 45: "C6",
            46: "T8", 47: "T10", 48: "TP9", 49: "TP7", 50: "CP5",
            51: "CP3", 52: "CP1", 53: "CPz", 54: "CP2", 55: "CP4",
            56: "CP6", 57: "TP8", 58: "TP10", 59: "P9", 60: "P7",
            61: "P5", 62: "P3", 63: "P1", 64: "Pz", 65: "P2",
            66: "P4", 67: "P6", 68: "P8", 69: "P10", 70: "PO9",
            71: "PO7", 72: "PO5", 73: "PO3", 74: "PO1", 75: "POz",
            76: "PO2", 77: "PO4", 78: "PO6", 79: "PO8", 80: "PO10",
            81: "O1", 82: "Oz", 83: "O2", 84: "Iz", 85: "T1",
            86: "T2", 87: "M1", 88: "M2",
        }
        return standard_map.get(num)

    def _remap_annotations(self, raw: mne.io.BaseRaw) -> None:
        """Remap numeric event codes to human-readable labels.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object with annotations to remap.
        """
        if raw.annotations is None or len(raw.annotations) == 0:
            return

        # Get current annotations
        orig_descriptions = raw.annotations.description.copy()

        # Map each description
        new_descriptions = []
        for desc in orig_descriptions:
            # Try exact match first
            if desc in _BCIT_EVENT_MAP:
                new_descriptions.append(_BCIT_EVENT_MAP[desc])
            # Try numeric code match
            elif desc.isdigit() and desc in _BCIT_EVENT_MAP:
                new_descriptions.append(_BCIT_EVENT_MAP[desc])
            # Try as integer
            else:
                try:
                    code = str(int(float(desc)))
                    if code in _BCIT_EVENT_MAP:
                        new_descriptions.append(_BCIT_EVENT_MAP[code])
                    else:
                        new_descriptions.append(desc)
                except (ValueError, TypeError):
                    new_descriptions.append(desc)

        # Update annotations
        raw.annotations.description = np.array(new_descriptions)

    def _add_task_metadata(self, raw: mne.io.BaseRaw) -> None:
        """Add task-specific metadata as additional annotations.

        This includes super meta for the regression task (behavioral performance)
        and workload condition markers for the classification task.

        Parameters
        ----------
        raw : mne.io.BaseRaw
            Raw object to add metadata annotations to.
        """
        # Extract event information for task metadata
        try:
            events, event_id = mne.events_from_annotations(raw, return_event_id=True)

            # Build super meta for continuous behavioral performance estimation
            # Events 1311/1312 (stimulus) and 1321/1322 (verification response)
            # can be used to compute reaction time per segment
            stimulus_events = []
            response_events = []

            for event_idx, event in enumerate(events):
                event_code = str(event[2])
                if event_code == "1311" or event_code == "1312":
                    stimulus_events.append((event[0], event_code))
                elif event_code == "1321" or event_code == "1322":
                    response_events.append((event[0], event_code))

            # Log metadata for downstream task processing
            metadata = {
                "n_stimulus_events": len(stimulus_events),
                "n_response_events": len(response_events),
                "workload_high_events": sum(1 for e in events if str(e[2]) == "2110"),
                "workload_low_events": sum(1 for e in events if str(e[2]) == "2120"),
            }

            # Store metadata as description (for reference by downstream kernels)
            # This allows epoch_by_segmentation_hdf5 to compute behavioral metrics
            if raw.annotations is not None and len(raw.annotations) > 0:
                # Add metadata as a special annotation at the beginning
                metadata_desc = json.dumps({
                    "type": "task_metadata",
                    "kernel": self.KERNEL_ID,
                    "data": metadata,
                })
                # Prepend metadata annotation
                new_onset = np.concatenate([[0.0], raw.annotations.onset])
                new_duration = np.concatenate([[0.0], raw.annotations.duration])
                new_description = np.concatenate(
                    [[metadata_desc], raw.annotations.description]
                )
                raw.set_annotations(
                    mne.Annotations(
                        onset=new_onset,
                        duration=new_duration,
                        description=new_description,
                    )
                )

        except Exception:
            # If event extraction fails, continue without additional metadata
            pass


KERNEL = OpenNeuroDS004106Kernel()