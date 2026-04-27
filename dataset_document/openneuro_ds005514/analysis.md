# Healthy Brain Network (HBN) EEG - Release 9

**Dataset**: `openneuro_ds005514` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005514
**Category**: Complex Applied | **Subjects**: 295 | **Files (Completed)**: 2885 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 9 is a large-scale, multi-task developmental battery collected from children and adolescents (ages 5-21). Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection with contrast change blocks, surrounding suppression, sequence learning with five progressive blocks, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population with multi-modal phenotypic assessment.

## File Scan Result

> **Kernel SHA256**: `86027ad9df54899b153e9a0d59e314d45072742e0b8be065535142202cb3d3b6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 2155 | admin | raw | End-of-recording marker |
| `boundary` | 1554 | admin | raw | Segment boundary marker |
| `break cnt` | 2807 | admin | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 226 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 253 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 217 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 16449 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 1204 | event | raw | Visual dot stimulus 1 offset |
| `dot_no1_ON` | 1204 | event | raw | Visual dot stimulus 1 onset |
| `dot_no2_OFF` | 2416 | event | raw | Visual dot stimulus 2 offset |
| `dot_no2_ON` | 2487 | event | raw | Visual dot stimulus 2 onset |
| `dot_no3_OFF` | 1204 | event | raw | Visual dot stimulus 3 offset |
| `dot_no3_ON` | 1226 | event | raw | Visual dot stimulus 3 onset |
| `dot_no4_OFF` | 1204 | event | raw | Visual dot stimulus 4 offset |
| `dot_no4_ON` | 1225 | event | raw | Visual dot stimulus 4 onset |
| `dot_no5_OFF` | 1204 | event | raw | Visual dot stimulus 5 offset |
| `dot_no5_ON` | 1204 | event | raw | Visual dot stimulus 5 onset |
| `dot_no6_OFF` | 1204 | event | raw | Visual dot stimulus 6 offset |
| `dot_no6_ON` | 1204 | event | raw | Visual dot stimulus 6 onset |
| `dot_no7_OFF` | 1536 | event | raw | Visual dot stimulus 7 offset |
| `dot_no7_ON` | 1532 | event | raw | Visual dot stimulus 7 onset |
| `dot_no8_OFF` | 766 | event | raw | Visual dot stimulus 8 offset |
| `dot_no8_ON` | 766 | event | raw | Visual dot stimulus 8 onset |
| `fixpoint_ON` | 30018 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 1325 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 1591 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 244 | event | raw | Sequence learning block 1 |
| `learningBlock_2` | 241 | event | raw | Sequence learning block 2 |
| `learningBlock_3` | 240 | event | raw | Sequence learning block 3 |
| `learningBlock_4` | 240 | event | raw | Sequence learning block 4 |
| `learningBlock_5` | 239 | event | raw | Sequence learning block 5 |
| `left_buttonPress` | 10593 | event | raw | Participant button press - left hand |
| `left_target` | 7857 | event | raw | Left-side target stimulus |
| `newPage` | 409 | event | raw | Page change/cue event (symbol search) |
| `resting_start` | 273 | event | raw | Resting-state block onset |
| `right_buttonPress` | 10002 | event | raw | Participant button press - right hand |
| `right_target` | 7910 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 244 | event | raw | Sequence learning block onset |
| `seqLearning_stop` | 239 | event | raw | Sequence learning block offset |
| `stim_ON` | 30059 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 234 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 235 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 161 | event | raw | Symbol search trial onset |
| `trialResponse` | 2569 | event | raw | Trial response event |
| `video_start` | 1157 | event | raw | Video/movie start |
| `video_stop` | 1085 | event | raw | Video/movie stop |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Resting-state EEG classification of psychiatric diagnoses
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `ADHD` | 0/1 | Attention-Deficit/Hyperactivity Disorder diagnosis |
  | `ANX (anxiety)` | 0/1 | Anxiety disorder diagnosis |
  | `SLD` | 0/1 | Specific Learning Disorder diagnosis |
  | `ASD` | 0/1 | Autism Spectrum Disorder diagnosis |
  | `DISR` | 0/1 | Disruptive disorders diagnosis |
  | `COM` | 0/1 | Communication disorders diagnosis |
  | `DEP` | 0/1 | Depressive disorders diagnosis |
  | `Other` | 0/1 | Other DSM-V diagnosis |
- **Super Meta Notes**: Derived from clinical DSM-V diagnoses made by licensed clinicians. Kernel step: Join EEG epoch files with phenotypic diagnosis tables by subject ID; compute binary labels per DSM-V category; use subject-wise splits to prevent data leakage.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Multi-label classification of 8 DSM-V psychiatric diagnoses from resting-state EEG in HBN pediatric sample
- **Kernel Notes**: Requires phenotypic data join; use leave-one-subject-out or subject-wise cross-validation; binary cross-entropy loss per diagnosis; resting blocks identified via `resting_start` (269 events) or `instructed_toOpenEyes`/`instructed_toCloseEyes` (2916 events).

### Classical Task 2: Resting-state EEG regression of dimensional symptom severity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|--------|
  | `SCARED GAD` | float | Screen for Child Anxiety Related Disorders – Generalized Anxiety subscale |
  | `SWAN IN` | float | Sustained Attention (Inattention) subscale score |
  | `SWAN HY` | float | Sustained Attention (Hyperactivity) subscale score |
  | `SRS-2 SCI` | float | Social Responsiveness Scale-2 Social Communication Index |
  | `SRS-2 RRB` | float | Social Responsiveness Scale-2 Restricted Interests/Repetitive Behavior subscale |
  | `WISC VCI` | float | Wechsler Intelligence Scale for Children Verbal Comprehension Index |
  | `WMI` | float | Working Memory Index |
- **Super Meta Notes**: Derived from standardized behavioral/questionnaire measures administered to HBN participants. Kernel step: Join EEG epoch files with behavioral questionnaire score tables by subject ID; segment continuous resting blocks into 2 s epochs; use subject-wise cross-validation to prevent data leakage.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Benchmark for prediction of psychiatric multimorbidity (regression of symptom severity scores)
  - DOI: 10.1016/j.neuroimage.2020.117001 — Functional connectivity of EEG associated with phenotypic measures including IQ, ADHD, age, anxiety, Child Behavior Checklist
- **Kernel Notes**: Requires phenotypic data join; use subject-wise cross-validation splits; MSE loss per target; resting blocks identified via `resting_start` or instruction events; recommend per-epoch feature extraction then aggregating predictions per subject.

### Potential Task 1: Contrast detection sensory ERP analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 0.8 s, baseline = (-0.2, 0.0) s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `left_target` | 0/1 | Left-side target stimulus (correct = left button) |
  | `right_target` | 0/1 | Right-side target stimulus (correct = right button) |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor (contrast detection paradigm listed among six tasks)
- **Kernel Notes**: Stimulus-locked epochs from `left_target` (7857 events) and `right_target` (7910 events); button presses (`left_buttonPress`, `right_buttonPress`) can be used to compute response accuracy as alternative label; tmin/tmax capture N100/P300 ERP components; ensure balanced trial counts across left/right conditions.

### Potential Task 2: Sequence learning block analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = trial-level window
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `seqLearning_start` | 0 | Sequence learning block onset |
  | `learningBlock_1` | 0 | Learning block 1 |
  | `learningBlock_5` | 1 | Learning block 5 (later stage) |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor (sequence learning paradigm included)
- **Kernel Notes**: Long-duration epochs spanning learning blocks (5 blocks of ~244 trials each); `seqLearning_start` (244 events) marks block onset, `learningBlock_1`–`learningBlock_5` (each ~240 events) subdivide learning progression; epochs capture implicit learning effects; alternative: segment block windows by `seqLearning_start` to `seqLearning_stop` (239 events).

### Potential Task 3: Symbol search cognitive task analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0 s, baseline = (-0.2, 0.0) s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `symbolSearch_start` | 1 | Symbol search trial onset |
  | `newPage` | 0 | Page change/cue event |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor (symbol search task listed among paradigms)
- **Kernel Notes**: Symbol search involves visual search and decision-making; `symbolSearch_start` (161 events) marks trial onset; `newPage` (409 events) used as cue; trialResponse (2569 events) provides response information; tmin/tmax capture P300 and late positive complex associated with search and decision processes.

### Potential Task 4: Surrounding suppression psychophysical analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0 s, baseline = (-0.2, 0.0) s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `surroundSuppB1_start` | 1 | Surrounding suppression block 1 onset |
  | `surroundSuppB2_start` | 2 | Surrounding suppression block 2 onset |
  | `surroundSuppB3_start` | 3 | Surrounding suppression block 3 onset |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor (surrounding suppression paradigm included)
- **Kernel Notes**: Three psychophysical blocks examining visual surround suppression; block onset events available (`surroundSuppB1_start`: 234, `surroundSuppB2_start`: 235, `surroundSuppB3_start`: 234); epochs capture VEP changes associated with suppression; alternative: epoch by block duration using block start/stop markers if stop events available; blocks may differ in suppression strength.

### Potential Task 5: Resting-state EEG prediction of psychopathology dimensions
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|--------|
  | `internalizing` | float | Internalizing factor score (bifactor model) |
  | `externalizing` | float | Externalizing factor score (bifactor model) |
  | `attention` | float | Attention factor score (bifactor model) |
  | `p_factor` | float | General psychopathology factor (p-factor) |
- **Super Meta Notes**: Four psychopathology dimensions from bifactor model are publicly available as participant metadata. Kernel step: Join segmented EEG epochs with phenotypic files by subject ID; subject-wise cross-validation prevents data leakage.
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG FAIR implementation (bifactor psychopathology dimensions publicly available in participant metadata)
- **Kernel Notes**: Resting blocks identified via `resting_start` (269 events) or instruction events; same segmentation approach as classical tasks; p-factor represents transdiagnostic liability; dimensional scores available per subject for regression; optional: multi-output regression for all four factors jointly.