# Validation of Sleep Staging with Forehead EEG Patch

**Dataset**: `openneuro_ds006695` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006695
**Category**: Biological State | **Subjects**: 19 | **Files (Completed)**: 19 | **Channels**: 3 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

This dataset validates a spectral sleep staging approach using a three-electrode forehead EEG patch against manual scoring from standard polysomnography (PSG). Overnight sleep recordings were collected from 19 subjects using a minimally intrusive forehead device placed over the frontal region, and sleep stages (Wake, N1, N2, N3, REM) were scored both manually by experts and algorithmically. The study examines whether simplified forehead EEG can reliably reproduce standard PSG hypnogram classifications across 30-second epochs.

## File Scan Result

> **Kernel SHA256**: `79475293afd909f4cc5ddcf8972754aa504848804472eddb7d0906ec875e0206`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | 19 | event | raw | No discrete event markers detected; continuous overnight EEG recordings require external PSG hypnogram labels for sleep staging. |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Sleep Stage Classification from Forehead EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`Wake`, `N1`, `N2`, `N3`, `REM`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `Wake` | 0 | Awake state (eyes open/closed, >=50% alpha or movement) |
  | `N1` | 1 | NREM stage 1 (light sleep, theta, slow eye movements) |
  | `N2` | 2 | NREM stage 2 (sleep spindles, K-complexes) |
  | `N3` | 3 | NREM stage 3 / Deep sleep (slow wave delta dominance) |
  | `REM` | 4 | Rapid Eye Movement (paradoxical sleep, desynchronized EEG) |
- **Super Meta Notes**: Sleep stage labels are derived from external PSG hypnogram scoring files (manual visual scoring per AASM guidelines). The EEG recordings contain no discrete event markers (`no_events`). Labels must be aligned by timestamp between the 3-channel forehead EEG patch and full PSG hypnogram files. Kernel step: Load PSG hypnogram CSV/TSV file, extract 30-sec epoch labels, align to EEGUnity epochs via timestamp matching.
- **Evidence**:
  - DOI: `10.3389/frsle.2024.1349537` — Onton et al. validation of spectral sleep scoring from 3-channel forehead EEG patch against manual PSG visual scoring using 30-sec epoch classification into 5 stages (Wake/N1/N2/N3/REM). Direct match to this dataset.
- **Kernel Notes**:
  1. Locate and load external PSG hypnogram scoring file (CSV/TSV) for each subject
  2. Parse 30-second epoch timestamps with corresponding sleep stage labels (Wake/N1/N2/N3/REM)
  3. Align hypnogram timestamps to forehead EEG recording onset via matching or offset calculation
  4. For each 30-sec EEG epoch (0–30s, 30–60s, etc.), assign the corresponding sleep stage label
  5. Map stages to integers: Wake→0, N1→1, N2→2, N3→3, REM→4
  6. Anticipate class imbalance (N3 and REM are typically underrepresented vs N2) — consider stratified sampling or class weighting
  7. Validate signal quality across all 3 forehead channels before classification
  8. Confirm manual PSG scoring used AASM 2007 rules (not older Rechtschaffen-Kales standard)

### Potential Task 1: Sleep Microarchitecture Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `event`
- **Target Definition**: N/A (labels derived from external scoring files for spindle/K-complex detection)
- **Super Meta Notes**: No EEG event markers available. Alternative segmentation approach for detecting transient sleep microevents (spindles, K-complexes, arousals) within continuous overnight recordings. Sliding 2-second windows with 50% overlap enable fine-grained detection of microarchitectural features.
- **Evidence**:
  - DOI: `10.1109/ISOIRS65690.2025.11168096` — Related work on interpretable sleep staging using forehead EEG patch with SHAP-guided clustering; supports microarchitecture detection methodology
  - Paradigm support: Plausible from sleep staging paradigm — transient features (spindles, arousals) require shorter windows than standard 30-sec epochs
- **Kernel Notes**:
  1. Use sliding 2-sec windows (50% overlap) to capture transient EEG features
  2. Extract spectral power features (sigma band 11–16 Hz for spindles; delta band for K-complexes)
  3. Limited to 3 forehead channels — frontal-specific features accessible but cortical topography resolution reduced
  4. Ground-truth labels for microevents may require manual annotation of spindle/K-complex occurrences

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
