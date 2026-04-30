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

### Potential Task 1: Fine-Grained Continuous EEG Segmentation
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
