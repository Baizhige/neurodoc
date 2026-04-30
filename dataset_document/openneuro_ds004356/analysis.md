# Subcortical responses to music and speech are alike while cortical responses diverge

**Dataset**: `openneuro_ds004356` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds004356
**Category**: Sensory/Response | **Subjects**: 22 | **Files (Completed)**: 24 | **Manual Review**:
**Channels**: 34 | **Sampling Rate**: 10000 Hz

## Paradigm

The study measures subcortical Auditory Brainstem Responses (ABR) and cortical auditory evoked potentials to continuous music and speech stimuli using a deconvolution method. Participants passively listened to different audio categories while continuous EEG was recorded at 10,000 Hz from 34 channels. The paradigm compares neural encoding of music versus speech at both subcortical and cortical levels, with click trains serving as a control condition for ABR baseline measurement.

## File Scan Result

> **Kernel SHA256**: `5c95da9f7885cfea812f8e9ae73c60a937cea95a8f3a1e8669e6afc53d8ab476`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 12733 | event | raw | Stimulus onset: acoustic music |
| `Stimulus/S  2` | 10771 | event | raw | Stimulus onset: classical music |
| `Stimulus/S  4` | 69798 | event | raw | Stimulus onset: jazz music |
| `Stimulus/S  8` | 51688 | event | raw | Stimulus onset: English audio book speech |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Music vs Speech Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s, tmax = 12 s, overlap = 0.0, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  4`, `Stimulus/S  8`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | acoustic music |
  | `Stimulus/S  2` | 0 | classical music |
  | `Stimulus/S  4` | 0 | jazz music |
  | `Stimulus/S  8` | 1 | English audio book speech |
- **Evidence**:
  - 10.1038/s41598-023-50438-0 — Published paper explicitly describes binary classification of music vs speech from continuous 12-second stimulus blocks, with three music genres mapped to one class and English audiobook speech to the other.
  - 10.1101/2022.10.14.512309 — Preprint confirms experimental design: 12-second continuous stimulus blocks with tmin=0s, tmax=12s, no overlap, and binary music vs speech classification paradigm.
- **Notes**: All three music genres (acoustic, classical, jazz) are merged into y=0 (music class) and English audiobook speech is y=1 (speech class), reflecting the binary music vs speech classification described in the source papers. The event IDs use binary-coded trigger values (1, 2, 4, 8) as documented in the dataset's events.json sidecar.

### Potential Task 1: Music Genre 3-Class Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: `tmin = 0 s *, tmax = 12 s *, overlap = 0.0 *, target_events = [`Stimulus/S  1`, `Stimulus/S  2`, `Stimulus/S  4`]`
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `Stimulus/S  1` | 0 | acoustic music |
  | `Stimulus/S  2` | 1 | classical music |
  | `Stimulus/S  4` | 2 | jazz music |
- **Evidence**:
  - task-MusicvsSpeech_events.json — Documents trial_type Levels: '1': 'acoustic', '2': 'classical', '4': 'jazz', with value field clarifying 'acoustic music', 'classical music', 'jazz music'
  - README — Describes 12-second stimulus clips from six music genres and six speech types, 40 trials each
  - sub-01_task-MusicvsSpeech_events.tsv — Shows consistent 12-second duration for music/speech trials with stim_file entries (e.g., 'acoustic/acoustic000.wav', 'classical/classical002.wav', 'jazz/jazz025.wav')
- **Notes**: Three music genres (acoustic, classical, jazz) selected from the broader 12-type stimulus set to form a balanced 3-class classification task. Each genre has 40 trials of 12-second continuous stimulation. Event IDs use binary-coded trigger values (1, 2, 4) corresponding to bits in the trial encoding scheme. Epoch timing inferred from stimulus duration; no explicit genre-classification paradigm found in literature, but event structure fully supports this potential task.

## Data Quality Notes

- No known data quality issues.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update
