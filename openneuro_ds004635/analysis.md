# Gaffrey Lab Infant EEG Microstates Reliability

**Dataset**: `openneuro_ds004635` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004635
**Category**: Biological State | **Subjects**: 48 | **Files (Completed)**: 1
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Infants watched a series of engaging and relaxing videos to facilitate recording of spontaneous EEG activity. The dataset was collected to assess the test-retest reliability of EEG microstate metrics in infants. The single aggregated file contains data from 48 infants with recording-boundary markers; no active task was required.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | 10 | event | raw | Beginning of a recording segment |
| `TRSP` | 10 | event | raw | Transition / segment boundary marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: EEG Microstate Segmentation
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1 s *, overlap = 0.0 *
- **Label Route**: `event`
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

### Potential Task 1: Recording Segment Boundary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 *, target_events = [`bgin`, `TRSP`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `bgin` | 0 | Recording segment start marker |
  | `TRSP` | 1 | Transition segment boundary marker |
- **Notes**: Only 10 events of each type - very limited for supervised classification. Primary scientific use is resting-state microstate analysis (Classical Task 1). Single aggregated file covers all 48 infants.

## Data Quality Notes

- Single file aggregating 48 infants - individual subject effects not separable.
- Only 10 events of each type; insufficient for robust supervised classification.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review