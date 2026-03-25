# EEG recordings for 200 object images presented in RSVP sequences at 5Hz or 20Hz

**Dataset**: `openneuro_ds004018` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004018
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

Rapid Serial Visual Presentation (RSVP) of 200 object images at two presentation frequencies (5 Hz and 20 Hz) to investigate the temporal dynamics of visual object representations. Images were categorized as "stars" or "boats" (two superordinate categories), allowing investigation of how presentation rate affects category-level neural decoding. This is a very small dataset (2 subjects).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004018

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stars` | 2 files | short | raw | RSVP onset - star/celestial category image |
| `boats` | 2 files | short | raw | RSVP onset - boat/vehicle category image |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Rsvp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004018 DOI: https://doi.org/10.1016/j.neuroimage.2018.12.046


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

- Only 2 subjects - extremely limited statistical power for group-level analysis
- RSVP at 5 Hz and 20 Hz: at 20 Hz, images appear for only 50 ms (near threshold for conscious processing)
- Verify that `stars` and `boats` events correspond to onset markers and not sustained states

## References

- **Reference**: `The representational dynamics of visual objects in rapid serial visual processing streams. NeuroImage, 188, 668-679`
