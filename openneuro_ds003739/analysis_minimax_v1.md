# Perturbed beam-walking task

**Dataset**: `openneuro_ds003739` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003739
**Category**: Complex Applied | **Subjects**: N/A | **Files (Completed)**: 120
**Channels**: 149.0 | **Sampling Rate**: 256.0 Hz

## Paradigm

Participants performed walking on a treadmill-mounted balance beam while being subjected to sensorimotor perturbations via virtual reality visual rotations and physical waist pulls.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003739

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## Tasks

### Primary Task 1: Perturbation Type Classification (Posture + Perturbation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s, tmax = 2 s, target_events = [`pull_stand_left`, `pull_stand_right`, `pull_walk_left`, `pull_walk_right`, `rotate_stand_cw`, `rotate_stand_ccw`, `rotate_walk_cw`, `rotate_walk_ccw`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `pull_stand_left` | 0 | Physical waist pull, standing, left direction |
  | `pull_stand_right` | 1 | Physical waist pull, standing, right direction |
  | `pull_walk_left` | 2 | Physical waist pull, walking, left direction |
  | `pull_walk_right` | 3 | Physical waist pull, walking, right direction |
  | `rotate_stand_cw` | 4 | Visual rotation, standing, clockwise |
  | `rotate_stand_ccw` | 5 | Visual rotation, standing, counter-clockwise |
  | `rotate_walk_cw` | 6 | Visual rotation, walking, clockwise |
  | `rotate_walk_ccw` | 7 | Visual rotation, walking, counter-clockwise |
- **Evidence**:
  - DOI: 10.1016/j.dib.2021.107635 — Data in Brief paper describing and publicly releasing the openneuro_ds003739 dataset with 150 perturbation events per 10-minute session and event timing, type, and direction recorded in _events.tsv files.
- **Kernel Notes**: Extract 8-class labels from event markers in _events.tsv files; epoch around perturbation onset with tmin=-1s, tmax=2s (2s epochs as reported in source-localized analysis). Use raw meta level as labels are directly available from event markers.

### Primary Task 2: Posture-Perturbation Condition Classification (Super Meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1 s *, tmax = 2 s *, target_events = [`stand_pull`, `walk_pull`, `stand_rotate`, `walk_rotate`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stand_pull` | 0 | Standing + physical waist pull |
  | `walk_pull` | 1 | Walking + physical waist pull |
  | `stand_rotate` | 2 | Standing + visual rotation |
  | `walk_rotate` | 3 | Walking + visual rotation |
- **Super Meta Notes**: Labels derived from experimental condition (task type: walking vs standing + perturbation type: pull vs rotation), not from raw event markers. Combines posture and perturbation type into 4 discrete classes.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2019.05.038 — Source-localized EEG connectivity analysis during four conditions: walking/standing with visual rotations or physical waist pulls, epoched from -1 to 2s around perturbation onset.
- **Kernel Notes**: Derive 4-class super-meta labels by combining posture (standing/walking) and perturbation type (pull/rotation) from experimental design metadata; route to `misc` channel.

### Normal Task 1: Raw-meta task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Needs verification

- **Kernel Notes**: Exclude admin markers from target labels.

### Normal Task 2: Super-meta task
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target / Label**: Needs verification
- **Kernel Notes**: Derive and version super-meta in kernel.

## Data Quality Notes

- Verify channel count consistency across subjects before pooling.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `eNeuro publication`
