# Dataset containing resting EEG for a sample of 103 normal infants in the first year of life

**Dataset**: `openneuro_ds004577` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004577
**Category**: Biological State | **Subjects**: 103 | **Files (Completed)**: 103 | **Channels**: 128 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings from 103 healthy infants (aged 1-12 months) during the first year of life. Recordings were made during natural infant rest/sleep states. Eyes-open and eyes-closed state markers are present but the primary data is continuous infant resting EEG. The dataset supports developmental neuroscience research on early brain maturation.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004577

## Event Structure

_No task event markers. State markers (eyes_closed, eyes_open) and artifact markers (discontinuity) are present but the dataset is primarily resting-state continuous EEG._

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `eyes_closed` | ~103xN | rest | raw | Eyes-closed resting state |
| `eyes_open` | ~103xN | rest | raw | Eyes-open resting state |
| `discontinuity` | ~103xN | admin | raw | Recording discontinuity/artifact marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Normal Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes_closed` | - | Eyes-closed resting state segment |
  | `eyes_open` | - | Eyes-open resting state segment |
- **Notes**: Infant resting EEG without trial structure. discontinuity markers indicate artifact segments. Use sliding window segmentation; consider excluding segments surrounding discontinuity markers. 
- **Kernel Notes**: Apply segmentation across continuous recording. Optionally filter out windows containing or adjacent to `discontinuity` events to avoid artifact-corrupted segments. This replaces the placeholder Primary Task 1 from original analysis.


## Data Quality Notes

- 103 infants aged 1-12 months; high variability in developmental stage
- 128 channels; high-density pediatric EEG cap
- discontinuity markers indicate artifact/movement artifacts in infant recordings

## References

- **Reference**: `Dataset containing resting EEG for a sample of 103 normal infants in the first year of life`
