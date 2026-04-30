# A multi-modal human neuroimaging dataset for data integration: simultaneous EEG and fMRI acquisition during a motor imagery neurofeedback task: XP2

**Dataset**: `openneuro_ds002338` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002338
**Category**: Action/Output | **Subjects**: 23 | **Files (Completed)**: 169 | **Channels**: 64 | **Sampling Rate**: 5000 Hz | **Manual Review**:

## Paradigm

Participants performed right-hand motor imagery and received neurofeedback (1D or 2D display) during simultaneous EEG-fMRI acquisition to learn to regulate sensorimotor rhythms. The task alternated between sustained Rest blocks and Task-NF (neurofeedback) blocks, each lasting 20 seconds. MRI gradient artifacts are marked with TPULSE markers which must be excluded during analysis. This is XP2 of a two-experiment series; XP1 is ds002336.

## File Scan Result

> **Kernel SHA256**: `cd54d7617a2e8b3df74b6743f9932df8d71d1fe12f1b9bf4fc72c7e6b72987a8`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 82 | admin | raw | Recording segment boundary onset |
| `Pulse Artifact/R` | 29958 | admin | raw | MRI pulse artifact marker (channel 32) |
| `Response/R128` | 54845 | event | raw | Response marker |
| `Stimulus/S  2` | 1350 | event | raw | Trial phase onset: task block or condition transition |
| `Stimulus/S 35` | 10 | event | raw | Stimulus marker (specific function unclear from available evidence) |
| `Stimulus/S 99` | 1354 | event | raw | Trial phase onset: initial baseline or recording start marker |
| `Stimulus/S101` | 95 | event | raw | Stimulus marker (specific function unclear from available evidence) |
| `TPULSE/TEND` | 83 | admin | raw | Pulse timing marker: pulse end |
| `TPULSE/TPEAK` | 83 | admin | raw | Pulse timing marker: pulse peak |
| `TPULSE/TSTART` | 83 | admin | raw | Pulse timing marker: pulse start |
| `Time 0/` | 82 | admin | raw | Recording time zero reference marker |


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

### Classical Task 1: Rest vs Motor Imagery Neurofeedback Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Stimulus/S 99`, `Stimulus/S  2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 99` | 0 | Rest phase onset |
  | `Stimulus/S  2` | 1 | Task-NF phase onset (motor imagery neurofeedback) |
- **Evidence**:
  - 10.1101/862375 — Primary data descriptor; describes 20-second alternating Rest and Task-NF blocks for motor imagery neurofeedback with simultaneous EEG-fMRI
  - 10.1038/s41597-020-0498-3 — Published data descriptor confirming task structure: Rest blocks alternate with Task-NF (1D or 2D neurofeedback) blocks, each 20 seconds duration
  - 10.1101/397729 — Original study paper describing the EEG-fMRI neurofeedback paradigm with sustained 20-second rest and motor imagery neurofeedback phases
- **Notes**: Event IDs `Stimulus/S 99` and `Stimulus/S  2` are trial phase onset markers (not MI class labels per se), but they validly encode the two cognitive states for classification: rest (y=0) versus motor imagery with neurofeedback (y=1). The events.tsv files confirm `trial_type` values of `Rest` and `Task-NF` with duration=20s for both. S 99 appears at recording start marking the initial Rest phase; S  2 marks transitions to Task-NF phases. The 20-second sustained blocks are explicitly validated across all three references.

### Potential Task 1: Feedback Type Stratification Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`Stimulus/S 99`, `Stimulus/S  2`]
- **Label Route**: `info`
- **Label Field**: `feedback_type`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | feedback_type | 1d | 0 | 1-dimensional neurofeedback |
  | feedback_type | 2d | 1 | 2-dimensional neurofeedback |
- **Evidence**:
  - 10.1101/397729 — Original XP2 study explicitly designed with 10 subjects per feedback type (1D vs 2D). participants.tsv contains feedback_type column with values '1d' and '2d'. This enables stratified analysis comparing neurofeedback learning between feedback modalities. Same epoch structure as primary task but with subject-level stratification label.
- **Notes**: Subject-level stratification task where each subject's entire recording is labeled by their assigned feedback type (1D vs 2D). Epochs are extracted from long event blocks (20s Rest/Task-NF periods marked by Stimulus/S 99 and Stimulus/S  2) and all epochs from a given subject share the same feedback_type label. This allows investigating whether EEG patterns differ between feedback modalities across the motor imagery neurofeedback paradigm.

### Potential Task 2: Age Regression from Neurofeedback Blocks
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 20 s *, overlap = 0.0 *, target_events = [`Stimulus/S 99`, `Stimulus/S  2`]
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–66.0 (years) | Subject-level continuous variable; each epoch inherits the participant's age value. N=23 subjects. |
- **Evidence**:
- **Notes**: Uses `Stimulus/S 99` (recording start/baseline onset) and `Stimulus/S  2` (task block transition) as epoch anchors to extract sustained 20-second neurofeedback blocks. Age is a native participants.tsv column with complete coverage (18–66 years), enabling subject-level regression. The epoch window matches the task block duration observed in events.tsv (20 s Rest/20 s Task-NF alternation).

