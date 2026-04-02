# Inner Speech

**Dataset**: `openneuro_ds003626` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003626
**Category**: High-level Mental | **Subjects**: 10 | **Files (Completed)**: 30
**Channels**: 137 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants performed inner speech (imagined speech), pronounced speech, and visualization tasks involving four directional commands (Up, Down, Right, Left) to explore the neural correlates of the 'inner voice' phenomenon for potential BCI applications. High-density EEG (137 channels) was recorded during all three modalities of speech production/imagery. No discrete event markers were captured in the EEG trigger channel; paradigm timing is encoded externally.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003626

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG recording |

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

### Primary Task 1: Inner speech word classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 0.5 s, target_events = [`child`, `daughter`, `father`, `wife`, `four`, `three`, `ten`, `six`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `child` | 0 | Social word - child |
  | `daughter` | 1 | Social word - daughter |
  | `father` | 2 | Social word - father |
  | `wife` | 3 | Social word - wife |
  | `four` | 4 | Numerical word - four |
  | `three` | 5 | Numerical word - three |
  | `ten` | 6 | Numerical word - ten |
  | `six` | 7 | Numerical word - six |
- **Evidence**:
  - DOI: 10.3389/fnhum.2025.1668935 — Uses OpenNeuro ds003626 to classify 8 imagined words (social and numerical categories) from EEG using EEGNet and Transformer models with LOSO cross-validation
- **Kernel Notes**: Verify event ID mapping from events.tsv. The 8-word classification task uses balanced classes from social (child, daughter, father, wife) and numerical (four, three, ten, six) categories. Apply bandpass 0.1-50Hz FIR filtering and artifact rejection ±300μV as per paper.

### Primary Task 2: Directional command decoding (inner, pronounced, visualization)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5` (or `epoch_by_event_hdf5` if external timing restored)
- **Epoch Parameters**: segment_length = 2.0 s *, overlap = 0.5 * | tmin = Needs verification *, tmax = Needs verification *, target_events = [`Up`, `Down`, `Left`, `Right`]
- **Label Route**: `Annotation` or `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Up` | 0 | Upward directional command |
  | `Down` | 1 | Downward directional command |
  | `Left` | 2 | Left directional command |
  | `Right` | 3 | Right directional command |
- **Super Meta Notes**: Derived from experimental protocol timing stored in events.tsv (no EEG trigger markers present). Three modalities: inner speech, pronounced speech, visualization. Kernel must reconstruct trial onsets from external timing files.
- **Evidence**:
  - DOI: https://doi.org/10.1038/s41597-022-01536-7 — GitHub repository provides MNE preprocessing scripts for OpenNeuro ds003626 with directional commands (Up/Down/Left/Right) across inner speech, pronounced speech, and visualization modalities for BCI decoding
- **Kernel Notes**: No EEG trigger markers in raw data; must use events.tsv or behavioral logs to reconstruct trial timing. Verify event ID mapping from events.tsv. Task covers three modalities — consider separate label per modality or collapsed across all three.


## Data Quality Notes

- No EEG trigger markers present; trial timing must be reconstructed from events.tsv or behavioral logs.
- Small sample size (10 subjects, 30 files across 3 conditions).
- High-density 137-channel EEG; requires careful re-referencing and ICA for artifact removal.

## References

- **Reference**: `Inner Speech Dataset. OpenNeuro ds003626.`
