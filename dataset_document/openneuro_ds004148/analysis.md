# A test-retest resting and cognitive state EEG dataset

**Dataset**: `openneuro_ds004148` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004148
**Category**: High-level Mental | **Subjects**: 60 | **Files (Completed)**: 1797 | **Channels**: 61 | **Sampling Rate**: 500 Hz | **Manual Review**: Pending

## Paradigm

A test-retest reliability study recording EEG during five cognitive/resting conditions: eyes closed (EC), eyes open (EO), mental arithmetic (Ma), memory task (Me), and music listening (Mu), repeated across three sessions. Each file corresponds to one 5-minute condition block, with a single condition marker embedded (S 33=EO, S 44=EC, S 55=Mu, S 66=Me, S 77=Ma). Subjects are healthy adults aged 18-45.

## File Scan Result

> **Kernel SHA256**: `dcafdcd15ba238c47ca2ab5180bba52f331198a9be7d52d1c07b24a878f15523`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 33` | 177 | event | raw | Eyes-open resting state block label |
| `S 44` | 180 | event | raw | Eyes-closed resting state block label |
| `S 55` | 180 | event | raw | Music listening block label |
| `S 66` | 180 | event | raw | Memory task block label |
| `S 77` | 180 | event | raw | Mental arithmetic task block label |
| `admin: marker-Stimulus/S 33` | 180 | event | raw | Stimulus marker for eyes-open condition |
| `admin: marker-Stimulus/S 44` | 180 | event | raw | Stimulus marker for eyes-closed condition |
| `admin: marker-Stimulus/S 55` | 180 | event | raw | Stimulus marker for music listening condition |
| `admin: marker-Stimulus/S 66` | 180 | event | raw | Stimulus marker for memory task condition |
| `admin: marker-Stimulus/S 77` | 180 | event | raw | Stimulus marker for mental arithmetic condition |
| `admin: marker-Sync Off` | 750 | event | raw | Periodic sync signal marker (administrative) |
| `admin: marker-SyncStatus/Sync Off` | 750 | event | raw | Sync status marker (administrative) |


### MISC Label Summary
(No misc channels present in this dataset)
### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Five-Class Mental State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `S 33` | 0 | Eyes-open resting state |
  | `S 44` | 1 | Eyes-closed resting state |
  | `S 55` | 2 | Music listening |
  | `S 66` | 3 | Memory task |
  | `S 77` | 4 | Mental arithmetic (subtraction) |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01607-9 — Paper presents the openneuro_ds004148 dataset and describes decoding five EEG mental states (eyes-open, eyes-closed, memory, music, subtraction) using 5-min state blocks segmented into 4-s epochs with Welch method.
- **Kernel Notes**: Segment continuous 5-min recordings into 4-s non-overlapping windows; extract spectral features (power spectrum, functional connectivity, microstates); train classifier to predict one of five mental states.

### Classical Task 2: Mental Arithmetic vs. Other States Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `S 33` | 0 | Eyes-open resting state |
  | `S 44` | 0 | Eyes-closed resting state |
  | `S 55` | 0 | Music listening |
  | `S 66` | 0 | Memory task |
  | `S 77` | 1 | Mental arithmetic (subtraction) |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01607-9 — Same dataset paper explicitly identifies mental arithmetic (subtraction) as a distinct cognitive state for decoding analysis.
- **Kernel Notes**: Focus binary classification on isolating mental arithmetic (S 77) from all other four states (resting, music, memory). Segment recordings into 4-s epochs; extract spectral features; discriminate arithmetic vs. non-arithmetic mental states.

### Potential Task 1: Fine-Grained Temporal Cognitive State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `S 33` | 0 | Eyes-open resting state |
  | `S 44` | 1 | Eyes-closed resting state |
  | `S 55` | 2 | Music listening |
  | `S 66` | 3 | Memory task |
  | `S 77` | 4 | Mental arithmetic |
- **Evidence**: Plausible from paradigm design. Alternative overlapping window approach for temporal analysis within continuous 5-min blocks. Excludes Sync Off events (~150/file admin markers).
- **Kernel Notes**: Use 2-s sliding windows with 50% overlap to capture transient dynamics within block; aggregate per condition; train classifier.

### Normal Task 1: Resting-State Classification (Eyes-Open vs. Eyes-Closed)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|--------|
  | `S 33` | 0 | Eyes-open resting state |
  | `S 44` | 1 | Eyes-closed resting state |
- **Evidence**: Paradigm provides EC/EO as standard rest conditions; supported by the dataset paper (DOI: 10.1038/s41597-022-01607-9) but not specifically highlighted for binary rest classification.
- **Kernel Notes**: Focus on discriminating EC vs EO only; segment into 4-s epochs; extract alpha power (expected higher in EC) and other spectral features.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review
