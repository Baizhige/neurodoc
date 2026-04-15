# Healthy Brain Network (HBN) EEG - Release 5

**Dataset**: `openneuro_ds005509` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005509
**Category**: Complex Applied | **Subjects**: 330 | **Files (Completed)**: 3326 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 5 is a large-scale, multi-task developmental battery collected from children and adolescents aged 5-21 years. Participants completed six paradigms including naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population using high-density EEG recordings.

## File Scan Result

> **Kernel SHA256**: `3a133c2829d8eba8a5d953595357084e6ccc9874cf4a3693fbe63d3df28d20c2`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 2339 | event | raw | End-of-recording marker |
| `boundary` | 1839 | event | raw | Segment boundary marker |
| `break cnt` | 3296 | event | raw | Break/counter marker between blocks |
| `contrastChangeB1_start` | 233 | event | raw | Contrast change block 1 onset |
| `contrastChangeB2_start` | 282 | event | raw | Contrast change block 2 onset |
| `contrastChangeB3_start` | 260 | event | raw | Contrast change block 3 onset |
| `contrastTrial_start` | 18682 | event | raw | Contrast detection trial block onset |
| `dot_no1_OFF` | 1553 | event | raw | Surrounding suppression dot 1 offset |
| `dot_no1_ON` | 1553 | event | raw | Surrounding suppression dot 1 onset |
| `dot_no2_OFF` | 3111 | event | raw | Surrounding suppression dot 2 offset |
| `dot_no2_ON` | 3119 | event | raw | Surrounding suppression dot 2 onset |
| `dot_no3_OFF` | 1553 | event | raw | Surrounding suppression dot 3 offset |
| `dot_no3_ON` | 1565 | event | raw | Surrounding suppression dot 3 onset |
| `dot_no4_OFF` | 1553 | event | raw | Surrounding suppression dot 4 offset |
| `dot_no4_ON` | 1558 | event | raw | Surrounding suppression dot 4 onset |
| `dot_no5_OFF` | 1553 | event | raw | Surrounding suppression dot 5 offset |
| `dot_no5_ON` | 1553 | event | raw | Surrounding suppression dot 5 onset |
| `dot_no6_OFF` | 1553 | event | raw | Surrounding suppression dot 6 offset |
| `dot_no6_ON` | 1553 | event | raw | Surrounding suppression dot 6 onset |
| `dot_no7_OFF` | 2104 | event | raw | Surrounding suppression dot 7 offset |
| `dot_no7_ON` | 2100 | event | raw | Surrounding suppression dot 7 onset |
| `dot_no8_OFF` | 1050 | event | raw | Surrounding suppression dot 8 offset |
| `dot_no8_ON` | 1050 | event | raw | Surrounding suppression dot 8 onset |
| `fixpoint_ON` | 35136 | event | raw | Fixation point onset (trial start cue) |
| `instructed_toCloseEyes` | 1639 | event | raw | Instruction to close eyes (resting block) |
| `instructed_toOpenEyes` | 1969 | event | raw | Instruction to open eyes (resting block) |
| `learningBlock_1` | 319 | event | raw | Sequence learning block 1 onset |
| `learningBlock_2` | 310 | event | raw | Sequence learning block 2 onset |
| `learningBlock_3` | 310 | event | raw | Sequence learning block 3 onset |
| `learningBlock_4` | 307 | event | raw | Sequence learning block 4 onset |
| `learningBlock_5` | 307 | event | raw | Sequence learning block 5 onset |
| `left_buttonPress` | 10192 | event | raw | Participant button press - left hand |
| `left_target` | 8947 | event | raw | Left-side target stimulus |
| `newPage` | 522 | event | raw | Page navigation event |
| `resting_start` | 336 | event | raw | Resting-state block onset |
| `right_buttonPress` | 9498 | event | raw | Participant button press - right hand |
| `right_target` | 8977 | event | raw | Right-side target stimulus |
| `seqLearning_start` | 319 | event | raw | Sequence learning paradigm onset |
| `seqLearning_stop` | 307 | event | raw | Sequence learning paradigm offset |
| `stim_ON` | 35156 | event | raw | Contrast detection stimulus onset |
| `surroundSuppB1_start` | 286 | event | raw | Surrounding suppression block 1 onset |
| `surroundSuppB2_start` | 263 | event | raw | Surrounding suppression block 2 onset |
| `symbolSearch_start` | 202 | event | raw | Symbol search task onset |
| `trialResponse` | 3367 | event | raw | Trial response event |
| `video_start` | 1205 | event | raw | Movie/video presentation onset |
| `video_stop` | 1190 | event | raw | Movie/video presentation offset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Sequence Learning State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stim_ON`, `seqLearning_start`, `learningBlock_1`, `learningBlock_2`, `learningBlock_3`, `learningBlock_4`, `learningBlock_5`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `stim_ON` | 0 | still-unknown (first presentation, not yet learned) |
  | `stim_ON` | 1 | newly-learned (recently acquired memory) |
  | `stim_ON` | 2 | known (well-established memory) |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Paradigm descriptor defining the six-task HBN battery including sequence learning with three learning states (still-unknown, newly-learned, known) derived from recall performance.
  - DOI: 10.1101_2024.10.03.615261 — FAIR implementation paper explicitly listing ds005509 and confirming sequence learning paradigm inclusion.
- **Kernel Notes**: Labels require merging `stim_ON` events with behavioral recall data per subject. Kernel must: (1) locate recall performance data, (2) join with stimulus event timestamps using subject ID, (3) assign y=0/1/2 based on learning state progression. Use learning block events to filter relevant epochs from sequence learning paradigm only.

### Normal Task 2: Contrast Detection ERP Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stim_ON`, `contrastTrial_start`, `contrastChangeB1_start`, `contrastChangeB2_start`, `contrastChangeB3_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `left_target` | 0 | left-hand response required |
  | `left_target` | 1 | correct left-hand response |
  | `right_target` | 0 | right-hand response required |
  | `right_target` | 1 | correct right-hand response |
  | `left_buttonPress` | 0 | incorrect left press (when right target) |
  | `right_buttonPress` | 0 | incorrect right press (when left target) |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Paradigm descriptor defining contrast detection task with visual contrast stimuli and button press responses.
  - DOI: 10.1101_2024.10.03.615261 — FAIR implementation confirming contrast detection paradigm in ds005509.
- **Kernel Notes**: ERP analysis requires alignment to `stim_ON` (not `fixpoint_ON`). Compute correct/incorrect labels by matching button press timestamps to target side. N200/P300 components expected for high-contrast targets. Filter epochs using `contrastTrial_start` to isolate task blocks from inter-trial intervals.

### Potential Task 1: Resting-State Psychiatric Multimorbidity Prediction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, overlap = 0.5, target_events = [`resting_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | continuous | ADHD | SWAN score (attention dimension) |
  | continuous | anxiety | SCARED score |
  | continuous | internalizing | Internalizing factor from CBCL |
  | continuous | externalizing | Externalizing factor from CBCL |
  | continuous | p_factor | P-factor (general psychopathology) |
  | continuous | 7_DSM_classes | Multi-label DSM-V diagnoses (ADHD, ODD, CD, MDD, GAD, SOP, specific phobias) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119348 — EEG benchmark paper demonstrating 7-class DSM-V multimorbidity prediction from resting EEG in N=2042 HBN participants using frequency-domain features.
- **Kernel Notes**: Requires join between EEG connectivity features and phenotypic CSV tables by subject ID. Use subject-wise cross-validation splits to prevent data leakage. Extract spectral power (delta/theta/alpha/beta) and connectivity (coherence) features from 4-s resting epochs. Labels are multi-label (subjects may have multiple diagnoses) requiring appropriate binary classification approach.

### Potential Task 2: Phenotypic Regression from Resting Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`resting_start`, `instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | continuous | age | Participant age in years |
  | binary | sex | Participant sex (M/F) |
  | continuous | IQ | WISC score |
  | continuous | SES | Barratt SES score |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — EEG functional connectivity study demonstrating subject-specific phase-coupling associations with age, sex, IQ, and SES using HBN Biobank data (N=1657).
- **Kernel Notes**: Extract instantaneous coherence (iCOH) across frequency bands from resting-state epochs. Kernel must load phenotypic CSV files per subject and perform multivariate regression. Use age-appropriate train/test splits accounting for developmental non-stationarity. Consider frequency-band-specific models (delta/theta for younger, alpha/beta for older participants).
