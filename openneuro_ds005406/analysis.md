# EEG Frequency Tagging Reveals the Integration of Dissimilar Observed Actions

**Dataset**: `openneuro_ds005406` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005406
**Category**: Sensory/Response | **Subjects**: 29 | **Files (Completed)**: 29 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

A frequency-tagging EEG study measuring steady-state visual evoked potentials (SSVEP) as participants observed dissimilar human actions presented in rapid visual sequences. The study uses neural entrainment at different tagging frequencies to measure the integration of distinct action components (e.g., arm and leg movements). Four action-pair conditions are encoded as S-code pairs (S11/12, S21/22, S31/32, S41/42).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005406

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 41` | 231 | short | raw | Action condition 4, sequence start |
| `Stimulus/S 21` | 231 | short | raw | Action condition 2, sequence start |
| `Stimulus/S 22` | 231 | short | raw | Action condition 2, sequence end |
| `Stimulus/S 42` | 230 | short | raw | Action condition 4, sequence end |
| `Stimulus/S 31` | 230 | short | raw | Action condition 3, sequence start |
| `Stimulus/S 32` | 230 | short | raw | Action condition 3, sequence end |
| `Stimulus/S 11` | 230 | short | raw | Action condition 1, sequence start |
| `Stimulus/S 12` | 230 | short | raw | Action condition 1, sequence end |
| `New Segment/` | 29 | admin | raw | BrainVision segment boundary (exclude) |
| `Stimulus/S255` | 24 | admin | raw | S255 admin sync trigger (exclude) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 41`, `Stimulus/S 21`, `Stimulus/S 22`, `Stimulus/S 42`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 11`, `Stimulus/S 12`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: SSVEP target/frequency decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `stim` or `Annotation`
- **Target Definition**: Stimulus frequency or target index
- **Evidence**: SSVEP paradigm is explicitly stated in dataset metadata/reference. Source: https://openneuro.org/datasets/ds005406 DOI: https://doi.org/10.1101/2024.05.10.593473v1


### Normal Task 1: Action Integration Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `EEG frequency tagging reveals the integration of dissimilar observed actions`
