# EEG recordings for 200 object images presented in RSVP sequences at 5Hz or 20Hz

**Dataset**: `openneuro_ds004018` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004018
**Category**: Sensory/Response | **Subjects**: 2 | **Files (Completed)**: 2
**Channels**: 63 | **Sampling Rate**: 1000 Hz

## Paradigm

Rapid Serial Visual Presentation (RSVP) of 200 object images at two presentation frequencies (5 Hz and 20 Hz) to investigate the temporal dynamics of visual object representations. Images were categorized as "stars" or "boats" (two superordinate categories), allowing investigation of how presentation rate affects category-level neural decoding. This is a very small dataset (2 subjects).

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004018

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stars` | 2 files | short | raw | RSVP onset - star/celestial category image |
| `boats` | 2 files | short | raw | RSVP onset - boat/vehicle category image |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## Tasks

### Primary Task 1: RSVP Object Category Classification (stars vs boats)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 1.0 s *, target_events = [`stars`, `boats`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stars` | 0 | Star/celestial category RSVP image onset |
  | `boats` | 1 | Boat/vehicle category RSVP image onset |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2018.12.046 — Original RSVP study with 200 object images at 5Hz and 20Hz, multi-class category decoding using LDA classifiers on epochs from -100 to 1000ms
- **Kernel Notes**: Extract epochs aligned to `stars` and `boats` onset markers. The paper demonstrates animacy (animate vs inanimate) and superordinate category decoding (e.g., mammals, tools, vehicles). The raw events `stars` and `boats` correspond to celestial vs vehicle superordinate categories. Verify that presentation frequency (5Hz vs 20Hz) is encoded in a separate metadata field or derive from inter-stimulus intervals. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: RSVP Target vs Distractor Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s *, tmax = 2.0 s *, target_events = [`stars`, `boats`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | target | 1 | Target stimulus in RSVP stream |
  | distractor | 0 | Non-target distractor stimulus |
- **Super Meta Notes**: Derived from raw event(s) [`stars`, `boats`] by analyzing trial-level target/distractor annotations in original study metadata. Kernel step: Load target vs distractor labels from original stimulus file (e.g., stimlist.csv) and merge with epoch timestamps based on presentation order.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2018.12.046 — Reports target vs distractor binary classification using LDA, with extended epoch window tmin=-0.1s to tmax=2.0s to capture N2/N4 components

### Normal Task 1: Super-meta task
- **Task Type**: regression/classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 1.0 s, target_events = [`stars`, `boats`]
- **Label Route**: `misc`
- **Target Definition**: Continuous or categorical superordinate labels (animacy, category, object identity) derived from original stimulus metadata

- **Kernel Notes**: Derive and version super-meta in kernel. Load original stimulus metadata (200 images) and map each epoch to its animacy label (animate/inanimate), category (10-way), or object identity (50-way). (replaces Normal Task 2 from original analysis.md)


## Data Quality Notes

- Only 2 subjects - extremely limited statistical power for group-level analysis
- RSVP at 5 Hz and 20 Hz: at 20 Hz, images appear for only 50 ms (near threshold for conscious processing)
- Verify that `stars` and `boats` events correspond to onset markers and not sustained states

## References

- **Reference**: `The representational dynamics of visual objects in rapid serial visual processing streams. NeuroImage, 188, 668-679`
