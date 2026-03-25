# Structural MRI, Resting-State fMRI, and PSG/EEG Dataset of Zoster-Associated Neuralgia

**Dataset**: `openneuro_ds007181` | **Year**: 2026 | **URL**: https://openneuro.org/datasets/ds007181
**Category**: Biological State | **Subjects**: 59 | **Files (Completed)**: 59 | **Channels**: 24 | **Sampling Rate**: 1024 Hz

## Paradigm

Resting-state EEG (part of a PSG recording) was collected from patients with zoster-associated neuralgia and healthy controls, alongside structural MRI and resting-state fMRI. Manual sleep staging is available from PSG annotations. The dataset enables investigation of brain activity and sleep architecture differences between healthy controls and patients with herpes zoster-associated chronic pain.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007181

## Event Structure

_No event markers detected (`no_events`). This dataset contains continuous PSG/EEG recordings without trial-level annotations._

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `no_events` | N/A | admin | raw | No discrete event markers detected; use continuous segmentation or external metadata labels. |

## Tasks

### Primary Task 1: Sleep stage classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification]
- **Label Route**: `Annotation`
- **Target Definition**: Sleep stage labels (W/N1/N2/N3/REM; mapping dataset-specific)
- **Evidence**: Dataset and references explicitly center on PSG/EEG sleep scoring. Source: https://openneuro.org/datasets/ds007181 DOI: https://doi.org/10.18112/openneuro.ds007181.v1.0.1


### Primary Task 2: Publisher-defined BIDS task: Rest
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds007181 DOI: https://doi.org/10.18112/openneuro.ds007181.v1.0.1


### Normal Task 1: Continuous Segmentation (segmentation)
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 2.0 s, overlap = 0.5 s
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no event markers; sleep stage labels from PSG scoring files)
- **Notes**: No EEG event markers available. Sleep stage labels (Wake/N1/N2/N3/REM) must be derived from PSG hypnogram annotations if present. Group labels (zoster neuralgia / healthy control) from participants.tsv.
## Data Quality Notes

- No event markers present; continuous-only processing.
- PSG-derived sleep stage labels require alignment with EEG data if available.
- 24-channel PSG EEG system; non-standard montage compared to research-grade EEG.

## References

- **Reference**: `Structural MRI, Resting-state fMRI, and PSG/EEG Dataset of Zoster-associated Neuralgia`
