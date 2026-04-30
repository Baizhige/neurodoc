# Resting-State EEG Dataset for Sleep Deprivation

**Dataset**: `openneuro_ds004902` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004902
**Category**: Biological State | **Subjects**: 71 | **Files (Completed)**: 218 | **Channels**: 61 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Resting-state EEG recordings with eyes open and eyes closed were conducted under two conditions: normal sleep and 24-hour sleep deprivation. The study investigates how sleep loss modulates spontaneous brain activity. Subjects participated in two sessions (normal sleep vs sleep-deprived) in a counterbalanced within-subject design. Files are split by condition (eyesopen/eyesclosed) with 5-minute continuous blocks.

## File Scan Result

> **Kernel SHA256**: `853b689d3ac3a4b842f90ee5a6bfcb311ac1e5d90547a4b1422d93c08fcf1930`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 33` | 60 | event | raw | Unknown trigger marker - frequent occurrence suggests possible recording segment or status marker |
| `S 44` | 7 | event | raw | Unknown trigger marker |
| `S 45` | 7 | event | raw | Unknown trigger marker |
| `S 55` | 7 | event | raw | Unknown trigger marker |
| `S 66` | 7 | event | raw | Unknown trigger marker |
| `S119` | 7 | event | raw | Unknown trigger marker |
| `boundary` | 14 | admin | raw | Data boundary marker - indicates discontinuity or epoch boundary in continuous recording |
| `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}` | 76 | event | super | Trial phase onset: eyes-closed resting-state recording condition |
| `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}` | 142 | event | super | Trial phase onset: eyes-open resting-state recording condition |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: eyes open vs eyes closed classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 5 s *, target_events = [`super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}`, `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_open"}` | 0 | eyes-open resting-state condition |
  | `super: {"sleep_condition": "unknown", "eyes_condition": "eyes_closed"}` | 1 | eyes-closed resting-state condition |
- **Evidence**:
- **Notes**: The 'super' event annotations with eyes_condition metadata are confirmed trial phase onsets from the dataset's pre-scan annotations, directly mapping to the two resting-state conditions (eyes_open: 142 occurrences, eyes_closed: 76 occurrences). The 5-second epoch window is inferred as a conservative estimate for stable resting-state brain activity, well within the 300-second continuous recording blocks. No explicit epoch timing was found in available references.

### Potential Task 1: Age Regression from Resting-State EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | Age | 18–22 (years) | Chronological age from participants.tsv; complete for all 71 participants. Applied to all resting-state segments regardless of eyes-open/closed condition or sleep deprivation state. |
- **Evidence**:
  - participants.tsv — Complete Age column with range 18-22 years (sample: 22, 21, 19, 18, 20).
- **Notes**: Standard neurodevelopmental/neuroaging regression task predicting chronological age from spontaneous EEG features. The 4-second non-overlapping segmentation is a default choice for resting-state analysis as no specific epoch length is established for age prediction in this dataset. The task uses all available resting-state EEG segments (both eyes-open and eyes-closed conditions, both normal sleep and sleep deprivation sessions) since age is a stable participant-level demographic variable independent of recording condition.

### Potential Task 2: Gender Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | M | 0 | Male |
  | Gender | F | 1 | Female |
- **Evidence**:
  - participants.tsv — 71 participants with complete Gender column (M/F values); binary sex classification from resting-state EEG segments
- **Notes**: Segmentation-based task: 4-second non-overlapping windows from continuous 5-minute resting-state recordings (eyes open/closed). Gender is a native participants.tsv column with complete coverage, enabling subject-level stratified classification. The model must learn sex-differentiating spectral or connectivity patterns from spontaneous EEG.

### Potential Task 3: Session Order Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `SessionOrder`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | SessionOrder | NS->SD | 0 | Normal sleep first, sleep deprivation second |
  | SessionOrder | SD->NS | 1 | Sleep deprivation first, normal sleep second |
- **Evidence**:
  - participants.tsv — `SessionOrder` column with complete coverage (71/71), values {NS->SD, SD->NS} indicating counterbalanced presentation order across participants
- **Notes**: Classification task distinguishes whether a recording comes from a participant who had normal sleep first (NS->SD) versus sleep deprivation first (SD->NS). This captures potential order/carryover effects in resting-state EEG. Segmentation-based epochs (4s non-overlapping) are used since this is a resting-state dataset without trial structure. The label is drawn directly from participants.tsv, requiring no kernel derivation.

