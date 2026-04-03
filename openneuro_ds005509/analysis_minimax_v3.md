# Healthy Brain Network (HBN) EEG - Release 5

**Dataset**: `openneuro_ds005509` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005509
**Category**: Complex Applied | **Subjects**: 330 | **Files (Completed)**: 3326 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 5 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Status**: wait_manual_review
> **Evidence Keywords**: response_time, externalizing, phenotypic, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005509

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 35156 | short | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 35136 | short | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 18682 | long | raw | Contrast detection trial block onset |
| `left_buttonPress` | 10192 | short | raw | Participant button press - left hand |
| `right_buttonPress` | 9498 | short | raw | Participant button press - right hand |
| `right_target` | 8977 | short | raw | Right-side target stimulus |
| `left_target` | 8947 | short | raw | Left-side target stimulus |
| `break cnt` | 3296 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 3367 | short | raw | Trial response event |
| `instructed_toOpenEyes` | 1969 | long | raw | Instruction to open eyes (resting block) |
| `boundary` | 1839 | admin | raw | Segment boundary marker |
| `instructed_toCloseEyes` | 1639 | long | raw | Instruction to close eyes (resting block) |
| `resting_start` | 329 | long | raw | Resting-state block onset |
| `9999` | 2339 | admin | raw | End-of-recording marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `externalizing_factor`, `p_factor`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stim_ON`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sequence Learning State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stim_ON`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stim_ON` | 0 | still-unknown (first presentation, not yet learned) |
  | `stim_ON` | 1 | newly-learned (recently acquired memory) |
  | `stim_ON` | 2 | known (well-established memory) |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — EEG dataset for assessing information processing including a sequence learning paradigm where trials were categorized as 'still-unknown', 'newly-learned', or 'known' based on participants' recall reports.
- **Kernel Notes**: Labels require recall performance data to determine learning state. Kernel must merge stimulus events with behavioral recall labels to assign 0/1/2. Verify event ID mapping from events.tsv - using `stim_ON` as proxy for stimulus_onset.

### Primary Task 2: Phenotypic Variable Prediction from Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, overlap = 0.0, target_events = [`resting_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | continuous | age | Participant age in years (continuous) |
  | binary | sex | Participant sex (M/F) |
  | continuous | IQ | WISC score |
  | continuous | ADHD | SWAN score |
  | continuous | SES | Barratt score |
  | continuous | anxiety | SCARED score |
  | continuous | CBCL | Child Behavior Checklist score |
- **Super Meta Notes**: Derived from phenotypic assessments (WISC, SWAN, Barratt, SCARED, CBCL) administered to participants, not from EEG event markers. Kernel step: Extract connectivity features (iCOH) from 2-s epochs during resting-state and video-viewing blocks, then perform multivariate regression against phenotypic vectors per subject.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — EEG functional connectivity from the HBN Biobank identifies associations between phase-coupling networks and phenotypic/demographic measures (age, sex, IQ, ADHD, SES, anxiety, CBCL) using multivariate distance matrix regression.
- **Kernel Notes**: Requires join between EEG epochs and phenotypic CSV tables by subject ID. Use subject-wise train/test splits to prevent leakage. Resting-state blocks identified by `resting_start` and `instructed_toOpenEyes`/`instructed_toCloseEyes` annotations.

### Normal Task 1: Raw-meta event decoding and classification (event-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use non-admin events such as `left_target`, `right_target`, `trialResponse`, `stim_ON`.

- **Kernel Notes**: Exclude admin markers from supervised target sets.

### Normal Task 2: Raw-meta state decoding (long-event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`, `video_start`, `video_stop`.

- **Kernel Notes**: Keep block-label mapping stable across releases.

### Normal Task 3: Super-meta response-time regression (competition-style)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: event-centered windows (task-dependent), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `response_time`
- **Kernel Notes**: Parse trial chains and write regression targets with unit/version metadata.

### Normal Task 4: Super-meta psychopathology-factor modeling
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

