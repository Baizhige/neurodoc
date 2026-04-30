# An EEG dataset recorded during affective music listening

**Dataset**: `openneuro_ds002721` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002721
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 185 | **Channels**: 19 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

Participants listened to music clips from film scores while their EEG was recorded, to investigate the neural correlates of music-induced emotional states. Each music clip is marked at onset with a numeric trigger code (800-908 range encode specific music tracks; system markers such as 32768 and 257 are used for synchronization). The study is part of a research series investigating affective processing in music, with participants reporting felt emotions across multiple affective dimensions. Emotion ratings were collected on a 9-point Likert scale across 8 affective dimensions including pleasantness.

## File Scan Result

> **Kernel SHA256**: `6bf8e6a13c940930c57917267c033a33bf77684c9aeef5788912caf77ee28cd1`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: age regression from resting EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 5 s *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | no mapping |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 — Dataset publication describing 31 participants (age 18-66) with 6-run paradigm including 300-second eyes-open resting state recordings in runs 1 and 6; standard brain-age prediction paradigm using continuous resting EEG.
- **Notes**: Standard resting-state brain-age regression. The 300-second resting runs (runs 1 and 6) are segmented into 10-second non-overlapping windows with 5-second overlap. Each segment is labeled with the participant's age from participants.tsv. No kernel derivation needed — age is a native info field.

### Classical Task 2: Age Regression from Music Listening EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 2.0 s *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | no mapping |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 — Dataset descriptor confirming 31 participants age 18–66 with 40 music clips of 12s duration in runs 2–5; resting-state runs 1 and 6
  - README — "31 healthy adult participants listened to 40 music clips of 12 s duration each"; age range 18-66, 18 female; 6 runs with first/last resting state and 4 music listening runs
  - participants.tsv — Complete age data for all 31 subjects (sample: 31, 29, 39, 49, 23, 63, 34)
- **Notes**: Segmentation-based brain age prediction from continuous music-listening EEG. 12s segments match individual music clip duration; 2s overlap allows denser sampling of the 40 clips × 4 runs = 160 trials per subject. No kernel derivation needed — age is a native participants.tsv column.

### Potential Task 1: Sex Classification from Resting EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 5.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | M -> 0 (Male); F -> 1 (Female) |
- **Evidence**:
  - participants.tsv — 31 participants with sex column (13 M, 18 F), complete demographic data
  - README — resting-state runs 1 and 6 are 300 s continuous EEG recordings per subject
  - eeg.json — 19 EEG channels, 1000 Hz sampling rate
- **Notes**: Segmentation-based classification using 10-second non-overlapping windows from resting-state runs (runs 1 and 6). Binary classification of sex from EEG during eyes-open resting state. Epoch parameters inferred from standard resting-state demographic classification practice.

### Potential Task 2: Sex Classification from Music Listening EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 12 s *, overlap = 2 s *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | M -> 0 (Male); F -> 1 (Female) |
- **Evidence**:
  - participants.tsv — 31 participants with complete sex labels (13 male, 18 female)
- **Notes**: Segmentation-based task using 12-second windows with 2-second overlap to match music clip duration. Binary classification of sex from EEG recorded during emotional music listening (runs 2-5).

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
