# EEG study of the attentional blink; before, during, and after transcranial Direct Current Stimulation (tDCS)

**Dataset**: `openneuro_ds001810` | **Year**: 2019 | **URL**: https://openneuro.org/datasets/ds001810
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 527 | **Channels**: 73 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Participants performed an attentional blink (AB) task using a Rapid Serial Visual Presentation (RSVP) stream to identify two targets (T1 and T2) embedded in a stream of distractors. EEG was recorded before, during, and after receiving anodal or cathodal transcranial Direct Current Stimulation (tDCS) to study how cortical excitability modulates the attentional blink—the impaired detection of T2 when it follows T1 within ~500 ms. BioSemi STATUS channels encode trial conditions and system markers as numeric codes. The RSVP stream duration was 1375 ms per trial, with T1-T2 lag manipulated at 3 (AB-susceptible) and 8 (control) positions.

## File Scan Result

> **Kernel SHA256**: `d55a66a4e3966fc9ce78ca8a74e33ec0ee53f7675c01b7ab05cc8b564bdf73d6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `RSVP_stream_item` | 51145 | event | raw | RSVP stream item presentation onset |
| `STATUS_-6` | 408405 | admin | raw | System status marker |
| `STATUS_126976` | 21 | admin | raw | System status marker |
| `STATUS_127230` | 226 | admin | raw | System status marker |
| `T1_T2_lag8` | 51144 | event | raw | Trial phase onset: T1-T2 lag 8 condition |
| `T1_onset` | 34082 | event | raw | Trial phase onset: first target (T1) presentation |
| `T1_present_T2_present_lag3` | 51144 | event | raw | Trial phase onset: T1-T2 lag 3 condition |
| `T1_target` | 51144 | event | raw | Trial phase onset: first target (T1) presentation |
| `T2_onset_variant1` | 23288 | event | raw | Trial phase onset: second target (T2) presentation variant 1 |
| `T2_onset_variant2` | 27597 | event | raw | Trial phase onset: second target (T2) presentation variant 2 |
| `T2_target` | 51115 | event | raw | Trial phase onset: second target (T2) presentation |
| `response_hit` | 40784 | event | raw | Participant response: correct detection |
| `response_miss` | 10216 | event | raw | Participant response: incorrect or missed detection |
| `stimulus_lag_variant` | 17062 | event | raw | Trial phase onset: stimulus lag condition indicator |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: T1-T2 Lag Condition Classification (Lag 3 vs Lag 8)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.5 s *, target_events = [`T1_present_T2_present_lag3`, `T1_T2_lag8`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `T1_present_T2_present_lag3` | 0 | T1-T2 lag 3 condition trial |
  | `T1_T2_lag8` | 1 | T1-T2 lag 8 condition trial |
- **Evidence**:
  - task-attentionalblink_events.json — "61463" defined as "onset of letter stream; lag 3 trial" and "61468" as "onset of letter stream; lag 8 trial", confirming the two lag conditions in the task structure
  - events.tsv sample — shows STATUS 61463 (lag 3) and 61468 (lag 8) appearing as trial onset markers in actual recordings
  - README — describes attentional blink RSVP task with varying T1-T2 lags as core paradigm manipulation
- **Notes**: Trial-level epoching from condition onset markers. The raw event IDs `T1_present_T2_present_lag3` and `T1_T2_lag8` (51144 occurrences each) are inferred to correspond to the lag-3 and lag-8 trial phase onsets respectively, based on their descriptive names and the task structure where 61463/61468 STATUS codes indicate lag conditions in the BIDS events files. The epoch window (-0.2 to 1.5s) captures pre-stimulus baseline and the full letter stream duration (1375ms) plus post-stream period, inferred from the 1375ms stream duration documented in events.json.

### Potential Task 2: Age Regression from Resting/Continuous EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | 18–28 (years); no mapping |
- **Evidence**:
  - participants.tsv — Age column present with values 18–28 years, 41 of 47 subjects have age data
  - dataset_description.json — EEG study with continuous recordings (~20 min blocks) enabling segmentation approach
  - eeg.json — RecordingType: continuous, supporting non-event-based epoching
- **Notes**: Standard brain-age prediction paradigm using 2-second non-overlapping segments from continuous EEG to extract spectral features for chronological age regression. Segmentation avoids task-locked event dependence, using inter-trial intervals and rest periods as effective "resting-state" data. The epoch length of 2s is inferred from common practice in brain-age literature for power spectral feature extraction. Partial completeness: 41/47 subjects; missing values excluded at kernel level.

### Potential Task 3: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | female -> 0; male -> 1 |
- **Evidence**:
- **Notes**: Binary classification with imbalanced classes (35 female, 12 male). Uses standard 2-second segmentation to capture stable spectral features for demographic prediction. All segments from a given subject share the same gender label.

## Data Quality Notes

- `device` field is completely missing from metadata, limiting hardware reproducibility and channel location verification.
- Event counts reveal imbalance between T2_onset_variant1 (~23.3k) and T2_onset_variant2 (~27.6k), suggesting unequal trial distribution across lag conditions or data loss in some files.
- T1_onset count (34082) is substantially lower than T1_target count (51144), indicating potential misalignment between onset markers and target identification events, or differential event extraction across recording sessions.
- The large number of STATUS_-6 events (408405) relative to task events suggests extensive system status logging that may require filtering to avoid epoching contamination.
- Age data is partially incomplete (41/47 subjects), which may reduce statistical power for Task 2 and requires missing-value handling at the kernel level.
- Gender classification (Task 3) has imbalanced classes (35 female vs 12 male), which may bias classifier performance and requires stratification or class-weighting.
- The tDCS_on_first_day variable is session-level, so all segments from a participant share the same label—this reduces effective sample independence for Task 4 and may inflate apparent classification/regression performance if not properly cross-validated.
- No direct DOI evidence is available for any task; all task definitions rely on inference from event names, README descriptions, and BIDS metadata.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