### Potential Task 4: Positive Affect Regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `PANAS_P_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | PANAS_P_NS | 10–50 (score) | PANAS Positive Affect subscale score during Normal Sleep session; complete for all 71 participants |
- **Evidence**:
  - participants.tsv — PANAS_P_NS column contains complete positive affect scores for all 71 participants in normal sleep session (sample values: 37, 28, 27)
  - dataset_description.json — Keywords include "mood"; dataset described as resting-state EEG with mood state information
  - README — Dataset provides information on participants' mood states alongside resting-state EEG data
- **Notes**: Standard 4-second segmentation applied to continuous resting-state EEG (eyes-closed, 300s duration) for subject-level regression. PANAS Positive Affect scores are native participant-level metadata requiring no kernel derivation.

### Potential Task 5: Positive Affect Regression SD
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PANAS_P_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | PANAS_P_SD | 10–50 (score) | Positive Affect subscale of PANAS after sleep deprivation; 68/71 participants available |
- **Evidence**:
- **Notes**: Regression task predicting positive mood state (PANAS Positive Affect) after sleep deprivation from resting-state EEG segments. Uses default 4-second non-overlapping segmentation consistent with primary analysis. Enables direct comparison with Task 6 (PANAS_P_NS) for condition effects. The PANAS_P_SD field is a native participants.tsv column with near-complete coverage (68/71).

### Potential Task 6: Negative Affect Regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PANAS_N_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | PANAS_N_NS | 10–29 (score) | PANAS Negative Affect subscale score during Normal Sleep session. Higher values indicate greater negative mood state. Complete for all 71 participants. |
- **Evidence**:
- **Notes**: Resting-state EEG segmentation with 4-second non-overlapping windows. The PANAS_N_NS score is a participant-level continuous measure (negative affect) collected during the normal sleep session, predicted from spectral features of resting-state EEG segments. No event markers are used for epoching; the entire continuous recording is segmented.

### Potential Task 7: Negative Affect Regression (Sleep Deprived)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PANAS_N_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | PANAS_N_SD | 10–29 (score) | PANAS Negative Affect subscale after sleep deprivation; higher values indicate greater negative mood. 68/71 subjects have valid data. |
- **Evidence**:
  - `participants.tsv` — PANAS_N_SD column contains negative affect scores after sleep deprivation (68/71 complete)
  - `README` — Dataset provides mood state information including sleep deprivation effects
  - `dataset_description.json` — Keywords include "sleep deprivation" and "mood"
- **Notes**: Resting-state EEG segmentation (4-second non-overlapping windows) used to predict negative affect after sleep deprivation. The PANAS_N_SD score is a validated psychological measure drawn directly from participants.tsv. No kernel derivation needed—native info field.

### Potential Task 8: PSQI global score regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PSQI_GlobalScore`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | PSQI_GlobalScore | 0–21 (score) | Pittsburgh Sleep Quality Index global score; higher = worse sleep quality; 66/71 participants have data |
- **Evidence**:
- **Notes**: Segmentation-based regression predicting PSQI global score from resting-state EEG features. Uses 4-second non-overlapping windows (default for resting-state feature extraction). PSQI_GlobalScore is a native participants.tsv column with 93% completeness (66/71).

### Potential Task 9: Trait Aggression Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `Buss_Perry`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Buss_Perry | 29–104 (score) | Buss-Perry Aggression Questionnaire total score; 55/71 participants (77% complete); higher scores indicate greater trait aggression |
- **Evidence**:
  - participants.tsv — Buss_Perry column contains numeric aggression questionnaire scores with 55/71 completeness
- **Notes**: Resting-state EEG segmentation with 4-second non-overlapping windows. The Buss-Perry score is a native participants.tsv column (B3 archetype, Meta Level = raw). No kernel derivation needed. Sample size limitation (55 subjects) should be noted for model power considerations.

### Potential Task 10: PVT mean RT regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Label Field**: `PVT_item2_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | PVT_item2_NS | ~286–393 (ms) | Mean reaction time on Psychomotor Vigilance Task, Normal Sleep condition. Incomplete coverage (31/71 participants). Higher values indicate poorer vigilance/sustained attention. |
- **Evidence**:
  - participants.tsv — PVT_item2_NS column contains mean RT values (ms) for NS condition; sample values [303, 349, 327.5]
- **Notes**: Resting-state EEG segmentation with 4-second non-overlapping windows. PVT_item2_NS is a native participants.tsv column (archetype B3), so Meta Level = raw. The task predicts individual vigilance level from resting-state EEG features; PVT is the gold-standard measure for sleepiness-related sustained attention. Only 31/71 participants have this data, so model will need to handle missing labels.

