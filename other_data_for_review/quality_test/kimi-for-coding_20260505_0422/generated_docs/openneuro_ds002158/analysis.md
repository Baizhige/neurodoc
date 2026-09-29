# Simultaneous EEG-fMRI during a working memory task

**Dataset**: `ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 64 | **Sampling Rate**: 5000 Hz | **Manual Review**:

## Paradigm

Twenty healthy young adults (ages 20–32) performed a working memory (N-back) task while simultaneous EEG and fMRI were recorded. The EEG was acquired at 5000 Hz using a 64-channel Brain Products system with MR-compatible amplifiers, synchronized to the MRI scanner via volume acquisition triggers. The high sampling rate and presence of synchronization markers indicate the dataset was designed for EEG-fMRI integration research, with the working memory paradigm serving as the cognitive load manipulation.

## File Scan Result

> **Kernel SHA256**: `63c70b2f68731d41c4bf1e5e3d07550e18eafaf2fad7444abd67a6f57c0e2269`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `Response/R128` | 44303 | event | raw | Response marker (unspecified response type) |
| `Stimulus/S  7` | 1347 | event | raw | Stimulus marker S7 (unspecified stimulus type) |
| `Stimulus/S  8` | 1477 | event | raw | Stimulus marker S8 (unspecified stimulus type) |
| `Stimulus/S 11` | 2851 | event | raw | Stimulus marker S11 (unspecified stimulus type) |
| `Stimulus/S 12` | 2854 | event | raw | Stimulus marker S12 (unspecified stimulus type) |
| `Stimulus/S 17` | 1356 | event | raw | Stimulus marker S17 (unspecified stimulus type) |
| `Stimulus/S 18` | 1489 | event | raw | Stimulus marker S18 (unspecified stimulus type) |
| `Stimulus/S 27` | 5657 | event | raw | Stimulus marker S27 (unspecified stimulus type) |
| `Stimulus/S 37` | 120 | event | raw | Stimulus marker S37 (unspecified stimulus type) |
| `Stimulus/S 38` | 109 | event | raw | Stimulus marker S38 (unspecified stimulus type) |
| `Stimulus/S 40` | 6175 | event | raw | Stimulus marker S40 (unspecified stimulus type) |
| `Stimulus/S 41` | 5703 | event | raw | Stimulus marker S41 (unspecified stimulus type) |
| `Stimulus/S 43` | 6583 | event | raw | Stimulus marker S43 (unspecified stimulus type) |
| `Stimulus/S 44` | 475 | event | raw | Stimulus marker S44 (unspecified stimulus type) |
| `Stimulus/S128` | 474612 | event | raw | High-frequency stimulus marker (likely volume acquisition trigger or scanner synchronization pulse for simultaneous EEG-fMRI) |
| `Stimulus/S140` | 3 | event | raw | Stimulus marker S140 (unspecified stimulus type) |
| `Stimulus/S145` | 1 | event | raw | Stimulus marker S145 (unspecified stimulus type) |
| `Stimulus/S155` | 2 | event | raw | Stimulus marker S155 (unspecified stimulus type) |
| `Stimulus/S165` | 39 | event | raw | Stimulus marker S165 (unspecified stimulus type) |
| `Stimulus/S166` | 48 | event | raw | Stimulus marker S166 (unspecified stimulus type) |
| `Stimulus/S169` | 1 | event | raw | Stimulus marker S169 (unspecified stimulus type) |
| `Stimulus/S171` | 4364 | event | raw | Stimulus marker S171 (unspecified stimulus type) |
| `SyncStatus/Sync On` | 30864 | admin | raw | Synchronization marker onset (EEG-fMRI clock alignment) |

### Info

| Field | Completeness | Notes |
|---|---|---|

## Tasks

### Potential Task 1: Age Regression from Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `age` | Continuous age in years (20–32), used directly as regression target per subject. All segments from a subject share the same age label. |
- **Evidence**:
  - `participants.tsv` — Age available for all 20 participants (range 20–32, mean ~25.5); complete coverage with no missing values.
- **Notes**: Subject-level biomarker regression task using continuous 2-second EEG segments with 50% overlap. No event structure is required since the goal is to predict a static subject-level demographic variable (age) from resting/task EEG patterns. All segments from a given subject receive the same age label, enabling subject-level train/test splits to avoid leakage.

### Potential Task 2: Sex Classification from Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  | sex | 0 = F (female), 1 = M (male) |
- **Evidence**:
  - participants.tsv — sex field available for all 20 participants (11 M, 9 F)
- **Notes**: Subject-level binary classification using 2-second non-overlapping segments of continuous EEG. The sex label is drawn from participants.tsv (native info field, archetype B3). Segmentation parameters inferred from default values since no task-specific timing constraints apply for subject-level biomarker classification.



## Data Quality Notes

- Extremely high sampling rate (5000 Hz) with massive volume of stimulus markers (474,612 S128 events) suggests dense fMRI volume triggers; downsampling or trigger decimation will likely be needed for practical analysis.
- Event meanings are unspecified in the raw markers; the working memory task structure (stimulus types, conditions, response mappings) is not documented in the event table and requires manual curation or reference to original publication.
- Synchronization markers (`SyncStatus/Sync On`, 30,864 occurrences) indicate active EEG-fMRI clock alignment; users must verify proper handling of these for any analysis removing gradient artifacts.
- The dataset appears to have only 20 completed files despite 20 subjects, suggesting one file per subject; verify if multiple runs or conditions are concatenated within single files.
- No known data quality issues regarding signal acquisition or participant coverage.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
