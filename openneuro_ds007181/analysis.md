# Structural MRI, Resting-State fMRI, and PSG/EEG Dataset of Zoster-Associated Neuralgia

**Dataset**: `openneuro_ds007181` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007181
**Category**: Biological State | **Subjects**: 59 | **Files (Completed)**: 59 | **Channels**: 24 | **Sampling Rate**: 1024 Hz

## Paradigm

Resting-state EEG (part of a PSG recording) was collected from patients with zoster-associated neuralgia and healthy controls, alongside structural MRI and resting-state fMRI. Manual sleep staging is available from PSG annotations. The dataset enables investigation of brain activity and sleep architecture differences between healthy controls and patients with herpes zoster-associated chronic pain.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds007181.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `d631998adfdbb515c3c65966381cfaf5f55b58d5d5b4b9ea34e31c58d9105ffe`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage N2` | 24882 | event | raw | Unresolved from current kernel facts |
| `Sleep stage R (REM)` | 8026 | event | raw | Unresolved from current kernel facts |
| `Sleep stage W` | 7224 | event | raw | Unresolved from current kernel facts |
| `Sleep stage N3` | 6967 | event | raw | Unresolved from current kernel facts |
| `Sleep stage N1` | 6647 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s *, overlap = 0.0, target_events = [`sleep_stage_annotation`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `W` | 0 | Wake stage |
  | `N1` | 1 | Stage 1 sleep |
  | `N2` | 2 | Stage 2 sleep |
  | `N3` | 3 | Stage 3 sleep (slow wave) |
  | `REM` | 4 | Rapid eye movement sleep |
- **Evidence**:
  - DOI: 10.1016/j.artmed.2021.102038 — Multi-modal sleep stage scoring using CNN + Bi-LSTM on PSG data (30s epochs, 5-class W/N1/N2/N3/REM)
  - DOI: 10.1109/TNSRE.2021.3076234 — AttnSleep deep learning model for 30-second sleep epoch classification (W/N1/N2/N3/REM)
- **Kernel Notes**: Verify sleep stage annotation label names from PSG/hypnogram files; align 30-second epoch windows to EEG data. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Resting-state segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.5 *, target_events = N/A
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**: N/A — continuous resting-state EEG without discrete event labels; use subject group labels from participants.tsv (zoster-associated neuralgia vs healthy control)
- **Evidence**:
  - DOI: 10.18112/openneuro.ds007181.v1.0.1 — Dataset includes resting-state PSG/EEG recordings from zoster-associated neuralgia patients and healthy controls
- **Kernel Notes**: Apply sliding window segmentation to continuous EEG; subject group labels must be obtained from participants.tsv and attached as metadata.

### Potential Task 1: Subject group classification (Zoster neuralgia vs healthy control)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30.0 s, overlap = 0.0
- **Label Route**: `misc`
- **Target Definition**: Group labels from participants.tsv: zoster-associated neuralgia (patient) vs healthy control
- **Notes**: Continuous EEG segmentation with subject-level label propagation. No EEG event markers; labels derived from dataset metadata.

## Data Quality Notes

- No event markers present; continuous-only processing.
- PSG-derived sleep stage labels require alignment with EEG data if available.
- 24-channel PSG EEG system; non-standard montage compared to research-grade EEG.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update