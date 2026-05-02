# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 22 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz | **Manual Review**: Yikai Dong

## Paradigm

A brain-computer interface (BCI) study investigating neural correlates of motor preparation and execution using high-density scalp EEG. Participants performed a cue-based motor task with a 130-channel GES400/Hydrocel GSN montage at 1000 Hz sampling. The experimental design includes both 2-phase (rest→task) and 4-phase (rest→ready→task→interval) paradigm sessions, with thirty subjects participating and handedness information available in the participants metadata.

## File Scan Result

> **Kernel SHA256**: `e882c899bcb6d30b0e0311b5eca21d951830de6467723b91a72c1eb23f2d4564`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1-rest` | 4180 | event | raw | Rest/relaxation instruction onset; trigger value 1, instruction `rest`, present in both 2-phase and 4-phase blocks. |
| `event_2-ready` | 910 | event | raw | Ready/preparation instruction onset in 4-phase blocks; trigger value 2, instruction `ready`, typically preceding the motor imagery task period. |
| `event_2-task` | 3270 | event | raw | Task/motor imagery instruction onset in 2-phase blocks; trigger value 2, instruction `task`, corresponding to right-finger kinesthetic motor imagery/SMR-ERD control. |
| `event_3-task` | 910 | event | raw | Task/motor imagery instruction onset in 4-phase blocks; trigger value 3, instruction `task`, corresponding to right-finger kinesthetic motor imagery/SMR-ERD control. |
| `event_4-interval` | 910 | event | raw | Interval/blank instruction onset in 4-phase blocks; trigger value 4, instruction `interval`, used as the post-task blank/break phase. |


> Event IDs are emitted as `event_<value>-<instruction>` because raw trigger value 2 is reused with different meanings (`ready` in 4-phase blocks and `task` in 2-phase blocks). Onsets are converted from the events.tsv millisecond unit to MNE seconds by the kernel.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | complete | EEG sidecar reports Manufacturer = Magstim EGI, ManufacturersModelName = GES400, SamplingFrequency = 1000, and EEGChannelCount = 129. |
| `amplifier` | complete | e.g. GES400 |
| `cap` | complete | e.g. Magstim EGI Hydrocel Geodesic Sensor Net |
| `dataset` | complete | e.g. openneuro_ds004447 |
| `eeg_channel_count` | complete | e.g. 129, 128 |
| `eeg_ground` | complete | e.g. CPz, placed on FCz |
| `eeg_placement_scheme` | complete | e.g. 10-20 system, 10 percent system |
| `eeg_reference` | complete | e.g. Cz |
| `event_description_format` | complete | e.g. event_<value>-<instruction> |
| `event_onset_units` | complete | e.g. ms converted to seconds |
| `handedness` | complete | e.g. left, right |
| `manufacturer` | complete | e.g. Magstim EGI |
| `paradigm_schema` | complete | e.g. 4phase, 2phase |
| `sampling_rate_hz` | complete | e.g. 1000 |
| `session` | complete | e.g. ses-01, ses-02, ses-03 |
| `source_file` | complete | e.g. sub-001_ses-01_task-smrbmi_eeg.edf, sub-001_ses-02_task-smrbmi_eeg.edf, sub-001_ses-03_task-smrbmi_eeg.edf |
| `stim_channel` | complete | e.g. Status |
| `subject_id` | complete | e.g. sub-001, sub-002, sub-003 |
| `task` | complete | e.g. smrbmi |


## Tasks

### Classical Task 1: Rest vs right-hand motor imagery state classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_1-rest`, `event_2-task`, `event_3-task`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_1-rest` | 0 | rest / relaxation phase |
  | `event_2-task` | 1 | right-hand motor imagery task phase in 2-phase training sessions |
  | `event_3-task` | 1 | right-hand motor imagery task phase in 4-phase assessment sessions |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — The data descriptor describes Dataset 3 as a sensorimotor rhythm-based BCI dataset using right-hand motor imagery and SMR-ERD control.
  - OpenNeuro ds004447 `events.tsv` — Public event files contain `rest` and `task` instructions; trigger value 2 is schema-dependent and must be disambiguated by instruction.
  - https://github.com/Junichi-Ushiba-Laboratory/pj-hd-smrbmi/blob/main/helper_analysis_EEG.m — Sample analysis code labels Dataset 3 windows as rest/task.
- **Notes**: This is the most defensible classical task because it matches the dataset's core SMR-ERD BCI contrast: rest versus right-hand motor imagery. It replaces the unsupported "motor preparation vs execution" formulation. `tmax = 2 s` is a conservative implementation window and is not claimed as a verbatim paper parameter.

### Potential Task 1: Ready vs task state classification in 4-phase assessment sessions
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_2-ready`, `event_3-task`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_2-ready` | 0 | ready / preparation instruction in 4-phase assessment sessions |
  | `event_3-task` | 1 | right-hand motor imagery task instruction in 4-phase assessment sessions |
- **Evidence**:
  - OpenNeuro ds004447 `events.tsv` — 4-phase sessions contain value 2 with instruction `ready` and value 3 with instruction `task`.
- **Notes**: This is data-supported but should remain a Potential Task. Current evidence confirms the event structure, but does not support treating ready-vs-task as the primary published benchmark.

### Potential Task 2: Four-state instruction classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_1-rest`, `event_2-ready`, `event_2-task`, `event_3-task`, `event_4-interval`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `event_1-rest` | 0 | rest / relaxation instruction |
  | `event_2-ready` | 1 | ready / preparation instruction in 4-phase assessment sessions |
  | `event_2-task` | 2 | right-hand motor imagery task instruction in 2-phase training sessions |
  | `event_3-task` | 2 | right-hand motor imagery task instruction in 4-phase assessment sessions |
  | `event_4-interval` | 3 | interval / blank instruction in 4-phase assessment sessions |
