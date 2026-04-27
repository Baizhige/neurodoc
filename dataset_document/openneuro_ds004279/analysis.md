# Large Spanish EEG

**Dataset**: `openneuro_ds004279` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004279
**Category**: High-level Mental | **Subjects**: 56 | **Files (Completed)**: 60 | **Channels**: 69 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

Participants performed speech perception and silent speech production tasks involving 30 daily Spanish sentences. Each sentence trial followed a fixed structure: a rest period, a preparation cue, a perception phase (hearing the sentence), and a production phase (silently producing the sentence). The study investigated EEG correlates of perceived and silently produced speech.

## File Scan Result

> **Kernel SHA256**: `d659db75b998c95432f7d5ce269d3ecd21ea826dbc6fd3871b395d5a8727414a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 370 | admin | raw | Impedance test onset |
| `10` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 10) |
| `11` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 11) |
| `12` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 12) |
| `13` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 13) |
| `14` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 14) |
| `15` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 15) |
| `16` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 16) |
| `17` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 17) |
| `18` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 18) |
| `19` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 19) |
| `2` | 370 | event | raw |  |
| `20` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 20) |
| `21` | 371 | event | raw | Trial phase onset: perception (sentence stimulus ID 21) |
| `22` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 22) |
| `23` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 23) |
| `24` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 24) |
| `25` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 25) |
| `26` | 365 | event | raw | Trial phase onset: perception (sentence stimulus ID 26) |
| `27` | 65 | event | raw | Trial phase onset: perception (sentence stimulus ID 27) |
| `28` | 60 | event | raw | Trial phase onset: perception (sentence stimulus ID 28) |
| `29` | 60 | event | raw | Trial phase onset: perception (sentence stimulus ID 29) |
| `3` | 370 | admin | raw | Bad artifact marker onset |
| `30` | 10921 | event | raw | Trial phase onset: preparation (sentence stimulus ID 0) |
| `31` | 11100 | event | raw | Trial phase onset: perception (sentence stimulus ID 31) |
| `32` | 11100 | event | raw | Trial phase onset: perception (sentence stimulus ID 32) |
| `33` | 544 | event | raw | Trial phase onset: perception (sentence stimulus ID 33) |
| `34` | 10926 | event | raw | Trial phase onset: preparation (sentence stimulus ID 4) |
| `35` | 298 | event | raw | Trial phase onset: perception (sentence stimulus ID 35) |
| `36` | 366 | event | raw | Trial phase onset: preparation (sentence stimulus ID 6) |
| `37` | 370 | event | raw | Trial phase onset: preparation (sentence stimulus ID 7) |
| `38` | 370 | event | raw | Trial phase onset: preparation (sentence stimulus ID 8) |
| `39` | 125 | event | raw | Trial phase onset: perception (sentence stimulus ID 39) |
| `4` | 370 | admin | raw | Pre-experiment bad period onset |
| `40` | 2 | event | raw | Trial phase onset: preparation (sentence stimulus ID 10) |
| `5` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 5) |
| `6` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 6) |
| `7` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 7) |
| `8` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 8) |
| `9` | 370 | event | raw | Trial phase onset: perception (sentence stimulus ID 9) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 30-class sentence perception identification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 4.0 s *, target_events = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 39]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 5 | 0 | perception sentence 5 |
  | 6 | 1 | perception sentence 6 |
  | 7 | 2 | perception sentence 7 |
  | 8 | 3 | perception sentence 8 |
  | 9 | 4 | perception sentence 9 |
  | 10 | 5 | perception sentence 10 |
  | 11 | 6 | perception sentence 11 |
  | 12 | 7 | perception sentence 12 |
  | 13 | 8 | perception sentence 13 |
  | 14 | 9 | perception sentence 14 |
  | 15 | 10 | perception sentence 15 |
  | 16 | 11 | perception sentence 16 |
  | 17 | 12 | perception sentence 17 |
  | 18 | 13 | perception sentence 18 |
  | 19 | 14 | perception sentence 19 |
  | 20 | 15 | perception sentence 20 |
  | 21 | 16 | perception sentence 21 |
  | 22 | 17 | perception sentence 22 |
  | 23 | 18 | perception sentence 23 |
  | 24 | 19 | perception sentence 24 |
  | 25 | 20 | perception sentence 25 |
  | 26 | 21 | perception sentence 26 |
  | 27 | 22 | perception sentence 27 |
  | 28 | 23 | perception sentence 28 |
  | 29 | 24 | perception sentence 29 |
  | 31 | 25 | perception sentence 31 |
  | 32 | 26 | perception sentence 32 |
  | 33 | 27 | perception sentence 33 |
  | 35 | 28 | perception sentence 35 |
  | 39 | 29 | perception sentence 39 |
- **Evidence**:
  - 10.1088/1741-2552/ad88a3 — Primary task from Valle et al. 2024: 30-class classification of perceived Spanish sentences using EEG with deep neural networks (EEGNet, DeepConvNet, ShallowConvNet) achieving subject-independent decoding.
- **Notes**: The original paper reports 30-class classification using sentences 5-29 (25 classes from the must_have_events list). To reach 30 classes, we include additional confirmed perception events 31, 32, 33, 35, and 39 from the grounded event meanings. Event IDs 1, 3, 4 are admin markers excluded per the paper. IDs 2 and 30-40 (with preparation/production/rest patterns) are non-perception phases and excluded. The epoch window covers the full 4s sentence presentation with -0.2s baseline for ERP analysis.

### Potential Task 1: Extended 39-Class Sentence Perception Identification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 4.0 s *, target_events = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 35, 39]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---------|
| 5 | 0 | perception sentence 5 |
| 6 | 1 | perception sentence 6 |
| 7 | 2 | perception sentence 7 |
| 8 | 3 | perception sentence 8 |
| 9 | 4 | perception sentence 9 |
| 10 | 5 | perception sentence 10 |
| 11 | 6 | perception sentence 11 |
| 12 | 7 | perception sentence 12 |
| 13 | 8 | perception sentence 13 |
| 14 | 9 | perception sentence 14 |
| 15 | 10 | perception sentence 15 |
| 16 | 11 | perception sentence 16 |
| 17 | 12 | perception sentence 17 |
| 18 | 13 | perception sentence 18 |
| 19 | 14 | perception sentence 19 |
| 20 | 15 | perception sentence 20 |
| 21 | 16 | perception sentence 21 |
| 22 | 17 | perception sentence 22 |
| 23 | 18 | perception sentence 23 |
| 24 | 19 | perception sentence 24 |
| 25 | 20 | perception sentence 25 |
| 26 | 21 | perception sentence 26 |
| 27 | 22 | perception sentence 27 |
| 28 | 23 | perception sentence 28 |
| 29 | 24 | perception sentence 29 |
| 31 | 25 | perception sentence 31 |
| 32 | 26 | perception sentence 32 |
| 35 | 27 | perception sentence 35 |
| 39 | 28 | perception sentence 39 |

- **Evidence**:
  - sub-002_ses-01_task-sentences_events.tsv — events.tsv showing trial_type/value mappings with perception events 5-39 and preparation/rest/production phases
  - events.json (implicit from events.tsv structure) — value encoding pattern: perception events use sentence stimulus IDs 1-39, preparation = perception + 30
  - README/publication — dataset described as 30 Spanish sentences for silent and perceived speech; this task extends to all perception events present in data
- **Notes**: This is a speculative extension beyond the paper's reported 30-class scope. The dataset contains perception events for sentence IDs 5-29, 31-32, 35, and 39 (29 distinct event IDs mapping to 29 unique sentence stimuli with y=0..28). Event 30 is excluded as it is preparation phase, not perception. Low-count events (27-29 with ~60 trials, 39 with 125 trials) have fewer trials due to counterbalancing. Event 33 was excluded from must_have_events despite being a perception event (sentence 33, count=544) — the candidate's kernel_needs specifies only events 5-29, 31-32, 35, 39. The epoch parameters (tmin=-0.2s, tmax=4.0s) are inferred from the 30-class task pattern, matching the 4.0s perception duration with -0.2s baseline.

### Potential Task 2: Rest vs Task State Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 5 s *, target_events = [35, 36, 37, 38, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 39, 40]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 35, 36, 37, 38 | 0 | rest (preparation phase markers serving as rest periods) |
  | 5-34, 39, 40 | 1 | task (perception/preparation/production phases combined) |
- **Evidence**:
  - events.tsv sample — trial structure shows rest_1 (value 95), perception_1 (value 5), preparation_1 (value 35), production_1 (value 65) with 5s rest periods between trials
  - events.tsv sample — pattern continues: rest_2 (value 106), perception_2 (value 16), preparation_2 (value 46), production_2 (value 76)
  - Evidence summary — encoding pattern: perception events use sentence stimulus IDs 1-39, preparation = perception + 30, production = perception + 60, rest = perception + 90
- **Notes**: Event IDs 35-38 are preparation phase onsets that function as rest/ready periods (trial_type=preparation in events.tsv with 1.0s duration, but the 5.0s rest periods are marked with values 95, 106, etc. which are perception+90). However, the must_have_events list only includes 35-38 as rest-like markers, not the actual rest events (95+). Using 35-38 as rest anchors since they are the closest available markers in the kernel_needs list. The task events (5-34, 39, 40) cover all perception and preparation/production onsets. The epoch parameters use 5s windows matching the documented rest period duration, with inferred values marked.

### Potential Task 3: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0 – 29.0 (years) | Continuous age of healthy participants; narrow 10-year span may limit predictive power |
- **Evidence**:
- **Notes**: Subject-level biomarker regression using non-overlapping 10-second windows to extract stable EEG features per participant. No event-based structure required; segmentation approach appropriate since age is a static subject-level variable with no temporal discriminative events. All 56 subjects have complete age data in participants.tsv.

### Potential Task 4: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level binary classification using 10-second non-overlapping EEG segments. The sex label is drawn from participants.tsv (native info field), making this a raw meta-level task. Segmentation is appropriate since sex is a subject-level demographic attribute not tied to specific experimental events. The 10-second window length provides sufficient data per sample while allowing multiple segments per subject's ~3200-second recording (~320 segments/subject).

### Potential Task 5: Continuous EEG Segmentation with Age Labels
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 5 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–29.0 (years) | Subject chronological age from participants.tsv; all 56 subjects have complete age data |
- **Evidence**:
- **Notes**: Segmentation-based regression using sliding windows across entire continuous EEG recording. No event structure is used; the kernel creates 10-second non-overlapping/overlapping segments from the full recording duration (~3200s). Each segment inherits the subject's age from participants.tsv as the regression target. This leverages all continuous data including rest periods, inter-trial intervals, and task-irrelevant periods that are excluded from event-based epoching. The overlap parameter (5s) provides increased sample count for subject-level prediction while maintaining feature stability.

### Potential Task 6: Sex Classification from Continuous EEG Segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 5 s *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - participants.tsv — sex column with values {F, M} for all 56 subjects (31 F, 25 M)
- **Notes**: Segmentation-based approach using all continuous EEG data without event restriction. Each subject contributes multiple 10-second overlapping segments, all labeled with the same sex value. This creates a subject-level classification task where the model must learn sex-related EEG features that generalize across repeated segments from the same individual.

## Data Quality Notes

- Event ID `2` has no documented meaning in the scan result, leaving its trial phase ambiguous.
- Event ID `30` shows an anomalously high count (10921) compared to other perception events (~370), suggesting it may represent a different trial phase or encoding scheme despite being labeled as "preparation (sentence stimulus ID 0)".
- Event IDs `31` and `32` also show extremely high counts (11100 each), inconsistent with typical perception event counts, indicating potential miscoding or duplicated entries.
- Event IDs `27`, `28`, `29`, and `39` have substantially fewer trials (65, 60, 60, 125 respectively) compared to the standard ~370 trials, which may create class imbalance in classification tasks.
- Event ID `40` has only 2 occurrences, making it statistically unreliable for any task inclusion.
- The `device` field is completely missing from metadata, limiting hardware reproducibility.
- The event structure shows overlapping/conflicting interpretations between the original draft and the authoritative scan result (e.g., event 30 was previously labeled "perception phase for sentence 30" but scan result shows "preparation (sentence stimulus ID 0)"), indicating prior documentation errors.
- Rest period markers referenced in task notes (values 95, 106, etc., corresponding to perception+90) do not appear in the scan result event table, suggesting they may be absent or encoded differently in the actual data files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
