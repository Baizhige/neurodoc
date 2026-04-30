# EEG: Amphetamine trials 5CCPT and Probabilistic Learning

**Dataset**: `openneuro_ds003987` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003987
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 69 | **Channels**: 71 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

A double-blind, crossover pharmacological study investigating the effects of d-amphetamine on cognitive performance using two tasks: the 5-Choice Continuous Performance Task (5CCPT), which assesses sustained attention and impulsivity, and a Probabilistic Selection Task (PST), which measures reinforcement learning. EEG was recorded from 23 subjects across three drug sessions (placebo, low-dose, high-dose amphetamine), with recordings obtained using a 71-channel system at 500 Hz.

## File Scan Result

> **Kernel SHA256**: `bc63a5f872f1f40b4689a56d0f0ba55ae04ca1a92ffd323d0c337362d7eea0ed`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `21 5CCPT` | 16558 | event | raw | Task event marker: 5CCPT response code 21 |
| `22 5CCPT` | 9811 | event | raw | Task event marker: 5CCPT response code 22 |
| `23 5CCPT` | 9547 | event | raw | Task event marker: 5CCPT response code 23 |
| `25 5CCPT` | 4442 | event | raw | Task event marker: 5CCPT response code 25 |
| `unknown_1` | 263 | event | raw | Unmapped task event marker |
| `unknown_10` | 4130 | event | raw | Unmapped task event marker |
| `unknown_11` | 2388 | event | raw | Unmapped task event marker |
| `unknown_12` | 2290 | event | raw | Unmapped task event marker |
| `unknown_13` | 2378 | event | raw | Unmapped task event marker |
| `unknown_14` | 2369 | event | raw | Unmapped task event marker |
| `unknown_15` | 2389 | event | raw | Unmapped task event marker |
| `unknown_16` | 3459 | event | raw | Unmapped task event marker |
| `unknown_17` | 7445 | event | raw | Unmapped task event marker |
| `unknown_18` | 5055 | event | raw | Unmapped task event marker |
| `unknown_19` | 3745 | event | raw | Unmapped task event marker |
| `unknown_2` | 2482 | event | raw | Unmapped task event marker |
| `unknown_20` | 2383 | event | raw | Unmapped task event marker |
| `unknown_24` | 4804 | event | raw | Unmapped task event marker |
| `unknown_26` | 2094 | event | raw | Unmapped task event marker |
| `unknown_27` | 536 | event | raw | Unmapped task event marker |
| `unknown_28` | 888 | event | raw | Unmapped task event marker |
| `unknown_29` | 1643 | event | raw | Unmapped task event marker |
| `unknown_3` | 2481 | event | raw | Unmapped task event marker |
| `unknown_30` | 1905 | event | raw | Unmapped task event marker |
| `unknown_31` | 1534 | event | raw | Unmapped task event marker |
| `unknown_32` | 3526 | event | raw | Unmapped task event marker |
| `unknown_33` | 5216 | event | raw | Unmapped task event marker |
| `unknown_34` | 4554 | event | raw | Unmapped task event marker |
| `unknown_35` | 8011 | event | raw | Unmapped task event marker |
| `unknown_36` | 12776 | event | raw | Unmapped task event marker |
| `unknown_37` | 13916 | event | raw | Unmapped task event marker |
| `unknown_38` | 9213 | event | raw | Unmapped task event marker |
| `unknown_39` | 9749 | event | raw | Unmapped task event marker |
| `unknown_4` | 2481 | event | raw | Unmapped task event marker |
| `unknown_40` | 12868 | event | raw | Unmapped task event marker |
| `unknown_41` | 7943 | event | raw | Unmapped task event marker |
| `unknown_42` | 2919 | event | raw | Unmapped task event marker |
| `unknown_43` | 1022 | event | raw | Unmapped task event marker |
| `unknown_44` | 279 | event | raw | Unmapped task event marker |
| `unknown_45` | 199 | event | raw | Unmapped task event marker |
| `unknown_46` | 89 | event | raw | Unmapped task event marker |
| `unknown_47` | 29 | event | raw | Unmapped task event marker |
| `unknown_48` | 7 | event | raw | Unmapped task event marker |
| `unknown_5` | 2482 | event | raw | Unmapped task event marker |
| `unknown_6` | 2484 | event | raw | Unmapped task event marker |
| `unknown_7` | 2484 | event | raw | Unmapped task event marker |
| `unknown_8` | 7245 | event | raw | Unmapped task event marker |
| `unknown_9` | 4049 | event | raw | Unmapped task event marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 3-class drug dose classification (session-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `session`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | session | 1 | 0 | Placebo (Sess1_Drug) |
  | session | 2 | 1 | 10 mg d-amphetamine (Sess2_Drug) |
  | session | 3 | 2 | 20 mg d-amphetamine (Sess3_Drug) |
- **Evidence**:
  - 10.1038/s41398-021-01562-w — Pharmacological EEG study using counterbalanced amphetamine doses with session-level drug conditions
  - 10.1007/s00213-022-06082-z — D-amphetamine dose effects on EEG measures in 5CCPT paradigm
  - participants.tsv — Contains Sess1_Drug, Sess2_Drug, Sess3_Drug columns with counterbalanced Placebo/10 mg/20 mg conditions; session column maps to drug dose per subject
  - README — "3 drug conditions: placebo, 10mg, 20mg" with counterbalanced design across sessions
- **Notes**: The session number (1, 2, 3) serves as the info field label, with drug dose determined by cross-referencing the corresponding SessN_Drug column in participants.tsv. Since events.tsv files contain only untranslated trigger codes (65535, 65289) and lack the actual 5CCPT response markers, segmentation is used instead of event-based epoching. The kernel must map session→drug dose using the per-subject Sess1_Drug/Sess2_Drug/Sess3_Drug values.

### Potential Task 1: 2-class sex classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | female | 0 | Female subject |
  | sex | male | 1 | Male subject |
- **Evidence**:
- **Notes**: Subject-level biometric classification from resting/task EEG using demographic sex labels from participants.tsv. Segmentation creates multiple samples per subject across the continuous recording. Small sample size (N=23, 12 male / 11 female) makes this a challenging few-subject classification problem. All 3 sessions per subject (placebo, 10mg, 20mg amphetamine conditions) are pooled, with drug condition treated as uncontrolled variability.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0 – 35.0 (years) | Continuous demographic variable from participants.tsv; N=23 subjects, mean ~24.5 years. Narrow range in young adults may limit predictive power. |
- **Evidence**:
- **Notes**: Standard brain-age regression paradigm using sliding-window segmentation. Each 2-second EEG segment is labeled with the subject's chronological age from participants.tsv. Segmentation with 50% overlap maximizes training samples given continuous resting/task-state recordings. The relatively narrow age range (18-35 years) in this young-adult cohort constrains the regression problem compared to lifespan brain-age models.

### Potential Task 3: 3-class session number classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `session`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | session | 1 | 0 | First testing session |
  | session | 2 | 1 | Second testing session |
  | session | 3 | 2 | Third testing session |
- **Evidence**:
- **Notes**: Session values 1, 2, 3 are drawn directly from the native participants.tsv `session` column (sample values: [1, 2, 3]). The three sessions represent counterbalanced drug conditions (Placebo/10mg/20mg amphetamine) administered in different orders per subject. Since drug condition is counterbalanced, session number captures order/habituation effects rather than drug state, making this a control variable for practice and session-dependent EEG changes. Segmentation with 2s windows and 50% overlap provides sufficient samples for session-level classification while respecting the continuous recording structure.

## Data Quality Notes

- The vast majority of event markers (44 of 48 event types) are unmapped/unknown task event codes, severely limiting event-based epoching for task conditions.
- Only four 5CCPT event codes (21, 22, 23, 25) are identified, with no PST event markers explicitly mapped.
- The `device` info field is completely missing from metadata, preventing equipment verification.
- Events.tsv files reportedly contain untranslated trigger codes (65535, 65289) rather than the actual task condition markers, indicating a BIDS conversion or recording issue.
- Small sample size (N=23) limits statistical power for subject-level classification tasks.
- Counterbalanced drug design across sessions means session number and drug condition are confounded at the group level but decoupled within subjects.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
