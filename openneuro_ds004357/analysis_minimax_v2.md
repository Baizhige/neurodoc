# Features-EEG

**Dataset**: `openneuro_ds004357` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004357
**Category**: Sensory/Response | **Subjects**: 16 | **Files (Completed)**: 16
**Channels**: 127 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants viewed rapid serial visual presentation (RSVP) streams of Gabor-like stimuli at 6.67 Hz and 20 Hz while performing an orthogonal fixation color change detection task. Three event types encode different feature or condition categories, enabling investigation of how visual features are dynamically encoded in EEG responses.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004357

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E 1` | 16x~16000 | short | raw | Stimulus feature condition 1 |
| `Event/E 2` | 16x~16000 | short | raw | Stimulus feature condition 2 |
| `Event/E 3` | 16x~60 | short | raw | Stimulus feature condition 3 (rare) |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Visual Feature Decoding from RSVP Stimuli
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Stimulus feature condition 1 (orientation/contrast/SF/color level 1) |
  | `Event/E 2` | 1 | Stimulus feature condition 2 (orientation/contrast/SF/color level 2) |
  | `Event/E 3` | 2 | Stimulus feature condition 3 (orientation/contrast/SF/color level 3) |
- **Super Meta Notes**: Derived from raw event(s) [`Event/E 1`, `Event/E 2`, `Event/E 3`] by mapping stimulus onset markers to visual feature conditions (orientation, contrast, spatial frequency, color). Kernel step: For each epoch, extract feature labels from the experimental condition log (or derive via MVPA pattern classification for orientation, contrast, spatial frequency, color - 4-class per feature). Paper reports separate binary/multiclass decoders for each of 4 visual features.
- **Evidence**:
  - DOI: 10.1038/s41598.025.27703.5 — MVPA decoding of visual grating stimuli varying in orientation, contrast, spatial frequency, and color using epochs from -0.1s to 0.6s post-stimulus
- **Kernel Notes**: Extract epochs aligned to stimulus onset events; apply MVPA classifier to decode which visual feature level was presented. Severe class imbalance: E1/E2 ~16000 trials each vs E3 ~60 trials. Handle imbalance via class weighting or oversampling.

### Normal Task 1: Visual Feature Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Event/E 3 count (~60 per file) is far lower than E 1 and E 2 (~16000 each) - severe class imbalance. Decode exact condition mapping from paper. Similar structure to ds004252.

| Event | y | Meaning |
 |-------|---|------|
 | `Event/E 1` | 0 | Stimulus feature condition 1 |
 | `Event/E 2` | 1 | Stimulus feature condition 2 |
 | `Event/E 3` | 2 | Stimulus feature condition 3 |


## Data Quality Notes

- Severe class imbalance: E 1 and E 2 have ~16000 trials each vs. E 3 with ~60 per subject
- 127-channel high-density EEG
- RSVP paradigm at 6.67 Hz and 20 Hz; stimuli are very brief

## References

- **Reference**: `Mapping the Dynamics of Visual Feature Coding: Insights into Perception and Integration`