### Potential Task 3: Sex Classification from Neurofeedback Blocks
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 20 s *, overlap = 0.0, target_events = [`Stimulus/S 99`, `Stimulus/S  2`]
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: This B3 archetype task uses the native `sex` column from participants.tsv, which is pre-existing metadata requiring no kernel derivation. The epoch windows are anchored to neurofeedback block onset markers (S 99 for initial baseline/recording start, S  2 for task block transitions) with 20-second windows matching the Rest/Task-NF block durations observed in events.tsv. All 23 subjects have complete sex labels (F=11, M=12) enabling balanced binary classification. The `*` on epoch parameters indicates these were inferred from the task block structure in events.tsv samples rather than from an explicit task definition.

### Potential Task 4: ECG Regression from Neurofeedback Blocks
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 20 s *, overlap = 0.0 *, target_events = [`Stimulus/S 99`, `Stimulus/S  2`]
- **Label Route**: `misc`
- **Label Field**: `ECG`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | ECG | continuous (mV) | Native ECG channel recorded simultaneously with EEG during motor imagery neurofeedback; target is the continuous ECG signal time series within each epoch |
- **Evidence**:
  - `d_sub-xp201_task-1dNF_run-01_eeg_pp.vhdr` — ECG channel present in native 64-channel EEG recording alongside standard EEG electrodes (Fp1, Fp2, F3, F4, C3, C4, etc.)
  - `d_sub-xp201_task-1dNF_run-02_eeg_pp.vhdr` — ECG channel confirmed present in second run of same subject
  - `events.tsv` (task-1dNF, task-2dNF) — Neurofeedback paradigm uses alternating 20-second Rest and 20-second Task-NF blocks, with `Stimulus/S 99` marking recording start and `Stimulus/S  2` marking mid-recording transition; these event anchors define sustained neurofeedback block epochs
  - `README` — Dataset involves simultaneous EEG-fMRI during right-hand motor imagery and neurofeedback; ECG provides physiological correlate of autonomic arousal during neurofeedback performance
- **Notes**: Archetype B1: native misc channel. The ECG channel is directly present on the raw EEG object (not kernel-derived), so Meta Level = super (requires reading from the raw data object, not from pre-extracted metadata). The `epoch_by_long_event_hdf5` method with 20-second epochs matches the block duration of the neurofeedback paradigm (Rest/ Task-NF alternating blocks). Both `Stimulus/S 99` (recording start/baseline onset) and `Stimulus/S  2` (task block transition) serve as epoch anchors to capture complete neurofeedback blocks. The continuous ECG signal within these epochs serves as the regression target, providing a physiological measure of autonomic state during motor imagery neurofeedback.

### Potential Task 5: Segmentation-based Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–66.0 (years) | Subject-level continuous target; all segments from a subject share the same age label |
- **Evidence**:
- **Notes**: Archetype C with native info column. Sliding window segmentation (4s windows, 50% overlap) applied to continuous EEG without relying on trial/block boundaries. Age is a native participants.tsv column, so Meta Level = raw. The kernel does not need to derive any channels; it only needs to read the pre-existing `age` field from participants.tsv and assign it to all segments belonging to each subject.

### Potential Task 6: Segmentation-based Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Archetype C with native info field (sex) and segmentation-based epoching. No event structure required; sliding 4-second windows with 50% overlap extract continuous EEG dynamics for subject-level sex classification. Binary classes reasonably balanced (11 F, 12 M out of 23 subjects).

### Potential Task 7: Segment-based Feedback Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `feedback_type`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | feedback_type | 1d | 0 | One-dimensional neurofeedback group |
  | feedback_type | 2d | 1 | Two-dimensional neurofeedback group |
- **Evidence**:
- **Notes**: Archetype C with native info column. Uses sliding-window segmentation (4-second windows, 50% overlap) to classify continuous EEG dynamics between 1D and 2D neurofeedback groups at the subject level. No event boundaries required; target_events=[] per segmentation method. The feedback_type column in participants.tsv is complete with values {1d, 2d}, explicitly comparing the two NF paradigms from Perronnet et al. (2018). Epoch parameters inferred from SKILL defaults for motor imagery segmentation analysis.

## Data Quality Notes

- Very high sampling rate of 5000 Hz requires significant storage and computational resources for processing.
- Simultaneous EEG-fMRI acquisition introduces substantial MRI gradient artifacts (29958 Pulse Artifact markers); proper artifact correction is essential before analysis.
- Device information is missing from metadata, limiting reproducibility of exact acquisition hardware specifications.
- The `Stimulus/S 35` and `Stimulus/S101` event markers have unclear functions with low counts (10 and 95 respectively), suggesting possible calibration or system events that may need exclusion.
- Subject count discrepancy between draft (16) and file scan metadata (23 subjects with complete age/sex/feedback_type) has been resolved in favor of the file scan result.
- ECG channel requires verification of units and proper role as physiological monitor rather than EEG signal.
- TPULSE markers indicate MRI pulse timing; these administrative markers should be excluded from event-based epoching to avoid contaminating neurophysiological data with artifact periods.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
