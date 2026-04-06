# A Large EEG Motor Imagery Dataset for EEG-BCI

**Dataset**: `figshare_largemi` | **Year**: 2018 | **URL**: https://figshare.com/collections/A_large_electroencephalographic_motor_imagery_dataset_for_electroencephalographic_brain_computer_interfaces/3917698
**Category**: Action/Output | **Subjects**: 13 | **Files (Completed)**: 73 | **Channels**: 22 | **Sampling Rate**: 200 or 1000 Hz (protocol-dependent)

## Paradigm

Thirteen subjects (A-M) participated in multiple EEG motor imagery sessions using five different paradigms (Kaya et al., 2018). EEG was recorded from 22 scalp channels. The paradigms are:
- **CLA**: 3-class MI - left hand, right hand, passive state.
- **HaLT**: 6-class MI - left hand, right hand, passive state, left leg, right leg, tongue.
- **FREEFORM / FREEDOM**: 2-class MI - left hand, right hand (free imagery style).
- **5F**: 5-class finger MI - thumb, index, middle, ring, and pinkie.
- **NoMT**: no-motor-task control sessions (resting state, no imagery).

Trials were cue-based with a blank screen rest period, followed by an arrow/cue presentation indicating the imagery target. Each trial lasted approximately 3 seconds of imagery. NoMT sessions serve as control recordings without motor task events.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Left hand MI` | varies by protocol | event | raw | Left-hand motor imagery cue |
| `Right hand MI` | varies by protocol | event | raw | Right-hand motor imagery cue |
| `Passive state` | varies by protocol | event | raw | Passive / idle state (CLA/HaLT) |
| `Left leg MI` | varies by protocol | event | raw | Left-leg motor imagery cue (HaLT) |
| `Right leg MI` | varies by protocol | event | raw | Right-leg motor imagery cue (HaLT) |
| `Tongue MI` | varies by protocol | event | raw | Tongue motor imagery cue (HaLT) |
| `Thumb MI` | varies by protocol | event | raw | Thumb finger imagery cue (5F) |
| `Index finger MI` | varies by protocol | event | raw | Index finger imagery cue (5F) |
| `Middle finger MI` | varies by protocol | event | raw | Middle finger imagery cue (5F) |
| `Ring finger MI` | varies by protocol | event | raw | Ring finger imagery cue (5F) |
| `Pinkie MI` | varies by protocol | event | raw | Little finger imagery cue (5F) |
| `none` | all NoMT files | admin | raw | No motor task (NoMT protocol control) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Multi-Paradigm Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.85 s *, target_events = [`Left hand MI`, `Right hand MI`, `Passive state`, `Left leg MI`, `Right leg MI`, `Tongue MI`, `Thumb MI`, `Index finger MI`, `Middle finger MI`, `Ring finger MI`, `Pinkie MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Left hand MI` | 0 | Left-hand motor imagery (marker 1) |
  | `Right hand MI` | 1 | Right-hand motor imagery (marker 2) |
  | `Passive state` | 2 | Passive/idle state (marker 3) |
  | `Left leg MI` | 3 | Left-leg motor imagery (marker 4) |
  | `Right leg MI` | 4 | Right-leg motor imagery (marker 6) |
  | `Tongue MI` | 5 | Tongue motor imagery (marker 5) |
  | `Thumb MI` | 6 | Thumb finger imagery (5F, marker 1) |
  | `Index finger MI` | 7 | Index finger imagery (5F, marker 2) |
  | `Middle finger MI` | 8 | Middle finger imagery (5F, marker 3) |
  | `Ring finger MI` | 9 | Ring finger imagery (5F, marker 4) |
  | `Pinkie MI` | 10 | Pinkie finger imagery (5F, marker 5) |
- **Super Meta Notes**: (N/A - raw meta)
- **Evidence**:
  - DOI: 10.1038/sdata.2018.211 — Validates dataset with SVM classification using 0.85s epochs from stimulus onset, supporting multi-class MI across CLA (3-class), HaLT (6-class), and 5F (5-class finger) paradigms
  - DOI: 10.1109/tnsre.2022.3186442 — Uses figshare_largemi for binary left vs right hand MI classification with 3-second epochs
- **Kernel Notes**: Filter data by protocol type (CLA/HaLT/5F/FREEFORM) before analysis. Select relevant target_events subset per paradigm. The 0.85s epoch aligns with original dataset validation; 3.0s may also be used per newer papers.

### Classical Task 2: Binary Left vs. Right Hand Motor Imagery
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = [`Left hand MI`, `Right hand MI`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Left hand MI` | 0 | Left-hand motor imagery |
  | `Right hand MI` | 1 | Right-hand motor imagery |
- **Evidence**:
  - DOI: 10.1109/tnsre.2022.3186442 — Binary classification of left vs right hand motor imagery using 3-second epoch window
- **Kernel Notes**: Use CLA or FREEFORM protocol files. Exclude passive/other class events. (replaces Potential Task 1 from original analysis.md)

### Potential Task 2: 6-Class Motor Imagery Classification - HaLT (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Left hand MI` | 0 | Left-hand MI |
| `Right hand MI` | 1 | Right-hand MI |
| `Passive state` | 2 | Passive/idle state |
| `Left leg MI` | 3 | Left-leg MI |
| `Right leg MI` | 4 | Right-leg MI |
| `Tongue MI` | 5 | Tongue MI |

### Potential Task 3: 5-Finger Motor Imagery Classification - 5F (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 3.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `Thumb MI` | 0 | Thumb finger MI |
| `Index finger MI` | 1 | Index finger MI |
| `Middle finger MI` | 2 | Middle finger MI |
| `Ring finger MI` | 3 | Ring finger MI |
| `Pinkie MI` | 4 | Little finger MI |

### Potential Task 4: Resting-State Segmentation - NoMT Control (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 3.0 s, overlap = 0.5 s
- **Label Route**: `event`
- **Target Definition**: N/A (no events; use as unlabeled or negative class)
- **Notes**: NoMT files have event annotation `none` set by kernel; use `epoch_by_segmentation_hdf5` for these files.

## Data Quality Notes

- Multiple paradigms in one dataset; **always filter by protocol type before analysis** (use file path to identify protocol: `CLA`, `HaLT`, `FREEFORM`, `5F`, `NoMT`).
- Sampling rates differ: 200 Hz (5F protocol), 1000 Hz (CLA/HaLT/FREEFORM); process separately or resample to a common rate.
- Subject demographics: 13 subjects (A-M), 9 female / 4 male, age ranges 20-35.
- NoMT sessions have `none` annotations; exclude from MI analysis or use as rest class.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review