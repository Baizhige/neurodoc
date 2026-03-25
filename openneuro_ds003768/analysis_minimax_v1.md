# Simultaneous EEG and fMRI Signals During Sleep from Humans

**Dataset**: `openneuro_ds003768` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds003768
**Category**: Biological State | **Subjects**: 33 | **Files (Completed)**: 252
**Channels**: 32 | **Sampling Rate**: 5000 Hz

## Paradigm

Simultaneous EEG-fMRI recordings were acquired during resting-state wakefulness and multiple sleep sessions (NREM, REM) to analyze spontaneous brain activity and sleep stage dynamics. Participants underwent extended sleep sessions in an MRI scanner while 32-channel EEG was recorded concurrently with fMRI. BrainVision numeric stimulus codes (S1, S2, S3) and response codes (R128) mark sleep stage transitions or scoring events. The dataset supports multimodal sleep neuroscience research.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003768

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 1` | 183 | long | raw | BrainVision S1 trigger (sleep stage marker) |
| `Stimulus/S 2` | 193 | long | raw | BrainVision S2 trigger (sleep stage marker) |
| `Stimulus/S 3` | 183 | long | raw | BrainVision S3 trigger (sleep stage marker) |
| `Response/R128` | 252 | admin | raw | BrainVision R128 response trigger |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep stage classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 30 s, overlap = 0.0 *, target_events = N/A (segmentation)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | w/W | 0 | Wake |
  | 1/NREM1 | 1 | NREM Stage 1 |
  | 2/NREM2 | 2 | NREM Stage 2 |
  | 3/NREM3 | 3 | NREM Stage 3 |
- **Super Meta Notes**: Sleep stages are manually annotated by a Registered Polysomnographic Technologist (RPT) based on AASM guidelines. Each 30-sec EEG epoch was scored as W (wake), NREM1, NREM2, NREM3, or REM. The scoring is provided in sourcedata folder with 'w' denoting wakefulness and '1,2,3' denoting NREM1, NREM2, NREM3 respectively. S1/S2/S3 triggers are raw button-press markers, but sleep stage labels are superordinate derived from EEG analysis.
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.109059 — This Data in Brief paper describes the openneuro_ds003768 dataset of simultaneous EEG-fMRI recordings during rest and sleep, providing manually annotated sleep stage labels (W, N1, N2, N3, REM) scored by a Registered Polysomnographic Technologist on 30-sec epochs, enabling automated sleep stage classification research.
- **Kernel Notes**: Read sleep stage annotations from sourcedata folder; map to 30-sec epochs aligned with raw recording; exclude uncertain/unscorable epochs.

### Primary Task 2: Binary arousal state classification (awake vs sleep)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 20 s *, overlap = 10 s * (50% overlap), target_events = N/A (segmentation)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | awake | 0 | Awake state |
  | sleep | 1 | Sleep state (any NREM/REM stage) |
- **Super Meta Notes**: Binary classification of 20-sec EEG epochs into awake vs non-awake states. Sleep stages scored by Registered Polysomnographic Technologist from EEG; each 30-second epoch originally classified into wake/REM/NREM1/NREM2/NREM3, then collapsed to binary awake/sleep.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2025.121384 — The sleep dataset used in this study was obtained from a publicly available dataset (Gu et al., 2023) accessible at https://openneuro.org/datasets/ds003768/versions/1.0.10
- **Kernel Notes**: Collapse multiclass sleep stage labels to binary; use 20-sec windows with 50% overlap; downsample to 250 Hz.

### Normal Task 1: Sleep stage classification (multiclass, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: S1/S2/S3 likely encode sleep stage transitions (Wake, NREM1/2/3, REM); exact mapping must be confirmed from events.tsv or dataset documentation. Sleep stages are sustained states (>=2 s); use long-event epoching. Very high sampling rate (5000 Hz); downsample to 250 Hz for standard sleep scoring.

| Event | y | Meaning |
|-------|---|------|
| `Stimulus/S 1` | 0 | Sleep stage 1 (need to confirm the specific sleep stage from events.tsv) |
| `Stimulus/S 2` | 1 | Sleep Stage 2 |
| `Stimulus/S 3` | 2 | Sleep Stage 3 |

## Data Quality Notes

- Very high sampling rate (5000 Hz); downsample to 250-500 Hz before analysis.
- EEG-fMRI simultaneous recording; gradient artifacts present; requires MRI artifact removal.
- R128 is a BrainVision response/sync marker; treat as admin.
- 252 files from 33 subjects across multiple sleep sessions.

## References

- **Reference**: `Albouy et al., Journal of Sleep Research, 2013. Simultaneous EEG and fMRI during sleep. OpenNeuro ds003768.`
