# Resting EEG with Structural MRI

**Dataset**: `openneuro_ds006525` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006525
**Category**: Biological State | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 128 | **Sampling Rate**: 250 Hz

## Paradigm

Spontaneous brain activity was recorded during resting-state EEG, supplemented by structural MRI scans. The dataset captures baseline neural dynamics in the absence of any task. Event markers include resting-state block onset (`rsts`), offset (`rstf`), and a session-begin marker (`bgin`), enabling segmentation of clean resting periods.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006525

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | 20400 | long | raw | Session begin marker |
| `rsts` | 20400 | rest | raw | Resting-state block start |
| `rstf` | 34 | rest | raw | Resting-state block finish/end |
| `NRST` | 34 | admin | raw | Non-resting state marker |
| `DIN` | 2 | admin | raw | Digital input trigger |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds006525 DOI: https://doi.org/10.3389/fninf.2021.770608


### Normal Task 1: Resting-State Segmentation (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `rsts` and `rstf` mark the boundaries of resting blocks; segment within these boundaries. `NRST` may indicate periods outside resting state that should be excluded.

 | Event | y | Meaning |
 |-------|---|---------|
 | `bgin` | 0 | Session begin |
 | `rsts` | 1 | Resting-state block start |
 | `rstf` | 2 | Resting-state block end |
 | `NRST` | 3 | Non-resting state period |
 | `DIN` | 4 | Digital input trigger |
## Data Quality Notes

- High channel count (128) with 250 Hz sampling rate; EGI/Geodesic system likely.
- `NRST` may indicate periods outside resting state that should be excluded from analysis.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

## References

- **Reference**: `Resting EEG`
