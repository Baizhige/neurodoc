# EEG, pupillometry, ECG and photoplethysmography, and behavioral data in the digit span task

**Dataset**: `openneuro_ds003838` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003838/versions/1.0.0
**Category**: High-level Mental | **Subjects**: 86 | **Files (Completed)**: 296 | **Channels**: 2 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants performed a classic digit span working memory task involving serial recall of digit sequences of 5, 9, or 13 digits, along with a separate eyes-closed resting state condition. Each digit in a sequence was marked with an event indicating the digit position, sequence length, and whether it was later correctly recalled or forgotten. The dataset also includes ECG/PPG physiological signals recorded simultaneously with EEG.

## File Scan Result

> **Kernel SHA256**: `72be9b71cff9d332c437c15932ff7b2710ac85e0f5b790a157ad8c3103e48c46`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `[98]` | 8 | event | raw |  |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `PPG` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `PPG`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0 – 44.0 (years) | Continuous age from participants.tsv; all 86 subjects have complete age data |
- **Evidence**:
- **Notes**: Standard segmentation approach for subject-level regression. Continuous EEG is divided into 4-second windows with 50% overlap; each window inherits the subject's age from participants.tsv as the regression target. No event structure is required since this is a subject-level biomarker prediction task.

### Potential Task 2: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | f | 0 | female |
  | sex | m | 1 | male |
- **Evidence**:
  - participants.tsv — N=86 subjects with complete sex data: 74 female (f), 12 male (m)
- **Notes**: Standard segmentation approach for subject-level demographic classification. 4-second non-overlapping/overlapping windows are extracted from continuous EEG and labeled with the subject's sex from participants.tsv. Class imbalance is notable (86% female, 14% male) but the task remains valid with two distinct classes. The epoch parameters are inferred from standard practice for subject-level prediction tasks since no specific segmentation parameters are documented in the dataset.

### Potential Task 3: NASA cognitive workload regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `NASA_cog_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | NASA_cog_1 | 0–20 (score) | NASA-TLX cognitive subscale rating from first administration (pre-task); higher values indicate greater subjective mental workload |
- **Evidence**:
  - participants.tsv — NASA_cog_1 column contains complete cognitive workload ratings for all 86 subjects (sample values: 15, 13, 16)
  - Pavlov et al. (2022) Scientific Data — dataset paper describing NASA-TLX workload assessments alongside EEG, pupillometry, and cardiovascular measures in digit span task
- **Notes**: Segmentation-based regression: 4-second non-overlapping/overlapping EEG windows are mapped to subject-level NASA-TLX cognitive workload rating. Since this is a trait-level prediction (one rating per subject), all windows from a given subject share the same regression target. The epoch parameters are inferred from the candidate's epoch_hint for continuous EEG segmentation suitable for subject-level trait regression.

### Potential Task 4: NASA Physical Demand Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `NASA_phys_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | NASA_phys_1 | 0–20 (Likert scale) | First administration of NASA-TLX physical demand subscale; complete across all 86 participants. Higher values indicate greater subjective physical exertion during the digit span task. |
- **Evidence**:
  - Pavlov et al. (2022) — NASA-TLX workload ratings collected at three timepoints during the experiment; physical demand subscale used to assess subjective physical exertion
- **Notes**: Segmentation-based regression approach: continuous EEG is divided into 4-second non-overlapping/overlapping windows, with each window assigned the subject-level NASA_phys_1 rating. This treats physical demand as a stable trait measure per subject rather than a time-varying state. The 4s segment length is inferred from the need to obtain sufficient samples for subject-level regression while maintaining reasonable stationarity; overlap of 0.5 increases sample count for model training.

### Potential Task 5: NASA performance regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `NASA_perf_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | NASA_perf_1 | 0–20 (score) | NASA-TLX performance subscale rating from first timepoint; higher = better self-assessed performance |
- **Evidence**:
- **Notes**: Segmentation-based regression: 4-second EEG windows are extracted from continuous recordings and mapped to the subject-level NASA-TLX performance rating. The overlap of 0.5 yields multiple segments per subject, all sharing the same performance score. This creates a subject-level trait regression task where the model learns to predict subjective performance self-assessment from spontaneous/resting EEG patterns. The kernel does not need to derive any new channels—NASA_perf_1 is a native participants.tsv column.

### Potential Task 6: NASA effort regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `NASA_effort_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | NASA_effort_1 | 1–20 (Likert scale) | NASA-TLX effort subscale, first timepoint; subjective effort expenditure rating |
- **Evidence**:
- **Notes**: Segmentation-based regression: 4-second EEG windows are extracted from continuous recordings and mapped to the subject-level NASA-TLX effort rating. This treats effort as a stable trait measure across the session rather than a time-varying state. The overlap of 0.5 increases the number of training samples per subject. Since tmin/tmax are not applicable to segmentation, segment_length and overlap were taken from the epoch_hint (inferred=true, marked with *).

