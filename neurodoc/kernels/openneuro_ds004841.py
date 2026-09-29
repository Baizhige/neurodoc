"""OpenNeuro DS004841 stage1 kernel for EEGUnity.

Semi-autonomous vehicle monitoring paradigm.
7-digit hierarchical operational state codes.
11 subjects, 70 channels, 256 Hz.

Source: https://doi.org/10.18112/openneuro.ds004841.v1.0.1
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import mne


# =============================================================================
# Event Code Mapping (7-digit hierarchical operational state codes)
# =============================================================================
# Source: Dataset README and analysis.md
# Primary operational states (for classification tasks)
_EVENT_MAP: Dict[int, str] = {
    2210001: "state_2210001",   # Operational state 1
    2210002: "state_2210002",   # Operational state 2
    2110000: "state_2110000",   # Operational state 3
    4310000: "state_4310000",   # Operational state 4
    4100001: "state_4100001",   # Operational state 5
    4320000: "state_4320000",   # Operational state 6
    4300010: "substate_4300010",  # Sub-state pattern
    4300020: "substate_4300020",  # Sub-state pattern
    4300100: "substate_4300100",  # Sub-state pattern
    1110002: "state_1110002",   # Additional state
    1110001: "state_1110001",   # Additional state
}

# Label mapping for classification tasks (y values)
_LABEL_MAP: Dict[str, int] = {
    "state_2210001": 0,
    "state_2210002": 1,
    "state_2110000": 2,
    "state_4310000": 3,
    "state_4100001": 4,
    "state_4320000": 5,
}


def _extract_subject_id(row) -> str:
    """Extract subject ID from row."""
    file_path = row.get("File Path", "")
    # Try to extract from path like sub-01/eeg/...
    match = re.search(r"sub-(\d+)", file_path)
    if match:
        return f"sub-{match.group(1)}"
    return "unknown"


def _parse_event_code(value: Any) -> Optional[int]:
    """Parse event code from various formats."""
    if isinstance(value, (int, float)):
        val = int(value)
        if 1000000 <= val <= 9999999:
            return val
    if isinstance(value, str):
        try:
            val = int(float(value))
            if 1000000 <= val <= 9999999:
                return val
        except (ValueError, TypeError):
            pass
    return None


def _detect_and_rename_channels(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """Detect non-standard channel names and rename if needed.
    
    This dataset uses standard 1020 electrode names but may have
    prefixes or non-standard numbering. Common patterns from OpenNeuro
    EEG datasets include:
    - EEG prefix (e.g., "EEG Fz" -> "Fz")
    - Numbers instead of standard names
    - Special characters in names
    
    Source: Observation based on 70-channel semi-autonomous vehicle paradigm.
    """
    rename_map: Dict[str, str] = {}
    existing_names = raw.ch_names
    
    # Standard 10-20 channel list for 70-channel system
    standard_channels = [
        "Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P7", "P3", "Pz", "P4", "P8",
        "O1", "Oz", "O2",
        "F1", "F2", "F4", "F6", "F8",
        "C1", "C2", "C6",
        "P1", "P2", "P4", "P6", "P8",
        "PO3", "PO4", "POz",
        "FC1", "FC2", "FC3", "FC4", "FC5", "FC6",
        "CP1", "CP2", "CP3", "CP4", "CP5", "CP6",
        "FT7", "FT8", "TP7", "TP8",
        "AF1", "AF2", "AF3", "AF4", "AF7", "AF8",
    ]
    
    standard_set = set(standard_channels)
    
    for ch_name in existing_names:
        # Skip non-EEG channels
        if ch_name.upper() in ["EOG", "ECG", "EMG", "REF", "GND"]:
            continue
        
        # Remove "EEG " prefix
        if ch_name.startswith("EEG "):
            clean_name = ch_name[4:].strip()
            if clean_name != ch_name:
                rename_map[ch_name] = clean_name
        
        # Handle numbered channels like "1", "2", etc. or "EEG001" 
        if ch_name.startswith("EEG"):
            # Try to extract standard name from numbered format
            suffix = re.sub(r'^EEG\s*', '', ch_name)
            if suffix.isdigit():
                # These need manual mapping based on actual dataset
                # For now, leave as-is and set montage to detect
                pass
    
    # Apply renames if any found
    if rename_map:
        mne.rename_channels(raw.info, rename_map)
    
    # Try to set montage (standard 1020)
    try:
        raw.set_montage("standard_1020", on_missing="warn")
    except Exception:
        pass  # Montage may not be available for all channels
    
    return raw


@dataclass
class OpenNeuroDS004841Kernel:
    """Stage1 kernel for OpenNeuro DS004841 dataset.
    
    Semi-autonomous vehicle monitoring with 7-digit hierarchical
    operational state codes. 11 subjects, 70 channels, 256 Hz.
    """

    KERNEL_ID: str = "openneuro-ds004841-stage1"
    
    # Subject metadata (from dataset documentation)
    # Source: Dataset README and publications (DOI: 10.1007/s12559-023-10179-8)
    # Age range: 22-45 (inferred by LLM, needs human review)
    # Sex distribution: mixed (inferred by LLM, needs human review)
    _subject_dict: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        f"sub-{i:02d}": {
            "age": "unknown",      # inferred by LLM, needs human review
            "sex": "unknown",      # inferred by LLM, needs human review
            "handedness": "unknown",  # inferred by LLM, needs human review
        }
        for i in range(1, 12)  # 11 subjects
    })

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        """Apply stage1 preprocessing to a single record.

        Parameters
        ----------
        udataset
            EEGUnity dataset context.
        raw
            In-memory MNE Raw object.
        row
            Locator row with File Path information.

        Returns
        -------
        mne.io.BaseRaw
            Preprocessed raw object with metadata and annotations.
        """
        # Step 1: Rename channels if needed
        raw = _detect_and_rename_channels(raw)
        
        # Step 2: Extract subject info
        subject_id = _extract_subject_id(row)
        subject_meta = self._subject_dict.get(subject_id, {
            "age": "unknown",
            "sex": "unknown",
            "handedness": "unknown",
        })
        
        # Step 3: Process events from annotations or stim channel
        self._process_events(raw)
        
        # Step 4: Write eegunity_description
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": subject_meta["age"],
                "sex": subject_meta["sex"],
                "amplifier": "unknown",      # inferred by LLM, needs human review
                "cap": "unknown",            # inferred by LLM, needs human review
                "handedness": subject_meta["handedness"],
            },
        }
        raw.info["description"] = json.dumps(description_dict)
        
        return raw
    
    def _process_events(self, raw: mne.io.BaseRaw) -> None:
        """Process events from raw annotations or stim channel.
        
        This dataset contains 7-digit hierarchical codes representing
        operational states in a semi-autonomous vehicle monitoring task.
        """
        annotations = raw.annotations
        
        if len(annotations) == 0:
            return
        
        # Build new annotation list with mapped descriptions
        new_descriptions = []
        new_onsets = []
        new_durations = []
        
        for i, desc in enumerate(annotations.description):
            # Try to parse as event code
            event_code = _parse_event_code(desc)
            
            if event_code is not None and event_code in _EVENT_MAP:
                new_descriptions.append(_EVENT_MAP[event_code])
                new_onsets.append(annotations.onset[i])
                new_durations.append(annotations.duration[i])
            elif isinstance(desc, str) and desc.startswith("state_"):
                # Already formatted
                new_descriptions.append(desc)
                new_onsets.append(annotations.onset[i])
                new_durations.append(annotations.duration[i])
            else:
                # Keep original for unrecognized events
                new_descriptions.append(str(desc))
                new_onsets.append(annotations.onset[i])
                new_durations.append(annotations.duration[i])
        
        # Set new annotations if we processed events
        if new_descriptions:
            new_annotations = mne.Annotations(
                onset=new_onsets,
                duration=new_durations,
                description=new_descriptions,
            )
            raw.set_annotations(new_annotations)


KERNEL = OpenNeuroDS004841Kernel()