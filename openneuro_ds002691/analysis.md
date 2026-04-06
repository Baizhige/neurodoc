# Internal attention study

**Dataset**: `openneuro_ds002691` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002691
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 32 | **Sampling Rate**: 250 Hz

## Paradigm

A sustained internal attention task where participants were asked to either mentally concentrate on a target (concentrate condition) or relax (relax condition) for 15-second sustained blocks with eyes closed. Transitional cues (`getready`, `wait`) marked preparation periods between active blocks. The study investigated EEG signatures of sustained internal attention versus relaxation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: response_time
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002691

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `concentrate` | 20 (files) | long | raw | 15-second sustained mental concentration block |
| `relax` | 20 (files) | long | raw | 15-second sustained relaxation block |
| `getready` | 20 (files) | admin | raw | Preparation cue between blocks - transitional |
| `wait` | 20 (files) | admin | raw | Wait period between blocks - transitional |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Internalattention
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds002691 DOI: https://doi.org/10.18112/openneuro.ds002691.v1.1.0


### Normal Task 1: Attention State Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `getready` and `wait` are transitional preparation markers - excluded from target_events. 15-second sustained blocks are appropriate for long_event epoching with 2 s windows and 0.5 overlap. Misc channel `response_time` available for regression.

 | Event | y | Meaning |
 |-------|---|---------|
 | `concentrate` | 0 | Sustained mental concentration (15 s blocks) |
 | `relax` | 1 | Sustained relaxation (15 s blocks) |
## Data Quality Notes

- Small dataset: 20 subjects, 1 file each.
- Eyes-closed recording throughout; no eye movement artifacts expected.
- The count column (20 files) reflects that every file has these events, not the per-subject trial count.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Internal attention study`
