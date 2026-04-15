# Placebo Neuroepo multisession

**Dataset**: `openneuro_ds003195` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003195
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 20 | **Channels**: 19 | **Sampling Rate**: 200 Hz
**Manual Review**: Pending

## Paradigm

Resting-state EEG recorded from Parkinson's disease patients who received a placebo (not active Neuroepo) during a six-month drug evaluation trial. Recordings were taken before and after the administration period. This is the placebo control arm companion to ds003194 (Neuroepo treatment). Protocol includes resting-state (eyes open/closed), hyperventilation, and recovery periods.

## File Scan Result

> **Kernel SHA256**: `b2040478710b0714b08cde4f0ea0751e94dea4f63870b9db4244efa543c31d62`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Brain State Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `ojos cerrados` | 0 | Eyes-closed resting state |
  | `ojos abiertos` | 1 | Eyes-open resting state |
  | `hiperventilacion 1` | 2 | Hyperventilation period 1 |
  | `hiperventilacion 2` | 3 | Hyperventilation period 2 |
  | `hiperventilacion 3` | 4 | Hyperventilation period 3 |
  | `recuperacion` | 5 | Recovery period after hyperventilation |
  | `hiperventilacion 4` | 6 | Hyperventilation period 4 |
  | `photic stimulation` | 7 | Photic stimulation (English) |
  | `fotoestimulacion` | 7 | Photic stimulation (Spanish, merged with label 7) |
  | `HPVOJOS ABIERTOS` | 8 | Eyes-open during hyperventilation |
  | `hipervantilacion 4` | 6 | Hyperventilation period 4 (typo variant, merged with label 6) |
- **Evidence**:
  - DOI: `10.3389/fnins.2022.841428` — Resting-state EEG analysis from OpenNeuro ds003195 (placebo group) used in qEEG source activity mediation analysis; derives spectral features from sustained brain states
- **Kernel Notes**: Exclude `discontinuity` admin markers. Merge `fotoestimulacion`→label 7 and `hipervantilacion 4`→label 6. Use 2.0 s epochs with 50% overlap for frequency-domain feature extraction matching spectral analysis approach. Clinical PD population may exhibit elevated artifact rates.

### Normal Task 1: Binary Eyes State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `ojos cerrados` | 0 | Eyes-closed resting state |
  | `ojos abiertos` | 1 | Eyes-open resting state |
  | `HPVOJOS ABIERTOS` | 1 | Eyes-open during hyperventilation |
- **Evidence**:
  - DOI: `10.3389/fnins.2022.841428` — Paradigm includes explicit eyes-open/closed conditions; spectral differences between eyes states are well-established in EEG literature
- **Kernel Notes**: Simplified binary task with both eyes-open conditions (`ojos abiertos`, `HPVOJOS ABIERTOS`) mapped to y=1. Same epoch parameters as main task for consistency.

### Normal Task 2: Hyperventilation State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `hiperventilacion 1` | 0 | Hyperventilation period 1 |
  | `hiperventilacion 2` | 1 | Hyperventilation period 2 |
  | `hiperventilacion 3` | 2 | Hyperventilation period 3 |
  | `hiperventilacion 4` | 3 | Hyperventilation period 4 |
  | `hipervantilacion 4` | 3 | Hyperventilation period 4 (typo variant, merged with label 3) |
  | `recuperacion` | 4 | Recovery period |
- **Evidence**:
  - DOI: `10.3389/fnins.2022.841428` — Dataset includes hyperventilation challenge protocol; hyperventilation evokes systematic EEG changes (alkalosis-induced vasoconstriction)
- **Kernel Notes**: Focuses on hyperventilation protocol states including sequential HV periods and recovery. Merge `hipervantilacion 4` typo into label 3. Exclude discontinuity markers.