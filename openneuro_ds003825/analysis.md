# Human electroencephalography recordings from 50 subjects for 22,248 images from 1,854 object concepts

**Dataset**: `openneuro_ds003825` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003825
**Category**: Sensory/Response | **Subjects**: 50 | **Files (Completed)**: 100
**Channels**: 64 | **Sampling Rate**: 250 Hz

## Paradigm

Participants viewed a large-scale set of 22,248 images spanning 1,854 object concepts presented in rapid serial visual presentation (RSVP) streams at 10 Hz while performing a fixation color change detection task. The study aimed to record high-resolution neural representations of everyday objects across a large stimulus set. Each image was presented for 100 ms in continuous streams, and participants responded to a concurrent fixation task to maintain attention.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003825

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `E 1` | ~1,237,200 | short | raw | Image onset (RSVP stimulus) |
| `E 2` | ~1,237,200 | short | raw | Second trial-type marker (redundant or condition flag) |
| `E 3` | ~4,200 | short | raw | Block/sequence boundary or target event |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Rsvp
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003825 DOI: https://doi.org/10.1167/13.10.1


### Normal Task 1: RSVP Image Viewing (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Extremely large dataset (~1.2M epochs per event type across 50 subjects). E 1 and E 2 occur in equal counts per subject (~22,248 each); E 3 is rare (~84 per subject) and may indicate special events or fixation targets. Consider subsampling for practical use.

| Event | y | Meaning |
 |-------|---|------|
 | `E 1` | 0 | RSVP image onset (primary stimulus stream) |
 | `E 2` | 1 | Secondary condition marker |
## Data Quality Notes

- Data from derivatives/eeglab directory; preprocessed with EEGLAB
- Very high epoch count (~24,648 E 1 events per subject); memory management required during HDF5 generation
- Sub-06 has fewer events (~12,360), suggesting a partial recording

## References

- **Reference**: `Grootswagers, T., Zhou, I., Robinson, A.K. et al. Human EEG recordings for 1,854 concepts presented in rapid serial visual presentation streams. Sci Data 9, 3 (2022).`
