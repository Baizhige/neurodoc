# A Multimodal Neuroimaging Dataset to Study Spatiotemporal Dynamics of Visual Processing in Humans

**Dataset**: `openneuro_ds002814` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002814
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 168 | **Channels**: 68.0 | **Sampling Rate**: 1200.0 Hz

## Paradigm

A multimodal neuroimaging study (EEG + MEG/MRI) investigating the spatiotemporal dynamics of visual processing in humans. Despite the dataset title implying an active visual processing task, no event markers are detectable in the BIDS EEG files. The visual stimulation protocol may be encoded in other modality files or events are not available in the EEG files processed by the locator pipeline.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds002814

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events

## Tasks

### Primary Task 1: 5-Class Visual Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`stimulus_onset`, `category_presentation`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | animals | 0 | Animal object category |
  | chairs | 1 | Chair object category |
  | faces | 2 | Face object category |
  | fruits | 3 | Fruit object category |
  | vehicles | 4 | Vehicle object category |
- **Evidence**:
  - DOI: 10.1101/2022.05.12.491595 — This paper describes the openneuro_ds002814 dataset and performs EEG category classification decoding among 5 visual object categories (animals, chairs, faces, fruits, vehicles) using SVM classifiers on epochs extracted from -100ms to +600ms relative to stimulus onset, achieving significant pairwise decoding accuracy.
- **Kernel Notes**: Extract epochs from -100ms to +600ms around stimulus onset events. Train SVM classifiers (one-vs-rest or pairwise) to decode visual object category from EEG features. High sampling rate (1200 Hz) may require downsampling for computational efficiency.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level labels available))
- **Notes**: No event markers found in EEG locator metadata. High sampling rate (1200 Hz); downsampling recommended. Part of a multimodal dataset - check MEG/MRI files for corresponding event timing.

## Data Quality Notes

- No event markers detected in any of the 168 EEG files.
- High sampling rate (1200 Hz); downsampling required before most analyses.
- Part of multimodal dataset; MEG or MRI-derived event timing may be applicable if aligned.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `A Multimodal Neuroimaging Dataset to Study Spatiotemporal Dynamics of Visual Processing in Humans`
