# Gaffrey Lab Infant EEG Microstates Reliability

**Dataset**: `openneuro_ds004635` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004635
**Category**: Biological State | **Subjects**: 48 | **Files (Completed)**: 1
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Infants watched a series of engaging and relaxing videos to facilitate recording of spontaneous EEG activity. The dataset was collected to assess the test-retest reliability of EEG microstate metrics in infants. The single aggregated file contains data from 48 infants with recording-boundary markers; no active task was required.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004635

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | 10 | long | raw | Beginning of a recording segment |
| `TRSP` | 10 | long | raw | Transition / segment boundary marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: EEG Microstate Segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1 s *, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `microstate 1` | 0 | First canonical topographic pattern identified by modified k-means clustering |
  | `microstate 2` | 1 | Second canonical topographic pattern identified by modified k-means clustering |
  | `microstate 3` | 2 | Third canonical topographic pattern identified by modified k-means clustering |
  | `microstate 4` | 3 | Fourth canonical topographic pattern identified by modified k-means clustering |
  | `microstate 5` | 4 | Fifth canonical topographic pattern identified by modified k-means clustering |
- **Super Meta Notes**: Derived from raw EEG signal by segmentation into 1-second epochs followed by modified k-means clustering at GFP peaks. Kernel step: Perform microstate segmentation using EEGLAB or equivalent toolbox, extract temporal properties (GEV, duration, coverage, occurrence) and transition probabilities for each microstate class. Raw boundary markers [`bgin`, `TRSP`] indicate recording segment boundaries but are not used as classification labels.
- **Evidence**:
  - DOI: 10.21203/rs.3.rs-3164735.v1 — This paper uses OpenNeuro ds004635 dataset to perform EEG microstate analysis on 55 infants during video-watching resting-state, identifying 5 microstates and assessing their psychometric reliability (stability across data durations and internal consistency via split-half reliability).
- **Kernel Notes**: Segment continuous EEG into 1-second windows, compute Global Field Power (GFP), identify GFP peaks, apply modified k-means clustering to identify 5 microstate classes. Assign each 1-second segment to a microstate label (0-4). Kernel should also compute microstate metrics (GEV, duration, coverage, occurrence, transition probabilities) for downstream reliability analysis.

### Normal Task 1: Recording Segment Boundary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 *, target_events = [`bgin`, `TRSP`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `bgin` | 0 | Recording segment start marker |
  | `TRSP` | 1 | Transition segment boundary marker |
- **Notes**: Only 10 events of each type - very limited for supervised classification. Primary scientific use is resting-state microstate analysis (Primary Task 1). Single aggregated file covers all 48 infants.

## Data Quality Notes

- Single file aggregating 48 infants - individual subject effects not separable.
- Only 10 events of each type; insufficient for robust supervised classification.

