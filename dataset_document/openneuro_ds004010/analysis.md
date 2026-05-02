# MAVIS

**Dataset**: `openneuro_ds004010` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004010
**Category**: Sensory/Response | **Subjects**: 24 | **Files (Completed)**: 24 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

A multisensory detection task (MAVIS) in which participants identified auditory and visual targets embedded within simultaneous audio-visual noise streams to investigate selective attention and crossmodal sensory processing. Participants attended to either auditory or visual modality in sustained attention blocks, with stimulus conditions varying in spectral exponent properties. EEG was recorded with 64 channels at 1000 Hz using a Brain Products system with event markers for block onsets, stimulus conditions, target onsets, and responses.

## File Scan Result

> **Kernel SHA256**: `2db640f44783825dfd2d9147e676f5bab91c8eaefd6050c267719ef7f2d2e3d4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `101` | 25 | event | raw | Trial phase onset: End of block 10 |
| `11` | 25 | event | raw | Trial phase onset: End of block 1 |
| `111` | 37 | event | raw | Trial phase onset: End of block 11 |
| `121` | 25 | event | raw | Trial phase onset: End of block 12 |
| `200` | 6101 | event | raw | Trial-level stimulus condition marker |
| `201` | 1959 | event | raw | Trial-level stimulus condition marker |
| `202` | 1641 | event | raw | Trial-level stimulus condition marker |
| `203` | 1099 | event | raw | Trial-level stimulus condition marker |
| `21` | 25 | event | raw | Trial phase onset: End of block 2 |
| `220` | 2700 | event | raw | Trial-level stimulus condition marker |
| `221` | 2700 | event | raw | Trial-level stimulus condition marker |
| `222` | 2700 | event | raw | Trial-level stimulus condition marker |
| `223` | 2700 | event | raw | Trial-level stimulus condition marker |
| `230` | 2700 | event | raw | Trial-level stimulus condition marker |
| `231` | 2771 | event | raw | Trial-level stimulus condition marker |
| `232` | 2700 | event | raw | Trial-level stimulus condition marker |
| `233` | 2764 | event | raw | Trial-level stimulus condition marker |
| `31` | 25 | event | raw | Trial phase onset: End of block 3 |
| `33` | 8267 | event | raw | Response given, space bar pressed |
| `34` | 3174 | event | raw | No response given within time window (during trial) |
| `41` | 25 | event | raw | Trial phase onset: End of block 4 |
| `44` | 8395 | event | raw | Onset of auditory target |
| `45` | 2428 | event | raw | Auditory catch trial, time point of 'target' |
| `51` | 25 | event | raw | Trial phase onset: End of block 5 |
| `55` | 8400 | event | raw | Onset of visual target |
| `56` | 2400 | event | raw | Visual catch trial, time point of 'target' |
| `61` | 244 | event | raw | Trial phase onset: End of block 6 |
| `66` | 150 | event | raw | Trial phase onset: Auditory attention block |
| `71` | 25 | event | raw | Trial phase onset: End of block 7 |
| `77` | 150 | event | raw | Trial phase onset: Visual attention block |
| `81` | 25 | event | raw | Trial phase onset: End of block 8 |
| `91` | 25 | event | raw | Trial phase onset: End of block 9 |
| `nan` | 24 | admin | raw | Missing or undefined marker |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 2-class auditory vs visual attention
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 30 s *, overlap = 0 *, target_events = [`66`, `77`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 66 | 0 | Auditory attention block |
  | 77 | 1 | Visual attention block |
- **Evidence**:
  - 10.7554/elife.70068 — The paper explicitly describes a multisensory detection task where participants attended to either auditory or visual modality. Event IDs 66 (auditory attention block) and 77 (visual attention block) mark the onset of sustained attention periods. Classification distinguishes between these two attention conditions using continuous EEG during the blocks.
  - task-MultisensoryDetectionTask_events.json — Confirms x66 = "Auditory attention block" and x77 = "Visual attention block" in the Levels field.
  - sub-1_task-MAVIS_events.tsv — Confirms event values 66 and 77 appear in actual data with corresponding trial_type descriptions.
- **Notes**: The task uses sustained attention block onsets (event IDs 66 and 77) as anchors for epoching. Block durations are not explicitly stated in metadata; the 30s segment length with 0 overlap is inferred from the epoch_hint as a reasonable duration for sustained attention analysis, marked with *. The long-event epoching method allows extraction of continuous EEG segments during attention blocks for classification of auditory vs visual attention states.

### Potential Task 1: 16-class stimulus condition classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 2.0 s *, target_events = [`200`, `201`, `202`, `203`, `220`, `221`, `222`, `223`, `230`, `231`, `232`, `233`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | 200 | 0 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 201 | 1 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 202 | 2 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 203 | 3 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 220 | 4 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 221 | 5 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 222 | 6 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 223 | 7 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 230 | 8 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 231 | 9 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 232 | 10 | Trial-level stimulus condition marker (spectral exponent condition) |
  | 233 | 11 | Trial-level stimulus condition marker (spectral exponent condition) |
- **Evidence**:
- **Notes**: The candidate proposes 16 classes but only 12 distinct event IDs are present in the data (200-203, 220-223, 230-233). The evidence summary mentions "plus any additional 200-series codes discovered" but no additional codes exist in the available event ID list. This task is emitted as a 12-class classification with the available codes. The systematic structure of these codes (200s, 220s, 230s with final digits 0-3) suggests encoding of spectral exponent × attention modality combinations per the TaskDescription mentioning "different spectral exponents between 1 and 4", but the exact mapping is not confirmed in available sidecars. Epoch window extended to 2s to capture sustained spectral dynamics as noted in the candidate's rationale.

### Potential Task 2: Age Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_age | no mapping |
- **Evidence**:
- **Notes**: Native info field regression task using continuous EEG segmentation. No kernel derivation required—subject_age is directly available in participants.tsv with complete coverage for all N=24 subjects (range 18–27 years). All segments from a given subject share the same age label. Segmentation parameters default to 2s windows with 50% overlap for subject-level prediction; all values inferred from task category defaults.

### Potential Task 3: Gender Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 2 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |------------|----------------|
  | subject_sex | M → 0; F → 1 |
- **Evidence**:
- **Notes**: Binary subject-level classification from continuous EEG segments. participants.tsv provides complete subject_sex column with M/F values for all 24 subjects. Segmentation with 2s windows and 50% overlap yields multiple samples per subject; the model must learn to aggregate or classify from segment-level features. No kernel derivation needed — subject_sex is a native participants.tsv column.

## Data Quality Notes

- Event marker `nan` appears 24 times (once per subject on average), indicating occasional missing or undefined triggers that should be excluded from analysis
- Stimulus condition markers (200-203, 220-223, 230-233) have highly imbalanced counts (ranging from ~1,099 to ~6,101), which may affect classification performance and requires stratified sampling
- Block-end markers (`11`, `21`, `31`, etc.) show inconsistent counts (25 for most blocks, but 37 for block 11 and 244 for block 6), suggesting possible recording anomalies or protocol variations for certain blocks
- Response markers (`33` vs `34`) indicate substantial missing-response trials (~28% no-response rate), which may reflect task difficulty or participant engagement issues
- Device metadata is missing from info fields, limiting hardware-specific reproducibility
- `age` and `sex` fields are marked complete but duplicate `Age` and `Gender` fields; verify consistency across these redundant columns
- Block duration for attention blocks (event IDs 66 and 77) is not explicitly documented; the 30s epoch length for the primary task is inferred and requires manual verification against actual stimulus logs

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
