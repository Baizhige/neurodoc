# TMS-EEG-MRI-fMRI-DWI data on paired associative stimulation and connectivity (Shirley Ryan AbilityLab, Chicago, IL)

**Dataset**: `openneuro_ds004024` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004024
**Category**: Sensory/Response | **Subjects**: 497 | **Files (Completed)**: 497
**Channels**: 69 | **Sampling Rate**: 20000 Hz

## Paradigm

A multi-modal neuroimaging study using Paired Associative Stimulation (PAS) combined with TMS-EEG to investigate cortical connectivity and neuroplasticity. Participants received precisely timed TMS pulses paired with peripheral nerve stimulation, and EEG was recorded at very high sampling rate (20 kHz) to capture TMS-evoked potentials. The study also collected MRI, fMRI, and DWI data. This is a clinical/neurophysiology dataset focusing on brain connectivity assessment.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/A` | 345 files | event | raw | TMS or PAS stimulus onset |
| `Out/A` | 378 files | event | raw | Stimulus output marker |
| `SB/A` | 33 files | event | raw | Sub-threshold baseline stimulus |
| `Video/B` | 32 files | event | raw | Video instruction marker |
| `New Segment/` | 497 files | admin | raw | Recording segment boundary - exclude |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
| `stim_route` | N/A | Trigger-channel or stimulus-marker based labeling via `stim` route |
| `candidate_trigger_labels` | N/A | `Stimulus/A` |

## Tasks

### Classical Task 1: TMS-evoked ccPAS Asynchrony Classification (LTP vs Control vs LTD)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/A`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | ccPAS_14ms | 0 | 14ms asynchrony - LTP condition (increased connectivity) |
  | ccPAS_9ms | 1 | 9ms asynchrony - control condition (no change) |
  | ccPAS_4ms | 2 | 4ms asynchrony - LTD condition (decreased connectivity) |
- **Super Meta Notes**: Derived from raw event `Stimulus/A` combined with experimental asynchrony condition metadata (4ms, 9ms, 14ms values set in the ccPAS protocol). Kernel step: Extract trial-wise asynchrony condition labels from the experimental design file (events.tsv or sidecar JSON) and merge with epoch labels. For papers analyzing Before vs After[1] (~10min) vs After[2] (~60min) sessions, also derive time-point labels. (replaces Potential Task 1 from original analysis.md)
- **Evidence**:
  - DOI: 10.1016/j.neurom.2022.10.045 — Three-class ccPAS asynchrony detection (14ms LTP vs 9ms no-change vs 4ms LTD) using TMS-evoked EEG connectivity changes with statistical analysis in 5-20ms post-stimulus window
- **Kernel Notes**: 
  - Verify event ID mapping from events.tsv - the paper refers to 'spTMS' and 'ccPAS stimulus pairs' which should map to available `Stimulus/A` marker
  - The 20kHz sampling rate requires downsampling before analysis
  - TMS artifact (first ~10ms) requires specialized cleaning (e.g., SSP, ICA)
  - Analysis window: 5-20ms post-stimulus for AUC calculation

### Potential Task 1: Sub-threshold Baseline vs Active TMS Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus/A` | 0 | Active TMS/PAS stimulus pulse - main evoked potential event |
  | `SB/A` | 1 | Sub-threshold baseline TMS pulse |
- **Notes**: New Segment/ is an admin boundary marker and must be excluded. Very high sampling rate (20 kHz) - downsampling to 1-5 kHz strongly recommended before HDF5 generation. The TMS artifact (first ~10 ms post-pulse) requires specialized cleaning before analysis.

## Data Quality Notes

- Very high sampling rate (20,000 Hz) - downsampling required
- TMS artifact contaminates first ~10 ms post-stimulus; specialized TMS-EEG artifact removal (e.g., SSP, ICA) is required
- New Segment/ is an admin boundary marker to exclude


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
> **Trigger Decoding**: Keep trigger decoding table versioned and auditable.