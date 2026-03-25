# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 418 | **Files (Completed)**: 418
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

A brain-computer interface (BCI) task based on sensorimotor rhythms (SMR) recorded with high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the third of four BMI-HDEEG datasets with a four-class design, though tongue and feet classes appear in fewer files.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004447

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 418xx | long | raw | Motor imagery cue - class 1 (left hand MI) |
| `2` | 418xx | long | raw | Motor imagery cue - class 2 (right hand MI) |
| `3` | 91xx | long | raw | Motor imagery cue - class 3 (feet MI) |
| `4` | 91xx | long | raw | Motor imagery cue - class 4 (tongue MI) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`rest`, `motor_imagery`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `rest` | 0 | Rest period |
  | `motor_imagery` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1038/s41597.023.02260.6 — This paper describes the BMI-HDEEG dataset 3 (OpenNeuro ds004447) and validates it by performing binary classification of rest vs motor imagery periods using spectral power-based features and random forest algorithms.
- **Kernel Notes**: Epoch window tmin=-0.5s to tmax=4.0s relative to event onset aligns with dataset paradigm (rest period 5-9s, imagery period 6-9s). Use event codes: 2 (right-hand MI) as motor_imagery, and inter-trial rest periods as rest class.


### Normal Task 1: Motor Imagery Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numerical codes 1-4 decoded by specific kernel. Classes 3 and 4 appear in only 91 of 418 files (subset of subjects). Binary left/right classification is the most balanced sub-task.

| Event | y | Meaning |
 |-------|---|------|
 | `left_hand_MI` | 0 | Left hand motor imagery |
 | `right_hand_MI` | 1 | Right hand motor imagery |
 | `feet_MI` | 2 | Feet motor imagery |
 | `tongue_MI` | 3 | Tongue motor imagery |

## Data Quality Notes

- Numerical event codes (1-4) require kernel-level decoding
- Classes 3 and 4 (feet/tongue) only appear in 91 of 418 files
- 130-channel high-density EEG with extended epochs

## References

- **Reference**: `High-density scalp electroencephalogram dataset during sensorimotor rhythm-based brain-computer interfacing. Sci Data 10, 385 (2023).`
