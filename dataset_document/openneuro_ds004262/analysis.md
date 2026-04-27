# Continuous Feedback Processing

**Dataset**: `openneuro_ds004262` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004262
**Category**: High-level Mental | **Subjects**: 21 | **Files (Completed)**: 21 | **Channels**: 31 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants predicted the final height of an animated rising bar based on cues with varying predictability to study continuous feedback processing and prediction error. Each trial involved observing bar motion and registering a prediction, allowing examination of EEG correlates of reward prediction error and uncertainty-driven learning. The experiment used 36 distinct stimulus subtypes encoding six levels of cue predictability (6 conditions × 6 repetitions per block).

## File Scan Result

> **Kernel SHA256**: `9701d09920a9a5e5312b7d7b3075acbfec9ac35a59e2b68bca56bb14a611a9e6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Comment/Active Shielding: On` | 21 | admin | raw | System marker: Active shielding enabled |
| `Stimulus/S  1` | 525 | event | raw | Trial phase onset: Condition 1 fixation cross |
| `Stimulus/S  2` | 525 | event | raw | Trial phase onset: Condition 2 fixation cross |
| `Stimulus/S  3` | 525 | event | raw | Trial phase onset: Condition 3 fixation cross |
| `Stimulus/S  4` | 525 | event | raw | Trial phase onset: Condition 4 fixation cross |
| `Stimulus/S  5` | 525 | event | raw | Trial phase onset: Condition 5 fixation cross |
| `Stimulus/S  6` | 525 | event | raw | Trial phase onset: Condition 6 fixation cross |
| `Stimulus/S 11` | 525 | event | raw | Trial phase onset: Condition 1 cue |
| `Stimulus/S 12` | 525 | event | raw | Trial phase onset: Condition 2 cue |
| `Stimulus/S 13` | 525 | event | raw | Trial phase onset: Condition 3 cue |
| `Stimulus/S 14` | 525 | event | raw | Trial phase onset: Condition 4 cue |
| `Stimulus/S 15` | 525 | event | raw | Trial phase onset: Condition 5 cue |
| `Stimulus/S 16` | 525 | event | raw | Trial phase onset: Condition 6 cue |
| `Stimulus/S 21` | 525 | event | raw | Trial phase onset: Condition 1 bar |
| `Stimulus/S 22` | 525 | event | raw | Trial phase onset: Condition 2 bar |
| `Stimulus/S 23` | 525 | event | raw | Trial phase onset: Condition 3 bar |
| `Stimulus/S 24` | 525 | event | raw | Trial phase onset: Condition 4 bar |
| `Stimulus/S 25` | 525 | event | raw | Trial phase onset: Condition 5 bar |
| `Stimulus/S 26` | 525 | event | raw | Trial phase onset: Condition 6 bar |
| `Stimulus/S 31` | 525 | event | raw | Trial phase onset: Condition 1 response |
| `Stimulus/S 32` | 525 | event | raw | Trial phase onset: Condition 2 response |
| `Stimulus/S 33` | 525 | event | raw | Trial phase onset: Condition 3 response |
| `Stimulus/S 34` | 525 | event | raw | Trial phase onset: Condition 4 response |
| `Stimulus/S 35` | 525 | event | raw | Trial phase onset: Condition 5 response |
| `Stimulus/S 36` | 525 | event | raw | Trial phase onset: Condition 6 response |
| `Stimulus/S 41` | 525 | event | raw | Trial phase onset: Condition 1 animation start |
| `Stimulus/S 42` | 525 | event | raw | Trial phase onset: Condition 2 animation start |
| `Stimulus/S 43` | 525 | event | raw | Trial phase onset: Condition 3 animation start |
| `Stimulus/S 44` | 525 | event | raw | Trial phase onset: Condition 4 animation start |
| `Stimulus/S 45` | 525 | event | raw | Trial phase onset: Condition 5 animation start |
| `Stimulus/S 46` | 525 | event | raw | Trial phase onset: Condition 6 animation start |
| `Stimulus/S 51` | 525 | event | raw | Trial phase onset: Condition 1 animation end |
| `Stimulus/S 52` | 525 | event | raw | Trial phase onset: Condition 2 animation end |
| `Stimulus/S 53` | 525 | event | raw | Trial phase onset: Condition 3 animation end |
| `Stimulus/S 54` | 525 | event | raw | Trial phase onset: Condition 4 animation end |
| `Stimulus/S 55` | 525 | event | raw | Trial phase onset: Condition 5 animation end |
| `Stimulus/S 56` | 525 | event | raw | Trial phase onset: Condition 6 animation end |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 6-class cue predictability classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 13`, `Stimulus/S 14`, `Stimulus/S 15`, `Stimulus/S 16`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 11` | 0 | Condition 1 cue: highly predictable - consistently low |
  | `Stimulus/S 12` | 1 | Condition 2 cue: highly predictable - consistently high |
  | `Stimulus/S 13` | 2 | Condition 3 cue: unpredictable - low or high with equal probability |
  | `Stimulus/S 14` | 3 | Condition 4 cue: somewhat predictable - usually (80%) low |
  | `Stimulus/S 15` | 4 | Condition 5 cue: somewhat predictable - usually (80%) high |
  | `Stimulus/S 16` | 5 | Condition 6 cue: unpredictable - random uniform distribution |
