# Auditory EEG Dataset (Biometric Identification)

**Dataset**: `physionet_auditoryeeg` | **Year**: 2021 | **URL**: https://physionet.org/content/auditory-eeg/1.0.0/
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 205 | **Channels**: 4 | **Sampling Rate**: 200 Hz
**Manual Review**: Liu Peng

## Paradigm

Twenty subjects participated in a biometric EEG identification study using resting-state and auditory stimulus paradigms (Abo Alzahab et al., 2021). EEG was recorded using an OpenBCI Ganglion Board (4 channels, gold-cup electrodes at T7, F8, Cz, P4). Each subject completed multiple recording sessions across different experimental conditions: two resting-state conditions (eyes open, eyes closed), eyes-open with noise isolation (not provided in the dataset), and six auditory stimulus conditions (native song, non-native song, neutral music - via in-ear headphones or bone-conduction headphones). Each recording is labeled by experiment code (ex01-ex12) encoded in the filename. Files from subject 5 (ex05) lack structured event codes and retain raw experiment codes as annotations.

## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

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


> 1. All descriptive Event IDs (such as ‘resting_eyes_open’ and ‘auditory_native_song_in_ear’) are not native labels in the raw data, but rather high-level labels derived from the original experimental codes (exXX, which belong to raw meta). Therefore, the Meta Level for these IDs must be marked as ‘super’ rather than ‘raw’; only ‘ex05’ is an experimental code from the raw data and belongs to raw meta, so it is correctly labelled. 
> 2. ex04 corresponds to the noise-reducing open-eye resting-state experiment, which is classified as a ‘Non-Related experiment’. As it is not provided in the dataset and there are no files related to ex04 in your current file structure, you must remove ex04 from the ‘Meaning’ section and retain only the valid code ex06. If you wish to retain ex04, you must add the annotation ‘ex04 not provided in dataset’.
> 3. There is no file to support the ex11 encoding for auditory_nonnative_song_bone.
> 4. In the original text, both ‘resting_eyes_open’ (ex01) and ‘resting_eyes_closed’ (ex02) consist of three sessions per participant, with each session recorded for two minutes; therefore, the ‘Count’ for both should be approximately equal.
> 5. There are no files related to ex11, so this Event ID must be deleted.
> 6. Each annotation spans the entire recording file. Counts are approximate.

### MISC Label Summary

- **Route**: `misc`
- **Role**: Stores derived labels (super meta) not directly present in raw event IDs.
- **Candidate Labels**: Needs verification
- **Kernel Note**: Document derivation logic, source fields, units, and version tags.

### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | Age range: 21-31 years; mean age: 26.0 years |
| `subject_sex` | missing | Male: 15; Female: 5 |
| `device` | missing | The core recording device is an OpenBCI Ganglion Board, a 4-channel EEG acquisition system that samples data at 200 Hz. It uses Gold Cup electrodes placed at standard scalp positions (T7, F8, Cz, P4) with Ten20 conductive paste, and is operated via the OpenBCI GUI software. |


## Tasks

### Classical Task 1: Biometric Identification (Subject Classification)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `misc`
- **Evidence**:
  - DOI: 10.13026/ps31 — fc50 — PhysioNet dataset page describing EEG-based biometric identification with 20 subjects and resting-state/auditory stimulus recordings
  - DOI: 10.1523/eneuro.0265.25.2025 — TriNet-MTL study training for biometric identification across 20 subjects using sliding window segmentation
- **Kernel Notes**: Extract subject ID from filename using regex pattern. Files from subject 5 (ex05) may have missing data; verify subject count matches actual files. Use 5-second windows with 50% overlap as specified in the paper.

### Potential Task 1: Stimulus Language Classification (Native vs Non-native)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `misc`
- **Evidence**:
  - DOI: 10.1523/eneuro.0265.25.2025 — TriNet-MTL study training for stimulus language classification (native vs non-native) using sliding window segmentation
- **Kernel Notes**: Group auditory events by language type. Native songs include `auditory_native_song_in_ear` and `auditory_native_song_bone` (y=0). Non-native songs include `auditory_nonnative_song_in_ear` and `auditory_nonnative_song_bone` (y=1). Neutral music events should be excluded from this binary classification task.

### Potential Task 2: Device Modality Classification (In-ear vs Bone Conduction)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `misc`
- **Evidence**:
  - DOI: 10.1523/eneuro.0265.25.2025 — TriNet-MTL study training for device modality recognition (in-ear vs bone conduction) using sliding window segmentation
- **Kernel Notes**: Classify based on headphone type. In-ear: `auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear` (y=0). Bone: `auditory_native_song_bone`, `auditory_nonnative_song_bone` (y=1). Resting-state events should be excluded from this task.

### Classical Task 2: Auditory Condition Classification (6-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5, target_events = [`auditory_native_song_in_ear`, `auditory_nonnative_song_in_ear`, `auditory_neutral_music_in_ear`, `auditory_native_song_bone`, `auditory_nonnative_song_bone`, `auditory_neutral_music_bone`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `auditory_native_song_in_ear` | 0 | Native song, in-ear |
  | `auditory_nonnative_song_in_ear` | 1 | Non-native song, in-ear |
  | `auditory_neutral_music_in_ear` | 2 | Neutral music, in-ear |
  | `auditory_native_song_bone` | 3 | Native song, bone-conduction |
  | `auditory_nonnative_song_bone` | 4 | Non-native song, bone-conduction |
  | `auditory_neutral_music_bone` | 5 | Neutral music, bone-conduction |
- **Evidence**:
  
  - DOI: 10.13026/ps31 — fc50 — Dataset describes 6 auditory stimulus conditions (native/non-native/neutral × in-ear/bone)
- **Kernel Notes**: Exclude `ex05` files (uncoded experiment codes). The 6-class task distinguishes both stimulus type and headphone modality. (replaces Normal Task 1 from original analysis.md)

### Potential Task 3: Resting-State vs. Auditory Stimulus (epoch_by_long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 5.0 s, overlap = 2.5
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  MISC channel: `misc`
- **Evidence**:

- **Kernel Notes**: Not included in resting_eyes_open_noise_isolation: This event is not available in the dataset; it is reasonable to ignore it.

## Data Quality Notes

- Only 4 EEG channels (T7, F8, Cz, P4, per the OpenBCI Ganglion setup); spatial coverage is extremely limited.
- `ex05` files (subject 5 recordings in some conditions) retain raw experiment codes and should be excluded from condition-labeled classification, especially if performing analysis based on experimental conditions.
- Primary use case is biometric identification (same person across sessions), not condition classification; adapt label source accordingly.
- Some subjects may be missing recordings for certain experiment codes.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update
