# Healthy Brain Network (HBN) EEG - Release 10

**Dataset**: `openneuro_ds005515` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005515
**Category**: Complex Applied | **Subjects**: 533 | **Files (Completed)**: 2515 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 10 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 10818 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 10562 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 5858 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 3689 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 3034 | event | raw | Participant button press - right hand |
| `instructed_toOpenEyes` | 2862 | event | raw | Instruction to open eyes (resting block) |
| `right_target` | 2812 | event | raw | Right-side target stimulus |
| `left_target` | 2545 | event | raw | Left-side target stimulus |
| `instructed_toCloseEyes` | 2365 | event | raw | Instruction to close eyes (resting block) |
| `video_start` | 1627 | event | raw | Movie clip onset |
| `video_stop` | 1610 | event | raw | Movie clip offset |
| `trialResponse` | 1211 | event | raw | Trial response event |
| `boundary` | 1385 | admin | raw | Segment boundary marker |
| `resting_start` | 516 | event | raw | Resting-state block onset |
| `9999` | 2105 | admin | raw | End-of-recording marker |


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
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stim_ON`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Contrast Detection Classification (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`left_target`, `right_target`, `left_buttonPress`, `right_buttonPress`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-tilted stimulus onset (contrast change) |
  | `right_target` | 1 | Right-tilted stimulus onset (contrast change) |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Presents a six-task EEG battery including contrast detection, extracting epochs -0.5s to 1.0s post-target
- **Kernel Notes**: Match button press responses to preceding target events to create correct/incorrect labels if needed. Exclude admin markers (`boundary`, `9999`).

### Classical Task 2: Resting State vs. Task EEG Classification (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s *, tmax = 2.0 s *, target_events = [`resting_start`, `video_start`, `contrastTrial_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | 0 | Resting-state block onset |
  | `video_start` | 1 | Naturalistic video viewing onset |
  | `contrastTrial_start` | 2 | Contrast detection trial block onset |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Six-task battery including resting-state (eyes-open/closed), naturalistic videos, contrast detection; 2s segments extracted for resting EEG
- **Kernel Notes**: Use long-event epochs sliding through each block. (replaces Classical Task 1 from original analysis.md)

### Classical Task 3: Phenotypic Variable Prediction from EEG Connectivity (Super-meta)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0 *, target_events = [`resting_start`, `video_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A | continuous | Age, IQ, ADHD-SWAN, CBCL, SCARED anxiety, Barratt SES |
- **Super Meta Notes**: Derived from phenotypic assessment instruments (WISC IQ, CBCL, SWAN ADHD, SCARED, Barratt SES) administered to participants, not from raw EEG event markers. Kernel must: (1) join EEG subjects with phenotypic CSV by subject ID, (2) compute iCOH or other FC features from 2s epochs, (3) use MDMR or regression to predict phenotypic values. Subject-wise splits required to prevent leakage.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Predicts phenotypic/demographic variables (age, IQ, ADHD, anxiety, SES, CBCL) from EEG functional connectivity using 2s epochs
- **Kernel Notes**: Requires phenotypic CSV download and harmonization. Merge on subject identifier. (replaces Classical Task 2 and Classical Task 3 from original analysis.md)

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