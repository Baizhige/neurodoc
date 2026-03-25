# Bimodal dataset on Inner speech

**Dataset**: `openneuro_ds004196` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004196
**Category**: High-level Mental | **Subjects**: 4 | **Files (Completed)**: 4 | **Channels**: 73 | **Sampling Rate**: 512 Hz

## Paradigm

An inner-speech production task where participants mentally vocalized eight specific words from social and numeric categories during nonsimultaneous EEG and fMRI recording. Subjects imagined speaking words without producing overt speech or movement. No trial-level event markers were embedded in the EEG recordings; the data is treated as continuous.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004196

## Event Structure

No trial events detected. This dataset contains continuous EEG without trial-level annotations.

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Inner Speech Category Classification (Social vs Numeric)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.1 s, target_events = [`child`, `daughter`, `father`, `wife`, `four`, `three`, `ten`, `six`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `child` | 0 | Social word |
  | `daughter` | 0 | Social word |
  | `father` | 0 | Social word |
  | `wife` | 0 | Social word |
  | `four` | 1 | Numeric word |
  | `three` | 1 | Numeric word |
  | `ten` | 1 | Numeric word |
  | `six` | 1 | Numeric word |
- **Evidence**:
  - DOI: 10.1038/s41597.023.02286.w — First publicly available bimodal dataset with 320 trials per subject (40 trials per word across 8 words in 2 categories) with event markers for fixation, rest, and 8 word stimuli
  - DOI: https://doi.org/10.1101/2022.05.24.492109 — Binary (social vs numeric) and multiclass (8 words) classification using epochs extracted from [-0.1, 0.1]s window around stimulus onset, Random Forest achieving 62.81% EEG-only accuracy for binary
- **Kernel Notes**: Extract epochs time-locked to stimulus onset for each word event. Map social category words (child, daughter, father, wife) to y=0 and numeric words (four, three, ten, six) to y=1. Use epoch window [-0.1, 0.1]s around stimulus onset.

### Primary Task 2: Inner Speech Word Classification (8-class)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.1 s, tmax = 0.1 s, target_events = [`child`, `daughter`, `father`, `wife`, `four`, `three`, `ten`, `six`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `child` | 0 | Social word: child |
  | `daughter` | 1 | Social word: daughter |
  | `father` | 2 | Social word: father |
  | `wife` | 3 | Social word: wife |
  | `four` | 4 | Numeric word: four |
  | `three` | 5 | Numeric word: three |
  | `ten` | 6 | Numeric word: ten |
  | `six` | 7 | Numeric word: six |
- **Evidence**:
  - DOI: 10.1038/s41597.023.02286.w — 8-class inner speech word classification across 8 words (4 social: child, daughter, father, wife; 4 number: four, three, ten, six)
  - DOI: https://doi.org/10.1101/2022.05.24.492109 — 8-class word classification with Random Forest achieving 22.19% accuracy using epochs from [-0.1, 0.1]s window
- **Kernel Notes**: Extract epochs time-locked to stimulus onset for each word event. Assign unique class labels (0-7) to each of the 8 words. Use epoch window [-0.1, 0.1]s around stimulus onset.

### Normal Task 1: Inner Speech Segmentation (resting)
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null)
- **Notes**: No event markers available. Sliding window segmentation only.

## Data Quality Notes

- Very small dataset (N=4); not suitable for cross-subject generalization
- Consider using fMRI labels aligned to EEG timing if available

## References

- **Reference**: `Bimodal dataset on Inner speech`
