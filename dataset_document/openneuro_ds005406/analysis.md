# EEG Frequency Tagging Reveals the Integration of Dissimilar Observed Actions

**Dataset**: `openneuro_ds005406` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005406
**Category**: Sensory/Response | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

A frequency-tagging EEG study measuring steady-state visual evoked potentials (SSVEP) as participants observed dissimilar human actions presented in rapid visual sequences. The study uses neural entrainment at different tagging frequencies to measure the integration of distinct action components (e.g., arm and leg movements). Four action-pair conditions are encoded as S-code pairs (S11/12, S21/22, S31/32, S41/42).

## File Scan Result

> **Kernel SHA256**: `31c1edbda1ea156c9a954d9e15b07057e742dd664f402adcf412b02e91845bca`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 11` | 230 | event | raw | Action condition 1 sequence start (same movement, 1 person) |
| `Stimulus/S 12` | 230 | event | raw | Action condition 1 sequence end |
| `Stimulus/S 21` | 231 | event | raw | Action condition 2 sequence start (different movement, 1 person) |
| `Stimulus/S 22` | 231 | event | raw | Action condition 2 sequence end |
| `Stimulus/S 31` | 230 | event | raw | Action condition 3 sequence start (same movement, 2 people) |
| `Stimulus/S 32` | 230 | event | raw | Action condition 3 sequence end |
| `Stimulus/S 41` | 231 | event | raw | Action condition 4 sequence start (different movement, 2 people) |
| `Stimulus/S 42` | 230 | event | raw | Action condition 4 sequence end |


### MISC Label Summary
- **Route**: `misc`
- **Role**: Stores continuous or derived channel labels.
- **Candidate Labels**: `65`
- **Kernel Note**: Verify channel roles and units.
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: SSVEP Action Condition Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s, tmax = 48.6 s, target_events = [`Stimulus/S 11`, `Stimulus/S 21`, `Stimulus/S 31`, `Stimulus/S 41`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Same movement, 1 person (condition 1) |
  | `Stimulus/S 21` | 1 | Different movement, 1 person (condition 2) |
  | `Stimulus/S 31` | 2 | Same movement, 2 people (condition 3) |
  | `Stimulus/S 41` | 3 | Different movement, 2 people (condition 4) |
- **Super Meta Notes**: Labels derived from raw start markers (S11/S21/S31/S41) mapping to 2x2 factorial design (movement type: same/different × agent number: 1P/2P). Use only start-of-sequence markers as epoch anchors; end markers (S12/S22/S32/S42) indicate sequence end but are not needed as separate anchors since each start uniquely identifies its condition.
- **Evidence**:
  - DOI: 10.1016/j.cortex.2024.10.015
  - DOI: 10.1101/2024.05.10.593473
- **Kernel Notes**: Extract epochs anchored at sequence start events (S11/S21/S31/S41). Compute SSVEP power spectral density in target frequency bands (2.5 Hz, 3.16 Hz, 5.66 Hz) for classification. Using tmax=48.6s (cropped from original 53.6s window) to focus on steady-state response phase.

### Potential Task 1: Action Integration Condition Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 41`, `Stimulus/S 42`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Action condition 1 start |
  | `Stimulus/S 12` | 1 | Action condition 1 end |
  | `Stimulus/S 21` | 2 | Action condition 2 start |
  | `Stimulus/S 22` | 3 | Action condition 2 end |
  | `Stimulus/S 31` | 4 | Action condition 3 start |
  | `Stimulus/S 32` | 5 | Action condition 3 end |
  | `Stimulus/S 41` | 6 | Action condition 4 start |
  | `Stimulus/S 42` | 7 | Action condition 4 end |
- **Evidence**:
  - Paradigm: Short-window transient analysis around individual action markers to capture event-related responses for action integration mechanisms.
- **Kernel Notes**: Epoch around all 8 markers to capture transient responses to both sequence start and end events. The -0.2s to 1.0s window captures pre-stimulus baseline and initial evoked response to each marker. Useful for distinguishing neural responses at sequence onset vs offset.