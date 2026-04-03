# Structural MRI, Resting-State fMRI, and PSG/EEG Dataset of Zoster-Associated Neuralgia

**Dataset**: `openneuro_ds007181` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007181
**Category**: Biological State | **Subjects**: 59 | **Files (Completed)**: 59 | **Channels**: 24 | **Sampling Rate**: 1024 Hz

## Paradigm

Resting-state EEG (part of a PSG recording) was collected from patients with zoster-associated neuralgia and healthy controls, alongside structural MRI and resting-state fMRI. Manual sleep staging is available from PSG annotations. The dataset enables investigation of brain activity and sleep architecture differences between healthy controls and patients with herpes zoster-associated chronic pain.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Status**: wait_kernel_update
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007181

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous PSG/EEG recordings without trial-level annotations._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s *, overlap = 0.0, target_events = [`sleep_stage_annotation`]
- **Label Route**: `Annotation`
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
- **Kernel Notes**: Verify sleep stage annotation label names from PSG/hypnogram files; align 30-second epoch windows to EEG data. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Resting-state segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.5 *, target_events = N/A
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**: N/A — continuous resting-state EEG without discrete event labels; use subject group labels from participants.tsv (zoster-associated neuralgia vs healthy control)
- **Evidence**:
  - DOI: 10.18112/openneuro.ds007181.v1.0.1 — Dataset includes resting-state PSG/EEG recordings from zoster-associated neuralgia patients and healthy controls
- **Kernel Notes**: Apply sliding window segmentation to continuous EEG; subject group labels must be obtained from participants.tsv and attached as metadata.

### Normal Task 1: Subject group classification (Zoster neuralgia vs healthy control)
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

