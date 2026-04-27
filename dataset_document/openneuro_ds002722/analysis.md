# A dataset recorded during development of an affective brain-computer music interface: calibration session

**Dataset**: `openneuro_ds002722` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002722
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 94 | **Channels**: 37 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants listened to 40-second synthetic music clips designed to induce specific affective states (varying valence and arousal) as a calibration session for an affective brain-computer music interface (BCMI). EEG and physiological signals were recorded to build a mapping from neural/physiological features to targeted emotional states. Codes 1-9 are primary music condition labels; 100-200 range codes encode specific music clip identifiers.

## File Scan Result

> **Kernel SHA256**: `6f4f4bba50913ffe10cf00b9d8352cbbe0dc7713c9b50d7bb39d4520e89cacec`
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

### Classical Task 1: Affective Music Listening Segmentation — Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0 – 30.0 (years) | Subject chronological age from participants.tsv; all segments from a given subject share the same age label |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 — Dataset publication describing affective BCMI calibration with music listening; participants.tsv contains age field used for subject-level regression
- **Notes**: Segmentation-based approach for continuous music listening EEG. Since the paradigm involves 21-second trials of continuous music stimulation with no clear event-boundary rest periods suitable for standard epoching, we use 10-second sliding windows (50% overlap) to capture local neural dynamics during affective music exposure. Age is a native participants.tsv column (B3 archetype), requiring no kernel derivation. The regression target is subject age, enabling exploration of age-related neural signatures during affective processing. This complements event-based classification tasks by leveraging the continuous nature of the stimulation.

### Potential Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–30.0 (years) | Subject-level age broadcast to all segments per subject. N=19 with complete age data. |
- **Evidence**:
- **Notes**: Segmentation-based regression task using 10-second non-overlapping windows (50% overlap) from continuous EEG recordings. No event-based discrimination required; age label is a native participants.tsv column (B3 archetype, raw meta level). The kernel simply reads the `age` field from participants.tsv and broadcasts it to all segments belonging to each subject.

### Potential Task 2: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - participants.tsv — N=19 subjects with complete sex information: 11 female (F), 8 male (M)
- **Notes**: Subject-level binary classification using continuous EEG segments. No event-based structure is used; 10-second windows with 50% overlap provide multiple samples per subject. Class balance is reasonable (58% female, 42% male). The sex field is a native participants.tsv column, so Meta Level is raw.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
