# Subcortical responses to music and speech are alike while cortical responses diverge

**Dataset**: `openneuro_ds004356` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004356
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 24
**Channels**: 34 | **Sampling Rate**: 10000 Hz
**Manual Review**: Pending

## Paradigm

The study measures subcortical Auditory Brainstem Responses (ABR) and cortical auditory evoked potentials to continuous music and speech stimuli using a deconvolution method. Participants passively listened to different audio categories while continuous EEG was recorded at 10,000 Hz from 34 channels. The paradigm compares neural encoding of music versus speech at both subcortical and cortical levels, with click trains serving as a control condition for ABR baseline measurement.

## File Scan Result

> **Kernel SHA256**: `b639ef8e96701c29739e6b30f2e22d6f83e9c44ae028259f63acbad7e75782fb`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 12733 | event | raw | Continuous music stimulus block (or click train control) |
| `Stimulus/S  2` | 10771 | event | raw | Continuous music stimulus block |
| `Stimulus/S  4` | 69798 | event | raw | Continuous music stimulus block |
| `Stimulus/S  8` | 51688 | event | raw | Continuous speech stimulus block |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Music vs Speech Binary Classification from Auditory Brainstem Responses
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12.0 s, overlap = 0.0, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  4`, `Stimulus/S  8`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S  1` | 0 | Music stimulus block |
  | `Stimulus/S  2` | 0 | Music stimulus block |
  | `Stimulus/S  4` | 0 | Music stimulus block |
  | `Stimulus/S  8` | 1 | Speech stimulus block |
- **Evidence**:
  - DOI: 10.1038/s41598-023-50438-0 — Binary classification of music vs speech based on auditory brainstem responses (ABR) using deconvolution on continuous 12s stimuli from OpenNeuro dataset ds004356
  - DOI: 10.1101/2022.10.14.512309 — Preprint version demonstrating music vs speech subcortical response comparison with same paradigm
- **Kernel Notes**: Extract continuous 12s stimulus blocks. Apply bandpass filtering for subcortical ABR (70-2000 Hz) or cortical analysis (0.5-40 Hz) depending on target response. Actual event IDs are Stimulus/S numeric codes (1,2,4,8) requiring mapping to descriptive categories from events.tsv metadata. Label 0 = music categories, label 1 = speech categories. The paper analyzes subcortical kernel [0,15]ms and cortical kernel [0,200]ms responses.

### Classical Task 2: Click Train ABR Control Task
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12.0 s, overlap = 0.0, target_events = [`Stimulus/S  1`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S  1` | 0 | Click train control stimulus |
- **Evidence**:
  - DOI: 10.1038/s41598-023-50438-0 — Uses click train stimuli as control condition for measuring auditory brainstem responses
- **Kernel Notes**: Extract continuous click train blocks (12s duration). Click trains serve as reference/control condition for ABR baseline. Apply appropriate ABR filtering (70-2000 Hz). Event code 1 has lowest count (12,733) consistent with separate click train blocks vs continuous stimulus blocks.