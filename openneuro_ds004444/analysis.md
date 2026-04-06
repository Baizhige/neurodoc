# The BMI-HDEEG dataset 1

**Dataset**: `openneuro_ds004444` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004444
**Category**: Action/Output | **Subjects**: 465 | **Files (Completed)**: 465
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

Brain-computer interfacing task based on sensorimotor rhythms (SMR) using high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the first of four BMI-HDEEG datasets, enabling classification of motor imagery across all four classes.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 465xx | event | raw | Motor imagery cue - class 1 (left hand MI) |
| `2` | 465xx | event | raw | Motor imagery cue - class 2 (right hand MI) |
| `3` | 465xx | event | raw | Motor imagery cue - class 3 (feet MI) |
| `4` | 465xx | event | raw | Motor imagery cue - class 4 (tongue MI) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Motor Imagery Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
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


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review