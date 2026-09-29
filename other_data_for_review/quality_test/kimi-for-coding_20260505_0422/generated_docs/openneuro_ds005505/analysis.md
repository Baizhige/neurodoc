# Healthy Brain Network (HBN) - EEG Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 136 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 dataset contains multi-paradigm EEG recordings from 136 children and adolescents (ages 5-21) collected as part of a large-scale community-based mental health study. Participants completed a battery of tasks including visual discrimination (contrast change detection, surround suppression), sequence learning (6-target and 8-target variants), symbol search, resting state with eyes open/closed, and naturalistic movie watching (four different clips). EEG was recorded using a 129-channel Geodesic Sensor Net (EGI) system at 500 Hz sampling rate. The dataset includes rich phenotypic data including psychopathology factor scores (p-factor, attention, internalizing, externalizing), age, sex, and handedness.

## File Scan Result

> **Kernel SHA256**: `1cb1de53d50788b1af698caeb90753794a8cfc1396507a46c505b73d6b57801a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1136 | admin | raw | Recording initialization marker |
| `boundary` | 728 | admin | raw | Recording boundary/end marker |
| `break cnt` | 1488 | admin | raw | Pre-task system marker at recording onset |
| `contrastChangeB1_start` | 102 | event | raw | Trial phase onset: block 1 start |
| `contrastChangeB2_start` | 117 | event | raw | Trial phase onset: block 2 start |
| `contrastChangeB3_start` | 143 | event | raw | Trial phase onset: block 3 start |
| `contrastTrial_start` | 8884 | event | raw | Trial phase onset: trial start |
| `dot_no1_OFF` | 600 | event | raw | Trial phase onset: dot 1 off |
| `dot_no1_ON` | 600 | event | raw | Trial phase onset: dot 1 on |
| `dot_no2_OFF` | 1202 | event | raw | Trial phase onset: dot 2 off |
| `dot_no2_ON` | 1234 | event | raw | Trial phase onset: dot 2 on |
| `dot_no3_OFF` | 600 | event | raw | Trial phase onset: dot 3 off |
| `dot_no3_ON` | 624 | event | raw | Trial phase onset: dot 3 on |
| `dot_no4_OFF` | 600 | event | raw | Trial phase onset: dot 4 off |
| `dot_no4_ON` | 600 | event | raw | Trial phase onset: dot 4 on |
| `dot_no5_OFF` | 600 | event | raw | Trial phase onset: dot 5 off |
| `dot_no5_ON` | 600 | event | raw | Trial phase onset: dot 5 on |
| `dot_no6_OFF` | 600 | event | raw | Trial phase onset: dot 6 off |
| `dot_no6_ON` | 600 | event | raw | Trial phase onset: dot 6 on |
| `dot_no7_OFF` | 796 | event | raw | Trial phase onset: dot 7 off |
| `dot_no7_ON` | 792 | event | raw | Trial phase onset: dot 7 on |
| `dot_no8_OFF` | 396 | event | raw | Trial phase onset: dot 8 off |
| `dot_no8_ON` | 396 | event | raw | Trial phase onset: dot 8 on |
| `fixpoint_ON` | 13248 | event | raw | Trial phase onset: fixation point on |
| `instructed_toCloseEyes` | 680 | event | raw | Trial phase onset: instructed to close eyes |
| `instructed_toOpenEyes` | 816 | event | raw | Trial phase onset: instructed to open eyes |
| `learningBlock_1` | 122 | event | raw | Trial phase onset: learning block 1 |
| `learningBlock_2` | 121 | event | raw | Trial phase onset: learning block 2 |
| `learningBlock_3` | 120 | event | raw | Trial phase onset: learning block 3 |
| `learningBlock_4` | 119 | event | raw | Trial phase onset: learning block 4 |
| `learningBlock_5` | 118 | event | raw | Trial phase onset: learning block 5 |
| `left_buttonPress` | 5095 | event | raw | Response: left button press |
| `left_target` | 4243 | event | raw | Stimulus: left target presented |
| `newPage` | 194 | event | raw | Trial phase onset: new page |
| `resting_start` | 139 | event | raw | Trial phase onset: resting task start |
| `right_buttonPress` | 4634 | event | raw | Response: right button press |
| `right_target` | 4251 | event | raw | Stimulus: right target presented |
| `seqLearning_start` | 122 | event | raw | Trial phase onset: sequence learning task start |
| `seqLearning_stop` | 118 | event | raw | Trial phase onset: sequence learning task stop |
| `stim_ON` | 13278 | event | raw | Stimulus: stimulus on |
| `surroundSuppB1_start` | 108 | event | raw | Trial phase onset: block 1 start |
| `surroundSuppB2_start` | 99 | event | raw | Trial phase onset: block 2 start |
| `symbolSearch_start` | 76 | event | raw | Trial phase onset: symbol search task start |
| `trialResponse` | 1247 | event | raw | Response: trial response |
| `video_start` | 761 | event | raw | Trial phase onset: video start |
| `video_stop` | 723 | event | raw | Trial phase onset: video stop |

### Info

| Field | Completeness | Notes |
|---|---|---|

## Tasks

### Classical Task 1: Contrast Change Detection Target Direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_target` | 0 | Left-side leaning target presented |
  | `right_target` | 1 | Right-side leaning target presented |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing contrast change detection task with left/right target discrimination
  - 10.1038/sdata.2017.40 — Original HBN project publication establishing the dataset framework
  - arXiv:2506.19141v2 — EEG ML benchmark paper utilizing this task for visual discrimination classification
