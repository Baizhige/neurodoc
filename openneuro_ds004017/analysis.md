# Embodied Learning for Literacy EEG

**Dataset**: `openneuro_ds004017` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004017
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 126
**Channels**: 65 | **Sampling Rate**: 2048 Hz

## Paradigm

A pre-post intervention study assessing literacy and orthographic processing in children through two tasks: a two-alternative forced choice letter discrimination task (b vs. d confusion) and a visual search task. EEG was recorded across multiple sessions to evaluate the neural effects of an embodied learning intervention on letter processing. Trigger codes 10/20 and 100/200 likely encode the two letter types or correct/incorrect responses.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `100.0` | 63 files | event | raw | Stimulus onset - letter type B or condition 100 |
| `200.0` | 63 files | event | raw | Stimulus onset - letter type D or condition 200 |
| `20.0` | 61 files | event | raw | Stimulus onset - response or sub-condition 20 |
| `10.0` | 61 files | event | raw | Stimulus onset - response or sub-condition 10 |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Letter discrimination (b vs d) under embodied literacy intervention
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`100.0`, `200.0`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `100.0` | 0 | Letter type b (condition 100) |
  | `200.0` | 1 | Letter type d (condition 200) |
- **Super Meta Notes**: (none)
- **Evidence**:
  - DOI: `10.31234/osf.io.zmctf` — This paper analyzes EEG data from Study 1 where 18 children (6-8 years) performed a visual search task discriminating letters 'b' and 'd' under embodied movement (MOVE) vs gaze fixation (CON) conditions, extracting stimulus-locked ERP components (P300a, N200, P300b) from epochs time-locked to target letter onset.
- **Kernel Notes**: Preprocessing: high-pass 0.1 Hz, low-pass 40 Hz, baseline correction -100ms to 0ms, downsample to 512 Hz. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Pre-post intervention longitudinal analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = [`100.0`, `200.0`, `10.0`, `20.0`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `100.0` | 0 | Letter type b (condition 100) |
  | `200.0` | 1 | Letter type d (condition 200) |
  | `10.0` | * | Response/sub-condition 10 (verify mapping) |
  | `20.0` | * | Response/sub-condition 20 (verify mapping) |
- **Notes**: 21 subjects × 6 sessions = 126 files. Pre-post intervention design allows longitudinal analysis of literacy-related neural changes. Events 10.0/20.0 may encode response outcomes or sub-conditions — verify against dataset documentation.

## Data Quality Notes

- Numerical trigger codes; full decoding requires dataset documentation
- 21 subjects x 6 sessions - session-level structure must be considered
- High sampling rate (2048 Hz); consider downsampling for efficiency


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review