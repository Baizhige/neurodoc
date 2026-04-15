# Rest Eyes Open (Parkinson's Disease)

**Dataset**: `openneuro_ds004584` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004584
**Category**: Biological State | **Subjects**: 149 | **Files (Completed)**: 149 | **Channels**: 63 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG was collected from 149 participants (100 with Parkinson's disease and 49 healthy controls) who sat quietly with eyes open for approximately two minutes. The study characterizes spontaneous neural oscillatory patterns to differentiate PD patients from controls. No active task was required; participants fixated on a cross and remained still.

## File Scan Result

> **Kernel SHA256**: `de7bae0b0747c90586ecbdc69f8f1887fc75dfde0032dac7dc4c482e8c058d06`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `boundary` | 149 | event | raw | Segment boundary marker inserted by recording software (exclude) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Cognitive Impairment Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `cognitively_normal` | 0 | MoCA score >= 26 |
  | `cognitive_impairment` | 1 | MoCA score < 26 |
- **Super Meta Notes**: Derived from MoCA (Montreal Cognitive Assessment) scores in participants.tsv. Kernel step: Read MoCA column from participants.tsv, binarize with threshold 26, assign to each participant's all epochs.
- **Evidence**:
  - DOI: 10.21203/rs.3.rs-2666578/v1 — Shows LEAPD algorithm classifies cognitive impairment (MoCA<26) vs normal (MoCA>=26) from resting-state EEG with 80% accuracy on this dataset.
  - DOI: 10.1038/s41531-023-00602-0 — Confirms same dataset (100 PD + 49 controls) used for cognitive impairment detection using linear predictive coding.
- **Kernel Notes**: Extract continuous resting-state EEG (~2-3 min per subject). Apply sliding-window segmentation. Compute spectral features (alpha, beta power) or LPC coefficients per segment. Use participant-level MoCA-derived labels for training.

### Classical Task 2: Parkinson's Disease vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `healthy_control` | 0 | Control participant (no Parkinson's disease) |
  | `parkinsons_disease` | 1 | Participant with Parkinson's disease |
- **Super Meta Notes**: Derived from participant group labels in participants.tsv. Kernel step: Read group/diagnosis column from participants.tsv, assign PD=1, control=0 to each participant's epochs.
- **Evidence**:
  - DOI: 10.1038/s41398-025-03506-0 — Uses resting-state EEG from this dataset to classify Parkinson's disease vs healthy controls using frontal Alpha inter-hemispheric synchronization.
- **Kernel Notes**: Compute Alpha band (8-13 Hz) envelope correlations between contralateral/ipsilateral frontal channels using sliding windows. Extract synchronization features per segment. Use participant-level PD/control labels for training.

### Potential Task 1: Resting State Segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: None (no task events)
- **Evidence**: None
- **Kernel Notes**: Only `boundary` admin markers present; no behavioral or stimulus events. Sliding-window segmentation required for resting-state data. Shorter 2s segments with 50% overlap provide fine-grained temporal coverage for exploratory spectral or connectivity feature extraction. PD/control group labels available in participants.tsv for downstream classification tasks.