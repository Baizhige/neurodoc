# Attended speaker paradigm (cEEGrid data)

**Dataset**: `openneuro_ds004015` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004015
**Category**: High-level Mental | **Subjects**: 36 | **Files (Completed)**: 36
**Channels**: 18 | **Sampling Rate**: 500 Hz

## Paradigm

A two-competing speaker auditory attention paradigm in which participants were instructed to selectively attend to one of two simultaneously presented audiobooks under varying spatial (same location vs. different locations) and loudness conditions. EEG was recorded using a cEEGrid around-the-ear electrode array. The dataset is intended for auditory attention decoding (AAD) research using ear-worn EEG.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations; stimulus delivery is continuous (audiobook streams)._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Auditory Attention Classification (Attended vs Ignored Speaker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attended_speaker` | 1 | Participant attended to this audiobook |
  | `ignored_speaker` | 0 | Participant ignored this audiobook |
- **Super Meta Notes**: Derived from experimental instructions - participants were instructed which audiobook to attend to throughout each block. The attended vs ignored speaker labels are derived from the task design, not from raw event markers. Kernel step: Load participant metadata files to determine attended speaker condition per block; assign labels to corresponding EEG segments.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.869426 — Shows cEEGrid data from 36 participants attending to one of two simultaneous audiobooks, using speech envelope tracking decoding to classify which speaker was attended (71-82% accuracy)
- **Kernel Notes**: Segment continuous EEG into 60s non-overlapping windows aligned with experimental blocks. Use task metadata to determine which speaker (left/right audiobook) was attended during each block. Apply speech envelope tracking features or alternative features (spectral entropy, ISC) for classification. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Auditory Attention Decoding - Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: None (attended speaker label from task metadata)
- **Notes**: cEEGrid only provides 18 channels around the ear; limited spatial coverage compared to standard scalp EEG. Auditory attention decoding typically requires aligning EEG segments with envelope of the attended speech stream. No discrete event markers; stimulus is continuous.

## Data Quality Notes

- Only 18 around-the-ear channels (cEEGrid) - very limited spatial coverage
- No discrete event markers; continuous stimulus paradigm
- Attended speaker condition metadata needed from external files for supervised learning


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review