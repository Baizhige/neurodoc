# Attended speaker paradigm (cEEGrid data)

**Dataset**: `openneuro_ds004015` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004015
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 36
**Channels**: 18 | **Sampling Rate**: 500 Hz

## Paradigm

A two-competing speaker auditory attention paradigm in which participants were instructed to selectively attend to one of two simultaneously presented audiobooks under varying spatial (same location vs. different locations) and loudness conditions. EEG was recorded using a cEEGrid around-the-ear electrode array. The dataset is intended for auditory attention decoding (AAD) research using ear-worn EEG.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004015

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations; stimulus delivery is continuous (audiobook streams)._

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Auditory Attention Classification (Attended vs Ignored Speaker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attended_speaker` | 1 | Participant attended to this audiobook |
  | `ignored_speaker` | 0 | Participant ignored this audiobook |
- **Super Meta Notes**: Derived from experimental instructions - participants were instructed which audiobook to attend to throughout each block. The attended vs ignored speaker labels are derived from the task design, not from raw event markers. Kernel step: Load participant metadata files to determine attended speaker condition per block; assign labels to corresponding EEG segments.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.869426 — Shows cEEGrid data from 36 participants attending to one of two simultaneous audiobooks, using speech envelope tracking decoding to classify which speaker was attended (71-82% accuracy)
- **Kernel Notes**: Segment continuous EEG into 60s non-overlapping windows aligned with experimental blocks. Use task metadata to determine which speaker (left/right audiobook) was attended during each block. Apply speech envelope tracking features or alternative features (spectral entropy, ISC) for classification. (replaces Primary Task 1 from original analysis.md)

### Normal Task 1: Auditory Attention Decoding - Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (attended speaker label from task metadata)
- **Notes**: cEEGrid only provides 18 channels around the ear; limited spatial coverage compared to standard scalp EEG. Auditory attention decoding typically requires aligning EEG segments with envelope of the attended speech stream. No discrete event markers; stimulus is continuous.

## Data Quality Notes

- Only 18 around-the-ear channels (cEEGrid) - very limited spatial coverage
- No discrete event markers; continuous stimulus paradigm
- Attended speaker condition metadata needed from external files for supervised learning

