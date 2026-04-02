# Social Memory cuing

**Dataset**: `openneuro_ds003702` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds003702
**Category**: Complex Applied | **Subjects**: N/A | **Files (Completed)**: 47
**Channels**: 64.0 | **Sampling Rate**: 500.0 Hz

## Paradigm

A visual working memory task performed in a virtual reality environment where participants recalled object locations and statuses following social (avatar) or non-social (stick) directional cues.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003702

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

### Primary Task 1: Social vs Non-Social Cue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 1.0 s, target_events = [`cue_onset`, `object_presentation`, `location_probe`, `status_probe`, `response`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `social` | 0 | Avatar cue (PeopleAll/PeopleCong/PeopleIncong) |
  | `non-social` | 1 | Stick cue (StickAll/StickCong/StickIncong) |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.107827 — Data in Brief paper describes epoching EEG from 1s pre-cue to 1s post-probe response for two-class classification of social (avatar) vs non-social (stick) cuing conditions in the VR working memory task.
- **Kernel Notes**: Merge behavioral response accuracy (correct/incorrect) with EEG epochs to enable accuracy-based analysis if needed; separate cue-locked vs probe-locked epochs based on event timing.

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

- _No paper reference available_
