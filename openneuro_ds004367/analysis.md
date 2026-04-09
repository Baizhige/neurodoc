# Meta-rdk: Raw EEG data

**Dataset**: `openneuro_ds004367` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004367
**Category**: High-level Mental | **Subjects**: 42 | **Files (Completed)**: 40
**Channels**: 68 | **Sampling Rate**: 1200 Hz

## Paradigm

A visual motion discrimination task involving left/right direction decisions on random dot kinematogram (RDK) stimuli followed by a metacognitive confidence assessment using a visual analog scale. The numerical trigger codes encode stimulus direction, coherence level, response direction, confidence level, and feedback. The dataset supports both motion perception classification and confidence/metacognition regression.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `3072` | 40x300 | short | raw | Motion stimulus onset (specific direction/coherence) |
| `3456` | 40x300 | short | raw | Motion stimulus onset (specific direction/coherence) |
| `3584` | 40x300 | short | raw | Motion stimulus onset (specific direction/coherence) |
| `3968` | 40x300 | short | raw | Motion stimulus onset (specific direction/coherence) |
| `4096` | 40x300 | short | raw | Motion stimulus onset (specific direction/coherence) |
| `4480` | 40x300 | short | raw | Motion stimulus onset (specific direction/coherence) |
| `31744`...`25984` | 40x10 each | short | raw | Response/confidence marker (numerical code) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

- **STIM Label Summary**: Route `stim`, role trigger-channel or stimulus-marker based labeling. Candidate Trigger Labels: Needs verification. Kernel Note: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Rdk
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004367 DOI: https://doi.org/10.1101/2022.10.19.22281249


### Normal Task 1: Motion Direction Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numerical trigger codes require specific kernel decoding. Regression target: response_time and confidence from misc channels.

| Event | y | Meaning |
|-------|---|-------|
| `motion_stimulus_onset` | 0 | Motion stimulus onset |
| `left_response` | 1 | Left direction response |
| `right_response` | 2 | Right direction response |
| `confidence_low` | 3 | Low confidence rating |
| `confidence_medium` | 4 | Medium confidence rating |
| `confidence_high` | 5 | High confidence rating |
| `feedback_onset` | 6 | Feedback onset |

## Data Quality Notes

- All event IDs are numerical codes requiring kernel-level decoding
- 68 channels includes EOG/ECG channels
- 42 subjects but only 40 files completed

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, confidence, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004367