# Somatosensory evoked potentials in the human spinal cord to mixed nerve stimulation

**Dataset**: `openneuro_ds004388` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004388
**Category**: Sensory/Response | **Subjects**: 40 | **Files (Completed)**: 399
**Channels**: 115 | **Sampling Rate**: 10000 Hz

## Paradigm

The dataset records somatosensory evoked potentials (SEPs) in response to mixed median and tibial nerve stimulation, alongside a resting state condition. Simultaneous EEG and epidural spinal cord recordings (ESG) were acquired to characterize the spinal and cortical processing of somatosensory signals.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `stimulus` | 399x~500 | event | raw | Electrical nerve stimulation onset |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Potential Task 1: SEP Stimulus Epoching (long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s (relative to event onset), overlap = 0.5, target_events = [`stimulus`]
- **Label Route**: `event`
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


## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_manual_review