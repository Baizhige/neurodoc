# EEG Mortality Dataset in Parkinson's Disease

**Dataset**: `openneuro_ds007020` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds007020
**Category**: Biological State | **Subjects**: 94 | **Files (Completed)**: 94 | **Channels**: 63 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

Resting-state EEG recordings (eyes open) were collected from Parkinson's disease (PD) patients and healthy controls to evaluate EEG-based biomarkers for mortality classification. The dataset enables investigation of spectral and connectivity biomarkers that predict mortality risk in PD. The sole event marker (`New Segment/`) indicates a recording segment boundary and carries no experimental meaning.

## File Scan Result

> **Kernel SHA256**: `2eb51dbfd0bf00ffaeaf96a7ca8df964f7f681752085713eb13bcbac25fdc653`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 3-Year Mortality Classification in Parkinson's Disease
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 120 s (2 minutes), overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `deceased` | 1 | Patient died within 3 years from recording |
  | `living` | 0 | Patient survived at least 3 years after recording |
- **Super Meta Notes**: Mortality labels (deceased/living) are derived from clinical follow-up metadata in participants.tsv (3-year mortality outcome). The `New Segment/` marker is an administrative boundary marker and must not be used as a classification target.
- **Evidence**:
  - DOI: 10.1016/j.prdoa.2025.100409 — Binary classification of 3-year mortality status in PD patients using Linear Predictive Coding EEG features from 2-minute resting-state segments at 500 Hz. Cohort: 94 PD patients (22 deceased, 72 living). Achieves 83% mean out-of-sample accuracy using 5-channel combination (LEAPD algorithm).
- **Kernel Notes**: Extract 2-minute non-overlapping segments from continuous EEG. Load mortality labels (y=1 for deceased within 3 years, y=0 for living) from participants.tsv. Exclude `New Segment/` marker from all analyses. Apply bandpass filter (0.5–40 Hz) and ICA-based artifact rejection before segmentation. For patient-level classification, aggregate segment-level predictions (majority vote or averaging). Expect class imbalance (~24% deceased) — consider class weighting or oversampling in model training.

---

### Potential Task 1: Resting-State Spectral/Connectivity Biomarker Exploration
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 10 s, overlap = 0.5 s
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**: N/A (no trial events; segmentation-based exploration)
- **Super Meta Notes**: Shorter overlapping segments enable exploratory spectral and connectivity analysis (alpha/beta power, coherence) without requiring explicit event markers. Group labels (PD vs healthy control, mortality outcome) must be derived from participants.tsv metadata.
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | Needs verification | Needs verification | No trial events present in Event Structure; segmentation-based exploration task with labels to be derived from participants.tsv metadata (e.g., PD vs healthy control, or mortality outcome) |

- **Evidence**: Not required — paradigm is plausible from resting-state EEG literature for PD spectral biomarker analysis.
- **Kernel Notes**: Extract 10-second overlapping segments (50% overlap) to increase sample count for exploratory analysis. Compute spectral power in canonical bands (delta, theta, alpha, beta, gamma) and connectivity metrics (coherence, phase-locking value). Aggregate metrics per subject for downstream classification or group comparison. Exclude `New Segment/` marker from all analyses.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
