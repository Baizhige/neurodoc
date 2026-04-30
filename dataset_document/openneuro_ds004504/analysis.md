# A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects

**Dataset**: `openneuro_ds004504` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004504
**Category**: Biological State | **Subjects**: 88 | **Files (Completed)**: 176 | **Channels**: 19 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Resting-state EEG recordings with eyes closed were collected from 88 participants across three diagnostic groups: 36 with Alzheimer's disease (AD), 23 with Frontotemporal dementia (FTD), and 29 cognitively normal healthy controls (CN). Data were recorded using a 19-channel EEG system at 500 Hz sampling rate during a quiet, eyes-closed resting condition. The dataset is designed for developing EEG-based biomarkers and machine learning classifiers to differentiate neurodegenerative dementias from healthy aging and from each other.

## File Scan Result

> **Kernel SHA256**: `a5a077e03a8e97e9503e578a34a4e0100bd823268763bd9b43b023e84609fded`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | 176 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 3-class dementia classification (AD vs FTD vs CN)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | A | 0 | Alzheimer's disease (AD) |
  | Group | F | 1 | Frontotemporal dementia (FTD) |
  | Group | C | 2 | Healthy control (CN) |
- **Evidence**:
  - 10.3390/data8060095 — Dataset descriptor paper: 88 subjects (36 AD, 23 FTD, 29 CN), 4s windows with 50% overlap, resting-state eyes-closed EEG; Group column encodes diagnosis
  - 10.1016/j.clinph.2024.12.008 — Clinical validation using this dataset for dementia classification
  - 10.1016/j.jagp.2024.06.009 — Additional clinical application demonstrating discriminability of AD vs FTD vs CN
- **Notes**: Segmentation-based epoching required due to absence of event markers in resting-state recordings. The Group field from participants.tsv provides subject-level diagnostic labels mapped to 0/1/2 for multi-class classification.

### Classical Task 2: 2-class AD vs CN dementia classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | A | 0 | Alzheimer's disease (AD) |
  | Group | C | 1 | Cognitively normal (CN) |
- **Evidence**:
  - 10.1109/access.2023.3294618 — DICE-Net binary classification with 30s windows and 15s overlap, 83.28% AD-CN accuracy
  - 10.1016/j.clinph.2024.12.008 — SVM achieves 95% AD-HC accuracy with LOSO validation
- **Notes**: FTD group (F) excluded to create binary AD vs CN classification as per primary evidence. Segment-based epoching with 30s windows and 50% overlap (15s step) matches DICE-Net methodology. Group values: A=AD, C=CN, F=FTD; only A and C retained for this 2-class task.

### Classical Task 3: 2-class FTD vs CN dementia classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | F | 0 | Frontotemporal Dementia (FTD) |
  | Group | C | 1 | Cognitively Normal (CN) |
- **Evidence**:
  - 10.1109/access.2023.3294618 — DICE-Net binary classification with 30s windows and 15s overlap, 86% FTD-HC accuracy with SVM, LOSO validation
  - 10.1016/j.clinph.2024.12.008 — Supporting dementia classification methodology
- **Notes**: Participants with Group=A (Alzheimer's disease, N=36) are excluded from this 2-class task to focus on FTD vs CN discrimination as reported in the primary DICE-Net paper. The Group field values are 'A' (AD), 'C' (CN/control), and 'F' (FTD) per participants.tsv sample.

### Classical Task 4: 3-class dementia classification (AD vs FTD vs CN) - 30s windows
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.5, target_events = []
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | A | 0 | Alzheimer's disease (AD) |
  | Group | F | 1 | Frontotemporal dementia (FTD) |
  | Group | C | 2 | Healthy control (CN) |
- **Evidence**:
  - 10.1109/access.2023.3294618 — DICE-Net paper: 30s windows with 15s overlap (0.5) for 3-class AD vs FTD vs CN classification using LOSO validation on same 88-subject dataset (36 AD, 23 FTD, 29 CN)
- **Notes**: Segmentation-based task with no event anchors. Uses participants.tsv Group column (A/F/C) for 3-class classification. Longer 30s windows compared to other parameterizations may capture different temporal dynamics of resting-state EEG for dementia classification.

### Potential Task 1: 2-class AD vs FTD dementia classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5 *, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Group`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Group | A | 0 | Alzheimer's disease |
  | Group | F | 1 | Frontotemporal dementia |
- **Evidence**:
- **Notes**: Segmentation-based task using 4-second non-overlapping windows (50% overlap inferred from dataset descriptor). The Group info field is natively available in participants.tsv with values A (AD, N=36) and F (FTD, N=23). Healthy controls (C) are excluded to create a direct binary differential diagnosis task between the two dementia subtypes. This is a potential task with no explicit literature reference for this exact binary formulation, though the dataset was designed for dementia classification research.

### Potential Task 2: MMSE regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.5 *, target_events = []
- **Label Route**: `info`
- **Label Field**: `MMSE`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | MMSE | 14–30 (score) | Mini-Mental State Examination; 0-30 scale, lower = more severe cognitive decline. AD mean 17.75, FTD mean 22.17, CN mean 30. |
- **Evidence**:
  - (empty — potential task)
- **Notes**: Segmentation-based epochs (4s windows, 50% overlap) from continuous eyes-closed resting-state EEG. MMSE is a native participants.tsv column providing continuous cognitive severity scores, enabling regression rather than categorical group classification.

### Potential Task 3: Age regression from resting-state EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Age`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Range (unit) | Notes |
  |------------|--------------|-------|
  | Age | 57–79 (years) | Complete across N=88 subjects; AD mean 66.4 (sd=7.9), FTD mean 63.6 (sd=8.2), CN mean 67.9 (sd=5.4) |
- **Evidence**:
  - `participants.tsv` — Age column complete for all 88 subjects, range 57–79 years
  - `dataset_description.json` — References brain age prediction studies using this dataset (Miltiadous et al. 2023 DICE-net)
  - `README` — Documents age demographics by diagnostic group
- **Notes**: Resting-state EEG segmentation with 4s windows and 50% overlap for brain age prediction paradigm. Age values sourced directly from participants.tsv native info field; no kernel derivation required.

### Potential Task 4: Gender classification from resting-state EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: `segment_length = 4 s *, overlap = 0.5, target_events = []`
- **Label Route**: `info`
- **Label Field**: `Gender`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | Value | y | Meaning |
  |------------|-------|---|---------|
  | Gender | F | 0 | Female |
  | Gender | M | 1 | Male |
- **Evidence**:
- **Notes**: 2-class classification using subject-level gender information from participants.tsv. Segmentation creates multiple 4-second epochs per subject from continuous resting-state EEG; all epochs from a subject share the same gender label. No kernel derivation needed—Gender is a native participants.tsv column.

## Data Quality Notes

- No discrete event markers exist in raw recordings; all epoching must use continuous segmentation.
- Standard BIDS fields `subject_age` and `subject_sex` are missing, but equivalent demographic data (`Age`, `Gender`) are available as custom info fields with complete coverage.
- `device` field is missing; equipment details must be inferred from dataset documentation or sidecar files.
- Group encoding uses single-letter codes (A/C/F) rather than full diagnostic labels; mapping must be handled during label extraction.
- Class imbalance exists in diagnostic groups (36 AD, 23 FTD, 29 CN), which should be considered in model training and validation strategies.
- Leave-One-Subject-Out (LOSO) cross-validation is strongly recommended due to high within-subject correlation of segmented epochs.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
