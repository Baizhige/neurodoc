# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2017/2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz | **Manual Review**: Chengxuan Qin

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale developmental EEG battery collected from children and adolescents. This release includes six paradigms: naturalistic movie watching, resting state with alternating eyes-open and eyes-closed periods, contrast change detection, surround suppression, sequence learning, and symbol search. For the current benchmark draft, we keep only the tasks that have strong grounding in the release documentation and can be implemented directly from native events or narrowly defined kernel derivations.

## File Scan Result

> **Kernel SHA256**: `f6ba47d7656d84e5080b68cbd7441e4d0d62823f934c16c417d30ecfafd68901`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `9999` | 1136 | admin | raw | Administrative recording/session marker |
| `boundary` | 728 | admin | raw | EEGLAB/BIDS boundary or discontinuity marker, not a stimulus class |
| `break cnt` | 1488 | admin | raw | Administrative break counter marker, often at recording onset |
| `contrastChangeB1_start` | 102 | event | raw | Start of contrast change detection block/run 1 |
| `contrastChangeB2_start` | 117 | event | raw | Start of contrast change detection block/run 2 |
| `contrastChangeB3_start` | 143 | event | raw | Start of contrast change detection block/run 3 |
| `contrastTrial_start` | 8884 | event | raw | Start of a single contrast change detection trial |
| `contrast_response_correct` | 6588 | event | super | Button response was correct for the preceding contrast target |
| `contrast_response_incorrect` | 731 | event | super | Button response was incorrect for the preceding contrast target |
| `dot_no1_OFF` | 600 | event | raw | Dot position 1 offset in sequence learning |
| `dot_no1_ON` | 600 | event | raw | Dot position 1 onset in sequence learning |
| `dot_no2_OFF` | 1202 | event | raw | Dot position 2 offset in sequence learning |
| `dot_no2_ON` | 1234 | event | raw | Dot position 2 onset in sequence learning |
| `dot_no3_OFF` | 600 | event | raw | Dot position 3 offset in sequence learning |
| `dot_no3_ON` | 624 | event | raw | Dot position 3 onset in sequence learning |
| `dot_no4_OFF` | 600 | event | raw | Dot position 4 offset in sequence learning |
| `dot_no4_ON` | 600 | event | raw | Dot position 4 onset in sequence learning |
| `dot_no5_OFF` | 600 | event | raw | Dot position 5 offset in sequence learning |
| `dot_no5_ON` | 600 | event | raw | Dot position 5 onset in sequence learning |
| `dot_no6_OFF` | 600 | event | raw | Dot position 6 offset in sequence learning |
| `dot_no6_ON` | 600 | event | raw | Dot position 6 onset in sequence learning |
| `dot_no7_OFF` | 793 | event | raw | Dot position 7 offset in sequence learning |
| `dot_no7_ON` | 792 | event | raw | Dot position 7 onset in sequence learning |
| `dot_no8_OFF` | 396 | event | raw | Dot position 8 offset in sequence learning |
| `dot_no8_ON` | 396 | event | raw | Dot position 8 onset in sequence learning |
| `fixpoint_ON` | 13248 | event | raw | Fixation point onset in the surround suppression task |
| `instructed_toCloseEyes` | 680 | event | raw | Auditory instruction to close eyes during resting state |
| `instructed_toOpenEyes` | 816 | event | raw | Auditory instruction to open eyes during resting state |
| `learningBlock_1` | 122 | event | raw | Start of sequence learning block 1 |
| `learningBlock_2` | 121 | event | raw | Start of sequence learning block 2 |
| `learningBlock_3` | 120 | event | raw | Start of sequence learning block 3 |
| `learningBlock_4` | 119 | event | raw | Start of sequence learning block 4 |
| `learningBlock_5` | 118 | event | raw | Start of sequence learning block 5 |
| `left_buttonPress` | 5095 | event | raw | Left mouse button press response in contrast change detection |
| `left_target` | 4243 | event | raw | Left-tilted contrast target presentation |
| `newPage` | 194 | event | raw | New symbol search page or query set presented |
| `resting_start` | 139 | event | raw | Start of resting-state recording |
| `right_buttonPress` | 4634 | event | raw | Right mouse button press response in contrast change detection |
| `right_target` | 4251 | event | raw | Right-tilted contrast target presentation |
| `seqLearning_start` | 122 | event | raw | Sequence learning task start |
| `seqLearning_stop` | 118 | event | raw | Sequence learning task stop |
| `stim_ON` | 13278 | event | raw | Surround suppression visual stimulus onset |
| `surroundSuppB1_start` | 108 | event | raw | Start of surround suppression block/run 1 |
| `surroundSuppB2_start` | 99 | event | raw | Start of surround suppression block/run 2 |
| `symbolSearch_start` | 76 | event | raw | Symbol search task start |
| `trialResponse` | 1247 | event | raw | Participant response in the symbol search task |
| `video_start` | 761 | event | raw | Movie stimulus presentation start |
| `video_stop` | 723 | event | raw | Movie stimulus presentation stop |


### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `response_time` | derived (kernel) | super | Seconds from contrast target onset to the first valid button press within the same trial; filled from target onset through the matched response and NaN elsewhere |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `DespicableMe` | complete | Availability flag for the Despicable Me movie watching recording |
| `DiaryOfAWimpyKid` | complete | Availability flag for the Diary of a Wimpy Kid movie watching recording |
| `FunwithFractals` | complete | Availability flag for the Fun with Fractals movie watching recording |
| `RestingState` | complete | Availability flag for the resting-state recording |
| `ThePresent` | complete | Availability flag for The Present movie watching recording |
| `age` | complete | Participant age in years |
| `attention` | partial (1304/1342) | CBCL-derived attention dimension score |
| `commercial_use` | complete | Participant consent flag for commercial use |
| `contrastChangeDetection_1` | complete | Availability/QC flag for contrast change detection run 1 |
| `contrastChangeDetection_2` | complete | Availability/QC flag for contrast change detection run 2 |
| `contrastChangeDetection_3` | complete | Availability/QC flag for contrast change detection run 3 |
| `dataset` | complete | Kernel-added dataset identifier |
| `dataset_root` | complete | Kernel-added absolute raw dataset root used for the scan |
| `device` | complete | Hardware label combined from EEG sidecar manufacturer and model fields |
| `eeg_reference` | complete | EEG reference from the EEG sidecar |
| `ehq_total` | partial (1325/1342) | Edinburgh Handedness Questionnaire total score; positive is more right-handed and negative is more left-handed |
| `externalizing` | partial (1304/1342) | CBCL-derived externalizing symptom dimension score |
| `full_pheno` | complete | Flag indicating whether a full phenotypic file is available |
| `internalizing` | partial (1304/1342) | CBCL-derived internalizing symptom dimension score |
| `manufacturer` | complete | EEG sidecar manufacturer field |
| `manufacturers_model_name` | complete | EEG sidecar amplifier/cap model field |
| `p_factor` | partial (1304/1342) | Participant-level general psychopathology factor score |
| `power_line_frequency` | complete | Power-line frequency in Hz from the EEG sidecar |
| `recording_type` | complete | BIDS recording type from the EEG sidecar |
| `release_number` | complete | HBN EEG release identifier |
| `run` | partial (500/1342) | BIDS run entity; blank for tasks without an explicit run index |
| `sampling_frequency` | complete | EEG sampling frequency in Hz from the EEG sidecar |
| `seqLearning6target` | complete | Availability flag for the 6-target sequence learning variant |
| `seqLearning8target` | complete | Availability flag for the 8-target sequence learning variant |
| `sex` | complete | Participant sex code from participants.tsv |
| `subject_id` | complete | BIDS participant identifier |
| `surroundSupp_1` | complete | Availability/QC flag for surround suppression run 1 |
| `surroundSupp_2` | complete | Availability/QC flag for surround suppression run 2 |
| `symbolSearch` | complete | Availability/QC flag for the symbol search recording |
| `task` | complete | BIDS task entity parsed from the file name |


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
