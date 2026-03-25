# Steer the Ship

**Dataset**: `openneuro_ds004264` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004264
**Category**: Complex Applied | **Subjects**: 21 | **Files (Completed)**: 21
**Channels**: 31 | **Sampling Rate**: 1000 Hz

## Paradigm

A ship-steering simulation where participants control a rotating arrow to maintain orientation against varying environmental and controller noise using unstable pole-and-cart physics. The task involves continuous manual control with varying noise levels, making it a real-world closed-loop BCI paradigm. EEG was recorded to study cognitive load and motor control under dynamic uncertainty.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004264

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 21x1000+ | short | raw | Stimulus/condition onset marker |
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

### Primary Task 1: Publisher-defined BIDS task: Steertheship
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004264 DOI: https://doi.org/10.18112/openneuro.ds004264.v1.1.0


### Normal Task 1: Stimulus Processing (single-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one event class available for epoching. New Segment and Comment are admin markers. Behavioral metadata (noise level, performance metrics) may be available in events.tsv for regression tasks.

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus` | 0 | Stimulus/condition onset |
## Data Quality Notes

- Only one non-admin event type (Stimulus); classification requires additional label parsing from events.tsv metadata columns
- New Segment and Comment are system/admin events excluded from epoching
- Variable trial counts across subjects (1473-2373 per subject)

## References

- **Reference**: `Steer the Ship`
