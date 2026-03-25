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

### Primary Task 1: THINGS-EEG Object Concept Classification (1,854 concepts)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0–1853 | RSVP image onset (1,854 object concept classes derived from stimulus design files) |
- **Super Meta Notes**: Raw events (E1/E2/E3) mark stimulus timing. The actual class labels (which of 1,854 object concepts or which of 200 validation images) are derived from the experimental design/stimulus order files, not from the event markers themselves. The paper performs pairwise classification decoding between images and concepts.
- **Evidence**:
  - DOI: 10.1038/s41597.021.01102.7 — The paper presents THINGS-EEG dataset of EEG responses to 22,248 images from 1,854 object concepts presented in RSVP streams at 10Hz, with epochs extracted from -100 to 1000ms relative to stimulus onset, and performs pairwise classification decoding between images and concepts.
- **Kernel Notes**: Must load stimulus design files to map each trial to its object concept label (1,854 classes). Consider pairwise classification or subset selection due to large number of classes.

### Primary Task 2: RSVP Event Type Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`E 1`, `E 2`, `E 3`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `E 1` | 0 | RSVP image onset (primary stimulus stream) |
  | `E 2` | 1 | Secondary condition marker / stimulus offset |
  | `E 3` | 2 | Sequence boundary / target event |
- **Evidence**:
  - DOI: 10.1038/s41597.021.01102-7 — The paper describes creating epochs from -100 to 1000 ms relative to stimulus onset (E1 triggers) and using linear discriminant classifiers to decode between 1,854 object concepts and 200 validation images presented in RSVP streams at 10 Hz.
- **Kernel Notes**: E3 events are rare (~84 per subject) compared to E1/E2 (~22,248 each). May require class balancing.

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
