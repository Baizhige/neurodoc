# EEG dataset for speech decoding

**Dataset**: `openneuro_ds006104` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006104
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 80 | **Channels**: 62 | **Sampling Rate**: 2000 Hz

## Paradigm

A phoneme discrimination task where participants listened to speech sounds - including single phonemes, phoneme pairs, and words - while undergoing transcranial magnetic stimulation (TMS) to test the role of speech motor cortex in auditory speech perception. Subjects provided button-press responses after each sound. The dataset supports decoding of speech perception from TMS-EEG.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `TMS` | 29260 | event | raw | TMS pulse delivery |
| `stimulus` | 29260 | event | raw | Auditory speech stimulus onset |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Phoneme Category Classification (Consonant vs Vowel)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `consonant` | 0 | Consonant phoneme stimulus |
  | `vowel` | 1 | Vowel phoneme stimulus |
- **Super Meta Notes**: Derived from raw event `stimulus` by mapping stimulus onset to phoneme category labels based on stimulus presentation logs. Kernel step: Load stimulus metadata (CSV/log) and map each stimulus onset timestamp to its phonetic category (consonant/vowel).
- **Evidence**:
  - DOI: 10.1038/s41597-025-05187-2 — classifies consonant vs vowel phonemes from TMS-EEG during speech perception
- **Kernel Notes**: Load phoneme label file; match stimulus timestamps to phoneme identity; extract consonant/vowel category. (replaces Classical Task 3 from original analysis.md)

### Classical Task 2: Word Type Classification (Real vs Pseudoword)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `real_word` | 0 | Real word stimulus |
  | `pseudoword` | 1 | Pseudoword stimulus |
- **Super Meta Notes**: Derived from raw event `stimulus` by mapping stimulus onset to word type labels based on stimulus presentation logs. Kernel step: Load stimulus metadata and classify each stimulus as real word or pseudoword.
- **Evidence**:
  - DOI: 10.1038/s41597-025-05187-2 — classifies real words vs pseudowords from TMS-EEG during speech perception
- **Kernel Notes**: Load word-type label file; match stimulus timestamps to word/pseudoword identity. (replaces Classical Task 2 from original analysis.md)

### Classical Task 3: Single Phoneme Identity Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `/b/` | 0 | bilabial stop |
  | `/p/` | 1 | bilabial stop (voiceless) |
  | `/d/` | 2 | alveolar stop |
  | `/t/` | 3 | alveolar stop (voiceless) |
  | `/s/` | 4 | alveolar fricative |
  | `/z/` | 5 | alveolar fricative (voiced) |
  | `/i/` | 6 | high front vowel |
  | `/ɛ/` | 7 | mid front vowel |
  | `/ɑ/` | 8 | low back vowel |
  | `/u/` | 9 | high back vowel |
  | `/oʊ/` | 10 | diphthong |
- **Super Meta Notes**: Derived from raw event `stimulus` by mapping stimulus onset to specific phoneme identity labels based on stimulus presentation logs. Kernel step: Load phoneme identity mapping; match each stimulus timestamp to its phoneme label.
- **Evidence**:
  - DOI: 10.1038/s41597-025-05187-2 — classifies single phoneme identity from TMS-EEG ERPs
- **Kernel Notes**: Requires phoneme label file with stimulus-to-phoneme mapping. (replaces Classical Task 1 from original analysis.md)

### Potential Task 1: TMS vs Stimulus Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Binary classification (TMS vs stimulus). TMS pulses produce large artifacts; apply TMS artifact rejection before epoching.

 | Event | y | Meaning |
 |-------|---|---------|
 | `TMS` | 0 | TMS pulse |
 | `stimulus` | 1 | Speech stimulus onset |

## Data Quality Notes

- Very high sampling rate (2000 Hz); downsample to 500 Hz for most analyses.
- TMS pulses produce large EEG artifacts requiring specialized artifact removal.
- Apply bandpass filter (1-80 Hz) after TMS artifact correction.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review