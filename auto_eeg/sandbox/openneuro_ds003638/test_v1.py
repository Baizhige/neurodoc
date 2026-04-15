import sys; sys.path.insert(0, "/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script")
import sys
import importlib.util
import traceback

kernel_path = "/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/auto_eeg/sandbox/openneuro_ds003638/kernel_v1.py"
spec = importlib.util.spec_from_file_location("_test_kernel", kernel_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["_test_kernel"] = mod  # required for @dataclass and similar decorators
spec.loader.exec_module(mod)

kernel = mod.KERNEL
print(f"[TEST] Kernel loaded: {kernel.KERNEL_ID}")

sample_files = ["/home/public/eeg_dataset/openneuro_raw/ds003638/code/chanlocs_BS64.mat", "/home/public/eeg_dataset/openneuro_raw/ds003638/code/Mouse/LEC4/5CCPT/1.5s-3s Rand/LEC4_4.0_FvS_D5_04042018_2.mat", "/home/public/eeg_dataset/openneuro_raw/ds003638/code/Mouse/LEC4/PRBP/LEC4_3.1_PR_04112018.mat", "/home/public/eeg_dataset/openneuro_raw/ds003638/code/Mouse/LEC3/PSD/3 Pair/LEC45.1_PSD3p20e_06-05-18.mat", "/home/public/eeg_dataset/openneuro_raw/ds003638/code/Mouse/LEC4/PSD/LEC4_4.1_PSD_D7_05282018.mat"]

import mne
mne.set_log_level("WARNING")

errors = []
_EXT_READERS = {
    ".edf": lambda f: mne.io.read_raw_edf(f, preload=False, verbose=False),
    ".bdf": lambda f: mne.io.read_raw_bdf(f, preload=False, verbose=False),
    ".gdf": lambda f: mne.io.read_raw_gdf(f, preload=False, verbose=False),
    ".set": lambda f: mne.io.read_raw_eeglab(f, preload=False, verbose=False),
    ".fif": lambda f: mne.io.read_raw_fif(f, preload=False, allow_maxshield=True, verbose=False),
    ".eeg": lambda f: mne.io.read_raw_brainvision(f, preload=False, verbose=False),
}

for fpath in sample_files:
    print(f"[TEST] Testing: {fpath}")
    try:
        import pandas as pd
        row = pd.Series({"File Path": fpath})
        ext = fpath[fpath.rfind("."):].lower()
        reader = _EXT_READERS.get(ext)
        if reader is None:
            print(f"  [SKIP] Unsupported extension: {ext}")
            continue
        try:
            raw = reader(fpath)
        except Exception as load_err:
            print(f"  [SKIP] Cannot load {fpath}: {load_err}")
            continue

        result = kernel.apply(None, raw, row)
        import json as _json
        desc = result.info.get("description", "")
        try:
            parsed = _json.loads(desc)
        except Exception:
            parsed = {}
        eegu = parsed.get("eegunity_description", {})
        required = {"age", "sex", "amplifier", "cap", "handedness"}
        missing = required - set(eegu.keys())
        if missing:
            errors.append(f"{fpath}: eegunity_description missing fields: {missing}")
        else:
            print(f"  [OK] age={eegu['age']!r} sex={eegu['sex']!r} channels={len(result.ch_names)}")
    except Exception as e:
        errors.append(f"{fpath}: {traceback.format_exc()}")

if errors:
    print("\n[FAIL] Errors:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"\n[PASS] All {len(sample_files)} test file(s) passed.")
    sys.exit(0)
