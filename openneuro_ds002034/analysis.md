# Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task

**Dataset**: `openneuro_ds002034` | **Year**: 2019/2022 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 167 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Liu Peng

## Paradigm

Participants performed a covert spatial attention task where they were trained to lateralize their alpha-band EEG power using real-time neurofeedback. The study evaluated whether closed-loop neurofeedback of alpha lateralization improves behavioral performance in a spatial attention paradigm. No trial-level event markers are stored in the BIDS EEG files; the task condition is reflected continuously in the EEG signal itself.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `*(none)*` | - | event | raw | No event markers detected in EEG files; continuous neurofeedback paradigm |


> This dataset consists of continuous EEG recordings without native event markers. All trial-level experimental events (including cues, attention phases, feedback conditions, and the three-day experimental procedure) must be extracted from the experimental protocol document and the paper. For details of the complete protocol, experimental design, feedback logic and recording parameters, please refer to the main text of the paper, Figures 1a–d, Supplementary Table S1 and the Methods section. Maybe we set super meta long, which belongs to epoch_by_long_event_hdf5, and rest for epoch_by_segmentation_hdf5.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Range from 21-27 y, Mean age = 23 y |
| `subject_sex` | missing | 7 female, 7 male (sex distribution fully reported in the manuscript) |
| `device` | missing | EEG recording: g.tec HIamp 64-channel active EEG amplifier (512 Hz sampling rate, linked ears reference, 10-10 international electrode system, ground at FCz); Eye tracking: SR Research EyeLink 1000 optical eye tracker (500 Hz sampling rate); Stimulus display: 24" LCD monitor (50 cm fixed viewing distance) |


## Tasks

### Classical Task 1: Covert Visuospatial Attention Decoding (Left vs Right Hemifield)
- **Task Type**: classification

- **Epoch Method**: `epoch_by_long_event_hdf5`

- **Epoch Parameters**: tmin = 0 s, tmax = 5.0 s, overlap = 0.0, target_events = [`left_cue`, `right_cue`]

- **Label Route**: `event`

- **Meta Level**: super

- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_cue` | 0 | Attend to left hemifield (left half-circle cue, excluding invalid cue trials) |
  | `right_cue` | 1 | Attend to right hemifield (right half-circle cue, excluding invalid cue trials) |
  
- **Evidence**:
  
  - DOI: 10.1007/s10548 — 019-00725-9 — Post-hoc single-trial binary classification to decode attended side (left vs right) from alpha-band EEG lateralization features using LDA classifiers with 10-fold cross-validation.
  
- **Kernel Notes**: 

  1. Label Derivation: `left_cue/right_cue` are super meta labels derived from raw cue events (left/right half-circle cues). Exclude central fixation (full-circle cue) trials and invalid cue trials from this task. 
  2. Epoch Window Rationale: 0-5s window is selected based on the offline trial sustained attention period (1-5s), which is the calibration basis for the real-time decoder; online trials are included with their early 5s window to maintain consistency. Overlap=0 to prevent cross-trial data leakage. 
  3. Classification Rationale: Follows the paper's post-hoc single-trial decoding approach, using LDA classifier with 10-fold cross-validation on alpha-band (8-13Hz) lateralization features at PO7/PO8 electrodes.

### Classical Task 2: Alpha Lateralization Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 5.0 s, overlap = 0.9375
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `Channel Name：α-LI；Meaning：y = continuous alpha-band lateralization index (alpha-LI) values, derived from PO7/PO8 EEG alpha-band (8–13Hz) power during sustained attention phases (offline: 1–5s, online: 2–20s)`
- **Evidence**:
  - DOI: 10.1007/s10548 — 019-00725-9 — Real-time neurofeedback study on alpha-band lateralization; dataset includes continuous alpha-LI values during feedback runs.
- **Kernel Notes**: 
  1. Label Derivation: `alpha_LI` is a super meta continuous channel, derived from raw EEG data (PO7/PO8 electrodes, alpha-band 8–13Hz power) during sustained attention phases, per the paper's real-time neurofeedback protocol. 
  2. Epoch Parameter Rationale: 0–5s window is selected based on offline trial sustained attention period (1–5s, calibration basis for real-time decoder); high overlap (93.75%, step size=0.3125s) generates temporally dense samples for continuous regression of alpha-LI.  
  3. Task Rationale: Regression task to predict continuous alpha-band lateralization index (alpha-LI) from EEG features, consistent with the paper's real-time neurofeedback study on alpha lateralization. 
  4. Exclusion Criteria: Exclude central fixation trials, invalid cue trials, and non-feedback runs from this task.

### Potential Task 1: Continuous Segmentation (Task-State, for Self-Supervised Preprocessing)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `Channel Name: continuous_segment；Meaning: Unlabeled continuous EEG segments from task-state recordings`
- **Evidence**:
  - DOI: DOI: **Kernel Notes**: — —
- **Kernel Notes**: 
  1. Task Rationale: Potential task for continuous segmentation of task-state EEG recordings (no dedicated resting-state data in this dataset), designed for self-supervised pre-training or unsupervised feature learning. 
  2. Epoch Parameter Rationale: 2-second window with 50% overlap is a standard configuration for continuous EEG analysis, balancing temporal resolution and sample density. 
  3. Label Derivation: Continuous segments are super meta derived from raw long task-state recordings; no raw resting-state labels exist in the dataset. 
  4. Exclusion Criteria: Exclude invalid cue trials, central fixation trials, and artifact-contaminated segments.

## Data Quality Notes

- No trial-level event markers detected in any EEG files; only continuous recordings available.
- Real-time neurofeedback paradigm - EEG signal itself contains the task-relevant information.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
