# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**:

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale, multi-task developmental battery collected from children and adolescents (ages 5.2–21.7). Participants completed six experimental paradigms: naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. EEG data were acquired using a 129-channel system at 500 Hz, with the dataset designed to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `4d9bd95acb0c7cca80d220585ce65a6fa7307d06e907c5ac4ec9fdf90394e96f`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 1136 | admin | raw | Recording onset marker (system sync) |
| `boundary` | 728 | admin | raw | Data boundary marker (continuous recording segment separator) |
| `break cnt` | 1488 | admin | raw | Break period marker (inter-trial/inter-block interval) |
| `contrastChangeB1_start` | 102 | event | raw | Contrast change detection block 1 onset |
| `contrastChangeB2_start` | 117 | event | raw | Contrast change detection block 2 onset |
| `contrastChangeB3_start` | 143 | event | raw | Contrast change detection block 3 onset |
| `contrastTrial_start` | 8884 | event | raw | Contrast change trial onset |
| `dot_no1_OFF` | 600 | event | raw | Sequence learning dot 1 illumination offset |
| `dot_no1_ON` | 600 | event | raw | Sequence learning dot 1 illumination onset |
| `dot_no2_OFF` | 1202 | event | raw | Sequence learning dot 2 illumination offset |
| `dot_no2_ON` | 1234 | event | raw | Sequence learning dot 2 illumination onset |
| `dot_no3_OFF` | 600 | event | raw | Sequence learning dot 3 illumination offset |
| `dot_no3_ON` | 624 | event | raw | Sequence learning dot 3 illumination onset |
| `dot_no4_OFF` | 600 | event | raw | Sequence learning dot 4 illumination offset |
| `dot_no4_ON` | 600 | event | raw | Sequence learning dot 4 illumination onset |
| `dot_no5_OFF` | 600 | event | raw | Sequence learning dot 5 illumination offset |
| `dot_no5_ON` | 600 | event | raw | Sequence learning dot 5 illumination onset |
| `dot_no6_OFF` | 600 | event | raw | Sequence learning dot 6 illumination offset |
| `dot_no6_ON` | 600 | event | raw | Sequence learning dot 6 illumination onset |
| `dot_no7_OFF` | 796 | event | raw | Sequence learning dot 7 illumination offset |
| `dot_no7_ON` | 792 | event | raw | Sequence learning dot 7 illumination onset |
| `dot_no8_OFF` | 396 | event | raw | Sequence learning dot 8 illumination offset |
| `dot_no8_ON` | 396 | event | raw | Sequence learning dot 8 illumination onset |
| `fixpoint_ON` | 13248 | event | raw | Fixation point onset |
| `instructed_toCloseEyes` | 680 | event | raw | Trial phase onset: Eyes closed instruction |
| `instructed_toOpenEyes` | 816 | event | raw | Trial phase onset: Eyes open instruction |
| `learningBlock_1` | 122 | event | raw | Trial phase onset: Sequence learning block 1 |
| `learningBlock_2` | 121 | event | raw | Trial phase onset: Sequence learning block 2 |
| `learningBlock_3` | 120 | event | raw | Trial phase onset: Sequence learning block 3 |
| `learningBlock_4` | 119 | event | raw | Trial phase onset: Sequence learning block 4 |
| `learningBlock_5` | 118 | event | raw | Trial phase onset: Sequence learning block 5 |
| `left_buttonPress` | 5095 | event | raw | Left-hand button press response |
| `left_target` | 4243 | event | raw | Left visual target onset (stimulus) |
| `newPage` | 194 | admin | raw | New page/segment onset marker |
| `resting_start` | 139 | event | raw | Trial phase onset: Resting state period |
| `right_buttonPress` | 4634 | event | raw | Right-hand button press response |
| `right_target` | 4251 | event | raw | Right visual target onset (stimulus) |
| `seqLearning_start` | 122 | event | raw | Trial phase onset: Sequence learning task |
| `seqLearning_stop` | 118 | event | raw | Trial phase offset: Sequence learning task |
| `stim_ON` | 13278 | event | raw | Surround suppression stimulus onset |
| `surroundSuppB1_start` | 108 | event | raw | Surround suppression block 1 onset |
| `surroundSuppB2_start` | 99 | event | raw | Surround suppression block 2 onset |
| `symbolSearch_start` | 76 | event | raw | Trial phase onset: Symbol search task |
| `trialResponse` | 1247 | event | raw | Symbol search trial response |
| `video_start` | 761 | event | raw | Trial phase onset: Video presentation |
| `video_stop` | 723 | event | raw | Trial phase offset: Video presentation |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: resting-state-eyes-open-vs-closed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 2.0 s, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: `event`
- **Label Field**: (not applicable for event route)
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|--------|
  | instructed_toOpenEyes | 1 | Eyes Open |
  | instructed_toCloseEyes | 0 | Eyes Closed |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.119348 — HBN resting state paradigm uses voice instructions to alternate between eyes-open and eyes-closed states; used for clinical classification across 2042 HBN participants.
  - 10.1016/j.neuroimage.2020.117001 — EEG resting state classification methodology confirming alternating eye-condition paradigm.
