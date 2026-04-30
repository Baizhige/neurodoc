# Structural MRI, Resting-State fMRI, and PSG/EEG Dataset of Zoster-Associated Neuralgia

**Dataset**: `openneuro_ds007181` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007181
**Category**: Biological State | **Subjects**: 59 | **Files (Completed)**: 59 | **Channels**: 24 | **Sampling Rate**: 1024 Hz | **Manual Review**: Pending

## Paradigm

Resting-state EEG (part of a full PSG recording) was collected from patients diagnosed with zoster-associated neuralgia and age/sex-matched healthy controls, alongside structural MRI and resting-state fMRI scans. Manual sleep staging was performed by experts using standard AASM criteria and is available as PSG annotations. The dataset enables investigation of brain activity and sleep architecture differences between healthy controls and patients with herpes zoster-associated chronic pain.

## File Scan Result

> **Kernel SHA256**: `c7a2badbf13ef768ecc7a1d58172c4ff9ffe004cfd6e934638a1c26aa11ba6dc`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Sleep stage N1` | 6647 | event | raw | Stage 1 sleep (light sleep, theta dominance) |
| `Sleep stage N2` | 24882 | event | raw | Stage 2 sleep (sleep spindles and K-complexes) |
| `Sleep stage N3` | 6967 | event | raw | Stage 3 sleep (slow wave sleep, delta dominance) |
| `Sleep stage R (REM)` | 8026 | event | raw | Rapid eye movement sleep |
| `Sleep stage W` | 7224 | event | raw | Wakefulness |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep Stage Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `Sleep stage W` | 0 | Wake |
  | `Sleep stage N1` | 1 | Stage 1 sleep |
  | `Sleep stage N2` | 2 | Stage 2 sleep |
  | `Sleep stage N3` | 3 | Stage 3 sleep (slow wave) |
  | `Sleep stage R (REM)` | 4 | Rapid eye movement sleep |
- **Evidence**:
  - DOI: 10.1016/j.artmed.2021.102038 — Multi-modal Spatial-Temporal CNN+Bi-LSTM for 30-second PSG epoch sleep scoring, 5-class AASM labels (W/N1/N2/N3/REM)
  - DOI: 10.1109/TNSRE.2021.3076234 — AttnSleep deep learning model for 30-second sleep epoch classification (W/N1/N2/N3/REM)
- **Kernel Notes**: Sleep stage annotations mark sustained 30-second PSG epochs aligned to onset. Class imbalance expected: N2 (24882) heavily dominates vs rare N3 (6967) and N1 (6647). Verify exact annotation strings from raw hypnogram files — kernel shows `Sleep stage R (REM)` but standard AASM notation uses `Sleep stage R`. Consider weighted loss or stratified sampling to handle the 3.6:1 ratio between N2 and N3.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
