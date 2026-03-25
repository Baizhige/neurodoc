# SJTU Emotion EEG Dataset (SEED)

**Dataset**: `other_seed` | **Year**: 2015 | **URL**: https://bcmi.sjtu.edu.cn<LOCAL_HOME>/
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 81 | **Channels**: 62 | **Sampling Rate**: 1000 Hz

## Paradigm

The SEED (SJTU Emotion EEG Dataset) was collected from 15 subjects who watched 15 emotional film clips (positive, neutral, negative) across three sessions (Zheng & Lu, 2015). EEG was recorded from 62 channels using an ESI NeuroScan system (Neuroscan cap) at 1000 Hz. Fifteen emotional video clips (~4 minutes each) were shown in each session, with sessions repeated on different days (up to 3 sessions per subject). Valence labels (+1 positive, 0 neutral, -1 negative) for each clip are stored in separate `*_label.mat` files; they are **not embedded** in the `.cnt` EEG recordings. The kernel does not extract emotion labels from EEG annotations; labels must be loaded externally.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://bcmi.sjtu.edu.cn<LOCAL_HOME>/

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0` | ~81 | admin | raw | File-level marker from `.cnt` format (no experimental meaning) |
| `255` | rare | admin | raw | End-of-file or reset marker in `.cnt` format |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
>
> **Critical**: Emotion valence labels (+1, 0, -1) are stored in companion `*_label.mat` files, NOT in the EEG event annotations. Events `0` and `255` are format-level markers with no experimental significance.

## Tasks

### Primary Task 1: Binary Emotion Classification (Positive vs Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 2.0 s, target_events = [`positive`, `negative`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `positive` | 0 | Positive valence (+1 from SEED label files) |
  | `negative` | 1 | Negative valence (-1 from SEED label files) |
- **Super Meta Notes**: Labels obtained from SEED `*_label.mat` files (+1 positive, -1 negative); neutral trials discarded for binary classification; labels aligned with EEG epochs post-hoc. Uses middle 1-minute portion of each 4-minute trial.
- **Evidence**:
  - DOI: 10.3389/fnins.2018.00162 — Binary cross-subject emotion classification (positive vs negative) using 4-s sliding window with 2-s overlap from middle 1-minute segment of each 4-min trial
- **Kernel Notes**: Segment EEG into 4-s windows with 2-s overlap; only use epochs from middle 1-minute of each 4-minute video clip; align with external label files for binary valence labels; exclude neutral (0) trials.

### Primary Task 2: Three-Class Emotion Valence Classification (Positive/Neutral/Negative)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s *, overlap = 0.0 s *, target_events = [`positive`, `neutral`, `negative`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `positive` | 0 | Positive valence (+1 from SEED label files) |
  | `neutral` | 1 | Neutral valence (0 from SEED label files) |
  | `negative` | 2 | Negative valence (-1 from SEED label files) |
- **Super Meta Notes**: Labels derived from experimental stimulus protocol (film clips designed to elicit specific emotions) and participant self-reports; not from EEG event markers. Uses valence categories assigned to each video clip.
- **Evidence**:
  - DOI: 10.1007/s12559-025-10516-z — Three-class emotion valence classification using entire 4-min video clips; fuzzy linguistic summarization with Russell's circumplex model
- **Kernel Notes**: Process entire 4-min video clip periods; align epochs with valence labels from external `*_label.mat` files by trial order; may optionally downsample to 200 Hz as in original paper.

### Normal Task 1: Emotion Valence Classification - 3-Class (epoch_by_segmentation + external labels)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: length = 4.0 s, overlap = 2.0 s (within each video clip window)
- **Label Route**: `Annotation`
- **Target Definition**: N/A from EEG annotations - apply labels post-hoc from `*_label.mat`:
- **Notes**: Segment the EEG into fixed windows during each video clip period. Map each epoch to the clip's valence label from the corresponding `*_label.mat` file. The kernel records subject ID and session ID in the description field to help align with label files.

| Label | y | Meaning |
|-------|---|---------|
| `+1` | 0 | Positive emotion |
| `0` | 1 | Neutral emotion |
| `-1` | 2 | Negative emotion |


### Normal Task 2: Binary Emotion Classification - Positive vs. Negative (epoch_by_segmentation)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation`
- **Epoch Parameters**: Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Needs verification.
- **Notes**: Use positive (y=0) and negative (y=2) labels only; discard neutral trials.

## Data Quality Notes

- **Emotion labels are not embedded in EEG files**; they must be loaded from companion `*_label.mat` files and aligned with EEG epochs by trial order.
- EEG events `0` and `255` are file-format markers; exclude from all analyses.
- 3 sessions per subject on different days; within-session and cross-session analyses are common.
- 15 video clips per session x 3 sessions x 15 subjects = 675 trials total.
- NeuroScan `.cnt` format; 62-channel standard 10-20 EEG montage.

## References

- **Reference**: Zheng W-L, Lu B-L (2015). Investigating Critical Frequency Bands and Channels for EEG-based Emotion Recognition with Deep Neural Networks. *IEEE Trans. Autonomous Mental Development*, 7(3), 162-175. https://bcmi.sjtu.edu.cn<LOCAL_HOME>/
