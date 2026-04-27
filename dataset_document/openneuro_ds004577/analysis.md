# Dataset containing resting EEG for a sample of 103 normal infants in the first year of life

**Dataset**: `openneuro_ds004577` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004577
**Category**: Biological State | **Subjects**: 103 | **Files (Completed)**: 103 | **Channels**: 128 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

Resting-state EEG recordings from 103 healthy infants (aged 1-12 months) during the first year of life. Recordings were made during natural infant rest/sleep states. Eyes-open and eyes-closed state markers are present but the primary data is continuous infant resting EEG. The dataset supports developmental neuroscience research on early brain maturation.

## File Scan Result

> **Kernel SHA256**: `e1637d1741cd7dcfae96b0fc025448949e83855805a558e4b57002f089be2e33`
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

### Classical Task 1: eyes-closed vs eyes-open state classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5, target_events = []
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 65 | 0 | eyes_closed |
  | 66 | 1 | eyes_open |
- **Evidence**:
  - 10.1038/s41597-024-03606-4 — Data descriptor paper describing 103 infants (0-12.5 months) with resting-state EEG; explicitly supports binary ML classification of eyes-closed vs eyes-open states using 2.0 s sliding windows with 0.5 overlap. Event markers 65 (eyes_closed) and 66 (eyes_open) indicate state onsets with segments inheriting corresponding labels.
- **Notes**: Segmentation-based approach required because state durations vary; labels are assigned to 2-second windows based on which state interval they fall into. Discontinuity markers (value=2) at recording onset are excluded from labeling. The event route with segmentation method treats the state onset markers as anchors for label propagation across contiguous segments.

### Potential Task 1: sex classification from continuous resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | male |
  | sex | F | 1 | female |
- **Evidence**:
- **Notes**: Segmentation-based task with no event structure; 4-second non-overlapping windows extracted from continuous resting-state EEG. Sex labels (62 M, 41 F) are drawn from participants.tsv and applied uniformly to all segments from each subject. Conservative 4 s segment length and 0% overlap chosen to maximize independence between windows; values marked with * as inferred from SKILL resting-state defaults. Imbalanced classes (60% M / 40% F) are usable for binary classification.

## Data Quality Notes

- `subject_age` field is missing from metadata, preventing age-based analyses despite the dataset's developmental focus on 1-12 month infants.
- `device` field is missing, obscuring which EEG amplifier and electrode system was used for the 128-channel recordings.
- Event structure table is empty in the file scan, though Tasks section identifies event markers 65 and 66 for eyes-closed and eyes-open states; this discrepancy suggests event extraction may require kernel update.
- Wide age range (1-12 months) with missing age metadata limits ability to control for developmental effects in analyses.
- State durations vary across subjects, requiring segmentation-based approaches rather than fixed epoch extraction.
- Discontinuity markers (value=2) present at recording onset must be excluded from labeling to avoid artifact contamination.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
