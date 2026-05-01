# IACKD: Intention Action Conflict EEG-Hand Kinematics Dataset

**Dataset**: `openneuro_ds006840` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006840
**Category**: High-level Mental | **Subjects**: 128 | **Files (Completed)**: 128 | **Channels**: 29 | **Sampling Rate**: 1024 Hz | **Manual Review**: Pending

## Paradigm

This dataset investigates the neural correlates and hand kinematics associated with conflicts between intended and executed actions. In an intention-action conflict paradigm, participants are cued to perform one action but must sometimes execute a competing action, creating conflict between motor intention and execution. EEG is recorded alongside hand kinematic data during pre-movement planning (`premove`), execution (`execution`), and successful hit trials (`hit`).

## File Scan Result

> **Kernel SHA256**: `c806331b2555e150293399309a114c72dd7de967c86557d7614352a764108e4f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `admin: marker-5` | 184 | event | raw | Administrative marker (session/block) |
| `admin: marker-6` | 2 | event | raw | Administrative marker (session/block) |
| `admin: marker-7` | 1 | event | raw | Administrative marker (session/block) |
| `execution` | 7026 | event | raw | Motor execution onset |
| `hit` | 7031 | event | raw | Successful trial completion |
| `incongruent_trial` | 6881 | event | raw | Conflict between intended and executed action |
| `premove` | 7022 | event | raw | Pre-movement preparation period onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Intention Action Congruency (Primary Publisher Task)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 4.0, overlap = null, target_events = [incongruent_trial] | segment_length = Needs Verification, overlap = Needs Verification
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds006840 DOI: https://doi.org/10.18112/openneuro.ds006840.v1.0.0
- **Kernel Notes**: Raw markers sufficient for primary classification. incongruent_trial marker (6881 events) serves as conflict condition label. Full motor trial spans ~3-4s from premove through execution to hit, supporting long event epoching.

### Normal Task 1: Motor Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, overlap = null, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping for motor planning-execution cycle phases.

| Event | y | Meaning |
|-------|---|---|
| `premove` | 0 | Pre-movement intention/preparation phase |
| `execution` | 1 | Motor execution onset |
| `hit` | 2 | Successful trial completion |

- **Evidence**: Epoch alignment recommendations. Well-balanced 3-class design (~7022-7031 events per type) making it ideal for classification. Short stimulus-onset markers (<2s) representing distinct moments in motor planning-execution cycle.
- **Kernel Notes**: Type 1 + Type 3 mode selected. Raw markers (premove/execution/hit) sufficient for motor phase classification via Annotation channel. Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

### Potential Task 1: Intention-Action Conflict Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, overlap = null, target_events = [incongruent_trial]
- **Label Route**: `event`
- **Target Definition**: Conflict condition detection.

| Event | y | Meaning |
|-------|---|---|
| `incongruent_trial` | 1 | Conflict between intended and executed action |
| (absence) | 0 | Congruent/non-conflict trial |

- **Evidence**: The incongruent_trial marker (6881 events) directly indicates conflict conditions in the intention-action paradigm. Paradigm plausibility: conflict between motor intention and execution creates measurable neural signatures (ERP components, beta rebound patterns) well-established in motor planning literature.
- **Kernel Notes**: Type 2 super-meta integration available if conflict-specific analysis required. Combine with motor phase markers to examine neural signatures at specific timepoints within conflict trials.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
