# Blink-Pause-Relation (Competing Speaker Paradigm)

**Dataset**: `openneuro_ds004369` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004369
**Category**: High-level Mental | **Subjects**: 41 | **Files (Completed)**: 41
**Channels**: 7 | **Sampling Rate**: 500 Hz

## Paradigm

A two-competing speaker paradigm where participants selectively attended to one of two concurrently presented audiobooks while ignoring the other. EEG was recorded to study the relationship between eye blinks and speech pauses during continuous auditory attention. No trial-level event markers are present in the EEG files.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Publisher-defined BIDS task: Attended Speaker Paradigm
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004369 DOI: 10.18112/openneuro.ds004369.v1.0.1


### Potential Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: No trial markers in EEG files; use sliding window segmentation. Only 7 channels (very low-density). Subject-level labels (attended speaker, blink/pause occurrence) may be available from behavioral logs.

## Data Quality Notes

- Very sparse channel setup (7 channels only)
- No trial-level event markers in the EEG files
- Continuous naturalistic listening paradigm (audiobook)


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: failed

---

> **auto_eeg FAILED**: No relevant or partial references exist in the extraction set (all are irrelevant/junk/uncertain), and while this is an OpenNeuro dataset with a described paradigm, the dataset explicitly lacks trial-level event markers and has no identifiable label structure in the EEG files. The analysis notes continuous segmentation as an unsupervised approach, but without events or external labels, no concrete supervised ML task can be defined.
