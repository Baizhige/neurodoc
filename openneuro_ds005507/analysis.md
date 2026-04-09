# Healthy Brain Network (HBN) EEG - Release 3

**Dataset**: `openneuro_ds005507` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005507
**Category**: Complex Applied | **Subjects**: 183 | **Files (Completed)**: 1812 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 3 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 18602 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 18564 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 12072 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 6995 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 6266 | event | raw | Participant button press - right hand |
| `right_target` | 5800 | event | raw | Right-side target stimulus |
| `left_target` | 5753 | event | raw | Left-side target stimulus |
| `break cnt` | 1973 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 1757 | event | raw | Trial response event |
| `instructed_toOpenEyes` | 1101 | event | raw | Instruction to open eyes (resting block) |
| `boundary` | 1074 | admin | raw | Segment boundary marker |
| `video_start` | 1041 | event | raw | Movie clip onset |
| `video_stop` | 1013 | event | raw | Movie clip offset |
| `instructed_toCloseEyes` | 915 | event | raw | Instruction to close eyes (resting block) |
| `resting_start` | 184 | event | raw | Resting-state block onset |
| `9999` | 1446 | admin | raw | End-of-recording marker |


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

### Classical Task 1: Phenotypic prediction from functional connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | continuous | Functional connectivity features from resting-state EEG epochs |
  | `video_start` | continuous | Functional connectivity features from movie-viewing EEG epochs |
- **Super Meta Notes**: Derived from raw events [`resting_start`, `video_start`, `video_stop`] by computing imaginary coherence (iCOH) on 2-s sliding windows, then regressing against phenotypic variables (age, sex, IQ, ADHD, anxiety, SES, CBCL). Kernel step: Extract EEG epochs around events → compute FC matrix → join with phenotypic table → train regression model.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Shows EEG functional connectivity from HBN Biobank resting state and video viewing predicts 10 phenotypic and 2 demographic variables
- **Kernel Notes**: Use source-localized EEG for iCOH computation. Exclude flicker task (no raw event marker available). Verify subject ID harmonization between EEG and phenotypic tables.


### Classical Task 2: Sequence learning state classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s *, target_events = [`contrastTrial_start`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `contrastTrial_start` | 0 | Still-unknown learning state |
  | `contrastTrial_start` | 1 | Newly-learned learning state |
  | `contrastTrial_start` | 2 | Known learning state |
- **Super Meta Notes**: Derived from raw events [`contrastTrial_start`] by mapping to learning states based on post-sequence recall reports (still-unknown, newly-learned, known). Kernel step: Parse trial chains → look up recall performance metadata → assign state label.
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Describes HBN sequence learning paradigm where trials categorized as still-unknown, newly-learned, or known based on recall reports
- **Kernel Notes**: Verify event ID mapping from events.tsv. Recall performance data must be joined from separate behavioral file. (replaces Classical Task 1 & 2 from original analysis.md)


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