- **Notes**: Standard visual discrimination ERP classification. Epochs are locked to target onset (left_target/right_target events) with a window covering pre-stimulus baseline (-200ms) through early visual and decision-related components (1000ms post-stimulus). The 1600ms target duration is longer than the epoch window; the 1000ms post-stimulus window captures the critical early evoked response period while avoiding late trial contamination from the comeback/feedback phases.

### Classical Task 2: Sequence Learning 6-Target Dot Position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.6 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `dot_no1_ON` | 0 | Dot 1 turned black (sequence position 1) |
  | `dot_no2_ON` | 1 | Dot 2 turned black (sequence position 2) |
  | `dot_no3_ON` | 2 | Dot 3 turned black (sequence position 3) |
  | `dot_no4_ON` | 3 | Dot 4 turned black (sequence position 4) |
  | `dot_no5_ON` | 4 | Dot 5 turned black (sequence position 5) |
  | `dot_no6_ON` | 5 | Dot 6 turned black (sequence position 6) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing sequence learning task with 6 target positions
  - arXiv:2506.19141v2 — Active sequence learning task with dot ON events marking sequential spatial positions
  - task-seqLearning6target_events.json — Confirmed event definitions: "Dot number 1 turned black" through "Dot number 6 turned black"
- **Notes**: Six-way classification of sequence position based on dot onset events. Each dot turns on sequentially in the learned order during the seqLearning6target task. Epoch window captures pre-stimulus baseline (-100 ms) and early visual evoked response plus initial sequence position encoding (600 ms post-onset). Parameters inferred from rapid sequential presentation paradigm; actual dot presentation timing may vary slightly across learning blocks.

### Classical Task 3: Sequence Learning 8-Target Dot Position Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.6 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `dot_no1_ON` | 0 | Dot position 1 turned black |
  | `dot_no2_ON` | 1 | Dot position 2 turned black |
  | `dot_no3_ON` | 2 | Dot position 3 turned black |
  | `dot_no4_ON` | 3 | Dot position 4 turned black |
  | `dot_no5_ON` | 4 | Dot position 5 turned black |
  | `dot_no6_ON` | 5 | Dot position 6 turned black |
  | `dot_no7_ON` | 6 | Dot position 7 turned black |
  | `dot_no8_ON` | 7 | Dot position 8 turned black |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing sequence learning tasks with 6-target and 8-target variants
  - arXiv:2506.19141v2 — Reference confirming 8-target sequence learning paradigm with dot position events
