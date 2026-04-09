# Sleep-EDF Database Expanded

**Dataset**: `physionet_sleepedfx` | **Year**: 1987-1991/1994 | **URL**: https://physionet.org/content/sleep-edfx/1.0.0/
**Category**: Biological State | **Subjects**: 106 | **Files (Completed)**: 197 | **Channels**: 7 | **Sampling Rate**: 100 Hz
**Manual Review**: Chengxuan Qin

## Paradigm

The sleep-edf database contains 197 whole-night PolySomnoGraphic sleep recordings, containing EEG, EOG, chin EMG, and event markers. Some records also contain respiration and body temperature. Corresponding hypnograms (sleep patterns) were manually scored by well-trained technicians according to the Rechtschaffen and Kales manual, and are also available.

## File Scan Result

> **Kernel SHA256**: `db96b3badc0af51588705980412f7ed0016ef5345e218e37bd3d1fd192911aad`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Movement time` | 196 | event | raw | Subject movement marker; out-of-bed period during recording |
| `Sleep stage 1` | 7292 | event | raw | Sleep stage 1 (light sleep) epoch annotation |
| `Sleep stage 2` | 8171 | event | raw | Sleep stage 2 (light sleep) epoch annotation |
| `Sleep stage 3` | 4820 | event | raw | Sleep stage 3 (slow wave sleep) epoch annotation |
| `Sleep stage 4` | 1462 | event | raw | Sleep stage 4 (deep slow wave sleep) epoch annotation |
| `Sleep stage ?` | 173 | event | raw | Unscored or ambiguous epoch; annotation uncertain |
| `Sleep stage R` | 1953 | event | raw | Sleep stage R (REM sleep) epoch annotation |
| `Sleep stage W` | 4461 | event | raw | Sleep stage W (wakefulness) epoch annotation |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Classical Task 1: Sleep stage classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage R`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | NREM Stage 1 |
  | `Sleep stage 2` | 2 | NREM Stage 2 |
  | `Sleep stage 3` | 3 | NREM Stage 3 (includes S3+S4 merged per AASM) |
  | `Sleep stage 4` | 3 | NREM Stage 3 (mapped to y=3; S3 and S4 merged) |
  | `Sleep stage R` | 4 | REM |
- **Evidence**:
  - 10.7717/peerjcs.1561_table — 2 — Five-class sleep staging (W, N1, N2, N3, REM) on Sleep-EDF Expanded, 30-second epochs, AASM standard merging S3+S4 into N3
- **Kernel Notes**: 

### Potential Task 1: Wake vs. Sleep Binary Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 30.0 s, overlap = 0.0, target_events = [`Sleep stage W`, `Sleep stage 1`, `Sleep stage 2`, `Sleep stage 3`, `Sleep stage 4`, `Sleep stage R`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage 1` | 1 | Any sleep (stages 1-4 and R) |
  | `Sleep stage 2` | 1 | Any sleep |
  | `Sleep stage 3` | 1 | Any sleep |
  | `Sleep stage 4` | 1 | Any sleep |
  | `Sleep stage R` | 1 | Any sleep |
- **Evidence**:
  - **Kernel Notes**:
- **Kernel Notes**: **Kernel Notes**:

## Data Quality Notes

- Only PSG files should be processed; Hypnogram files (matched companion files) are used for annotation only and are returned unchanged by the kernel.
- Class imbalance: Stage 2 is the most frequent stage; Wake also contributes large counts from lights-on periods at start/end of recording.
- Two EEG channels only (Fpz-Cz, Pz-Oz); limited spatial resolution.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
