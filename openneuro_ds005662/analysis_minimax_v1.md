# A high-quality EEG dataset for studying visual touch perception

**Dataset**: `openneuro_ds005662` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds005662
**Category**: Sensory/Response | **Subjects**: N/A | **Files (Completed)**: 80 | **Channels**: 65 | **Sampling Rate**: 2048 Hz

## Paradigm

Participants viewed rapid streams of videos depicting touch to a hand or an object to investigate visual touch perception. The experiment used target and non-target trials to measure brain responses to observed touch. No event markers are present in the BIDS metadata; the EEG is stored as continuous recordings requiring segmentation for downstream analysis.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005662

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous EEG recordings without trial-level annotations in events.tsv._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Visual Touch Perception - Perspective Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stimulus_onset`, `touch_video_presentation`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `self` | 0 | First-person perspective (seeing one's own hand) |
  | `other` | 1 | Third-person perspective (seeing another person's hand) |
- **Super Meta Notes**: Labels derived from video metadata: perspective orientation (self vs other) encoded in the Validated Touch-Video Database; EEG epochs extracted -100 to 800 ms relative to stimulus onset.
- **Evidence**:
  - DOI: 10.1038/s41597.026.06714.5 — Presents and validates openneuro_ds005662 for visual touch perception, using MVPA to decode perspective (self vs other) from EEG epochs -100 to 800 ms relative to stimulus onset.
  - DOI: 10.1101/2025.07.10.664069 — Performs MVPA decoding to classify perspective (self vs other) from EEG epochs time-locked to stimulus onset.
- **Kernel Notes**: Extract epochs from -0.1s to 0.8s around stimulus_onset events; apply baseline correction (-0.1s to 0s); downsample to 200 Hz; apply 1-100 Hz bandpass filter; use common average reference; labels from video presentation metadata (perspective field).

### Primary Task 2: Visual Touch Perception - Material Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stimulus_onset`, `touch_video_presentation`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | material_1 | 0 | Object material category 1 |
  | material_2 | 1 | Object material category 2 |
  | material_3 | 2 | Object material category 3 |
  | material_4 | 3 | Object material category 4 |
  | material_5 | 4 | Object material category 5 |
  | material_6 | 5 | Object material category 6 |
  | material_7 | 6 | Object material category 7 |
  | material_8 | 7 | Object material category 8 |
- **Super Meta Notes**: Labels derived from video metadata: 8 material categories (e.g., wood, metal, fabric, skin, etc.) from the Validated Touch-Video Database.
- **Evidence**:
  - DOI: 10.1038/s41597.026.06714.5 — Uses MVPA to decode material (8 categories) from EEG epochs.
  - DOI: 10.1101_2025.07.10.664069 — Performs MVPA to classify material (8 categories) from EEG epochs.
- **Kernel Notes**: Same epoch parameters as Primary Task 1; labels from video metadata (material field); 8-class classification.

### Primary Task 3: Visual Touch Perception - Hand Orientation Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stimulus_onset`, `touch_video_presentation`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | left_self | 0 | Left hand, first-person perspective |
  | right_self | 1 | Right hand, first-person perspective |
  | left_other | 2 | Left hand, third-person perspective |
  | right_other | 3 | Right hand, third-person perspective |
- **Super Meta Notes**: Labels derived from video metadata: hand laterality (left vs right) crossed with perspective (self vs other), yielding 4 categories.
- **Evidence**:
  - DOI: 10.1038/s41597.026.06714.5 — Uses MVPA to decode hand orientation (4 categories: left/right hand x self/other perspective).
  - DOI: 10.1101_2025.07.10.664069 — Performs MVPA to classify hand orientation from EEG epochs.
- **Kernel Notes**: Same epoch parameters; combine hand_laterality and perspective fields from video metadata to create 4-class labels.

### Primary Task 4: Visual Touch Perception - Valence Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.8 s, target_events = [`stimulus_onset`, `touch_video_presentation`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | continuous | continuous | Valence rating (continuous scale, e.g., 1-7 or 0-100) |
- **Super Meta Notes**: Continuous valence ratings from validated database (subjective ratings of how pleasant/pleasant vs. unpleasant the touch appears).
- **Evidence**:
  - DOI: 10.1038/s41597.026.06714.5 — Uses regression to decode valence (continuous) from EEG epochs.
  - DOI: 10.1101_2025.07.10.664069 — Performs regression to predict valence from EEG epochs.
- **Kernel Notes**: Same epoch parameters; regression target is continuous valence value from video metadata; report RMSE/MAE as metrics.

### Normal Task 1: Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no events))
- **Notes**: No trial-level events found. Treat as continuous EEG; sliding window segmentation only.
## Data Quality Notes

- No event markers available - cannot perform event-locked epoching without additional annotation files.
- High sampling rate (2048 Hz); downsample to 500 Hz before processing.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to segmentation.

## References

- **Reference**: `Validated Touch-Video Database (Smit & Rich, 2025)`

## Data Quality Notes

- No event markers available - cannot perform event-locked epoching without additional annotation files.
- High sampling rate (2048 Hz); downsample to 500 Hz before processing.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to segmentation.

## References

- **Reference**: `Validated Touch-Video Database (Smit & Rich, 2025)`
