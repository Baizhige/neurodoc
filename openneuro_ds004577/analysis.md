# Dataset containing resting EEG for a sample of 103 normal infants in the first year of life

**Dataset**: `openneuro_ds004577` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004577
**Category**: Biological State | **Subjects**: 103 | **Files (Completed)**: 103 | **Channels**: 128 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings from 103 healthy infants (aged 1-12 months) during the first year of life. Recordings were made during natural infant rest/sleep states. Eyes-open and eyes-closed state markers are present but the primary data is continuous infant resting EEG. The dataset supports developmental neuroscience research on early brain maturation.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No task event markers. State markers (eyes_closed, eyes_open) and artifact markers (discontinuity) are present but the dataset is primarily resting-state continuous EEG._

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `eyes_closed` | ~103xN | event | raw | Eyes-closed resting state |
| `eyes_open` | ~103xN | event | raw | Eyes-open resting state |
| `discontinuity` | ~103xN | admin | raw | Recording discontinuity/artifact marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes_closed` | - | Eyes-closed resting state segment |
  | `eyes_open` | - | Eyes-open resting state segment |
- **Notes**: Infant resting EEG without trial structure. discontinuity markers indicate artifact segments. Use sliding window segmentation; consider excluding segments surrounding discontinuity markers. 
- **Kernel Notes**: Apply segmentation across continuous recording. Optionally filter out windows containing or adjacent to `discontinuity` events to avoid artifact-corrupted segments. This replaces the placeholder Classical Task 1 from original analysis.

## Data Quality Notes

- 103 infants aged 1-12 months; high variability in developmental stage
- 128 channels; high-density pediatric EEG cap
- discontinuity markers indicate artifact/movement artifacts in infant recordings


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review