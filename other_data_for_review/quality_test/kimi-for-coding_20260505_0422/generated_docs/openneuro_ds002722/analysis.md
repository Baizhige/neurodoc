# BCMI-MIdAS: Calibration Dataset for Affective Brain-Computer Music Interface

**Dataset**: `openneuro_ds002722` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002722
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 14 | **Sampling Rate**: 128 Hz | **Manual Review**:

## Paradigm

Nineteen healthy participants (ages 19-30, 11 female) listened to music excerpts while 14-channel EEG was recorded using a Muse headband at 128 Hz. The study employed a continuous affective music listening paradigm designed for brain-computer music interface (BCMI) calibration, where participants experienced music stimuli intended to induce varying valence and arousal states. Each music trial lasted 21 seconds, with the original FEELTRACE methodology intended to capture continuous subjective ratings; however, only trial-level event markers are preserved in the available BIDS data.

## File Scan Result

> **Kernel SHA256**: `c73a2ecd98591288b7aac34886e4a13e7c32a4348ad28833dad178bc32bc52c5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|

### MISC Label Summary

| Channel | Source | Meta | Notes |
|---|---|---|---|
| `TP10` | native (raw misc in EEG file) | raw | Native raw misc channel in EEG file; one of 4 Misc channels |
| `TP9` | native (raw misc in EEG file) | raw | Native raw misc channel in EEG file; one of 4 Misc channels |

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Recorded in participants.tsv; samples include 19-24 years |
| `amplifier` | missing |  |
| `cap` | missing |  |
| `handedness` | missing |  |
| `sex` | complete | Recorded in participants.tsv as F/M; samples include female and male |

## Tasks

### Classical Task 1: Continuous Affective Music Listening Segmentation (Age Regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 21 s *, overlap = 0.0, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | `age` | Continuous subject age in years (19–30); same value assigned to all segments from a given participant |
- **Evidence**:
  - 10.1038/s41597-020-0507-6 — Dataset descriptor describing BCMI-MIdAS calibration with 21-s music trials targeting valence/arousal states
  - 10.1038/s41598-019-45105-2 — Related BCMI-MIdAS work on affective brain-computer music interface with continuous music listening paradigm
  - events.json — Confirmed trial duration of 21s for all affect condition and music stimulus events
  - participants.tsv — Complete age field (19–30 years, N=19) with numeric dtype
- **Notes**: This is a degraded archetype-C approximation. The true continuous FEELTRACE valence/arousal trajectories described in the paradigm literature are not present in the available BIDS files (no continuous misc channels, no per-trial numeric ratings in events.tsv). Segmentation at 21s matches the trial duration from events.tsv. Age is used as a fallback subject-level regression target since it is the only available complete numeric field in participants.tsv. The kernel does not need to derive any channels; Meta Level remains raw because `age` is a native info field.

### Potential Task 1: Age Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | age | Continuous numeric age in years (19–30 range); used directly as regression target. All epochs from a subject share the same age label. |
- **Evidence**:
- **Notes**: Subject-level biomarker regression task. The full continuous EEG recording is segmented into 10-second non-overlapping windows. Each window inherits the subject's age from participants.tsv as its regression target. No trial events are required since the label is per-subject rather than per-trial. Typical EEG brain-age estimation approach where model learns to predict chronological age from spontaneous/ongoing EEG patterns during music listening.

### Potential Task 2: Sex Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s *, overlap = 0.0 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|-----------------|
  | sex | 0=F (female), 1=M (male) |
- **Evidence**:
- **Notes**: Subject-level biomarker classification using non-overlapping 10-second windows. The sex field from participants.tsv is a stable per-subject characteristic, making it suitable for subject-level classification. All windows from the same subject share the same label. Binary classes: 0=F (n=11 subjects), 1=M (n=8 subjects).

## Data Quality Notes

- No continuous valence/arousal ratings (FEELTRACE trajectories) are present in the BIDS data despite being central to the original paradigm; only 21-s trial event markers are available.
- Event table is empty (no event IDs detected), limiting task design to subject-level labels (age, sex) rather than trial-level affective state prediction.
- Two MISC channels (TP9, TP10) are present as native raw channels; these may correspond to auxiliary sensors but their intended use for affect tracking is not realized in the available data.
- Critical metadata fields are missing: amplifier, cap, and handedness are not recorded.
- Small sample size (N=19) with imbalanced sex distribution (11F/8M) may limit generalizability for biomarker tasks.
- Only 14 channels from consumer-grade Muse headband; spatial resolution is limited compared to research-grade systems.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
