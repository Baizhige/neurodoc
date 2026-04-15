# PEARL-Neuro Database (Alzheimer's Risk Genes, Lifestyle, Neuroimaging)

## Paradigm

(See existing draft)

## File Scan Result

> **Kernel SHA256**: `c24e666a19c1f54653c5adf990d9b6a3644fd96816140c499de0408a097c371c`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 7 | event | raw |  |
| `Stimulus/S  1` | 10282 | event | raw |  |
| `Stimulus/S  2` | 9918 | event | raw |  |
| `Stimulus/S  3` | 6246 | event | raw |  |
| `Stimulus/S  4` | 8495 | event | raw |  |
| `Stimulus/S  5` | 6564 | event | raw |  |
| `Stimulus/S 10` | 706 | event | raw |  |
| `Stimulus/S 11` | 3821 | event | raw |  |
| `Stimulus/S 12` | 11237 | event | raw |  |
| `Time 0/` | 1 | event | raw |  |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: APOE4 Genetic Status Classification (MSIT)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.84 s, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`, `Stimulus/S  4`, `Stimulus/S  5`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | derived from genetic data | 0 | APOE4- (no APOE4 allele) |
  | derived from genetic data | 1 | APOE4+ (at least one APOE4 allele) |
- **Super Meta Notes**: Derived from participant genetic testing data (APOE genotyping). Kernel step: Load external APOE genotype file and map participant ID to binary APOE4+ (y=1) / APOE4- (y=0) label. Epoch by stimulus events from MSIT task runs.
- **Evidence**:
  - DOI: 10.3389/fnins.2025.1579329 — Binary classification of APOE4 genetic status using theta oscillation propagation features from MSIT cognitive task (stimulus to response: 0.84 +/- 0.16 s)
  - DOI: 10.1038/s41597-024-03106-5 — PEARL-Neuro Database descriptor with EEG/fMRI from 79 participants, genetic data on APOE/PICALM, MSIT and Sternberg task protocols
- **Kernel Notes**: Filter files by task label 'MSIT'. Map Stimulus/S 1-5 as target events. Epoch from stimulus onset to average response time (~0.84 s). Extract theta propagation features (LPG length) from frontal midline electrodes.

### Classical Task 2: APOE4 Genetic Status Classification (Sternberg)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12.36 s, target_events = [`Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | derived from genetic data | 0 | APOE4- (no APOE4 allele) |
  | derived from genetic data | 1 | APOE4+ (at least one APOE4 allele) |
- **Super Meta Notes**: Derived from participant genetic testing data (APOE genotyping). Kernel step: Load external APOE genotype file and map participant ID to binary APOE4+ (y=1) / APOE4- (y=0) label. Epoch by stimulus events from Sternberg task runs.
- **Evidence**:
  - DOI: 10.3389/fnins.2025.1579329 — Binary classification of APOE4 genetic status using theta oscillation propagation features from Sternberg memory task (stimulus onset to last behavioral timing: 12.36 +/- 0.20 s)
  - DOI: 10.1038/s41597-024-03106-5 — PEARL-Neuro Database descriptor with EEG/fMRI from 79 participants, genetic data on APOE/PICALM, MSIT and Sternberg task protocols
- **Kernel Notes**: Filter files by task label 'Sternberg'. Map Stimulus/S 10-12 as target events. Epoch from stimulus onset to last behavioral response (~12.36 s). Extract theta propagation features from frontal midline electrodes.

