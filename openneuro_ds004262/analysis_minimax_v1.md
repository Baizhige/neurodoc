# Continuous Feedback Processing

**Dataset**: `openneuro_ds004262` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004262
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 21
**Channels**: 31 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants predicted the final height of an animated rising bar based on cues with varying predictability to study continuous feedback processing and prediction error. Each trial involved observing bar motion and registering a prediction, allowing examination of EEG correlates of reward prediction error and uncertainty-driven learning.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004262

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 21x900 | short | raw | Stimulus onset marker (bar appearance) |
| `New Segment` | 21 | admin | raw | Recording segment boundary |
| `Comment` | 21 | admin | raw | Experimenter comment/annotation |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Continuous Reward Prediction Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -4.0 s, tmax = 0.2 s, target_events = [`Stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus` | continuous (0-1) | Normalized reward value (continuous reward signal) |
  | `Stimulus` | continuous | Reward expectancy (trial-by-trial average reward per cue) |
  | `Stimulus` | categorical (0/1/2) | Outcome predictability: high(0)/medium(1)/low(2) |
- **Super Meta Notes**: Labels are derived continuous variables computed from behavioral data: continuous reward signal (time-varying), trial-by-trial average reward (expectancy), outcome predictability (high/medium/low). These are computed from participant guesses and actual outcomes, not raw event markers.
- **Evidence**:
  - DOI: 10.1101/2022.10.06.511117 — This paper analyzes EEG data from openneuro_ds004262 using correlation and regression-based approaches to examine how scalp potentials track continuous reward prediction, testing whether the signal reflects reward prediction errors vs state values.
  - DOI: 10.1111/psyp.14399 — This paper analyzes EEG data from OpenNeuro dataset ds004262 using regression-based unmixing to identify neural correlates of continuous feedback processing, testing whether EEG tracks a continuously varying reward signal and how this varies with outcome predictability.
- **Kernel Notes**: Must compute continuous reward labels from behavioral data: (1) normalize raw reward values per participant, (2) compute reward expectancy as rolling average per cue type, (3) derive predictability from cue identity and trial history. Labels routed to Annotation channel as numeric values.

### Primary Task 2: Publisher-defined BIDS task: Gnomes
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004262 DOI: https://doi.org/10.18112/openneuro.ds004262.v1.0.0

### Normal Task 1: Stimulus Processing (single-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one event class available for epoching. New Segment and Comment are admin markers. Behavioral metadata (prediction, actual height) may be available in events.tsv for regression tasks.

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus` | 0 | Stimulus onset (bar presentation) |

## Data Quality Notes

- Only one non-admin event type (Stimulus); classification requires additional label parsing from events.tsv metadata columns
- New Segment and Comment are system/admin events excluded from epoching

## References

- **Reference**: `Continuous Feedback Processing`
