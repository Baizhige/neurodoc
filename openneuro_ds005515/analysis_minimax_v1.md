# Healthy Brain Network (HBN) EEG - Release 10

**Dataset**: `openneuro_ds005515` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005515
**Category**: Complex Applied | **Subjects**: 533 | **Files (Completed)**: 2515 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 10 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, externalizing, phenotypic, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005515

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 10818 | short | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 10562 | short | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 5858 | long | raw | Contrast detection trial block onset |
| `left_buttonPress` | 3689 | short | raw | Participant button press - left hand |
| `right_buttonPress` | 3034 | short | raw | Participant button press - right hand |
| `instructed_toOpenEyes` | 2862 | long | raw | Instruction to open eyes (resting block) |
| `right_target` | 2812 | short | raw | Right-side target stimulus |
| `left_target` | 2545 | short | raw | Left-side target stimulus |
| `instructed_toCloseEyes` | 2365 | long | raw | Instruction to close eyes (resting block) |
| `video_start` | 1627 | long | raw | Movie clip onset |
| `video_stop` | 1610 | long | raw | Movie clip offset |
| `trialResponse` | 1211 | short | raw | Trial response event |
| `boundary` | 1385 | admin | raw | Segment boundary marker |
| `resting_start` | 516 | long | raw | Resting-state block onset |
| `9999` | 2105 | admin | raw | End-of-recording marker |

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

### Primary Task 1: Phenotypic Variable Prediction from EEG Functional Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`resting_start`, `video_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | age | continuous | Participant age in years |
  | sex | 0/1 | Biological sex (categorical encoded) |
  | IQ | continuous | WISC/WAIS IQ score |
  | ADHD-SWAN | continuous | ADHD rating from SWAN instrument |
  | CBCL | continuous | Child Behavior Checklist total score |
  | SCARED | continuous | Screen for Child Anxiety Related Disorders |
  | Barratt SES | continuous | Socioeconomic status measure |
- **Super Meta Notes**: Labels are derived from phenotypic assessment instruments (WISC IQ, CBCL, SWAN ADHD, SCARED, Barratt SES) administered to participants, not from raw EEG event markers. The paper computes imaginary coherence (iCOH) functional connectivity from concatenated epochs across resting state and task paradigms.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — This paper analyzes EEG from HBN Biobank, computing source-localized functional connectivity (iCOH) from concatenated resting state and task data, and uses multivariate distance matrix regression (MDMR) to associate connectivity patterns with phenotypic assessment instruments (age, sex, IQ, ADHD, CBCL, anxiety, SES).
- **Kernel Notes**: Extract 2-second epochs from resting state (eyes-open/closed), inhibition/excitation paradigms, and naturalistic video segments. Compute iCOH connectivity matrix per subject. Join with phenotypic CSV by subject ID using leave-one-subject-out cross-validation to prevent leakage.

### Primary Task 2: Contrast Detection ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_target`, `right_target`, `stim_ON`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-tilted contrast increase stimulus |
  | `right_target` | 1 | Right-tilted contrast increase stimulus |
- **Super Meta Notes**: N/A - uses raw event markers only.
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — This paper presents the HBN six-task EEG battery including contrast detection, with target epochs extracted -0.5s to 1.0s post-target for analyzing CPP and P300 components.
- **Kernel Notes**: Epoch around target stimulus onset. Exclude trials without subsequent button press response. Label based on target side (left vs right). Could extend to include response-locked epochs around buttonPress events.

### Primary Task 3: Resting-State EEG Classification (Eyes-Open vs Eyes-Closed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state block |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state block |
- **Super Meta Notes**: N/A - uses raw event markers indicating instruction to open/close eyes.
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — The six-task battery includes resting-state paradigms with eyes-open and eyes-closed conditions; 2-second segments used for analysis.
- **Kernel Notes**: Extract epochs during resting state blocks labeled by instruction event. Use eyes-open vs eyes-closed as binary classification target.

### Normal Task 1: Raw-meta event decoding and classification (event-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use non-admin events such as `left_target`, `right_target`, `trialResponse`, `stim_ON`.

- **Kernel Notes**: Exclude admin markers from supervised target sets.


### Normal Task 2: Raw-meta state decoding (long-event)
- **Task Type**: classification/segmentation
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
- **Task Type**: regression (or discretized classification baseline)
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

## References

- OpenNeuro dataset page: `https://openneuro.org/datasets/ds005515/versions/1.0.1`
- EEG2025 challenge portal: `https://eeg2025.github.io/`
- EEGUnity kernel tutorial (rich/super meta abstraction): `https://eegunity.readthedocs.io/en/v0.7.0/tutorial/How%20to%20Reading%20Rich%20Meta%20Data%20via%20Kernel.html`
- EEGUnity batch API (`epoch_by_event_hdf5`, `epoch_by_long_event_hdf5`): `https://eegunity.readthedocs.io/en/v0.7.0/eegunity.modules.batch.html`
