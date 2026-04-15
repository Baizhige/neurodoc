# The BMI-HDEEG dataset 2

**Dataset**: `openneuro_ds004446` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004446
**Category**: Action/Output | **Subjects**: 237 | **Files (Completed)**: 237 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A high-density EEG dataset focused on sensorimotor rhythm-based brain-computer interfacing (BCI) with three motor imagery classes (left hand, right hand, feet). This is the second of four BMI-HDEEG datasets, using the same high-density setup as dataset 1 but with a three-class motor imagery design.

## File Scan Result

> **Kernel SHA256**: `ae57d29f77257fab6c377381c8a6cd425f89a7d778d05419241dd6102b20231d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 6782 | event | raw | Motor imagery cue - class 1 (left hand MI) |
| `event_2` | 5633 | event | raw | Motor imagery cue - class 2 (right hand MI) |
| `event_3` | 4020 | event | raw | Motor imagery cue - class 3 (feet MI) |
| `event_4` | 5487 | event | raw | Fixation/rest marker |
| `event_5` | 1258 | event | raw | Rest marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Three-Class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`1`, `2`, `3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `1` | 0 | Left hand motor imagery |
  | `2` | 1 | Right hand motor imagery |
  | `3` | 2 | Feet motor imagery |
- **Evidence**: DOI: 10.1038/s41597-023-02260-6
- **Kernel Notes**: Alignment assumption: event markers represent cue ONSET (standard BCI2000-style paradigm). tmin=-0.5s captures pre-stimulus baseline for baseline correction; tmax=4.0s covers the full 4-second imagery window. Events 4 and 5 exist in raw data but are NOT part of the three MI classes—likely fixation/rest markers to be excluded. High-density 130-channel setup with 237 subjects may require memory-efficient epoching. Numerical event codes (1-3) require kernel-level decoding to semantic MI labels.

### Potential Task 2: Binary Motor Imagery Classification (Left vs Right Hand)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `1` | 0 | Left hand motor imagery |
  | `2` | 1 | Right hand motor imagery |
- **Evidence**: Plausible from paradigm; left/right hand discrimination is a standard binary MI task.
- **Kernel Notes**: Binary subset of the three-class paradigm. Events 3 (feet MI) excluded. Same alignment and epoch parameters as Normal Task 1.

### Potential Task 3: Binary Motor Imagery Classification (Hand vs Feet)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`1`, `2`, `3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `1` | 0 | Hand motor imagery (left or right) |
  | `2` | 0 | Hand motor imagery (left or right) |
  | `3` | 1 | Feet motor imagery |
- **Evidence**: Plausible from paradigm; hand vs feet is a standard binary MI subset.
- **Kernel Notes**: Binary classification pooling left and right hand into a single class. Requires event grouping during label assignment. Same epoch window as Normal Task 1.

### Potential Task 4: Individual Alpha Frequency (IAF) Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 2.0 s (suggested window for resting-state alpha analysis)
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `4` | continuous | Resting-state alpha frequency |
  | `5` | continuous | Resting-state alpha frequency |
- **Evidence**: DOI: 10.1109/TNSRE.2024.3365197
- **Kernel Notes**: Events 4 and 5 require investigation—they appear to be fixation/rest markers based on event distribution. If confirmed as resting-state segments, they can be used for IAF extraction. Paper uses this dataset collection for IAF analysis, but the exact event IDs for their resting-state segments need verification. Alternatively, pre-trial baseline periods could be used for IAF estimation.