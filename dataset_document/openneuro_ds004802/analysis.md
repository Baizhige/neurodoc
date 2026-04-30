# Loneliness in the Brain: Distinguishing Between Hypersensitivity and Hyperalertness (Pilot)

**Dataset**: `openneuro_ds004802` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004802
**Category**: High-level Mental | **Subjects**: 79 | **Files (Completed)**: 79 | **Channels**: 73 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

A pilot EEG study investigating the neural underpinnings of loneliness by contrasting social hypersensitivity (amplified neural responses to social stimuli) and hyperalertness (heightened attention to potential social threats). Participants viewed emotional face stimuli (angry, happy, neutral) in a roving oddball paradigm while EEG was recorded at 73 channels with a 512 Hz sampling rate. Trigger codes encode stimulus type, emotional valence, and repetition position within roving sequences (deviant first presentation vs repeated standard presentations). Code event_20 (white fixation cross, 49,566 occurrences) dominates the event structure and serves as a high-frequency inter-trial fixation signal.

## File Scan Result

> **Kernel SHA256**: `969ccec64d6022cd0426dc183d1f2e496ca601c022defefb2d85286e29971e8b`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_100` | 5 | admin | raw | System/trigger event 100 |
| `event_101` | 2 | admin | raw | System/trigger event 101 |
| `event_11` | 148 | event | raw | Trial phase onset: stimulus presentation (condition variant 11) |
| `event_111` | 4083 | event | raw | Space bar button press |
| `event_12` | 184 | event | raw | Trial phase onset: stimulus presentation (condition variant 12) |
| `event_127` | 135 | admin | raw | System/trigger event 127 |
| `event_13` | 257 | event | raw | Trial phase onset: stimulus presentation (condition variant 13) |
| `event_14` | 148 | event | raw | Trial phase onset: stimulus presentation (condition variant 14) |
| `event_15` | 110 | event | raw | Trial phase onset: stimulus presentation (condition variant 15) |
| `event_16` | 258 | event | raw | Trial phase onset: stimulus presentation (condition variant 16) |
| `event_17` | 74 | event | raw | Trial phase onset: stimulus presentation (condition variant 17) |
| `event_20` | 49566 | event | raw | White fixation cross |
| `event_200` | 256 | event | raw | Feedback screen during training |
| `event_21` | 2690 | event | raw | White fixation cross, angry face, first presentation (deviant) |
| `event_22` | 2612 | event | raw | White fixation cross, angry face, second presentation (standard) |
| `event_23` | 2613 | event | raw | White fixation cross, angry face, third presentation (standard) |
| `event_24` | 2761 | event | raw | White fixation cross, angry face, fourth presentation (standard) |
| `event_25` | 2764 | event | raw | White fixation cross, angry face, fifth presentation (standard) |
| `event_254` | 8 | admin | raw | System marker or trigger sync event |
| `event_255` | 1 | admin | raw | System marker or trigger sync event |
| `event_26` | 1955 | event | raw | White fixation cross, angry face, sixth presentation (standard) |
| `event_27` | 919 | event | raw | White fixation cross, angry face, seventh presentation (standard) |
| `event_28` | 147 | event | raw | White fixation cross, angry face, eighth presentation (standard) |
| `event_30` | 18 | event | raw | Trial phase onset: stimulus presentation (condition variant 30) |
| `event_31` | 220 | event | raw | Trial phase onset: stimulus presentation (condition variant 31) |
| `event_32` | 73 | event | raw | Trial phase onset: stimulus presentation (condition variant 32) |
| `event_33` | 147 | event | raw | Trial phase onset: stimulus presentation (condition variant 33) |
| `event_34` | 74 | event | raw | Trial phase onset: stimulus presentation (condition variant 34) |
| `event_35` | 219 | event | raw | Trial phase onset: stimulus presentation (condition variant 35) |
| `event_36` | 110 | event | raw | Trial phase onset: stimulus presentation (condition variant 36) |
| `event_41` | 2125 | event | raw | White fixation cross, happy face, first presentation (deviant) |
| `event_42` | 2277 | event | raw | White fixation cross, happy face, second presentation (standard) |
| `event_43` | 2205 | event | raw | White fixation cross, happy face, third presentation (standard) |
| `event_44` | 2276 | event | raw | White fixation cross, happy face, fourth presentation (standard) |
| `event_45` | 2136 | event | raw | White fixation cross, happy face, fifth presentation (standard) |
| `event_46` | 1614 | event | raw | White fixation cross, happy face, sixth presentation (standard) |
| `event_47` | 953 | event | raw | White fixation cross, happy face, seventh presentation (standard) |
| `event_48` | 255 | event | raw | White fixation cross, happy face, eighth presentation (standard) |
| `event_51` | 37 | event | raw | Trial phase onset: stimulus presentation (condition variant 51) |
| `event_52` | 74 | event | raw | Trial phase onset: stimulus presentation (condition variant 52) |
| `event_53` | 185 | event | raw | Trial phase onset: stimulus presentation (condition variant 53) |
| `event_54` | 185 | event | raw | Trial phase onset: stimulus presentation (condition variant 54) |
| `event_55` | 74 | event | raw | Trial phase onset: stimulus presentation (condition variant 55) |
| `event_56` | 111 | event | raw | Trial phase onset: stimulus presentation (condition variant 56) |
| `event_57` | 74 | event | raw | Trial phase onset: stimulus presentation (condition variant 57) |
| `event_61` | 2177 | event | raw | White fixation cross, neutral face, first presentation (deviant) |
| `event_62` | 2140 | event | raw | White fixation cross, neutral face, second presentation (standard) |
| `event_63` | 2030 | event | raw | White fixation cross, neutral face, third presentation (standard) |
| `event_64` | 2025 | event | raw | White fixation cross, neutral face, fourth presentation (standard) |
| `event_65` | 2140 | event | raw | White fixation cross, neutral face, fifth presentation (standard) |
| `event_65536` | 1 | admin | raw | Data stream marker or system boundary |
| `event_65556` | 1 | admin | raw | Data stream marker or system boundary |
| `event_65790` | 7 | admin | raw | Data stream marker or system boundary |
| `event_66` | 1549 | event | raw | White fixation cross, neutral face, sixth presentation (standard) |
| `event_67` | 699 | event | raw | White fixation cross, neutral face, seventh presentation (standard) |
| `event_68` | 294 | event | raw | White fixation cross, neutral face, eighth presentation (standard) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class emotional face valence (angry vs happy)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`event_21`, `event_41`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_21 | 0 | angry face, first presentation (deviant) |
  | event_41 | 1 | happy face, first presentation (deviant) |
- **Evidence**:
  - 10.31219/osf.io/j5v9b — Reference explicitly describes angry vs happy face classification in roving oddball design using first presentation (deviant) events
  - task-roddball_events.json — event_21: "white/angry/deviant/1" (angry face first presentation), event_41: "white/happy/deviant/1" (happy face first presentation)
  - events.tsv samples — confirmed presence of event_21 (2690 occurrences) and event_41 (2125 occurrences) across subjects
- **Notes**: Using only first presentation (deviant) events per reference design. Neutral face events (event_61+) excluded to match the 2-class angry vs happy valence classification described in the reference. Epoch window (-200ms to 800ms) covers standard face-processing ERP components (N170, EPN, LPP) following face onset.

### Classical Task 2: 2-class emotional face valence with repetition (angry 1st vs happy 1st)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`event_21`, `event_41`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_21` | 0 | angry face, first presentation (deviant) |
  | `event_41` | 1 | happy face, first presentation (deviant) |
