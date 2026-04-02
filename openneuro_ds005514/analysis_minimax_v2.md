# Healthy Brain Network (HBN) EEG - Release 9

**Dataset**: `openneuro_ds005514` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005514
**Category**: Complex Applied | **Subjects**: 295 | **Files (Completed)**: 2885 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 9 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, externalizing, phenotypic, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005514

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 30059 | short | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 30018 | short | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 16449 | long | raw | Contrast detection trial block onset |
| `left_buttonPress` | 10593 | short | raw | Participant button press - left hand |
| `right_buttonPress` | 10002 | short | raw | Participant button press - right hand |
| `right_target` | 7910 | short | raw | Right-side target stimulus |
| `left_target` | 7857 | short | raw | Left-side target stimulus |
| `break cnt` | 2807 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 2569 | short | raw | Trial response event |
| `instructed_toOpenEyes` | 1591 | long | raw | Instruction to open eyes (resting block) |
| `boundary` | 1554 | admin | raw | Segment boundary marker |
| `instructed_toCloseEyes` | 1325 | long | raw | Instruction to close eyes (resting block) |
| `resting_start` | 269 | long | raw | Resting-state block onset |
| `9999` | 2155 | admin | raw | End-of-recording marker |

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

### Primary Task 1: Resting-state EEG classification of psychiatric diagnoses
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ADHD` | 0/1 | Attention-Deficit/Hyperactivity Disorder diagnosis |
  | `ANX (anxiety)` | 0/1 | Anxiety disorder diagnosis |
  | `SLD` | 0/1 | Specific Learning Disorder diagnosis |
  | `ASD` | 0/1 | Autism Spectrum Disorder diagnosis |
  | `DISR` | 0/1 | Disruptive disorders diagnosis |
  | `COM` | 0/1 | Communication disorders diagnosis |
  | `DEP` | 0/1 | Depressive disorders diagnosis |
  | `Other` | 0/1 | Other DSM-V diagnosis |
- **Super Meta Notes**: Derived from clinical DSM-V diagnoses made by licensed clinicians. Kernel step: Join EEG epoch files with phenotypic diagnosis tables by subject ID; compute binary labels per DSM-V category; use subject-wise splits to prevent data leakage.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-label classification of 8 DSM-V psychiatric diagnoses from resting-state EEG in HBN pediatric sample
- **Kernel Notes**: Requires phenotypic data join; use leave-one-subject-out or subject-wise cross-validation; binary cross-entropy loss per diagnosis.

### Primary Task 2: Resting-state EEG regression of dimensional symptom severity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `SCARED GAD` | float | Screen for Child Anxiety Related Disorders - Generalized Anxiety |
  | `SWAN IN` | float | Sustained Attention (Inattention) subscale score |
  | `SWAN HY` | float | Sustained Attention (Hyperactivity) subscale score |
  | `SRS-2 SCI` | float | Social Responsiveness Scale-2 Social Communication Index |
  | `SRS-2 RRB` | float | Social Responsiveness Scale-2 Restricted Interests/Repetitive Behavior |
  | `WISC VCI` | float | Wechsler Intelligence Scale for Children Verbal Comprehension Index |
  | `WMI` | float | Working Memory Index |
- **Super Meta Notes**: Derived from standardized behavioral/questionnaire assessments (SCARED, SWAN, SRS-2, WISC-V). Kernel step: Join EEG epochs with phenotypic tables; use age/gender adjusted standardized scores as regression targets.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-target regression of 7 continuous dimensional measures from resting-state EEG
- **Kernel Notes**: Requires phenotypic data join; subject-wise splits mandatory; MSE loss; standardize targets within age/gender bins.

### Primary Task 3: Contrast detection target classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`left_target`, `right_target`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-side target stimulus presented |
  | `right_target` | 1 | Right-side target stimulus presented |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — HBN dataset description with contrast change detection paradigm using left vs right target classification
- **Kernel Notes**: Verify tmin/tmax from paper; filter epochs with `stim_ON` preceding target for valid trials; exclude incorrect responses if behavioral accuracy is needed.

### Primary Task 4: Resting-state eyes condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s *, overlap = 0.0 *, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting block |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting block |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Resting-state paradigm with 20s eyes-open and 40s eyes-closed blocks; epochs extracted from these long events
- **Kernel Notes**: Verify actual block durations from events; use 30s default if duration variable; filter blocks marked by `resting_start` if needed for strict resting identification.

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

- OpenNeuro dataset page: `https://openneuro.org/datasets/ds005514/versions/1.0.1`
- EEG2025 challenge portal: `https://eeg2025.github.io/`
- EEGUnity kernel tutorial (rich/super meta abstraction): `https://eegunity.readthedocs.io/en/v0.7.0/tutorial/How%20to%20Reading%20Rich%20Meta%20Data%20via%20Kernel.html`
- EEGUnity batch API (`epoch_by_event_hdf5`, `epoch_by_long_event_hdf5`): `https://eegunity.readthedocs.io/en/v0.7.0/eegunity.modules.batch.html`
