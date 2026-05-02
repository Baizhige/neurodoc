# Resting State EEG with Closed Eyes and Open Eyes in Females from 60 to 80 Years Old

**Dataset**: `openneuro_ds005420` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005420
**Category**: Biological State | **Subjects**: 72 | **Files (Completed)**: 72 | **Manual Review**: Pending
**Channels**: 20 | **Sampling Rate**: 500 Hz

## Paradigm

Spontaneous resting-state EEG was recorded in a cohort of females aged 60-80 years during alternating eyes-open and eyes-closed conditions. The dataset investigates age-related changes in spontaneous brain activity in older women. No event markers were included in events.tsv; the EEG is stored as continuous recordings. Eyes-open vs. eyes-closed condition can be inferred from the file naming or participants.tsv.

## File Scan Result

> **Kernel SHA256**: `a1eca7fb36e57f045f47e25392f88bf796e7e2fea8d1a589482b95dcaa337c32`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Eyes-Open vs Eyes-Closed Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 1.0 s
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes-open (EO)` | 0 | Eyes open resting state |
  | `eyes-closed (EC)` | 1 | Eyes closed resting state |
- **Kernel Notes**: No discrete event markers exist in events.tsv. Condition labels (EO/EC) must be inferred from BIDS task identifiers in filenames (e.g., 'task-Oa' = eyes-open, 'task-Oc' = eyes-closed) or participants.tsv metadata. Apply bandpass filter (0.5–40 Hz) and artifact rejection (amplitude threshold ±100 μV) prior to segmentation. Assign binary labels per segment based on source recording's condition metadata. Use subject-wise train/test splits to avoid data leakage. The dataset contains only females aged 60–80 years; confirm that model generalizability to other demographics is beyond scope.
- **Evidence**:
  - DOI: 10.1109/UBMK67458.2025.11207051 — Validated on OpenNeuro ds005420 for cross-dataset validation using VGG-19 and custom 6-layer CNN. Converted EEG to composite CWT images for binary classification. Segmented raw files into 10-s epochs with 1.0-s overlap to generate sufficient samples. Dataset-specific parameters confirmed: 20-channel EEG, 500 Hz sampling rate, 72 subjects (females, age 60–80).

### Potential Task 1: Resting-State Segmentation for Frequency-Domain Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5 s
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes-open (EO)` | 0 | Eyes open resting state |
  | `eyes-closed (EC)` | 1 | Eyes closed resting state |
- **Kernel Notes**: Shorter 4-s segments with 0.5-s overlap suitable for alpha/beta power comparisons between eyes-open and eyes-closed states. Condition labels derived from BIDS task identifiers (Oa/Oc) as described for Classical Task 1. Apply bandpass filter (0.5–40 Hz), notch filter (50/60 Hz), and artifact rejection before segmentation. This alternative segmentation scheme is plausible for frequency-domain analyses but lacks direct validation on this dataset.
- **Evidence**:
  - DOI: 10.1109/UBMK67458.2025.11207051 — Reference confirms 10-s segmentation approach; 4-s alternative is plausible for frequency-domain analyses but not directly validated.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
