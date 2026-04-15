# Healthy Brain Network (HBN) EEG - Release 11

**Dataset**: `openneuro_ds005516` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005516
**Category**: Complex Applied | **Subjects**: 3000 | **Files (Completed)**: 3396 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 11 is a large-scale, multi-task developmental battery collected from children and adolescents aged 5-22 years. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, serial dot, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recording.

## File Scan Result

> **Kernel SHA256**: `c85548ebc527e585364c42eb6356397ebe0c9bbb52fd1c24f4f9166dba15ce36`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 3038 | admin | raw | End-of-recording marker |
| `IBEG` | 19 | event | raw | Interval/image begin marker |
| `IEND` | 22 | event | raw | Interval/image end marker |
| `SPIK` | 2 | event | raw | Spike detection marker |
| `boundary` | 1462 | admin | raw | Segment boundary marker |
| `break cnt` | 3196 | admin | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 398 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 283 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 234 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 19366 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 19 | event | raw | Serial dot stimulus 1 offset |
| `dot_no1_ON` | 19 | event | raw | Serial dot stimulus 1 onset |
| `dot_no2_OFF` | 48 | event | raw | Serial dot stimulus 2 offset |
| `dot_no2_ON` | 107 | event | raw | Serial dot stimulus 2 onset |
| `dot_no3_OFF` | 19 | event | raw | Serial dot stimulus 3 offset |
| `dot_no3_ON` | 72 | event | raw | Serial dot stimulus 3 onset |
| `dot_no4_OFF` | 19 | event | raw | Serial dot stimulus 4 offset |
| `dot_no4_ON` | 22 | event | raw | Serial dot stimulus 4 onset |
| `dot_no5_OFF` | 19 | event | raw | Serial dot stimulus 5 offset |
| `dot_no5_ON` | 19 | event | raw | Serial dot stimulus 5 onset |
| `dot_no6_OFF` | 19 | event | raw | Serial dot stimulus 6 offset |
| `dot_no6_ON` | 19 | event | raw | Serial dot stimulus 6 onset |
| `dot_no7_OFF` | 10 | event | raw | Serial dot stimulus 7 offset |
| `dot_no7_ON` | 6 | event | raw | Serial dot stimulus 7 onset |
| `dot_no8_OFF` | 3 | event | raw | Serial dot stimulus 8 offset |
| `dot_no8_ON` | 3 | event | raw | Serial dot stimulus 8 onset |
| `fixpoint_ON` | 37760 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 1370 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 1644 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 8 | event | raw | Sequence learning block 1 onset |
| `learningBlock_2` | 3 | event | raw | Sequence learning block 2 onset |
| `learningBlock_3` | 3 | event | raw | Sequence learning block 3 onset |
| `learningBlock_4` | 3 | event | raw | Sequence learning block 4 onset |
| `learningBlock_5` | 2 | event | raw | Sequence learning block 5 onset |
| `left_buttonPress` | 14777 | event | raw | Participant button press - left hand |
| `left_target` | 9226 | event | raw | Left-side target stimulus |
| `net` | 4 | event | raw | EEG net/sensor reference marker |
| `newPage` | 601 | event | raw | Symbol search page/trial change |
| `resting_start` | 372 | event | raw | Resting-state block onset |
| `right_buttonPress` | 13758 | event | raw | Participant button press - right hand |
| `right_target` | 9311 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 8 | event | raw | Sequence learning task onset |
| `seqLearning_stop` | 1 | event | raw | Sequence learning task offset |
| `stim_ON` | 37825 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 327 | event | raw | Surround suppression block 1 onset |
| `surroundSuppB2_start` | 262 | event | raw | Surround suppression block 2 onset |
| `symbolSearch_start` | 222 | event | raw | Symbol search task onset |
| `trialResponse` | 4056 | event | raw | Trial response event |
| `video_start` | 1666 | event | raw | Movie clip onset |
| `video_stop` | 1541 | event | raw | Movie clip offset |


