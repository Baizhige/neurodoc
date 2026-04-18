# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale, multi-task developmental battery collected from children and adolescents (ages 5.2–21.7). Participants completed six experimental paradigms: naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. EEG data were acquired using a 129-channel system at 500 Hz, with the dataset designed to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `77d31ab4881800621e9621cc5cc1515549c7932a57bae9c974e7a6fec901bd70`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `9999` | 1136 | admin | raw | System marker/trigger (unclear function) |
| `boundary` | 728 | admin | raw | Boundary marker (MNE-format epoch boundary) |
| `break cnt` | 1488 | event | raw | Break/rest period onset |
| `contrastChangeB1_start` | 102 | event | raw | Contrast change detection block 1 onset |
| `contrastChangeB2_start` | 117 | event | raw | Contrast change detection block 2 onset |
| `contrastChangeB3_start` | 143 | event | raw | Contrast change detection block 3 onset |
| `contrastTrial_start` | 8884 | event | raw | Contrast change detection trial onset |
| `dot_no1_OFF` | 600 | event | raw | Dot position 1 offset (stimulus off) |
| `dot_no1_ON` | 600 | event | raw | Dot position 1 onset (stimulus on) |
| `dot_no2_OFF` | 1202 | event | raw | Dot position 2 offset (stimulus off) |
| `dot_no2_ON` | 1234 | event | raw | Dot position 2 onset (stimulus on) |
| `dot_no3_OFF` | 600 | event | raw | Dot position 3 offset (stimulus off) |
| `dot_no3_ON` | 624 | event | raw | Dot position 3 onset (stimulus on) |
| `dot_no4_OFF` | 600 | event | raw | Dot position 4 offset (stimulus off) |
| `dot_no4_ON` | 600 | event | raw | Dot position 4 onset (stimulus on) |
| `dot_no5_OFF` | 600 | event | raw | Dot position 5 offset (stimulus off) |
| `dot_no5_ON` | 600 | event | raw | Dot position 5 onset (stimulus on) |
| `dot_no6_OFF` | 600 | event | raw | Dot position 6 offset (stimulus off) |
| `dot_no6_ON` | 600 | event | raw | Dot position 6 onset (stimulus on) |
| `dot_no7_OFF` | 796 | event | raw | Dot position 7 offset (stimulus off) |
| `dot_no7_ON` | 792 | event | raw | Dot position 7 onset (stimulus on) |
| `dot_no8_OFF` | 396 | event | raw | Dot position 8 offset (stimulus off) |
| `dot_no8_ON` | 396 | event | raw | Dot position 8 onset (stimulus on) |
| `fixpoint_ON` | 13248 | event | raw | Fixation point onset |
| `instructed_toCloseEyes` | 680 | event | raw | Trial phase onset: instructed to close eyes |
| `instructed_toOpenEyes` | 816 | event | raw | Trial phase onset: instructed to open eyes |
| `learningBlock_1` | 122 | event | raw | Sequence learning block 1 onset |
| `learningBlock_2` | 121 | event | raw | Sequence learning block 2 onset |
| `learningBlock_3` | 120 | event | raw | Sequence learning block 3 onset |
| `learningBlock_4` | 119 | event | raw | Sequence learning block 4 onset |
| `learningBlock_5` | 118 | event | raw | Sequence learning block 5 onset |
| `left_buttonPress` | 5095 | event | raw | Left button press response |
| `left_target` | 4243 | event | raw | Left target cue onset |
| `newPage` | 194 | event | raw | New stimulus page onset |
| `resting_start` | 139 | event | raw | Resting state period onset |
| `right_buttonPress` | 4634 | event | raw | Right button press response |
| `right_target` | 4251 | event | raw | Right target cue onset |
| `seqLearning_start` | 122 | event | raw | Sequence learning task onset |
| `seqLearning_stop` | 118 | event | raw | Sequence learning task offset |
| `stim_ON` | 13278 | event | raw | Visual stimulus onset (duration 2.4s) |
| `surroundSuppB1_start` | 108 | event | raw | Surround suppression block 1 onset |
| `surroundSuppB2_start` | 99 | event | raw | Surround suppression block 2 onset |
| `symbolSearch_start` | 76 | event | raw | Symbol search task onset |
| `trialResponse` | 1247 | event | raw | Trial response (user answer) |
| `video_start` | 761 | event | raw | Video stimulus onset |
| `video_stop` | 723 | event | raw | Video stimulus offset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Psychopathology Dimensions Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.6 s, target_events = [`contrastTrial_start`, `left_target`, `right_target`, `left_buttonPress`, `right_buttonPress`]
- **Label Route**: info
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `contrastTrial_start` | 0 | internalizing dimension (low) |
  | `contrastTrial_start` | 1 | internalizing dimension (high) |
  | `contrastTrial_start` | 0 | externalizing dimension (low) |
  | `contrastTrial_start` | 1 | externalizing dimension (high) |
  | `contrastTrial_start` | 0 | attention dimension (low) |
  | `contrastTrial_start` | 1 | attention dimension (high) |
  | `contrastTrial_start` | 0 | p-factor dimension (low) |
  | `contrastTrial_start` | 1 | p-factor dimension (high) |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor paper describing four-class psychopathology dimensions (internalizing, externalizing, attention, p-factor) derived from bifactor model; explicit multi-task paradigm with contrast detection, video stimuli, rest periods; participant-level phenotypic labels enable downstream classification
  - DOI: 10.1038/sdata.2017.181 — HBN protocol paper establishing phenotypic framework with transdiagnostic research dimensions
