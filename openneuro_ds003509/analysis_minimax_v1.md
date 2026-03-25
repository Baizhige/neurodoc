# EEG: Simon Conflict in Parkinson's

**Dataset**: `openneuro_ds003509` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003509
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 84
**Channels**: 67 | **Sampling Rate**: 500 Hz

## Paradigm

This study investigates mid-frontal theta deficits in Parkinson's disease (PD) patients during a modified Simon reaction-time task that requires cognitive control. Participants (high-performing PD patients and matched controls) performed congruent and incongruent Simon trials where stimulus position and response direction could conflict. The task included both a training phase with reinforcement feedback and a test phase without feedback. Mid-frontal theta (4-8 Hz) activity serves as an index of cognitive control and is modulated by cortical dopamine.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003509

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Trn Stim` | 1344 | short | raw | Training phase stimulus (congruent/incongruent) |
| `Test Stim` | 1008 | short | raw | Test phase stimulus (congruent/incongruent) |
| `correct` | 336 | short | raw | Correct response marker |
| `incorrect` | 334 | short | raw | Incorrect response / error marker |
| `Trn Resp` | 335 | short | raw | Training phase button-press response |
| `Test Resp` | 335 | short | raw | Test phase button-press response |
| `FB` | 168 | short | raw | Feedback stimulus in training phase |
| `Trn No Response` | 83 | short | raw | Missing response in training phase |
| `Test No Response` | 54 | short | raw | Missing response in test phase |
| `STATUS` | 84 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Trn Stim`, `Test Stim`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Simon Conflict Classification (Congruent vs Incongruent)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`Trn Stim`, `Test Stim`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `congruent` | 0 | Stimulus position matches response direction |
  | `incongruent` | 1 | Stimulus position conflicts with response direction |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — EEG data from modified Simon task used for binary classification of conflict trials (congruent→0, incongruent→1) using theta-band time-frequency ROI features from conflict/error contrasts.

### Primary Task 2: PD vs Control Classification (Subject-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`Trn Stim`, `Test Stim`, `resting`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | control subject | 0 | Healthy control participant |
  | PD patient | 1 | Parkinson's disease patient |
- **Super Meta Notes**: Requires aggregating epoch-level features (theta-band power from conflict/error contrasts) per subject to predict subject-level diagnosis. The paper used SVM with features from both task epochs and resting-state alpha power.
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — SVM classification of PD patients vs controls using theta-band time-frequency ROI features from conflict/error contrasts and resting alpha power, achieving 69% sensitivity and 72% specificity.

### Normal Task 1: Correct/Incorrect Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Correct and incorrect counts are approximately balanced (~336 vs ~334 total). Epoch on the response marker; exclude no-response trials.

| Event | y | Meaning |
|-------|---|------|
| `correct` | 1 | Correct response |
| `incorrect` | 0 | Error response |

## Data Quality Notes

- 67 channels including VEOG and positional channels (X, Y, Z); exclude non-EEG channels before analysis.
- Two sessions per subject for many participants; verify session consistency.
- `Trn Stim` and `Test Stim` have detailed subtypes in events.tsv (congruent/incongruent) that can support conflict classification.

## References

- **Reference**: `Mid-frontal theta activity is diminished during cognitive control in Parkinson's disease. Neuropsychologia, 2018. DOI: 10.1016/j.neuropsychologia.2018.05.020`
