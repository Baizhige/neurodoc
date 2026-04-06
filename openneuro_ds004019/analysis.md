# Effect of obesity on arithmetic processing in preteens with high and low math skills. An event-related potentials study

**Dataset**: `openneuro_ds004019` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004019
**Category**: High-level Mental | **Subjects**: 62 | **Files (Completed)**: 62
**Channels**: 132 | **Sampling Rate**: 500 Hz

## Paradigm

Obese and non-obese preteens (ages 9-10) performed a delayed-verification arithmetic task to evaluate the effects of weight status and math skill level on arithmetic processing. Participants viewed an arithmetic problem (prob), then a delay (bgin), then a verification digit (face) and responded (resp). Trigger codes 0 and 1 encode response correctness (0=incorrect, 1=correct). The study uses ERPs to investigate neural correlates of arithmetic cognition in the context of childhood obesity.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | ~14,880 | event | raw | Trial beginning / delay period onset |
| `prob` | ~14,880 | event | raw | Arithmetic problem onset |
| `ch++` | ~14,880 | event | raw | Choice/comparison stimulus onset |
| `face` | ~14,880 | event | raw | Verification digit (face stimulus) onset |
| `resp` | ~14,600 | event | raw | Participant button-press response |
| `1` | ~14,364 | event | raw | Correct response (1=correct) |
| `0` | ~6,156 | event | raw | Incorrect response (0=incorrect) |
| `sync` | ~310 | admin | raw | Hardware sync pulse |
| `CELL` | ~248 | admin | raw | Cell/block marker |
| `SESS` | 62 | admin | raw | Session start marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Correct vs Incorrect Arithmetic Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`1`, `0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `0` | 0 | Incorrect arithmetic response |
  | `1` | 1 | Correct arithmetic response |
- **Evidence**:
  - DOI: 10.3389/fnhum.2022.760234 — This paper analyzes ERP components (P150, P300, N400) time-locked to answer choice presentation to compare obese vs non-obese preteens with high/low math skills on arithmetic verification tasks, using correct vs incorrect response events (1 and 0) for epoching.
- **Kernel Notes**: Epochs are time-locked to answer choice onset (face/ch++ events). The `1` and `0` events mark response correctness concurrent with `resp`. Class imbalance (~70% correct across subjects) should be addressed using weighted loss or undersampling. Exclude admin markers (sync, CELL, SESS) from analysis.

## Data Quality Notes

- 132-channel EGI cap (E1-E128 + ECG/Respiration/SP channels); remove non-EEG channels before analysis
- sync/CELL/SESS are admin markers to exclude
- Class imbalance: ~70% correct trials - apply undersampling or weighted loss


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review