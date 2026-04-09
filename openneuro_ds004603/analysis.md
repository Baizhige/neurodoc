# Visual Attribute-Specific Contextual Trajectory Paradigm

**Dataset**: `openneuro_ds004603` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004603
**Category**: Sensory/Response | **Subjects**: 37 | **Files (Completed)**: 37 | **Channels**: 65 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants observed sequences of visual stimuli that either followed or violated an established contextual trajectory in one of three visual attributes - brightness (color), size, or orientation. The paradigm tests predictive coding by contrasting EEG responses to expected (step) stimuli against unexpected violations and a no-trajectory control condition. Each sequence comprised four ordered steps followed by a target or violation stimulus.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `step_1` | 31368 | event | raw | Sequence step 1 - first ordered stimulus in trajectory |
| `step_2` | 31367 | event | raw | Sequence step 2 |
| `step_3` | 31367 | event | raw | Sequence step 3 |
| `step_4` | 31367 | event | raw | Sequence step 4 - final step before target/violation |
| `control` | 14203 | event | raw | Control condition - no established trajectory |
| `siz_vio` | 4736 | event | raw | Size trajectory violation |
| `ori_vio` | 4735 | event | raw | Orientation trajectory violation |
| `col_vio` | 4735 | event | raw | Color/brightness trajectory violation |
| `catch` | 2958 | event | raw | Catch trial requiring button-press response |
| `initalising_triggers` | 1 | admin | raw | System initialisation trigger (exclude) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Violation Detection (Multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.7 s, target_events = [`control`, `siz_vio`, `ori_vio`, `col_vio`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `control` | 0 | No-trajectory control condition |
  | `siz_vio` | 1 | Size trajectory violation |
  | `ori_vio` | 2 | Orientation trajectory violation |
  | `col_vio` | 3 | Color/brightness trajectory violation |
- **Evidence**:
  - DOI: `10.1016/j.cortex.2023.08.004` — Linear SVM classifiers decoded expectation violation signals by comparing each violation type (brightness/size/orientation) to physically identical control trials using epoched data time-locked to final stimulus onset (segmented -200 to 700 ms, baselined -100 to 0 ms)
- **Kernel Notes**: Baseline correction applied to -100 to 0 ms pre-stimulus window. Exclude `initalising_triggers` (admin). Catch trials (`catch`) contain motor response component and should be excluded from violation analysis. Sequence steps (`step_1` through `step_4`) can be used separately for prediction build-up ERP analysis but are not part of this primary classification task. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Exclude `initalising_triggers` from all analysis.
- Catch trials have a motor response component - treat separately or exclude from violation analysis.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review