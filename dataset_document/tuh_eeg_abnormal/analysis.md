# TUH EEG Abnormal Corpus

**Dataset**: `tuh_eeg_abnormal` | **Year**: 2016-2017/2024 | **URL**: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
**Category**: Biological State | **Subjects**: 2383 | **Files (Completed)**: 2983 | **Channels**: 27-36 | **Sampling Rate**: 250 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The TUH EEG Abnormal Corpus (v3.0.1) is a clinically annotated subset of the TUH EEG Corpus where each recording has been classified as **normal** or **abnormal** by board-certified neurologists. Recordings are routine clinical EEG sessions acquired in an outpatient setting at Temple University Hospital. The normal/abnormal label reflects the overall clinical impression of the EEG recording, not individual event annotations. The label is encoded in the directory path (`normal/` or `abnormal/`) and extracted by the kernel to create a single whole-recording annotation.

## File Scan Result

> **Kernel SHA256**: `644d71b532db95d6bc8a1e80722382dbac84ca6c834951df359825f61b56f3d3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `abnormal` | 1466 | event | raw | Whole-recording label: clinically abnormal EEG finding |
| `normal` | 1517 | event | raw | Whole-recording label: clinically normal EEG finding |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Normal vs Abnormal EEG Recording Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 10 s, overlap = 0.0, target_events = [`abnormal`, `normal`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `normal` | 0 | Normal EEG recording |
  | `abnormal` | 1 | Abnormal EEG recording |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119521 — Uses 10-second non-overlapping epochs on TUAB dataset (resting-state EEG recordings with normal/abnormal labels) with 10-fold cross-validation, establishing standard epoching parameters for this dataset.
- **Notes**: 

## Data Quality Notes

- Variable channel count (27-36) across recordings; normalize before cross-recording analysis if needed.
- Train/dev split is encoded in directory path; respect the split for proper evaluation.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
