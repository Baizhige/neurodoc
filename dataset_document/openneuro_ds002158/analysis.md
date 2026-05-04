# Disentangling the origins of confidence in speeded perceptual judgments through multimodal imaging

**Dataset**: `openneuro_ds002158` | **Year**: 2020 | **URL**: https://openneuro.org/datasets/ds002158
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 119 | **Channels**: 63 | **Sampling Rate**: 5000 Hz | **Manual Review**: Liu Peng

## Paradigm

Participants performed speeded perceptual judgments and subsequently reported their confidence in either their own decisions or in observed decisions made by another person. The study used multimodal neuroimaging (EEG + fMRI) to isolate the neural correlates of metacognitive confidence, distinguishing whether confidence reflects the quality of perceptual evidence or post-decisional processes. Confidence estimates were collected using a visual analogue scale (VAS). High sampling rate (5000 Hz) requires downsampling before epoching.

## File Scan Result

> **Kernel SHA256**: `4d30b57d695216b4e8f4a5fdbbadedb027c4765cdc89f1213930b45da09404a5`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
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


> 1. The experimental paradigm of the paper consists of an active/observation dual-condition design (lines 655–659 of the paper), with trials alternating within blocks (4 blocks per run, alternating between active and observation). The type of all trials is a fixed attribute of the experimental design and is not ‘unknown’;  
> 2.  The key events in the trial sequences described in the paper (start of gaze, start of stimulus, start of response, start of masking, start of confidence scale) are all clearly defined experimental marker events; there are no ‘unknown events’ serving as core epoch anchors or trial markers, and the ‘unknown’ Event ID has no basis in the paper.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | Mean age = 24.6 ± 1.43 y |
| `sex` | complete | Twenty-five healthy volunteers (12 females) |
| `device` | missing | EEG Recording: Data acquired via BrainVision system; MR-gradient artifacts removed via sliding window template subtraction. BCG artifacts removed using TP10 electrode (right mastoid) with semi-automatic procedure. Preprocessing included 1-10 Hz Butterworth filter (4th order zero-phase), [-0.2, 0.6] s epoching around response onset, common average reference, and ICA for artifact removal (EEGLAB/MATLAB). fMRI Recording: Structural (T1) and functional MRI data included; preprocessed using fMRIPrep with GLM analysis for BOLD signal estimation. |


## Tasks

### Classical Task 1: Binary Classification of Perceptual Decision Accuracy
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.5 s, target_events = [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 17`, `Stimulus/S 18`, `Stimulus/S 27`, `Stimulus/S 40`, `Stimulus/S 41`, `Stimulus/S 43`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `Stimulus/S 40` | 0 | Correct perceptual decision |
  | `Stimulus/S 41` | 1 | Correct perceptual decision |
  | `Stimulus/S 43` | 2 | Correct perceptual decision |
  | `Stimulus/S 27` | 3 | Correct perceptual decision |
  | `Stimulus/S 11` | 4 | Erroneous perceptual decision |
  | `Stimulus/S 12` | 5 | Erroneous perceptual decision |
  | `Stimulus/S 17` | 6 | Erroneous perceptual decision |
  | `Stimulus/S 18` | 7 | Erroneous perceptual decision |
- **Evidence**:
  - 10.1073/pnas.1918335117 - Binary classification of correct vs. erroneous perceptual decisions with eight stimulus markers mapped to two accuracy classes
  - 10.1038/s41467-021-23540-y - Binary classification of choice accuracy with epochs -0.2s to 1.5s relative to stimulus onset
  - 10.7554/eLife.53900 - Binary classification of first-order choice accuracy using trial-locked EEG epochs with correct (S 40/41/43/27) and erroneous (S 11/12/17/18) decision markers
- **Notes**: The eight stimulus markers are pooled into two classes reflecting speeded perceptual decision outcomes. The 5000 Hz sampling rate requires downsampling before epoching. The `Response/R128` event was excluded from target_events despite appearing in one reference because the primary epoching is stimulus-locked per the majority of sources; response-locked analyses are secondary.

### Classical Task 2: Segmentation-Based Analysis for Resting-State Sessions
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0, target_events = []
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Y Mapping Notes |
  |---|---|
  | `sex` | F -> 0; M -> 1 |
- **Evidence**:
  - openneuro_ds002158 — Resting-state sessions lack all event markers (no events.tsv, no .vmrk), enforcing segmentation-based approaches only for those files
- **Notes**: This task serves as a fallback for resting-state sessions that lack event markers entirely. The `sex` field is complete across all participants. Classification is binary with two distinct classes. The `age` field could alternatively be used for regression (Potential Task), but the age range in a sample of 20 participants may be limited. This task is explicitly segmentation-based with empty target_events as required.

## Data Quality Notes

- Extremely high sampling rate (5000 Hz) requires substantial downsampling before practical analysis; native resolution is well above typical EEG analysis needs and will increase computational load and storage requirements significantly.
- Large number of continuous sampling triggers (`Stimulus/S128`, 474612 events) indicates a feedback or rating device sending dense markers during confidence VAS periods; these must be excluded from epoching to avoid contaminating trial-locked analyses.
- fMRI-EEG synchronization pulses (`SyncStatus/Sync On`, 30864 events) present as admin markers; these require filtering during event extraction for pure EEG analyses.
- `device` field is missing from info metadata, limiting hardware documentation for reproducibility.
- Event meanings for stimulus markers are inferred from paper and events.tsv mappings rather than explicit documentation in sidecar files; kernel must validate mappings against actual `events.tsv` trial_type columns.
- Resting-state sessions lack all event markers (no events.tsv, no .vmrk), enforcing segmentation-based approaches only for those files.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