### Classical Task 3: Resting-State Spectral Power Ratio Analysis
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = N/A (continuous segmentation)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | segment | continuous | Clinical score (e.g., attention deficit, hyperactivity) for correlation with spectral features |
- **Super Meta Notes**: Labels derived from spectral analysis—delta/beta and theta/beta power ratios as biomarkers of cortical dysregulation, correlated with external clinical attention/hyperactivity scores. Kernel step: Load separate clinical scores file and match by participant ID.
- **Evidence**:
  - DOI: 10.1109/ICDMW69685.2025.00218 — Uses Hann-windowed 4 second epochs with 50% overlap (Welch's method) to compute delta/beta and theta/beta power ratios from resting-state EEG, correlated with dementia risk clinical scores
  - DOI: 10.1038/s41597-024-03106-5 — PEARL-Neuro Database with resting-state (eyes open/closed) EEG recordings from 79 middle-aged adults at dementia risk
- **Kernel Notes**: Filter files by task label 'rest'. Apply 4s sliding window segmentation with 50% overlap. Compute PSD using Welch's method. Extract delta/beta and theta/beta power ratios. Correlation with external clinical scores requires kernel to load separate clinical data file.

### Normal Task 1: MSIT Interference Level Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 0.84 s, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`, `Stimulus/S  4`, `Stimulus/S  5`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S  1` | 1 | MSIT low interference (congruent) |
  | `Stimulus/S  2` | 1 | MSIT low interference (congruent) |
  | `Stimulus/S  3` | 1 | MSIT low interference (congruent) |
  | `Stimulus/S  4` | 2 | MSIT high interference (incongruent) |
  | `Stimulus/S  5` | 2 | MSIT high interference (incongruent) |
- **Evidence**:
  - DOI: 10.3389/fnins.2025.1579329 — Describes MSIT low/high demand trials in the dataset
  - DOI: 10.1038/s41597-024-03106-5 — PEARL-Neuro Database with MSIT cognitive task
- **Kernel Notes**: Filter by task label 'MSIT'. Map Stimulus/S 1-3 to low interference class (y=1), Stimulus/S 4-5 to high interference class (y=2). Extract event-related spectral perturbations during interference processing window.

### Normal Task 2: Sternberg Memory Set Size Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 12.36 s, target_events = [`Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 10` | 1 | Sternberg memory set size 1 |
  | `Stimulus/S 11` | 2 | Sternberg memory set size 3 |
  | `Stimulus/S 12` | 3 | Sternberg memory set size 5 |
- **Evidence**:
  - DOI: 10.3389/fnins.2025.1579329 — Describes Sternberg task with memory set size variations
  - DOI: 10.1038/s41597-024-03106-5 — PEARL-Neuro Database with Sternberg memory task
- **Kernel Notes**: Filter by task label 'Sternberg'. Map Stimulus/S 10 to set size 1 (y=1), Stimulus/S 11 to set size 3 (y=2), Stimulus/S 12 to set size 5 (y=3). Extract theta power during memory maintenance period (1-5s post-stimulus).

### Potential Task 1: Response-locked Event Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 0 s, target_events = [`response`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `response` | binary | Response correctness or stimulus type association |
- **Kernel Notes**: Response events (24051 total) available for validation. Epoch time-locked to button-press with pre-response window. Use for motor-related potential analysis or error detection.

### Potential Task 2: PICALM Genetic Risk Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = dependent on paradigm, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`, `Stimulus/S  4`, `Stimulus/S  5`, `Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | derived from genetic data | 0 | PICALM GG (protective) |
  | derived from genetic data | 1 | PICALM non-GG (risk) |
- **Super Meta Notes**: Derived from PICALM genotyping (rs543018). Kernel step: Load external PICALM genotype file and map participant ID to binary GG (y=0) / non-GG (y=1) label.
- **Evidence**:
  - DOI: 10.1038/s41597-024-03106-5 — PEARL-Neuro Database includes PICALM risk allele data
  - DOI: 10.3389/fragi.2025.1694701 — PICALM GG vs non-GG cognitive profile differences in the PEARL-Neuro cohort
- **Kernel Notes**: PICALM genotype labels require external file integration. Same epoch parameters as APOE4 classification tasks.

### Potential Task 3: Cognitive Performance Subgroup Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.5, target_events = N/A (continuous)
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | segment | cluster | Cognitive subgroup (better vs worse performance) from neuropsychological test clustering |
- **Evidence**:
  - DOI: 10.3389/fragi.2025.1694701 — Uses agglomerative hierarchical clustering on neuropsychological tests (CVLT, Raven's Progressive Matrices) to identify cognitive performance subgroups
- **Kernel Notes**: Requires external neuropsychological test data and clustering step. Correlation with resting-state spectral features for biomarker discovery.

### Potential Task 4: Sex Differences in APOE/PICALM Cognitive Profiles
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = dependent on paradigm, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  3`, `Stimulus/S  4`, `Stimulus/S  5`, `Stimulus/S 10`, `Stimulus/S 11`, `Stimulus/S 12`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | derived from genetic and demographic data | multi-class | Sex x genotype interaction (e.g., Female/APOE4+, Male/APOE4-, etc.) |
- **Evidence**:
  - DOI: 10.3389/fragi.2025.1694701 — Sex differences in APOE- and PICALM-related cognitive profiles; 192 participants with cognitive and genetic data
- **Kernel Notes**: Requires external demographic data for sex labels. Four-class problem: Female/APOE4+, Female/APOE4-, Male/APOE4+, Male/APOE4-. Interaction analysis for sex-specific genetic effects.
