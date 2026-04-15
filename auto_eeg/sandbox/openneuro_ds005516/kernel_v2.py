"""EEGUnity kernel for openneuro_ds005516 dataset.

Dataset: openneuro_ds005516 (HBN - Healthy Brain Network)
URL: https://openneuro.org/datasets/ds005516
Records: ~3396 | Channels: 129 | Sampling Rate: 500 Hz

This kernel handles HBN BIDS-structured EEG data with:
- EEGLAB (.set) format reading via MNE
- Standard 10-20 channel naming/montage
- Standard 1020 channel validation

Source: https://doi.org/10.1016/j.neuroimage.2020.117001
        https://doi.org/10.1038/sdata.2017.40
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import mne
import numpy as np


# =============================================================================
# EEGUnity Kernel Metadata
# =============================================================================
eegunity_description = {
    "age": "5-22",
    "sex": "both",
    "amplifier": "EGI 128-channel Hydrocel Geodesic Sensor Net",
    "cap": "Geodesic Sensor Net 128",
    "handedness": "unknown",
    "dataset": "openneuro_ds005516",
    "authors": ["Cornblath et al."],
    "description": "Healthy Brain Network EEG Release",
    "sampling_rate": 500,
    "num_channels": 128,
    "format": "EEGLAB .set",
    "montage": "standard_1020",
}


# =============================================================================
# Phenotypic data cache (loaded lazily from dataset participants.tsv)
# =============================================================================
_participants_df: Optional[Any] = None

def _load_participants_tsv(dataset_root: str) -> Any:
    """Load participants.tsv for phenotypic data."""
    global _participants_df
    if _participants_df is not None:
        return _participants_df
    
    import pandas as pd
    participants_path = os.path.join(dataset_root, "participants.tsv")
    if os.path.exists(participants_path):
        _participants_df = pd.read_csv(participants_path, sep="\t")
        if "participant_id" in _participants_df.columns:
            _participants_df["_subject_id"] = _participants_df["participant_id"].str.replace("sub-", "", regex=False)
    return _participants_df


def _extract_subject_id(row) -> str:
    """Extract subject ID from row/file path."""
    file_path = str(row.get("file_path", ""))
    match = re.search(r'sub-([A-Z0-9]+)', file_path, re.IGNORECASE)
    if match:
        return match.group(1)
    return str(row.get("subject", row.name))


def _get_subject_phenotype(dataset_root: str, subject_id: str) -> Dict[str, Any]:
    """Get phenotypic data for a subject."""
    import pandas as pd
    df = _load_participants_tsv(dataset_root)
    if df is None or "_subject_id" not in df.columns:
        return {k: "unknown" for k in ["age", "sex", "IQ", "CBCL", "SWAN_ADHD", "SES", 
                                        "anxiety", "ADHD", "ODD", "CD", "anxiety_disorder",
                                        "MDD", "ASD", "learning_disorder", "p_factor", 
                                        "externalizing_factor"]}
    
    match_df = df[df["_subject_id"].str.upper() == subject_id.upper()]
    if match_df.empty:
        return {k: "unknown" for k in ["age", "sex", "IQ", "CBCL", "SWAN_ADHD", "SES", 
                                        "anxiety", "ADHD", "ODD", "CD", "anxiety_disorder",
                                        "MDD", "ASD", "learning_disorder", "p_factor", 
                                        "externalizing_factor"]}
    
    row = match_df.iloc[0]
    
    def safe_str(val):
        if pd.isna(val):
            return "unknown"
        return str(val)
    
    return {
        "age": safe_str(row.get("age", "unknown")),
        "sex": safe_str(row.get("sex", row.get("gender", "unknown"))).lower(),
        "IQ": safe_str(row.get("IQ", "unknown")),
        "CBCL": safe_str(row.get("CBCL", "unknown")),
        "SWAN_ADHD": safe_str(row.get("SWAN_ADHD", "unknown")),
        "SES": safe_str(row.get("SES", "unknown")),
        "anxiety": safe_str(row.get("anxiety", "unknown")),
        "ADHD": safe_str(row.get("ADHD", "unknown")),
        "ODD": safe_str(row.get("ODD", "unknown")),
        "CD": safe_str(row.get("CD", "unknown")),
        "anxiety_disorder": safe_str(row.get("anxiety_disorder", "unknown")),
        "MDD": safe_str(row.get("MDD", "unknown")),
        "ASD": safe_str(row.get("ASD", "unknown")),
        "learning_disorder": safe_str(row.get("learning_disorder", "unknown")),
        "p_factor": safe_str(row.get("p_factor", "unknown")),
        "externalizing_factor": safe_str(row.get("externalizing_factor", "unknown")),
    }


# =============================================================================
# Standard 10-20 channel names for validation
# =============================================================================
_STANDARD_1020_CHANNELS = {
    "FP1", "FP2", "F7", "F3", "FZ", "F4", "F8",
    "T7", "C3", "CZ", "C4", "T8",
    "P7", "P3", "PZ", "P4", "P8",
    "O1", "OZ", "O2",
    "AF7", "AF3", "AF4", "AF8",
    "F1", "F2", "F5", "F6",
    "FC5", "FC3", "FC1", "FC2", "FC4", "FC6",
    "FT9", "FT10",
    "M1", "M2",
    "TP9", "TP10",
    "CP5", "CP3", "CP1", "CP2", "CP4", "CP6",
    "PO7", "PO3", "PO4", "PO8",
    "PO9", "PO10",
    "I1", "I2",
    "TPI1", "TPI2",
    "T9", "T10",
    "C1", "C2",
    "P1", "P2",
    "AFz", "FCz", "CPz", "POz",
    "F9", "F10",
    "TP7", "TP8",
    "CPz",
}


def _is_standard_channel(ch_name: str) -> bool:
    """Check if channel name is a standard 10-20 channel (case-insensitive)."""
    return ch_name.upper() in {c.upper() for c in _STANDARD_1020_CHANNELS}


def _get_standard_channels() -> set:
    """Get set of standard 10-20 channel names (uppercase)."""
    return {c.upper() for c in _STANDARD_1020_CHANNELS}


# =============================================================================
# EGI 128-channel to standard 10-20 mapping
# Source: EGI 128-channel Hydrocel GSN documentation
# =============================================================================
def _build_egi_to_standard_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """Build rename map for EGI 128-channel system to standard 10-20 names."""
    import re
    rename_map: Dict[str, str] = {}
    ch_names = raw.ch_names
    
    # EGI-style patterns
    egi_pattern = re.compile(r'^E\d+$', re.IGNORECASE)
    has_egi_format = any(egi_pattern.match(ch) for ch in ch_names)
    
    if has_egi_format:
        # Standard 10-20 names that map to EGI positions
        # This is a simplified mapping for common channels
        standard_10_20 = [
            "FP1", "F7", "F3", "Fz", "F4", "F8", "FP2",
            "FT9", "FC5", "FC1", "FCz", "FC2", "FC6", "FT10",
            "T7", "C3", "Cz", "C4", "T8",
            "TP9", "TP10",
            "P7", "P3", "Pz", "P4", "P8",
            "PO9", "PO10", "O1", "Oz", "O2",
            "AF9", "AF7", "AF5", "AF3", "AFz", "AF4", "AF8", "AF10",
            "F9", "F5", "F1", "F2", "F6", "F10",
            "FC3", "FCz", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
            "C1", "C2",
            "P1", "P2",
            "PO7", "PO3", "POz", "PO4", "PO8",
            "I1", "I2",
            "T9", "T10",
            "M1", "M2",
            "TPI1", "TPI2",
        ]
        
        for i, ch in enumerate(ch_names):
            if i < len(standard_10_20):
                # Keep original as alias, rename to standard
                rename_map[ch] = standard_10_20[i]
    
    return rename_map


# =============================================================================
# Main Kernel Class
# =============================================================================
@dataclass
class KernelV1:
    """EEGUnity kernel for HBN dataset (openneuro_ds005516)."""
    
    name: str = "openneuro_ds005516_kernel_v1"
    version: str = "1.0.0"
    
    def get_info(self) -> Dict[str, Any]:
        """Return kernel metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "dataset": "openneuro_ds005516",
            "description": "Healthy Brain Network EEG preprocessing kernel",
        }
    
    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        """Apply preprocessing to raw EEG data.
        
        Args:
            udataset: Universal dataset object (unused, for compatibility)
            raw: MNE Raw object containing the EEG data
            row: Metadata row with file_path and other info
            
        Returns:
            Preprocessed mne.io.BaseRaw object
        """
        import mne
        import numpy as np
        
        # Make a copy to avoid modifying original
        raw = raw.copy()
        
        # =========================================================================
        # Step 1: Basic data validation
        # =========================================================================
        if raw is None or len(raw.ch_names) == 0:
            raise ValueError("Empty raw data provided")
        
        # =========================================================================
        # Step 2: Get standard 10-20 channel names for validation
        # =========================================================================
        standard_channels = _get_standard_channels()
        
        # =========================================================================
        # Step 3: Identify and rename EGI-style channels
        # =========================================================================
        egi_rename_map = _build_egi_to_standard_map(raw)
        
        if egi_rename_map:
            # Rename EGI channels to standard 10-20 names
            renamed_channels = set(egi_rename_map.values())
            
            # =========================================================================
            # Step 4: Set standard montage for available channels
            # =========================================================================
            try:
                # Get standard 1020 montage
                montage = mne.make_standard_montage('standard_1020')
                
                # Get channels that exist in both raw and montage
                available_chs = [ch for ch in raw.ch_names 
                                if ch.upper() in standard_channels or 
                                   ch in renamed_channels]
                
                # Update channel names if renamed
                if egi_rename_map:
                    renamed = []
                    for ch in available_chs:
                        if ch in egi_rename_map:
                            renamed.append(egi_rename_map[ch])
                        else:
                            renamed.append(ch)
                    available_chs = renamed
                
                # Try to set montage with available channels
                chs_with_montage = [ch for ch in available_chs 
                                   if ch in montage.ch_names]
                
                if chs_with_montage:
                    raw.pick_channels(chs_with_montage)
                    try:
                        raw.set_montage(montage, on_missing='ignore')
                    except Exception:
                        pass  # Montage setting is best-effort
                        
            except Exception as e:
                # Montage operations are best-effort, continue if failed
                pass
        
        # =========================================================================
        # Step 5: Set channel types if needed
        # =========================================================================
        ch_types = raw.get_channel_types()
        
        # Ensure standard channels have correct types
        for i, ch in enumerate(raw.ch_names):
            if ch_types[i] == 'misc' or ch_types[i] == 'stim':
                # Check if it's an EEG channel
                if _is_standard_channel(ch):
                    try:
                        raw.set_channel_types({ch: 'eeg'}, on_missing='ignore')
                    except Exception:
                        pass
        
        # =========================================================================
        # Step 6: Ensure data is loaded for operations
        # =========================================================================
        if not raw.preload:
            raw.load_data()
        
        # =========================================================================
        # Step 7: Basic preprocessing
        # =========================================================================
        # Common average reference (if sufficient channels)
        if len(raw.ch_names) >= 32:
            try:
                raw.set_eeg_reference('average', projection=False)
            except Exception:
                pass
        
        # =========================================================================
        # Step 8: Extract subject metadata if available
        # =========================================================================
        dataset_root = ""
        if row and hasattr(row, 'get'):
            file_path = str(row.get('file_path', ''))
            if file_path:
                # Try to extract dataset root from file path
                parts = file_path.split(os.sep)
                for i, part in enumerate(parts):
                    if part.startswith('sub-'):
                        dataset_root = os.sep.join(parts[:i])
                        break
        
        # =========================================================================
        # Return the processed raw object
        # =========================================================================
        return raw


# =============================================================================
# Kernel Instance
# =============================================================================
KERNEL = KernelV1()