### MISC Label Summary
- **Route**: `misc`
- **Role**: No MISC channels detected in current scan (derived phenotypic labels stored externally)
- **Candidate Labels**: N/A
- **Kernel Note**: Phenotypic variables (age, sex, diagnoses) must be sourced from external companion CSV files aligned by subject ID
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: FC-phenotype association regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0 (segments concatenated across entire recording for FC computation)
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `age` | continuous | Participant age in years |
  | `sex` | 0/1 | Biological sex (binary) |
  | `IQ` | continuous | WISC-measured intelligence quotient |
  | `CBCL` | continuous | Child Behavior Checklist score |
  | `SWAN_ADHD` | continuous | SWAN ADHD measure |
  | `SES` | continuous | Barratt Socioeconomic Status |
  | `anxiety` | continuous | SCARED anxiety score |
- **Super Meta Notes**: Derived from phenotypic assessment tables (WISC, CBCL, SWAN, Barratt, SCARED) external to EEG. Kernel must: (1) identify subject ID from EEG filename, (2) join with phenotypic CSV by subject, (3) compute FC (iCOH) from 2s segments across concatenated tasks, (4) apply MDMR or similar multivariate regression to predict phenotypic vectors from FC matrices.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Uses HBN EEG source-space connectivity (iCOH) to predict age, sex, IQ, CBCL, ADHD, SES, anxiety via MDMR association analysis
- **Kernel Notes**: Requires full-recording concatenation across multiple task blocks (resting 300s, video 117-230s, visual flicker 210s). Segment-level FC computed per 2s window, then aggregated into subject-level connectivity matrix. Phenotypic labels must be aligned by subject ID. Use subject-wise splits to prevent data leakage.

### Classical Task 2: Psychiatric multimorbidity classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 300.0, overlap = null
- **Label Route**: `info`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `ADHD` | 0/1 | Attention-Deficit/Hyperactivity Disorder diagnosis |
  | `ODD` | 0/1 | Oppositional Defiant Disorder diagnosis |
  | `CD` | 0/1 | Conduct Disorder diagnosis |
  | `Anxiety_Disorder` | 0/1 | Anxiety Disorder diagnosis |
  | `MDD` | 0/1 | Major Depressive Disorder diagnosis |
  | `ASD` | 0/1 | Autism Spectrum Disorder diagnosis |
  | `Learning_Disorder` | 0/1 | Learning Disorder diagnosis |
