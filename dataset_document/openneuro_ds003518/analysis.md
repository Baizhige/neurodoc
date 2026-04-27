# EEG: Simon Conflict with Reinforcement + Cabergoline Challenge

**Dataset**: `openneuro_ds003518` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003518
**Category**: High-level Mental | **Subjects**: 110 | **Files (Completed)**: 137 | **Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

This study examines whether conflict acts as an implicit cost in reinforcement learning using a modified Simon task with pharmacological manipulation. Healthy participants performed a Simon conflict task across training and test phases, with a double-blind Cabergoline (dopamine D2/D3 agonist) challenge administered to examine dopaminergic modulation. The training phase included reinforcement feedback to shape behavior; the test phase probed learned conflict avoidance. Mid-frontal theta and error-related negativity are key EEG measures.

## File Scan Result

> **Kernel SHA256**: `acb6b744009087a86d617f1b6e416921b67ad6d6365b12f26c4430057c8d8fe9`
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

### Potential Task 1: Regression of Subject Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18–30 (years) | Subject chronological age from participants.tsv; complete for all 110 subjects (Study 1: n=83, Study 2: n=27) |
- **Evidence**:
- **Notes**: Continuous EEG is segmented into 2-second non-overlapping windows for brain-age prediction. No event structure is required—each window inherits the subject's age as the regression target. This follows standard brain-age prediction setups where subject-level demographics are predicted from resting/task-continuous EEG features.

### Potential Task 2: 2-class sex classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | Male | 0 | Male subject |
  | sex | Female | 1 | Female subject |
- **Evidence**:
  - participants.tsv — N=110 subjects with complete sex information (46 Male, 64 Female)
- **Notes**: Subject-level sex classification from continuous EEG using 2-second non-overlapping windows. The sex field is a native participants.tsv column with two balanced classes, making this a straightforward demographic prediction benchmark. Segmentation allows the model to learn sex-differentiating spectral/spatial patterns across the continuous recording without event-locked constraints.

### Potential Task 3: 2-class study cohort
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Study`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Study | Study 1 | 0 | Study 1 cohort (behavioral + 5 placebo pilot, N=83, circa 2012-2013) |
  | Study | Study 2 | 1 | Study 2 cohort (cabergoline double-blind, N=27) |
- **Evidence**:
  - participants.tsv — Study column with values "Study 1" (N=83) and "Study 2" (N=27)
  - README — "Study 1: 80 healthy participants (2 removed) + 5 placebo session from a pilot of the drug study. Total n=83. Study 2: 30 healthy participants (3 dropout) in a double-blind drug study. Total n=27."
- **Notes**: Subject-level classification task predicting which study cohort a recording belongs to based on 2-second EEG segments. Study 1 and Study 2 represent different experimental designs (behavioral vs. cabergoline drug challenge), different sample sizes, and potentially different recording protocols/eras. The classification may capture systematic differences in EEG due to different study protocols, equipment calibration over time, or population differences.

### Potential Task 4: 2-class drug condition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sess1_Drug`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sess1_Drug | Placebo | 0 | Placebo session |
  | sess1_Drug | Cab | 1 | Cabergoline 1.25 mg |
- **Evidence**:
- **Notes**: Per-subject drug assignment from participants.tsv. Only 27/110 subjects (Study 2) have non-NaN values for sess1_Drug. Study 1 subjects have n/a in this field and must be excluded. The 2-second segmentation is a default choice for detecting pharmacological effects on continuous EEG; no event-locked design is used. The label is per-subject (not per-session), so all segments from a given subject share the same drug label. Subjects with sess1_Drug=Placebo received placebo in session 1 and cabergoline in session 2; subjects with sess1_Drug=Cab received cabergoline in session 1 and placebo in session 2. For this task we use only the session 1 drug assignment as the classification label.

### Potential Task 5: Continuous EEG Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–30.0 (years) | Subject chronological age from participants.tsv; all segments from a subject share the same age label |
- **Evidence**:
  - (none — Potential task)
- **Notes**: Archetype C variant of age regression using segmentation since no discriminating events exist for a subject-level continuous label. Continuous 2-second non-overlapping segments extracted from full recordings. Age is a native participants.tsv column (B3-equivalent info source), so Meta Level = raw per taxonomy (segmentation + info-native). The kernel does not need to derive any misc channel; it only needs to read the pre-existing `age` field from participants metadata and broadcast it to all segments per subject.

## Data Quality Notes

- Event structure table is empty in File Scan Result, indicating no event codes were successfully extracted or parsed from the dataset files.
- `device` field is completely missing from info metadata, limiting knowledge about EEG amplifier/equipment used across studies.
- Drug condition fields (`sess1_Drug`, `sess2_Drug`) are highly incomplete (27/110 subjects), restricting pharmacological analyses to Study 2 subset only.
- Study 1 and Study 2 have substantially different sample sizes (83 vs 27) and experimental designs, creating potential confounds for cross-study analyses.
- No known data quality issues for core demographic fields (`subject_age`, `subject_sex`, `Original_ID`, `Study`) which are all complete.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
