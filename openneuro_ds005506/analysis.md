# Healthy Brain Network (HBN) EEG - Release 2

**Dataset**: `openneuro_ds005506` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005506
**Category**: Complex Applied | **Subjects**: 152 | **Files (Completed)**: 1405 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 2 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `4a1d43c3be46afdd8d1652c35836f64bbffb8609c451ea9fab1360705fb5640f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 799 | event | raw | Segment boundary marker |
| `break_cnt` | 1577 | event | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 107 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 120 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 154 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 9310 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 640 | event | raw | Dot probe 1 offset |
| `dot_no1_ON` | 640 | event | raw | Dot probe 1 onset |
| `dot_no2_OFF` | 1288 | event | raw | Dot probe 2 offset |
| `dot_no2_ON` | 1326 | event | raw | Dot probe 2 onset |
| `dot_no3_OFF` | 640 | event | raw | Dot probe 3 offset |
| `dot_no3_ON` | 679 | event | raw | Dot probe 3 onset |
| `dot_no4_OFF` | 640 | event | raw | Dot probe 4 offset |
| `dot_no4_ON` | 640 | event | raw | Dot probe 4 onset |
| `dot_no5_OFF` | 640 | event | raw | Dot probe 5 offset |
| `dot_no5_ON` | 640 | event | raw | Dot probe 5 onset |
| `dot_no6_OFF` | 640 | event | raw | Dot probe 6 offset |
| `dot_no6_ON` | 640 | event | raw | Dot probe 6 onset |
| `dot_no7_OFF` | 756 | event | raw | Dot probe 7 offset |
| `dot_no7_ON` | 756 | event | raw | Dot probe 7 onset |
| `dot_no8_OFF` | 378 | event | raw | Dot probe 8 offset |
| `dot_no8_ON` | 378 | event | raw | Dot probe 8 onset |
| `end_of_recording` | 1150 | event | raw | End-of-recording marker |
| `fixpoint_ON` | 14081 | event | raw | Fixation point onset (trial cue) |
| `instructed_toCloseEyes` | 736 | event | raw | Instruction to close eyes (resting) |
| `instructed_toOpenEyes` | 883 | event | raw | Instruction to open eyes (resting) |
| `learningBlock_1` | 131 | event | raw | Sequence learning block 1 |
| `learningBlock_2` | 129 | event | raw | Sequence learning block 2 |
| `learningBlock_3` | 128 | event | raw | Sequence learning block 3 |
| `learningBlock_4` | 126 | event | raw | Sequence learning block 4 |
| `learningBlock_5` | 126 | event | raw | Sequence learning block 5 |
| `left_buttonPress` | 5762 | event | raw | Left-hand button press response |
| `left_target` | 4439 | event | raw | Left-side target stimulus |
| `newPage` | 215 | event | raw | New page/screen event |
| `resting_start` | 156 | event | raw | Resting-state block onset |
| `right_buttonPress` | 4970 | event | raw | Right-hand button press response |
| `right_target` | 4463 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 131 | event | raw | Sequence learning block onset |
| `seqLearning_stop` | 126 | event | raw | Sequence learning block offset |
| `stim_ON` | 14116 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 117 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 103 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 84 | event | raw | Symbol search task block onset |
| `trialResponse` | 1372 | event | raw | Trial response event |
| `video_start` | 797 | event | raw | Movie clip onset |
| `video_stop` | 765 | event | raw | Movie clip offset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Phenotypic Regression from Functional Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`video_start`, `resting_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|�---|
  | N/A (continuous) | age | Subject age in years |
  | N/A (continuous) | sex | Subject biological sex (binary) |
  | N/A (continuous) | IQ | WISC full-scale IQ score |
  | N/A (continuous) | ADHD | SWAN ADHD measure |
  | N/A (continuous) | anxiety | SCARED anxiety measure |
  | N/A (continuous) | CBCL | Child Behavior Checklist total score |
  | N/A (continuous) | SES | Barratt SES score |
- **Super Meta Notes**: Derived from behavioral assessments (WISC, CBCL, Barratt SES, SWAN, SCARED, MFQ, IAT, SDS, DTS) administered separately from EEG recording. Kernel step: Compute imaginary coherence (iCOH) in delta/theta/alpha/beta bands from 2s epochs aligned to video_start and resting_start, then apply MDMR or similar multivariate regression to relate connectivity matrices to phenotypic variables. Subject-wise train/test splits required to prevent data leakage when joining EEG epochs with phenotypic CSV by subject ID.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Functional connectivity regression of 12 phenotypic/demographic variables (age, sex, IQ, ADHD, anxiety, CBC, SES) from whole-brain iCOH connectivity patterns in source space across resting and video tasks (N=1657, HBN Biobank)
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-domain psychiatric prediction benchmark using resting EEG; includes symptom severity regression as secondary challenge
- **Kernel Notes**: Extract 2s contiguous epochs (no overlap) from video and resting segments to compute clean frequency-band connectivity matrices. Resting epochs align to `resting_start` (156 events); video epochs align to `video_start` (797 events). Exclude admin markers (boundary, break_cnt, end_of_recording) from segmentation.

