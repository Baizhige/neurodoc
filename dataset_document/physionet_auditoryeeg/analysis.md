# Auditory EEG Dataset (Biometric Identification)

**Dataset**: `physionet_auditoryeeg` | **Year**: 2021 | **URL**: https://physionet.org/content/auditory-eeg/1.0.0/
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 205 | **Channels**: 4 | **Sampling Rate**: 200 Hz |**Manual Review**: Liu Peng

## Paradigm

Nineteen subjects (s01-s20, one subject absent) aged 21-31 participated in a biometric EEG identification study using resting-state and auditory stimulus paradigms (Trujillo et al., 2021). EEG was recorded using an OpenBCI Cyton board (13 channels, gold-cup electrodes at T7, F8, Cz, P4 and surrounding positions). Each subject completed multiple recording sessions across different experimental conditions: two resting-state conditions (eyes open, eyes closed), eyes-open with noise isolation, and six auditory stimulus conditions (native song, non-native song, neutral music - via in-ear headphones or bone-conduction headphones). Each recording is labeled by experiment code (ex01-ex12) encoded in the filename. Files from subject 5 (ex05) lack structured event codes and retain raw experiment codes as annotations.

## File Scan Result

> **Kernel**: N/A
> **Kernel SHA256**: `b0fb53a13b65ddd627a459885811c0110078172e3fe0af22802920a04880cb10`

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `resting_eyes_open` | ~50 | event | raw | Resting state with eyes open (ex01) |
| `resting_eyes_closed` | ~25 | event | raw | Resting state with eyes closed (ex02) |
| `resting_eyes_open_noise_isolation` | ~50 | event | raw | Eyes open with acoustic isolation (ex06) |
| `auditory_native_song_in_ear` | ~25 | event | raw | Native-language song via in-ear headphones (ex07) |
| `auditory_nonnative_song_in_ear` | ~25 | event | raw | Non-native language song via in-ear headphones (ex08) |
| `auditory_neutral_music_in_ear` | ~25 | event | raw | Neutral instrumental music via in-ear headphones (ex09) |
| `auditory_native_song_bone` | ~25 | event | raw | Native song via bone-conduction headphones (ex10) |
| `auditory_nonnative_song_bone` | ~25 | event | raw | Non-native song via bone-conduction headphones (ex11) |
| `ex05` | ~19 | event | raw | Uncoded experiment (raw experiment code, exclude from classification) |


> Each annotation spans the entire recording file. Counts are approximate.

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | Age range: 21-31 years; mean age: 26.0 years |
| `sex` | missing | Male: 15; Female: 5 |
| `device` | missing | The core recording device is an OpenBCI Ganglion Board, a 4-channel EEG acquisition system that samples data at 200 Hz. It uses Gold Cup electrodes placed at standard scalp positions (T7, F8, Cz, P4) with Ten20 conductive paste, and is operated via the OpenBCI GUI software. |


## Tasks

### Classical Task 1: Resting State vs. Auditory Stimulus Classification
- **Task Type**: regression
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`resting_eyes_open`, `resting_eyes_closed`, `resting_eyes_open_noise_isolation`, `auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | Value | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting state eyes open |
  | `resting_eyes_closed` | 1 | Resting state eyes closed |
  | `resting_eyes_open_noise_isolation` | 2 | Resting eyes open with noise isolation |
  | `auditory_native_song_in_ear` | 3 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 4 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 5 | Neutral music in-ear |
  | `auditory_native_song_bone` | 6 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 7 | Non-native song bone-conduction |
- **Evidence**:
  - Event Structure table shows 8 distinct experimental conditions with event-level annotations spanning entire recordings
  - Paradigm section describes multiple auditory stimulus conditions and resting-state conditions
- **Notes**: `ex05` excluded due to uncoded raw experiment codes. Each annotation spans full recording file; long-event epoching with 30s windows captures sustained state. Primary dataset purpose is biometric identification, but condition classification is derivable from event labels.

### Classical Task 2: Resting State vs. Auditory Stimulus (Eyes-Open Conditions Only)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`resting_eyes_open`, `resting_eyes_open_noise_isolation`, `auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting state eyes open baseline |
  | `resting_eyes_open_noise_isolation` | 1 | Resting eyes open with noise isolation |
  | `auditory_native_song_in_ear` | 2 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 3 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 4 | Neutral music in-ear |
  | `auditory_native_song_bone` | 5 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 6 | Non-native song bone-conduction |
- **Evidence**:
  - Event Structure table provides event IDs for all eyes-open conditions
  - Paradigm notes eyes-open resting and all auditory conditions use comparable alertness state
- **Notes**: Excludes `resting_eyes_closed` to control for eye-state confound, and excludes `ex05`. Useful for comparing auditory delivery methods while holding eye state constant.

### Potential Task 1: In-Ear vs. Bone-Conduction Headphone Comparison
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `auditory_native_song_in_ear` | 0 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 1 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 2 | Neutral music in-ear |
  | `auditory_native_song_bone` | 3 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 4 | Non-native song bone-conduction |
- **Evidence**:
  - Paradigm explicitly contrasts in-ear vs. bone-conduction headphone delivery
  - Event Structure contains matched stimulus types across both delivery methods
- **Notes**: Neutral music bone-conduction condition (`ex12`) not present in event whitelist, so only 5 classes. Compares neural response to same/similar stimuli via different transduction pathways.

### Classical Task 3: Binary Resting vs. Auditory Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`resting_eyes_open`, `resting_eyes_closed`, `resting_eyes_open_noise_isolation`, `auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting (any state) |
  | `resting_eyes_closed` | 1 | Resting (any state) |
  | `resting_eyes_open_noise_isolation` | 2 | Resting (any state) |
  | `auditory_native_song_in_ear` | 3 | Auditory stimulation |
  | `auditory_nonnative_song_in_ear` | 4 | Auditory stimulation |
  | `auditory_neutral_music_in_ear` | 5 | Auditory stimulation |
  | `auditory_native_song_bone` | 6 | Auditory stimulation |
  | `auditory_nonnative_song_bone` | 7 | Auditory stimulation |
- **Evidence**:
  - Paradigm describes two major condition classes: resting-state and auditory stimulus paradigms
  - Event Structure provides sufficient counts for both super-classes
- **Notes**: Collapses 8 conditions into 2 superordinate categories. Excludes `ex05`. Useful for simplest baseline task before finer-grained condition classification.

## Data Quality Notes

- Only 13 EEG channels (non-standard OpenBCI placement); spatial coverage is limited.
- `ex05` files (subject 5 recordings in some conditions) retain raw experiment codes and should be excluded from condition-labeled classification.
- Primary use case is biometric identification (same person across sessions), not condition classification; adapt label source accordingly.
- Some subjects may be missing recordings for certain experiment codes.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
