# Shanghai University EEG Dataset (SHU-EEG)

**Dataset**: `figshare_shudb` | **Year**: 2024 | **URL**: https://figshare.com/articles/dataset/An_EEG_dataset_for_cross-session_motor_imagery_BCI/24236767
**Category**: Action/Output | **Subjects**: 232 | **Files (Completed)**: 856 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset was collected for cross-session motor imagery (MI) brain-computer interface (BCI) research at Shanghai University. Subjects performed motor imagery tasks across multiple sessions, with EEG recorded using a 64-channel system at 1000 Hz sampling rate. The paradigm involves standard left/right hand motor imagery cues, with event markers indicating task periods (event IDs 1.0 and 2.0 likely corresponding to two MI classes). All subjects are categorized as 'novice' in the participants metadata, indicating limited or no prior BCI experience.

## File Scan Result

> **Kernel SHA256**: `db2b397cd2a691b879f03b9483e8fc33f65748ca87e63a29109566fc226aeaf2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `1.0` | 5524 | event | raw |  |
| `2.0` | 5537 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (232/856) | Values: 22-24. All subjects appear to be young adults. |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | partial (232/856) | Encoded as 'M'/'F' in participants.tsv; samples show male/female distribution. All subjects in group 'novice'. |

## Tasks

### Potential Task 1: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | gender | 0 = 'F' (female), 1 = 'M' (male); subject-level label applied to all segmented epochs |
- **Evidence**:
- **Notes**: Subject-level demographic classification task using gender from participants.tsv. All epochs from a given subject share the same label. This is a potential (non-classical) task as no literature references were found using gender as a prediction target for this dataset. The 4-second segmentation matches the MI task execution window (4-8s) and provides sufficient samples for subject-level prediction.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | age | Continuous age in years (20–24); assigned to all epochs from the same subject. Predict age from resting/segmented EEG. |
- **Evidence**:
- **Notes**: Standard segmentation approach applied since age is a subject-level demographic variable with no trial-bound temporal structure. 4-second segments with no overlap match the MI task execution window (4–8s) and provide sufficient samples for subject-level label propagation. Small age range (4 years) limits predictive utility but enables exploratory age-regression benchmarking on this dataset.


## Data Quality Notes

- Missing amplifier and cap metadata limits hardware reproducibility and channel location verification.
- Age and sex metadata only available for 232 out of 856 files (27% completeness), suggesting potential subset labeling or multiple files per subject without propagated metadata.
- All subjects are labeled 'novice' with narrow age range (22-24 years), limiting generalizability to broader populations.
- Event meanings (1.0 vs 2.0) are undocumented in scan results; manual review needed to confirm motor imagery class assignments.
- File count (856) exceeds subject count (232) by factor of ~3.7, indicating multiple sessions/runs per subject without explicit session metadata in info fields.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
