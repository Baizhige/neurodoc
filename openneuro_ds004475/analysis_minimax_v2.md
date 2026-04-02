# Mobile EEG split-belt walking study

**Dataset**: `openneuro_ds004475` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004475
**Category**: Complex Applied | **Subjects**: 30 | **Files (Completed)**: 30
**Channels**: 260 | **Sampling Rate**: 512 Hz

## Paradigm

A mobile brain-body imaging experiment investigating brain activity during gait adaptation using abrupt and gradual split-belt treadmill walking. Participants walked on a split-belt treadmill with different belt speeds while EEG and gait events (heel strikes, toe-offs) were recorded to study locomotor adaptation and associated cortical dynamics.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004475

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LHS` | 30xx | short | raw | Left heel strike (gait event) |
| `LTO` | 30xx | short | raw | Left toe-off (gait event) |
| `RHS` | 30xx | short | raw | Right heel strike (gait event) |
| `RTO` | 30xx | short | raw | Right toe-off (gait event) |
| `TRIG` | 30xx | short | raw | External trigger marker |
| `BUTTON` | 30xx | short | raw | Button press event |
| `SB1` | 30 | long | raw | Split-belt block 1 start (tied speed) |
| `SB2` | 30 | long | raw | Split-belt block 2 start (split speed) |
| `B1` | 30 | long | raw | Baseline block 1 |
| `B2` | 30 | long | raw | Baseline block 2 |
| `B3` | 30 | long | raw | Baseline block 3 |
| `P1` | 30 | long | raw | Perturbation block 1 |
| `P2` | 30 | long | raw | Perturbation block 2 |
| `End SB1` | 30 | admin | raw | End of split-belt block 1 |
| `End SB2` | 30 | admin | raw | End of split-belt block 2 |
| `End B1` | 30 | admin | raw | End of baseline block 1 |
| `End B2` | 30 | admin | raw | End of baseline block 2 |
| `End B3` | 30 | admin | raw | End of baseline block 3 |
| `End P1` | 30 | admin | raw | End of perturbation block 1 |
| `End P2` | 30 | admin | raw | End of perturbation block 2 |
| `boundary` | 8 | admin | raw | Segment boundary marker |
| `9633791` | 30 | admin | raw | Numerical system trigger |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Gait Event Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`LHS`, `LTO`, `RHS`, `RTO`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `LHS` | 0 | Left heel strike |
  | `LTO` | 1 | Left toe-off |
  | `RHS` | 2 | Right heel strike |
  | `RTO` | 3 | Right toe-off |
- **Evidence**:
  - DOI: `10.1113/jp284505` — This paper analyzes high-density EEG recorded during split-belt treadmill walking from 30 participants (dataset openneuro_ds004475) to examine spectral power changes in alpha, beta, and theta bands across gait adaptation stages, using gait events (heel strikes and toe-offs) detected from force plates as epoching points.
- **Kernel Notes**: (replaces Normal Task 1 from original analysis.md)

## Data Quality Notes

- boundary and 9633791 must be excluded as admin markers
- 260 channels includes motion capture channels; filter to EEG only
- Gait event counts vary across walking conditions (tied vs. split-belt speeds)

## References

- **Reference**: `Mobile EEG split-belt walking study`


## Data Quality Notes

- boundary and 9633791 must be excluded as admin markers
- 260 channels includes motion capture channels; filter to EEG only
- Gait event counts vary across walking conditions (tied vs. split-belt speeds)

## References

- **Reference**: `Mobile EEG split-belt walking study`
