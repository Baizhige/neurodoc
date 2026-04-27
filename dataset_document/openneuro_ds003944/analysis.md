# EEG: First Episode Psychosis vs. Control Resting-State EEG

**Dataset**: `openneuro_ds003944` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003944
**Category**: Biological State | **Subjects**: 82 | **Files (Completed)**: 82 | **Channels**: 64 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A 5-minute eyes-open resting-state EEG recording comparing spontaneous brain activity between individuals with First Episode Psychosis (FEP) and age-matched healthy controls. The dataset is designed to identify EEG biomarkers of psychosis onset using machine learning approaches. No trial-level stimuli are presented; the label of interest is the clinical group membership (FEP vs. control) stored in participants.tsv. Each subject performed a single continuous 5-minute recording while maintaining eyes-open rest.

## File Scan Result

> **Kernel SHA256**: `5eecba9d39f0f731fe85fa7b3831e1dd4d05902987b87e3c939b5c0368eceaa6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: First Episode Psychosis vs. Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `Control` | 0 | Healthy control subject |
  | `FEP` | 1 | First Episode Psychosis patient |
- **Evidence**:
  - DOI: 10.1038/s41598-024-66110-0 — Classifies FEP vs. healthy controls using PSD features (delta/theta/alpha/low-beta bands) from 30-second segments of 5-minute resting-state EEG. Achieves 95.51% accuracy with Gaussian Process Classifier using balanced borderline-SMOTE resampling. Directly uses the openneuro_ds003944 dataset.
  - DOI: 10.3390/biomedicines11123223 — Uses ciSSA (complex interval singular spectrum analysis) decomposition with entropy (permutation, spectral), frequency domain, and statistical features extracted from 2-second windows. Achieves AUC=0.9893, accuracy=96.23% with SVM/ANN/ensemble classifiers on the same dataset. Confirms both 30-second and shorter segment approaches are viable.
- **Kernel Notes**: Resting-state EEG contains no discrete task events; use segmentation-based epoching only. Load `participants.tsv` and extract the group/diagnosis column for each subject. Apply subject-level binary label (FEP=1, Control=0) uniformly to all segments from that subject. For a 5-minute recording at 1000 Hz with 30-second segments and 50% overlap: ~9-10 segments per subject. Extract PSD features per segment (delta 0.5-4 Hz, theta 4-8 Hz, alpha 8-12 Hz, low-beta 12-16 Hz) and train binary classifier. Class imbalance between groups should be checked in participants.tsv before model training. Exclude `unknown` admin events entirely—they contain no usable markers.