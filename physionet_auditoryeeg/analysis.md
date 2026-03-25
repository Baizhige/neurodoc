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

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://physionet.org/content/auditory-eeg/1.0.0/ DOI: https://doi.org/10.13026/ps31


### Normal Task 1: Auditory Condition Classification (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Exclude `ex05` files (uncoded). For a simpler 3-class task, group by stimulus type (native/non-native/neutral) ignoring headphone type.

| Event | y | Meaning |
|-------|---|---------|
| `auditory_native_song_in_ear` | 0 | Native song, in-ear |
| `auditory_nonnative_song_in_ear` | 1 | Non-native song, in-ear |
| `auditory_neutral_music_in_ear` | 2 | Neutral music, in-ear |
| `auditory_native_song_bone` | 3 | Native song, bone-conduction |
| `auditory_nonnative_song_bone` | 4 | Non-native song, bone-conduction |


### Normal Task 2: Resting-State vs. Auditory Stimulus (epoch_by_long_event)
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

## References

- **Reference**: Trujillo LT et al. (2021). EEG recordings for biometric identification. Physionet. https://physionet.org/content/auditory-eeg/1.0.0/
