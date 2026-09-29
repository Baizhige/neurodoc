# Covert Attention in a Sustained Attention Task

**Dataset**: `openneuro_ds002034` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: High-level Mental | **Subjects**: 14 | **Files (Completed)**: 84 | **Channels**: 64 | **Sampling Rate**: 5000 Hz | **Manual Review**:

## Paradigm

This dataset investigates covert spatial attention using a sustained attention task with lateralized visual cues. Fourteen healthy young adults (21-27 years, 7 male/7 female) performed cued attention tasks while 64-channel EEG was recorded at 5000 Hz. Each trial began with a 1-2 second fixation period, followed by a 100 ms cue indicating the likely target location (left, right, or center), then a 1-5 second sustained attention period during which subjects maintained covert attention to the cued location. Targets appeared at the cued location on ~80% of trials (valid) or at an uncued lateral location on ~20% of trials (invalid), requiring a button press response. The paradigm enables investigation of alpha lateralization during sustained attention and behavioral consequences of valid/invalid cueing.

## File Scan Result

> **Kernel SHA256**: `d908a3f6ed42add853145878a7bdd9f1d39451a8ab99d9a36c24a015a8138a42`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `event_1` | 16179 | event | raw | Trial phase onset: cue left |
| `event_11` | 3013 | event | raw | Trial phase onset: target left |
| `event_12` | 2248 | event | raw | Trial phase onset: target right |
| `event_13` | 1129 | event | raw | Trial phase onset: target center |
| `event_15` | 938 | event | raw | Button press correct |
| `event_2` | 5020 | event | raw | Trial phase onset: cue right |
| `event_4` | 5020 | admin | raw | Run start |
| `event_5` | 9333 | admin | raw | Run end |
| `event_6` | 6720 | event | raw | Trial phase onset: trial start |
| `event_8` | 1711 | event | raw | Trial phase onset: trial start |
| `event_9` | 4995 | event | raw | Trial phase onset: fixation on |

### Info

| Field | Completeness | Notes |
|---|---|---|

## Tasks

### Classical Task 1: 2-class covert attention direction (cue left vs cue right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 5.0 s *, target_events = [`event_1`, `event_2`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_1 | 0 | cue left |
  | event_2 | 1 | cue right |
- **Evidence**:
  - 10.1007/s10548-019-00725-9 — Primary task from Schneider et al. (2019): binary classification of left vs right covert attention based on cue onset. 14 subjects, offline runs with 80 trials each. Cue duration 100ms followed by 1-5s sustained attention period.
- **Notes**: The two classes are cue left (event_1) and cue right (event_2). Central cue (event_3) excluded for pure lateral attention task. Epoch window from -0.2s to 5.0s captures pre-cue baseline and the full sustained attention period (1-5s after cue onset).

### Classical Task 2: 2-class target location (target left vs target right)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.5 s *, tmax = 2.0 s *, target_events = [`event_11`, `event_12`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_11` | 0 | target left |
  | `event_12` | 1 | target right |
- **Evidence**:
  - Schneider, C., Pereira, M., Tonin, L. et al. (2019) — https://doi.org/10.1007/s10548-019-00725-9 — Target appearance provides classification task: target left (event_11) vs target right (event_12). Targets appear at cued location on valid trials (~80%) or uncued location on invalid trials (~20%). Target onset follows the 1-5s sustained attention period, providing a later temporal anchor than cue onset.
  - sub-01_ses-01_task-offline_run-01_events.json — event_value levels confirm x11='target left', x12='target right'
  - sub-01_ses-01_task-offline_run-01_events.tsv — sample trigger sequence shows event_value 12 (target_right) following cue_right, and event_value 15 (reaction_correct) confirming behavioral response to target
- **Notes**: Epoch window -0.5 to 2.0s captures pre-target attention state and post-target processing including reaction time period (~400ms). Both event_11 and event_12 are confirmed trial phase onset markers for target appearance, making this a valid event-route classification task distinct from the cue-based task (which uses event_1/event_2).

### Classical Task 3: Valid vs Invalid Cue-Target Trial Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 5.0 s *, target_events = [`event_1`, `event_2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_1 | 0 | cue left → target left (valid trial) |
  | event_1 | 0 | cue left → target right (invalid trial) |
  | event_2 | 1 | cue right → target right (valid trial) |
  | event_2 | 1 | cue right → target left (invalid trial) |
- **Evidence**:
  - 10.1007/s10548-019-00725-9 — Paper explicitly analyzes valid vs invalid trials as behavioral outcome measure; valid trials have target at cued location, invalid trials have target at uncued location
- **Notes**: This task requires trial-level parsing of event sequences: after a cue event (event_1 or event_2), the subsequent target event (event_11 or event_12) determines validity. For cue left (event_1): target left (event_11) = valid (y=0), target right (event_12) = invalid (y=0). For cue right (event_2): target right (event_12) = valid (y=1), target left (event_11) = invalid (y=1). Center cues (event_3) and center targets (event_13) are excluded as they do not map to valid/invalid lateralized attention. The kernel must match cue-target pairs within a trial window and assign the validity label based on spatial congruency. Epochs are locked to cue onset to enable prediction of subsequent trial validity from early neural activity (alpha lateralization during sustained attention period).

