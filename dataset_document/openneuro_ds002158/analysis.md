# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 119 | **Channels**: 63 | **Sampling Rate**: 5000 Hz | **Manual Review**:

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. Confidence estimates were collected using a visual analogue scale (VAS). High sampling rate (5000 Hz) requires downsampling before epoching.

## File Scan Result

> **Kernel SHA256**: `a6df321b40731aa8c9ea1eefe7979e21b9467d923ec7a8aa26f2972a40bbaf32`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Response/R128` | 44303 | event | raw | Response trigger |
| `Stimulus/S  7` | 1347 | event | raw | Trial phase onset: stimulus marker 7 |
| `Stimulus/S  8` | 1477 | event | raw | Trial phase onset: stimulus marker 8 |
| `Stimulus/S 11` | 2851 | event | raw | Trial phase onset: stimulus marker 11 |
| `Stimulus/S 12` | 2854 | event | raw | Trial phase onset: stimulus marker 12 |
| `Stimulus/S 17` | 1356 | event | raw | Trial phase onset: stimulus marker 17 |
| `Stimulus/S 18` | 1489 | event | raw | Trial phase onset: stimulus marker 18 |
| `Stimulus/S 27` | 5657 | event | raw | Trial phase onset: stimulus marker 27 |
| `Stimulus/S 37` | 120 | event | raw | Trial phase onset: stimulus marker 37 |
| `Stimulus/S 38` | 109 | event | raw | Trial phase onset: stimulus marker 38 |
| `Stimulus/S 40` | 6175 | event | raw | Trial phase onset: stimulus marker 40 |
| `Stimulus/S 41` | 5703 | event | raw | Trial phase onset: stimulus marker 41 |
| `Stimulus/S 43` | 6583 | event | raw | Trial phase onset: stimulus marker 43 |
| `Stimulus/S 44` | 475 | event | raw | Trial phase onset: stimulus marker 44 |
| `Stimulus/S128` | 474612 | event | raw | Continuous sampling trigger |
| `Stimulus/S140` | 3 | event | raw | Trial phase onset: stimulus marker 140 |
| `Stimulus/S145` | 1 | event | raw | Trial phase onset: stimulus marker 145 |
| `Stimulus/S155` | 2 | event | raw | Trial phase onset: stimulus marker 155 |
| `Stimulus/S165` | 39 | event | raw | Trial phase onset: stimulus marker 165 |
| `Stimulus/S166` | 48 | event | raw | Trial phase onset: stimulus marker 166 |
| `Stimulus/S169` | 1 | event | raw | Trial phase onset: stimulus marker 169 |
| `Stimulus/S171` | 4364 | event | raw | Trial phase onset: stimulus marker 171 |
| `SyncStatus/Sync On` | 30864 | admin | raw | Synchronization trigger onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Choice Accuracy Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43`, `Stimulus/S 27`, `Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 17`, `Stimulus/S 18`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Stimulus/S 40 | 0 | Correct perceptual decision (cor) |
  | Stimulus/S 41 | 0 | Correct perceptual decision (cor) |
  | Stimulus/S 43 | 0 | Correct perceptual decision (cor) |
  | Stimulus/S 27 | 0 | Correct perceptual decision (cor) |
  | Stimulus/S 11 | 1 | Erroneous perceptual decision (err) |
  | Stimulus/S 12 | 1 | Erroneous perceptual decision (err) |
  | Stimulus/S 17 | 1 | Erroneous perceptual decision (err) |
  | Stimulus/S 18 | 1 | Erroneous perceptual decision (err) |
- **Evidence**:
  - 10.1073/pnas.1918335117 — Binary classification of correct vs. erroneous perceptual decisions based on trial markers; paper analyzes first-order accuracy (correct vs. incorrect) as a key variable alongside confidence.
- **Notes**: The events.tsv shows `choice_accuracy` levels 'cor' and 'err' mapping to correct and erroneous decisions. The stimulus markers S 40/S 41/S 43/S 27 and S 11/S 12/S 17/S 18 correspond to the two accuracy conditions in the perceptual decision task. All eight event IDs are pooled into two classes: y=0 for correct (cor) and y=1 for erroneous (err) decisions, reflecting the binary choice accuracy classification objective described in the paper.

### Classical Task 2: Active vs Observed Decision Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43`, `Stimulus/S 27`, `Stimulus/S 37`, `Stimulus/S 38`, `Stimulus/S 44`, `Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 17`, `Stimulus/S 18`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43` | 0 | Active/committed decision trials (act, act-bad) |
  | `Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 17`, `Stimulus/S 18`, `Stimulus/S 27`, `Stimulus/S 37`, `Stimulus/S 38`, `Stimulus/S 44` | 1 | Observed decision trials (obs, obs-bad) |
- **Evidence**:
  - 10.1073/pnas.1918335117 — Binary classification distinguishing trials where participant made their own decision (active/committed) vs. observed another's decision. The paper's core manipulation: participants reported confidence in own decisions (act) or observed decisions (obs). Events.tsv shows trial_types 'act', 'act-bad', 'obs', 'obs-bad'. Better metacognitive performance for committed vs. observed decisions was a key finding.
