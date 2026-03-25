# Bimodal dataset on Inner speech

**Dataset**: `openneuro_ds004196` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004196
**Category**: High-level Mental | **Subjects**: 4 | **Files (Completed)**: 4 | **Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

An inner-speech production task where participants mentally vocalized eight specific words from social and numeric categories during nonsimultaneous EEG and fMRI recording. Subjects imagined speaking words without producing overt speech or movement. No trial-level event markers were embedded in the EEG recordings; the data is treated as continuous.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004196

## Event Structure

No trial events detected. This dataset contains continuous EEG without trial-level annotations.

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Inner Speech
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004196 DOI: https://doi.org/10.1101/2022.05.24.492109


### Normal Task 1: Inner Speech Segmentation (resting)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null)
- **Notes**: No event markers available. Sliding window segmentation only.
## Data Quality Notes

- Very small dataset (N=4); not suitable for cross-subject generalization
- Consider using fMRI labels aligned to EEG timing if available

## References

- **Reference**: `Bimodal dataset on Inner speech`
