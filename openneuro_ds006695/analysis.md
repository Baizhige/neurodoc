# Validation of Sleep Staging with Forehead EEG Patch

**Dataset**: `openneuro_ds006695` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006695
**Category**: Biological State | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 3 | **Sampling Rate**: 500 Hz

## Paradigm

This dataset validates a spectral sleep staging approach using a three-electrode forehead EEG patch against manual scoring from standard polysomnography (PSG). Overnight sleep recordings were collected using a minimally intrusive forehead device, and sleep stages (Wake, N1, N2, N3, REM) were scored both manually and algorithmically. The study examines whether simplified forehead EEG can reliably reproduce standard PSG hypnogram classifications.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous overnight EEG recordings without trial-level annotations._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Sleep stage classification from PSG hypnogram
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Wake`, `N1`, `N2`, `N3`, `REM`] *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Wake` | 0 | Awake state (eyes open/closed, >=50% alpha or movement) |
  | `N1` | 1 | NREM stage 1 (light sleep, theta, slow eye movements) |
  | `N2` | 2 | NREM stage 2 (sleep spindles, K-complexes) |
  | `N3` | 3 | NREM stage 3 / Deep sleep (slow wave delta dominance) |
  | `REM` | 4 | Rapid Eye Movement (paradoxical sleep, desynchronized EEG) |
- **Super Meta Notes**: Sleep stage labels derived from external PSG hypnogram scoring files (manual visual scoring by technicians per AASM rules). The dataset contains only continuous EEG recordings with `no_events` marker. Labels must be aligned by timestamp between the 3-channel forehead EEG patch and full 32-channel PSG cap recordings. Kernel step: Load PSG hypnogram file (CSV/TSV), extract 30-sec epoch labels, align to EEGUnity epochs via timestamp matching.
- **Evidence**:
  - DOI: `10.3389/frsle.2024.1349537` — Validates spectral sleep scoring from 3-channel forehead EEG patch against manual visual PSG scoring using 30-sec epoch classification into 5 stages (Wake/N1/N2/N3/REM)
- **Kernel Notes**: 
    1. Locate and load PSG hypnogram scoring file (external to EEG raw files)
    2. Parse sleep stage labels with timestamp annotations
    3. For each 30-sec EEG epoch (0-30s, 30-60s, etc.), assign corresponding sleep stage label
    4. Map visual stages: Wake→0, N1→1, N2→2, N3→3, REM→4
    5. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `event`
- **Target Definition**: N/A (no event markers; sleep stage labels from external PSG scoring)
- **Notes**: No EEG event markers available. Sleep stage labels (Wake/N1/N2/N3/REM) must be derived from PSG hypnogram annotations stored as separate scoring files. Very few channels (3); limited spatial resolution for advanced decoding.

## Data Quality Notes

- Only 3 channels (forehead placement); very limited spatial information.
- Overnight recordings are long (hours); memory-efficient processing needed.
- Sleep stage labels require alignment with PSG hypnogram files.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review