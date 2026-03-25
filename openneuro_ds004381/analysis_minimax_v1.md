# Intraoperative EEG dataset during medianus-tibialis stimulation with 8 different rates

**Dataset**: `openneuro_ds004381` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004381
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 770
**Channels**: 4 | **Sampling Rate**: 20000 Hz

## Paradigm

Intraoperative recording of Somatosensory Evoked Potentials (SEP) elicited by medianus and tibial nerve stimulation at eight different repetition rates to optimize signal-to-noise ratio for intraoperative monitoring. Recordings were made during neurosurgery using a minimal-channel invasive EEG setup with very high sampling rate for subcortical potential resolution.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004381

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous SEP recordings without trial-level BIDS annotations._

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: SEP Stimulation Rate Optimization (SNR Regression)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.05 s (medianus), tmax = 0.1 s (tibial), target_events = ['N20', 'P40', 'stimulation_rate_*']
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | continuous | float | SNR (signal amplitude / 0.5 × noise RMS) |
- **Super Meta Notes**: SNR computed from artifact-rejected sweeps (± averaging for noise estimation). Stimulus artifact detection via 200 Hz high-pass filter and local peak detection; amplitude threshold >10 µV for artifact rejection.
- **Evidence**:
  - DOI: 10.1016/j.clinph.2023.03.008 — Uses this dataset to optimize SEP stimulation rate by analyzing SNR across 8 rates (2.7–28.7 Hz) with sweep lengths of 50 ms (medianus) and 100 ms (tibial), resampled to 1200 Hz
- **Kernel Notes**: Filter raw data at 200 Hz high-pass to detect stimulus artifacts; epoch around N20/P40 peaks; reject sweeps with amplitude >10 µV; compute SNR as amplitude/(0.5×noise_rms); fit amplitude decay model Amplitude = a × Rate^k

### Primary Task 2: SEP Rate Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.05 s (medianus), tmax = 0.1 s (tibial), target_events = ['N20', 'P40']
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulation_rate_2.7Hz` | 0 | 2.7 Hz stimulation rate |
  | `stimulation_rate_4.7Hz` | 1 | 4.7 Hz stimulation rate |
  | `stimulation_rate_8.7Hz` | 2 | 8.7 Hz stimulation rate |
  | `stimulation_rate_12.7Hz` | 3 | 12.7 Hz stimulation rate |
  | `stimulation_rate_16.7Hz` | 4 | 16.7 Hz stimulation rate |
  | `stimulation_rate_20.7Hz` | 5 | 20.7 Hz stimulation rate |
  | `stimulation_rate_24.7Hz` | 6 | 24.7 Hz stimulation rate |
  | `stimulation_rate_28.7Hz` | 7 | 28.7 Hz stimulation rate |
- **Evidence**:
  - DOI: 10.1016/j.clinph.2023.03.008 — Dataset contains 8 different stimulation rates (2.7–28.7 Hz) for medianus and tibial nerves
- **Kernel Notes**: Extract stimulation rate from file metadata or event headers; epoch around SEP peaks; classify rate from epoched segments

### Normal Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (unsupervised segmentation)
- **Notes**: No BIDS trial event markers; stimulation rate (8 levels) encoded in filename/metadata. SEP analysis requires specialized averaging pipeline rather than standard epoch classification.

## Data Quality Notes

- Very high sampling rate (20 kHz) for subcortical SEP; downsampling required for standard EEG analysis
- Only 4 channels (intraoperative minimal setup)
- 770 files across 18 subjects (many runs per subject, 8 stimulation rates)

## References

- **Reference**: `Optimization of signal-to-noise ratio in short-duration SEP recordings by variation of stimulation rate`
