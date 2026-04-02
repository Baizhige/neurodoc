# EEG: Attended Speaker Paradigm (Own Name in Ignored Stream)

**Dataset**: `openneuro_ds003516` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003516
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25
**Channels**: 49 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed a cocktail-party selective auditory attention task with two competing speakers. They listened to audio books from one speaker (attended stream) while their own name was occasionally presented in the ignored stream. This paradigm investigates the neural correlates of selective attention and the salience of self-referential stimuli (own name) in the unattended auditory channel. No discrete trial-level event markers were recorded in the EEG data.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003516

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG recording |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Own-Name P3 Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`name_onset`, `control_word_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `name_onset` | 0 | Own name presented in ignored speaker stream (higher salience) |
  | `control_word_onset` | 1 | Control word presented in ignored speaker stream (baseline) |
- **Super Meta Notes**: Event timings derived from experimental design log (name embedment times, block onsets) rather than raw EEG markers. Labels represent binary classification between own-name and control-word conditions within the 500-1200ms P3 window.
- **Evidence**:
  - DOI: 10.3389/fnins.2021.643705 — Uses dataset ds003516 to analyze P3 responses (tmin=-0.5s, tmax=1.5s) to participants' own names embedded in ignored speech, comparing amplitude in the 500-1200ms window between name_onset and control_word_onset conditions.
- **Kernel Notes**: Extract event timings from provided experimental design logs; epoch EEG around name_onset and control_word_onset; compute P3 amplitude in 500-1200ms window for classification.

### Primary Task 2: Speech Envelope Tracking (Attended vs Ignored)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.0
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `attended_speech_envelope` | continuous | Cross-correlation magnitude (0-500ms lag) between EEG and attended speech envelope |
  | `ignored_speech_envelope` | continuous | Cross-correlation magnitude (0-500ms lag) between EEG and ignored speech envelope |
- **Super Meta Notes**: Block-level conditions (higher/lower intelligibility) assigned post-hoc; compute cross-correlation between EEG and Hilbert-transformed speech envelopes in 5-s segments.
- **Evidence**:
  - DOI: 10.3389/fnins.2021.643705 — Analyzes neural tracking of attended and ignored speech envelopes using 5-s segments before/after name occurrences, measuring cross-correlation magnitude with time lags up to 500ms.
- **Kernel Notes**: Segment continuous EEG into 5-s windows aligned with speech envelope stimuli; compute Hilbert transform of audio envelopes; calculate cross-correlation between EEG channels and attended/ignored envelopes at 0-500ms lags.

### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no labels, for unsupervised or feature extraction))
- **Notes**: No trial-level annotations available; treat as continuous listening EEG. Suitable for neural tracking analyzes or subject-level classification using demographic labels.

## Data Quality Notes

- No event markers present; cannot epoch by stimulus onset.
- Continuous EEG during selective attention task; audio stimuli timing not embedded in EEG annotations.

## References

- **Reference**: `Bjorn Holtze (January, 2021). Own-name salience in selective auditory attention.`
