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

### Primary Task 1: Binary Semantic Target Identification in Chinese Reading
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 2.0 s, target_events = [`target_sentence`, `non-target_sentence`]
- **Label Route**: `Annotation` | `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `non-target_sentence` | 0 | No target word present in sentence |
  | `target_sentence` | 1 | Contains target semantic word (names, means of transportation, animals, fruits) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-05036-2 — TMNRED dataset paper presenting Chinese natural reading EEG where 30 participants read sentences containing target semantic words vs non-target sentences; EEG recorded during 2-second stimulus presentation windows with binary labels indicating target presence
- **Kernel Notes**: The paper defines stimulus presentation windows of 2.0 s with inter-trial interval of 0.2 s. Use epoch tmin=0 s to tmax=2.0 s aligned to sentence onset triggers. The raw events.tsv contains condition labels that map to binary target/non-target labels.

### Normal Task 1: Semantic Target Identification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30 distinct numerical codes across all files; full decode from events.tsv or paper required. 720 files from 30 subjects x 24 sessions/files. Low sampling rate (200 Hz) limits high-frequency analysis.

| Event | y | Meaning |
|-------|---|------|
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

## Data Quality Notes

- Numerical trigger codes require decode from events.tsv or dataset paper for semantic interpretation.
- 30 distinct codes; group by semantic condition (target/non-target) when possible.
- Low sampling rate (200 Hz) - suitable for N400/P600 ERP components but not high-gamma analysis.

## References

- **Reference**: `TMNRED, A Chinese Language EEG Dataset for Fuzzy Semantic Target Identification in Natural Reading Environments`