- **Notes**: Task uses the 8-target variant of sequence learning (distinct from the 6-target variant). Subjects are filtered by `seqLearning8target == available` in participants.tsv. Epoch window inferred from the 6-target variant timing structure; same pre-stimulus baseline and post-onset window appropriate for visual ERP analysis of dot position encoding. The eight classes represent spatial positions in a sequence learning working memory task, with approximately 400-800 presentations per dot position depending on subject.

### Classical Task 4: Resting State Eyes Open vs Closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 30 s *, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `instructed_toOpenEyes` | 0 | Voice prompt instructed subject to open their eyes |
  | `instructed_toCloseEyes` | 1 | Voice prompt instructed subject to close their eyes |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Classic resting state paradigm with explicit eyes-open/eyes-closed instructions in HBN dataset
  - 10.1016/j.neuroimage.2020.117001 — Used in HBN analysis papers for alpha power modulation between eyes-open/closed states
  - 10.1016/j.neuroimage.2022.119348 — Resting state EEG analysis with eyes-open vs eyes-closed classification
  - arXiv:2506.19141v2 — HBN resting state paradigm with voice prompt onset markers for state transitions
- **Notes**: Standard resting state classification task. Two classes from voice prompt onset events: instructed_toOpenEyes (~816 events) and instructed_toCloseEyes (~680 events). Epoching from instruction onset captures both the transition and sustained state period. The 30-second window is inferred from typical block durations in resting state paradigms; actual blocks may extend longer but this captures the stable state period. Alpha power modulation (8-12 Hz) is the primary expected neural signature distinguishing these conditions, with higher posterior alpha power during eyes-closed periods.

### Classical Task 5: Surround Suppression Stimulus Presence vs Fixation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.5 s *, target_events = [`stim_ON`, `fixpoint_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `stim_ON` | 0 | Stimulus onset (peripheral disk flash with background present/absent and contrast conditions) |
  | `fixpoint_ON` | 1 | Fixation point onset (baseline/no-stimulus control period) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing surround suppression task with peripheral disk stimulation and parametric conditions
  - 10.1038/sdata.2017.40 — Original HBN publication describing the broader project including visual paradigms
  - arXiv:2506.19141v2 — HBN-EEG dataset documentation confirming stim_ON events (~13,278) with background/foreground_contrast/stimulus_cond parameters
- **Notes**: Binary classification of stimulus presence versus fixation baseline. The stim_ON event marks the onset of peripheral disk stimulation with parametric variations (background present/absent, foreground contrast levels, stimulus condition). The fixpoint_ON event marks fixation periods that serve as explicit non-stimulus baseline for comparison. Epoch window (-0.1 to 0.5 s) captures the C1/P1/N1 VEP components. Both event types are confirmed in task-surroundSupp_events.json. This forms a proper two-class detection task: evoked visual response (y=0) versus fixation baseline (y=1).

### Classical Task 6: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | p_factor | Continuous transdiagnostic psychopathology factor from bifactor model; higher values indicate greater psychopathology burden. Available for 132/136 subjects. |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — General psychopathology factor from bifactor model, continuous variable used as Challenge 2 benchmark target
  - arXiv:2506.19141v2 — Competition benchmark using p-factor for subject-level prediction from EEG
  - 10.1016/j.neuroimage.2022.119348 — Prior work on EEG-based prediction of transdiagnostic psychopathology dimensions
- **Notes**: Subject-level regression from continuous EEG segments. No event structure required; segments span any available task or resting-state recording. The 10-second segment length with 50% overlap is standard for phenotype prediction from continuous EEG and was inferred from the paradigm description (epoch_hint.inferred=true).

### Classical Task 7: Attention Problems Factor Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | attention | Continuous z-scored attention problems factor from bifactor model (132/136 subjects). Higher values indicate greater attention-deficit symptoms. Predict from EEG spectral/connectivity features across all available task segments. |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing bifactor model with attention as specific dimension of psychopathology distinct from general p-factor; continuous variable available for 132/136 subjects
  - arXiv:2506.19141v2 — EEG-based prediction of specific psychopathology factors including attention problems from resting-state and task EEG using segmentation approach
