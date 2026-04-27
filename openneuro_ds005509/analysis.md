# Healthy Brain Network (HBN) EEG - Release 5

**Dataset**: `openneuro_ds005509` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005509
**Category**: Complex Applied | **Subjects**: 330 | **Files (Completed)**: 3326 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

The Healthy Brain Network (HBN) EEG Release 5 is a large-scale, multi-task developmental battery collected from children and adolescents aged 5-21 years. Participants completed six paradigms including naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `cd0428f4c2d883197e217263d674e9396e02295c8c2537055ab47a7f49020043`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 2339 | admin | raw | Task initialization/start marker |
| `boundary` | 1839 | admin | raw | Recording boundary/end marker |
| `break cnt` | 3296 | admin | raw | Segment break or recording segment counter |
| `contrastChangeB1_start` | 233 | event | raw | Trial phase onset: contrast change block 1 |
| `contrastChangeB2_start` | 282 | event | raw | Trial phase onset: contrast change block 2 |
| `contrastChangeB3_start` | 260 | event | raw | Trial phase onset: contrast change block 3 |
| `contrastTrial_start` | 18682 | event | raw | Trial phase onset: contrast detection trial |
| `dot_no1_OFF` | 1553 | event | raw | Trial phase onset: dot 1 offset |
| `dot_no1_ON` | 1553 | event | raw | Trial phase onset: dot 1 onset |
| `dot_no2_OFF` | 3111 | event | raw | Trial phase onset: dot 2 offset |
| `dot_no2_ON` | 3119 | event | raw | Trial phase onset: dot 2 onset |
| `dot_no3_OFF` | 1553 | event | raw | Trial phase onset: dot 3 offset |
| `dot_no3_ON` | 1565 | event | raw | Trial phase onset: dot 3 onset |
| `dot_no4_OFF` | 1553 | event | raw | Trial phase onset: dot 4 offset |
| `dot_no4_ON` | 1558 | event | raw | Trial phase onset: dot 4 onset |
| `dot_no5_OFF` | 1553 | event | raw | Trial phase onset: dot 5 offset |
| `dot_no5_ON` | 1553 | event | raw | Trial phase onset: dot 5 onset |
| `dot_no6_OFF` | 1553 | event | raw | Trial phase onset: dot 6 offset |
| `dot_no6_ON` | 1553 | event | raw | Trial phase onset: dot 6 onset |
| `dot_no7_OFF` | 2104 | event | raw | Trial phase onset: dot 7 offset |
| `dot_no7_ON` | 2100 | event | raw | Trial phase onset: dot 7 onset |
| `dot_no8_OFF` | 1050 | event | raw | Trial phase onset: dot 8 offset |
| `dot_no8_ON` | 1050 | event | raw | Trial phase onset: dot 8 onset |
| `fixpoint_ON` | 35136 | event | raw | Trial phase onset: fixation point onset |
| `instructed_toCloseEyes` | 1639 | event | raw | Trial phase onset: instruction to close eyes |
| `instructed_toOpenEyes` | 1969 | event | raw | Trial phase onset: instruction to open eyes |
| `learningBlock_1` | 319 | event | raw | Trial phase onset: learning block 1 |
| `learningBlock_2` | 310 | event | raw | Trial phase onset: learning block 2 |
| `learningBlock_3` | 310 | event | raw | Trial phase onset: learning block 3 |
| `learningBlock_4` | 307 | event | raw | Trial phase onset: learning block 4 |
| `learningBlock_5` | 307 | event | raw | Trial phase onset: learning block 5 |
| `left_buttonPress` | 10192 | event | raw | Response: left button press |
| `left_target` | 8947 | event | raw | Trial phase onset: left target stimulus |
| `newPage` | 522 | event | raw | Trial phase onset: new page display |
| `resting_start` | 336 | event | raw | Trial phase onset: resting period |
| `right_buttonPress` | 9498 | event | raw | Response: right button press |
| `right_target` | 8977 | event | raw | Trial phase onset: right target stimulus |
| `seqLearning_start` | 319 | event | raw | Trial phase onset: sequence learning task |
| `seqLearning_stop` | 307 | event | raw | Trial phase onset: sequence learning task end |
| `stim_ON` | 35156 | event | raw | Trial phase onset: stimulus onset |
| `surroundSuppB1_start` | 286 | event | raw | Trial phase onset: surround suppression block 1 |
| `surroundSuppB2_start` | 263 | event | raw | Trial phase onset: surround suppression block 2 |
| `symbolSearch_start` | 202 | event | raw | Trial phase onset: symbol search task |
| `trialResponse` | 3367 | event | raw | Response: trial response |
| `video_start` | 1205 | event | raw | Trial phase onset: video playback |
| `video_stop` | 1190 | event | raw | Trial phase onset: video playback end |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 30 s *, overlap = 0.0, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — 2-class classification from alternating eyes-open/eyes-closed instructions during resting state
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset description with 1639 close-eye and 1969 open-eye events across 336 recordings
- **Notes**: Epoch parameters inferred from typical block durations (~30-60s) with 30s windows chosen to capture stable state without boundary contamination. Long-event epoching used due to sustained nature of resting state periods. The `resting_start` event marks task onset but is not used as a class label; class labels derive from the instruction events that demarcate alternating eyes-open and eyes-closed blocks.

