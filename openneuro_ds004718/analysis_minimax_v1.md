# Le Petit Prince Hong Kong: Naturalistic fMRI and EEG Dataset

**Dataset**: `openneuro_ds004718` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds004718
**Category**: Complex Applied | **Subjects**: 52 | **Files (Completed)**: 102 | **Channels**: 62 | **Sampling Rate**: 1000 Hz

## Paradigm

Naturalistic listening task where older Cantonese-speaking adults (65+) listened to a Cantonese translation of "The Little Prince" divided into story sections, followed by periodic comprehension checks, during simultaneous EEG and fMRI recording. Numeric trigger codes 1-30+ mark story segments, comprehension questions, and experimental conditions. Code 14 is most frequent (1,053 total), followed by codes 15 (648), and many codes at ~258 each - consistent with a factorial design across 102 files with ~2-10 events per file per code.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004718

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `14` | 1053 | long | raw | Story section / condition code 14 |
| `15` | 648 | long | raw | Story section / condition code 15 |
| `7` | 270 | long | raw | Story section / condition code 7 |
| `3` | 268 | long | raw | Story section / condition code 3 |
| `5` | 266 | long | raw | Story section / condition code 5 |
| `4` | 263 | long | raw | Story section / condition code 4 |
| `6` | 262 | long | raw | Story section / condition code 6 |
| `88` | 259 | long | raw | Story section / condition code 88 |
| `40`-`112` | ~258 each | long | raw | Additional story/condition codes |
| `1`-`30` | ~257-258 each | long | raw | Story section codes 1-30 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Story Section Classification (Raw Triggers)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.6 s, target_events = [`1`, `2`, `3`, `4`, `5`, `6`, `7`, `14`, `15`, `88`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `48`, `49`, `50`, `51`, `52`, `53`, `54`, `55`, `56`, `57`, `58`, `59`, `60`, `61`, `62`, `63`, `64`, `65`, `66`, `67`, `68`, `69`, `70`, `71`, `72`, `73`, `74`, `75`, `76`, `77`, `78`, `79`, `80`, `81`, `82`, `83`, `84`, `85`, `86`, `87`, `89`, `90`, `91`, `92`, `93`, `94`, `95`, `96`, `97`, `98`, `99`, `100`, `101`, `102`, `103`, `104`, `105`, `106`, `107`, `108`, `109`, `110`, `111`, `112`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1`-`30`, `40`-`112` | 0-~71 | Story section/condition codes from STIM triggers (exact mapping requires dataset README) |
  | `14` | ~13 | Most frequent story section (1,053 occurrences) |
  | `15` | ~14 | Second most frequent (648 occurrences) |
  | `88` | ~58 | Additional condition code |
- **Super Meta Notes**: N/A (raw meta level)
- **Evidence**:
  - DOI: 10.1038/s41597.024.03745-8 — Paper describes EEG epoched at word onsets (0-600ms) for ERP analysis with condition codes 1-30+ from triggers indicating story sections. Raw STIM triggers mark sentence onsets (codes 1-30, 40-112).
- **Kernel Notes**: Extract trigger codes from stim channel; map numeric codes to integer labels for multiclass classification. Code 14 appears most frequently (1,053x), suggesting variable-length story segments.

### Primary Task 2: Linguistic Feature Regression/Classification (Super Meta)
- **Task Type**: regression | classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.6 s, target_events = [`word_onset`]
- **Label Route**: `misc`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | word_onset | continuous | Word frequency (lexical frequency measure) |
  | word_onset | continuous | POS tags (part-of-speech: noun, verb, etc.) |
  | word_onset | continuous | f0 intensity (fundamental frequency) |
  | word_onset | continuous | Word rate (speech rate regressor) |
- **Super Meta Notes**: NLP-derived labels are computed from audio/text stimuli and aligned to word onset times. These super labels are not present in raw EEG triggers but must be merged from external annotation files (LPPHK_word_annotations.csv or similar). The paper reports 4,473 word epochs per participant for ERP/ISC analysis.
- **Evidence**:
  - DOI: 10.1038/s41597.024.03745-8 — Paper describes word-level epoching (0-600ms) with NLP-derived super labels including word frequency, POS tags, f0 intensity, and word rate regressors for GLM and ERP analyses.
- **Kernel Notes**: Load external NLP annotation file; align word onset timestamps with EEG epochs; extract linguistic features as additional channels or merge as label vectors. Requires timestamp matching between EEG events and stimulus timing files.

### Primary Task 3: Rest Condition Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 0.6 s, target_events = [`rest`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `rest` | 0 | Rest condition (baseline) |
- **Super Meta Notes**: N/A
- **Evidence**:
  - DOI: 10.1038/s41597.024.03745-8 — Dataset includes rest task as experimental baseline condition; trigger code for rest is included in the event structure.
- **Kernel Notes**: Identify rest condition from trigger codes; separate rest epochs from active listening epochs.

### Normal Task 1: Story Section / Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numeric codes require full decode from dataset README or events.tsv. Naturalistic listening paradigm; continuous EEG during extended story segments. Code 14 is dominant (1,053) vs many codes at ~258 - likely reflects story structure (code 14 = more frequent section). 30+ distinct numeric codes; consider grouping.

 | Event | y | Meaning |
 |-------|---|---------|
 | `1` | 0 | Story/condition code 1 |
 | `2` | 1 | Story/condition code 2 |
 | `3` | 2 | Story/condition code 3 |
 | `4` | 3 | Story/condition code 4 |
 | `5` | 4 | Story/condition code 5 |
 | `6` | 5 | Story/condition code 6 |
 | `7` | 6 | Story/condition code 7 |

## Data Quality Notes

- Numeric code meaning requires README or events.tsv decode.
- Naturalistic paradigm - EEG is continuous during extended listening blocks.
- Simultaneous 7T fMRI and EEG - verify gradient artifact removal.

## References

- **Reference**: `Le Petit Prince Hong Kong: Naturalistic fMRI and EEG dataset from older Cantonese speakers`
