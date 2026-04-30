# Imagined Emotion Study

**Dataset**: `openneuro_ds003004` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003004
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 34 | **Channels**: 219 | **Sampling Rate**: 256 Hz | **Manual Review**:

## Paradigm

Participants used voice-guided imagery to induce and sustain 15 distinct emotional states (awe, anger, compassion, content, disgust, excitement, fear, frustration, grief, happiness, jealousy, joy, love, relief, relaxation, sadness), using button presses to indicate the onset and offset of each imagined emotion. The paradigm includes pre-baseline and post-baseline recording periods, with initial instructions and imagination suggestions provided throughout the session. High-density EEG recordings were collected using a 256-channel system.

## File Scan Result

> **Kernel SHA256**: `9c087043f37ac6921fc1b534eb9f79b4f58c41884cf33a3bbd5820b1f68a4d5c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ExitThankYou` | 34 | event | raw | Trial phase onset: ExitThankYou |
| `FeelingItInstructionsButton` | 18 | event | raw | Trial phase onset: FeelingItInstructionsButton |
| `FeelingItInstructionsNoButton` | 19 | event | raw | Trial phase onset: FeelingItInstructionsNoButton |
| `ImaginationSuggestions` | 34 | event | raw | Trial phase onset: ImaginationSuggestions |
| `InitialInstructions` | 31 | event | raw | Trial phase onset: InitialInstructions |
| `InstructionsForEnding` | 34 | event | raw | Trial phase onset: InstructionsForEnding |
| `anger` | 34 | event | raw | Trial phase onset: anger |
| `awe` | 35 | event | raw | Trial phase onset: awe |
| `compassion` | 34 | event | raw | Trial phase onset: compassion |
| `content` | 34 | event | raw | Trial phase onset: content |
| `disgust` | 34 | event | raw | Trial phase onset: disgust |
| `enter` | 508 | event | raw | Trial phase onset: enter |
| `excite` | 34 | event | raw | Trial phase onset: excite |
| `exit` | 558 | event | raw | Trial phase onset: exit |
| `fear` | 34 | event | raw | Trial phase onset: fear |
| `frustration` | 34 | event | raw | Trial phase onset: frustration |
| `grief` | 34 | event | raw | Trial phase onset: grief |
| `happy` | 34 | event | raw | Trial phase onset: happy |
| `jealousy` | 34 | event | raw | Trial phase onset: jealousy |
| `joy` | 34 | event | raw | Trial phase onset: joy |
| `love` | 34 | event | raw | Trial phase onset: love |
| `postbase` | 34 | event | raw | Trial phase onset: postbase |
| `postbase_instruct` | 34 | event | raw | Trial phase onset: postbase_instruct |
| `prebase` | 34 | event | raw | Trial phase onset: prebase |
| `prebase_instruct` | 33 | event | raw | Trial phase onset: prebase_instruct |
| `press` | 703 | event | raw | Trial phase onset: press |
| `press1` | 492 | event | raw | Trial phase onset: press1 |
| `relax` | 34 | event | raw | Trial phase onset: relax |
| `relief` | 34 | event | raw | Trial phase onset: relief |
| `sad` | 34 | event | raw | Trial phase onset: sad |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 15-class emotion imagination
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 360 s *, overlap = 0.0, target_events = [`anger`, `awe`, `compassion`, `content`, `disgust`, `excite`, `fear`, `frustration`, `grief`, `happy`, `jealousy`, `joy`, `love`, `relief`, `relax`, `sad`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `anger` | 0 | anger imagination period |
  | `awe` | 1 | awe imagination period |
  | `compassion` | 2 | compassion imagination period |
  | `content` | 3 | content imagination period |
  | `disgust` | 4 | disgust imagination period |
  | `excite` | 5 | excite imagination period |
  | `fear` | 6 | fear imagination period |
  | `frustration` | 7 | frustration imagination period |
  | `grief` | 8 | grief imagination period |
  | `happy` | 9 | happy imagination period |
  | `jealousy` | 10 | jealousy imagination period |
  | `joy` | 11 | joy imagination period |
  | `love` | 12 | love imagination period |
  | `relief` | 13 | relief imagination period |
  | `relax` | 14 | relax imagination period |
  | `sad` | 15 | sad imagination period |
- **Evidence**:
  - 10.1016/j.neuroimage.2022.118873 — AMICA decomposition paper analyzing full 3-5 minute emotion imagination periods from this dataset
  - 10.1109/ACII.2013.160 — Original ACII 2013 paper using 6-second segments from within longer emotion periods for classification
- **Notes**: The dataset contains 16 emotion events, but the README and papers describe 15 emotion narratives. The event `excite` and `relax` may be treated differently across papers (relax as a non-emotion rest condition in some analyses). All 16 events are retained here to match the event structure; downstream analyses may merge or exclude as needed. The long epoch window (360s) accommodates the full 3-5 minute emotion periods described in the NeuroImage 2022 paper; for short-segment classification as in ACII 2013, use tmax=6s with segmentation. Epoch parameters are inferred from paper descriptions since event durations are zero in the BIDS files (impulse markers).

### Classical Task 2: 2-class valence emotion
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 6 s, overlap = 0, target_events = [`anger`, `awe`, `compassion`, `content`, `disgust`, `excite`, `fear`, `frustration`, `grief`, `happy`, `jealousy`, `joy`, `love`, `relief`, `sad`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `anger` | 0 | negative valence |
  | `frustration` | 0 | negative valence |
  | `fear` | 0 | negative valence |
  | `sad` | 0 | negative valence |
  | `grief` | 0 | negative valence |
  | `jealousy` | 0 | negative valence |
  | `disgust` | 0 | negative valence |
  | `awe` | 1 | positive valence |
  | `joy` | 1 | positive valence |
  | `happy` | 1 | positive valence |
  | `relief` | 1 | positive valence |
  | `compassion` | 1 | positive valence |
  | `content` | 1 | positive valence |
  | `love` | 1 | positive valence |
- **Evidence**:
  - 10.1109/ACCII.2013.160 — Binary valence classification from original ACII 2013 paper: positive emotions (love, joy, happy, relief, compassion, content, awe) vs negative emotions (anger, jealousy, disgust, frustration, fear, sad, grief). Uses 6-second EEG segments with FBCSP.
- **Notes**: Per the ACII 2013 paper, `excite` and `relax` are excluded due to unclear/undefined valence. The paper also excluded `compassion` and `disgust` in some analyses, but here we follow the standard positive/negative mapping: positive valence = {awe, compassion, content, happy, joy, love, relief} and negative valence = {anger, disgust, fear, frustration, grief, jealousy, sad}. The `excite` event is excluded from target_events as its valence is ambiguous (could be positive or negative arousal without clear valence). `relax` is excluded as it is a low-arousal neutral/positive state not fitting the binary valence scheme. Epochs are extracted from within longer emotion periods using 6-second windows as explicitly stated in the paper.

### Potential Task 1: 2-class valence emotion (extended 16-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 6 s *, overlap = 0.5 *, target_events = [`anger`, `awe`, `compassion`, `content`, `disgust`, `excite`, `fear`, `frustration`, `grief`, `happy`, `jealousy`, `joy`, `love`, `relief`, `relax`, `sad`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `awe` | 0 | positive valence |
  | `compassion` | 0 | positive valence |
  | `content` | 0 | positive valence |
  | `excite` | 0 | positive valence |
  | `happy` | 0 | positive valence |
  | `joy` | 0 | positive valence |
  | `love` | 0 | positive valence |
  | `relief` | 0 | positive valence |
  | `relax` | 0 | positive valence |
  | `anger` | 1 | negative valence |
  | `disgust` | 1 | negative valence |
  | `fear` | 1 | negative valence |
  | `frustration` | 1 | negative valence |
  | `grief` | 1 | negative valence |
  | `jealousy` | 1 | negative valence |
  | `sad` | 1 | negative valence |
- **Evidence**:
- **Notes**: Extended 2-class valence classification using all 16 emotion events in the dataset. Positive valence class (y=0) includes: awe, compassion, content, excite, happy, joy, love, relief, relax. Negative valence class (y=1) includes: anger, disgust, fear, frustration, grief, jealousy, sad. The `excite` and `relax` events extend beyond the classical 15-emotion set. Overlap value of 0.5 inferred from long-event epoching best practice for 6-second emotion imagination segments. All parameters marked with * due to inferred status from candidate epoch_hint.

### Potential Task 2: 3-class valence-arousal emotion
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 6 s *, overlap = 0 s *, target_events = [`anger`, `awe`, `compassion`, `content`, `disgust`, `excite`, `fear`, `frustration`, `grief`, `happy`, `jealousy`, `joy`, `love`, `relief`, `relax`, `sad`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `joy`, `happy`, `excite`, `love`, `calm`, `content`, `relief`, `relax`, `awe`, `compassion` | 0 | positive valence (high and low arousal) |
  | `anger`, `fear`, `frustration`, `jealousy`, `disgust` | 1 | high-arousal negative valence |
  | `sad`, `grief` | 2 | low-arousal negative valence |
- **Evidence**:
- **Notes**: Emotion events are grouped by valence-arousal dimensions into 3 classes. Positive valence emotions (y=0) collapse both high-arousal (joy, happy, excite, love) and low-arousal (calm, content, relief, relax, awe, compassion) positive states. Negative valence is split by arousal: high-arousal negative (y=1: anger, fear, frustration, jealousy, disgust) and low-arousal negative (y=2: sad, grief). The `relax` event is included as a low-arousal positive emotion per the emotion imagination paradigm context. Epoch parameters are inferred from standard emotion dimension theory with 6-second segments; overlap set to 0 s as default for long-event epochs when not specified. Note: `calm` is not present in available event IDs but the mapping structure is preserved for consistency with the theoretical framework.

### Potential Task 3: Rest vs Task State Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 120 s *, target_events = ['prebase', 'postbase', 'anger', 'awe', 'compassion', 'content', 'disgust', 'excite', 'fear', 'frustration', 'grief', 'happy', 'jealousy', 'joy', 'love', 'relief', 'relax', 'sad']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | prebase | 0 | silent 2-min baseline rest period |
  | postbase | 0 | silent 2-min post-session baseline rest period |
  | anger | 1 | active guided imagery: anger emotion |
  | awe | 1 | active guided imagery: awe emotion |
  | compassion | 1 | active guided imagery: compassion emotion |
  | content | 1 | active guided imagery: content emotion |
  | disgust | 1 | active guided imagery: disgust emotion |
  | excite | 1 | active guided imagery: excite emotion |
  | fear | 1 | active guided imagery: fear emotion |
  | frustration | 1 | active guided imagery: frustration emotion |
  | grief | 1 | active guided imagery: grief emotion |
  | happy | 1 | active guided imagery: happy emotion |
  | jealousy | 1 | active guided imagery: jealousy emotion |
  | joy | 1 | active guided imagery: joy emotion |
  | love | 1 | active guided imagery: love emotion |
  | relief | 1 | active guided imagery: relief emotion |
  | relax | 1 | active guided imagery: relax emotion |
  | sad | 1 | active guided imagery: sad emotion |
- **Evidence**:
  - events.json — "prebase" event marks the beginning of the silent 2-min period to collect baseline data; prebase_instruct describes obtaining pre-session baseline brain activity by sitting quietly for two minutes
  - events.json — emotion events (anger, awe, compassion, etc.) are trial phase onsets for guided imagery episodes where subjects imagine emotional scenarios
  - README — subjects listen to voice recordings suggesting an emotional feeling and imagine/recall an emotional scenario; subjects indicate when they begin to feel the emotion via button press
- **Notes**: All 15 emotion events plus 'relax' are merged into y=1 (active task/engaged emotional processing state), while 'prebase' and 'postbase' are merged into y=0 (rest state). The 120s epoch duration is inferred from the described 2-minute baseline periods; emotion periods are variable but truncated to match for balanced comparison. This is a simple 2-class contrast between disengaged rest and active emotional imagery engagement.

### Potential Task 4: Button Press Response Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -2 s *, tmax = 1 s *, target_events = [`press1`, `press`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `press1` | 0 | Subject indicated starting to feel the specified emotion (initial button press) |
  | `press` | 1 | Subsequent pressure-sensing button press expressing the emotion |
- **Evidence**:
  - `sub-01_task-ImaginedEmotion_events.json` / `sub-02_task-ImaginedEmotion_events.json` — "'press1' events are when the subject indicated with a button press that they were starting to feel the specified emotion"; "'press' events are subsequent pressure-sensing button presses meant to express the specified emotion"
  - `sub-01_task-ImaginedEmotion_events.tsv` / `sub-02_task-ImaginedEmotion_events.tsv` — Direct observation of `press1` and `press` event occurrences in data
  - `README` — "When the subject first begins to feel filled with the suggested emotion, they indicate this by pressing the finger pressure sensor"
- **Notes**: Binary classification distinguishing the initial emotion-onset press (press1) from subsequent expression presses (press). The 2-second pre-stimulus window captures readiness potential and anticipatory EEG dynamics preceding the motor response; the 1-second post-stimulus window captures the motor response execution. Epoch parameters are inferred from standard ERP approaches for button press studies.

### Potential Task 5: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | Age | 20–35 (years) | Subject chronological age; continuous regression target. Sample values: 20, 22, 23, 29, 35. |
- **Evidence**:
  - participants.tsv — Age column complete for all 34 subjects with numeric values ranging 20–35 years
- **Notes**: Segmentation-based approach for subject-level biomarker regression. No event structure required; full continuous EEG is divided into 10-second windows with 50% overlap to provide multiple samples per subject while capturing sufficient spectral dynamics for age prediction. Age is a native participants.tsv column (archetype B3, Meta Level = raw).

### Potential Task 6: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | F | 0 | Female |
  | Gender | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level biomarker classification using 10-second non-overlapping windows (50% overlap) from continuous EEG. The task treats gender as a binary classification problem (F/M) based on potential sex differences in EEG spectral patterns during emotional imagery. All 34 subjects have complete gender information in participants.tsv. Segmentation is used rather than event-based epoching because this is a subject-level trait classification where the goal is to learn stable individual differences across the entire recording, not transient event-locked responses.

### Potential Task 7: Handedness Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Handedness | L | 0 | Left-handed |
  | Handedness | R | 1 | Right-handed |
- **Evidence**:
- **Notes**: Subject-level biomarker classification using 10-second non-overlapping segments of continuous EEG. Two subjects (sub-01 and one other) have NA/ missing Handedness values and must be excluded, leaving 32 subjects with valid labels. The task tests whether resting/task EEG contains lateralization signatures predictive of handedness. All segments from a given subject share the same Handedness label.

### Potential Task 8: YOB regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 10 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `YOB`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | YOB | 1970–1984 (year) | Year of birth derived from participants.tsv; redundant with Age but provides alternative temporal encoding for cohort analysis |
- **Evidence**:
  - participants.tsv — YOB column present with complete data (N=34, range 1970–1984, e.g., sub-01: 1981, sub-10: 1975, sub-15: 1970)
- **Notes**: Segmentation-based regression with no event anchoring. YOB and Age are linearly related (YOB ≈ current_year - Age) so this task is redundant with Age regression; however, YOB may be preferred for cohort analysis as it provides absolute temporal reference rather than relative age. Same segmentation parameters as Age regression task (10s windows, 50% overlap).

### Potential Task 9: Emotion Imagination Segmentation with Age Covariate
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | Age | 20–35 (years) | Subject chronological age from participants.tsv; applied as subject-level covariate to all segments |
- **Evidence**:
- **Notes**: Segmentation-based regression with subject-level age as target. Continuous 10-second segments with 50% overlap are extracted from the full recording (which spans emotion imagination periods among other task phases). Since Age is a native participants.tsv column and the epoch method is segmentation with info route, Meta Level = raw per archetype C rules. The segment_length and overlap values are inferred from the candidate hint; no tmin/tmax are required for segmentation method.

## Data Quality Notes

- Event durations are zero in BIDS files (impulse markers), requiring epoch parameters to be inferred from paper descriptions rather than derived from event boundaries.
- Subject count discrepancy: metadata states 31 subjects but 34 files completed; the File Scan Result shows 34 subjects with complete Age/Gender/YOB data and 32/34 with Handedness data.
- The dataset contains 16 emotion events (`anger`, `awe`, `compassion`, `content`, `disgust`, `excite`, `fear`, `frustration`, `grief`, `happy`, `jealousy`, `joy`, `love`, `relief`, `relax`, `sad`) but papers describe 15 emotion narratives, creating ambiguity around whether `excite` and/or `relax` should be treated as emotions or control conditions.
- `subject_age` and `subject_sex` fields are missing from BIDS files; age and gender information is only available through the non-BIDS `Age` and `Gender` info fields in participants.tsv.
- `device` metadata is missing from BIDS files despite the use of a high-density 256-channel EEG system (only 219 channels present in processed data).
- `prebase_instruct` event count (33) does not match `prebase` event count (34), suggesting one subject may be missing the pre-baseline instruction event.
- `InitialInstructions` event count (31) is lower than the number of completed files (34), suggesting 3 subjects may lack this event or it was not recorded.
- `FeelingItInstructionsButton` (18) and `FeelingItInstructionsNoButton` (19) counts are imbalanced and sum to 37, exceeding the number of subjects, indicating some subjects may have received both instruction types or events were duplicated.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
