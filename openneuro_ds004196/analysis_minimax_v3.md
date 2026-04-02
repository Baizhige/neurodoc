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

### Primary Task 1: Inner Speech Word Classification (Binary: Social vs Numeric)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `social_word` | 0 | Social category words (child, daughter, father, wife) |
  | `numeric_word` | 1 | Numeric category words (four, three, ten, six) |
- **Super Meta Notes**: Derived from experimental design metadata (stimulus timing in seconds). Kernel step: Read trial timing from events.tsv sidecar file, segment EEG at 2s windows aligned to stimulus onsets, assign category labels based on word type (social vs numeric). If events.tsv unavailable, use dataset description: 40 trials per word, 320 trials/subject, 4 subjects.
- **Evidence**:
  - DOI: 10.1038/s41597-023-02286.w — "This paper presents the first publicly available bimodal dataset with nonsimultaneous EEG-fMRI recordings of inner speech, containing 320 trials per subject (40 trials per word across 8 words in 2 categories) with event markers for fixation, rest, and 8 word stimuli."
  - DOI: 10.1101/2022.05.24.492109 — "Using epochs extracted from [-0.1, 0.1]s window around stimulus onset for binary (social vs numeric) and multiclass (8 words) classification with Random Forest achieving 62.81% EEG-only accuracy for binary."
- **Kernel Notes**: Must read trial metadata from events.tsv (if available) or derive from paper's trial structure (fixation 1s, task 2s, rest 1s per trial). Sliding window segmentation required since no raw event markers embedded in EEG. (replaces Primary Task 1 and Normal Task 1 from original analysis.md)

### Primary Task 2: Inner Speech 8-Class Word Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Meta Level**: super
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
- **Super Meta Notes**: Derived from experimental design metadata (8 distinct word stimuli). Kernel step: Read trial timing and word identity from events.tsv, segment EEG at 2s windows aligned to stimulus onsets, assign 8-class labels based on which word was mentally vocalized.
- **Evidence**:
  - DOI: 10.1038/s41597-023-02286.w — "EventID 1=fixation, 2=rest, 3=child, 4=daughter, 5=father, 6=wife, 7=four, 8=three, 9=ten, 10=six; for classification: social->[3,4,5,6], number->[7,8,9,10]"
  - DOI: 10.1101/2022.05.24.492109 — "Multiclass (8 words) classification with Random Forest achieving 22.19% for 8-class word classification."
- **Kernel Notes**: Requires events.tsv sidecar with trial-level timing. 40 trials per word per subject × 4 subjects = 1280 total trials. Alternative: use paper-reported trial structure for epoch extraction.

## Data Quality Notes

- Very small dataset (N=4); not suitable for cross-subject generalization
- Consider using fMRI labels aligned to EEG timing if available

