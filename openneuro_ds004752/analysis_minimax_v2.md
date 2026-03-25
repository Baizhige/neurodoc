# Dataset of Intracranial EEG, Scalp EEG and Beamforming Sources from Epilepsy Patients - Verbal Working Memory

**Dataset**: `openneuro_ds004752` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004752
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 136
**Channels**: 64 | **Sampling Rate**: 2000 Hz

## Paradigm

Epilepsy patients performed a modified Sternberg verbal working memory task consisting of encoding, maintenance, and recall phases while simultaneous scalp and intracranial EEG were recorded. The dataset includes iEEG from depth electrodes, scalp EEG, single-unit neuron spike times, and electrode localizations, enabling multi-level analysis of memory processes. No trial-level event annotations are available in the BIDS events.tsv.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004752

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| (no events) | - | - | raw | No event markers detected in events.tsv |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Normal Task 1: Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: None (no event tag)
- **Notes**: No trial-level events available in events.tsv. EEG is continuous during task performance. Use sliding-window segmentation. Trial timing may be available in accompanying behavioral logs not captured in BIDS events.tsv.


## Data Quality Notes

- No event markers - trial-epoch structure not available from events.tsv.
- Very high sampling rate (2000 Hz) - downsample before analysis.
- Epilepsy patients; ictal episodes should be identified and excluded.

## References

- **Reference**: `Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task. DOI: 10.1038/s41597-020-0364-3`
