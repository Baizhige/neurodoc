# Healthy Brain Network (HBN) EEG - Release 10

**Dataset**: `openneuro_ds005515` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005515
**Category**: Complex Applied | **Subjects**: 533 | **Files (Completed)**: 2515 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The Healthy Brain Network (HBN) EEG Release 10 is a large-scale, multi-task developmental battery collected from children and adolescents. Participants completed naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, symbol search, and sequence learning tasks. The dataset aims to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `b07fb98eb91956901f6040d0f4d6cd21c85c456c0b68c06c05a57e5198d5737f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 2105 | event | raw |  |
| `IBEG` | 4 | event | raw |  |
| `IEND` | 12 | event | raw |  |
| `boundary` | 1385 | event | raw |  |
| `break cnt` | 1451 | event | raw |  |
| `contrastChangeB1_start` | 75 | event | raw |  |
| `contrastChangeB2_start` | 132 | event | raw |  |
| `contrastChangeB3_start` | 91 | event | raw |  |
| `contrastTrial_start` | 5858 | event | raw |  |
| `contrast_response_correct` | 3731 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 493 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 24 | event | raw |  |
| `dot_no1_ON` | 24 | event | raw |  |
| `dot_no2_OFF` | 48 | event | raw |  |
| `dot_no2_ON` | 521 | event | raw |  |
| `dot_no3_OFF` | 24 | event | raw |  |
| `dot_no3_ON` | 474 | event | raw |  |
| `dot_no4_OFF` | 24 | event | raw |  |
| `dot_no4_ON` | 24 | event | raw |  |
| `dot_no5_OFF` | 24 | event | raw |  |
| `dot_no5_ON` | 24 | event | raw |  |
| `dot_no6_OFF` | 24 | event | raw |  |
| `dot_no6_ON` | 24 | event | raw |  |
| `dot_no7_OFF` | 26 | event | raw |  |
| `dot_no7_ON` | 24 | event | raw |  |
| `dot_no8_OFF` | 12 | event | raw |  |
| `dot_no8_ON` | 12 | event | raw |  |
| `fixpoint_ON` | 10562 | event | raw |  |
| `instructed_toCloseEyes` | 2365 | event | raw |  |
| `instructed_toOpenEyes` | 2862 | event | raw |  |
| `learningBlock_1` | 17 | event | raw |  |
| `learningBlock_2` | 4 | event | raw |  |
| `learningBlock_3` | 2 | event | raw |  |
| `learningBlock_4` | 1 | event | raw |  |
| `left_buttonPress` | 3689 | event | raw |  |
| `left_target` | 2545 | event | raw |  |
| `net` | 2 | event | raw |  |
| `newPage` | 188 | event | raw |  |
| `resting_start` | 516 | event | raw |  |
| `right_buttonPress` | 3034 | event | raw |  |
| `right_target` | 2812 | event | raw |  |
| `seqLearning_start` | 18 | event | raw |  |
| `seqLearning_stop` | 9 | event | raw |  |
| `stim_ON` | 10818 | event | raw |  |
| `surroundSuppB1_start` | 98 | event | raw |  |
| `surroundSuppB2_start` | 67 | event | raw |  |
| `symbolSearch_start` | 70 | event | raw |  |
| `trialResponse` | 1211 | event | raw |  |
| `video_start` | 1627 | event | raw |  |
| `video_stop` | 1610 | event | raw |  |

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Latency in seconds from left_target/right_target onset to the first valid left_buttonPress/right_buttonPress in the same contrast trial |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | e.g. available, unavailable, caution |
| `DiaryOfAWimpyKid` | complete | e.g. available, caution, unavailable |
| `FunwithFractals` | complete | e.g. available, unavailable, caution |
| `RestingState` | complete | e.g. available, caution, unavailable |
| `ThePresent` | complete | e.g. unavailable, available, caution |
| `age` | complete | e.g. 7.0599, 13.6389, 7.0018 |
| `attention` | complete | e.g. -0.363, -0.866, -0.434 |
| `commercial_use` | complete | e.g. Yes |
| `contrastChangeDetection_1` | complete | e.g. unavailable, caution, available |
| `contrastChangeDetection_2` | complete | e.g. unavailable, caution, available |
| `contrastChangeDetection_3` | complete | e.g. caution, unavailable, available |
| `dataset` | complete | e.g. openneuro_ds005515 |
| `dataset_root` | complete | e.g. <LOCAL_HOME>/eeg_dataset/openneuro_raw/ds005515 |
| `device` | complete | e.g. Magtism EGI 128-channel GSN 200 v.2.1 |
| `eeg_reference` | complete | e.g. Cz |
| `ehq_total` | complete | e.g. 55.63, 100.05, -86.71 |
| `externalizing` | complete | e.g. -0.05, -0.348, -0.235 |
| `full_pheno` | complete | e.g. No, Yes |
| `internalizing` | complete | e.g. -0.042, -0.373, -1.491 |
| `manufacturer` | complete | e.g. Magtism EGI |
| `manufacturers_model_name` | complete | e.g. 128-channel GSN 200 v.2.1 |
| `p_factor` | complete | e.g. -0.636, -1.681, -0.268 |
| `power_line_frequency` | complete | e.g. 60 |
| `recording_type` | complete | e.g. continuous |
| `release_number` | complete | e.g. R10 |
| `run` | partial (377/2515) | e.g. 1, 2, 3 |
| `sampling_frequency` | complete | e.g. 500 |
| `seqLearning6target` | complete | e.g. unavailable |
| `seqLearning8target` | complete | e.g. unavailable |
| `sex` | complete | e.g. M, F |
| `subject_id` | complete | e.g. sub-NDARAA396TWZ, sub-NDARAA773LUW, sub-NDARAB674LNB |
| `surroundSupp_1` | complete | e.g. caution, unavailable, available |
| `surroundSupp_2` | complete | e.g. unavailable, caution, available |
| `symbolSearch` | complete | e.g. caution, unavailable, available |
| `task` | complete | e.g. DespicableMe, DiaryOfAWimpyKid, FunwithFractals |

## Tasks

### Classical Task 1: resting state eyes-open vs eyes-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 2.0 s, tmax = 20.0 s, overlap = 0.0, target_events = [`instructed_toCloseEyes`, `instructed_toOpenEyes`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `instructed_toOpenEyes` | 0 | Eyes-open resting state |
  | `instructed_toCloseEyes` | 1 | Eyes-closed resting state |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper describes alternating eyes-open and eyes-closed resting-state periods and documents the corresponding instruction events in the release.
- **Notes**: This is a sustained-state classification task. The first 2 seconds after each auditory instruction are skipped to reduce cue-evoked activity, and the 20-second window avoids crossing from the shorter eyes-open periods into the following eyes-closed period.

### Classical Task 2: contrast change target direction
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `left_target` | 0 | Left-leaning target stimulus |
  | `right_target` | 1 | Right-leaning target stimulus |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release documentation explicitly identifies `left_target` and `right_target` as distinct contrast-detection stimulus events.
- **Notes**: This is the cleanest native event classification task in the active contrast paradigm.

### Classical Task 3: contrast response time
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`left_target`, `right_target`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | MISC Channel Name | Y Mapping Notes |
  |---|---|
  | `response_time` | y directly equals the latency in seconds from contrast target onset to the first valid button press in the same trial; no class mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release describes active button-press behavior for the contrast-change paradigm.
  - EEG 2025 Challenge 1 tutorial — The public challenge task for this paradigm uses a derived stimulus-to-response latency target (`rt_from_stimulus`), supporting the same label construction principle.
- **Notes**: The kernel fills this misc channel only between the target onset and the matched button press. Samples outside those per-trial windows remain NaN.

### Classical Task 4: externalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `externalizing` | y directly equals the participant-level externalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The HBN-EEG release paper states that openly available participant information includes externalizing, internalizing, attention, and p-factor dimensions derived from questionnaire modeling.
  - EEG 2025 Challenge website — The current Challenge 2 target is externalizing factor prediction from HBN-EEG recordings.
- **Notes**: This is an info-route participant-level regression task. Windows with missing `externalizing` values should be excluded before training or evaluation.

### Classical Task 5: p-factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `p_factor` | y directly equals the participant-level p-factor score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper explicitly exposes `p_factor` as an openly available participant-level psychopathology dimension.
  - EEGDash Challenge 2 tutorial — Public benchmark materials for the HBN EEG release use `p_factor` as a participant-level prediction target.
- **Notes**: This is an info-route regression task. The current EEG 2025 final challenge target has shifted to `externalizing`, but `p_factor` remains a documented HBN phenotype field and a previously published benchmark target.

### Classical Task 6: sequence learning 6-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
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

### Classical Task 7: sequence learning 8-target stimulus position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
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
  - 10.1101/2024.10.03.615261 — The release paper states that older participants completed an 8-target sequence-learning variant in which each flashed dot position is explicitly encoded by native event IDs.
  - 10.1101/2024.10.03.615261 — The same paper notes that response timestamps for the later recall phase were not recorded, so the grounded task here is stimulus-position decoding, not recall-performance decoding.
- **Notes**: This task captures sequence stimulus-position decoding during repeated observation. It should be restricted to the 8-target variant rather than pooled with the 6-target recordings.

### Potential Task 1: contrast response correctness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.6 s, tmax = 0.4 s, target_events = [`contrast_response_correct`, `contrast_response_incorrect`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `contrast_response_correct` | 0 | Response side matched the preceding contrast target |
  | `contrast_response_incorrect` | 1 | Response side did not match the preceding contrast target |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper describes the contrast-change task as an active discrimination task with button-press responses and feedback.
- **Notes**: The kernel derives these response-locked super events by pairing each `left_target` or `right_target` with the first subsequent `left_buttonPress` or `right_buttonPress` before the next target event. This is physiologically meaningful for response and error monitoring, but it is listed as potential because the current EEG 2025 challenge explicitly does not use correct/incorrect classification.

### Potential Task 2: internalizing factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `internalizing` | y directly equals the participant-level internalizing score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists internalizing as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses internalizing as the primary regression target.

### Potential Task 3: attention factor regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `attention` | y directly equals the participant-level attention score from participants.tsv; no mapping |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — The release paper lists attention as one of the openly available psychopathology dimensions.
- **Notes**: This target is documented and directly available, but it is listed as potential because the current EEG 2025 final challenge no longer uses attention as the primary regression target.

## Data Quality Notes

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: completed
