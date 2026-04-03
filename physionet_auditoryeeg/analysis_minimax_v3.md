# Auditory EEG Dataset (Biometric Identification)

**Dataset**: `physionet_auditoryeeg` | **Year**: 2021 | **URL**: https://physionet.org/content/auditory-eeg/1.0.0/
**Category**: High-level Mental | **Subjects**: 19 | **Files (Completed)**: 205 | **Channels**: 13 | **Sampling Rate**: 200 Hz

## Paradigm

Nineteen subjects (s01-s20, one subject absent) aged 21-31 participated in a biometric EEG identification study using resting-state and auditory stimulus paradigms (Trujillo et al., 2021). EEG was recorded using an OpenBCI Cyton board (13 channels, gold-cup electrodes at T7, F8, Cz, P4 and surrounding positions). Each subject completed multiple recording sessions across different experimental conditions: two resting-state conditions (eyes open, eyes closed), eyes-open with noise isolation, and six auditory stimulus conditions (native song, non-native song, neutral music - via in-ear headphones or bone-conduction headphones). Each recording is labeled by experiment code (ex01-ex12) encoded in the filename. Files from subject 5 (ex05) lack structured event codes and retain raw experiment codes as annotations.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 2 + Type 3
> **Why**: Derived targets are needed beyond raw markers.
> **Primary Label Routes**: Annotation, misc
> **Status**: wait_kernel_update
> **Evidence Keywords**: questionnaire
> **Web Reference Used for Decision**: https://physionet.org/content/auditory-eeg/1.0.0/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `resting_eyes_open` | ~50 | long | raw | Resting state with eyes open (ex01) |
| `resting_eyes_closed` | ~25 | long | raw | Resting state with eyes closed (ex02) |
| `resting_eyes_open_noise_isolation` | ~50 | long | raw | Eyes open with acoustic isolation (ex04, ex06) |
| `auditory_native_song_in_ear` | ~25 | long | raw | Native-language song via in-ear headphones (ex07) |
| `auditory_nonnative_song_in_ear` | ~25 | long | raw | Non-native language song via in-ear headphones (ex08) |
| `auditory_neutral_music_in_ear` | ~25 | long | raw | Neutral instrumental music via in-ear headphones (ex09) |
| `auditory_native_song_bone` | ~25 | long | raw | Native song via bone-conduction headphones (ex10) |
| `auditory_nonnative_song_bone` | ~25 | long | raw | Non-native song via bone-conduction headphones (ex11) |
| `ex05` | ~19 | long | raw | Uncoded experiment (raw experiment code, exclude from classification) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> Each annotation spans the entire recording file. Counts are approximate.
## MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

## Tasks

### Primary Task 1: Biometric Identification (Subject Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `biometric_identity` | 0-19 | Subject identifier (20 subjects, s01-s20) |
- **Super Meta Notes**: Derived from raw event(s) by extracting subject ID from filename (e.g., s01_ex01.mat → subject 1). Kernel step: Parse subject ID from filename pattern `{subject}_ex{code}.mat` and assign numeric label 0-19.
- **Evidence**:
  - DOI: 10.13026/ps31-fc50 — PhysioNet dataset page describing EEG-based biometric identification with 20 subjects and resting-state/auditory stimulus recordings
  - DOI: 10.1523/eneuro.0265.25.2025 — TriNet-MTL study training for biometric identification across 20 subjects using sliding window segmentation
- **Kernel Notes**: Extract subject ID from filename using regex pattern. Files from subject 5 (ex05) may have missing data; verify subject count matches actual files. Use 5-second windows with 50% overlap as specified in the paper.

### Primary Task 2: Stimulus Language Classification (Native vs Non-native)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus_language` | 0 | Native language song |
  | `stimulus_language` | 1 | Non-native language song |
- **Super Meta Notes**: Derived from raw event(s) [`auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]. Kernel step: Map native song events to label 0, non-native song events to label 1. Exclude neutral music events.
- **Evidence**:
  - DOI: 10.1523/eneuro.0265.25.2025 — TriNet-MTL study training for stimulus language classification (native vs non-native) using sliding window segmentation
- **Kernel Notes**: Group auditory events by language type. Native songs include `auditory_native_song_in_ear` and `auditory_native_song_bone` (y=0). Non-native songs include `auditory_nonnative_song_in_ear` and `auditory_nonnative_song_bone` (y=1). Neutral music events should be excluded from this binary classification task.

### Primary Task 3: Device Modality Classification (In-ear vs Bone Conduction)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `device_modality` | 0 | In-ear headphones |
  | `device_modality` | 1 | Bone-conduction headphones |
- **Super Meta Notes**: Derived from raw event(s) [`auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]. Kernel step: Map in-ear events to label 0, bone-conduction events to label 1.
- **Evidence**:
  - DOI: 10.1523/eneuro.0265.25.2025 — TriNet-MTL study training for device modality recognition (in-ear vs bone conduction) using sliding window segmentation
- **Kernel Notes**: Classify based on headphone type. In-ear: `auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear` (y=0). Bone: `auditory_native_song_bone`, `auditory_nonnative_song_bone` (y=1). Resting-state events should be excluded from this task.

### Primary Task 4: Auditory Condition Classification (6-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s *, overlap = 2.5 s *, target_events = [`auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `auditory_native_song_in_ear` | 0 | Native song, in-ear |
  | `auditory_nonnative_song_in_ear` | 1 | Non-native song, in-ear |
  | `auditory_neutral_music_in_ear` | 2 | Neutral music, in-ear |
  | `auditory_native_song_bone` | 3 | Native song, bone-conduction |
  | `auditory_nonnative_song_bone` | 4 | Non-native song, bone-conduction |
- **Evidence**:
  - DOI: 10.13026/ps31-fc50 — Dataset describes 6 auditory stimulus conditions (native/non-native/neutral × in-ear/bone)
- **Kernel Notes**: Exclude `ex05` files (uncoded experiment codes). The 6-class task distinguishes both stimulus type and headphone modality. (replaces Normal Task 1 from original analysis.md)

### Normal Task 1: Resting-State vs. Auditory Stimulus (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.

| Event | y | Meaning |
|-------|---|---------|
| `resting_eyes_open` | 0 | Resting state |
| `resting_eyes_closed` | 0 | Resting state |
| `auditory_native_song_in_ear` | 1 | Any auditory condition |
| `auditory_nonnative_song_in_ear` | 1 | Any auditory condition |
| `auditory_neutral_music_in_ear` | 1 | Any auditory condition |
| `auditory_native_song_bone` | 1 | Any auditory condition |
| `auditory_nonnative_song_bone` | 1 | Any auditory condition |

## Data Quality Notes

- Only 13 EEG channels (non-standard OpenBCI placement); spatial coverage is limited.
- `ex05` files (subject 5 recordings in some conditions) retain raw experiment codes and should be excluded from condition-labeled classification.
- Primary use case is biometric identification (same person across sessions), not condition classification; adapt label source accordingly.
- Some subjects may be missing recordings for certain experiment codes.

