# Healthy Brain Network (HBN) EEG - Release 8

**Dataset**: `openneuro_ds005512` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005512
**Category**: Complex Applied | **Subjects**: 257 | **Files (Completed)**: 2320 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 8 is a large-scale, multi-task developmental battery collected from children and adolescents across the New York City area. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population, enabling multi-label classification of DSM-V diagnoses.

## File Scan Result

> **Kernel SHA256**: `1de300b1f9f342318c2e24b4f83d3cea81182875e0285df17bd675309c276388`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 1751 | event | raw | End-of-recording marker |
| `boundary` | 1237 | event | raw | Segment boundary marker |
| `break cnt` | 2258 | event | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 182 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 194 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 170 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 12963 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 968 | event | raw | Dot stimulus 1 offset |
| `dot_no1_ON` | 968 | event | raw | Dot stimulus 1 onset |
| `dot_no2_OFF` | 1946 | event | raw | Dot stimulus 2 offset |
| `dot_no2_ON` | 1992 | event | raw | Dot stimulus 2 onset |
| `dot_no3_OFF` | 968 | event | raw | Dot stimulus 3 offset |
| `dot_no3_ON` | 1017 | event | raw | Dot stimulus 3 onset |
| `dot_no4_OFF` | 968 | event | raw | Dot stimulus 4 offset |
| `dot_no4_ON` | 984 | event | raw | Dot stimulus 4 onset |
| `dot_no5_OFF` | 968 | event | raw | Dot stimulus 5 offset |
| `dot_no5_ON` | 968 | event | raw | Dot stimulus 5 onset |
| `dot_no6_OFF` | 968 | event | raw | Dot stimulus 6 offset |
| `dot_no6_ON` | 968 | event | raw | Dot stimulus 6 onset |
| `dot_no7_OFF` | 1076 | event | raw | Dot stimulus 7 offset |
| `dot_no7_ON` | 1072 | event | raw | Dot stimulus 7 onset |
| `dot_no8_OFF` | 536 | event | raw | Dot stimulus 8 offset |
| `dot_no8_ON` | 536 | event | raw | Dot stimulus 8 onset |
| `fixpoint_ON` | 22913 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 1104 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 1326 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 200 | event | raw | Sequence learning block 1 |
| `learningBlock_2` | 195 | event | raw | Sequence learning block 2 |
| `learningBlock_3` | 191 | event | raw | Sequence learning block 3 |
| `learningBlock_4` | 191 | event | raw | Sequence learning block 4 |
| `learningBlock_5` | 191 | event | raw | Sequence learning block 5 |
| `left_buttonPress` | 6946 | event | raw | Participant button press - left hand |
| `left_target` | 6151 | event | raw | Left-side target stimulus |
| `newPage` | 366 | event | raw | New page/instruction display |
| `resting_start` | 229 | event | raw | Resting-state block onset |
| `right_buttonPress` | 6875 | event | raw | Participant button press - right hand |
| `right_target` | 6231 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 202 | event | raw | Sequence learning block onset |
| `seqLearning_stop` | 191 | event | raw | Sequence learning block offset |
| `stim_ON` | 22981 | event | raw | Contrast change stimulus onset |
| `surroundSuppB1_start` | 182 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 176 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 144 | event | raw | Symbol search task onset |
| `trialResponse` | 2318 | event | raw | Trial response event (correct responses) |
| `video_start` | 950 | event | raw | Movie watching onset |
| `video_stop` | 877 | event | raw | Movie watching offset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Psychiatric Diagnosis Classification from Resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 40.0 s, overlap = 0.95, target_events = [`instructed_toCloseEyes`, `resting_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | DSM-V diagnosis column | 0 | No diagnosis (neurotypical) |
  | DSM-V diagnosis column | 1 | Presence of diagnosis (ADHD/ANX/SLD/ASD/DISR/COM/DEP/Other) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-task multi-label classification of 7 DSM-V psychiatric diagnoses (ADHD, ODD, anxiety disorder, mood disorder, ASD, SLD, communication disorder) from resting EEG using eyes-closed blocks, 2s epochs with 95% overlap, and 1-40 Hz spectral features
- **Kernel Notes**: Filter for `instructed_toCloseEyes` or `resting_start` events to isolate eyes-closed resting segments. Extract 2s epochs with ~0.1s step (~38 epochs per 40s block) to match the spectral feature extraction pipeline. Compute spectral power in canonical bands (delta 1-4 Hz, theta 4-8 Hz, alpha 8-13 Hz, beta 13-30 Hz, gamma 30-40 Hz). Load DSM-V derived labels (8 binary vectors) from misc label source. Use multi-label classification (one-vs-rest or multi-output approach) to predict diagnosis presence/absence. Implement subject-wise train/test splits to prevent label leakage. Note: N~2,042 from earlier HBN releases used in paper; openneuro_ds005512 is a later release from the same ecosystem with matching paradigm structure.

### Normal Task 1: Contrast Detection Sensory Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stim_ON`, `left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stim_ON` | 0 | Contrast change stimulus onset |
  | `left_target` | 1 | Left-side target stimulus |
  | `right_target` | 2 | Right-side target stimulus |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset documentation confirming contrast detection paradigm with `stim_ON`, `fixpoint_ON`, `left_target`, `right_target` as primary events
- **Kernel Notes**: Use `stim_ON` (n=22981) as primary contrast change marker; negative tmin captures pre-stimulus baseline. `fixpoint_ON` (n=22913) marks trial start cue preceding stimulus change. Note mismatch between `trialResponse` (n=2318) and button press counts (~13821) suggesting selective trial marking—likely correct responses only. Extract stimulus-locked epochs for sensory processing analysis. Admin markers (`boundary`, `break cnt`, `9999`) should be excluded from supervised targets.

### Potential Task 1: Block/State Decoding Across Paradigms
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`, `video_start`, `video_stop`, `seqLearning_start`, `symbolSearch_start`, `contrastTrial_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
  | `video_start` | 2 | Movie watching onset |
  | `video_stop` | 3 | Movie watching offset |
  | `seqLearning_start` | 4 | Sequence learning block |
  | `symbolSearch_start` | 5 | Symbol search task |
  | `contrastTrial_start` | 6 | Contrast detection trial block |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG documentation lists 6 paradigms: resting state, movie watching, contrast detection, surround suppression, sequence learning, and symbol search with corresponding block markers
  - DOI: 10.1038/sdata.2017.40 — Earlier HBN pilot (N=126) confirms multi-task battery structure with block-level state markers
- **Kernel Notes**: Overlap=0.5 creates dense segment coverage for state classification across sustained blocks. Verify block durations vary by paradigm (resting ~40s, movie watching ~variable, tasks ~variable). Keep block-label mapping stable across releases. `learningBlock_1-5` (n~200 each) and `surroundSuppB1-3` provide additional task-specific segments. `break cnt` (2258) and `boundary` (1237) are admin markers—exclude from supervised targets.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
