# Imagined Emotion Study

**Dataset**: `openneuro_ds003004` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003004
**Category**: High-level Mental | **Subjects**: N/A | **Files (Completed)**: 34 | **Channels**: 219 | **Sampling Rate**: 256 Hz

## Paradigm

Participants used voice-guided imagery to induce and sustain 15 distinct emotional states, using button presses to indicate the onset and offset of each imagined emotion. Despite the paradigm involving discrete emotional state onsets (button presses), no event markers were detected in the BIDS EEG files by the locator pipeline. The button-press events may be stored in separate behavioral logs or were not encoded in the EEG trigger channel.

## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds003004.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `a4c55d18dc5360ecd9facfff5489c50a477ae8ddf504b1b5bdf4ad55a3b9041c`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `<LOCAL_HOME>/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|----------|
| `press` | 703 | event | raw | Unresolved from current kernel facts |
| `exit` | 558 | event | raw | Exit |
| `enter` | 508 | event | raw | Enter |
| `press1` | 492 | event | raw | Unresolved from current kernel facts |
| `awe` | 35 | event | raw | Awe |
| `ExitThankYou` | 34 | event | raw | Exit thank you |
| `ImaginationSuggestions` | 34 | event | raw | Imagination suggestions |
| `InstructionsForEnding` | 34 | event | raw | Instructions for ending |
| `anger` | 34 | event | raw | Anger |
| `compassion` | 34 | event | raw | Compassion |
| `content` | 34 | event | raw | Content |
| `disgust` | 34 | event | raw | Disgust |
| `excite` | 34 | event | raw | Excite |
| `fear` | 34 | event | raw | Fear |
| `frustration` | 34 | event | raw | Frustration |
| `grief` | 34 | event | raw | Grief |
| `happy` | 34 | event | raw | Happy |
| `jealousy` | 34 | event | raw | Jealousy |
| `joy` | 34 | event | raw | Joy |
| `love` | 34 | event | raw | Love |
| `postbase` | 34 | event | raw | Unresolved from current kernel facts |
| `postbase_instruct` | 34 | event | raw | Unresolved from current kernel facts |
| `prebase` | 34 | event | raw | Unresolved from current kernel facts |
| `relax` | 34 | event | raw | Relax |
| `relief` | 34 | event | raw | Relief |
| `sad` | 34 | event | raw | Sad |
| `prebase_instruct` | 33 | event | raw | Unresolved from current kernel facts |
| `InitialInstructions` | 31 | event | raw | Initial instructions |
| `FeelingItInstructionsNoButton` | 19 | event | raw | Feeling it instructions no button |
| `FeelingItInstructionsButton` | 18 | event | raw | Feeling it instructions button |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: 15-class Imagined Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 218 s *, overlap = 0.75 *, target_events = [`button_press_onset`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
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
- **Kernel Notes**: Button-press onsets defined emotion start times; emotion periods lasted 43s-12min (mean 218±94s). Use 75%-overlapping 2-s Hanning windows for spectral decomposition as per original analysis. Verify event ID mapping from events.tsv - original trigger channel did not capture button presses; they were logged in separate behavioral files. (replaces Classical Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.3389/neuro.09.061.2009 — UCSD study examining high-frequency broadband EEG modulations during 15-class imagined emotion task using ICA-based spectral decomposition, with 32 subjects performing guided imagery of emotions.
  - DOI: 10.1016/j.neuroimage.2022.118873 — Applied 20-model AMICA decomposition to high-density EEG data from 31 participants during self-paced emotion imagination with 15 distinct emotional states, using button-press markers to define emotion onsets/offsets.

### Classical Task 2: Binary Valence Classification (Positive vs Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|----------|
  | `positive_valence` | 0 | positive valence (love, joy, happiness, relief, contentment, excitement, awe, compassion) |
  | `negative_valence` | 1 | negative valence (anger, jealousy, disgust, frustration, fear, sadness, grief) |
- **Super Meta Notes**: Derived from raw event(s) [`button_press_onset`] by grouping 15 emotion conditions into binary valence categories. Excluded first 60s and last 10s of each emotion block per original FBCSP analysis. Kernel step: For each 6s segment, assign valence label based on which emotion block the segment falls within (positive=8 emotions, negative=7 emotions).
- **Kernel Notes**: Exclude first 2 emotion blocks per subject as per original analysis; use 40 equally spaced segments per block. Verify event timing in events.tsv for accurate block boundaries. (replaces Potential Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.1109/acii.2013.160 — Analyzes 12-subject guided emotion imagery EEG dataset, classifying positive vs negative valence from 6-second EEG segments using Filter-Bank Common Spatial Pattern (FBCSP) with block-wise cross-validation.

### Potential Task 1: Resting / Continuous Segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null - no trial-level event markers in locator; rest periods were 2min eyes-closed at start/end of session)
- **Notes**: High-density 219-channel EEG. Rest periods (2min eyes-closed at start/end) could be used for baseline/control analysis.

## Data Quality Notes

- No event markers detected in EEG files by locator pipeline - verify events.tsv directly.
- High-density 219-channel array; verify electrode positions and system (likely EGI/Geodesic).
- 15 distinct emotional states if properly annotated - valuable for affective BCI research.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update