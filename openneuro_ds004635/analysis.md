# Gaffrey Lab Infant EEG Microstates Reliability

**Dataset**: `openneuro_ds004635` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004635
**Category**: Biological State | **Subjects**: 48 | **Files (Completed)**: 1 | **Channels**: 129 | **Sampling Rate**: 1000 Hz
**Manual Review**: Pending

## Paradigm

Infants watched a series of engaging and relaxing videos to facilitate recording of spontaneous EEG activity. The dataset was collected to assess the test-retest reliability of EEG microstate metrics in infants. The single aggregated file contains data from 48 infants with recording-boundary markers; no active task was required.

## File Scan Result

> **Kernel SHA256**: `da76bf1dea148211b5bb5f4f4351365f9d418b0d2b8fe7eec9da9ffdeed80e30`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `TRSP` | 10 | event | raw | Transition / segment boundary marker |
| `bgin` | 10 | event | raw | Beginning of a recording segment |


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
- **Epoch Parameters**: segment_length = 1 s, overlap = 0.0
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
- **Evidence**:
  - DOI: 10.1007/s10548-024-01043-5 — Published tutorial in Brain Topography (2024) using the same 48-infant dataset; provides step-by-step microstate analysis workflow with 5 canonical classes, temporal metrics (GEV, duration, coverage, occurrence, transition probabilities), and reliability assessment.
  - DOI: 10.21203/rs.3.rs-3164735.v1 — Preprint version (July 2023) with identical methodology; identifies 5 microstate classes during video-watching resting-state and assesses test-retest reliability across infants.
- **Kernel Notes**: Segment continuous EEG into 1-second non-overlapping windows. Compute Global Field Power (GFP) for each segment and identify GFP peaks. Apply modified k-means clustering to identify 5 canonical topographic patterns (labels 0-4). Assign each 1-second segment to its dominant microstate class based on GFP-peak topographic similarity. Extract microstate metrics: Global Explained Variance (GEV), duration, coverage, occurrence, and transition probabilities for downstream reliability analysis. Boundary events (`bgin`, `TRSP`) mark recording segment transitions for quality checks but are not used as classification labels. Note: single aggregated file prevents subject-level separation; class imbalance potential if microstate distribution is uneven.

### Potential Task 1: Recording Segment Boundary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`bgin`, `TRSP`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `bgin` | 0 | Recording segment start marker |
  | `TRSP` | 1 | Transition segment boundary marker |
- **Evidence**: None — task is plausible from paradigm but insufficient events for robust supervised learning.
- **Kernel Notes**: Only 10 events of each type exist—severely limited for supervised classification. Primary scientific value lies in microstate analysis (Classical Task 1). This task remains Potential only for completeness; `bgin` and `TRSP` events serve as quality-check markers rather than discriminative targets.