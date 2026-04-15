# Healthy Brain Network (HBN) EEG - Release 1

**Dataset**: `openneuro_ds005505` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005505
**Category**: Complex Applied | **Subjects**: 136 | **Files (Completed)**: 1342 | **Channels**: 129 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

The Healthy Brain Network (HBN) EEG Release 1 is a large-scale, multi-task developmental battery collected from children and adolescents (ages 5.2–21.7). Participants completed six experimental paradigms: naturalistic movie watching, eyes-open/closed resting state, sensory contrast detection, surrounding suppression, sequence learning, and symbol search tasks. EEG data were acquired using a 129-channel system at 500 Hz, with the dataset designed to characterize neurodevelopmental and psychopathological profiles across a broad pediatric population.

## File Scan Result

> **Kernel SHA256**: `1e4bbaac5d9f2aa7e8f213f0534a948615c1dbeb27279bb638de77d72c983839`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `admin: end_marker` | 730 | admin | raw | End-of-recording marker |
| `boundary` | 460 | admin | raw | Segment boundary marker |
| `break cnt` | 508 | admin | raw | Break/counter marker between blocks |
| `contrast:admin: end_marker` | 370 | admin | raw | Contrast detection block end marker |
| `contrast:boundary` | 33 | admin | raw | Contrast detection segment boundary |
| `contrast:break cnt` | 696 | admin | raw | Contrast detection break marker |
| `contrast:contrastChangeB1_start` | 102 | event | raw | Contrast change block 1 onset |
| `contrast:contrastChangeB2_start` | 111 | event | raw | Contrast change block 2 onset |
| `contrast:contrastChangeB3_start` | 142 | event | raw | Contrast change block 3 onset |
| `contrast:contrastTrial_start` | 8829 | event | raw | Contrast detection trial block onset |
| `contrast:left_buttonPress` | 5095 | event | raw | Participant left-hand button press response |
| `contrast:left_target` | 4243 | event | raw | Left-side visual target stimulus |
| `contrast:right_buttonPress` | 4634 | event | raw | Participant right-hand button press response |
| `contrast:right_target` | 4231 | event | raw | Right-side visual target stimulus |
| `contrast:video_start` | 116 | event | raw | Contrast task movie clip onset |
| `contrast:video_stop` | 89 | event | raw | Contrast task movie clip offset |
| `contrastChangeB2_start` | 6 | event | raw | Contrast change block 2 onset (orphan) |
| `contrastChangeB3_start` | 1 | event | raw | Contrast change block 3 onset (orphan) |
| `contrastTrial_start` | 55 | event | raw | Contrast trial block onset (orphan) |
| `dot_no2_OFF` | 2 | event | raw | Dot stimulus 2 offset (orphan) |
| `dot_no2_ON` | 34 | event | raw | Dot stimulus 2 onset (orphan) |
| `dot_no3_ON` | 24 | event | raw | Dot stimulus 3 onset (orphan) |
| `dot_no7_OFF` | 1 | event | raw | Dot stimulus 7 offset (orphan) |
| `fixpoint_ON` | 13248 | event | raw | Fixation point onset (trial cue) |
| `newPage` | 194 | event | raw | New search page display event |
| `resting:admin: end_marker` | 29 | admin | raw | Resting-state block end marker |
| `resting:boundary` | 120 | admin | raw | Resting-state segment boundary |
| `resting:break cnt` | 164 | admin | raw | Resting-state break marker |
| `resting:dot_no1_OFF` | 10 | event | raw | Resting-state dot 1 offset |
| `resting:dot_no1_ON` | 10 | event | raw | Resting-state dot 1 onset |
| `resting:dot_no2_OFF` | 20 | event | raw | Resting-state dot 2 offset |
| `resting:dot_no2_ON` | 20 | event | raw | Resting-state dot 2 onset |
| `resting:dot_no3_OFF` | 10 | event | raw | Resting-state dot 3 offset |
| `resting:dot_no3_ON` | 10 | event | raw | Resting-state dot 3 onset |
| `resting:dot_no4_OFF` | 10 | event | raw | Resting-state dot 4 offset |
| `resting:dot_no4_ON` | 10 | event | raw | Resting-state dot 4 onset |
| `resting:dot_no5_OFF` | 10 | event | raw | Resting-state dot 5 offset |
| `resting:dot_no5_ON` | 10 | event | raw | Resting-state dot 5 onset |
| `resting:dot_no6_OFF` | 10 | event | raw | Resting-state dot 6 offset |
| `resting:dot_no6_ON` | 10 | event | raw | Resting-state dot 6 onset |
| `resting:dot_no7_OFF` | 12 | event | raw | Resting-state dot 7 offset |
| `resting:dot_no7_ON` | 12 | event | raw | Resting-state dot 7 onset |
| `resting:dot_no8_OFF` | 6 | event | raw | Resting-state dot 8 offset |
| `resting:dot_no8_ON` | 6 | event | raw | Resting-state dot 8 onset |
| `resting:instructed_toCloseEyes` | 680 | event | raw | Eyes-closed instruction onset |
| `resting:instructed_toOpenEyes` | 816 | event | raw | Eyes-open instruction onset |
| `resting:learningBlock_1` | 4 | event | raw | Resting-state learning block 1 (orphan) |
| `resting:learningBlock_2` | 3 | event | raw | Resting-state learning block 2 (orphan) |
| `resting:learningBlock_3` | 2 | event | raw | Resting-state learning block 3 (orphan) |
| `resting:learningBlock_4` | 1 | event | raw | Resting-state learning block 4 (orphan) |
| `resting:resting_start` | 139 | event | raw | Resting-state period onset |
| `resting:seqLearning_start` | 4 | event | raw | Resting-state sequence learning onset (orphan) |
| `resting:video_start` | 17 | event | raw | Resting-state video clip onset (orphan) |
| `resting:video_stop` | 14 | event | raw | Resting-state video clip offset (orphan) |
| `right_target` | 20 | event | raw | Right-side visual target stimulus (orphan) |
| `seqLearning:admin: end_marker` | 7 | admin | raw | Sequence learning block end marker |
| `seqLearning:boundary` | 115 | admin | raw | Sequence learning segment boundary |
| `seqLearning:break cnt` | 120 | admin | raw | Sequence learning break marker |
| `seqLearning:dot_no1_OFF` | 590 | event | raw | Sequence learning dot 1 offset |
| `seqLearning:dot_no1_ON` | 590 | event | raw | Sequence learning dot 1 onset |
| `seqLearning:dot_no2_OFF` | 1180 | event | raw | Sequence learning dot 2 offset |
| `seqLearning:dot_no2_ON` | 1180 | event | raw | Sequence learning dot 2 onset |
| `seqLearning:dot_no3_OFF` | 590 | event | raw | Sequence learning dot 3 offset |
| `seqLearning:dot_no3_ON` | 590 | event | raw | Sequence learning dot 3 onset |
| `seqLearning:dot_no4_OFF` | 590 | event | raw | Sequence learning dot 4 offset |
| `seqLearning:dot_no4_ON` | 590 | event | raw | Sequence learning dot 4 onset |
| `seqLearning:dot_no5_OFF` | 590 | event | raw | Sequence learning dot 5 offset |
| `seqLearning:dot_no5_ON` | 590 | event | raw | Sequence learning dot 5 onset |
| `seqLearning:dot_no6_OFF` | 590 | event | raw | Sequence learning dot 6 offset |
| `seqLearning:dot_no6_ON` | 590 | event | raw | Sequence learning dot 6 onset |
| `seqLearning:dot_no7_OFF` | 783 | event | raw | Sequence learning dot 7 offset |
| `seqLearning:dot_no7_ON` | 780 | event | raw | Sequence learning dot 7 onset |
| `seqLearning:dot_no8_OFF` | 390 | event | raw | Sequence learning dot 8 offset |
| `seqLearning:dot_no8_ON` | 390 | event | raw | Sequence learning dot 8 onset |
| `seqLearning:learningBlock_1` | 118 | event | raw | Sequence learning block 1 start |
| `seqLearning:learningBlock_2` | 118 | event | raw | Sequence learning block 2 start |
| `seqLearning:learningBlock_3` | 118 | event | raw | Sequence learning block 3 start |
| `seqLearning:learningBlock_4` | 118 | event | raw | Sequence learning block 4 start |
| `seqLearning:learningBlock_5` | 118 | event | raw | Sequence learning block 5 start |
| `seqLearning:seqLearning_start` | 118 | event | raw | Sequence learning task onset |
| `seqLearning:seqLearning_stop` | 118 | event | raw | Sequence learning task offset |
| `seqLearning:video_start` | 4 | event | raw | Sequence learning video clip onset (orphan) |
| `seqLearning:video_stop` | 2 | event | raw | Sequence learning video clip offset (orphan) |
| `stim_ON` | 13278 | event | raw | Visual stimulus onset (peripheral disks) |
| `surroundSuppB1_start` | 108 | event | raw | Surround suppression block 1 onset |
| `surroundSuppB2_start` | 99 | event | raw | Surround suppression block 2 onset |
| `symbolSearch_start` | 76 | event | raw | Symbol search task onset |
| `trialResponse` | 1247 | event | raw | Subject provided a response |
| `video_start` | 624 | event | raw | Video stream started (movie onset) |
| `video_stop` | 618 | event | raw | Video stream completed (movie offset) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Contrast Change Detection

