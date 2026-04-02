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

### Primary Task 1: Listening Condition Classification (Multitalker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 600 s (10 minutes), overlap = 0.0 *, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
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
  - DOI: 10.1101/2025.04.03.646958 — Validates LPP Multi-talker Dataset with 64-channel EEG from 26 participants listening to single-talker and multi-talker conditions (Stimulus/S 11, 31-34), epochs segmented from -500ms to 10 minutes after section onset
  - DOI: 10.1038/s41597.025.05158.7 — Describes LPP Multi-talker Dataset (OpenNeuro ds005345) with EEG from 26 participants during naturalistic listening to single-talker and multi-talker speech conditions, validated via ISC analysis
- **Kernel Notes**: Verify event ID mapping from events.tsv. Overlap set to 0.0 for contiguous block analysis; adjust if needed for sliding window. Exclude `Comment/actiCAP Data On` admin marker. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: Word-Level Epoch Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.5 s, target_events = [`Stimulus/S 11`, `Stimulus/S 31`, `Stimulus/S 32`, `Stimulus/S 33`, `Stimulus/S 34`]
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/S 11` | 0 | Single-talker word epoch |
  | `Stimulus/S 31` | 1 | Multi-talker condition 31 word epoch |
  | `Stimulus/S 32` | 2 | Multi-talker condition 32 word epoch |
  | `Stimulus/S 33` | 3 | Multi-talker condition 33 word epoch |
  | `Stimulus/S 34` | 4 | Multi-talker condition 34 word epoch |
- **Evidence**:
  - DOI: 10.1101/2025.04.03.646958 — Additional word-level epochs extracted from -100ms to 500ms after word offset
  - DOI: 10.1038/s41597.025.05158-7 — Validates evoked word responses with word-level epochs
- **Kernel Notes**: Requires word-level event markers in the dataset; verify if such markers exist in events.tsv. If not available, task cannot be executed.


## Data Quality Notes

- Very small dataset (28 files, 25 subjects).
- `Comment/actiCAP Data On` is an admin system marker - exclude from epoching.
- Simultaneous 7T fMRI - MR gradient artifacts may require removal if present.

## References

- **Reference**: `Le Petit Prince Multitalker: Naturalistic 7T fMRI and EEG Dataset`
