import mne
import os
from mne.datasets import openneuro as openneuro_loader

class OpenNeuroDS004602Kernel:
    """
    EEGUnity kernel for the openneuro_ds004602 dataset.
    Loads raw data from OpenNeuro and returns an mne.io.BaseRaw object.
    """
    def __init__(self):
        # Minimal EEGUnity description – replace with real metadata when known.
        self.eegunity_description = {
            'age': 'unknown',
            'sex': 'unknown',
            'amplifier': 'unknown',
            'cap': 'unknown',
            'handedness': 'unknown'
        }

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # If a raw object is already supplied, use it directly.
        if isinstance(raw, mne.io.BaseRaw):
            return raw

        # Determine the dataset location.
        if udataset and isinstance(udataset, str):
            data_path = udataset
        else:
            # Fetch the OpenNeuro dataset if no local copy is provided.
            data_path = openneuro_loader.fetch(
                dataset_id='ds004602',
                resume=True,
                force_update=False,
                verbose=True
            )

        # Locate all EDF files in the dataset directory.
        edf_files = []
        for root, _, files in os.walk(data_path):
            for fname in files:
                if fname.lower().endswith('.edf'):
                    edf_files.append(os.path.join(root, fname))

        if not edf_files:
            raise FileNotFoundError('No EDF files found in the dataset directory.')

        # If row metadata is supplied, try to load the requested file.
        if row and isinstance(row, dict):
            target = row.get('filename')
            if target:
                candidate = os.path.join(data_path, target)
                if os.path.isfile(candidate):
                    chosen = candidate
                else:
                    # Case‑insensitive fallback search.
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

        # Default: load the first EDF file encountered.
        return mne.io.read_raw_edf(edf_files[0], preload=True, verbose=False)


# Singleton instance required by EEGUnity.
KERNEL = OpenNeuroDS004602Kernel()