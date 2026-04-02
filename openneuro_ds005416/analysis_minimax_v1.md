# Fatigue Characterization of EEG under Mixed Reality Stereo Vision

**Dataset**: `openneuro_ds005416` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005416
**Category**: Complex Applied | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 64 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants viewed resting and movement scenes in a Mixed Reality (MR) stereo vision environment to characterize EEG-based fatigue during periodic visual depth and velocity changes. The study investigates neural correlates of visual fatigue induced by MR headset viewing under different dynamic visual conditions. No trial events were captured in events.tsv; data is continuous.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005416

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: EEG-based Fatigue Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|-|
  | `comfort` | 0 | Pre-watching relaxation period (first 5 min) |
  | `fatigue` | 1 | Post-watching after 15 blocks of MR content |
- **Super Meta Notes**: Labels are derived from temporal position in the recording: the first 5 minutes (relax scene before MR viewing) are labeled as 'comfort', and segments after the 15 blocks of MR content are labeled as 'fatigue'. Not from raw event markers; labels computed based on experiment timing.
- **Evidence**:
  - DOI: 10.3390/brainsci14111126 — This paper analyzes EEG data from 18 participants viewing MR stereo vision content to compare brain network topological properties between comfort and fatigue states using 2-second epochs segmented from continuous recordings.
- **Kernel Notes**: Segment continuous EEG into non-overlapping 2-second windows. Assign labels based on window timing: windows in first 5 min = comfort (y=0), windows after 15 blocks = fatigue (y=1). Exclude transition periods between conditions.

### Normal Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None
- **Notes**: No event markers in events.tsv. EEG is continuous during MR viewing task. Use sliding-window segmentation. Condition labels (fatigue level, visual condition) may be available from session metadata.

## Data Quality Notes

- No event markers; continuous EEG during MR task.
- High sampling rate (1000 Hz) adequate for spectral fatigue analysis.
- MR headset may introduce electrical interference artifacts.

## References

- **Reference**: `Fatigue Characterization of EEG under Mixed Reality Stereo Vision`