### Potential Task 7: NASA frustration regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `NASA_dissap_1`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | NASA_dissap_1 | 1–20 ( Likert scale ) | NASA-TLX frustration/disappointment subscale, first timepoint; higher = more frustrated |
- **Evidence**:
  - participants.tsv — NASA_dissap_1 complete for all 86 subjects (sample values: 12, 16, 8, 18, 1, 18, 12)
- **Notes**: Segmentation-based regression: continuous EEG is sliced into 4-second non-overlapping/overlapping windows, each mapped to the subject-level NASA frustration rating. This yields a subject-level trait regression task where the model learns to predict self-reported frustration from resting-state or task EEG patterns.

### Potential Task 8: Handedness Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `hand`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | hand | r | 0 | right-handed |
  | hand | l | 1 | left-handed |
  | hand | b | 2 | ambidextrous (both) |
- **Evidence**:
- **Notes**: Segmentation-based subject-level classification: 4-second non-overlapping windows are extracted from continuous EEG and labeled by the subject's handedness from participants.tsv. The `*` on segment_length indicates this was inferred from the epoch hint (no explicit domain default exists for handedness classification). All three handedness categories (r, l, b) are present in the dataset with complete coverage across N=86 subjects.

### Potential Task 9: Eye Dominance Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `eye`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | eye | r | 0 | right eye dominant |
  | eye | l | 1 | left eye dominant |
- **Evidence**:
  - participants.tsv — Column `eye` contains categorical values 'r' (right) and 'l' (left) for all 86 subjects, enabling binary subject-level classification from segmented EEG
- **Notes**: Segmentation-based approach for subject-level phenotyping: continuous EEG is sliced into 4-second windows with 50% overlap, each window inheriting the subject's eye dominance label from participants.tsv. This treats eye dominance as a stable trait to be decoded from resting-state or task EEG patterns. No kernel derivation needed—label is native to the info file.

### Potential Task 10: Resting State Segmentation with Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–44.0 (years) | Continuous age from participants.tsv; all 86 subjects have complete age data |
- **Evidence**:
- **Notes**: Archetype C (segmentation + info-native). Continuous 4-minute eyes-closed resting-state EEG is segmented into 4-second non-overlapping windows with 50% overlap. No event-based labels exist for rest segments, so segmentation is used with subject age as the continuous regression target. Age is a native participants.tsv column (Meta Level = raw). Segment length of 4s is standard for resting-state EEG feature extraction; overlap of 0.5 maximizes data usage for regression. The 4-minute recording duration yields approximately 120 segments per subject (240 with overlap), providing substantial sample size for age prediction models.

### Potential Task 11: Resting State Segmentation with Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | m | 0 | male |
  | sex | f | 1 | female |
- **Evidence**:
  - participants.tsv — sex column with complete coverage (N=86: 12 male, 74 female)
  - README — describes 4 minutes of eyes-closed resting state EEG data
- **Notes**: Standard resting-state segmentation approach: continuous 4-minute eyes-closed rest EEG is divided into 4-second non-overlapping or overlapping windows. Since no event-based labels exist for rest segments, archetype C (segmentation + info-native) is used with subject sex as the binary classification target. This is a common biomarker benchmark for resting-state EEG. Segment length and overlap are inferred from standard resting-state analysis conventions.

### Potential Task 12: data quality exclusion prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `EEG_excluded`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | EEG_excluded | no | 0 | EEG retained for analysis |
  | EEG_excluded | yes | 1 | EEG excluded due to poor signal quality |
- **Evidence**:
- **Notes**: Subject-level binary classification predicting EEG quality exclusion. Since participants.tsv provides EEG_excluded for all 86 subjects, each 4-second segmented window from a subject's recording inherits the same label. The majority class is 'yes' (excluded), making this an imbalanced quality-control prediction task. Segment length and overlap are inferred from the epoch hint for subject-level classification with segmentation.

## Data Quality Notes

- Event structure shows only a single generic event ID `[98]` with 8 total occurrences across all files, indicating event metadata is not fully parsed or the digit span trial markers are stored in a format not captured by the current scan.
- The Tasks section describes rich event-based tasks (correct vs error memory encoding, working memory load classification) but the File Scan Result does not confirm the presence of these event codes in the parsed data; event parsing may require kernel update or manual inspection.
- Device information is completely missing from info fields, limiting hardware provenance documentation.
- NASA_phys_3 field has partial completeness (85/86 subjects), leaving one missing value for physical demand at the third timepoint.
- PPG channel is present as a native MISC channel but requires verification of channel role and unit for proper physiological interpretation.
- EEG_excluded field indicates some subjects were excluded from EEG analysis due to poor signal quality; users should consider filtering on this field or using it as a quality control prediction target.
- The dataset contains only 2 EEG channels, which is unusually sparse for typical EEG analysis and may limit spatial resolution of neural signatures.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
