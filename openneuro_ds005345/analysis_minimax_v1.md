# Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset

**Dataset**: `openneuro_ds005345` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005345
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 28
**Channels**: 64 | **Sampling Rate**: 500 Hz

## Paradigm

Participants engaged in naturalistic listening to excerpts of "Le Petit Prince" (The Little Prince) under single-talker and multi-talker conditions during simultaneous EEG and 7T fMRI recording. The study investigates neural processing of speech under cocktail-party-style listening conditions. Stimulus/S 11 marks single-talker condition onsets; Stimulus/S 31-S 34 mark multi-talker condition variants. `Comment/actiCAP Data On` is an EEG system administrative marker.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005345

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S 11` | ~19/file | long | raw | Single-talker listening block onset |
| `Stimulus/S 31` | ~6/file | long | raw | Multi-talker condition variant 31 onset |
| `Stimulus/S 32` | ~6/file | long | raw | Multi-talker condition variant 32 onset |
| `Stimulus/S 33` | ~6/file | long | raw | Multi-talker condition variant 33 onset |
| `Stimulus/S 34` | ~6/file | long | raw | Multi-talker condition variant 34 onset |
| `Comment/actiCAP Data On` | 25/file | admin | raw | EEG recording system marker (exclude) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Listening Condition Classification (5-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 600.0 s (10 min), overlap = 0.0 *, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Single-talker listening |
  | `Stimulus/S 31` | 1 | Multi-talker mix_f attended |
  | `Stimulus/S 32` | 2 | Multi-talker mix_m attended |
  | `Stimulus/S 33` | 3 | Multi-talker mix_f unattended |
  | `Stimulus/S 34` | 4 | Multi-talker mix_m unattended |
- **Evidence**:
  - DOI: 10.1101/2025.04.03.646958 — Validates LPP Multi-talker Dataset with 64-channel EEG from 26 participants listening to single-talker and multi-talker conditions (Stimulus/S 11, 31-34), epochs from -500ms to 10 minutes after section onset.
  - DOI: 10.1038/s41597.025.05158.7 — Describes same dataset with EEG from 26 participants during naturalistic listening to single-talker and multi-talker speech conditions, validated via ISC analysis.
- **Kernel Notes**: Use long event epoching (tmin=-0.5s, tmax=10min) for sustained block-level classification. Exclude `Comment/actiCAP Data On` (admin marker).

### Primary Task 2: Word-Level Epoch Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.5 s, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Single-talker word |
  | `Stimulus/S 31-34` | 1 | Multi-talker word (pooled) |
- **Evidence**:
  - DOI: 10.1101/2025.04.03.646958 — Additional word-level epochs segmented from -100ms to 500ms after word offset for evoked word response analysis.
- **Kernel Notes**: Requires word-onset annotations beyond block markers — derive from stimulus timing if available; otherwise use block-level epochs only.

### Normal Task 1: Listening Condition Classification (binary/multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `Comment/actiCAP Data On` is admin - exclude. Naturalistic listening paradigm with sustained EEG blocks. Very small dataset (28 files, 25 subjects).

| Event | y | Meaning |
 |-------|---|------|
 | `Stimulus/S 11` | 0 | Single-talker listening |
 | `Stimulus/S 31` | 1 | Multi-talker condition 31 |
 | `Stimulus/S 32` | 2 | Multi-talker condition 32 |
 | `Stimulus/S 33` | 3 | Multi-talker condition 33 |
 | `Stimulus/S 34` | 4 | Multi-talker condition 34 |

## Data Quality Notes

- Very small dataset (28 files, 25 subjects).
- `Comment/actiCAP Data On` is an admin system marker - exclude from epoching.
- Simultaneous 7T fMRI - MR gradient artifacts may require removal if present.

## References

- **Reference**: `Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset`
