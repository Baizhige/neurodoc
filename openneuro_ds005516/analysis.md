# Healthy Brain Network (HBN) EEG - Release 11

**Dataset**: `openneuro_ds005516` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005516
**Category**: Complex Applied | **Subjects**: 3000 | **Files (Completed)**: 3396 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 11 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 37825 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 37760 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 19366 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 14777 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 13758 | event | raw | Participant button press - right hand |
| `right_target` | 9311 | event | raw | Right-side target stimulus |
| `left_target` | 9226 | event | raw | Left-side target stimulus |
| `trialResponse` | 4056 | event | raw | Trial response event |
| `break cnt` | 3196 | admin | raw | Break/counter marker between blocks |
| `video_start` | 1666 | event | raw | Movie clip onset |
| `instructed_toOpenEyes` | 1644 | event | raw | Instruction to open eyes (resting block) |
| `video_stop` | 1541 | event | raw | Movie clip offset |
| `boundary` | 1462 | admin | raw | Segment boundary marker |
| `instructed_toCloseEyes` | 1370 | event | raw | Instruction to close eyes (resting block) |
| `resting_start` | 372 | event | raw | Resting-state block onset |
| `9999` | 3038 | admin | raw | End-of-recording marker |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `externalizing_factor`, `p_factor`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: FC-phenotype association regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0 (segments concatenated across entire recording for FC computation)
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `age` | continuous | Participant age in years |
  | `sex` | 0/1 | Biological sex (binary) |
  | `IQ` | continuous | WISC-measured intelligence quotient |
  | `CBCL` | continuous | Child Behavior Checklist score |
  | `SWAN_ADHD` | continuous | SWAN ADHD measure |
  | `SES` | continuous | Barratt Socioeconomic Status |
  | `anxiety` | continuous | SCARED anxiety score |
- **Super Meta Notes**: Derived from phenotypic assessment tables (WISC, CBCL, SWAN, Barratt, SCARED) external to EEG. Kernel must: (1) identify subject ID from EEG filename, (2) join with phenotypic CSV by subject, (3) compute FC (iCOH) from 2s segments across concatenated tasks, (4) apply MDMR or similar multivariate regression to predict phenotypic vectors from FC matrices.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Uses HBN EEG source-space connectivity (iCOH) to predict age, sex, IQ, CBCL, ADHD, SES, anxiety via MDMR association analysis
- **Kernel Notes**: Requires full-recording concatenation across multiple task blocks (resting 300s, video 117-230s, visual flicker 210s). Segment-level FC computed per 2s window, then aggregated into subject-level connectivity matrix. Phenotypic labels must be aligned by subject ID. Use subject-wise splits to prevent data leakage.

### Classical Task 2: Publisher-defined BIDS task: Despicable Me
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://eeg2025.github.io/ DOI: https://doi.org/10.1101/089060


### Classical Task 3: Publisher-defined BIDS task: Surround Supp
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://eeg2025.github.io/ DOI: https://doi.org/10.1101/089060


### Classical Task 4: Publisher-defined BIDS task: Funwith Fractals
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://eeg2025.github.io/ DOI: https://doi.org/10.1101/089060

### Potential Task 1: Raw-meta event decoding and classification (event-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Use non-admin events such as `left_target`, `right_target`, `trialResponse`, `stim_ON`.

- **Kernel Notes**: Exclude admin markers from supervised target sets.

### Potential Task 2: Raw-meta state decoding (long-event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`, `video_start`, `video_stop`.

- **Kernel Notes**: Keep block-label mapping stable across releases.

### Potential Task 3: Super-meta response-time regression (competition-style)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: event-centered windows (task-dependent), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `response_time`
- **Kernel Notes**: Parse trial chains and write regression targets with unit/version metadata.

### Potential Task 4: Super-meta psychopathology-factor modeling
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs Verification, target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `p_factor` / `externalizing_factor` (schema dependent)
- **Kernel Notes**: Join EEG with phenotypic tables by subject key and use subject-wise splits to prevent leakage.

## Data Quality Notes

- HBN is a heterogeneous multi-task battery; task availability differs across participants and files.
- Event naming and density are not perfectly uniform across releases; mapping tables should be explicit.
- Admin markers (`boundary`, `9999`, etc.) are frequent and must be filtered before model target construction.
- Super-meta tasks are sensitive to join quality (subject ID harmonization, missingness, leakage control).
- Report clearly whether each experiment uses raw meta labels or super meta labels.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review