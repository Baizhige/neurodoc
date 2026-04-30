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

### Classical Task 1: Resting-State Psychiatric Disorder Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20.0 s (eyes-open) * or 40.0 s (eyes-closed) *, overlap = 0.0, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `instructed_toOpenEyes` | DSM-V diagnosis from subject metadata | Resting EEG during eyes-open; label from clinical assessment |
  | `instructed_toCloseEyes` | DSM-V diagnosis from subject metadata | Resting EEG during eyes-closed; label from clinical assessment |
- **Super Meta Notes**: Labels derived from subject-level psychiatric diagnoses (ADHD, ODD, CD, Anxiety, Mood, ASD, Psychosis spectrum) and continuous symptom severity measures from companion HBN clinical assessment files. Kernel step: Load per-subject diagnosis vector from metadata; assign same label to all resting-state epochs from that subject. Multi-label formulation possible (subjects may have comorbid diagnoses).
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2022.119348` — Explicit ML benchmark defining 7-class psychiatric multimorbidity classification from HBN resting EEG; uses eyes-open/closed epochs with tmax=20s/40s respectively; reports multi-label formulation for comorbid diagnoses
  - DOI: `10.1016/j.neuroimage.2020.117001` — Validates HBN resting EEG for predicting phenotypic measures including ADHD, anxiety, and CBCL scores; supports regression and classification of continuous symptom severity
- **Kernel Notes**: Use long-event epochs to capture sustained resting-state neural dynamics. Labels are subject-level (not trial-level)—ensure all epochs from same subject share the same diagnosis label. For multi-label classification, binarize each diagnosis independently. Validate using stratified subject-wise splits to prevent data leakage.

### Normal Task 1: Motor Response Lateralization Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_buttonPress`, `right_buttonPress`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_buttonPress` | 0 | Left-hand button press response |
  | `right_buttonPress` | 1 | Right-hand button press response |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2022.119348` — Supports lateralized motor responses as features in psychiatric prediction; motor asymmetry patterns differ across disorders
  - Paradigm: Event structure explicitly distinguishes left (11,751 trials) and right (10,656 trials) hand responses with sufficient trial counts for classification
- **Kernel Notes**: Epoch around motor response events to capture pre-movement planning (LRP) and post-response processing. Filter by block membership (`contrastTrial_start`) for task-related responses vs. spontaneous presses. Use cue-aligned epochs from corresponding stimulus events for stimulus-locked analysis.

### Normal Task 2: Target vs. Non-Target Contrast Detection ERP
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-side target stimulus in contrast detection task |
  | `right_target` | 1 | Right-side target stimulus in contrast detection task |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — Original HBN paradigm description includes contrast detection as core information processing task
  - Paradigm: Clear event structure with 9,806 left-target and 9,909 right-target trials; block markers (`contrastTrial_start`: 20,646) confirm experimental context
- **Kernel Notes**: Epoch around target stimulus onsets to capture visual ERP components (N100, P200, P300). Pre-stimulus window (-0.5 to 0 s) provides baseline. Filter epochs to ensure they fall within `contrastTrial_start` blocks. Consider side-agnostic target vs. non-target classification by adding `stim_ON` as non-target events.

### Potential Task 1: Sequence Learning State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stim_ON`, `fixpoint_ON`]
- **Label Route**: `Annotation`
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

### Potential Task 3: Naturalistic Movie Viewing Time-Frequency Analysis
- **Task Type**: regression / classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 300.0 s, overlap = 0.5, segment_length = 10.0 s, target_events = [`video_start`, `video_stop`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `video_start` | Movie content label from annotation | Continuous naturalistic stimulus epoch |
- **Super Meta Notes**: Labels derived from movie annotation files (scene boundaries, emotional content, narrative events). Kernel step: Load frame-accurate movie annotations; map segment timestamps to EEG epochs. Without annotations, treat as unsupervised time-frequency decomposition task.
- **Evidence**:
  - DOI: `10.1101/089060` — Discusses neural responses to naturalistic videos in HBN context (partial evidence; sample size and dataset version differ)
  - Paradigm: Movie watching segments (`video_start`: 1,368, `video_stop`: 1,342) provide continuous naturalistic stimulus periods
- **Kernel Notes**: Use overlapping short segments (10 s) for time-frequency analysis. Without external annotations, perform exploratory TF decomposition without supervised labels. Frame-rate sync may enable stimulus-locked analysis if movie ID and timestamp alignment are available.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
