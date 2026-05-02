# Fatigue Characterization of EEG under Mixed Reality Stereo Vision

**Dataset**: `openneuro_ds005416` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005416
**Category**: Complex Applied | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 64 | **Sampling Rate**: 1000 Hz | **Manual Review**: Pending

## Paradigm

Participants viewed resting and movement scenes in a Mixed Reality (MR) stereo vision environment to characterize EEG-based fatigue during periodic visual depth and velocity changes. The study investigates neural correlates of visual fatigue induced by MR headset viewing under different dynamic visual conditions. No trial events were captured in events.tsv; data is continuous.

## File Scan Result

> **Kernel SHA256**: `4413fa79df8b82d3f35ee2b20b9e7e6c8a8ab59438e05322163058428bf672e3`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|



### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Fatigue State Classification (EEG Brain Networks)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| subjective_rating | comfort | Comfort state (ratings: normal/relaxed on 5-point scale) |
| subjective_rating | fatigue | Fatigue state (ratings: mild/moderate/severe on 5-point scale) |

- **Notes**: Continuous EEG segmented into sliding windows. Labels derived from per-subject, per-scene subjective ratings (5-point ordinal scales for fatigue level and comfort level). Binary classification: comfort state vs fatigue state. Analysis focuses on brain network connectivity features (PLV, betweenness centrality, clustering coefficient, node efficiency, characteristic path length) in delta (0.5–4 Hz), theta (4–8 Hz), alpha (8–13 Hz) bands.

### Potential Task 1: MR Fatigue Condition Blocks (Sustained States)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = 300.0, overlap = null
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:

| Event | y | Meaning |
|---|---|---|
| 11 | condition_block | Block onset (23 per dataset, 1 per subject) — likely resting scene condition |
| 12 | trial | Trial marker (345 total, ~15 per subject) — visual depth/velocity change events during MR viewing |
| 13 | condition_block | Block onset (23 per dataset, 1 per subject) — likely movement scene condition |

- **Notes**: Events 11 and 13 occur once per subject, indicating sustained condition blocks. Epoch as long events to capture sustained fatigue-related neural changes across MR viewing periods. Events 21 and 23 (single occurrence) are recording metadata markers (task start/end). Labels from subjective ratings mapped to comfort/fatigue states at condition-block level.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
