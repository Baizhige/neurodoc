# Drum Trainer

**Dataset**: `openneuro_ds004152` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004152
**Category**: Complex Applied | **Subjects**: 21 | **Files (Completed)**: 21 | **Channels**: 31 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants learned and performed specific rhythmic drumming patterns at varying tempos using keyboard keys, receiving adaptive visual feedback on timing accuracy. EEG was recorded continuously during drumming training. Each key press generates a Stimulus event marker; the dataset contains thousands of drumming events per participant (2300-4700 Stimulus events per file).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004152

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | ~65000 | short | raw | Individual drum key press / beat onset |
| `New Segment` | 21 | admin | raw | Recording segment boundary |
| `Comment` | 21 | admin | raw | Experimenter comment marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Reward Positivity Predicts Timing Adjustment
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.5 s, tmax = 1.5 s, target_events = [`feedback_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `feedback_onset` | continuous | RT adjustment value (positive = slowing, negative = speeding) |
- **Evidence**:
  - DOI: 10.1111/psyp.14589 — Regression-based ERP analysis examining whether trial-to-trial fluctuations in RewP (240-340ms at FCz) predict timing adjustment on the subsequent trial in a continuous drumming task with color-coded feedback.
- **Kernel Notes**: Extract feedback_onset events; compute continuous RT adjustment labels from timing data; use stick functions -1500 to 1500ms around feedback onset for epoching; predict RT adjustment from RewP (240-340ms window).

### Primary Task 2: Publisher-defined BIDS task: Drumtrainer
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`Stimulus`] *
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**:
  - OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004152 DOI: https://doi.org/10.18112/openneuro.ds004152.v1.1.2


### Normal Task 1: Drum Beat Detection (single-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one event class. Useful for stimulus-locked ERP analysis. New Segment and Comment are admin events, excluded.

 | Event | y | Meaning |
 |-------|---|---------|
 | `Stimulus` | 0 | Drum key press / beat onset |

## Data Quality Notes

- Very high event rate; check for event jitter in timing accuracy analysis
- Only 21 subjects; limited generalizability

## References

- **Reference**: `Drum Trainer EEG dataset`
