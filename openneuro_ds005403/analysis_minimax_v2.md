# Delayed Auditory Feedback EEG/EGG

**Dataset**: `openneuro_ds005403` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005403
**Category**: High-level Mental | **Subjects**: 66 | **Files (Completed)**: 66
**Channels**: 66 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed a speech production task while receiving delayed auditory feedback (DAF) to study neural processing of self-generated speech and auditory-motor monitoring. Three DAF conditions were used: an adaptation condition (fixed delay) and two random delay conditions (random1, random2), compared against a baseline (no delay). EEG was recorded alongside electroglottography (EGG) to capture vocal fold activity simultaneously. The event markers label continuous speech production blocks.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005403

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `adaption` | ~64/file | long | raw | Adaptation DAF condition block |
| `random1` | ~64/file | long | raw | Random delay condition 1 block |
| `random2` | ~64/file | long | raw | Random delay condition 2 block |
| `baseline` | ~64/file | rest | raw | Baseline (no delay) speech block |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: EEG Encoding/Decoding of Glottal and Audio Features During DAF
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = * (full block duration), overlap = 0.0 *, target_events = [`baseline`, `adaption`]
- **Label Route**: `misc`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `baseline` | continuous | Baseline (no delay) speech production block |
  | `adaption` | continuous | Adaptation DAF condition block |
- **Super Meta Notes**: Features (audio envelope, audio onsets, EGG envelope, EGG onsets) are derived from raw audio/EGG signals through signal processing (gammatone filter bank, envelope computation, onset detection).
- **Evidence**:
  - DOI: 10.1523/jneurosci.2294.24.2025 — Encoding models predict EEG from glottal/audio features; decoding models predict glottal event onsets from EEG during speech production with delayed auditory feedback
- **Kernel Notes**: 
    1. Extract raw EEG epochs aligned to baseline/adaption blocks using epoch_by_long_event_hdf5
    2. Derive audio envelope from raw audio channels (if available) or generate synthetic envelope features
    3. Derive EGG envelope from EGG channel (channel type check required)
    4. Compute onset times from audio envelope and EGG envelope
    5. Compute time-lagged features (e.g., -0.5s to +0.5s around each EEG time point)
    6. Train encoding model: predict EEG from audio/EGG features using ridge regression or similar
    7. Train decoding model: predict glottal event onsets from EEG using regression

### Normal Task 1: DAF Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: All four conditions are sustained speech production blocks (>=2 s). Simultaneous EGG channels included; verify channel naming in channel metadata.

| Event | y | Meaning |
|-------|---|----------|
| `baseline` | 0 | Baseline (no delay) |
| `adaption` | 1 | Adaptation DAF condition |
| `random1` | 2 | Random delay condition 1 |
| `random2` | 3 | Random delay condition 2 |


## Data Quality Notes

- Simultaneous EGG recording alongside EEG - verify channel type labels.
- Speech production task - EMG artifacts from jaw/throat movement expected.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `Delayed Auditory Feedback EEG/EGG`
