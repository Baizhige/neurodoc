# Auditory Gamma Entrainment

**Dataset**: `openneuro_ds003800` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003800
**Category**: Sensory/Response | **Subjects**: 8 | **Files (Completed)**: 24
**Channels**: 19 | **Sampling Rate**: 250 Hz

## Paradigm

Elderly participants with dementia received 40 Hz amplitude-modulated (AM) auditory stimulation to induce gamma-band entrainment of brain oscillations. The paradigm alternated between active 40 Hz AM stimulation (Stimulus) periods and quiet rest periods. The study investigates whether auditory gamma entrainment can modulate neural oscillations in a dementia population, potentially as a therapeutic intervention. EEG was recorded using a standard 10-20 system.


## File Scan Result

> **Kernel**: N/A
> **SHA256**: N/A

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 13 | event | raw | 40 Hz AM auditory stimulation period onset |
| `Rest` | 13 | event | raw | Resting/quiet period |


### Info

| Field | Completeness | Notes |
|---|---|---|
| `subject_age` | missing | N/A |
| `subject_sex` | missing | N/A |
| `device` | missing | N/A |
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Classical Task 1: Stimulus vs Rest Classification (Gamma Entrainment)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s (Stimulus), tmax = 20 s (Rest), overlap = 0.0, target_events = [`Stimulus`, `Rest`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Stimulus` | 1 | 40 Hz AM auditory stimulation period (event code 2) |
  | `Rest` | 0 | Resting/quiet period (event code 1) |
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.107839 — Binary classification of stimulus vs rest during 40 Hz auditory gamma entrainment. Stimulus trials: 40s duration; rest trials: 20s duration; total task: 340s (6x40s stimulus + 5x20s rest).
- **Kernel Notes**: Use long-event epoching to extract 40s windows for Stimulus and 20s windows for Rest periods. The dataset contains 6 stimulus and 5 rest periods per session. (replaces Potential Task 1 from original analysis.md)

### Classical Task 2: Entrained vs Non-Entrained Classification (Super Meta)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s, overlap = 0.0, target_events = [`Stimulus`]
- **Label Route**: `event`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Entrained` | 1 | Participant showed 40Hz response amplitude >= 3 SD above mean of adjacent frequencies (38-42Hz) |
  | `Non-Entrained` | 0 | Participant showed 40Hz response amplitude < 3 SD above mean of adjacent frequencies |
- **Super Meta Notes**: Derived from raw events [`Stimulus`, `Rest`] by computing peak 40Hz response amplitude in the gamma band (38-42Hz) during stimulus periods. Kernel step: Compute FFT/power spectral density for each stimulus epoch, extract gamma band power, classify as entrained if >= 3 standard deviations above mean of adjacent frequencies.
- **Evidence**:
  - DOI: 10.18178/ijpmbs.13.1.14-18 — Binary classification of stimulus vs rest periods and entrained vs non-entrained patients based on gamma response. Entrained/non-entrained classification derived from whether peak 40Hz response amplitude >= 3 standard deviations above mean of adjacent frequencies.
- **Kernel Notes**: Requires computing power spectral density for each stimulus epoch and applying threshold-based classification for entrainment status.

## Data Quality Notes

- Very small dataset (8 subjects, 24 files); results may not generalize.
- Elderly dementia population; data quality may be variable.
- 19-channel 10-20 EEG; limited spatial resolution.
- 250 Hz sampling rate; adequate for gamma entrainment analysis up to 125 Hz.


## Kernel Responsibilities

> **Super Meta Required**: Yes
> **Status**: wait_manual_review