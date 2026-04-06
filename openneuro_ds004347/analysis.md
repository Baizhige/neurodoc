# Symmetry perception and affective responses: a combined EEG/EMG study

**Dataset**: `openneuro_ds004347` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004347
**Category**: Sensory/Response | **Subjects**: 24 | **Files (Completed)**: 24
**Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

Participants performed a visual perception task identifying whether stimuli were regular (symmetric) or random (asymmetric) patterns to investigate symmetry perception and affective responses. EEG and EMG were simultaneously recorded to capture both neural and facial muscle activity. No trial-level event markers are present in the EEG files; the dataset is processed as continuous recordings.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations._


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

### Potential Task 1: Continuous Segmentation (resting/segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**:
  | Segment Condition | y | Meaning |
  |------------------|---|--------|
  | Pre-stimulus baseline | 0 | Window before stimulus onset (if available from external metadata) |
  | Symmetry condition | 1 | Reflectional/rotational symmetry trials (from experimental design) |
  | Asymmetry condition | 2 | Random/asymmetric patterns (from experimental design) |
- **Evidence**:
  - DOI: `10.1016/j.neuropsychologia.2012.10.003` — Paper describes symmetry vs random pattern classification with 80 trials per condition per participant, analyzing ERPs and time-frequency power
- **Kernel Notes**: No trial-level event markers present in EEG files (only `no_events` admin marker). Kernel must use external metadata ( stimulus timing files) to derive condition labels per time segment. Apply sliding window segmentation across continuous recording, then merge with condition labels from experimental design log. (replaces Potential Task 1 from original analysis.md)

## Data Quality Notes

- No trial-level event markers in the EEG files
- 73 channels includes EMG/EOG channels that should be excluded from EEG analysis
- Continuous recordings suitable for spectral or connectivity analysis


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review