### Potential Task 11: PVT mean RT regression SD
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PVT_item2_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | PVT_item2_SD | ~286–396 ms | Mean reaction time on PVT during sleep deprivation session; 37/71 participants have data. Lower values indicate faster responses/higher vigilance. |
- **Evidence**:
- **Notes**: Regression task predicting mean PVT reaction time during sleep deprivation from resting-state EEG segments. The 4-second segmentation with no overlap is a standard default for resting-state EEG analysis when no event structure guides epoching. Participants with missing PVT_item2_SD values will be excluded during target preparation. The PVT (Psychomotor Vigilance Task) is a well-established measure of sustained attention and vigilance; sleep deprivation characteristically increases mean RT, making this a meaningful behavioral target for EEG-based vigilance prediction.

### Potential Task 12: PVT lapses regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `PVT_item1_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | PVT_item1_NS | 0–? (count) | Number of attention lapses (RT > 500 ms) on Psychomotor Vigilance Task during Normal Sleep session; available for 31/71 participants |
- **Evidence**:
- **Notes**: Resting-state EEG segmentation into 4-second non-overlapping windows. Each segment inherits the participant-level PVT_item1_NS value as the regression target, predicting individual tendency for attention lapses from eyes-open/eyes-closed resting-state brain activity. The epoch parameters use default 4-second segmentation with no overlap as no task-specific timing constraints apply to continuous resting-state data.

### Potential Task 13: PVT lapses regression SD
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `PVT_item1_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | PVT_item1_SD | 0–7 (lapses) | Number of lapses on PVT during sleep-deprived session; available for 37/71 participants. Higher values indicate greater attention failure due to sleep deprivation. |
- **Evidence**:
- **Notes**: Regression task predicting individual differences in attention lapse susceptibility during sleep deprivation from resting-state EEG features. The PVT (Psychomotor Vigilance Task) is a standard sustained attention measure where lapses (reaction times > 500 ms) indicate microsleeps. Sleep deprivation is known to increase lapse frequency. The 4-second non-overlapping segmentation extracts stationary EEG features (e.g., power spectral density, connectivity) that may correlate with trait-like vulnerability to sleep-loss-induced attention failures. Label availability is partial (37/71), so the effective sample size is limited to participants with both EEG and PVT data in the sleep-deprived session.

### Potential Task 14: KSS sleepiness regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `KSS_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | KSS_NS | 1–9 (scale) | Karolinska Sleepiness Scale during Normal Sleep session; 1 = very alert, 9 = very sleepy; 33/71 participants have values |
- **Evidence**:
  - participants.tsv — KSS_NS column contains subjective sleepiness ratings (1-9 scale) for 33 of 71 participants in the normal sleep condition
  - README — Dataset provides information on participants' sleepiness and mood states alongside resting-state EEG
  - dataset_description.json — Keywords include "sleepiness"; dataset focuses on resting-state EEG for sleep deprivation research
- **Notes**: Regression task predicting subjective sleepiness level from resting-state EEG segments during the normal sleep (NS) session. The KSS_NS field is a native participants.tsv column requiring no kernel derivation. 4-second non-overlapping segmentation is used as a standard approach for resting-state EEG feature extraction. Only 33/71 participants have KSS_NS values, so the effective sample size is limited by this field's completeness.

### Potential Task 15: KSS Sleepiness Regression SD
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `KSS_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | KSS_SD | 1–9 (scale) | Karolinska Sleepiness Scale after sleep deprivation; 33/71 participants with values |
- **Evidence**:
  - participants.tsv — KSS_SD column contains subjective sleepiness ratings (1-9 scale) for sleep deprivation session
  - README — Dataset provides information on participants' sleepiness and mood states across normal sleep and sleep deprivation sessions
- **Notes**: Segmentation-based regression task predicting continuous KSS sleepiness score from resting-state EEG segments. The KSS_SD field is a native participants.tsv column (archetype B3) with incomplete coverage (33/71). Segmentation creates 4-second non-overlapping epochs from continuous resting-state recordings; all segments from a given participant share the same KSS_SD label value.

### Potential Task 16: SAI anxiety regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `SAI_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | SAI_NS | 20–80 (score) | State Anxiety Inventory score under Normal Sleep condition; available for 31/71 participants |
- **Evidence**:
  - participants.tsv — SAI_NS column contains state anxiety inventory scores for normal sleep session (31/71 complete)
  - README — dataset provides mood state information including anxiety measures alongside resting-state EEG
  - dataset_description.json — keywords include "mood"; study examines sleep deprivation effects on resting-state EEG and mood states
