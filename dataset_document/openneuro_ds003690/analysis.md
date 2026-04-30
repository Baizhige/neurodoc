# EEG, ECG and Pupil Data from Young and Older Adults: Rest and Auditory Cued Reaction Time Tasks

**Dataset**: `openneuro_ds003690` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003690
**Category**: Sensory/Response | **Subjects**: 75 | **Files (Completed)**: 375 | **Channels**: 66 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Young and older adults performed auditory-cued simple reaction time and go/no-go tasks to investigate age-related differences in neural and physiological activity. An auditory warning cue preceded each trial; participants pressed a button to go stimuli and withheld responses to no-go stimuli. Error feedback tones were provided after slow responses or commission errors. The study also included a passive resting-like condition with only cue tones and no motor responses. Data were acquired with simultaneous EEG, ECG, and pupillography to examine how aging affects preparatory neural activity, inhibitory control, autonomic regulation, and pupil dilation responses.

## File Scan Result

> **Kernel SHA256**: `ae1771744b1e9be52e1185e15ec5a571439a12368d20c2faf981c8daf98a2cba`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 20250 | event | raw | Auditory temporal cue (warning stimulus) presented at the beginning of each trial |
| `10` | 375 | admin | raw | Task end |
| `11` | 99 | event | raw | Error feedback tone presented after the participants committed an error |
| `2` | 13500 | event | raw | Auditory go stimulus |
| `3` | 254 | event | raw | Error feedback tone signaling slow responses |
| `4` | 1500 | event | raw | Auditory no-go stimulus presented only in go/no-go task condition |
| `5` | 13525 | event | raw | Keypress |
| `6` | 88 | event | raw | Keypress after no-go stimulus - error of commission |
| `7` | 88 | event | raw | Error feedback tone presented after the participants committed an error - responded after cue presentation |
| `9` | 320 | admin | raw | Task start |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 3-class go/no-go response inhibition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 6.0 s, target_events = [`1`, `2`, `4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 1 | 0 | cue (auditory temporal cue / warning stimulus) |
  | 2 | 1 | go (auditory go stimulus) |
  | 4 | 2 | no-go (auditory no-go stimulus) |
- **Evidence**:
  - 10.1016/j.neurobiolaging.2018.09.028 — Primary paradigm: cued auditory go/no-go and simple RT tasks with 75 subjects (36 young, 39 older); cue-locked epochs with baseline correction; event IDs 1 (cue), 2 (go), 4 (no-go) used for 3-class classification
  - 10.1016/j.neuroimage.2019.06.004 — Same dataset and paradigm; ERP and beta oscillation analysis; excludes error of commission trials (6,7,11) from main classification
- **Notes**: The three target classes correspond to the three trial types in the go/no-go task: cue-only trials (16% of trials per README, where no target follows), go trials (cue→go sequence), and no-go trials (cue→no-go sequence). Epochs are locked to the cue onset (event 1) for all three classes, with tmin=-0.2s allowing baseline correction and tmax=6.0s covering the full ERP and beta oscillation range as specified in the primary references. Error trials (events 6, 7, 11) are excluded from this classification task.

### Classical Task 2: 2-class go vs no-go inhibition
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`2`, `4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 2 | 0 | auditory go stimulus |
  | 4 | 1 | auditory no-go stimulus |
- **Evidence**:
  - 10.1016/j.neurobiolaging.2018.09.028 — Age-related differences in ERPs during auditory cued reaction time tasks; analyzes go/no-go discrimination as core contrast
  - 10.1016/j.neuroimage.2019.06.004 — Neural correlates of anticipatory cardiac deceleration and perceptual decision-making; includes go/no-go task analysis
- **Notes**: Epoch window inferred from standard go/no-go ERP literature to capture N200/P300 inhibitory components. Stimulus-locked epochs on auditory go (2) and no-go (4) events exclude cue-only trials as specified in paradigm.

### Classical Task 3: 2-class simple RT detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 2.0 s *, target_events = ['1', '2']`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1` | 0 | Auditory temporal cue (warning stimulus) |
  | `2` | 1 | Auditory go stimulus |
- **Evidence**:
  - 10.1016/j.neurobiolaging.2018.09.028 — Simple RT task condition; event IDs 1 (cue) and 2 (go) used in cued simple reaction time paradigm with 100 cue-go trials and 20 cue-only trials per run
  - 10.1016/j.neuroimage.2019.06.004 — Simple RT task explicitly contrasted with go/no-go; cue-locked and stimulus-locked epochs valid for ERP analysis
- **Notes**: Classification distinguishes between the two trial phases in the simple RT task: the warning cue (event 1) versus the imperative go stimulus (event 2). The 2-second window captures the typical cue-to-go interval and post-go ERP components. Epoch timing inferred from standard ERP windows for cued reaction time paradigms; actual cue-go interval varies but 2s covers the typical simple RT response period.

### Classical Task 4: Age Group Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | group | Young | 0 | Young adult group (age ~19-35) |
  | group | Older | 1 | Older adult group (age ~55-70) |
- **Evidence**:
  - 10.1016/j.neurobiolaging.2018.09.028 — Primary group comparison of young (N=36) vs older (N=39) adults in auditory cued reaction time tasks with EEG/ERP analysis
  - 10.1016/j.neuroimage.2019.06.004 — Neural correlates of anticipatory cardiac deceleration analyzed by young vs older group, same dataset
- **Notes**: Segmentation-based epochs with 2-second non-overlapping windows; group label from participants.tsv is broadcast to all epochs per subject. This is a subject-level classification task since no trial-level event discriminates age groups. Segment length inferred from resting/continuous data paradigm with task periods.

### Classical Task 5: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–70.0 (years) | Continuous chronological age from participants.tsv; N=75 complete |
- **Evidence**:
  - 10.1016/j.neurobiolaging.2018.09.028 — Age-related differences in ERPs and pupillary responses; age treated as continuous covariate in analyses
  - 10.1016/j.neuroimage.2019.06.004 — Neural correlates of anticipatory cardiac deceleration; age as continuous predictor of neural dynamics
- **Notes**: Segmentation-based regression with 2-second non-overlapping windows. Age is a native participants.tsv column (B3 archetype, raw meta level). The kernel simply reads the pre-existing `age` field per subject and assigns it to all epochs from that subject. No derivation required.

### Potential Task 1: Sex Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Subject-level classification using demographic sex information from participants.tsv. The dataset contains 60 Female and 15 Male participants (4:1 class imbalance). Segmentation creates 2-second non-overlapping epochs from continuous EEG recordings, with all epochs from a given subject receiving the same sex label. This is a potential (not classical) task as no published analysis explicitly examines sex classification from EEG in this dataset.

### Potential Task 2: MoCA cognitive score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `MoCA`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | MoCA | 24–30 (score) | Montreal Cognitive Assessment total score; 74/75 participants complete (one missing); higher scores indicate better cognitive function |
- **Evidence**:
  - participants.tsv — MoCA column present with values [29, 27, 26, 28, 24, ...]; 74/75 complete; dtype=numeric
  - dataset_description.json — References Ribeiro & Castelo-Branco 2019 aging studies, establishing cognitive assessment context for young vs older adult comparison
- **Notes**: Segmentation-based regression task using 2-second non-overlapping windows to predict MoCA cognitive screening score from resting/task EEG. The MoCA score is a native participants.tsv column (archetype B3), requiring no kernel derivation. Default 2-second segment length used due to lack of paradigm-specific epoch constraints for continuous score prediction.

### Potential Task 3: Education Years Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `education_years`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | education_years | 12–17 (years) | Continuous demographic variable from participants.tsv; used as regression target for cognitive reserve proxy |
- **Evidence**:
  - participants.tsv — `education_years` column complete (N=75), numeric dtype, sample values [14, 15, 12, 16, 17]
- **Notes**: Segmentation-based regression with no event anchoring. Each 2-second EEG segment is labeled with the participant's education years from participants.tsv. No kernel derivation needed; label is natively available in BIDS info metadata.

### Potential Task 4: Smoking status classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `smoker`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | smoker | No | 0 | Non-smoker |
  | smoker | Yes | 1 | Smoker |
- **Evidence**:
  - participants.tsv — `smoker` column with complete Yes/No values for all 75 participants; sample values [No, Yes]
- **Notes**: Subject-level binary classification using segmentation epochs. The 2-second segment length is inferred from the candidate's epoch_hint as a default for subject-level labels with no event-locked structure. Each segment from a participant receives the same smoker label. This is a potential (not classical) task as it uses a demographic variable rather than a task-related neural paradigm.

### Potential Task 5: Handedness Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `hand_laterality`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | hand_laterality | R | 0 | Right-handed |
  | hand_laterality | L | 1 | Left-handed |
  | hand_laterality | R? | 0 | Right-handed (uncertain, merged with R) |
- **Evidence**:
- **Notes**: Subject-level classification using handedness from participants.tsv. The R? value (uncertain right-handed) is merged with R (y=0) to maintain a binary classification. This is a native info field requiring no kernel derivation. Segmentation epochs are used since handedness is a subject-level trait not tied to specific events. Class imbalance expected (mostly right-handed participants).

### Potential Task 6: Task Order Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `task_order`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | task_order | SRT_GNG | 0 | Simple reaction time task first, go/no-go second |
  | task_order | GNG_SRT | 1 | Go/no-go task first, simple reaction time second |
- **Evidence**:
- **Notes**: Potential task using counterbalanced task order from participants.tsv. Binary classification of whether participants performed SRT first or GNG first. Segment-level classification with 2-second non-overlapping windows across all EEG data; each segment inherits the participant's task_order label. Low expected neural discriminability since order is a between-subjects design factor rather than an event-related manipulation, but may capture state/trait differences associated with order effects or session dynamics.

### Potential Task 7: Pupil Data Availability Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `pupil_data`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | pupil_data | No | 0 | No pupil data available |
  | pupil_data | Yes | 1 | Pupil data successfully recorded |
- **Evidence**:
  - participants.tsv — `pupil_data` column with complete Yes/No coverage across all 75 participants (sample: sub-AB4=Yes, sub-AB6=No)
  - dataset_description.json — Confirms pupillography acquired with iView X Hi-Speed 1250 system from SMI, indicating pupil data was intended but not always successfully recorded
- **Notes**: Binary classification task using participants.tsv `pupil_data` as a proxy for data quality or technical recording success. The 2-second segmentation with no overlap provides uniform epoch extraction across all recordings, with the label determined per-participant from the info file. This is a B3 archetype (native info column, Meta Level = raw).

### Potential Task 8: Resting State Segmentation with Age Group
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | group | Young | 0 | Young adult group (age ~19-35) |
  | group | Older | 1 | Older adult group (age ~60-70) |
- **Evidence**:
  - participants.tsv — group column with values Young/Older (N=36 Young, N=39 Older)
  - README — "passive task - 4 minutes acquired at the beginning of the session" with only cue tones, approximating low-demand resting-like state
- **Notes**: Segmentation approach applied to passive listening runs where only cue tones (event 1) and task start/end (events 9/10) occur, with no motor responses required. This creates non-overlapping 2-second windows for analysis of spontaneous/ongoing EEG activity differences between age groups. Archetype C because age group labels come from participants.tsv info field with no discriminating event trigger for the classification target.

### Potential Task 9: Resting State Segmentation with Continuous Age
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 19.0–70.0 (years) | Continuous chronological age from participants.tsv; used for regression on segmented resting-state/passive-task EEG |
- **Evidence**:
- **Notes**: Segmentation-based task with no event anchoring. Uses standard 2-second non-overlapping windows (overlap=0.0) on continuous passive/resting-state recordings. Age is a native participants.tsv column (Meta Level = raw). The passive task consists of 4 minutes of auditory cue listening with no motor response required, serving as a resting-state proxy. Regression target captures fine-grained age-related differences in spectral power or connectivity patterns across the 19-70 year lifespan range.

## Data Quality Notes

- `device` field is completely missing from info metadata; equipment details must be inferred from dataset_description.json or README.
- `MoCA` field has one missing value (74/75 complete); any task using this field should handle the missing entry.
- Event ID meanings differ between the draft File Scan Result and the authoritative File Scan Result block; the authoritative block uses more detailed descriptions and reclassifies events 10 and 9 as `admin` type rather than `event` type.
- Event counts show substantial imbalance: cue events (20,250) greatly outnumber no-go events (1,500), which will affect class balance in go/no-go classification tasks.
- Error of commission events (6) and associated error feedback tones (7, 11) are rare (88-99 occurrences); exclusion from main analyses as noted in task definitions is appropriate.
- The `hand_laterality` field contains an ambiguous `R?` value requiring merge with `R` for binary classification.
- Sex classification has severe class imbalance (60 F vs 15 M).
- Pupil data availability is uneven across participants (Yes/No in `pupil_data`); this may correlate with other factors but is recorded as a binary field.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
