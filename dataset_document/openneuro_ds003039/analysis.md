# Free Walking Study

**Dataset**: `openneuro_ds003039` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds003039
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 67 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants walked two different outdoor routes while performing a self-paced button-pressing task, with gait events (heel strikes, toe-offs, steps) recorded alongside button-press responses. This is a mobile EEG study capturing brain activity during naturalistic free-walking gait. The experimental design includes multiple conditions: standing still, walking initiation, easy/difficult button-pressing tasks, and 10-fast/10-own pacing conditions.

## File Scan Result

> **Kernel SHA256**: `5c16bd9ef04bfe59190a1721435c3a658b30a981317461472a0299bfde78bc71`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `LeftButtonPress` | 5263 | event | raw | Button press with left thumb |
| `LeftHS` | 16018 | event | raw | Left heel strike (as determined by foot acceleration) |
| `LeftStep` | 4832 | event | raw | Left step (as determined by foot acceleration) during gait initiation condition |
| `LeftTO` | 15632 | event | raw | Left toe-off (as determined by foot acceleration) |
| `MissLeftButtonPress` | 502 | event | raw | Press with left thumb that missed the button, only relevant in button pressing conditions |
| `MissRightButtonPress` | 840 | event | raw | Press with right thumb that missed the button, only relevant in button pressing conditions |
| `Play` | 2049 | event | raw | Button press (experimenter), to switch to next screen/trial |
| `RightButtonPress` | 5459 | event | raw | Button press with right thumb |
| `RightHS` | 16217 | event | raw | Right heel strike (as determined by foot acceleration) |
| `RightStep` | 4716 | event | raw | Right step (as determined by foot acceleration) during gait initiation condition |
| `RightTO` | 16186 | event | raw | Right toe-off (as determined by foot acceleration) |
| `boundary` | 2 | admin | raw | Session or data boundary marker |
| `difficult` | 19 | event | raw | Trial phase onset: difficult condition |
| `easy` | 19 | event | raw | Trial phase onset: easy condition |
| `end_10fast` | 19 | event | raw | Trial phase offset: 10fast condition |
| `end_10own` | 23 | event | raw | Trial phase offset: 10own condition |
| `end_difficult` | 19 | event | raw | Trial phase offset: difficult condition |
| `end_difficult_button` | 19 | event | raw | Trial phase offset: difficult_button condition |
| `end_easy` | 19 | event | raw | Trial phase offset: easy condition |
| `end_easy_button` | 19 | event | raw | Trial phase offset: easy_button condition |
| `end_experiment` | 11 | admin | raw | Trial phase offset: experiment |
| `end_initiation` | 19 | event | raw | Trial phase offset: initiation |
| `end_restEEG` | 19 | event | raw | Trial phase offset: restEEG |
| `end_standing` | 19 | event | raw | Trial phase offset: standing |
| `initiation` | 1881 | event | raw | Start of a gait initiation trial |
| `initiationHeadLeft` | 825 | event | raw | Gait initiation with the left leg (as determined by the head acceleration) |
| `initiationHeadRight` | 1030 | event | raw | Gait initiation with the right leg (as determined by the head acceleration) |
| `initiationLeft` | 825 | event | raw | Gait initiation with the left leg (as determined by the foot acceleration), more accurate than initiation determined by head acceleration |
| `initiationRight` | 1031 | event | raw | Gait initiation with the right leg (as determined by the foot acceleration), more accurate than initiation determined by head acceleration |
| `instruct_10fast` | 19 | event | raw | Trial phase onset: instructions for 10fast condition |
| `instruct_10own` | 23 | event | raw | Trial phase onset: instructions for 10own condition |
| `instruct_difficult` | 19 | event | raw | Trial phase onset: instructions for difficult condition |
| `instruct_difficult_button` | 19 | event | raw | Trial phase onset: instructions for difficult_button condition |
| `instruct_easy` | 19 | event | raw | Trial phase onset: instructions for easy condition |
| `instruct_easy_button` | 19 | event | raw | Trial phase onset: instructions for easy_button condition |
| `instruct_restEEG` | 19 | event | raw | Trial phase onset: instructions for restEEG condition |
| `instruct_standing` | 19 | event | raw | Trial phase onset: instructions for standing condition |
| `standingStill` | 1856 | event | raw | Trial phase marker: standing still |
| `start_10fast` | 19 | event | raw | Trial phase onset: 10fast condition |
| `start_10own` | 23 | event | raw | Trial phase onset: 10own condition |
| `start_difficult` | 19 | event | raw | Trial phase onset: difficult condition |
| `start_difficult_button` | 19 | event | raw | Trial phase onset: difficult_button condition |
| `start_easy` | 19 | event | raw | Trial phase onset: easy condition |
| `start_easy_button` | 19 | event | raw | Trial phase onset: easy_button condition |
| `start_experiment` | 19 | admin | raw | Trial phase onset: experiment start |
| `start_initiation` | 19 | event | raw | Trial phase onset: initiation |
| `start_pause` | 38 | event | raw | Trial phase onset: pause |
| `start_restEEG` | 19 | event | raw | Trial phase onset: restEEG condition |
| `start_standing` | 19 | event | raw | Trial phase onset: standing condition |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `x_dir` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `y_dir` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `z_dir` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `x_dir` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
| `y_dir` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
| `z_dir` | derived (per Task Notes) | super | Super Meta — kernel derives per-segmentation value |
- **Candidate Labels**: `x_dir`, `y_dir`, `z_dir`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Button Press vs Missed Button Press
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`LeftButtonPress`, `RightButtonPress`, `MissLeftButtonPress`, `MissRightButtonPress`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | LeftButtonPress | 0 | Successful left thumb button press |
  | RightButtonPress | 0 | Successful right thumb button press |
  | MissLeftButtonPress | 1 | Missed left thumb button press |
  | MissRightButtonPress | 1 | Missed right thumb button press |
