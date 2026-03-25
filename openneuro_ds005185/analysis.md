# Ear-EEG Sleep Monitoring 2019 (EESM19)

**Dataset**: `openneuro_ds005185` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds005185
**Category**: Biological State | **Subjects**: 20 | **Files (Completed)**: 516 | **Channels**: 25 | **Sampling Rate**: 500 Hz

## Paradigm

Naturalistic multi-night sleep monitoring using ear-EEG and polysomnography (PSG) in a home environment collected in 2019. Participants self-applied in-ear EEG electrodes over multiple nights for sleep staging and feasibility assessment. Event markers are Danish-language protocol annotations (lights out, going to bed, waking up), synchronization pulses, and calibration periods. The dominant event is `trigger` (30,726 total) - a PSG synchronization pulse. Sleep stage labels are derived from PSG annotations rather than EEG event markers.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds005185

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `trigger` | 30726 | admin | raw | Synchronization trigger between ear-EEG and PSG (exclude) |
| `Lights Out` | 94 | rest | raw | Lights out - sleep onset marker |
| `Gik i seng` | 80 | rest | raw | "Went to bed" (Danish) |
| `Biocalibrations` | 79 | admin | raw | Biocalibration period (exclude) |
| `Sync` | 77 | admin | raw | Synchronization marker (exclude) |
| `Start af maling` | 75 | admin | raw | "Start of recording" (Danish, exclude) |
| `Stod op` | 70 | rest | raw | "Got up" (Danish) - wake marker |
| `Biocalibrations start` | 11 | admin | raw | Biocalibration start (exclude) |
| `Vagen` / `vagen` | 13 | rest | raw | "Awake" (Danish) |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `trigger`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Sleep stage labels (W/N1/N2/N3/REM; mapping dataset-specific)
- **Evidence**: Dataset and references explicitly center on PSG/EEG sleep scoring. Source: https://openneuro.org/datasets/ds005185 DOI: https://doi.org/10.1038/s41598-019-53115-3


### Primary Task 2: Publisher-defined BIDS task: ASSR
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005185 DOI: https://doi.org/10.1038/s41598-019-53115-3


### Primary Task 3: Publisher-defined BIDS task: Comfort
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds005185 DOI: https://doi.org/10.1038/s41598-019-53115-3


### Normal Task 1: Sleep Monitoring Segmentation (segmentation)
- **Task Type**: classification
- **Epoch Method**: `segmentation`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `stim`
- **Target Definition**: None
- **Notes**: All event markers are Danish-language protocol annotations or sync triggers - not suitable as EEG classification targets. Sleep stage labels (N1/N2/N3/REM/Wake) should be obtained from PSG annotation files. `trigger` (30,726) is a high-frequency sync pulse - exclude.
## Data Quality Notes

- `trigger` (30,726) is a sync pulse - exclude from classification.
- All event markers are protocol annotations, not neural response labels.
- 25-channel ear-EEG with limited spatial resolution.
- PSG reference annotations required for sleep staging labels.

## References

- **Reference**: `Ear-EEG Sleep Monitoring 2019 (EESM19)`