- **Evidence**:
  - OpenNeuro ds004447 `events.tsv` — Public event files expose `rest`, `ready`, `task`, and `interval` instructions.
- **Notes**: This task classifies instruction/phase state rather than motor-imagery class. Because `ready` and `interval` occur only in 4-phase sessions, downstream use should report schema imbalance.

### Potential Task 3: Age regression from EEG segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `subject_age` | no mapping; numeric age in years, range 19-27 for the 22 publicly available EEG subjects |
- **Evidence**:
  - OpenNeuro ds004447 `participants.tsv` — Age metadata is available; only `sub-001` to `sub-022` have public EEG data directories.
- **Notes**: Subject-level metadata task. It is technically implementable but not the core BCI benchmark.

### Potential Task 4: Sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `subject_sex` | female -> 0; male -> 1 |
- **Evidence**:
  - OpenNeuro ds004447 `participants.tsv` — Sex metadata is available; among the 22 publicly available EEG subjects the distribution is 3 female / 19 male.
- **Notes**: Technically valid binary metadata task, but strongly imbalanced and not central to the BCI paradigm.

### Potential Task 5: Handedness classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s, overlap = 1, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `handedness` | left -> 0; right -> 1 |
- **Evidence**:
  - OpenNeuro ds004447 `participants.tsv` — Handedness metadata is available; among the 22 publicly available EEG subjects the distribution is 1 left / 21 right.
- **Notes**: Satisfies the two-class requirement but is extremely imbalanced; treat as an edge-case metadata task.

## Data Quality Notes

- Event meanings differ across session schemas (Schema A vs Schema B), requiring careful session-aware task construction.
- Schema A (assessment sessions: ses-01, ses-07, ses-13, ses-19) uses 4-phase structure with event_1=rest, event_6=ready, event_4=task, event_5=interval.
- Schema B (training sessions: ses-02-06, ses-08-12, ses-14-18) uses 2-phase structure with event_2=task, event_3=rest.
- Severe class imbalance in Schema A: event_6 (ready) has only 91 events versus ~1237 for task/interval.
- Device metadata is missing from the dataset scan results.
- Gender distribution is highly imbalanced (5 female, 25 male).
- Handedness is extremely imbalanced (1 left-handed, 29 right-handed).
- Age range is narrow (18-27 years), potentially limiting regression task viability.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
