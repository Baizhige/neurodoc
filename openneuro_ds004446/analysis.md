# The BMI-HDEEG dataset 2

**Dataset**: `openneuro_ds004446` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004446
**Category**: Action/Output | **Subjects**: 237 | **Files (Completed)**: 237
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

A high-density EEG dataset focused on sensorimotor rhythm-based brain-computer interfacing (BCI) with three motor imagery classes (left hand, right hand, feet). This is the second of four BMI-HDEEG datasets, using the same high-density setup as dataset 1 but with a three-class motor imagery design.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 237xx | event | raw | Motor imagery cue - class 1 (left hand MI) |
| `2` | 237xx | event | raw | Motor imagery cue - class 2 (right hand MI) |
| `3` | 237xx | event | raw | Motor imagery cue - class 3 (feet MI) |


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
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`1`, `2`, `3`]
- **Label Route**: `event`
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


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review