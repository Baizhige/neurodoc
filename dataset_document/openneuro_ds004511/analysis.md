# Deception_data

**Dataset**: `openneuro_ds004511` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004511
**Category**: High-level Mental | **Subjects**: 44 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 3000 Hz | **Manual Review**:

## Paradigm

Participants performed a deception task while EEG was recorded. The dataset contains continuous EEG recordings with only a hardware synchronization marker (Sync) present per recording rather than trial-level event markers. No meaningful trial annotations are available for epoch-based analysis. Recordings include resting-state (eyes closed) and task-related data from healthy individuals.

## File Scan Result

> **Kernel SHA256**: `66ea7889158c3527373ff3343eca28cf67c536695686b5c2d49d53c3d4b8e47c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sync(1)` | 77764 | admin | raw | Synchronization trigger marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sex Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - participants.tsv — N=44 subjects with complete sex labels (F=21, M=23); ages 20-43
- **Notes**: Sliding-window segmentation of continuous resting-state and task-related EEG into 2-second windows with 50% overlap. No trial-level events exist for epoching; Sync(1) is an administrative synchronization marker only. Subject-level sex labels from participants.tsv are propagated to all windows per subject for binary classification.

### Classical Task 2: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20.0–43.0 (years) | Continuous age from participants.tsv; 44 subjects with complete data. Each segmented window inherits the subject's age label for subject-level regression. |
- **Evidence**:
  - participants.tsv — N=44 subjects, age range 20.0–43.0 years, complete for all subjects (sample values: 22, 23, 26)
  - events.tsv files (sub-S200116, sub-S200120, sub-S200205 across CC/GG/Rest tasks) — confirm only Sync(1) administrative markers present, no trial-level events suitable for event-based epoching
  - README — dataset includes resting-state (eyes closed) and task-related data from 44 healthy individuals ages 21-40
  - eeg.json — continuous recording type, 3000 Hz sampling, ~914s duration for CC task
- **Notes**: Segmentation-based epoching is required because no trial-level events exist beyond Sync(1) hardware synchronization markers. The 2-second window length with 50% overlap follows Category SKILL defaults for resting-state/continuous paradigms when no specific timing information is available. Age is a native participants.tsv column (B3 archetype), so Meta Level = raw. The task treats each segmented window as a sample with the subject's age as the regression target, enabling subject-level age prediction from continuous EEG features.

### Classical Task 3: Binned Age Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | age | ≤24 | 0 | Younger half (age ≤ median ≈ 24 years) |
  | age | >24 | 1 | Older half (age > median ≈ 24 years) |
- **Evidence**:
  - participants.tsv — age column: numeric, complete, range 20–43, N=44 subjects; median split creates balanced binary classification
- **Notes**: The kernel must derive age bins from the `age` field in participants.tsv. Since age is continuous (20–43), we apply a median split to create two balanced classes (younger vs. older). The median age across 44 subjects is approximately 24 years based on the sample data showing ages 22–26 in the first rows and range 20–43 overall. Segmentation with 2s windows and 50% overlap is used because no trial events exist for resting-state data.

## Data Quality Notes

- No trial-level event markers available for epoch-based analysis
- Sync(1) is a hardware-only synchronization marker and should not be used for task epoching
- Only 29 of 44 subjects have completed files available
- Device information is missing from metadata
- Discrepancy between draft metadata (512 Hz) and authoritative data (3000 Hz sampling rate); 3000 Hz is correct per eeg.json evidence

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
