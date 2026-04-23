# Meta-rdk: Raw EEG data

**Dataset**: `openneuro_ds004367` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004367
**Category**: High-level Mental | **Subjects**: 42 | **Files (Completed)**: 40 | **Channels**: 68 | **Sampling Rate**: 1200 Hz
**Manual Review**:

## Paradigm

A visual motion discrimination task involving left/right direction decisions on random dot kinematogram (RDK) stimuli followed by a metacognitive confidence assessment using a visual analog scale. The numerical trigger codes encode stimulus direction, coherence level, response direction, confidence level, and feedback. The dataset supports both motion perception classification and confidence/metacognition regression.

## File Scan Result

> **Kernel SHA256**: `d89b05628847049682560ac8a7ac64ce492a8d1b6c4c74a813f598c6943268a0`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 19–60 (years) | Continuous age in years from participants.tsv; subject-level label applied to all segments |
- **Evidence**:
  - participants.tsv — Age column complete for all 40 participants (sample values: 40, 19, 26; range 19–60)
- **Notes**: B3 archetype using native participants.tsv info field. Segmentation approach with 2-second non-overlapping windows produces multiple samples per subject, all sharing the same age label. Standard for subject-level regression when no event structure is needed.

### Potential Task 2: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | M | 0 | Male |
  | Gender | F | 1 | Female |
- **Evidence**:
  - participants.tsv — Gender column complete for all 40 participants with values M/F (sample: S01=M, S02=M, S03=M)
  - README — Study reports 31 male and 9 female participants total (16 males + 4 females in patient group, 15 males + 7 females in control group)
- **Notes**: Subject-level demographic prediction task. EEG segments are extracted via non-overlapping 2-second segmentation and labeled by participant Gender from participants.tsv. Binary classification with 0-based integer labels for sklearn compatibility.

### Potential Task 3: Patient vs Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | Patient | 0 | Schizophrenia spectrum disorder patient |
  | Group | Control | 1 | Healthy control participant |
- **Evidence**:
  - https://doi.org/10.1038/s41537-023-00333-4 — Group variable distinguishes schizophrenia spectrum disorder patients (N=20) from healthy controls (N=22); primary clinical contrast in study design with binary classification of clinical relevance.
- **Notes**: Segmentation-based approach for clinical group classification. Each 2-second segment inherits the participant's group label from participants.tsv. The published paper explicitly analyzes group differences in metacognition and EEG markers, supporting this contrast as a meaningful ML target. Segment length inferred from typical ERP/oscillatory analysis windows in clinical EEG studies.

### Potential Task 4: Segmented RDK Task with Group Label
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | Patient | 0 | Schizophrenia spectrum disorder (schizophrenia or schizoaffective disorder) |
  | Group | Control | 1 | Healthy control participant |
- **Evidence**:
  - https://doi.org/10.1038/s41537-023-00333-4 — Archetype C task using continuous EEG segmentation during RDK task performance with patient/control group as label; sliding windows capture sustained task-state differences between clinical groups.
- **Notes**: Segmentation-based approach with no event locking. The 2-second window length and 50% overlap are inferred from the need to capture sustained oscillatory dynamics rather than transient ERPs, as group differences in this clinical paradigm are expected to manifest in ongoing task-related EEG activity rather than time-locked responses. The Group label is drawn from participants.tsv, a native info field requiring no kernel derivation.

### Potential Task 5: Segmented RDK Task with Age Label
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 19–60 (years) | Continuous age prediction from 2-second EEG segments during random-dot kinematogram task performance |
- **Evidence**:
  - participants.tsv — Age column available for all 40 subjects with range 19-60 years (complete, numeric)
  - README — Study includes 22 healthy controls and 20 schizophrenia spectrum participants with age variation
- **Notes**: Archetype C with native info field (Age). Segmentation-based epochs with 50% overlap to maximize data utilization for regression. Age effects on motion processing and decision-making dynamics captured in sustained EEG patterns during RDK task.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