### Classical Task 2: Contrast Change Detection Target Direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  | --- | --- | --- |
  | `left_target` | 0 | Left-side leaning target stimulus onset |
  | `right_target` | 1 | Right-side leaning target stimulus onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — 2-class classification of left vs right tilted target in contrast change detection. 8947 left_target and 8977 right_target events across 18682 trials. Active visual discrimination task with motor response.
- **Notes**: Event route archetype A; target events directly encode the visual discrimination classes. Epoch window spans pre-stimulus baseline (-0.2s) through stimulus processing and motor response period (1.5s), inferred from HED Duration/1600 ms stimulus plus response time. Both event IDs confirmed in events.json with HED definitions for left-target and right-target presentations.

### Classical Task 3: Surround Suppression Stimulus Onset
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.1 s *, tmax = 0.5 s *, target_events = [`stim_ON`, `fixpoint_ON`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stim_ON` | 0 | Peripheral disk stimulus onset |
  | `fixpoint_ON` | 1 | Fixation point onset (baseline/fixation control) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Visual evoked potential classification from stimulus onset events. 35156 stim_ON events across 2 blocks with fixation point onset (35136 fixpoint_ON). Peripheral disk stimulation with background contrast manipulation.
- **Notes**: This task uses two event types from the surroundSupp task: `stim_ON` (peripheral disk stimulus onset) and `fixpoint_ON` (fixation point onset). The `stim_ON` events represent the primary visual evoked response to peripheral stimulation, while `fixpoint_ON` serves as a control/baseline condition for fixation-related visual responses. Both event types are confirmed in the task-surroundSupp_events.json sidecar with HED annotations. The epoch window (-100ms to 500ms) is standard for capturing transient VEP components (P1, N1, P2) following peripheral visual stimulation. The classification distinguishes between stimulus-driven vs. fixation-driven visual evoked potentials.

### Classical Task 4: Sequence Learning 6-Target Dot Position Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — 6-class classification of dot position in sequence learning task with dot_no1_ON through dot_no6_ON events; 5 learning blocks with sequential pattern, distinct from 8-target variant
- **Notes**: Archetype A event-route classification using the six dot onset events as class labels. Each event marks when a specific dot position turns black in the sequence learning paradigm. The 1-second post-onset window captures visual ERP and working memory updating processes. Epoch parameters inferred from standard cognitive ERP literature for sequential stimulus processing.

### Classical Task 5: Sequence Learning 8-Target Dot Position Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `dot_no1_ON` | 0 | Dot position 1 onset (turned black) |
  | `dot_no2_ON` | 1 | Dot position 2 onset (turned black) |
  | `dot_no3_ON` | 2 | Dot position 3 onset (turned black) |
  | `dot_no4_ON` | 3 | Dot position 4 onset (turned black) |
  | `dot_no5_ON` | 4 | Dot position 5 onset (turned black) |
  | `dot_no6_ON` | 5 | Dot position 6 onset (turned black) |
  | `dot_no7_ON` | 6 | Dot position 7 onset (turned black) |
  | `dot_no8_ON` | 7 | Dot position 8 onset (turned black) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — 8-class classification of dot position in extended sequence learning task; events dot_no1_ON through dot_no8_ON encode distinct spatial positions in the 8-target sequence learning paradigm
  - task-seqLearning8target_events.json — Confirmed event definitions: "Dot number X turned black" for dot_no1_ON through dot_no8_ON, with scope limited to seqLearning8target task
- **Notes**: Eight-class classification task distinguishing which of 8 dot positions turned black during sequence learning. Epoch window (-0.2, 1.0)s captures pre-onset baseline and 1 second of visual processing. Inferred parameters marked with * based on 6-target variant timing and standard sequence element processing window. Distinct from 6-target variant due to different cognitive load (8 positions) and separate event set (dot_no7_ON/dot_no8_ON exclusive to 8-target).

### Classical Task 6: Symbol Search Accuracy
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`trialResponse`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `trialResponse` (correct_answer=1, user_answer=1) | 0 | Correct response - symbol found correctly |
  | `trialResponse` (correct_answer=0, user_answer=0) | 1 | Correct response - symbol absent correctly identified |
  | `trialResponse` (correct_answer=1, user_answer=0) | 2 | Incorrect response - false negative |
  | `trialResponse` (correct_answer=0, user_answer=1) | 3 | Incorrect response - false positive |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Symbol search task with 3367 trialResponse events; user_answer and correct_answer columns in events.tsv enable accuracy classification by comparing participant response to ground truth
- **Notes**: The task uses a single event ID (`trialResponse`) with label derived from comparing `user_answer` and `correct_answer` columns in events.tsv. For binary accuracy classification, y=0 and y=1 represent correct responses (hit and correct rejection), while y=2 and y=3 represent incorrect responses (miss and false alarm). The kernel must match each `trialResponse` event with its corresponding `user_answer` and `correct_answer` values from the events.tsv columns to assign the class label. For a cleaner 2-class formulation, correct trials (y∈{0,1}) can be merged to y=0 and incorrect trials (y∈{2,3}) merged to y=1.

### Classical Task 7: Movie Watching Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 120 s *, overlap = 0, target_events = [`video_start`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `video_start` (DespicableMe) | 0 | Despicable Me movie clip |
  | `video_start` (DiaryOfAWimpyKid) | 1 | Diary of a Wimpy Kid movie clip |
  | `video_start` (FunwithFractals) | 2 | Fun with Fractals movie clip |
  | `video_start` (ThePresent) | 3 | The Present movie clip |
- **Evidence**:
  - 10.1101/089060 — HBN EEG dataset description with movie watching tasks including four video clips (DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent)
  - 10.1101/2024.10.03.615261 — Release 5 dataset paper confirming naturalistic video viewing paradigm with video_start/video_stop event markers
- **Notes**: The four movie conditions are distinguished by the BIDS task file from which each video_start event originates (task-DespicableMe, task-DiaryOfAWimpyKid, task-FunwithFractals, task-ThePresent). The kernel must map each video_start event to its corresponding task file to assign the correct class label. Epoch duration capped at 120s (minimum clip length) to ensure consistent epoch lengths across conditions; actual clips range up to ~180s. Long-event epoching with zero overlap treats each video presentation as a single continuous epoch.

### Classical Task 8: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `p_factor`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | p_factor | continuous (z-score) | General psychopathology factor from CBCL/YSR items; 323/330 subjects have values. Higher values indicate greater transdiagnostic psychopathology burden. |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Regression of general psychopathology factor (p-factor) from EEG features for transdiagnostic prediction.
  - 10.1101/2024.10.03.615261 — HBN-EEG Release 5 dataset paper describing p-factor derivation and clinical biomarker applications.
- **Notes**: Segmentation-based regression to a continuous clinical score. The p_factor is a native participants.tsv column (z-scored dimensional psychopathology factor), so Meta Level = raw. Epoch parameters follow SKILL defaults for clinical/disorder segmentation: 4-second non-overlapping segments applied to continuous EEG recordings, with features extracted per segment for regression to the subject-level p_factor score. Subjects without p_factor values are excluded from training/evaluation.

### Classical Task 9: Attention Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `attention`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | attention | z-scored dimension score (unitless) | 323/330 subjects with values; higher values indicate greater attention problems |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Regression of attention problems dimension from EEG features
  - 10.1101/2024.10.03.615261 — HBN-EEG Release 5 dataset paper describing psychopathology dimensions including attention
- **Notes**: Segmentation-based regression task using all available continuous EEG data. The attention dimension is a specific psychopathology factor distinct from p-factor and internalizing/externalizing dimensions, derived from participants.tsv. No kernel derivation needed—label is native info field.

### Classical Task 10: Internalizing Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `internalizing`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | internalizing | z-scored factor score (unitless) | HBN psychopathology dimension; anxiety/depression-related; 323/330 subjects with values; higher values indicate greater internalizing symptoms |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Regression of internalizing symptoms dimension from EEG features
  - 10.1101/2024.10.03.615261 — HBN Release 5 dataset paper describing internalizing as one of four core psychopathology dimensions for dimensional prediction
- **Notes**: Standard 4-second segmentation applied across continuous EEG recordings for clinical biomarker regression. The internalizing factor score is a native participants.tsv column (archetype B3), requiring no kernel derivation. Missing values (7/330 subjects) will be handled by standard sample exclusion.

### Classical Task 11: Externalizing Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `externalizing`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | externalizing | z-scored dimension score (unitless) | HBN psychopathology factor; ADHD/conduct-related; partial coverage 323/330 subjects; higher values indicate greater externalizing symptoms |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Regression of externalizing symptoms dimension from EEG features
  - 10.1101/2024.10.03.615261 — HBN EEG Release 5 dataset descriptor; externalizing as one of four core psychopathology dimensions
- **Notes**: Standard 4-second segmentation for clinical regression. The externalizing factor is a pre-computed z-scored dimension from participants.tsv, requiring no kernel derivation. Segmentation-based epoching is used since this is a clinical biomarker prediction task rather than an event-locked paradigm. Overlap is set to 0.0 to ensure independent segments for regression.

### Classical Task 12: Resting State Segmentation p-factor
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `p_factor`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | p_factor | continuous (z-score) | Transdiagnostic psychopathology factor; partial completeness (323/330). Higher values indicate greater overall psychopathology burden across internalizing and externalizing domains. |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Segmentation-based regression of p-factor specifically from resting state EEG. Uses instructed_toOpenEyes/instructed_toCloseEyes events to identify resting periods, then segments for feature extraction. Matches benchmark challenge design.
- **Notes**: Archetype C with info-native label (p_factor from participants.tsv). Segmentation is performed within resting state blocks demarcated by instructed_toOpenEyes and instructed_toCloseEyes events. The kernel must first identify these anchor events to delimit valid resting-state intervals, then create 4-second non-overlapping segments exclusively within those intervals. Each segment inherits the same p_factor value from the participant's info record. No derived misc channel is needed since p_factor is a native participants.tsv column.

### Potential Task 1: Contrast Change Detection Response Side
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -1.0 s *, tmax = 0.5 s *, target_events = [`left_buttonPress`, `right_buttonPress`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_buttonPress` | 0 | Left button press response |
  | `right_buttonPress` | 1 | Right button press response |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — 2-class classification from left vs right button press responses. 10192 left_buttonPress and 9498 right_buttonPress events. Derived from same contrast change detection task but labels motor response rather than stimulus.
- **Notes**: Response-locked epoching capturing readiness potential (1s pre-response) and motor execution (0.5s post-response). Both event IDs are confirmed in the contrastChangeDetection task events.json with explicit HED tags defining left/right mouse button presses with corresponding index fingers.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 5.2–20.9 (years) | Chronological age from participants.tsv; complete for all 330 subjects (ages 5.2–20.9). Used as continuous regression target for developmental biomarker prediction. |
- **Evidence**:
  - 10.1101/089060 — Regression of chronological age from EEG features. Complete data for all 330 subjects (ages 5.2-20.9). Developmental prediction task leveraging neurodevelopmental changes across childhood/adolescence.
- **Notes**: Native info field from participants.tsv. Segmentation-based epoching with 4s windows; no event alignment needed. Age is a continuous variable suitable for regression with wide developmental range.

### Potential Task 3: Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | Male |
  | sex | F | 1 | Female |
- **Evidence**:
- **Notes**: Subject-level classification using 4-second non-overlapping EEG segments. All segments from a single subject share the same sex label from participants.tsv. The binary target (M/F) is encoded as y=0/1. Segment length and overlap are inferred from the candidate hint; no fixed trial structure applies since this is a biological state classification across continuous recordings.

### Potential Task 4: ehq_total regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `ehq_total`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | ehq_total | -100 to +100 (dimensionless) | Edinburgh Handedness Questionnaire total score; complete for all 330 subjects; higher values indicate stronger right-handedness |
- **Evidence**:
- **Notes**: Native info field from participants.tsv. 4-second non-overlapping segmentation applied across continuous EEG recordings to extract features for predicting the continuous handedness trait score. The ehq_total values range approximately -100 (strongly left-handed) to +100 (strongly right-handed) based on sample data.

### Potential Task 5: RestingState Availability Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `RestingState`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | RestingState | available | 0 | RestingState data is available and usable |
  | RestingState | unavailable | 1 | RestingState data is not available |
- **Evidence**:
- **Notes**: Segmentation-based subject-level classification using any available EEG data segments to predict whether a subject has usable RestingState task data. The RestingState column in participants.tsv indicates data availability status (available/unavailable) for each subject. This is a data quality/automated QC task where the model learns to predict which subjects have usable recordings for specific tasks without requiring the actual task events to be present in the recording being classified.

### Potential Task 6: Full Phenotype Availability Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `full_pheno`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | full_pheno | No | 0 | Incomplete phenotypic data |
  | full_pheno | Yes | 1 | Complete phenotypic data |
- **Evidence**:
  - participants.tsv — `full_pheno` column with values No/Yes; 323/330 subjects have complete phenotypic data
- **Notes**: Subject-level classification task predicting whether a participant has complete phenotypic data based on EEG patterns. Uses 4-second non-overlapping windows across all available EEG recordings. The `full_pheno` field is a native participants.tsv column indicating Yes/No for complete phenotypic assessment availability.

## Data Quality Notes

- `device` field is completely missing from info metadata, limiting hardware provenance tracking.
- Psychopathology dimensions (`p_factor`, `attention`, `internalizing`, `externalizing`) have partial coverage (323/330 subjects), requiring exclusion or imputation for 7 subjects in regression tasks.
- Multiple task availability columns (e.g., `DespicableMe`, `FunwithFractals`, `ThePresent`, `DiaryOfAWimpyKid`, `contrastChangeDetection_1-3`, `surroundSupp_1-2`, `seqLearning8target`, `symbolSearch`) include `caution` values indicating potential data quality concerns for specific recordings.
- Event counts show slight imbalances between left/right targets and button presses that may affect classification performance.
- The `seqLearning_start` event count (319) exceeds `seqLearning_stop` count (307), suggesting possible incomplete recordings or missing stop events in some sequence learning blocks.
- Resting state eyes-open/eyes-closed event counts are imbalanced (1969 open vs 1639 close), which may bias classification models toward the majority class.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
