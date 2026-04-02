# Spatial Memory and Non-Invasive Closed-Loop Stimulus Timing

**Dataset**: `openneuro_ds004706` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004706
**Category**: High-level Mental | **Subjects**: 149 | **Files (Completed)**: 298
**Channels**: 137 | **Sampling Rate**: 2048 Hz

## Paradigm

A hybrid spatial-navigation and free recall task where participants delivered items to locations in a virtual town environment, with EEG recorded during both encoding and retrieval phases. The paradigm incorporates closed-loop stimulus timing to investigate the relationship between memory encoding, theta oscillations, and stimulation-driven memory enhancement. Sessions included free recall and cued recall phases with video stimuli.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004706

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `FFR_REC_WORD` | 55013 | short | raw | Free-form recall word event |
| `CUED_REC_STOP` | 44064 | short | raw | Cued recall stop marker |
| `CUED_REC_CUE` | 44064 | short | raw | Cued recall cue onset |
| `WORD` | 43260 | short | raw | Word stimulus onset (encoding) |
| `REC_WORD` | 39061 | short | raw | Recalled word event |
| `CUED_REC_WORD` | 34381 | short | raw | Cued recall word event |
| `CLASSIFIER_WAIT` | 22890 | short | raw | Closed-loop classifier waiting |
| `POINTER_ON` | 20872 | short | raw | Spatial navigation pointer onset |
| `CLASSIFIER` | 19005 | short | raw | Closed-loop classifier event |
| `EFR_MARK` | 11498 | short | raw | EFR (encoding-phase) marker |
| `CUED_REC_WORD_VV` | 11328 | short | raw | Cued recall word (video verified) |
| `TRIAL_END` | 2888 | short | raw | Trial end marker |
| `TRIAL_START` | 2884 | short | raw | Trial start marker |
| `REC_STOP` | 2952 | short | raw | Recording stop marker |
| `REC_START` | 2952 | short | raw | Recording start marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Memory Encoding Success Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.3 s, tmax = 1.3 s, target_events = [`WORD`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `WORD` | 1 | Word subsequently remembered (encoding success) |
  | `WORD` | 0 | Word subsequently forgotten (encoding failure) |
- **Kernel Notes**: Extract epochs centered on WORD events (0.3-1.3s post-onset). Derive labels by matching WORD events to subsequent REC_WORD events. If a WORD is followed by a REC_WORD with matching content, label as 1 (remembered); otherwise label as 0 (forgotten). Use spectral features (128 channels × 8 frequencies) for classification. (replaces Primary Task 1 & 2 from original analysis.md)
- **Evidence**:
  - DOI: 10.1037/xlm0001341 — Binary classification of memory encoding success using L2-penalized logistic regression on spectral features to decode remembered vs forgotten words

### Normal Task 1: Memory encoding/recall classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: High sampling rate (2048 Hz). BREAK_START/STOP, SESS_END are session markers. Closed-loop classifier events (CLASSIFIER, CLASSIFIER_WAIT) may interfere - treat as admin.

| Event | y | Meaning |
|-------|---|------|
| `WORD` | 0 | Word encoding |
| `REC_WORD` | 1 | Recalled word |
| `CUED_REC_CUE` | 2 | Cued recall cue |
| `CUED_REC_WORD` | 3 | Cued recall response |

## Data Quality Notes

- High sampling rate (2048 Hz) - downsample for efficiency.
- 30+ event types; focus on WORD/REC_WORD for memory encoding analysis.

