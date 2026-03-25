# Neural Tracking to Go

**Dataset**: `openneuro_ds003801` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003801
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 20
**Channels**: 24 | **Sampling Rate**: 250 Hz

## Paradigm

A mobile EEG study where participants performed a dichotic listening task (two competing speakers) while either sitting in a quiet indoor environment or walking along a pre-defined indoor route with environmental distractions. The study investigates how locomotion and environmental complexity affect neural tracking of attended speech (measured by auditory EEG envelope tracking). No discrete trial-level event markers were embedded in the EEG recording.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003801

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous EEG during dichotic listening and walking |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Auditory Attention Decoding - Attended vs Ignored Speaker
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0 *
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `to-be-attended_speech` | 0 | Participant instructed to attend to this speaker's speech |
  | `to-be-ignored_speech` | 1 | Competing speaker participant should ignore |
- **Super Meta Notes**: Labels derived from experimental instruction (which speaker to attend). Classification based on neural envelope tracking correlation: decode attended if reconstructed speech envelope correlates more strongly with attended than ignored speech stream.
- **Evidence**:
  - DOI: 10.3389/fnhum.2024.1483024 — Uses mTRF decoding to reconstruct speech envelopes and classify attended vs ignored speaker in single/dual-speaker conditions during mobile EEG (sitting/walking). Non-overlapping 60-s segments used for model training/testing.
  - DOI: 10.1088/1741-2552.ac42b5.2 — Uses mTRF models to decode which of two competing speakers the participant is attending to during sitting and walking conditions. Trial lengths ranged 5-60s.
  - DOI: 10.1088/1741-2552.ac42b5 — Decodes attended vs ignored speaker using multivariate linear regression (mTRF) on mobile EEG during dichotic listening.
- **Kernel Notes**: Compute neural speech envelope tracking using temporal response functions (time lags 0-500ms). For each segment, reconstruct speech envelope from EEG and compare correlation with attended vs ignored stimulus envelopes. Classify based on which correlation is higher.

### Primary Task 2: Salient Event-related Potential (P300) Analysis
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.5 s *, target_events = [`salient_event`, `control_event`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `control_event` | 0 | Non-salient control event in audio stream |
  | `salient_event` | 1 | Salient event in audio stream (detected from audio) |
- **Evidence**:
  - DOI: 10.1088/1741-2552.ac42b5.2 — Analysis of P3 ERP epochs from -500 to 1500ms around salient/control events. Uses 5s windows before/after salient events for distraction analysis.
  - DOI: 10.1088/1741-2552.ac42b5 — ERP epochs -500 to 150ms around salient/control events for P300 analysis.
- **Kernel Notes**: Extract epochs around salient events detected from audio signal (not embedded triggers). Note: These events are derived from audio analysis, not explicit EEG markers - kernel must implement salient event detection or use provided annotations.

### Normal Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (conditional label sit/walk needs to be obtained from file-level metadata))
- **Notes**: Mobile EEG; motion artifacts expected during walking condition. 20 subjects, 20 files (1 per subject). Condition (sitting/walking) is file-level metadata. Neural tracking of speech envelope requires cross-correlation with audio stimulus waveform.

## Data Quality Notes

- Mobile EEG recording; significant motion artifacts during walking condition.
- No trial-level event markers; condition label is file-level or block-level.
- Small dataset (20 subjects, 20 files); limited statistical power.
- 24-channel EEG at 250 Hz; modest spatial and temporal resolution.

## References

- **Reference**: `Neural Tracking to Go. OpenNeuro ds003801.`
