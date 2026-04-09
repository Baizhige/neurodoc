# Healthy Brain Network (HBN) EEG - Release 4

**Dataset**: `openneuro_ds005508` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005508
**Category**: Complex Applied | **Subjects**: 324 | **Files (Completed)**: 3342 | **Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

The Healthy Brain Network (HBN) EEG Release 4 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `stim_ON` | 35171 | event | raw | Contrast detection stimulus onset |
| `fixpoint_ON` | 35072 | event | raw | Fixation point onset (trial start cue) |
| `contrastTrial_start` | 20646 | event | raw | Contrast detection trial block onset |
| `left_buttonPress` | 11751 | event | raw | Participant button press - left hand |
| `right_buttonPress` | 10656 | event | raw | Participant button press - right hand |
| `right_target` | 9909 | event | raw | Right-side target stimulus |
| `left_target` | 9806 | event | raw | Left-side target stimulus |
| `break cnt` | 3452 | admin | raw | Break/counter marker between blocks |
| `trialResponse` | 3286 | event | raw | Trial response event |
| `instructed_toOpenEyes` | 1929 | event | raw | Instruction to open eyes (resting block) |
| `boundary` | 1871 | admin | raw | Segment boundary marker |
| `instructed_toCloseEyes` | 1608 | event | raw | Instruction to close eyes (resting block) |
| `resting_start` | 322 | event | raw | Resting-state block onset |
| `9999` | 2502 | admin | raw | End-of-recording marker |


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

### Classical Task 1: Resting State Classification (Eyes-Open vs Eyes-Closed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20.0 s (eyes-open) * or 40.0 s (eyes-closed) *, overlap = 0.0, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — Paper describes the HBN dataset with resting-state paradigm using 20s eyes-open and 40s eyes-closed segments
- **Kernel Notes**: Use long-event epochs to capture sustained resting-state blocks. Map `instructed_toOpenEyes` to eyes-open class and `instructed_toCloseEyes` to eyes-closed class. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Sequence Learning Classification (Unknown vs Newly-Learned vs Known)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stim_ON`, `fixpoint_ON`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | unknown_stimulus | 0 | Stimulus still unknown to participant |
  | newly_learned_stimulus | 1 | Stimulus newly learned by participant |
  | known_stimulus | 2 | Stimulus well-known to participant |
- **Super Meta Notes**: Derived from raw events [`left_target`, `right_target`, `stim_ON`, `fixpoint_ON`] combined with behavioral recall performance data. Kernel step: Parse trial sequence and join with participant recall reports to determine learning state label for each stimulus.
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — Paper describes sequence learning paradigm with learning state categories (still-unknown, newly-learned, known) derived from participant recall reports
- **Kernel Notes**: Epoch around stimulus onsets. Join EEG epochs with behavioral recall data to derive learning state labels. Use subject-wise splits to prevent leakage. (replaces Classical Task 2 from original analysis.md)

### Classical Task 3: Contrast Detection Trial Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s *, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `left_target` | 0 | Left-side target stimulus |
  | `right_target` | 1 | Right-side target stimulus |
- **Evidence**:
  - DOI: `10.1038/sdata.2017.40` — Paper describes contrast detection paradigm with 500ms pre-target to 1000ms post-peak sensory evidence epochs
- **Kernel Notes**: Epoch around left/right target stimuli to classify which side target was presented. (replaces Classical Task 3 from original analysis.md)

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
- **Target Definition**: Use state/block markers such as `instructed_toOpenEyes`, `instructed_toCloseEyes`, `resting_start`, `contrastTrial_start`.

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