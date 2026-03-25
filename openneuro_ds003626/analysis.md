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
- **Epoch Method**: `epoch_by_segmentation_hdf5` (or `epoch_by_event_hdf5` when external timing is restored)
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation` or `misc`
- **Target Definition**: Directional command classes (Up/Down/Left/Right) across inner, pronounced, and visualization modalities.
- **Evidence**: Dataset documentation describes inner speech command paradigms for BCI-oriented decoding. Source: https://openneuro.org/datasets/ds003626 DOI: https://doi.org/10.1086/509092


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
