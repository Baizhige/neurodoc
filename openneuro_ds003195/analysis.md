# Placebo Neuroepo multisession

**Dataset**: `openneuro_ds003195` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003195
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 19 | **Sampling Rate**: 200 Hz
**Manual Review**:

## Paradigm

Resting-state EEG recorded from Parkinson's disease patients who received a placebo (not active Neuroepo) during a six-month drug evaluation trial. Recordings were taken before and after the administration period. This is the placebo control arm companion to ds003194 (Neuroepo treatment). Protocol includes resting-state (eyes open/closed), hyperventilation, and recovery periods.

## File Scan Result

> **Kernel SHA256**: `a8d33d3dabe9077b0653fcc7b6c67408e630b4fb1f108bcda2df57d9c9035899`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: sex-coded regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | sex | {0, 1, 6} (coded) | Numeric sex code from participants.tsv; 0 and 1 are standard codes, 6 is an anomalous value present in one subject (sub-PLAC19). Values preserved as-is for continuous regression framing. |
- **Evidence**:
- **Notes**: Resting-state EEG segmented into 4-second non-overlapping windows. Subject-level regression target is the raw sex code (0, 1, or 6) from participants.tsv. The anomalous value 6 may represent a data quality issue but is preserved as-is per grounded catalog. This task explores whether EEG features correlate with sex code in a continuous fashion, as an alternative framing to binary classification.

### Potential Task 2: continuous resting-state EEG segmentation with subject-level sex
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | 0 | 0 | female |
  | sex | 1 | 1 | male |
  | sex | 6 | 2 | unknown/unspecified |
- **Evidence**:
- **Notes**: Archetype C with native info column: continuous resting-state EEG is segmented into 10-second non-overlapping windows (50% overlap), and each segment inherits the subject-level `sex` label from participants.tsv. The three distinct values (0, 1, 6) map to y=0,1,2 respectively. This task provides a subject-grouping variable suitable for self-supervised or contrastive pretraining frameworks where demographic grouping can serve as a pretext task. No event anchors are used; segmentation is purely time-based.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
