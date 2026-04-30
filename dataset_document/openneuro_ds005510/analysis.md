# Healthy Brain Network (HBN) EEG - Release 6

**Dataset**: `openneuro_ds005510` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005510
**Category**: Complex Applied | **Subjects**: 3000 | **Files (Completed)**: 1227 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 6 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching (Despicable Me, The Present, Diary of a Wimpy Kid, Fun with Fractals), eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population with phenotypic assessments including IQ, behavioral problems, ADHD, anxiety, and socioeconomic status.

## File Scan Result

> **Kernel SHA256**: `91fb01ced8d2c0bb6e3439df752198906b8698b9ee4263f78340a136ecd2e06e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 866 | admin | raw | End-of-recording marker |
| `boundary` | 666 | admin | raw | Segment boundary marker |
| `break cnt` | 1242 | admin | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 44 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 111 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 94 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 5817 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 634 | event | raw | Surround suppression stimulus element 1 offset |
| `dot_no1_ON` | 634 | event | raw | Surround suppression stimulus element 1 onset |
| `dot_no2_OFF` | 1271 | event | raw | Surround suppression stimulus element 2 offset |
| `dot_no2_ON` | 1268 | event | raw | Surround suppression stimulus element 2 onset |
| `dot_no3_OFF` | 634 | event | raw | Surround suppression stimulus element 3 offset |
| `dot_no3_ON` | 634 | event | raw | Surround suppression stimulus element 3 onset |
| `dot_no4_OFF` | 634 | event | raw | Surround suppression stimulus element 4 offset |
| `dot_no4_ON` | 648 | event | raw | Surround suppression stimulus element 4 onset |
| `dot_no5_OFF` | 634 | event | raw | Surround suppression stimulus element 5 offset |
| `dot_no5_ON` | 634 | event | raw | Surround suppression stimulus element 5 onset |
| `dot_no6_OFF` | 634 | event | raw | Surround suppression stimulus element 6 offset |
| `dot_no6_ON` | 634 | event | raw | Surround suppression stimulus element 6 onset |
| `dot_no7_OFF` | 854 | event | raw | Surround suppression stimulus element 7 offset |
| `dot_no7_ON` | 852 | event | raw | Surround suppression stimulus element 7 onset |
| `dot_no8_OFF` | 426 | event | raw | Surround suppression stimulus element 8 offset |
| `dot_no8_ON` | 426 | event | raw | Surround suppression stimulus element 8 onset |
| `fixpoint_ON` | 13696 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 676 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 810 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 129 | event | raw | Sequence learning sub-block 1 |
| `learningBlock_2` | 127 | event | raw | Sequence learning sub-block 2 |
| `learningBlock_3` | 126 | event | raw | Sequence learning sub-block 3 |
| `learningBlock_4` | 126 | event | raw | Sequence learning sub-block 4 |
| `learningBlock_5` | 126 | event | raw | Sequence learning sub-block 5 |
| `left_buttonPress` | 3743 | event | raw | Participant button press - left hand |
| `left_target` | 2793 | event | raw | Left visual field target stimulus |
| `newPage` | 224 | event | raw | New page/symbol search trial marker |
| `resting_start` | 138 | event | raw | Resting-state block onset |
| `right_buttonPress` | 3249 | event | raw | Participant button press - right hand |
| `right_target` | 2796 | event | raw | Right visual field target stimulus |
| `seqLearning_start` | 129 | event | raw | Sequence learning block onset |
| `seqLearning_stop` | 126 | event | raw | Sequence learning block offset |
| `stim_ON` | 13706 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 118 | event | raw | Surround suppression block 1 onset |
| `surroundSuppB2_start` | 96 | event | raw | Surround suppression block 2 onset |
| `symbolSearch_start` | 86 | event | raw | Symbol search task onset |
| `trialResponse` | 1483 | event | raw | Trial response event |
| `video_start` | 441 | event | raw | Movie viewing onset |
| `video_stop` | 435 | event | raw | Movie viewing offset |


### MISC Label Summary
*No MISC channels detected in this dataset scan.*
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Surround Suppression ERP Paradigm
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `dot_no1_ON` | continuous | Surround suppression stimulus element 1 onset |
  | `dot_no2_ON` | continuous | Surround suppression stimulus element 2 onset |
  | `dot_no3_ON` | continuous | Surround suppression stimulus element 3 onset |
  | `dot_no4_ON` | continuous | Surround suppression stimulus element 4 onset |
  | `dot_no5_ON` | continuous | Surround suppression stimulus element 5 onset |
  | `dot_no6_ON` | continuous | Surround suppression stimulus element 6 onset |
  | `dot_no7_ON` | continuous | Surround suppression stimulus element 7 onset |
  | `dot_no8_ON` | continuous | Surround suppression stimulus element 8 onset |
- **Evidence**:
  - DOI: `10.1101/2024.10.03.615261` — Dataset paper mentions surround suppression as one of the six HBN-EEG sensory paradigms.
  - DOI: `10.1038/sdata.2017.40` — Parent resource describes surround suppression paradigm for information processing assessment.
- **Kernel Notes**: The dot_ON/dot_OFF events (n=634–1271) likely represent individual elements in a surround suppression stimulus configuration (central target + surrounding context). Use `surroundSuppB1_start`, `surroundSuppB2_start` (n=118, 96) to identify task blocks. Compute suppression index (response amplitude in suppressive vs facilitative contexts). Requires understanding of stimulus configuration from task-sidecar JSON — verify element mapping and suppression condition coding before analysis.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
