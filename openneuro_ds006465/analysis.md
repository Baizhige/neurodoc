# 3M-CPSEED: EEG Dataset for Chinese Pinyin Production in Overt, Silent-Intended, and Imagined Speech

**Dataset**: `openneuro_ds006465` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006465
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 84 | **Channels**: 33 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed three modes of speech production - overt (spoken aloud), silent-intended (mouthed without sound), and imagined (mental speech without movement) - for specific Chinese Pinyin sounds including initials and finals. The dataset enables comparison of neural signatures across overt, silent, and imagined speech conditions. Each trial consisted of a visual cue (stimulus_presentation) followed by a production phase and a response confirmation. Numeric codes 1-10 encode specific phoneme or condition types.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus_presentation` | 42 | event | raw | Visual cue onset prompting speech production |
| `1` | 302 | event | raw | Phoneme/condition code 1 |
| `2` | 200 | event | raw | Phoneme/condition code 2 |
| `3` | 200 | event | raw | Phoneme/condition code 3 |
| `4` | 200 | event | raw | Phoneme/condition code 4 |
| `5` | 200 | event | raw | Phoneme/condition code 5 |
| `6` | 200 | event | raw | Phoneme/condition code 6 |
| `7` | 200 | event | raw | Phoneme/condition code 7 |
| `8` | 200 | event | raw | Phoneme/condition code 8 |
| `9` | 200 | event | raw | Phoneme/condition code 9 |
| `10` | 200 | event | raw | Phoneme/condition code 10 |
| `response` | 84 | event | raw | Participant response / confirmation |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: Speech Mode Classification (Overt/Silent/Imagined)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 3.0 s *, tmax = 5.0 s *, target_events = [`stimulus_presentation`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | Speak window (3-5s, 5-7s, 7-9s) | 0 | Overt speech (spoken aloud) |
  | Silently articulated window (10-12s, 12-14s, 14-16s) | 1 | Silent-intended (mouthed without sound) |
  | Imagine window (17-19s, 19-21s, 21-23s) | 2 | Imagined (mental speech) |
- **Super Meta Notes**: Derived from raw event `stimulus_presentation` by using temporal position within trial structure. Kernel step: for each trial, extract 2-second epochs at positions [3-5s], [5-7s], [7-9s] (overt), [10-12s], [12-14s], [14-16s] (silent), [17-19s], [19-21s], [21-23s] (imagined) and assign label based on time window.
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — validates 3M-CPSEED with EEGNet-based binary classification achieving 60-73% accuracy for speech mode discrimination
- **Kernel Notes**: Extract epochs anchored at stimulus_presentation cue; derive speech mode label from epoch timing relative to trial structure (9 epochs per trial: 3 per mode). Apply bandpass filter 0.5-40 Hz before epoching.

### Classical Task 2: Pinyin Syllable Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s *, tmax = 1.0 s *, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Pinyin syllable code 1 |
  | `2` | 1 | Pinyin syllable code 2 |
  | `3` | 2 | Pinyin syllable code 3 |
  | `4` | 3 | Pinyin syllable code 4 |
  | `5` | 4 | Pinyin syllable code 5 |
  | `6` | 5 | Pinyin syllable code 6 |
  | `7` | 6 | Pinyin syllable code 7 |
  | `8` | 7 | Pinyin syllable code 8 |
  | `9` | 8 | Pinyin syllable code 9 |
  | `10` | 9 | Pinyin syllable code 10 |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — validates >55% accuracy for pinyin syllable pairwise classification
- **Kernel Notes**: Numeric codes 1-10 correspond to specific Pinyin syllables (a,i,u,ü,m,f,j,l,k,ch with pairings). Extract epochs around numeric trigger events; exclude `response` events from classification.

### Potential Task 1: Speech Production Mode Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric codes 1-10 correspond to specific Pinyin sounds or speech modes; decode from events.tsv. `response` is a motor response event. Some files show only numeric triggers; mixed annotation format across subjects.

 | Event | y | Meaning |
 |-------|---|---------|
 | `stimulus_presentation` | 0 | Visual cue for speech production |
 | `1` | 1 | Phoneme/condition code 1 |
 | `5` | 2 | Phoneme/condition code 5 |
 | `6` | 3 | Phoneme/condition code 6 |
 | `7` | 4 | Phoneme/condition code 7 |
 | `4` | 5 | Phoneme/condition code 4 |
 | `3` | 6 | Phoneme/condition code 3 |
 | `2` | 7 | Phoneme/condition code 2 |
 | `10` | 8 | Phoneme/condition code 10 |
 | `8` | 9 | Phoneme/condition code 8 |
 | `9` | 10 | Phoneme/condition code 9 |

## Data Quality Notes

- Some files show only numeric triggers while others include `stimulus_presentation`; mixed annotation format across sessions.
- Derivatives (preprocessed) files available alongside raw data.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection before epoching.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review