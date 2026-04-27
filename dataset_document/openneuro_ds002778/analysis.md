# UC San Diego Resting State EEG Data from Patients with Parkinson's Disease

**Dataset**: `openneuro_ds002778` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds002778
**Category**: Biological State | **Subjects**: N/A | **Files (Completed)**: 46 | **Channels**: 41 | **Sampling Rate**: 512 Hz
**Manual Review**: Pending

## Paradigm

Spontaneous scalp EEG recorded from patients with Parkinson's disease (PD) and healthy controls during resting-state conditions. The study investigated abnormal beta-band synchrony and beta waveform shape features (phase amplitude coupling, non-sinusoidal characteristics) as biomarkers of PD. All events in the BioSemi recording are system status markers (65536 = CM_in_range baseline, 130817 = CM status); no task events exist.

## File Scan Result

> **Kernel SHA256**: `be10479841313314c0e24a0c18cfe514d131441a85541ecc65d0c4d02c84069d`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `event_1` | 43 | event | raw |  |
| `event_131071` | 1 | event | raw |  |
| `event_65536` | 1 | event | raw |  |
| `event_98304` | 1 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Parkinson's Disease vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `PD` | 1 | Parkinson's disease patient |
  | `HC` | 0 | Healthy control subject |
- **Super Meta Notes**: Labels derived from participant metadata (participants.tsv). This dataset contains only BioSemi system status markers (65536, 130817) as raw events—no task-related event markers exist. The kernel must read disease status (PD vs HC) from participants.tsv and apply segment-level labels uniformly to all segments from each subject.
- **Evidence**:
  - DOI: 10.1016/j.compbiomed.2023.107031 — PD vs HC classification using 1-s epochs with CSP features achieving 99.31% accuracy on SanDiego dataset
  - DOI: 10.1038/s41598-022-26644-7 — Binary PD vs HC classification using 10-second epochs with DWT-based entropy features (99.89% accuracy)
  - DOI: 10.3389/fnins.2022.957181 — PD vs HC classification using 1-second segments with PSD and PLV features
  - DOI: 10.3390/diagnostics15060773 — Binary PD vs HC classification using 1-second epochs with PSD features
- **Kernel Notes**: No epochable task events exist in this dataset. All segments from the same subject share identical labels. Segment_length=2.0s with overlap=0.5s is supported by multiple references using similar windowing strategies.

### Classical Task 2: PD Medication State Classification (HC vs PD_OFF vs PD_ON)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3.0 s, overlap = 0.0
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |----|---|---|
  | `HC` | 0 | Healthy control subject |
  | `PD_OFF` | 1 | Parkinson's disease patient off medication |
  | `PD_ON` | 2 | Parkinson's disease patient on medication |
- **Super Meta Notes**: Labels derived from participant metadata (participants.tsv). Kernel must read both disease status and medication status (on/off) to construct three-class labels. All segments from a given subject receive the same three-class label.
- **Evidence**:
  - DOI: 10.1523/ENEURO.0151-19.2019 — Three-group comparison: PD off medication, PD on medication, and healthy controls using beta waveform shape features
  - DOI: 10.1038/s41598-022-26644-7 — Three-class classification off-PD vs on-PD vs HC using DWT-based entropy features
  - DOI: 10.3389/fnins.2022.957181 — Three-class classification: HC=0, PD_OFF=1, PD_ON=2 with multi-scale CNN
- **Kernel Notes**: Optional task; for binary PD vs HC use Classical Task 1. Requires medication_status field in participants.tsv. Segment_length=3.0s with no overlap matches literature parameters for DWT-based entropy classification.
