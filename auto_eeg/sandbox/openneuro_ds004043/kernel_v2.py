import mne

# Required description of the dataset (fields can be updated per‑subject)
eegunity_description = {
    "age": "N/A",
    "sex": "N/A",
    "amplifier": "N/A",
    "cap": "N/A",
    "handedness": "N/A"
}

class Kernel:
    """
    EEGUnity processing kernel for the OpenNeuro dataset ds004043.

    Parameters
    ----------
    udataset : object
        Placeholder for the dataset loader (not used directly here).
    raw : mne.io.BaseRaw
        The raw EEG data to be processed.
    row : dict or pandas.Series
        Subject metadata (age, sex, handedness, amplifier, cap).

    Returns
    -------
    mne.io.BaseRaw
        The processed raw data.
    """

    def __init__(self):
        # Local copy that can be enriched with per‑subject information
        self.description = eegunity_description.copy()

    @property
    def eegunity_description(self):
        return self.description

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # ------------------------------------------------------------------
        # 1) Update description from subject metadata (if provided)
        # ------------------------------------------------------------------
        if row is not None:
            for key in ("age", "sex", "handedness", "amplifier", "cap"):
                value = None
                if isinstance(row, dict):
                    value = row.get(key) or row.get(key.capitalize())
                else:
                    value = getattr(row, key, None)
                if value is not None:
                    self.description[key] = str(value)

        # ------------------------------------------------------------------
        # 2) Rename BioSemi‑style auxiliary channels (e.g., "A1") to a generic
        #    EEG label if desired. This step is optional and can be adjusted.
        # ------------------------------------------------------------------
        ch_names = raw.info["ch_names"]
        rename_map = {}
        for name in ch_names:
            # Example: BioSemi uses 'A' prefix for auxiliary channels
            if name.startswith("A"):
                rename_map[name] = "EEG_" + name
        if rename_map:
            raw.rename_channels(rename_map)

        # ------------------------------------------------------------------
        # 3) Set channel types for known non‑EEG channels (EOG, ECG, EMG, …)
        # ------------------------------------------------------------------
        for ch in raw.info["ch_names"]:
            if "EOG" in ch:
                raw.set_channel_types({ch: "eog"})
            elif "ECG" in ch:
                raw.set_channel_types({ch: "ecg"})
            elif "EMG" in ch:
                raw.set_channel_types({ch: "emg"})

        # ------------------------------------------------------------------
        # 4) Attach a standard 10‑20 montage only when no 3‑D positions are
        #    present (fallback). Adjust as needed for the actual dataset.
        # ------------------------------------------------------------------
        # Check whether any channel has non‑zero location data
        has_locs = any(ch["loc"][:3] != (0.0, 0.0, 0.0) for ch in raw.info["chs"])
        if not has_locs:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, raise_errors=False)
            except Exception:
                # If montage setting fails, continue without it
                pass

        # ------------------------------------------------------------------
        # 5) Ensure a measurement date is present (MNE can handle None)
        # ------------------------------------------------------------------
        if raw.info["meas_date"] is None:
            raw.set_meas_date(None)

        # ------------------------------------------------------------------
        # 6) Return the processed raw object
        # ------------------------------------------------------------------
        return raw

KERNEL = Kernel()