# The BMI-HDEEG dataset 1

**Dataset**: `openneuro_ds004444` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004444
**Category**: Action/Output | **Subjects**: 465 | **Files (Completed)**: 465
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

Brain-computer interfacing task based on sensorimotor rhythms (SMR) using high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the first of four BMI-HDEEG datasets, enabling classification of motor imagery across all four classes.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_manual_review
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004444

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 465xx | long | raw | Motor imagery cue - class 1 (left hand MI) |
| `2` | 465xx | long | raw | Motor imagery cue - class 2 (right hand MI) |
| `3` | 465xx | long | raw | Motor imagery cue - class 3 (feet MI) |
| `4` | 465xx | long | raw | Motor imagery cue - class 4 (tongue MI) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Normal Task 1: Motor Imagery Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numerical codes 1-4 decoded by specific kernel to semantic MI labels. Extended epoch window (-0.5 to 4.0 s) captures full motor imagery period. High-density 130-channel EEG.

| Event | y | Meaning |
|-------|---|---------|
| `left_hand_MI` | 0 | Left hand motor imagery |
| `right_hand_MI` | 1 | Right hand motor imagery |
| `feet_MI` | 2 | Feet motor imagery |
| `tongue_MI` | 3 | Tongue motor imagery |

## Data Quality Notes

- Numerical event codes (1-4) require kernel-level decoding to semantic MI labels
- 130-channel high-density EEG with extended epochs
- Large dataset (465 files); batch processing required