- **Evidence**:
  - 10.31219/osf.io/j5v9b — Reference mentions 'first vs fifth repetition' as key contrast; this task uses only deviant/first presentations (event_21 angry vs event_41 happy) for purest test of valence without repetition confound
  - task-roddball_events.json — Defines `white/angry/deviant/1` (event_21) and `white/happy/deviant/1` (event_41) as first presentation deviant conditions
  - sub-19601, sub-AS events.tsv — Confirm face stimulus events in 20s (angry) and 40s (happy) ranges present in actual data
- **Notes**: Standard ERP epoch for face-evoked responses; deviant responses expected in N170 (~170ms) and P300 (~300-600ms) time windows. Both event_21 and event_41 have substantial trial counts (2690 and 2125 respectively) ensuring adequate statistical power.

### Classical Task 3: 2-class repetition effect (1st vs 5th angry)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`event_21`, `event_25`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_21` | 0 | angry face, first presentation (deviant) |
  | `event_25` | 1 | angry face, fifth presentation (standard) |
- **Evidence**:
  - 10.31219/osf.io/j5v9b — Reference explicitly contrasts first vs fifth repetition. Using angry face stream: event_21 (1st/deviant) vs event_25 (5th/standard). Tests repetition suppression/sensitization within same valence. N=2 classes with clear repetition distinction.
