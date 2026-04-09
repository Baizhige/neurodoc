# Vicarious touch: overlapping neural patterns between seeing and feeling touch

**Dataset**: `openneuro_ds004563` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004563
**Category**: Sensory/Response | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 512 Hz

## Paradigm

Participants either saw someone else being touched (vicarious touch, event 4) or felt touch themselves (direct touch, event 1). EEG was recorded to investigate overlapping neural patterns between observed and experienced tactile stimulation. The study tests whether vicarious touch engages somatosensory cortex similarly to directly felt touch.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `4` | ~29xN | short | raw | Seeing touch (vicarious touch condition) |
| `1` | ~29xN | short | raw | Feeling touch (direct touch condition) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

### Info

No additional scan information available.

## Tasks


### Primary Task 1: Publisher-defined BIDS task: Touch decoding
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004563 DOI: https://doi.org/10.1101/2022.06.21.497107


### Normal Task 1: Raw-meta task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Needs verification

- **Kernel Notes**: Exclude admin markers from target labels.


### Normal Task 2: Super-meta task
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target / Label**: Needs verification
- **Kernel Notes**: Derive and version super-meta in kernel.

## Data Quality Notes

- 29 subjects with binary condition structure
- 64 channels at 512 Hz

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004563