**Task Type**: ERP/Sensory

**Epoch Method**: epoch_by_event_hdf5

**Epoch Parameters**: tmin=-0.2, tmax=1.0, overlap=null, segment_length=null

**Label Route**: event

**Meta Level**: raw

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `contrast:contrastTrial_start` | 0 | Baseline epoch (no target locked) |
| `contrast:left_target` | 1 | Left-side visual target stimulus onset |
| `contrast:right_target` | 2 | Right-side visual target stimulus onset |
| `contrast:left_buttonPress` | 3 | Left-hand button press response |
| `contrast:right_buttonPress` | 4 | Right-hand button press response |

**Evidence (DOI)**: 10.1101/2024.10.03.615261 | 10.1016/j.neuroimage.2020.117001

**Kernel Notes**: Paradigm uses prefix `contrast:` for all events. Orphan events (contrastChangeB2_start, contrastChangeB3_start) without prefix should be excluded. 3 blocks per subject (B1/B2/B3). Target duration ~1600ms per HED schema. Button presses serve as response-locked alternative.

---

### Classical Task 2: Resting State

**Task Type**: Connectivity/Spectral

**Epoch Method**: epoch_by_long_event_hdf5

**Epoch Parameters**: tmin=0.0, tmax=30.0, overlap=0.0, segment_length=30.0

