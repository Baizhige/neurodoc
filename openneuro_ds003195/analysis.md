# Placebo Neuroepo multisession

**Dataset**: `openneuro_ds003195` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003195
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 20
**Channels**: 19 | **Sampling Rate**: 200 Hz

## Paradigm

Resting-state EEG recorded from Parkinson's disease patients who received a placebo (not active Neuroepo) during a six-month drug evaluation trial. Recordings were taken before and after the administration period. This is the placebo control arm companion to ds003194 (Neuroepo treatment). Protocol includes resting-state (eyes open/closed), hyperventilation, and recovery periods.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ojos cerrados` | 20 (files) | event | raw | Eyes-closed resting state |
| `ojos abiertos` | 19 (files) | event | raw | Eyes-open resting state |
| `hiperventilacion 1` | 19 (files) | event | raw | Hyperventilation period 1 |
| `hiperventilacion 2` | 19 (files) | event | raw | Hyperventilation period 2 |
| `hiperventilacion 3` | 19 (files) | event | raw | Hyperventilation period 3 |
| `recuperacion` | 19 (files) | event | raw | Recovery period after hyperventilation |
| `hiperventilacion 4` | 12 (files) | event | raw | Hyperventilation period 4 |
| `discontinuity` | 8 (files) | admin | raw | Recording discontinuity marker - exclude |
| `photic stimulation` | 3 (files) | event | raw | Photic stimulation block |
| `fotoestimulacion` | 3 (files) | event | raw | Photic stimulation (Spanish label) |
| `HPVOJOS ABIERTOS` | 2 (files) | event | raw | Eyes-open during hyperventilation |
| `hipervantilacion 4` | 1 (file) | event | raw | Hyperventilation period 4 (variant spelling) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `photic stimulation`, `fotoestimulacion`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Brain State Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`ojos cerrados`, `ojos abiertos`, `hiperventilacion 1`, `hiperventilacion 2`, `hiperventilacion 3`, `recuperacion`, `hiperventilacion 4`, `photic stimulation`, `fotoestimulacion`, `HPVOJOS ABIERTOS`, `hipervantilacion 4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ojos cerrados` | 0 | Eyes-closed resting state |
  | `ojos abiertos` | 1 | Eyes-open resting state |
  | `hiperventilacion 1` | 2 | Hyperventilation period 1 |
  | `hiperventilacion 2` | 3 | Hyperventilation period 2 |
  | `hiperventilacion 3` | 4 | Hyperventilation period 3 |
  | `recuperacion` | 5 | Recovery period |
  | `hiperventilacion 4` | 6 | Hyperventilation period 4 |
  | `photic stimulation` | 7 | Photic stimulation (English) |
  | `fotoestimulacion` | 8 | Photic stimulation (Spanish) |
  | `HPVOJOS ABIERTOS` | 9 | Eyes-open during hyperventilation |
  | `hipervantilacion 4` | 10 | Hyperventilation period 4 (variant spelling) |
- **Evidence**:
  - DOI: `10.3389/fnins.2022.841428` — Uses EEG data from OpenNeuro ds003195 (placebo group) to analyze qEEG source activity as mediator between Neuroepo dose and cognitive performance; derives latent qEEG variables from resting-state spectra
- **Kernel Notes**: Exclude `discontinuity` events (admin marker). Merge `fotoestimulacion` with `photic stimulation` (label 7) and `hipervantilacion 4` with `hiperventilacion 4` (label 6) for cleaner classification. Use 2.0 s epochs with 50% overlap to match paper's 2.56 s epoch approach. (replaces Potential Task 1 from original analysis.md)

### Potential Task 1: Binary Eyes State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`ojos cerrados`, `ojos abiertos`, `HPVOJOS ABIERTOS`]
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ojos cerrados` | 0 | Eyes-closed resting state |
  | `ojos abiertos` | 1 | Eyes-open resting state |
  | `HPVOJOS ABIERTOS` | 1 | Eyes-open during hyperventilation |
- **Notes**: Simplified binary classification of eyes-open vs eyes-closed states. Both eyes-open conditions map to y=1.

## Data Quality Notes

- Clinical recording from Parkinson's patients; expect higher artifact rate.
- `photic stimulation` and `fotoestimulacion` are equivalent labels - merge if needed.
- `hipervantilacion 4` is a spelling variant of `hiperventilacion 4` - treat as same condition.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review