- **Super Meta Notes**: Multi-label classification for 7 DSM-V diagnoses. Labels derived from clinical assessment; kernel must load per-subject diagnostic labels from companion phenotypic file. Hidden test sets defined in original benchmark paper.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2022.119348` — Benchmark paper defining psychiatric multimorbidity prediction from resting EEG data in N=2042 HBN participants; establishes 7-class classification and symptom severity regression tasks with hidden test sets
- **Kernel Notes**: Resting state epochs from `resting_start` events (372 total) capture spontaneous activity for disorder classification. Frequency band features (delta, theta, alpha, beta, gamma) commonly used. Multi-label format allows comorbid diagnoses. Subject-wise splits essential.

### Classical Task 3: Contrast detection ERP analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, overlap = null
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `left_target` | 1 | Left-side target stimulus |
  | `right_target` | 2 | Right-side target stimulus |
  | `stim_ON` | 0 | Non-target stimulus (catch) |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — Original HBN EEG paradigm design describing contrast detection task with left/right target discrimination
  - DOI: `10.1038/sdata.2017.181` — Foundational HBN Biobank paper providing context for paradigm design
- **Kernel Notes**: `stim_ON` (37,825 events) serves as primary stimulus onset; approximately 1:1 with `fixpoint_ON` indicating trial structure. Button presses (`left_buttonPress`: 14,777, `right_buttonPress`: 13,758) provide response-locked analysis opportunity. Task involves sensory contrast detection requiring fine-grained temporal resolution. 500 Hz sampling adequate for ERP characterization.

### Classical Task 4: Resting state functional connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 300.0, overlap = null
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `resting_start` | 1 | Resting-state block onset (combined eye-open/closed) |
  | `instructed_toOpenEyes` | 2 | Eye-open resting condition |
  | `instructed_toCloseEyes` | 3 | Eye-closed resting condition |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Resting state EEG used for iCOH functional connectivity computation across frequency bands
  - DOI: `10.1016/j.neuroimage.2022.119348` — Resting state segments used as primary input for psychiatric classification benchmark
- **Kernel Notes**: 372 `resting_start` events define resting blocks; separate `instructed_toOpenEyes` (1,644) and `instructed_toCloseEyes` (1,370) allow condition-specific analysis. Long epochs capture sustained oscillatory activity for functional connectivity. Eye condition may modulate alpha power and connectivity patterns.

### Classical Task 5: Surround suppression ERP analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 0.8, overlap = null
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `contrastChangeB1_start` | 1 | Surround suppression block 1 onset |
  | `contrastChangeB2_start` | 2 | Surround suppression block 2 onset |
  | `contrastChangeB3_start` | 3 | Surround suppression block 3 onset |
  | `surroundSuppB1_start` | 4 | Surround suppression task block 1 |
  | `surroundSuppB2_start` | 5 | Surround suppression task block 2 |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — HBN paradigm design includes surround suppression task as one of six key paradigms
  - DOI: `10.1038/sdata.2017.181` — HBN Biobank context for paradigm implementation
- **Kernel Notes**: Contrast change events (B1: 398, B2: 283, B3: 234) capture surround suppression responses; block onset events provide trial structure. Standard ERP window (tmax=0.8s) captures early visual processing. Paradigm measures contrast discrimination with contextual modulation.

### Classical Task 6: Sequence learning ERD/ERP analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5, tmax = 2.0, overlap = null
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `seqLearning_start` | 1 | Sequence learning task onset |
  | `learningBlock_1` | 2 | Learning block 1 |
  | `learningBlock_2` | 3 | Learning block 2 |
  | `learningBlock_3` | 4 | Learning block 3 |
  | `learningBlock_4` | 5 | Learning block 4 |
  | `learningBlock_5` | 6 | Learning block 5 |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — HBN paradigm includes sequence learning as active task (one of 3 active paradigms)
- **Kernel Notes**: Sequence learning is an active paradigm requiring motor response. Extended epoch window (tmax=2.0s) captures learning-related ERD in motor cortex and later cognitive ERP components. Block progression (learningBlock_1 through learningBlock_5) enables analysis of skill acquisition across training.

### Classical Task 7: Symbol search ERP analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2, tmax = 1.0, overlap = null
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `symbolSearch_start` | 1 | Symbol search task onset |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — HBN paradigm includes symbol search as active cognitive task (one of 3 active paradigms)
- **Kernel Notes**: Symbol search is a cognitive assessment task measuring visual search and processing speed. `symbolSearch_start` (222 events) defines task blocks; `newPage` (601 events) indicates trial boundaries within blocks. Standard ERP window captures stimulus-locked processing and cognitive workload components.

### Classical Task 8: Movie watching functional connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 230.0, overlap = null
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `video_start` | 1 | Movie clip onset |
  | `video_stop` | 0 | Movie clip offset (segment boundary) |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Video watching segments concatenated with resting state for full-recording FC computation
  - DOI: `10.1101/089060` — Age and sex modulate variability of neural responses to naturalistic videos in developmental sample
- **Kernel Notes**: Movie viewing blocks (video_start: 1,666, video_stop: 1,541) provide sustained naturalistic stimulation for FC analysis. Clip durations 117-230s. Concatenated with resting and other tasks for subject-level connectivity matrices. Naturalistic paradigm may elicit inter-subject correlation patterns.