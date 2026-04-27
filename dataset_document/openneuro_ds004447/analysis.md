# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

A brain-computer interface (BCI) study investigating neural correlates of motor preparation and execution using high-density scalp EEG. Participants performed a cue-based motor task with a 130-channel GES400/Hydrocel GSN montage at 1000 Hz sampling. The experimental design includes both 2-phase (rest→task) and 4-phase (rest→ready→task→interval) paradigm sessions, with thirty subjects participating and handedness information available in the participants metadata.

## File Scan Result

> **Kernel SHA256**: `a622f3c18fda073fcab4904a246197ba85ac15a30fabf10670a0af99d88be864`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 327 | event | raw | Trial phase onset: rest |
| `event_2` | 5090 | event | raw | Trial phase onset: task |
| `event_3` | 3270 | event | raw | Trial phase onset: rest |
| `event_4` | 1237 | event | raw | Trial phase onset: task |
| `event_5` | 1237 | event | raw | Trial phase onset: interval |
| `event_6` | 91 | event | raw | Trial phase onset: ready |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class motor preparation vs execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 2 s, target_events = [`event_2`, `event_3`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_2 | 0 | task phase (Schema B: training sessions) |
  | event_3 | 1 | rest phase (Schema B: training sessions) |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Paper explicitly uses tmin=0s, tmax=2s for ready vs task comparison with C3-targeted ERD detection in 30 participants with 128-channel EEG at 1000 Hz
  - 10.1109/tnsre.2024.3365197 — Follow-up analysis using same epoching parameters for motor preparation vs execution discrimination
- **Notes**: The original paper's terminology conflates schemas: their "ready" maps to event_6 (assessment sessions only, 91 events) and "task" maps to event_4 (assessment, 1237 events) OR event_2 (training, 5090 events). The locked meanings reveal event_2=task and event_3=rest in Schema B (training sessions, dominant data volume). We emit a grounded rest-vs-task discrimination using the dominant Schema B data (event_2 vs event_3), which captures the BCI's core rest-task state discrimination with substantial trial count (5090 vs 3270). This is NOT the paper's exact "preparation vs execution" mapping (which would require event_6 vs event_4, limited to 91+1237 assessment trials), but is the most statistically viable and schema-honest classification task from this dataset. The event_2=task label represents the active motor execution state; event_3=rest represents the resting baseline state.

### Classical Task 2: Ready vs Task State Classification (Schema A Assessment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 2 s, target_events = [`event_6`, `event_4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_6 | 0 | ready |
  | event_4 | 1 | task |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Schema A assessment sessions (ses-01, ses-07, ses-13, ses-19) contain event_6 (ready, 91 events) and event_4 (task, 1237 events); ready phase has 2s duration per events.tsv, supporting tmax=2s for preparation-execution comparison
- **Notes**: Classification of trial phase: ready (preparation) versus task (execution) in assessment sessions. Both classes are phase markers, not motor imagery classes. The 2-second epoch window captures the full ready period and early task period, matching the paper's analysis approach for motor preparation vs motor execution comparison.

### Potential Task 1: Rest vs Task State Classification (Schema B)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_2`, `event_3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_2 | 0 | task |
  | event_3 | 1 | rest |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Schema B (training sessions, ses-02-06, ses-08-12, ses-14-18) contains 5090 event_2 (task) and 3270 event_3 (rest) events across 15 sessions per subject; locked meanings confirm event_2=task and event_3=rest in Schema B
- **Notes**: Fundamental SMR-ERD BCI discrimination: rest state (no ERD) vs task state (motor imagery producing ERD). Schema B is the dominant data schema with the majority of events. The 0-2s window captures the early task execution period while avoiding transition overlap, as task duration varies 5-6s per events.tsv.

### Potential Task 2: 4-class trial phase classification (Schema A)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 2 s *, target_events = [`event_1`, `event_4`, `event_5`, `event_6`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_1 | 0 | rest |
  | event_6 | 1 | ready |
  | event_4 | 2 | task |
  | event_5 | 3 | interval |
- **Evidence**:
- **Notes**: Epoch parameters inferred from standard BCI epoching practice and the constraint that ready phase (event_6) is only 2s long, making tmax=2s the safe upper bound to capture all phases without exceeding the shortest duration. Severe class imbalance exists: ready (91 events) vs task/interval (~1237 each) vs rest (~327). This task classifies trial phase state in assessment sessions (ses-01, ses-07, ses-13, ses-19) where Schema A is used.

### Potential Task 3: 3-class rest vs ready vs task (Schema A)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 2 s *, target_events = [`event_1`, `event_6`, `event_4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_1` | 0 | rest |
  | `event_6` | 1 | ready |
  | `event_4` | 2 | task |
- **Evidence**:
  - events.tsv (sub-001_ses-01) — Schema A assessment sessions show value 1='rest', value 2='ready', value 3='task' with durations 5s, 2s, 6s respectively; ready phase is 2s duration supporting tmax=2s window
  - events.json — 'value' column defined as 'The code (EEG Marker or Trigger value) associated with an event', 'instruction' column describes task content
- **Notes**: Task discriminates three cognitive-motor states from assessment sessions only (ses-01, ses-07, ses-13, ses-19). event_1 (rest, 327 events), event_6 (ready, 91 events), and event_4 (task, 1237 events) are phase markers not MI class labels, forming a valid state detection task. Imbalanced classes with ready being scarce; excludes event_5 (interval) to focus on progression from rest through preparation to execution. tmin/tmax inferred from classical reference and ready phase duration.

### Potential Task 4: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–27.0 (years) | N=30 subjects; narrow 9-year span may limit predictive signal |
- **Evidence**:
  - participants.tsv — age column complete for all 30 subjects (range 18–27 years)
- **Notes**: Segmentation-based subject-level regression. No event structure needed; fixed 2-second windows with 50% overlap provide multiple samples per recording while preserving frequency resolution at 1000 Hz sampling rate. Age is a native participants.tsv column (B3 archetype, Meta Level = raw).

### Potential Task 5: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | female | 0 | female |
  | gender | male | 1 | male |
- **Evidence**:
  - participants.tsv — N=30 subjects with gender column: 5 female, 25 male (complete, categorical)
- **Notes**: Subject-level trait prediction via fixed-window EEG segmentation. Severe class imbalance (5:25) but technically valid binary classification with ≥2 distinct classes. 2-second windows with 50% overlap are inferred defaults for subject-level classification tasks where no trial structure is needed.

### Potential Task 6: handedness classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | handedness | left | 0 | left-handed |
  | handedness | right | 1 | right-handed |
- **Evidence**:
- **Notes**: Binary classification of subject handedness from segmented resting/task EEG. Extremely imbalanced dataset (1 left-handed vs 29 right-handed subjects). The single left-handed subject may be an outlier, making this task likely not learnable in practice. Included per soft guideline favoring inclusion of technically valid tasks. Segmentation parameters inferred from default subject-level classification settings.

### Potential Task 7: Continuous EEG Segmentation with Age Label
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–27.0 (years) | Subject chronological age from participants.tsv; used as continuous regression target for subject trait prediction |
- **Evidence**:
  - participants.tsv — age column complete for N=30 subjects, range 18.0–27.0 years, sample values [22, 23, 24]
- **Notes**: Archetype C (segmentation + info-native). Uses fixed-length 2-second non-overlapping windows (50% overlap) from continuous EEG without event locking, paired with subject age as regression target. Suitable for self-supervised pretraining or contrastive learning with age as downstream biomarker. Meta Level is raw because age is a native participants.tsv column requiring no kernel computation.

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
> **Status**: wait_kernel_update
