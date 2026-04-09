# EEG: Probabilistic Learning with Affective Feedback: Exp #2

**Dataset**: `openneuro_ds003753` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003753
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25
**Channels**: 66 | **Sampling Rate**: 500 Hz

## Paradigm

A reinforcement learning task involving probabilistic affective feedback to investigate the Reward Positivity (RewP) EEG component and its sensitivity to affective stimulus properties. Participants made binary choices (left/right button) between cue stimuli (CUE) associated with positive or negative affective feedback images. Following each choice, an affective feedback image (FB) was presented. The study examines whether the RewP tracks reward value beyond mere monetary reward, responding to affective liking of feedback stimuli.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CUE` | 100 | event | raw | Cue stimulus requiring binary choice |
| `FB` | 100 | event | raw | Affective feedback stimulus (liked/disliked image) |
| `Left Button` | 25 | event | raw | Left button press response |
| `Right Button` | 25 | event | raw | Right button press response |
| `STATUS` | 25 | admin | raw | System status marker |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Affective Feedback Classification (Liked vs Disliked)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -1.0 s, tmax = 3.0 s *, target_events = [`FB`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `FB` (liked/rewarding) | 1 | Liked affective feedback (puppy images, positive valence) |
  | `FB` (disliked/non-rewarding) | 0 | Disliked affective feedback (chair/negative images, negative valence) |
- **Super Meta Notes**: Derived from raw event `FB` by decoding `trial_type` column in events.tsv to obtain liked/disliked affective value. Puppy images = liked (rewarding), chair/negative images = disliked (non-rewarding). Kernel step: Merge events.tsv metadata with raw `FB` events to produce binary affective labels. RewP ERP measured 200-350ms at Cz electrode for reward vs punishment conditions.
- **Evidence**:
  - DOI: 10.3758/s13415-021-00950-5 — Binary classification of feedback valence (liked/rewarding vs disliked/non-rewarding affective images) in a probabilistic reinforcement learning task with EEG epochs time-locked to outcome cues.
- **Kernel Notes**: Epoch relative to FB onset. Baseline correct -200 to 0 ms. Verify event ID mapping from events.tsv. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Publisher-defined BIDS task: Probabilistic Selection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `event`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**:
  - DOI: 10.18112/openneuro.ds003753.v1.1.0 — OpenNeuro metadata.tasksCompleted and dataset readme.
- **Kernel Notes**: Verify epoch parameters from dataset documentation.

## Data Quality Notes

- Small dataset (25 subjects, 25 files).
- FB event subtype labels (affective value) must be decoded from events.tsv metadata.
- STATUS is a single admin marker per file; exclude from epoching.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
- **Stim Labeling**: Route `stim` with trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.