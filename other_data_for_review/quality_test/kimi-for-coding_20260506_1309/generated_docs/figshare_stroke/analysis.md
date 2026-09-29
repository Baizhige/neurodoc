# Stroke EEG Dataset (figshare_stroke)

**Dataset**: `figshare_stroke` | **Year**: 2023 | **URL**: https://figshare.com/articles/dataset/Stroke_EEG_Dataset/21831688
**Category**: Biological State | **Subjects**: 50 | **Files (Completed)**: 50 | **Channels**: 32 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

This dataset contains resting-state EEG recordings from 50 stroke patients (age 44-66 years) recorded at Xiangya Hospital, Central South University, China. Data were collected using a Xian ZhenTec Intelligence ZhenTec NT1 amplifier with a standard 10-20 cap placement at 1000 Hz sampling rate. No explicit task paradigm was employed; recordings appear to be continuous resting-state EEG used for clinical assessment, with clinical metadata including NIHSS, mRS, MBI, and stroke characteristics collected for each patient.

## File Scan Result

> **Kernel SHA256**: `4baa4ab200299cb30746c0076ea8818fb633816ad969d1e85ad907aca067d0b3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### Info

| Field | Completeness | Notes |
|---|---|---|
| `Age` | complete | Age range 44-66 years, stroke patients |
| `Duration` | complete | Duration in unspecified units, range 1-14 |
| `Gender` | complete | Binary: male/female |
| `Handedness` | complete | Binary: right/left |
| `IsFirstTime` | complete | Binary yes/no, indicates first-time stroke |
| `MBI` | complete | Modified Barthel Index, range 50-100 |
| `NIHSS` | complete | NIH Stroke Scale, range 2-11 |
| `ParalysisSide` | complete | Binary: right/left side paralysis |
| `StrokeLocation` | complete | Multiple locations possible per patient, comma-separated |
| `age` | complete | Same as Age, duplicate field |
| `amplifier` | missing | No data; manufacturer is Xian ZhenTec Intelligence, model ZhenTec NT1 |
| `cap` | complete | Standard 10-20 placement scheme |
| `handedness` | complete | Same as Handedness, duplicate field |
| `mRS` | complete | Modified Rankin Scale, range 1-4 |
| `sex` | complete | Same as Gender, duplicate field |

## Tasks

### Potential Task 1: NIHSS regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | NIHSS | Numeric clinical severity score (range 2-11 in this sample), regressed directly as continuous target |
- **Evidence**:
- **Notes**: Segmentation-based epoching with subject-level label regression. No event structure exists that discriminates NIHSS values; all segments from a given subject share the same NIHSS score. 4-second segments with 50% overlap are standard defaults for continuous resting/paradigm-free EEG analysis. The NIHSS field is a native participants.tsv column with complete coverage across all 50 subjects.

### Potential Task 2: mRS Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | mRS | Numeric functional outcome score; values 1-4 in this sample, higher indicates greater disability |
- **Evidence**:
- **Notes**: Subject-level regression predicting modified Rankin Scale (mRS) from continuous resting/segmented EEG. Segmentation-based epoching (4s windows, 50% overlap) is used since there is no event structure suitable for this subject-level clinical prediction task. The mRS score is a native participants.tsv column, so Meta Level = raw.

### Potential Task 3: MBI Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | MBI | Numeric disability score (range 50-100 in this sample); higher values indicate greater functional independence. Used as continuous regression target at subject level. All segments from a subject share the same MBI value. |
- **Evidence**:
- **Notes**: Subject-level regression task using segmentation-based epoching. Since MBI is a per-subject clinical score (not time-varying), all 4-second segments extracted from a given subject's continuous EEG will share the same regression target. The kernel must read MBI from participants.tsv and broadcast it to all segments for that subject. Segmentation parameters fall back to Category SKILL defaults (4s segments, 50% overlap) as no event structure guides epoching for this subject-level clinical prediction task.

### Potential Task 4: Age regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | Age | Numeric age in years (44-66), used directly as regression target |
- **Evidence**:
- **Notes**: Subject-level demographic regression. Each segmented epoch from a participant receives the same Age value from participants.tsv. No kernel derivation needed — Age is a native info field.

### Potential Task 5: ParalysisSide classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | ParalysisSide | left → 0, right → 1 (2-class binary classification) |
- **Evidence**:
  - participants.tsv — ParalysisSide column with complete coverage (N=50), values 'left' and 'right'
- **Notes**: Subject-level clinical characteristic classification using continuous EEG segmented into 4s windows. ParalysisSide is a native participants.tsv column (B3 archetype), requiring no kernel derivation. The 4s segment length and 0.5 overlap are inferred from Category SKILL defaults for continuous EEG with no event structure, as this dataset has no usable event-based labels for this task.

### Potential Task 6: IsFirstTime classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | IsFirstTime | yes → 0 (first-ever stroke), no → 1 (recurrent stroke) |
- **Evidence**:
- **Notes**: Subject-level binary classification using clinical characteristic from participants.tsv. Since IsFirstTime is a per-subject categorical variable (yes/no) and EEG is recorded continuously with no trial-level event structure for this task, segmentation-based epoching is used to create multiple epochs per subject, all sharing the same label. The 4-second segment length with 50% overlap follows Category SKILL defaults for continuous EEG with no event markers. All segments from a given subject receive that subject's IsFirstTime value as label.

### Potential Task 7: Handedness classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | Handedness | left → 0, right → 1 (2-class binary classification) |
- **Evidence**:
- **Notes**: Subject-level demographic classification using continuous EEG segmented into 4-second windows. Handedness is a native participants.tsv column with complete coverage across all 50 subjects (values: left, right). This is a subject-level prediction task where all epochs from a given subject share the same label. Epoch parameters use Category SKILL defaults for segmentation-based epoching (4s segments, 50% overlap) as no event structure is needed for this subject-level paradigm.

### Potential Task 8: Gender classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | Gender | male=0, female=1 (binary classification; 2 classes) |
- **Evidence**:
  - participants.tsv — Gender column available for all 50 participants with values 'male' and 'female'
- **Notes**: Subject-level demographic classification using continuous EEG segmented into 4-second windows with 50% overlap. Each segment from a subject inherits the same gender label. Segmentation parameters inferred from Category SKILL defaults as no trial structure is required for this subject-level paradigm.

### Potential Task 9: StrokeLocation classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | StrokeLocation | Kernel maps each unique anatomical location string to a 0-based sequential integer class label. Observed values include: 'Left pons', 'Right pons', 'Left cerebellum, bilateral paraventricular, Right corona radiata', 'Left frontal parietal cortex, Left centrum semiovale', etc. Multi-class classification with ≥4 distinct stroke locations expected. |
- **Evidence**:
- **Notes**: Subject-level clinical characteristic classification. Since StrokeLocation is a native participants.tsv column (B3 archetype), no kernel derivation is needed for the label itself. The kernel only needs to map the categorical string values to sequential integer class labels. Segmentation-based epoching is used because this is a subject-level characteristic with no trial event structure — all segments from a subject share the same label.

### Potential Task 10: Duration regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | Duration | Numeric days post-stroke (range 1–14); subject-level continuous target assigned to all epochs from that participant |
- **Evidence**:
- **Notes**: Subject-level regression using continuous EEG segments. The `Duration` field from participants.tsv indicates days elapsed since stroke onset (range 1–14 days). Since this is a subject-level variable, all segmented epochs from a given participant share the same regression target. Segmentation parameters use Category SKILL defaults (4s windows, 50% overlap) as no trial-locked event structure is required for this subject-level clinical prediction task.

## Data Quality Notes

- No event structure exists in the dataset; all tasks rely on segmentation-based epoching of continuous resting-state EEG.
- Duplicate fields present: `age`/`Age`, `handedness`/`Handedness`, `sex`/`Gender` — these are exact duplicates and may cause confusion.
- `amplifier` field is missing from metadata despite equipment being known (Xian ZhenTec Intelligence ZhenTec NT1).
- `Duration` field units are unspecified in metadata (inferred as days post-stroke from clinical context but not explicitly documented).
- `StrokeLocation` contains comma-separated multiple locations for some patients, which may complicate multi-class classification if treated as a single label.
- Small sample size (N=50) with multiple clinical variables may lead to overfitting for machine learning tasks.
- No control/healthy subject group is present; all subjects are stroke patients.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
