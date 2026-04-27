# TUH EEG Slowing Corpus

**Dataset**: `tuh_eeg_slowing` | **Year**: 2017 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg
**Category**: Biological State | **Subjects**: 38 | **Files (Completed)**: 112 | **Channels**: 27-41 | **Sampling Rate**: 250/256/400/512 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

The TUH EEG Slowing Corpus is a subset of the TUH EEG Corpus, designed to aid in the development of algorithms that can differentiate between seizure and slowing events in EEG data. The dataset includes sessions with seizure events, slowing events, and complex background events. It contains 300 files, divided into 3 main categories: complex background, seizure, and slowing.

The corpus features EEG data in the European Data Format (EDF), along with annotated files in both term-based and event-based formats. Term-based annotations provide labels for 10-second segments, making them useful for machine learning tasks that focus on overall classification rather than individual channels. Event-based annotations include detailed timings and channel indices, representing the onset and duration of events across different channels.

Clinical EEGs in the dataset utilize two common reference configurations: averaged reference (AR) and linked ears reference (LE), in line with the 10/20 electrode system. A total of 38 patients contributed to the dataset across 75 sessions.

## File Scan Result

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `seiz` | varies | event | raw | Seizure activity |
| `slow` | varies | event | raw | EEG slowing (pathological slow-wave activity) |
| `bckg` | varies | event | raw | Background - normal EEG |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Potential Task 1: EEG Slowing Detection (2-Class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`slow`, `bckg`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `bckg` | 0 | Normal background EEG |
  | `slow` | 1 | EEG slowing (pathological slow-wave activity) |
- **Evidence**:

- **Notes**: 

### Potential Task 2: 3-Class EEG State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 1 s, overlap = 0.0, target_events = [`seiz`, `slow`, `bckg`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `bckg` | 0 | Normal background EEG |
  | `slow` | 1 | EEG slowing |
  | `seiz` | 2 | Seizure activity |
- **Evidence**:

- **Notes**: 

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
