# Perturbed beam-walking task

**Dataset**: `openneuro_ds003739` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003739
**Category**: Complex Applied | **Subjects**: N/A | **Files (Completed)**: 120
**Channels**: 149.0 | **Sampling Rate**: 256.0 Hz

## Paradigm

Participants performed walking on a treadmill-mounted balance beam while being subjected to sensorimotor perturbations via virtual reality visual rotations and physical waist pulls.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Perturbation Type and Posture Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 2.0 s *, target_events = [`stand_pull`, `walk_pull`, `stand_rotate`, `walk_rotate`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stand_pull` | 0 | Physical waist pull while standing |
  | `walk_pull` | 1 | Physical waist pull while walking |
  | `stand_rotate` | 2 | Visual field rotation while standing |
  | `walk_rotate` | 3 | Visual field rotation while walking |
- **Super Meta Notes**: Derived from experimental condition (posture: standing/walking + perturbation type: pull/rotation). Kernel must combine posture and perturbation type from _events.tsv to generate 4-class labels.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.05.038 — Source-localized EEG connectivity analysis during four conditions: walking/standing with visual rotations or physical waist pulls, epoched from -1 to 2s around perturbation onset.
  - DOI: 10.1016/j.dib.2021.107635 — Dataset with 150 perturbation events per 10-minute session (75 per direction), pull duration=1s, rotation duration=0.5s.
- **Kernel Notes**: Load _events.tsv to extract perturbation type and posture condition. Epoch EEG around perturbation onset (±1s pre, 2s post). Apply bandpass filter (0.5-40 Hz). (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Perturbation Type, Posture, and Direction Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 2.0 s *, target_events = [`pull_stand_left`, `pull_stand_right`, `pull_walk_left`, `pull_walk_right`, `rotate_stand_cw`, `rotate_stand_ccw`, `rotate_walk_cw`, `rotate_walk_ccw`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `pull_stand_left` | 0 | Waist pull to left while standing |
  | `pull_stand_right` | 1 | Waist pull to right while standing |
  | `pull_walk_left` | 2 | Waist pull to left while walking |
  | `pull_walk_right` | 3 | Waist pull to right while walking |
  | `rotate_stand_cw` | 4 | Visual rotation clockwise while standing |
  | `rotate_stand_ccw` | 5 | Visual rotation counter-clockwise while standing |
  | `rotate_walk_cw` | 6 | Visual rotation clockwise while walking |
  | `rotate_walk_ccw` | 7 | Visual rotation counter-clockwise while walking |
- **Super Meta Notes**: Derived from raw event markers in _events.tsv combining perturbation type (pull/rotate) + posture (stand/walk) + direction (left/right or cw/ccw). Kernel must combine all three factors to generate 8-class labels.
- **Evidence**:
  - DOI: 10.1016/j.dib.2021.107635 — 150 perturbation events per session (75 per direction), pull duration=1s, rotation duration=0.5s, epoch around perturbation onset.
- **Kernel Notes**: Load _events.tsv to extract perturbation type, posture, and direction. Epoch EEG around perturbation onset (±1s pre, 2s post). Apply bandpass filter (0.5-40 Hz). Verify event ID mapping from events.tsv.

### Potential Task 1: Raw-meta task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Needs verification

- **Kernel Notes**: Exclude admin markers from target labels.

### Potential Task 2: Super-meta task
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target / Label**: Needs verification
- **Kernel Notes**: Derive and version super-meta in kernel.

## Data Quality Notes

- Verify channel count consistency across subjects before pooling.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review