- **Notes**: Resting-state EEG segmentation into 4-second non-overlapping windows for regression against per-participant SAI_NS state anxiety score. The SAI_NS field is a native participants.tsv column (archetype B3), requiring no kernel derivation. Only participants with valid SAI_NS values will contribute labeled samples; others are excluded by the kernel's label-availability filter.

### Potential Task 17: SAI anxiety regression SD
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `SAI_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | SAI_SD | 20–80 (score) | State Anxiety Inventory score after sleep deprivation; incomplete coverage (31/71 participants) |
- **Evidence**:
- **Notes**: Resting-state EEG segmentation with 4-second non-overlapping windows. SAI_SD is a native participants.tsv column providing state anxiety scores after sleep deprivation session. The task predicts continuous anxiety levels from EEG features extracted during resting-state recordings (eyes open/closed). Participants with missing SAI_SD values will be excluded from training/evaluation.

### Potential Task 18: SSS Sleepiness Regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `SSS_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | SSS_NS | 1–7 (ordinal) | Stanford Sleepiness Scale during Normal Sleep session; higher = sleepier. Available for 38/71 participants. |
- **Evidence**:
- **Notes**: Regression task predicting subjective sleepiness from 4-second non-overlapping EEG segments during resting-state (eyes-open/eyes-closed) recordings. SSS_NS is a native participants.tsv column (archetype B3, Meta Level = raw). The SSS (Stanford Sleepiness Scale) is an alternative subjective sleepiness measure to KSS in this dataset, providing a 1–7 ordinal scale where 1 = feeling active and vital, 7 = almost in reverie. Segmentation is used since no task events correspond to sleepiness ratings; the rating was collected once per session.

### Potential Task 19: SSS Sleepiness Regression SD
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `SSS_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | SSS_SD | 1–7 (scale) | Stanford Sleepiness Scale after sleep deprivation; higher values indicate greater sleepiness. Available for 37/71 participants. |
- **Evidence**:
  - participants.tsv — SSS_SD column contains subjective sleepiness ratings on 1–7 Stanford Sleepiness Scale for sleep-deprived session (37/71 complete)
- **Notes**: Default 4-second non-overlapping segmentation applied to continuous resting-state EEG recordings. The SSS_SD score is a validated subjective measure of sleepiness where 1 = feeling active and vital, 7 = almost in reverie, cannot stay awake. Values are participant-level and will be broadcast to all epochs from the same subject/session.

### Potential Task 20: ATQ attention regression NS
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `ATQ_NS`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | ATQ_NS | 20–80 (score) | Attentional Control Scale (ATQ) score for Normal Sleep session; higher scores indicate better attention control. Incomplete coverage (27/71 participants). |
- **Evidence**:
  - participants.tsv — ATQ_NS column contains Attentional Control Scale scores for Normal Sleep session with numeric values (sample: 52, 44, 59)
- **Notes**: Exploratory regression task predicting individual differences in attention control from resting-state EEG features. The ATQ (Attentional Control Scale) is a self-report measure of attentional control capacity. Lower completeness (27/71) limits statistical power but the task remains viable for exploratory analysis. Segmentation-based epoching with 4-second non-overlapping windows applied to continuous resting-state recordings.

### Potential Task 21: ATQ Attention Regression Sleep Deprived
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `ATQ_SD`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | ATQ_SD | 25–75 (score) | Attentional Control Scale score under sleep deprivation; lower scores indicate poorer attention control; 25/71 complete |
- **Evidence**:
- **Notes**: Exploratory regression task predicting individual differences in attentional control (ATQ_SD) from resting-state EEG segments recorded during sleep deprivation. The ATQ (Attentional Control Scale) is a self-report measure; this task uses the sleep-deprived session score. Due to incomplete coverage (25/71), results should be interpreted with caution. Segmentation-based epoching with 4-second non-overlapping windows applied to continuous resting-state recordings.

### Potential Task 22: EQ Empathy Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Label Field**: `EQ`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|-------------|-------|
  | EQ | 0–80 (score) | Empathy Quotient self-report score; available for 56/71 participants (79%); higher scores indicate greater trait empathy |
- **Evidence**:
- **Notes**: Resting-state EEG segmentation into 4-second non-overlapping windows for regression prediction of trait empathy (EQ score). Uses all available resting-state segments from both eyes-open and eyes-closed conditions as unlabeled input features; the per-participant EQ score from participants.tsv serves as the regression target. Missing EQ values (15/71 participants) will be handled by the dataloader via sample exclusion.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
