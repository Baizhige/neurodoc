import mne
import numpy as np

class Kernel:
    """
    EEGUnity processing kernel for the OpenNeuro dataset ds004043.
    """

    KERNEL_ID = "openneuro_ds004043"
    
    eegunity_description = {
        "age": "N/A",
        "sex": "N/A",
        "amplifier": "N/A",
        "cap": "N/A",
        "handedness": "N/A"
    }

    def __init__(self):
        self.description = self.eegunity_description.copy()

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        if row is not None:
            for key in ("age", "sex", "handedness", "amplifier", "cap"):
                value = None
                if isinstance(row, dict):
                    value = row.get(key) or row.get(key.capitalize())
                else:
                    value = getattr(row, key, None)
                if value is not None:
                    self.description[key] = str(value)

        ch_names = raw.info["ch_names"]
        rename_map = {}
        for name in ch_names:
            if name.startswith("A"):
                rename_map[name] = "EEG_" + name
        if rename_map:
            raw.rename_channels(rename_map)

        for ch in raw.info["ch_names"]:
            if "EOG" in ch:
                raw.set_channel_types({ch: "eog"})
            elif "ECG" in ch:
                raw.set_channel_types({ch: "ecg"})
            elif "EMG" in ch:
                raw.set_channel_types({ch: "emg"})

        has_locs = any(not np.allclose(ch["loc"][:3], (0.0, 0.0, 0.0)) for ch in raw.info["chs"])
        if not has_locs:
            try:
                montage = mne.channels.make_standard_montage("standard_1020")
                raw.set_montage(montage, raise_errors=False)
            except Exception:
                pass

        if raw.info["meas_date"] is None:
            raw.set_meas_date(None)

        return raw

KERNEL = Kernel()