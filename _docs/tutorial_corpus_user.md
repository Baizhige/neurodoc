# Corpus User Guide

This guide shows you how to browse the EEG corpus, select datasets, export data to HDF5 with EEGUnity, and feed it into a PyTorch training loop.

---

## Step 1 — Browse the Corpus

Open [`corpus_index.md`](corpus_index.md) for a full table of all 55 completed datasets, grouped by paradigm category:

| Category | Description |
|---|---|
| 🤜 Action/Output | Motor imagery, BCI, movement execution, key-press |
| 👁️ Sensory/Response | SSVEP, visual/auditory ERP, steady-state evoked potentials |
| 🧠 High-level Mental | Emotion, cognitive load, attention, memory, meditation |
| 🔀 Complex Applied | Multi-paradigm or applied BCI combining the above |
| 🩺 Biological State | Sleep staging, seizure/epilepsy, clinical monitoring |
| 📦 Others | Datasets not clearly fitting the above |

Each row in the index links directly to that dataset's `analysis.md`.

---

## Step 2 — Read a Dataset Document

Each `dataset_document/<dataset>/analysis.md` contains five sections:

```
## Paradigm            — Experimental design, subjects, equipment
## File Scan Result    — Ground-truth event structure and metadata from EEGUnity scan
## Tasks               — ML task definitions (label routes, target events, class mappings)
## Data Quality Notes  — Known issues or limitations
## Kernel Responsibilities — Kernel capability declaration
```

**Key fields to check before committing to a dataset:**

| Field | Where | What to verify |
|---|---|---|
| `Subjects` | Header | Enough data for your experiment |
| `Sampling Rate` | Header | Compatible with your model's input requirements |
| `Tasks → Target Events` | Tasks section | Event IDs that exist in the scan result |
| `Tasks → Meta Level` | Tasks section | `raw` = direct event labels; `super` = semantically derived labels |
| `Data Quality Notes` | Data Quality section | Any class imbalance, missing channels, or known artifacts |

---

## Step 3 — Select Your Datasets

You can mix and match datasets from multiple categories. A few common patterns:

**Single-paradigm benchmark** — pick all datasets under one category, e.g. all `Action/Output` datasets for a motor imagery benchmark.

**Cross-paradigm study** — pick datasets from multiple categories and use the `label_route` field to ensure a consistent data interface.

**Single-dataset exploration** — pick one dataset, inspect the `Tasks` section, and verify the event IDs match what you expect.

> [!TIP]
> The `Tasks → Task Type` field tells you whether a dataset is set up for `classification` or `regression`. The `Tasks → label_route` tells you where the label comes from: `event` (from EEG event markers), `misc` (a per-epoch numerical channel), or `info` (a per-subject attribute like age or diagnosis).

---

## Step 4 — Clone the Repository and Copy Kernels

```bash
git clone https://github.com/EEG-BenchmarkSkill/EEGBenchmarkSKILL.git
cd EEGBenchmarkSKILL
```

The kernels live in `neurodoc/kernels/`. Copy the ones you need to your project, or add the repo to your Python path:

```bash
# Option A — copy specific kernel files
cp neurodoc/kernels/bcic_iv_2a.py  /your/project/kernels/
cp neurodoc/kernels/physionet_mi.py /your/project/kernels/

# Option B — use the repo kernels in-place (add to sys.path)
export PYTHONPATH="/path/to/EEGBenchmarkSKILL:$PYTHONPATH"
```

---

## Step 5 — Install EEGUnity

```bash
pip install eegunity
# or from source:
pip install -e /path/to/eegunity
```

> [!NOTE]
> EEGUnity is the scan and export engine behind this corpus. All kernel files in `neurodoc/kernels/` are written to its `KERNEL` interface. Make sure the EEGUnity version matches the one used to generate the corpus documents (see `## File Scan Result → EEGUnity Version` in each `analysis.md`).

---

## Step 6 — Export to HDF5

EEGUnity provides two export modes. Choose based on your use case.

### 6a. Event-Based Epochs (recommended for classification)

Exports fixed-length epochs locked to EEG event markers. This is the standard format for event-related paradigms (motor imagery, ERP, SSVEP, etc.).

