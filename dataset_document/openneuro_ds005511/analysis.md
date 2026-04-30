# Healthy Brain Network (HBN) EEG - Release 7

**Dataset**: `openneuro_ds005511` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005511
**Category**: Complex Applied | **Subjects**: 381 | **Files (Completed)**: 3100 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 7 is a large-scale, multi-task developmental battery collected from children and adolescents ages 5–21. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks across multiple recording sessions. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using standardized clinical assessments and high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `653efcd3f42364f68252d19dd092a59c303dadbb65fee162019431e8e8f84f00`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 2143 | admin | raw | End-of-recording marker |
| `boundary` | 1728 | admin | raw | Segment boundary marker |
| `break cnt` | 3092 | admin | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 118 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 232 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 206 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 13272 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 1668 | event | raw | Surrounding suppression dot 1 offset |
| `dot_no1_ON` | 1668 | event | raw | Surrounding suppression dot 1 onset |
| `dot_no2_OFF` | 3347 | event | raw | Surrounding suppression dot 2 offset |
| `dot_no2_ON` | 3345 | event | raw | Surrounding suppression dot 2 onset |
| `dot_no3_OFF` | 1668 | event | raw | Surrounding suppression dot 3 offset |
| `dot_no3_ON` | 1675 | event | raw | Surrounding suppression dot 3 onset |
| `dot_no4_OFF` | 1668 | event | raw | Surrounding suppression dot 4 offset |
| `dot_no4_ON` | 1668 | event | raw | Surrounding suppression dot 4 onset |
| `dot_no5_OFF` | 1668 | event | raw | Surrounding suppression dot 5 offset |
| `dot_no5_ON` | 1668 | event | raw | Surrounding suppression dot 5 onset |
| `dot_no6_OFF` | 1668 | event | raw | Surrounding suppression dot 6 offset |
| `dot_no6_ON` | 1668 | event | raw | Surrounding suppression dot 6 onset |
| `dot_no7_OFF` | 2235 | event | raw | Surrounding suppression dot 7 offset |
| `dot_no7_ON` | 2232 | event | raw | Surrounding suppression dot 7 onset |
| `dot_no8_OFF` | 1116 | event | raw | Surrounding suppression dot 8 offset |
| `dot_no8_ON` | 1116 | event | raw | Surrounding suppression dot 8 onset |
| `fixpoint_ON` | 34688 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 1825 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 2193 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 338 | event | raw | Sequence learning block 1 onset |
| `learningBlock_2` | 333 | event | raw | Sequence learning block 2 onset |
| `learningBlock_3` | 333 | event | raw | Sequence learning block 3 onset |
| `learningBlock_4` | 332 | event | raw | Sequence learning block 4 onset |
| `learningBlock_5` | 332 | event | raw | Sequence learning block 5 onset |
| `left_buttonPress` | 7530 | event | raw | Participant button press - left hand |
| `left_target` | 6361 | event | raw | Left-side target stimulus |
| `newPage` | 603 | admin | raw | New page transition (task instruction) |
| `resting_start` | 377 | event | raw | Resting-state block onset |
| `right_buttonPress` | 6992 | event | raw | Participant button press - right hand |
| `right_target` | 6384 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 338 | event | raw | Sequence learning task onset |
| `seqLearning_stop` | 332 | event | raw | Sequence learning task offset |
| `stim_ON` | 34708 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 314 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 228 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 228 | event | raw | Symbol search task onset |
| `trialResponse` | 4059 | event | raw | Trial response event |
| `video_start` | 1115 | event | raw | Naturalistic movie playback start |
| `video_stop` | 1097 | event | raw | Naturalistic movie playback stop |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

(No tasks could be synthesized.)

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
