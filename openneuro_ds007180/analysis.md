# Exo-EEG Experiment

**Dataset**: `openneuro_ds007180` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007180
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 25 | **Channels**: 63 | **Sampling Rate**: 500 Hz

## Paradigm

EEG was recorded during interaction with an exoskeleton in a gait or robotic-assisted movement task. Participants performed motor tasks with varying exoskeleton assistance levels and movement conditions. BrainVision trigger codes (S-prefixed) encode specific movement phases, assistance levels, and stimulus conditions across 30 categories.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S21` | 1885 | event | raw | Exo stimulus condition S21 |
| `S22` | 1885 | event | raw | Exo stimulus condition S22 |
| `S12` | 1884 | event | raw | Exo stimulus condition S12 |
| `S11` | 1884 | event | raw | Exo stimulus condition S11 |
| `S32` | 1876 | event | raw | Exo stimulus condition S32 |
| `S31` | 1876 | event | raw | Exo stimulus condition S31 |
| `S41` | 1872 | event | raw | Exo stimulus condition S41 |
| `S42` | 1872 | event | raw | Exo stimulus condition S42 |
| `S62` | 1872 | event | raw | Exo stimulus condition S62 |
| `S61` | 1872 | event | raw | Exo stimulus condition S61 |
| `S52` | 1872 | event | raw | Exo stimulus condition S52 |
| `S51` | 1872 | event | raw | Exo stimulus condition S51 |
| `S72` | 1868 | event | raw | Exo stimulus condition S72 |
| `S71` | 1868 | event | raw | Exo stimulus condition S71 |
| `S81` | 1860 | event | raw | Exo stimulus condition S81 |
| `S82` | 1860 | event | raw | Exo stimulus condition S82 |
| `S13` | 1750 | event | raw | Exo stimulus condition S13 |
| `S43` | 1750 | event | raw | Exo stimulus condition S43 |
| `S73` | 1750 | event | raw | Exo stimulus condition S73 |
| `S63` | 1750 | event | raw | Exo stimulus condition S63 |
| `S53` | 1750 | event | raw | Exo stimulus condition S53 |
| `S33` | 1750 | event | raw | Exo stimulus condition S33 |
| `S23` | 1750 | event | raw | Exo stimulus condition S23 |
| `S83` | 1750 | event | raw | Exo stimulus condition S83 |
| `S102` | 1300 | event | raw | Exo stimulus condition S102 |
| `S101` | 1300 | event | raw | Exo stimulus condition S101 |
| `S92` | 1300 | event | raw | Exo stimulus condition S92 |
| `S91` | 1300 | event | raw | Exo stimulus condition S91 |
| `S111` | 1275 | event | raw | Exo stimulus condition S111 |
| `S122` | 1275 | event | raw | Exo stimulus condition S122 |


### MISC Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S21`, `S22`, `S12`, `S11`, `S32`, `S31`, `S41`, `S42`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Upper Limb Movement Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.4 s, tmax = 0.4 s, target_events = [`S13`, `S23`, `S33`, `S43`, `S53`, `S63`, `S73`, `S83`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S13` | 0 | Upper limb movement: elbow flexion (Fle) |
  | `S23` | 1 | Upper limb movement: elbow extension (Ext) |
  | `S33` | 2 | Upper limb movement: forearm supination (Sup) |
  | `S43` | 3 | Upper limb movement: forearm pronation (Pro) |
  | `S53` | 4 | Upper limb movement: hand close (Clo) |
  | `S63` | 5 | Upper limb movement: hand open (Opn) |
  | `S73` | 6 | Rest condition |
  | `S83` | 7 | Movement imagination variant * |
- **Evidence**:
  - DOI: 10.1371/journal.pone.0182578 — Classifies six upper limb movements and rest from low-frequency EEG during executed and imagined movements with exoskeleton support
- **Kernel Notes**: Filter EEG to 0.3-3 Hz passband. Use epoch window [-0.4, 0.4] s around stimulus onset. Verify S83 mapping to imagination condition from events.tsv.

### Classical Task 2: Exoskeleton Mode Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`S21`, `S22`, `S31`, `S32`, `S41`, `S42`, `S51`, `S52`, `S61`, `S62`, `S71`, `S72`, `S81`, `S82`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S21` | 0 | Exoskeleton mode S21 |
  | `S22` | 1 | Exoskeleton mode S22 |
  | `S31` | 2 | Exoskeleton mode S31 |
  | `S32` | 3 | Exoskeleton mode S32 |
  | `S41` | 4 | Exoskeleton mode S41 |
  | `S42` | 5 | Exoskeleton mode S42 |
  | `S51` | 6 | Exoskeleton mode S51 |
  | `S52` | 7 | Exoskeleton mode S52 |
  | `S61` | 8 | Exoskeleton mode S61 |
  | `S62` | 9 | Exoskeleton mode S62 |
  | `S71` | 10 | Exoskeleton mode S71 |
  | `S72` | 11 | Exoskeleton mode S72 |
  | `S81` | 12 | Exoskeleton mode S81 |
  | `S82` | 13 | Exoskeleton mode S82 |
- **Evidence**:
  - DOI: 10.1109/TNSRE.2023.3294435 — Classifies EEG into swing/stance phases during different exoskeleton walking modes (supports multi-class exo condition classification)
- **Kernel Notes**: Epoch window defaults are inferenced; verify from dataset README. Exclude S255 and 'start' admin markers. Apply bandpass 0.5-40 Hz filter. (replaces Potential Task 1 from original analysis.md)

### Classical Task 3: Gait Phase Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 0.4 s, overlap = 0.9
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `swing_phase` | 0 | Swing phase of gait cycle |
  | `stance_phase` | 1 | Stance phase of gait cycle |
- **Super Meta Notes**: Derived from gait event markers (RTO-RHS, LTO-LHS, RHS-LTO, LHS-RTO) in original data. Kernel step: Compute STFT spectrograms from 0.4s sliding windows (90% overlap), then classify using CNN-LSTM model trained to distinguish swing (positive) vs stance (negative) phase based on spectral features.
- **Evidence**:
  - DOI: 10.1109/TNSRE.2023.3294435 — Uses CNN-LSTM to classify EEG power spectrograms into swing and stance phases, achieving 84.13% average accuracy
- **Kernel Notes**: Requires deriving swing/stance labels from gait event timestamps in the dataset. Filter to appropriate frequency band for spectrogram computation (typically 1-40 Hz for movement-related EEG). Class imbalance: ~70% stance, ~30% swing.

### Classical Task 4: BIDS Task - Exo
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`S91`, `S92`, `S101`, `S102`, `S111`, `S122`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S91` | 0 | Exo task condition S91 |
  | `S92` | 1 | Exo task condition S92 |
  | `S101` | 2 | Exo task condition S101 |
  | `S102` | 3 | Exo task condition S102 |
  | `S111` | 4 | Exo task condition S111 |
  | `S122` | 5 | Exo task condition S122 |
- **Evidence**:
  - DOI: 10.18112/openneuro.ds007180.v1.0.0 — Publisher-defined BIDS task "Exo" with 30 stimulus conditions
- **Kernel Notes**: These S9x-S12x events represent additional experimental conditions; verify condition meanings from dataset README.

## Data Quality Notes

- BrainVision format; 30 S-coded stimulus conditions require README decoding.
- `S255` (saturation marker) and `start` events in some files; exclude from analysis.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review