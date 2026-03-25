# Resting EEG with Structural MRI

**Dataset**: `openneuro_ds006525` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006525
**Category**: Biological State | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 128 | **Sampling Rate**: 250 Hz

## Paradigm

Spontaneous brain activity was recorded during resting-state EEG, supplemented by structural MRI scans. The dataset captures baseline neural dynamics in the absence of any task. Event markers include resting-state block onset (`rsts`), offset (`rstf`), and a session-begin marker (`bgin`), enabling segmentation of clean resting periods.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006525

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `bgin` | 20400 | long | raw | Session begin marker |
| `rsts` | 20400 | rest | raw | Resting-state block start |
| `rstf` | 34 | rest | raw | Resting-state block finish/end |
| `NRST` | 34 | admin | raw | Non-resting state marker |
| `DIN` | 2 | admin | raw | Digital input trigger |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Resting-state co-activation pattern (cCAP) segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.0 s
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | cCAP_1 | 0 | Cluster 1: co-activation pattern 1 |
  | cCAP_2 | 1 | Cluster 2: co-activation pattern 2 |
  | cCAP_3 | 2 | Cluster 3: co-activation pattern 3 |
  | cCAP_4 | 3 | Cluster 4: co-activation pattern 4 |
  | cCAP_5 | 4 | Cluster 5: co-activation pattern 5 |
  | cCAP_6 | 5 | Cluster 6: co-activation pattern 6 |
  | cCAP_7 | 6 | Cluster 7: co-activation pattern 7 |
  | cCAP_8 | 7 | Cluster 8: co-activation pattern 8 |
- **Super Meta Notes**: Labels derived via K-means clustering (k=8) on ICA components or alpha-band (8-12 Hz) instantaneous amplitude features extracted from continuous EEG. Each 1-s epoch is assigned to one of 8 cCAP clusters representing recurring brain states.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119461 — Analyzes resting-state EEG from 34 participants using ICA and K-means clustering to identify 8 component-based co-activation patterns (cCAPs) representing recurring brain states and their dynamic transitions
  - DOI: 10.1016/j.neuroimage.2025.121408 — Uses resting-state EEG data from openneuro_ds006525 (34 participants) to identify transient co-activation patterns (CAPs) via K-means clustering on alpha-band (8-12 Hz) instantaneous amplitude data, comparing human EEG CAPs to monkey ECoG CAPs
- **Kernel Notes**: (1) Extract continuous EEG from 10-min resting-state recording; (2) Apply ICA decomposition to isolate independent components; (3) Compute time-frequency features (alpha-band instantaneous amplitude via Hilbert transform) for each component; (4) Apply K-means clustering (k=8) to identify 8 cCAP clusters; (5) Assign each 1-s segment a cluster label (0-7) and write to Annotation channel.

### Normal Task 1: Resting-State Segmentation (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `Resting EEG`
