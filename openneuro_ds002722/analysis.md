# A dataset recorded during development of an affective brain-computer music interface: calibration session

**Dataset**: `openneuro_ds002722` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002722
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 94 | **Channels**: 37 | **Sampling Rate**: 1000 Hz
**Manual Review**: Mingze Tang

## Paradigm

Participants listened to 40-second synthetic music clips designed to induce specific affective states (varying valence and arousal) as a calibration session for an affective brain-computer music interface (BCMI). EEG and physiological signals were recorded to build a mapping from neural/physiological features to targeted emotional states. Codes 1-9 are primary music condition labels; 100-200 range codes encode specific music clip identifiers.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9` | 94 (files) | event | raw | Music condition 9 onset (high arousalx) |
| `4` | 90 (files) | event | raw | Music condition 4 onset |
| `5` | 89 (files) | event | raw | Music condition 5 onset |
| `6` | 89 (files) | event | raw | Music condition 6 onset |
| `7` | 89 (files) | event | raw | Music condition 7 onset |
| `2` | 89 (files) | event | raw | Music condition 2 onset |
| `1` | 60 (files) | event | raw | Music condition 1 onset |
| `3` | 59 (files) | event | raw | Music condition 3 onset |
| `104`-`205` range | 19 (files each) | event | raw | Specific music clip identifiers |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Affective Music Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 40.0 s, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Music condition 1 |
  | `2` | 1 | Music condition 2 |
  | `3` | 2 | Music condition 3 |
  | `4` | 3 | Music condition 4 |
  | `5` | 4 | Music condition 5 |
  | `6` | 5 | Music condition 6 |
  | `7` | 6 | Music condition 7 |
  | `8` | 7 | Music condition 8 |
  | `9` | 8 | Music condition 9 |
- **Evidence**:
  - DOI: `10.1038/s41597-020-0507-6` — The paper describes the BCMI calibration dataset (openneuro_ds002722) containing EEG and physiological recordings from 19 participants listening to 40-second synthetic music clips with 9 different affective conditions (codes 1-9), presented during 5 runs of 18 trials each.
- **Kernel Notes**: Epoch relative to music clip onset markers. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- 30 distinct event types; codes 1-9 are the primary condition labels.
- Decode exact valence/arousal mapping for codes 1-9 from Daly et al. 2018 paper.
- 37-channel EEG includes physiological channels (ECG, GSR, etc.); identify EEG-only channels.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review