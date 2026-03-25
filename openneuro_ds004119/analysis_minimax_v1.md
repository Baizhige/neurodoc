# BCIT Basic Guard Duty

**Dataset**: `openneuro_ds004119` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004119
**Category**: Complex Applied | **Subjects**: 22 | **Files (Completed)**: 22
**Channels**: 262 | **Sampling Rate**: 1024 Hz

## Paradigm

A realistic sustained vigilance task in which subjects verified multiple identification card fields against reference images in a simulated security environment under varying card arrival rates. This basic guard duty variant uses a simpler verification protocol compared to the Advanced Guard Duty (ds004106), and is designed to study EEG correlates of sustained attention and vigilance decrement over extended duty periods.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004119

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1311` | 22 files | short | raw | Card arrival / verification stimulus onset |
| `1312` | 22 files | short | raw | Card arrival event |
| `1321`-`1322` | 22 files | short | raw | Verification response events |
| `1331`-`1332` | 22 files | short | raw | Guard duty task events |
| `1341`-`1342` | 22 files | short | raw | Guard duty task events |
| `1351`-`1352` | 22 files | short | raw | Guard duty task events |
| `1361`-`1362` | 22 files | short | raw | Guard duty task events |
| `1231`-`1232` | 22 files | short | raw | Guard duty task events |
| `2110` | 22 files | short | raw | High workload condition marker |
| `2120` | 22 files | short | raw | Low workload condition marker |
| `3111`-`3112` | 20 files | short | raw | Block/session markers |
| `1111`-`1112` | 21 files | short | raw | Guard duty task events |
| `3241`-`3242` | 6 files | short | raw | Rare condition events |
| `3231`-`3232` | 1 file | short | raw | Very rare condition events |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Continuous Behavioral Performance Regression
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 3 s, overlap = 0.33 *
- **Label Route**: `Annotation`
- **Meta Level**: raw
- **Target Definition**:
  | y | Meaning |
  |---|---------|
  | continuous | Lane deviation (driving), perturbation RT (driving), RT (guard duty), accuracy (guard duty) |
- **Super Meta Notes**: Target is continuous behavioral performance metric derived from behavioral measurements (lane deviation, RT, accuracy), not from raw event markers. Performance is smoothed with 90s centered mean filter. The kernel must compute smoothed behavioral metrics (RT, accuracy) from behavioral logs, then match each 3s EEG epoch with the corresponding smoothed behavioral value at the epoch center time.
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — Linear regression to estimate continuous behavioral performance (lane deviation and RT for driving, RT and accuracy for guard duty) from EEG power spectral density features extracted via ICA and smoothed with a 90s mean filter.

### Normal Task 1: High vs Low Workload (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: Small cohort (22 subjects). 262-channel BioSemi cap. Paired with ds004106 (Advanced Guard Duty) - can be combined for larger guard duty cohort.

| Event | y | Meaning |
|-------|---|------|
| `2110` | 0 | High workload condition |
| `2120` | 1 | Low workload condition |

## Data Quality Notes

- 262 channels - very high-density EEG; high memory requirements
- Only 22 subjects - small sample size
- Full event code decoding requires BCIT codebook documentation

## References

- **Reference**: `Gross, Matthews, Cohn, Kanade, & Baker, 2010`
