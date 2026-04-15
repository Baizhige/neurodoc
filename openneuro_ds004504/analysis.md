# A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects

**Dataset**: `openneuro_ds004504` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004504
**Category**: Biological State | **Subjects**: 88 | **Files (Completed)**: 176
**Channels**: 19 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG recordings with eyes closed collected from healthy controls and patients with Alzheimer's disease (AD) and Frontotemporal Dementia (FTD). The study provides a clinical EEG dataset for developing diagnostic biomarkers and machine learning classifiers to differentiate neurodegenerative conditions from healthy aging.

## File Scan Result

> **Kernel SHA256**: `b26ad48f7cead5fe7b38c01bb72f72c38f9f5af9c8f0a24952fda0982e746fbe`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | 176 | event | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Resting-state EEG Dementia Classification (AD vs FTD vs CN)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, tmin = 0.0, tmax = 4.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AD` | 0 | Alzheimer's disease diagnosis |
  | `FTD` | 1 | Frontotemporal dementia diagnosis |
  | `CN` | 2 | Cognitively normal / Healthy controls |
- **Kernel Notes**: No discrete event markers exist in this dataset. Labels must be propagated from subject-level diagnosis in `participants.tsv` via super meta. For each segmented epoch, assign the diagnostic label of the subject (AD/FTD/CN) from which the epoch was recorded. Use Leave-One-Subject-Out validation to prevent data leakage since epochs from the same subject are highly correlated. Class composition: 36 AD, 23 FTD, 29 CN.
- **Evidence**:
  - DOI: 10.1016/j.clinph.2024.12.008 — SVM classifiers with time-frequency connectivity features achieved 95% accuracy for AD vs HC and 86% for FTD vs HC on this dataset.
  - DOI: 10.1109/access.2023.3294618 — DICE-Net binary classification (AD-CN, FTD-CN) using 30s windows with 15s overlap on 88 subjects (36 AD, 23 FTD, 29 CN).
  - DOI: 10.3390/data8060095 — Direct dataset publication; benchmarks 4s windows with 50% overlap for AD/FTD/CN classification using Leave-One-Subject-Out validation.
  - DOI: 10.1016/j.jagp.2024.6.009 — Beta-to-Theta entropy ratio analysis on the same dataset; explicitly confirms 29 HC, 23 FTD, 36 AD composition.

### Potential Task 1: Resting-state EEG Dementia Classification with Shorter Windows (AD vs FTD vs CN)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5, tmin = 0.0, tmax = 2.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `AD` | 0 | Alzheimer's disease diagnosis |
  | `FTD` | 1 | Frontotemporal dementia diagnosis |
  | `CN` | 2 | Cognitively normal / Healthy controls |
- **Kernel Notes**: Alternative segmentation using 2s windows with 50% overlap providing finer temporal resolution at the cost of more epochs. Labels must be propagated from subject-level diagnosis in participants.tsv via super meta. No discrete event markers exist in this dataset. Consider class imbalance (36 AD, 23 FTD, 29 CN) during training.
- **Evidence**: None (plausible from paradigm alone; 2s windows provide higher temporal resolution for capturing transient EEG dynamics while maintaining sufficient frequency resolution for delta-alpha analysis)