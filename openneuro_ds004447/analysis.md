# The BMI-HDEEG dataset 3

**Dataset**: `openneuro_ds004447` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004447
**Category**: Action/Output | **Subjects**: 30 | **Files (Completed)**: 418 | **Channels**: 130 | **Sampling Rate**: 1000 Hz
**Manual Review**:

## Paradigm

A brain-computer interface (BCI) study investigating neural correlates of motor preparation and execution using high-density scalp EEG. Participants performed a cue-based motor task with a 130-channel GES400/Hydrocel GSN montage at 1000 Hz sampling. The experimental design includes both 2-phase (rest→task) and 4-phase (rest→ready→task→interval) paradigm sessions, with thirty subjects participating and handedness information available in the participants metadata.

## File Scan Result

> **Kernel SHA256**: `f7512d4e42b692417d61359f1f0e9e57abc0e90a3d7092f73ba8abafcfc75e84`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 327 | event | raw | Trial phase onset: rest |
| `event_2` | 5090 | event | raw | Trial phase onset: task |
| `event_3` | 3270 | event | raw | Trial phase onset: ready |
| `event_4` | 1237 | event | raw | Trial phase onset: interval |
| `event_5` | 1237 | admin | raw | System/administrative marker (unidentified - not present in sampled events.tsv files) |
| `event_6` | 91 | admin | raw | System/administrative marker (unidentified - not present in sampled events.tsv files) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Motor Preparation vs Execution
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2 s, target_events = [`event_3`, `event_2`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|-------------|
  | event_3 | 0 | Motor preparation (ready phase) |
  | event_2 | 1 | Motor execution (task phase) |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Analysis.md identifies motor preparation detection as a potential task contrasting ready phase (event_3, 2s) vs motor execution (event_2, 6s). Both phases present in 4-phase paradigm sessions. Detects CS (contingent negative variation) and pre-movement mu suppression.
- **Notes**: Classification of motor preparation vs execution uses ready phase (trial phase onset: ready) as class 0 and task phase (trial phase onset: task) as class 1. The 2s epoch window captures the onset transition between preparation and execution states.

### Potential Task 2: Gender Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 4 s *, target_events = [`event_1`, `event_2`, `event_3`, `event_4`]
- **Label Route**: `info`
- **Label Field**: `gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|--------|
  | gender | female | 0 | Female participant |
  | gender | male | 1 | Male participant |
- **Evidence**:
  - participants.tsv contains complete gender data (5 female, 25 male)
  - Gender differences in mu rhythm lateralization and alpha peak frequency are documented in motor imagery literature
  - Epoch window aligns with motor-related EEG phases where gender effects are observable
- **Notes**: This task classifies EEG epochs by participant gender, using trial phase events as anchors. Gender effects on motor-related cortical activity (mu/alpha rhythms) provide discriminative features.

### Potential Task 3: Handedness Classification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 4 s *, target_events = ["event_1", "event_2", "event_3", "event_4"]`
- **Label Route**: `info`
- **Label Field**: `handedness`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|-------------|
  | handedness | left | 0 | left-handed participant |
  | handedness | right | 1 | right-handed participant |
- **Evidence**:
  - participants.tsv contains handedness data (1 left, 29 right per sample) — directly verified in first 7 rows showing sub-001=left, sub-002 through sub-007=right
  - BIDS sidecar confirms "handedness" column is available as native info field with categorical dtype (left/right)
  - Reference: Iwama et al. (2023) Sci Data — High-density scalp EEG dataset during SMR-based BCI
  - Evidence summary: Handedness affects motor cortex lateralization and may influence SMR patterns during motor imagery; binary classification of handedness from EEG using motor-related trial phases.
- **Notes**: All four trial phase events (rest/ready/task/interval) are included to maximize EEG data coverage per participant. Since handedness is a participant-level characteristic, all epochs from a given subject receive the same label. Epoch window (0–4 s) inferred from motor state detection paradigm rationale — captures motor-related EEG activity where handedness lateralization effects manifest.

### Potential Task 4: Resting State EEG Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2.0 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | age | 18.0–27.0 (years) | Subject-level continuous variable from participants.tsv |
- **Evidence**:
  - 10.1038/s41597-023-02260-6 — Dataset includes continuous resting-state periods between trials. Segmentation into fixed windows enables analysis of individual differences in EEG features across subjects.
- **Notes**: Segmentation-based resting state analysis. The interval periods (event_4=interval) between task trials provide natural resting-state segments. Using SKILL defaults for segment length (2s) and overlap (50%) to capture alpha/mu rhythms while maintaining temporal resolution. Subject-level labels from participants.tsv enable regression on individual differences.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
