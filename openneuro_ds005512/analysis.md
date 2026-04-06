# Healthy Brain Network (HBN) EEG - Release 8

**Dataset**: `openneuro_ds005512` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005512
**Category**: Complex Applied | **Subjects**: 257 | **Files (Completed)**: 2320 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 8 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 22981 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 22913 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 12963 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 6946 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 6875 | event | raw | Participant button press - right hand |
| `right_target` | 6231 | event | raw | Right-side target stimulus |
| `left_target` | 6151 | event | raw | Left-side target stimulus |
| `trialResponse` | 2318 | event | raw | Trial response event |
| `break cnt` | 2258 | admin | raw | Break/counter marker between blocks |
| `instructed_toOpenEyes` | 1326 | event | raw | Instruction to open eyes (resting block) |
| `boundary` | 1237 | admin | raw | Segment boundary marker |
| `instructed_toCloseEyes` | 1104 | event | raw | Instruction to close eyes (resting block) |
| `resting_start` | 223 | event | raw | Resting-state block onset |
| `9999` | 1751 | admin | raw | End-of-recording marker |


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

### Classical Task 1: Psychiatric Diagnosis Classification from Resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s *, overlap = 0.95 * (to generate 2s epochs with ~0.1s step), target_events = [`instructed_toCloseEyes`, `resting_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | DSM-V diagnosis column | 0 | No diagnosis (neurotypical) |
  | DSM-V diagnosis column | 1 | Presence of diagnosis (ADHD/ANX/SLD/ASD/DISR/COM/DEP/Other) |
- **Super Meta Notes**: Derived from clinical DSM-V diagnostic assessments. Labels are binary vectors (8 categories) indicating presence/absence of psychiatric diagnoses. Kernel step: Concatenate eyes-closed resting blocks per subject, extract 2s epochs, extract spectral features (1-40 Hz), predict 8 binary diagnosis labels via multi-label classifier.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-task multi-label classification of 8 DSM-V psychiatric diagnoses from resting EEG (eyes-closed blocks, 2s epochs, 1-40 Hz spectral features)
- **Kernel Notes**: Filter for `instructed_toCloseEyes` or `resting_start` events (eyes-closed resting). Extract 2s epochs with ~0.1s step to achieve ~95% overlap. Compute spectral power in canonical bands (delta, theta, alpha, beta, gamma). Use multi-label classification (one classifier per diagnosis or multi-output approach). Ensure subject-wise train/test splits to prevent leakage. (replaces Classical Tasks 1-3 from original analysis.md)

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