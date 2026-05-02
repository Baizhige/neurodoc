# EEG dataset for speech decoding

**Dataset**: `openneuro_ds006104` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006104
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 80 | **Channels**: 62 | **Sampling Rate**: 2000 Hz | **Manual Review**: Pending

## Paradigm

A phoneme discrimination task where participants listened to speech sounds—including single phonemes, phoneme pairs, and words—while undergoing transcranial magnetic stimulation (TMS) to test the role of speech motor cortex in auditory speech perception. Subjects provided button-press responses after each sound. The dataset supports decoding of speech perception from TMS-EEG at a high 2000 Hz sampling rate.

## File Scan Result

> **Kernel SHA256**: `47c3f681b0582d6ebfffde103e500959e4e49dc6560e4e9dd72900c51ad9ef39`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `TMS` | 14630 | event | raw | TMS pulse delivery |
| `event_131071` | 9116 | event | raw | Button press response |
| `event_2` | 4450 | event | raw | Response event (secondary) |
| `event_47186` | 41 | event | raw | Novelty/oddball marker |
| `event_66406` | 1 | event | raw | Unique trial marker |
| `event_67985` | 3 | event | raw | Rare condition marker |
| `event_72857` | 3 | event | raw | Rare condition marker |
| `event_77864` | 1 | event | raw | Unique trial marker |
| `stimulus` | 14630 | event | raw | Auditory speech stimulus onset |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | missing | N/A |
| `device` | missing | N/A |

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
- **Super Meta Notes**: Labels derived from stimulus presentation logs mapping phoneme categories to stimulus onset events. Requires loading external phoneme category file to map each `stimulus` event to consonant/vowel label.
- **Evidence**:
  - DOI: 10.1038/s41597-025-05187-2 — classifies consonant vs vowel phonemes from TMS-EEG during speech perception
- **Kernel Notes**: Load phoneme category label file; match stimulus timestamps to phoneme identity; extract consonant/vowel category. Apply TMS artifact rejection before feature extraction.

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
- **Super Meta Notes**: Labels derived from stimulus presentation logs mapping word types to stimulus onset events. Requires loading external word-type label file to classify each `stimulus` event.
- **Evidence**:
  - DOI: 10.1038/s41597-025-05187-2 — classifies real words vs pseudowords from TMS-EEG during speech perception
- **Kernel Notes**: Load word-type label file; match stimulus timestamps to word/pseudoword identity. The 2000 Hz sampling rate provides sufficient temporal resolution for lexical processing effects.

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
- **Super Meta Notes**: Labels derived from stimulus presentation logs mapping phoneme identity to stimulus onset events. Requires loading phoneme identity mapping file with all 11 phoneme classes.
- **Evidence**:
  - DOI: 10.1038/s41597-025-05187-2 — classifies single phoneme identity from TMS-EEG ERPs
- **Kernel Notes**: Requires phoneme label file with stimulus-to-phoneme mapping. Epoch parameters capture N100/P200 components relevant for phoneme discrimination. TMS artifacts should be addressed before feature extraction.

### Potential Task 1: TMS vs Stimulus Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`TMS`, `stimulus`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `TMS` | 0 | TMS pulse |
  | `stimulus` | 1 | Speech stimulus onset |
- **Evidence**: Equal event counts (14630 each) indicate systematic 1:1 pairing. Task is supported by paradigm logic; TMS pulses co-occur with stimuli to test speech motor cortex involvement.
- **Kernel Notes**: Binary classification of TMS artifact vs auditory evoked response morphology. Apply TMS artifact rejection before analysis. Verify temporal offset between TMS and stimulus within each trial.

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
