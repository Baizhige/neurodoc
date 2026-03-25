# Interval Timing Task

**Dataset**: `openneuro_ds004579` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004579
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed an interval timing task where they estimated durations of different intervals. BrainVision S-codes (S 1-S 7) encode different timing conditions or interval lengths. Participants produced or reproduced time intervals by button press (R 3). The study investigates neural oscillations and temporal processing mechanisms.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004579

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | ~30xN | short | raw | Timing condition 1 |
| `S 2` | ~30xN | short | raw | Timing condition 2 |
| `S 3` | ~30xN | short | raw | Timing condition 3 |
| `S 4` | ~30xN | short | raw | Timing condition 4 |
| `S 5` | ~30xN | short | raw | Timing condition 5 |
| `S 6` | ~30xN | short | raw | Timing condition 6 |
| `S 7` | ~30xN | short | raw | Timing condition 7 |
| `R 3` | ~30xN | short | raw | Button press response |
| `boundary` | ~30xN | admin | raw | Recording boundary marker |
| `S255` | ~30xN | admin | raw | BrainVision overflow/system marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 1`, `S 2`, `S 3`, `S 4`, `S 5`, `S 6`, `S 7`, `S255`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Interval Timing
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004579 DOI: https://doi.org/10.1101/2022.07.26.22278079


### Normal Task 1: Timing Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: boundary and S255 are admin events - exclude from target_events. R 3 is a response event - can be used as an additional classification target. S255 is a BrainVision system marker (overflow/sync), not a task event.

| Event | y | Meaning |
 |-------|---|------|
 | `S 1` | 0 | Timing condition 1 |
 | `S 2` | 1 | Timing condition 2 |
 | `S 3` | 2 | Timing condition 3 |
 | `S 4` | 3 | Timing condition 4 |
 | `S 5` | 4 | Timing condition 5 |
 | `S 6` | 5 | Timing condition 6 |
 | `S 7` | 6 | Timing condition 7 |
## Data Quality Notes

- boundary and S255 must be excluded from epoching
- S255 is a BrainVision system marker, not a task event
- 30 subjects with 7 timing conditions

## References

- **Reference**: `Interval Timing Task`