- **Kernel Notes**: Labels (p_factor, attention, internalizing, externalizing) sourced from participants.tsv. Use median split or clinical threshold for binary classification. Resting state segments also viable for resting-state biomarkers of psychopathology. Clinical phenotypes available for 136 subjects with age range 5.2–21.7 years.

### Classical Task 2: Age and Sex Neural Response Regression
- **Task Type**: regression
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = null, target_events = [`video_start`, `video_stop`]
- **Label Route**: info
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `video_start` | age (continuous) | Participant age in years (5.2–21.7) |
  | `video_start` | sex (categorical) | Participant sex (M/F) |
- **Evidence**:
  - DOI: 10.1101/089060 — Age and sex modulate neural responses to naturalistic videos; inter-subject correlation of EEG responses quantifying neural variability across development; age and sex treated as predictors in regression models; naturalistic video stimuli matching HBN paradigm (classroom, Hollywood films)
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset descriptor supporting movie-watching paradigm (DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent)
- **Kernel Notes**: Use epoch_by_long_event_hdf5 with 4s segments for continuous movie viewing. Video type (4 movies) serves as within-subject experimental control. Age range spans pediatric to young adult; developmental confounds should be considered. Sex distribution: M=90, F=46.

### Potential Task 1: Contrast Change Detection (Left vs Right Target)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.6 s, target_events = [`contrastTrial_start`, `left_target`, `right_target`, `left_buttonPress`, `right_buttonPress`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `left_target` | 0 | Left-side visual target stimulus |
  | `right_target` | 1 | Right-side visual target stimulus |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — EEG paradigm for assessing information processing includes contrast detection task with left/right target discrimination
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG dataset explicitly describes contrast change detection paradigm with left/right target cues and button press responses
- **Kernel Notes**: Contrast detection is a sensory contrast task, not motor imagery. Left/right denote stimulus position, not movement intention. Epoch alignment to contrastTrial_start for trial onset or left/right_target for stimulus-locked analysis. 8829 contrastTrial_start events, 4243 left_target, 4251 right_target events available. Response-locked analysis using left_buttonPress (5095) / right_buttonPress (4634) events enables hit rate computation.

### Potential Task 2: Sequence Learning Variant Classification (6 vs 8 Targets)
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`seqLearning_start`, `dot_no1_ON`, `dot_no2_ON`, `dot_no3_ON`, `dot_no4_ON`, `dot_no5_ON`, `dot_no6_ON`, `dot_no7_ON`, `dot_no8_ON`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `seqLearning_start` | 0 | Sequence learning with 6 target dots |
  | `seqLearning_start` | 1 | Sequence learning with 8 target dots |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Information processing assessment includes sequence learning paradigm with discrete dot stimuli
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG paradigm includes seqLearning6target and seqLearning8target variants (confirmed via participants.tsv availability flags)
- **Kernel Notes**: Dataset includes both seqLearning6target and seqLearning8target task variants requiring separate task labels. 6-target variant has dot_no1_ON–dot_no6_ON; 8-target variant extends to dot_no7_ON and dot_no8_ON. Use learningBlock_* events for block-level analysis. Task variant classification enables comparison of working memory load effects.

