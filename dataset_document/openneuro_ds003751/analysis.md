# Dataset on Emotion with Naturalistic Stimuli (DENS)

**Dataset**: `openneuro_ds003751` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds003751
**Category**: High-level Mental | **Subjects**: 40 | **Files (Completed)**: 40 | **Manual Review**: Pending
**Channels**: 132 | **Sampling Rate**: 250 Hz

## Paradigm

Participants viewed naturalistic multimedia video clips (film excerpts, documentaries) to elicit a range of emotional states while EEG, ECG, and EMG data were simultaneously recorded. During viewing, participants provided continuous self-report ratings of emotional dimensions (valence, arousal, dominance, frustration, relief, looking behavior) by clicking at moments of emotional significance. After each video clip, participants also provided categorical emotion labels and continuous ratings. The dataset supports multimodal emotion recognition research using ecologically valid naturalistic stimuli.

## File Scan Result

> **Kernel SHA256**: `c667176ee37367028edf39272aa7b49de7d660958c021021a8a618188ae5ce22`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `arousal_low` | 431 | event | raw | Continuous arousal rating (low threshold marker) |
| `baseline` | 40 | event | raw | Baseline period onset |
| `baseline_end` | 40 | event | raw | Baseline period end |
| `boundary` | 53 | event | raw | Data file boundary marker |
| `category` | 288 | event | raw | Emotion category rating response |
| `click` | 744 | event | raw | Mouse click marking emotional moment |
| `dominance` | 431 | event | raw | Continuous dominance rating |
| `fixation_left` | 430 | event | raw | Fixation cross onset (left position) |
| `frustration` | 431 | event | raw | Continuous frustration rating |
| `interval_begin` | 134 | event | raw | Video clip block beginning |
| `interval_end` | 133 | event | raw | Video clip block end |
| `looking` | 431 | event | raw | Looking behavior rating |
| `net` | 2 | admin | raw | Network marker |
| `pause` | 50 | admin | raw | Pause marker |
| `quiz` | 15 | event | raw | Comprehension quiz question |
| `quiz_done` | 14 | event | raw | Quiz completion marker |
| `relief` | 431 | event | raw | Continuous relief rating |
| `restart` | 48 | admin | raw | Restart marker |
| `stimulus` | 432 | event | raw | Video clip onset |
| `stop` | 37 | admin | raw | Stop/pause marker |
| `trial_number` | 433 | event | raw | Trial number marker |
| `valence_negative_centered` | 431 | event | raw | Valence rating (negative-centered scale) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Binary VAD (Valence-Arousal-Dominance) Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`click`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | high_valence | 1 | Valence rating ≥ 5 (high positive) |
  | low_valence | 0 | Valence rating < 5 (negative/lower) |
  | high_arousal | 1 | Arousal rating ≥ 5 (high) |
  | low_arousal | 0 | Arousal rating < 5 (low) |
  | high_dominance | 1 | Dominance rating ≥ 5 (high) |
  | low_dominance | 0 | Dominance rating < 5 (low) |
- **Evidence**:
  - DOI: 10.1101/2021.08.05.455187 — Binary classification of valence, arousal, dominance (threshold 5) using EEG during naturalistic video stimuli; 465 emotional events from 40 participants
  - DOI: 10.1109/ACCESS.2023.3266804 — Binary valence and arousal classification using temporally localized emotional events from DENS dataset
- **Kernel Notes**: Labels derived from `valence_negative_centered` (431 events) and `dominance` (431 events) continuous rating events paired with `click` (744) subjective emotional moment markers. Merge epochs around `click` events with corresponding continuous ratings and threshold at 5. Original analysis.md used `clic` but available event is `click` (744 events).

### Classical Task 2: 4-Class VA (Valence-Arousal) Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`click`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | HVHA | 0 | High Valence, High Arousal |
  | HVLA | 1 | High Valence, Low Arousal |
  | LVHA | 2 | Low Valence, High Arousal |
  | LVLA | 3 | Low Valence, Low Arousal |
- **Evidence**:
  - DOI: 10.1109/ACCESS.2023.3266804 — 4-class valence-arousal classification using 7-second EEG epochs around emotion click events; CNN-LSTM hybrid architecture; compares DENS with DEAP and SEED datasets
