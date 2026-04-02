# TMNRED: A Chinese Language EEG Dataset for Fuzzy Semantic Target Identification in Natural Reading Environments

**Dataset**: `openneuro_ds005383` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005383
**Category**: High-level Mental | **Subjects**: 30 | **Files (Completed)**: 720
**Channels**: 30 | **Sampling Rate**: 200 Hz

## Paradigm

Participants engaged in self-paced natural reading of Chinese sentences and news headlines to identify fuzzy semantic targets embedded in text. The study investigates neural correlates of semantic processing during naturalistic reading, recording EEG with 30 channels at 200 Hz. Numerical BioSemi trigger codes mark word/sentence onset events across three sessions per subject (3 x 240 files = 720 total). The trigger code structure encodes semantic conditions, target presence, and reading context.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005383

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `55` | 240/file | short | raw | Stimulus condition code 55 (decode from events.tsv) |
| `31` | 240/file | short | raw | Stimulus condition code 31 |
| `56` | 240/file | short | raw | Stimulus condition code 56 |
| `36` | 240/file | short | raw | Stimulus condition code 36 |
| `41` | 240/file | short | raw | Stimulus condition code 41 |
| `51` | 240/file | short | raw | Stimulus condition code 51 |
| `16` | 240/file | short | raw | Stimulus condition code 16 |
| `61` | 240/file | short | raw | Stimulus condition code 61 |
| `26` | 240/file | short | raw | Stimulus condition code 26 |
| `46` | 240/file | short | raw | Stimulus condition code 46 |
| `21` | 240/file | short | raw | Stimulus condition code 21 |
| `22` | 240/file | short | raw | Stimulus condition code 22 |
| `32` | 240/file | short | raw | Stimulus condition code 32 |
| `42` | 240/file | short | raw | Stimulus condition code 42 |
| `52` | 240/file | short | raw | Stimulus condition code 52 |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Binary Semantic Target Identification in Chinese Sentences
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.0 s, target_events = [see Target Definition]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `31` | 0 | Non-target sentence (no fuzzy semantic target word) |
  | `32` | 1 | Target sentence (contains fuzzy semantic target word: name, means of transportation, animal, or fruit) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05036-2 — TMNRED dataset paper confirming 30 participants read Chinese sentences with vs without target semantic words during 2-second stimulus presentation windows; binary classification of target presence.
- **Kernel Notes**: Verify event ID mapping from events.tsv. The mapping `31→non-target, 32→target` is inferred from code proximity; alternative grouping may be needed. Default tmin=0s aligns with stimulus onset; tmax=2.0s matches presentation duration from paper. (replaces Primary Task 1 and Normal Task 1 from original analysis.md)

### Normal Task 1: Multiclass Condition Code Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s *, tmax = 2.0 s *, target_events = [`16`, `21`, `22`, `26`, `31`, `32`, `36`, `41`, `42`, `46`, `51`, `52`, `55`, `56`, `61`]
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `16` | 0 | Condition code 16 |
  | `21` | 1 | Condition code 21 |
  | `22` | 2 | Condition code 22 |
  | `26` | 3 | Condition code 26 |
  | `31` | 4 | Condition code 31 |
  | `32` | 5 | Condition code 32 |
  | `36` | 6 | Condition code 36 |
  | `41` | 7 | Condition code 41 |
  | `42` | 8 | Condition code 42 |
  | `46` | 9 | Condition code 46 |
  | `51` | 10 | Condition code 51 |
  | `52` | 11 | Condition code 52 |
  | `55` | 12 | Condition code 55 |
  | `56` | 13 | Condition code 56 |
  | `61` | 14 | Condition code 61 |
- **Notes**: 15 distinct numerical codes; full decode from events.tsv required for semantic meaning. Epoch parameters inferred from paper's 2-second stimulus window (tmin=0s, tmax=2.0s).

## Data Quality Notes

- Numerical trigger codes require decode from events.tsv or dataset paper for semantic interpretation.
- 30 distinct codes; group by semantic condition (target/non-target) when possible.
- Low sampling rate (200 Hz) - suitable for N400/P600 ERP components but not high-gamma analysis.

