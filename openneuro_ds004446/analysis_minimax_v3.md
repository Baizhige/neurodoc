# The BMI-HDEEG dataset 2

**Dataset**: `openneuro_ds004446` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004446
**Category**: Action/Output | **Subjects**: 237 | **Files (Completed)**: 237
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

A high-density EEG dataset focused on sensorimotor rhythm-based brain-computer interfacing (BCI) with three motor imagery classes (left hand, right hand, feet). This is the second of four BMI-HDEEG datasets, using the same high-density setup as dataset 1 but with a three-class motor imagery design.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004446

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 237xx | long | raw | Motor imagery cue - class 1 (left hand MI) |
| `2` | 237xx | long | raw | Motor imagery cue - class 2 (right hand MI) |
| `3` | 237xx | long | raw | Motor imagery cue - class 3 (feet MI) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Normal Task 1: Motor Imagery Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`1`, `2`, `3`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Left hand motor imagery |
  | `2` | 1 | Right hand motor imagery |
  | `3` | 2 | Feet motor imagery |
- **Kernel Notes**: Numerical event codes (1-3) require kernel-level decoding to semantic MI labels (left_hand_MI, right_hand_MI, feet_MI).

## Data Quality Notes

- Numerical event codes (1-3) require kernel-level decoding to semantic MI labels
- 130-channel high-density EEG with extended epochs
- 237 files; smaller than dataset 1

