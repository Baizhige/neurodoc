# High-Density Resting-State EEG of Phantom Limb Pain and Controls

**Dataset**: `openneuro_ds006921` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006921
**Category**: Biological State | **Subjects**: 152 | **Files (Completed)**: 152 | **Channels**: 128 | **Sampling Rate**: 2400 Hz | **Manual Review**:

## Paradigm

High-density resting-state EEG recordings were collected from three groups: amputees with phantom limb pain (PLP), amputees without phantom limb pain, and healthy controls. Recordings were made during eyes-open and eyes-closed conditions. The dataset enables investigation of neural correlates associated with phantom limb pain, cortical reorganization following amputation, and resting-state oscillatory differences across groups.

## File Scan Result

> **Kernel SHA256**: `N/A`
> **EEGUnity Version**: `N/A`
> **Scan Type**: Full

### Event Structure

_No event markers detected (`no_events`). This dataset contains continuous resting-state EEG recordings without trial-level annotations._


| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Resting-state group classification (PLP vs non-PLP vs controls)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `AmpPLP` | 0 | Amputee with phantom limb pain |
  | `AmpNoPLP` | 1 | Amputee without phantom limb pain |
  | `IC` | 2 | Intact healthy control |
- **Super Meta Notes**: Derived from participants.tsv metadata (group column). Kernel step: Load participants.tsv, extract group label (AmpPLP/AmpNoPLP/IC) for each subject, merge with segmented epochs. Eyes-open and eyes-closed condition labels may be added as additional features or separate classification task.
- **Evidence**:
  - DOI: 10.21203/rs.3.rs-8645281.v1 — Pre-registered study analyzing high-density resting-state EEG from openneuro_ds006921 to compare theta power and peak alpha frequency between amputees with phantom limb pain, amputees without pain, and healthy controls using mixed-effects models.
- **Kernel Notes**: 1) Segment continuous EEG into 5-second windows with 50% overlap. 2) Load participants.tsv to obtain group labels per subject. 3) Map group labels to epochs (same label for all epochs from same subject). 4) High sampling rate (2400 Hz); consider downsampling to 500-1000 Hz before feature extraction.

### Classical Task 2: Resting-state condition classification (eyes-open vs eyes-closed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `eyes-open` | 0 | Eyes-open resting condition |
  | `eyes-closed` | 1 | Eyes-closed resting condition |
- **Super Meta Notes**: Derived from BIDS task labels in filenames or metadata. Kernel step: Parse file/session identifiers to determine eyes-open vs eyes-closed condition for each recording, apply to all epochs from that recording.
- **Evidence**:
  - DOI: 10.21203/rs.3.rs-8645281.v1 — Uses both eyes-open and eyes-closed conditions in analysis; reports separate analyses for each condition.
- **Kernel Notes**: Requires metadata to distinguish eyes-open vs eyes-closed recordings. If unavailable, treat as single resting-state condition.

### Potential Task 1: Resting-State Segmentation (segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `event`
- **Target Definition**: N/A (no event markers; group labels from participants.tsv)
- **Notes**: No trial-level events. Group labels (PLP amputee / non-PLP amputee / healthy control) must be derived from participants.tsv metadata. Very high sampling rate (2400 Hz); downsample before analysis.

## Data Quality Notes

- Very high sampling rate (2400 Hz); downsample to 500-1000 Hz for most analyses.
- 152 files may include multiple sessions per subject; verify session structure.
- High-density 128-channel system (likely EGI/Geodesic); non-standard montage.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: failed
