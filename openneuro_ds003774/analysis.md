# Music Listening Genre EEG Dataset (MUSIN-G)

**Dataset**: `openneuro_ds003774` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003774
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 260
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Twenty participants listened to 12 music tracks spanning various genres (classical, jazz, rock, etc.) with eyes closed while high-density EEG was recorded. After each track, participants provided subjective ratings for familiarity and enjoyment. The dataset supports EEG-based music genre classification and exploration of neural correlates of music preference and familiarity. No discrete event markers were embedded in the EEG recording.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; continuous music listening EEG |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Music Genre Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.5 *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Deep House` | 1 | Music genre class 1 |
  | `Indie` | 2 | Music genre class 2 |
  | `Electronics` | 3 | Music genre class 3 |
  | `New Age` | 4 | Music genre class 4 |
  | `Electronic Dance` | 5 | Music genre class 5 |
  | `Ambient` | 6 | Music genre class 6 |
  | `Hindustani Classical` | 7 | Music genre class 7 |
  | `Indian Semi-Classical` | 8 | Music genre class 8 |
  | `Indian Folk` | 9 | Music genre class 9 |
  | `Soft Jazz` | 10 | Music genre class 10 |
  | `Goth Rock` | 11 | Music genre class 11 |
  | `Progressive Instrumental Rock` | 12 | Music genre class 12 |
- **Super Meta Notes**: Derived from file-level song metadata (genre) by extracting sliding windows from continuous EEG per song recording. Kernel step: Parse genre label from filename/path, then apply to all segments from that file. Also collect post-recording familiarity (1-5) and enjoyment (1-5) ratings as auxiliary labels if available.
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — Data in Brief paper describing MUSIN-G dataset with 20 participants listening to 12 songs of different genres, enabling multi-class music genre classification from high-density EEG
- **Kernel Notes**: Since no event markers exist in raw EEG, use segmentation. Downsample to 250Hz as per paper. Filter into frequency bands (delta, theta, alpha, beta, gamma) for feature extraction. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Listener Identity / Person Identification from EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.0 *
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `sub-01` | 1 | Listener/Subject ID 1 |
  | `sub-02` | 2 | Listener/Subject ID 2 |
  | ... | ... | ... |
  | `sub-20` | 20 | Listener/Subject ID 20 |
- **Evidence**:
  - DOI: 10.36227/techrxiv.20502423.v2 — Research using Random Forest classifiers on 5-second epochs from MUSIN-G, achieving 95.1% accuracy for person identification (biometric identification of which of 20 participants produced the neural responses)
- **Kernel Notes**: Extract 5-second non-overlapping windows from continuous EEG, filter into standard frequency bands, train classifier to identify listener identity. Subject ID is inherent from file metadata (filename contains subject identifier).

### Potential Task 1: Continuous EEG segmentation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `event`
- **Target Definition**: N/A (null (music genre tags need to be appended after parsing from events.tsv))
- **Notes**: 260 files for 20 subjects (13 files each: 12 tracks + 1 baseline). Music genre labels are file-level metadata; apply as segment-level labels for genre classification. High-density 129-channel EEG at 1000 Hz.

## Data Quality Notes

- No EEG trigger events present; music onset timing not embedded in EEG.
- 260 files likely correspond to individual music track recordings; genre label per file.
- High-density 129-channel EEG; high computational requirements.
- Eyes-closed listening; fewer motion artifacts but possible drowsiness.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review