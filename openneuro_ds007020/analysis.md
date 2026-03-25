# EEG Mortality Dataset in Parkinson's Disease

**Dataset**: `openneuro_ds007020` | **Year**: 2025 | **URL**: https://openneuro.org/datasets/ds007020
**Category**: Biological State | **Subjects**: 94 | **Files (Completed)**: 94 | **Channels**: 63 | **Sampling Rate**: 500 Hz

## Paradigm

Resting-state EEG recordings (eyes open) were collected from Parkinson's disease (PD) patients and healthy controls to evaluate EEG-based biomarkers for mortality classification. The dataset enables investigation of spectral and connectivity biomarkers that predict mortality risk in PD. The sole event marker (`New Segment/`) indicates a recording segment boundary and carries no experimental meaning.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds007020

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `New Segment/` | 94 | admin | raw | Recording segment boundary marker |

> **Event Type**: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

## Tasks

### Primary Task 1: Resting-state analysis baseline
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_segmentation_hdf5` or `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Condition/group labels from metadata when available
- **Evidence**: Dataset is primarily resting-state or spontaneous-state EEG. Source: https://openneuro.org/datasets/ds007020 DOI: https://doi.org/10.1016/j.prdoa.2025.100409


### Normal Task 1: Resting-State Segmentation (long_event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5 s, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: N/A (no trial events; target_events: null)
- **Notes**: `New Segment/` is a BrainVision segment boundary marker and must never be used as a classification target. Group labels (PD patient / healthy control, mortality outcome) must be derived from clinical metadata in participants.tsv.
## Data Quality Notes

- `New Segment/` is a BrainVision format boundary marker; exclude from all analyses.
- Labels for mortality prediction must be derived from clinical metadata in participants.tsv.
- Apply bandpass filter (0.5-40 Hz) and artifact rejection prior to segmentation.

## References

- **Reference**: `EEG Mortality Dataset in Parkinson's Disease`