### Potential Task 1: 2-class trial phase (fixation vs sustained attention)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 2 s *, target_events = [`event_6`, `event_9`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_9` | 0 | fixation_on (fixation period) |
  | `event_6` | 1 | trial_start (sustained attention period) |
- **Evidence**:
  - events.json — event_value 9 defined as "trial start" in JSON, but event_name column confirms "fixation_on"; values 6,7,8 all redundantly defined as "trial start" in JSON with event_name confirming trial start semantics
  - events.tsv samples — fixation_on (value 9) appears before cue onset; trial_start (value 6) appears at cue onset marking sustained attention phase
  - README — describes trial structure: 1-2s fixation period followed by 100ms cue, then 1-5s sustained attention period
- **Notes**: Values 7 and 8 are also "trial start" per JSON but event_6 is selected as representative trial start marker. The 2s window captures comparable epochs from both the pre-cue fixation period (event_9) and the post-cue sustained attention period (event_6). This creates a task-vs-rest-like discrimination within the trial structure, distinguishing preparatory fixation state from active sustained attention state.

### Potential Task 2: Age Prediction from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | age | Continuous age in years (21–27, mean 23±1.52). Each segment inherits the subject's age value from participants.tsv. |
- **Evidence**:
  - Schneider et al. (2019) — participants.tsv contains age values for all 14 subjects (21–27 years, mean 23±1.52)
- **Notes**: Subject-level biomarker regression using native info field 'age' from participants.tsv. Segmentation-based epoching with 2-second non-overlapping windows (50% overlap) is used since no event structure is required for this subject-level prediction task. The small age range (6 years) and limited sample size (N=14) make this a challenging prediction problem; results should be interpreted with caution.

### Potential Task 3: Sex Prediction from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | 0=M (male), 1=F (female); balanced binary: 7 M / 7 F |
- **Evidence**:
- **Notes**: Subject-level biomarker task. Native info field `sex` from participants.tsv provides per-subject binary labels. EEG is segmented into 2-second non-overlapping windows (with 50% overlap) to create multiple samples per subject for classification. All segments from a given subject share the same sex label. This is a B3 archetype using native pre-existing info column, hence Meta Level = raw.

### Potential Task 4: Segmentation-based Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | 0 = 'F' (female), 1 = 'M' (male); subject-level label applied to all segments from that participant |
- **Evidence**:
- **Notes**: Archetype C with info-native label. Continuous EEG is segmented into 2-second windows with 50% overlap. Each segment inherits the subject's sex from participants.tsv as its class label. This creates a subject-level classification task from continuous data without event locking. The kernel must read participants.tsv and broadcast the sex value to all segments belonging to each subject.

### Potential Task 5: Segmentation-based Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|---------------|
  | `age` | Continuous age in years (range ~21–27); each segment inherits the subject's age for subject-level biomarker regression. |
- **Evidence**:
  - (none — potential task)
- **Notes**: Archetype C segmentation formulation of age regression. Uses 2-second non-overlapping/overlapping segments (50% overlap) to create multiple samples per subject, all labeled with the same subject age from participants.tsv. Contrasts with event-locked B3 formulation by removing event-dependency entirely, enabling comparison of segment-based vs. event-based approaches for subject-level biomarker prediction. No kernel derivation needed — age is a native participants.tsv column.

## Data Quality Notes

- Extremely high sampling rate (5000 Hz) may require downsampling for practical processing; verify if this is native or upsampled.
- Large discrepancy in event counts: event_1 (cue left, n=16179) vs event_2 (cue right, n=5020) suggests possible data aggregation issue or multiple runs/sessions with imbalanced cue presentations — event counts should be roughly balanced per subject.
- Event_1 count (16179) is more than 3× event_2 count (5020), which is inconsistent with the described 80-trial runs with balanced cue types; this may indicate duplicate event entries or merged files.
- Multiple redundant trial start markers (event_6, event_7, event_8) with overlapping semantics require careful validation to avoid epoching errors.
- Event_8 (trial start, n=1711) appears to be a subset/variant of event_6 (trial start, n=6720); clarify whether these represent different task conditions or recording anomalies.
- Missing event_3 (center cue) and event_7 from event table despite being referenced in task definitions and JSON metadata.
- Button press correct events (event_15, n=938) are substantially fewer than target events (event_11+event_12+event_13 = 6390), suggesting many trials lack recorded responses or responses are in a different event code.
- Small sample size (N=14) limits generalizability for all machine learning tasks, especially subject-level biomarker predictions.
- Age range is very narrow (21-27 years, 6-year span), making age regression statistically challenging and likely dominated by noise.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
