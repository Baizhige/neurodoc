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
  | `WORD` (subsequently remembered) | 1 | Successful memory encoding |
  | `WORD` (subsequently forgotten) | 0 | Failed memory encoding |
- **Evidence**:
  - DOI: 10.1037/xlm0001341 — Uses OpenNeuro dataset ds004706 to train L2-penalized logistic regression classifiers on spectral features to decode successful versus failed memory encoding based on subsequent recall. Epoch window: 300ms-1300ms post word onset.
- **Kernel Notes**: Requires aligning WORD events with subsequent recall outcomes (REC_WORD) to derive labels. Extract spectral features (128 channels × 8 frequencies) from epoched data.

### Primary Task 2: Memory Retrieval Success Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = -0.05 s, target_events = [`REC_WORD`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `REC_WORD` (correct recall) | 1 | Successful retrieval |
  | `REC_WORD` (deliberation) | 0 | Failed/deliberation retrieval |
- **Evidence**:
  - DOI: 10.1037/xlm0001341 — Uses OpenNeuro dataset ds004706 to decode successful retrieval versus deliberation periods. Epoch window: 900ms-50ms prior to vocalization (tmin=-1.0s, tmax=-0.05s).
- **Kernel Notes**: Requires extracting pre-vocalization period of REC_WORD events to classify correct vs. deliberation responses.

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
 | `CUED_REC_WORD` | 3 | Cued recall response

## Data Quality Notes

- High sampling rate (2048 Hz) - downsample for efficiency.
- 30+ event types; focus on WORD/REC_WORD for memory encoding analysis.

## References

- **Reference**: `Spatial memory and non-invasive closed-loop stimulus timing`
