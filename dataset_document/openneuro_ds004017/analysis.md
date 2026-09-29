# Embodied Learning for Literacy EEG

**Dataset**: `openneuro_ds004017` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004017
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 126 | **Manual Review**: Pending
**Channels**: 65 | **Sampling Rate**: 2048 Hz

## Paradigm

A pre-post intervention study assessing literacy and orthographic processing in children through two tasks: a two-alternative forced choice letter discrimination task (b vs. d confusion) and a visual search task. EEG was recorded across multiple sessions to evaluate the neural effects of an embodied learning intervention on letter processing. The paradigm includes stimulus-locked epochs (time-locked to letter onset) and response-locked epochs capturing motor execution and accuracy markers.

## File Scan Result

> **Kernel SHA256**: `617df94976f45a7172ae1ae19f7f7fede106dc0c83406e9bfc0daaefe43ccc17`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_-6.750007999999999` | 1 | event | raw | Sparse timing marker |
| `event_-6.750197999999999` | 3 | event | raw | Sparse timing marker |
| `event_-6.750208` | 6 | event | raw | Sparse timing marker |
| `event_-6.815544` | 3770 | event | raw | Trial-level timing marker (condition variant) |
| `event_-6.815644` | 3693 | event | raw | Trial-level timing marker (condition variant) |
| `event_-6.8157239999999994` | 864 | event | raw | Response-aligned timing marker |
| `event_-6.815734` | 800 | event | raw | Response-aligned timing marker |
| `event_-6.815744` | 9340 | event | raw | Trial-level timing marker (unspecified) |
| `event_-7.86412` | 9 | event | raw | Session or block boundary marker |
| `event_-7.8642199999999995` | 7 | event | raw | Session or block boundary marker |
| `event_-7.864319999999999` | 168 | event | raw | Session or block boundary marker |
| `event_0.0` | 9205 | event | raw | Session baseline or offset marker |
| `event_65536.0` | 6 | event | raw | System or hardware event code |
| `event_65546.0` | 3 | event | raw | System or hardware event code |
| `event_65736.0` | 1 | event | raw | System or hardware event code |
| `response_10` | 800 | event | raw | Response or sub-condition 10 |
| `response_20` | 864 | event | raw | Response or sub-condition 20 |
| `stimulus_b` | 3700 | event | raw | Letter type b stimulus onset |
| `stimulus_d` | 3779 | event | raw | Letter type d stimulus onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Letter discrimination (b vs d) under embodied literacy intervention
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus_b`, `stimulus_d`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stimulus_b` | 0 | Letter type b stimulus onset |
  | `stimulus_d` | 1 | Letter type d stimulus onset |
- **Evidence**:
  - DOI: `10.31234/osf.io/zmctf` — Damsgaard, Topor et al. EEG study (n=18 children 6-8 years) analyzing letter discrimination (b vs d) under embodied movement vs control conditions; ERP components P300a, N200, P300b extracted from stimulus-locked epochs.
  - DOI: `10.1016/j.neuropsychologia.2022.108061` — Companion publication supporting embodied learning paradigm for early literacy.
  - GitHub: `https://github.com/MovementAndNeuroscience/B-D_EEG_Child` — Repository with MATLAB preprocessing scripts (s01-s06) validating event-based epoching approach for this dataset.
- **Kernel Notes**: High sampling rate (2048 Hz); downsampling to 512 Hz recommended per published pipeline. Use semantic event names (stimulus_b/stimulus_d) rather than raw trigger codes. Balanced trial counts (3700 vs 3779) support binary classification.

---

### Potential Task 1: Response-locked ERP analysis for response categorization
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, target_events = [`response_10`, `response_20`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `response_10` | 0 | Response or sub-condition 10 |
  | `response_20` | 1 | Response or sub-condition 20 |
- **Evidence**:
  - DOI: `10.31234/osf.io/zmctf` — Paradigm includes response-locked measures alongside stimulus-locked analysis; response events provide motor execution and accuracy markers.
- **Kernel Notes**: Lower trial counts (800/864) vs stimulus events (~3700 each) suggests response events mark specific trial subsets (e.g., error trials, condition-specific responses). Window captures motor preparation (-500ms to 0ms) and execution (0 to +500ms). Verify mapping with dataset documentation.

---

### Potential Task 1: Pre-post intervention longitudinal analysis of literacy-related neural changes
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus_b`, `stimulus_d`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stimulus_b` | 0 | Letter type b stimulus onset |
  | `stimulus_d` | 1 | Letter type d stimulus onset |
- **Notes**: 21 subjects × 6 sessions = 126 files. Sessions 1-3 likely pre-intervention, sessions 4-6 post-intervention. Within-subject comparison of letter discrimination ERP changes across intervention timeline. Epoch parameters consistent with Classical Task 1 for valid comparison.
- **Kernel Notes**: Session-level structure must be inferred from file ordering since subject metadata is missing. Use same epoch parameters as Classical Task 1 for longitudinal comparability.

---

### Potential Task 2: Visual search task component analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus_b`, `stimulus_d`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stimulus_b` | 0 | Letter type b stimulus onset |
  | `stimulus_d` | 1 | Letter type d stimulus onset |
- **Notes**: Paradigm includes visual search task alongside letter discrimination. Stimulus events likely shared across both tasks within sessions. Plausible to extract visual search-specific epochs if task markers are present in annotations.
- **Kernel Notes**: Verify if visual search trials are distinguished via annotations or additional event codes not captured in initial file scan.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