- **Notes**: Segmentation-based regression predicting continuous attention problems factor from EEG features. Same 10-second non-overlapping segmentation strategy as p-factor task (archetype B3, info-native). The attention factor is a specific dimension from the bifactor model capturing attention-deficit symptoms independent of general psychopathology. Subjects missing this phenotype (4/136) are excluded from training/evaluation.

### Classical Task 8: Internalizing Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10.0 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | internalizing | Continuous internalizing problems factor score (bifactor model: anxiety/depression dimension). Values range approximately -0.3 to 1.9. Available for 132/136 subjects. Higher values indicate greater internalizing symptom severity. |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing psychopathology bifactor model with internalizing, externalizing, and attention factors derived from parent-report measures
  - arXiv:2506.19141v2 — Follow-up analysis using HBN-EEG data for phenotype prediction with internalizing as continuous target variable
- **Notes**: Segmentation-based approach for subject-level phenotype prediction. The internalizing factor is a pre-computed scalar in participants.tsv (native info field), requiring no kernel derivation. Standard 10-second windows with 50% overlap provide sufficient samples per subject for stable feature estimation while capturing frequency-domain markers (e.g., frontal alpha asymmetry) previously linked to internalizing symptoms in youth.

### Classical Task 9: Externalizing Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | externalizing | Continuous z-scored externalizing problems factor score (conduct problems, hyperactivity). Range approximately -0.9 to 0.9. Available for 132/136 subjects. Higher values indicate greater externalizing symptomatology. |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing bifactor model with externalizing as specific dimension distinct from p-factor and internalizing
  - arXiv:2506.19141v2 — Externalizing problems factor validated as continuous psychopathology predictor; sample range -0.9 to 0.9 for 132 subjects
- **Notes**: Segmentation-based regression predicting continuous externalizing factor from resting-state or task-EEG segments. The 10-second window with 50% overlap is standard for spectral/feature-based biomarker extraction in psychopathology prediction studies. The externalizing dimension captures conduct problems and hyperactivity/inattention distinct from internalizing (anxiety/depression) and general psychopathology (p-factor).

### Classical Task 10: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `age` | Continuous chronological age in years (range ~5.2–21.7); used directly as regression target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing developmental EEG data with age range 5–21 years
  - 10.1016/j.neuroimage.2020.117001 — Brain-age prediction from EEG as established benchmark methodology
  - arXiv:2506.19141v2 — Recent validation of EEG-based age prediction across developmental samples
- **Notes**: Standard brain-age prediction setup using 10-second non-overlapping segments with 50% overlap. Age is a per-subject variable from participants.tsv, making this a subject-level regression task. All task conditions (resting state, video watching, active tasks) can be pooled since age is task-independent. Segment length and overlap inferred from brain-age prediction literature standard practices.

### Classical Task 11: Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `sex` | `F` → y=0 (female, n=46); `M` → y=1 (male, n=90). Class imbalance: ~66% male. |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN-EEG dataset paper describing sex-stratified sample (F=46, M=90) and demographic variables
  - 10.1016/j.neuroimage.2020.117001 — Sex differences in EEG power and connectivity as established neurophysiological markers
- **Notes**: Subject-level classification task using all available continuous EEG segments. The 10-second segmentation with 50% overlap is inferred from standard practice for demographic prediction tasks where stable spectral features (e.g., alpha power, coherence) require multi-second windows. Sex is a native participants.tsv column with complete coverage (136/136 subjects).

### Classical Task 12: Movie Watching Task Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 120 s *, overlap = 0, target_events = [`video_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `video_start` (code 81) | 0 | DiaryOfAWimpyKid |
  | `video_start` (code 82) | 1 | FunwithFractals |
  | `video_start` (code 83) | 2 | DespicableMe |
  | `video_start` (code 84) | 3 | ThePresent |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Dataset descriptor confirming four distinct movie clips (DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent) as naturalistic viewing tasks with video_start/video_stop event markers
  - arXiv:2506.19141v2 — HBN-EEG dataset documentation confirming movie watching paradigm with unique event codes per clip (81/101, 82/102, 83/103, 84/104)
  - 10.1016/j.neuroimage.2020.117001 — Prior HBN neuroimaging work validating naturalistic viewing paradigms for sustained engagement analysis in developmental cohorts
