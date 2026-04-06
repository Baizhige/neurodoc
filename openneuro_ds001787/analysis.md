# EEG meditation study

**Dataset**: `openneuro_ds001787` | **Year**: 2024 | **URL**: https://openneuro.org/datasets/ds001787
**Category**: Biological State | **Subjects**: 24 | **Files (Completed)**: 40 | **Channels**: 80 | **Sampling Rate**: 256 Hz

## Paradigm

Subjects engaged in focused meditation sessions that were interrupted every two minutes by a brief probe assessing concentration level and mind-wandering. EEG was recorded continuously with stimulus markers at probe onsets and response markers at button-press responses. The study examined neural correlates of sustained attention and mind-wandering during meditation using ERP and time-frequency analysis.

## Subject Information

<!-- AUTO-KERNEL-SUBJECT-INFO:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
- **Record Count**: 40
- **Age Completeness**: 38/40 (95.0%)
- **Sex Completeness**: 40/40 (100.0%)
- **Observed Age Examples**: `32.0`, `35.0`, `41.0`, `29.0`, `34.0`, `43.0`, `33.0`, `62.0`
- **Observed Sex Examples**: `Male`, `Female`
<!-- AUTO-KERNEL-SUBJECT-INFO:END -->


## File Scan Result

> **Kernel**: EEGUnity v3 | `Script/kernels/openneuro_specific/openneuro_ds001787.py`, `Script/kernels/openneuro_specific/_base.py`, `Script/kernels/bids.py`
> **SHA256**: `a57ee39dc55a7a56bbc26e5c0f591520f6a139f070cb78bd4dbfa9a96ad64143`

### Event Structure

<!-- AUTO-KERNEL-EVENT-STRUCTURE:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Event ID / Count / Type / Meta Level` are kernel-derived facts.

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `response` | 2143 | event | raw | Unresolved from current kernel facts |
| `stimulus` | 983 | event | raw | Unresolved from current kernel facts |
| `STATUS` | 5 | event | raw | Unresolved from current kernel facts |
<!-- AUTO-KERNEL-EVENT-STRUCTURE:END -->


### MISC Label Summary

<!-- AUTO-KERNEL-MISC:START -->
> **Kernel Fact Source**: current kernel scan from `/home/zgchen/code/EEGBenchmarkSkill/BIDS_description/Script/locator_meta_kernel_v3`
> **Meaning Policy**: `Meaning` is interpretive; `Label / Source / Meta Level` are kernel-derived facts.

| Label / Field | Source | Meta Level | Meaning |
|---------------|--------|------------|---------|
| *(none currently materialized by kernel)* | - | - | No dedicated labels currently materialized by kernel for this route |
<!-- AUTO-KERNEL-MISC:END -->

- **Route**: `misc`
- **Role**: Kernel-derived label summary for the current route only.


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | complete | N/A |
| `subject_sex` | complete | N/A |
| `device` | missing | N/A |
## Tasks

### Classical Task 1: EEG ISA-GSR Phase-Amplitude Coupling Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus` | 1 | High d-prime group (high ISA-GSR coupling) |
  | `stimulus` | 0 | Low d-prime group (low ISA-GSR coupling) |
- **Super Meta Notes**: Derived from raw event(s) [`stimulus`, `response`] by computing d-prime of phase-amplitude coupling between EEG infraslow activity (0.01-0.1 Hz) phase and GSR amplitude during first 30s of each meditation trial; subjects divided into high/low coupling groups based on channel-average d-prime values. Kernel step: Load EEG and GSR signals, compute ISA phase via Hilbert transform, compute GSR amplitude envelope, calculate phase-amplitude coupling d-prime, threshold to create binary labels.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.765585 — The paper analyzes coupling between EEG infraslow activity (0.01-0.1 Hz) phase and galvanic skin response amplitude during the first 30 seconds of each meditation trial from openneuro dataset ds001787, computing d-prime values and dividing subjects into high/low coupling groups.
- **Kernel Notes**: Verify event ID mapping from events.tsv — the paper references 'meditation_onset' but this is not available in raw events; using 'stimulus' as proxy for meditation session probe. Also computes expert vs novice classification which can be added as separate label set. (replaces incomplete Classical Task 1 from original analysis.md)

### Classical Task 2: Expert vs Novice Meditator Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 30 s, overlap = 0.0, target_events = [`stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `stimulus` | 1 | Expert meditator |
  | `stimulus` | 0 | Novice meditator |
- **Super Meta Notes**: Derived from raw event(s) [`stimulus`, `response`] by subject group assignment (expert vs novice) as defined in dataset demographics. Kernel step: Load subject metadata, map subject IDs to expertise level, create binary labels per trial.
- **Evidence**:
  - DOI: 10.3389/fnins.2022.765585 — The paper compares expert versus novice meditators in EEG ISA-GSR coupling analysis.
- **Kernel Notes**: Requires subject demographic data from dataset; verify expertise level encoding in participants.tsv.

### Potential Task 1: Stimulus-Response ERP (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `event`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: `STATUS` is a BioSemi admin marker (count=5 files only) - excluded from target_events. Regression target: `response_time` from misc channel. The count column shows files-with-event, not total trial count.

 | Event | y | Meaning |
 |-------|---|---------|
 | `stimulus` | 0 | Probe stimulus onset |
 | `response` | 1 | Button-press response |

## Data Quality Notes

- `STATUS` events are BioSemi system markers, not task events - do not epoch on these.
- Multiple `response` events may occur per `stimulus` probe; consider windowing to first response only.
- Verify channel count consistency across subjects before pooling.

## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_kernel_update