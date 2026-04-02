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

### Primary Task 1: Binary Classification of Self-Assessment Dimensions (Valence, Arousal, Dominance)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`clic`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | high_vlnc | 1 | Valence rating ≥ 5 (high) |
  | low_vlnc | 0 | Valence rating < 5 (low) |
  | high_arsl | 1 | Arousal rating ≥ 5 (high) |
  | low_arsl | 0 | Arousal rating < 5 (low) |
  | high_dmns | 1 | Dominance rating ≥ 5 (high) |
  | low_dmns | 0 | Dominance rating < 5 (low) |
- **Super Meta Notes**: Derived from raw event `clic` (mouse click marking emotional moment) paired with post-stimulus self-assessment ratings (vlnc/arsl/dmns). Kernel step: Extract epochs around `clic` events; merge with continuous ratings; threshold each dimension at 5 to create binary labels. Note: Paper uses threshold 2.5 for liking/familiarity/relevance (separate binary tasks).
- **Evidence**:
  - DOI: 10.1101/2021.08.05.455187 — Shows binary classification of valence, arousal, dominance (threshold 5), and liking/familiarity/relevance (threshold 2.5) from EEG during naturalistic video stimuli
- **Kernel Notes**: Extract epochs from `clic` events; merge with per-trial rating data; apply threshold-based binarization. (replaces Normal Task 1 from original analysis.md)

### Primary Task 2: 8-Class VAD (Valence-Arousal-Dominance) Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`clic`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | HVHA | 0 | High Valence, High Arousal, High Dominance |
  | HVLA | 1 | High Valence, High Arousal, Low Dominance |
  | HVLHAD | 2 | High Valence, Low Arousal, High Dominance |
  | HVLAL | 3 | High Valence, Low Arousal, Low Dominance |
  | LVHA | 4 | Low Valence, High Arousal, High Dominance |
  | LVLAL | 5 | Low Valence, High Arousal, Low Dominance |
  | LVLAD | 6 | Low Valence, Low Arousal, High Dominance |
  | LVLALow | 7 | Low Valence, Low Arousal, Low Dominance |
- **Super Meta Notes**: Derived from raw event `clic` (subjective emotional marking mouse click) paired with post-stimulus VAD ratings. Kernel step: Extract epochs around `clic`; merge with VAD ratings; threshold each dimension at 5 to create 2^3=8 quadrant labels.
- **Evidence**:
  - DOI: 10.1007/978.3.031.27199.1.8 — Shows 8-class VAD classification using CNN-GRU hybrid model on DENS dataset
- **Kernel Notes**: Extract epochs from `clic` events; merge with continuous VAD ratings; apply threshold 5 for high/low on each dimension; map to 8-class quadrant labels.

### Primary Task 3: 4-Class Valence-Arousal Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`clic`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | HVHA | 0 | High Valence, High Arousal |
  | HVLA | 1 | High Valence, Low Arousal |
  | LVHA | 2 | Low Valence, High Arousal |
  | LVLA | 3 | Low Valence, Low Arousal |
- **Super Meta Notes**: Derived from raw event `clic` paired with post-stimulus valence/arousal ratings. Kernel step: Extract epochs around `clic`; merge with VA ratings; threshold at 5 to create 4-quadrant VA labels.
- **Evidence**:
  - DOI: 10.1109/ACCESS.2023.3266804 — Shows 4-class VA classification using 7-second epochs around emotional clicks
- **Kernel Notes**: Extract epochs from `clic` events; merge with continuous valence/arousal ratings; apply threshold 5 for high/low; map to 4-class VA labels.

### Primary Task 4: 24-Class Emotion Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`clic`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | amuse | 0 | Amused |
  | sad | 1 | Sadness |
  | fear | 2 | Fear |
  | happy | 3 | Happiness |
  | ... | ... | (24 emotion categories from self-report) |
- **Super Meta Notes**: Derived from raw event `clic` (emotional moment marking) paired with emotion category ratings (`cate`). Kernel step: Extract epochs around `clic`; merge with category self-reports; map to 24-class labels.
- **Evidence**:
  - DOI: 10.1109/icccnt61001.2024.10725514 — Shows 24-class emotion classification using CNN-LSTM achieving 93.28% accuracy on DENS dataset
- **Kernel Notes**: Extract epochs from `clic` events; merge with emotion category ratings from `cate` field; map to 24-class labels. Verify category list from original dataset annotations.

### Primary Task 5: 3-Class Valence Classification (Negative/Neutral/Positive)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`clic`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | negative | 0 | Valence 1-4.5 |
  | neutral | 1 | Valence 4.5-5.5 |
  | positive | 2 | Valence 5.5-9 |
- **Super Meta Notes**: Derived from raw event `clic` paired with post-stimulus valence ratings. Kernel step: Extract epochs around `clic`; merge with valence ratings; apply 3-class thresholds (4.5, 5.5).
- **Evidence**:
  - DOI: 10.1109/ACCESS.2023.3266804 — Shows 3-class valence classification (negative/neutral/positive) on DENS dataset
- **Kernel Notes**: Extract epochs from `clic` events; merge with continuous valence ratings; apply thresholds at 4.5 and 5.5 for 3-class division.

## Data Quality Notes

- 132-channel high-density EEG; requires careful preprocessing and ICA.
- Naturalistic stimuli with varying durations; trial lengths are not uniform.
- `stop`, `puse`, `rsrt`, `net` are administrative markers; exclude from epoching.
- Continuous emotion ratings stored separately; must be merged with EEG epochs for regression tasks.

