# Healthy Brain Network (HBN) EEG - Release 6

**Dataset**: `openneuro_ds005510` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005510
**Category**: Complex Applied | **Subjects**: 3000 | **Files (Completed)**: 1227 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 6 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 13706 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 13696 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 5817 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 3743 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 3249 | event | raw | Participant button press - right hand |
| `right_target` | 2796 | event | raw | Right-side target stimulus |
| `left_target` | 2793 | event | raw | Left-side target stimulus |
| `break cnt` | 1242 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 1483 | event | raw | Trial response event |
| `instructed_toOpenEyes` | 810 | event | raw | Instruction to open eyes (resting block) |
| `instructed_toCloseEyes` | 676 | event | raw | Instruction to close eyes (resting block) |
| `boundary` | 666 | admin | raw | Segment boundary marker |
| `resting_start` | 135 | event | raw | Resting-state block onset |
| `9999` | 866 | admin | raw | End-of-recording marker |


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

### Classical Task 1: Phenotypic Factor Regression from EEG Functional Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, overlap = 0.0 *, target_events = [`resting_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | continuous | Resting-state EEG epochs for FC computation |
  | `instructed_toOpenEyes` | continuous | Eyes-open resting |
  | `instructed_toCloseEyes` | continuous | Eyes-closed resting |
- **Super Meta Notes**: Derived from external phenotypic assessments (WISC IQ, CBCL behavioral problems, SWAN ADHD, SCARED anxiety, Barratt SES) and demographic variables (age, sex). Kernel step: Compute iCOH (imaginary coherence) in frequency bands (delta 0.5-4Hz, theta 4-7.5Hz, alpha 7.5-15Hz, beta 15-30Hz) from 2s epochs, then train regression model to predict phenotypic/demographic continuous values. Must use subject-wise splits to prevent leakage.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — This paper analyzes EEG functional connectivity (imaginary coherence) from the HBN Biobank to identify associations between brain connectivity patterns and phenotypic measures including age, sex, IQ, ADHD, anxiety, and socioeconomic status.
- **Kernel Notes**: Combine resting-state epochs (~300s per subject) from `resting_start`, `instructed_toOpenEyes`, and `instructed_toCloseEyes` events. Compute connectivity features per epoch in multiple frequency bands. Join EEG-derived features with phenotypic CSV tables using subject IDs. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Video Viewing Task Epoch Extraction (Despicable Me)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | N/A | Video viewing segments (Despicable Me movie) |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Paper mentions video viewing (Despicable Me, The Present, Diary of a Wimpy Kid, Fun with Fractals) as part of the EEG recording paradigm.
- **Kernel Notes**: Use segmentation on continuous data during movie viewing periods. Verify movie start/end markers from task-sidecar JSON. (replaces Classical Task 2 from original analysis.md)

### Classical Task 3: Sequence Learning Task Epoch Extraction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | N/A | Sequence learning task segments (Seq Learning6target, Seq Learning8target) |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Paper references inhibition/excitation paradigm task included in HBN EEG recordings.
- **Kernel Notes**: Identify sequence learning task blocks from BIDS task labels. Extract epochs aligned to task structure. (replaces Classical Task 3 from original analysis.md)

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
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`.

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