- **Evidence**:
  - 10.1101/2022.10.06.511117 — 6-condition predictability manipulation with cue onset events S11-S16 representing different gnome cue types
  - 10.1111/psyp.14399 — Published version confirming 525 trials per condition and cue-based predictability paradigm
  - sub-01_task-gnomes_events.json / sub-02_task-gnomes_events.json — BIDS sidecar confirming S11-S16 map to Condition 1-6 cues respectively
  - README — Confirms cue duration 1500ms, condition descriptions, and trigger modifier +10 for cue onset
- **Notes**: tmin/tmax inferred from README cue duration (1500ms) and standard ERP practice to include pre-cue baseline; references primarily use continuous regression approaches rather than discrete epoching, so window parameters are marked as inferred.

### Classical Task 2: 2-class predictable vs unpredictable
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 13`, `Stimulus/S 14`, `Stimulus/S 15`, `Stimulus/S 16`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 23`, `Stimulus/S 24`, `Stimulus/S 25`, `Stimulus/S 26`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 13`, `Stimulus/S 16`, `Stimulus/S 23`, `Stimulus/S 26` | 0 | unpredictable (conditions 3,6) |
  | `Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 14`, `Stimulus/S 15`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 24`, `Stimulus/S 25` | 1 | predictable (conditions 1,2,4,5) |
- **Evidence**:
  - 10.1101/2022.10.06.511117 — Binary predictability contrast central to RPE analysis; conditions 1,2,4,5 predictable vs conditions 3,6 unpredictable
  - 10.1111/psyp.14399 — Published version confirming same 2-class grouping for reward prediction error hypothesis testing
- **Notes**: Cue-locked epoching at gnome onset (S11-S16). The binary predictability contrast is fundamental to the study's design: conditions 1,2,4,5 have some degree of outcome predictability (highly or somewhat predictable), while conditions 3,6 are unpredictable. Event IDs S21-S26 (bar onset) are also included as valid anchors since they carry the same condition information and may be used for alternative phase-locking; however, the primary epoching targets are cue onsets. All target events are confirmed present in the dataset's event structure with 525 occurrences each.

### Classical Task 3: cue-locked SPN amplitude regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 13`, `Stimulus/S 14`, `Stimulus/S 15`, `Stimulus/S 16`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |----------|-------|---------|
  | Stimulus/S 11 | 0 | Condition 1 cue (highly predictable - consistently low) |
  | Stimulus/S 12 | 1 | Condition 2 cue (highly predictable - consistently high) |
  | Stimulus/S 13 | 2 | Condition 3 cue (unpredictable - low or high equal probability) |
  | Stimulus/S 14 | 3 | Condition 4 cue (somewhat predictable - usually low) |
  | Stimulus/S 15 | 4 | Condition 5 cue (somewhat predictable - usually high) |
  | Stimulus/S 16 | 5 | Condition 6 cue (unpredictable - random uniform) |
- **Evidence**:
  - 10.1101/2022.10.06.511117 — SPN component isolation from continuous reward cue periods; SPN is slow negative potential ramping during cue period predicting upcoming reward magnitude
  - 10.1111/psyp.14399 — SPN measured during cue period as core neural signature for reward prediction; cue-locked epochs capture SPN ramping amplitude
- **Notes**: The target is a continuous regression value representing SPN amplitude at each timepoint within the cue-locked epoch. The six cue conditions (S11-S16) serve as event anchors for epoching; the regression target is the EEG amplitude itself (the SPN), not the condition label. The SPN is measured as the slow negative potential developing during the 1500 ms cue period, with -500 ms capturing any pre-cue fixation carryover baseline. This follows the standard SPN analysis approach where the dependent measure is the continuous amplitude of the negative ramp, typically quantified as mean amplitude over the cue window or extracted as single-trial time-series for regression.

