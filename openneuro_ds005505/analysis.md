# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection (contrastTrial), surrounding suppression, sequence learning (seqLearning), and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 13278 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 13248 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 8884 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 5095 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 4634 | event | raw | Participant button press - right hand |
| `right_target` | 4251 | event | raw | Right-side target stimulus |
| `left_target` | 4243 | event | raw | Left-side target stimulus |
| `break cnt` | 1488 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 1247 | event | raw | Trial response event |
| `instructed_toOpenEyes` | 816 | event | raw | Instruction to open eyes (resting block) |
| `video_start` | 761 | event | raw | Movie clip onset |
| `boundary` | 728 | admin | raw | Segment boundary marker |
| `video_stop` | 723 | event | raw | Movie clip offset |
| `instructed_toCloseEyes` | 680 | event | raw | Instruction to close eyes (resting block) |
| `resting_start` | 136 | event | raw | Resting-state block onset |
| `seqLearning_start` | 122 | event | raw | Sequence learning block onset |
| `learningBlock_1` | 122 | event | raw | Sequence learning block 1 onset |
| `9999` | 1136 | admin | raw | End-of-recording marker |

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `externalizing_factor`, `p_factor`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Functional Connectivity to Phenotypic Variables Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | continuous | Resting-state FC epochs targeting phenotypic variables |
  | `video_start` | continuous | Video viewing FC epochs targeting phenotypic variables |
- **Super Meta Notes**: Derived from raw events [`resting_start`, `video_start`, `video_stop`, `contrastTrial_start`] by computing imaginary coherence (iCOH) on 2-s EEG segments, then correlating connectivity patterns with phenotypic measures (age, sex, IQ, ADHD, anxiety, SES). Kernel step: (1) segment all task data into 2-s windows, (2) compute FC matrix per window, (3) flatten upper triangle as features, (4) regress phenotypic targets using these connectivity features.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Uses HBN Biobank EEG to predict ten phenotypic/demographic measures (age, sex, IQ, ADHD, anxiety, SES) from functional connectivity patterns computed on 2-s epochs
- **Kernel Notes**: Must join EEG epochs with phenotypic CSV by subject ID; use subject-wise train/test splits to prevent leakage; store regression target version and assessment instrument name.

### Classical Task 2: Resting-State Functional Connectivity Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 300 s *, overlap = 0.0, target_events = [`resting_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `resting_start` | 0 | Resting-state with eyes open |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Analyzes 300s resting-state EEG functional connectivity patterns from HBN dataset
- **Kernel Notes**: Extract 300s resting-state blocks (eyes-open resting); compute FC features; predict phenotypic variables. (replaces Potential Task 4 from original analysis.md)

### Classical Task 3: Video Viewing Functional Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 170-230 s *, overlap = 0.0, target_events = [`video_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `video_start` | continuous | Movie viewing epoch for FC extraction |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Uses 170-230s video task segments concatenated with resting-state for connectivity analysis
- **Kernel Notes**: Extract video viewing epochs between `video_start` and `video_stop`; segment into 2-s windows for FC computation; regress phenotypic targets.

### Potential Task 1: Raw-meta event decoding and classification (event-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Use non-admin events such as `left_target`, `right_target`, `trialResponse`, `stim_ON`.

- **Kernel Notes**: Exclude admin markers from supervised target sets.

### Potential Task 2: Raw-meta state decoding (long-event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`, `video_start`, `video_stop`.

- **Kernel Notes**: Keep block-label mapping stable across releases.

### Potential Task 3: Super-meta response-time regression (competition-style)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: event-centered windows (task-dependent), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `response_time`
- **Kernel Notes**: Parse trial chains and write regression targets with unit/version metadata.


## Data Quality Notes

- HBN is a heterogeneous multi-task battery; task availability differs across participants and files.
- Event naming and density are not perfectly uniform across releases; mapping tables should be explicit.
- Admin markers (`boundary`, `9999`, etc.) are frequent and must be filtered before model target construction.
- Super-meta tasks are sensitive to join quality (subject ID harmonization, missingness, leakage control).
- Report clearly whether each experiment uses raw meta labels or super meta labels.


## Kernel Responsibilities


> **Super Meta Required**: Yes
> **Status**: wait_manual_review