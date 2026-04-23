# An EEG dataset recorded during affective music listening

**Dataset**: `openneuro_ds002721` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002721
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 185 | **Channels**: 19 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants listened to music clips from film scores while their EEG was recorded, to investigate the neural correlates of music-induced emotional states. Each music clip is marked at onset with a numeric trigger code (800-908 range encode specific music tracks; system markers such as 32768 and 257 are used for synchronization). The study is part of a research series investigating affective processing in music, with participants reporting felt emotions across multiple affective dimensions. Emotion ratings were collected on a 9-point Likert scale across 8 affective dimensions including pleasantness.

## File Scan Result

> **Kernel SHA256**: `6fa63c9ad6f7df97c0442c9b4be7306f09b4c6d7d8cbdbbffc1f73692c43685e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Age Regression from Resting EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 5.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18–66 (years) | Subject-level chronological age from participants.tsv; all 31 participants have complete age data. Each 10 s segment inherits the same subject age label. |
- **Evidence**:
  - participants.tsv — complete age data for N=31 participants (range 18–66 years)
  - README — confirms task-run1 and task-run6 are 300 s resting state runs with eyes-open/relaxed instruction
  - eeg.json / EDF header — 19-channel EEG at 1000 Hz, ~304 s duration confirms continuous resting recordings
- **Notes**: Standard brain-age prediction paradigm. Continuous 300 s resting-state EEG (runs 1 and 6) is segmented into 10 s windows with 5 s overlap, producing ~59 segments per run per subject. Subject-level age from participants.tsv serves as the regression target for each segment. No kernel derivation needed—age is a native participants.tsv column.

### Classical Task 2: Age Regression from Music Listening EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 12 s *, overlap = 2.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–66.0 (years) | Subject chronological age from participants.tsv; applied as subject-level label to all music-listening segments |
- **Evidence**:
- **Notes**: Segments 12-second continuous windows from music listening runs (task-run2–task-run5), matching the 12s music clip duration. Overlap of 2s provides coverage across the continuous recording. Age label is drawn from participants.tsv (native info column, archetype B3). No kernel derivation needed — label is pre-existing in dataset metadata. This task tests whether age-related EEG patterns generalize from resting state to active music listening paradigm.

### Classical Task 3: Sex Classification from Resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 5.0 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level classification using 10-second non-overlapping windows from 300-second resting-state runs (run1 and run6). The kernel should filter to task-run1 and task-run6 (resting state) and segment into 10s windows with 5s overlap. Labels are drawn from participants.tsv sex column (13 M, 18 F). This is a standard demographic prediction paradigm from resting-state EEG.

### Classical Task 4: Sex Classification from Music Listening EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 12 s *, overlap = 2.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - `participants.tsv` — N=31 subjects with sex column (M=13, F=18), complete coverage
  - `README` — 4 music listening runs with 10 trials each, 40 music clips of 12s duration
  - `events.json` — Music play onset marked by event 788, fixation cross 786, music stimuli 301-360
- **Notes**: Segmentation approach uses 12s windows matching music clip duration with 2s overlap for coverage across the active music-listening periods. Binary sex classification tests whether EEG during affective music processing carries sex-differentiable information. All labels drawn from native participants.tsv info field; no kernel derivation required.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
