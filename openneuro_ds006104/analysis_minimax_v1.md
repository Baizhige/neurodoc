# EEG dataset for speech decoding

**Dataset**: `openneuro_ds006104` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006104
**Category**: High-level Mental | **Subjects**: 24 | **Files (Completed)**: 80 | **Channels**: 62 | **Sampling Rate**: 2000 Hz

## Paradigm

A phoneme discrimination task where participants listened to speech sounds - including single phonemes, phoneme pairs, and words - while undergoing transcranial magnetic stimulation (TMS) to test the role of speech motor cortex in auditory speech perception. Subjects provided button-press responses after each sound. The dataset supports decoding of speech perception from TMS-EEG.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006104

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `TMS` | 29260 | short | raw | TMS pulse delivery |
| `stimulus` | 29260 | short | raw | Auditory speech stimulus onset |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Phoneme Category Classification (Consonant vs Vowel)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | consonant phoneme | 0 | Consonant phoneme stimulus (/b/,/p/,/d/,/t/,/s/,/z/) |
  | vowel phoneme | 1 | Vowel phoneme stimulus (/i/,/ɛ/,/ɑ/,/u/,/oʊ/) |
- **Evidence**:
  - DOI: 10.1038/s41597.025.05187-2 — Demonstrates multiclass classification of phoneme identity including consonant/vowel categories from TMS-EEG during speech perception

### Primary Task 2: Phoneme Identity Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | /b/ | 0 | Bilabial stop voiced |
  | /p/ | 1 | Bilabial stop unvoiced |
  | /d/ | 2 | Alveolar stop voiced |
  | /t/ | 3 | Alveolar stop unvoiced |
  | /s/ | 4 | Alveolar fricative unvoiced |
  | /z/ | 5 | Alveolar fricative voiced |
  | /i/ | 6 | High front vowel |
  | /ɛ/ | 7 | Mid front vowel |
  | /ɑ/ | 8 | Low back vowel |
  | /u/ | 9 | High back vowel |
  | /oʊ/ | 10 | Mid back diphthong |
- **Evidence**:
  - DOI: 10.1038/s41597.025.05187-2 — Shows classification of specific phoneme identity from single phoneme stimuli

### Primary Task 3: Word Type Classification (Real Word vs Pseudoword)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | real_word | 0 | Real word stimulus |
  | pseudoword | 1 | Pseudoword stimulus (CVC structure) |
- **Evidence**:
  - DOI: 10.1038/s41597.025.05187-2 — Demonstrates classification of word type (real vs pseudoword) from EEG during speech perception

### Primary Task 4: Articulatory Feature Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Feature | Categories | Meaning |
  |---------|------------|---------|
  | place_of_articulation | bilabial, alveolar | Place where articulators meet |
  | manner_of_articulation | stop, fricative | How airflow is obstructed |
  | voicing | voiced, unvoiced | Vibration of vocal cords |
- **Super Meta Notes**: Three separate binary classification tasks for each articulatory feature dimension
- **Evidence**:
  - DOI: 10.1038/s41597.025.05187-2 — Shows classification of articulatory features (place, manner, voicing) from TMS-EEG recordings

### Primary Task 5: TMS Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`TMS`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | control | 0 | Control TMS condition (no stimulation) |
  | LipM1 | 1 | TMS targeting lip motor cortex |
  | TongueM1 | 2 | TMS targeting tongue motor cortex |
- **Evidence**:
  - DOI: 10.1038/s41597.025.05187-2 — Dataset includes TMS condition labels (control, LipM1, TongueM1) for studying speech motor cortex role

### Normal Task 1: TMS vs Stimulus Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `Moreira et al. "An open-access EEG dataset for speech decoding: Exploring the role of articulation and coarticulation"`
