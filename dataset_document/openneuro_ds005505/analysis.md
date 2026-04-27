# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale, multi-task developmental battery collected from children and adolescents (ages 5.2–21.7). Participants completed six experimental paradigms: naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. EEG data were acquired using a 129-channel system at 500 Hz, with the dataset designed to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `c5d5b3fcfb5b16a1fccbc0117b3c2383aed75a44e6b7c37c2962d9b7d35acbbb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 1136 | admin | raw | Recording start marker |
| `boundary` | 728 | admin | raw | Boundary between video segments |
| `break cnt` | 1488 | admin | raw | Break/cue period marker |
| `contrastChangeB1_start` | 102 | event | raw | Trial phase onset: Contrast change detection block 1 start |
| `contrastChangeB2_start` | 117 | event | raw | Trial phase onset: Contrast change detection block 2 start |
| `contrastChangeB3_start` | 143 | event | raw | Trial phase onset: Contrast change detection block 3 start |
| `contrastTrial_start` | 8884 | event | raw | Trial phase onset: Contrast trial start |
| `dot_no1_OFF` | 600 | event | raw | Dot 1 turned white (OFF) |
| `dot_no1_ON` | 600 | event | raw | Dot 1 turned black (ON) |
| `dot_no2_OFF` | 1202 | event | raw | Dot 2 turned white (OFF) |
| `dot_no2_ON` | 1234 | event | raw | Dot 2 turned black (ON) |
| `dot_no3_OFF` | 600 | event | raw | Dot 3 turned white (OFF) |
| `dot_no3_ON` | 624 | event | raw | Dot 3 turned black (ON) |
| `dot_no4_OFF` | 600 | event | raw | Dot 4 turned white (OFF) |
| `dot_no4_ON` | 600 | event | raw | Dot 4 turned black (ON) |
| `dot_no5_OFF` | 600 | event | raw | Dot 5 turned white (OFF) |
| `dot_no5_ON` | 600 | event | raw | Dot 5 turned black (ON) |
| `dot_no6_OFF` | 600 | event | raw | Dot 6 turned white (OFF) |
| `dot_no6_ON` | 600 | event | raw | Dot 6 turned black (ON) |
| `dot_no7_OFF` | 796 | event | raw | Dot 7 turned white (OFF) |
| `dot_no7_ON` | 792 | event | raw | Dot 7 turned black (ON) |
| `dot_no8_OFF` | 396 | event | raw | Dot 8 turned white (OFF) |
| `dot_no8_ON` | 396 | event | raw | Dot 8 turned black (ON) |
| `fixpoint_ON` | 13248 | event | raw | Fixation point appears |
| `instructed_toCloseEyes` | 680 | event | raw | Trial phase onset: Eyes closed instruction |
| `instructed_toOpenEyes` | 816 | event | raw | Trial phase onset: Eyes open instruction |
| `learningBlock_1` | 122 | event | raw | Trial phase onset: Learning block 1 start |
| `learningBlock_2` | 121 | event | raw | Trial phase onset: Learning block 2 start |
| `learningBlock_3` | 120 | event | raw | Trial phase onset: Learning block 3 start |
| `learningBlock_4` | 119 | event | raw | Trial phase onset: Learning block 4 start |
| `learningBlock_5` | 118 | event | raw | Trial phase onset: Learning block 5 start |
| `left_buttonPress` | 5095 | event | raw | Left button press response |
| `left_target` | 4243 | event | raw | Left-leaning target stimulus |
| `newPage` | 194 | event | raw | New page of symbol search queries |
| `resting_start` | 139 | event | raw | Trial phase onset: Resting state start |
| `right_buttonPress` | 4634 | event | raw | Right button press response |
| `right_target` | 4251 | event | raw | Right-leaning target stimulus |
| `seqLearning_start` | 122 | event | raw | Trial phase onset: Sequence learning task start |
| `seqLearning_stop` | 118 | event | raw | Trial phase onset: Sequence learning task stop |
| `stim_ON` | 13278 | event | raw | Stimulus appears (with 2.4s duration) |
| `surroundSuppB1_start` | 108 | event | raw | Trial phase onset: Surround suppression block 1 start |
| `surroundSuppB2_start` | 99 | event | raw | Trial phase onset: Surround suppression block 2 start |
| `symbolSearch_start` | 76 | event | raw | Trial phase onset: Symbol search task start |
| `trialResponse` | 1247 | event | raw | Subject response in trial |
| `video_start` | 761 | event | raw | Video stream started |
| `video_stop` | 723 | event | raw | Video stream stopped |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: contrast change target direction (2-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s, tmax = 1.0 s, target_events = ["left_target", "right_target"]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|--------|
  | left_target | 0 | Left-leaning target stimulus |
  | right_target | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Dataset documentation explicitly shows left_target and right_target events as distinct stimulus classes in the contrast change detection paradigm, with 4243 left_target and 4251 right_target events across 136 subjects.
- **Notes**: None

### Classical Task 2: symbol search accuracy (2-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = ['trialResponse']`
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|--------|
  | trialResponse | 1 | Correct response (user_answer matched correct_answer) |
  | trialResponse | 0 | Incorrect response (user_answer did not match correct_answer) |
- **Evidence**:
  - task-symbolSearch_events.json (Level ①) — defines `trialResponse` as subject response event, `correct_answer` (0/1 meaning presence/absence of symbol), and `user_answer` (0/1 meaning false/true detection)
  - events.tsv samples — confirmed trialResponse events (n=1247) with user_answer and correct_answer columns
- **Notes**: Kernel derives `accuracy` misc channel by comparing `user_answer` to `correct_answer` per trialResponse event. Binary y=1 for correct, y=0 for incorrect. Since accuracy is kernel-derived, Meta Level = super.

### Classical Task 3: sequence learning 8-target dot position (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s *, tmax = 0.5 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

  | Event ID | y | Meaning |
  |---|---|---|
  | dot_no1_ON | 1 | Dot 1 position |
  | dot_no2_ON | 2 | Dot 2 position |
  | dot_no3_ON | 3 | Dot 3 position |
  | dot_no4_ON | 4 | Dot 4 position |
  | dot_no5_ON | 5 | Dot 5 position |
  | dot_no6_ON | 6 | Dot 6 position |
  | dot_no7_ON | 7 | Dot 7 position |
  | dot_no8_ON | 8 | Dot 8 position |

- **Evidence**:
  - task-seqLearning8target_events.json — Defines all 8 dot_ON events as "Dot number N turned black" within seqLearning scope
  - Event counts confirm: dot_no1_ON=600, dot_no2_ON=1234, dot_no3_ON=624, dot_no4_ON=600, dot_no5_ON=600, dot_no6_ON=600, dot_no7_ON=792, dot_no8_ON=396 (396–1234 per class, ≥2 distinct y: ✓)
- **Notes**: tmin/tmax marked inferred (epoch_hint.inferred=true); each dot number maps to a distinct Event ID as the classification target.

### Potential Task 1: age prediction from resting state
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 5.0 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (years) | Notes |
  |------------|---------------|-------|
  | age | 5.2–21.7 | continuous developmental age variable |
- **Evidence**:
  - 10.1101/089060 — Reference explicitly targets age as continuous predictor using inter-subject correlation of EEG responses; participants.tsv contains age with range 5.2–21.7 years, continuous numeric values. Resting state provides clean segmentation baseline.
  - HBN dataset description confirms RestingState task availability and participants.tsv completeness for age across all 136 subjects (N=136, age=5.2–21.7).
- **Notes**: Archetype C (segmentation + info-native) task using resting-state EEG segments to predict continuous developmental age. Segment length and overlap follow clinical guidelines for developmental EEG analysis. Since the label field `age` is a native participant-level column in participants.tsv, no derived misc channels are required; Meta Level is raw. For segmentation method, tmin/tmax are not applicable parameters.

### Potential Task 2: p-factor psychopathology dimension prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `p_factor`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |---|---|---|
  | p_factor | -0.603 to 1.094 (unitless) | Bifactor model dimensional score from HBN dataset; partial completeness (132/136 subjects) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Dataset documentation identifies p_factor as bifactor model dimensional score and super-level prediction target; participants.tsv shows values from -0.603 to 1.094
- **Notes**: Clinical dimension regression; segment_length derived per SKILL clinical guidelines for resting-state EEG segmentation.

### Potential Task 3: attention dimension prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4.0 s, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `attention`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |---|---|---|
  | attention | -1.085 to 1.826 | super-level target (bifactor phenotypic dimension) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN dataset paper describing bifactor model with attention as distinct phenotypic dimension; participants.tsv attention values confirmed in sample data (132/136 participants)
- **Notes**: Segmentation across all task recordings; attention scores are subject-level (super-level) phenotypic variables constant across all epochs per participant. Range inferred from participants.tsv sample rows (sub-NDARAP359UM6=1.826, sub-NDARBD879MBX=-1.085).

### Potential Task 4: internalizing dimension prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `internalizing`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|---|
  | internalizing | -1.124 – 1.949 (z-score) | Bifactor model internalizing dimension (anxiety/depression spectrum) from HBN participants.tsv |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN dataset paper describing bifactor model including internalizing dimension; participants.tsv values range from -1.124 to 1.949 |
- **Notes**: B3 archetype uses native info column `internalizing` from participants.tsv. Segmentation epochs with 4 s sliding windows and 50% overlap per clinical dimension regression guidelines.

### Potential Task 5: Externalizing Dimension Prediction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4.0 s, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `externalizing`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range | Notes |
  |---|---|---|
  | externalizing | −0.926 to 0.928 | Bifactor model behavioral dimension; super-level phenotypic target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN dataset documentation identifies externalizing as a super-level behavioral dimension in the bifactor model; participants.tsv values range −0.926 to 0.928 across 132/136 participants with complete data
- **Notes**: Clinical dimension regression task; segment_length set per SKILL clinical guidelines. No event anchoring required; epochs are uniformly segmented from continuous EEG recordings.

### Potential Task 6: sex classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |---|---|---|---|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
  - 10.1101/089060 — Reference targets sex as categorical factor in developmental analysis. participants.tsv shows F (46) and M (90) with complete data. H3: Route=info requires Label Field from participants.tsv. Binary classification valid under H2.
- **Notes**: Potential Task using B3 archetype (Route=info, native participants.tsv column). Segmentation approach avoids event anchoring; epochs sampled uniformly from continuous EEG at 50% overlap. Sex field confirmed complete in catalog (N=136, F=46, M=90).

### Potential Task 7: Naturalistic Viewing with Psychopathology Label (Segmented)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 5.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `p_factor`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|---|
  | p_factor | [-1.085, 1.826] (z-score) | Bifactor general psychopathology factor; normative distribution across development |
- **Evidence**:
  - 10.1101/089060 — HBN dataset original protocol connecting EEG to phenotypic measures
  - 10.1101/2024.10.03.615261 — HBN Release 1 paper explicitly linking video-watching EEG biomarkers to age/sex effects and bifactor model dimensions (p_factor, attention, internalizing, externalizing)
- **Notes**: Segments are extracted from video_start-anchored continuous recording. Each subject's segmented epochs receive the same super-level p_factor label (subject-level regression). The p_factor captures general psychopathology variance above specific dimension contributions.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
