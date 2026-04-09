# Healthy Brain Network (HBN) EEG - Release 2

**Dataset**: `openneuro_ds005506` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005506
**Category**: Complex Applied | **Subjects**: 152 | **Files (Completed)**: 1405 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 2 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 14116 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 14081 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 9310 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 5762 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 4970 | event | raw | Participant button press - right hand |
| `right_target` | 4463 | event | raw | Right-side target stimulus |
| `left_target` | 4439 | event | raw | Left-side target stimulus |
| `break cnt` | 1577 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 1372 | event | raw | Trial response event |
| `instructed_toOpenEyes` | 883 | event | raw | Instruction to open eyes (resting block) |
| `boundary` | 799 | admin | raw | Segment boundary marker |
| `video_start` | 797 | event | raw | Movie clip onset |
| `video_stop` | 765 | event | raw | Movie clip offset |
| `instructed_toCloseEyes` | 736 | event | raw | Instruction to close eyes (resting block) |
| `resting_start` | 150 | event | raw | Resting-state block onset |
| `9999` | 1150 | admin | raw | End-of-recording marker |


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

### Classical Task 1: Phenotypic regression from functional connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, overlap = 0.0, target_events = [`video_start`, `resting_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | age | Subject age in years |
  | N/A (continuous) | sex | Subject biological sex (binary) |
  | N/A (continuous) | IQ | WISC score |
  | N/A (continuous) | CBCL | Child Behavior Checklist score |
  | N/A (continuous) | ADHD | SWAN ADHD measure |
  | N/A (continuous) | anxiety | SCARED anxiety measure |
  | N/A (continuous) | SES | Barratt SES score |
- **Super Meta Notes**: Derived from behavioral assessments (WISC, CBCL, Barratt SES, SWAN, SCARED, MFQ, IAT, SDS, DTS) and demographic data administered separately from EEG recording. Kernel step: Compute imaginary coherence (iCOH) in delta/theta/alpha/beta bands from 2s epochs, then apply MDMR to regress phenotypic variables from connectivity matrices.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Regression of 12 phenotypic/demographic variables (age, sex, IQ, ADHD, anxiety, SES, CBCL) from whole-brain functional connectivity patterns in source space
- **Kernel Notes**: Extract 2s epochs from video and resting segments, compute iCOH across frequency bands, join with phenotypic CSV by subject ID using subject-wise splits to prevent data leakage.

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
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
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