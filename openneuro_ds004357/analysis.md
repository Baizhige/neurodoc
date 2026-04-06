# Features-EEG

**Dataset**: `openneuro_ds004357` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004357
**Category**: Sensory/Response | **Subjects**: 16 | **Files (Completed)**: 16
**Channels**: 127 | **Sampling Rate**: 1000 Hz

## Paradigm

Participants viewed rapid serial visual presentation (RSVP) streams of Gabor-like stimuli at 6.67 Hz and 20 Hz while performing an orthogonal fixation color change detection task. Three event types encode different feature or condition categories, enabling investigation of how visual features are dynamically encoded in EEG responses.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Event/E 1` | 16x~16000 | event | raw | Stimulus feature condition 1 |
| `Event/E 2` | 16x~16000 | event | raw | Stimulus feature condition 2 |
| `Event/E 3` | 16x~60 | event | raw | Stimulus feature condition 3 (rare) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Visual Feature Decoding from RSVP Stimuli
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.6 s, target_events = [`Event/E 1`, `Event/E 2`, `Event/E 3`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Event/E 1` | 0 | Stimulus feature condition 1 (orientation/contrast/SF/color level 1) |
  | `Event/E 2` | 1 | Stimulus feature condition 2 (orientation/contrast/SF/color level 2) |
  | `Event/E 3` | 2 | Stimulus feature condition 3 (orientation/contrast/SF/color level 3) |
- **Super Meta Notes**: Derived from raw event(s) [`Event/E 1`, `Event/E 2`, `Event/E 3`] by mapping stimulus onset markers to visual feature conditions (orientation, contrast, spatial frequency, color). Kernel step: For each epoch, extract feature labels from the experimental condition log (or derive via MVPA pattern classification for orientation, contrast, spatial frequency, color - 4-class per feature). Paper reports separate binary/multiclass decoders for each of 4 visual features.
- **Evidence**:
  - DOI: 10.1038/s41598-025-27703-5 — MVPA decoding of visual grating stimuli varying in orientation, contrast, spatial frequency, and color using epochs from -0.1s to 0.6s post-stimulus
- **Kernel Notes**: Extract epochs aligned to stimulus onset events; apply MVPA classifier to decode which visual feature level was presented. Severe class imbalance: E1/E2 ~16000 trials each vs E3 ~60 trials. Handle imbalance via class weighting or oversampling.

### Potential Task 1: Visual Feature Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
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


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review