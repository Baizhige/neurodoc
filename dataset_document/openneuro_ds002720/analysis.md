# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2018 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 18 | **Files (Completed)**: 165 | **Channels**: 19 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants used EEG self-regulation to control the tempo of music in a tempo-based brain-computer music interface (BCMI). One condition instructed participants to lower their alpha levels and the other instructed participants to raise their alpha levels. Each labeled event spans a full 20-second music clip interval. The dataset contains multiple runs per participant.

## File Scan Result

> **Kernel SHA256**: `f8ccabb74f55b6325ba81c0083fcd40a7776d77052a73c4c34fbbad4f06e3208`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event` | raw | event |  |  |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |


## Tasks

### Potential Task 1: age regression from EEG segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range | Notes |
  |---|---|---|
  | `age` | 18.0 – 28.0 (years) | Subject chronological age from participants.tsv; N=18, mean ~23 |
- **Evidence**:
  - participants.tsv — age field complete for all 18 subjects (range 18–28 years)
  - dataset_description.json — BCMI-MIdAS dataset with 19 healthy participants
- **Notes**: Continuous EEG segmentation (4s windows, 50% overlap) extracts samples from BCMI runs without requiring event-locked epochs. Age is a native numeric field in participants.tsv, suitable for subject-level regression. No derived kernel computation needed.

### Potential Task 2: sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |---|---|---|---|
  | `subject_sex` | M | 0 | Male |
  | `subject_sex` | F | 1 | Female |
- **Evidence**:

- **Notes**: Continuous EEG segmentation (4s windows, 50% overlap) applied across all BCMI runs per subject. Binary classification of subject sex from resting/task-continuous EEG. Class imbalance present (M=14, F=4 out of 18 subjects). The segment_length and overlap values are standard defaults for continuous EEG segmentation with no task-specific reference guidance.

### Potential Task 3: Binned-Age Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |---|---|---|---|
  | `subject_age` | ≤22 | 0 | Younger (18–22 years) |
  | `subject_age` | >22 | 1 | Older (23–28 years) |
- **Evidence**:
  - participants.tsv — age column complete for N=18, range 18–28, sample values [23, 24, 28, 20, 19, 26, 20]
- **Notes**: The kernel must derive binary binned labels from the native age field using a median split at approximately 22–23 years (median of 18–28 range ≈ 23). This is a derived classification variant of the continuous age regression task; the kernel discretizes the continuous age into two balanced classes for segment-level classification. Segmentation produces fixed-length windows with 50% overlap; no event alignment is used.

## Data Quality Notes

- Twenty-two event files are empty (no events recorded), leaving 143 files with usable event data.
- The Event Structure table in the File Scan Result is empty, indicating no events were found across scanned files despite the paradigm description mentioning 20-second music clip intervals.
- Device metadata is completely missing from the dataset; equipment information must be inferred from other sources.
- There is a discrepancy in subject count between the metadata (18 subjects) and dataset_description.json which mentions 19 healthy participants.
- Class imbalance is present in sex classification (14 male, 4 female), which may affect model training and evaluation.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
