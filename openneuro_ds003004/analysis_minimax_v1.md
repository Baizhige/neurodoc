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

### Primary Task 1: Binary Valence Classification (Positive vs Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 6.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `positive_valence` | 1 | Positive emotions (love, joy, happiness, relief, contentment, awe) |
  | `negative_valence` | 0 | Negative emotions (anger, jealousy, disgust, frustration, fear, sadness, grief) |
- **Super Meta Notes**: Labels derived from block-level valence annotations (positive/negative) assigned to all 6s segments within each emotion block; original 15 emotion conditions collapsed into binary valence (8 positive vs 7 negative emotions). First 60s and last 10s of each emotion block excluded.
- **Evidence**:
  - DOI: 10.1109/acii.2013.160 — This paper analyzes the same 12-subject guided emotion imagery EEG dataset (originally collected by Onton and Makeig 2009, the source for openneuro_ds003004), classifying positive vs negative valence from 6-second EEG segments using Filter-Bank Common Spatial Pattern (FBCSP) with block-wise cross-validation.
- **Kernel Notes**: Apply segmentation to full continuous recording, then assign valence labels based on timing of emotion blocks. Requires block onset/offset timing from experimental protocol.

### Primary Task 2: 15-Class Imagined Emotion Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = varies per emotion (43 s to 12 min, mean ~218 s), overlap = 0.0, target_events = [`love`, `joy`, `happiness`, `relief`, `compassion`, `contentedness`, `excitement`, `awe`, `anger`, `jealousy`, `disgust`, `frustration`, `fear`, `sadness`, `grief`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `love` | 0 | Guided imagery of love |
  | `joy` | 1 | Guided imagery of joy |
  | `happiness` | 2 | Guided imagery of happiness |
  | `relief` | 3 | Guided imagery of relief |
  | `compassion` | 4 | Guided imagery of compassion |
  | `contentedness` | 5 | Guided imagery of contentment |
  | `excitement` | 6 | Guided imagery of excitement |
  | `awe` | 7 | Guided imagery of awe |
  | `anger` | 8 | Guided imagery of anger |
  | `jealousy` | 9 | Guided imagery of jealousy |
  | `disgust` | 10 | Guided imagery of disgust |
  | `frustration` | 11 | Guided imagery of frustration |
  | `fear` | 12 | Guided imagery of fear |
  | `sadness` | 13 | Guided imagery of sadness |
  | `grief` | 14 | Guided imagery of grief |
- **Super Meta Notes**: Button presses (right hand thumb button for emotion onset, left hand button for offset) recorded manually but not in EEG trigger channel - labels derived from participant button-presses indicating felt emotion onset/offset.
- **Evidence**:
  - DOI: 10.1016/j.neuroimage.2022.118873 — This study applied 20-model AMICA decomposition to high-density EEG data from 31 participants during a self-paced emotion imagination experiment with 15 distinct emotional states, using button-press markers to define emotion onsets and offsets for unsupervised learning of brain state dynamics.
  - DOI: 10.3389/neuro.09.061.2009 — This 2009 paper by Onton and Makeig presents the original UCSD study (later archived as openneuro_ds003004) examining high-frequency broadband EEG modulations during 15-class imagined emotion task using ICA-based spectral decomposition, with 32 subjects performing guided imagery of emotions while 250-channel EEG was recorded at 256 Hz.
- **Kernel Notes**: Extract epochs using long-event method around button-press onset markers. Emotion periods varied 43s-12min (mean 218±94s). Use non-overlapping windows within each emotion period for feature extraction.

### Primary Task 3: Resting-State Segmentation (for rest periods)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.75 *
- **Label Route**: `Annotation`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `rest` | 0 | Resting-state (2 min eyes-closed at start/end of session) |
- **Evidence**:
  - DOI: 10.3389/neuro.09.061.2009 — The original study included 2-minute eyes-closed rest periods at the start and end of each recording session.
- **Kernel Notes**: Segment the rest periods (first and last 2 min of each session) using sliding windows. These can serve as baseline or control condition.

### Normal Task 1: Resting / Continuous Segmentation (resting)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no trial-level event markers in locator; check events.tsv directly for button-press events))
- **Notes**: High-density 219-channel EEG. If button-press onset/offset events are available in events.tsv, 15 emotional states could be used as multiclass labels with long_event epoching.

## Data Quality Notes

- No event markers detected in EEG files by locator pipeline - verify events.tsv directly.
- High-density 219-channel array; verify electrode positions and system (likely EGI/Geodesic).
- 15 distinct emotional states if properly annotated - valuable for affective BCI research.
- Verify channel count consistency across subjects before pooling.

## References

- **Reference**: `Imagined Emotion Study`
