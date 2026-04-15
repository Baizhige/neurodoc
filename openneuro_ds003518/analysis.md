# EEG: Simon Conflict with Reinforcement + Cabergoline Challenge

**Dataset**: `openneuro_ds003518` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003518
**Category**: High-level Mental | **Subjects**: 110 | **Files (Completed)**: 137
**Channels**: 64 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

This study examines whether conflict acts as an implicit cost in reinforcement learning using a modified Simon task with pharmacological manipulation. Healthy participants performed a Simon conflict task across training and test phases, with a double-blind Cabergoline (dopamine D2/D3 agonist) challenge administered to examine dopaminergic modulation. The training phase included reinforcement feedback to shape behavior; the test phase probed learned conflict avoidance. Mid-frontal theta and error-related negativity are key EEG measures.

## File Scan Result

> **Kernel SHA256**: `5228689e8c1103296ad691b6b7796a20782a31b16bbd5e7b17fa4b91636c752e`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Correct/Incorrect Response Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`Trn Stim`, `Test Stim`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|--------|
  | `incorrect` | 0 | Error response |
  | `correct` | 1 | Correct response |
- **Evidence**:
  - DOI: `10.1038/ncomms6394` — EEG frontal midline theta analyzed from -500 to +1000 ms around stimulus events; correct/incorrect outcome classification used to examine conflict costs in reinforcement learning during Simon task performance.
- **Kernel Notes**: Epochs aligned to stimulus onset (Trn Stim, Test Stim), capturing both pre-stimulus preparation and post-response outcome processing within the epoch window. Labels derived from subsequent correct/incorrect outcome events following each stimulus trial. Drug condition (cabergoline vs placebo) available as grouping variable for stratified analysis.

### Potential Task 1: Stimulus Congruency Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.0 s, target_events = [`Trn Stim`, `Test Stim`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|--------|
  | `Trn Stim` (congruent) | 0 | Congruent Simon trial |
  | `Trn Stim` (incongruent) | 1 | Incongruent Simon trial |
  | `Test Stim` (congruent) | 0 | Congruent Simon trial |
  | `Test Stim` (incongruent) | 1 | Incongruent Simon trial |
- **Evidence**: Simon conflict paradigm inherently involves congruent vs incongruent stimulus-response mappings; mid-frontal theta known to be modulated by response conflict (NComm 2014) though explicit stimulus label mapping to congruency not provided in available references.
- **Kernel Notes**: Stimulus label mapping (S-codes to Trn Stim/Test Stim) and congruency sub-type require clarification from paradigm documentation. Verify mapping between raw event codes and semantic stimulus types.

### Potential Task 2: Response-Locked Performance Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.6 s, target_events = [`Trn Resp`, `Test Resp`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|--------|
  | `Trn Resp` | 1 | Training phase response made |
  | `Test Resp` | 1 | Test phase response made |
- **Evidence**: Response events (Trn Resp, Test Resp) available in dataset; error-related negativity (ERN) and correct-related negativity (CRN) are established EEG markers of motor response monitoring in conflict tasks.
- **Kernel Notes**: Some trials lack response (Trn No Response: 136, Test No Response: 55); response-locked epochs capture motor-related activity. Error-related potentials (ERN) expected over frontal midline electrodes following incorrect responses.

### Potential Task 3: Feedback-Related Learning Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.3 s, tmax = 0.8 s, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|-----|--------|
  | `FB` | 1 | Feedback stimulus in training phase |
- **Evidence**: Feedback events (FB, n=274) present in training phase; reinforcement learning paradigm suggests feedback-related negativity (FRN) and P300 markers of reward/punishment processing are analyzable.
- **Kernel Notes**: FB events relatively sparse compared to stimulus events; feedback-locked epochs enable analysis of reward learning signals. Cabergoline manipulation expected to modulate feedback processing via dopaminergic mechanisms.