**Label Route**: stim

**Meta Level**: super

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `resting:instructed_toOpenEyes` | 1 | Eyes-open resting state period |
| `resting:instructed_toCloseEyes` | 0 | Eyes-closed resting state period |

**Evidence (DOI)**: 10.1101/2024.10.03.615261 | 10.1016/j.neuroimage.2022.119348 | 10.1016/j.neuroimage.2020.117001

**Kernel Notes**: Explicitly benchmarked for psychiatric multimorbidity prediction (7 DSM-V diagnoses). Super-meta labels derived from participants.tsv fields (attention, internalizing, externalizing, p-factor). Paradigm uses prefix `resting:` for events. 680 open-eye and 816 close-eye events across dataset. Fixation cross displayed during rest.

---

### Classical Task 3: Clinical Psychopathology Classification

**Task Type**: Classification

**Epoch Method**: epoch_by_long_event_hdf5

**Epoch Parameters**: tmin=0.0, tmax=10.0, overlap=0.0, segment_length=10.0

**Label Route**: misc

**Meta Level**: super

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `resting:resting_start` | super | Subject-level clinical labels from participants.tsv |

**Evidence (DOI)**: 10.1016/j.neuroimage.2022.119348 | 10.1101/2024.10.03.615261

**Kernel Notes**: Super-meta labels derived from subject metadata field [diagnosis] — kernel must load per-subject label from companion file. Benchmark defines 7 DSM-V psychiatric diagnoses for multi-label classification plus dimensional symptom severity regression (attention, internalizing, externalizing, p-factor). Resting-state EEG features (spectral power, connectivity) linked to psychopathology dimensions.

---

### Normal Task 4: Surround Suppression

**Task Type**: ERP/Sensory

**Epoch Method**: epoch_by_event_hdf5

**Epoch Parameters**: tmin=-0.2, tmax=0.5, overlap=null, segment_length=null

