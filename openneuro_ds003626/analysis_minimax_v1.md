# Inner Speech

**Dataset**: `openneuro_ds003626` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003626
**Category**: High-level Mental | **Subjects**: 10 | **Files (Completed)**: 30
**Channels**: 137 | **Sampling Rate**: 1024 Hz

## Paradigm

Participants performed inner speech (imagined speech), pronounced speech, and visualization tasks involving four directional commands (Up, Down, Right, Left) to explore the neural correlates of the 'inner voice' phenomenon for potential BCI applications. High-density EEG (137 channels) was recorded during all three modalities of speech production/imagery. No discrete event markers were captured in the EEG trigger channel; paradigm timing is encoded externally.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003626

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG recording |

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

### Primary Task 1: Inner speech command decoding
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 4.0 s *, target_events = [`Up`, `Down`, `Left`, `Right`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Up` | 0 | Imagined/pronounced/visualized upward directional command |
  | `Down` | 1 | Imagined/pronounced/visualized downward directional command |
  | `Left` | 2 | Imagined/pronounced/visualized left directional command |
  | `Right` | 3 | Imagined/pronounced/visualized right directional command |
- **Super Meta Notes**: No EEG trigger markers present in recordings. Events must be reconstructed from experimental protocol timing in events.tsv. The dataset contains three modalities (inner speech, pronounced speech, visualization) which can be encoded as separate classification problems or combined for a 12-class (4 directions × 3 modalities) task.
- **Evidence**:
  - DOI: https://doi.org/10.1038/s41597-022-01536-7 — Scientific data paper describing the Inner Speech Dataset with high-density EEG for classifying directional commands (Up/Down/Left/Right) across inner speech, pronounced speech, and visualization modalities for BCI applications.
- **Kernel Notes**: Must parse events.tsv to recover trial onsets and assign labels. If events.tsv contains modality information (inner/pronounced/visualization), kernel should create separate label columns or encode as multi-class labels. Verify tmin/tmax from original paradigm timing if available; defaults marked with * may need adjustment.

### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `stim`
- **Target Definition**: N/A (null (no tag, needs to be restored from events.tsv or external annotation))
- **Notes**: No EEG trigger markers detected. If events.tsv contains trial onset annotations, epoching by event may be possible. High-density 137-channel EEG suitable for source imaging of inner speech networks. Only 10 subjects.

## Data Quality Notes

- No EEG trigger markers present; trial timing must be reconstructed from events.tsv or behavioral logs.
- Small sample size (10 subjects, 30 files across 3 conditions).
- High-density 137-channel EEG; requires careful re-referencing and ICA for artifact removal.

## References

- **Reference**: `Inner Speech Dataset. OpenNeuro ds003626.`
