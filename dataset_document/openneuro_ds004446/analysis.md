# The BMI-HDEEG dataset 2

**Dataset**: `openneuro_ds004446` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004446
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 237 | **Channels**: 130 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

A high-density EEG dataset focused on sensorimotor rhythm-based brain-computer interfacing (BCI). Subjects performed a motor imagery task with three trial phases: rest (~8s), task execution (~7s), and interval (~5s). EEG was recorded using a 130-channel high-density setup at 1000 Hz sampling rate. The paradigm follows a standard SMR-BCI trial structure with phase onset markers rather than traditional motor imagery class cues.

## File Scan Result

> **Kernel SHA256**: `846f88e87a5726a11f362cc12f7e71288781559b9b1ba11d04a676cb789854ff`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 6782 | event | raw | Trial phase onset: rest |
| `event_2` | 5633 | event | raw | Trial phase onset: task |
| `event_3` | 4020 | event | raw | Trial phase onset: interval |
| `event_4` | 5487 | event | raw | Unobserved event ID - not present in sampled events.tsv files |
| `event_5` | 1258 | event | raw | Unobserved event ID - not present in sampled events.tsv files |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: rest vs task phase detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 7 s *, target_events = [`event_1`, `event_2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | event_1 | 0 | rest phase onset |
  | event_2 | 1 | task phase onset |
- **Evidence**:
- **Notes**: This task discriminates between rest and task execution states using trial phase onset markers from the BMI-HDEEG SMR-BCI paradigm. Event 1 marks rest periods (~8s) and Event 2 marks task periods (~7s). The tmax=7s is set to the shorter phase duration to maintain balanced epoch lengths; tmin=0 at phase onset for standard phase-locked analysis. Event 3 (interval) is excluded as it serves as an inter-trial buffer. This is a Potential Task derived from confirmed event structure rather than an explicitly published analysis.

### Classical Task 2: Rest vs Task vs Interval Phase Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 5 s *, target_events = [`event_1`, `event_2`, `event_3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:

| Event ID | y | Meaning |
|----------|---|---|
| event_1 | 0 | rest |
| event_2 | 1 | task |
| event_3 | 2 | interval |

- **Evidence**:
  - sub-001_ses-01_task-smrbmi_events.tsv — Sampled events.tsv shows repeating trial structure with value=1/'rest' (duration ~8s), value=2/'task' (duration ~7s), value=3/'interval' (duration ~5s); confirmed across all 6 subjects and multiple sessions
  - task-smrbmi_events.json — BIDS sidecar defines 'value' column as 'The code (EEG Marker or Trigger value) associated with an event' and 'instruction' column as 'content of task participants executed'
- **Notes**: Three-phase trial classification leveraging the full trial structure of this SMR-BMI dataset. Epochs are cropped to 5s to match the shortest phase (interval) and avoid phase overlap, with zero-padded or truncated epochs for longer rest/task phases. This is a Potential Task as it uses phase markers for state classification rather than a traditional BCI decoding target.

### Classical Task 3: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | no mapping |
- **Evidence**:
- **Notes**: Segmentation-based epoching extracts fixed-length 4-second windows with 50% overlap from continuous EEG recordings. No event alignment is required for this subject-level regression task. The age label is a native participants.tsv column (B3 archetype, Meta Level = raw).

### Classical Task 4: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | female -> 0; male -> 1 |
- **Evidence**:
- **Notes**: Subject-level binary classification using 4-second non-overlapping segments of continuous EEG. All segments from a given subject share the same gender label from participants.tsv. Class imbalance (5 female, 25 male) is noted; appropriate stratification or class weighting is recommended during model training.

### Classical Task 5: continuous EEG segmentation with age labels
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | no mapping |
- **Evidence**:
- **Notes**: Archetype C (segmentation + info-native). Uses pure segmentation without event anchoring to extract representative 2-second samples from continuous 424-541 second recordings. Same age regression target as B3 variant but explicitly structured as segmentation paradigm for pipeline flexibility. Meta Level is raw because age is a native participants.tsv column with no kernel derivation required. Shorter 2-second segments with no overlap increase sample density for regression modeling.

## Data Quality Notes

- Event counts in File Scan Result (events 1-3) differ substantially from counts in the existing draft (6782 vs 6782 for event 1, 5633 vs 5633 for event 2, 4020 vs 4020 for event 3), but event meanings have changed completely between drafts — from motor imagery class cues (left hand, right hand, feet) to trial phase markers (rest, task, interval). This is a fundamental semantic discrepancy that requires manual review.
- Events 4 and 5 are marked as "Unobserved event ID - not present in sampled events.tsv files" yet have high total counts (5487 and 1258), suggesting these may be synthetic or aggregated counts from kernel processing rather than direct file observations.
- Subject count discrepancy: existing draft states 237 subjects, but Tasks section references N=30 subjects for demographic tasks. The 30-subject figure appears in task evidence ("confirmed across all 6 subjects and multiple sessions" and "N=30" in age regression), suggesting the actual completed/usable subject count may be 30 rather than 237.
- Device metadata is completely missing across all files.
- Severe class imbalance in handedness classification (1 left-handed vs 29 right-handed) limits practical utility of that task.
- Gender classification also shows class imbalance (5 female vs 25 male).
- The existing draft's three-class motor imagery paradigm description conflicts with the authoritative File Scan Result's phase-based event structure — the dataset may not contain traditional motor imagery class markers as originally assumed.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
