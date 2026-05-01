# Healthy Brain Network (HBN) EEG - Release 4

**Dataset**: `openneuro_ds005508` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005508
**Category**: Complex Applied | **Subjects**: 324 | **Files (Completed)**: 3342 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 4 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `8ca00d13062ddeb2c9ff9fec7ba02291f7ded72272f85478303cca5b9787f50c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 2502 | admin | raw | End-of-recording marker |
| `boundary` | 1871 | admin | raw | Segment boundary marker |
| `break cnt` | 3452 | admin | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 258 | event | raw | Contrast change block 1 onset (surrounding suppression) |
| `contrastChangeB2_start` | 279 | event | raw | Contrast change block 2 onset (surrounding suppression) |
| `contrastChangeB3_start` | 304 | event | raw | Contrast change block 3 onset (surrounding suppression) |
| `contrastTrial_start` | 20646 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 1468 | event | raw | Dot pattern offset - position 1 (surrounding suppression) |
| `dot_no1_ON` | 1468 | event | raw | Dot pattern onset - position 1 (surrounding suppression) |
| `dot_no2_OFF` | 2941 | event | raw | Dot pattern offset - position 2 (surrounding suppression) |
| `dot_no2_ON` | 3055 | event | raw | Dot pattern onset - position 2 (surrounding suppression) |
| `dot_no3_OFF` | 1468 | event | raw | Dot pattern offset - position 3 (surrounding suppression) |
| `dot_no3_ON` | 1570 | event | raw | Dot pattern onset - position 3 (surrounding suppression) |
| `dot_no4_OFF` | 1468 | event | raw | Dot pattern offset - position 4 (surrounding suppression) |
| `dot_no4_ON` | 1468 | event | raw | Dot pattern onset - position 4 (surrounding suppression) |
| `dot_no5_OFF` | 1468 | event | raw | Dot pattern offset - position 5 (surrounding suppression) |
| `dot_no5_ON` | 1468 | event | raw | Dot pattern onset - position 5 (surrounding suppression) |
| `dot_no6_OFF` | 1468 | event | raw | Dot pattern offset - position 6 (surrounding suppression) |
| `dot_no6_ON` | 1468 | event | raw | Dot pattern onset - position 6 (surrounding suppression) |
| `dot_no7_OFF` | 1735 | event | raw | Dot pattern offset - position 7 (surrounding suppression) |
| `dot_no7_ON` | 1734 | event | raw | Dot pattern onset - position 7 (surrounding suppression) |
| `dot_no8_OFF` | 867 | event | raw | Dot pattern offset - position 8 (surrounding suppression, deviant) |
| `dot_no8_ON` | 867 | event | raw | Dot pattern onset - position 8 (surrounding suppression, deviant) |
| `fixpoint_ON` | 35072 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 1608 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 1929 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 296 | event | raw | Sequence learning block 1 onset |
| `learningBlock_2` | 295 | event | raw | Sequence learning block 2 onset |
| `learningBlock_3` | 293 | event | raw | Sequence learning block 3 onset |
| `learningBlock_4` | 293 | event | raw | Sequence learning block 4 onset |
| `learningBlock_5` | 291 | event | raw | Sequence learning block 5 onset |
| `left_buttonPress` | 11751 | event | raw | Participant button press - left hand |
| `left_target` | 9806 | event | raw | Left-side target stimulus |
| `newPage` | 509 | event | raw | New page/screen presentation |
| `resting_start` | 326 | event | raw | Resting-state block onset |
| `right_buttonPress` | 10656 | event | raw | Participant button press - right hand |
| `right_target` | 9909 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 296 | event | raw | Sequence learning task onset |
| `seqLearning_stop` | 291 | event | raw | Sequence learning task offset |
| `stim_ON` | 35171 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 278 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 270 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 195 | event | raw | Symbol search task onset |
| `trialResponse` | 3286 | event | raw | Trial response event |
| `video_start` | 1368 | event | raw | Movie/video viewing onset |
| `video_stop` | 1342 | event | raw | Movie/video viewing offset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Sequence Learning State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stim_ON`, `fixpoint_ON`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stim_ON` (within learning block) | Learning state from behavioral recall | Stimulus at unknown/newly-learned/known stage |
- **Super Meta Notes**: Learning state labels (unknown vs. newly-learned vs. known) must be derived from participant behavioral recall reports. Kernel step: Parse trial sequence within `learningBlock_1` through `learningBlock_5` (1,468 combined); join with per-subject recall accuracy data to assign learning state labels. States progress from unknown → newly-learned → known as blocks advance.
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — Describes sequence learning paradigm with explicit learning state categories
  - Paradigm: Block markers (`seqLearning_start`: 296, `learningBlock_1-5`: 1,468) and stimulus events exist, but learning state labels require derivation from behavioral data not present in event structure
- **Kernel Notes**: Requires joining EEG epochs with external behavioral recall files to determine learning state. Use subject-wise splits—learning state is confounded with time within session. Alternative: predict block number (1-5) as proxy for learning progression.

### Potential Task 2: Surrounding Suppression Visual Processing
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `dot_no1_ON` through `dot_no7_ON` | 0 | Standard surround condition |
  | `dot_no8_ON` | 1 | Deviant/singleton surround condition |
- **Evidence**:
  - Paradigm: Surrounding suppression blocks (`surroundSuppB1_start`: 278, `surroundSuppB2_start`: 270) with 8 dot pattern types (~10,000 combined onset events). Dot_no8 has fewer trials (867) suggesting it may be the deviant/singleton condition.
  - DOI: `10.1038/sdata.2017.40` — Lists surround suppression as core paradigm
- **Kernel Notes**: Longer tmax=1.5s captures sustained suppression effects. Condition labels (standard vs. deviant) require verification from paradigm documentation. Alternative: binary classification of dot patterns by surround configuration if stimulus parameters are known.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