### Potential Task 3: Resting State Eyes Condition (Eyes-Open vs Eyes-Closed)
- **Task Type**: classification
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = -0.5 s, tmax = 4.0 s, target_events = [`instructed_toOpenEyes`, `instructed_toCloseEyes`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `instructed_toOpenEyes` | 0 | Eyes-open rest phase |
  | `instructed_toCloseEyes` | 1 | Eyes-close rest phase |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — Resting state paradigm with alternating eyes-open/closed periods; instructed_toOpenEyes and instructed_toCloseEyes markers confirmed in events.json
- **Kernel Notes**: Resting state is a sustained-state paradigm requiring epoch_by_long_event_hdf5 with 5s segments overlapping by 0.5s. 816 instructed_toOpenEyes and 680 instructed_toCloseEyes events available. Supports spectral analysis (alpha power differences between conditions) and clinical resting-state biomarkers. Task-ContrastChangeDetection task can be added if needed.

### Potential Task 4: Surround Suppression Visual Evoked Response
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 3.0 s, target_events = [`stim_ON`, `fixpoint_ON`, `surroundSuppB1_start`, `surroundSuppB2_start`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `stim_ON` | 0 | Visual stimulus with background |
  | `stim_ON` | 1 | Visual stimulus without background |
- **Evidence**:
  - DOI: 10.1038/sdata.2017.40 — Surround suppression paradigm with contrasting backgrounds
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG includes surround suppression task with background condition variations
- **Kernel Notes**: stim_ON events have 2.4s duration per HED definitions. Background presence (0/1) is encoded in event metadata (e.g., task-surroundSupp_events.json). fixpoint_ON (13248 events) serves as preparatory cue. Use tmax=3.0s to capture full stimulus presentation and post-stimulus dynamics. Block-level analysis possible using surroundSuppB1_start (108) / surroundSuppB2_start (99) events.

### Potential Task 5: Symbol Search Response Accuracy
- **Task Type**: classification
- **Epoch Method**: epoch_by_event_hdf5
- **Epoch Parameters**: tmin = -0.2 s, tmax = 2.0 s, target_events = [`newPage`, `trialResponse`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `newPage` | 0 | Incorrect response on subsequent trialResponse |
  | `newPage` | 1 | Correct response on subsequent trialResponse |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG includes symbol search active cognitive task with behavioral responses
  - DOI: 10.1038/sdata.2017.40 — Processing speed and cognitive search tasks part of paradigm battery
- **Kernel Notes**: Symbol search is an active cognitive task with newPage (194 events) marking stimulus display onset and trialResponse (1247 events) marking behavioral responses. user_answer and correct_answer fields in events.json define accuracy labels (0=false, 1=true). Align epochs to newPage for stimulus-locked analysis. Response-locked analysis using trialResponse events enables motor response characterization separate from accuracy classification.

### Potential Task 6: Movie Type Classification
- **Task Type**: classification
- **Epoch Method**: epoch_by_long_event_hdf5
- **Epoch Parameters**: tmin = 0.0 s, tmax = null, target_events = [`video_start`, `video_stop`]
- **Label Route**: event
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-----------|
  | `video_start` | 0 | DespicableMe (animated comedy) |
  | `video_start` | 1 | DiaryOfAWimpyKid (animated comedy) |
  | `video_start` | 2 | FunwithFractals (fractal visuals) |
  | `video_start` | 3 | ThePresent (short film) |
- **Evidence**:
  - DOI: 10.1101/2024.10.03.615261 — HBN-EEG includes four short movies: DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent
  - DOI: 10.1101/089060 — Naturalistic video stimuli from classroom and Hollywood films matching HBN paradigm
- **Kernel Notes**: Four movies span different genres (animated comedies, fractal visuals, short film) providing natural stimulus variation. Use epoch_by_long_event_hdf5 with 4s segments for sustained processing analysis. Video_start (761) / video_stop (723) events mark segment boundaries. Supports time-frequency and connectivity analyses of movie-driven brain dynamics. Parent review of clips confirmed appropriate for pediatric population (ages 5.2–21.7).

## Data Quality Notes

- The `device` field is missing from the dataset metadata, so recording equipment details are unavailable.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
