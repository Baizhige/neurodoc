# Somatosensory evoked potentials in the human spinal cord to mixed nerve stimulation

**Dataset**: `openneuro_ds004388` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004388
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 399
**Channels**: 115 | **Sampling Rate**: 10000 Hz

## Paradigm

The dataset records somatosensory evoked potentials (SEPs) in response to mixed median and tibial nerve stimulation, alongside a resting state condition. Simultaneous EEG and epidural spinal cord recordings (ESG) were acquired to characterize the spinal and cortical processing of somatosensory signals.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004388

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 399x~500 | long | raw | Electrical nerve stimulation onset |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Normal Task 1: SEP Stimulus Epoching (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = [`stimulus`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus` | 0 | Nerve stimulation onset |
- **Kernel Notes**: Only one event class; suitable for evoked potential analysis or regression on stimulation parameters. Multiple nerve sites and stimulation rates encoded in file naming conventions.
- **Evidence**: OpenNeuro metadata indicates stimulus-locked SEP acquisition with multiple runs per subject.


## Data Quality Notes

- Very high sampling rate (10 kHz) for SEP/ESG; downsampling required for standard EEG analysis
- 115 channels includes spinal cord (ESG) and peripheral nerve (ENG/EMG) channels
- 399 files across 40 subjects (multiple runs/conditions per subject)

## References

- **Reference**: `Somatosensory evoked potentials in the human spinal cord to mixed nerve stimulation`
