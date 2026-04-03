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
> **Status**: wait_manual_review
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

### Primary Task 1: Conflict Trial Classification (Congruent vs Incongruent)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`Trn Stim`, `Test Stim`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Trn Stim` | 0 | Congruent trial (stimulus-response compatible) |
  | `Trn Stim` | 1 | Incongruent trial (stimulus-response conflict) |
  | `Test Stim` | 0 | Congruent trial (stimulus-response compatible) |
  | `Test Stim` | 1 | Incongruent trial (stimulus-response conflict) |
- **Super Meta Notes**: Derived from raw event subtypes in events.tsv (congruent/incongruent columns). Kernel step: Read events.tsv, extract stimulus onset events, map trial_type column (congruent=0, incongruent=1).
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — SVM classification of congruent vs incongruent Simon trials using theta-band time-frequency ROI features from conflict/error contrasts.
- **Kernel Notes**: Verify event ID mapping from events.tsv. The raw events `Trn Stim` and `Test Stim` contain congruent/incongruent subtypes in the trial_type column that must be extracted. Baseline window: -300 to -200 ms prior to stimulus.

### Primary Task 2: Response Outcome Classification (Correct vs Error)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`correct`, `incorrect`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `correct` | 1 | Correct response |
  | `incorrect` | 0 | Error/incorrect response |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2018.05.020` — Classification of correct vs error responses using theta-band features, with post-correct and post-error contrast analysis.
- **Kernel Notes**: Epoch on response markers. Exclude no-response trials (`Trn No Response`, `Test No Response`). (replaces Normal Task 1 from original analysis.md)

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

