# EEG: Electrophysiological Biomarkers of Behavioral Dimensions from Cross-Species Paradigms

**Dataset**: `openneuro_ds003638` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003638
**Category**: High-level Mental | **Subjects**: 57 | **Files (Completed)**: 57 | **Channels**: 73 | **Sampling Rate**: 512 Hz
**Manual Review**:

## Paradigm

This study employs three cross-species behavioral paradigms (5-Choice Continuous Performance Task [5CCPT], Probabilistic Reward/Punishment task [PRBP], and Pavlovian-to-Instrumental Transfer [PST]) to identify electrophysiological biomarkers associated with various behavioral dimensions including attention, impulsivity, and reward sensitivity. All 57 subjects completed all three paradigms in a single session. Stimulus events are encoded as numeric trigger codes with behavioral responses marked by dedicated event codes. EEG was recorded with 73 channels at 512 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `c2a2ef344f6f244253df13aa1d78c12743cd86515c5af5512f519c499626be7d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_130816` | 166 | admin | raw | System status marker: recording boundary or session state (STATUS with value 65280 in lower 8 bits, variant 0) |
| `event_131070` | 170 | admin | raw | System status marker: recording boundary or session state (STATUS with value 65278 in lower 8 bits, variant 254) |
| `event_131071` | 1 | admin | raw | System status marker: recording boundary or session state (STATUS with value 65279 in lower 8 bits, variant 255) |
| `event_65281` | 1476 | event | raw | 5CCPT: Go stimulus 1 onset |
| `event_65282` | 1475 | event | raw | 5CCPT: Go stimulus 2 onset |
| `event_65283` | 1476 | event | raw | 5CCPT: Go stimulus 3 onset |
| `event_65284` | 1475 | event | raw | 5CCPT: Go stimulus 4 onset |
| `event_65285` | 1476 | event | raw | 5CCPT: Go stimulus 5 onset |
| `event_65286` | 1476 | event | raw | 5CCPT: NoGo stimulus onset |
| `event_65287` | 2911 | event | raw | 5CCPT: Mask onset (easy/unmasked condition, trigger 7) |
| `event_65291` | 1355 | event | raw | 5CCPT: Go Response Hit (correct response to Go stimulus 1) |
| `event_65292` | 1254 | event | raw | 5CCPT: Go Response Hit (correct response to Go stimulus 2) |
| `event_65293` | 1371 | event | raw | 5CCPT: Go Response Hit (correct response to Go stimulus 3) |
| `event_65294` | 1325 | event | raw | 5CCPT: Go Response Hit (correct response to Go stimulus 4) |
| `event_65295` | 1338 | event | raw | 5CCPT: Go Response Hit (correct response to Go stimulus 5) |
| `event_65301` | 2006 | event | raw | 5CCPT: Instant Go Response (response code 21) |
| `event_65302` | 4427 | event | raw | 5CCPT: Mask onset (hard/masked condition, trigger 22) |
| `event_65303` | 2859 | event | raw | 5CCPT: Instant Go Response (response code 23) |
| `event_65305` | 2126 | event | raw | 5CCPT: Instant Go Response (response code 25) |
| `event_65310` | 1412 | event | raw | 5CCPT: NoGo Non-Response Correct Rejection (CR) |
| `event_65311` | 8199 | event | raw | PST: Image pair displayed (Probabilistic Learning trial onset) |
| `event_65312` | 4865 | event | raw | PST: Correct feedback onset |
| `event_65313` | 38 | event | raw | PST: Block or condition marker (trigger 33, block-related) |
| `event_65316` | 12 | event | raw | PST: Block or condition marker (trigger 36) |
| `event_65319` | 3323 | event | raw | PST: Block or condition marker (trigger 39, Incorrect feedback or block identifier) |
| `event_65320` | 3936 | event | raw | PST: Incorrect feedback onset (trigger 40, variant) |
| `event_65321` | 90 | event | raw | PST: Block or condition marker (trigger 41) |
| `event_65322` | 37 | event | raw | PST: Block or condition marker (trigger 42) |
| `event_65323` | 54 | event | raw | PST: Block or condition marker (trigger 43) |
| `event_65324` | 44 | event | raw | PST: Block or condition marker (trigger 44) |
| `event_65325` | 47 | event | raw | PST: Block or condition marker (trigger 45) |
| `event_65326` | 1487 | event | raw | 5CCPT: False alarm to NoGo stimulus (incorrect response, trigger 46) |
| `event_65327` | 1487 | event | raw | 5CCPT: False alarm to NoGo stimulus (incorrect response, trigger 47) |
| `event_65330` | 1826 | event | raw | 5CCPT: False alarm to NoGo stimulus (incorrect response, trigger 50) |
| `event_65336` | 979 | event | raw | 5CCPT: Incorrect response to Go stimulus (trigger 56) |
| `event_65337` | 981 | event | raw | 5CCPT: Incorrect response to Go stimulus (trigger 57) |
| `event_65338` | 2 | event | raw | 5CCPT: Incorrect response to Go stimulus (trigger 58, rare) |
| `event_65339` | 623 | event | raw | 5CCPT: Incorrect response to Go stimulus (trigger 59) |
| `event_65340` | 641 | event | raw | 5CCPT: Incorrect response to Go stimulus (trigger 60) |
| `event_65341` | 3 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 61, rare) |
| `event_65342` | 3 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 62, rare) |
| `event_65343` | 45 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 63) |
| `event_65344` | 3 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 64, rare) |
| `event_65345` | 3 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 65, rare) |
| `event_65346` | 602 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 66) |
| `event_65347` | 603 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 67) |
| `event_65349` | 204 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 69) |
| `event_65360` | 425 | event | raw | 5CCPT: Go Non-Response Miss (omitted response to Go stimulus, trigger 80) |
| `event_65361` | 1679 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 81) |
| `event_65362` | 1232 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 82) |
| `event_65363` | 1496 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 83) |
| `event_65364` | 581 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 84) |
| `event_65366` | 834 | event | raw | 5CCPT: False alarm to NoGo stimulus (trigger 86) |
| `event_65396` | 22281 | event | raw | PRBP: 1 second clock tick (trial timing marker) |
| `event_65397` | 14138 | event | raw | PRBP: Visual feedback to every third response |
| `event_65398` | 370 | event | raw | PRBP: Sloppy responding feedback, start of 2 second timeout |
| `event_65399` | 370 | event | raw | PRBP: Restoration of normal screen |
| `event_65401` | 322 | event | raw | PRBP: Level complete reward display |
| `event_65402` | 322 | event | raw | PRBP: Level complete reward display offset |
| `event_65406` | 1 | event | raw | PRBP: Task marker (trigger 126, rare) |
| `event_65407` | 1 | event | raw | PRBP: Task marker (trigger 127, rare) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age regression from continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 18.0–35.0 (years) | Continuous age from participants.tsv; all 57 subjects have complete age data |
- **Evidence**:
  - participants.tsv — age column contains continuous values 18.0–35.0 for all 57 subjects
