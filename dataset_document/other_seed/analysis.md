# SJTU Emotion EEG Dataset (SEED)

**Dataset**: `other_seed` | **Year**: 2015 | **URL**: https://bcmi.sjtu.edu.cn/home/seed/
**Category**: High-level Mental | **Subjects**: 15 | **Files (Completed)**: 81 | **Channels**: 62 | **Sampling Rate**: 1000 Hz | **Manual Review**:

## Paradigm

The SEED (SJTU Emotion EEG Dataset) was collected from 15 subjects who watched 15 emotional film clips (positive, neutral, negative) across three sessions (Zheng & Lu, 2015). EEG was recorded from 62 channels using an ESI NeuroScan system (Neuroscan cap) at 1000 Hz. Fifteen emotional video clips (~4 minutes each) were shown in each session, with sessions repeated on different days (up to 3 sessions per subject). Valence labels (+1 positive, 0 neutral, -1 negative) for each clip are stored in separate `*_label.mat` files; they are **not embedded** in the `.cnt` EEG recordings. The kernel does not extract emotion labels from EEG annotations; labels must be loaded externally.

## File Scan Result

> **Kernel SHA256**: `4077512da7329b9fac63d2a2e6f7d61ec825919cdf2cd9a8aeb3b5c4f756a39a`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `0` | 2 | admin | raw | System trigger code |
| `255` | 4 | admin | raw | System trigger code |
| `KeyPad Response 1` | 4 | event | raw | Trial phase onset: KeyPad Response 1 |
| `KeyPad Response 13` | 2 | event | raw | Trial phase onset: KeyPad Response 13 |
| `KeyPad Response 15` | 8 | event | raw | Trial phase onset: KeyPad Response 15 |
| `KeyPad Response 4` | 2 | event | raw | Trial phase onset: KeyPad Response 4 |
| `KeyPad Response 7` | 2 | event | raw | Trial phase onset: KeyPad Response 7 |


### MISC Label Summary
| Channel | Source | Meta | Notes |
|---|---|---|---|
| `M1` | native (raw misc in EEG file) | raw | Verify channel role and unit |
| `M2` | native (raw misc in EEG file) | raw | Verify channel role and unit |
- **Candidate Labels**: `M1`, `M2`

### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: binary positive vs negative emotion classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 *, target_events = []
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `emotion_valence_binary` | `+1` | 0 | positive emotion |
  | `emotion_valence_binary` | `-1` | 1 | negative emotion |
- **Evidence**:
  - https://bcmi.sjtu.edu.cn/home/seed/ — SEED dataset homepage describing emotion induction via film clips with positive/neutral/negative labels
  - 10.3389/fnins.2018.00162 — SEED paper establishing 3-class valence paradigm; binary positive/negative reduction is standard derivative analysis
- **Notes**: Kernel must derive `emotion_valence_binary` from `events.tsv:label` (sourced from *_label.mat files). Load label file, filter to +1 and -1 trials excluding 0/neutral, then broadcast binary labels to 4-second sliding windows with 2-second overlap. Same segmentation approach as 3-class task but with cleaner binary discrimination boundary. Reduces from 15 to ~10 trials per session depending on label distribution.

### Potential Task 1: binary high vs low arousal emotion classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4 s *, overlap = 2.0 *, target_events = []
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `emotion_arousal_binary` | 0 | 0 | low arousal (neutral valence) |
  | `emotion_arousal_binary` | 1 | 1 | high arousal (positive or negative valence) |
- **Evidence**:
  - 10.1007/s12559-025-10516-z — Russell's circumplex model cited as theoretical framework for SEED emotion analysis
  - Preprocessed_EEG/readme.txt — confirms three valence labels: 1=positive, 0=neutral, -1=negative
- **Notes**: Derived misc channel implementing Russell's circumplex model: valence labels {+1, -1} (positive/negative emotions) both imply higher arousal than neutral (0), collapsed to binary arousal. Kernel must load *_label.mat files, map valence to arousal, and broadcast per-trial labels to all segments within each trial.

### Potential Task 2: Keypad Response Detection
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.5 s *, tmax = 1.0 s *, target_events = [`KeyPad Response 1`, `KeyPad Response 4`, `KeyPad Response 7`, `KeyPad Response 13`, `KeyPad Response 15`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---------|
  | `KeyPad Response 1` | 0 | Trial phase onset: KeyPad Response 1 |
  | `KeyPad Response 4` | 1 | Trial phase onset: KeyPad Response 4 |
  | `KeyPad Response 7` | 2 | Trial phase onset: KeyPad Response 7 |
  | `KeyPad Response 13` | 3 | Trial phase onset: KeyPad Response 13 |
  | `KeyPad Response 15` | 4 | Trial phase onset: KeyPad Response 15 |
- **Evidence**:
- **Notes**: Five-class classification of distinct keypad button press responses during emotion viewing task. Highly imbalanced class distribution (Response 15: 8 occurrences; others: 2-4 each). No semantic mapping of keypad numbers to response meanings was found in dataset documentation. The epoch window (-0.5 to 1.0s) targets motor/response-related ERP components including readiness potential and post-response processing. Consider merging classes or treating as binary response vs. non-response if sample size proves insufficient.

## Data Quality Notes

- Emotion valence labels (+1, 0, -1) are stored in external `*_label.mat` files and are **not embedded** in raw `.cnt` EEG recordings; kernel must implement external label loading and alignment by subject/session ID.
- Event structure in raw files contains only sparse keypad response markers (`KeyPad Response 1/4/7/13/15`) and system trigger codes (`0`, `255`); no trial onset or emotion condition markers are present in the EEG event stream.
- Keypad response events are highly imbalanced (Response 15: 8 occurrences; others: 2-4 each), limiting statistical power for response classification tasks.
- No semantic mapping of keypad numbers to actual response meanings was found in dataset documentation.
- `age`, `sex`, and `device` fields are missing from file metadata; demographic and equipment information must be inferred from the original SEED publication.
- MISC channels `M1` and `M2` are present in raw files but their roles (reference, EOG, or other) and units require verification.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
