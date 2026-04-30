# Neuroepo multisession

**Dataset**: `openneuro_ds003194` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003194
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 29 | **Manual Review**: Pending
**Channels**: 19 | **Sampling Rate**: 200 Hz

## Paradigm

Resting-state EEG recorded before and after a six-month Neuroepo drug administration period to evaluate neuroprotective effects in Parkinson's disease patients. The protocol includes resting-state (eyes closed / eyes open), hyperventilation periods, and photic stimulation sections. This is a clinical neurological assessment battery recorded in Spanish (event labels in Spanish).

## File Scan Result

> **Kernel SHA256**: `10d519af7b7b69ec1c59163c3aff14f3e34d3352d92ed7aa40355ef44c1d3549`
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

### Classical Task 1: Mediation Analysis of Neuroepo Effect on Cognitive Performance via qEEG Source Activity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.56 s, overlap = 0.0, target_events = [`ojos cerrados`]
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `ojos cerrados` | continuous | qEEG source spectral power (latent variable via pCCA from 3,244 features) |
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — Uses openneuro_ds003194 EEG data to test whether qEEG source activity mediates the effect of Neuroepo dosage on cognitive performance in PD patients, using pCCA to extract latent variables from 2.56-s resting-state epochs and linear mixed-effects mediation models.
- **Kernel Notes**: 1) Extract 2.56-s epochs (512 samples at 200 Hz) from `ojos cerrados` onset-aligned segments. 2) Apply VARETA inverse solution to compute source activity. 3) Compute PSD in 0.78–19.14 Hz range (49 frequency bins). 4) Perform probabilistic CCA (pCCA) to derive latent variables coupling qEEG spectra with cognitive test scores (MMSE, DRS, FAB, Sequencing, Memory, Recognition). 5) Run mediation analysis with Neuroepo dose (0 vs 5mg) as treatment, pCCA latents as mediator, cognitive scores as outcome.

### Classical Task 2: Multiclass Brain State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`ojos cerrados`, `ojos abiertos`, `recuperacion`, `hiperventilacion 2`, `hiperventilacion 3`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `ojos cerrados` | 0 | Eyes-closed resting state |
  | `ojos abiertos` | 1 | Eyes-open resting state |
  | `recuperacion` | 2 | Recovery period after hyperventilation |
  | `hiperventilacion 2` | 3 | Hyperventilation period 2 |
  | `hiperventilacion 3` | 4 | Hyperventilation period 3 |
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — The paradigm includes sustained clinical brain states (resting-state eyes closed/open, hyperventilation, recovery) that are differentiable via EEG spectral features; the dataset's clinical protocol validates these as distinct biological states for classification.
- **Kernel Notes**: 1) Exclude `discontinuity` events (recording artifact markers) from all analyses. 2) Merge `photic stimulation` and `fotoestimulacion` as equivalent labels if included in classification. 3) Variable hyperventilation event counts across files (HV1: 27, HV2: 28, HV3: 28, HV4: 15) — ensure balanced sampling. 4) Use 50% overlap to increase training samples for the 5-class classifier. 5) Consider spectral features (alpha power, hyperventilation-induced slow waves) as discriminative features.

### Potential Task 1: Eyes-Closed Resting-State Spectral Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 0.5, target_events = [`ojos cerrados`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `ojos cerrados` | continuous | Spectral power in alpha/theta/beta bands |
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — Standard resting-state qEEG analysis approach for PD patients using eyes-closed segments; alpha power reduction is a documented PD biomarker.
- **Kernel Notes**: 1) Use 4.0-s fixed-length segmentation (800 samples at 200 Hz) with 50% overlap. 2) Compute band-limited spectral power for delta (0.5–4 Hz), theta (4–8 Hz), alpha (8–13 Hz), beta (13–30 Hz). 3) Focus on alpha suppression as a potential PD state marker. 4) For source-level analysis, apply VARETA inverse solution as documented in the classical task.

### Potential Task 2: Hyperventilation Response Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.0, target_events = [`hiperventilacion 1`, `hiperventilacion 2`, `hiperventilacion 3`, `hiperventilacion 4`, `recuperacion`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `hiperventilacion 1` | 0 | Hyperventilation period 1 |
  | `hiperventilacion 2` | 1 | Hyperventilation period 2 |
  | `hiperventilacion 3` | 2 | Hyperventilation period 3 |
  | `hiperventilacion 4` | 3 | Hyperventilation period 4 |
  | `recuperacion` | 4 | Recovery period after hyperventilation |
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — Hyperventilation induces EEG changes (slow wave activity) used clinically to assess neurological function; the dataset explicitly includes hyperventilation protocol periods for this purpose.
- **Kernel Notes**: 1) Hyperventilation periods 1–4 may have variable durations across files; extract epochs at onset. 2) Note that HV4 has only 15 files (vs 27–28 for HV1–3) — reduced sample size. 3) Compare spectral changes (theta/delta increase) across hyperventilation phases and recovery. 4) Exclude `discontinuity` events; optionally merge `HPVOJOS ABIERTOS` and `HEPERVENTILACION OJOS ABIERTOS` with standard hyperventilation events if clinically appropriate.

### Potential Task 3: Photic Stimulation Response Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`photic stimulation`, `fotoestimulacion`]
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|---------|
  | `photic stimulation` | 0 | Photic stimulation (English label) |
  | `fotoestimulacion` | 1 | Photic stimulation (Spanish label) |
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — Photic stimulation is part of the standard clinical neurological assessment battery; the dataset includes photic stimulation events to assess cortical responsiveness.
- **Kernel Notes**: 1) `photic stimulation` and `fotoestimulacion` are equivalent labels (Spanish/English) for the same condition — merge for single-class analysis or use as label noise detection task. 2) Photic stimulation events present in 11 files only — limited sample size. 3) Analyze frequency-following response (FFR) in EEG during photic stimulation. 4) Merge with other brain state events for extended classification task.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