- **Notes**: The event IDs used for this task are stimulus markers whose specific mappings to act/act-bad vs. obs/obs-bad conditions are inferred from the experimental design described in the paper. The kernel must map these Stimulus/S codes to the appropriate trial types based on the events.tsv trial_type column. The epoch window captures both the decision period and subsequent confidence rating period, consistent with the paper's focus on post-decisional confidence processing differences between active and observed conditions.

### Potential Task 1: Stimulus Side Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = -0.1 s *, tmax = 1.0 s *, target_events = [`Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43`, `Stimulus/S 27`, `Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 17`, `Stimulus/S 18`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S 40` | 0 | Stimulus marker 40 (left side more dots) |
  | `Stimulus/S 41` | 0 | Stimulus marker 41 (left side more dots) |
  | `Stimulus/S 43` | 0 | Stimulus marker 43 (left side more dots) |
  | `Stimulus/S 27` | 1 | Stimulus marker 27 (right side more dots) |
  | `Stimulus/S 11` | 1 | Stimulus marker 11 (right side more dots) |
  | `Stimulus/S 12` | 1 | Stimulus marker 12 (right side more dots) |
  | `Stimulus/S 17` | 1 | Stimulus marker 17 (right side more dots) |
  | `Stimulus/S 18` | 1 | Stimulus marker 18 (right side more dots) |
- **Evidence**:
  - events.tsv sample — `stim_side` column shows values 'left' and 'right' with `dots_difference` indicating perceptual decision task
  - task-main_events.json — `stim_side` defined with Levels: left="Left has most dots", right="Right has most dots"
  - README — Dataset involves speeded perceptual judgments with confidence ratings; participants decide which side has more dots
- **Notes**: The specific mapping between stimulus markers and left/right side is not explicitly documented in the available sidecar files. The events.tsv shows trial_type values (act, act-bad, obs, obs-bad) but does not directly map to the S 40/S 41/S 43/S 27/S 11/S 12/S 17/S 18 trigger codes. Based on the candidate's evidence summary stating these events encode stim_side values, we group markers into two classes (y=0 for left, y=1 for right). The exact left/right assignment per marker ID is inferred from the candidate's kernel_needs grouping. All eight stimulus markers are included as target_events to capture both sides; the kernel must extract stim_side labels from the events.tsv and assign class labels accordingly. The epoch window [-0.1, 1.0] s captures pre-stimulus baseline and early decision-related ERP components including potential contralateral delay activity and lateralized readiness potential.

### Potential Task 2: Age Regression from Resting Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20–32 (years) | Continuous age from participants.tsv; all 20 subjects have complete age data |
- **Evidence**:
  - participants.tsv — 20 participants with complete age data (range 20–32 years, mean ~25.5)
  - scans.tsv & file system — task-rest has no events.tsv and no EEG .vmrk file, confirming absence of event markers for resting-state EEG
  - README & dataset_description.json — dataset contains EEG-fMRI multimodal recordings with resting-state sessions
- **Notes**: Segmentation approach required because task-rest EEG lacks any event markers (no events.tsv, no .vmrk file). 2-second segments with 50% overlap provide sufficient samples per subject for subject-level age regression while preserving spectral content relevant to age-related EEG changes. Age range 20–32 is narrow but provides continuous variance for regression benchmarking of physiological variation across young adults.

### Potential Task 3: Sex Classification from Resting Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | F | 0 | Female |
  | sex | M | 1 | Male |
- **Evidence**:
- **Notes**: Segmentation-based task with no events (task-rest has no events.tsv and no .vmrk file). Sex is a native participants.tsv column with complete coverage (F=9, M=11, N=20). Segment length and overlap inferred from Category SKILL defaults for resting-state segmentation tasks.

### Potential Task 4: Age Regression from Task Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 20–32 (years) | Participant chronological age from participants.tsv; all 20 subjects have complete age data. Each 2-second segment from task-main continuous EEG inherits the subject's age as regression target. |
- **Evidence**:
  - participants.tsv — age column complete for N=20 subjects, range 20–32 years
  - epoch_hint — segmentation approach with 2s windows and 50% overlap for continuous task data
- **Notes**: Segmentation-based alternative to event-locked age prediction. Uses fixed 2-second non-overlapping segments (with 50% overlap) from continuous task-main EEG recordings. Each segment receives the same age label for its subject. This avoids reliance on complex event structure while leveraging the full continuous recording for subject-level demographic prediction.

## Data Quality Notes

- Extremely high sampling rate (5000 Hz) requires substantial downsampling before practical analysis; native resolution is well above typical EEG analysis needs and will increase computational load and storage requirements significantly.
- Large number of continuous sampling triggers (`Stimulus/S128`, 474612 events) indicates a feedback or rating device sending dense markers during confidence VAS periods; these must be excluded from epoching to avoid contaminating trial-locked analyses.
- fMRI-EEG synchronization pulses (`SyncStatus/Sync On`, 30864 events) present as admin markers; these require filtering during event extraction for pure EEG analyses.
- `device` field is missing from info metadata, limiting hardware documentation for reproducibility.
- Event meanings for stimulus markers are inferred from paper and events.tsv mappings rather than explicit documentation in sidecar files; kernel must validate mappings against actual `events.tsv` trial_type columns.
- Resting-state sessions lack all event markers (no events.tsv, no .vmrk), enforcing segmentation-based approaches only for those files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
