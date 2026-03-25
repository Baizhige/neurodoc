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

### Primary Task 1: Word-Onset ERP Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s *, tmax = 0.6 s, target_events = [`word_onset`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `word_onset` | 0 | Word onset from NLP-aligned text |
- **Super Meta Notes**: Derived from raw events by NLP text-audio alignment pipeline. Kernel step: Load word_onset timestamps from annotations file, epoch EEG at these onsets for 0-600ms windows.
- **Evidence**:
  - DOI: 10.1038/s41597-024-03745-8 — EEG epoched at word onsets (0-600ms) for ERP and ISC analyses across 4473 word events per participant during Cantonese audiobook listening
- **Kernel Notes**: Must read word-onset annotations from separate NLP-derived file; these are NOT raw STIM triggers. (replaces Primary Task 1 from original analysis.md)

### Primary Task 2: Story Section/Condition Code Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s *, tmax = 0.6 s *, target_events = [`1`, `3`, `4`, `5`, `6`, `7`, `14`, `15`, `88`]
- **Label Route**: `stim`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `1` | 0 | Story section code 1 |
  | `3` | 1 | Story section code 3 |
  | `4` | 2 | Story section code 4 |
  | `5` | 3 | Story section code 5 |
  | `6` | 4 | Story section code 6 |
  | `7` | 5 | Story section code 7 |
  | `14` | 6 | Story section code 14 |
  | `15` | 7 | Story section code 15 |
  | `88` | 8 | Story section code 88 |
- **Evidence**:
  - DOI: 10.1038/s41597-024-03745-8 — Triggers at sentence onsets (codes 1-30+) indicate story sections; used for GLM analyses of pitch, intensity, and word rate regressors
- **Kernel Notes**: Verify full mapping of codes 1-30 from events.tsv; codes 40-112 also present but not in available raw event list. (replaces Primary Task 2 from original analysis.md)

### Normal Task 1: Story Section / Condition Classification (multiclass)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = [`14`, `15`, `7`, `3`, `5`, `4`, `6`, `88`, `1`]
- **Label Route**: `Annotation`
- **Target Definition**: 
 | Event | y | Meaning |
 |-------|---|---------|
 | `1` | 0 | Story/condition code 1 |
 | `3` | 1 | Story/condition code 3 |
 | `4` | 2 | Story/condition code 4 |
 | `5` | 3 | Story/condition code 5 |
 | `6` | 4 | Story/condition code 6 |
 | `7` | 5 | Story/condition code 7 |
 | `14` | 6 | Story/condition code 14 |
 | `15` | 7 | Story/condition code 15 |
 | `88` | 8 | Story/condition code 88 |


## Data Quality Notes

- Numeric code meaning requires README or events.tsv decode.
- Naturalistic paradigm - EEG is continuous during extended listening blocks.
- Simultaneous 7T fMRI and EEG - verify gradient artifact removal.

## References

- **Reference**: `Le Petit Prince Hong Kong: Naturalistic fMRI and EEG dataset from older Cantonese speakers`
