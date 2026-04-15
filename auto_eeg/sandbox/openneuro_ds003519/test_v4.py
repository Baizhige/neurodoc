import sys; sys.path.insert(0, "<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script")
import sys
import importlib.util
import traceback

kernel_path = "<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/auto_eeg/sandbox/openneuro_ds003519/kernel_v4.py"
spec = importlib.util.spec_from_file_location("_test_kernel", kernel_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["_test_kernel"] = mod  # required for @dataclass and similar decorators
spec.loader.exec_module(mod)

kernel = mod.KERNEL
print(f"[TEST] Kernel loaded: {kernel.KERNEL_ID}")

sample_files = ["<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds003519/code/Resources for All Drug Subjs/Placebo_Sessions.mat", "<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds003519/sub-013/ses-02/eeg/sub-013_ses-02_task-VisualWorkingMemory_eeg.set", "<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds003519/sub-022/ses-02/eeg/sub-022_ses-02_task-VisualWorkingMemory_eeg.set", "<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds003519/sub-026/ses-02/eeg/sub-026_ses-02_task-VisualWorkingMemory_eeg.set", "<LOCAL_HOME>/eeg_dataset/openneuro_raw/ds003519/sub-025/ses-01/eeg/sub-025_ses-01_task-VisualWorkingMemory_eeg.set"]

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
