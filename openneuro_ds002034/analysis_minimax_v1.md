# Real-time EEG feedback on alpha power lateralization leads to behavioral improvements in a covert attention task

**Dataset**: `openneuro_ds002034` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds002034
**Category**: Action/Output | **Subjects**: 14 | **Files (Completed)**: 167 | **Channels**: 82.0 | **Sampling Rate**: 512.0 Hz

## Paradigm

Participants performed a covert spatial attention task where they were trained to lateralize their alpha-band EEG power using real-time neurofeedback. The study evaluated whether closed-loop neurofeedback of alpha lateralization improves behavioral performance in a spatial attention paradigm. No trial-level event markers are stored in the BIDS EEG files; the task condition is reflected continuously in the EEG signal itself.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002034

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; continuous neurofeedback paradigm |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: Covert Visuospatial Attention Decoding (Left vs Right Hemifield)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.9375
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | left_attention | 0 | Attend left hemifield (left_cue condition) |
  | right_attention | 1 | Attend right hemifield (right_cue condition) |
- **Super Meta Notes**: Labels derived from experimental cue direction (left half-circle vs right half-circle). Raw EEG is segmented into sliding windows (1s, 62.5ms overlap per paper), then alpha-band lateralization index (alpha-LI) is computed per window as features for binary classification of attended side.
- **Evidence**:
  - DOI: 10.1007/s10548-019-00725-9 — This paper presents a real-time EEG neurofeedback study on alpha-band lateralization for covert visuospatial attention, with post-hoc single-trial classification to decode attended hemifield (left vs right) using alpha-LI features.
  - DOI: 10.1007/s10548-019-00725-9 — The paper performs post-hoc single-trial binary classification to decode the attended side (left vs right) from alpha-band EEG lateralization features using LDA classifiers with 10-fold cross-validation.
- **Kernel Notes**: (1) Identify task runs from BIDS (task-offline, task-catch, task-sham). (2) Segment each run into 1s windows with 62.5ms overlap. (3) Compute alpha-band (8-13 Hz) power in left vs right posterior channels. (4) Calculate lateralization index: (R-L)/(R+L) per window. (5) Derive trial labels from experimental design metadata (cue direction) since no event markers exist in BIDS. (6) Train classifier (e.g., LDA) to predict left vs right attention from alpha-LI features.

### Primary Task 2: Alpha Lateralization Index Regression (Continuous)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.9375
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**: Continuous alpha lateralization index (alpha-LI) computed from EEG power in alpha band (8-13 Hz)
- **Super Meta Notes**: For each 1s sliding window, compute alpha power in left posterior channels (O1, PO7, P7, etc.) and right posterior channels (O2, PO8, P8, etc.). Alpha-LI = (R - L) / (R + L). Higher positive values indicate rightward lateralization, lower (negative) indicate leftward.
- **Evidence**:
  - DOI: 10.1007/s10548-019-00725-9 — Real-time neurofeedback study where participants learned to control alpha lateralization; the alpha-LI is the primary feature used for both feedback and classification.
- **Kernel Notes**: (1) Bandpass filter EEG 8-13 Hz. (2) Segment into 1s windows with 62.5ms overlap. (3) Compute RMS/band power in left vs right posterior ROI. (4) Calculate alpha-LI per window as regression target. (5) Store as misc channel for downstream use.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level labels available))
- **Notes**: Continuous neurofeedback paradigm; alpha lateralization index may be computed from raw EEG as a continuous target if desired.

## Data Quality Notes

- No trial-level event markers detected in any EEG files; only continuous recordings available.
- Real-time neurofeedback paradigm - EEG signal itself contains the task-relevant information.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Real-time EEG Feedback on Alpha Power Lateralization Leads to Behavioral Improvements in a Covert Attention Task`