- **Notes**: Event code disambiguation is required: the kernel must inspect the `event_code` column (or task filename) to determine which of the four movies corresponds to each `video_start` event, since all clips share the same `video_start` value string but have distinct numeric codes (81, 82, 83, 84). The tmax=120s is inferred from the epoch_hint and covers a major portion of the 2-3 minute clips; actual clip durations vary (e.g., ~119s DiaryOfAWimpyKid, ~164s FunwithFractals, ~171s DespicableMe per sample events.tsv). Overlap=0 prevents redundant epochs from the same continuous viewing period.

### Classical Task 13: Movie vs Resting State Task Discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 30 s *, overlap = 0.0, target_events = [`video_start`, `resting_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `video_start` | 0 | Movie watching (engaged brain state) |
  | `resting_start` | 1 | Resting state (relaxed brain state) |
- **Evidence**:
  - arXiv:2506.19141v2 — Meta-level task discrimination benchmark; classifies passive conditions (movie watching vs resting state) from EEG, with 30-second segments used to capture stable state differences
- **Notes**: Task uses trial phase onset markers (`video_start` for movie watching tasks, `resting_start` for resting state) as class-conditional anchors. The 30-second epoch duration is inferred to capture stable brain state differences while allowing multiple samples per condition; overlap=0.0 prevents redundant samples. All four video tasks (DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent) share the same `video_start` event code, so they are pooled into a single "movie watching" class (y=0) versus resting state (y=1). This is a task-state discrimination paradigm, not motor imagery.

### Classical Task 14: Active vs Passive Task Discrimination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 10 s *, target_events = [`contrastChangeB1_start`, `seqLearning_start`, `symbolSearch_start`, `resting_start`, `surroundSuppB1_start`, `video_start`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | contrastChangeB1_start | 0 | Active task: contrast change detection with motor responses |
  | seqLearning_start | 0 | Active task: sequence learning with motor responses |
  | symbolSearch_start | 0 | Active task: symbol search with motor responses |
  | resting_start | 1 | Passive task: eyes-open/closed resting state |
  | surroundSuppB1_start | 1 | Passive task: visual stimulation without response |
  | video_start | 1 | Passive task: movie watching without response |
- **Evidence**:
  - arXiv:2506.19141v2 — Highest-level task taxonomy from competition: active tasks (contrastChangeDetection, seqLearning, symbolSearch with responses) vs passive tasks (restingState, surroundSupp, movie watching); uses task start events as anchors for general task-demand detection
- **Notes**: All six event IDs are native task-start markers confirmed in events.json sidecars and events.tsv files. Active tasks require overt motor responses (button presses in contrastChangeDetection and symbolSearch; dot sequence reproduction in seqLearning), while passive tasks involve only visual fixation or free viewing without required responses. The 10-second epoch from task onset captures initial engagement dynamics and allows spectral features to distinguish active cognitive-motor engagement from passive sensory processing. y=0 aggregates all active task starts and y=1 aggregates all passive task starts, forming a binary classification of general task-demand state.

### Classical Task 15: Resting State Segmentation P-Factor Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | p_factor | Subject-level continuous p-factor score from participants.tsv; higher values indicate greater psychopathology burden. Applied uniformly to all segments from the same subject. Partial completeness (132/136 subjects). |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Resting-state only phenotype prediction as in dedicated benchmark. Segmentation with subject-level p-factor label. No event discrimination needed. Purely data-driven features from continuous resting EEG. Most validated HBN benchmark task.
- **Notes**: Archetype C with info-native label (p_factor from participants.tsv). Segmentation-based epoching with 10s non-overlapping windows from continuous resting-state EEG. No kernel derivation needed — label is pre-existing in participants.tsv.

### Classical Task 16: Resting State Brain Age Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous chronological age in years (float); range ~5.2–21.7; directly predicts brain age from resting-state EEG segments |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — Brain age prediction from resting-state EEG using segmentation-based approaches with continuous age targets
  - 10.1016/j.neuroimage.2020.117001 — Developmental brain age models leveraging large age-range pediatric/adolescent samples for robust EEG-based age estimation
