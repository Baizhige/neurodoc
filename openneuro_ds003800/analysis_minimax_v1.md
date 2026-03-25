# Auditory Gamma Entrainment

**Dataset**: `openneuro_ds003800` | **Year**: 2021 | **URL**: https://openneuro.org/datasets/ds003800
**Category**: Sensory/Response | **Subjects**: 8 | **Files (Completed)**: 24
**Channels**: 19 | **Sampling Rate**: 250 Hz

## Paradigm

Elderly participants with dementia received 40 Hz amplitude-modulated (AM) auditory stimulation to induce gamma-band entrainment of brain oscillations. The paradigm alternated between active 40 Hz AM stimulation (Stimulus) periods and quiet rest periods. The study investigates whether auditory gamma entrainment can modulate neural oscillations in a dementia population, potentially as a therapeutic intervention. EEG was recorded using a standard 10-20 system.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation, stim
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds003800

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `Stimulus` | 13 | long | raw | 40 Hz AM auditory stimulation period onset |
| `Rest` | 13 | long | raw | Resting/quiet period |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**
## STIM Label Summary

- **Route**: `stim`
- **Role**: Trigger-channel or stimulus-marker based labeling.
- **Candidate Trigger Labels**: `Stimulus`
- **Kernel Note**: Keep trigger decoding table versioned and auditable.

## Tasks

### Primary Task 1: Auditory Gamma Entrainment - Stimulus vs Rest Binary Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s (stimulus) / 20 s (rest), overlap = 0.0, target_events = [`Stimulus`, `Rest`]
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Rest` | 0 | Rest/quiet period (event code 1) |
  | `Stimulus` | 1 | 40 Hz AM auditory stimulation period (event code 2) |
- **Super Meta Notes**: (Not applicable - meta_level is raw)
- **Evidence**:
  - DOI: 10.1016/j.dib.2022.107839 — Data in Brief article describing Auditory Gamma Entrainment dataset with EEG recordings from elderly participants during 40 Hz auditory stimulation trials (6×40s) interleaved with rest periods (5×20s), events labeled as 1 for rest and 2 for stimulus onset.
  - DOI: 10.18178/ijpmbs.13.1.14-18 — Paper analyzing brain oscillations comparing rest vs stimulus trials using the same dataset with stimulus event code 2 and rest event code 1.
- **Kernel Notes**: Use event codes from triggers (1=Rest, 2=Stimulus). Each stimulus block is 40s, each rest block is 20s. Session consists of initial 1-min rest followed by 6 stimulus blocks (40s each) and 5 rest blocks (20s each), totaling ~340s.

### Primary Task 2: Entrained vs Non-Entrained Patient Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0 s, tmax = 40 s (stimulus) / 20 s (rest), overlap = 0.0, target_events = [`Stimulus`, `Rest`]
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `Non-Entrained` | 0 | Patient showing gamma response amplitude < 3 SD above mean of adjacent frequencies (38-42 Hz) |
  | `Entrained` | 1 | Patient showing gamma response amplitude ≥ 3 SD above mean of adjacent frequencies (38-42 Hz) |
- **Super Meta Notes**: Classification derived from whether peak 40 Hz response amplitude in the stimulus condition is >= 3 standard deviations above the mean of adjacent frequencies (38-42 Hz). Requires spectral analysis of epoched stimulus data to compute gamma power.
- **Evidence**:
  - DOI: 10.18178/ijpmbs.13.1.14-18 — Paper classifying patients as entrained or non-entrained based on gamma power response to 40 Hz auditory stimulation, using the threshold of >=3 SD above mean of adjacent frequencies (38-42 Hz).
- **Kernel Notes**: Requires computing FFT/PSD on stimulus epoch data, extracting gamma-band (40 Hz) power, comparing to adjacent frequencies (38-42 Hz), and applying threshold to create binary entrained/non-entrained labels per subject.

### Normal Task 1: Stimulation period vs resting period (binary, long event)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_long_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 2.0 s, overlap = 0.5, target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Stimulation and rest periods are sustained states (likely 1-5 min each); use long-event epoching. Only 8 subjects and 24 files - very small dataset. 19-channel EEG (10-20 system).

| Event | y | Meaning |
|-------|---|------|
| `Stimulus` | 1 | 40 Hz AM auditory stimulation activation period |
| `Rest` | 0 | Rest/quiet period |

## Data Quality Notes

- Very small dataset (8 subjects, 24 files); results may not generalize.
- Elderly dementia population; data quality may be variable.
- 19-channel 10-20 EEG; limited spatial resolution.
- 250 Hz sampling rate; adequate for gamma entrainment analysis up to 125 Hz.

## References

- **Reference**: `Auditory Gamma Entrainment in Elderly with Dementia. OpenNeuro ds003800.`
