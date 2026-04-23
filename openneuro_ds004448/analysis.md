# The BMI-HDEEG dataset 4

**Dataset**: `openneuro_ds004448` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004448
**Category**: Action/Output | **Subjects**: 280 | **Files (Completed)**: 280 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants performed a sensorimotor rhythm-based brain-computer interface task using high-density scalp EEG. This is the fourth BMI-HDEEG dataset with a two-class (binary) motor imagery design (left hand vs. right hand). The experimental paradigm involved motor imagery training with neurofeedback components, where subjects alternated between performing motor imagery and relaxation/rest periods.

## File Scan Result

> **Kernel SHA256**: `d7835252d7ec39b9a16515aadeeb9bc140180770c47f49bd8295a2eb781df3cb`
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

### Classical Task 1: Age Regression from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 1 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 19.0–58.0 (years) | Subject chronological age from participants.tsv; all 56 subjects have complete age data |
- **Evidence**:
- **Notes**: Segmentation-based regression task using uniform 2-second windows with 50% overlap (1-second step). Each segment inherits the subject's age as the regression target. No event structure is required. The kernel segments continuous EEG and assigns the per-subject age value from participants.tsv to all segments from that subject.

### Classical Task 2: Gender Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 1.0 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | male | 0 | Male subject |
  | gender | female | 1 | Female subject |
- **Evidence**:
- **Notes**: Binary gender classification from continuous EEG segments. The 2-second windows with 50% overlap (1s step) are standard for subject-level demographic prediction. Class distribution is highly imbalanced (49 male vs 7 female, ~87.5% vs 12.5%); stratified sampling or class weighting is recommended for downstream training. The label is drawn from participants.tsv 'gender' column, a native info field requiring no kernel derivation.

### Classical Task 3: Handedness Classification from EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 1.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | right | 0 | right-handed |
  | handedness | left | 1 | left-handed |
- **Evidence**:
- **Notes**: Subject-level classification using 2-second non-overlapping EEG segments (1-second step). Handedness is a stable individual trait that may manifest in motor cortex asymmetry, particularly relevant given this motor imagery BCI dataset. The participants.tsv file confirms complete coverage of handedness labels (right/left) across all 56 subjects. No derived kernel computation needed — handedness is read directly from the native participants.tsv info field.

### Potential Task 1: Continuous Motor Imagery Segmentation with Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 1.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–58.0 (years) | Subject chronological age from participants.tsv; continuous label for age-related SMR dynamics regression |
- **Evidence**:
  - (empty — Potential task)
- **Notes**: Segmentation-based approach for continuous monitoring paradigm. Uses 2-second non-overlapping windows (overlap=1.0 means 100% overlap, i.e., sliding window with 1s step) across full continuous recording to capture alpha/beta SMR dynamics without event-locked constraints. Age label is native participants.tsv column, requiring no kernel derivation. The 128-channel HD-EEG at 1000 Hz provides spatial-spectral features for modeling age-related changes in motor cortex oscillatory activity.

### Potential Task 2: Continuous Motor Imagery Segmentation with Gender
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 1.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | male | 0 | Male subject |
  | gender | female | 1 | Female subject |
- **Evidence**:
  - participants.tsv — N=56 subjects with gender column (49 male, 7 female); directly readable from BIDS sidecar
- **Notes**: Segmentation-based approach: continuous 2-second windows (1-second step) from motor imagery recordings are labeled with subject gender. This explores whether sex differences in sensorimotor rhythm patterns are detectable during BCI tasks. Significant class imbalance (49:7) should be considered in model evaluation. No derived channels needed; gender is a native participants.tsv column.

## Data Quality Notes

- No event markers were detected in the file scan; the Event Structure table is empty, which conflicts with the draft's mention of trial start markers (event_1, event_2, event_3).
- The dataset reports 280 subjects in metadata but only 56 subjects have complete age, sex, and handedness data in participants.tsv, indicating substantial missing demographic information.
- Device information is completely missing from the info fields.
- Severe class imbalance exists for gender classification (49 male vs 7 female, ~87.5% vs 12.5%).
- The overlap parameter notation is inconsistent across tasks ("1 s" vs "1.0" vs "1.0 s"), though all appear to indicate 50% overlap (1-second step for 2-second windows).
- The Potential Task 1 notes incorrectly state "overlap=1.0 means 100% overlap" when it actually indicates 50% overlap (1-second step); this is a documentation error in the source material.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
