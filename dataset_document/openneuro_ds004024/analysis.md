# TMS-EEG-MRI-fMRI-DWI data on paired associative stimulation and connectivity (Shirley Ryan AbilityLab, Chicago, IL)

**Dataset**: `openneuro_ds004024` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004024
**Category**: Sensory/Response | **Subjects**: 497 | **Files (Completed)**: 497 | **Channels**: 69 | **Sampling Rate**: 20000 Hz | **Manual Review**: Pending

## Paradigm

A multi-modal neuroimaging study using Paired Associative Stimulation (PAS) combined with TMS-EEG to investigate cortical connectivity and neuroplasticity. Participants received precisely timed TMS pulses paired with peripheral nerve stimulation, and EEG was recorded at very high sampling rate (20 kHz) to capture TMS-evoked potentials. The study also collected MRI, fMRI, and DWI data. This is a clinical/neurophysiology dataset focusing on brain connectivity assessment.

## File Scan Result

> **Kernel SHA256**: `988cb59edb145a20bce331016908f2354f7e6d8186b847043025a57a0ed13640`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus/S  1` | 497 | event | raw | Recording segment boundary marker |
| `Stimulus/S  2` | 33153 | event | raw | Active TMS/PAS stimulus onset |
| `Stimulus/S  3` | 33153 | event | raw | Stimulus output marker |
| `Stimulus/S  4` | 5406 | event | raw | Sub-threshold baseline TMS pulse |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | missing | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks

### Classical Task 1: ccPAS Asynchrony Classification (LTP vs Control vs LTD)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S  2`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `Stimulus/S  2` (14ms condition) | 0 | 14ms asynchrony - LTP condition (increased connectivity); Needs verification: condition derived from experimental metadata |
  | `Stimulus/S  2` (9ms condition) | 1 | 9ms asynchrony - control condition (no change); Needs verification: condition derived from experimental metadata |
  | `Stimulus/S  2` (4ms condition) | 2 | 4ms asynchrony - LTD condition (decreased connectivity); Needs verification: condition derived from experimental metadata |
- **Super Meta Notes**: Labels derived from experimental asynchrony condition metadata (4ms, 9ms, 14ms values) in the ccPAS protocol design files. Kernel step: Extract trial-wise asynchrony condition labels from the experimental design file (events.tsv or sidecar JSON) and merge with epoch labels. For papers analyzing Before vs After[1] (~10min) vs After[2] (~60min) sessions, also derive time-point labels from session markers.
- **Evidence**:
  - DOI: 10.1016/j.neurom.2022.10.045 — Three-class ccPAS asynchrony detection (14ms LTP vs 9ms no-change vs 4ms LTD) using TMS-evoked EEG connectivity changes with statistical analysis in 5-20ms post-stimulus window
- **Kernel Notes**: 
  - CRITICAL: Event IDs in this analysis use `Stimulus/S  X` format (not `Stimulus/A` as in legacy documentation). Verify mapping: `Stimulus/S  2` (33,153 events) = stimulus onset, `Stimulus/S  3` = output marker, `Stimulus/S  4` = sub-threshold baseline
  - The 20kHz sampling rate requires downsampling to 1-5 kHz before analysis
  - TMS artifact (first ~10ms) requires specialized cleaning (e.g., SSP, ICA, template subtraction)
  - Analysis window: 5-20ms post-stimulus for AUC/connectivity calculation
  - Super Meta required to decode asynchrony condition from experimental design metadata

---

### Potential Task 1: Sub-threshold Baseline vs Active TMS Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s, target_events = [`Stimulus/S  2`, `Stimulus/S  4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event ID | y | Meaning |
  |----------|---|---|
  | `Stimulus/S  2` | 0 | Active TMS/PAS stimulus pulse (33,153 trials) |
  | `Stimulus/S  4` | 1 | Sub-threshold baseline TMS pulse (5,406 trials) |
- **Evidence**:
  - DOI: 10.3389/fnbot.2024.1336438 (partial) — Uses Dataset 2 (openneuro_ds004024) for TMS-EEG analysis; supports presence of active and sub-threshold TMS conditions in dataset
- **Kernel Notes**: 
  - Event ID mapping: `Stimulus/S  4` provides sub-threshold baseline trials (vs `Stimulus/S  2` for active TMS)
  - Class imbalance present (33,153 vs 5,406) - consider stratified sampling or class weighting
  - The 20kHz sampling rate requires downsampling before analysis
  - TMS artifact contaminates first ~10ms; specialized cleaning required before analysis
  - Verify sub-threshold condition timing matches experimental protocol specifications

## Data Quality Notes

- Pending manual review.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review