- **Notes**: Segmentation approach pools eyes-open and eyes-closed resting-state periods into 10s non-overlapping segments. The `age` field is a native participants.tsv column (complete, numeric), requiring no kernel derivation. Meta Level is raw because the label source is pre-existing in the dataset metadata. The `resting_start`, `instructed_toOpenEyes`, and `instructed_toCloseEyes` events demarcate the resting-state recording periods but are not used as epoch anchors due to the segmentation method.

### Classical Task 17: All-Task Segmentation p-Factor Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | p_factor | Continuous z-scored p-factor from participants.tsv; higher values indicate greater general psychopathology burden. Applied to all segments from all available tasks per subject (RestingState, video-watching, contrastChangeDetection, surroundSupp, seqLearning, symbolSearch). |
- **Evidence**:
  - arXiv:2506.19141v2 — Multi-task phenotype prediction using all available EEG data; p-factor predicted from segments across all six tasks with task-agnostic feature learning; competition benchmark allows any task combination to maximize data usage per subject.
- **Notes**: Archetype C with segmentation + info-native label. No kernel derivation needed—p_factor is a pre-existing participants.tsv column. The 10s segment length with 50% overlap is inferred from the multi-task learning design rationale (maximizing segment count across all tasks while maintaining statistical power). All task recordings for a subject are concatenated or processed jointly, then segmented uniformly; each segment inherits the same subject-level p_factor value.

