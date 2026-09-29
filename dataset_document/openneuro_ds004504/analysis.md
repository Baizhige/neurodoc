# A dataset of EEG recordings from: Alzheimer's disease, Frontotemporal dementia and Healthy subjects

**Dataset**: `openneuro_ds004504` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004504
**Category**: Biological State | **Subjects**: 88 | **Files (Completed)**: 176 | **Channels**: 19 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Resting-state EEG recordings with eyes closed were collected from 88 participants across three diagnostic groups: 36 with Alzheimer's disease (AD), 23 with Frontotemporal dementia (FTD), and 29 cognitively normal healthy controls (CN). Data were recorded using a 19-channel EEG system at 500 Hz sampling rate during a quiet, eyes-closed resting condition. The dataset is designed for developing EEG-based biomarkers and machine learning classifiers to differentiate neurodegenerative dementias from healthy aging and from each other.

## File Scan Result

> **Kernel SHA256**: `bf522927b635f7a26208a29133fbf0cc072d017e9bf1d12d0071f47864b7a2da`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | 176 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- No discrete event markers exist in raw recordings; all epoching must use continuous segmentation.
- Standard BIDS fields `age` and `sex` are missing, but equivalent demographic data (`Age`, `Gender`) are available as custom info fields with complete coverage.
- `device` field is missing; equipment details must be inferred from dataset documentation or sidecar files.
- Group encoding uses single-letter codes (A/C/F) rather than full diagnostic labels; mapping must be handled during label extraction.
- Class imbalance exists in diagnostic groups (36 AD, 23 FTD, 29 CN), which should be considered in model training and validation strategies.
- Leave-One-Subject-Out (LOSO) cross-validation is strongly recommended due to high within-subject correlation of segmented epochs.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
