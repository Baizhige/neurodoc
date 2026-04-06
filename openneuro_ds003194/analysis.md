# Neuroepo multisession

**Dataset**: `openneuro_ds003194` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003194
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 29
**Channels**: 19 | **Sampling Rate**: 200 Hz

## Paradigm

Resting-state EEG recorded before and after a six-month Neuroepo drug administration period to evaluate neuroprotective effects in Parkinson's disease patients. The protocol includes resting-state (eyes closed / eyes open), hyperventilation periods, and photic stimulation sections. This is a clinical neurological assessment battery recorded in Spanish (event labels in Spanish).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ojos cerrados` | 29 (files) | event | raw | Eyes-closed resting state |
| `ojos abiertos` | 28 (files) | event | raw | Eyes-open resting state |
| `recuperacion` | 28 (files) | event | raw | Recovery period after hyperventilation |
| `hiperventilacion 1` | 27 (files) | event | raw | Hyperventilation period 1 |
| `hiperventilacion 2` | 28 (files) | event | raw | Hyperventilation period 2 |
| `hiperventilacion 3` | 28 (files) | event | raw | Hyperventilation period 3 |
| `hiperventilacion 4` | 15 (files) | event | raw | Hyperventilation period 4 |
| `photic stimulation` | 11 (files) | event | raw | Photic stimulation block |
| `fotoestimulacion` | 11 (files) | event | raw | Photic stimulation (Spanish label) |
| `discontinuity` | 9 (files) | admin | raw | Recording discontinuity marker - exclude |
| `HPVOJOS ABIERTOS` | 6 (files) | event | raw | Eyes-open during hyperventilation |
| `HEPERVENTILACION OJOS ABIERTOS` | 1 (file) | event | raw | Hyperventilation eyes-open variant |


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

### Classical Task 1: Mediation Analysis of Neuroepo Effect on Cognitive Performance via qEEG Source Activity
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.56 s, overlap = 0.0, target_events = [`ojos cerrados`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `ojos cerrados` | continuous | qEEG source spectral power (latent variable via pCCA from 3,244 features) |
- **Super Meta Notes**: Derived from raw event `ojoscerrados` by extracting 2.56-s artifact-free epochs (512 samples at 200 Hz), computing qEEG source spectra using VARETA inverse solution, and applying probabilistic CCA (pCCA) with cognitive test scores (MMSE, DRS, FAB, Sequencing, Memory, Recognition). Kernel step: Compute PSD from 0.78-19.14 Hz (49 frequency bins), then perform pCCA to obtain latent variables representing qEEG-cognition coupling. The mediation analysis uses Neuroepo dosage (0 vs 5mg) as treatment, pCCA latent variables as mediator, and cognitive scores as outcome.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — Uses openneuro_ds003194 EEG data to test whether qEEG source activity mediates the effect of Neuroepo dosage on cognitive performance in PD patients, using pCCA to extract latent variables from 2.56-s resting-state epochs and linear mixed-effects mediation models.
- **Kernel Notes**: 1) Extract 2.56-s epochs from `ojoscerrados` resting-state segments. 2) Apply VARETA inverse solution to compute source activity. 3) Compute PSD in 0.78-19.14 Hz range (49 frequency bins). 4) Perform pCCA to derive latent variables from qEEG spectra and cognitive test scores. 5) Run mediation analysis with Neuroepo dose as treatment, pCCA latents as mediator, cognitive scores as outcome.

### Potential Task 1: Brain State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `discontinuity` is a recording discontinuity marker - excluded. All other events are sustained clinical states (>=2 s). `photic stimulation` and `fotoestimulacion` are equivalent labels (Spanish/English) for the same condition.

| Event | y | Meaning |
|-------|---|---------|
| `ojos cerrados` | 0 | Eyes-closed resting state |
| `ojos abiertos` | 1 | Eyes-open resting state |
| `recuperacion` | 2 | Recovery period |
| `hiperventilacion 2` | 3 | Hyperventilation period 2 |
| `hiperventilacion 3` | 4 | Hyperventilation period 3 |
| `hiperventilacion 1` | 5 | Hyperventilation period 1 |
| `hiperventilacion 4` | 6 | Hyperventilation period 4 |
| `photic stimulation` | 7 | Photic stimulation |
| `fotoestimulacion` | 8 | Photic stimulation (Spanish) |
| `HPVOJOS ABIERTOS` | 9 | Eyes-open during hyperventilation |
| `HEPERVENTILACION OJOS ABIERTOS` | 10 | Hyperventilation eyes-open variant |

## Data Quality Notes

- Clinical recording from Parkinson's patients; expect higher artifact rate than healthy subjects.
- `photic stimulation` / `fotoestimulacion` are duplicate labels for the same condition.
- `discontinuity` events mark recording gaps - exclude from epoch analysis.
- Verify channel count consistency across subjects before pooling.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review