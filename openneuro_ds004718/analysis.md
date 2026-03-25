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

### Primary Task 1: Publisher-defined BIDS task: Lpp HK
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004718 DOI: https://doi.org/10.18112/openneuro.ds004718.v1.1.2


### Primary Task 2: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds004718 DOI: https://doi.org/10.18112/openneuro.ds004718.v1.1.2


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
