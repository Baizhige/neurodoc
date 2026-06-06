# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 56 | **Files (Completed)**: 280 | **Channels**: 130 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This is the fourth BMI-HDEEG sensorimotor rhythm-based BCI dataset. Scientific Data 2023 describes Dataset 4 as a bivariate BCI using alpha-band and beta-band activity. Participants performed kinesthetic motor imagery of right finger movement during the imagery period and active relaxation of the right finger during the relaxation period. The public OpenNeuro ds004448 v1.0.2 file tree contains EEG data for 56 subjects and 280 EEG EDF files. Public BIDS events.tsv files contain only Trial start annotations and do not directly expose left/right, rest/imagery, feedback group, verum/placebo, alpha/beta, or phase labels. Therefore this document does not define left-vs-right or rest-vs-imagery event-route tasks from the current public BIDS event labels.

## File Scan Result

> **Kernel SHA256**: `b5085020f658e1d30a43e1e7085b48dc158685b15d9d1a807d721830343fc3f6`
> **EEGUnity Version**: `0.8.2`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 3608 | event | raw | Trial phase onset: Trial start |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `trial_index` | native (raw misc in EEG file) | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | e.g. 23, 22, 24 |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | complete | e.g. right, left |
| `sex` | complete | e.g. male, female |

## Tasks

### Potential Task 1: Age regression from EEG segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `age` | no mapping; numeric age in years, range 19-58 |
- **Evidence**:
  - OpenNeuro ds004448 `participants.tsv` — `age` is complete for all 56 public participants.
- **Notes**: Subject-level metadata task using fixed EEG segmentation. This is technically implementable but is not the core BCI benchmark described by the data descriptor.

### Potential Task 2: Gender classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | female -> 0; male -> 1 |
- **Evidence**:
  - OpenNeuro ds004448 `participants.tsv` — `gender` is complete; distribution is 7 female / 49 male.
- **Notes**: Technically valid binary metadata task, but highly imbalanced and not central to the BCI paradigm.

## Data Quality Notes

- Event codes `event_2` (n=1723) and `event_3` (n=1875) are present in the raw data but have no corresponding annotations in BIDS events.tsv files, limiting interpretability of trial structure.
- File count (280) exceeds subject count (56), indicating multiple files per subject (likely multiple runs/sessions); users should verify within-subject consistency before pooling.
- Gender classification task has severe class imbalance (~87.5% male vs ~12.5% female) which may bias model training without mitigation strategies.
- `handedness` is available in `participants.tsv`, but it is not defined as a task label because the distribution is extremely imbalanced (1 left / 55 right) and it is not part of the core BCI paradigm.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