```python
from eegunity import UnifiedDataset

# Load dataset with its kernel
ud = UnifiedDataset(
    dataset_path="/data/bcic_iv_2a",
    domain_tag="bcic_iv_2a",
    kernel_spec="neurodoc/kernels/bcic_iv_2a.py",
)

# Export event-locked epochs to HDF5 (format v2 = PyTorch-ready flat layout)
ud.eeg_batch.epoch_by_event_hdf5(
    output_path="./hdf5_output",
    file_name_prefix="bcic_iv_2a",
    format_version="v2",
    resample_params={"sfreq": 250},        # resample to 250 Hz
    epoch_params={"tmin": -0.5, "tmax": 3.0},  # window around each event
    miss_bad_data=True,
)
# → creates ./hdf5_output/bcic_iv_2a.hdf5
```

### 6b. Fixed-Window Segmentation (recommended for continuous paradigms)

For datasets without discrete events (e.g., sleep staging, continuous mental state), segment the continuous signal into fixed-length windows.

```python
ud.eeg_batch.epoch_by_segmentation_hdf5(
    output_path="./hdf5_output",
    file_name_prefix="sleep_cassette",
    format_version="v2",
    segment_params={"segment_length": 30.0, "overlap": 0.0},  # 30-second non-overlapping windows
    resample_params={"sfreq": 100},
    miss_bad_data=True,
)
```

### 6c. Raw Continuous Export

For custom preprocessing pipelines that need the full continuous signal:

```python
ud.eeg_batch.export_h5Dataset(
    output_path="./hdf5_output",
    name="bcic_iv_2a_raw",
    miss_bad_data=True,
)
```

---

## Step 7 — Read HDF5 in PyTorch

The v2 HDF5 format produced above is a flat array layout optimised for random-access `DataLoader` usage. Use the `dataset_api` wrappers provided in this repo:

```python
from neurodoc.dataset_api.factory import build_dataset_from_task
import yaml, torch

# Load the task definition from analysis.md (or paste it directly)
# Example task dict for bcic_iv_2a motor imagery:
task = {
    "task_type": "classification",
    "label_route": "event",
    "target_events": {
        "769": {"y": 0, "label": "left hand MI"},
        "770": {"y": 1, "label": "right hand MI"},
        "771": {"y": 2, "label": "foot MI"},
        "772": {"y": 3, "label": "tongue MI"},
    },
}

dataset = build_dataset_from_task(
    task=task,
    h5_path="./hdf5_output/bcic_iv_2a.hdf5",
)

loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

for data, label, meta in loader:
    # data:  (batch, channels, time)  float32
    # label: (batch,)                 int64
    # meta:  dict of per-epoch metadata
    print(data.shape, label.shape)
    break
```

**Label route variants:**

| `label_route` | Dataset class | Label source |
|---|---|---|
| `event` | `EventDataset` | EEG event marker code → integer class |
| `misc` | `MISCDataset` | Per-epoch MISC channel (e.g. reaction time) |
| `info` | `InfoDataset` | Per-subject attribute (e.g. age, diagnosis group) |

---

## Step 8 — Multi-Dataset Training

To combine multiple datasets in one training run, export each separately and concatenate:

```python
from torch.utils.data import ConcatDataset, DataLoader
from neurodoc.dataset_api.factory import build_dataset_from_task

mi_task = {
    "task_type": "classification",
    "label_route": "event",
    "target_events": {
        "769": {"y": 0, "label": "left hand MI"},
        "770": {"y": 1, "label": "right hand MI"},
    },
}

datasets = [
    build_dataset_from_task(mi_task, h5_path=f"./hdf5_output/{name}.hdf5")
    for name in ["bcic_iv_2a", "bcic_iv_2b", "physionet_mi"]
]

combined = ConcatDataset(datasets)
loader = DataLoader(combined, batch_size=64, shuffle=True, num_workers=4)
```

> [!TIP]
> Before combining datasets, verify that `Channels` and `Sampling Rate` are compatible across all selected datasets. Mismatched channel counts will cause shape errors. Use the `pipeline` parameter in the export step to standardise channels and resampling.

---

## Further Reading

For advanced EEGUnity usage — custom preprocessing pipelines, locator files, batch processing, and HDF5 format specification — refer to the official documentation:

**[EEGUnity Documentation → eegunity.readthedocs.io](https://eegunity.readthedocs.io/)**

Search for:
- *"Export epochs to HDF5"* — full parameter reference for `epoch_by_event_hdf5`
- *"Read HDF5 with PyTorch"* — DataLoader integration patterns
- *"Kernel interface"* — how to write or adapt a custom kernel for a new dataset
