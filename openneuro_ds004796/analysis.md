# PEARL-Neuro Database (Alzheimer's Risk Genes, Lifestyle, Neuroimaging)

**Dataset**: `openneuro_ds004796` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds004796
**Category**: High-level Mental | **Subjects**: 79 | **Files (Completed)**: 233
**Channels**: 127 | **Sampling Rate**: 1000 Hz

## Paradigm

A multimodal neuroimaging database of healthy middle-aged adults (50-63 years) carrying Alzheimer's risk genes (APOE, PICALM). The EEG protocol includes resting-state recordings (eyes open and closed) and two active cognitive tasks: the Multi-Source Interference Task (MSIT) and Sternberg's memory task. Stimulus and button-press response events are recorded across task sessions.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 27862 | event | raw | Stimulus onset (MSIT or Sternberg item) |
| `response` | 24051 | event | raw | Participant button-press response |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: APOE4 Genetic Status Classification (MSIT)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.84 s *, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | derived from genetic data | 0 | APOE4- (no APOE4 allele) |
  | derived from genetic data | 1 | APOE4+ (at least one APOE4 allele) |
- **Super Meta Notes**: Derived from participant genetic testing data (APOE genotyping). Kernel step: Load external APOE genotype file and map participant ID to binary APOE4+ (y=1) / APOE4- (y=0) label. Epoch by stimulus events from MSIT task runs.
- **Evidence**:
  - DOI: 10.3389/fnins.2025.1579329 — Binary classification of APOE4 genetic status using theta oscillation propagation features from MSIT cognitive task (stimulus to response: 0.84 +/- 0.16 s)
- **Kernel Notes**: Filter files by task label 'MSIT'. Epoch from stimulus onset to average response time (~0.84 s). Extract theta propagation features (LPG length) from frontal midline electrodes.

### Classical Task 2: APOE4 Genetic Status Classification (Sternberg)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12.36 s *, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | derived from genetic data | 0 | APOE4- (no APOE4 allele) |
  | derived from genetic data | 1 | APOE4+ (at least one APOE4 allele) |
- **Super Meta Notes**: Derived from participant genetic testing data (APOE genotyping). Kernel step: Load external APOE genotype file and map participant ID to binary APOE4+ (y=1) / APOE4- (y=0) label. Epoch by stimulus events from Sternberg task runs.
- **Evidence**:
  - DOI: 10.3389/fnins.2025.1579329 — Binary classification of APOE4 genetic status using theta oscillation propagation features from Sternberg memory task (stimulus onset to last behavioral timing: 12.36 +/- 0.20 s)
- **Kernel Notes**: Filter files by task label 'Sternberg'. Epoch from stimulus onset to last behavioral response (~12.36 s). Extract theta propagation features from frontal midline electrodes.

### Classical Task 3: Resting-State Spectral Power Ratio Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = N/A (continuous segmentation)
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: Continuous clinical scores (external super-meta) for correlation analysis
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | segment | continuous | Clinical score (e.g., attention deficit, hyperactivity) for correlation with spectral features |
- **Evidence**:
  - DOI: 10.1109/icdmw69685.2025.00218 — Uses Hann-windowed 4 second epochs with 50% overlap (Welch's method) to compute delta/beta and theta/beta power ratios from resting-state EEG, correlated with dementia risk clinical scores
- **Kernel Notes**: Filter files by task label 'rest'. Apply 4s sliding window segmentation with 50% overlap. Compute PSD using Welch's method. Extract delta/beta and theta/beta power ratios. Correlation with external clinical scores requires kernel to load separate clinical data file.

### Potential Task 1: Stimulus vs response classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 233 files = 79 subjects x ~3 sessions. Resting-state sessions have no stimulus events; only task sessions contribute stimulus/response epochs.

| Event | y | Meaning |
 |-------|---|------|
 | `stimulus` | 0 | Stimulus onset |
 | `response` | 1 | Button-press response |

## Data Quality Notes

- Mixed resting-state and task sessions; filter by file task label.
- High channel count (127); may include non-EEG channels.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review