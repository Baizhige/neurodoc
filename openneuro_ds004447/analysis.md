# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 418 | **Files (Completed)**: 418
**Channels**: 130 | **Sampling Rate**: 1000 Hz

## Paradigm

A brain-computer interface (BCI) task based on sensorimotor rhythms (SMR) recorded with high-density scalp EEG. Subjects performed motor imagery of four limb movements (left hand, right hand, feet, tongue) following visual cues. This is the third of four BMI-HDEEG datasets with a four-class design, though tongue and feet classes appear in fewer files.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 418xx | event | raw | Motor imagery cue - class 1 (left hand MI) |
| `2` | 418xx | event | raw | Motor imagery cue - class 2 (right hand MI) |
| `3` | 91xx | event | raw | Motor imagery cue - class 3 (feet MI) |
| `4` | 91xx | event | raw | Motor imagery cue - class 4 (tongue MI) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Binary Motor Imagery Classification (rest vs right-hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `2` | 1 | Right-hand motor imagery (class 2) |
  | (implicit rest period between cues) | 0 | Rest baseline |
- **Evidence**:
  - DOI: `10.1038/s41597-023-02260-6` — Binary classification of rest vs motor imagery periods validated using spectral power features and random forest on this dataset
- **Kernel Notes**: Extract epochs around event code 2 (right-hand MI). The implicit rest periods between MI cues serve as class 0. Verify rest period duration from event timing. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Four-class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`1`, `2`, `3`, `4`]
- **Label Route**: `event`
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


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review