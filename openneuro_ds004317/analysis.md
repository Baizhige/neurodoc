# Mood Manipulation and PST, Experiment 2

**Dataset**: `openneuro_ds004317` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004317
**Category**: High-level Mental | **Subjects**: 50 | **Files (Completed)**: 50
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

A reinforcement learning task (Probabilistic Selection Task) performed by participants following sad or happy mood manipulations. The paradigm mirrors Experiment 1 but compares sad and happy mood conditions rather than sad versus neutral. EEG was recorded to examine mood-dependent differences in reinforcement learning neural signatures.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004317

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `STIM` | 50x~240 | short | raw | Stimulus onset (stimulus pair presented) |
| `RESP` | 50x~230 | short | raw | Participant button-press response |
| `FB` | 50x~240 | short | raw | Feedback onset (reward/punishment) |
| `Correct` | 50x~198 | short | raw | Correct response outcome |
| `Incorrect` | 50x~100 | short | raw | Incorrect response outcome |
| `TESTING` | 50x~1664 | short | raw | Testing phase trial marker |
| `STATUS` | 50 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STIM`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: PST
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004317 DOI: https://doi.org/10.18112/openneuro.ds004317.v1.0.3


### Normal Task 1: Feedback Outcome Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS is an admin marker (exclude). TESTING events contain rich sub-labels in events.tsv. Better class balance than Experiment 1 (~198 correct vs ~100 incorrect in training phase).

| Event | y | Meaning |
 |-------|---|------|
 | `Correct` | 0 | Correct response |
 | `Incorrect` | 1 | Incorrect response |
## Data Quality Notes

- STATUS is an admin/system marker and must not be included in target events
- TESTING events contain rich sub-labels in events.tsv; the trial_type column provides full label strings
- Better class balance than Experiment 1

## References

- **Reference**: `Mood Manipulation and PST, Experiment 2`
