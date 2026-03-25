# SRM Resting-State EEG

**Dataset**: `openneuro_ds003775` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds003775
**Category**: Biological State | **Subjects**: 111 | **Files (Completed)**: 153
**Channels**: 64 | **Sampling Rate**: 1024 Hz

## Paradigm

Four minutes of uninterrupted eyes-closed resting-state EEG recorded from healthy adult participants as part of a larger experimental paradigm. This dataset was collected to provide a normative baseline for comparing resting EEG characteristics across studies. The resting-state recording provides a standardized, task-free EEG sample suitable for spectral power analysis, functional connectivity, and individual difference studies.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003775

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| - | - | - | raw | No event markers detected; pure resting-state EEG |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Publisher-defined BIDS task: Resteyesc
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003775 DOI: https://doi.org/10.1111/ejn.14964


### Normal Task 1: Resting state EEG segmentation
- **Task Type**: segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5
- **Label Route**: `Annotation`
- **Target Definition**: N/A (null (no labels, used for unsupervised analysis or individual differences research))
- **Notes**: Pure 4-minute eyes-closed resting-state; 111 subjects, 153 files (some subjects may have multiple sessions). Suitable for individual alpha frequency, spectral power, and connectivity analyses. Large normative dataset.
## Data Quality Notes

- Purely resting-state; no task events or stimuli.
- 153 files from 111 subjects; some subjects have multiple files (repeat sessions).
- 64-channel EEG at 1024 Hz; standard configuration for resting-state analysis.

## References

- **Reference**: `Hatlestad-Hall, C., Rygvold, T. W., & Andersson, S. (2022). BIDS-structured resting-state electroencephalography (EEG) data extracted from an experimental paradigm. Data in Brief, 45, 108647.`
