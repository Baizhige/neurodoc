# Resting EEG with Structural MRI

**Dataset**: `openneuro_ds006525` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006525
**Category**: Biological State | **Subjects**: 34 | **Files (Completed)**: 34 | **Channels**: 128 | **Sampling Rate**: 250 Hz | **Manual Review**: Pending

## Paradigm

Spontaneous brain activity was recorded during resting-state EEG from 34 participants, supplemented by structural MRI scans. The dataset captures baseline neural dynamics in the absence of any task, with high-density 128-channel EEG acquisition at 250 Hz. Event markers include resting-state block onset (`rsts`), offset (`rstf`), and a session-begin marker (`bgin`), enabling segmentation of clean resting periods for downstream analysis.

## File Scan Result

> **Kernel SHA256**: `6f1dabb43d92702a7fcea0eeded397c95e5f3f452481e1eb98bd99591eddb9e6`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `DIN` | 34 | event | raw | Digital input trigger |
| `NRST` | 1232 | event | raw | Non-resting state marker |
| `bgin` | 19202 | event | raw | Session begin marker |
| `event-6` | 1200 | event | raw | Unclassified trigger event |
| `rstf` | 19202 | event | raw | Resting-state block finish/end |
| `rsts` | 34 | event | raw | Resting-state block start |


### MISC Label Summary
*(No misc channels present in this dataset)*
### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Potential Task 1: Resting-State Brain State Discovery (cCAP Clustering)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 1.0 s, overlap = 0.0 s
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | cCAP1 | 0 | Cluster 1 - co-activation pattern |
  | cCAP2 | 1 | Cluster 2 - co-activation pattern |
  | cCAP3 | 2 | Cluster 3 - co-activation pattern |
  | cCAP4 | 3 | Cluster 4 - co-activation pattern |
  | cCAP5 | 4 | Cluster 5 - co-activation pattern |
  | cCAP6 | 5 | Cluster 6 - co-activation pattern |
  | cCAP7 | 6 | Cluster 7 - co-activation pattern |
  | cCAP8 | 7 | Cluster 8 - co-activation pattern |
- **Super Meta Notes**: Cluster labels (cCAP1-cCAP8) are derived post-hoc from raw EEG signals by ICA decomposition followed by K-means clustering on time-frequency features of 1-s epochs; each epoch receives a cCAP cluster label representing a distinct brain state. Kernel step: Extract ICA components, compute time-frequency power features per epoch, run K-means (k=8), assign cluster labels as epoch annotations.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.119461 — Uses ICA and K-means clustering on resting-state EEG (34 participants) to identify 8 component-based co-activation patterns (cCAPs) representing recurring brain states and their dynamic transitions
  - DOI: 10.1016/j.neuroimage.2025.121408 — Identifies transient co-activation patterns (CAPs) via K-means clustering on alpha-band (8-12 Hz) instantaneous amplitude data from resting-state EEG
- **Kernel Notes**: Segment continuous EEG into 1-s non-overlapping epochs; apply ICA (e.g., FastICA with n_components=20-30) to decompose signals; extract time-frequency features (power in delta/theta/alpha/beta/gamma bands) from ICs; run K-means (k=8) on standardized feature vectors; assign cluster labels (cCAP1-cCAP8) as epoch annotations. Expect class imbalance across clusters; consider silhouette scoring for cluster quality assessment. High channel count (128ch) at 250 Hz—use channel subset (e.g., 64ch) or dimensionality reduction for computational efficiency.

---

### Potential Task 2: Resting-State Segmentation (Long Event Boundaries)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `rsts` | 0 | Resting-state block start |
  | `rstf` | 1 | Resting-state block end |
  | `NRST` | 2 | Non-resting state period |
  | `DIN` | 3 | Digital input trigger |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2025.121408 — Uses resting-state block markers (rsts/rstf) to define boundaries for CAP analysis, applying sliding windows within these boundaries
- **Kernel Notes**: Use `rsts` and `rstf` markers to define resting-state block boundaries; extract epochs within these boundaries only using 2-s sliding windows with 50% overlap to capture transient CAP transitions. Exclude `NRST` periods (y=2) from resting-state analyses—these periods are labeled but not included in the resting-state target set. Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation. 34 resting blocks total (one per subject), with 19202 end markers indicating multiple start-stop cycles per session.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
