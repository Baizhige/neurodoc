# Healthy Brain Network (HBN) EEG - Release 3

**Dataset**: `openneuro_ds005507` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005507
**Category**: Complex Applied | **Subjects**: 183 | **Files (Completed)**: 1812 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 3 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `88f6fb972833ad2d7ce0abc71410b452a4645352fe4047a1b393791c09ee933b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 1446 | event | raw | End-of-recording marker |
| `boundary` | 1074 | event | raw | Segment boundary marker |
| `break cnt` | 1973 | event | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 140 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 151 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 208 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 12072 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 823 | event | raw | Dot stimulus 1 offset |
| `dot_no1_ON` | 823 | event | raw | Dot stimulus 1 onset |
| `dot_no2_OFF` | 1653 | event | raw | Dot stimulus 2 offset |
| `dot_no2_ON` | 1694 | event | raw | Dot stimulus 2 onset |
| `dot_no3_OFF` | 823 | event | raw | Dot stimulus 3 offset |
| `dot_no3_ON` | 858 | event | raw | Dot stimulus 3 onset |
| `dot_no4_OFF` | 823 | event | raw | Dot stimulus 4 offset |
| `dot_no4_ON` | 832 | event | raw | Dot stimulus 4 onset |
| `dot_no5_OFF` | 823 | event | raw | Dot stimulus 5 offset |
| `dot_no5_ON` | 823 | event | raw | Dot stimulus 5 onset |
| `dot_no6_OFF` | 823 | event | raw | Dot stimulus 6 offset |
| `dot_no6_ON` | 823 | event | raw | Dot stimulus 6 onset |
| `dot_no7_OFF` | 963 | event | raw | Dot stimulus 7 offset |
| `dot_no7_ON` | 962 | event | raw | Dot stimulus 7 onset |
| `dot_no8_OFF` | 481 | event | raw | Dot stimulus 8 offset |
| `dot_no8_ON` | 481 | event | raw | Dot stimulus 8 onset |
| `fixpoint_ON` | 18564 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 915 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 1101 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 171 | event | raw | Sequence learning block 1 onset |
| `learningBlock_2` | 165 | event | raw | Sequence learning block 2 onset |
| `learningBlock_3` | 163 | event | raw | Sequence learning block 3 onset |
| `learningBlock_4` | 162 | event | raw | Sequence learning block 4 onset |
| `learningBlock_5` | 162 | event | raw | Sequence learning block 5 onset |
| `left_buttonPress` | 6995 | event | raw | Participant button press - left hand |
| `left_target` | 5753 | event | raw | Left-side target stimulus |
| `newPage` | 274 | event | raw | New page/display onset |
| `resting_start` | 194 | event | raw | Resting-state block onset |
| `right_buttonPress` | 6266 | event | raw | Participant button press - right hand |
| `right_target` | 5800 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 171 | event | raw | Sequence learning task onset |
| `seqLearning_stop` | 160 | event | raw | Sequence learning task offset |
| `stim_ON` | 18602 | event | raw | Stimulus onset (contrast detection) |
| `surroundSuppB1_start` | 154 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 137 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 107 | event | raw | Symbol search task onset |
| `trialResponse` | 1757 | event | raw | Trial response event |
| `video_start` | 1041 | event | raw | Movie clip onset |
| `video_stop` | 1013 | event | raw | Movie clip offset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Phenotypic prediction from functional connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | continuous | Functional connectivity features from resting-state EEG epochs |
  | `video_start` | continuous | Functional connectivity features from movie-viewing EEG epochs |
- **Super Meta Notes**: Derived from raw events [`resting_start`, `video_start`, `video_stop`] by computing imaginary coherence (iCOH) on 2-s sliding windows, then regressing against phenotypic variables (age, sex, IQ, ADHD, anxiety, SES, CBCL). Kernel step: Extract EEG epochs around events → compute FC matrix → join with phenotypic table → train regression model.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Analyzes N=1657 children/adolescents from HBN; investigates phase-coupling (iCOH) FC networks and their correlation with 10 phenotypic/demographic measures.
- **Kernel Notes**: Use source-localized EEG for iCOH computation. Exclude flicker task (no raw event marker available). Verify subject ID harmonization between EEG and phenotypic tables.

### Classical Task 2: Psychiatric multimorbidity classification from resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | ADHD | Attention-deficit/hyperactivity disorder |
  | `resting_start` | ODD | Oppositional defiant disorder |
  | `resting_start` | ASD | Autism spectrum disorder |
  | `resting_start` | anxiety | Anxiety disorders |
  | `resting_start` | depression | Depressive disorders |
  | `resting_start` | learning | Learning disorders |
  | `resting_start` | enuresis | Enuresis |
- **Super Meta Notes**: Labels derived from subject metadata DSM-V diagnosis fields. Kernel must load per-subject diagnostic labels from companion clinical assessment file and join to resting-state EEG segments. Over 56% of children have multiple psychiatric disorders.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — ML benchmark for psychiatric multimorbidity prediction using resting EEG; predicts 7 DSM-V diagnoses (ADHD, ODD, ASD, anxiety disorders, depressive disorders, learning disorders, enuresis) in large pediatric sample including HBN hidden test sets.
- **Kernel Notes**: Resting-state segments extracted using same 2-s sliding window approach as functional connectivity task. Verify diagnostic criteria used across sites. Multi-label classification may be required given high comorbidity rates.

### Classical Task 3: Sequence learning state classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`contrastTrial_start`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `contrastTrial_start` | 0 | Still-unknown learning state |
  | `contrastTrial_start` | 1 | Newly-learned learning state |
  | `contrastTrial_start` | 2 | Known learning state |
- **Super Meta Notes**: Derived from raw events [`contrastTrial_start`] by mapping to learning states based on post-sequence recall reports (still-unknown, newly-learned, known). Kernel step: Parse trial chains → look up recall performance metadata → assign state label (0/1/2).
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Describes HBN sequence learning paradigm where trials categorized as still-unknown, newly-learned, or known based on recall reports.
- **Kernel Notes**: Verify event ID mapping from events.tsv. Recall performance data must be joined from separate behavioral file. Exclude incomplete trial chains.

### Classical Task 4: Contrast detection ERP (stimulus-locked)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stim_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-side target stimulus |
  | `right_target` | 1 | Right-side target stimulus |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — HBN sensory contrast detection paradigm with left/right target discrimination.
- **Kernel Notes**: stim_ON (18,602 events) is primary perceptual onset event. left_target (5,753) and right_target (5,800) can be used as trial-type labels. Standard ERP parameters capture pre-stimulus baseline and post-stimulus processing.

### Normal Task 1: Contrast detection response-locked motor analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0.5 s, target_events = [`left_buttonPress`, `right_buttonPress`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_buttonPress` | 0 | Left-hand response |
  | `right_buttonPress` | 1 | Right-hand response |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Contrast detection task requires left/right button responses.
- **Kernel Notes**: Combined button press events (~13,261 total) enable response-locked analysis for motor preparation and execution components. Window centered on button press captures motor-related activity.

### Potential Task 1: Surrounding suppression paradigm analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`surroundSuppB1_start`, `surroundSuppB2_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `surroundSuppB1_start` | 1 | Surrounding suppression block 1 |
  | `surroundSuppB2_start` | 2 | Surrounding suppression block 2 |
- **Evidence**: Paradigm exists in dataset (291 total events across two block types). DOI: 10.1016/j.neuroimage.2020.117001 mentions surround suppression as passive task.
- **Kernel Notes**: Verify behavioral outcome measures for suppression effect quantification. Lower event count (154 + 137) may require combining blocks.

### Potential Task 2: Symbol search cognitive task analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`symbolSearch_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `symbolSearch_start` | continuous | Symbol search task epochs (accuracy/RT from misc) |
- **Evidence**: Paradigm exists in dataset (107 events). DOI: 10.1038/sdata.2017.40 describes active tasks including symbol search.
- **Kernel Notes**: Low event count (107) suggests few trials per subject. May require aggregation across subjects for population-level analysis. Verify accuracy/RT availability in behavioral files.