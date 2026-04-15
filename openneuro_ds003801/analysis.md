# Neural Tracking to Go

**Dataset**: `openneuro_ds003801` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003801
**Category**: Complex Applied | **Subjects**: 20 | **Files (Completed)**: 20
**Channels**: 24 | **Sampling Rate**: 250 Hz
**Manual Review**: Pending

## Paradigm

A mobile EEG study investigating neural speech tracking during a dichotic listening paradigm (two competing speakers) across different postures and locomotion states. Participants performed auditory attention tasks while either sitting, standing, or walking along a pre-defined indoor route with environmental distractions. The study examines how locomotion and environmental complexity affect neural envelope tracking of attended speech. Sound stimuli (6 different sounds) were presented in alternating sitting and walking blocks, with participants providing yes/no responses to questions about the attended speaker.

## File Scan Result

> **Kernel SHA256**: `89267b4a22e1e69444505ea8505cb6a9e72d5fcc007a38d7ace08453d76444ee`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full
### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no` | 181 | event | raw | No response button press |
| `play` | 179 | event | raw | Audio stimulus playback event |
| `rest_sit` | 20 | event | raw | Rest period while sitting |
| `rest_stand` | 20 | event | raw | Rest period while standing |
| `start_exp` | 20 | event | raw | Experiment start marker |
| `start_sound1_sit` | 10 | event | raw | Start of sound 1 presentation during sitting |
| `start_sound1_walk` | 10 | event | raw | Start of sound 1 presentation during walking |
| `start_sound2_sit` | 10 | event | raw | Start of sound 2 presentation during sitting |
| `start_sound2_walk` | 10 | event | raw | Start of sound 2 presentation during walking |
| `start_sound3_sit` | 10 | event | raw | Start of sound 3 presentation during sitting |
| `start_sound3_walk` | 10 | event | raw | Start of sound 3 presentation during walking |
| `start_sound4_sit` | 10 | event | raw | Start of sound 4 presentation during sitting |
| `start_sound4_walk` | 10 | event | raw | Start of sound 4 presentation during walking |
| `start_sound5_sit` | 10 | event | raw | Start of sound 5 presentation during sitting |
| `start_sound5_walk` | 10 | event | raw | Start of sound 5 presentation during walking |
| `start_sound6_sit` | 10 | event | raw | Start of sound 6 presentation during sitting |
| `start_sound6_walk` | 10 | event | raw | Start of sound 6 presentation during walking |
| `stop_sound1_sit` | 10 | event | raw | End of sound 1 presentation during sitting |
| `stop_sound1_walk` | 10 | event | raw | End of sound 1 presentation during walking |
| `stop_sound2_sit` | 10 | event | raw | End of sound 2 presentation during sitting |
| `stop_sound2_walk` | 10 | event | raw | End of sound 2 presentation during walking |
| `stop_sound3_sit` | 10 | event | raw | End of sound 3 presentation during sitting |
| `stop_sound3_walk` | 10 | event | raw | End of sound 3 presentation during walking |
| `stop_sound4_sit` | 10 | event | raw | End of sound 4 presentation during sitting |
| `stop_sound4_walk` | 10 | event | raw | End of sound 4 presentation during walking |
| `stop_sound5_sit` | 10 | event | raw | End of sound 5 presentation during sitting |
| `stop_sound5_walk` | 10 | event | raw | End of sound 5 presentation during walking |
| `stop_sound6_sit` | 10 | event | raw | End of sound 6 presentation during sitting |
| `stop_sound6_walk` | 10 | event | raw | End of sound 6 presentation during walking |
| `yes` | 156 | event | raw | Yes response button press |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Condition Classification (Sitting vs Walking)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0, tmax = None (duration of listening block)
- **Label Route**: `event`
- **Meta Level**: `raw`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `start_sound1_sit` | 0 | Sitting condition during sound 1 presentation |
  | `start_sound2_sit` | 0 | Sitting condition during sound 2 presentation |
  | `start_sound3_sit` | 0 | Sitting condition during sound 3 presentation |
  | `start_sound4_sit` | 0 | Sitting condition during sound 4 presentation |
  | `start_sound5_sit` | 0 | Sitting condition during sound 5 presentation |
  | `start_sound6_sit` | 0 | Sitting condition during sound 6 presentation |
  | `start_sound1_walk` | 1 | Walking condition during sound 1 presentation |
  | `start_sound2_walk` | 1 | Walking condition during sound 2 presentation |
  | `start_sound3_walk` | 1 | Walking condition during sound 3 presentation |
  | `start_sound4_walk` | 1 | Walking condition during sound 4 presentation |
  | `start_sound5_walk` | 1 | Walking condition during sound 5 presentation |
  | `start_sound6_walk` | 1 | Walking condition during sound 6 presentation |
