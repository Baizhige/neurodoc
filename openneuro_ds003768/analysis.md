# Simultaneous EEG and fMRI Signals During Sleep from Humans

**Dataset**: `openneuro_ds003768` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds003768
**Category**: Biological State | **Subjects**: 33 | **Files (Completed)**: 252
**Channels**: 32 | **Sampling Rate**: 5000 Hz

## Paradigm

Simultaneous EEG-fMRI recordings were acquired during resting-state wakefulness and multiple sleep sessions (NREM, REM) to analyze spontaneous brain activity and sleep stage dynamics. Participants underwent extended sleep sessions in an MRI scanner while 32-channel EEG was recorded concurrently with fMRI. BrainVision numeric stimulus codes (S1, S2, S3) and response codes (R128) mark sleep stage transitions or scoring events. The dataset supports multimodal sleep neuroscience research.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 1` | 183 | event | raw | BrainVision S1 trigger (sleep stage marker) |
| `Stimulus/S 2` | 193 | event | raw | BrainVision S2 trigger (sleep stage marker) |
| `Stimulus/S 3` | 183 | event | raw | BrainVision S3 trigger (sleep stage marker) |
| `Response/R128` | 252 | admin | raw | BrainVision R128 response trigger |

**Route**: `stim`
**Role**: Trigger-channel or stimulus-marker based labeling.
**Candidate Trigger Labels**: `Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`
**Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep stage classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`] *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---\u2500------|
  | S1 trigger | 0 | Wake (W) |
  | S1 trigger | 1 | NREM1 (N1) |
  | S2 trigger | 2 | NREM2 (N2) |
  | S3 trigger | 3 | NREM3 (N3) |
- **Super Meta Notes**: Derived from raw events [`Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`] by mapping button-press triggers to sleep stage labels. Sleep stages are manually annotated by a Registered Polysomnographic Technologist (RPT) based on AASM guidelines in sourcedata folder (w=wake, 1=NREM1, 2=NREM2, 3=NREM3). Kernel step: Extract 30-sec EEG epochs aligned to S1/S2/S3 triggers, then map each epoch to corresponding sleep stage label from sourcedata annotations.
- **Evidence**:
  - DOI: 10.1016/j.dib.2023.109059 — Data in Brief paper describing simultaneous EEG-fMRI sleep dataset with manually annotated sleep stage labels (W, N1, N2, N3) scored by RPT on 30-sec epochs
  - DOI: 10.1016/j.neuroimage.2025.121384 — Uses same dataset for arousal state classification with 20-second epochs
- **Kernel Notes**: Use 30-sec long-event epoching aligned with AASM standard sleep scoring. Downsample from 5000 Hz to 250 Hz. Apply MRI artifact removal for EEG-fMRI data. Verify event-to-sleep-stage mapping from sourcedata events.tsv. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Arousal state binary classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 20 s, overlap = 0.5, target_events = [`Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`] *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---\u2500------|
  | S1/S2/S3 triggers | 0 | Awake (W) |
  | S1/S2/S3 triggers | 1 | Sleep (NREM2) or Anesthesia |
- **Super Meta Notes**: Derived from raw events [`Stimulus/S 1`, `Stimulus/S 2`, `Stimulus/S 3`]. Sleep stage labels scored by RPT from EEG enable binary wake vs sleep classification. Kernel step: Extract 20-sec epochs aligned to S1/S2/S3, then binarize labels (W=awake, N1/N2/N3=sleep).
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2025.121384 — Uses openneuro_ds003768 for binary classification of awake vs sleep/arousal states with 20-second epochs
- **Kernel Notes**: Use 20-sec epochs with 50% overlap (standard for this paper). Downsample to 250 Hz. Apply MRI artifact removal. Verify sleep/wake labeling from sourcedata.

### Potential Task 1: Sleep stage classification (multiclass, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: S1/S2/S3 likely encode sleep stage transitions (Wake, NREM1/2/3, REM); exact mapping must be confirmed from events.tsv or dataset documentation. Sleep stages are sustained states (>=2 s); use long-event epoching. Very high sampling rate (5000 Hz); downsample to 250 Hz for standard sleep scoring.

| Event | y | Meaning |
|-------\u2500--|------|
| `Stimulus/S 1` | 0 | Sleep stage 1 (need to confirm the specific sleep stage from events.tsv) |
| `Stimulus/S 2` | 1 | Sleep Stage 2 |
| `Stimulus/S 3` | 2 | Sleep Stage 3 |

## Data Quality Notes

- Very high sampling rate (5000 Hz); downsample to 250-500 Hz before analysis.
- EEG-fMRI simultaneous recording; gradient artifacts present; requires MRI artifact removal.
- R128 is a BrainVision response/sync marker; treat as admin.
- 252 files from 33 subjects across multiple sleep sessions.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review