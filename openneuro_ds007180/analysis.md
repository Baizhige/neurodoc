# Exo-EEG Experiment

**Dataset**: `openneuro_ds007180` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007180
**Category**: Complex Applied | **Subjects**: 25 | **Files (Completed)**: 25 | **Channels**: 63 | **Sampling Rate**: 500 Hz

## Paradigm

EEG was recorded during interaction with an exoskeleton in a gait or robotic-assisted movement task. Participants performed motor tasks with varying exoskeleton assistance levels and movement conditions. BrainVision trigger codes (S-prefixed) encode specific movement phases, assistance levels, and stimulus conditions across 30 categories.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007180

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `S21` | 1885 | short | raw | Exo stimulus condition S21 |
| `S22` | 1885 | short | raw | Exo stimulus condition S22 |
| `S12` | 1884 | short | raw | Exo stimulus condition S12 |
| `S11` | 1884 | short | raw | Exo stimulus condition S11 |
| `S32` | 1876 | short | raw | Exo stimulus condition S32 |
| `S31` | 1876 | short | raw | Exo stimulus condition S31 |
| `S41` | 1872 | short | raw | Exo stimulus condition S41 |
| `S42` | 1872 | short | raw | Exo stimulus condition S42 |
| `S62` | 1872 | short | raw | Exo stimulus condition S62 |
| `S61` | 1872 | short | raw | Exo stimulus condition S61 |
| `S52` | 1872 | short | raw | Exo stimulus condition S52 |
| `S51` | 1872 | short | raw | Exo stimulus condition S51 |
| `S72` | 1868 | short | raw | Exo stimulus condition S72 |
| `S71` | 1868 | short | raw | Exo stimulus condition S71 |
| `S81` | 1860 | short | raw | Exo stimulus condition S81 |
| `S82` | 1860 | short | raw | Exo stimulus condition S82 |
| `S13` | 1750 | short | raw | Exo stimulus condition S13 |
| `S43` | 1750 | short | raw | Exo stimulus condition S43 |
| `S73` | 1750 | short | raw | Exo stimulus condition S73 |
| `S63` | 1750 | short | raw | Exo stimulus condition S63 |
| `S53` | 1750 | short | raw | Exo stimulus condition S53 |
| `S33` | 1750 | short | raw | Exo stimulus condition S33 |
| `S23` | 1750 | short | raw | Exo stimulus condition S23 |
| `S83` | 1750 | short | raw | Exo stimulus condition S83 |
| `S102` | 1300 | short | raw | Exo stimulus condition S102 |
| `S101` | 1300 | short | raw | Exo stimulus condition S101 |
| `S92` | 1300 | short | raw | Exo stimulus condition S92 |
| `S91` | 1300 | short | raw | Exo stimulus condition S91 |
| `S111` | 1275 | short | raw | Exo stimulus condition S111 |
| `S122` | 1275 | short | raw | Exo stimulus condition S122 |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `S21`, `S22`, `S12`, `S11`, `S32`, `S31`, `S41`, `S42`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Exo
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds007180 DOI: https://doi.org/10.18112/openneuro.ds007180.v1.0.0


### Normal Task 1: Exoskeleton Condition Classification (epoch_by_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 30 distinct BrainVision stimulus codes; decode from events.tsv or README for exact condition meaning. `S255` and `start` are admin markers in some files; exclude from analysis.

 | Event | y | Meaning |
 |-------|---|---------|
 | `S62` | 0 | Exo condition S62 |
 | `S61` | 1 | Exo condition S61 |
 | `S52` | 2 | Exo condition S52 |
 | `S51` | 3 | Exo condition S51 |
 | `S21` | 4 | Exo condition S21 |
 | `S22` | 5 | Exo condition S22 |
 | `S12` | 6 | Exo condition S12 |
 | `S11` | 7 | Exo condition S11 |
 | `S32` | 8 | Exo condition S32 |
 | `S41` | 9 | Exo condition S41 |
 | `S42` | 10 | Exo condition S42 |
 | `S31` | 11 | Exo condition S31 |
 | `S72` | 12 | Exo condition S72 |
 | `S71` | 13 | Exo condition S71 |
 | `S81` | 14 | Exo condition S81 |
 | `S82` | 15 | Exo condition S82 |
 | `S13` | 16 | Exo condition S13 |
 | `S43` | 17 | Exo condition S43 |
 | `S73` | 18 | Exo condition S73 |
 | `S63` | 19 | Exo condition S63 |
 | `S53` | 20 | Exo condition S53 |
 | `S33` | 21 | Exo condition S33 |
 | `S23` | 22 | Exo condition S23 |
 | `S83` | 23 | Exo condition S83 |
 | `S102` | 24 | Exo condition S102 |
 | `S101` | 25 | Exo condition S101 |
 | `S92` | 26 | Exo condition S92 |
 | `S91` | 27 | Exo condition S91 |
 | `S111` | 28 | Exo condition S111 |
 | `S122` | 29 | Exo condition S122 |
## Data Quality Notes

- BrainVision format; 30 S-coded stimulus conditions require README decoding.
- `S255` (saturation marker) and `start` events in some files; exclude from analysis.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to epoching.

## References

- _No paper reference available_
