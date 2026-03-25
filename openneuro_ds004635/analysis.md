# Gaffrey Lab Infant EEG Microstates Reliability

**Dataset**: `openneuro_ds004635` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004635
**Category**: Biological State | **Subjects**: 48 | **Files (Completed)**: 1
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Infants watched a series of engaging and relaxing videos to facilitate recording of spontaneous EEG activity. The dataset was collected to assess the test-retest reliability of EEG microstate metrics in infants. The single aggregated file contains data from 48 infants with recording-boundary markers; no active task was required.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004635

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | 10 | long | raw | Beginning of a recording segment |
| `TRSP` | 10 | long | raw | Transition / segment boundary marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Resting
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004635 DOI: https://doi.org/10.1038/35081509


### Normal Task 1: Long-term classification of paragraph tags (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 10 events of each type - very limited for supervised classification. Primary scientific use is resting-state microstate analysis. Single aggregated file covers all 48 infants.

| Event | y | Meaning |
 |-------|---|------|
 | `bgin` | 0 | Recording segment start |
 | `TRSP` | 1 | Transition segment marker |
## Data Quality Notes

- Single file aggregating 48 infants - individual subject effects not separable.
- Only 10 events of each type; insufficient for robust supervised classification.

## References

- **Reference**: `Gaffrey Lab Infant EEG Microstates Reliability`
