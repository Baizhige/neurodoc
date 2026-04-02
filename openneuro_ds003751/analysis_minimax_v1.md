# Dataset on Emotion with Naturalistic Stimuli (DENS)

**Dataset**: `openneuro_ds003751` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003751
**Category**: High-level Mental | **Subjects**: 40 | **Files (Completed)**: 40
**Channels**: 132 | **Sampling Rate**: 250 Hz

## Paradigm

Participants viewed naturalistic multimedia video clips (film excerpts, documentaries) to elicit a range of emotional states while EEG, ECG, and EMG data were simultaneously recorded. After each video clip, participants provided continuous subjective ratings of valence, arousal, dominance, liking, familiarity, and emotional category. The dataset supports multimodal emotion recognition research using naturalistic (ecologically valid) stimuli rather than standardized posed expressions.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Evidence Keywords**: regression target
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003751

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stm` | 40 | long | raw | Stimulus (video clip) onset marker |
| `IBEG` | 40 | long | raw | Image/video block beginning |
| `base` | 40 | long | raw | Baseline period onset |
| `bend` | 40 | long | raw | Baseline period end |
| `IEND` | 39 | long | raw | Image/video block end |
| `vlnc` | 40 | short | raw | Valence rating event |
| `arsl` | 40 | short | raw | Arousal rating event |
| `dmns` | 40 | short | raw | Dominance rating event |
| `lkng` | 40 | short | raw | Liking rating event |
| `relv` | 40 | short | raw | Relevance rating event |
| `fmrt` | 40 | short | raw | Familiarity rating event |
| `cate` | 40 | short | raw | Emotion category rating event |
| `clic` | 40 | short | raw | Mouse click rating response |
| `trno` | 40 | short | raw | Trial number marker |
| `fixL` | 40 | short | raw | Fixation cross onset |
| `quiz` | 15 | short | raw | Comprehension quiz question |
| `qdon` | 14 | short | raw | Quiz done marker |
| `stop` | 37 | admin | raw | Stop/pause marker |
| `puse` | 34 | admin | raw | Pause marker |
| `rsrt` | 32 | admin | raw | Restart marker |
| `net` | 2 | admin | raw | Network marker |

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

### Primary Task 1: Valence-Arousal Emotion Classification from Emotional Events
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`clic`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | HVHA | 0 | High Valence, High Arousal |
  | HVLA | 1 | High Valence, Low Arousal |
  | LVHA | 2 | Low Valence, High Arousal |
  | LVLA | 3 | Low Valence, Low Arousal |
- **Super Meta Notes**: Labels derived from post-stimulus self-assessment ratings of valence and arousal (scale 1-9) collected after each video clip. High/Low threshold at 5. Mouse clicks (`clic`) mark subjectively perceived emotional moments during video viewing.
- **Evidence**:
  - DOI: 10.1109/ACCESS.2023.3266804 — Classifies EEG epochs into 4-quadrant Valence-Arousal categories using 7-second segments around emotional events (1s before + 6s after mouse click)
  - DOI: 10.1007/978.3.031.27199.1.8 — Classifies emotional events into 8-class VAD space and 4-class VA space using CNN-GRU hybrid model with 7-second EEG segments around subjectively marked emotional moments
- **Kernel Notes**: Extract epochs centered on mouse click events (`clic`). Merge with post-stimulus ratings from `vlnc` (valence) and `arsl` (arousal) to derive VA labels. Use threshold 5 to binarize each dimension, then combine into 4-class quadrant labels.

### Primary Task 2: 24-Class Emotion Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s *, tmax = 6.0 s *, target_events = [`clic`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | 24 emotion categories | 0-23 | Participant-selected emotion categories from predetermined list (e.g., Amused, Sad, Fear, Happy) |
- **Super Meta Notes**: Labels derived from participant self-reports selecting emotion categories from a predetermined list that most accurately captured their experiences during video stimuli.
- **Evidence**:
  - DOI: 10.1109/icccnt61001.2024.10725514 — Classifies 24 unique categorized emotions from DENS dataset using optimized CNN-LSTM model with 7-second EEG epochs
- **Kernel Notes**: Extract epochs around `clic` events. Map emotion category ratings (`cate` event annotations) to class indices 0-23.

### Primary Task 3: Binary Self-Assessment Dimension Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -6.0 s, tmax = 1.0 s, target_events = [`clic`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | valence | 0 | Low (1-5) |
  | valence | 1 | High (5-9) |
  | arousal | 0 | Low (1-5) |
  | arousal | 1 | High (5-9) |
  | dominance | 0 | Low (1-5) |
  | dominance | 1 | High (5-9) |
  | liking | 0 | Low (1-2.5) |
  | liking | 1 | High (2.5-9) |
  | familiarity | 0 | Low (1-2.5) |
  | familiarity | 1 | High (2.5-9) |
  | relevance | 0 | Low (1-2.5) |
  | relevance | 1 | High (2.5-9) |
- **Super Meta Notes**: Labels derived from post-stimulus self-assessment ratings collected via questionnaire after each video clip. Binary threshold: V/A/D at 5, L/F/R at 2.5.
- **Evidence**:
  - DOI: 10.1101_2021.08.05.455187 — Classifies high vs low self-assessment dimensions (valence, arousal, dominance, liking, familiarity, relevance) from EEG features using k-NN classifier with labels derived from post-stimulus behavioral ratings
- **Kernel Notes**: Extract epochs from -6s to +1s relative to mouse click (`clic`). Merge with rating events (`vlnc`, `arsl`, `dmns`, `lkng`, `fmrt`, `relv`). Apply thresholding to create binary labels for each dimension.

### Normal Task 1: Emotion analysis during video stimulation period (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Video clips are naturalistic stimuli lasting many seconds; use long-event epoching. Continuous emotion ratings (valence, arousal) are the primary labels - treat as regression targets from behavioral data rather than discrete y values. Only 40 subjects and files.

| Event | y | Meaning |
 |-------|---|------|
| `stm` | - | Video stimulation period (continuous emotion labels from vlnc/arsl scoring) |

## Data Quality Notes

- 132-channel high-density EEG; requires careful preprocessing and ICA.
- Naturalistic stimuli with varying durations; trial lengths are not uniform.
- `stop`, `puse`, `rsrt`, `net` are administrative markers; exclude from epoching.
- Continuous emotion ratings stored separately; must be merged with EEG epochs for regression tasks.

## References

- **Reference**: `Sudhakar Mishra and Md. Asif and Uma Shanker Tiwary and Narayanan Srinivasan (2023). Dataset on Emotion with Naturalistic Stimuli (DENS). OpenNeuro ds003751.`
