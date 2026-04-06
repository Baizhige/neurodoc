# SJTU Emotion EEG Dataset (SEED)

**Dataset**: `other_seed` | **Year**: 2015 | **URL**: https://bcmi.sjtu.edu.cn/home/seed/
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 81 | **Channels**: 62 | **Sampling Rate**: 1000 Hz

## Paradigm

The SEED (SJTU Emotion EEG Dataset) was collected from 15 subjects who watched 15 emotional film clips (positive, neutral, negative) across three sessions (Zheng & Lu, 2015). EEG was recorded from 62 channels using an ESI NeuroScan system (Neuroscan cap) at 1000 Hz. Fifteen emotional video clips (~4 minutes each) were shown in each session, with sessions repeated on different days (up to 3 sessions per subject). Valence labels (+1 positive, 0 neutral, -1 negative) for each clip are stored in separate `*_label.mat` files; they are **not embedded** in the `.cnt` EEG recordings. The kernel does not extract emotion labels from EEG annotations; labels must be loaded externally.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0` | ~81 | admin | raw | File-level marker from `.cnt` format (no experimental meaning) |
| `255` | rare | admin | raw | End-of-file or reset marker in `.cnt` format |

>
> **Critical**: Emotion valence labels (+1, 0, -1) are stored in companion `*_label.mat` files, NOT in the EEG event annotations. Events `0` and `255` are format-level markers with no experimental significance.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: Three-class Emotion Valence Classification (Positive/Neutral/Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 2.0 s *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Label | y | Meaning |
  |-------|---|---------|
  | `positive` | 0 | Positive emotion (valence +1) |
  | `neutral` | 1 | Neutral emotion (valence 0) |
  | `negative` | 2 | Negative emotion (valence -1) |
- **Super Meta Notes**: Derived from experimental stimulus protocol (film clips designed to elicit specific emotions). Labels stored in companion `*_label.mat` files (+1 positive, 0 neutral, -1 negative). Kernel must align EEG epochs with label files by subject ID and session ID (trial order within each session).
- **Evidence**:
  - DOI: 10.1007/s12559-025-10516-z — Fuzzy linguistic summarization with Russell's circumplex model achieved 80% accuracy classifying SEED EEG into three valence categories using frontal alpha/beta bands.
  - DOI: 10.3389/fnins.2018.00162 — Used 4-s sliding window with 2-s overlap from middle 1-minute of each 4-min trial for 3-class emotion recognition.
- **Kernel Notes**: Segment continuous EEG into 4-s windows with 2-s overlap. For each window, record subject ID and session ID. Load valence labels from corresponding `*_label.mat` file and map: +1→positive (y=0), 0→neutral (y=1), -1→negative (y=2). (replaces Classical Task 1 from original analysis.md)

### Classical Task 2: Binary Emotion Classification (Positive vs Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 2.0 s *
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Label | y | Meaning |
  |-------|---|---------|
  | `positive` | 0 | Positive emotion (valence +1) |
  | `negative` | 1 | Negative emotion (valence -1) |
- **Super Meta Notes**: Derived from SEED label files (+1 positive, -1 negative). Neutral trials (valence 0) discarded. Kernel aligns EEG epochs with external label files by subject and session.
- **Evidence**:
  - DOI: 10.3389/fnins.2018.00162 — Binary cross-subject emotion classification (positive vs negative) using 4-s sliding window with 2-s overlap from middle 1-minute segment of each 4-minute trial, achieving cross-subject generalization.
- **Kernel Notes**: Same segmentation as Classical Task 1, but filter to only positive (y=0) and negative (y=1) classes. Neutral labels are excluded.

### Potential Task 1: Emotion Valence Classification - 3-Class (epoch_by_segmentation + external labels)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 2.0 s
- **Label Route**: `event`
- **Target Definition**: N/A from EEG annotations - apply labels post-hoc from `*_label.mat`:
- **Notes**: Segment the EEG into fixed windows during each video clip period. Map each epoch to the clip's valence label from the corresponding `*_label.mat` file. The kernel records subject ID and session ID in the description field to help align with label files.

| Label | y | Meaning |
|-------|---|---------|
| `+1` | 0 | Positive emotion |
| `0` | 1 | Neutral emotion |
| `-1` | 2 | Negative emotion |

### Potential Task 2: Binary Emotion Classification - Positive vs. Negative (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 2.0 s
- **Label Route**: `event`
- **Target Definition**: Needs verification.
- **Notes**: Use positive (y=0) and negative (y=2) labels only; discard neutral trials.

## Data Quality Notes

- **Emotion labels are not embedded in EEG files**; they must be loaded from companion `*_label.mat` files and aligned with EEG epochs by trial order.
- EEG events `0` and `255` are file-format markers; exclude from all analyses.
- 3 sessions per subject on different days; within-session and cross-session analyses are common.
- 15 video clips per session x 3 sessions x 15 subjects = 675 trials total.
- NeuroScan `.cnt` format; 62-channel standard 10-20 EEG montage.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review