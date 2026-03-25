# Sternberg Working Memory

**Dataset**: `openneuro_ds004117` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004117
**Category**: High-level Mental | **Subjects**: 23 | **Files (Completed)**: 85
**Channels**: 71 | **Sampling Rate**: 250 Hz

## Paradigm

A modified Sternberg working memory task in which participants selectively memorized sets of 3, 5, or 7 target letters (marked with lowercase 'g' prefix, e.g., gH) while ignoring identical-font distractor letters. After a retention period, a probe letter was presented and participants indicated with auditory feedback whether it was in the memorized set. The study investigates frontal midline EEG dynamics (particularly theta oscillations) during working memory maintenance.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004117

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `WM` | 85 files | short | raw | Working memory trial onset / encoding phase |
| `nonWM` | 85 files | short | raw | Non-working-memory (distractor) trial |
| `gA`-`gZ` (prefixed letters) | 85 files | short | raw | Working memory target letter onset (to be memorized) |
| `A`-`Z` (plain letters) | 85 files | short | raw | Distractor letter onset (to be ignored) |
| `255` | 85 files | admin | raw | System trigger (likely BrainVision marker 255 = all bits) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Memorize vs Ignore Letter Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 2.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `WM` / `gA`-`gZ` (memorize letters) | 1 | Working memory target letter (to be memorized) |
  | `nonWM` / `A`-`Z` (ignore letters) | 0 | Distractor letter (to be ignored) |
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2005.04.014 — This 2005 NeuroImage paper presents the original EEG study from which the openneuro_ds004117 dataset derives, analyzing frontal midline theta dynamics in 23 subjects during a modified Sternberg working memory task with 71-channel EEG at 250 Hz, using ICA decomposition to separate Memorize vs Ignore letter trials and examining theta power changes with memory load.
- **Kernel Notes**: Exclude admin marker `255`. Map `WM` events (and prefixed letters `gA`-`gZ`) to y=1 (Memorize), map `nonWM` events (and plain letters `A`-`Z`) to y=0 (Ignore). Optionally include memory load (3, 5, 7 letters) as a secondary dimension.

### Normal Task 1: WM vs Non-WM Letter Encoding (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 255 is an admin marker and must be excluded. Individual letter events (A-Z, gA-gZ) mark specific letter presentations and can be used for fine-grained analysis. 23 subjects x ~3.7 sessions on average = 85 files.

| Event | y | Meaning |
 |-------|---|------|
 | `WM` | 1 | Working memory encoding trial |
 | `nonWM` | 0 | Non-working-memory (distractor) trial |

## Data Quality Notes

- Trigger 255 (all-bits-high) is a system artifact and must be excluded
- Individual letter events provide fine-grained trial structure for ERP analysis
- 23 subjects x multiple sessions - verify session structure before pooling

## References

- **Reference**: `Onton, J., Delorme, A. and Makeig, S., 2005. Frontal midline EEG dynamics during working memory. Neuroimage, 27(2), pp.341-356.`
