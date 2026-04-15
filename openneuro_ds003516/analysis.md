# EEG: Attended Speaker Paradigm (Own Name in Ignored Stream)

**Dataset**: `openneuro_ds003516` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003516
**Category**: High-level Mental | **Subjects**: 25 | **Files (Completed)**: 25 | **Channels**: 49 | **Sampling Rate**: 500 Hz
**Manual Review**: Pending

## Paradigm

Participants performed a cocktail-party selective auditory attention task with two competing speakers. They listened to audio books from one speaker (attended stream) while their own name was occasionally presented in the ignored stream. This paradigm investigates the neural correlates of selective attention and the salience of self-referential stimuli (own name) in the unattended auditory channel. No discrete trial-level event markers were recorded in the EEG data.

## File Scan Result

> **Kernel SHA256**: `ab3203b0314d66402523c7e0da16ac339f14e963890ec81ff54fba69d79bb286`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Beep` | 25 | event | raw | Calibration system check beep |
| `Calib_End` | 8 | event | raw | End of calibration phase |
| `Calib_Start` | 25 | event | raw | Start of calibration phase |
| `StartTrigger` | 125 | event | raw | Block-level attention shift trigger |
| `beam` | 500 | event | raw | Audio stimulus encoding marker (beam stream) |
| `beep` | 500 | event | raw | Audio stimulus encoding marker (beep stream) |
| `boundary` | 175 | event | raw | Preprocessing segment boundary |
| `omni` | 500 | event | raw | Audio stimulus encoding marker (omni stream) |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Neural Speech Envelope Tracking (Attended vs Ignored)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `attended_segment` | continuous 0-1 | Cross-correlation magnitude between EEG and attended speech envelope (higher = stronger neural tracking of attended speech) |
  | `ignored_segment` | continuous 0-1 | Cross-correlation magnitude between EEG and ignored speech envelope (lower = weaker neural tracking of ignored speech) |
- **Super Meta Notes**: Labels derived from experimental design log (block onsets, name embedment times) rather than raw EEG markers. Block-level conditions (attended/ignored speaker) assigned post-hoc per block. Envelope computed from audio stimuli using Hilbert transform. Requires loading separate audio files to compute speech envelopes and cross-correlating with segmented EEG at 0-500ms lag.
- **Evidence**:
  - DOI: 10.3389/fnins.2021.643705 — Uses ds003516 to investigate neural tracking of attended and ignored speech envelopes using 5-s segments before/after name occurrences with cross-correlation analysis
  - DOI: https://doi.org/10.1162/nol.a.14 — Uses mTRF toolbox for neural speech tracking by applying linear forward modeling on continuous EEG segmented by block-level conditions

### Classical Task 2: Own-Name P300 Response Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s, tmax = 1.5 s, target_events = [`name_onset`, `control_word_onset`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---|
  | `name_onset` | 1 | Participant's own name presented in ignored speaker stream |
  | `control_word_onset` | 0 | Control word presented in ignored speaker stream (matched length/frequency to names) |
- **Super Meta Notes**: Event timings derived from experimental design log (name embedment times in audio files) rather than raw EEG markers. Name onsets are known from stimulus creation. Kernel step: Extract name/control-word onset timestamps from design log, epoch EEG around those times, extract P3 amplitude in 500-1200ms window. Raw EEG events (`beam`, `beep`, `omni`) relate to audio stimulus encoding—not behavioral events—and do not align with name presentations.
- **Evidence**:
  - DOI: 10.3389/fnins.2021.643705 — Analyzes P3 responses to participants' own names embedded in ignored speech with epochs tmin=-0.5s tmax=1.5s and amplitude in 500-1200ms window

### Potential Task 1: Continuous EEG Feature Extraction
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null; unsupervised or feature extraction only)
- **Notes**: No trial-level annotations available in raw EEG; treat as continuous listening recording. Suitable for exploratory neural tracking analyses or feature-based classification using demographic labels (subject_age, subject_sex). The 175 `boundary` events indicate preprocessing segments—exclude from analysis. The 125 `StartTrigger` events (~5 per subject) likely mark block-level attention shifts rather than trial-level occurrences.

## Data Quality Notes

- No discrete trial-level event markers for name presentations in raw EEG
- Available events (`beam`, `beep`, `omni`, `StartTrigger`) do not align with critical behavioral events (own-name in ignored stream)
- Critical task analysis (Classical Task 2) requires external experimental design logs with precise name/control-word onset timestamps
- Must load audio stimulus files separately to compute speech envelopes via Hilbert transform for envelope tracking tasks