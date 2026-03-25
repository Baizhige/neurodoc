# Research data supporting 'EEG recording during playing MOBA game'

**Dataset**: `openneuro_ds005520` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005520
**Category**: Complex Applied | **Subjects**: 23 | **Files (Completed)**: 23 | **Channels**: 60 | **Sampling Rate**: 256 Hz

## Paradigm

Participants played a real MOBA (Multiplayer Online Battle Arena) game while 60-channel EEG was recorded alongside resting-state sessions. Trigger codes mark game events such as kills, deaths, and other in-game actions. The study investigates neural correlates of naturalistic gaming behavior.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005520

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `13` | 834 | long | raw | In-game event code 13 (decode from events.tsv) |
| `14` | 520 | long | raw | In-game event code 14 (decode from events.tsv) |
| `66` | 137 | long | raw | In-game event code 66 (decode from events.tsv) |
| `666` | 89 | long | raw | In-game event code 666 (decode from events.tsv) |
| `444` | 45 | long | raw | In-game event code 444 (decode from events.tsv) |
| `-255` | 9 | admin | raw | System overflow / boundary marker |
| `4` | 9 | long | raw | In-game event code 4 (decode from events.tsv) |
| `100008` | 9 | long | raw | In-game event code 100008 (decode from events.tsv) |
| `164` | 3 | long | raw | In-game event code 164 (decode from events.tsv) |
| `244` | 1 | long | raw | In-game event code 244 (decode from events.tsv) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: Needs verification
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Resting eye open
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005520 DOI: https://doi.org/10.18112/openneuro.ds005520.v1.0.1


### Primary Task 2: Publisher-defined BIDS task: Resting eye closed
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005520 DOI: https://doi.org/10.18112/openneuro.ds005520.v1.0.1


### Primary Task 3: Publisher-defined BIDS task: MOBA game
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005520 DOI: https://doi.org/10.18112/openneuro.ds005520.v1.0.1


### Normal Task 1: MOBA Game Events (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Numerical trigger codes require mapping from events.tsv or dataset README. Very small dataset (23 subjects); low event counts for rare codes.

 | Event | y | Meaning |
 |-------|---|---------|
 | `13` | 0 | Game event 13 |
 | `14` | 1 | Game event 14 |
 | `66` | 2 | Game event 66 |
 | `666` | 3 | Game event 666 |
 | `444` | 4 | Game event 444 |
 | `-255` | 5 | System marker |
 | `4` | 6 | Game event 4 |
 | `100008` | 7 | Game event 100008 |
 | `164` | 8 | Game event 164 |
 | `244` | 9 | Game event 244 |
## Data Quality Notes

- Event codes require decoding from dataset events.tsv or README.
- Very small dataset (23 subjects, 23 files); rare codes (164, 244, -255) have <10 occurrences total.
- Apply bandpass filter (1-40 Hz) and artifact rejection prior to epoching.

## References

- **Reference**: `EEG recording during playing MOBA game`
