# Mind in Motion: Young Adults Walking Over Uneven Terrain

**Dataset**: `openneuro_ds004625` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004625
**Category**: Complex Applied | **Subjects**: 32 | **Files (Completed)**: 543 | **Channels**: 284 | **Sampling Rate**: 500 Hz

## Paradigm

Participants walked over uneven terrain at different speeds while high-density EEG, EMG, and kinematic data were simultaneously recorded, with a seated resting condition also included. The study examines neural correlates of locomotor control and gait adaptation during ambulatory tasks. Gait events (heel-strikes, toe-offs) were synchronized with EEG via force-sensitive insoles.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004625

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LHS` | 65124 | short | raw | Left heel strike |
| `LTO` | 65105 | short | raw | Left toe off |
| `RHS` | 63800 | short | raw | Right heel strike |
| `RTO` | 63792 | short | raw | Right toe off |
| `CGY-T 1` | 2786 | short | raw | Terrain change trigger |
| `CGY-M 1` | 676 | short | raw | Gait measurement marker |
| `spare-M 1` | 635 | short | raw | Spare measurement marker |
| `boundary` | 543 | admin | raw | Segment boundary (exclude) |
| `TrialStart` | 543 | long | raw | Trial start marker |
| `TrialEnd` | 543 | long | raw | Trial end marker |
| `LS-Sync` | 536 | admin | raw | Insole sync pulse (exclude) |
| `CWR-M 1` | 269 | short | raw | Cobblestone walk marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Mixed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004625 DOI: https://doi.org/10.18112/openneuro.ds004625.v1.0.2


### Normal Task 1: Gait Event Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: High channel count (284-channel HD-EEG). boundary and LS-Sync are admin - exclude. TrialStart/TrialEnd define walking bouts. Extensive motion artifact rejection required.

 | Event | y | Meaning |
 |-------|---|---------|
 | `LHS` | 0 | Left heel strike |
 | `LTO` | 1 | Left toe off |
 | `RHS` | 2 | Right heel strike |
 | `RTO` | 3 | Right toe off |
## Data Quality Notes

- High-density EEG (284 channels) with significant motion artifacts from walking.
- boundary and LS-Sync markers are administrative - exclude.
- Mobile EEG data - apply ICA-based artifact correction.

## References

- **Reference**: `Mind in Motion: Young Adults Walking Over Uneven Terrain`
