# EEG Dataset for Cursor BCI (Meng 2019)

**Dataset**: `figshare_meng2019` | **Year**: 2019 | **URL**: https://doi.org/10.6084/m9.figshare.7959572
**Category**: Action/Output | **Subjects**: N/A (see notes) | **Files (Completed)**: 126 | **Channels**: 64 | **Sampling Rate**: 128 Hz

## Paradigm

Participants performed a one-dimensional cursor BCI task using mental imagery in three experiments (Meng et al., 2019). EEG was recorded from 64 channels. Subjects imagined motor or other mental activities to move a cursor toward a target positioned above ("+") or below ("-") center, or at rest (center target). The dataset covers three experiments (Exp1, Exp2, Exp3); Exp1 and Exp2 used a Neuroscan SynAmps RT amplifier, while Exp3 used a Biosemi Active Two system. The paradigm recorded both target intent events (what the subject was trying to do) and result events (what the BCI decoded), enabling analysis of mental imagery decoding accuracy.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `target cursor plus` | varies | event | raw | Target positioned above center; subject imagines upward/+ movement |
| `target cursor minus` | varies | event | raw | Target positioned below center; subject imagines downward/- movement |
| `target rest` | varies | event | raw | Target at center; subject imagines neutral/rest state |
| `result cursor plus` | varies | admin | raw | BCI decoded + direction (feedback signal) |
| `result cursor minus` | varies | admin | raw | BCI decoded - direction (feedback signal) |

>
> `result cursor *` events encode BCI feedback and are not ground-truth labels; use only `target cursor *` events for supervised classification.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Two-class motor imagery cursor direction decoding (left vs right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`target cursor plus`, `target cursor minus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `target cursor plus` | 1 | Left-hand motor imagery (cursor moves up/+) |
  | `target cursor minus` | 0 | Right-hand motor imagery (cursor moves down/-) |
- **Evidence**:
  - DOI: 10.3389/fnhum.2019.00128 — This paper analyzes the same figshare dataset from 42 subjects performing left/right hand motor imagery to control a cursor BCI, evaluating behavioral performance and ERD/ERS patterns.
- **Kernel Notes**: Exclude `result cursor *` events (BCI feedback, not ground truth). Use only `target cursor *` events as class labels. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Three-class motor imagery cursor control (plus, minus, rest)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = [`target cursor plus`, `target cursor minus`, `target rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `target cursor plus` | 0 | Left-hand motor imagery (cursor up/+) |
  | `target cursor minus` | 1 | Right-hand motor imagery (cursor down/-) |
  | `target rest` | 2 | Rest / neutral state |
- **Evidence**:
  - DOI: 10.3389/fnhum.2019.00128 — Same dataset used for cursor BCI with three target types (up, down, center/rest).
- **Kernel Notes**: Exclude `result cursor *` events. Include `target rest` trials for 3-class classification.

### Potential Task 1: Cursor Direction Classification - Up vs. Down (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `result cursor *` events - these encode the BCI output, not the ground-truth label. Exclude `target rest` trials unless a 3-class task is intended.

| Event | y | Meaning |
|-------|---|-|
| `target cursor plus` | 1 | Imagined upward / + cursor movement |
| `target cursor minus` | 0 | Imagined downward / - cursor movement |


### Potential Task 2: 3-Class Cursor BCI Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|-|
| `target cursor plus` | 0 | Imagined + cursor movement |
| `target cursor minus` | 1 | Imagined - cursor movement |
| `target rest` | 2 | Rest / neutral state |

## Data Quality Notes

- Sex information is not available in the dataset metadata.
- Three experiments (Exp1, Exp2, Exp3) use different amplifier systems; process per-experiment or normalize across systems.
- `result cursor *` events are BCI feedback signals, not labels; do not use for classification targets.
- Subject count is not explicitly stated; estimate from unique subject folders in file paths.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review