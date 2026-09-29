# Placebo Neuroepo multisession

**Dataset**: `openneuro_ds003195` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003195
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 19 | **Sampling Rate**: 200 Hz | **Manual Review**:

## Paradigm

Resting-state EEG recorded from Parkinson's disease patients who received a placebo (not active Neuroepo) during a six-month drug evaluation trial. Recordings were taken before and after the administration period. This is the placebo control arm companion to ds003194 (Neuroepo treatment). Protocol includes resting-state (eyes open/closed), hyperventilation, and recovery periods.

## File Scan Result

> **Kernel SHA256**: `3904908dbd355dfda93ce6fed2d798b5b89509ece3c4eb9c538389062b3797af`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
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
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | Numeric sex code from participants.tsv; values {0, 1, 6} preserved as-is for continuous regression framing. 0 and 1 are standard codes; 6 is an anomalous value present in one subject (sub-PLAC19). |
- **Evidence**:
- **Notes**: Resting-state EEG segmented into 4-second non-overlapping windows. Subject-level regression target is the raw sex code (0, 1, or 6) from participants.tsv. The anomalous value 6 may represent a data quality issue but is preserved as-is per grounded catalog. This task explores whether EEG features correlate with sex code in a continuous fashion, as an alternative framing to binary classification.

---

### Potential Task 2: continuous resting-state EEG segmentation with subject-level sex
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | Value 0 maps to y=0 (female); value 1 maps to y=1 (male); value 6 maps to y=2 (unknown/unspecified). Three-class classification from participants.tsv sex codes. |
- **Evidence**:
- **Notes**: Archetype C with native info column: continuous resting-state EEG is segmented into 10-second non-overlapping windows (50% overlap), and each segment inherits the subject-level `sex` label from participants.tsv. The three distinct values (0, 1, 6) map to y=0,1,2 respectively. This task provides a subject-grouping variable suitable for self-supervised or contrastive pretraining frameworks where demographic grouping can serve as a pretext task. No event anchors are used; segmentation is purely time-based.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