- **Notes**: Two-class binary classification of eyes-open vs eyes-closed resting state epochs. Events confirmed in task-RestingState scope (816 × open, 680 × closed).

### Classical Task 2: Contrast Detection Target Direction
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.8 s, target_events = [`left_target`, `right_target`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|--------|
  | left_target | 0 | Left visual target onset (stimulus) |
  | right_target | 1 | Right visual target onset (stimulus) |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — Dataset paper describing contrast change detection paradigm with directional targets and mouse button responses
  - arXiv:2506.19141v2 — EEG2025 competition baseline includes this task in multi-task prediction
- **Notes**: Stimulus-locked binary classification of visual target direction (left vs right leaning). Epoch window -0.2 to 0.8s captures early visual ERP components and motor preparation for button response.

### Classical Task 3: seqLearning6target-spatial-position
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 0.3 s *, target_events = [`dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|--------|
  | dot_no1_ON | 1 | Spatial position 1 |
  | dot_no2_ON | 2 | Spatial position 2 |
  | dot_no3_ON | 3 | Spatial position 3 |
  | dot_no4_ON | 4 | Spatial position 4 |
  | dot_no5_ON | 5 | Spatial position 5 |
  | dot_no6_ON | 6 | Spatial position 6 |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN dataset paper confirming 6-target sequence learning variant with dot illumination patterns
  - task-seqLearning6target_events.json — Confirmed event definitions for dot_no1_ON through dot_no6_ON (Sequence Learning task dot illumination onset)
- **Notes**: Six-class spatial position classification of dot illumination onset. Epoch window captures the transient visual response at dot onset. tmin/tmax inferred from paradigm structure (brief dot flashes ~200-400ms).

### Classical Task 4: Clinical Psychopathology Regression (p-factor)
- **Task Type**: regression
- **Epoch Method**: epoch_by_segmentation_hdf5
- **Epoch Parameters**: segment_length = 5.0 s *, overlap = 0.5, target_events = []
- **Label Route**: info
- **Label Field**: p_factor
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | p_factor | [-0.603, 1.094] (z-score) | General psychopathology factor; bifactor model from HBN phenomics |
- **Evidence**:
  - Alexander et al. (2017), Sci Data — HBN dataset includes bifactor model psychopathology dimensions (p_factor, attention, internalizing, externalizing) for 132 subjects with valid EEG data
  - 10.1016/j.neuroimage.2022.119348 — Uses HBN resting EEG to predict p_factor as primary regression target for clinical prediction
  - arXiv:2506.19141v2 — EEG2025 competition benchmark; multi-task learning on internalizing, externalizing, attention, p-factor from HBN segments
- **Notes**: Sliding window segmentation (5s, 50% overlap) extracts features from continuous resting + task EEG data. The p-factor represents the general liability underlying all psychopathology dimensions; segment-level features enable cross-subject prediction via kernel regression.

### Potential Task 1: age-regression-multi-paradigm
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 5.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (years) | Notes |
  |------------|---------------|-------|
  | age | 5.2–21.7 | Developmental age from HBN participants.tsv |
- **Evidence**:
  - 10.1101/089060 — Uses age as regression target for neural response variability during video watching
  - 10.1016/j.neuroimage.2020.117001 — Age correlates with EEG functional connectivity patterns across 1657 HBN subjects
- **Notes**: Segmentation-based approach extracts 5-second windows with 50% overlap across all available EEG recordings. Age has complete coverage (136/136) unlike clinical dimensions (132/136), making it the most reliable phenotypic target for developmental brain-age prediction.

### Potential Task 2: naturalistic-movie-segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 30.0 s *, overlap = 0.0 s *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|---------------|-------|
  | age | 5.2–21.7 (years) | Participant age at enrollment |
- **Evidence**:
  - 10.1101/2024.10.03.615261 — HBN EEG dataset paper describing naturalistic movie watching tasks (DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent) with video_start/stop markers
  - 10.1101/089060 — Inter-subject correlation approach using video epochs; demonstrates feasibility of predicting subject-level measures from movie-watching EEG
- **Notes**: Segments are extracted from continuous movie-watching recordings without discriminating events (archetype C). Subject-level age is assigned to all segments from each participant. Epoch parameters inferred from naturalistic viewing guidelines: 30s segments provide sufficient temporal context for capturing dynamic movie responses while maintaining independence between excerpts.

## Data Quality Notes

- The `device` metadata field is missing across all subjects; hardware-specific calibration parameters may be unavailable for preprocessing standardization.
- Some phenotypic measures (p_factor, attention, internalizing, externalizing) are available for only 132 of 136 subjects (97% completeness).
- Several tasks are flagged as "caution" status in some subjects (contrastChangeDetection tasks, symbolSearch), suggesting possible data quality or artifact concerns for those recordings.
- A subset of subjects lack `seqLearning8target` data (only `seqLearning6target` available), indicating incomplete coverage for the 8-dot sequence learning variant.
- Unusually large values in `ehq_total` (e.g., -53.36) may indicate data entry errors or non-standard scoring for certain participants.
- The `newPage` event is classified as admin rather than event type, suggesting it serves a structural marker function rather than representing an experimental stimulus.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
