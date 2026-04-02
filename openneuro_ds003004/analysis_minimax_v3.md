# Imagined Emotion Study

**Dataset**: `openneuro_ds003004` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003004
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 34 | **Channels**: 219.0 | **Sampling Rate**: 256.0 Hz

## Paradigm

Participants used voice-guided imagery to induce and sustain 15 distinct emotional states, using button presses to indicate the onset and offset of each imagined emotion. Despite the paradigm involving discrete emotional state onsets (button presses), no event markers were detected in the BIDS EEG files by the locator pipeline. The button-press events may be stored in separate behavioral logs or were not encoded in the EEG trigger channel.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003004

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| *(none)* | - | - | raw | No event markers detected in EEG files; button-press onsets not captured in locator |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
> - `long`: sustained-state marker (>=2 s), for `epoch_by_long_event_hdf5`
> - `rest`: resting-state segment marker, for `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **exclude** from epoch target_events
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: 15-class Imagined Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 218 s *, overlap = 0.75 *, target_events = [`button_press_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `button_press_onset` | 0 | love |
  | `button_press_onset` | 1 | joy |
  | `button_press_onset` | 2 | happiness |
  | `button_press_onset` | 3 | relief |
  | `button_press_onset` | 4 | compassion |
  | `button_press_onset` | 5 | contentedness |
  | `button_press_onset` | 6 | excitement |
  | `button_press_onset` | 7 | awe |
  | `button_press_onset` | 8 | anger |
  | `button_press_onset` | 9 | jealousy |
  | `button_press_onset` | 10 | disgust |
  | `button_press_onset` | 11 | frustration |
  | `button_press_onset` | 12 | fear |
  | `button_press_onset` | 13 | sadness |
  | `button_press_onset` | 14 | grief |
- **Kernel Notes**: Button-press onsets defined emotion start times; emotion periods lasted 43s-12min (mean 218±94s). Use 75%-overlapping 2-s Hanning windows for spectral decomposition as per original analysis. Verify event ID mapping from events.tsv - original trigger channel did not capture button presses; they were logged in separate behavioral files. (replaces Primary Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.3389/neuro.09.061.2009 — UCSD study examining high-frequency broadband EEG modulations during 15-class imagined emotion task using ICA-based spectral decomposition, with 32 subjects performing guided imagery of emotions.
  - DOI: 10.1016/j.neuroimage.2022.118873 — Applied 20-model AMICA decomposition to high-density EEG data from 31 participants during self-paced emotion imagination with 15 distinct emotional states, using button-press markers to define emotion onsets/offsets.

### Primary Task 2: Binary Valence Classification (Positive vs Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `positive_valence` | 0 | positive valence (love, joy, happiness, relief, contentment, excitement, awe, compassion) |
  | `negative_valence` | 1 | negative valence (anger, jealousy, disgust, frustration, fear, sadness, grief) |
- **Super Meta Notes**: Derived from raw event(s) [`button_press_onset`] by grouping 15 emotion conditions into binary valence categories. Excluded first 60s and last 10s of each emotion block per original FBCSP analysis. Kernel step: For each 6s segment, assign valence label based on which emotion block the segment falls within (positive=8 emotions, negative=7 emotions).
- **Kernel Notes**: Exclude first 2 emotion blocks per subject as per original analysis; use 40 equally spaced segments per block. Verify event timing in events.tsv for accurate block boundaries. (replaces Normal Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.1109/acii.2013.160 — Analyzes 12-subject guided emotion imagery EEG dataset, classifying positive vs negative valence from 6-second EEG segments using Filter-Bank Common Spatial Pattern (FBCSP) with block-wise cross-validation.

### Normal Task 1: Resting / Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null - no trial-level event markers in locator; rest periods were 2min eyes-closed at start/end of session)
- **Notes**: High-density 219-channel EEG. Rest periods (2min eyes-closed at start/end) could be used for baseline/control analysis.

## Data Quality Notes

- No event markers detected in EEG files by locator pipeline - verify events.tsv directly.
- High-density 219-channel array; verify electrode positions and system (likely EGI/Geodesic).
- 15 distinct emotional states if properly annotated - valuable for affective BCI research.
- Verify channel count consistency across subjects before pooling.

