# A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects

**Dataset**: `openneuro_ds004504` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004504
**Category**: Biological State | **Subjects**: 88 | **Files (Completed)**: 176
**Channels**: 19 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings with eyes closed collected from healthy controls and patients with Alzheimer's disease (AD) and Frontotemporal Dementia (FTD). The study provides a clinical EEG dataset for developing diagnostic biomarkers and machine learning classifiers to differentiate neurodegenerative conditions from healthy aging.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004504

## Event Structure

_No event markers detected (`no_events`). This dataset contains resting-state EEG recordings without trial-level annotations._

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds004504 DOI: https://doi.org/10.3390/diagnostics11081437


### Normal Task 1: Dementia Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (subject-level labels from participants.tsv)
- **Notes**: Subject-level diagnosis labels (HC/AD/FTD) in participants.tsv used as ground truth. 19-channel 10-20 system EEG; standard clinical montage. 2 sessions per subject (176 files / 88 subjects).
## Data Quality Notes

- No trial-level event markers; pure resting-state dataset
- Subject diagnosis labels (HC/AD/FTD) available in participants.tsv
- Standard 10-20 montage (19 channels)
- 2 recordings per subject (176 files / 88 subjects)

## References

- **Reference**: `A Dataset of Scalp EEG Recordings of Alzheimers Disease, Frontotemporal Dementia and Healthy Subjects from Routine EEG`
