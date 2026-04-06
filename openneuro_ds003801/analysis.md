# Neural Tracking to Go

**Dataset**: `openneuro_ds003801` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003801
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 20
**Channels**: 24 | **Sampling Rate**: 250 Hz

## Paradigm

A mobile EEG study where participants performed a dichotic listening task (two competing speakers) while either sitting in a quiet indoor environment or walking along a pre-defined indoor route with environmental distractions. The study investigates how locomotion and environmental complexity affect neural tracking of attended speech (measured by auditory EEG envelope tracking). No discrete trial-level event markers were embedded in the EEG recording.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG during dichotic listening and walking |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Auditory Attention Decoding (Attended vs Ignored Speaker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attended_speaker` | 0 | Participant instructed to attend to this speaker |
  | `ignored_speaker` | 1 | Participant instructed to ignore this speaker |
- **Super Meta Notes**: Labels derived from experimental instruction (which speaker to attend). Kernel step: Compute correlation between reconstructed speech envelope (via mTRF) from EEG and both speaker audio envelopes. Classify based on which correlation is higher. Requires speech stimulus audio files for envelope extraction.
- **Evidence**:
  - DOI: 10.1088/1741-2552/ac42b5 — Used OpenNeuro ds003801 to decode which of two competing speakers participants were attending to during dichotic listening (sitting/walking) using mTRF models
  - DOI: 10.3389/fnhum.2024.1483024 — Used 60-s non-overlapping segments with mTRF to reconstruct speech envelopes and decode attended vs ignored speaker based on correlation strength
- **Kernel Notes**: Requires speech stimulus audio files (not included in EEG dataset). Must extract audio envelopes for both speakers. Fit mTRF model (multivariate linear regression) to predict speech envelope from EEG. Use time lags 0-500ms. Compare correlation of predicted envelope with attended vs ignored speaker envelopes. Walking condition has significant motion artifacts; consider artifact rejection.

### Classical Task 2: Condition Classification (Sitting vs Walking)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `sitting` | 0 | Participant seated in quiet indoor environment |
  | `walking` | 1 | Participant walking along pre-defined indoor route |
- **Super Meta Notes**: Condition labels obtained from file-level metadata. Kernel step: Segments from each recording file inherit condition label from file metadata.
- **Evidence**:
  - DOI: 10.1088/1741-2552/ac42b5 — Study performed during both sitting and walking conditions
  - DOI: 10.3389/fnhum.2024.1483024 — Experiments conducted in single/dual-speaker conditions during sitting and walking
- **Kernel Notes**: Condition label is file-level metadata. Walking segments will have motion artifacts; may need specialized preprocessing.

### Potential Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null (conditional label sit/walk needs to be obtained from file-level metadata))
- **Notes**: Mobile EEG; motion artifacts expected during walking condition. 20 subjects, 20 files (1 per subject). Condition (sitting/walking) is file-level metadata. Neural tracking of speech envelope requires cross-correlation with audio stimulus waveform. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- Mobile EEG recording; significant motion artifacts during walking condition.
- No trial-level event markers; condition label is file-level or block-level.
- Small dataset (20 subjects, 20 files); limited statistical power.
- 24-channel EEG at 250 Hz; modest spatial and temporal resolution.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review