- **Evidence**:
  - 10.1111/ejn.14965 — ERP analysis of button presses during dual-task walking; distinguishes successful and missed button presses
  - 10.3389/fspor.2022.945341 — Explicit ERP analysis of button-press responses in gait-related mobile EEG study
- **Notes**: Two-class classification merging left/right by outcome (success vs miss). Left and right successful presses are pooled as y=0; left and right missed presses are pooled as y=1. This yields a motor response detection task (successful execution vs error/missed response) that is well-powered with 10,722 success trials vs 1,342 miss trials. The epoch window (-0.2 to 0.8s) captures the readiness potential preceding the press and the P300/error-related negativity following the response.

### Classical Task 2: Walking Condition Classification (Easy vs Difficult)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, overlap = 0.5 *, target_events = [`start_easy`, `start_difficult`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `start_easy` | 0 | Easy button-pressing condition onset |
  | `start_difficult` | 1 | Difficult button-pressing condition onset |
- **Evidence**:
  - 10.1111/ejn.14965 — Jacobsen et al. (2020) characterizes gait-related artifacts in mobile EEG during free walking with easy vs difficult button-pressing conditions
  - 10.3389/fspor.2022.945341 — Follow-up analysis explicitly comparing easy vs difficult cognitive load conditions during walking
- **Notes**: Long-event epoching with 4s segments and 50% overlap for sustained cognitive load classification. tmax inferred from segment_length hint (4s) since condition blocks are self-paced outdoor walking without fixed duration; tmin=0 anchors at condition onset. The `easy` and `difficult` markers (also 19 occurrences each) are alternative phase onsets that could be used, but `start_easy`/`start_difficult` provide cleaner block boundaries with corresponding `end_easy`/`end_difficult` markers. Only start markers are used as target events to avoid label ambiguity within blocks.

### Classical Task 3: Single-Task vs Dual-Task Walking Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, overlap = 0.5 *, target_events = [`start_easy`, `start_difficult`, `start_easy_button`, `start_difficult_button`, `standingStill`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `start_easy` | 0 | single-task walking (easy pace, no button pressing) |
  | `start_difficult` | 0 | single-task walking (difficult pace, no button pressing) |
  | `start_easy_button` | 1 | dual-task walking (easy pace + button pressing) |
  | `start_difficult_button` | 1 | dual-task walking (difficult pace + button pressing) |
  | `standingStill` | 2 | standing still (baseline/no walking) |
- **Evidence**:
  - 10.3389/fspor.2022.945341 — The 2022 Frontiers paper explicitly tests single-task (walking only) vs dual-task (walking + button pressing) conditions, using markers for start_easy/start_difficult vs start_easy_button/start_difficult_button and standingStill as a baseline condition.
- **Notes**: The epoch parameters are inferred from the candidate's epoch_hint (tmin=0, segment_length=4s with 0.5 overlap). Since epoch_by_long_event_hdf5 requires tmax rather than segment_length, tmax is set to 4s to match the segment_length hint. All three conditions (single-task, dual-task, standing) are merged into a 3-class problem: y=0 for all non-button walking (easy+difficult), y=1 for button-press walking (dual-task), and y=2 for standing still baseline. The `standingStill` event (1856 occurrences) provides substantial baseline data. The start_* events mark the onset of sustained walking blocks, making them suitable anchors for long-event epoching with 4-second segments.

### Potential Task 1: Pacing Condition Classification (10fast vs 10own)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, overlap = 0.5 *, target_events = [`start_10fast`, `end_10fast`, `start_10own`, `end_10own`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | start_10fast | 0 | fast-paced walking condition onset |
  | end_10fast | 0 | fast-paced walking condition offset (same class) |
  | start_10own | 1 | self-paced walking condition onset |
  | end_10own | 1 | self-paced walking condition offset (same class) |