### Potential Task 1: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 21.0–41.0 (years) | Subject-level biomarker; all 21 subjects have complete age data in participants.tsv. Each segment from a subject receives the same age label. |
- **Evidence**:
- **Notes**: Pure subject-level regression task using segmented continuous EEG to predict chronological age. No event structure is leveraged—instead, the continuous recording is divided into 2-second non-overlapping windows (with 50% overlap) and each window is labeled with the subject's age from participants.tsv. This serves as a brain-age estimation baseline. Epoch parameters inferred from standard segmentation practices for subject-level biomarker tasks.

### Potential Task 2: Sex Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level biomarker task using segmented continuous EEG (2s windows, 50% overlap) to classify sex from resting/task-contaminated continuous recordings. Class imbalance is notable (16 F, 5 M). The info field 'sex' is native to participants.tsv with complete coverage across all 21 subjects. Segmentation parameters are inferred from standard practice for subject-level classification with continuous data.

### Potential Task 3: handedness classification from continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | R | 0 | right-handed |
  | handedness | L | 1 | left-handed |
- **Evidence**:
- **Notes**: Subject-level biomarker task using 2-second non-overlapping windows of continuous EEG to predict handedness from participants.tsv. Severe class imbalance (18 right-handed vs 3 left-handed). segment_length and overlap inferred from standard practice for subject-level classification with continuous EEG; no trial structure is leveraged.

### Potential Task 4: Fixation-Locked Baseline Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 0.5 s *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`, `Stimulus/S  4`, `Stimulus/S  5`, `Stimulus/S  6`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | Condition 1 fixation cross (highly predictable - consistently low) |
  | `Stimulus/S  2` | 1 | Condition 2 fixation cross (highly predictable - consistently high) |
  | `Stimulus/S  3` | 2 | Condition 3 fixation cross (unpredictable - low or high equal probability) |
  | `Stimulus/S  4` | 3 | Condition 4 fixation cross (somewhat predictable - usually low) |
  | `Stimulus/S  5` | 4 | Condition 5 fixation cross (somewhat predictable - usually high) |
  | `Stimulus/S  6` | 5 | Condition 6 fixation cross (unpredictable - random uniform) |
- **Evidence**:
- **Notes**: This task tests whether preparatory neural activity during the fixation period (400-600ms) differs across the 6 gnome condition types before any cue information is presented. The 6 conditions represent different predictability structures of the upcoming feedback. Epoch parameters marked with * are inferred from the stated fixation duration of 400-600ms; 500ms window captures the full fixation period.

### Potential Task 5: animation-locked feedback processing classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 3 s *, overlap = 0 *, target_events = [`Stimulus/S 41`, `Stimulus/S 42`, `Stimulus/S 43`, `Stimulus/S 44`, `Stimulus/S 45`, `Stimulus/S 46`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 41` | 0 | Condition 1 animation start (highly predictable - consistently low) |
  | `Stimulus/S 42` | 1 | Condition 2 animation start (highly predictable - consistently high) |
  | `Stimulus/S 43` | 2 | Condition 3 animation start (unpredictable - low or high equal) |
  | `Stimulus/S 44` | 3 | Condition 4 animation start (somewhat predictable - usually low) |
  | `Stimulus/S 45` | 4 | Condition 5 animation start (somewhat predictable - usually high) |
  | `Stimulus/S 46` | 5 | Condition 6 animation start (unpredictable - random uniform) |
- **Evidence**:
- **Notes**: Long-event epoching from animation onset captures the continuous visual feedback period during which the bar rises. The 6 conditions differ in their temporal dynamics of prediction error based on prior learned expectations. The 3-second window captures the typical rising period (animation speed: 1 degree/second). Overlap=0 for non-overlapping long epochs. This task is distinct from RPE regression by using discrete condition labels rather than continuous reward prediction error values.

### Potential Task 6: Subject-Level Continuous EEG Segmentation with Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | age | 21.0–41.0 (years) | Subject chronological age from participants.tsv; each 2-second segment inherits the subject's age label |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Continuous EEG recordings are segmented into non-overlapping/overlapping 2-second windows (50% overlap) to create multiple samples per subject. Each segment is labeled with the subject's age from participants.tsv, enabling regression models to learn age-related EEG biomarkers from resting/task-continuous data. This differs from B3 whole-recording regression by explicitly using segmentation to increase sample size. Parameters marked with * are inferred from standard continuous EEG segmentation practices for subject-level prediction tasks.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
