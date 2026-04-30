# Healthy Brain Network (HBN) EEG - Release 10

**Dataset**: `openneuro_ds005515` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005515
**Category**: Complex Applied | **Subjects**: 533 | **Files (Completed)**: 2515 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 10 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `ef980d7b864fceb627a20b5551f437591c612916ba3ca15cdfc74126c4a3143d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Psychiatric Multimorbidity Classification from Resting EEG (Super-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.0, target_events = [`resting_start`]
- **Label Route**: `info`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | N/A | 0–6 (multi-label) | ADHD, ODD, ASD, anxiety disorder, mood disorder, PTSD, psychotic symptoms |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — Benchmark for prediction of psychiatric multimorbidity from resting EEG; N=2042; 7 DSM-V diagnoses; community challenge format with hidden test sets
- **Kernel Notes**: Kernel must join EEG subject IDs with phenotypic CSV containing DSM-V diagnosis fields. Multi-label setup (binary per diagnosis) rather than single-label; exclude subjects missing all diagnosis labels. Admin markers (`boundary`, `9999`) excluded from segmentation.

### Classical Task 2: Phenotypic Regression from EEG Connectivity (Super-meta)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`resting_start`, `video_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | N/A | continuous | Age, IQ, ADHD-SWAN, CBCL, SCARED anxiety, Barratt SES |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Functional connectivity predicts phenotype; N=1657; connectivity (imaginary coherence) across alpha/theta/beta/gamma bands correlates with age, sex, IQ, ADHD, anxiety, SES, CBCL scores
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG FAIR implementation; describes internalizing, externalizing, attention, p-factor dimensions available as super-level labels
- **Kernel Notes**: Kernel must compute connectivity features (phase coupling) before regression. Use resting state segments for primary analysis; video segments as secondary condition. MISC labels (`response_time`) available but phenotypic variables require join with subject metadata CSV.

### Classical Task 3: Contrast Detection Stimulus Classification (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `left_target` | 0 | Left-tilted stimulus onset (contrast change) |
  | `right_target` | 1 | Right-tilted stimulus onset (contrast change) |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Pilot HBN dataset (n=126) establishing six-task paradigm including contrast detection; active task with button press responses
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG release describes contrast detection as active task with stimulus-locked epochs
- **Kernel Notes**: Exclude admin markers (`boundary`, `9999`). Fixation point (`fixpoint_ON`) precedes targets as trial cue. May extend to stimulus-response accuracy by matching button presses to preceding targets.

### Normal Task 1: Resting-State EEG vs. Active Task State Classification (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`resting_start`, `contrastTrial_start`, `seqLearning_start`, `symbolSearch_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `resting_start` | 0 | Resting-state block onset |
  | `contrastTrial_start` | 1 | Contrast detection trial block onset |
  | `seqLearning_start` | 2 | Sequence learning block onset |
  | `symbolSearch_start` | 3 | Symbol search block onset |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — Multi-task battery description; resting, passive, and active task conditions are distinguishable paradigm types
  - DOI: 10.1038/sdata.2017.40 — Three active and three passive tasks described; active tasks require button press responses
- **Kernel Notes**: 4-class classification of brain state from block-onset epochs. Video watching excluded from primary task due to longer sustained processing. Eye-instruction events (`instructed_toOpenEyes`, `instructed_toCloseEyes`) may enable eyes-open vs eyes-closed sub-classification within resting.

### Potential Task 1: Sequence Learning Paradigm Classification (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 0.0, target_events = [`seqLearning_start`, `seqLearning_stop`, `learningBlock_1`, `learningBlock_2`, `learningBlock_3`, `learningBlock_4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `seqLearning_start` | 0 | Sequence learning block onset |
  | `seqLearning_stop` | 1 | Sequence learning block offset |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — Describes sequence learning as active task in HBN battery
  - DOI: 10.1038/sdata.2017.40 — Sequence learning described in six-task paradigm
- **Kernel Notes**: Limited event counts (seqLearning_start: 18, seqLearning_stop: 9) may restrict sample size. Aggregate across learningBlock markers to increase trials if individual block counts insufficient.

### Potential Task 2: Symbol Search Cognitive Task Classification (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`symbolSearch_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `symbolSearch_start` | 0 | Symbol search trial block onset |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — Symbol search listed as active task requiring cognitive processing
  - DOI: 10.1038/sdata.2017.40 — Symbol search in six-task battery
- **Kernel Notes**: Single condition (no binary classification) limits discriminative analysis. Consider regression on response time or trial accuracy if behavioral data available. Limited events (70) may restrict model training.

### Potential Task 3: Surround Suppression Paradigm Analysis (Raw-meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`surroundSuppB1_start`, `surroundSuppB2_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `surroundSuppB1_start` | 0 | Surround suppression block 1 onset |
  | `surroundSuppB2_start` | 1 | Surround suppression block 2 onset |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Surround suppression listed as passive task in six-task paradigm
- **Kernel Notes**: Sub-block markers with limited counts (B1: 98, B2: 67). May need to aggregate or use parent-level event if available. Passive task—no motor response required.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
