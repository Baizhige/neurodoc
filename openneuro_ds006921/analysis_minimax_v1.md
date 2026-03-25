# High-Density Resting-State EEG of Phantom Limb Pain and Controls

**Dataset**: `openneuro_ds006921` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006921
**Category**: Biological State | **Subjects**: 152 | **Files (Completed)**: 152 | **Channels**: 128 | **Sampling Rate**: 2400 Hz

## Paradigm

High-density resting-state EEG recordings were collected from three groups: amputees with phantom limb pain (PLP), amputees without phantom limb pain, and healthy controls. Recordings were made during eyes-open and eyes-closed conditions. The dataset enables investigation of neural correlates associated with phantom limb pain, cortical reorganization following amputation, and resting-state oscillatory differences across groups.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006921

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous resting-state EEG recordings without trial-level annotations._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Phantom Limb Pain Group Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 30 s, tmax = 390 s, overlap = 0.0 *, target_events = [`eyes-open`, `eyes-closed`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `IC` | 0 | Healthy intact control |
  | `AmpNoPLP` | 1 | Amputee without phantom limb pain |
  | `AmpPLP` | 2 | Amputee with phantom limb pain |
- **Super Meta Notes**: Group labels (IC/AmpNoPLP/AmpPLP) derived from participants.tsv metadata; each 7-min recording is treated as one long event per condition (eyes-open, eyes-closed); first/last 30s truncated per paper protocol; 5s epochs extracted from remaining 360s.
- **Evidence**:
  - DOI: 10.21203/rs.3.rs-8645281.v1 — Pre-registered study analyzing high-density resting-state EEG from openneuro_ds006921 comparing theta power and peak alpha frequency between amputees with phantom limb pain, amputees without pain, and healthy controls using mixed-effects models; uses 5s epochs from truncated (first/last 30s removed) 7-min recordings across eyes-open and eyes-closed conditions.
- **Kernel Notes**: Load participants.tsv to map subject IDs to group labels (IC/AmpNoPLP/AmpPLP). Truncate first and last 30s of each 7-min recording. Extract non-overlapping 5s epochs from the middle 360s segment. Assign epoch label based on subject's group. Downsample from 2400 Hz to 500-1000 Hz before feature extraction.

### Primary Task 2: Eyes-Open vs Eyes-Closed Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 30 s, tmax = 390 s, overlap = 0.0 *, target_events = [`eyes-open`, `eyes-closed`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `eyes-closed` | 0 | Eyes-closed resting condition |
  | `eyes-open` | 1 | Eyes-open resting condition |
- **Evidence**:
  - DOI: 10.21203/rs.3.rs-8645281.v1 — Study collects 7-min recordings under both eyes-open and eyes-closed conditions; first/last 30s truncated; 5s epochs used for analysis.
- **Kernel Notes**: Identify separate files for eyes-open and eyes-closed conditions from BIDS task labels. Apply same truncation (30s from start/end) and 5s epoching as group classification task. Label epochs by condition type.

### Normal Task 1: Resting-State Segmentation (segmentation)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no event markers; group labels from participants.tsv)
- **Notes**: No trial-level events. Group labels (PLP amputee / non-PLP amputee / healthy control) must be derived from participants.tsv metadata. Very high sampling rate (2400 Hz); downsample before analysis.

## Data Quality Notes

- Very high sampling rate (2400 Hz); downsample to 500-1000 Hz for most analyses.
- 152 files may include multiple sessions per subject; verify session structure.
- High-density 128-channel system (likely EGI/Geodesic); non-standard montage.

## References

- **Reference**: `High Density Resting State EEG of Phantom Limb Pain and Controls`
