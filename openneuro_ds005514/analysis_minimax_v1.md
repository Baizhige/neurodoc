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

### Primary Task 1: Psychiatric Diagnosis Classification (DSM-V Multi-Label)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0*
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ADHD` | 0/1 | Attention-Deficit/Hyperactivity Disorder diagnosis |
  | `ANX` | 0/1 | Anxiety disorder diagnosis |
  | `SLD` | 0/1 | Specific Learning Disorder diagnosis |
  | `ASD` | 0/1 | Autism Spectrum Disorder diagnosis |
  | `DISR` | 0/1 | Disruptive disorders diagnosis |
  | `COM` | 0/1 | Communication disorders diagnosis |
  | `DEP` | 0/1 | Depressive disorders diagnosis |
  | `Other` | 0/1 | Other DSM-V diagnosis category |
- **Super Meta Notes**: Labels derived from clinical DSM-V diagnoses by licensed clinicians (consensus-based). Binary multi-label classification per subject.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Benchmarks ML models for predicting 8 DSM-V psychiatric diagnoses using resting-state EEG (eyes-closed, 2-second epochs)
- **Kernel Notes**: Use concatenated eyes-closed resting-state segments; subject-wise train/test splits required; multi-label output layer.

### Primary Task 2: Dimensional Symptom Severity Regression (Multi-Target)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0*
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `SCARED_GAD` | continuous | SCARED Generalized Anxiety Disorder score (age/gender adjusted) |
  | `SWAN_IN` | continuous | SWAN Inattention score (age/gender adjusted) |
  | `SWAN_HY` | continuous | SWAN Hyperactivity score (age/gender adjusted) |
  | `SRS2_SCI` | continuous | SRS-2 Social Communication Index (age/gender adjusted) |
  | `SRS2_RRB` | continuous | SRS-2 Restricted Interests/Repetitive Behavior (age/gender adjusted) |
  | `WISC_VCI` | continuous | WISC Verbal Comprehension Index |
  | `WMI` | continuous | WISC Working Memory Index |
- **Super Meta Notes**: Labels derived from standardized behavioral/questionnaire assessments (SCARED, SWAN, SRS-2, WISC-V). Continuous regression targets.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-target regression of 7 continuous dimensional measures from resting-state EEG
- **Kernel Notes**: Standardize regression targets; subject-wise splits; join EEG with phenotypic tables by subject key; handle missing values explicitly.

### Primary Task 3: Contrast Detection Event Classification (Raw Meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-side target stimulus presentation |
  | `right_target` | 1 | Right-side target stimulus presentation |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Describes contrast detection paradigm with left/right target stimuli (tmin=-0.5s, tmax=1.0s epochs)
- **Kernel Notes**: Exclude admin markers; align epochs to `stim_ON` or `fixpoint_ON` triggers; filter by condition.

### Primary Task 4: Sequence Learning Event Classification (Raw Meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.8 s, target_events = [`trialResponse`]*
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `trialResponse` | 0/1* | Sequence learning trial response (accuracy label derived from sequence stage)* |
- **Super Meta Notes**: Learning stage labels (unknown/newly-learned/known) derived from behavioral performance.
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Sequence learning paradigm with 900ms epochs (tmin=-0.1s, tmax=0.8s); P300 amplitude as neural correlate of learning
- **Kernel Notes**: Parse trial chains; derive accuracy labels from response timing/selection; keep stimulus onset alignment.

### Primary Task 5: Resting State Segmentation (Raw Meta)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 20.0 s (eyes-open)*, overlap = 0.0*, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state block |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state block |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Resting-state blocks: 20s eyes-open, 40s eyes-closed
- **Kernel Notes**: Use long-event epochs on resting-state markers; differentiate eyes-open vs eyes-closed conditions.

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