- **Notes**: ERP repetition effect comparing 1st (novel/deviant) vs 5th (repeated/standard) presentation of angry faces in a roving oddball paradigm. The 1-second epoch (-200 to 800 ms) captures the N170 and subsequent late positive components where repetition effects are typically observed.

### Classical Task 4: 2-class repetition effect (1st vs 5th happy)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`event_41`, `event_45`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_41` | 0 | White fixation cross, happy face, first presentation (deviant) |
  | `event_45` | 1 | White fixation cross, happy face, fifth presentation (standard) |
- **Evidence**:
  - 10.31219/osf.io/j5v9b — Parallel to angry repetition contrast. Using happy face stream: event_41 (1st/deviant) vs event_45 (5th/standard). Tests whether repetition effects generalize across positive valence. N=2 classes.
  - task-roddball_events.json — Defines `white/happy/deviant/1` (event_41) and `white/happy/standard/5` (event_45) levels confirming happy face repetition paradigm structure.
  - events.tsv (sub-10522, sub-19601, sub-AS) — Observed event_41 and event_45 trigger values in actual recordings.
- **Notes**: Epoch window matches angry repetition contrast (Task 3) for direct comparability across valence conditions. Both event IDs confirmed in events.json with explicit happy face labels.

### Potential Task 1: 3-class face valence (angry vs happy vs neutral)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`event_21`, `event_41`, `event_61`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `event_21` | 0 | angry face, first presentation (deviant) |
  | `event_41` | 1 | happy face, first presentation (deviant) |
  | `event_61` | 2 | neutral face, first presentation (deviant) |
- **Evidence**:
- **Notes**: Extends the classical angry-vs-happy deviant comparison to a 3-class problem by including neutral faces (event_61). All three event types represent first presentations (deviants) in the roving oddball sequence, ensuring balanced novelty status across classes. Epoch window inferred from standard face ERP literature; values marked with *.

### Potential Task 2: 2-class oddball detection (deviant vs standard)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 0.8 s *, target_events = [`event_21`, `event_22`, `event_41`, `event_42`, `event_61`, `event_62`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | event_21, event_41, event_61 | 0 | deviant (first presentation) |
  | event_22, event_42, event_62 | 1 | standard (second presentation) |
- **Evidence**:
  - task-roddball_events.json — Defines event levels: white/happy/deviant/1, white/angry/deviant/1, white/neutral/deviant/1 for first presentations; white/happy/standard/2, white/angry/standard/2, white/neutral/standard/2 for second presentations
  - sub-19601, sub-AS events.tsv — Confirm presence of event_21-28, event_41-48, event_61-68 ranges in actual recordings
  - eeg.json — TaskDescription confirms roving oddball with happy/angry/neutral face stimuli
- **Notes**: Pools across all three emotional valences (angry, happy, neutral) to create a generic oddball detection task. Deviant class (y=0) comprises first presentations (event_21, event_41, event_61); standard class (y=1) comprises second presentations (event_22, event_42, event_62). The roving oddball structure means each face identity becomes its own standard after the first presentation, making this a pure sequential-position oddball contrast regardless of stimulus content.

### Potential Task 3: loneliness score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `loneliness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | loneliness | 27–63 (score) | UCLA Loneliness Scale total score; complete across N=38 subjects |
- **Evidence**:
  - participants.tsv — loneliness column complete (38/38), numeric scores ranging 27–63
- **Notes**: Subject-level trait regression from continuous resting-state-like EEG segments. Segmentation chosen because no discriminating event structure is needed for predicting a stable trait measure; each segment inherits the subject's loneliness score as the regression target. Epoch parameters inferred from SKILL defaults for subject-level regression tasks.

### Potential Task 4: Diagnosis Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `diagnosis`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | diagnosis | No | 0 | No clinical diagnosis |
  | diagnosis | Yes | 1 | Clinical diagnosis present |
  | diagnosis | Don't know | 2 | Diagnosis unknown |
