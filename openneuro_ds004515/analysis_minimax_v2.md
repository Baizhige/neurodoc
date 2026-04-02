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
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`FB`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `FB` | 0 | Punishment feedback (red screen) |
  | `FB` | 1 | Reward feedback (green screen) |
- **Evidence**:
  - DOI: `10.1016/j.pscychresns.2023.111685` — EEG classification of reward vs punishment feedback detection using RewP and delta power in a reinforcement learning task
- **Kernel Notes**: The paper epochs from -2000 to 6000 ms around feedback onset, cut to -500 to +1000 ms with baseline correction. Verify feedback color mapping (green=reward, red=punishment) from dataset documentation.

### Primary Task 2: Affective Imagery Type Classification (Puppy vs Alcohol)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`CUE`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `CUE` | 0 | Neutral imagery (puppy) |
  | `CUE` | 1 | Alcohol-related imagery |
- **Evidence**:
  - DOI: `10.1016/j.pscychresns.2023.111685` — Classification of affective imagery type (puppy vs alcohol) showing differential RewP and delta power effects across hazardous drinkers and controls
- **Kernel Notes**: Imagery type is embedded in the trial structure. Verify mapping between CUE events and image type (puppy/alcohol) from events.tsv. May require inferring image type from trial order or additional annotation columns.

### Primary Task 3: Drinking Group Classification (Hazardous vs Control)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`FB`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `FB` | 0 | Control group (light drinkers) |
  | `FB` | 1 | Hazardous drinkers (heavy drinkers) |
- **Super Meta Notes**: Derived from subject-level metadata (AUDIT scores). Kernel step: Map subject IDs to group labels using participant demographics file; assign group label to all epochs from each subject.
- **Evidence**:
  - DOI: `10.1016/j.pscychresns.2023.111685` — Finds group differences in alcohol-specific RewP correlation with AUDIT scores between hazardous drinkers and controls
- **Kernel Notes**: Requires loading participant metadata to obtain group assignment. Use AUDIT score threshold (e.g., ≥8 for hazardous) or pre-defined group labels from dataset.

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
