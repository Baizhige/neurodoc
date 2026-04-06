# A Multimodal Neuroimaging Dataset to Study Spatiotemporal Dynamics of Visual Processing in Humans

**Dataset**: `openneuro_ds002814` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002814
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 168 | **Channels**: 68 | **Sampling Rate**: 1200 Hz

## Paradigm

A multimodal neuroimaging study (EEG + MEG/MRI) investigating the spatiotemporal dynamics of visual processing in humans. Despite the dataset title implying an active visual processing task, no event markers are detectable in the BIDS EEG files. The visual stimulation protocol may be encoded in other modality files or events are not available in the EEG files processed by the locator pipeline.

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 168
- **Age Completeness**: 168/168 (100.0%)
- **Sex Completeness**: 168/168 (100.0%)
- **Observed Age Examples**: `23`, `30`, `24`, `22`, `19`, `25`, `32`, `31`
- **Observed Sex Examples**: `Male`, `Female`
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds002814.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `e436e48f239db115957dccf5bc2307cb3ac75fbce463245b3e85cf82d5fd5c9e`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No task-relevant event labels currently materialized by kernel |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


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