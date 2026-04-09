# PES - Pandemic Emergency Scenario

**Dataset**: `openneuro_ds004477` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004477
**Category**: Complex Applied | **Subjects**: 9 | **Files (Completed)**: 9
**Channels**: 80 | **Sampling Rate**: 2048 Hz

## Paradigm

A strategic pandemic simulation task where participants allocate limited resources to cities on a map and report their decision confidence while interacting with an artificial agent. EEG was recorded to investigate neural correlates of complex decision-making, confidence estimation, and strategy formation in a realistic multi-agent scenario.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 9xx | short | raw | Decision stimulus onset |
| `resp_hold` | 9xx | short | raw | Response hold (button press start) |
| `resp_release` | 9xx | short | raw | Response release (button press end) |
| `confidence` | 9xx | short | raw | Confidence rating onset |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

Placeholder for additional file scan metadata.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: PES
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs Verification, tmax = Needs Verification, overlap = Needs Verification, target_events = [Needs Verification] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004477 DOI: https://doi.org/10.3389/fnhum.2019.00013


### Normal Task 1: Decision Making (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only 9 subjects; limited generalization. Small dataset suitable for within-subject analysis. Confidence ratings may be used as regression target.


| Event | y | Meaning |
|-------|---|------|
| `resp_hold` | 0 | Response initiation |
| `resp_release` | 1 | Response release |
| `stimulus` | 2 | Decision stimulus |
| `confidence` | 3 | Confidence rating |

## Data Quality Notes

- Only 9 subjects; very small dataset
- 80 channels at 2048 Hz (high temporal resolution)
- Complex task with strategic decisions; behavioral data critical for labeling

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: confidence, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004477