- **Kernel Notes**: Labels derived by mapping `valence_negative_centered` and `arousal_low` (431 events each) to binary thresholds and combining into 4 quadrants. Each `click` event mapped to corresponding VAD ratings within the trial window.

### Classical Task 3: 8-Class VAD (Valence-Arousal-Dominance) Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`click`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | HVHA_HD | 0 | High V, High A, High D |
  | HVHA_LD | 1 | High V, High A, Low D |
  | HVLA_HD | 2 | High V, Low A, High D |
  | HVLA_LD | 3 | High V, Low A, Low D |
  | LVHA_HD | 4 | Low V, High A, High D |
  | LVHA_LD | 5 | Low V, High A, Low D |
  | LVLA_HD | 6 | Low V, Low A, High D |
  | LVLA_LD | 7 | Low V, Low A, Low D |
- **Evidence**:
  - DOI: 10.1101/2021.08.05.455187 — 8-class VAD classification from EEG; connectivity patterns and source localization analysis
  - DOI: 10.1007/978-3-031-27199-1.8 — CNN-GRU hybrid model for 8-class VAD emotion classification using 7-second epochs; 465 emotional events; achieves high accuracy on naturalistic emotion recognition
- **Kernel Notes**: Labels derived from ternary combination of binary-thresholded VAD ratings. Use `valence_negative_centered` (high/low threshold 5), `arousal_low` (high/low threshold 5), `dominance` (high/low threshold 5) to create 8 classes.

### Classical Task 4: 24-Class Emotion Category Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`click`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | category_0–23 | 0–23 | 24 unique emotion categories from participant self-report |
- **Evidence**:
  - DOI: 10.1109/ICCCNT61001.2024.10725514 — 24-class emotion classification using CNN-LSTM-GA model; 93.28% accuracy; 465 emotional events from 40 participants; 128-channel EEG at 125 Hz
- **Kernel Notes**: Labels sourced from `category` events (288 events). Match category labels to corresponding `click` events within each trial. Categories are predetermined emotion labels self-reported by participants.

### Normal Task 1: Frustration and Relief Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`click`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | high_frustration | 1 | Frustration rating ≥ threshold |
  | low_frustration | 0 | Frustration rating < threshold |
  | high_relief | 1 | Relief rating ≥ threshold |
  | low_relief | 0 | Relief rating < threshold |
- **Evidence**:
  - DOI: 10.1101/2021.08.05.455187 — Mentions analysis of emotional dimensions including frustration and relief in naturalistic paradigm
  - DOI: 10.1109/ACCESS.2023.3266804 — Dataset includes frustration and relief as emotional response dimensions
- **Kernel Notes**: Labels from `frustration` (431 events) and `relief` (431 events) continuous rating events. These secondary affect dimensions complement VAD ratings for comprehensive emotion modeling.

### Normal Task 2: Looking Behavior Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 6.0 s, target_events = [`click`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | looking_high | 1 | High visual engagement/attention |
  | looking_low | 0 | Low visual engagement/attention |
- **Evidence**:
  - DOI: 10.1109/ACCESS.2023.3266804 — Looking behavior tracked as engagement metric during naturalistic stimuli
- **Kernel Notes**: Labels from `looking` events (431 events). Looking behavior serves as an engagement/attention proxy during video watching, potentially useful for attention-aware emotion modeling.

### Potential Task 1: Naturalistic Video Block Segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = video_duration, target_events = [`interval_begin`, `interval_end`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | block_segment | video_id | Naturalistic video block identifier |
- **Evidence**: N/A (plausible from paradigm alone)
- **Kernel Notes**: Use `interval_begin` (134 events) and `interval_end` (133 events) as segment boundaries. Each segment corresponds to a full video clip with aggregated emotional labels. Supports continuous/long-segment analysis of emotion dynamics within videos.

### Potential Task 2: Stimulus-Locked Emotional Response Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 5.0 s, target_events = [`stimulus`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | stimulus | video_id | Video clip onset (432 events) |
- **Evidence**: N/A (plausible from paradigm alone)
- **Kernel Notes**: Alternative epoching approach using stimulus onset (`stimulus`, 432 events) instead of subjective click markers. Labels derived from subsequent continuous ratings. Captures initial stimulus-driven emotional response vs. self-initiated moment marking.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
