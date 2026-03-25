# Delayed Auditory Feedback EEG/EGG

**Dataset**: `openneuro_ds005403` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005403
**Category**: High-level Mental | **Subjects**: 66 | **Files (Completed)**: 66
**Channels**: 66 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed a speech production task while receiving delayed auditory feedback (DAF) to study neural processing of self-generated speech and auditory-motor monitoring. Three DAF conditions were used: an adaptation condition (fixed delay) and two random delay conditions (random1, random2), compared against a baseline (no delay). EEG was recorded alongside electroglottography (EGG) to capture vocal fold activity simultaneously. The event markers label continuous speech production blocks.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005403

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `adaption` | ~64/file | long | raw | Adaptation DAF condition block |
| `random1` | ~64/file | long | raw | Random delay condition 1 block |
| `random2` | ~64/file | long | raw | Random delay condition 2 block |
| `baseline` | ~64/file | rest | raw | Baseline (no delay) speech block |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Daf
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005403 DOI: https://doi.org/10.18112/openneuro.ds005403.v1.0.1


### Normal Task 1: DAF Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: All four conditions are sustained speech production blocks (>=2 s). Simultaneous EGG channels included; verify channel naming in channel metadata.

| Event | y | Meaning |
 |-------|---|------|
 | `baseline` | 0 | Baseline (no delay) |
 | `adaption` | 1 | Adaptation DAF condition |
 | `random1` | 2 | Random delay condition 1 |
 | `random2` | 3 | Random delay condition 2 |
## Data Quality Notes

- Simultaneous EGG recording alongside EEG - verify channel type labels.
- Speech production task - EMG artifacts from jaw/throat movement expected.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `Delayed Auditory Feedback EEG/EGG`
