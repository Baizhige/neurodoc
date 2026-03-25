# A Resource for Assessing Dynamic Binary Choices in the Adult Brain Using EEG and Mouse-Tracking

**Dataset**: `openneuro_ds003766` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds003766
**Category**: High-level Mental | **Subjects**: 31 | **Files (Completed)**: 217
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants performed dynamic decision-making tasks including food preference choices and semantic judgments while high-density EEG and continuous mouse-tracking were recorded simultaneously. The study captures the real-time neural dynamics of binary choice formation, including evidence accumulation, conflict, and response selection. Numeric trigger codes (0200-0506 series) encode stimulus, response, and condition information. Boundary markers appear in some files from EEGLAB preprocessing.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003766

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0400` | 186 | short | raw | Trigger code 0400 (stimulus/task event - decode from events.tsv) |
| `0500` | 186 | short | raw | Trigger code 0500 (stimulus/task event - decode from events.tsv) |
| `0401`-`0403` | 124 each | short | raw | Stimulus variant trigger codes |
| `0503`, `0505`, `0506` | 124 each | short | raw | Response/outcome trigger codes |
| `0501` | 95 | short | raw | Trigger code 0501 |
| `0202`-`0221` | 93 each | short | raw | Trial-phase trigger codes (0200 series) |
| `0210` | 93 | short | raw | Trigger code 0210 |
| `boundary` | 97 | admin | raw | EEGLAB boundary marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Foodchoice
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003766 DOI: https://doi.org/10.18112/openneuro.ds003766.v2.0.3


### Primary Task 2: Publisher-defined BIDS task: Resting
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003766 DOI: https://doi.org/10.18112/openneuro.ds003766.v2.0.3


### Primary Task 3: Publisher-defined BIDS task: Imagechoice
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003766 DOI: https://doi.org/10.18112/openneuro.ds003766.v2.0.3


### Normal Task 1: Binary choice classification (need to decode event meaning)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric trigger codes must be decoded from events.tsv. The 0200-series codes likely encode trial-phase timing; 0400/0500-series likely encode stimulus presentation. 217 files across 31 subjects (~7 sessions each). `boundary` is an EEGLAB admin marker; exclude from epoching.

| Event | y | Meaning |
 |-------|---|------|
| `0400` | 0 | Stimulus/Option A (decode from events.tsv) |
| `0500` | 1 | Stimulus/Option B (decode from events.tsv) |
## Data Quality Notes

- 30+ distinct numeric event codes; decode mapping required from events.tsv or dataset paper.
- `boundary` events are EEGLAB data-continuity markers; must be excluded from epoching.
- High-density 129-channel EEG at 1000 Hz; high computational requirements.
- Multiple sessions per subject; verify session consistency before pooling.

## References

- **Reference**: `Chen, K., Wang, R., Huang, J., Gao, F., Yuan, Z., Qi, Y., & Wu, H. (2022). A resource for assessing dynamic binary choices in the adult brain using EEG and mouse-tracking. Scientific Data, 9(1), 416.`