- **Evidence**:
  - DOI: 10.1088/1741-2552/ac42b5 — Original ds003801 publication demonstrating that the study was conducted during both sitting and walking conditions with mobile EEG
- **Kernel Notes**: Use start_soundX_sit/walk events as epoch anchors. Each epoch captures the full listening block (until corresponding stop_soundX event). Condition label is directly encoded in event ID suffix. Walking condition segments will contain significant motion artifacts from locomotion; specialized preprocessing (ICA, ASR) recommended. 20 subjects × up to 12 listening blocks per condition provides adequate samples for classification.

### Potential Task 1: Auditory Attention Decoding (Attended vs Ignored Speaker)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 60.0 s, overlap = 0.0
- **Label Route**: `misc`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (experimental instruction metadata) | 0 | Participant instructed to attend to this speaker |
  | N/A (experimental instruction metadata) | 1 | Participant instructed to ignore this speaker |
- **Super Meta Notes**: Labels derived from experimental protocol (dichotic listening task where participants were instructed to attend to one of two competing speakers). Kernel step: For each 60s segment, compute mTRF-based speech envelope reconstruction from EEG, then calculate correlation between reconstructed envelope and audio envelopes of both speakers. Classify as attended if correlation with speaker A envelope exceeds that with speaker B envelope. Requires speech stimulus audio files and per-block attended speaker metadata from experimental design.
- **Evidence**:
  - DOI: 10.1088/1741-2552/ac42b5 — Original ds003801 publication demonstrating successful attended vs ignored speaker decoding using mTRF with 60s segments on this exact dataset
  - DOI: 10.3389/fnins.2022.869426 — Demonstrates feasibility of attended speaker identification from ear-EEG during two-competing speaker paradigm (supports paradigm plausibility)
- **Kernel Notes**: Requires speech stimulus audio files for both speakers (not included in EEG dataset). Extract audio envelopes from stimulus recordings. Fit multivariate TRF (mTRF) model predicting speech envelope from EEG features using time lags 0–500ms. Compare correlation of predicted envelope with both speaker envelopes. Higher correlation indicates attended speaker. Attention instructions change per block; kernel must load block-level attended speaker metadata. Motion artifacts during walking conditions may degrade tracking performance.

### Normal Task 1: Continuous Neural Speech Envelope Tracking
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Meta Level**: `super`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | N/A (continuous analysis) | continuous | Speech envelope time series from attended speaker audio |
- **Super Meta Notes**: Regression target is the speech envelope waveform from the attended speaker stimulus. Continuous labels aligned to EEG timestamps. Condition metadata (sit/walk) must be obtained from file-level metadata as event suffixes only indicate within-block condition.
- **Evidence**:
  - DOI: 10.1088/1741-2552/ac42b5 — Demonstrates neural tracking of speech envelope during both sitting and walking; mTRF models quantify the strength of EEG-speech envelope correlation
- **Kernel Notes**: Requires speech stimulus audio files. Extract audio envelope via Hilbert transform or bandpass filtering (0.5–8 Hz). Compute correlation between EEG-derived envelope and stimulus envelope per segment as quality metric. Segment-level condition (sit/walk) inferred from event structure within segment or from file metadata. Shorter 2s windows with 50% overlap enable fine-grained temporal analysis of tracking strength across the recording. Motion artifact contamination more prevalent in walking condition segments.