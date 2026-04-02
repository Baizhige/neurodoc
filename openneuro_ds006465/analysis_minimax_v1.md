# 3M-CPSEED: EEG Dataset for Chinese Pinyin Production in Overt, Silent-Intended, and Imagined Speech

**Dataset**: `openneuro_ds006465` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds006465
**Category**: High-level Mental | **Subjects**: 20 | **Files (Completed)**: 84 | **Channels**: 33 | **Sampling Rate**: 500 Hz

## Paradigm

Participants performed three modes of speech production - overt (spoken aloud), silent-intended (mouthed without sound), and imagined (mental speech without movement) - for specific Chinese Pinyin sounds including initials and finals. The dataset enables comparison of neural signatures across overt, silent, and imagined speech conditions. Each trial consisted of a visual cue (stimulus_presentation) followed by a production phase and a response confirmation. Numeric codes 1-10 encode specific phoneme or condition types.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds006465

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus_presentation` | 42 | short | raw | Visual cue onset prompting speech production |
| `1` | 302 | short | raw | Phoneme/condition code 1 |
| `2` | 200 | short | raw | Phoneme/condition code 2 |
| `3` | 200 | short | raw | Phoneme/condition code 3 |
| `4` | 200 | short | raw | Phoneme/condition code 4 |
| `5` | 200 | short | raw | Phoneme/condition code 5 |
| `6` | 200 | short | raw | Phoneme/condition code 6 |
| `7` | 200 | short | raw | Phoneme/condition code 7 |
| `8` | 200 | short | raw | Phoneme/condition code 8 |
| `9` | 200 | short | raw | Phoneme/condition code 9 |
| `10` | 200 | short | raw | Phoneme/condition code 10 |
| `response` | 84 | short | raw | Participant response / confirmation |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus_presentation`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Chinese Pinyin Speech Production Mode Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 3 s, tmax = 5 s * (or 5-7s, 7-9s for Speak phase; 10-12s, 12-14s, 14-16s for Silent; 17-19s, 19-21s, 21-23s for Imagine), target_events = [`stimulus_presentation`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `response`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus_presentation` | 0 | Visual cue for speech production (baseline/control) |
  | `1`-`10` | 1-10 | Pinyin syllable codes (a,i,u,ü,m,f,j,l,k,ch with pairings) |
- **Evidence**:
  - DOI: 10.1038/s41597-025-06346-1 — Paper introduces 3M-CPSEED dataset for Chinese Pinyin production across three speech modes (overt, silently articulated, imagined) and validates with EEGNet-based binary classification achieving 60-73% accuracy for speech mode discrimination and >55% for pinyin syllable pairwise classification.
- **Kernel Notes**: The paper extracts 2-second epochs from specific temporal windows within each trial: Speak phase [3-5s, 5-7s, 7-9s], Silently articulated [10-12s, 12-14s, 14-16s], Imagine [17-19s, 19-21s, 21-23s] — total 9 epochs per trial. Speech mode labels derived from trial temporal structure. Apply bandpass filter (0.5-40 Hz) before epoching.

### Primary Task 2: BIDS Task: Imaginedspeech (from dataset metadata)
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 3 s, tmax = 5 s *, target_events = [`stimulus_presentation`, `response`]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**:
  - DOI: https://doi.org/10.18112/openneuro.ds006465.v2.0.0 — OpenNeuro metadata indicates tasksCompleted includes "imaginedspeech" as a BIDS task.
- **Kernel Notes**: Verify exact epoch boundaries from events.tsv; use default 2-second window aligned with Imagine phase (17-23s region) for pure imagined speech trials.

### Normal Task 1: Speech Production Mode Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
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

## References

- **Reference**: `3M-CPSEED: An EEG-based Dataset for Chinese Pinyin Production in Overt, Silent-intended, and Imagined Speech`
