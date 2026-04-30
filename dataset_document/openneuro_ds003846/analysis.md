# Prediction Error

**Dataset**: `openneuro_ds003846` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003846
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 50 | **Manual Review**:
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

A virtual reality haptic interaction study where participants reached out to touch spawned virtual boxes while receiving varied combinations of visual, vibrotactile, and electrical muscle stimulation (EMS) feedback. Trials were marked as "normal" (congruent feedback) or "conflict" (incongruent prediction error condition), allowing investigation of multisensory prediction error processing. Three feedback modality conditions were run in separate sessions: visual-only, vibrotactile-only, and combined EMS conditions.

## File Scan Result

> **Kernel SHA256**: `7f74f7e3fbcbc9c441066de0be6e0c963c61370c4444f4fd9b49517aa7134126`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 18.0–34.0 (years) | Continuous age of young adult participants; all 19 subjects have complete age data |
- **Evidence**:
- **Notes**: Segmentation-based approach with 4-second non-overlapping windows. No event structure required since age is a subject-level continuous variable. The narrow age range (18-34 years, young adults only) may limit prediction accuracy but provides a valid regression target. Each segment from a given subject receives the same age label, and the model must learn age-related spectral or spatial patterns from resting/task EEG dynamics.

### Potential Task 2: Cap Size Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `cap_size`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | cap_size | 54–60 (arbitrary cap size units) | Continuous integer cap sizes from participants.tsv; complete data for all 19 participants. Range is limited (7 unique values) but may capture brain size-related EEG variations. |
- **Evidence**:
  - participants.tsv — cap_size column with values 54–60, complete for all 19 participants
  - README — "Cap Size: Varied, with sizes ranging from 54 to 60"
- **Notes**: Segmentation-based subject-level regression. Each 4s non-overlapping segment from a subject's EEG is labeled with that subject's cap_size. Since cap_size is a between-subjects variable, the model must learn to predict a subject-level property from short EEG segments, making this a challenging methodological benchmark for EEG biomarker research.

### Potential Task 3: 2-class first block stimulation type
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `block_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | block_1 | Visual | 0 | Visual-only stimulation |
  | block_1 | Visual + Vibro | 1 | Visual plus vibrotactile stimulation |
- **Evidence**:
- **Notes**: Subject-level classification task predicting whether the first stimulation block used Visual-only or Visual+Vibro feedback. The block_1 column in participants.tsv contains the stimulation condition for each subject's first block. One subject (sub-04) has block_1=Visual, block_2=Visual + Vibro, block_3=0 (missing/invalid), confirming the two-class structure. The 4-second non-overlapping segmentation treats each subject's EEG recording as a bag of segments for subject-level prediction, with all segments from a subject sharing the same label. This is a simpler alternative to full protocol classification with larger per-class sample sizes (19 subjects total with block_1 data).

### Potential Task 4: continuous EEG segmentation with age labels
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–34.0 (years) | Subject chronological age from participants.tsv; N=19, complete coverage |
- **Evidence**:
  - participants.tsv — age column complete for all 19 subjects, range 18–34 years
  - README — "The study sample consists of 19 participants... with ages ranging from 18 to 34 years"
- **Notes**: Archetype C framing: continuous EEG segmentation without event-locked epochs, treating the task-embedded EEG as quasi-resting state for age biomarker development. Same age labels as B3 candidate but distinct conceptual framing emphasizing absence of discriminating events — useful for kernel builders developing age-prediction models independent of task structure. 10s segments with 50% overlap chosen to capture sufficient spectral features for continuous neural signal analysis.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
