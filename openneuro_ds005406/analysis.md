# EEG Frequency Tagging Reveals the Integration of Dissimilar Observed Actions

**Dataset**: `openneuro_ds005406` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005406
**Category**: Sensory/Response | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

A frequency-tagging EEG study measuring steady-state visual evoked potentials (SSVEP) as participants observed dissimilar human actions presented in rapid visual sequences. The study uses neural entrainment at different tagging frequencies to measure the integration of distinct action components (e.g., arm and leg movements). Four action-pair conditions are encoded as S-code pairs (S11/12, S21/22, S31/32, S41/42).


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 41` | 231 | event | raw | Action condition 4, sequence start |
| `Stimulus/S 21` | 231 | event | raw | Action condition 2, sequence start |
| `Stimulus/S 22` | 231 | event | raw | Action condition 2, sequence end |
| `Stimulus/S 42` | 230 | event | raw | Action condition 4, sequence end |
| `Stimulus/S 31` | 230 | event | raw | Action condition 3, sequence start |
| `Stimulus/S 32` | 230 | event | raw | Action condition 3, sequence end |
| `Stimulus/S 11` | 230 | event | raw | Action condition 1, sequence start |
| `Stimulus/S 12` | 230 | event | raw | Action condition 1, sequence end |
| `New Segment/` | 29 | admin | raw | BrainVision segment boundary (exclude) |
| `Stimulus/S255` | 24 | admin | raw | S255 admin sync trigger (exclude) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 41`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 42`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 11`, `Stimulus/S 12`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: SSVEP Action Condition Classification (4-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -2.0 s *, tmax = 48.6 s *, target_events = [`Stimulus/S 11`, `Stimulus/S 21`, `Stimulus/S 31`, `Stimulus/S 41`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Same movement, 1 person (condition 1) |
  | `Stimulus/S 21` | 1 | Different movement, 1 person (condition 2) |
  | `Stimulus/S 31` | 2 | Same movement, 2 people (condition 3) |
  | `Stimulus/S 41` | 3 | Different movement, 2 people (condition 4) |
- **Super Meta Notes**: Derived from raw event(s) [`Stimulus/S 11`, `Stimulus/S 12`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 41`, `Stimulus/S 42`] by mapping start markers (S11/S21/S31/S41) to 4 conditions based on 2x2 factorial design (movement type: same/different × agent number: 1P/2P). Kernel step: Use only start-of-sequence markers (S11/S21/S31/S41) as epoch anchors; apply label mapping to derive 4-class condition labels (0-3). End markers (S12/S22/S32/S42) indicate sequence end but are not needed as separate epoch anchors since each start marker uniquely identifies its condition.
- **Evidence**:
  - DOI: 10.1101/2024.05.10.593473 — EEG frequency-tagging study with 29 participants analyzing SSVEP responses at base frequencies (2.5 Hz, 3.16 Hz) and intermodulation component (5.66 Hz) across four action conditions varying in movement type (same/different) and agent number (1P/2P)
- **Kernel Notes**: Extract epochs anchored at sequence start events (S11/S21/S31/S41). Compute SSVEP power spectral density in target frequency bands (2.5 Hz, 3.16 Hz, 5.66 Hz) for classification. Original paper used tmin=-2.0s, tmax=53.6s initial, cropped to 3s-48.6s post-movement onset; using final cropped window (tmax=48.6s) to focus on steady-state response. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Action Integration Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: New Segment/ (29) and Stimulus/S255 (24) are admin - exclude. Four action conditions with start/end markers each.

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

## Data Quality Notes

- New Segment/ and Stimulus/S255 are administrative - exclude.
- Frequency-tagging paradigm; SSVEP analysis may be more appropriate than traditional ERP epoching.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review