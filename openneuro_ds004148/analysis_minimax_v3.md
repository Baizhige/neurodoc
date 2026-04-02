# A test-retest resting and cognitive state EEG dataset

**Dataset**: `openneuro_ds004148` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004148
**Category**: High-level Mental | **Subjects**: 60 | **Files (Completed)**: 1797 | **Channels**: 61 | **Sampling Rate**: 500 Hz

## Paradigm

A test-retest reliability study recording EEG during five cognitive/resting conditions: eyes closed (EC), eyes open (EO), mental arithmetic (Ma), memory task (Me), and music listening (Mu), repeated across three sessions. Each file corresponds to one 5-minute condition block, with a single condition marker embedded (S 33=EO, S 44=EC, S 55=Mu, S 66=Me, S 77=Ma). Subjects are healthy adults aged 18-45.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004148

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S 44` | 360 | long | raw | Eyes-closed resting state block label |
| `S 77` | 360 | long | raw | Mental arithmetic task block label |
| `S 66` | 360 | long | raw | Memory task block label |
| `S 55` | 360 | long | raw | Music listening block label |
| `S 33` | 357 | long | raw | Eyes-open resting state block label |
| `Sync Off` | ~270000 | admin | raw | Periodic sync signal (~150/file), not a trial event |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S 44`, `S 77`, `S 66`, `S 55`, `S 33`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Five-Class Mental State Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s, overlap = 0.0
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 33` | 0 | Eyes-open resting state |
  | `S 44` | 1 | Eyes-closed resting state |
  | `S 55` | 2 | Music listening |
  | `S 66` | 3 | Memory task |
  | `S 77` | 4 | Mental arithmetic (subtraction) |
- **Evidence**:
  - DOI: 10.1038/s41597-022-01607-9 — Paper presents the openneuro_ds004148 dataset and describes decoding five EEG mental states (eyes-open, eyes-closed, memory, music, subtraction) using 5-min state blocks segmented into 4-s epochs with Welch method (4s window, no overlap).
- **Kernel Notes**: Segment continuous 5-min recordings into 4-s non-overlapping windows; extract spectral features (power spectrum, functional connectivity, microstates); train classifier to predict one of five mental states.

### Primary Task 2: Sex Classification from Resting-State EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 0.0 *
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `S 33` | 0 | Eyes-open resting state (male) |
  | `S 33` | 1 | Eyes-open resting state (female) |
  | `S 44` | 0 | Eyes-closed resting state (male) |
  | `S 44` | 1 | Eyes-closed resting state (female) |
- **Super Meta Notes**: Derived from raw events [`S 33`, `S 44`] by computing power spectral density (PSD) using multi-taper method in delta, theta, alpha, beta bands, then deriving relative power normalized by total power (3-30 Hz). Kernel step: Extract PSD features per epoch, normalize to relative power, train classifier on demographic sex labels.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2025.121231 — Paper uses openneuro_ds004148 (Southwest University EEG dataset) to investigate age-dependent sex differences in low alpha and low beta EEG oscillations, analyzing spectral power in eyes-open and eyes-closed resting states.
- **Kernel Notes**: Segment EC/EO recordings into 4-s epochs; compute PSD using multi-taper method; calculate relative power per band; train binary sex classifier. Note: Sex labels obtained from demographic data, not from event markers.

### Normal Task 1: Cognitive State Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Each file contains exactly one condition marker; 1797 files x ~150s each. Sync Off is a periodic synchronization signal (150 per file), excluded.

 | Event | y | Meaning |
 |-------|---|---------|
 | `S 33` | 0 | Eyes-open resting state |
 | `S 44` | 1 | Eyes-closed resting state |
 | `S 55` | 2 | Music listening |
 | `S 66` | 3 | Memory task |
 | `S 77` | 4 | Mental arithmetic |

## Data Quality Notes

- Sync Off at ~150 events/file is hardware sync, not a task event
- Three test-retest sessions allow reliability analyses