- **Notes**: Standard resting-state segmentation approach for subject-level biomarker regression. Since this is a continuous recording with no discriminating rest-specific events, the full continuous EEG is segmented into 2-second non-overlapping windows (50% overlap) and each window inherits the subject's age label from participants.tsv. Archetype B3 (native info field) requires no kernel derivation.

### Potential Task 2: Sex classification from continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level binary classification using resting-state segmentation. 2-second non-overlapping windows (50% overlap) are extracted from continuous EEG and labeled by the participant's sex from participants.tsv. This is a demographic prediction task rather than a task-evoked paradigm; all task events are ignored and the continuous recording is treated as a source of stable subject-level EEG features.

### Potential Task 3: Subject ID prediction from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `UH2_ID`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | UH2_ID | 1 | 0 | Subject 001 |
  | UH2_ID | 2 | 1 | Subject 002 |
  | UH2_ID | 3 | 2 | Subject 003 |
  | UH2_ID | ... | ... | ... |
  | UH2_ID | 57 | 56 | Subject 057 |
- **Evidence**:
- **Notes**: 57-class subject identification from continuous resting-state EEG segments. UH2_ID is a native participants.tsv column (1-57). Each subject's continuous EEG is segmented into 2-second windows with 50% overlap, creating multiple samples per subject. This is a common biometric/deep learning benchmark for EEG-based subject identification. The 57 classes are balanced at the subject level (one subject per class), though segment counts may vary slightly by recording duration. Classification targets are 0-based sequential integers mapping directly to UH2_ID values (y = UH2_ID - 1).

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
