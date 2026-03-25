# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection (contrastTrial), surrounding suppression, sequence learning (seqLearning), and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, stim, misc
> **Evidence Keywords**: response_time, externalizing, phenotypic, regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005505

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stim_ON` | 13278 | short | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 13248 | short | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 8884 | long | raw | Contrast detection trial block onset |
| `left_buttonPress` | 5095 | short | raw | Participant button press - left hand |
| `right_buttonPress` | 4634 | short | raw | Participant button press - right hand |
| `right_target` | 4251 | short | raw | Right-side target stimulus |
| `left_target` | 4243 | short | raw | Left-side target stimulus |
| `break cnt` | 1488 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 1247 | short | raw | Trial response event |
| `instructed_toOpenEyes` | 816 | long | raw | Instruction to open eyes (resting block) |
| `video_start` | 761 | long | raw | Movie clip onset |
| `boundary` | 728 | admin | raw | Segment boundary marker |
| `video_stop` | 723 | long | raw | Movie clip offset |
| `instructed_toCloseEyes` | 680 | long | raw | Instruction to close eyes (resting block) |
| `resting_start` | 136 | long | raw | Resting-state block onset |
| `seqLearning_start` | 122 | long | raw | Sequence learning block onset |
| `learningBlock_1` | 122 | long | raw | Sequence learning block 1 onset |
| `9999` | 1136 | admin | raw | End-of-recording marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `externalizing_factor`, `p_factor`, `response_time`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stim_ON`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Brain-Behavior Regression from EEG Functional Connectivity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Target Variable | Type | Source Instrument |
  |-----------------|------|-------------------|
  | `age` | continuous | years |
  | `sex` | categorical | M/F |
  | `IQ` | continuous | WISC score |
  | `ADHD` | continuous | SWAN score |
  | `CBCL` | continuous | behavioral score |
  | `SES` | continuous | Barratt scale |
  | `anxiety` | continuous | SCARED |
  | `IAT` | continuous | internet addiction |
  | `MFQ` | continuous | mood questionnaire |
  | `SDS` | continuous | sleep scale |
  | `DTS` | continuous | distress tolerance |
- **Super Meta Notes**: Labels derived from standardized assessment instruments (WISC, SWAN, CBCL, Barratt, SCARED, etc.) administered to participants, not from raw EEG event markers. FC-phenotype associations tested using Multivariate Distance Matrix Regression (MDMR).
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2020.117001 — Uses EEG functional connectivity (imaginary coherence) from HBN Biobank to identify associations between brain connectivity patterns and ten phenotypic/demographic measures including age, sex, and IQ. Uses 2-second epochs for iCOH computation from resting state and video tasks.
- **Kernel Notes**: Compute imaginary coherence (iCOH) between electrode pairs on 2-second epochs, then correlate connectivity matrices with phenotypic variables. Use subject-wise splits to prevent leakage when joining with phenotypic tables.

### Primary Task 2: Publisher-defined BIDS task: Despicable Me
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://eeg2025.github.io/` DOI: https://doi.org/10.1101/089060


### Primary Task 3: Publisher-defined BIDS task: Seq Learning6target
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://eeg2025.github.io/` DOI: https://doi.org/10.1101/089060


### Primary Task 4: Publisher-defined BIDS task: Seq Learning8target
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://eeg2025.github.io/` DOI: https://doi.org/10.1101/089060

### Normal Task 1: Raw-meta event decoding and classification (event-level)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use non-admin events such as `left_target`, `right_target`, `trialResponse`, `stim_ON`.

- **Kernel Notes**: Exclude admin markers from supervised target sets.


### Normal Task 2: Raw-meta state decoding (long-event)
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`, `video_start`, `video_stop`.

- **Kernel Notes**: Keep block-label mapping stable across releases.


### Normal Task 3: Super-meta response-time regression (competition-style)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: event-centered windows (task-dependent), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `response_time`
- **Kernel Notes**: Parse trial chains and write regression targets with unit/version metadata.


### Normal Task 4: Super-meta psychopathology-factor modeling
- **Task Type**: regression (or discretized classification baseline)
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: Needs verification, target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `p_factor` / `externalizing_factor` (schema dependent)
- **Kernel Notes**: Join EEG with phenotypic tables by subject key and use subject-wise splits to prevent leakage.

## Data Quality Notes

- HBN is a heterogeneous multi-task battery; task availability differs across participants and files.
- Event naming and density are not perfectly uniform across releases; mapping tables should be explicit.
- Admin markers (`boundary`, `9999`, etc.) are frequent and must be filtered before model target construction.
- Super-meta tasks are sensitive to join quality (subject ID harmonization, missingness, leakage control).
- Report clearly whether each experiment uses raw meta labels or super meta labels.

## References

- OpenNeuro dataset page: `https://openneuro.org/datasets/ds005505/versions/1.0.1`
- EEG2025 challenge portal: `https://eeg2025.github.io/`
- EEGUnity kernel tutorial (rich/super meta abstraction): `https://eegunity.readthedocs.io/en/v0.7.0/tutorial/How%20to%20Reading%20Rich%20Meta%20Data%20via%20Kernel.html`
- EEGUnity batch API (`epoch_by_event_hdf5`, `epoch_by_long_event_hdf5`): `https://eegunity.readthedocs.io/en/v0.7.0/eegunity.modules.batch.html`
