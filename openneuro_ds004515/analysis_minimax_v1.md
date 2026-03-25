# EEG: Alcohol imagery reinforcement learning task with light and heavy drinker participants

**Dataset**: `openneuro_ds004515` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004515
**Category**: High-level Mental | **Subjects**: 42 | **Files (Completed)**: 42 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants (light and heavy drinkers) performed a reinforcement learning task involving alcohol-related and neutral imagery cues. On each trial, participants chose between left and right buttons in response to cues, with feedback (FB) indicating correct/incorrect responses. The study investigates how reward learning interacts with alcohol cue reactivity across drinking groups.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004515

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CUE` | ~42xN | short | raw | Stimulus cue onset |
| `Left Button` | ~42xN | short | raw | Left button press response |
| `Right Button` | ~42xN | short | raw | Right button press response |
| `FB` | ~42xN | short | raw | Feedback onset |
| `STATUS` | ~42xN | admin | raw | BrainVision hardware status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Reward vs Punishment Feedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`FB`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB` (punishment/red screen) | 0 | Punishment feedback (negative outcome) |
  | `FB` (reward/green screen) | 1 | Reward feedback (positive outcome) |
- **Evidence**:
  - DOI: 10.1016/j.pscychresns.2023.111685 — Uses EEG data from OpenNeuro ds004515 to examine reward positivity (RewP) and delta band power in response to feedback (reward vs punishment) in a reinforcement learning task with affective imagery across hazardous drinkers and control groups
- **Kernel Notes**: The FB event encodes reward (green screen) vs punishment (red screen) outcomes. Epochs are extracted around feedback onset (-2000 to 6000 ms in original analysis, then cut to -500 to +1000 ms). Kernel must identify reward vs punishment condition from FB event metadata or associated stimulus channel.

### Primary Task 2: Affective Imagery Type Classification (Puppy vs Alcohol)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`CUE`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `CUE` (puppy image) | 0 | Neutral/positive affective image (puppy) |
  | `CUE` (alcohol image) | 1 | Alcohol-related cue image |
- **Evidence**:
  - DOI: 10.1016/j.pscychresns.2023.111685 — Secondary analysis examines how affective imagery type (puppy vs alcohol) modulates RewP and delta power, with image type coded as puppy->0 and alcohol->1
- **Kernel Notes**: The CUE event precedes display of affective images (puppy or alcohol). Must map CUE events to associated image type via stimulus metadata or trial structure.

### Normal Task 1: Response Direction Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS is an admin event - exclude from target_events. CUE and FB are trial markers but not the primary classification target. Left vs Right button press provides a binary motor/decision classification.

| Event | y | Meaning |
 |-------|---|------|
 | `Left Button` | 0 | Left button press |
 | `Right Button` | 1 | Right button press |

## Data Quality Notes

- 42 subjects split between light and heavy drinkers
- STATUS markers are BrainVision hardware events, not task-related

## References

- **Reference**: `EEG: Alcohol imagery reinforcement learning task with light and heavy drinker participants`
