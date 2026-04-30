# EEG: First Episode Psychosis vs. Control Resting Task 2

**Dataset**: `openneuro_ds003947` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003947
**Category**: Biological State | **Subjects**: 61 | **Files (Completed)**: 61 | **Channels**: 64 | **Sampling Rate**: 3000 Hz | **Manual Review**:

## Paradigm

Five minutes of resting-state EEG recording used to compare spontaneous brain activity between individuals with First Episode Psychosis (FEP) and healthy controls. This is a second independent resting-state dataset from the same clinical study series as ds003944, recorded at a higher sampling rate (3000 Hz). Group membership (FEP vs. control) serves as the classification label.

## File Scan Result

> **Kernel SHA256**: `fbd4ac8748e05bfe6864be140ae0828d105c2e1924b258f15c9edb261e26981c`
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

### Classical Task 1: FEP vs Control Classification (2-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `type`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | type | Control | 0 | Healthy control participant |
  | type | Psychosis | 1 | First Episode Psychosis participant |
- **Evidence**:
  - 10.1038/s41598-024-66110-0 — Binary classification of FEP vs controls from resting-state EEG on ds003947, 95.51% accuracy using PSD features with GPC on 72 subjects (44 FEP, 28 controls)
  - 10.48550/arxiv.2411.18392 — Uses 4-second non-overlapping windows yielding ~75 epochs per subject for FEP vs control classification
- **Notes**: Segmentation-based epoching for resting-state clinical paradigm. The 4-second window length and 0 overlap are inferred from the arXiv paper analysis and consistent with standard resting-state EEG segmentation approaches. The 'type' column in participants.tsv provides native subject-level diagnosis labels (Control/Psychosis) without requiring kernel derivation.

### Potential Task 1: Age Regression from Resting-State EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 14.3–38.3 (years) | Chronological age from participants.tsv; subject-level label applied to all segmented epochs |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Segmentation of 5-minute resting-state recordings into 4-second non-overlapping windows yields approximately 75 epochs per subject. Age is a complete numeric variable (14.3–38.3 years) suitable for regression. No event markers are required for this continuous resting-state paradigm.

### Potential Task 2: Gender Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | M | 0 | Male |
  | gender | F | 1 | Female |
- **Evidence**:
- **Notes**: Subject-level classification using resting-state EEG segments. Gender is a complete categorical variable in participants.tsv (38 M, 23 F). Segmentation creates multiple epochs per subject; all segments from a subject share the same gender label. The 4-second segment length is inferred from standard resting-state analysis practices as no gender-specific epoch guidance exists in the dataset.

### Potential Task 3: Race Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `race`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | race | Asian | 0 | Asian racial category |
  | race | Black | 1 | Black racial category |
  | race | White | 2 | White racial category |
- **Evidence**:
- **Notes**: Segmented resting-state EEG (4-second non-overlapping windows) with subject-level race labels from participants.tsv. This is a 3-class classification task predicting racial category from spontaneous EEG activity. Note: race prediction from EEG is scientifically controversial and likely reflects demographic confounds (e.g., skull thickness, hair type affecting electrode impedance) rather than intrinsic neural differences. Included for completeness as the grounded catalog permits. All three racial categories (Asian, Black, White) have complete data across N=61 subjects.

### Potential Task 4: Ethnicity Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `ethnicity`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | ethnicity | Not Hispanic | 0 | Not Hispanic |
  | ethnicity | Hispanic | 1 | Hispanic |
- **Evidence**:
- **Notes**: This is a subject-level classification task derived from the `ethnicity` column in participants.tsv. The `Unknown` category (present in the raw data) is excluded, leaving a binary classification between `Not Hispanic` (y=0) and `Hispanic` (y=1). The epoch parameters are inferred for standard resting-state analysis with 4-second non-overlapping segments. This task is scientifically questionable as resting-state EEG contains no obvious neural correlate of ethnicity; it serves as a demographic prediction benchmark rather than a neurophysiologically grounded task.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
