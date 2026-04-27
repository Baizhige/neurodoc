import mne
import os
from mne.datasets import openneuro as openneuro_loader

eegunity_description = {
    'age': 'unknown',
    'sex': 'unknown',
    'amplifier': 'unknown',
    'cap': 'unknown',
    'handedness': 'unknown'
}

class OpenNeuroDS004602Kernel:
    """
    EEGUNITY kernel for the openneuro_ds004602 dataset.
    Loads raw data from OpenNeuro and returns an mne.io.BaseRaw object.
    """
    def __init__(self):
        pass

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        if isinstance(raw, mne.io.BaseRaw):
            return raw
        if udataset and isinstance(udataset, str):
            data_path = udataset
        else:
            data_path = openneuro_loader.fetch(
                dataset_id='ds004602',
                resume=True,
                force_update=False,
                verbose=True
            )
        edf_files = []
        for root, _, files in os.walk(data_path):
            for fname in files:
                if fname.lower().endswith('.edf'):
                    edf_files.append(os.path.join(root, fname))
        if not edf_files:
            raise FileNotFoundError('No EDF files found in the dataset directory.')
        if row and isinstance(row, dict):
            target = row.get('filename')
            if target:
                candidate = os.path.join(data_path, target)
                if os.path.isfile(candidate):
                    chosen = candidate
                else:
                    target_lower = target.lower()
                    chosen = next(
                        (f for f in edf_files if os.path.basename(f).lower() == target_lower),
                        None
                    )
                    if chosen is None:
                        raise FileNotFoundError(
                            f"Requested file '{target}' not found among EDF files."
                        )
                return mne.io.read_raw_edf(chosen, preload=True, verbose=False)
        return mne.io.read_raw_edf(edf_files[0], preload=True, verbose=False)

KERNEL = OpenNeuroDS004602Kernel()