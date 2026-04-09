# Healthy Brain Network (HBN) EEG - Release 7

**Dataset**: `openneuro_ds005511` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005511
**Category**: Complex Applied | **Subjects**: 381 | **Files (Completed)**: 3100 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 7 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `stim_ON` | 34708 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 34688 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 13272 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 7530 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 6992 | event | raw | Participant button press - right hand |
| `right_target` | 6384 | event | raw | Right-side target stimulus |
| `left_target` | 6361 | event | raw | Left-side target stimulus |
| `trialResponse` | 4059 | event | raw | Trial response event |
| `break cnt` | 3092 | admin | raw | Break/counter marker between blocks |
| `instructed_toOpenEyes` | 2193 | event | raw | Instruction to open eyes (resting block) |
| `instructed_toCloseEyes` | 1825 | event | raw | Instruction to close eyes (resting block) |
| `boundary` | 1728 | admin | raw | Segment boundary marker |
| `resting_start` | 371 | event | raw | Resting-state block onset |
| `9999` | 2143 | admin | raw | End-of-recording marker |


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

### Classical Task 1: Resting-state EEG multi-label psychiatric diagnosis classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `resting_start`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ADHD` | 0/1 | ADHD diagnosis (DSM-V) |
  | `ANX` | 0/1 | Anxiety diagnosis (DSM-V) |
  | `SLD` | 0/1 | Specific Learning Disorder (DSM-V) |
  | `ASD` | 0/1 | Autism Spectrum Disorder (DSM-V) |
  | `DISR` | 0/1 | Disruptive/Impulsive disorder (DSM-V) |
  | `COM` | 0/1 | Communication disorder (DSM-V) |
  | `DEP` | 0/1 | Depressive disorder (DSM-V) |
  | `Other` | 0/1 | Other DSM-V diagnosis |
  | `NoDiagnosis` | 0/1 | No diagnosis |
- **Super Meta Notes**: Derived from clinical assessment tables (SCARED-GAD, SWAN-IN, SWAN-HY, SRS-2-SCI, SRS-2-RRB, WISC-VCI, WISC-WMI) by licensed clinicians. Kernel step: Join EEG epochs with phenotypic diagnosis tables by subject ID, apply amplitude threshold ±90μV for epoch rejection, then construct multi-label binary vectors per subject.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2022.119348` — Multi-task multi-label classification of 8 DSM-V categories from 2s resting EEG epoch spectral features
- **Kernel Notes**: Concatenate eyes-closed resting blocks (5 blocks × 40s each), segment into 2s non-overlapping epochs, reject epochs exceeding ±90μV amplitude, compute spectral features, then map to multi-label diagnosis vector.

### Classical Task 2: Resting-state EEG symptom severity regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `resting_start`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `SCARED_GAD` | float | SCARED-GAD anxiety score |
  | `SWAN_IN` | float | SWAN-Inattention score |
  | `SWAN_HY` | float | SWAN-Hyperactivity score |
  | `SRS2_SCI` | float | SRS-2 Social Communication score |
  | `SRS2_RRB` | float | SRS-2 Restricted/Repetitive Behavior score |
  | `WISC_VCI` | float | WISC-V Verbal Comprehension Index |
  | `WISC_WMI` | float | WISC-V Working Memory Index |
- **Super Meta Notes**: Derived from standardized behavioral/cognitive assessments (SCARED, SWAN, SRS-2, WISC-V). Kernel step: Extract spectral features from 2s epochs, aggregate per subject (e.g., mean), then predict 7 continuous symptom severity measures.
- **Evidence**:
  - DOI: `10.1016/j.neuroimage.2022.119348` — Multi-target regression of 7 continuous symptom severity measures from resting EEG spectral features
- **Kernel Notes**: Same epoching as classification task, but regression targets are 7 continuous clinical scores. Use subject-wise splits to prevent label leakage between train/test.

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
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`.

- **Kernel Notes**: Keep block-label mapping stable across releases.

### Potential Task 3: Super-meta response-time regression (competition-style)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: event-centered windows (task-dependent), target_events = see Target Definition
- **Label Route**: `misc`
- **Target Definition**: Continuous target value as defined by kernel and label route.

- **Regression Target**: `response_time`
- **Kernel Notes**: Parse trial chains and write regression targets with unit/version metadata.

### Potential Task 4: Super-meta psychopathology-factor modeling
- **Task Type**: regression
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


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review