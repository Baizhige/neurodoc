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

### Primary Task 1: Binary Motor Imagery Classification (rest vs right-hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`2`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 1 | Right-hand motor imagery (class 2) |
  | (implicit rest period between cues) | 0 | Rest baseline |
- **Evidence**:
  - DOI: `10.1038/s41597-023-02260-6` — Binary classification of rest vs motor imagery periods validated using spectral power features and random forest on this dataset
- **Kernel Notes**: Extract epochs around event code 2 (right-hand MI). The implicit rest periods between MI cues serve as class 0. Verify rest period duration from event timing. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Four-class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`1`, `2`, `3`, `4`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Left-hand motor imagery (class 1) |
  | `2` | 1 | Right-hand motor imagery (class 2) |
  | `3` | 2 | Feet motor imagery (class 3) |
  | `4` | 3 | Tongue motor imagery (class 4) |
- **Evidence**:
  - DOI: `10.1038/s41597-023-02260-6` — Dataset described as four-class MI BCI paradigm; paper validates binary but dataset supports four-class
- **Kernel Notes**: Classes 3 and 4 (feet/tongue) appear in only 91 of 418 files—use file filtering. Kernel must decode numerical codes 1-4 to semantic labels.

## Data Quality Notes

- Numerical event codes (1-4) require kernel-level decoding
- Classes 3 and 4 (feet/tongue) only appear in 91 of 418 files
- 130-channel high-density EEG with extended epochs