- **Evidence**:
- **Notes**: Subject-level classification from resting-state continuous EEG segments. The 'Don't know' category is sparse (N~1 of 38) but retained as a distinct class per the grounded data. Segmentation parameters inferred from SKILL defaults for clinical biomarker discovery tasks with subject-level labels.

### Potential Task 5: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | gender | Female | 0 | Female participant |
  | gender | Male | 1 | Male participant |
  | gender | Other | 2 | Other gender identity |
- **Evidence**:
- **Notes**: Three-class demographic classification from resting-state EEG segments. The 'Other' category has N=1 (sub-20348), creating a severe class imbalance; this task is included for completeness as a grounded label exists in participants.tsv, but practical utility is limited. Standard 2-second windows with 50% overlap are used for demographic prediction from continuous EEG. Scientific validity of sex/gender classification from EEG is debated; this task serves as a benchmark only.

### Potential Task 6: Age Regression from Birth Year
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `birth_year`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | birth_year | 1968–2001 (year) | Numeric birth year from participants.tsv; approximate age can be derived as recording year minus birth_year. 37/38 subjects have complete data. |
- **Evidence**:
  - participants.tsv — birth_year column present with values 1968–2001, 37/38 complete
- **Notes**: Segmentation-based resting-state style task using continuous EEG. The birth_year field is a native participants.tsv column (archetype B3, Meta Level = raw). While the dataset contains task data (RovingOddball), segmentation without event targeting allows treating the continuous recording as a source for brain-age prediction benchmarks. The label is birth_year itself; a kernel could optionally derive approximate age if recording year is known from dataset metadata.

### Potential Task 7: 2-class high vs low loneliness
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `loneliness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | loneliness | ≤ median (≤45) | 0 | low loneliness |
  | loneliness | > median (>45) | 1 | high loneliness |
- **Evidence**:
- **Notes**: Dichotomized from continuous loneliness scores via median split (N=38, range 27-63). The median of 45 creates balanced groups (~19 per group). This is a B3 info-native classification derived from the same `loneliness` field used in the continuous regression variant, applying a threshold transform to produce binary labels. Segmentation-based epochs are used since this is a resting-state/trait prediction paradigm without task-event structure.

### Potential Task 8: 2-class diagnosed vs not diagnosed
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `diagnosis`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | diagnosis | No | 0 | Not diagnosed |
  | diagnosis | Yes | 1 | Diagnosed |
- **Evidence**:
  - participants.tsv — diagnosis column contains categorical values [No, Yes, Don't know] across all 38 subjects; complete with no missing values
- **Notes**: Subjects with 'Don't know' in the diagnosis field (e.g., sub-19604) must be excluded by the kernel during label extraction to produce a clean binary classification. This is a B3 archetype using native participants.tsv info field with segmentation-based epoching for resting-state clinical prediction. The 2-second segments with 50% overlap follow standard biomarker study conventions for clinical EEG prediction.

## Data Quality Notes

- Subject metadata is highly incomplete: only 38 of 79 subjects have usable participants.tsv entries (birth_month, birth_year, diagnosis, loneliness), while the remaining 41 subjects lack demographic and trait data entirely.
- `subject_age` is completely missing across all subjects; age must be approximated from `birth_year` where available (37/38 subjects), but recording year is not explicitly documented.
- `device` field is completely missing — EEG amplifier and electrode system (likely Biosemi given 73 channels) is undocumented in dataset metadata.
- Event code meanings for condition variants 11-17, 30-36, and 51-57 are unknown and not described in accompanying task documentation; these may represent practice trials, catch trials, or auxiliary conditions.
- The extremely high count of event_20 (49,566 occurrences, ~84% of all events) indicates dense fixation cross presentation that may complicate baseline correction and require careful epoch rejection around overlapping events.
- Repetition counts decay non-monotonically across positions (e.g., angry face: 2690 → 2612 → 2613 → 2761 → 2764 → 1955 → 919 → 147), suggesting possible trial attrition, participant disengagement, or adaptive stopping rules in later repetitions.
- Several high-value event IDs (65536, 65556, 65790) appear as system boundary markers with very low counts; these may indicate data stream resets or synchronization artifacts requiring kernel-level handling.
- Only 38 subjects have complete loneliness scores and diagnosis labels, severely limiting statistical power for trait-based regression and classification tasks relative to the full 79-subject EEG sample.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
