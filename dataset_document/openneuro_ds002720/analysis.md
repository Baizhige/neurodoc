# A dataset recorded during development of a tempo-based brain-computer music interface

**Dataset**: `openneuro_ds002720` | **Year**: 2018 | **URL**: https://openneuro.org/datasets/ds002720
**Category**: Action/Output | **Subjects**: 18 | **Files (Completed)**: 165 | **Channels**: 19 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants used EEG self-regulation to control the tempo of music in a tempo-based brain-computer music interface (BCMI). One condition instructed participants to lower their alpha levels and the other instructed participants to raise their alpha levels. Each labeled event spans a full 20-second music clip interval. The dataset contains multiple runs per participant.

## File Scan Result

> **Kernel SHA256**: `ebc8108fe8d4e055bcec1d19676f2b228af0595909a5042752c27eda2447188d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1` | 1353 | event | raw | Lower alpha: participants instructed to lower their alpha levels to modulate the position of an on-screen cue or the tempo of some music |
| `2` | 1358 | event | raw | Raise alpha: participants instructed to increase their alpha levels to modulate the position of an on-screen cue or the tempo of some music |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class alpha self-regulation (lower vs raise)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [`1`, `2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `1` | 0 | Lower alpha: participants instructed to lower their alpha levels to modulate the position of an on-screen cue or the tempo of some music |
  | `2` | 1 | Raise alpha: participants instructed to increase their alpha levels to modulate the position of an on-screen cue or the tempo of some music |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 — Binary classification of two instructed alpha modulation states: lower alpha (event ID 1) and raise alpha (event ID 2). Each event spans a full 20-second music clip interval. N=2711 total events across 18 subjects (~1353 lower, ~1358 raise). Core BCMI paradigm where participants self-regulate EEG alpha to control music tempo.
- **Notes**: Event IDs 1 and 2 are the two self-regulation conditions in the BCMI paradigm. The 20-second duration is explicitly confirmed by both the events.tsv duration column (20) and the publication description. Long-event epoching with overlap=0 captures each full music clip as a single epoch. y=0 for lower alpha, y=1 for raise alpha follows 0-based sequential integer convention.

### Potential Task 1: Age Regression from EEG Segments
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–28.0 (years) | Subject-level age from participants.tsv; all segments from a subject share the same age label. N=18 subjects. |
- **Evidence**:
- **Notes**: Segmentation-based regression with no event dependence. Age is a native participants.tsv column (B3 archetype, raw meta level). Standard 4s windows with 50% overlap applied per Category SKILL defaults for continuous task-EEG since no reference guidance exists for this dataset's continuous BCMI paradigm.

### Potential Task 2: sex classification from EEG segments
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `sex`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | sex | M | 0 | Male |
  | sex | F | 1 | Female |
- **Evidence**:
  - participants.tsv — N=18 subjects with sex column: M=14, F=4 (complete)
- **Notes**: Continuous EEG segmentation with 4s windows and 50% overlap for subject-level sex classification. Class imbalance noted (78% male). Labels mapped to 0-based integers: 0=Male, 1=Female. No event-locked structure required; segmentation extracts fixed-length windows from continuous recordings.

## Data Quality Notes

- Device information is missing from info fields; equipment details must be inferred from publication or dataset documentation.
- The two alpha modulation conditions (lower vs raise) are well-balanced with nearly equal event counts (1353 vs 1358).
- Sex classification task has significant class imbalance (M=14, F=4).
- Event durations are consistently 20 seconds as confirmed by both events.tsv and publication, supporting reliable long-event epoching.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
