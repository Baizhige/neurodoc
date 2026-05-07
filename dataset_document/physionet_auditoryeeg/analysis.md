# Auditory evoked potential EEG-Biometric dataset

**Dataset**: `physionet_auditoryeeg` | **Year**: 2021 | **URL**: https://physionet.org/content/auditory-eeg/1.0.0/
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 205 | **Channels**: 4 | **Sampling Rate**: 200 Hz | **Manual Review**: Shu Peng

## Paradigm

Twenty volunteers (s01-s20) aged 21-31 participated in a multipurpose EEG study involving resting-state and auditory stimulus paradigms, completing all tasks in a single day while seated comfortably. EEG data was recorded at a 200 Hz sampling rate using an OpenBCI Ganglion board with four gold-cup electrodes (T7, F8, Cz, P4) positioned according to the 10/10 international system, alongside ear-placed reference and ground electrodes. The recording conditions consisted of three-minute sessions for resting states (eyes open, eyes closed) and six auditory stimulus tasks. For the auditory stimuli, subjects listened to a native song, a non-native song (Arabic for Italian subjects, and Italian for non-Italian subjects), and neutral instrumental music, which were delivered via both in-ear and bone-conducting headphones.

## File Scan Result

> **Kernel SHA256**: `f2baba5ab9eae9018027474a4a0fd04e526a9b49f98707e5b415b7e04bf76e9a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|---|---|---|---|---|
| `auditory_native_song_bone` | 120 | event | raw | Native song via bone-conduction headphones (ex08) |
| `auditory_native_song_in_ear` | 120 | event | raw | Native-language song via in-ear headphones (ex05) |
| `auditory_neutral_music_bone` | 120 | event | raw | Neutral instrumental music via bone-conduction headphones (ex10) |
| `auditory_neutral_music_in_ear` | 120 | event | raw | Neutral instrumental music via in-ear headphones (ex07) |
| `auditory_nonnative_song_bone` | 120 | event | raw | Non-native song via bone-conduction headphones (ex09) |
| `auditory_nonnative_song_in_ear` | 120 | event | raw | Non-native language song via in-ear headphones (ex06) |
| `resting_eyes_closed` | 360 | event | raw | Resting state with eyes closed (ex02) |
| `resting_eyes_open` | 358 | event | raw | Resting state with eyes open (ex01) |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `age` | partial (1438/2166) | e.g. 27, 23, 26 |
| `amplifier` | partial (1438/2166) | e.g. OpenBCI Ganglion Board |
| `cap` | partial (1438/2166) | e.g. gold-cup electrodes with Ten20 conductive paste |
| `device` | partial (1438/2166) | e.g. OpenBCI Ganglion Board, a 4-channel EEG acquisition system sampling at 200 Hz, with gold-cup electrodes at T7, F8, Cz, and P4 using Ten20 conductive paste and OpenBCI GUI v5.0.3. |
| `handedness` | missing | N/A |
| `sex` | partial (1438/2166) | e.g. male, female |


## Tasks

### Potential Task 1: Experimental Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`, `resting_eyes_closed`, `resting_eyes_open`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting state eyes open |
  | `resting_eyes_closed` | 1 | Resting state eyes closed |
  | `auditory_native_song_in_ear` | 2 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 3 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 4 | Neutral music in-ear |
  | `auditory_native_song_bone` | 5 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 6 | Non-native song bone-conduction |
  | `auditory_neutral_music_bone` | 7 | Neutral music bone-conduction |
- **Evidence**:
  - Event Structure table shows 8 file-supported experimental conditions with event-level annotations spanning entire recordings
  - Paradigm section describes resting-state conditions and six auditory stimulus conditions
- **Notes**: Noise-isolation conditions are excluded because no corresponding scanable records are present in the local `RECORDS`/file inventory. Each annotation spans the full recording file; long-event epoching with 30s windows captures sustained state. Primary dataset purpose is biometric identification, but condition classification is derivable from event labels.

### Potential Task 2: Eyes-Open Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`, `resting_eyes_open`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting state eyes open baseline |
  | `auditory_native_song_in_ear` | 1 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 2 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 3 | Neutral music in-ear |
  | `auditory_native_song_bone` | 4 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 5 | Non-native song bone-conduction |
  | `auditory_neutral_music_bone` | 6 | Neutral music bone-conduction |
- **Evidence**:
  - Event Structure table provides event IDs for eyes-open resting and auditory conditions
  - Paradigm notes eyes-open resting and all auditory conditions use comparable alertness state
- **Notes**: Excludes `resting_eyes_closed` to control for eye-state confound and excludes unavailable noise-isolation records. Useful for comparing auditory delivery methods while holding eye state constant.

### Potential Task 3: Binary Resting vs. Auditory Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`, `resting_eyes_closed`, `resting_eyes_open`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `resting_eyes_open` | 0 | Resting (any state) |
  | `resting_eyes_closed` | 0 | Resting (any state) |
  | `auditory_native_song_in_ear` | 1 | Auditory stimulation |
  | `auditory_nonnative_song_in_ear` | 1 | Auditory stimulation |
  | `auditory_neutral_music_in_ear` | 1 | Auditory stimulation |
  | `auditory_native_song_bone` | 1 | Auditory stimulation |
  | `auditory_nonnative_song_bone` | 1 | Auditory stimulation |
  | `auditory_neutral_music_bone` | 1 | Auditory stimulation |
- **Evidence**:
  - Paradigm describes two major condition classes: resting-state and auditory stimulus paradigms
  - Event Structure provides sufficient counts for both super-classes
- **Notes**: Collapses 8 file-supported conditions into 2 superordinate categories. Useful for the simplest baseline task before finer-grained condition classification.

### Potential Task 4: In-Ear vs. Bone-Conduction Headphone Comparison
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`auditory_native_song_bone`, `auditory_native_song_in_ear`, `auditory_neutral_music_bone`, `auditory_neutral_music_in_ear`, `auditory_nonnative_song_bone`, `auditory_nonnative_song_in_ear`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |---|---|---|
  | `auditory_native_song_in_ear` | 0 | Native song in-ear |
  | `auditory_nonnative_song_in_ear` | 0 | Non-native song in-ear |
  | `auditory_neutral_music_in_ear` | 0 | Neutral music in-ear |
  | `auditory_native_song_bone` | 1 | Native song bone-conduction |
  | `auditory_nonnative_song_bone` | 1 | Non-native song bone-conduction |
  | `auditory_neutral_music_bone` | 1 | Neutral music bone-conduction |
- **Evidence**:
  - Paradigm explicitly contrasts in-ear vs. bone-conduction headphone delivery
  - Event Structure contains matched stimulus types across both delivery methods
- **Notes**: Uses all six file-supported auditory events as a binary delivery-method task: in-ear (`y=0`) versus bone-conduction (`y=1`). Compares neural response to matched stimulus categories via different transduction pathways.

## Data Quality Notes

- Only 4 EEG channels (non-standard OpenBCI placement); spatial coverage is limited.
- Primary use case is biometric identification (same person across sessions), not condition classification; adapt label source accordingly.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: completed
