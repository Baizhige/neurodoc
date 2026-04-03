# Penn Electrophysiology of Encoding and Retrieval Study (PEERS)

**Dataset**: `openneuro_ds004395` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004395
**Category**: High-level Mental | **Subjects**: 300 | **Files (Completed)**: 6480
**Channels**: 129 | **Sampling Rate**: 500 Hz

## Paradigm

A large-scale study investigating the electrophysiological correlates of memory encoding and retrieval using various free recall tasks. Participants encoded word lists and subsequently recalled them (free recall), also performing recognition memory tasks. The study provides a rich dataset for ERP analysis of encoding success, retrieval effort, and memory-related oscillations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Status**: wait_manual_review
> **Evidence Keywords**: confidence
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004395

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `WORD` | 6480x~256 | short | raw | Word presentation onset (encoding) |
| `REC_WORD` | 6480x~100 | short | raw | Recalled word onset (retrieval) |
| `RECOG_TARGET` | 3581x~160 | short | raw | Recognition target word onset |
| `RECOG_LURE` | 3581x~80 | short | raw | Recognition lure word onset |
| `RECOG_RESP` | 3581x~320 | short | raw | Recognition response |
| `RECOG_CONF` | 3563x~320 | short | raw | Confidence rating |
| `DISTRACTOR` | 2439xx | short | raw | Distractor task stimulus |
| `REC_WORD_VV` | 5001xx | short | raw | Recalled word (voice-verified) |
| `REST_REWET` | 5955x1 | rest | raw | Rest/reward-with-eye-tracking marker |
| `SESS_START` | 6478 | admin | raw | Session start marker |
| `SESS_END` | 6474 | admin | raw | Session end marker |
| `REC_START` | 6480 | admin | raw | Recall period start |
| `START` | 3668 | admin | raw | Start marker |
| `STOP` | 3668 | admin | raw | Stop marker |
| `BREAK_START` | 459 | admin | raw | Break start marker |
| `BREAK_STOP` | 459 | admin | raw | Break stop marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived/continuous labels that are not native raw event IDs.
- **Candidate Labels**: `confidence`
- **Kernel Note**: Keep derivation source, unit, and version metadata.

## Tasks

### Primary Task 1: Recognition Memory Old/New Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.2 s, target_events = [`RECOG_TARGET`, `RECOG_LURE`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `RECOG_TARGET` | 0 | Target (old item - previously seen) |
  | `RECOG_LURE` | 1 | Lure (new item - not previously seen) |
- **Evidence**:
  - DOI: 10.31234/osf.io/64j58 — This study used EEG data from the PEERS dataset (openneuro_ds004395) to generate single-trial regressors via logistic regression classifiers on 100ms time windows (500-800ms) to predict drift rate in Diffusion Decision Models for recognition memory old/new decisions.
- **Kernel Notes**: Epoch window covers stimulus-locked response period (-1.0s pre-stimulus to 2.2s post-stimulus). Task predicts DDM drift rate: old items (RECOG_TARGET) yield higher drift rates, new items (RECOG_LURE) yield lower drift rates. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Memory Encoding Classification (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: SESS_START/END, REC_START, START/STOP, BREAK_START/STOP are admin markers - exclude. REST_REWET is a rest marker. Very large dataset (300 subjects, 6480 files); suitable for large-scale ERP studies.

| Event | y | Meaning |
|-------|---|------|
| `RECOG_TARGET` | 0 | Recognition target (previously seen) |
| `RECOG_LURE` | 1 | Recognition lure (not previously seen) |

### Primary Task 2: Publisher-defined BIDS task: Ltp FR
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification *, tmax = Needs verification *, target_events = [Needs verification *]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004395 DOI: 10.18112/openneuro.ds004395.v2.0.0
- **Kernel Notes**: Verify epoch parameters and target_events mapping from events.tsv. BIDS task 'Ltp FR' corresponds to word encoding/free recall paradigm. Likely uses `WORD` (encoding) and `REC_WORD` (retrieval) events.

### Primary Task 3: Publisher-defined BIDS task: Ltp FR2
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification *, tmax = Needs verification *, target_events = [Needs verification *]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004395 DOI: 10.18112/openneuro.ds004395.v2.0.0
- **Kernel Notes**: Verify epoch parameters and target_events mapping from events.tsv. BIDS task 'Ltp FR2' likely uses similar events to Ltp FR but with different word lists/trials.

### Primary Task 4: Publisher-defined BIDS task: VFFR
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification *, tmax = Needs verification *, target_events = [Needs verification *]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004395 DOI: 10.18112/openneuro.ds004395.v2.0.0
- **Kernel Notes**: Verify epoch parameters and target_events mapping from events.tsv. VFFR likely uses voice-verified recall events (`REC_WORD_VV`).

## Data Quality Notes

- Very large dataset (300 subjects, 6480 files); processing time is substantial
- Session-level admin markers (SESS_START/END) must be excluded from epoching
- Multiple sub-tasks with different event structures; separate HDF5 per sub-task recommended

