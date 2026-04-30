# Resting-State EEG Dataset for Sleep Deprivation

**Dataset**: `openneuro_ds004902` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004902
**Category**: Biological State | **Subjects**: 71 | **Files (Completed)**: 218 | **Channels**: 61 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Resting-state EEG recordings with eyes open and eyes closed were conducted under two conditions: normal sleep and 24-hour sleep deprivation. The study investigates how sleep loss modulates spontaneous brain activity. Subjects participated in two sessions (normal sleep vs sleep-deprived) in a counterbalanced within-subject design. Files are split by condition (eyesopen/eyesclosed) with 5-minute continuous blocks.

## File Scan Result

> **Kernel SHA256**: `853b689d3ac3a4b842f90ee5a6bfcb311ac1e5d90547a4b1422d93c08fcf1930`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 33` | 60 | event | raw | Unknown trigger marker - frequent occurrence suggests possible recording segment or status marker |
| `S 44` | 7 | event | raw | Unknown trigger marker |
| `S 45` | 7 | event | raw | Unknown trigger marker |
| `S 55` | 7 | event | raw | Unknown trigger marker |
| `S 66` | 7 | event | raw | Unknown trigger marker |
| `S119` | 7 | event | raw | Unknown trigger marker |
| `boundary` | 14 | admin | raw | Data boundary marker - indicates discontinuity or epoch boundary in continuous recording |
| `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}` | 76 | event | super | Trial phase onset: eyes-closed resting-state recording condition |
| `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}` | 142 | event | super | Trial phase onset: eyes-open resting-state recording condition |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: eyes open vs eyes closed classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 5 s *, target_events = [`super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}`, `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}` | 0 | eyes-open resting-state condition |
  | `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}` | 1 | eyes-closed resting-state condition |
- **Evidence**:
- **Notes**: The 'super' event annotations with eyes_condition metadata are confirmed trial phase onsets from the dataset's pre-scan annotations, directly mapping to the two resting-state conditions (eyes_open: 142 occurrences, eyes_closed: 76 occurrences). The 5-second epoch window is inferred as a conservative estimate for stable resting-state brain activity, well within the 300-second continuous recording blocks. No explicit epoch timing was found in available references.

### Potential Task 1: Gender Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | M -> 0; F -> 1 |
- **Evidence**:
  - participants.tsv — 71 participants with complete subject_sex column (M/F values); binary sex classification from resting-state EEG segments
- **Notes**: Segmentation-based task: 4-second non-overlapping windows from continuous 5-minute resting-state recordings (eyes open/closed). Gender is a native participants.tsv column with complete coverage, enabling subject-level stratified classification. The model must learn sex-differentiating spectral or connectivity patterns from spontaneous EEG.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
