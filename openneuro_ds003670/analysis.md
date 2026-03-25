# Dataset of Concurrent EEG, ECG, and Behavior with Multiple Doses of Transcranial Electrical Stimulation

**Dataset**: `openneuro_ds003670` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003670
**Category**: Complex Applied | **Subjects**: 19 | **Files (Completed)**: 62
**Channels**: 35 | **Sampling Rate**: 2000 Hz

## Paradigm

Participants performed a continuous tracking task (CTT) requiring them to maintain a ball at the center of a screen to assess vigilance and sustained alertness. Simultaneously, multi-site transcranial electrical stimulation (tES) was applied at varying dose combinations (sham, low, high) to modulate arousal and attention. EEG, ECG, and behavioral tracking data were recorded concurrently. The study aims to identify optimal tES parameters for enhancing cognitive performance.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003670

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulation Start` | 62 | long | raw | Transcranial stimulation onset (sustained state) |
| `Stimulation Stop` | 62 | long | raw | Transcranial stimulation offset |
| `Block Start` | 62 | long | raw | Task block onset marker |
| `STATUS` | 62 | admin | raw | System status marker |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulation Start`, `Stimulation Stop`, `STATUS`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Publisher-defined BIDS task: GXt ESCTT
- **Task Type**: classification/segmentation
- **Epoch Method**: `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: tmin = Needs verification, tmax = Needs verification, overlap = Needs verification, target_events = [Needs verification] | segment_length = Needs verification, overlap = Needs verification
- **Label Route**: `Annotation`
- **Target Definition**: Event/condition labels for this BIDS task (dataset-specific mapping)
- **Evidence**: OpenNeuro metadata.tasksCompleted and dataset readme. Source: https://openneuro.org/datasets/ds003670 DOI: https://doi.org/10.18112/openneuro.ds003670.v1.1.0


### Normal Task 1: Stimulation period analysis (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Stimulation periods are sustained states (several minutes each); use long-event epoching. Dose condition (sham/low/high) should be in events.tsv or participants.tsv. Very high sampling rate (2000 Hz) increases memory requirements.

| Event | y | Meaning |
 |-------|---|------|
| `Stimulation Start` | 1 | Transcranial electrical stimulation activation period |
| `Block Start` | 0 | Task block (baseline/control) |
## Data Quality Notes

- Very high sampling rate (2000 Hz); downsample to 250-500 Hz for standard EEG analyses.
- tES artifacts present during stimulation periods; independent component analysis required.
- ECG channels included; can be used for cardiac artifact removal.

## References

- **Reference**: `Dataset of concurrent EEG, ECG, and behavior with multiple doses of transcranial Electrical Stimulation. OpenNeuro ds003670.`
