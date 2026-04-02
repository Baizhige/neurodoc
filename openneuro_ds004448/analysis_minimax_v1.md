# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 280 | **Files (Completed)**: 280
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed a sensorimotor rhythm-based brain-computer interface task using high-density scalp EEG. This is the fourth BMI-HDEEG dataset with a two-class (binary) motor imagery design (left hand vs. right hand). Only one event code is present in the data, suggesting the class label is encoded differently.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004448

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 280xx | long | raw | Motor imagery cue - class 1 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Motor imagery decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 6.0 s, overlap = 0.0, target_events = [`motor_imagery`, `relaxation`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `relaxation` | 0 | Relaxation/Rest period (reference) |
  | `motor_imagery` | 1 | Right-hand motor imagery (positive class) |
- **Evidence**:
  - DOI: `10.1038/s41597.023.02260.6` — This paper describes and provides the BMI-HDEEG dataset 4 (OpenNeuro ds004448) consisting of high-density EEG recordings during SMR-based BCI neurofeedback training where participants performed right-hand motor imagery vs relaxation, and validates it with binary classification of spectral power features to decode resting vs imagery periods.
- **Kernel Notes**: Use epoch_by_long_event_hdf5 to extract sustained periods of motor imagery (6-9s) and relaxation (5-9s) from the data. Apply binary classification: motor imagery periods labeled as class 1, relaxation periods as class 0. The kernel should extract spectral power features (e.g., mu/beta band) from the epoched data for classification.

### Normal Task 1: Motor Imagery Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Only one numerical code (1) visible in locator_meta; actual binary class label likely encoded in events.tsv metadata columns or file-level metadata. Specific kernel required.

| Event | y | Meaning |
 |-------|---|------|
 | `left_hand_MI` | 0 | Left hand motor imagery |
 | `right_hand_MI` | 1 | Right hand motor imagery |

## Data Quality Notes

- Only one event code in metadata; class label may be in events.tsv columns rather than trial_type
- 130-channel high-density EEG with extended epochs
- 280 files; binary MI design

## References

- **Reference**: `High-density scalp electroencephalogram dataset during sensorimotor rhythm-based brain-computer interfacing. Sci Data 10, 385 (2023)`
