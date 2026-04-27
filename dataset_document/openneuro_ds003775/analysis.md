# SRM Resting-State EEG

**Dataset**: `openneuro_ds003775` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003775
**Category**: Biological State | **Subjects**: 111 | **Files (Completed)**: 152 | **Channels**: 64 | **Sampling Rate**: 1024 Hz
**Manual Review**: Pending

## Paradigm

Four minutes of uninterrupted eyes-closed resting-state EEG recorded from healthy adult participants as part of a larger experimental paradigm. This dataset was collected to provide a normative baseline for comparing resting EEG characteristics across studies. The resting-state recording provides a standardized, task-free EEG sample suitable for spectral power analysis, functional connectivity, and individual difference studies.

## File Scan Result

> **Kernel SHA256**: `e962bd927fb0b37a55f8e4f9c5988bcf17e17df5e2de6e262fcb438084b429db`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `resting-state-eyes-closed` | 152 | event | raw | Eyes-closed resting-state recording segment |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Age Regression from Resting-State EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | age | Subject age in years (continuous) |
- **Super Meta Notes**: Derived from dataset subject metadata (demographics CSV). Kernel step: Extract subject age from BIDS participants.tsv and map to each epoch segment.
- **Evidence**:
  - DOI: `10.1016/j.clinph.2024.09.019` — ComBat harmonization study explicitly using Oslo dataset (n=111) from openneuro ds003775 for spectral feature correlation with age
  - DOI: `10.1016/j.dib.2022.108647` — Dataset documentation confirming 111 subjects with age metadata available in participants.tsv; confirms utility for age-based machine learning
- **Kernel Notes**: Extract 5-second epochs from continuous resting-state signal using sliding window with 50% overlap. Load participant ages from dataset metadata (participants.tsv). Train regression model to predict age from spectral features (alpha, beta, theta, delta power, aperiodic components). Ensure epochs from same subject stay in same cross-validation fold to prevent data leakage. (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Sex Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | male | Male subject |
  | N/A (continuous) | female | Female subject |
- **Super Meta Notes**: Derived from dataset subject metadata (demographics CSV). Kernel step: Extract subject sex from BIDS participants.tsv and map to each epoch segment.
- **Evidence**:
  - DOI: `10.1016/j.dib.2022.108647` — Dataset documentation explicitly states data can be used for "machine learning classification of age/sex"; confirms sex labels in participants.tsv
  - DOI: `10.1016/j.clinph.2024.09.019` — Same dataset used for harmonization analysis includes sex as a covariate alongside age
- **Kernel Notes**: Extract 5-second epochs from continuous resting-state signal using sliding window with 50% overlap. Load participant sex from dataset metadata (participants.tsv). Train binary classifier to predict sex from spectral features. Apply subject-level cross-validation splits to prevent leakage given 153 files from 111 subjects (some have multiple sessions). (replaces Classical Task 2 from original analysis.md)

### Potential Task 1: Resting State EEG Segmentation (Unsupervised)
- **Task Type**: clustering
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous) | N/A (null) | No labels; unsupervised/individual differences analysis |
- **Super Meta Notes**: No target labels; epochs used for exploratory analyses.
- **Evidence**:
  - DOI: `10.1016/j.dib.2022.108647` — Dataset documentation describes 4-minute eyes-closed resting-state suitable for spectral power, connectivity, and individual difference studies; no discrete trial events, only continuous recording with resting-state annotation
- **Kernel Notes**: Pure 4-minute eyes-closed resting-state with no discrete events. Extract 2-second epochs with 50% overlap for finer temporal resolution. Use for exploratory analyses such as individual alpha frequency estimation, microstate analysis, sliding-window connectivity metrics, or unsupervised clustering. The only available event `resting-state-eyes-closed` (152 occurrences) marks the continuous recording segments rather than discrete trial markers. Suitable for normative baseline characterization and individual differences research.