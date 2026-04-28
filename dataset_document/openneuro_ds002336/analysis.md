# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP1

**Dataset**: `openneuro_ds002336` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002336
**Category**: Action/Output | **Subjects**: 10 | **Files (Completed)**: 107 | **Channels**: 64 | **Sampling Rate**: 5000 Hz
**Manual Review**:

## Paradigm

Simultaneous EEG-fMRI acquisition during a kinesthetic motor imagery neurofeedback task. Subjects performed right-hand motor imagery or motor execution during sustained task blocks alternating with rest blocks, while receiving unimodal (EEG or fMRI) or bimodal neurofeedback. Each task block (Task-NF: neurofeedback, Task-ME: motor execution, Task-MI: motor imagery) is a sustained mental state lasting several seconds. BrainVision format with MRI artifact markers (TPULSE, R128) that must be excluded.

## File Scan Result

> **Kernel SHA256**: `473b878007298e99017272ff1692ffc0a62d4c34df8ef9b124a4757608ef8452`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 41 | admin | raw | Session/data segment start boundary marker |
| `Rest` | 880 | event | raw | Trial phase onset: rest/baseline period |
| `Stimulus/S  1` | 152 | event | raw | Stimulus marker S 1 (condition code 1) |
| `Stimulus/S  2` | 740 | event | raw | Stimulus marker S 2 (condition code 2) |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `ECG` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `ECG` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
- **Candidate Labels**: `ECG`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from Resting-State EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–39.0 (years) | Continuous age from participants.tsv; N=10 subjects |
- **Evidence**:
- **Notes**: Segmentation-based task (archetype C) using native info field `age`. The kernel segments continuous EEG into 4-second windows with 50% overlap during sustained Rest periods (20s blocks yield ~7 segments per block after edge handling). Each segment inherits the subject's age as the regression target. Limited sample size (N=10) is noted as a practical constraint for this neurodevelopmental benchmarking paradigm.

### Potential Task 2: sex classification from resting-state EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | male |
  | sex | F | 1 | female |
- **Evidence**:
  - participants.tsv — N=10 subjects with sex column (M=8, F=2), complete demographic data
  - events.tsv (task-MIpre, task-MIpost) — Rest trial phase onset with 20s duration, providing resting-state EEG segments for feature extraction
- **Notes**: Segmentation-based task using 4s non-overlapping windows from resting-state EEG blocks. The 'Rest' trial phase markers (20s duration) provide the source data segments. Classification is highly imbalanced (8:2 male:female ratio) with small sample size; this is noted as a limitation. Archetype C with native info field (sex) → Meta Level = raw.

### Potential Task 3: ECG amplitude regression from resting-state segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5, target_events = []`
- **Label Route**: `misc`
- **Label Field**: `ECG`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |---|---|---|
  | ECG | ECG amplitude (mV or arbitrary units) | Continuous ECG signal amplitude from native ECG channel; regression target extracted per 4 s segment during resting-state periods |
- **Evidence**:
  - (none — Potential task)
- **Notes**: Native ECG channel is available as a continuous misc channel in the preprocessed EEG recordings. This task segments the resting-state portions of the recording (20 s Rest blocks from MIpre/MIpost tasks, or continuous rest from NF runs) into 4-second overlapping windows and uses the ECG amplitude as a regression target. The segment_length and overlap values are inferred from the epoch hint (inferred=true) to maximize sample yield from limited rest periods. Useful for autonomic state characterization and physiological artifact modeling in simultaneous EEG-fMRI contexts. Meta Level changed to `super` because the regression target (amplitude per segment) is a derived quantity from the native ECG channel, not raw values.

## Data Quality Notes

- MRI gradient artifact contamination present; TPULSE markers indicate artifact regions.
- High sampling rate (5000 Hz); downsampling to 250-1000 Hz recommended.
- Task-ME and Task-MI blocks are sparsely present (subset of sessions only).
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