### Classical Task 2: Psychiatric Multimorbidity Multi-Label Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 0.5, target_events = [`resting_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|�---|
  | N/A (multi-label) | internalizing | Internalizing disorder dimension (anxiety, depression, OCD) |
  | N/A (multi-label) | externalizing | Externalizing disorder dimension (ADHD, ODD, CD) |
  | N/A (multi-label) | attention | Attention domain score |
  | N/A (multi-label) | p_factor | P-factor (general psychopathology) |
  | N/A (multi-label) | DSM_diagnoses | 7 DSM-V diagnoses (multi-label binary flags) |
- **Super Meta Notes**: Labels derived from clinical assessment batteries administered during HBN study visit. Bifactor model dimensions (internalizing, externalizing, attention, p-factor) from questionnaire data per DOI 10.1101/2024.10.03.615261. DSM-V diagnoses are binary multi-label per DOI 10.1016/j.neuroimage.2022.119348. Kernel must load per-subject labels from companion clinical assessment files.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Benchmark for prediction of psychiatric multimorbidity from resting EEG; defines multi-label classification of 7 DSM-V diagnoses and symptom severity regression (N=2042)
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG FAIR implementation; explicitly lists internalizing, externalizing, attention, p-factor labels available for ML tasks from mixed task battery
- **Kernel Notes**: Resting-state segments defined by `resting_start` (156 events) with instruction markers (`instructed_toOpenEyes`, `instructed_toCloseEyes`) and implicit block boundaries. 50% overlap increases sample size for multi-label classification. Apply subject-wise cross-validation to prevent data leakage across psychiatric label categories.

### Potential Task 1: Contrast Detection Sensory ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [`stim_ON`, `left_target`, `right_target`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|�---|
  | `stim_ON` | 1 | Contrast detection stimulus presented |
  | `left_target` | 2 | Left-side target stimulus |
  | `right_target` | 3 | Right-side target stimulus |
  | `left_buttonPress` | 4 | Left-hand button press (response) |
  | `right_buttonPress` | 5 | Right-hand button press (response) |
- **Super Meta Notes**: (none — trial-level event labels)
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor; defines contrast detection task structure with stim_ON (14116), fixpoint_ON (14081), left/right target events, and button press responses
  - DOI: 10.1016/j.neuroimage.2020.117001 — [indirect] Contrast detection paradigms commonly used for sensory ERP analysis in developmental populations
- **Kernel Notes**: Use `fixpoint_ON` (14081 events) as trial cue anchor; stimulus events aligned to `stim_ON` (14116 events). Standard -0.2 to 1.0s window captures pre-stimulus baseline and stimulus-evoked N100/P200 ERP components. Exclude admin events (boundary=799, break_cnt=1577, end_of_recording=1150) from supervised target sets.

### Potential Task 2: Experimental Task State Decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`video_start`, `resting_start`, `seqLearning_start`, `surroundSuppB1_start`, `surroundSuppB2_start`, `symbolSearch_start`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|�---|
  | `video_start` | 1 | Movie watching block |
  | `video_stop` | 2 | End of movie segment |
  | `resting_start` | 3 | Resting-state block |
  | `seqLearning_start` | 4 | Sequence learning block onset |
  | `surroundSuppB1_start` | 5 | Surrounding suppression block 1 |
  | `surroundSuppB2_start` | 6 | Surrounding suppression block 2 |
  | `symbolSearch_start` | 7 | Symbol search task block |
- **Super Meta Notes**: (none — block-level state labels)
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor; lists naturalistic movie watching, resting state, sequence learning, surrounding suppression, and symbol search as distinct experimental paradigms within the mixed task battery
- **Kernel Notes**: 50% overlap recommended to increase sample size for multi-class state decoding across paradigms. Block onsets define experimental states rather than individual trials. Exclude `boundary` (799), `break_cnt` (1577), and `end_of_recording` (1150) admin markers from target event lists.

### Normal Task 1: Sequence Learning Oscillatory Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 0.0, target_events = [`learningBlock_1`, `learningBlock_2`, `learningBlock_3`, `learningBlock_4`, `learningBlock_5`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|�---|
  | `learningBlock_1` | 1 | Sequence learning block 1 (earliest) |
  | `learningBlock_2` | 2 | Sequence learning block 2 |
  | `learningBlock_3` | 3 | Sequence learning block 3 |
  | `learningBlock_4` | 4 | Sequence learning block 4 |
  | `learningBlock_5` | 5 | Sequence learning block 5 (latest) |
- **Super Meta Notes**: (none — block-level sequential labels)
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — [indirect] Lists sequence learning as one of the five core HBN paradigms; learningBlock_1 through _5 events (131, 129, 128, 126, 126 counts) suggest progressive learning across 5 sub-blocks
  - DOI: 10.1016/j.neuroimage.2020.117001 — [indirect] Oscillatory changes across learning trials observed in similar developmental EEG studies
- **Kernel Notes**: Fixed 4s windows aligned to learning block onsets without overlap to capture learning-related theta/beta oscillatory changes across progressive blocks. 5-class block ordering may serve as proxy for learning progression when behavioral accuracy data is unavailable. Exclude `seqLearning_stop` (126 events) and `boundary` (799) admin markers.