# Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task

**Dataset**: `openneuro_ds002034` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 167 | **Channels**: 64 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a covert spatial attention task where they were trained to lateralize their alpha-band EEG power using real-time neurofeedback. The study evaluated whether closed-loop neurofeedback of alpha lateralization improves behavioral performance in a spatial attention paradigm. Subjects attended to left or right hemifields based on visual cue presentations (half-circle cues), with continuous alpha-band lateralization index (LI) computed from posterior electrodes and fed back in real-time. No trial-level event markers are stored in the BIDS EEG files; the task condition is reflected continuously in the EEG signal itself.

## File Scan Result

> **Kernel SHA256**: `aaa6fd3f30f8be61248305ae692af61648b1fa5fc573102d8de5f1f2e8b8523c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 16179 | event | raw | Neurofeedback pulse (continuous alpha-LI feedback signal) |
| `event_11` | 3013 | event | raw | Feedback phase marker (likely block start/end) |
| `event_12` | 2248 | event | raw | Response or feedback confirmation event |
| `event_13` | 1129 | event | raw | Secondary response or validation event |
| `event_15` | 938 | event | raw | Instruction or cue validation event |
| `event_2` | 5020 | event | raw | Left cue marker (complementary to event_4, 1:1 correspondence) |
| `event_4` | 5020 | event | raw | Left cue onset (attend left hemifield) |
| `event_5` | 9333 | event | raw | Right cue marker variant (feedback selection event) |
| `event_6` | 6720 | event | raw | Right cue onset (attend right hemifield) |
| `event_8` | 1711 | event | raw | Feedback or response calibration event |
| `event_9` | 4995 | event | raw | Target presentation or response event |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Covert Visuospatial Attention Decoding (Left vs Right Hemifield)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 5.0 s, overlap = 0.0, target_events = [`event_4`, `event_6`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `event_4` | 0 | Attend to left hemifield (left half-circle cue) |
  | `event_6` | 1 | Attend to right hemifield (right half-circle cue) |
- **Super Meta Notes**: Event meanings derived from experimental paradigm. Event_4 has 5020 occurrences and event_6 has 6720 occurrences; the count discrepancy suggests some event_6 markers may include additional trial phases or feedback events. Kernel must verify event-to-cue mapping against dataset sidecar JSON if available.
- **Evidence**:
  - DOI: 10.1007/s10548-019-00725-9 — Post-hoc single-trial binary classification to decode attended side (left vs right) from alpha-band EEG lateralization features using LDA classifiers with 10-fold cross-validation. Full paper methods describe offline paradigm with 80 trials/run, cue presentation (left/right half-circle), sustained attention phase.
- **Kernel Notes**: Compute alpha-band (8-13 Hz) power spectral density using 1s sliding windows with 62.5ms overlap across the epoch. Calculate Lateralization Index (LI = (right - left) / (right + left)) from posterior electrodes (PO7, PO8, O1, O2). Use averaged features across trial for classification. Verify event_4→left_cue and event_6→right_cue mapping before epoching; if unmappable, derive trial onsets from sidecar JSON timing parameters.

### Classical Task 2: Alpha Lateralization Index Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 5.0 s, overlap = 0.9375, target_events = [`event_4`, `event_6`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|
  | `event_4` | continuous | Alpha Lateralization Index per sliding window (negative = left lateralized) |
  | `event_6` | continuous | Alpha Lateralization Index per sliding window (positive = right lateralized) |
- **Super Meta Notes**: Regression target is the computed alpha-band lateralization index per sliding window within each epoch. High overlap (0.9375) recommended to capture the continuous alpha-LI feedback signal across 5s epochs, enabling fine-grained lateralization estimation. The 6720 count for event_6 exceeds the expected 5020 left-cue trials; kernel should filter or validate before epoching.
- **Evidence**:
  - DOI: 10.1007/s10548-019-00725-9 — Real-time neurofeedback study on alpha-band lateralization; dataset includes continuous alpha-LI values during feedback runs. Supplementary material contains RT and alpha-LI tables by subject pairs, correlation figures showing alpha-lateralization effects.
- **Kernel Notes**: For each sliding window (62.5ms step), compute PSD in alpha band (8-13 Hz) for left (PO7, O1) and right (PO8, O2) posterior electrodes. Compute LI = (alpha_R - alpha_L) / (alpha_R + alpha_L). Aggregate windows within epoch for regression target. Verify event_4→left_cue and event_6→right_cue mapping before epoching.

### Potential Task 1: Continuous Alpha-Band Lateralization Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null — no trial-level labels available)
- **Notes**: Continuous neurofeedback paradigm; task condition is reflected continuously in the EEG signal itself. Alpha lateralization index may be computed from raw EEG as a continuous target. Fallback approach when raw event meanings cannot be verified against sidecar files.
