# BCIT Advanced Guard Duty

**Dataset**: `openneuro_ds004106` | **Year**: 2022 | **URL**: https://openneuro.org/datasets/ds004106
**Category**: Complex Applied | **Subjects**: 29 | **Files (Completed)**: 29
**Channels**: 262 | **Sampling Rate**: 1024 Hz

## Paradigm

Subjects performed a sustained vigilance task simulating advanced security guard duties by verifying multiple fields on replica ID cards against reference images, under varying workloads and stochastic arrival rates of cards. EEG was recorded to identify biomarkers of mental fatigue and vigilance decrement over extended duty periods. Part of the BCIT sustained attention / guard duty dataset series.

## Kernel Responsibilities

- **Type 1 (Raw-meta extraction only)**: Extract and normalize raw labels from events/trigger streams.
- **Type 2 (Raw + Super meta integration)**: Derive and merge high-level labels that are not directly represented in raw events.
- **Type 3 (Label-route orchestration)**: Route final labels to EEGUnity-compatible channels (`Annotation`, `stim`, `misc`) with reproducible schema.

> **Selected Mode**: Type 1 + Type 3
> **Why**: Raw markers are sufficient for primary tasks.
> **Primary Label Routes**: Annotation
> **Web Reference Used for Decision**: https://openneuro.org/datasets/ds004106

## Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `1311` | 29 files | short | raw | Card/stimulus arrival event - type 1311 |
| `1312` | 29 files | short | raw | Card/stimulus arrival event - type 1312 |
| `1321` | 29 files | short | raw | Verification response event |
| `1322` | 29 files | short | raw | Verification response event |
| `1331`-`1362` | 27-29 files | short | raw | Guard duty task events (various verification stages) |
| `1341`-`1342` | 29 files | short | raw | Guard duty task events |
| `1351`-`1352` | 27-29 files | short | raw | Guard duty task events |
| `1221`-`1222` | 29 files | short | raw | Guard duty task events |
| `1211`-`1212` | 28 files | short | raw | Guard duty task events |
| `1231`-`1232` | 28 files | short | raw | Guard duty task events |
| `1241`-`1242` | 27 files | short | raw | Guard duty task events |
| `1251`-`1252` | 27 files | short | raw | Guard duty task events |
| `1121`-`1122` | 27 files | short | raw | Guard duty task events |
| `2110` | 29 files | short | raw | Workload condition marker - high |
| `2120` | 29 files | short | raw | Workload condition marker - low |
| `3111`-`3112` | 26 files | short | raw | Block/session markers |
| `3231`-`3232` | 2 files | short | raw | Rare condition events |

> **Event Type Description**:
> - `short`: short stimulus onset marker (presentation duration <2 s), for `epoch_by_event_hdf5`
> - `long`: long-term status flag (retention period is usually >=2 s), used for `epoch_by_long_event_hdf5`
> - `rest`: Rest block tag, used for `epoch_by_long_event_hdf5` or `epoch_by_segmentation_hdf5`
> - `admin`: system/boundary marker, **not used for epoch**

## Tasks

### Primary Task 1: Continuous Behavioral Performance Estimation
- **Task Type**: regression
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = ~0.73 s * (750 points at 1024 Hz), overlap = ~0.33 * (500-point step ≈ 0.49 s overlap), target_events = N/A (sliding window on raw signal)
- **Label Route**: `Annotation`
- **Meta Level**: super
- **Target Definition**:
  | y | Meaning |
  |---|---------|
  | continuous (meters) | Lane deviation from driving simulator |
  | continuous (seconds) | Response time (RT) from ID verification task |
  | continuous (proportion) | Accuracy (proportion correct) from ID verification task |
- **Super Meta Notes**: Behavioral labels are derived from task performance metrics computed over time. The paper applies a 90s centered mean filter to both EEG power spectra and behavioral measures to align temporal dynamics. Linear regression with ICA-based EEG spectral features is used to predict these continuous behavioral metrics.
- **Evidence**:
  - DOI: 10.1016/j.biopsycho.2015.12.009 — This 2016 study by Touryan et al. used linear regression with ICA-based EEG spectral features to estimate continuous behavioral performance (lane deviation, RT, accuracy) in a simulated guard duty task similar to the BCIT Advanced Guard Duty dataset, achieving correlation coefficients of 0.548±0.117 for driving and 0.701±0.154 for guard duty tasks.
- **Kernel Notes**: Must compute ICA decomposition first, extract spectral power features (likely alpha/theta bands), then train linear regression to predict each behavioral metric. Apply 90s centered mean smoothing to both EEG and behavioral labels before training.

### Normal Task 1: High vs Low Workload (binary)
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = -0.2 s, tmax = 1.0 s (relative to event onset), target_events = see Target Definition
- **Label Route**: `Annotation`
- **Target Definition**: Event-to-label mapping table below.
- **Notes**: 262-channel BioSemi cap - very high-density EEG. Full BCIT event codebook required for precise decoding. Part of the BCIT guard duty series (see also ds004119 Basic Guard Duty).

| Event | y | Meaning |
 |-------|---|------|
 | `2110` | 0 | High workload condition marker |
 | `2120` | 1 | Low workload condition marker |

## Data Quality Notes

- 262 channels - largest EEG cap in the BCIT series; high memory requirements
- Full event decoding requires BCIT codebook documentation
- Very limited subjects (29) for the large channel count

## References

- **Reference**: `BCIT Advanced Guard Duty`