- **Evidence**:
- **Notes**: Uses long-event epoching with 4-second segments and 50% overlap to capture sustained neural states during continuous walking conditions. The start_* and end_* events for each condition are mapped to the same class label (y=0 for 10fast, y=1 for 10own) to enable condition-level classification from overlapping segments within each trial block. tmax inferred as 4 s based on segment_length from epoch_hint; actual condition durations vary and are bounded by paired start/end events.

### Potential Task 2: Direction Channel Regression (x_dir)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `x_dir`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | x_dir | continuous (a.u.) | Horizontal movement direction component; native continuous misc channel from mobile EEG during free walking |
- **Evidence**:
  - eeg.json — MiscChannelCount: 3 confirms presence of misc channels including x_dir
  - channels.tsv (inferred from header) — x_dir listed as native misc channel alongside y_dir, z_dir
  - dataset_description.json — "free walking study" with mobile EEG recordings; Jacobsen et al. (2020) characterizes gait-related artifacts in mobile EEG
- **Notes**: Native misc channel x_dir is directly available on the raw object (archetype B1). No kernel derivation needed. The 2s segment length with 50% overlap is inferred from standard practice for continuous decoding from mobile EEG during locomotion. The x_dir channel likely represents horizontal head/body orientation or movement direction during free walking, forming a continuous regression target for predicting directional movement from EEG. **Super Meta**: Derived from native MISC channel `x_dir` — kernel must read per-sample values from the raw object and use as continuous regression target.

### Potential Task 3: Direction Channel Regression (y_dir)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `y_dir`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | y_dir | continuous | Vertical/anterior-posterior movement direction component from head-mounted IMU; regression target for movement direction prediction |
- **Evidence**:
  - eeg.json — MiscChannelCount=3 confirms three auxiliary channels present (x_dir, y_dir, z_dir)
  - EEG File Header Sample — 67 total channels includes 64 EEG + 3 misc channels
  - evidence_summary — Native continuous y_dir channel available for vertical/anterior-posterior direction regression
- **Notes**: Native B1 archetype using pre-existing misc channel y_dir from head-mounted IMU. No kernel derivation needed; channel is directly available on the raw object. Segmentation approach (2s windows, 50% overlap) chosen for continuous regression target without event-locked structure. **Super Meta**: Derived from native MISC channel `y_dir` — kernel must read per-sample values from the raw object and use as continuous regression target.

### Potential Task 4: Direction Channel Regression (z_dir)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `misc`
- **Label Field**: `z_dir`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel | Value (unit) | Notes |
  |--------------|--------------|-------|
  | z_dir | continuous (a.u.) | Vertical/gravity-aligned movement direction component; third axis of 3D directional sensing from motion sensors. May capture trunk/head vertical oscillation during gait. |
- **Evidence**:
- **Notes**: Native continuous misc channel z_dir available on the raw EEG object as one of three directional channels (x_dir, y_dir, z_dir). This is a B1 archetype task using native misc channel regression with segmentation-based epochs. The 2-second window with 50% overlap follows the same segmentation pattern used for other direction channels in this dataset. Values are inferred from the candidate's epoch_hint. **Super Meta**: Derived from native MISC channel `z_dir` — kernel must read per-sample values from the raw object and use as continuous regression target.

### Potential Task 5: age regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19–32 (years) | Subject-level continuous age from participants.tsv; N=19 complete |
- **Evidence**:
- **Notes**: Brain-age prediction using continuous 10-second EEG segments with 50% overlap. No event-locked structure required since this is a subject-level regression task. The age values are continuous numeric (19–32 years) from the native participants.tsv info field. Segmentation approach maximizes usable data volume per subject for regression model training. **Super Meta**: Derived from subject metadata field `age` — kernel must load per-subject label from participants.tsv and broadcast to all segments.

### Potential Task 6: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | F | 0 | Female |
  | gender | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level binary classification using 10-second non-overlapping segments with 50% overlap. Classes are imbalanced (13 Female, 6 Male). Since no task events discriminate gender, segmentation is used to create samples from continuous EEG, with labels drawn from participants.tsv. The kernel must read the `gender` column from participants.tsv and broadcast it to all segments belonging to that subject. **Super Meta**: Derived from subject metadata field `gender` — kernel must load per-subject label from participants.tsv and broadcast to all segments.

### Potential Task 7: Continuous Walking Segmentation with Gender Labels
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.75 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | F | 0 | Female participant |
  | gender | M | 1 | Male participant |
- **Evidence**:
- **Notes**: Archetype C with native info column. The entire continuous walking recording is segmented into 4-second windows with 75% overlap; each segment inherits the subject's gender label from participants.tsv. This tests whether gait-related EEG spectral features can distinguish female vs male participants without any event-locked structure. **Super Meta**: Derived from subject metadata field `gender` — kernel must load per-subject label from participants.tsv and broadcast to all segments.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