### Potential Task 1: Contrast Change Detection Response Side
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 0.5 s *, target_events = [`left_buttonPress`, `right_buttonPress`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `left_buttonPress` | 0 | Left mouse button press response |
  | `right_buttonPress` | 1 | Right mouse button press response |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Alternative labeling using motor response instead of stimulus; two classes left_buttonPress and right_buttonPress with ~9,700 response events total for lateralized readiness potential analysis
- **Notes**: Response-locked epochs centered on button press to capture readiness potential and motor execution. tmin/tmax inferred from standard motor ERP literature (-500ms to +500ms) as epoch_hint.inferred=true.

### Potential Task 2: ehq_total regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | ehq_total | Continuous Edinburgh Handedness Questionnaire total score; range approximately -54.5 to 100.05; higher values indicate stronger right-handedness; missing for 2/136 subjects |
- **Evidence**:
  - participants.tsv — ehq_total column: numeric handedness score, 134/136 subjects available, sample values include 71.17, 100.05, -53.36, -54.49
- **Notes**: Archetype B3 (info-native). The ehq_total field is a pre-existing participants.tsv column requiring no kernel derivation. Segmentation-based epoching is used since handedness is a stable trait variable hypothesized to correlate with sustained EEG features such as frontal alpha asymmetry rather than transient event-locked responses. The 10-second segment length and 50% overlap are inferred from standard practice for trait-level EEG biomarker extraction.

### Potential Task 3: Sequence Learning Block Progression
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 60 s *, target_events = [`learningBlock_1`, `learningBlock_2`, `learningBlock_3`, `learningBlock_4`, `learningBlock_5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `learningBlock_1` | 0 | Start of first sequence learning block |
  | `learningBlock_2` | 1 | Start of second sequence learning block |
  | `learningBlock_3` | 2 | Start of third sequence learning block |
  | `learningBlock_4` | 3 | Start of fourth sequence learning block |
  | `learningBlock_5` | 4 | Start of fifth sequence learning block |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Five learning blocks within sequence learning tasks; learningBlock_1 through learningBlock_5 mark block onsets; ~118-122 block starts per class across seqLearning6target and seqLearning8target variants
- **Notes**: Block-locked epochs capture sustained learning state. 60s duration covers substantial portion of each block; early vs late blocks expected to show different neural signatures of sequence knowledge acquisition. Both 6-target and 8-target sequence learning variants share this block structure. Epoch timing inferred from task structure (blocks are continuous sequence exposure periods).

### Potential Task 4: full_pheno availability classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | full_pheno | Yes → 0 (complete phenotype), No → 1 (incomplete phenotype) |
- **Evidence**:
  - participants.tsv — full_pheno column with values [Yes, No], completeness=complete
- **Notes**: Exploratory proxy task for data quality/recruitment completeness. Uses standard 10-second segmentation with 50% overlap. The full_pheno field is a native participants.tsv column indicating whether all phenotypic assessments were completed for a subject. All samples in the shown rows are Yes, but the column explicitly contains No values in the dataset (dtype=categorical, sample=[Yes, No]). Class imbalance expected with majority Yes.

### Potential Task 5: Contrast Change Detection Block Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 120 s *, target_events = [`contrastChangeB1_start`, `contrastChangeB2_start`, `contrastChangeB3_start`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `contrastChangeB1_start` | 0 | Start of contrast change detection block 1 |
  | `contrastChangeB2_start` | 1 | Start of contrast change detection block 2 |
  | `contrastChangeB3_start` | 2 | Start of contrast change detection block 3 |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Three blocks of contrast change detection with block-start events; ~102-143 block starts per class; tests block-order effects or time-on-task fatigue
- **Notes**: Block-level epoching (120s) captures sustained attention/vigilance periods spanning multiple trials within each block. The three block-start events provide a natural 3-way classification of block order, allowing analysis of fatigue-related neural changes across the session. tmin/tmax inferred from paradigm description (block-level analysis for sustained attention).

### Potential Task 6: Surround Suppression Block Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 120 s *, target_events = [`surroundSuppB1_start`, `surroundSuppB2_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `surroundSuppB1_start` | 0 | Block 1 start of surround suppression task |
  | `surroundSuppB2_start` | 1 | Block 2 start of surround suppression task |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Two blocks of surround suppression task with block-level VEP analysis; ~99-108 block starts per class; tests adaptation/repetition effects across sustained 120s stimulation periods
- **Notes**: Block-level alternative to individual stim_ON events for studying sustained visual adaptation. The 120s epoch captures the full stimulation period where surround suppression shows strong temporal dynamics. Both block start events are confirmed in task-surroundSupp_events.json with event codes 93 (B1) and 97 (B2).

### Potential Task 7: Symbol Search Response Type
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`newPage`, `trialResponse`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `newPage` | 0 | Stimulus onset: new page of symbol search queries shown |
  | `trialResponse` | 1 | Response: subject provided a button press response |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Symbol search task with newPage (~194 events) and trialResponse (~1,247 events) markers; separates perceptual encoding from decision/response stages
- **Notes**: Two-class classification distinguishing stimulus-locked epochs (newPage, perceptual encoding stage) from response-locked epochs (trialResponse, decision/response stage). Class imbalance expected due to fewer newPage events. Epoch window chosen to capture both early visual processing and motor response preparation within the same [-0.2, 1.0]s window.

## Data Quality Notes

- Four subjects (4/136, ~3%) are missing p-factor, attention, internalizing, and externalizing psychopathology scores, limiting sample size for phenotype prediction tasks.
- Two subjects (2/136, ~1.5%) are missing Edinburgh Handedness Questionnaire (ehq_total) scores.
- Sex class imbalance: ~66% male (n=90) versus ~34% female (n=46), which may affect classifier training and evaluation metrics.
- Event counts for dot_no7 and dot_no8 are substantially lower (~396-796) than dot_no1 through dot_no6 (~600-1234), reflecting the 8-target variant being available for fewer subjects than the 6-target variant.
- Movie watching task requires event code disambiguation: all four clips share the same `video_start` event string but have distinct numeric codes (81-84) that must be inspected for correct labeling.
- Several epoch parameter values (tmin, tmax, segment_length, overlap) are marked with asterisks (*) indicating they were inferred from paradigm descriptions rather than explicitly documented in dataset metadata.
- The `Info` table in the File Scan Result is empty (no fields listed), suggesting limited structured metadata extraction at scan time.
- Boundary and break cnt admin events (728 and 1488 total respectively) indicate frequent recording interruptions or concatenated files that may require careful epoch rejection around discontinuities.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
