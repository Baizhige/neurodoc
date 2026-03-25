# Resting State EEG with Closed Eyes and Open Eyes in Females from 60 to 80 Years Old

**Dataset**: `openneuro_ds005420` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005420
**Category**: Biological State | **Subjects**: 72 | **Files (Completed)**: 72
**Channels**: 20 | **Sampling Rate**: 500 Hz

## Paradigm

Spontaneous resting-state EEG was recorded in a cohort of females aged 60-80 years during alternating eyes-open and eyes-closed conditions. The dataset investigates age-related changes in spontaneous brain activity in older women. No event markers were included in events.tsv; the EEG is stored as continuous recordings. Eyes-open vs. eyes-closed condition can be inferred from the file naming or participants.tsv.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005420

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous resting-state EEG recordings without trial-level annotations._

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Eyes-Open vs Eyes-Closed Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 1.0 s
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes-open (EO)` | 0 | Eyes open resting state condition |
  | `eyes-closed (EC)` | 1 | Eyes closed resting state condition |
- **Super Meta Notes**: Labels derived from file naming or participants.tsv; the dataset contains no event markers - continuous recordings with eyes-open/eyes-closed conditions inferred from metadata.
- **Evidence**:
  - DOI: 10.1109/ubmk67458.2025.11207051 — The paper used OpenNeuro ds005420 for cross-dataset validation, segmenting each raw file into 10-s epochs with 1.0-s overlap to generate sufficient samples for binary eyes-open vs eyes-closed classification using VGG-19 and custom CNN models.
- **Kernel Notes**: Extract eyes-open/eyes-closed condition from file naming (e.g., 'eo'/'ec' in filename) or participants.tsv. Apply segmentation to raw continuous EEG with 10-s windows and 1.0-s overlap. Map EO to class 0, EC to class 1.

### Normal Task 1: Resting-State Segmentation (segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null(no events; use file-level condition label for eyes-open/closed from filename or participants.tsv))
- **Notes**: No event markers. Only 20 EEG channels. Female-only sample aged 60-80. Eyes-open/closed condition may be in filename.

## Data Quality Notes

- No event markers - purely continuous resting-state recordings.
- 20-channel montage; limited spatial coverage.
- Female-only cohort aged 60-80; demographic info in participants.tsv.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

## References

- **Reference**: `EEG-BIDS, an extension to the brain imaging data structure for electroencephalography`
