# Dataset of EEG Recordings of Pediatric Patients with Epilepsy Based on the 10-20 System

**Dataset**: `openneuro_ds003555` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003555
**Category**: Biological State | **Subjects**: 30 | **Files (Completed)**: 257
**Channels**: 52 | **Sampling Rate**: 2000 Hz

## Paradigm

Continuous sleep EEG recordings from pediatric patients with epilepsy, focused on identifying High-Frequency Oscillations (HFOs) as clinical biomarkers during N3 slow-wave sleep stages. The dataset was recorded using the standard 10-20 electrode system and is intended for automated HFO detection algorithm development and sleep stage analysis. No task-based paradigm was employed; recordings capture spontaneous brain activity during sleep.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous sleep EEG recording |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Potential Task 1: Continuous sleep EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null, no label; for unsupervised or HFO detection)
- **Notes**: High sampling rate (2000 Hz) is appropriate for HFO detection (80-500 Hz). Sleep stage labels (if available from hypnogram) can serve as y labels for sleep classification tasks. No trial-level events present.

## Data Quality Notes

- Very high sampling rate (2000 Hz); high memory requirements for processing.
- Pediatric epilepsy population; inter-individual variability in seizure history and medications.
- HFO detection requires high-frequency filtering (80-500 Hz); standard 0.5-40 Hz bandpass not appropriate for primary analysis goal.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review