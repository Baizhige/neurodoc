# The time-course of feature-based attention effects dissociated from temporal expectation and target-related processes

**Dataset**: `openneuro_ds004043` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004043
**Category**: Sensory/Response | **Subjects**: 20 | **Files (Completed)**: 40
**Channels**: 63 | **Sampling Rate**: 250 Hz

## Paradigm

Participants viewed rapid sequences of overlaid oriented grating pairs (presented at ~10 Hz) and detected a target orientation while attention was cued to different feature dimensions (orientation or color). The study dissociates the time-course of feature-based attention effects from temporal expectation and target-detection processes using EEG frequency-tagging and ERP methods.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004043

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | 20 files | short | raw | Grating stimulus onset - condition 1 (e.g., attended feature) |
| `E 2` | 20 files | short | raw | Grating stimulus onset - condition 2 |
| `E 3` | 20 files | short | raw | Grating stimulus onset - condition 3 (e.g., target/distractor) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Temporal expectation
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004043 DOI: https://doi.org/10.1101/530352


### Normal Task 1: Attention Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 20 subjects x 2 sessions = 40 files. E 1/E 2/E 3 are EEGLAB-style markers; full decoding requires consulting the original study events.tsv. Balanced across conditions per session.

| Event | y | Meaning |
 |-------|---|------|
 | `E 1` | 0 | Attention condition 1 |
 | `E 2` | 1 | Attention condition 2 |
 | `E 3` | 2 | Attention condition 3 (target or distractor) |
## Data Quality Notes

- Events encoded as generic E markers; semantic meaning requires events.tsv inspection
- 20 subjects x 2 files suggests two sessions or two task conditions per subject
- 250 Hz sampling rate; adequate for ERP/steady-state visual evoked potential analysis

## References

- **Reference**: `Undivided attention: The temporal effects of attention dissociated from decision, memory, and expectation`
