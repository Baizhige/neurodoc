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
> **Status**: wait_manual_review
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

### Primary Task 1: Neural Speech Envelope Tracking (Attended vs Ignored)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.5 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | attended_segment | continuous 0-1 | Cross-correlation magnitude between EEG and attended speech envelope (higher = stronger tracking) |
  | ignored_segment | continuous 0-1 | Cross-correlation magnitude between EEG and ignored speech envelope |
- **Super Meta Notes**: Derived from experimental design log (block onsets, name embedment times) rather than raw EEG markers. Block-level conditions (attended/ignored speaker) assigned post-hoc. Envelope computed from audio stimuli using Hilbert transform. Kernel step: Extract audio files, compute speech envelope via Hilbert transform, segment EEG into sliding windows, compute cross-correlation at 0-500ms lag between EEG and envelope.
- **Evidence**:
  - DOI: 10.3389/fnins.2021.643705 — Uses ds003516 to investigate neural tracking of attended and ignored speech envelopes using 5-s segments before/after name occurrences with cross-correlation analysis
  - DOI: https://doi.org/10.1162/nol.a.14 — Uses mTRF toolbox for neural speech tracking by applying linear forward modeling on continuous EEG segmented by 10-minute blocks
- **Kernel Notes**: Must load audio stimuli files to compute speech envelopes; segment EEG into sliding windows; compute TRF or cross-correlation between envelope and EEG channels. (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: Own-Name P300 Response Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.5 s *, target_events = [`name_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | name_onset | 1 | Participant's own name presented in ignored speaker stream |
  | control_word_onset | 0 | Control word presented in ignored speaker stream |
- **Super Meta Notes**: Event timings derived from experimental design log (name embedment times in audio files) rather than raw EEG markers. Name onsets known from stimulus creation. Kernel step: Extract name onset timestamps from design log, epoch EEG around those times, extract P3 amplitude in 500-1200ms window.
- **Evidence**:
  - DOI: 10.3389/fnins.2021.643705 — Analyzes P3 responses to participants' own names embedded in ignored speech with epochs tmin=-0.5s tmax=1.5s and amplitude in 500-1200ms window
- **Kernel Notes**: Must obtain design log with name/control word timestamps; epoch EEG around those times; extract P3 amplitude as features for classification. Verify event timing from experimental design documentation.

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

