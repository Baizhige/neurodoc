# Resting-State EEG Before and After Different Study Methods

**Dataset**: `openneuro_ds006801` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006801
**Category**: Biological State | **Subjects**: 21 | **Files (Completed)**: 42 | **Channels**: 31 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG was recorded before and after an educational intervention in which participants engaged in active retrieval practice, passive review, or a control condition. The design examines how different study strategies affect resting-state neural oscillations. Each participant completed eyes-open and eyes-closed resting blocks. The 42 files correspond to pre- and post-intervention recordings for 21 subjects.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006801

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/LostSamples` | 1 | admin | raw | Segment discontinuity marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Normal Task 1: Resting-State Segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.5 *
- **Label Route**: `Annotation`
- **Target Definition**: Labels must be derived from participants.tsv metadata (pre/post intervention, study condition, eyes-open/eyes-closed)
- **Notes**: The only raw event in this dataset is `New Segment/LostSamples`, which is an admin marker indicating signal discontinuity and should be excluded from analysis. This is a resting-state dataset where classification labels (e.g., pre-intervention vs. post-intervention, active retrieval vs. passive review vs. control) must be derived from the BIDS participants.tsv file rather than from EEG event markers.

## Data Quality Notes

- `New Segment/LostSamples` is a signal discontinuity marker - exclude from all analyses.
- 42 files = 21 subjects x 2 sessions (pre/post intervention).
- Eyes-open vs eyes-closed blocks may be distinguished by duration or metadata.

