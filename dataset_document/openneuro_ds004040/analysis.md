# Trance Channeling EEG Dataset

**Dataset**: openneuro_ds004040 | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds004040
**Category**: Neuroscience | **Subjects**: 13 | **Files (Completed)**: 26 | **Channels**: 64 | **Sampling Rate**: 512 Hz | **Manual Review**:

## Paradigm

Thirteen experienced trance channelers performed alternating 5-minute blocks of trance channeling (a mediumistic altered state of consciousness) and matched resting state conditions across two separate recording sessions. The study investigates neural correlates of voluntarily induced altered states of consciousness compared to wakeful rest. Each session contains three trance blocks and three rest blocks with precise onset/offset markers available as event triggers.

## File Scan Result

> **Kernel SHA256**: `2dae4eccd153c0f54620bb55ee284ed6ebe47dc306b8abaa5ee6c09a6c3c539e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `rest1_end` | 26 | event | raw | Trial phase offset: rest period 1 |
| `rest1_start` | 26 | event | raw | Trial phase onset: rest period 1 |
| `rest2_end` | 26 | event | raw | Trial phase offset: rest period 2 |
| `rest2_start` | 26 | event | raw | Trial phase onset: rest period 2 |
| `rest3_end` | 26 | event | raw | Trial phase offset: rest period 3 |
| `rest3_start` | 26 | event | raw | Trial phase onset: rest period 3 |
| `trance1_end` | 26 | event | raw | Trial phase offset: trance period 1 |
| `trance1_start` | 26 | event | raw | Trial phase onset: trance period 1 |
| `trance2_end` | 26 | event | raw | Trial phase offset: trance period 2 |
| `trance2_start` | 26 | event | raw | Trial phase onset: trance period 2 |
| `trance3_end` | 26 | event | raw | Trial phase offset: trance period 3 |
| `trance3_start` | 26 | event | raw | Trial phase onset: trance period 3 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Trance vs Rest Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 300 s, overlap = 0, target_events = [`rest1_start`, `rest2_start`, `rest3_start`, `trance1_start`, `trance2_start`, `trance3_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `rest1_start`, `rest2_start`, `rest3_start` | 0 | Rest period onset (resting state) |
  | `trance1_start`, `trance2_start`, `trance3_start` | 1 | Trance period onset (altered state) |
- **Evidence**:
  - 10.12688/f1000research.17157.2 — Beaver et al. (2021) defines 5-minute alternating blocks of trance channeling vs resting state, 3 periods per session per condition
  - https://doi.org/10.18112/openneuro.ds004040.v1.0.0 — README confirms "alternating (5 minutes) blocs of trance channeling and resting state (3 periods per session for each condition)"; events.tsv files show consistent rest/trance start events across all subjects and sessions
- **Notes**: Six onset events per session (three rest starts, three trance starts) mapped to binary y labels. All three rest start events collapse to y=0 and all three trance start events collapse to y=1, reflecting the condition-level contrast rather than period-specific differences. tmax=300s corresponds to the explicit 5-minute block duration. Overlap=0 since blocks are contiguous but non-overlapping by design.

### Potential Task 1: trance vs rest 6-class block identity
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 300 s *, overlap = 0, target_events = [`trance1_start`, `trance2_start`, `trance3_start`, `rest1_start`, `rest2_start`, `rest3_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `trance1_start` | 0 | Trial phase onset: trance period 1 |
  | `trance2_start` | 1 | Trial phase onset: trance period 2 |
  | `trance3_start` | 2 | Trial phase onset: trance period 3 |
  | `rest1_start` | 3 | Trial phase onset: rest period 1 |
  | `rest2_start` | 4 | Trial phase onset: rest period 2 |
  | `rest3_start` | 5 | Trial phase onset: rest period 3 |
- **Evidence**:
- **Notes**: Block identity decoding task treating each of the 6 block onsets as a distinct class. Each block lasts approximately 5 minutes (300 s). The overlap parameter is set to 0 to create non-overlapping epochs spanning the full block duration. All 6 event IDs appear 26 times each across the dataset. Event order varies by session (some start with rest, others with trance), but all 12 event IDs appear consistently. The `epoch_by_long_event_hdf5` method is used because each epoch spans the full 5-minute block duration, which exceeds typical short-epoch lengths.

### Potential Task 2: trance vs rest 3-class ordinal
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 300 s *, overlap = 0.0 *, target_events = [`trance1_start`, `rest1_start`, `trance2_start`, `rest2_start`, `trance3_start`, `rest3_start`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | trance1_start, rest1_start | 0 | First block in session (ordinal position 1) |
  | trance2_start, rest2_start | 1 | Second block in session (ordinal position 2) |
  | trance3_start, rest3_start | 2 | Third block in session (ordinal position 3) |
- **Evidence**:
  - sub-001_ses-01_task-trance_events.tsv — events.tsv showing alternating rest/trance blocks with numbered phases (rest1_start, trance1_start, etc.)
  - sub-001_ses-02_task-trance_events.tsv — confirms block order varies by session (ses-02 starts with trance), but all 6 start events present
  - README — "alternating (5 minutes) blocs of trance channeling and resting state (3 periods per session for each condition)"
- **Notes**: This task tests whether EEG carries temporal/session structure (practice/fatigue effects) by classifying the ordinal position of each 5-minute block regardless of whether it is trance or rest. All six start events are used as epoch anchors, with y determined by block number (1/2/3). The 300-second epoch length matches the 5-minute block duration described in the README. Overlap set to 0 to avoid duplicate samples from adjacent blocks.

## Data Quality Notes

- Missing demographic metadata: subject_age, subject_sex, and device fields are absent from all files.
- Small sample size (13 subjects, 26 files) limits generalizability; results should be interpreted with caution.
- Block order varies across sessions (some begin with rest, others with trance), which is a known design feature but should be accounted for in analyses sensitive to order effects.
- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
