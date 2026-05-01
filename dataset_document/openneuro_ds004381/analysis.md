# Intraoperative EEG dataset during medianus-tibialis stimulation with 8 different rates

**Dataset**: `openneuro_ds004381` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004381
**Category**: Sensory/Response | **Subjects**: 18 | **Files (Completed)**: 763 | **Channels**: 4 | **Sampling Rate**: 20000 Hz | **Manual Review**: Pending

## Paradigm

Intraoperative recording of Somatosensory Evoked Potentials (SEP) elicited by medianus and tibial nerve stimulation at eight different repetition rates to optimize signal-to-noise ratio for intraoperative monitoring. Recordings were made during neurosurgery using a minimal-channel invasive EEG setup with very high sampling rate (20 kHz) for subcortical potential resolution. No discrete trial events are present in the raw data; stimulation rate information is encoded in file metadata and must be parsed to segment epochs aligned to stimulus timing.

## File Scan Result

> **Kernel SHA256**: `c6927a6f05fd704c492903a3a626c79c005833345653ec08e757ad043712fd51`
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

### Classical Task 1: SEP SNR Regression by Stimulation Rate
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5` (no raw events detected; stimulation timing derived from metadata encoding)
- **Epoch Parameters**: segment_length = 0.05 s (medianus N20), segment_length = 0.1 s (tibial P40), overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulation_rate_2.7Hz` | continuous | SNR value at 2.7 Hz stimulation |
  | `stimulation_rate_4.7Hz` | continuous | SNR value at 4.7 Hz stimulation |
  | `stimulation_rate_8.7Hz` | continuous | SNR value at 8.7 Hz stimulation |
  | `stimulation_rate_12.7Hz` | continuous | SNR value at 12.7 Hz stimulation |
  | `stimulation_rate_16.7Hz` | continuous | SNR value at 16.7 Hz stimulation |
  | `stimulation_rate_20.7Hz` | continuous | SNR value at 20.7 Hz stimulation |
  | `stimulation_rate_24.7Hz` | continuous | SNR value at 24.7 Hz stimulation |
  | `stimulation_rate_28.7Hz` | continuous | SNR value at 28.7 Hz stimulation |
- **Evidence**:
  - DOI: 10.1016/j.clinph.2023.03.008 — Uses this dataset to optimize SEP stimulation rate by analyzing SNR as a function of stimulation rate (2.7–28.7 Hz), finding optimal rates of 12.7 Hz for medianus and 4.7 Hz for tibial SEP recordings
- **Kernel Notes**: No discrete events exist in raw data (`no_events` only). Super meta parsing required to extract stimulation rate from filenames/metadata. Segmentation aligned to stimulus artifact detection; compute SNR = signal_amplitude / (0.5 * noise_rms) per sweep for regression target. Downsampling from 20 kHz to ~1000 Hz recommended.

### Potential Task 1: Continuous Segmentation for Artifact Rejection
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**: N/A (unsupervised segmentation for artifact detection/quality control before SEP averaging)
- **Notes**: No BIDS trial event markers; stimulation rate (8 levels) encoded in filename/metadata only. Continuous segmentation enables artifact rejection before per-stimulus SEP averaging.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
