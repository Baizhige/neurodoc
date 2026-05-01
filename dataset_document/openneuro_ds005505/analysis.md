# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale developmental EEG battery collected from children and adolescents. This release includes six paradigms: naturalistic movie watching, resting state with alternating eyes-open and eyes-closed periods, contrast change detection, surround suppression, sequence learning, and symbol search. For the current benchmark draft, we keep only the tasks that have strong grounding in the release documentation and can be implemented directly from native events or narrowly defined kernel derivations.

## File Scan Result

> **Kernel SHA256**: `f6ba47d7656d84e5080b68cbd7441e4d0d62823f934c16c417d30ecfafd68901`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1136 | event | raw |  |
| `boundary` | 728 | event | raw |  |
| `break cnt` | 1488 | event | raw |  |
| `contrastChangeB1_start` | 102 | event | raw |  |
| `contrastChangeB2_start` | 117 | event | raw |  |
| `contrastChangeB3_start` | 143 | event | raw |  |
| `contrastTrial_start` | 8884 | event | raw |  |
| `contrast_response_correct` | 6588 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 731 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 600 | event | raw |  |
| `dot_no1_ON` | 600 | event | raw |  |
| `dot_no2_OFF` | 1202 | event | raw |  |
| `dot_no2_ON` | 1234 | event | raw |  |
| `dot_no3_OFF` | 600 | event | raw |  |
| `dot_no3_ON` | 624 | event | raw |  |
| `dot_no4_OFF` | 600 | event | raw |  |
| `dot_no4_ON` | 600 | event | raw |  |
| `dot_no5_OFF` | 600 | event | raw |  |
| `dot_no5_ON` | 600 | event | raw |  |
| `dot_no6_OFF` | 600 | event | raw |  |
| `dot_no6_ON` | 600 | event | raw |  |
| `dot_no7_OFF` | 793 | event | raw |  |
| `dot_no7_ON` | 792 | event | raw |  |
| `dot_no8_OFF` | 396 | event | raw |  |
| `dot_no8_ON` | 396 | event | raw |  |
| `fixpoint_ON` | 13248 | event | raw |  |
| `instructed_toCloseEyes` | 680 | event | raw |  |
| `instructed_toOpenEyes` | 816 | event | raw |  |
| `learningBlock_1` | 122 | event | raw |  |
| `learningBlock_2` | 121 | event | raw |  |
| `learningBlock_3` | 120 | event | raw |  |
| `learningBlock_4` | 119 | event | raw |  |
| `learningBlock_5` | 118 | event | raw |  |
| `left_buttonPress` | 5095 | event | raw |  |
| `left_target` | 4243 | event | raw |  |
| `newPage` | 194 | event | raw |  |
| `resting_start` | 139 | event | raw |  |
| `right_buttonPress` | 4634 | event | raw |  |
| `right_target` | 4251 | event | raw |  |
| `seqLearning_start` | 122 | event | raw |  |
| `seqLearning_stop` | 118 | event | raw |  |
| `stim_ON` | 13278 | event | raw |  |
| `surroundSuppB1_start` | 108 | event | raw |  |
| `surroundSuppB2_start` | 99 | event | raw |  |
| `symbolSearch_start` | 76 | event | raw |  |
| `trialResponse` | 1247 | event | raw |  |
| `video_start` | 761 | event | raw |  |
| `video_stop` | 723 | event | raw |  |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | complete | N/A |
| `DespicableMe` | complete | e.g. available, unavailable |
| `DiaryOfAWimpyKid` | complete | e.g. available, unavailable |
| `FunwithFractals` | complete | e.g. available, unavailable |
| `RestingState` | complete | e.g. available |
| `ThePresent` | complete | e.g. available, unavailable |
| `attention` | partial (1304/1342) | e.g. -0.446, -0.425, -0.119 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_2` | complete | e.g. available, unavailable, caution |
| `contrastChangeDetection_3` | complete | e.g. available, unavailable, caution |
| `dataset` | complete | e.g. openneuro_ds005505 |
| `dataset_root` | complete | e.g. <LOCAL_HOME>/eeg_dataset/openneuro_raw/ds005505 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | partial (1325/1342) | e.g. 71.17, 100.05, -53.36 |
| `externalizing` | partial (1304/1342) | e.g. 0.325, 0.509, 0.366 |
| `full_pheno` | complete | e.g. Yes, No |
| `internalizing` | partial (1304/1342) | e.g. 1.248, 1.006, 0.222 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | partial (1304/1342) | e.g. -0.603, -0.258, 0.062 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R1 |
| `run` | partial (500/1342) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable, available |
| `seqLearning8target` | complete | e.g. available, unavailable |
| `subject_id` | complete | e.g. sub-NDARAC904DMU, sub-NDARAG143ARJ, sub-NDARAM704GKZ |
| `surroundSupp_1` | complete | e.g. available, unavailable |
| `surroundSupp_2` | complete | e.g. available, unavailable |
| `symbolSearch` | complete | e.g. available, caution, unavailable |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0.0 s *, tmax = 30.0 s *, overlap = 0.0, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The long-event window is intended to capture stable resting-state activity rather than transient cue responses.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`left_target`, `right_target`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.6 s *, tmax = 0.4 s *, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]`
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper describes the contrast-change task as an active discrimination task with button-press responses, making response correctness a grounded derived target when paired to the target side.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event.

### Classical Task 4: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`left_target`, `right_target`]`
- **Label Route**: `misc`
- **Label Field**: `response_time`
- **Meta Level**: super
- **Target Definition**:
  | Misc Channel | Value | Notes |
  |---|---|---|
  | `response_time` | continuous (s) | Latency from target onset to the first subsequent button press in the same contrast trial |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial - The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 5: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that younger participants completed a 6-target variant of the sequence-learning paradigm.
- **Notes**: This task should be restricted to recordings or participants belonging to the 6-target variant, using dataset evidence such as `seqLearning6target` and the absence of `dot_no7_ON` and `dot_no8_ON`.

### Classical Task 6: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `dot_no1_ON` | 0 | Dot position 1 onset |
  | `dot_no2_ON` | 1 | Dot position 2 onset |
  | `dot_no3_ON` | 2 | Dot position 3 onset |
  | `dot_no4_ON` | 3 | Dot position 4 onset |
  | `dot_no5_ON` | 4 | Dot position 5 onset |
  | `dot_no6_ON` | 5 | Dot position 6 onset |
  | `dot_no7_ON` | 6 | Dot position 7 onset |
  | `dot_no8_ON` | 7 | Dot position 8 onset |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Classical Task 7: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4.0 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `p_factor`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range | Notes |
  |---|---|---|
  | `p_factor` | continuous (z-score-like unitless score) | Participant-level general psychopathology factor derived from HBN questionnaire modeling |
- **Evidence**:
  - `10.1101/2024.10.03.615261` - The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEG 2025 Challenge 2 tutorial - Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. No extra kernel-derived misc channel is needed because the target is already a participant-level field.

## Data Quality Notes

- The current raw-event counts come from the last completed scan, but the newly added super events and the `response_time` misc channel still require a fresh full scan to populate final counts and to refresh the MISC summary directly from the updated kernel.
- `contrast_response_correct` and `contrast_response_incorrect` are intentionally listed as pending rescan because they are kernel-derived events, not native BIDS events.
- The symbol-search correctness task is intentionally left out of this benchmark draft until the correctness grounding for each `trialResponse` is re-verified on Release 1.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
