# Simon-conflict Task

**Dataset**: `openneuro_ds004580` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004580
**Category**: Sensory/Response | **Subjects**: 30 | **Files (Completed)**: 30 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed the Simon conflict task in which stimulus location (left/right) could be congruent or incongruent with the required response direction. S 1 and S 2 encode congruent and incongruent trial types respectively; S 3 marks rare/catch trials. The study investigates conflict monitoring and executive control neural signatures (N2, P3 ERP components).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004580

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 1` | 30x384 | short | raw | Congruent trial (stimulus side matches response side) |
| `S 2` | 30x383 | short | raw | Incongruent trial (stimulus side opposite to response side) |
| `S 3` | ~30xN | short | raw | Rare/catch trial |
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
- **Candidate Trigger Labels**: `S 1`, `S 2`, `S 3`, `S255`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Simon
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004580 DOI: https://doi.org/10.1101/2022.07.26.22278079


### Normal Task 1: Congruent vs Incongruent Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: boundary and S255 are admin events - exclude from target_events. S255 is a BrainVision system marker (overflow/sync), not a task event. S 3 (rare trials) can be optionally included as a third class.

| Event | y | Meaning |
 |-------|---|------|
 | `S 1` | 0 | Congruent trial |
 | `S 2` | 1 | Incongruent trial |
## Data Quality Notes

- boundary and S255 must be excluded from epoching
- Balanced S 1 and S 2 counts (~384 vs ~383 per subject)
- 30 subjects with consistent congruent/incongruent structure

## References

- **Reference**: `Simon-conflict Task`
