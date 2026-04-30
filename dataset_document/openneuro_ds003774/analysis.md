# Music Listening Genre EEG Dataset (MUSIN-G)

**Dataset**: `openneuro_ds003774` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003774
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 260 | **Manual Review**: Pending
**Channels**: 129 | **Sampling Rate**: 1000 Hz

## Paradigm

Twenty participants listened to 12 music tracks spanning various genres (classical, jazz, rock, etc.) with eyes closed while high-density EEG was recorded using a 129-channel system. After each track, participants provided subjective ratings for familiarity and enjoyment on a 1-5 scale. The dataset supports EEG-based music genre classification, person identification as a biometric measure, and exploration of neural correlates of music preference and familiarity. Discrete event markers are embedded in the recordings including stimulus onsets, fixation cues, and behavioral responses.

## File Scan Result

> **Kernel SHA256**: `f30691bc53a2a28c00a2169a91162de693b2913d17a5ccd93b0b5b66ce3871e4`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `CELL` | 3380 | event | raw | Cell-level recording marker indicating segment boundaries within continuous EEG |
| `IBEG` | 2 | event | raw | Initialization beginning marker for recording session startup |
| `IEND` | 2 | event | raw | Initialization end marker confirming recording session initialization complete |
| `SESS` | 260 | event | raw | Session marker identifying individual recording sessions per subject-track |
| `TRSP` | 720 | event | raw | Track/transport segment marker indicating song segment or transition point |
| `bgin` | 620 | event | raw | Beginning marker denoting start of trial or recording segment |
| `boundary` | 400 | event | raw | Discontinuity boundary marker indicating data gaps or segment transitions |
| `clyp` | 260 | event | raw | Clip/playback marker indicating audio clip playback onset |
| `fxcl` | 340 | event | raw | Fixation cue marker prompting participant eye fixation |
| `fxnd` | 240 | event | raw | Fixation end marker indicating fixation period completion |
| `opyp` | 158 | event | raw | Opinion prompt marker initiating subjective rating response |
| `resp` | 480 | event | raw | Response marker indicating participant button press or rating submission |
| `stim` | 260 | event | raw | Music stimulus onset marker indicating track playback start |
| `stm+` | 240 | event | raw | Music stimulus offset marker indicating track playback end |
| `subject_id: sub-001` | 13 | event | raw | Subject identifier for participant 001 |
| `subject_id: sub-002` | 13 | event | raw | Subject identifier for participant 002 |
| `subject_id: sub-003` | 13 | event | raw | Subject identifier for participant 003 |
| `subject_id: sub-004` | 13 | event | raw | Subject identifier for participant 004 |
| `subject_id: sub-005` | 13 | event | raw | Subject identifier for participant 005 |
| `subject_id: sub-006` | 13 | event | raw | Subject identifier for participant 006 |
| `subject_id: sub-007` | 13 | event | raw | Subject identifier for participant 007 |
| `subject_id: sub-008` | 13 | event | raw | Subject identifier for participant 008 |
| `subject_id: sub-009` | 13 | event | raw | Subject identifier for participant 009 |
| `subject_id: sub-010` | 13 | event | raw | Subject identifier for participant 010 |
| `subject_id: sub-011` | 13 | event | raw | Subject identifier for participant 011 |
| `subject_id: sub-012` | 13 | event | raw | Subject identifier for participant 012 |
| `subject_id: sub-013` | 13 | event | raw | Subject identifier for participant 013 |
| `subject_id: sub-014` | 13 | event | raw | Subject identifier for participant 014 |
| `subject_id: sub-015` | 13 | event | raw | Subject identifier for participant 015 |
| `subject_id: sub-016` | 13 | event | raw | Subject identifier for participant 016 |
| `subject_id: sub-017` | 13 | event | raw | Subject identifier for participant 017 |
| `subject_id: sub-018` | 13 | event | raw | Subject identifier for participant 018 |
| `subject_id: sub-019` | 13 | event | raw | Subject identifier for participant 019 |
| `subject_id: sub-020` | 13 | event | raw | Subject identifier for participant 020 |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Normal Task 1: Music Genre Classification from Continuous EEG
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `genre_label: Deep House` | 1 | Music genre class 1 |
  | `genre_label: Indie` | 2 | Music genre class 2 |
  | `genre_label: Electronics` | 3 | Music genre class 3 |
  | `genre_label: New Age` | 4 | Music genre class 4 |
  | `genre_label: Electronic Dance` | 5 | Music genre class 5 |
  | `genre_label: Ambient` | 6 | Music genre class 6 |
  | `genre_label: Hindustani Classical` | 7 | Music genre class 7 |
  | `genre_label: Indian Semi-Classical` | 8 | Music genre class 8 |
  | `genre_label: Indian Folk` | 9 | Music genre class 9 |
  | `genre_label: Soft Jazz` | 10 | Music genre class 10 |
  | `genre_label: Goth Rock` | 11 | Music genre class 11 |
  | `genre_label: Progressive Instrumental Rock` | 12 | Music genre class 12 |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — MUSIN-G dataset paper describing 20 participants listening to 12 songs across 12 distinct genres with high-density EEG, enabling multi-class genre classification from neural responses
