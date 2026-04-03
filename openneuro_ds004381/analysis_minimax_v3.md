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
> **Status**: wait_manual_review
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

### Primary Task 1: SEP SNR Regression by Stimulation Rate
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5` (due to no_events in raw data; metadata-driven segmentation required)
- **Epoch Parameters**: segment_length = 0.05 s (medianus N20 window), segment_length = 0.1 s (tibial P40 window), overlap = 0.0
- **Label Route**: `Annotation`
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
- **Super Meta Notes**: Derived from metadata (filename/subject ID) encoding 8 stimulation rates. No raw event markers present in EEG. Kernel step: Parse stimulation rate from file metadata, segment continuous data at per-stimulus windows (50ms for medianus N20, 100ms for tibial P40), compute SNR = signal_amplitude / (0.5 * noise_rms) for each sweep and average, train regression model predicting SNR from stimulation rate.*
- **Evidence**:
  - DOI: 10.1016/j.clinph.2023.03.008 — Uses openneuro_ds004381 dataset to optimize SEP stimulation rate by analyzing SNR as a function of stimulation rate (2.7-28.7 Hz) and recording duration (5-20 s), finding optimal rates of 12.7 Hz for short medianus SEP and 4.7 Hz for tibial SEP recordings
- **Kernel Notes**: This task replaces the original Primary Task 1 (which lacked proper epoch parameters). No discrete events exist in raw data (`no_events` only), requiring metadata-driven segmentation. Verify stimulation rate mapping from filenames/subject metadata.

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

