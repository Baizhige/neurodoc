# BMI-HDEEG: High-Density EEG During Motor-Imagery-Based Brain-Computer Interface Training

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 570 | **Channels**: 256 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

This dataset contains high-density EEG recordings from 30 healthy participants (5 female, 25 male; ages 18–27) performing motor imagery-based brain-computer interface (MI-BCI) neurofeedback training. Participants underwent 19 training sessions each, with two experimental patterns: Pattern A (ses-01 and ses-19) used a 4-event structure with motor imagery classes (left hand, right hand, feet, rest), while Pattern B (ses-02 through ses-18) used a simplified 2-event structure with rest and task phases only. EEG was recorded using a 256-channel Magstim EGI GES400 amplifier with a Hydrocel Geodesic Sensor Net at 500 Hz sampling rate. The BCI system provided real-time neurofeedback based on sensorimotor rhythm (SMR) modulation during motor imagery tasks.

## File Scan Result

> **Kernel SHA256**: `d00e23c7d1839dd526925e72f4d56bb242867eebd3bb53938d58fb8b7fc7e15b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 4180 | event | raw | Trial phase onset: rest |
| `event_2` | 4180 | event | raw | Trial phase onset: task |
| `event_3` | 910 | event | raw | Trial phase onset: rest |
| `event_4` | 910 | event | raw | Trial phase onset: ready |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Ages range from 22-26 based on participants_tsv_sample; dataset_description references BMI-HDEEG dataset 3 |
| `amplifier` | complete | eeg_json indicates Manufacturer 'Magstim EGI' and ManufacturersModelName 'GES400', not g.USBamp/g.HIamp |
| `cap` | complete | eeg_json indicates CapManufacturer 'Magstim EGI' and CapManufacturersModelName 'Hydrocel Geodesic Sensor Net', not g.GAMMAcap |
| `gender` | complete | Values 'female' and 'male' confirmed in participants_tsv_sample |
| `handedness` | complete | Values 'left' and 'right' confirmed in participants_tsv_sample |
| `sex` | complete | No explicit 'sex' field found in evidence; only 'gender' field present in participants_tsv_sample with values 'female' and 'male' |

## Tasks

### Classical Task 1: Rest vs Task State Detection (Pattern B)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 6 s *, target_events = [`event_2`, `event_3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_3` | 0 | rest (Pattern B sessions: ses-02 through ses-18) |
  | `event_2` | 1 | task (Pattern B sessions: ses-02 through ses-18) |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Pattern B sessions (ses-02 through ses-18) contain two trial phases: rest (event_3, value=1) and task (event_2, value=2), forming a simplified 2-event cycle that supports rest vs task state classification.
  - 10.1109/tnsre.2024.3365197 — Task periods are 6s duration; rest periods vary but typically 5-6s; epoch window 0-6s from phase onset used for consistency.
- **Notes**: This task uses Pattern B's phase markers (event_2=task, event_3=rest) for binary state classification. These are trial phase onsets, not motor imagery class labels. The 0-6s window captures the full task period and comparable rest period. Sessions ses-01 and ses-19 (Pattern A) are excluded as they use a different 4-event structure.

### Potential Task 1: Age Regression from Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | `age` | Continuous age in years (18.0–27.0); used as regression target |
- **Evidence**:
  - `participants.tsv` — Age values complete for all 30 subjects (range 18–27, mean ~22.5)
- **Notes**: Segmentation-based approach with no event dependency; each 6-second segment from continuous EEG is labeled with the subject's age from participants.tsv. This tests whether EEG spectral or spatial features during SMR-BCI task performance predict participant age. Segment length matches typical task period duration in the paradigm.

### Potential Task 2: Gender Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | gender | female → 0, male → 1 (binary; 5 female / 25 male, class imbalance) |
- **Evidence**:
  - (none — potential task)
- **Notes**: Segmentation-based task using 6-second non-overlapping windows from continuous SMR-BCI neurofeedback EEG. Subject-level gender label from participants.tsv applied to all segments from that subject. Tests sex-related EEG differences during SMR-BCI neurofeedback training.

### Potential Task 3: Handedness Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | handedness | left → y=0, right → y=1 (29 right, 1 left; severely imbalanced) |
- **Evidence**:
- **Notes**: Segments continuous EEG into non-overlapping 6-second windows. Each segment inherits the subject's handedness from participants.tsv as the label. Tests whether lateralization-related EEG features during SMR-based BCI neurofeedback (right-hand motor imagery) can discriminate left- vs right-handed individuals despite the extreme class imbalance (1:29 ratio).

### Potential Task 4: Continuous EEG Segmentation with Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 6 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `age` | Continuous age in years (18.0–27.0); used directly as regression target |
- **Evidence**:
- **Notes**: Archetype C segmentation task with no event discrimination. The 6-second non-overlapping windows partition continuous EEG recordings into fixed-length segments, with each segment inheriting the participant's age from participants.tsv as the regression target. This differs from event-based approaches by treating the data as naturalistic/continuous without relying on trial phase markers.

## Data Quality Notes

- Event counts show unequal distribution between Pattern A (event_1/event_2: 4180 each) and Pattern B (event_3/event_4: 910 each), confirming substantial structural differences between session types that require careful separation for task design.
- Gender classification task has severe class imbalance (5 female vs 25 male, 1:5 ratio), which may limit model generalizability and require stratified sampling or class weighting.
- Handedness classification task has extreme class imbalance (1 left vs 29 right, 1:29 ratio), making this task practically unfeasible for meaningful machine learning without specialized techniques.
- The `sex` field is marked complete in metadata but evidence notes only `gender` field exists in participants.tsv; this is a documentation inconsistency in the source data.
- Equipment metadata (amplifier and cap) differs from what might be expected based on dataset_description references, with actual recordings using Magstim EGI GES400 and Hydrocel Geodesic Sensor Net rather than g.tec systems.
- Age range in participants.tsv (18–27) differs from the range mentioned in info notes (22–26), suggesting possible data subset considerations or documentation drift.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
