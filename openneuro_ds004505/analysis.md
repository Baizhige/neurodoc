# Real World Table Tennis

**Dataset**: `openneuro_ds004505` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004505
**Category**: Action/Output | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants played real table tennis matches in two conditions: cooperative (rallying) and competitive (point-scoring). EEG was recorded during actual gameplay using a mobile EEG system. Events mark the condition type and specific ball-hit moments (moving_serve vs stationary_serve shots). The study investigates motor cortex dynamics during ecological real-world sport.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004505

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `moving_hit` | ~19xN | short | raw | Ball hit during moving serve condition |
| `stationary_hit` | ~19xN | short | raw | Ball hit during stationary serve condition |
| `cooperative` | ~19xN | long | raw | Cooperative play condition block |
| `competitive` | ~19xN | long | raw | Competitive play condition block |
| `moving_serve` | ~19xN | long | raw | Moving serve condition block |
| `stationary_serve` | ~19xN | long | raw | Stationary serve condition block |
| `STATUS` | ~19xN | admin | raw | BrainVision hardware status marker |
| `M 1` | ~19xN | admin | raw | Miscellaneous hardware marker |

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

### Primary Task 1: Publisher-defined BIDS task: Table Tennis
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004505 DOI: https://doi.org/10.3390/s22155867


### Normal Task 1: Hit Type Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: STATUS and M 1 are admin events - exclude from target_events. cooperative/competitive/moving_serve/stationary_serve are long condition blocks. Focus on discrete hit events for epoch-based analysis.

| Event | y | Meaning |
 |-------|---|------|
 | `moving_hit` | 0 | Ball hit in moving serve condition |
 | `stationary_hit` | 1 | Ball hit in stationary serve condition |
## Data Quality Notes

- Real-world mobile EEG with significant motion artifacts expected
- STATUS and M 1 are hardware markers, not task events

## References

- **Reference**: `Real World Table Tennis`
