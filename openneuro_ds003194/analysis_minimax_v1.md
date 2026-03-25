# Neuroepo multisession

**Dataset**: `openneuro_ds003194` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003194
**Category**: Biological State | **Subjects**: 25 | **Files (Completed)**: 29
**Channels**: 19 | **Sampling Rate**: 200 Hz

## Paradigm

Resting-state EEG recorded before and after a six-month Neuroepo drug administration period to evaluate neuroprotective effects in Parkinson's disease patients. The protocol includes resting-state (eyes closed / eyes open), hyperventilation periods, and photic stimulation sections. This is a clinical neurological assessment battery recorded in Spanish (event labels in Spanish).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003194

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `ojos cerrados` | 29 (files) | long | raw | Eyes-closed resting state |
| `ojos abiertos` | 28 (files) | long | raw | Eyes-open resting state |
| `recuperacion` | 28 (files) | long | raw | Recovery period after hyperventilation |
| `hiperventilacion 1` | 27 (files) | long | raw | Hyperventilation period 1 |
| `hiperventilacion 2` | 28 (files) | long | raw | Hyperventilation period 2 |
| `hiperventilacion 3` | 28 (files) | long | raw | Hyperventilation period 3 |
| `hiperventilacion 4` | 15 (files) | long | raw | Hyperventilation period 4 |
| `photic stimulation` | 11 (files) | long | raw | Photic stimulation block |
| `fotoestimulacion` | 11 (files) | long | raw | Photic stimulation (Spanish label) |
| `discontinuity` | 9 (files) | admin | raw | Recording discontinuity marker - exclude |
| `HPVOJOS ABIERTOS` | 6 (files) | long | raw | Eyes-open during hyperventilation |
| `HEPERVENTILACION OJOS ABIERTOS` | 1 (file) | long | raw | Hyperventilation eyes-open variant |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `photic stimulation`, `fotoestimulacion`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Cognitive Performance Regression via qEEG Mediation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.56 s, overlap = 0.0, target_events = [`ojoscerrados`] *
- **Label Route**: `Annotation` | `misc`
- **Meta Level**: super
- **Target Definition**:
  | y | Meaning |
  |---|---|
  | MMSE | Mini-Mental State Examination score |
  | DRS | Mattis Dementia Rating Scale score |
  | FAB | Frontal Assessment Battery score |
  | Sequency | Sequential cognitive task score |
  | Memory | Memory test score |
  | Recognition | Recognition test score |
- **Super Meta Notes**: Latent variables derived via probabilistic CCA (pCCA) from 3,244 qEEG source spectra and 6 cognitive test scores. qEEG source spectra computed using VARETA inverse solution on 2.56-s epochs, transformed to frequency domain (0.78-19.14 Hz, 49 frequency bins). Predictors: Neuroepo dose (0 at baseline, 5mg at 6 months for treatment group; placebo: 0 at all timepoints). Mediation model tests whether qEEG source activity mediates the effect of Neuroepo dosage on cognitive performance.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.841428 — Uses openneuro_ds003194 EEG data to test whether qEEG source activity mediates the effect of Neuroepo dosage on cognitive performance in PD patients, using pCCA to extract latent variables from 2.56-s resting-state epochs and linear mixed-effects mediation models.
- **Kernel Notes**: 1) Extract 2.56-s epochs from `ojoscerrados` events (eyes-closed resting state); 2) Apply VARETA inverse solution to obtain qEEG source spectra; 3) Transform to frequency domain (0.78-19.14 Hz, 49 bins); 4) Use pCCA to derive latent variables from spectra and cognitive scores; 5) Fit linear mixed-effects mediation model with Neuroepo dose as predictor, qEEG latent vars as mediator, cognitive scores as outcome.


### Primary Task 2: Publisher-defined BIDS task: Task pre nepo
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003194 DOI: https://doi.org/10.18112/openneuro.ds003194.v1.0.4


### Primary Task 3: Publisher-defined BIDS task: Task 6m nepo
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003194 DOI: https://doi.org/10.18112/openneuro.ds003194.v1.0.4


### Normal Task 1: Brain State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `discontinuity` is a recording discontinuity marker - excluded. All other events are sustained clinical states (>=2 s). `photic stimulation` and `fotoestimulacion` are equivalent labels (Spanish/English) for the same condition.

| Event | y | Meaning |
 |-------|---|------|
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

## References

- **Reference**: `EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. Sci. data 6, 103 (2019)`
