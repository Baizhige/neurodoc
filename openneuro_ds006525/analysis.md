# Resting EEG with Structural MRI

**Dataset**: `openneuro_ds006525` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006525
**Category**: Biological State | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 128 | **Sampling Rate**: 250 Hz

## Paradigm

Spontaneous brain activity was recorded during resting-state EEG, supplemented by structural MRI scans. The dataset captures baseline neural dynamics in the absence of any task. Event markers include resting-state block onset (`rsts`), offset (`rstf`), and a session-begin marker (`bgin`), enabling segmentation of clean resting periods.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | 20400 | event | raw | Session begin marker |
| `rsts` | 20400 | event | raw | Resting-state block start |
| `rstf` | 34 | event | raw | Resting-state block finish/end |
| `NRST` | 34 | admin | raw | Non-resting state marker |
| `DIN` | 2 | admin | raw | Digital input trigger |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Resting-State Brain State Discovery (cCAP/CAP Clustering)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.0 s
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | cCAP1 | 0 | Cluster 1 - co-activation pattern |
  | cCAP2 | 1 | Cluster 2 - co-activation pattern |
  | cCAP3 | 2 | Cluster 3 - co-activation pattern |
  | cCAP4 | 3 | Cluster 4 - co-activation pattern |
  | cCAP5 | 4 | Cluster 5 - co-activation pattern |
  | cCAP6 | 5 | Cluster 6 - co-activation pattern |
  | cCAP7 | 6 | Cluster 7 - co-activation pattern |
  | cCAP8 | 7 | Cluster 8 - co-activation pattern |
- **Super Meta Notes**: Derived from raw EEG signals by ICA decomposition followed by K-means clustering (k=8) on time-frequency features of 1-s epochs; each epoch receives a cCAP cluster label representing a brain state. Kernel step: Extract ICA components, compute time-frequency power features per epoch, run K-means (k=8), assign cluster labels to epochs.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119461 — Analyzes resting-state EEG from 34 participants using ICA and K-means clustering to identify 8 component-based co-activation patterns (cCAPs) representing recurring brain states and their dynamic transitions
  - DOI: 10.1016/j.neuroimage.2025.121408 — Uses resting-state EEG from openneuro_ds006525 to identify transient co-activation patterns (CAPs) via K-means clustering on alpha-band (8-12 Hz) instantaneous amplitude data
- **Kernel Notes**: Segment continuous EEG into 1-s non-overlapping epochs; apply ICA (e.g., FastICA) to decompose signals; extract time-frequency features (power in delta/theta/alpha/beta/gamma bands) from ICs; run K-means (k=8) on feature vectors; assign cluster labels as epoch annotations. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: Resting-State Segmentation (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `rsts` and `rstf` mark the boundaries of resting blocks; segment within these boundaries. `NRST` may indicate periods outside resting state that should be excluded.

 | Event | y | Meaning |
 |-------|---|---------|
 | `bgin` | 0 | Session begin |
 | `rsts` | 1 | Resting-state block start |
 | `rstf` | 2 | Resting-state block end |
 | `NRST` | 3 | Non-resting state period |
 | `DIN` | 4 | Digital input trigger |

## Data Quality Notes

- High channel count (128) with 250 Hz sampling rate; EGI/Geodesic system likely.
- `NRST` may indicate periods outside resting state that should be excluded from analysis.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review