**Label Route**: event

**Meta Level**: raw

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `fixpoint_ON` | 0 | Fixation point onset (trial cue) |
| `stim_ON` | 1 | Visual stimulus onset (peripheral disks) |
| `surroundSuppB1_start` | 2 | Surround suppression block 1 onset |
| `surroundSuppB2_start` | 3 | Surround suppression block 2 onset |

**Evidence (DOI)**: 10.1038/sdata.2017.40 | 10.1101/2024.10.03.615261

**Kernel Notes**: 13278 stim_ON events enable robust averaging. Visual perception task measuring surround suppression with contrasting backgrounds. HED schema defines stimulus conditions (background presence, luminance contrast, spatial relations). Short 0.7s window captures early visual components (C1, P1).

---

### Normal Task 5: Sequence Learning

**Task Type**: Motor/Sequence

**Epoch Method**: epoch_by_event_hdf5

**Epoch Parameters**: tmin=-0.2, tmax=0.8, overlap=null, segment_length=null

**Label Route**: event

**Meta Level**: raw

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `seqLearning:seqLearning_start` | 0 | Sequence learning task onset |
| `seqLearning:learningBlock_1` | 1 | Learning block 1 start |
| `seqLearning:learningBlock_2` | 2 | Learning block 2 start |
| `seqLearning:learningBlock_3` | 3 | Learning block 3 start |
| `seqLearning:dot_no1_ON` | 4 | Dot 1 turned black (sequence position) |
| `seqLearning:dot_no2_ON` | 5 | Dot 2 turned black (sequence position) |
| `seqLearning:dot_no3_ON` | 6 | Dot 3 turned black (sequence position) |
| `seqLearning:dot_no4_ON` | 7 | Dot 4 turned black (sequence position) |

**Evidence (DOI)**: 10.1038/sdata.2017.40 | 10.1101/2024.10.03.615261

**Kernel Notes**: Paradigm uses prefix `seqLearning:` for events. Two variants: 6-target (590-1180 dot events) and 8-target (780-1180 dot events). Orphan dot events (dot_no2_ON, dot_no3_ON, dot_no7_OFF) without prefix should be excluded. 5 learning blocks per run enable analysis of sequence acquisition across time.

---

### Normal Task 6: Symbol Search

**Task Type**: Cognitive/Active

**Epoch Method**: epoch_by_event_hdf5

**Epoch Parameters**: tmin=-0.2, tmax=1.0, overlap=null, segment_length=null

**Label Route**: event

**Meta Level**: raw

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `symbolSearch_start` | 0 | Symbol search task onset |
| `newPage` | 1 | New page of symbol search queries presented |
| `trialResponse` | 2 | Subject provided a response |

**Evidence (DOI)**: 10.1038/sdata.2017.40 | 10.1101/2024.10.03.615261

**Kernel Notes**: 194 newPage events and 1247 trialResponse events available. HED schema defines correct_answer and user_answer for accuracy computation (user_answer: 0=False, 1=True; correct_answer: 0=not present, 1=present). Active cognitive task measuring search efficiency. Can analyze both stimulus-locked (newPage) and response-locked (trialResponse) epochs.

---

### Potential Task 7: Movie Watching (Naturalistic)

**Task Type**: Time-Frequency/Sustained Attention

**Epoch Method**: epoch_by_long_event_hdf5

**Epoch Parameters**: tmin=0.0, tmax=4.0, overlap=0.0, segment_length=4.0

**Label Route**: stim

**Meta Level**: raw

**Target Definition**:

| Event | y | Meaning |
|---|---|---|
| `video_start` | 1 | Video stream started (movie onset) |
| `video_stop` | 0 | Video stream completed (movie offset) |

**Evidence (DOI)**: 10.1038/sdata.2017.40

**Kernel Notes**: 4 movies: DespicableMe, DiaryOfAWimpyKid, FunwithFractals, ThePresent (age-appropriate video clips). 624 video_start and 618 video_stop events. Segment into 4s non-overlapping epochs for time-frequency analysis. Naturalistic paradigm enables study of sustained attentional engagement. No direct ML benchmark exists for this specific BIDS release; classified as Potential due to partial support from paradigm literature.