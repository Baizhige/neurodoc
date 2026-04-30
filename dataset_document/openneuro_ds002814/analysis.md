# A Multimodal Neuroimaging Dataset to Study Spatiotemporal Dynamics of Visual Processing in Humans

**Dataset**: `openneuro_ds002814` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002814
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 168 | **Channels**: 68 | **Sampling Rate**: 1200 Hz | **Manual Review**:

## Paradigm

A multimodal neuroimaging study (EEG + MEG/MRI) investigating the spatiotemporal dynamics of visual processing in humans. Despite the dataset title implying an active visual processing task, no event markers are detectable in the BIDS EEG files. The visual stimulation protocol may be encoded in other modality files or events are not available in the EEG files processed by the locator pipeline.

## File Scan Result

> **Kernel SHA256**: `76d6a1e02e2103b4a6de56938e3866a6618f85f4a1093e5ec755c47725bb3fbb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Visual Category Classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`stimulus_onset`, `category_presentation`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus_onset` (animals) | 0 | Animal category presentation |
  | `stimulus_onset` (chairs) | 1 | Chair category presentation |
  | `stimulus_onset` (faces) | 2 | Face category presentation |
  | `stimulus_onset` (fruits) | 3 | Fruit category presentation |
  | `stimulus_onset` (vehicles) | 4 | Vehicle category presentation |
- **Evidence**:
  - DOI: `10.1101/2022.05.12.491595` — Performs EEG category classification decoding among 5 visual object categories (animals, chairs, faces, fruits, vehicles) using SVM classifiers on epochs extracted from -100ms to +600ms relative to stimulus onset
- **Kernel Notes**: Verify event ID mapping from events.tsv. Paper indicates stimulus_onset events exist for epoching. Labels may be stored in a separate condition or trial_type column rather than as separate event IDs. Map trial_type values (animal/chair/face/fruit/vehicle) to numeric class labels 0-4.

### Potential Task 1: Resting / Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null - no trial-level labels available)
- **Notes**: High sampling rate (1200 Hz); downsampling recommended. Part of a multimodal dataset - check MEG/MRI files for corresponding event timing.

## Data Quality Notes

- No event markers detected in any of the 168 EEG files.
- High sampling rate (1200 Hz); downsampling required before most analyses.
- Part of multimodal dataset; MEG or MRI-derived event timing may be applicable if aligned.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
