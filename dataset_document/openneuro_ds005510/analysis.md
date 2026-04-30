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

### Classical Task 1: Phenotypic Factor Regression from Resting EEG Functional Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`resting_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `resting_start` | continuous | Resting-state EEG epochs for FC computation |
  | `instructed_toOpenEyes` | continuous | Eyes-open resting state |
  | `instructed_toCloseEyes` | continuous | Eyes-closed resting state |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Uses HBN Biobank EEG data (n=1657) to analyze imaginary coherence functional connectivity across resting, video, and flicker tasks, correlating FC features with phenotypic measures (age, sex, IQ, ADHD, anxiety, SES).
- **Kernel Notes**: Combine resting-state epochs from `resting_start`, `instructed_toOpenEyes`, and `instructed_toCloseEyes` events. Compute connectivity features (iCOH) per 4s epoch with 50% overlap in delta (0.5–4 Hz), theta (4–7.5 Hz), alpha (7.5–15 Hz), and beta (15–30 Hz) bands. Join EEG-derived features with phenotypic CSV tables using subject IDs. Subject-wise cross-validation splits are mandatory to prevent label leakage. The `externalizing_factor` and `p_factor` from misc channel can serve as primary regression targets; verify derivation source (CBCL/SWAN/SCARED factor analysis version).

### Classical Task 2: Multi-Label Psychiatric Diagnosis Classification from Resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`resting_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `resting_start` | multi-label binary (7 classes) | Resting-state EEG epochs for diagnosis classification |
  | `instructed_toOpenEyes` | multi-label binary (7 classes) | Eyes-open resting state |
  | `instructed_toCloseEyes` | multi-label binary (7 classes) | Eyes-closed resting state |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2022.119348` — Benchmark study (n=2042) defining two challenges using HBN resting EEG: (1) multi-label classification of 7 DSM-V diagnoses, (2) regression on symptom severity dimensions. Reports ROC-AUC, PR-AUC, and balanced accuracy as evaluation metrics.
- **Kernel Notes**: Use identical epoching as Classical Task 1 (resting-state FC task). The 7 DSM-V diagnosis labels must be loaded from external phenotypic CSV and joined by subject ID. Recommended target columns: ADHD, anxiety disorder, ASD, conduct disorder, depression, eating disorder, OCD (verify exact column names from benchmark challenge). Apply subject-wise cross-validation with stratification by diagnosis label combinations. Report per-class and macro-averaged metrics.

### Normal Task 3: Contrast Detection ERP Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = [`stim_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `stim_ON` | continuous | Contrast detection stimulus onset (trial anchor) |
- **Evidence**:
  - DOI: `10.1101/2024.10.03.615261` — Dataset descriptor paper explicitly listing contrast detection as one of six HBN-EEG paradigms; defines `stim_ON` event as contrast stimulus onset with HED annotations.
  - DOI: `10.1038/sdata.2017.40` — Parent resource describing similar contrast detection task paradigm for assessing information processing in developing brain.
- **Kernel Notes**: Extract epochs aligned to `stim_ON` (n=13706) with baseline window [-0.2, 0]s. Apply standard artifact rejection (amplitude threshold ±100 μV). Compute grand average ERP to characterize P1/N1/P3 components. May be combined with `left_target`/`right_target` for lateralized analysis or with `trialResponse` for RT-linked ERP decomposition. The `contrastTrial_start` (n=5817) marks trial block onset and can be used for block-level normalization.

### Normal Task 4: Video Viewing Naturalistic Paradigm Epoch Extraction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 0.0, target_events = [`video_start`, `video_stop`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `video_start` | continuous | Movie viewing onset (Despicable Me, The Present, Diary of a Wimpy Kid, Fun with Fractals) |
  | `video_stop` | continuous | Movie viewing offset |
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2020.117001` — Mentions video watching (Despicable Me) as one of the EEG recording paradigms in HBN data, alongside resting state and visual flicker.
  - DOI: `10.1101/2024.10.03.615261` — Dataset paper includes video viewing as a naturalistic passive task with HED schema annotations.
- **Kernel Notes**: Segment continuous EEG between `video_start` (n=441) and `video_stop` (n=435) into 2s non-overlapping windows. Count mismatch (~6 unclosed segments) indicates data quality issue requiring boundary-aware cropping. Verify movie type from task-sidecar JSON for stimulus-specific analysis. Supports naturalistic movie decoding or emotional content regression if stimulus annotations become available.

### Normal Task 5: Sequence Learning Oscillatory Dynamics
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`seqLearning_start`, `learningBlock_1`, `learningBlock_2`, `learningBlock_3`, `learningBlock_4`, `learningBlock_5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `seqLearning_start` | continuous | Sequence learning block onset |
  | `learningBlock_1` | continuous | Sub-block 1 within sequence learning |
  | `learningBlock_2` | continuous | Sub-block 2 within sequence learning |
  | `learningBlock_3` | continuous | Sub-block 3 within sequence learning |
  | `learningBlock_4` | continuous | Sub-block 4 within sequence learning |
  | `learningBlock_5` | continuous | Sub-block 5 within sequence learning |
- **Evidence**:
  - DOI: `10.1101/2024.10.03.615261` — Dataset paper lists sequence learning as one of the six HBN-EEG active tasks with event markers.
  - DOI: `10.1016/j.neuroimage.2020.117001` — General reference to HBN paradigm; sequence learning implicates theta/alpha power changes.
- **Kernel Notes**: Use `seqLearning_start` for block-level epoching; `learningBlock_1`–`learningBlock_5` provide finer-grained within-block segmentation for learning curve analysis. Compute time-frequency representations (TFR) in theta (4–8 Hz) and alpha (8–12 Hz) bands to capture sequence learning oscillatory markers. Can regress against behavioral performance measures if available from behavioral logs.

### Normal Task 6: Lateralized Target Detection (N2pc/P3 Analysis)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, overlap = null, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `left_target` | binary (0) | Left visual field target stimulus |
  | `right_target` | binary (1) | Right visual field target stimulus |
- **Evidence**:
  - DOI: `10.1101/2024.10.03.615261` — Dataset paper documents lateralized target events (`left_target`, `right_target`) as part of the visual paradigm.
- **Kernel Notes**: Extract epochs from lateralized target onset events with balanced counts (left: 2793, right: 2796). Compute lateralized ERP components (N2pc at posterior contralateral electrodes ~200ms, P3 at 300–500ms) to assess spatial attention. Pair with `left_buttonPress`/`right_buttonPress` for response-locked analysis. May be extended to brain-computer interface (BCI) binary classification using posterior parietal channels. `trialResponse` events can serve as quality check for stimulus-response mapping.

### Potential Task 7: Symbol Search Cognitive Load Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 4 s, overlap = 0.5, target_events = [`symbolSearch_start`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `symbolSearch_start` | continuous | Symbol search task onset (visual search/working memory) |
- **Evidence**:
  - DOI: `10.1101/2024.10.03.615261` — Dataset paper lists symbol search as one of six HBN-EEG tasks involving sustained visual attention and working memory.
- **Kernel Notes**: Extract long epochs from `symbolSearch_start` (n=86) with 4s windows and 50% overlap. Symbol search is a cognitive task involving visual search and working memory, implicating frontal theta and parietal alpha dynamics. Join with `response_time` from misc channel for RT-linked analysis. `newPage` events (n=224) may provide trial-level segmentation within the symbol search block if finer resolution is needed. Low event count limits statistical power — consider pooling across subjects for group-level analysis.

### Potential Task 8: Surround Suppression ERP Paradigm
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