- **Kernel Notes**: Genre labels are embedded in BIDS filename/path structure (e.g., `sub-XXX_task-music_genre-DEEPHOUSE_*.vhdr`), requiring extraction and mapping to each file. Apply genre label from file-level metadata to all segments derived from that recording. Use `stim` (260) and `stm+` (240) events as anchors when available; otherwise segment from file start. Downsample to 250 Hz for computational efficiency per paper recommendation. The `clyp` (260) and `TRSP` (720) events may indicate track-specific boundaries requiring filtering during segmentation.

### Normal Task 2: Person Identification (Biometric EEG) from Music Listening
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 0.0 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `subject_id: sub-001` | 1 | Listener/Subject ID 1 |
  | `subject_id: sub-002` | 2 | Listener/Subject ID 2 |
  | `subject_id: sub-003` | 3 | Listener/Subject ID 3 |
  | `subject_id: sub-004` | 4 | Listener/Subject ID 4 |
  | `subject_id: sub-005` | 5 | Listener/Subject ID 5 |
  | `subject_id: sub-006` | 6 | Listener/Subject ID 6 |
  | `subject_id: sub-007` | 7 | Listener/Subject ID 7 |
  | `subject_id: sub-008` | 8 | Listener/Subject ID 8 |
  | `subject_id: sub-009` | 9 | Listener/Subject ID 9 |
  | `subject_id: sub-010` | 10 | Listener/Subject ID 10 |
  | `subject_id: sub-011` | 11 | Listener/Subject ID 11 |
  | `subject_id: sub-012` | 12 | Listener/Subject ID 12 |
  | `subject_id: sub-013` | 13 | Listener/Subject ID 13 |
  | `subject_id: sub-014` | 14 | Listener/Subject ID 14 |
  | `subject_id: sub-015` | 15 | Listener/Subject ID 15 |
  | `subject_id: sub-016` | 16 | Listener/Subject ID 16 |
  | `subject_id: sub-017` | 17 | Listener/Subject ID 17 |
  | `subject_id: sub-018` | 18 | Listener/Subject ID 18 |
  | `subject_id: sub-019` | 19 | Listener/Subject ID 19 |
  | `subject_id: sub-020` | 20 | Listener/Subject ID 20 |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — Dataset paper confirming 20 participants with 13 files each (12 tracks + 1 baseline), enabling person identification as a biometric task from neural responses to music
- **Kernel Notes**: Subject ID inherently available from `subject_id` events (13 per subject). Extract 5-second non-overlapping windows from continuous EEG segments. Each subject has 13 recordings; aggregate all segments across tracks. The `boundary` (400) events indicate discontinuities—apply appropriate handling during epoch extraction. Exclude or flag baseline recordings if domain-specific model is desired.

### Potential Task 1: Music Familiarity Rating Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `familiarity_rating` | continuous [1.0–5.0] | Post-recording familiarity rating per song; 1=highest familiarity, 5=lowest |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — Dataset paper describing post-recording familiarity ratings collected on 1–5 scale for each of 12 songs per participant
- **Kernel Notes**: Familiarity ratings are behavioral metadata collected post-recording, not embedded as EEG events. Extract genre labels from filename metadata and merge with behavioral ratings from accompanying TSV files. Each song has one familiarity rating applied to all derived EEG segments.

### Potential Task 2: Music Enjoyment Rating Regression from EEG
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 5.0 s, overlap = 2.5 s
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `enjoyment_rating` | continuous [1.0–5.0] | Post-recording enjoyment rating per song; 1=highest enjoyment, 5=lowest |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — Dataset paper describing post-recording enjoyment ratings collected on 1–5 scale for each of 12 songs per participant
- **Kernel Notes**: Enjoyment ratings are behavioral metadata not present in EEG events. Map ratings from behavioral TSV files to corresponding recordings. Apply same genre label to segments as in Task 1. Consider multi-task learning with familiarity ratings if combining tasks.

### Potential Task 3: Fine-Grained Continuous EEG Segmentation
- **Task Type**: feature_extraction
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 1.0 s
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stim` | continuous | Music stimulus onset anchor |
  | `stm+` | continuous | Music stimulus offset confirmation |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.108663 — Dataset supports various epoch lengths for frequency band analysis and feature extraction
- **Kernel Notes**: Use 2-second windows with 50% overlap for fine-grained frequency band feature extraction (delta, theta, alpha, beta, gamma). The `TRSP` (720) events may indicate track transitions within recordings requiring additional segmentation logic. The `clyp` (260) events likely indicate clip boundaries that should be respected during segmentation.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
